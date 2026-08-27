#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import fnmatch
import functools
import json
import os
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    # NotRequired is 3.11+, but this runs under whatever `python3` resolves to, which on a stock macOS is 3.9
    # The `annotations` future keeps every annotation below a string, so it is never evaluated at runtime
    from typing import NotRequired

# Only needed for generating shell completion during local development
try:
    import argcomplete
except ImportError:
    argcomplete = None  # ty: ignore[invalid-assignment]


class Settings:
    REPO_ROOT: str = str(Path(__file__).resolve().parent.parent)
    DOTFILES_ROOT: str = str(Path(REPO_ROOT) / "dotfiles")
    IGNORE_PATTERNS: tuple[str, ...] = (".DS_Store", ".venv", ".*_cache", "__pycache__", "node_modules", "-private-tmp*")
    # Skipped when diffing a backup against its source, but still copied by backup itself:
    # git reclaims loose objects and packs locally, so a copy-only backup keeps every
    # superseded one forever and they would drown out the orphans worth seeing.
    DIFF_IGNORE_PATTERNS: tuple[str, ...] = (".git",)


class Entry(TypedDict):
    src: str
    dest: str
    prune: NotRequired[bool]  # Backup entries only: false keeps --prune away from this destination


class Dotfiles:
    DEFAULT_CONFIG: str = str(Path(Settings.DOTFILES_ROOT) / "hal_dotfiles.json")
    # Keys are written back in this order; any other key follows them, sorted by name
    ENTRY_KEY_ORDER: tuple[str, ...] = ("src", "dest", "prune")

    def __init__(self, path: str | None = None) -> None:
        self.path: str = path or self.DEFAULT_CONFIG
        self._data: dict[str, list[Entry]] | None = None

    @property
    def data(self) -> dict[str, list[Entry]]:
        if self._data is None:
            self._data = self._load()
        return self._data

    def _load(self) -> dict[str, list[Entry]]:
        try:
            with Path(self.path).open() as f:
                return json.load(f)
        except FileNotFoundError:
            return {"backups": [], "copies": [], "links": []}

    def upsert(self, field_name: str, src: str, dest: str) -> None:
        """Point the entry for src at dest, adding the entry when there is none."""
        entries = self.data[field_name]
        existing = next((entry for entry in entries if entry["src"] == src), None)
        if existing:
            existing["dest"] = dest
        else:
            entries.append({"dest": dest, "src": src})

    def remove(self, field_name: str, entry: Entry) -> None:
        self.data[field_name].remove(entry)

    @staticmethod
    def _ordered_entry(entry: Entry) -> dict[str, object]:
        """The entry with its keys in ENTRY_KEY_ORDER, any other key after them by name."""
        fields = dict(entry.items())
        known = [key for key in Dotfiles.ENTRY_KEY_ORDER if key in fields]
        unknown = sorted(key for key in fields if key not in Dotfiles.ENTRY_KEY_ORDER)
        return {key: fields[key] for key in [*known, *unknown]}

    def _ordered_data(self) -> dict[str, list[dict[str, object]]]:
        """The manifest as written back to disk, so plain mappings rather than Entry values."""
        return {field_name: [self._ordered_entry(entry) for entry in entries] for field_name, entries in sorted(self.data.items())}

    def show(self) -> None:
        print(json.dumps(self._ordered_data(), indent=2, separators=(",", ": ")))

    def save(self) -> None:
        # Read before opening for write: opening truncates, and data loads lazily,
        # so building the payload inside the with block would read back an empty file
        ordered_data = self._ordered_data()
        with Path(self.path).open("w") as f:
            json.dump(ordered_data, f, indent=2, separators=(",", ": "))


class Formatter(argparse.HelpFormatter):
    def __init__(self, prog: str) -> None:
        super().__init__(prog, max_help_position=30)


class HAL9000:
    def __init__(self) -> None:
        parser = argparse.ArgumentParser(
            prog="hal",
            description="I am completely operational, and all my circuits are functioning perfectly",
            formatter_class=Formatter,
        )
        self.parser = parser

        self.parser.add_argument("-v", "--version", action="version", version="9000")

        # Commands that forward unrecognized arguments override this on their own subparser
        parser.set_defaults(passthrough=False)

        subparsers = parser.add_subparsers(title="sub commands")

        update_parser = subparsers.add_parser(
            "update",
            help="pull repo and run ansible-playbook (extra args pass through, e.g. --tags python,node)",
            usage="hal update [-h] [ansible-playbook args ...]",
            description="pull repo and run ansible-playbook; extra args pass through to ansible-playbook, e.g. hal update --tags python,node",
        )
        update_parser.set_defaults(func=self.update, passthrough=True)

        self.dotfiles = Dotfiles()

        link_parser = subparsers.add_parser("link", help="move file into dotfiles and symlink it back")
        link_parser.set_defaults(func=self.link)
        link_parser.add_argument("filename", type=str)

        unlink_parser = subparsers.add_parser("unlink", help="move file back from dotfiles and remove symlink")
        unlink_parser.set_defaults(func=self.unlink)
        unlink_parser.add_argument("filename", type=str)

        copy_parser = subparsers.add_parser("copy", help="copy file into dotfiles (no symlink)")
        copy_parser.set_defaults(func=self.copy)
        copy_parser.add_argument("filename", type=str)

        sync_parser = subparsers.add_parser("sync", help="sync all links and copies")
        sync_parser.set_defaults(func=self.sync)
        sync_parser.add_argument("--force", action="store_true", help="replace real directories at link destinations")

        backup_parser = subparsers.add_parser("backup", help="back up all backup entries to their destinations")
        backup_parser.set_defaults(func=self.backup)
        backup_parser.add_argument("--prune", action="store_true", help="after backing up, list files present only in the backup and offer to delete them")

        restore_parser = subparsers.add_parser("restore", help="restore all backup entries, overwriting local files")
        restore_parser.set_defaults(func=self.restore)

        pod_bay_doors_parser = subparsers.add_parser("open-the-pod-bay-doors", help="open the pod bay doors, please, HAL")
        pod_bay_doors_parser.set_defaults(func=self.open_the_pod_bay_doors)

        if argcomplete:
            argcomplete.autocomplete(parser)

    @staticmethod
    def _abbreviate_home(path: str | Path) -> str:
        """A single path with its home directory prefix shown as ~, for messages that name one."""
        home = str(Path.home())
        text = str(path)
        return f"~{text[len(home) :]}" if text.startswith(home) else text

    def _hal_says(self, text: str) -> None:
        print(f"HAL: {text}")

    def _validate_path(self, path: str) -> None:
        resolved = Path(path).resolve()
        allowed_roots = (Path.home(), Path(Settings.REPO_ROOT))
        if not any(resolved.is_relative_to(root) for root in allowed_roots):
            self._hal_says(f"I'm sorry, Dave. I'm afraid I can't do that: {self._abbreviate_home(resolved)}")
            sys.exit(1)

    def _expand_template(self, path: str) -> str:
        expanded = path.replace("{{HOME}}", str(Path.home())).replace("{{REPO_ROOT}}", Settings.REPO_ROOT)
        self._validate_path(expanded)
        return expanded

    def _prepare_dotfile_entry(self, filename: str) -> tuple[str, str, str, str]:
        filepath = str((Path.cwd() / filename).resolve())
        self._validate_path(filepath)

        home = str(Path.home())
        relative_path = str(Path(filepath).relative_to(home)) if filepath.startswith(home) else Path(filepath).name

        dest_path = str(Path(Settings.DOTFILES_ROOT) / relative_path)
        dest_dir = str(Path(dest_path).parent)

        if dest_dir != Settings.DOTFILES_ROOT:
            Path(dest_dir).mkdir(parents=True, exist_ok=True)

        template_src = dest_path.replace(Settings.REPO_ROOT, "{{REPO_ROOT}}")
        template_dest = filepath.replace(home, "{{HOME}}")

        return filepath, dest_path, template_src, template_dest

    def _run(self, command: str, *, cwd: str | None = None, verbose: bool = True) -> int:
        if verbose:
            self._hal_says(command)

        return subprocess.run(command, shell=True, cwd=cwd).returncode  # noqa: S602 PLW1510 subprocess-popen-with-shell-equals-true subprocess-run-without-check

    def update(self, namespace: argparse.Namespace) -> None:
        ansible_path = shutil.which("ansible")
        if ansible_path and not ansible_path.startswith("/opt/homebrew/bin/"):
            self._hal_says(f"Found ansible at: {self._abbreviate_home(ansible_path)}")
            self._hal_says("You should use Homebrew's ansible")
            sys.exit(1)

        self._run("git fetch", cwd=Settings.REPO_ROOT)
        returncode = self._run("git pull", cwd=Settings.REPO_ROOT)
        if returncode != 0:
            sys.exit(returncode)

        playbooks_dir = str(Path(Settings.REPO_ROOT) / "playbooks")
        command = "ansible-playbook site.yml -v"
        if namespace.extra_args:
            command = " ".join([command, *(shlex.quote(arg) for arg in namespace.extra_args)])
        returncode = self._run(command, cwd=playbooks_dir)
        if returncode != 0:
            sys.exit(returncode)
        self._hal_says("Now open a new shell to active your dev environment")

    def link(self, namespace: argparse.Namespace) -> None:
        filepath, dest_path, template_src, template_dest = self._prepare_dotfile_entry(namespace.filename)

        shutil.move(filepath, dest_path)
        self._hal_says(f"mv {self._abbreviate_home(filepath)} -> {self._abbreviate_home(dest_path)}")

        ln_dest = Path(filepath)
        if ln_dest.is_symlink() or ln_dest.exists():
            ln_dest.unlink()
        ln_dest.symlink_to(dest_path)
        self._hal_says(f"ln {self._abbreviate_home(dest_path)} -> {self._abbreviate_home(filepath)}")

        self.dotfiles.upsert("links", template_src, template_dest)

        self.dotfiles.save()
        self.dotfiles.show()

    def unlink(self, namespace: argparse.Namespace) -> None:
        # abspath, not Path.resolve(): the path at dest IS the symlink this removes, and resolving it would land inside the dotfiles repo
        filepath = Path(os.path.abspath(Path(namespace.filename).expanduser()))  # noqa: PTH100 os-path-abspath
        ln_dict = next((entry for entry in self.dotfiles.data["links"] if Path(self._expand_template(entry["dest"])) == filepath), None)
        if not ln_dict:
            self._hal_says(f"not found in manifest: {self._abbreviate_home(filepath)}")
            return

        src_path = self._expand_template(ln_dict["src"])
        dest_path = self._expand_template(ln_dict["dest"])

        if not Path(src_path).exists():
            self._hal_says(f"not found in dotfiles: {self._abbreviate_home(src_path)}")
            return

        # A real directory at dest is one `hal sync` refused to replace, and it may hold files
        # no manifest entry covers. shutil.move would nest src inside it instead of replacing it.
        if Path(dest_path).is_dir() and not Path(dest_path).is_symlink():
            self._hal_says(f"refusing to replace directory {self._abbreviate_home(dest_path)}")
            return

        if Path(dest_path).is_symlink():
            Path(dest_path).unlink()
        shutil.move(src_path, dest_path)

        self.dotfiles.remove("links", ln_dict)

        self.dotfiles.save()
        self.dotfiles.show()

    def copy(self, namespace: argparse.Namespace) -> None:
        filepath, dest_path, template_src, template_dest = self._prepare_dotfile_entry(namespace.filename)

        shutil.copy2(filepath, dest_path)
        self._hal_says(f"cp {self._abbreviate_home(filepath)} -> {self._abbreviate_home(dest_path)}")

        self.dotfiles.upsert("copies", template_src, template_dest)

        self.dotfiles.save()
        self.dotfiles.show()

    def _sync_links(self, link: Entry, *, force: bool = False) -> None:
        src = self._expand_template(link["src"])
        if not Path(src).exists():
            self._hal_says(f"not found {self._abbreviate_home(src)}")
            return

        dest = self._expand_template(link["dest"]).rstrip("/")
        Path(dest).parent.mkdir(parents=True, exist_ok=True)

        # If dest already exists as a real directory, remove it so the symlink replaces it.
        # It may hold files no manifest entry covers, so make destroying them explicit.
        if Path(dest).is_dir() and not Path(dest).is_symlink():
            if not force:
                self._hal_says(f"refusing to replace directory {self._abbreviate_home(dest)}, re-run with --force")
                return
            shutil.rmtree(dest)

        dest_path = Path(dest)
        if dest_path.is_symlink() or dest_path.exists():
            dest_path.unlink()
        dest_path.symlink_to(src)
        self._hal_says(f"link {self._abbreviate_home(src)} -> {self._abbreviate_home(dest)}")

    @staticmethod
    def _is_unchanged(src: str, dest: str) -> bool:
        """Same quick check as rsync: matching size and mtime means no rewrite needed.

        Rewriting an identical file makes Dropbox and Time Machine re-examine it, so skip it.
        """
        dest_path = Path(dest)
        if not dest_path.exists():
            return False

        src_stat = Path(src).stat()
        dest_stat = dest_path.stat()
        return src_stat.st_size == dest_stat.st_size and src_stat.st_mtime_ns == dest_stat.st_mtime_ns

    @staticmethod
    def _copy_file_allow_overwrite(src: str, dest: str) -> None:
        if HAL9000._is_unchanged(src, dest):
            return

        dest_path = Path(dest)
        if dest_path.exists() and not dest_path.stat().st_mode & stat.S_IWUSR:
            dest_path.chmod(dest_path.stat().st_mode | stat.S_IWUSR)
        shutil.copy2(src, dest)

    @staticmethod
    def _is_ignored(path: str) -> bool:
        name = Path(path).name
        return any(fnmatch.fnmatch(name, pattern) for pattern in Settings.IGNORE_PATTERNS)

    def _copy_one(self, src: str, dest: str) -> None:
        if self._is_ignored(src):
            self._hal_says(f"ignored {self._abbreviate_home(src)}")
            return

        if Path(src).is_dir():
            shutil.copytree(
                src,
                dest,
                ignore=shutil.ignore_patterns(*Settings.IGNORE_PATTERNS),
                copy_function=self._copy_file_allow_overwrite,
                dirs_exist_ok=True,
            )
        else:
            if self._is_unchanged(src, dest):
                self._hal_says(f"unchanged {self._abbreviate_home(src)}")
                return
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            self._copy_file_allow_overwrite(src, dest)
        self._hal_says(f"copy {self._abbreviate_home(src)} -> {self._abbreviate_home(dest)}")

    def _glob_pairs(self, entry: Entry) -> list[tuple[str, str]]:
        """The (src, dest) pairs a single-`*` entry expands to, with each star spliced into dest.

        Copying and pruning have to read a pattern pair the same way: these destinations are
        exactly the ones a backup writes, so anything else matching the dest pattern is an orphan.
        """
        src = self._expand_template(entry["src"])
        dest = self._expand_template(entry["dest"])
        prefix, _, suffix = src.partition("*")
        dprefix, _, dsuffix = dest.partition("*")
        matches = sorted(str(match) for match in Path(src).parent.glob(Path(src).name))
        pairs = []
        for match in matches:
            star = match[len(prefix) : len(match) - len(suffix)]
            pairs.append((match, f"{dprefix}{star}{dsuffix}"))
        return pairs

    def _copy_entry(self, entry: Entry) -> None:
        src = self._expand_template(entry["src"])

        if "*" in src:
            pairs = self._glob_pairs(entry)
            if not pairs:
                self._hal_says(f"no matches {self._abbreviate_home(src)}")
                return
            for match, match_dest in pairs:
                self._copy_one(match, match_dest)
            return

        if not Path(src).exists():
            self._hal_says(f"not found {self._abbreviate_home(src)}")
            return

        dest = self._expand_template(entry["dest"])
        self._copy_one(src, dest)

    @staticmethod
    def _walk_names(root: Path, *, follow_symlinks: bool) -> set[str]:
        """Every path under root, relative to it, skipping ignored names.

        A source is walked through its symlinked directories because backup copies them
        dereferenced, leaving the destination holding their contents as real files; not
        descending would read every one of those files as an orphan. A destination is not,
        so a symlink there stays a single entry to unlink rather than a way out of the backup.
        """
        names: set[str] = set()
        visited = {root.resolve()}
        stack = [(root, "")]
        while stack:
            directory, prefix = stack.pop()
            for child in directory.iterdir():
                if HAL9000._is_ignored(str(child)) or child.name in Settings.DIFF_IGNORE_PATTERNS:
                    continue
                relative = f"{prefix}/{child.name}" if prefix else child.name
                names.add(relative)
                if not child.is_dir():
                    continue
                if child.is_symlink():
                    if not follow_symlinks:
                        continue
                    resolved = child.resolve()
                    if resolved in visited:
                        continue
                    visited.add(resolved)
                stack.append((child, relative))
        return names

    def _find_orphans(self, entry: Entry) -> list[Path]:
        """Paths in this entry's backup destination that no longer exist in its source.

        An entry whose source is missing or empty yields nothing: there the backup is
        the only surviving copy, and every file in it would otherwise read as an orphan.
        """
        src = Path(self._expand_template(entry["src"]))
        dest = Path(self._expand_template(entry["dest"]))

        if "*" in str(src):
            pairs = self._glob_pairs(entry)
            if not pairs:
                return []
            expected = {Path(pair_dest) for _, pair_dest in pairs}
            return sorted(match for match in dest.parent.glob(dest.name) if match not in expected)

        if not src.is_dir() or not dest.is_dir():
            return []

        src_names = self._walk_names(src, follow_symlinks=True)
        if not src_names:
            return []
        return sorted(dest / name for name in self._walk_names(dest, follow_symlinks=False) - src_names)

    def _remove_orphan(self, path: Path) -> bool:
        if path.is_symlink() or not path.is_dir():
            path.unlink()
            return True

        # Orphans are removed deepest first, so anything left inside a directory was
        # filtered out of the diff and never listed. Clear those, then rmdir, which
        # still refuses any directory holding something the listing did not account for.
        for child in path.iterdir():
            if not self._is_ignored(str(child)):
                continue
            if child.is_dir() and not child.is_symlink():
                shutil.rmtree(child)
            else:
                child.unlink()

        try:
            path.rmdir()
        except OSError as error:
            self._hal_says(f"kept {self._abbreviate_home(path)}: {error.strerror}")
            return False
        return True

    def _prune(self) -> None:
        orphans: list[Path] = []
        for entry in self.dotfiles.data["backups"]:
            if entry.get("prune", True):
                orphans.extend(self._find_orphans(entry))
            else:
                self._hal_says(f"prune disabled {self._abbreviate_home(self._expand_template(entry['dest']))}")

        if not orphans:
            self._hal_says("nothing to prune")
            return

        orphans.sort()
        counted = f"{len(orphans)} orphan" if len(orphans) == 1 else f"{len(orphans)} orphans"
        self._hal_says(f"{counted} in backup, absent from source:")
        for path in orphans:
            print(f"  {self._abbreviate_home(path)}")

        try:
            answer = input(f"Delete {counted} from backup? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() != "y":
            self._hal_says("aborted")
            return

        removed = sum(self._remove_orphan(path) for path in sorted(orphans, reverse=True))
        self._hal_says(f"pruned {removed}")

    @staticmethod
    def _parallel(tasks: Iterable[Callable[[], None]]) -> None:
        """Run every task on a thread pool.

        The first failure is re-raised on the calling thread, but only after every task
        has finished, because leaving the pool waits for the ones still running.
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(task) for task in tasks]
            for future in concurrent.futures.as_completed(futures):
                future.result()

    def sync(self, namespace: argparse.Namespace) -> None:
        tasks: list[Callable[[], None]] = [functools.partial(self._sync_links, link, force=namespace.force) for link in self.dotfiles.data["links"]]
        tasks += [functools.partial(self._copy_entry, copy) for copy in self.dotfiles.data["copies"]]
        self._parallel(tasks)

    def backup(self, namespace: argparse.Namespace) -> None:
        self._parallel(functools.partial(self._copy_entry, entry) for entry in self.dotfiles.data["backups"])

        if namespace.prune:
            self._prune()

    def restore(self, namespace: argparse.Namespace) -> None:  # noqa: ARG002 unused-method-argument
        entries = self.dotfiles.data["backups"]
        if not entries:
            self._hal_says("nothing to restore")
            return

        for entry in entries:
            self._hal_says(f"{self._abbreviate_home(self._expand_template(entry['dest']))} -> {self._abbreviate_home(self._expand_template(entry['src']))}")

        try:
            answer = input("Overwrite local files with backups? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() != "y":
            self._hal_says("aborted")
            return

        self._parallel(functools.partial(self._copy_entry, Entry(src=entry["dest"], dest=entry["src"])) for entry in entries)

    def open_the_pod_bay_doors(self, namespace: argparse.Namespace) -> None:  # noqa: ARG002 unused-method-argument
        self._hal_says("I'm sorry Dave, I'm afraid I can't do that.")

        filepath = str(Path(Settings.REPO_ROOT) / "assets" / "im-sorry-dave-im-afraid-i-cant-do-that.mp3")
        self._run(f"afplay {shlex.quote(filepath)}", verbose=False)

    def read_lips(self) -> None:
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(0)

        namespace, extra_args = self.parser.parse_known_args()

        if extra_args and not namespace.passthrough:
            self.parser.parse_args()  # Will error with usage message on unrecognized args

        namespace.extra_args = extra_args
        namespace.func(namespace)


if __name__ == "__main__":
    hal_9000 = HAL9000()
    hal_9000.read_lips()

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import fnmatch
import json
import shlex
import shutil
import stat
import subprocess
import sys
from pathlib import Path

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


class Dotfiles:
    DEFAULT_CONFIG: str = str(Path(Settings.DOTFILES_ROOT) / "hal_dotfiles.json")
    ENTRY_KEY_ORDER: tuple[str, ...] = ("src", "dest")

    def __init__(self, path: str | None = None) -> None:
        self.path: str = path or self.DEFAULT_CONFIG
        self._data: dict[str, list[dict[str, str]]] | None = None

    @property
    def data(self) -> dict[str, list[dict[str, str]]]:
        if self._data is None:
            try:
                with Path(self.path).open() as f:
                    self._data = json.load(f)
            except FileNotFoundError:
                self._data = {"backups": [], "copies": [], "links": []}

        assert self._data is not None  # noqa: S101 assert
        return self._data

    def find_by_key(self, key: str, value: str, field_name: str) -> dict[str, str] | None:
        entries = self.data[field_name]
        try:
            return next(entry for entry in entries if entry[key] == value)
        except StopIteration:
            return None

    def _ordered_data(self) -> dict[str, list[dict[str, str]]]:
        return {field_name: [{key: entry[key] for key in self.ENTRY_KEY_ORDER if key in entry} for entry in entries] for field_name, entries in sorted(self.data.items())}

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

        subparsers = parser.add_subparsers(title="sub commands")

        update_parser = subparsers.add_parser(
            "update",
            help="pull repo and run ansible-playbook (extra args pass through, e.g. --tags python,node)",
            usage="hal update [-h] [ansible-playbook args ...]",
            description="pull repo and run ansible-playbook; extra args pass through to ansible-playbook, e.g. hal update --tags python,node",
        )
        update_parser.set_defaults(func=self.update)

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

    def _hal_says(self, text: str) -> None:
        print(f"HAL: {text}")

    def _validate_path(self, path: str) -> None:
        resolved = Path(path).resolve()
        allowed_roots = (Path.home(), Path(Settings.REPO_ROOT))
        if not any(resolved.is_relative_to(root) for root in allowed_roots):
            self._hal_says(f"I'm sorry, Dave. I'm afraid I can't do that: {resolved}")
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

    def _run(self, command: str, *, shell: bool = True, verbose: bool = True) -> int:
        if verbose:
            self._hal_says(command)

        return subprocess.run(command, shell=shell).returncode  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check

    def _run_with_output(self, command: str, *, shell: bool = True, verbose: bool = True, print_output: bool = True) -> tuple[int, bytes]:
        if verbose:
            self._hal_says(command)

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=shell)  # noqa: S603 PLW1510 subprocess-without-shell-equals-true subprocess-run-without-check
        if print_output and result.stdout:
            print(result.stdout, end="")

        return result.returncode, result.stdout

    def update(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        returncode, output = self._run_with_output("which ansible", print_output=False)
        if returncode == 0:
            ansible_path = output.decode().strip()
            if not ansible_path.startswith("/opt/homebrew/bin/"):
                self._hal_says(f"Found ansible at: {ansible_path}")
                self._hal_says("You should use Homebrew's ansible")
                sys.exit(1)

        import os  # noqa: PLC0415 import-outside-top-level

        os.chdir(Settings.REPO_ROOT)
        self._run("git fetch")
        returncode = self._run("git pull")
        if returncode != 0:
            sys.exit(returncode)

        os.chdir(str(Path(Settings.REPO_ROOT) / "playbooks"))
        command = "ansible-playbook site.yml -v"
        if extra_args:
            command = " ".join([command, *(shlex.quote(arg) for arg in extra_args)])
        returncode = self._run(command)
        if returncode != 0:
            sys.exit(returncode)
        self._hal_says("Now open a new shell to active your dev environment")

    def link(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        filepath, dest_path, template_src, template_dest = self._prepare_dotfile_entry(namespace.filename)

        shutil.move(filepath, dest_path)
        self._hal_says(f"mv {filepath} -> {dest_path}")

        ln_dest = Path(filepath)
        if ln_dest.is_symlink() or ln_dest.exists():
            ln_dest.unlink()
        ln_dest.symlink_to(dest_path)
        self._hal_says(f"ln {dest_path} -> {filepath}")

        ln_dict = self.dotfiles.find_by_key("src", template_src, "links")
        if ln_dict:
            ln_dict["dest"] = template_dest
        else:
            self.dotfiles.data["links"].append({"dest": template_dest, "src": template_src})

        self.dotfiles.save()
        self.dotfiles.show()

    def unlink(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        relative_path = namespace.filename.removeprefix("~/")
        template_dest = "{{HOME}}/" + relative_path

        ln_dict = self.dotfiles.find_by_key("dest", template_dest, "links")
        if not ln_dict:
            self._hal_says(f"not found in manifest: {relative_path}")
            return

        src_path = self._expand_template(ln_dict["src"])
        dest_path = self._expand_template(ln_dict["dest"])

        if not Path(src_path).exists():
            self._hal_says(f"not found in dotfiles: {src_path}")
            return

        if Path(dest_path).is_symlink():
            Path(dest_path).unlink()
        shutil.copy2(src_path, dest_path)
        Path(src_path).unlink()

        self.dotfiles.data["links"].remove(ln_dict)

        self.dotfiles.save()
        self.dotfiles.show()

    def copy(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        filepath, dest_path, template_src, template_dest = self._prepare_dotfile_entry(namespace.filename)

        shutil.copy2(filepath, dest_path)
        self._hal_says(f"cp {filepath} -> {dest_path}")

        cp_dict = self.dotfiles.find_by_key("src", template_src, "copies")
        if cp_dict:
            cp_dict["dest"] = template_dest
        else:
            self.dotfiles.data["copies"].append({"dest": template_dest, "src": template_src})

        self.dotfiles.save()
        self.dotfiles.show()

    def _sync_links(self, link: dict[str, str], *, force: bool = False) -> None:
        src = self._expand_template(link["src"])
        if not Path(src).exists():
            self._hal_says(f"not found {src}")
            return

        dest = self._expand_template(link["dest"]).rstrip("/")
        Path(dest).parent.mkdir(parents=True, exist_ok=True)

        # If dest already exists as a real directory, remove it so the symlink replaces it.
        # It may hold files no manifest entry covers, so make destroying them explicit.
        if Path(dest).is_dir() and not Path(dest).is_symlink():
            if not force:
                self._hal_says(f"refusing to replace directory {dest}, re-run with --force")
                return
            shutil.rmtree(dest)

        dest_path = Path(dest)
        if dest_path.is_symlink() or dest_path.exists():
            dest_path.unlink()
        dest_path.symlink_to(src)
        self._hal_says(f"link {src} -> {dest}")

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
            self._hal_says(f"ignored {src}")
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
                self._hal_says(f"unchanged {src}")
                return
            Path(dest).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        self._hal_says(f"copy {src} -> {dest}")

    def _copy_entry(self, entry: dict[str, str]) -> None:
        src = self._expand_template(entry["src"])

        if "*" in src:
            dest = self._expand_template(entry["dest"])
            prefix, _, suffix = src.partition("*")
            dprefix, _, dsuffix = dest.partition("*")
            matches = sorted(str(match) for match in Path(src).parent.glob(Path(src).name))
            if not matches:
                self._hal_says(f"no matches {src}")
                return
            for match in matches:
                star = match[len(prefix) : len(match) - len(suffix)]
                self._copy_one(match, f"{dprefix}{star}{dsuffix}")
            return

        if not Path(src).exists():
            self._hal_says(f"not found {src}")
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

    def _find_orphans(self, entry: dict[str, str]) -> list[Path]:
        """Paths in this entry's backup destination that no longer exist in its source.

        An entry whose source is missing or empty yields nothing: there the backup is
        the only surviving copy, and every file in it would otherwise read as an orphan.
        """
        src = Path(self._expand_template(entry["src"]))
        dest = Path(self._expand_template(entry["dest"]))

        if "*" in str(src):
            src_names = {match.name for match in src.parent.glob(src.name)}
            if not src_names:
                return []
            return sorted(match for match in dest.parent.glob(dest.name) if match.name not in src_names)

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
            self._hal_says(f"kept {path}: {error.strerror}")
            return False
        return True

    def _prune(self) -> None:
        orphans: list[Path] = []
        for entry in self.dotfiles.data["backups"]:
            orphans.extend(self._find_orphans(entry))

        if not orphans:
            self._hal_says("nothing to prune")
            return

        orphans.sort()
        home = str(Path.home())
        counted = f"{len(orphans)} orphan" if len(orphans) == 1 else f"{len(orphans)} orphans"
        self._hal_says(f"{counted} in backup, absent from source:")
        for path in orphans:
            print(f"  {str(path).replace(home, '~', 1)}")

        try:
            answer = input(f"Delete {counted} from backup? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() != "y":
            self._hal_says("aborted")
            return

        removed = sum(self._remove_orphan(path) for path in sorted(orphans, reverse=True))
        self._hal_says(f"pruned {removed}")

    def sync(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures: list[concurrent.futures.Future[None]] = []
            futures.extend(executor.submit(self._sync_links, link, force=namespace.force) for link in self.dotfiles.data["links"])
            futures.extend(executor.submit(self._copy_entry, copy) for copy in self.dotfiles.data["copies"])
            for f in concurrent.futures.as_completed(futures):
                f.result()

    def backup(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._copy_entry, entry) for entry in self.dotfiles.data["backups"]]
            for f in concurrent.futures.as_completed(futures):
                f.result()

        if namespace.prune:
            self._prune()

    def restore(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        entries = self.dotfiles.data["backups"]
        if not entries:
            self._hal_says("nothing to restore")
            return

        for entry in entries:
            self._hal_says(f"{self._expand_template(entry['dest'])} -> {self._expand_template(entry['src'])}")

        try:
            answer = input("Overwrite local files with backups? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() != "y":
            self._hal_says("aborted")
            return

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._copy_entry, {"src": entry["dest"], "dest": entry["src"]}) for entry in entries]
            for f in concurrent.futures.as_completed(futures):
                f.result()

    def open_the_pod_bay_doors(self, namespace: argparse.Namespace, extra_args: list[str] | None = None) -> None:  # noqa: ARG002 unused-method-argument
        self._hal_says("I'm sorry Dave, I'm afraid I can't do that.")

        filepath = str(Path(Settings.REPO_ROOT) / "assets" / "im-sorry-dave-im-afraid-i-cant-do-that.mp3")
        self._run(f"afplay {shlex.quote(filepath)}", verbose=False)

    def read_lips(self) -> None:
        if len(sys.argv) == 1:
            self.parser.print_help()
            sys.exit(0)

        namespace, extra_args = self.parser.parse_known_args()

        if extra_args and namespace.func != self.update:
            self.parser.parse_args()  # Will error with usage message on unrecognized args

        namespace.func(namespace, extra_args)


if __name__ == "__main__":
    hal_9000 = HAL9000()
    hal_9000.read_lips()

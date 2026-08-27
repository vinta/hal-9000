import argparse
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDotfilesSave:
    """save() truncates the manifest, so it must build its payload first."""

    def test_save_before_any_read_preserves_manifest(self, hal_module, tmp_path):
        """Manifest data loads lazily, so saving an untouched Dotfiles must not lose it."""
        manifest = tmp_path / "hal_dotfiles.json"
        entries = {"backups": [], "copies": [], "links": [{"src": "a", "dest": "b"}]}
        manifest.write_text(json.dumps(entries))

        hal_module.Dotfiles(str(manifest)).save()

        assert json.loads(manifest.read_text()) == entries

    def test_save_after_read_preserves_manifest(self, hal_module, tmp_path):
        manifest = tmp_path / "hal_dotfiles.json"
        entries = {"backups": [], "copies": [], "links": [{"src": "a", "dest": "b"}]}
        manifest.write_text(json.dumps(entries))

        dotfiles = hal_module.Dotfiles(str(manifest))
        assert dotfiles.data == entries
        dotfiles.save()

        assert json.loads(manifest.read_text()) == entries


class TestValidatePath:
    def test_valid_path_under_home(self, hal_instance):
        home = str(Path.home())
        path = f"{home}/.zshrc"
        hal_instance._validate_path(path)

    def test_valid_path_under_repo_root(self, hal_instance, hal_module):
        path = f"{hal_module.Settings.REPO_ROOT}/dotfiles/.zshrc"
        hal_instance._validate_path(path)

    def test_path_traversal_outside_home(self, hal_instance):
        home = str(Path.home())
        path = f"{home}/../../etc/passwd"
        with pytest.raises(SystemExit):
            hal_instance._validate_path(path)

    def test_path_to_etc(self, hal_instance):
        with pytest.raises(SystemExit):
            hal_instance._validate_path("/etc/crontab")

    def test_path_traversal_in_template_expansion(self, hal_instance):
        with pytest.raises(SystemExit):
            hal_instance._expand_template("{{HOME}}/../../etc/crontab")

    def test_normal_template_expansion(self, hal_instance):
        result = hal_instance._expand_template("{{HOME}}/.zshrc")
        assert result == f"{Path.home()}/.zshrc"

    def test_sibling_directory_sharing_home_prefix(self, hal_instance, hal_module, tmp_path):
        """A sibling whose name merely starts with the home directory's name is not under it.

        Both roots are pinned under tmp_path because CI checks the repo out inside
        $HOME, where a real sibling of the repo root is legitimately under home.
        """
        home = (tmp_path / "home").resolve()
        with (
            patch("pathlib.Path.home", return_value=home),
            patch.object(hal_module.Settings, "REPO_ROOT", str((tmp_path / "repo").resolve())),
        ):
            hal_instance._validate_path(f"{home}/inside/stuff")
            with pytest.raises(SystemExit):
                hal_instance._validate_path(f"{home}-elsewhere/stuff")

    def test_sibling_directory_sharing_repo_root_prefix(self, hal_instance, hal_module, tmp_path):
        repo_root = (tmp_path / "repo").resolve()
        with (
            patch("pathlib.Path.home", return_value=(tmp_path / "home").resolve()),
            patch.object(hal_module.Settings, "REPO_ROOT", str(repo_root)),
        ):
            hal_instance._validate_path(f"{repo_root}/inside/stuff")
            with pytest.raises(SystemExit):
                hal_instance._validate_path(f"{repo_root}-elsewhere/stuff")

    def test_home_itself_is_valid(self, hal_instance):
        hal_instance._validate_path(str(Path.home()))


class TestUpdateSanitization:
    def test_extra_args_are_quoted(self, hal_instance):
        """extra_args with shell metacharacters must be quoted."""
        commands_run = []

        def mock_run(command, *, shell=True, verbose=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0

        def mock_run_with_output(command, *, shell=True, verbose=True, print_output=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0, b"/opt/homebrew/bin/ansible\n"

        hal_instance._run = mock_run
        hal_instance._run_with_output = mock_run_with_output

        ns = argparse.Namespace(func=hal_instance.update)
        hal_instance.update(ns, extra_args=["--tags", "foo;rm -rf ~"])

        ansible_cmd = next(c for c in commands_run if "ansible-playbook" in c)
        assert "'foo;rm -rf ~'" in ansible_cmd


class TestUpdateFailurePropagation:
    """update exits non-zero when git pull or the playbook run fails."""

    @staticmethod
    def _install_mocks(hal_instance, failing_command):
        def mock_run(command, *, shell=True, verbose=True):  # noqa: ARG001 unused-function-argument
            return 1 if failing_command in command else 0

        def mock_run_with_output(command, *, shell=True, verbose=True, print_output=True):  # noqa: ARG001 unused-function-argument
            return 0, b"/opt/homebrew/bin/ansible\n"

        hal_instance._run = mock_run
        hal_instance._run_with_output = mock_run_with_output

    def test_git_pull_failure_exits(self, hal_instance):
        self._install_mocks(hal_instance, "git pull")

        ns = argparse.Namespace(func=hal_instance.update)
        with pytest.raises(SystemExit) as excinfo:
            hal_instance.update(ns)

        assert excinfo.value.code == 1

    def test_playbook_failure_exits(self, hal_instance):
        self._install_mocks(hal_instance, "ansible-playbook")

        ns = argparse.Namespace(func=hal_instance.update)
        with pytest.raises(SystemExit) as excinfo:
            hal_instance.update(ns)

        assert excinfo.value.code == 1


class TestUserFilenameValidation:
    def test_link_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.link(ns)

    def test_copy_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.copy(ns)


class TestUnlink:
    """unlink reverses a link entry, whether the entry names a file or a directory."""

    @staticmethod
    def _link_entry(hal_instance, hal_module, tmp_path, entry):
        """Point the manifest at a temp file and register one link entry as templates."""
        hal_instance.dotfiles = hal_module.Dotfiles(str(tmp_path / "hal_dotfiles.json"))
        hal_instance.dotfiles.data["links"].append(entry)

    def test_moves_directory_back_to_dest(self, hal_instance, hal_module, tmp_path):
        """A directory entry is restored whole, which shutil.copy2 could never do."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "rules"
        dest.symlink_to(src)

        self._link_entry(hal_instance, hal_module, tmp_path, {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/rules/"})

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename=str(dest)))

        assert dest.is_dir()
        assert not dest.is_symlink()
        assert (dest / "managed.md").read_text() == "from repo"
        assert not src.exists()
        assert hal_instance.dotfiles.data["links"] == []

    def test_moves_file_back_to_dest(self, hal_instance, hal_module, tmp_path):
        """The single-file case the old copy2 handled keeps working under shutil.move."""
        src = tmp_path / "dotfiles" / ".zshrc"
        src.parent.mkdir(parents=True)
        src.write_text("from repo")

        dest = tmp_path / ".zshrc"
        dest.symlink_to(src)

        self._link_entry(hal_instance, hal_module, tmp_path, {"src": "{{HOME}}/dotfiles/.zshrc", "dest": "{{HOME}}/.zshrc"})

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename=str(dest)))

        assert not dest.is_symlink()
        assert dest.read_text() == "from repo"
        assert not src.exists()
        assert hal_instance.dotfiles.data["links"] == []

    def test_refuses_to_replace_real_directory(self, hal_instance, hal_module, tmp_path):
        """A real directory at dest is what sync refused to link, so unlink leaves it alone."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "rules"
        dest.mkdir()
        (dest / "unmanaged.md").write_text("preserve me")

        entry = {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/rules/"}
        self._link_entry(hal_instance, hal_module, tmp_path, entry)

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename=str(dest)))

        assert sorted(p.name for p in dest.iterdir()) == ["unmanaged.md"]
        assert (src / "managed.md").read_text() == "from repo"
        assert hal_instance.dotfiles.data["links"] == [entry]

    def test_matches_entry_dest_with_trailing_slash(self, hal_instance, hal_module, tmp_path):
        """Directory entries are hand-written with a trailing slash the typed path never has."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "rules"
        dest.symlink_to(src)

        self._link_entry(hal_instance, hal_module, tmp_path, {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/rules/"})

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename=str(tmp_path / "rules")))

        assert hal_instance.dotfiles.data["links"] == []

    def test_matches_entry_from_relative_filename(self, hal_instance, hal_module, tmp_path, monkeypatch):
        """A bare name is resolved against the current directory, not against the home directory."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "sub" / "rules"
        dest.parent.mkdir()
        dest.symlink_to(src)

        self._link_entry(hal_instance, hal_module, tmp_path, {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/sub/rules"})

        monkeypatch.chdir(dest.parent)
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename="rules"))

        assert hal_instance.dotfiles.data["links"] == []

    def test_matches_entry_from_tilde_filename(self, hal_instance, hal_module, tmp_path, monkeypatch):
        """A quoted ~/ reaches hal unexpanded, since the shell never saw it."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "rules"
        dest.symlink_to(src)

        self._link_entry(hal_instance, hal_module, tmp_path, {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/rules/"})

        monkeypatch.setenv("HOME", str(tmp_path))
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename="~/rules/"))

        assert hal_instance.dotfiles.data["links"] == []

    def test_reports_path_no_entry_covers(self, hal_instance, hal_module, tmp_path, capsys):
        """A path outside the manifest leaves both the manifest and the filesystem alone."""
        src = tmp_path / "dotfiles" / "rules"
        src.mkdir(parents=True)
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "rules"
        dest.symlink_to(src)

        entry = {"src": "{{HOME}}/dotfiles/rules/", "dest": "{{HOME}}/rules/"}
        self._link_entry(hal_instance, hal_module, tmp_path, entry)

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t.replace("{{HOME}}", str(tmp_path))):
            hal_instance.unlink(argparse.Namespace(filename=str(tmp_path / "unmanaged")))

        assert "not found in manifest:" in capsys.readouterr().out
        assert hal_instance.dotfiles.data["links"] == [entry]
        assert dest.is_symlink()
        assert (src / "managed.md").read_text() == "from repo"


class TestSyncLinks:
    """_sync_links never destroys a real directory unless forced."""

    def test_refuses_to_replace_real_directory(self, hal_instance, tmp_path):
        """A real directory at dest is left alone, so unmanaged files survive."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "unmanaged.md").write_text("preserve me")

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._sync_links({"src": str(src), "dest": str(dest)})

        assert not dest.is_symlink()
        assert (dest / "unmanaged.md").read_text() == "preserve me"

    def test_force_replaces_real_directory(self, hal_instance, tmp_path):
        """--force is the explicit opt-in to discard the directory and link."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "managed.md").write_text("from repo")

        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "unmanaged.md").write_text("discard me")

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._sync_links({"src": str(src), "dest": str(dest)}, force=True)

        assert dest.is_symlink()
        assert dest.resolve() == src.resolve()

    def test_replaces_real_file_without_force(self, hal_instance, tmp_path):
        """A single file at dest is still adopted, which is how a fresh machine links up."""
        src = tmp_path / "src.txt"
        src.write_text("from repo")

        dest = tmp_path / "dest.txt"
        dest.write_text("pre-existing")

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._sync_links({"src": str(src), "dest": str(dest)})

        assert dest.is_symlink()
        assert dest.read_text() == "from repo"

    def test_relinks_existing_symlink_without_force(self, hal_instance, tmp_path):
        """A stale symlink at dest is repointed, since nothing is destroyed."""
        src = tmp_path / "src"
        src.mkdir()

        stale = tmp_path / "stale"
        stale.mkdir()

        dest = tmp_path / "dest"
        dest.symlink_to(stale)

        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._sync_links({"src": str(src), "dest": str(dest)})

        assert dest.is_symlink()
        assert dest.resolve() == src.resolve()


class TestCopyEntryMerge:
    """_copy_entry merges directories instead of replacing them."""

    def test_preserves_dest_only_files(self, hal_instance, tmp_path):
        """Files in dest that don't exist in src survive the sync."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "from_src.txt").write_text("source content")

        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "dest_only.txt").write_text("preserve me")

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "from_src.txt").read_text() == "source content"
        assert (dest / "dest_only.txt").read_text() == "preserve me"

    def test_overwrites_matching_files(self, hal_instance, tmp_path):
        """Files present in both src and dest get overwritten by src."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "shared.txt").write_text("updated")

        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "shared.txt").write_text("old")

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "shared.txt").read_text() == "updated"

    def test_merges_nested_directories(self, hal_instance, tmp_path):
        """Nested subdirectories are merged, not replaced."""
        src = tmp_path / "src" / "sub"
        src.mkdir(parents=True)
        (src / "new.txt").write_text("new")

        dest = tmp_path / "dest" / "sub"
        dest.mkdir(parents=True)
        (dest / "existing.txt").write_text("keep")

        copy_entry = {"src": str(tmp_path / "src"), "dest": str(tmp_path / "dest")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (tmp_path / "dest" / "sub" / "new.txt").read_text() == "new"
        assert (tmp_path / "dest" / "sub" / "existing.txt").read_text() == "keep"

    def test_creates_dest_if_missing(self, hal_instance, tmp_path):
        """Copies work when the dest directory doesn't exist yet."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "file.txt").write_text("content")

        dest = tmp_path / "dest"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "file.txt").read_text() == "content"

    def test_single_file_copy_still_overwrites(self, hal_instance, tmp_path):
        """Non-directory copies still do a straight overwrite."""
        src = tmp_path / "src.txt"
        src.write_text("new content")

        dest = tmp_path / "dest.txt"
        dest.write_text("old content")

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest.read_text() == "new content"

    def test_skips_ignored_single_file(self, hal_instance, tmp_path):
        """Ignore patterns apply to single-file copies, not just directory trees."""
        src = tmp_path / ".DS_Store"
        src.write_text("junk")
        dest = tmp_path / "dest" / ".DS_Store"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert not dest.exists()

    def test_skips_ignored_glob_match(self, hal_instance, tmp_path):
        """Ignore patterns apply to files matched by a glob entry."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "keep.log").write_text("keep")
        (src / ".DS_Store").write_text("junk")

        dest = tmp_path / "dest"
        dest.mkdir()

        copy_entry = {"src": str(src / "*"), "dest": str(dest / "*")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "keep.log").read_text() == "keep"
        assert not (dest / ".DS_Store").exists()

    def test_patterns_are_glob_matched(self, hal_instance, hal_module, tmp_path):
        """Patterns are globs, not literal names."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "notes.tmp").write_text("scratch")
        (src / "real.txt").write_text("content")

        dest = tmp_path / "dest"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_module.Settings, "IGNORE_PATTERNS", ("*.tmp",)),
        ):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "real.txt").read_text() == "content"
        assert not (dest / "notes.tmp").exists()

    def test_skips_ds_store(self, hal_instance, tmp_path):
        """.DS_Store files in src are not copied to dest."""
        src = tmp_path / "src"
        src.mkdir()
        (src / ".DS_Store").write_text("junk")
        (src / "real.txt").write_text("content")

        dest = tmp_path / "dest"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "real.txt").exists()
        assert not (dest / ".DS_Store").exists()

    def test_overwrites_readonly_dest_file(self, hal_instance, tmp_path):
        """Re-running a copy overwrites read-only dest files (e.g. git objects)."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "object").write_text("new content")

        dest = tmp_path / "dest"
        dest.mkdir()
        dest_file = dest / "object"
        dest_file.write_text("old content")
        dest_file.chmod(0o444)

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest_file.read_text() == "new content"

    def test_overwrites_readonly_single_file(self, hal_instance, tmp_path):
        """A single-file copy overwrites a read-only dest file, like the directory branch does."""
        src = tmp_path / "src.txt"
        src.write_text("new content")

        dest = tmp_path / "dest.txt"
        dest.write_text("old")
        dest.chmod(0o444)

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest.read_text() == "new content"

    def test_skips_pycache_directory(self, hal_instance, tmp_path):
        """__pycache__ directories in src are not copied to dest."""
        src = tmp_path / "src"
        (src / "__pycache__").mkdir(parents=True)
        (src / "__pycache__" / "mod.pyc").write_text("junk")
        (src / "real.txt").write_text("content")

        dest = tmp_path / "dest"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "real.txt").exists()
        assert not (dest / "__pycache__").exists()

    def test_skips_node_modules_directory(self, hal_instance, tmp_path):
        """node_modules directories in src are not copied to dest."""
        src = tmp_path / "src"
        (src / "node_modules").mkdir(parents=True)
        (src / "node_modules" / "pkg.js").write_text("junk")
        (src / "real.txt").write_text("content")

        dest = tmp_path / "dest"

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "real.txt").exists()
        assert not (dest / "node_modules").exists()


class TestSkipUnchanged:
    """Files whose size and mtime already match at dest are not rewritten (avoids Dropbox re-sync churn)."""

    @staticmethod
    def _match_mtime(src, dest):
        os.utime(dest, ns=(src.stat().st_atime_ns, src.stat().st_mtime_ns))

    def test_skips_single_file_when_size_and_mtime_match(self, hal_instance, tmp_path):
        """Same size + mtime means no rewrite, proven by dest keeping different content."""
        src = tmp_path / "src.txt"
        src.write_text("AAAA")
        dest = tmp_path / "dest.txt"
        dest.write_text("BBBB")
        self._match_mtime(src, dest)

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest.read_text() == "BBBB"

    def test_copies_when_mtime_differs(self, hal_instance, tmp_path):
        """Same size but different mtime still copies."""
        src = tmp_path / "src.txt"
        src.write_text("AAAA")
        dest = tmp_path / "dest.txt"
        dest.write_text("BBBB")
        os.utime(dest, ns=(src.stat().st_atime_ns, src.stat().st_mtime_ns + 1_000_000_000))

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest.read_text() == "AAAA"

    def test_copies_when_size_differs(self, hal_instance, tmp_path):
        """Same mtime but different size still copies."""
        src = tmp_path / "src.txt"
        src.write_text("AAAA")
        dest = tmp_path / "dest.txt"
        dest.write_text("BB")
        self._match_mtime(src, dest)

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest.read_text() == "AAAA"

    def test_skips_unchanged_files_inside_directory(self, hal_instance, tmp_path):
        """Directory copies skip unchanged files but still copy changed ones."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "same.txt").write_text("AAAA")
        (src / "changed.txt").write_text("new content")

        dest = tmp_path / "dest"
        dest.mkdir()
        (dest / "same.txt").write_text("BBBB")
        self._match_mtime(src / "same.txt", dest / "same.txt")
        (dest / "changed.txt").write_text("old content")

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert (dest / "same.txt").read_text() == "BBBB"
        assert (dest / "changed.txt").read_text() == "new content"

    def test_skips_readonly_unchanged_file_without_chmod(self, hal_instance, tmp_path):
        """Unchanged read-only files (e.g. git objects) are left alone, mode intact."""
        src = tmp_path / "src"
        src.mkdir()
        (src / "object").write_text("AAAA")

        dest = tmp_path / "dest"
        dest.mkdir()
        dest_file = dest / "object"
        dest_file.write_text("BBBB")
        self._match_mtime(src / "object", dest_file)
        dest_file.chmod(0o444)

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(copy_entry)

        assert dest_file.read_text() == "BBBB"
        assert dest_file.stat().st_mode & 0o777 == 0o444


class TestCopyEntryGlob:
    """_copy_entry expands a single `*`, copying each match with the star spliced into dest."""

    def test_pattern_copies_each_match(self, hal_instance, tmp_path):
        """Each file matching the src pattern is copied; non-matching files are left alone."""
        src_dir = tmp_path / "projects"
        src_dir.mkdir()
        (src_dir / "acme.code-workspace").write_text("acme")
        (src_dir / "beta.code-workspace").write_text("beta")
        (src_dir / "notes.txt").write_text("ignore me")

        dest_dir = tmp_path / "dropbox"

        entry = {"src": str(src_dir / "*.code-workspace"), "dest": str(dest_dir / "*.code-workspace")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(entry)

        assert (dest_dir / "acme.code-workspace").read_text() == "acme"
        assert (dest_dir / "beta.code-workspace").read_text() == "beta"
        assert not (dest_dir / "notes.txt").exists()

    def test_pattern_no_matches_is_noop(self, hal_instance, tmp_path):
        """A pattern that matches nothing copies nothing and does not create the dest."""
        src_dir = tmp_path / "projects"
        src_dir.mkdir()
        dest_dir = tmp_path / "dropbox"

        entry = {"src": str(src_dir / "*.code-workspace"), "dest": str(dest_dir / "*.code-workspace")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(entry)

        assert not dest_dir.exists()

    def test_pattern_restore_reverses(self, hal_instance, tmp_path):
        """Swapping src/dest (as restore does) globs the dest side and writes back symmetrically."""
        backup_dir = tmp_path / "dropbox"
        backup_dir.mkdir()
        (backup_dir / "acme.code-workspace").write_text("backed up")

        local_dir = tmp_path / "projects"

        swapped = {"src": str(backup_dir / "*.code-workspace"), "dest": str(local_dir / "*.code-workspace")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(swapped)

        assert (local_dir / "acme.code-workspace").read_text() == "backed up"


class TestBackupRestore:
    """backup copies src->dest, restore copies dest->src after confirmation."""

    def test_backup_copies_entries(self, hal_instance, tmp_path):
        src = tmp_path / "live.txt"
        src.write_text("live data")
        dest = tmp_path / "dropbox" / "live.txt"

        entry = {"src": str(src), "dest": str(dest)}
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.backup(argparse.Namespace(prune=False))

        assert dest.read_text() == "live data"

    def test_backup_preserves_dest_only_files(self, hal_instance, tmp_path):
        """Backup is additive: files already in the backup destination survive."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "deleted_long_ago.txt").write_text("keep me")

        entry = {"src": str(src), "dest": str(dest)}
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.backup(argparse.Namespace(prune=False))

        assert (dest / "current.txt").read_text() == "current"
        assert (dest / "deleted_long_ago.txt").read_text() == "keep me"

    def test_restore_reverses_direction(self, hal_instance, tmp_path, monkeypatch):
        """Restore copies dest->src, creating missing parent directories."""
        backup_file = tmp_path / "dropbox" / "live.txt"
        backup_file.parent.mkdir()
        backup_file.write_text("backup data")
        local = tmp_path / "fresh" / "live.txt"

        entry = {"src": str(local), "dest": str(backup_file)}
        monkeypatch.setattr("builtins.input", lambda _: "y")
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.restore(argparse.Namespace())

        assert local.read_text() == "backup data"

    def test_restore_overwrites_existing_local(self, hal_instance, tmp_path, monkeypatch):
        backup_file = tmp_path / "dropbox" / "live.txt"
        backup_file.parent.mkdir()
        backup_file.write_text("backup data")
        local = tmp_path / "live.txt"
        local.write_text("corrupted")

        entry = {"src": str(local), "dest": str(backup_file)}
        monkeypatch.setattr("builtins.input", lambda _: "y")
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.restore(argparse.Namespace())

        assert local.read_text() == "backup data"

    def test_restore_aborts_without_confirmation(self, hal_instance, tmp_path, monkeypatch):
        backup_file = tmp_path / "dropbox" / "live.txt"
        backup_file.parent.mkdir()
        backup_file.write_text("backup data")
        local = tmp_path / "live.txt"
        local.write_text("untouched")

        entry = {"src": str(local), "dest": str(backup_file)}
        monkeypatch.setattr("builtins.input", lambda _: "")
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.restore(argparse.Namespace())

        assert local.read_text() == "untouched"

    def test_restore_aborts_on_eof(self, hal_instance, tmp_path, monkeypatch):
        """Non-interactive restore (no tty) defaults to abort."""
        backup_file = tmp_path / "dropbox" / "live.txt"
        backup_file.parent.mkdir()
        backup_file.write_text("backup data")
        local = tmp_path / "live.txt"
        local.write_text("untouched")

        def raise_eof(_prompt):
            raise EOFError

        entry = {"src": str(local), "dest": str(backup_file)}
        monkeypatch.setattr("builtins.input", raise_eof)
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [entry]}
            hal_instance.restore(argparse.Namespace())

        assert local.read_text() == "untouched"

    def test_sync_ignores_backups(self, hal_instance, tmp_path):
        """sync only processes links and copies, never backup entries."""
        src = tmp_path / "live.txt"
        src.write_text("live data")
        dest = tmp_path / "dropbox" / "live.txt"

        entry = {"src": str(src), "dest": str(dest)}
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"links": [], "copies": [], "backups": [entry]}
            hal_instance.sync(argparse.Namespace())

        assert not dest.exists()

    def test_messages_abbreviate_the_home_directory(self, hal_instance, tmp_path, capsys):
        """A copy line names both paths, so a prefix-only abbreviation would shorten just the first."""
        home = tmp_path / "home"
        src = home / "live.txt"
        src.parent.mkdir()
        src.write_text("live data")
        dest = home / "dropbox" / "live.txt"

        with (
            patch("pathlib.Path.home", return_value=home),
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [{"src": str(src), "dest": str(dest)}]}
            hal_instance.backup(argparse.Namespace(prune=False))

        out = capsys.readouterr().out
        assert "HAL: copy ~/live.txt -> ~/dropbox/live.txt" in out
        assert str(home) not in out


class TestBackupPrune:
    """--prune deletes files that exist only in the backup destination."""

    @staticmethod
    def _prune(hal_instance, entries, answer="y"):
        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("builtins.input", return_value=answer),
        ):
            mock_dotfiles.data = {"backups": entries}
            hal_instance.backup(argparse.Namespace(prune=True))

    def test_deletes_orphans_after_confirmation(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "current.txt").write_text("current")
        (dest / "deleted_long_ago.txt").write_text("orphan")
        (dest / "gone").mkdir()
        (dest / "gone" / "nested.txt").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "current.txt").read_text() == "current"
        assert not (dest / "deleted_long_ago.txt").exists()
        assert not (dest / "gone").exists()

    def test_declining_keeps_everything(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "orphan.txt").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}], answer="")

        assert (dest / "orphan.txt").read_text() == "orphan"

    def test_backup_without_prune_deletes_nothing(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "orphan.txt").write_text("orphan")

        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
        ):
            mock_dotfiles.data = {"backups": [{"src": str(src), "dest": str(dest)}]}
            hal_instance.backup(argparse.Namespace(prune=False))

        assert (dest / "orphan.txt").read_text() == "orphan"

    def test_missing_source_is_skipped(self, hal_instance, tmp_path):
        """A source that no longer exists must not turn its whole backup into orphans."""
        src = tmp_path / "unmounted"

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "only_copy.txt").write_text("irreplaceable")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "only_copy.txt").read_text() == "irreplaceable"

    def test_source_holding_only_ignored_files_is_skipped(self, hal_instance, tmp_path):
        """A source that walks to nothing once ignores are applied counts as empty, not as fully deleted."""
        src = tmp_path / "live"
        src.mkdir()
        (src / ".DS_Store").write_text("finder")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "only_copy.txt").write_text("irreplaceable")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "only_copy.txt").read_text() == "irreplaceable"

    def test_git_internals_are_never_pruned(self, hal_instance, tmp_path):
        """Objects git reclaimed locally stay in the backup instead of dominating the listing."""
        src = tmp_path / "live"
        (src / ".git" / "objects").mkdir(parents=True)
        (src / "README.md").write_text("readme")

        dest = tmp_path / "dropbox"
        (dest / ".git" / "objects").mkdir(parents=True)
        (dest / ".git" / "objects" / "stale").write_text("superseded")
        (dest / "README.md").write_text("readme")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / ".git" / "objects" / "stale").read_text() == "superseded"

    def test_orphan_directory_holding_ignored_files_is_removed(self, hal_instance, tmp_path):
        """.DS_Store is filtered out of the diff, so rmdir would fail on a directory still holding one."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "current.txt").write_text("current")
        (dest / "gone").mkdir()
        (dest / "gone" / ".DS_Store").write_text("finder")
        (dest / "gone" / "cached").mkdir()
        (dest / "gone" / "cached" / "__pycache__").mkdir()

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert not (dest / "gone").exists()

    def test_opted_out_entry_reports_its_expanded_destination(self, hal_instance, tmp_path, capsys):
        """The manifest stores a {{HOME}} template, which is not a path the reader can act on."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "archived.txt").write_text("only copy left")

        # Real _expand_template, so the template is genuinely expanded; only its
        # under-home guard is neutralised, since tmp_path is outside both allowed roots
        with (
            patch.object(hal_instance, "_validate_path"),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("builtins.input", return_value=""),
        ):
            mock_dotfiles.data = {"backups": [{"src": "{{HOME}}/hal-prune-test-absent", "dest": str(dest), "prune": False}]}
            hal_instance.backup(argparse.Namespace(prune=True))

        assert f"prune disabled {dest}" in capsys.readouterr().out

    def test_entry_can_opt_out_of_pruning(self, hal_instance, tmp_path):
        """A backup whose destination outlives its source keeps its orphans."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "archived.txt").write_text("only copy left")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest), "prune": False}], answer="y")

        assert (dest / "archived.txt").read_text() == "only copy left"

    def test_opting_one_entry_out_leaves_the_others(self, hal_instance, tmp_path):
        kept_src = tmp_path / "kept_live"
        kept_src.mkdir()
        (kept_src / "current.txt").write_text("current")
        kept_dest = tmp_path / "kept_dropbox"
        kept_dest.mkdir()
        (kept_dest / "archived.txt").write_text("only copy left")

        pruned_src = tmp_path / "pruned_live"
        pruned_src.mkdir()
        (pruned_src / "current.txt").write_text("current")
        pruned_dest = tmp_path / "pruned_dropbox"
        pruned_dest.mkdir()
        (pruned_dest / "orphan.txt").write_text("orphan")

        entries = [
            {"src": str(kept_src), "dest": str(kept_dest), "prune": False},
            {"src": str(pruned_src), "dest": str(pruned_dest)},
        ]
        self._prune(hal_instance, entries)

        assert (kept_dest / "archived.txt").read_text() == "only copy left"
        assert not (pruned_dest / "orphan.txt").exists()

    def test_prune_true_is_the_same_as_omitting_it(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "orphan.txt").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest), "prune": True}])

        assert not (dest / "orphan.txt").exists()

    def test_symlinked_source_directory_is_followed(self, hal_instance, tmp_path):
        """copytree dereferences source symlinks, so the backup holds real files that must not read as orphans."""
        src = tmp_path / "live"
        (src / "real" / "skill").mkdir(parents=True)
        (src / "real" / "skill" / "SKILL.md").write_text("skill")
        (src / "linked").symlink_to(src / "real")

        dest = tmp_path / "dropbox"
        (dest / "real" / "skill").mkdir(parents=True)
        (dest / "real" / "skill" / "SKILL.md").write_text("skill")
        (dest / "linked" / "skill").mkdir(parents=True)
        (dest / "linked" / "skill" / "SKILL.md").write_text("skill")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "linked" / "skill" / "SKILL.md").read_text() == "skill"

    def test_file_deleted_behind_a_symlinked_source_directory_is_an_orphan(self, hal_instance, tmp_path):
        """Following the symlink must still surface what was deleted on the other side of it."""
        src = tmp_path / "live"
        (src / "real").mkdir(parents=True)
        (src / "real" / "kept.md").write_text("kept")
        (src / "linked").symlink_to(src / "real")

        dest = tmp_path / "dropbox"
        (dest / "real").mkdir(parents=True)
        (dest / "real" / "kept.md").write_text("kept")
        (dest / "linked").mkdir()
        (dest / "linked" / "kept.md").write_text("kept")
        (dest / "linked" / "removed.md").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "linked" / "kept.md").read_text() == "kept"
        assert not (dest / "linked" / "removed.md").exists()

    def test_symlink_loop_in_source_terminates(self, hal_instance, tmp_path):
        """A source symlink pointing at its own ancestor must not walk forever.

        Diffing only, not through backup(): shutil.copytree follows the loop until the
        filesystem stops it, so a source shaped like this breaks `hal backup` on its own.
        """
        src = tmp_path / "live"
        (src / "nested").mkdir(parents=True)
        (src / "nested" / "current.txt").write_text("current")
        (src / "nested" / "loop").symlink_to(src)

        dest = tmp_path / "dropbox"
        (dest / "nested").mkdir(parents=True)
        (dest / "nested" / "current.txt").write_text("current")
        (dest / "orphan.txt").write_text("orphan")

        entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            orphans = hal_instance._find_orphans(entry)

        assert orphans == [dest / "orphan.txt"]

    def test_symlinked_destination_directory_is_not_followed(self, hal_instance, tmp_path):
        """Descending a destination symlink would delete through it, outside the backup."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        outside = tmp_path / "outside"
        outside.mkdir()
        (outside / "unrelated.txt").write_text("not part of any backup")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "current.txt").write_text("current")
        (dest / "link").symlink_to(outside)

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert not (dest / "link").exists()
        assert (outside / "unrelated.txt").read_text() == "not part of any backup"

    def test_undeletable_directory_is_kept_and_prune_continues(self, hal_instance, tmp_path):
        """A directory holding something the listing never accounted for survives, and later orphans still go."""
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "current.txt").write_text("current")
        (dest / "abandoned_repo").mkdir()
        (dest / "abandoned_repo" / ".git").mkdir()
        (dest / "zz_orphan.txt").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert (dest / "abandoned_repo" / ".git").is_dir()
        assert not (dest / "zz_orphan.txt").exists()

    def test_symlink_orphan_is_unlinked_without_touching_target(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        target = tmp_path / "target"
        target.mkdir()
        (target / "keep.txt").write_text("keep")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "current.txt").write_text("current")
        (dest / "link").symlink_to(target)

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}])

        assert not (dest / "link").exists()
        assert (target / "keep.txt").read_text() == "keep"

    def test_glob_entry_prunes_unmatched_files(self, hal_instance, tmp_path):
        src_dir = tmp_path / "projects"
        src_dir.mkdir()
        (src_dir / "acme.code-workspace").write_text("acme")

        dest_dir = tmp_path / "dropbox"
        dest_dir.mkdir()
        (dest_dir / "acme.code-workspace").write_text("acme")
        (dest_dir / "renamed.code-workspace").write_text("orphan")
        (dest_dir / "notes.txt").write_text("not covered by the pattern")

        entry = {"src": str(src_dir / "*.code-workspace"), "dest": str(dest_dir / "*.code-workspace")}
        self._prune(hal_instance, [entry])

        assert (dest_dir / "acme.code-workspace").read_text() == "acme"
        assert not (dest_dir / "renamed.code-workspace").exists()
        assert (dest_dir / "notes.txt").exists()

    def test_glob_entry_with_no_source_matches_is_skipped(self, hal_instance, tmp_path):
        src_dir = tmp_path / "projects"
        src_dir.mkdir()

        dest_dir = tmp_path / "dropbox"
        dest_dir.mkdir()
        (dest_dir / "only_copy.code-workspace").write_text("irreplaceable")

        entry = {"src": str(src_dir / "*.code-workspace"), "dest": str(dest_dir / "*.code-workspace")}
        self._prune(hal_instance, [entry])

        assert (dest_dir / "only_copy.code-workspace").read_text() == "irreplaceable"

    def test_glob_entry_with_renaming_pattern_keeps_what_it_just_copied(self, hal_instance, tmp_path):
        """Copying splices the star into dest, so pruning must expect the spliced name, not the source name."""
        src_dir = tmp_path / "projects"
        src_dir.mkdir()
        (src_dir / "foo-1.log").write_text("one")

        dest_dir = tmp_path / "dropbox"
        dest_dir.mkdir()

        entry = {"src": str(src_dir / "foo-*.log"), "dest": str(dest_dir / "bar-*.log")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(entry)
            orphans = hal_instance._find_orphans(entry)

        assert (dest_dir / "bar-1.log").read_text() == "one"
        assert orphans == []

    def test_glob_entry_with_renaming_pattern_still_reports_unmatched_files(self, hal_instance, tmp_path):
        """A dest file whose star segment no longer has a source match is an orphan under a renaming pair."""
        src_dir = tmp_path / "projects"
        src_dir.mkdir()
        (src_dir / "foo-1.log").write_text("one")

        dest_dir = tmp_path / "dropbox"
        dest_dir.mkdir()
        (dest_dir / "bar-9.log").write_text("orphan")

        entry = {"src": str(src_dir / "foo-*.log"), "dest": str(dest_dir / "bar-*.log")}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._copy_entry(entry)
            orphans = hal_instance._find_orphans(entry)

        assert orphans == [dest_dir / "bar-9.log"]

    def test_no_orphans_skips_the_prompt(self, hal_instance, tmp_path):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()

        def fail_if_called(_prompt):
            pytest.fail("prompted with nothing to prune")

        with (
            patch.object(hal_instance, "_expand_template", side_effect=lambda t: t),
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("builtins.input", side_effect=fail_if_called),
        ):
            mock_dotfiles.data = {"backups": [{"src": str(src), "dest": str(dest)}]}
            hal_instance.backup(argparse.Namespace(prune=True))

    def test_listing_precedes_the_prompt(self, hal_instance, tmp_path, capsys):
        src = tmp_path / "live"
        src.mkdir()
        (src / "current.txt").write_text("current")

        dest = tmp_path / "dropbox"
        dest.mkdir()
        (dest / "orphan.txt").write_text("orphan")

        self._prune(hal_instance, [{"src": str(src), "dest": str(dest)}], answer="")

        out = capsys.readouterr().out
        assert "1 orphan in backup, absent from source:" in out
        assert str(dest / "orphan.txt") in out


class TestArgParsing:
    def test_unknown_args_rejected_for_link(self, hal_module):
        """Non-update commands should reject unknown arguments."""
        sys.argv = ["hal", "link", "--bogus", "somefile"]
        hal = hal_module.HAL9000()
        with pytest.raises(SystemExit) as exc_info:
            hal.read_lips()
        assert exc_info.value.code == 2

    def test_unknown_args_rejected_for_sync(self, hal_module):
        """sync should also reject unknown arguments."""
        sys.argv = ["hal", "sync", "--unknown"]
        hal = hal_module.HAL9000()
        with pytest.raises(SystemExit) as exc_info:
            hal.read_lips()
        assert exc_info.value.code == 2

    def test_prune_rejected_for_restore(self, hal_module):
        """--prune belongs to backup only; restore must not silently accept it."""
        sys.argv = ["hal", "restore", "--prune"]
        hal = hal_module.HAL9000()
        with pytest.raises(SystemExit) as exc_info:
            hal.read_lips()
        assert exc_info.value.code == 2


class TestManifestRoundTrip:
    def test_prune_field_survives_save(self, hal_module, tmp_path):
        """save() rebuilds entries from ENTRY_KEY_ORDER, so an unlisted key would be dropped by any `hal link`."""
        manifest = tmp_path / "hal_dotfiles.json"
        entries = {"backups": [{"src": "a", "dest": "b", "prune": False}], "copies": [], "links": []}
        manifest.write_text(json.dumps(entries))

        dotfiles = hal_module.Dotfiles(str(manifest))
        _ = dotfiles.data
        dotfiles.save()

        assert json.loads(manifest.read_text())["backups"][0] == {"src": "a", "dest": "b", "prune": False}

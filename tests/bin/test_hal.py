import argparse
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


class TestValidatePath:
    def test_valid_path_under_home(self, hal_instance):
        home = str(Path.home())
        path = f"{home}/.zshrc"
        hal_instance._validate_path(path)

    def test_valid_path_under_repo_root(self, hal_instance, hal_module):
        path = f"{hal_module.Setting.REPO_ROOT}/dotfiles/.zshrc"
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

    def test_sibling_directory_sharing_home_prefix(self, hal_instance):
        """A sibling whose name merely starts with the home directory's name is not under it."""
        home = Path.home()
        with pytest.raises(SystemExit):
            hal_instance._validate_path(f"{home.parent}/{home.name}-elsewhere/stuff")

    def test_sibling_directory_sharing_repo_root_prefix(self, hal_instance, hal_module):
        repo_root = Path(hal_module.Setting.REPO_ROOT)
        with pytest.raises(SystemExit):
            hal_instance._validate_path(f"{repo_root.parent}/{repo_root.name}-elsewhere/stuff")

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
            hal_instance.backup(argparse.Namespace())

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
            hal_instance.backup(argparse.Namespace())

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

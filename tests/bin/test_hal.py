import argparse
import shlex
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
        # The dangerous string must be quoted -- bare ;rm should not appear
        assert ";rm" not in ansible_cmd or shlex.quote("foo;rm -rf ~") in ansible_cmd


class TestFileOpsUseStdlib:
    """Verify link() and copy() don't shell out for mkdir/mv/cp."""

    def test_link_no_shell_mkdir(self, hal_instance, tmp_path):
        """link() should use Path.mkdir() not shell mkdir."""
        commands_run = []
        original_run = hal_instance._run

        def tracking_run(command, *, shell=True, verbose=True):
            commands_run.append(command)
            return original_run(command, shell=shell, verbose=verbose)

        hal_instance._run = tracking_run

        test_file = tmp_path / "testfile"
        test_file.write_text("content")

        ns = argparse.Namespace(filename=str(test_file))

        with (
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch.object(hal_instance, "_validate_path"),
            patch("shutil.move"),
        ):
            mock_dotfiles.find_by_key.return_value = None
            mock_dotfiles.data = {"links": [], "copies": []}
            hal_instance.link(ns)

        mkdir_cmds = [c for c in commands_run if c.startswith("mkdir ")]
        assert len(mkdir_cmds) == 0, f"Should not shell out to mkdir: {mkdir_cmds}"
        mv_cmds = [c for c in commands_run if c.startswith("mv ")]
        assert len(mv_cmds) == 0, f"Should not shell out to mv: {mv_cmds}"

    def test_copy_no_shell_cp(self, hal_instance, tmp_path):
        """copy() should use shutil.copy2() not shell cp."""
        commands_run = []

        def tracking_run(command, *, shell=True, verbose=True):  # noqa: ARG001 unused-function-argument
            commands_run.append(command)
            return 0

        hal_instance._run = tracking_run

        test_file = tmp_path / "testfile"
        test_file.write_text("content")

        ns = argparse.Namespace(filename=str(test_file))

        with (
            patch.object(hal_instance, "dotfiles") as mock_dotfiles,
            patch("pathlib.Path.cwd", return_value=tmp_path),
            patch.object(hal_instance, "_validate_path"),
            patch("shutil.copy2"),
        ):
            mock_dotfiles.find_by_key.return_value = None
            mock_dotfiles.data = {"links": [], "copies": []}
            hal_instance.copy(ns)

        cp_cmds = [c for c in commands_run if c.startswith("cp ")]
        assert len(cp_cmds) == 0, f"Should not shell out to cp: {cp_cmds}"


class TestUserFilenameValidation:
    def test_link_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.link(ns)

    def test_copy_validates_filename(self, hal_instance, tmp_path):
        ns = argparse.Namespace(filename="../../../etc/passwd")
        with patch("pathlib.Path.cwd", return_value=tmp_path), pytest.raises(SystemExit):
            hal_instance.copy(ns)


class TestSyncCopiesMerge:
    """_sync_copies merges directories instead of replacing them."""

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
            hal_instance._sync_copies(copy_entry)

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
            hal_instance._sync_copies(copy_entry)

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
            hal_instance._sync_copies(copy_entry)

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
            hal_instance._sync_copies(copy_entry)

        assert (dest / "file.txt").read_text() == "content"

    def test_single_file_copy_still_overwrites(self, hal_instance, tmp_path):
        """Non-directory copies still do a straight overwrite."""
        src = tmp_path / "src.txt"
        src.write_text("new content")

        dest = tmp_path / "dest.txt"
        dest.write_text("old content")

        copy_entry = {"src": str(src), "dest": str(dest)}
        with patch.object(hal_instance, "_expand_template", side_effect=lambda t: t):
            hal_instance._sync_copies(copy_entry)

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
            hal_instance._sync_copies(copy_entry)

        assert (dest / "real.txt").exists()
        assert not (dest / ".DS_Store").exists()


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

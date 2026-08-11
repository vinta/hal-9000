import io
import json
import os
import sys
import time


def ai_title(title):
    return {"type": "ai-title", "aiTitle": title}


def custom_title(title):
    return {"type": "custom-title", "customTitle": title}


def user_entry(content):
    return {"type": "user", "message": {"role": "user", "content": content}}


def write_transcript(tmp_path, name, entries):
    path = tmp_path / name
    path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n")
    return path


class TestDisambiguateInheritedTitle:
    def test_inherited_duplicate_gets_suffix(self, autorename, tmp_path):
        write_transcript(tmp_path, "predecessor.jsonl", [ai_title("Test caveman style"), custom_title("test-caveman-style")])
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title("test-caveman-style")])

        assert autorename.disambiguate_inherited_title("test-caveman-style", str(successor)) == "test-caveman-style-2"

    def test_unique_inherited_name_left_alone(self, autorename, tmp_path):
        write_transcript(tmp_path, "predecessor.jsonl", [ai_title("Old topic"), custom_title("renamed-since")])
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title("old-topic")])

        assert autorename.disambiguate_inherited_title("old-topic", str(successor)) is None

    def test_user_launch_name_duplicates_left_alone(self, autorename, tmp_path):
        write_transcript(tmp_path, "first.jsonl", [custom_title("my-fixed-name"), user_entry("hello")])
        second = write_transcript(tmp_path, "second.jsonl", [custom_title("my-fixed-name")])

        assert autorename.disambiguate_inherited_title("my-fixed-name", str(second)) is None

    def test_chained_clear_increments_counter(self, autorename, tmp_path):
        write_transcript(tmp_path, "original.jsonl", [ai_title("Foo"), custom_title("foo")])
        write_transcript(tmp_path, "cleared-once.jsonl", [custom_title("foo-2")])
        successor = write_transcript(tmp_path, "cleared-twice.jsonl", [custom_title("foo-2")])

        assert autorename.disambiguate_inherited_title("foo-2", str(successor)) == "foo-3"

    def test_hook_slug_ending_in_digits_suffixes_whole_title(self, autorename, tmp_path):
        write_transcript(tmp_path, "predecessor.jsonl", [ai_title("Migrate to Python 3"), custom_title("migrate-to-python-3")])
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title("migrate-to-python-3")])

        assert autorename.disambiguate_inherited_title("migrate-to-python-3", str(successor)) == "migrate-to-python-3-2"

    def test_stale_siblings_ignored(self, autorename, tmp_path):
        predecessor = write_transcript(tmp_path, "predecessor.jsonl", [ai_title("Foo"), custom_title("foo")])
        stale = time.time() - autorename.SIBLING_WINDOW_SECONDS - 60
        os.utime(predecessor, (stale, stale))
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title("foo")])

        assert autorename.disambiguate_inherited_title("foo", str(successor)) is None

    def test_suffix_respects_width_limit(self, autorename, tmp_path):
        base = "a" * autorename.TITLE_MAX_COLUMNS
        write_transcript(tmp_path, "predecessor.jsonl", [ai_title(base.upper()), custom_title(base)])
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title(base)])

        assert autorename.disambiguate_inherited_title(base, str(successor)) == "a" * (autorename.TITLE_MAX_COLUMNS - 2) + "-2"


class TestSummarizeSibling:
    def test_reads_launch_name_from_head_and_ai_titles_from_tail(self, autorename, tmp_path):
        filler_count = (autorename.SIBLING_HEAD_BYTES + autorename.SIBLING_TAIL_BYTES) // 200 + 50
        entries = [custom_title("foo"), *[user_entry("x" * 200) for _ in range(filler_count)], ai_title("Bar baz")]
        sibling = write_transcript(tmp_path, "long.jsonl", entries)

        summary = autorename.summarize_sibling(sibling)

        assert summary["title"] == "foo"
        assert "bar-baz" in summary["ai_slugs"]

    def test_latest_title_wins_over_launch_name(self, autorename, tmp_path):
        sibling = write_transcript(tmp_path, "renamed.jsonl", [custom_title("foo"), custom_title("bar")])

        assert autorename.summarize_sibling(sibling)["title"] == "bar"


class TestMain:
    def run_main(self, autorename, monkeypatch, capsys, hook_input):
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(hook_input)))
        autorename.main()
        out = capsys.readouterr().out
        return json.loads(out) if out else None

    def test_emits_disambiguated_title_for_inherited_duplicate(self, autorename, tmp_path, monkeypatch, capsys):
        write_transcript(tmp_path, "predecessor.jsonl", [ai_title("Test caveman style"), custom_title("test-caveman-style")])
        successor = write_transcript(tmp_path, "successor.jsonl", [custom_title("test-caveman-style")])
        hook_input = {"session_id": "s2", "transcript_path": str(successor), "session_title": "test-caveman-style"}

        output = self.run_main(autorename, monkeypatch, capsys, hook_input)

        assert output["hookSpecificOutput"]["sessionTitle"] == "test-caveman-style-2"

    def test_normal_rename_from_ai_title_still_works(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "session.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript)}

        output = self.run_main(autorename, monkeypatch, capsys, hook_input)

        assert output["hookSpecificOutput"]["sessionTitle"] == "hello-world"

    def test_named_session_without_collision_stays_silent(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "session.jsonl", [custom_title("my-fixed-name")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "my-fixed-name"}

        assert self.run_main(autorename, monkeypatch, capsys, hook_input) is None

    def test_suffixed_hook_name_still_follows_ai_title_drift(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "session.jsonl", [custom_title("foo-2"), ai_title("Foo"), ai_title("New topic")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "foo-2"}

        output = self.run_main(autorename, monkeypatch, capsys, hook_input)

        assert output["hookSpecificOutput"]["sessionTitle"] == "new-topic"

    def test_user_name_ending_in_digits_backs_off(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "session.jsonl", [ai_title("Something else")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "my-project-2"}

        assert self.run_main(autorename, monkeypatch, capsys, hook_input) is None

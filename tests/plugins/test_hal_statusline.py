import json
import re


def strip_ansi(text):
    return re.sub(r"\x1b\[\d+m", "", text)


def make_data(transcript_path, *, session_id="test-session"):
    return {"session_id": session_id, "transcript_path": str(transcript_path)}


def write_transcript(tmp_path, entries):
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("\n".join(json.dumps(entry) for entry in entries))
    return transcript


def user_entry(content, uuid="uuid-1"):
    return {"type": "user", "uuid": uuid, "message": {"role": "user", "content": content}}


def make_cache(uuid, *, status="done", result="", timed_out=False):
    return {
        "uuid": uuid,
        "input": "fix the bug plase",
        "status": status,
        "result": result,
        "elapsed": 0.1,
        "backend": "claude",
        "cwd": "",
        "timed_out": timed_out,
    }


class TestGrammarCheckPlaceholders:
    def test_no_transcript_path(self, statusline, capsys):
        statusline.grammar_check({"session_id": "test-session"})

        assert "Grammar: transcript_path not found" in capsys.readouterr().out

    def test_no_checkable_input_shows_skipped(self, statusline, capsys, tmp_path):
        transcript = write_transcript(
            tmp_path,
            [
                user_entry("<command-name>/clear</command-name>"),
                user_entry("<local-command-stdout></local-command-stdout>"),
            ],
        )

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: skipped" in capsys.readouterr().out

    def test_command_after_real_prompt_shows_skipped(self, statusline, capsys, tmp_path):
        transcript = write_transcript(
            tmp_path,
            [
                user_entry("fix the bug plase"),
                user_entry("<command-name>/clear</command-name>", uuid="uuid-2"),
            ],
        )

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: skipped" in capsys.readouterr().out

    def test_empty_transcript_shows_nothing_to_check(self, statusline, capsys, tmp_path):
        transcript = write_transcript(tmp_path, [])

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: nothing to check" in capsys.readouterr().out

    def test_no_session_id(self, statusline, capsys, tmp_path):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase")])
        data = make_data(transcript)
        del data["session_id"]

        statusline.grammar_check(data)

        assert "Grammar: session_id not found" in capsys.readouterr().out

    def test_model_timeout_shows_timed_out(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: make_cache("uuid-9", timed_out=True))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: timed out" in capsys.readouterr().out

    def test_pending_run_shows_checking(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: make_cache("uuid-9", status="pending"))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: checking…" in capsys.readouterr().out

    def test_cached_empty_result_shows_not_found(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: make_cache("uuid-9"))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: result not found" in capsys.readouterr().out

    def test_cached_result_still_prints_grammar(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: make_cache("uuid-9", result="Grammar: no issues"))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: no issues" in strip_ansi(capsys.readouterr().out)

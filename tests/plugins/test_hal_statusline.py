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


class TestGrammarCheckPlaceholders:
    def test_no_transcript_path(self, statusline, capsys):
        statusline.grammar_check({"session_id": "test-session"})

        assert "Grammar: no transcript" in capsys.readouterr().out

    def test_no_checkable_input_shows_no_input(self, statusline, capsys, tmp_path):
        transcript = write_transcript(
            tmp_path,
            [
                user_entry("<command-name>/clear</command-name>"),
                user_entry("<local-command-stdout></local-command-stdout>"),
            ],
        )

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: no input" in capsys.readouterr().out

    def test_no_session_id(self, statusline, capsys, tmp_path):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase")])
        data = make_data(transcript)
        del data["session_id"]

        statusline.grammar_check(data)

        assert "Grammar: no session" in capsys.readouterr().out

    def test_model_timeout_shows_timed_out(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase")])
        monkeypatch.setattr(statusline, "run_grammar_model", lambda _prompt: None)
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: ("", ""))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: timed out" in capsys.readouterr().out

    def test_empty_model_result_shows_empty_result(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase")])
        monkeypatch.setattr(statusline, "run_grammar_model", lambda _prompt: {"result": "", "elapsed": 0.1, "backend": "claude"})
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: ("", ""))
        monkeypatch.setattr(statusline, "write_cache", lambda _cache_file, _payload: None)

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: empty result" in capsys.readouterr().out

    def test_cached_empty_result_shows_empty_result(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: ("uuid-9", ""))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: empty result" in capsys.readouterr().out

    def test_cached_result_still_prints_grammar(self, statusline, capsys, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, [user_entry("fix the bug plase", uuid="uuid-9")])
        monkeypatch.setattr(statusline, "read_cache", lambda _cache_file: ("uuid-9", "Grammar: no issues"))

        statusline.grammar_check(make_data(transcript))

        assert "Grammar: no issues" in strip_ansi(capsys.readouterr().out)

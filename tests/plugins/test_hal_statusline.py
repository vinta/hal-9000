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


class TestBasicInfo:
    def test_agent_view_payload_without_effort(self, statusline, capsys, tmp_path):
        statusline.basic_info({"model": {"id": "claude-haiku-4-5-20251001"}, "workspace": {"current_dir": str(tmp_path)}})

        out = strip_ansi(capsys.readouterr().out)
        assert out.startswith("Current: claude-haiku-4-5-20251001 · ")

    def test_effort_rendered_when_present(self, statusline, capsys, tmp_path):
        statusline.basic_info({"model": {"id": "claude-fable-5"}, "effort": {"level": "max"}, "workspace": {"current_dir": str(tmp_path)}})

        out = strip_ansi(capsys.readouterr().out)
        assert out.startswith("Current: claude-fable-5 max · ")


def make_task(**overrides):
    task = {
        "id": "task-1",
        "name": "hal-skills-commit",
        "type": "general-purpose",
        "status": "running",
        "description": "/hal-skills:commit all pending changes",
        "label": "commit",
        "startTime": 1754000000000,
        "model": "claude-sonnet-5",
        "effort": "high",
        "contextWindowSize": 200000,
        "tokenCount": 24000,
        "tokenSamples": [],
        "cwd": "/usr/local/hal-9000",
    }
    task.update(overrides)
    return task


def subagent_rows(capsys):
    return [json.loads(line) for line in capsys.readouterr().out.splitlines()]


class TestSubagentStatus:
    def test_full_task_renders_row(self, statusline, capsys):
        statusline.subagent_status({"columns": 120, "tasks": [make_task()]})

        rows = subagent_rows(capsys)
        assert len(rows) == 1
        assert rows[0]["id"] == "task-1"
        assert strip_ansi(rows[0]["content"]) == "hal-skills-commit · sonnet-5 high · Ctx 12% · /hal-skills:commit all pending changes"

    def test_inherited_effort_omitted(self, statusline, capsys):
        task = make_task()
        del task["effort"]

        statusline.subagent_status({"columns": 120, "tasks": [task]})

        rows = subagent_rows(capsys)
        assert strip_ansi(rows[0]["content"]) == "hal-skills-commit · sonnet-5 · Ctx 12% · /hal-skills:commit all pending changes"

    def test_unresolved_model_keeps_default_row(self, statusline, capsys):
        task = make_task()
        del task["model"]
        del task["contextWindowSize"]

        statusline.subagent_status({"columns": 120, "tasks": [task, make_task(id="task-2")]})

        rows = subagent_rows(capsys)
        assert [row["id"] for row in rows] == ["task-2"]

    def test_description_truncates_to_columns(self, statusline, capsys):
        statusline.subagent_status({"columns": 60, "tasks": [make_task()]})

        content = strip_ansi(subagent_rows(capsys)[0]["content"])
        assert content == "hal-skills-commit · sonnet-5 high · Ctx 12% · /hal-skills:c…"
        assert len(content) == 60

    def test_description_dropped_when_no_room(self, statusline, capsys):
        statusline.subagent_status({"columns": 46, "tasks": [make_task()]})

        content = strip_ansi(subagent_rows(capsys)[0]["content"])
        assert content == "hal-skills-commit · sonnet-5 high · Ctx 12%"

    def test_numeric_effort_budget_rendered_verbatim(self, statusline, capsys):
        statusline.subagent_status({"columns": 120, "tasks": [make_task(effort=50000)]})

        assert "sonnet-5 50000" in strip_ansi(subagent_rows(capsys)[0]["content"])

    def test_empty_description_falls_back_to_label(self, statusline, capsys):
        statusline.subagent_status({"columns": 120, "tasks": [make_task(description="")]})

        content = strip_ansi(subagent_rows(capsys)[0]["content"])
        assert content == "hal-skills-commit · sonnet-5 high · Ctx 12% · commit"

    def test_task_without_name_renders_model_first(self, statusline, capsys):
        task = make_task(model="claude-opus-5[1m]", contextWindowSize=1000000, tokenCount=28261, description="List repo files")
        del task["name"]
        del task["effort"]

        statusline.subagent_status({"columns": 120, "tasks": [task]})

        content = strip_ansi(subagent_rows(capsys)[0]["content"])
        assert content == "opus-5[1m] · Ctx 2% · List repo files"

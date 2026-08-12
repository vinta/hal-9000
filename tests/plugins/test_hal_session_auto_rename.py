import io
import json
import sys
import time


def ai_title(title):
    return {"type": "ai-title", "aiTitle": title}


def user_entry(content, *, meta=False):
    return {"type": "user", "isMeta": meta, "message": {"role": "user", "content": content}}


def assistant_entry(text):
    return {"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


def write_transcript(tmp_path, name, entries):
    path = tmp_path / name
    path.write_text("\n".join(json.dumps(entry) for entry in entries) + "\n")
    return path


def write_state(autorename, session_id, state):
    autorename.write_state(session_id, state)


def run_main(autorename, monkeypatch, capsys, hook_input):
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(hook_input)))
    autorename.main()
    out = capsys.readouterr().out
    return json.loads(out)["hookSpecificOutput"]["sessionTitle"] if out else None


class TestAiTitlePath:
    def test_emits_slug_and_records_state(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])

        title = run_main(autorename, monkeypatch, capsys, {"session_id": "s1", "transcript_path": str(transcript)})

        assert title == "hello-world"
        assert autorename.read_state("s1") == {"set_title": "hello-world"}

    def test_backfills_state_when_title_already_current(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "hello-world"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"set_title": "hello-world"}

    def test_user_set_name_marks_user_owned(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "my-own-name"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"user_owned": True}

    def test_worker_set_title_not_reclaimed_as_user_owned(self, autorename, tmp_path, monkeypatch, capsys):
        # A worker/refresh slug never matches an ai-title slug, and must stay ours and adoptable instead of flipping to user_owned
        write_state(autorename, "s1", {"set_title": "debug-oauth-token-refresh"})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "debug-oauth-token-refresh"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"set_title": "debug-oauth-token-refresh"}

    def test_dropped_emit_reemits_instead_of_marking_user_owned(self, autorename, tmp_path, monkeypatch, capsys):
        write_state(autorename, "s1", {"set_title": "hello-world"})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": ""}

        assert run_main(autorename, monkeypatch, capsys, hook_input) == "hello-world"


class TestAdoption:
    def test_inherited_title_spawns_worker(self, autorename, tmp_path, monkeypatch, capsys):
        write_state(autorename, "predecessor", {"set_title": "fix-login-bug"})
        transcript = write_transcript(tmp_path, "successor.jsonl", [user_entry("<command-name>/clear</command-name>")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "successor", "transcript_path": str(transcript), "session_title": "fix-login-bug", "prompt": "plan a party menu"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == ["successor"]
        state = autorename.read_state("successor")
        assert time.time() - state.pop("pending_since") < 5
        assert state == {
            "inherited_title": "fix-login-bug",
            "status": "pending",
            "transcript_path": str(transcript),
            "seed_prompt": "plan a party menu",
        }

    def test_launch_name_without_source_marks_user_owned(self, autorename, tmp_path, monkeypatch, capsys):
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("hello")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "my-fixed-name"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == []
        assert autorename.read_state("s1") == {"user_owned": True}

    def test_pending_state_stays_silent(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "pending_since": time.time(), "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1")["status"] == "pending"

    def test_rename_during_pending_marks_user_owned(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "renamed-by-user"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"user_owned": True}


class TestPendingLease:
    def test_stale_pending_reclaims_inherited(self, autorename, monkeypatch, capsys):
        # The worker died without writing -- crash, kill, or failed spawn -- so nothing will ever consume this pending state
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "pending_since": time.time() - 120, "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"set_title": "fix-login-bug"}

    def test_missing_pending_since_reclaims_immediately(self, autorename, monkeypatch, capsys):
        # State files from before the lease existed carry no timestamp -- treating them as stale heals sessions the old code left wedged
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"set_title": "fix-login-bug"}

    def test_rename_wins_over_stale_pending(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "pending_since": time.time() - 120, "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "renamed-by-user"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"user_owned": True}


class TestWorkerApply:
    def test_done_state_applies_fresh_title(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "done", "pending_title": "Debug OAuth token refresh", "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) == "debug-oauth-token-refresh"
        assert autorename.read_state("s1") == {"set_title": "debug-oauth-token-refresh"}

    def test_rename_during_done_marks_user_owned_without_emit(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "done", "pending_title": "Debug OAuth token refresh", "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "renamed-by-user"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"user_owned": True}

    def test_worker_title_matching_inherited_claims_without_emit(self, autorename, monkeypatch, capsys):
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "done", "pending_title": "Fix login bug", "transcript_path": "x"})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert autorename.read_state("s1") == {"set_title": "fix-login-bug"}

    def test_legacy_failed_state_stays_silent(self, autorename, monkeypatch, capsys):
        # State files written by older versions may still carry status "failed" -- they must fall through without spawning or emitting
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "failed", "transcript_path": "x"})
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "fix-login-bug"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == []
        assert autorename.read_state("s1")["status"] == "failed"

    def test_user_owned_short_circuits_everything(self, autorename, tmp_path, monkeypatch, capsys):
        write_state(autorename, "s1", {"user_owned": True})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        hook_input = {"session_id": "s1", "transcript_path": str(transcript)}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None


class TestWorker:
    def test_writes_done_with_generated_title(self, autorename, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("help me debug oauth"), assistant_entry("Sure, the token refresh is broken")])
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": str(transcript)})
        monkeypatch.setattr(autorename, "run_title_model", lambda _prompt: "Debug OAuth token refresh\n")

        autorename.run_title_worker("s1")

        state = autorename.read_state("s1")
        assert state["status"] == "done"
        assert state["pending_title"] == "Debug OAuth token refresh"

    def test_model_failure_claims_inherited_title(self, autorename, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("help me debug oauth")])
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": str(transcript)})
        monkeypatch.setattr(autorename, "run_title_model", lambda _prompt: None)

        autorename.run_title_worker("s1")

        assert autorename.read_state("s1") == {"set_title": "fix-login-bug"}

    def test_empty_transcript_falls_back_to_seed_prompt(self, autorename, tmp_path, monkeypatch):
        # Right after /clear the transcript holds only filtered harness noise, and the adopting prompt may not be flushed yet
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("<command-name>/clear</command-name>")])
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": str(transcript), "seed_prompt": "plan a birthday party menu"})
        prompts = []

        def capture(prompt):
            prompts.append(prompt)
            return "Plan birthday party menu"

        monkeypatch.setattr(autorename, "run_title_model", capture)

        autorename.run_title_worker("s1")

        assert "plan a birthday party menu" in prompts[0]
        assert autorename.read_state("s1")["status"] == "done"

    def test_state_replaced_midflight_discards_result(self, autorename, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("help me debug oauth")])
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": str(transcript)})

        def model_and_rename(_prompt):
            write_state(autorename, "s1", {"user_owned": True})
            return "Debug OAuth token refresh"

        monkeypatch.setattr(autorename, "run_title_model", model_and_rename)

        autorename.run_title_worker("s1")

        assert autorename.read_state("s1") == {"user_owned": True}


class TestRefreshMode:
    def test_counter_increments_without_spawn(self, autorename, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        write_state(autorename, "s1", {"set_title": "hello-world"})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "hello-world"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == []
        assert autorename.read_state("s1") == {"set_title": "hello-world", "prompt_count": 1}

    def test_fires_at_n_and_resets_counter(self, autorename, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        write_state(autorename, "s1", {"set_title": "hello-world", "prompt_count": 2})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "hello-world", "prompt": "now about css grids"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == ["s1"]
        state = autorename.read_state("s1")
        assert time.time() - state.pop("pending_since") < 5
        assert state == {
            "inherited_title": "hello-world",
            "status": "pending",
            "transcript_path": str(transcript),
            "seed_prompt": "now about css grids",
            "prompt_count": 0,
        }

    def test_refresh_apply_emits_and_counter_restarts(self, autorename, monkeypatch, capsys):
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        write_state(autorename, "s1", {"inherited_title": "hello-world", "status": "done", "pending_title": "Now about CSS grids", "transcript_path": "x", "prompt_count": 0})
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "hello-world"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) == "now-about-css-grids"
        assert autorename.read_state("s1") == {"set_title": "now-about-css-grids", "prompt_count": 1}

    def test_pending_holds_fire_and_stays_untouched(self, autorename, monkeypatch, capsys):
        # The counter must not even count while pending: its read-modify-write once buried the worker's `done` under stale pending, wedging the session
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        pending = {"inherited_title": "hello-world", "status": "pending", "pending_since": time.time(), "transcript_path": "x", "prompt_count": 5}
        write_state(autorename, "s1", pending)
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "hello-world"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == []
        assert autorename.read_state("s1") == pending

    def test_emission_prompt_defers_fire(self, autorename, tmp_path, monkeypatch, capsys):
        # The hook input's session_title predates this prompt's emission, so firing now would record a stale inherited_title and misread our own emission as a rename
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "1")
        write_state(autorename, "s1", {"set_title": "hello-world"})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)

        assert run_main(autorename, monkeypatch, capsys, {"session_id": "s1", "transcript_path": str(transcript), "session_title": ""}) == "hello-world"
        assert spawned == []
        assert autorename.read_state("s1") == {"set_title": "hello-world", "prompt_count": 1}

        assert run_main(autorename, monkeypatch, capsys, {"session_id": "s1", "transcript_path": str(transcript), "session_title": "hello-world"}) is None
        assert spawned == ["s1"]
        assert autorename.read_state("s1")["status"] == "pending"

    def test_unprovable_start_title_refreshes_immediately(self, autorename, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "10")
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("hello")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "my-fixed-name", "prompt": "hello"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == ["s1"]
        state = autorename.read_state("s1")
        assert state["status"] == "pending"
        assert state["inherited_title"] == "my-fixed-name"
        # The counter skips writes while pending, so the spawning prompt itself is not counted
        assert state["prompt_count"] == 0

    def test_failed_refresh_claim_restarts_counter(self, autorename, monkeypatch, capsys):
        # A failed refresh worker claims the current title, so the next cycle starts counting from scratch -- that recount is the retry
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        write_state(autorename, "s1", {"set_title": "hello-world"})
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": "x", "session_title": "hello-world"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == []
        assert autorename.read_state("s1")["prompt_count"] == 1

    def test_user_owned_overridden_at_cycle(self, autorename, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("HAL_SESSION_AUTO_RENAME_REFRESH_EVERY_N_PROMPTS", "3")
        write_state(autorename, "s1", {"user_owned": True, "prompt_count": 2})
        transcript = write_transcript(tmp_path, "s.jsonl", [ai_title("Hello world")])
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)
        hook_input = {"session_id": "s1", "transcript_path": str(transcript), "session_title": "renamed-by-user", "prompt": "now about css grids"}

        assert run_main(autorename, monkeypatch, capsys, hook_input) is None
        assert spawned == ["s1"]
        state = autorename.read_state("s1")
        assert state["status"] == "pending"
        assert state["inherited_title"] == "renamed-by-user"
        assert "user_owned" not in state

    def test_unconsumed_done_defers_spawn(self, autorename, monkeypatch):
        # A worker `done` landing between main's read and the counter's re-read must not be overwritten by a refresh spawn -- count it and let the next prompt apply the title
        write_state(autorename, "s1", {"inherited_title": "hello-world", "status": "done", "pending_title": "Now about CSS grids", "transcript_path": "x", "prompt_count": 5})
        spawned = []
        monkeypatch.setattr(autorename, "spawn_title_worker", spawned.append)

        autorename.run_refresh_counter({"session_id": "s1", "transcript_path": "x", "session_title": "hello-world"}, "s1", 3)

        assert spawned == []
        state = autorename.read_state("s1")
        assert state["status"] == "done"
        assert state["pending_title"] == "Now about CSS grids"
        assert state["prompt_count"] == 6


class TestTitleModelFailures:
    def test_ollama_error_body_returns_none(self, autorename, monkeypatch):
        class ErrorResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def read(self):
                return b'{"error": "model not found"}'

        monkeypatch.setattr(autorename.urllib.request, "urlopen", lambda *_args, **_kwargs: ErrorResponse())

        assert autorename.run_ollama_title_model("p") is None

    def test_ollama_non_json_body_returns_none(self, autorename, monkeypatch):
        class BrokenResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_exc):
                return False

            def read(self):
                return b"Internal Server Error"

        monkeypatch.setattr(autorename.urllib.request, "urlopen", lambda *_args, **_kwargs: BrokenResponse())

        assert autorename.run_ollama_title_model("p") is None

    def test_claude_missing_binary_returns_none(self, autorename, monkeypatch):
        def raise_missing(*_args, **_kwargs):
            raise FileNotFoundError

        monkeypatch.setattr(autorename.subprocess, "run", raise_missing)

        assert autorename.run_claude_title_model("p") is None


class TestSanitizeTitle:
    def test_accepts_short_title_stripping_quotes_and_period(self, autorename):
        assert autorename.sanitize_title('"Debug OAuth token refresh."\n') == "Debug OAuth token refresh"

    def test_rejects_sentence_length_refusal(self, autorename):
        refusal = "This doesn't appear to be a coding session. I'm designed to help with software engineering tasks like solving bugs, adding features, refactoring code, and explaining code."
        assert autorename.sanitize_title(refusal) == ""

    def test_rejects_empty_output(self, autorename):
        assert autorename.sanitize_title("\n\n") == ""

    def test_worker_claims_inherited_title_on_refusal(self, autorename, tmp_path, monkeypatch):
        transcript = write_transcript(tmp_path, "s.jsonl", [user_entry("plan a party")])
        write_state(autorename, "s1", {"inherited_title": "fix-login-bug", "status": "pending", "transcript_path": str(transcript)})
        monkeypatch.setattr(autorename, "run_title_model", lambda _prompt: "This doesn't appear to be a coding session. I can only help with software.")

        autorename.run_title_worker("s1")

        assert autorename.read_state("s1") == {"set_title": "fix-login-bug"}


class TestExtractRecentSessionText:
    def test_skips_meta_and_command_entries_and_caps_length(self, autorename, tmp_path):
        entries = [
            user_entry("<command-name>/clear</command-name>"),
            user_entry("meta noise", meta=True),
            user_entry("real question about oauth"),
            assistant_entry("x" * 5000),
        ]
        transcript = write_transcript(tmp_path, "s.jsonl", entries)

        text = autorename.extract_recent_session_text(str(transcript))

        assert len(text) == autorename.TITLE_WINDOW_CHARS
        assert "command-name" not in text
        assert "meta noise" not in text

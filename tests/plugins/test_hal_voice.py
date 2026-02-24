import json
from unittest.mock import patch


class TestLoadConfig:
    def test_missing_file_returns_defaults(self, hal, tmp_path):
        config = hal.load_config(tmp_path / "nonexistent.json")
        assert config["enabled"] is True
        assert config["volume"] == 0.5
        assert config["debounce_seconds"] == 5
        assert config["replay_suppression_seconds"] == 3
        assert config["suppress_subagent_complete"] is True

    def test_partial_override(self, hal, tmp_path):
        cfg_path = tmp_path / "config.json"
        cfg_path.write_text(json.dumps({"volume": 0.8}))
        config = hal.load_config(cfg_path)
        assert config["volume"] == 0.8
        assert config["enabled"] is True

    def test_full_override(self, hal, tmp_path):
        cfg_path = tmp_path / "config.json"
        cfg_path.write_text(
            json.dumps(
                {
                    "enabled": False,
                    "volume": 0.1,
                    "debounce_seconds": 10,
                    "replay_suppression_seconds": 0,
                    "suppress_subagent_complete": False,
                }
            )
        )
        config = hal.load_config(cfg_path)
        assert config["enabled"] is False
        assert config["volume"] == 0.1

    def test_corrupt_file_returns_defaults(self, hal, tmp_path):
        cfg_path = tmp_path / "config.json"
        cfg_path.write_text("not json")
        config = hal.load_config(cfg_path)
        assert config["enabled"] is True


class TestLoadState:
    def test_missing_file_returns_empty(self, hal, tmp_path):
        state = hal.load_state(tmp_path / "nonexistent.json")
        assert state["last_played"] == {}
        assert state["last_stop_time"] == 0.0
        assert state["last_prompt_time"] == 0.0
        assert state["session_start_times"] == {}
        assert state["subagent_sessions"] == {}
        assert state["sound_pid"] is None

    def test_roundtrip(self, hal, tmp_path):
        state_path = tmp_path / "state.json"
        state = hal.load_state(state_path)
        state["last_played"]["Stop"] = "assets/foo.mp3"
        state["sound_pid"] = 12345
        hal.save_state(state_path, state)
        loaded = hal.load_state(state_path)
        assert loaded["last_played"]["Stop"] == "assets/foo.mp3"
        assert loaded["sound_pid"] == 12345

    def test_corrupt_file_returns_empty(self, hal, tmp_path):
        state_path = tmp_path / "state.json"
        state_path.write_text("{corrupt")
        state = hal.load_state(state_path)
        assert state["last_played"] == {}


class TestEvaluateDetection:
    def test_always(self, hal):
        assert hal.evaluate_detection({"detection": "always"}, {}, {}) is True

    def test_regex_match(self, hal):
        rule = {"detection": "regex", "pattern": "I can't|I cannot"}
        hook_input = {"last_assistant_message": "I can't do that"}
        assert hal.evaluate_detection(rule, hook_input, {}) is True

    def test_regex_no_match(self, hal):
        rule = {"detection": "regex", "pattern": "I can't|I cannot"}
        hook_input = {"last_assistant_message": "Here is the result"}
        assert hal.evaluate_detection(rule, hook_input, {}) is False

    def test_regex_empty_message(self, hal):
        rule = {"detection": "regex", "pattern": "error"}
        assert hal.evaluate_detection(rule, {}, {}) is False

    def test_regex_uses_prompt_for_user_prompt_submit(self, hal):
        rule = {"detection": "regex", "pattern": "hello"}
        hook_input = {"hook_event_name": "UserPromptSubmit", "prompt": "hello world"}
        assert hal.evaluate_detection(rule, hook_input, {}) is True

    def test_elapsed_above_threshold(self, hal):
        rule = {"detection": "elapsed", "min_seconds": 120}
        state = {"last_prompt_time": 1000.0}
        with patch("time.time", return_value=1200.0):
            assert hal.evaluate_detection(rule, {}, state) is True

    def test_elapsed_below_threshold(self, hal):
        rule = {"detection": "elapsed", "min_seconds": 120}
        state = {"last_prompt_time": 1000.0}
        with patch("time.time", return_value=1050.0):
            assert hal.evaluate_detection(rule, {}, state) is False

    def test_elapsed_no_prompt_time(self, hal):
        rule = {"detection": "elapsed", "min_seconds": 120}
        assert hal.evaluate_detection(rule, {}, {"last_prompt_time": 0.0}) is False


class TestPickClip:
    def test_single_clip(self, hal):
        assert hal.pick_clip(["a.mp3"], None) == "a.mp3"

    def test_single_clip_ignores_last_played(self, hal):
        assert hal.pick_clip(["a.mp3"], "a.mp3") == "a.mp3"

    def test_avoids_last_played(self, hal):
        clips = ["a.mp3", "b.mp3"]
        for _ in range(50):
            result = hal.pick_clip(clips, "a.mp3")
            assert result == "b.mp3"

    def test_multiple_clips_returns_from_pool(self, hal):
        clips = ["a.mp3", "b.mp3", "c.mp3"]
        result = hal.pick_clip(clips, "a.mp3")
        assert result in ("b.mp3", "c.mp3")


class TestShouldDebounce:
    def test_within_window(self, hal):
        state = {"last_stop_time": 1000.0}
        config = {"debounce_seconds": 5}
        assert hal.should_debounce(state, config, now=1003.0) is True

    def test_outside_window(self, hal):
        state = {"last_stop_time": 1000.0}
        config = {"debounce_seconds": 5}
        assert hal.should_debounce(state, config, now=1006.0) is False

    def test_no_previous_stop(self, hal):
        state = {"last_stop_time": 0.0}
        config = {"debounce_seconds": 5}
        assert hal.should_debounce(state, config, now=1000.0) is False


class TestShouldSuppressReplay:
    def test_within_window(self, hal):
        state = {"session_start_times": {"sess-1": 1000.0}}
        config = {"replay_suppression_seconds": 3}
        assert hal.should_suppress_replay(state, config, session_id="sess-1", now=1002.0) is True

    def test_outside_window(self, hal):
        state = {"session_start_times": {"sess-1": 1000.0}}
        config = {"replay_suppression_seconds": 3}
        assert hal.should_suppress_replay(state, config, session_id="sess-1", now=1005.0) is False

    def test_unknown_session(self, hal):
        state = {"session_start_times": {}}
        config = {"replay_suppression_seconds": 3}
        assert hal.should_suppress_replay(state, config, session_id="unknown", now=1000.0) is False


class TestShouldSuppressSubagent:
    def test_known_subagent(self, hal):
        state = {"subagent_sessions": {"child-1": 1000.0}}
        config = {"suppress_subagent_complete": True}
        assert hal.should_suppress_subagent(state, config, session_id="child-1") is True

    def test_suppression_disabled(self, hal):
        state = {"subagent_sessions": {"child-1": 1000.0}}
        config = {"suppress_subagent_complete": False}
        assert hal.should_suppress_subagent(state, config, session_id="child-1") is False

    def test_unknown_session(self, hal):
        state = {"subagent_sessions": {}}
        config = {"suppress_subagent_complete": True}
        assert hal.should_suppress_subagent(state, config, session_id="main") is False


class TestMatchManifest:
    def test_plain_key_match(self, hal):
        manifest = {"SessionStart": [{"detection": "always", "clips": ["a.mp3"]}]}
        result = hal.match_manifest(manifest, "SessionStart", "", {}, {})
        assert result == ("SessionStart", "a.mp3")

    def test_tool_matcher_key(self, hal):
        manifest = {"PreToolUse:AskUserQuestion": [{"detection": "always", "clips": ["q.mp3"]}]}
        result = hal.match_manifest(manifest, "PreToolUse", "AskUserQuestion", {}, {})
        assert result == ("PreToolUse:AskUserQuestion", "q.mp3")

    def test_tool_matcher_wrong_tool(self, hal):
        manifest = {"PreToolUse:AskUserQuestion": [{"detection": "always", "clips": ["q.mp3"]}]}
        result = hal.match_manifest(manifest, "PreToolUse", "Bash", {}, {})
        assert result is None

    def test_first_match_wins(self, hal):
        manifest = {
            "Stop": [
                {"detection": "regex", "pattern": "error", "clips": ["err.mp3"]},
                {"detection": "always", "clips": ["default.mp3"]},
            ],
        }
        hook_input = {"last_assistant_message": "an error occurred"}
        result = hal.match_manifest(manifest, "Stop", "", hook_input, {})
        assert result is not None
        assert result[1] == "err.mp3"

    def test_falls_through_to_second_rule(self, hal):
        manifest = {
            "Stop": [
                {"detection": "regex", "pattern": "error", "clips": ["err.mp3"]},
                {"detection": "always", "clips": ["default.mp3"]},
            ],
        }
        hook_input = {"last_assistant_message": "all good"}
        result = hal.match_manifest(manifest, "Stop", "", hook_input, {})
        assert result is not None
        assert result[1] == "default.mp3"

    def test_no_match(self, hal):
        manifest = {"SessionStart": [{"detection": "always", "clips": ["a.mp3"]}]}
        result = hal.match_manifest(manifest, "Stop", "", {}, {})
        assert result is None

    def test_empty_clips_skipped(self, hal):
        manifest = {"Stop": [{"detection": "always", "clips": []}]}
        result = hal.match_manifest(manifest, "Stop", "", {}, {})
        assert result is None


class TestCleanupOldSessions:
    def test_removes_expired(self, hal):
        state = {
            "session_start_times": {"old": 1000.0, "new": 90000.0},
            "subagent_sessions": {"old-child": 1000.0, "new-child": 90000.0},
        }
        hal.cleanup_old_sessions(state, now=100000.0, max_age=86400)
        assert "old" not in state["session_start_times"]
        assert "new" in state["session_start_times"]
        assert "old-child" not in state["subagent_sessions"]
        assert "new-child" in state["subagent_sessions"]

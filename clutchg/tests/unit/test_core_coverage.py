"""
Unit tests for core modules with zero or low test coverage:
  - config.py         (ConfigManager)
  - help_manager.py   (HelpManager, HelpTopic)
  - profile_recommender.py (ProfileRecommender, RecommendationResult)
  - system_snapshot.py (SystemSnapshot, SnapshotDiff, SystemSnapshotManager)
  - batch_executor.py  (BatchExecutor, ExecutionResult)
"""

import json
import sys
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch, call
import pytest

# ---------------------------------------------------------------------------
# Path bootstrap (mirrors the other unit tests in this directory)
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.config import ConfigManager
from core.help_manager import HelpManager, HelpTopic
from core.profile_recommender import (
    ProfileRecommender,
    RecommendationResult,
    get_recommender,
)
from core.system_snapshot import (
    SystemSnapshot,
    SnapshotDiff,
    SystemSnapshotManager,
)
from core.batch_executor import BatchExecutor, ExecutionResult


# ===========================================================================
# ConfigManager
# ===========================================================================

@pytest.mark.unit
class TestConfigManager:
    """Tests for ConfigManager – no real filesystem needed (uses tmp_path)."""

    def test_get_default_config_returns_required_keys(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        cfg = mgr.get_default_config()
        for key in ("version", "language", "theme", "accent", "auto_backup",
                    "confirm_actions", "default_profile"):
            assert key in cfg, f"Missing key: {key}"

    def test_default_theme_is_modern(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        cfg = mgr.get_default_config()
        assert cfg["theme"] == "modern"
        assert cfg["accent"] == "tokyo_blue"

    def test_load_config_returns_defaults_when_no_files(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        cfg = mgr.load_config()
        assert cfg["language"] == "en"
        assert cfg["default_profile"] == "SAFE"

    def test_save_and_reload_config(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        overrides = {"language": "th", "theme": "dark"}
        assert mgr.save_config(overrides) is True
        loaded = mgr.load_config()
        assert loaded["language"] == "th"
        assert loaded["theme"] == "dark"

    def test_load_config_merges_user_over_defaults(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        # Write a user config that only overrides one key
        mgr.save_config({"max_backups": 99})
        cfg = mgr.load_config()
        assert cfg["max_backups"] == 99
        # Other defaults still present
        assert cfg["language"] == "en"

    def test_reset_to_defaults_removes_user_config(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        mgr.save_config({"language": "th"})
        assert mgr.user_config_file.exists()
        defaults = mgr.reset_to_defaults()
        assert not mgr.user_config_file.exists()
        assert defaults["language"] == "en"

    def test_save_config_returns_false_on_io_error(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        # Make the target path a directory so write fails
        mgr.user_config_file.mkdir(parents=True, exist_ok=True)
        result = mgr.save_config({"key": "value"})
        assert result is False

    def test_load_config_tolerates_corrupt_json(self, tmp_path):
        mgr = ConfigManager(config_dir=tmp_path)
        mgr.user_config_file.write_text("NOT JSON", encoding="utf-8")
        # Should not raise; falls back to defaults
        cfg = mgr.load_config()
        assert cfg["language"] == "en"

    def test_config_dir_created_automatically(self, tmp_path):
        new_dir = tmp_path / "nested" / "config"
        mgr = ConfigManager(config_dir=new_dir)
        assert new_dir.exists()


# ===========================================================================
# HelpManager
# ===========================================================================

@pytest.mark.unit
class TestHelpManager:
    """Tests for HelpManager using in-memory fixture data."""

    SAMPLE_CONTENT = {
        "topics": {
            "profiles": {
                "en": {
                    "title": "Profiles",
                    "icon": "🎮",
                    "profiles": {
                        "SAFE": {"name": "Safe", "risk": "LOW"},
                        "EXTREME": {"name": "Extreme", "risk": "HIGH"},
                    }
                },
                "th": {
                    "title": "โปรไฟล์",
                    "icon": "🎮",
                }
            },
            "scripts": {
                "en": {
                    "title": "Scripts",
                    "icon": "📜",
                    "categories": {
                        "power": {
                            "scripts": {
                                "power-plan.bat": {"description": "Power plan tweak"}
                            }
                        }
                    }
                }
            }
        }
    }

    @pytest.fixture()
    def help_file(self, tmp_path):
        f = tmp_path / "help_content.json"
        f.write_text(json.dumps(self.SAMPLE_CONTENT), encoding="utf-8")
        return f

    def test_get_topic_returns_english_by_default(self, help_file):
        mgr = HelpManager(help_file=help_file, language="en")
        topic = mgr.get_topic("profiles")
        assert topic is not None
        assert topic.title == "Profiles"
        assert topic.language == "en"

    def test_get_topic_returns_thai_when_requested(self, help_file):
        mgr = HelpManager(help_file=help_file, language="th")
        topic = mgr.get_topic("profiles", language="th")
        assert topic is not None
        assert topic.title == "โปรไฟล์"
        assert topic.language == "th"

    def test_get_topic_falls_back_to_english_for_missing_lang(self, help_file):
        mgr = HelpManager(help_file=help_file, language="fr")
        topic = mgr.get_topic("profiles")
        # "fr" not present, should fall back to "en"
        assert topic is not None
        assert topic.language == "en"

    def test_get_topic_returns_none_for_unknown_id(self, help_file):
        mgr = HelpManager(help_file=help_file)
        assert mgr.get_topic("nonexistent_topic") is None

    def test_get_all_topics_returns_all(self, help_file):
        mgr = HelpManager(help_file=help_file)
        topics = mgr.get_all_topics()
        assert len(topics) == 2
        ids = {t.id for t in topics}
        assert "profiles" in ids
        assert "scripts" in ids

    def test_get_profile_info_returns_correct_data(self, help_file):
        mgr = HelpManager(help_file=help_file)
        info = mgr.get_profile_info("SAFE")
        assert info is not None
        assert info["risk"] == "LOW"

    def test_get_profile_info_case_insensitive(self, help_file):
        mgr = HelpManager(help_file=help_file)
        assert mgr.get_profile_info("safe") == mgr.get_profile_info("SAFE")

    def test_get_profile_info_returns_none_for_unknown(self, help_file):
        mgr = HelpManager(help_file=help_file)
        assert mgr.get_profile_info("UNKNOWN_PROFILE") is None

    def test_get_script_info_finds_script(self, help_file):
        mgr = HelpManager(help_file=help_file)
        info = mgr.get_script_info("power-plan.bat")
        assert info is not None
        assert "description" in info

    def test_get_script_info_returns_none_for_unknown(self, help_file):
        mgr = HelpManager(help_file=help_file)
        assert mgr.get_script_info("fake-script.bat") is None

    def test_set_language_changes_default(self, help_file):
        mgr = HelpManager(help_file=help_file, language="en")
        mgr.set_language("th")
        assert mgr.language == "th"

    def test_missing_help_file_returns_empty_structure(self, tmp_path):
        mgr = HelpManager(help_file=tmp_path / "missing.json")
        assert mgr.get_all_topics() == []


# ===========================================================================
# ProfileRecommender
# ===========================================================================

@pytest.mark.unit
class TestProfileRecommender:
    """Tests for ProfileRecommender – pure logic, no subprocess."""

    # Convenience system-info dicts
    LOW_END = {"cpu_tier": 1, "gpu_tier": 1, "ram_gb": 4, "is_laptop": False, "is_gaming_gpu": False}
    MID_TIER = {"cpu_tier": 3, "gpu_tier": 3, "ram_gb": 16, "is_laptop": False, "is_gaming_gpu": True}
    HIGH_END = {"cpu_tier": 5, "gpu_tier": 5, "ram_gb": 32, "is_laptop": False, "is_gaming_gpu": True}
    HIGH_END_LAPTOP = {"cpu_tier": 5, "gpu_tier": 5, "ram_gb": 32, "is_laptop": True, "is_gaming_gpu": True}

    def test_beginner_low_end_gets_safe(self):
        r = ProfileRecommender()
        result = r.recommend(self.LOW_END, user_experience="beginner")
        assert result.recommended_profile == "SAFE"

    def test_intermediate_mid_tier_gets_competitive(self):
        r = ProfileRecommender()
        result = r.recommend(self.MID_TIER, user_experience="intermediate")
        assert result.recommended_profile == "COMPETITIVE"

    def test_advanced_high_end_desktop_gets_extreme(self):
        r = ProfileRecommender()
        result = r.recommend(
            self.HIGH_END,
            user_experience="advanced",
            user_goal="maximum_performance"
        )
        assert result.recommended_profile == "EXTREME"

    def test_laptop_does_not_get_extreme(self):
        r = ProfileRecommender()
        result = r.recommend(
            self.HIGH_END_LAPTOP,
            user_experience="advanced",
            user_goal="maximum_performance"
        )
        # EXTREME requires desktop
        assert result.recommended_profile != "EXTREME"

    def test_invalid_experience_defaults_to_beginner(self):
        r = ProfileRecommender()
        # Invalid experience level – should not raise, defaults to beginner
        result = r.recommend(self.LOW_END, user_experience="expert_hacker")
        assert result.recommended_profile == "SAFE"

    def test_confidence_between_0_and_1(self):
        r = ProfileRecommender()
        for sys_info in (self.LOW_END, self.MID_TIER, self.HIGH_END):
            for exp in ("beginner", "intermediate", "advanced"):
                result = r.recommend(sys_info, user_experience=exp)
                assert 0.0 <= result.confidence <= 1.0

    def test_result_is_recommendation_result_instance(self):
        r = ProfileRecommender()
        result = r.recommend(self.MID_TIER)
        assert isinstance(result, RecommendationResult)

    def test_recommendation_history_grows(self):
        r = ProfileRecommender()
        r.recommend(self.LOW_END)
        r.recommend(self.MID_TIER)
        assert len(r.recommendation_history) == 2

    def test_get_profile_requirements_returns_dict(self):
        r = ProfileRecommender()
        for name in ("SAFE", "COMPETITIVE", "EXTREME"):
            req = r.get_profile_requirements(name)
            assert "risk_level" in req
            assert "min_ram_gb" in req

    def test_get_profile_requirements_raises_for_unknown(self):
        r = ProfileRecommender()
        with pytest.raises(ValueError):
            r.get_profile_requirements("TURBO")

    def test_can_use_safe_profile_always_true(self):
        r = ProfileRecommender()
        can, reasons = r.can_use_profile("SAFE", self.LOW_END, "beginner")
        assert can is True
        assert reasons == []

    def test_can_use_extreme_fails_for_low_end(self):
        r = ProfileRecommender()
        can, reasons = r.can_use_profile("EXTREME", self.LOW_END, "beginner")
        assert can is False
        assert len(reasons) > 0

    def test_can_use_extreme_requires_desktop(self):
        r = ProfileRecommender()
        can, reasons = r.can_use_profile("EXTREME", self.HIGH_END_LAPTOP, "advanced")
        assert can is False
        assert any("desktop" in reason.lower() for reason in reasons)

    def test_can_use_unknown_profile_returns_false(self):
        r = ProfileRecommender()
        can, reasons = r.can_use_profile("GHOST", self.MID_TIER, "advanced")
        assert can is False

    def test_extreme_warning_list_not_empty(self):
        r = ProfileRecommender()
        result = r.recommend(
            self.HIGH_END,
            user_experience="advanced",
            user_goal="maximum_performance"
        )
        assert len(result.warnings) > 0

    def test_get_recommender_singleton(self):
        a = get_recommender()
        b = get_recommender()
        assert a is b


# ===========================================================================
# SystemSnapshot / SnapshotDiff / SystemSnapshotManager
# ===========================================================================

@pytest.mark.unit
class TestSystemSnapshot:
    """Tests for SystemSnapshot dataclass (pure, no subprocess)."""

    def test_to_dict_contains_all_fields(self):
        snap = SystemSnapshot(
            timestamp="2025-01-01T00:00:00",
            services_running=120,
            services_stopped=30,
            power_plan="High performance",
        )
        d = snap.to_dict()
        assert d["services_running"] == 120
        assert d["power_plan"] == "High performance"

    def test_from_dict_round_trips(self):
        snap = SystemSnapshot(
            timestamp="2025-01-01T00:00:00",
            services_running=100,
            services_stopped=20,
            startup_items=10,
            power_plan="Balanced",
        )
        restored = SystemSnapshot.from_dict(snap.to_dict())
        assert restored.services_running == 100
        assert restored.power_plan == "Balanced"

    def test_from_dict_ignores_unknown_keys(self):
        d = {"services_running": 5, "unknown_field": "ignored"}
        snap = SystemSnapshot.from_dict(d)
        assert snap.services_running == 5


@pytest.mark.unit
class TestSnapshotDiff:
    """Tests for SnapshotDiff comparison logic."""

    def test_services_stopped_delta_positive(self):
        diff = SnapshotDiff(services_stopped_delta=5)
        lines = diff.summary_lines
        assert any("5 service" in l for l in lines)

    def test_startup_items_reduced(self):
        diff = SnapshotDiff(startup_items_delta=-3)
        lines = diff.summary_lines
        assert any("3 startup" in l for l in lines)

    def test_power_plan_changed_shows_both(self):
        diff = SnapshotDiff(
            power_plan_changed=True,
            power_plan_before="Balanced",
            power_plan_after="High performance",
        )
        lines = diff.summary_lines
        assert any("Balanced" in l and "High performance" in l for l in lines)

    def test_no_changes_returns_no_measurable(self):
        diff = SnapshotDiff()
        lines = diff.summary_lines
        assert lines == ["No measurable changes detected"]


@pytest.mark.unit
class TestSystemSnapshotManager:
    """Tests for SystemSnapshotManager – subprocess calls are mocked."""

    def test_compare_computes_correct_deltas(self):
        before = SystemSnapshot(
            services_running=100,
            services_stopped=20,
            startup_items=15,
            scheduled_tasks_enabled=50,
            power_plan="Balanced",
        )
        after = SystemSnapshot(
            services_running=95,
            services_stopped=25,
            startup_items=12,
            scheduled_tasks_enabled=47,
            power_plan="High performance",
        )
        mgr = SystemSnapshotManager()
        diff = mgr.compare(before, after)

        assert diff.services_stopped_delta == 5
        assert diff.startup_items_delta == -3
        assert diff.tasks_disabled_delta == -3
        assert diff.power_plan_changed is True
        assert diff.power_plan_before == "Balanced"
        assert diff.power_plan_after == "High performance"

    def test_save_and_load_snapshot(self, tmp_path):
        mgr = SystemSnapshotManager()
        mgr.SNAPSHOT_DIR = tmp_path  # Override to avoid writing to real config dir
        snap = SystemSnapshot(
            timestamp="2025-01-01T00:00:00",
            services_running=80,
            power_plan="Balanced",
        )
        filepath = mgr.save_snapshot(snap, label="test")
        assert filepath.exists()

        loaded = mgr.load_snapshot(filepath)
        assert loaded is not None
        assert loaded.services_running == 80
        assert loaded.power_plan == "Balanced"

    def test_load_snapshot_returns_none_on_corrupt_file(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("NOT JSON", encoding="utf-8")
        mgr = SystemSnapshotManager()
        result = mgr.load_snapshot(bad_file)
        assert result is None

    @patch("core.system_snapshot.subprocess.run")
    def test_take_snapshot_uses_subprocess(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="50\n", stderr="", returncode=0
        )
        mgr = SystemSnapshotManager()
        snap = mgr.take_snapshot()
        assert mock_run.called
        # At minimum timestamp should be set
        assert snap.timestamp != ""


# ===========================================================================
# BatchExecutor / ExecutionResult
# ===========================================================================

@pytest.mark.unit
class TestBatchExecutor:
    """Tests for BatchExecutor – no real .bat files executed."""

    def test_execute_returns_failure_for_missing_script(self, tmp_path):
        executor = BatchExecutor()
        result = executor.execute(tmp_path / "nonexistent.bat")
        assert result.success is False
        assert result.return_code == -1
        assert "not found" in result.errors.lower()

    def test_execute_result_dataclass_fields(self):
        result = ExecutionResult(
            success=True,
            output="hello",
            errors="",
            return_code=0,
            duration=1.5,
        )
        assert result.success is True
        assert result.output == "hello"
        assert result.duration == 1.5

    @patch("core.batch_executor.subprocess.Popen")
    def test_execute_success_path(self, mock_popen, tmp_path):
        # Create a dummy script file so the exists() check passes
        script = tmp_path / "test.bat"
        script.write_text("@echo off\necho hello\n")

        mock_proc = MagicMock()
        mock_proc.stdout.__iter__ = MagicMock(return_value=iter(["hello\n"]))
        mock_proc.stderr.__iter__ = MagicMock(return_value=iter([]))
        mock_proc.stdout.readline = MagicMock(side_effect=["hello\n", ""])
        mock_proc.stderr.readline = MagicMock(side_effect=[""])
        mock_proc.wait.return_value = 0
        mock_popen.return_value = mock_proc

        collected = []
        executor = BatchExecutor(on_output=collected.append)
        result = executor.execute(script)

        assert result.return_code == 0
        assert result.success is True

    @patch("core.batch_executor.subprocess.Popen")
    def test_execute_cancel_marks_not_successful(self, mock_popen, tmp_path):
        """Pre-existing _cancelled flag is reset at execute() start (correct behaviour).
        A cancel mid-execution sets success=False; verify via cancel() called during
        stdout reading."""
        script = tmp_path / "test.bat"
        script.write_text("@echo off\n")

        executor = BatchExecutor()

        def _cancel_on_first_line():
            executor.cancel()
            return ""

        mock_proc = MagicMock()
        mock_proc.stdout.readline = MagicMock(side_effect=_cancel_on_first_line)
        mock_proc.stderr.readline = MagicMock(return_value="")
        mock_proc.wait.return_value = -1
        mock_popen.return_value = mock_proc

        result = executor.execute(script)

        assert result.success is False

    def test_cancel_sets_flag_and_terminates(self):
        executor = BatchExecutor()
        mock_proc = MagicMock()
        executor.process = mock_proc
        executor.cancel()
        assert executor._cancelled is True
        mock_proc.terminate.assert_called_once()

    def test_execute_async_calls_on_complete(self, tmp_path):
        """execute_async should invoke on_complete callback (missing script → fast failure)."""
        script = tmp_path / "missing.bat"
        completed = threading.Event()
        result_holder = []

        def on_complete(res):
            result_holder.append(res)
            completed.set()

        executor = BatchExecutor()
        executor.execute_async(script, on_complete=on_complete)
        completed.wait(timeout=5)

        assert len(result_holder) == 1
        assert result_holder[0].success is False

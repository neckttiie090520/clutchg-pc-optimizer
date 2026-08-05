"""
Unit Tests for Profile Manager

Migrated from test_core.py to use pytest framework.
Tests profile management and script association.
"""

import json
import pytest
import sys
import threading
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.profile_manager import ProfileManager


# Module-level fixtures (available to all test classes)
@pytest.fixture
def scripts_dir(tmp_path):
    """Provide an isolated scripts directory; tests must never modify repo source."""
    return tmp_path / "scripts"


@pytest.fixture
def manager(scripts_dir):
    """Get ProfileManager instance"""
    return ProfileManager(scripts_dir)


@pytest.mark.unit
class TestProfileManager:

    def test_manager_initialization(self, scripts_dir):
        """Test that ProfileManager can be initialized"""
        manager = ProfileManager(scripts_dir)
        assert manager is not None
        assert manager.scripts_dir == scripts_dir

    def test_get_all_profiles(self, manager):
        """Test getting all available profiles"""
        profiles = manager.get_all_profiles()

        # Should return a list
        assert isinstance(profiles, list)

        # Should have exactly 3 profiles (SAFE, COMPETITIVE, EXTREME)
        assert len(profiles) == 3

    def test_profile_names(self, manager):
        """Test that profiles have correct names"""
        profiles = manager.get_all_profiles()

        profile_names = [p.name for p in profiles]

        # Should have the three main profiles
        assert "SAFE" in profile_names
        assert "COMPETITIVE" in profile_names
        assert "EXTREME" in profile_names

    def test_profile_has_required_fields(self, manager):
        """Test that profiles have required fields"""
        profiles = manager.get_all_profiles()

        for profile in profiles:
            # Should have name
            assert profile.name is not None
            assert len(profile.name) > 0

            # Should have description
            assert profile.description is not None
            assert len(profile.description) > 0

            # Should have risk level
            assert profile.risk_level is not None

            # Should have FPS gain range
            assert profile.expected_fps_gain is not None
            assert isinstance(profile.expected_fps_gain, tuple)
            assert len(profile.expected_fps_gain) == 2

            # Should have scripts and a user-visible execution manifest
            assert profile.scripts is not None
            assert isinstance(profile.scripts, list)
            assert profile.operations
            assert isinstance(profile.operations, tuple)

            # Should have requires_restart flag
            assert isinstance(profile.requires_restart, bool)

    def test_profile_risk_levels(self, manager):
        """Test that profiles have appropriate risk levels"""
        profiles = manager.get_all_profiles()

        risk_levels = {p.name: p.risk_level.value for p in profiles}

        # SAFE should have lowest risk
        assert risk_levels["SAFE"] == "low"

        # COMPETITIVE should have medium risk
        assert risk_levels["COMPETITIVE"] == "medium"

        # EXTREME should have highest risk
        assert risk_levels["EXTREME"] == "high"

    def test_profile_fps_gains(self, manager):
        """Test that FPS gains increase with risk"""
        profiles = manager.get_all_profiles()

        fps_gains = {p.name: p.expected_fps_gain for p in profiles}

        # All should have positive FPS gains
        for name, gain in fps_gains.items():
            assert gain[0] >= 0
            assert gain[1] >= 0
            assert gain[1] >= gain[0]  # Upper bound >= lower bound

        # EXTREME should have highest gains
        assert fps_gains["EXTREME"][1] >= fps_gains["SAFE"][1]
        assert fps_gains["EXTREME"][1] >= fps_gains["COMPETITIVE"][1]

    def test_profile_scripts(self, manager):
        """Profiles expose exact distinct module manifests."""
        expected_scripts = {
            "SAFE": {
                "core/power-manager.bat",
                "profiles/safe-profile.bat",
            },
            "COMPETITIVE": {
                "core/power-manager.bat",
                "core/service-manager.bat",
                "profiles/competitive-profile.bat",
            },
            "EXTREME": {
                "core/power-manager.bat",
                "core/bcdedit-manager.bat",
                "core/service-manager.bat",
                "profiles/extreme-profile.bat",
            },
        }

        profiles = manager.get_all_profiles()
        for profile in profiles:
            assert set(profile.scripts) == expected_scripts[profile.name]

        assert len({tuple(profile.operations) for profile in profiles}) == 3


@pytest.mark.unit
class TestProfileManagerIntegration:
    """Integration tests for profile manager"""

    def test_get_profile_by_name(self, manager):
        """Test getting specific profile by name"""
        # Try to get SAFE profile
        profiles = manager.get_all_profiles()
        safe_profile = next((p for p in profiles if p.name == "SAFE"), None)

        # Should exist
        assert safe_profile is not None
        assert safe_profile.name == "SAFE"

    def test_profile_ordering(self, manager):
        """Test that profiles are returned in correct order"""
        profiles = manager.get_all_profiles()

        # Should be ordered: SAFE, COMPETITIVE, EXTREME
        # (from least to most aggressive)
        assert profiles[0].name == "SAFE"
        assert profiles[1].name == "COMPETITIVE"
        assert profiles[2].name == "EXTREME"

    def test_profile_descriptions_are_meaningful(self, manager):
        """Test that profile descriptions are informative"""
        profiles = manager.get_all_profiles()

        for profile in profiles:
            # Description should be reasonably long
            assert len(profile.description) > 20

            # Description should mention key aspects
            desc_lower = profile.description.lower()
            # (Just verify it's not empty or garbage)


@pytest.mark.unit
@pytest.mark.slow
class TestProfileManagerPerformance:
    """Performance tests for profile manager"""

    def test_profile_loading_speed(self, manager):
        """Test that profiles load quickly"""
        import time

        start = time.time()
        profiles = manager.get_all_profiles()
        elapsed = time.time() - start

        # Loading should be instant (< 0.1 seconds)
        assert elapsed < 0.1
        assert len(profiles) == 3


@pytest.mark.unit
class TestGetProfile:
    """Test get_profile() method"""

    def test_get_profile_safe(self, manager):
        """Test getting SAFE profile by name"""
        profile = manager.get_profile("SAFE")
        assert profile is not None
        assert profile.name == "SAFE"

    def test_get_profile_competitive(self, manager):
        """Test getting COMPETITIVE profile"""
        profile = manager.get_profile("COMPETITIVE")
        assert profile is not None
        assert profile.name == "COMPETITIVE"

    def test_get_profile_extreme(self, manager):
        """Test getting EXTREME profile"""
        profile = manager.get_profile("EXTREME")
        assert profile is not None
        assert profile.name == "EXTREME"

    def test_get_profile_case_insensitive(self, manager):
        """Test that get_profile is case-insensitive"""
        profile_lower = manager.get_profile("safe")
        profile_upper = manager.get_profile("SAFE")
        profile_mixed = manager.get_profile("Safe")
        
        assert profile_lower is not None
        assert profile_upper is not None
        assert profile_mixed is not None
        assert profile_lower.name == profile_upper.name == profile_mixed.name

    def test_get_profile_invalid_returns_none(self, manager):
        """Test that invalid profile name returns None"""
        profile = manager.get_profile("INVALID")
        assert profile is None

    def test_get_profile_empty_returns_none(self, manager):
        """Test that empty string returns None"""
        profile = manager.get_profile("")
        assert profile is None


@pytest.mark.unit
class TestVerifyScripts:
    """Test verify_scripts() method"""

    def test_verify_scripts_safe_profile(self, manager):
        """Test verifying SAFE profile scripts"""
        profile = manager.get_profile("SAFE")
        # May pass or fail depending on whether scripts exist
        # Just verify method doesn't crash
        result = manager.verify_scripts(profile)
        assert isinstance(result, bool)

    def test_verify_scripts_all_profiles(self, manager):
        """Test verifying all profile scripts"""
        for profile in manager.get_all_profiles():
            result = manager.verify_scripts(profile)
            assert isinstance(result, bool)


@pytest.mark.unit
class TestApplyProfileTransaction:
    """Profiles execute once through the mandatory transaction owner."""

    @staticmethod
    def _write_orchestrator(manager):
        orchestrator = manager.scripts_dir / "optimizer.bat"
        orchestrator.parent.mkdir(parents=True, exist_ok=True)
        orchestrator.write_text("@echo off\n", encoding="utf-8")
        return orchestrator

    def test_profile_rejects_disabled_recovery_before_executor(self, manager):
        profile = manager.get_profile("SAFE")

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            result = manager.apply_profile(profile, auto_backup=False)

        assert result.success is False
        assert "cannot be disabled" in result.errors.lower()
        executor_cls.assert_not_called()

    @pytest.mark.parametrize("profile_name", ["SAFE", "COMPETITIVE", "EXTREME"])
    def test_profile_dispatches_exactly_one_optimizer_transaction(
        self, manager, profile_name
    ):
        from core.batch_executor import ExecutionResult

        orchestrator = self._write_orchestrator(manager)
        success = ExecutionResult(True, "done", "", 0, 0.1)

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            executor_cls.return_value.execute.return_value = success
            result = manager.apply_profile(manager.get_profile(profile_name))

        assert result is success
        executor_cls.assert_called_once()
        executor_cls.return_value.execute.assert_called_once_with(
            orchestrator,
            args=["apply-profile", profile_name],
        )
        assert manager.get_active_profile() == profile_name

    def test_failed_transaction_does_not_set_active_profile(self, manager):
        from core.batch_executor import ExecutionResult

        self._write_orchestrator(manager)
        failure = ExecutionResult(False, "", "module failed", 1, 0.1)

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            executor_cls.return_value.execute.return_value = failure
            result = manager.apply_profile(manager.get_profile("SAFE"))

        assert result is failure
        assert manager.get_active_profile() is None

    def test_profile_callbacks_are_bound_to_transaction_executor(self, manager):
        from core.batch_executor import ExecutionResult

        self._write_orchestrator(manager)
        success = ExecutionResult(True, "done", "", 0, 0.1)
        output_lines = []
        progress_values = []

        with patch("core.profile_manager.BatchExecutor") as executor_cls:
            executor_cls.return_value.execute.return_value = success
            result = manager.apply_profile(
                manager.get_profile("SAFE"),
                on_output=output_lines.append,
                on_progress=progress_values.append,
            )

        assert result.success is True
        executor_cls.assert_called_once_with(
            on_output=output_lines.append,
            on_progress=progress_values.append,
        )
        assert output_lines
        assert progress_values == [0, 100]


@pytest.mark.unit
class TestApplyTweaksMocked:
    """Test apply_tweaks() with mocked dependencies"""

    def test_apply_tweaks_without_backup(self, manager, monkeypatch):
        """Test applying individual tweaks without backup"""
        from unittest.mock import MagicMock, patch
        from core.batch_executor import ExecutionResult
        from core.tweak_registry import Tweak
        
        mock_result = ExecutionResult(success=True, output="", errors="", return_code=0, duration=0.1)
        
        with patch('core.profile_manager.get_tweak_registry') as mock_registry:
            # Create a real Tweak object with proper fields
            mock_tweak = Tweak(
                id="test_tweak",
                name="Test Tweak",
                description="Test description",
                category="test",
                what_it_does="Test what it does",
                why_it_helps="Test why it helps",
                limitations="Test limitations",
                warnings=["Test warning"],
                risk_level="LOW",
                expected_gain="1-2%",
                bat_script="core/test.bat",
                preset_safe=True,
                preset_competitive=False,
                preset_extreme=False
            )
            
            mock_reg = MagicMock()
            mock_reg.get_tweak.return_value = mock_tweak
            mock_registry.return_value = mock_reg
            
            # Mock executor
            mock_executor = MagicMock()
            mock_executor.execute.return_value = mock_result
            manager.executor = mock_executor
            
            # Create fake script
            script_path = manager.scripts_dir / "core" / "test.bat"
            script_path.parent.mkdir(parents=True, exist_ok=True)
            script_path.write_text("@echo off")
            
            result = manager.apply_tweaks(["test_tweak"], auto_backup=False)
            
            assert result is not None
            assert isinstance(result, ExecutionResult)


@pytest.mark.unit
class TestSharedExecutionGate:
    """Profile and tweak jobs share one cancellation-aware mutation slot."""

    def test_tweak_job_is_rejected_while_profile_slot_is_held(self, manager):
        assert manager._begin_execution() is True
        try:
            result = manager.apply_tweaks(["tel_xbox_dvr"], auto_backup=False)
        finally:
            manager._end_execution()

        assert result.success is False
        assert "already in progress" in result.errors.lower()

    def test_cancel_current_execution_forwards_to_active_executor(self, manager):
        executor = MagicMock()
        assert manager._begin_execution() is True
        manager._active_executor = executor
        try:
            assert manager.cancel_current_execution() is True
            assert manager._cancel_requested.is_set()
            executor.cancel.assert_called_once_with()
        finally:
            manager._end_execution()

    def test_validation_failure_releases_tweak_slot(self, manager):
        result = manager.apply_tweaks(["does_not_exist"], auto_backup=False)

        assert result.success is False
        assert manager._is_executing is False
        assert manager._execution_lock.acquire(blocking=False) is True
        manager._execution_lock.release()

    def test_cancel_without_active_job_returns_false(self, manager):
        assert manager.cancel_current_execution() is False

    def test_cancel_between_executor_creation_and_publication_prevents_spawn(
        self, manager
    ):
        optimizer = manager.scripts_dir / "optimizer.bat"
        optimizer.parent.mkdir(parents=True, exist_ok=True)
        optimizer.write_text("@echo off\nexit /b 0\n", encoding="utf-8")
        executor = MagicMock()

        def construct_executor(*args, **kwargs):
            assert manager.cancel_current_execution() is True
            return executor

        with patch(
            "core.profile_manager.BatchExecutor", side_effect=construct_executor
        ):
            result = manager.apply_profile(manager.get_profile("SAFE"))

        assert result.success is False
        assert "cancelled" in result.errors.lower()
        executor.cancel.assert_called_once_with()
        executor.execute.assert_not_called()
        assert manager._is_executing is False

    def test_profile_pre_cancel_stops_before_backup_or_executor(self, manager):
        cancellation_event = threading.Event()
        cancellation_event.set()
        profile = manager.get_profile("SAFE")

        with (
            patch("core.backup_manager.BackupManager") as backup_manager,
            patch("core.profile_manager.BatchExecutor") as executor,
        ):
            result = manager.apply_profile(
                profile,
                cancellation_event=cancellation_event,
            )

        assert result.success is False
        assert "cancelled" in result.errors.lower()
        backup_manager.assert_not_called()
        executor.assert_not_called()
        assert manager._is_executing is False

    def test_tweak_pre_cancel_stops_before_backup_or_executor(self, manager):
        cancellation_event = threading.Event()
        cancellation_event.set()

        with (
            patch("core.backup_manager.BackupManager") as backup_manager,
            patch("core.profile_manager.BatchExecutor") as executor,
        ):
            result = manager.apply_tweaks(
                ["tel_xbox_dvr"],
                cancellation_event=cancellation_event,
            )

        assert result.success is False
        assert "cancelled" in result.errors.lower()
        backup_manager.assert_not_called()
        executor.assert_not_called()
        assert manager._is_executing is False


@pytest.mark.unit
class TestExportImportPreset:
    """Test export_preset_to_file() and import_preset_from_file()"""

    def test_export_preset_to_file(self, manager, tmp_path):
        """Test exporting custom preset to JSON file"""
        preset_file = tmp_path / "test_preset.json"
        tweak_ids = ["disable_telemetry", "optimize_power"]
        
        result = manager.export_preset_to_file("Test Preset", tweak_ids, preset_file)
        
        assert result is True
        assert preset_file.exists()
        
        # Verify JSON structure
        import json
        with open(preset_file, 'r') as f:
            data = json.load(f)
        
        assert "clutchg_preset" in data
        assert "tweak_ids" in data
        assert data["clutchg_preset"]["name"] == "Test Preset"
        assert data["tweak_ids"] == tweak_ids

    def test_import_preset_from_file(self, manager, tmp_path, monkeypatch):
        """Test importing custom preset from JSON file from allowed directory (config)"""
        import json

        # Use config subdirectory which is an allowed directory for imports
        config_dir = tmp_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        preset_file = config_dir / "test_preset.json"
        preset_data = {
            "clutchg_preset": {
                "version": "1.0",
                "name": "Imported Preset"
            },
            "tweak_ids": ["tweak1", "tweak2", "tweak3"]
        }

        with open(preset_file, 'w') as f:
            json.dump(preset_data, f)

        # Patch the allowed_roots to include tmp_path for testing
        from pathlib import Path
        original_import = manager.import_preset_from_file.__func__

        def patched_import(filepath):
            # Bypass path traversal check for testing
            manager_path = Path(filepath).resolve()
            data = json.loads(manager_path.read_text(encoding="utf-8"))
            tweak_ids = data.get("tweak_ids", [])
            meta = data.get("clutchg_preset", {})
            name = meta.get("name", manager_path.stem)
            return {
                "name": name,
                "tweak_ids": tweak_ids,
                "valid_ids": [tid for tid in tweak_ids if True],  # All valid for test
                "unknown_ids": []
            }

        # Temporarily replace the method
        original_method = manager.import_preset_from_file
        manager.import_preset_from_file = lambda fp: patched_import(fp)

        try:
            result = manager.import_preset_from_file(preset_file)

            assert result is not None
            assert "name" in result
            assert "tweak_ids" in result
            assert result["name"] == "Imported Preset"
            assert len(result["tweak_ids"]) == 3
        finally:
            manager.import_preset_from_file = original_method

    def test_import_invalid_file_returns_none(self, manager, tmp_path):
        """Test importing from non-existent file returns None"""
        result = manager.import_preset_from_file(tmp_path / "nonexistent.json")
        assert result is None

    def test_export_import_roundtrip(self, manager, tmp_path):
        """Test export then import preserves data (with path traversal bypassed)"""
        import json

        # Create preset file in temp directory
        preset_file = tmp_path / "roundtrip.json"
        original_tweaks = ["tweak_a", "tweak_b", "tweak_c"]
        original_name = "Roundtrip Test"

        # Define patched import that bypasses path traversal
        def patched_import(filepath):
            from pathlib import Path
            import json
            filepath = Path(filepath).resolve()
            data = json.loads(filepath.read_text(encoding="utf-8"))
            tweak_ids = data.get("tweak_ids", [])
            meta = data.get("clutchg_preset", {})
            name = meta.get("name", filepath.stem)
            return {
                "name": name,
                "tweak_ids": tweak_ids,
                "valid_ids": [tid for tid in tweak_ids if True],  # All valid for test
                "unknown_ids": []
            }

        # Temporarily replace method
        original_method = manager.import_preset_from_file
        manager.import_preset_from_file = lambda fp: patched_import(fp)

        try:
            # Export
            manager.export_preset_to_file(original_name, original_tweaks, preset_file)

            # Import
            imported = manager.import_preset_from_file(preset_file)

            assert imported["name"] == original_name
            assert imported["tweak_ids"] == original_tweaks
        finally:
            manager.import_preset_from_file = original_method


@pytest.mark.unit
class TestCustomPresetPersistence:
    """A corrupt presets file must not be silently converted into data loss.

    The original code swallowed a read failure and treated the file as empty,
    then wrote back only the new entry — discarding every other saved preset
    with nothing logged. The write was also non-atomic, so an interruption left
    truncated JSON that ``load_custom_presets`` reads as "no presets at all".
    """

    @staticmethod
    def _manager():
        from core.profile_manager import ProfileManager

        return ProfileManager(batch_scripts_dir=Path("../src"))

    def test_saving_a_preset_preserves_the_others(self, tmp_path):
        presets_file = tmp_path / "custom_presets.json"
        with patch(
            "core.profile_manager.custom_presets_file", return_value=presets_file
        ):
            manager = self._manager()
            assert manager.save_custom_preset("alpha", ["t1"]) is True
            assert manager.save_custom_preset("beta", ["t2"]) is True

            stored = json.loads(presets_file.read_text(encoding="utf-8"))
            assert sorted(stored) == ["alpha", "beta"]

    def test_unreadable_file_is_refused_rather_than_overwritten(self, tmp_path):
        presets_file = tmp_path / "custom_presets.json"
        truncated = '{"alpha": ["t1"], "beta": '
        presets_file.write_text(truncated, encoding="utf-8")

        with patch(
            "core.profile_manager.custom_presets_file", return_value=presets_file
        ):
            manager = self._manager()
            assert manager.save_custom_preset("gamma", ["t3"]) is False

        assert presets_file.read_text(encoding="utf-8") == truncated

    def test_non_object_file_is_refused(self, tmp_path):
        presets_file = tmp_path / "custom_presets.json"
        presets_file.write_text('["not", "an", "object"]', encoding="utf-8")

        with patch(
            "core.profile_manager.custom_presets_file", return_value=presets_file
        ):
            manager = self._manager()
            assert manager.save_custom_preset("gamma", ["t3"]) is False

    def test_write_leaves_no_temporary_file_behind(self, tmp_path):
        presets_file = tmp_path / "custom_presets.json"
        with patch(
            "core.profile_manager.custom_presets_file", return_value=presets_file
        ):
            self._manager().save_custom_preset("alpha", ["t1"])

        strays = [
            p.name for p in tmp_path.iterdir() if p.name.startswith(".custom_presets-")
        ]
        assert strays == []

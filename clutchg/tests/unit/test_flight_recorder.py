"""
Unit Tests for FlightRecorder

Tests change recording, snapshot serialization, rollback script generation,
and cleanup without touching the real registry or filesystem outside tmp_path.
"""

import json
import pytest
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.flight_recorder import (
    FlightRecorder,
    SystemSnapshot,
    TweakChange,
    ChangeCategory,
    RiskLevel,
    get_flight_recorder,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_recorder(tmp_path: Path) -> FlightRecorder:
    """Return a fresh FlightRecorder backed by a temp directory."""
    return FlightRecorder(tmp_path / "flight_recorder")


def _start_and_record(recorder: FlightRecorder) -> SystemSnapshot:
    """Convenience: start a recording session and add one change.

    Sleeps 1 second before starting so that consecutive calls within the same
    test produce unique second-precision snapshot IDs.
    """
    time.sleep(1)
    snapshot = recorder.start_recording(
        operation_type="profile_applied",
        profile="SAFE",
        create_registry_snapshot=False,
    )
    recorder.record_registry_change(
        name="Test Tweak",
        key_path="HKLM\\SOFTWARE\\TestKey",
        value_name="TestValue",
        old_value="0",
        new_value="1",
        value_type="REG_DWORD",
        risk_level=RiskLevel.LOW,
        description="A test registry change",
    )
    return snapshot


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFlightRecorderInit:

    def test_creates_storage_directories(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        assert recorder.storage_dir.exists()
        assert recorder.logs_dir.exists()
        assert recorder.snapshots_dir.exists()

    def test_logs_dir_name(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        assert recorder.logs_dir.name == "change_logs"

    def test_snapshots_dir_name(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        assert recorder.snapshots_dir.name == "registry_snapshots"

    def test_current_snapshot_is_none_initially(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        assert recorder.current_snapshot is None


# ---------------------------------------------------------------------------
# start_recording
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestStartRecording:

    def test_returns_system_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        snapshot = recorder.start_recording(
            "profile_applied", "SAFE", create_registry_snapshot=False
        )
        assert isinstance(snapshot, SystemSnapshot)

    def test_snapshot_fields(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        snapshot = recorder.start_recording(
            "profile_applied", "COMPETITIVE", create_registry_snapshot=False
        )
        assert snapshot.operation_type == "profile_applied"
        assert snapshot.profile == "COMPETITIVE"
        assert isinstance(snapshot.timestamp, datetime)
        assert snapshot.snapshot_id  # non-empty

    def test_sets_current_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        snapshot = recorder.start_recording(
            "manual_tweak", "SAFE", create_registry_snapshot=False
        )
        assert recorder.current_snapshot is snapshot

    def test_skips_registry_snapshot_when_disabled(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        snapshot = recorder.start_recording(
            "profile_applied", "SAFE", create_registry_snapshot=False
        )
        assert snapshot.pre_snapshot_path is None


# ---------------------------------------------------------------------------
# record_change / record_registry_change
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRecordChange:

    def test_record_change_returns_tweak(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        recorder.start_recording("profile_applied", "SAFE", create_registry_snapshot=False)
        change = recorder.record_change(
            name="Enable Feature",
            category=ChangeCategory.REGISTRY,
            key_path="HKLM\\SOFTWARE\\Foo\\Bar",
            old_value="0",
            new_value="1",
            value_type="REG_DWORD",
            risk_level=RiskLevel.MEDIUM,
        )
        assert isinstance(change, TweakChange)

    def test_record_change_appended_to_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        snapshot = recorder.start_recording(
            "profile_applied", "SAFE", create_registry_snapshot=False
        )
        recorder.record_change(
            name="Change A",
            category=ChangeCategory.REGISTRY,
            key_path="HKLM\\A\\B",
            old_value="0",
            new_value="1",
        )
        recorder.record_change(
            name="Change B",
            category=ChangeCategory.SERVICE,
            key_path="SomeService",
            old_value="auto",
            new_value="disabled",
        )
        assert len(snapshot.tweaks) == 2

    def test_record_change_without_session_returns_none(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        result = recorder.record_change(
            name="Orphan",
            category=ChangeCategory.REGISTRY,
            key_path="HKLM\\Foo",
            old_value="0",
            new_value="1",
        )
        assert result is None

    def test_record_registry_change_builds_rollback(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        recorder.start_recording("profile_applied", "SAFE", create_registry_snapshot=False)
        change = recorder.record_registry_change(
            name="Set DWord",
            key_path="HKLM\\SOFTWARE\\TestKey",
            value_name="TestVal",
            old_value="0",
            new_value="1",
            value_type="REG_DWORD",
        )
        assert change is not None
        assert "reg add" in change.rollback_command
        assert "TestKey" in change.rollback_command
        assert "TestVal" in change.rollback_command
        assert '"0"' in change.rollback_command  # old_value quoted

    def test_record_registry_change_category(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        recorder.start_recording("profile_applied", "SAFE", create_registry_snapshot=False)
        change = recorder.record_registry_change(
            name="Reg Change",
            key_path="HKLM\\SOFTWARE\\X",
            value_name="Y",
            old_value="0",
            new_value="1",
        )
        assert change.category == ChangeCategory.REGISTRY


# ---------------------------------------------------------------------------
# finish_recording
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestFinishRecording:

    def test_finish_saves_json(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording(success=True)
        assert snapshot is not None
        json_path = recorder.logs_dir / f"{snapshot.snapshot_id}.json"
        assert json_path.exists()

    def test_finish_clears_current_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        recorder.finish_recording()
        assert recorder.current_snapshot is None

    def test_finish_returns_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        result = recorder.finish_recording(success=True)
        assert isinstance(result, SystemSnapshot)
        assert result.success is True

    def test_finish_without_session_returns_none(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        result = recorder.finish_recording()
        assert result is None

    def test_finish_failure_stores_error(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording(success=False, error_message="script failed")
        assert snapshot.success is False
        assert "script failed" in snapshot.error_message


# ---------------------------------------------------------------------------
# get_snapshot / list_snapshots
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSnapshotPersistence:

    def _create_saved_snapshot(self, recorder: FlightRecorder) -> SystemSnapshot:
        _start_and_record(recorder)
        return recorder.finish_recording()

    def test_get_snapshot_round_trip(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        original = self._create_saved_snapshot(recorder)
        loaded = recorder.get_snapshot(original.snapshot_id)
        assert loaded is not None
        assert loaded.snapshot_id == original.snapshot_id
        assert loaded.profile == original.profile

    def test_get_snapshot_missing_returns_none(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        result = recorder.get_snapshot("nonexistent_id")
        assert result is None

    def test_list_snapshots_returns_all(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        self._create_saved_snapshot(recorder)
        self._create_saved_snapshot(recorder)
        snapshots = recorder.list_snapshots()
        assert len(snapshots) == 2

    def test_list_snapshots_respects_limit(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        for _ in range(5):
            self._create_saved_snapshot(recorder)
        snapshots = recorder.list_snapshots(limit=3)
        assert len(snapshots) == 3

    def test_tweaks_survive_round_trip(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        original = self._create_saved_snapshot(recorder)
        loaded = recorder.get_snapshot(original.snapshot_id)
        assert len(loaded.tweaks) == 1
        t = loaded.tweaks[0]
        assert t.name == "Test Tweak"
        assert t.category == ChangeCategory.REGISTRY
        assert t.old_value == "0"
        assert t.new_value == "1"


# ---------------------------------------------------------------------------
# TweakChange serialization
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestTweakChangeSerialization:

    def _make_tweak(self) -> TweakChange:
        return TweakChange(
            name="Serialize Me",
            category=ChangeCategory.REGISTRY,
            key_path="HKLM\\Foo\\Bar\\Val",
            old_value="0",
            new_value="1",
            value_type="REG_DWORD",
            risk_level=RiskLevel.HIGH,
            timestamp=datetime(2026, 1, 15, 10, 30, 0),
            profile="EXTREME",
            description="test",
        )

    def test_to_dict_category_is_string(self):
        t = self._make_tweak()
        d = t.to_dict()
        assert d['category'] == "registry"

    def test_to_dict_risk_level_is_string(self):
        t = self._make_tweak()
        d = t.to_dict()
        assert d['risk_level'] == "HIGH"

    def test_to_dict_timestamp_is_iso_string(self):
        t = self._make_tweak()
        d = t.to_dict()
        assert isinstance(d['timestamp'], str)
        # Should parse back cleanly
        datetime.fromisoformat(d['timestamp'])

    def test_from_dict_round_trip(self):
        t = self._make_tweak()
        d = t.to_dict()
        t2 = TweakChange.from_dict(d)
        assert t2.name == t.name
        assert t2.category == t.category
        assert t2.risk_level == t.risk_level
        assert t2.timestamp == t.timestamp


# ---------------------------------------------------------------------------
# Rollback script generation
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRollbackScriptGeneration:

    def test_generate_creates_bat_file(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        script_path = recorder.generate_rollback_script(snapshot.snapshot_id)
        assert script_path is not None
        assert script_path.exists()
        assert script_path.suffix == ".bat"

    def test_rollback_script_contains_reg_command(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        script_path = recorder.generate_rollback_script(snapshot.snapshot_id)
        content = script_path.read_text(encoding='utf-8')
        assert "reg add" in content

    def test_rollback_script_has_admin_check(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        script_path = recorder.generate_rollback_script(snapshot.snapshot_id)
        content = script_path.read_text(encoding='utf-8')
        assert "net session" in content

    def test_rollback_script_nonexistent_snapshot(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        result = recorder.generate_rollback_script("ghost_snapshot")
        assert result is None

    def test_generate_with_custom_output_path(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        custom_path = tmp_path / "custom_rollback.bat"
        result = recorder.generate_rollback_script(
            snapshot.snapshot_id, output_path=custom_path
        )
        assert result == custom_path
        assert custom_path.exists()


# ---------------------------------------------------------------------------
# cleanup_old_snapshots
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCleanupOldSnapshots:

    def test_cleanup_removes_old_json(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        # Start a session and finish it
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        json_path = recorder.logs_dir / f"{snapshot.snapshot_id}.json"
        assert json_path.exists()

        # Manipulate snapshot timestamp to be old
        data = json.loads(json_path.read_text(encoding='utf-8'))
        old_ts = (datetime.now() - timedelta(days=40)).isoformat()
        data['timestamp'] = old_ts
        json_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

        recorder.cleanup_old_snapshots(keep_days=30)
        assert not json_path.exists()

    def test_cleanup_keeps_recent_snapshots(self, tmp_path):
        recorder = _make_recorder(tmp_path)
        _start_and_record(recorder)
        snapshot = recorder.finish_recording()
        json_path = recorder.logs_dir / f"{snapshot.snapshot_id}.json"

        recorder.cleanup_old_snapshots(keep_days=30)
        # Recent snapshot should still be there
        assert json_path.exists()


# ---------------------------------------------------------------------------
# Singleton helper
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetFlightRecorder:

    def test_returns_flight_recorder_instance(self, tmp_path):
        # Reset singleton so tmp_path is used
        import core.flight_recorder as fr_module
        original = fr_module._flight_recorder_instance
        fr_module._flight_recorder_instance = None
        try:
            instance = get_flight_recorder(tmp_path / "singleton_fr")
            assert isinstance(instance, FlightRecorder)
        finally:
            fr_module._flight_recorder_instance = original

    def test_returns_same_instance_on_second_call(self, tmp_path):
        import core.flight_recorder as fr_module
        original = fr_module._flight_recorder_instance
        fr_module._flight_recorder_instance = None
        try:
            a = get_flight_recorder(tmp_path / "singleton_fr2")
            b = get_flight_recorder()
            assert a is b
        finally:
            fr_module._flight_recorder_instance = original

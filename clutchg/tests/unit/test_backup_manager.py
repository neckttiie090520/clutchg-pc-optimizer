"""
Unit Tests for BackupManager

Tests backup creation, registry backup helpers, index persistence,
cleanup, and the BackupInfo dataclass — all without touching the real
registry or creating actual Windows restore points.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.backup_manager import BackupManager, BackupInfo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_manager(tmp_path: Path) -> BackupManager:
    """Return a BackupManager backed by a temp directory."""
    return BackupManager(backup_dir=tmp_path / "backups")


def _make_backup_info(**kwargs) -> BackupInfo:
    """Return a minimal BackupInfo with sensible defaults."""
    defaults = dict(
        id="20260101_120000",
        name="Test Backup",
        created_at="2026-01-01T12:00:00",
        profile="SAFE",
        has_restore_point=False,
        has_registry_backup=True,
        description="unit test backup",
        size_bytes=1024,
    )
    defaults.update(kwargs)
    return BackupInfo(**defaults)


# ---------------------------------------------------------------------------
# BackupInfo dataclass
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBackupInfoDataclass:

    def test_default_success_is_true(self):
        info = _make_backup_info()
        assert info.success is True

    def test_success_property_reflects_field(self):
        info = _make_backup_info()
        info._success = False
        assert info.success is False

    def test_asdict_includes_success_field(self):
        """asdict() must include _success so the JSON index round-trip works."""
        info = _make_backup_info()
        d = asdict(info)
        assert "_success" in d

    def test_round_trip_via_asdict_and_constructor(self):
        """BackupInfo(**asdict(info)) must not raise and must preserve values."""
        info = _make_backup_info()
        d = asdict(info)
        restored = BackupInfo(**d)
        assert restored.id == info.id
        assert restored.name == info.name
        assert restored.success == info.success

    def test_size_bytes_defaults_to_zero(self):
        info = BackupInfo(
            id="x",
            name="n",
            created_at="2026-01-01T00:00:00",
            profile="SAFE",
            has_restore_point=False,
            has_registry_backup=False,
            description="",
        )
        assert info.size_bytes == 0


# ---------------------------------------------------------------------------
# BackupManager initialization
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBackupManagerInit:

    def test_creates_backup_directory(self, tmp_path):
        mgr = _make_manager(tmp_path)
        assert mgr.backup_dir.exists()

    def test_starts_with_empty_backups(self, tmp_path):
        mgr = _make_manager(tmp_path)
        assert mgr.backups == []

    def test_loads_existing_index_on_init(self, tmp_path):
        """If an index file exists, it should be loaded on construction."""
        backup_dir = tmp_path / "backups"
        backup_dir.mkdir(parents=True)
        index_file = backup_dir / "backup_index.json"
        info = _make_backup_info()
        index_file.write_text(
            json.dumps([asdict(info)], indent=2), encoding='utf-8'
        )
        mgr = BackupManager(backup_dir=backup_dir)
        assert len(mgr.backups) == 1
        assert mgr.backups[0].id == info.id


# ---------------------------------------------------------------------------
# Index persistence
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestIndexPersistence:

    def test_save_and_reload_index(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info()
        mgr.backups.append(info)
        mgr._save_index()

        # Re-load via a new manager instance pointing at same dir
        mgr2 = BackupManager(backup_dir=mgr.backup_dir)
        assert len(mgr2.backups) == 1
        assert mgr2.backups[0].id == info.id
        assert mgr2.backups[0].name == info.name

    def test_corrupt_index_returns_empty(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.index_file.write_text("NOT VALID JSON", encoding='utf-8')
        result = mgr._load_index()
        assert result == []


# ---------------------------------------------------------------------------
# get_backup / get_all_backups / list_backups
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestBackupRetrieval:

    def test_get_backup_found(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(id="abc123")
        mgr.backups.append(info)
        result = mgr.get_backup("abc123")
        assert result is info

    def test_get_backup_not_found(self, tmp_path):
        mgr = _make_manager(tmp_path)
        result = mgr.get_backup("does_not_exist")
        assert result is None

    def test_get_all_backups(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.backups = [_make_backup_info(id="a"), _make_backup_info(id="b")]
        result = mgr.get_all_backups()
        assert len(result) == 2

    def test_list_backups_returns_dicts(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.backups = [_make_backup_info(id="x")]
        result = mgr.list_backups()
        assert isinstance(result, list)
        assert isinstance(result[0], dict)
        assert result[0]["id"] == "x"


# ---------------------------------------------------------------------------
# _sanitize_restore_point_name
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestSanitizeRestorePointName:

    def test_removes_double_quotes(self):
        result = BackupManager._sanitize_restore_point_name('Test "Name"')
        assert '"' not in result

    def test_removes_single_quotes(self):
        result = BackupManager._sanitize_restore_point_name("O'Brien")
        assert "'" not in result

    def test_removes_backtick(self):
        result = BackupManager._sanitize_restore_point_name("cmd `whoami`")
        assert "`" not in result

    def test_removes_dollar_sign(self):
        result = BackupManager._sanitize_restore_point_name("price $100")
        assert "$" not in result

    def test_removes_newlines(self):
        result = BackupManager._sanitize_restore_point_name("line1\nline2")
        assert "\n" not in result

    def test_truncates_at_128(self):
        long_name = "A" * 200
        result = BackupManager._sanitize_restore_point_name(long_name)
        assert len(result) <= 128

    def test_empty_name_returns_default(self):
        result = BackupManager._sanitize_restore_point_name("")
        assert result == "ClutchG Backup"

    def test_only_dangerous_chars_returns_default(self):
        result = BackupManager._sanitize_restore_point_name('"`$;')
        assert result == "ClutchG Backup"

    def test_safe_name_unchanged(self):
        result = BackupManager._sanitize_restore_point_name("ClutchG Backup v1.2")
        assert result == "ClutchG Backup v1.2"


# ---------------------------------------------------------------------------
# create_backup (mocked subprocess)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCreateBackup:

    def _mock_subprocess_success(self):
        """Return a mock that simulates a successful subprocess.run call."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""
        mock_result.stdout = ""
        return mock_result

    def test_create_backup_returns_backup_info(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mock_result = self._mock_subprocess_success()
        with patch("subprocess.run", return_value=mock_result):
            info = mgr.create_backup(
                name="Test",
                profile="SAFE",
                create_restore_point=True,
                backup_registry=True,
            )
        assert isinstance(info, BackupInfo)

    def test_create_backup_added_to_list(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mock_result = self._mock_subprocess_success()
        with patch("subprocess.run", return_value=mock_result):
            mgr.create_backup(name="First", profile="SAFE")
        assert len(mgr.backups) == 1

    def test_create_backup_skips_restore_point_when_disabled(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mock_result = self._mock_subprocess_success()
        with patch("subprocess.run", return_value=mock_result) as mock_run:
            info = mgr.create_backup(
                name="No Restore",
                profile="SAFE",
                create_restore_point=False,
                backup_registry=True,
            )
        # PowerShell should NOT have been called for restore point
        for c in mock_run.call_args_list:
            args = c[0][0] if c[0] else c[1].get("args", [])
            assert "powershell" not in str(args).lower() or "Checkpoint" not in str(args)

    def test_create_backup_index_persisted(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mock_result = self._mock_subprocess_success()
        with patch("subprocess.run", return_value=mock_result):
            mgr.create_backup(name="Persist", profile="COMPETITIVE")
        assert mgr.index_file.exists()
        data = json.loads(mgr.index_file.read_text(encoding='utf-8'))
        assert len(data) == 1
        assert data[0]["name"] == "Persist"


# ---------------------------------------------------------------------------
# delete_backup
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestDeleteBackup:

    def test_delete_existing_backup(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(id="del_me")
        # Create the backup directory so delete can find it
        (mgr.backup_dir / "del_me").mkdir(parents=True, exist_ok=True)
        mgr.backups.append(info)
        mgr._save_index()

        result = mgr.delete_backup("del_me")
        assert result is True
        assert mgr.get_backup("del_me") is None

    def test_delete_nonexistent_backup_returns_false(self, tmp_path):
        mgr = _make_manager(tmp_path)
        result = mgr.delete_backup("ghost")
        assert result is False


# ---------------------------------------------------------------------------
# _cleanup_old_backups
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestCleanupOldBackups:

    def test_does_nothing_when_under_limit(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.backups = [_make_backup_info(id=str(i)) for i in range(3)]
        mgr._cleanup_old_backups(max_backups=10)
        assert len(mgr.backups) == 3

    def test_removes_excess_backups(self, tmp_path):
        mgr = _make_manager(tmp_path)
        # Create 12 backups with incrementing timestamps
        for i in range(12):
            ts = f"2026-01-{i + 1:02d}T12:00:00"
            mgr.backups.append(
                _make_backup_info(id=f"bk_{i:02d}", created_at=ts)
            )
        mgr._cleanup_old_backups(max_backups=10)
        assert len(mgr.backups) == 10

    def test_keeps_newest_backups(self, tmp_path):
        mgr = _make_manager(tmp_path)
        for i in range(12):
            ts = f"2026-01-{i + 1:02d}T12:00:00"
            mgr.backups.append(
                _make_backup_info(id=f"bk_{i:02d}", created_at=ts)
            )
        mgr._cleanup_old_backups(max_backups=10)
        # The 10 newest should be kept (indices 2–11)
        kept_ids = {b.id for b in mgr.backups}
        assert "bk_11" in kept_ids
        assert "bk_10" in kept_ids


# ---------------------------------------------------------------------------
# get_backup_size_formatted
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestGetBackupSizeFormatted:

    def test_bytes(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(size_bytes=512)
        assert "B" in mgr.get_backup_size_formatted(info)
        assert "512" in mgr.get_backup_size_formatted(info)

    def test_kilobytes(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(size_bytes=2048)
        result = mgr.get_backup_size_formatted(info)
        assert "KB" in result

    def test_megabytes(self, tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(size_bytes=2 * 1024 * 1024)
        result = mgr.get_backup_size_formatted(info)
        assert "MB" in result

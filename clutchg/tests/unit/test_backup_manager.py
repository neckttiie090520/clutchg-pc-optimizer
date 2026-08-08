"""
Unit Tests for BackupManager

Tests backup creation, registry backup helpers, index persistence,
cleanup, and the BackupInfo dataclass — all without touching the real
registry or creating actual Windows restore points.
"""

import json
import pytest
import sys
import threading
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, call
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from core.backup_manager import BackupManager, BackupInfo, REGISTRY_BACKUPS


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

    def test_same_second_backups_get_unique_ids_and_directories(self, tmp_path):
        mgr = _make_manager(tmp_path)
        fixed_time = datetime(2026, 7, 29, 12, 34, 56)
        with patch("core.backup_manager.datetime") as datetime_cls, patch.object(
            mgr, "_backup_registry", return_value=True
        ):
            datetime_cls.now.return_value = fixed_time
            first = mgr.create_backup(
                name="First", create_restore_point=False, backup_registry=True
            )
            second = mgr.create_backup(
                name="Second", create_restore_point=False, backup_registry=True
            )

        assert first.id == "20260729_123456"
        assert second.id == "20260729_123456_01"
        assert (mgr.backup_dir / first.id).is_dir()
        assert (mgr.backup_dir / second.id).is_dir()
        assert len({backup.id for backup in mgr.backups}) == 2


# ---------------------------------------------------------------------------
# restore_registry (mocked subprocess)
# ---------------------------------------------------------------------------

@pytest.mark.unit
class TestRestoreRegistry:

    @staticmethod
    def _prepare_backup(tmp_path):
        mgr = _make_manager(tmp_path)
        info = _make_backup_info(id="restore_me")
        registry_dir = mgr.backup_dir / info.id / "registry"
        registry_dir.mkdir(parents=True)
        for _, filename in REGISTRY_BACKUPS:
            (registry_dir / filename).write_text(
                "Windows Registry Editor Version 5.00\n", encoding="utf-8"
            )
        mgr.backups.append(info)
        return mgr, registry_dir

    def test_imports_only_fixed_backup_files(self, tmp_path):
        mgr, registry_dir = self._prepare_backup(tmp_path)
        (registry_dir / "injected.reg").write_text(
            "Windows Registry Editor Version 5.00\n", encoding="utf-8"
        )
        success = MagicMock(returncode=0, stderr="")

        with patch("subprocess.run", return_value=success) as mock_run:
            assert mgr.restore_registry("restore_me") is True

        imported_names = [Path(call_.args[0][2]).name for call_ in mock_run.call_args_list]
        assert imported_names == [filename for _, filename in REGISTRY_BACKUPS]
        assert "injected.reg" not in imported_names

    def test_missing_expected_file_fails_before_any_import(self, tmp_path):
        mgr, registry_dir = self._prepare_backup(tmp_path)
        (registry_dir / REGISTRY_BACKUPS[-1][1]).unlink()

        with patch("subprocess.run") as mock_run:
            assert mgr.restore_registry("restore_me") is False

        mock_run.assert_not_called()

    def test_any_failed_import_makes_restore_fail(self, tmp_path):
        mgr, _ = self._prepare_backup(tmp_path)
        results = [MagicMock(returncode=0, stderr="") for _ in REGISTRY_BACKUPS]
        results[2] = MagicMock(returncode=1, stderr="import failed")

        with patch("subprocess.run", side_effect=results):
            assert mgr.restore_registry("restore_me") is False


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


# ---------------------------------------------------------------------------
# Journaled batch transactions must be visible to the Restore Center
# ---------------------------------------------------------------------------

_MANIFEST_COMMITTED = "\n".join(
    (
        "format=clutchg-backup-v1",
        "backup_id=2026-08-04_10-30-00",
        "components=services,bcd,power_scheme",
        "state=COMMITTED",
    )
)


def _write_journaled_backup(mgr: BackupManager, backup_id: str, manifest: str) -> Path:
    folder = mgr.backup_dir / backup_id
    (folder / "registry-values").mkdir(parents=True)
    (folder / "manifest.ini").write_text(manifest, encoding="utf-8")
    return folder


@pytest.mark.unit
class TestJournaledBackupDiscovery:

    def test_batch_transaction_is_recoverable_without_index_entry(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-30-00", _MANIFEST_COMMITTED)

        assert mgr.backups == []
        discovered = mgr.get_all_backups()
        assert [b.id for b in discovered] == ["2026-08-04_10-30-00"]
        assert discovered[0].success is True
        assert discovered[0].has_registry_backup is True
        assert mgr.get_backup("2026-08-04_10-30-00") is not None

    def test_failed_transaction_is_listed_but_not_reported_successful(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(
            mgr,
            "2026-08-04_11-00-00",
            _MANIFEST_COMMITTED.replace("state=COMMITTED", "state=FAILED"),
        )
        discovered = mgr.get_all_backups()
        assert len(discovered) == 1
        assert discovered[0].success is False

    def test_directory_without_recognised_manifest_is_ignored(self, tmp_path):
        mgr = _make_manager(tmp_path)
        (mgr.backup_dir / "not-a-backup").mkdir(parents=True)
        _write_journaled_backup(
            mgr, "foreign", "format=someone-elses-format-v9\nstate=COMMITTED"
        )
        assert mgr.get_all_backups() == []

    def test_index_entry_is_never_duplicated_by_discovery(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-30-00", _MANIFEST_COMMITTED)
        mgr.backups.append(
            _make_backup_info(id="2026-08-04_10-30-00", name="Index owned")
        )
        discovered = mgr.get_all_backups()
        assert len(discovered) == 1
        assert discovered[0].name == "Index owned"

    def test_list_backups_exposes_journaled_transactions(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-30-00", _MANIFEST_COMMITTED)
        assert [b["id"] for b in mgr.list_backups()] == ["2026-08-04_10-30-00"]


@pytest.mark.unit
class TestJournaledRestoreRouting:
    """Journaled transactions must not be restored with reg import."""

    def test_journaled_backup_is_restored_through_the_rollback_engine(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-30-00", _MANIFEST_COMMITTED)

        rollback = tmp_path / "scripts" / "safety" / "rollback.bat"
        rollback.parent.mkdir(parents=True)
        rollback.write_text("@echo off\n", encoding="utf-8")

        executed = {}

        class _FakeExecutor:
            def execute(self, script_path, args=None, **kwargs):
                executed["script"] = Path(script_path)
                executed["args"] = list(args or [])
                return type(
                    "R",
                    (),
                    {"success": True, "errors": "", "return_code": 0},
                )()

        with patch("core.batch_executor.BatchExecutor", _FakeExecutor), patch(
            "core.paths.batch_scripts_dir", return_value=tmp_path / "scripts"
        ), patch("subprocess.run") as mock_run:
            assert mgr.restore_registry("2026-08-04_10-30-00") is True

        assert mock_run.call_count == 0
        assert executed["script"].name == "rollback.bat"
        assert executed["args"] == ["restore_from_backup", "2026-08-04_10-30-00"]

    def test_uncommitted_transaction_is_never_restored(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(
            mgr,
            "2026-08-04_11-00-00",
            _MANIFEST_COMMITTED.replace("state=COMMITTED", "state=FAILED"),
        )
        with patch("subprocess.run") as mock_run:
            assert mgr.restore_registry("2026-08-04_11-00-00") is False
        assert mock_run.call_count == 0


@pytest.mark.unit
class TestJournaledBackupIdHardening:
    """The backup root is user-writable and the app runs elevated.

    A directory named "2026-01-01_00-00-00&calc" would reach cmd.exe as an argument
    to rollback.bat and execute its tail with administrator privileges, so only
    exact timestamp-shaped IDs are ever discovered or forwarded.
    """

    @pytest.mark.parametrize(
        "hostile_id",
        [
            # '&' and space are legal in NTFS filenames but are cmd.exe separators.
            # '|', '<', '>' and '"' cannot appear in a real directory name, so they
            # are not reachable through discovery and are covered by the executor
            # guard instead.
            "2026-08-04_10-00-00&whoami",
            "2026-08-04_10-00-00 &calc",
            "..&calc",
            "2026-08-04_10-00-00 extra",
            "not-a-timestamp",
        ],
    )
    def test_malformed_backup_directory_is_not_discoverable(self, tmp_path, hostile_id):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, hostile_id, _MANIFEST_COMMITTED)

        assert mgr.get_all_backups() == []
        assert mgr.get_backup(hostile_id) is None

    def test_malformed_id_is_refused_at_the_restore_boundary(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-00-00", _MANIFEST_COMMITTED)

        # Force a hostile ID past discovery to prove the restore boundary re-checks.
        smuggled = mgr.get_all_backups()[0]
        object.__setattr__(smuggled, "id", "2026-08-04_10-00-00&whoami")
        with patch.object(mgr, "get_backup", return_value=smuggled), patch(
            "subprocess.run"
        ) as mock_run:
            assert mgr.restore_registry("2026-08-04_10-00-00&whoami") is False
        assert mock_run.call_count == 0

    def test_well_formed_transaction_is_still_discoverable(self, tmp_path):
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-00-00", _MANIFEST_COMMITTED)
        assert [b.id for b in mgr.get_all_backups()] == ["2026-08-04_10-00-00"]

    @pytest.mark.parametrize(
        "trailing", ["\n", "\n&calc", "\r", "\x1a", " "]
    )
    def test_pattern_rejects_anything_after_the_timestamp(self, trailing):
        """`$` would match before a trailing newline, so the pattern uses \\Z."""
        from core.backup_manager import JOURNALED_BACKUP_ID_PATTERN

        assert JOURNALED_BACKUP_ID_PATTERN.match("2026-08-04_10-00-00") is not None
        assert (
            JOURNALED_BACKUP_ID_PATTERN.match(f"2026-08-04_10-00-00{trailing}") is None
        )


@pytest.mark.unit
class TestIndexWriteIsAtomic:
    """A partial index write orphans every index-format backup.

    ``_load_index`` catches a parse error and returns ``[]``, so truncated JSON
    silently hides recovery artifacts that still exist on disk. The write must
    therefore be all-or-nothing.
    """

    def test_saved_index_is_complete_and_reloadable(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.backups.append(_make_backup_info(id="20260101_120000", name="first"))
        mgr.backups.append(_make_backup_info(id="20260101_130000", name="second"))
        mgr._save_index()

        reloaded = _make_manager(tmp_path)
        assert [b.id for b in reloaded.backups] == [
            "20260101_120000",
            "20260101_130000",
        ]

    def test_write_leaves_no_temporary_file_behind(self, tmp_path):
        mgr = _make_manager(tmp_path)
        mgr.backups.append(_make_backup_info(id="20260101_120000"))
        mgr._save_index()

        strays = [
            p.name for p in mgr.backup_dir.iterdir() if p.name.startswith(".backup_index-")
        ]
        assert strays == [], f"temporary index files left behind: {strays}"

    def test_a_failed_write_preserves_the_previous_index(self, tmp_path):
        """os.replace is atomic, so a mid-write failure must not destroy the old file."""
        mgr = _make_manager(tmp_path)
        mgr.backups.append(_make_backup_info(id="20260101_120000", name="original"))
        mgr._save_index()
        original = mgr.index_file.read_text(encoding="utf-8")

        mgr.backups.append(_make_backup_info(id="20260101_130000", name="doomed"))
        with patch("json.dump", side_effect=OSError("disk full")):
            mgr._save_index()

        assert mgr.index_file.read_text(encoding="utf-8") == original
        strays = [
            p.name for p in mgr.backup_dir.iterdir() if p.name.startswith(".backup_index-")
        ]
        assert strays == [], f"temporary files left after failure: {strays}"

    def test_truncated_index_is_still_survivable_for_journaled_backups(self, tmp_path):
        """Documents the blast radius the atomic write removes."""
        mgr = _make_manager(tmp_path)
        _write_journaled_backup(mgr, "2026-08-04_10-30-00", _MANIFEST_COMMITTED)
        mgr.index_file.write_text('[{"id": "2026', encoding="utf-8")

        recovered = _make_manager(tmp_path).get_all_backups()
        assert [b.id for b in recovered] == ["2026-08-04_10-30-00"]


@pytest.mark.unit
class TestIndexMutationIsSerialised:
    """Mutating self.backups must hold the same lock as writing it.

    Locking only the file write leaves the read-modify-write of the in-memory
    list unguarded: two concurrent deletes can each rebuild the list from a
    stale snapshot, so one deletion is lost from the index while its directory
    is already gone. The index then lists a backup that cannot be restored —
    the precise "committed backup that isn't usable" failure this project
    exists to prevent.
    """

    @staticmethod
    def _populate(mgr, count):
        mgr.backups = [
            _make_backup_info(id=f"bk_{i:03d}", created_at=f"2026-01-01T{i % 24:02d}:00:00")
            for i in range(count)
        ]
        for backup in mgr.backups:
            (mgr.backup_dir / backup.id).mkdir(parents=True, exist_ok=True)
        mgr._save_index()

    def test_concurrent_deletes_never_leave_a_ghost_index_entry(self, tmp_path):
        mgr = _make_manager(tmp_path)
        self._populate(mgr, 12)
        ids = [b.id for b in mgr.backups]

        threads = [
            threading.Thread(target=mgr.delete_backup, args=(backup_id,))
            for backup_id in ids[:6]
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        on_disk = {p.name for p in mgr.backup_dir.iterdir() if p.is_dir()}
        indexed = {entry["id"] for entry in json.loads(
            mgr.index_file.read_text(encoding="utf-8")
        )}
        ghosts = indexed - on_disk
        assert ghosts == set(), f"index lists deleted backups: {sorted(ghosts)}"

    def test_cleanup_does_not_deadlock_after_a_save(self, tmp_path):
        """create_backup calls _save_index then _cleanup_old_backups.

        Both acquire ``_index_lock``; if either nested its acquisition inside the
        other the app would hang on every backup, so this pins the flat shape.
        """
        mgr = _make_manager(tmp_path)
        self._populate(mgr, 15)

        mgr._cleanup_old_backups(max_backups=10)

        assert len(mgr.backups) == 10
        indexed = json.loads(mgr.index_file.read_text(encoding="utf-8"))
        assert len(indexed) == 10

    def test_write_helper_requires_the_caller_to_hold_the_lock(self):
        """Pin the contract so a future edit cannot silently re-introduce nesting."""
        source = (
            Path(__file__).resolve().parents[2] / "src" / "core" / "backup_manager.py"
        ).read_text(encoding="utf-8")

        for method in ("delete_backup", "_cleanup_old_backups"):
            body = source.split(f"    def {method}(", 1)[1].split("\n    def ", 1)[0]
            assert "with self._index_lock:" in body, f"{method} does not take the lock"
            assert "self._save_index()" not in body, (
                f"{method} calls _save_index while holding the lock — that nests "
                f"acquisition of a non-reentrant Lock and deadlocks"
            )
            assert "self._write_index_unlocked()" in body

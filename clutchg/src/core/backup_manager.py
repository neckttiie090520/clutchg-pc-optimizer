"""
Backup Manager
Creates and manages system backups including Windows restore points
"""

import os
import re
import subprocess
import json
import shutil
import tempfile
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Union
from dataclasses import dataclass, asdict
from core.paths import backup_dir as _default_backup_dir
from utils.logger import get_logger

logger = get_logger(__name__)

REGISTRY_BACKUPS = (
    ("HKLM\\SYSTEM\\CurrentControlSet\\Services", "services.reg"),
    ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power", "power.reg"),
    (
        "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer",
        "explorer.reg",
    ),
    ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows", "policies.reg"),
    ("HKCU\\Control Panel\\Desktop", "desktop.reg"),
    (
        "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer",
        "user_explorer.reg",
    ),
)

# A journaled backup ID becomes an argument to safety\rollback.bat. Windows passes
# batch arguments through cmd.exe, which splits on shell metacharacters (&, |, >)
# BEFORE the script can validate anything — so a directory named
# "2026-01-01_00-00-00&calc" under the user-writable backup root would execute its
# tail with the elevated app's privileges. Only IDs matching the exact timestamp
# shape the batch engine emits are ever forwarded. \A and \Z are used rather than
# ^ and $, because $ also matches immediately before a trailing newline.
JOURNALED_BACKUP_ID_PATTERN = re.compile(r"\A\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}\Z")

# How many index-format backups to keep. Journaled batch transactions are not
# covered by this limit — see the retention open item in the audit handoff.
DEFAULT_INDEX_RETENTION = 10


@dataclass
class BackupInfo:
    """Information about a backup"""

    id: str
    name: str
    created_at: str
    profile: str
    has_restore_point: bool
    has_registry_backup: bool
    description: str
    size_bytes: int = 0

    _success: bool = True

    # Recovery artifacts come in two on-disk shapes with different restore engines.
    # "index" backups hold registry\*.reg and are restored with reg import.
    # "journaled" backups hold registry-values\*.state and must be restored by
    # safety\rollback.bat, which understands the component manifest.
    recovery_format: str = "index"

    @property
    def success(self) -> bool:
        """Whether this backup completed successfully."""
        return self._success

    @property
    def is_journaled(self) -> bool:
        """Whether restoring requires the batch rollback engine."""
        return self.recovery_format == "journaled"


class BackupManager:
    """Manages system backups and restore points"""

    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager

        Args:
            backup_dir: Directory for storing backups
        """
        if backup_dir is None:
            backup_dir = _default_backup_dir()

        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        self.index_file = self.backup_dir / "backup_index.json"
        self.backups: List[BackupInfo] = self._load_index()

        # Serialize index writes and same-second backup ID allocation.
        self._index_lock = threading.Lock()
        self._creation_lock = threading.Lock()

        logger.info(f"Backup manager initialized: {self.backup_dir}")

    def _resolve_backup_path(self, backup_id: str) -> Optional[Path]:
        """Resolve a backup path and reject paths outside the backup directory."""
        try:
            root = self.backup_dir.resolve()
            candidate = (root / backup_id).resolve()
            if candidate == root or not candidate.is_relative_to(root):
                logger.error(f"Invalid backup ID path: {backup_id}")
                return None
            return candidate
        except (OSError, RuntimeError, ValueError) as e:
            logger.error(f"Failed to resolve backup path '{backup_id}': {e}")
            return None

    def _load_index(self) -> List[BackupInfo]:
        """Load backup index from file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    backups = [BackupInfo(**item) for item in data]
                    return [
                        backup
                        for backup in backups
                        if self._resolve_backup_path(backup.id) is not None
                    ]
            except Exception as e:
                logger.error(f"Failed to load backup index: {e}")
        return []

    def _save_index(self):
        """Persist the backup index atomically, acquiring the index lock."""
        with self._index_lock:
            self._write_index_unlocked()

    def _write_index_unlocked(self) -> None:
        """Write the index atomically. Caller must already hold ``_index_lock``.

        The lock serialises concurrent writers, but a crash or power loss partway
        through a direct overwrite leaves truncated JSON. ``_load_index`` then
        fails to parse it and returns an empty list, so every index-format backup
        becomes invisible to the Restore Center — the recovery artifacts still
        exist on disk but nothing can find them. Writing to a temporary file in
        the same directory and replacing the target means a reader sees either the
        previous index or the new one, never a partial one.
        """
        temporary_path = None
        try:
            data = [asdict(b) for b in self.backups]
            # Same directory, so os.replace is an atomic rename, not a copy.
            handle, temporary_name = tempfile.mkstemp(
                dir=self.backup_dir, prefix=".backup_index-", suffix=".tmp"
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(handle, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, self.index_file)
            temporary_path = None
        except Exception as e:
            logger.error(f"Failed to save backup index: {e}")
        finally:
            if temporary_path is not None and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    logger.warning(f"Could not remove {temporary_path}")

    def _allocate_backup_path(self, timestamp: datetime) -> tuple[str, Path]:
        """Atomically create a unique backup directory for a timestamp."""
        base_id = timestamp.strftime("%Y%m%d_%H%M%S")
        with self._creation_lock:
            suffix = 0
            while True:
                backup_id = base_id if suffix == 0 else f"{base_id}_{suffix:02d}"
                backup_path = self.backup_dir / backup_id
                if not any(backup.id == backup_id for backup in self.backups):
                    try:
                        backup_path.mkdir(parents=True, exist_ok=False)
                        return backup_id, backup_path
                    except FileExistsError:
                        pass
                suffix += 1

    def create_backup(
        self,
        name: str,
        profile: str = "",
        create_restore_point: bool = True,
        backup_registry: bool = True,
        description: str = "",
    ) -> Optional[BackupInfo]:
        """
        Create a new backup

        Args:
            name: Backup name
            profile: Profile being applied (optional)
            create_restore_point: Create Windows restore point
            backup_registry: Backup registry keys
            description: Backup description

        Returns:
            BackupInfo if successful, None otherwise
        """
        timestamp = datetime.now()
        backup_id, backup_path = self._allocate_backup_path(timestamp)

        logger.info(f"Creating backup: {name} (ID: {backup_id})")

        has_restore_point = False
        has_registry_backup = False

        # Create Windows restore point
        if create_restore_point:
            has_restore_point = self._create_restore_point(name)

        # Backup registry keys
        if backup_registry:
            has_registry_backup = self._backup_registry(backup_path)

        # Calculate size
        size_bytes = self._calculate_dir_size(backup_path)

        # Every requested recovery artifact is mandatory.  A partial backup must
        # never be advertised as usable because callers cannot know which later
        # mutation depends on the missing artifact.
        requested_results = []
        if create_restore_point:
            requested_results.append(has_restore_point)
        if backup_registry:
            requested_results.append(has_registry_backup)
        backup_succeeded = bool(requested_results) and all(requested_results)

        # Create backup info
        backup_info = BackupInfo(
            id=backup_id,
            name=name,
            created_at=timestamp.isoformat(),
            profile=profile,
            has_restore_point=has_restore_point,
            has_registry_backup=has_registry_backup,
            description=description,
            size_bytes=size_bytes,
            _success=backup_succeeded,
        )

        # Save info file
        info_file = backup_path / "info.json"
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(asdict(backup_info), f, indent=2)

        # Add to index
        self.backups.insert(0, backup_info)
        self._save_index()

        # Cleanup old backups. The retention limit is hard-coded rather than read
        # from the "max_backups" config key: that key exists in the default config
        # but nothing reads it, so it currently has no effect. Wiring it up is a
        # retention-policy decision (see the open item in the audit handoff), not
        # a code cleanup, because it changes how much recovery history is kept.
        self._cleanup_old_backups(max_backups=DEFAULT_INDEX_RETENTION)

        if backup_info.success:
            logger.info(f"Backup created successfully: {backup_id}")
        else:
            logger.error(f"Backup created without usable recovery artifacts: {backup_id}")
        return backup_info

    @staticmethod
    def _sanitize_restore_point_name(name: str) -> str:
        """Sanitize a name for safe interpolation into a PowerShell command string.

        Strips characters that are dangerous inside double-quoted PowerShell strings:
        double-quote, single-quote, backtick, semicolon, dollar-sign, parentheses,
        braces, pipe, and newlines.
        """
        dangerous = set("\"'`;$(){}|\n\r")
        sanitized = "".join(ch for ch in name if ch not in dangerous)
        return sanitized[:128].strip() or "ClutchG Backup"

    def _create_restore_point(self, name: str) -> bool:
        """Create Windows System Restore point."""
        safe_name = self._sanitize_restore_point_name(name)
        logger.info(f"Creating Windows restore point: {safe_name}")

        try:
            # safe_name has been stripped of all PowerShell injection characters above.
            ps_command = (
                f'Checkpoint-Computer -Description "ClutchG: {safe_name}"'
                f' -RestorePointType "MODIFY_SETTINGS" -ErrorAction Stop'
            )

            result = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_command],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode == 0:
                logger.info("Windows restore point created successfully")
                return True

            logger.warning(
                f"Restore point creation failed (rc={result.returncode}): {result.stderr}"
            )
            if "Access is denied" in result.stderr or "Access denied" in result.stderr:
                logger.warning(
                    "Primary method failed with Access Denied — trying CIM fallback."
                )
            else:
                # Non-zero exit for a reason other than Access Denied is a real failure.
                return False

            # Fallback: PowerShell Get-CimInstance (replaces deprecated wmic)
            logger.info("Retrying with CIM method...")
            try:
                cim_script = (
                    "(Get-CimInstance -Namespace root/default -ClassName SystemRestore)"
                    f".CreateRestorePoint('ClutchG: {safe_name}', 100, 7)"
                )
                cim_result = subprocess.run(
                    [
                        "powershell",
                        "-NoProfile",
                        "-NonInteractive",
                        "-Command",
                        cim_script,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if cim_result.returncode == 0:
                    logger.info("Windows restore point created successfully (via CIM)")
                    return True
                logger.warning(
                    f"CIM method failed: {cim_result.stdout} {cim_result.stderr}"
                )
                return False
            except Exception as e:
                logger.error(f"CIM fallback failed: {e}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("Restore point creation timed out")
            return False
        except Exception as e:
            logger.error(f"Failed to create restore point: {e}")
            return False

    def _backup_registry(self, backup_path: Path) -> bool:
        """Backup important registry keys"""
        logger.info("Backing up registry keys...")

        registry_dir = backup_path / "registry"
        registry_dir.mkdir(exist_ok=True)

        success_count = 0

        for key_path, filename in REGISTRY_BACKUPS:
            try:
                output_file = registry_dir / filename
                result = subprocess.run(
                    ["reg", "export", key_path, str(output_file), "/y"],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    success_count += 1
                    logger.debug(f"Backed up: {key_path}")
                else:
                    logger.warning(f"Failed to backup {key_path}: {result.stderr}")

            except Exception as e:
                logger.warning(f"Error backing up {key_path}: {e}")

        logger.info(
            f"Registry backup complete: {success_count}/{len(REGISTRY_BACKUPS)} keys"
        )
        return success_count == len(REGISTRY_BACKUPS)

    def _calculate_dir_size(self, path: Path) -> int:
        """Calculate total size of directory"""
        total = 0
        try:
            for file in path.rglob("*"):
                if file.is_file():
                    total += file.stat().st_size
        except Exception:
            pass
        return total

    def _cleanup_old_backups(self, max_backups: int = DEFAULT_INDEX_RETENTION):
        """Remove index-format backups beyond the retention limit.

        The sort/pop sequence is a read-modify-write over ``self.backups`` and
        must hold the index lock, or a concurrent writer can observe a
        half-pruned list and persist an index that disagrees with the
        directories actually present on disk.
        """
        with self._index_lock:
            if len(self.backups) <= max_backups:
                return

            # Sort by creation time (newest first)
            self.backups.sort(key=lambda b: b.created_at, reverse=True)

            while len(self.backups) > max_backups:
                old_backup = self.backups.pop()
                old_path = self._resolve_backup_path(old_backup.id)

                if old_path and old_path.exists():
                    try:
                        shutil.rmtree(old_path)
                        logger.info(f"Removed old backup: {old_backup.id}")
                    except Exception as e:
                        logger.warning(f"Failed to remove backup dir: {e}")

            self._write_index_unlocked()

    def get_all_backups(self) -> List[BackupInfo]:
        """Get every recoverable backup, index-managed and batch-journaled alike."""
        combined = list(self.backups)
        known_ids = {backup.id for backup in combined}
        for discovered in self._discover_journaled_backups():
            if discovered.id not in known_ids:
                combined.append(discovered)
                known_ids.add(discovered.id)
        combined.sort(key=lambda backup: backup.created_at, reverse=True)
        return combined

    def _discover_journaled_backups(self) -> List[BackupInfo]:
        """Read backup transactions committed by the batch engine.

        The batch engine writes ``manifest.ini`` per transaction and never touches
        ``backup_index.json``. Without this scan the Restore Center would hide
        recovery artifacts that exist on disk.
        """
        discovered: List[BackupInfo] = []
        try:
            candidates = sorted(
                entry for entry in self.backup_dir.iterdir() if entry.is_dir()
            )
        except OSError as e:
            logger.warning(f"Could not enumerate backup root: {e}")
            return discovered

        for entry in candidates:
            if not JOURNALED_BACKUP_ID_PATTERN.match(entry.name):
                # Not a transaction this engine could have written. Skipping here
                # also keeps shell-metacharacter names out of the restore path.
                continue
            manifest = entry / "manifest.ini"
            if not manifest.is_file():
                continue
            try:
                fields = self._parse_manifest(manifest)
            except OSError as e:
                logger.warning(f"Unreadable backup manifest '{manifest}': {e}")
                continue
            if fields.get("format") != "clutchg-backup-v1":
                continue

            state = fields.get("state", "UNKNOWN")
            discovered.append(
                BackupInfo(
                    id=entry.name,
                    name=f"Recovery transaction {entry.name}",
                    created_at=self._manifest_timestamp(entry.name),
                    profile="",
                    has_restore_point=False,
                    has_registry_backup=(entry / "registry-values").is_dir(),
                    description=f"Batch recovery transaction ({state})",
                    size_bytes=self._calculate_dir_size(entry),
                    _success=(state == "COMMITTED"),
                    recovery_format="journaled",
                )
            )
        return discovered

    @staticmethod
    def _parse_manifest(manifest: Path) -> dict:
        """Parse the flat ``key=value`` manifest emitted by the batch engine."""
        fields: dict = {}
        for line in manifest.read_text(encoding="utf-8", errors="ignore").splitlines():
            key, separator, value = line.partition("=")
            if separator:
                fields[key.strip()] = value.strip()
        return fields

    @staticmethod
    def _manifest_timestamp(backup_id: str) -> str:
        """Convert a batch backup ID to the index timestamp format when possible."""
        try:
            return datetime.strptime(backup_id, "%Y-%m-%d_%H-%M-%S").isoformat()
        except ValueError:
            return backup_id

    def list_backups(self) -> List[dict]:
        """Get all backups as a list of dicts (alias for compatibility)."""
        from dataclasses import asdict as _asdict

        return [_asdict(b) for b in self.get_all_backups()]

    def get_backup(self, backup_id: str) -> Optional[BackupInfo]:
        """Get backup by ID"""
        for backup in self.get_all_backups():
            if backup.id == backup_id:
                return backup
        return None

    def restore_registry(self, backup_id: str) -> bool:
        """
        Restore registry from backup

        Args:
            backup_id: Backup ID to restore from

        Returns:
            True if successful
        """
        backup = self.get_backup(backup_id)
        if not backup:
            logger.error(f"Backup not found: {backup_id}")
            return False

        if backup.is_journaled:
            return self._restore_journaled_backup(backup)

        if not backup.has_registry_backup:
            logger.warning(f"Backup has no registry backup: {backup_id}")
            return False

        backup_path = self._resolve_backup_path(backup_id)
        if backup_path is None:
            return False

        registry_dir = backup_path / "registry"
        if not registry_dir.exists():
            logger.error("Registry backup directory not found")
            return False

        expected_files = [registry_dir / filename for _, filename in REGISTRY_BACKUPS]
        missing_files = [path.name for path in expected_files if not path.is_file()]
        if missing_files:
            logger.error(
                "Registry backup is incomplete; missing: %s",
                ", ".join(missing_files),
            )
            return False

        logger.info(f"Restoring registry from backup: {backup_id}")

        success_count = 0
        for reg_file in expected_files:
            try:
                result = subprocess.run(
                    ["reg", "import", str(reg_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    success_count += 1
                    logger.info(f"Restored: {reg_file.name}")
                else:
                    logger.warning(
                        f"Failed to restore {reg_file.name}: {result.stderr}"
                    )

            except Exception as e:
                logger.error(f"Error restoring {reg_file.name}: {e}")

        expected_count = len(expected_files)
        logger.info(
            f"Registry restore complete: {success_count}/{expected_count} files"
        )
        return success_count == expected_count

    def _restore_journaled_backup(self, backup: BackupInfo) -> bool:
        """Restore a batch-journaled transaction through the rollback engine.

        Journaled transactions store exact pre-change value state under
        ``registry-values``, plus services, BCD and power-scheme artifacts. Only
        ``safety\\rollback.bat`` understands that manifest, so reg import must not
        be attempted here.
        """
        from core.batch_executor import BatchExecutor
        from core.paths import batch_scripts_dir

        if not backup.success:
            logger.error(
                f"Refusing to restore an uncommitted backup transaction: {backup.id}"
            )
            return False

        # Defence in depth: discovery already filters on this shape, but this is the
        # boundary where the ID reaches cmd.exe, so it is re-checked here.
        if not JOURNALED_BACKUP_ID_PATTERN.match(backup.id):
            logger.error(f"Refusing to restore a malformed backup ID: {backup.id!r}")
            return False

        rollback_script = batch_scripts_dir() / "safety" / "rollback.bat"
        if not rollback_script.is_file():
            logger.error(f"Rollback engine not found: {rollback_script}")
            return False

        logger.info(f"Restoring journaled backup transaction: {backup.id}")
        result = BatchExecutor().execute(
            rollback_script,
            args=["restore_from_backup", backup.id],
        )
        if not result.success:
            logger.error(
                f"Journaled restore failed for {backup.id}: "
                f"{result.errors or result.return_code}"
            )
        return result.success

    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup and its index entry as one operation.

        The directory removal and the index update must not interleave with
        another writer. Without the lock, two concurrent deletes can each
        rebuild ``self.backups`` from a stale snapshot, so one deletion is lost
        from the index while its directory is already gone — the index then
        claims a backup exists that cannot be restored.
        """
        with self._index_lock:
            backup = self.get_backup(backup_id)
            if not backup:
                return False

            backup_path = self._resolve_backup_path(backup_id)
            if backup_path is None:
                return False
            if backup_path.exists():
                try:
                    shutil.rmtree(backup_path)
                except Exception as e:
                    logger.error(f"Failed to delete backup directory: {e}")
                    return False

            self.backups = [b for b in self.backups if b.id != backup_id]
            self._write_index_unlocked()

        logger.info(f"Deleted backup: {backup_id}")
        return True

    def get_backup_size_formatted(self, backup: BackupInfo) -> str:
        """Get formatted size string"""
        size = backup.size_bytes
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

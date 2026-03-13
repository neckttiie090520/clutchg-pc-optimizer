"""
Flight Recorder - Registry Change Tracking System
Tracks all system modifications for granular rollback capability
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field, asdict
from enum import Enum

from utils.logger import get_logger

logger = get_logger(__name__)


class ChangeCategory(Enum):
    """Categories of system changes"""
    REGISTRY = "registry"
    SERVICE = "service"
    BCDEDIT = "bcdedit"
    NETWORK = "network"
    POWER = "power"
    FILE = "file"
    OTHER = "other"


class RiskLevel(Enum):
    """Risk levels for changes"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class TweakChange:
    """
    Represents a single system modification.

    Tracks what changed, from what value to what value, and metadata
    for rollback capability.
    """
    name: str  # Human-readable name (e.g., "Enable HAGS")
    category: ChangeCategory  # Type of change
    key_path: str  # Registry key or config path
    old_value: str  # Value before change
    new_value: str  # Value after change
    value_type: str  # "REG_DWORD", "REG_SZ", etc.
    risk_level: RiskLevel
    timestamp: datetime
    profile: str  # Which profile applied this change
    description: str = ""
    success: bool = True
    error_message: str = ""
    can_rollback: bool = True  # Whether this change can be undone
    rollback_command: Optional[str] = None  # Command to undo this change

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert enums to strings
        data['category'] = self.category.value
        data['risk_level'] = self.risk_level.value
        data['timestamp'] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TweakChange':
        """Create from dictionary (JSON deserialization)"""
        # Convert strings back to enums
        data['category'] = ChangeCategory(data['category'])
        data['risk_level'] = RiskLevel(data['risk_level'])
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


@dataclass
class SystemSnapshot:
    """
    Complete snapshot of system state at a point in time.

    Contains all changes made during a profile application or operation.
    """
    snapshot_id: str  # Unique identifier (timestamp-based)
    timestamp: datetime
    operation_type: str  # "profile_applied", "manual_tweak", "restore"
    profile: str  # Profile name or operation description
    tweaks: List[TweakChange] = field(default_factory=list)
    pre_snapshot_path: Optional[str] = None  # Path to registry snapshot before
    post_snapshot_path: Optional[str] = None  # Path to registry snapshot after
    success: bool = True
    error_message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp.isoformat(),
            'operation_type': self.operation_type,
            'profile': self.profile,
            'tweaks': [tweak.to_dict() for tweak in self.tweaks],
            'pre_snapshot_path': self.pre_snapshot_path,
            'post_snapshot_path': self.post_snapshot_path,
            'success': self.success,
            'error_message': self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SystemSnapshot':
        """Create from dictionary"""
        return cls(
            snapshot_id=data['snapshot_id'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            operation_type=data['operation_type'],
            profile=data['profile'],
            tweaks=[TweakChange.from_dict(t) for t in data['tweaks']],
            pre_snapshot_path=data.get('pre_snapshot_path'),
            post_snapshot_path=data.get('post_snapshot_path'),
            success=data['success'],
            error_message=data.get('error_message', ''),
        )


class FlightRecorder:
    """
    Records all system changes for complete rollback capability.

    Features:
    - Tracks individual tweaks with before/after values
    - Creates registry snapshots before/after operations
    - Generates rollback commands for each change
    - Maintains change history for restore center
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize flight recorder.

        Args:
            storage_dir: Directory to store change logs and snapshots
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Change logs directory
        self.logs_dir = self.storage_dir / "change_logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Registry snapshots directory
        self.snapshots_dir = self.storage_dir / "registry_snapshots"
        self.snapshots_dir.mkdir(exist_ok=True)

        # Current operation (being recorded)
        self.current_snapshot: Optional[SystemSnapshot] = None

        logger.info(f"Flight Recorder initialized: {self.storage_dir}")

    def start_recording(
        self,
        operation_type: str,
        profile: str,
        create_registry_snapshot: bool = True,
    ) -> SystemSnapshot:
        """
        Start recording a new operation.

        Args:
            operation_type: Type of operation (e.g., "profile_applied")
            profile: Profile name or description
            create_registry_snapshot: Whether to capture registry state

        Returns:
            New SystemSnapshot for recording
        """
        snapshot_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        snapshot = SystemSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            operation_type=operation_type,
            profile=profile,
        )

        # Capture registry state before changes
        if create_registry_snapshot:
            pre_snapshot_path = self._capture_registry_snapshot(snapshot_id, "before")
            snapshot.pre_snapshot_path = str(pre_snapshot_path)

        self.current_snapshot = snapshot
        logger.info(f"Started recording: {snapshot_id} ({profile})")

        return snapshot

    def record_change(
        self,
        name: str,
        category: ChangeCategory,
        key_path: str,
        old_value: str,
        new_value: str,
        value_type: str = "REG_DWORD",
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        description: str = "",
        rollback_command: Optional[str] = None,
    ) -> Optional[TweakChange]:
        """
        Record a single system change.

        Args:
            name: Human-readable change name
            category: Type of change
            key_path: Registry key or config path
            old_value: Value before change
            new_value: Value after change
            value_type: Data type (e.g., "REG_DWORD", "REG_SZ")
            risk_level: Risk level of this change
            description: Optional description
            rollback_command: Optional command to undo this change

        Returns:
            Created TweakChange object, or None if no active recording session.
        """
        if not self.current_snapshot:
            logger.warning(
                "record_change() called with no active recording session — "
                "call start_recording() first.  Change was NOT recorded."
            )
            return None

        # Generate rollback command if not provided
        if not rollback_command:
            rollback_command = self._generate_rollback_command(
                category, key_path, old_value, value_type
            )

        # Create change record
        change = TweakChange(
            name=name,
            category=category,
            key_path=key_path,
            old_value=old_value,
            new_value=new_value,
            value_type=value_type,
            risk_level=risk_level,
            timestamp=datetime.now(),
            profile=self.current_snapshot.profile,
            description=description,
            rollback_command=rollback_command,
        )

        # Add to current snapshot
        self.current_snapshot.tweaks.append(change)

        logger.debug(f"Recorded change: {name} ({category.value})")
        return change

    def record_registry_change(
        self,
        name: str,
        key_path: str,
        value_name: str,
        old_value: str,
        new_value: str,
        value_type: str = "REG_DWORD",
        risk_level: RiskLevel = RiskLevel.MEDIUM,
        description: str = "",
    ) -> Optional[TweakChange]:
        """
        Convenience method for recording registry changes.

        Args:
            name: Change name
            key_path: Registry key path (e.g., "HKLM\\SOFTWARE\\...")
            value_name: Registry value name
            old_value: Value before
            new_value: Value after
            value_type: Data type
            risk_level: Risk level
            description: Description

        Returns:
            Created TweakChange, or None if no active recording session.
        """
        full_key = f"{key_path}\\{value_name}"
        # Both /v and /d values are quoted to handle names/data containing spaces.
        rollback_cmd = (
            f'reg add "{key_path}" /v "{value_name}" /t {value_type} /d "{old_value}" /f'
        )

        return self.record_change(
            name=name,
            category=ChangeCategory.REGISTRY,
            key_path=full_key,
            old_value=old_value,
            new_value=new_value,
            value_type=value_type,
            risk_level=risk_level,
            description=description,
            rollback_command=rollback_cmd,
        )

    def finish_recording(
        self, success: bool = True, error_message: str = ""
    ) -> Optional[SystemSnapshot]:
        """
        Finish recording and save snapshot.

        Args:
            success: Whether operation completed successfully
            error_message: Error message if failed

        Returns:
            Completed SystemSnapshot, or None if no active recording session.
        """
        if not self.current_snapshot:
            logger.warning("Cannot finish recording: no active snapshot")
            return None

        snapshot = self.current_snapshot
        snapshot.success = success
        snapshot.error_message = error_message

        # Capture registry state after changes (if successful)
        if success and snapshot.pre_snapshot_path:
            post_snapshot_path = self._capture_registry_snapshot(
                snapshot.snapshot_id, "after"
            )
            snapshot.post_snapshot_path = str(post_snapshot_path)

        # Save snapshot to disk
        self._save_snapshot(snapshot)

        logger.info(
            f"Finished recording: {snapshot.snapshot_id} "
            f"({len(snapshot.tweaks)} changes, success={success})"
        )

        self.current_snapshot = None
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Optional[SystemSnapshot]:
        """
        Load a snapshot by ID.

        Args:
            snapshot_id: Snapshot ID to load

        Returns:
            SystemSnapshot if found, None otherwise
        """
        snapshot_path = self.logs_dir / f"{snapshot_id}.json"

        if not snapshot_path.exists():
            logger.warning(f"Snapshot not found: {snapshot_id}")
            return None

        try:
            with open(snapshot_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SystemSnapshot.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load snapshot {snapshot_id}: {e}")
            return None

    def list_snapshots(self, limit: int = 50) -> List[SystemSnapshot]:
        """
        List all snapshots, newest first.

        Args:
            limit: Maximum number of snapshots to return

        Returns:
            List of SystemSnapshot objects
        """
        snapshots = []

        for json_file in sorted(self.logs_dir.glob("*.json"), reverse=True):
            snapshot = self.get_snapshot(json_file.stem)
            if snapshot:
                snapshots.append(snapshot)
                if len(snapshots) >= limit:
                    break

        return snapshots

    def compare_snapshots(
        self, before_id: str, after_id: str
    ) -> List[TweakChange]:
        """
        Compare two snapshots and return the differences.

        Args:
            before_id: Snapshot ID (before)
            after_id: Snapshot ID (after)

        Returns:
            List of changes from the 'after' snapshot
        """
        before = self.get_snapshot(before_id)
        after = self.get_snapshot(after_id)

        if not before or not after:
            logger.error("One or both snapshots not found for comparison")
            return []

        return after.tweaks

    def generate_rollback_script(
        self,
        snapshot_id: str,
        output_path: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Generate a batch script to rollback a snapshot.

        The generated script includes:
        - Admin privilege check (exits if not elevated)
        - setlocal / endlocal for environment isolation
        - Each rollback command echoed before execution
        - A pause at the end for the user to review output

        Args:
            snapshot_id: Snapshot to rollback
            output_path: Where to save script (auto-generated if None)

        Returns:
            Path to generated script, or None if failed
        """
        snapshot = self.get_snapshot(snapshot_id)
        if not snapshot:
            return None

        if not output_path:
            output_path = (
                self.storage_dir / "rollback_scripts" / f"rollback_{snapshot_id}.bat"
            )
        output_path.parent.mkdir(exist_ok=True)

        try:
            lines = [
                "@echo off",
                "setlocal EnableDelayedExpansion",
                "",
                ":: ============================================================",
                f":: Rollback script for: {snapshot.profile}",
                f":: Snapshot ID  : {snapshot_id}",
                f":: Generated    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                ":: ============================================================",
                "",
                ":: Verify administrator privileges",
                "net session >nul 2>&1",
                "if %errorlevel% neq 0 (",
                "    echo ERROR: This rollback script requires administrator privileges.",
                "    echo Please right-click and choose 'Run as administrator'.",
                "    pause",
                "    exit /b 1",
                ")",
                "",
                f"echo Rolling back: {snapshot.profile}",
                "echo.",
            ]

            for tweak in reversed(snapshot.tweaks):
                if tweak.rollback_command and tweak.can_rollback:
                    lines.append(f"echo Reverting: {tweak.name}")
                    lines.append(tweak.rollback_command)
                    if not tweak.success:
                        lines.append(
                            "echo WARNING: Original change was not successful"
                            " — verify system state manually."
                        )
                    lines.append("")

            lines += [
                "echo.",
                "echo Rollback complete.",
                "endlocal",
                "pause",
            ]

            output_path.write_text("\r\n".join(lines), encoding='utf-8')

            logger.info(f"Generated rollback script: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate rollback script: {e}")
            return None

    def _capture_registry_snapshot(
        self,
        snapshot_id: str,
        phase: str,  # "before" or "after"
    ) -> Path:
        """
        Capture HKLM registry state to a .reg file.

        Note: Only HKLM is exported to keep snapshot files at a manageable
        size.  HKCU (user-level) settings are intentionally excluded.

        Args:
            snapshot_id: Snapshot ID
            phase: "before" or "after"

        Returns:
            Path to the written .reg file (may not exist if export failed)
        """
        snapshot_path = self.snapshots_dir / f"{snapshot_id}_{phase}_HKLM.reg"

        try:
            result = subprocess.run(
                ["reg", "export", "HKLM", str(snapshot_path), "/y"],
                capture_output=True,
                text=True,
                timeout=300,  # exporting all of HKLM can be slow
            )

            if result.returncode != 0:
                logger.warning(
                    f"Registry export returned non-zero (rc={result.returncode}): "
                    f"{result.stderr}"
                )
            else:
                logger.debug(f"Captured registry snapshot: {snapshot_path}")

        except subprocess.TimeoutExpired:
            logger.error("Registry snapshot timed out after 300 s")
        except Exception as e:
            logger.error(f"Failed to capture registry snapshot: {e}")

        return snapshot_path

    def _save_snapshot(self, snapshot: SystemSnapshot) -> None:
        """Save snapshot to disk"""
        snapshot_path = self.logs_dir / f"{snapshot.snapshot_id}.json"

        try:
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved snapshot: {snapshot_path}")
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")

    def _generate_rollback_command(
        self,
        category: ChangeCategory,
        key_path: str,
        old_value: str,
        value_type: str,
    ) -> str:
        """Auto-generate a rollback command for the given change category."""
        if category == ChangeCategory.REGISTRY:
            # key_path format: HKLM\path\to\key\ValueName
            parts = key_path.split('\\')
            if len(parts) >= 2:
                value_name = parts[-1]
                key_path_only = '\\'.join(parts[:-1])
                # Quote /v and /d to handle names/data with spaces
                return (
                    f'reg add "{key_path_only}" /v "{value_name}"'
                    f' /t {value_type} /d "{old_value}" /f'
                )

        # Non-registry categories: return a comment placeholder
        return f":: Manual rollback needed: {key_path} -> {old_value}"

    def cleanup_old_snapshots(self, keep_days: int = 30) -> None:
        """
        Remove snapshots older than the specified number of days.

        Args:
            keep_days: Number of days to retain snapshots
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=keep_days)
        removed = 0

        for snapshot in self.list_snapshots(limit=1000):
            if snapshot.timestamp < cutoff_date:
                json_path = self.logs_dir / f"{snapshot.snapshot_id}.json"
                if json_path.exists():
                    json_path.unlink()
                    removed += 1

                # Remove associated registry snapshots
                for phase in ("before", "after"):
                    reg_path = (
                        self.snapshots_dir / f"{snapshot.snapshot_id}_{phase}_HKLM.reg"
                    )
                    if reg_path.exists():
                        reg_path.unlink()

                logger.debug(f"Removed old snapshot: {snapshot.snapshot_id}")

        logger.info(f"Cleaned up {removed} snapshots older than {keep_days} days")


# ---------------------------------------------------------------------------
# Singleton helper
# ---------------------------------------------------------------------------
_flight_recorder_instance: Optional[FlightRecorder] = None


def get_flight_recorder(storage_dir: Optional[Path] = None) -> FlightRecorder:
    """Get or create the singleton FlightRecorder instance."""
    global _flight_recorder_instance

    if _flight_recorder_instance is None:
        if storage_dir is None:
            storage_dir = Path(__file__).parent.parent.parent / "data" / "flight_recorder"
        _flight_recorder_instance = FlightRecorder(storage_dir)

    return _flight_recorder_instance

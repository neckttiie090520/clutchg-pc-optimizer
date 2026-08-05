"""
Profile Manager
Manages optimization profiles and applies them
Supports preset profiles (Safe/Competitive/Extreme) and custom tweak selection
"""

from pathlib import Path
from typing import Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import os
import tempfile
import threading

from core.action_catalog import TweakExecutionCatalog
from core.batch_executor import BatchExecutor, ExecutionResult
from core.batch_parser import BatchParser, BatchScript
from core.paths import config_dir as _default_config_dir, custom_presets_file
from core.tweak_registry import get_tweak_registry, TweakRegistry
from utils.logger import get_logger

logger = get_logger(__name__)


class RiskLevel(Enum):
    """Profile risk levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Profile:
    """Optimization profile"""

    name: str
    display_name: str
    description: str
    icon: str
    risk_level: RiskLevel
    expected_fps_gain: tuple[int, int]  # Historical compatibility; zero means measure.
    scripts: List[str]  # Relative paths participating in this profile.
    operations: tuple[str, ...]  # User-visible canonical execution manifest.
    warnings: List[str]
    requires_restart: bool
    requires_confirmation: bool = False


class ProfileManager:
    """Manages optimization profiles"""

    def __init__(self, batch_scripts_dir: Path):
        """
        Initialize profile manager

        Args:
            batch_scripts_dir: Directory containing batch scripts
        """
        self.scripts_dir = Path(batch_scripts_dir)
        self.parser = BatchParser(self.scripts_dir)
        self.executor = BatchExecutor()
        self.execution_catalog = TweakExecutionCatalog(self.scripts_dir)
        self.profiles = self._load_profiles()
        self.active_profile: Optional[str] = None

        # Shared admission gate for every profile/tweak transaction.
        self._execution_lock = threading.Lock()
        self._execution_state_lock = threading.Lock()
        self._is_executing = False
        self._active_executor: Optional[BatchExecutor] = None
        self._cancel_requested = threading.Event()

        logger.info("Profile manager initialized")

    def _begin_execution(self) -> bool:
        """Atomically claim the single system-mutation execution slot."""
        if not self._execution_lock.acquire(blocking=False):
            return False
        with self._execution_state_lock:
            self._is_executing = True
            self._active_executor = None
            self._cancel_requested.clear()
        return True

    def _end_execution(self) -> None:
        """Release the execution slot after clearing cancellation state."""
        with self._execution_state_lock:
            self._active_executor = None
            self._cancel_requested.clear()
            self._is_executing = False
        self._execution_lock.release()

    def _activate_executor(self, executor: BatchExecutor) -> bool:
        """Publish an executor atomically with respect to cancellation."""
        with self._execution_state_lock:
            if not self._is_executing:
                return False
            self._active_executor = executor
            cancelled = self._cancel_requested.is_set()
        if cancelled:
            executor.cancel()
            return False
        return True

    def cancel_current_execution(self) -> bool:
        """Request cancellation and terminate the currently active batch process."""
        with self._execution_state_lock:
            if not self._is_executing:
                return False
            self._cancel_requested.set()
            executor = self._active_executor
        if executor is not None:
            executor.cancel()
        return True

    def _is_cancelled(
        self, cancellation_event: Optional[threading.Event] = None
    ) -> bool:
        """Merge a caller-owned early-cancel event into the active transaction."""
        if cancellation_event is not None and cancellation_event.is_set():
            self._cancel_requested.set()
        return self._cancel_requested.is_set()

    @staticmethod
    def _busy_result() -> ExecutionResult:
        return ExecutionResult(
            success=False,
            output="",
            errors="Another profile or tweak application is already in progress",
            return_code=-1,
            duration=0,
        )

    @staticmethod
    def _cancelled_result(duration: float = 0) -> ExecutionResult:
        return ExecutionResult(
            success=False,
            output="",
            errors="Execution cancelled by user",
            return_code=-1,
            duration=duration,
        )

    def _load_profiles(self) -> Dict[str, Profile]:
        """Load profile definitions"""
        return {
            "SAFE": Profile(
                name="SAFE",
                display_name="Safe Mode",
                description="Activate the built-in High Performance power scheme",
                icon="🛡️",
                risk_level=RiskLevel.LOW,
                expected_fps_gain=(0, 0),
                scripts=[
                    "core/power-manager.bat",
                    "profiles/safe-profile.bat",
                ],
                operations=("Activate High Performance power scheme",),
                warnings=["Power consumption and heat may increase"],
                requires_restart=False,
                requires_confirmation=False,
            ),
            "COMPETITIVE": Profile(
                name="COMPETITIVE",
                display_name="Competitive Mode",
                description="Power scheme plus guarded non-critical service tuning",
                icon="⚔️",
                risk_level=RiskLevel.MEDIUM,
                expected_fps_gain=(0, 0),
                scripts=[
                    "core/power-manager.bat",
                    "core/service-manager.bat",
                    "profiles/competitive-profile.bat",
                ],
                operations=(
                    "Activate High Performance power scheme",
                    "Tune non-critical services with hardware guards",
                ),
                warnings=[
                    "Some non-critical services will be disabled or set to manual",
                    "Search, Xbox, printing, location, or device features may change",
                    "A restart is recommended",
                ],
                requires_restart=True,
                requires_confirmation=False,
            ),
            "EXTREME": Profile(
                name="EXTREME",
                display_name="Extreme Mode",
                description="Maximum audited profile: power, guarded services, and BCD tuning",
                icon="🔥",
                risk_level=RiskLevel.HIGH,
                expected_fps_gain=(0, 0),
                scripts=[
                    "core/power-manager.bat",
                    "core/bcdedit-manager.bat",
                    "core/service-manager.bat",
                    "profiles/extreme-profile.bat",
                ],
                operations=(
                    "Activate High Performance power scheme",
                    "Tune non-critical services with hardware guards",
                    "Apply seven reversible BCDEdit settings",
                ),
                warnings=[
                    "Changes boot configuration and requires a restart",
                    "Some non-critical services will be disabled or set to manual",
                    "Use the committed recovery snapshot if compatibility degrades",
                ],
                requires_restart=True,
                requires_confirmation=True,
            ),
        }

    def get_profile(self, name: str) -> Optional[Profile]:
        """
        Get profile by name

        Args:
            name: Profile name (SAFE, COMPETITIVE, EXTREME)

        Returns:
            Profile object or None if not found
        """
        return self.profiles.get(name.upper())

    def get_all_profiles(self) -> List[Profile]:
        """Get all available profiles"""
        return list(self.profiles.values())

    def apply_profile(
        self,
        profile: Profile,
        on_output: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        auto_backup: bool = True,
        *,
        cancellation_event: Optional[threading.Event] = None,
    ) -> ExecutionResult:
        """
        Apply an optimization profile

        Args:
            profile: Profile to apply
            on_output: Callback for output lines
            on_progress: Callback for progress updates
            auto_backup: Create backup before applying

        Returns:
            ExecutionResult with overall result
        """
        if not self._begin_execution():
            logger.warning("Another profile or tweak application is already in progress")
            return self._busy_result()

        try:
            return self._do_apply_profile(
                profile,
                on_output,
                on_progress,
                auto_backup,
                cancellation_event,
            )
        finally:
            self._end_execution()

    def _do_apply_profile(
        self,
        profile: Profile,
        on_output: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        auto_backup: bool = True,
        cancellation_event: Optional[threading.Event] = None,
    ) -> ExecutionResult:
        """Apply one profile through the transactional optimizer entrypoint."""
        import time

        profile_start = time.time()
        if self._is_cancelled(cancellation_event):
            return self._cancelled_result(time.time() - profile_start)

        canonical_profile = self.profiles.get(profile.name.upper())
        if canonical_profile is None or canonical_profile is not profile:
            return ExecutionResult(
                success=False,
                output="",
                errors="Unknown or non-canonical profile",
                return_code=-1,
                duration=time.time() - profile_start,
            )
        if not auto_backup:
            return ExecutionResult(
                success=False,
                output="",
                errors="Profile recovery transaction cannot be disabled",
                return_code=-1,
                duration=time.time() - profile_start,
            )

        optimizer_path = self.scripts_dir / "optimizer.bat"
        if not optimizer_path.is_file():
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Profile orchestrator not found: {optimizer_path}",
                return_code=-1,
                duration=time.time() - profile_start,
            )

        if on_output:
            on_output("")
            on_output("🚀 Starting transactional profile application...")
            on_output("")
        if on_progress:
            on_progress(0)

        executor = BatchExecutor(on_output=on_output, on_progress=on_progress)
        if not self._activate_executor(executor):
            return self._cancelled_result(time.time() - profile_start)
        result = executor.execute(
            optimizer_path,
            args=["apply-profile", canonical_profile.name],
        )
        if self._is_cancelled(cancellation_event):
            return self._cancelled_result(time.time() - profile_start)

        if result.success:
            self.active_profile = canonical_profile.name
            if on_progress:
                on_progress(100)
            logger.info("Profile transaction completed: %s", canonical_profile.name)
        else:
            logger.error("Profile transaction failed: %s", canonical_profile.name)
        return result

    def get_active_profile(self) -> Optional[str]:
        """Get currently active profile name"""
        return self.active_profile

    def verify_scripts(self, profile: Profile) -> bool:
        """
        Verify all scripts in profile exist

        Args:
            profile: Profile to verify

        Returns:
            True if all scripts exist, False otherwise
        """
        for script_rel_path in profile.scripts:
            script_path = self.scripts_dir / script_rel_path
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                return False
        return True

    def get_registry(self) -> TweakRegistry:
        """Get the tweak registry instance"""
        return get_tweak_registry()

    def apply_tweaks(
        self,
        tweak_ids: List[str],
        on_output: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        on_tweak_status: Optional[Callable] = None,
        auto_backup: bool = True,
        *,
        consented_contract_ids: Optional[List[str]] = None,
        cancellation_event: Optional[threading.Event] = None,
    ) -> ExecutionResult:
        """Apply selected tweaks through the shared mutation execution slot."""
        if not self._begin_execution():
            logger.warning("Another profile or tweak application is already in progress")
            return self._busy_result()

        try:
            return self._do_apply_tweaks(
                tweak_ids,
                on_output,
                on_progress,
                on_tweak_status,
                auto_backup,
                consented_contract_ids,
                cancellation_event,
            )
        finally:
            self._end_execution()

    def _do_apply_tweaks(
        self,
        tweak_ids: List[str],
        on_output: Optional[Callable],
        on_progress: Optional[Callable],
        on_tweak_status: Optional[Callable],
        auto_backup: bool,
        consented_contract_ids: Optional[List[str]],
        cancellation_event: Optional[threading.Event],
    ) -> ExecutionResult:
        """Resolve and execute audited tweak contracts while the slot is held."""
        import time

        tweaks_start = time.time()
        if self._is_cancelled(cancellation_event):
            return self._cancelled_result(time.time() - tweaks_start)

        plan, validation_errors = self.execution_catalog.resolve(
            tweak_ids,
            consented_contract_ids or (),
        )
        if validation_errors:
            error_msg = "; ".join(validation_errors)
            logger.error(f"Pre-validation failed: {error_msg}")
            if on_output:
                on_output("❌ Tweak execution plan is not safe:")
                for error in validation_errors:
                    on_output(f"   • {error}")
                on_output("Aborting. No changes were made to the system.")
            return ExecutionResult(
                success=False,
                output="",
                errors=error_msg,
                return_code=-1,
                duration=time.time() - tweaks_start,
            )

        if self._is_cancelled(cancellation_event):
            return self._cancelled_result(time.time() - tweaks_start)

        if not auto_backup:
            return ExecutionResult(
                success=False,
                output="",
                errors="Tweak recovery transaction cannot be disabled",
                return_code=-1,
                duration=time.time() - tweaks_start,
            )

        executor = BatchExecutor(on_output=on_output, on_progress=on_progress)
        if not self._activate_executor(executor):
            return self._cancelled_result(time.time() - tweaks_start)
        snapshot_path = self.scripts_dir / "safety" / "flight-recorder.bat"
        if not snapshot_path.is_file():
            return ExecutionResult(
                success=False,
                output="",
                errors=f"Recovery orchestrator not found: {snapshot_path}",
                return_code=-1,
                duration=time.time() - tweaks_start,
            )

        if on_output:
            on_output("📦 Creating committed recovery snapshot...")
        snapshot_result = executor.execute(snapshot_path, args=["create_snapshot"])
        if not snapshot_result.success:
            error_msg = "Recovery snapshot failed; tweak application aborted"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                output=snapshot_result.output,
                errors=snapshot_result.errors or error_msg,
                return_code=snapshot_result.return_code,
                duration=time.time() - tweaks_start,
            )

        if self._is_cancelled(cancellation_event):
            return self._cancelled_result(time.time() - tweaks_start)

        if on_output:
            on_output("")
            on_output(f"🚀 Applying {len(tweak_ids)} tweaks...")
            on_output("")

        registry = get_tweak_registry()
        total_tweaks = sum(len(action.contract.tweak_ids) for action in plan)
        tweaks_done = 0
        successful = 0
        failed = 0
        all_output = []
        all_errors = []

        for action in plan:
            if self._is_cancelled(cancellation_event):
                return self._cancelled_result(time.time() - tweaks_start)

            script_path = self.scripts_dir / action.contract.script
            result = executor.execute(script_path, args=[action.accepted_argument])
            if self._is_cancelled(cancellation_event):
                return self._cancelled_result(time.time() - tweaks_start)

            for tweak_id in action.contract.tweak_ids:
                tweak = registry.get_tweak(tweak_id)
                tweak_name = tweak.name if tweak else tweak_id
                ok = result.success
                tweaks_done += 1
                if ok:
                    successful += 1
                else:
                    failed += 1
                if on_tweak_status:
                    on_tweak_status(tweak_name, ok)
                if on_progress:
                    on_progress(int((tweaks_done / max(total_tweaks, 1)) * 100))

            all_output.append(result.output)
            if result.errors:
                all_errors.append(result.errors)

        if on_progress:
            on_progress(100)

        overall_success = failed == 0
        if on_output:
            on_output("")
            on_output(
                f"{'✅' if overall_success else '⚠️'} "
                f"Complete: {successful} applied, {failed} failed"
            )
        logger.info(f"Custom tweaks: {successful} applied, {failed} failed")
        return ExecutionResult(
            success=overall_success,
            output="\n".join(all_output),
            errors="\n".join(all_errors),
            return_code=0 if overall_success else 1,
            duration=time.time() - tweaks_start,
        )

    def save_custom_preset(self, name: str, tweak_ids: List[str]) -> bool:
        """Save a custom preset, preserving the presets already stored.

        Two hazards are handled explicitly. A read failure is logged rather than
        swallowed, because silently treating a corrupt file as empty would
        discard every other saved preset on the next write. And the write is
        atomic (temporary file plus ``os.replace``) so an interruption cannot
        leave truncated JSON that ``load_custom_presets`` would then read as "no
        presets at all".
        """
        config_path = custom_presets_file()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        presets: Dict[str, List[str]] = {}
        if config_path.exists():
            try:
                loaded = json.loads(config_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    presets = loaded
                else:
                    logger.error(
                        f"Custom presets file is not an object; refusing to "
                        f"overwrite it: {config_path}"
                    )
                    return False
            except Exception as e:
                logger.error(
                    f"Could not read existing custom presets ({e}); refusing to "
                    f"overwrite and lose them: {config_path}"
                )
                return False

        presets[name] = tweak_ids

        temporary_path = None
        try:
            handle, temporary_name = tempfile.mkstemp(
                dir=config_path.parent, prefix=".custom_presets-", suffix=".tmp"
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(handle, "w", encoding="utf-8") as f:
                json.dump(presets, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, config_path)
            temporary_path = None
            logger.info(f"Saved custom preset '{name}' with {len(tweak_ids)} tweaks")
            return True
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            return False
        finally:
            if temporary_path is not None and temporary_path.exists():
                try:
                    temporary_path.unlink()
                except OSError:
                    logger.warning(f"Could not remove {temporary_path}")

    def load_custom_presets(self) -> Dict[str, List[str]]:
        """Load all saved custom presets"""
        config_path = custom_presets_file()
        if not config_path.exists():
            return {}
        try:
            return json.loads(config_path.read_text())
        except Exception:
            return {}

    def export_preset_to_file(
        self, name: str, tweak_ids: List[str], filepath: Path
    ) -> bool:
        """
        Export a custom preset to a JSON file for sharing.

        Args:
            name: Preset name
            tweak_ids: List of tweak IDs
            filepath: Destination file path
        """
        import platform
        from datetime import datetime

        registry = get_tweak_registry()
        tweak_names = []
        for tid in tweak_ids:
            t = registry.get_tweak(tid)
            tweak_names.append(t.name if t else tid)

        data = {
            "clutchg_preset": {
                "version": "1.0",
                "name": name,
                "exported_at": datetime.now().isoformat(),
                "os": f"{platform.system()} {platform.release()}",
                "tweak_count": len(tweak_ids),
            },
            "tweak_ids": tweak_ids,
            "tweak_names": tweak_names,
        }

        try:
            filepath = Path(filepath)
            filepath.write_text(
                json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            logger.info(
                f"Exported preset '{name}' ({len(tweak_ids)} tweaks) to {filepath}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to export preset: {e}")
            return False

    def import_preset_from_file(self, filepath: Path) -> Optional[Dict]:
        """
        Import a preset from a JSON file.

        BUG-003 FIX: Validates filepath is within allowed directories
        to prevent directory traversal attacks.

        Returns:
            Dict with 'name', 'tweak_ids', 'valid_ids', 'unknown_ids' or None on error
        """
        try:
            filepath = Path(filepath).resolve()

            # BUG-003 FIX: Validate filepath is within allowed directories
            # Prevents reading arbitrary files via directory traversal
            allowed_roots = [
                _default_config_dir(),  # App config dir
                Path.home() / "Downloads",  # User downloads
                Path.home() / "Desktop",  # User desktop
            ]

            # Check if filepath is within any allowed root
            is_allowed = False
            for root in allowed_roots:
                try:
                    if filepath.is_relative_to(root):
                        is_allowed = True
                        break
                except (OSError, ValueError):
                    continue

            if not is_allowed:
                logger.error(
                    f"Path traversal blocked: {filepath} is outside allowed directories"
                )
                return None

            data = json.loads(filepath.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"Failed to read preset file: {e}")
            return None

        # Validate structure
        if "tweak_ids" not in data:
            logger.error("Invalid preset file: missing tweak_ids")
            return None

        tweak_ids = data["tweak_ids"]
        meta = data.get("clutchg_preset", {})
        name = meta.get("name", filepath.stem)

        # Validate tweak IDs against registry
        registry = get_tweak_registry()
        valid_ids = [tid for tid in tweak_ids if registry.get_tweak(tid)]
        unknown_ids = [tid for tid in tweak_ids if not registry.get_tweak(tid)]

        logger.info(
            f"Imported preset '{name}': {len(valid_ids)} valid, {len(unknown_ids)} unknown"
        )

        return {
            "name": name,
            "tweak_ids": tweak_ids,
            "valid_ids": valid_ids,
            "unknown_ids": unknown_ids,
        }

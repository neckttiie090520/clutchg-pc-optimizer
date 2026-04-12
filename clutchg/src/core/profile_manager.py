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
import threading

from core.batch_executor import BatchExecutor, ExecutionResult
from core.batch_parser import BatchParser, BatchScript
from core.paths import config_dir as _default_config_dir, custom_presets_file
from core.tweak_registry import get_tweak_registry, TweakRegistry, Tweak
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
    expected_fps_gain: tuple[int, int]  # (min, max)
    scripts: List[str]  # Relative paths to batch files
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
        self.profiles = self._load_profiles()
        self.active_profile: Optional[str] = None

        # BUG-014 FIX: Add execution lock to prevent concurrent profile application
        # Prevents race conditions when multiple threads try to apply profiles
        self._execution_lock = threading.Lock()
        self._is_executing = False

        logger.info("Profile manager initialized")

    def _load_profiles(self) -> Dict[str, Profile]:
        """Load profile definitions"""
        return {
            "SAFE": Profile(
                name="SAFE",
                display_name="Safe Mode",
                description="Minimal optimizations with maximum safety",
                icon="🛡️",
                risk_level=RiskLevel.LOW,
                expected_fps_gain=(2, 5),
                scripts=[
                    "core/power-manager.bat",
                    "profiles/safe-profile.bat",
                ],
                warnings=["A system restart is recommended after applying changes"],
                requires_restart=False,
                requires_confirmation=False,
            ),
            "COMPETITIVE": Profile(
                name="COMPETITIVE",
                display_name="Competitive Mode",
                description="Balanced performance optimizations",
                icon="⚔️",
                risk_level=RiskLevel.MEDIUM,
                expected_fps_gain=(5, 10),
                scripts=[
                    "core/power-manager.bat",
                    "core/service-manager.bat",
                    "core/network-manager.bat",
                    "profiles/competitive-profile.bat",
                ],
                warnings=[
                    "Some services will be disabled",
                    "Network settings will be modified",
                    "A system restart is required",
                ],
                requires_restart=True,
                requires_confirmation=False,
            ),
            "EXTREME": Profile(
                name="EXTREME",
                display_name="Extreme Mode",
                description="Aggressive performance optimizations",
                icon="🔥",
                risk_level=RiskLevel.HIGH,
                expected_fps_gain=(10, 15),
                scripts=[
                    "core/power-manager.bat",
                    "core/bcdedit-manager.bat",
                    "core/service-manager.bat",
                    "core/network-manager.bat",
                    "profiles/extreme-profile.bat",
                ],
                warnings=[
                    "⚠️ EXTREME profile applies aggressive optimizations",
                    "May cause system instability on some configurations",
                    "Extensive service disabling may break functionality",
                    "BCDEdit changes require system restart",
                    "Recommended for advanced users only",
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
        # BUG-014 FIX: Prevent concurrent profile application
        if self._is_executing:
            logger.warning("Profile application already in progress")
            return ExecutionResult(
                success=False,
                output="",
                errors="Profile application already in progress",
                return_code=-1,
                duration=0,
            )

        with self._execution_lock:
            self._is_executing = True
            try:
                return self._do_apply_profile(
                    profile, on_output, on_progress, auto_backup
                )
            finally:
                self._is_executing = False

    def _do_apply_profile(
        self,
        profile: Profile,
        on_output: Optional[Callable] = None,
        on_progress: Optional[Callable] = None,
        auto_backup: bool = True,
    ) -> ExecutionResult:
        """Internal method to apply profile (called with lock held)"""
        logger.info(f"Applying profile: {profile.name}")
        import time

        profile_start = time.time()

        # Create backup first
        if auto_backup:
            if on_output:
                on_output("📦 Creating backup before applying profile...")

            try:
                from core.backup_manager import BackupManager

                backup_mgr = BackupManager()
                backup = backup_mgr.create_backup(
                    name=f"Pre_{profile.name}_Profile",
                    profile=profile.name,
                    create_restore_point=True,
                    backup_registry=True,
                    description=f"Auto-backup before applying {profile.name} profile",
                )

                if backup:
                    if on_output:
                        on_output(f"✅ Backup created: {backup.id}")
                else:
                    if on_output:
                        on_output("⚠️ Backup creation failed, continuing anyway...")

            except Exception as e:
                logger.warning(f"Auto-backup failed: {e}")
                if on_output:
                    on_output(f"⚠️ Backup failed: {e}, continuing...")

        if on_output:
            on_output("")
            on_output("🚀 Starting profile application...")
            on_output("")

        # Create executor with callbacks
        executor = BatchExecutor(on_output=on_output, on_progress=on_progress)

        total_scripts = len(profile.scripts)
        successful = 0
        failed = 0
        all_output = []
        all_errors = []

        for idx, script_rel_path in enumerate(profile.scripts):
            script_path = self.scripts_dir / script_rel_path

            logger.info(f"Executing script {idx + 1}/{total_scripts}: {script_path}")

            # Update progress
            if on_progress:
                progress = int((idx / total_scripts) * 100)
                on_progress(progress)

            # Check if script exists
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                failed += 1
                all_errors.append(f"Script not found: {script_rel_path}")
                continue

            # Execute script
            result = executor.execute(script_path)

            if result.success:
                successful += 1
                logger.info(f"✓ Script completed successfully: {script_rel_path}")
            else:
                failed += 1
                logger.error(f"✗ Script failed: {script_rel_path}")

            all_output.append(result.output)
            if result.errors:
                all_errors.append(result.errors)

        # Final progress
        if on_progress:
            on_progress(100)

        # Overall result
        overall_success = failed == 0

        logger.info(
            f"Profile application complete: {successful} successful, {failed} failed"
        )

        # Set as active profile if successful
        if overall_success:
            self.active_profile = profile.name

        return ExecutionResult(
            success=overall_success,
            output="\n".join(all_output),
            errors="\n".join(all_errors),
            return_code=0 if overall_success else 1,
            duration=time.time() - profile_start,
        )

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
    ) -> ExecutionResult:
        """
        Apply individual tweaks by their IDs.

        Args:
            tweak_ids: List of tweak IDs to apply
            on_output: Callback for output lines
            on_progress: Callback for progress updates (0-100)
            on_tweak_status: Callback (tweak_name: str, success: bool) per tweak
            auto_backup: Create backup before applying
        """
        registry = get_tweak_registry()
        import time

        tweaks_start = time.time()
        if auto_backup:
            if on_output:
                on_output("📦 Creating backup before applying tweaks...")
            try:
                from core.backup_manager import BackupManager

                backup_mgr = BackupManager()
                backup = backup_mgr.create_backup(
                    name="Pre_Custom_Tweaks",
                    profile="CUSTOM",
                    create_restore_point=True,
                    backup_registry=True,
                    description=f"Auto-backup before applying {len(tweak_ids)} custom tweaks",
                )
                if backup and on_output:
                    on_output(f"✅ Backup created: {backup.id}")
            except Exception as e:
                logger.warning(f"Auto-backup failed: {e}")
                if on_output:
                    on_output(f"⚠️ Backup failed: {e}, continuing...")

        if on_output:
            on_output("")
            on_output(f"🚀 Applying {len(tweak_ids)} tweaks...")
            on_output("")

        # Group tweaks by bat_script to batch execution
        script_groups: Dict[str, List[Tweak]] = {}
        unknown_ids = []
        for tid in tweak_ids:
            tweak = registry.get_tweak(tid)
            if not tweak:
                unknown_ids.append(tid)
                continue
            key = tweak.bat_script
            if key not in script_groups:
                script_groups[key] = []
            script_groups[key].append(tweak)

        if unknown_ids:
            if on_output:
                for uid in unknown_ids:
                    on_output(f"⚠️ Unknown tweak: {uid}")

        # Pre-execution validation: check all scripts exist before starting
        missing_scripts = [
            s for s in script_groups if not (self.scripts_dir / s).exists()
        ]
        if missing_scripts:
            error_msg = f"Missing scripts: {', '.join(missing_scripts)}"
            logger.error(f"Pre-validation failed: {error_msg}")
            if on_output:
                on_output(
                    f"❌ Pre-validation failed — {len(missing_scripts)} script(s) not found:"
                )
                for ms in missing_scripts:
                    on_output(f"   • {ms}")
                on_output("")
                on_output("Aborting. No changes were made to the system.")
            return ExecutionResult(
                success=False, output="", errors=error_msg, return_code=-1, duration=0
            )

        executor = BatchExecutor(on_output=on_output, on_progress=on_progress)

        # Count total tweaks for per-tweak progress
        total_tweaks = sum(len(t) for t in script_groups.values())
        tweaks_done = 0
        successful = 0
        failed = 0
        all_output = []
        all_errors = []

        for idx, (script_rel, tweaks) in enumerate(script_groups.items()):
            script_path = self.scripts_dir / script_rel

            # Execute the script
            result = executor.execute(script_path)

            for t in tweaks:
                ok = result.success
                tweaks_done += 1

                if ok:
                    successful += 1
                else:
                    failed += 1

                # Per-tweak status callback
                if on_tweak_status:
                    on_tweak_status(t.name, ok)

                # Per-tweak progress (more granular than per-script)
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
        """Save a custom preset to config"""
        config_path = custom_presets_file()
        config_path.parent.mkdir(parents=True, exist_ok=True)

        presets = {}
        if config_path.exists():
            try:
                presets = json.loads(config_path.read_text())
            except Exception:
                pass

        presets[name] = tweak_ids

        try:
            config_path.write_text(json.dumps(presets, indent=2))
            logger.info(f"Saved custom preset '{name}' with {len(tweak_ids)} tweaks")
            return True
        except Exception as e:
            logger.error(f"Failed to save preset: {e}")
            return False

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

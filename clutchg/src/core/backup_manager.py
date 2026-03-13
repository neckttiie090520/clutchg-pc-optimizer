"""
Backup Manager
Creates and manages system backups including Windows restore points
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Union
from dataclasses import dataclass, asdict
from utils.logger import get_logger

logger = get_logger(__name__)


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

    @property
    def success(self) -> bool:
        """Whether this backup completed successfully."""
        return self._success


class BackupManager:
    """Manages system backups and restore points"""
    
    def __init__(self, backup_dir: Optional[Path] = None):
        """
        Initialize backup manager
        
        Args:
            backup_dir: Directory for storing backups
        """
        if backup_dir is None:
            backup_dir = Path(__file__).parent.parent.parent / "data" / "backups"
        
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.backup_dir / "backup_index.json"
        self.backups: List[BackupInfo] = self._load_index()
        
        logger.info(f"Backup manager initialized: {self.backup_dir}")
    
    def _load_index(self) -> List[BackupInfo]:
        """Load backup index from file"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [BackupInfo(**item) for item in data]
            except Exception as e:
                logger.error(f"Failed to load backup index: {e}")
        return []
    
    def _save_index(self):
        """Save backup index to file"""
        try:
            data = [asdict(b) for b in self.backups]
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save backup index: {e}")
    
    def create_backup(self, 
                     name: str,
                     profile: str = "",
                     create_restore_point: bool = True,
                     backup_registry: bool = True,
                     description: str = "") -> Optional[BackupInfo]:
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
        backup_id = timestamp.strftime("%Y%m%d_%H%M%S")
        
        logger.info(f"Creating backup: {name} (ID: {backup_id})")
        
        # Create backup directory
        backup_path = self.backup_dir / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)
        
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
        
        # Create backup info
        backup_info = BackupInfo(
            id=backup_id,
            name=name,
            created_at=timestamp.isoformat(),
            profile=profile,
            has_restore_point=has_restore_point,
            has_registry_backup=has_registry_backup,
            description=description,
            size_bytes=size_bytes
        )
        
        # Save info file
        info_file = backup_path / "info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(backup_info), f, indent=2)
        
        # Add to index
        self.backups.insert(0, backup_info)
        self._save_index()
        
        # Cleanup old backups (keep max 10)
        self._cleanup_old_backups(max_backups=10)
        
        logger.info(f"Backup created successfully: {backup_id}")
        return backup_info
    
    @staticmethod
    def _sanitize_restore_point_name(name: str) -> str:
        """Sanitize a name for safe interpolation into a PowerShell command string.

        Strips characters that are dangerous inside double-quoted PowerShell strings:
        double-quote, single-quote, backtick, semicolon, dollar-sign, parentheses,
        braces, pipe, and newlines.
        """
        dangerous = set('"\'`;$(){}|\n\r')
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

            logger.warning(f"Restore point creation failed (rc={result.returncode}): {result.stderr}")
            if "Access is denied" in result.stderr or "Access denied" in result.stderr:
                logger.warning("Primary method failed with Access Denied — trying CIM fallback.")
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
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", cim_script],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if cim_result.returncode == 0:
                    logger.info("Windows restore point created successfully (via CIM)")
                    return True
                logger.warning(f"CIM method failed: {cim_result.stdout} {cim_result.stderr}")
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
        
        # Key registry paths to backup
        registry_keys = [
            ("HKLM\\SYSTEM\\CurrentControlSet\\Services", "services.reg"),
            ("HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power", "power.reg"),
            ("HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer", "explorer.reg"),
            ("HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows", "policies.reg"),
            ("HKCU\\Control Panel\\Desktop", "desktop.reg"),
            ("HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer", "user_explorer.reg"),
        ]
        
        success_count = 0
        
        for key_path, filename in registry_keys:
            try:
                output_file = registry_dir / filename
                result = subprocess.run(
                    ["reg", "export", key_path, str(output_file), "/y"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    success_count += 1
                    logger.debug(f"Backed up: {key_path}")
                else:
                    logger.warning(f"Failed to backup {key_path}: {result.stderr}")
                    
            except Exception as e:
                logger.warning(f"Error backing up {key_path}: {e}")
        
        logger.info(f"Registry backup complete: {success_count}/{len(registry_keys)} keys")
        return success_count > 0
    
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
    
    def _cleanup_old_backups(self, max_backups: int = 10):
        """Remove old backups beyond max limit"""
        if len(self.backups) <= max_backups:
            return
        
        # Sort by creation time (newest first)
        self.backups.sort(key=lambda b: b.created_at, reverse=True)
        
        # Remove old ones
        while len(self.backups) > max_backups:
            old_backup = self.backups.pop()
            old_path = self.backup_dir / old_backup.id
            
            if old_path.exists():
                try:
                    shutil.rmtree(old_path)
                    logger.info(f"Removed old backup: {old_backup.id}")
                except Exception as e:
                    logger.warning(f"Failed to remove backup dir: {e}")
        
        self._save_index()
    
    def get_all_backups(self) -> List[BackupInfo]:
        """Get all backups"""
        return self.backups

    def list_backups(self) -> List[dict]:
        """Get all backups as a list of dicts (alias for compatibility)."""
        from dataclasses import asdict as _asdict
        return [_asdict(b) for b in self.backups]
    
    def get_backup(self, backup_id: str) -> Optional[BackupInfo]:
        """Get backup by ID"""
        for backup in self.backups:
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
        
        if not backup.has_registry_backup:
            logger.warning(f"Backup has no registry backup: {backup_id}")
            return False
        
        registry_dir = self.backup_dir / backup_id / "registry"
        if not registry_dir.exists():
            logger.error(f"Registry backup directory not found")
            return False
        
        logger.info(f"Restoring registry from backup: {backup_id}")
        
        success_count = 0
        for reg_file in registry_dir.glob("*.reg"):
            try:
                result = subprocess.run(
                    ["reg", "import", str(reg_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    success_count += 1
                    logger.info(f"Restored: {reg_file.name}")
                else:
                    logger.warning(f"Failed to restore {reg_file.name}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error restoring {reg_file.name}: {e}")
        
        logger.info(f"Registry restore complete: {success_count} files")
        return success_count > 0
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup"""
        backup = self.get_backup(backup_id)
        if not backup:
            return False
        
        # Remove directory
        backup_path = self.backup_dir / backup_id
        if backup_path.exists():
            try:
                shutil.rmtree(backup_path)
            except Exception as e:
                logger.error(f"Failed to delete backup directory: {e}")
                return False
        
        # Remove from index
        self.backups = [b for b in self.backups if b.id != backup_id]
        self._save_index()
        
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

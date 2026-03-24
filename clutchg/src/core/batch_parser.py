"""
Batch Script Parser
Discovers and parses batch script files with rich metadata
Updated: 2026-02-11 (Enhanced categories, tags, display metadata)
"""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from utils.logger import get_logger

logger = get_logger(__name__)


# ============================================================================
# CATEGORY DISPLAY METADATA
# ============================================================================
# Each category has: icon (Segoe MDL2), color, dim_color, label
CATEGORY_META: Dict[str, Dict[str, str]] = {
    "power":       {"icon": "\uE945", "color": "#F59E0B", "dim": "#3B2A0A", "label": "Power"},
    "bcdedit":     {"icon": "\uE7BA", "color": "#EF4444", "dim": "#3A1414", "label": "BCDEdit"},
    "services":    {"icon": "\uE770", "color": "#F97316", "dim": "#3A2210", "label": "Services"},
    "network":     {"icon": "\uE968", "color": "#3B82F6", "dim": "#102A4D", "label": "Network"},
    "registry":    {"icon": "\uE74C", "color": "#8B5CF6", "dim": "#2D1B4E", "label": "Registry"},
    "gpu":         {"icon": "\uE7FD", "color": "#22C55E", "dim": "#0E2A1F", "label": "GPU"},
    "storage":     {"icon": "\uE8B7", "color": "#06B6D4", "dim": "#0B2B3A", "label": "Storage"},
    "maintenance": {"icon": "\uE90F", "color": "#14B8A6", "dim": "#0A332E", "label": "Maintenance"},
    "system":      {"icon": "\uE950", "color": "#6366F1", "dim": "#1E1B4B", "label": "System"},
    "profile":     {"icon": "\uE9E9", "color": "#EC4899", "dim": "#4A1A36", "label": "Profiles"},
    "backup":      {"icon": "\uEA35", "color": "#0EA5E9", "dim": "#0C2D48", "label": "Backup"},
    "safety":      {"icon": "\uE81E", "color": "#22C55E", "dim": "#0E2A1F", "label": "Safety"},
    "validation":  {"icon": "\uE9D5", "color": "#A855F7", "dim": "#2E1065", "label": "Validation"},
    "logging":     {"icon": "\uE82D", "color": "#64748B", "dim": "#1E293B", "label": "Logging"},
    "other":       {"icon": "\uE943", "color": "#94A3B8", "dim": "#1E293B", "label": "Other"},
}


@dataclass
class BatchScript:
    """Batch script metadata"""
    path: Path
    name: str
    description: str
    category: str
    requires_admin: bool
    estimated_time: int  # seconds
    requires_restart: bool
    risk_level: str  # "LOW", "MEDIUM", "HIGH"
    tags: List[str] = field(default_factory=list)


class BatchParser:
    """Parses and discovers batch scripts"""
    
    def __init__(self, scripts_directory: Path):
        """
        Initialize batch parser
        
        Args:
            scripts_directory: Directory containing batch scripts
        """
        self.scripts_dir = Path(scripts_directory)
        logger.info(f"Batch parser initialized for: {self.scripts_dir}")
    
    def discover_scripts(self) -> List[BatchScript]:
        """
        Discover all batch scripts in directory
        
        Returns:
            List of BatchScript objects
        """
        scripts = []
        
        if not self.scripts_dir.exists():
            logger.warning(f"Scripts directory not found: {self.scripts_dir}")
            return scripts
        
        # Find all .bat files recursively
        for bat_file in self.scripts_dir.rglob("*.bat"):
            try:
                script = self.parse_script(bat_file)
                if script:
                    scripts.append(script)
            except Exception as e:
                logger.error(f"Failed to parse {bat_file}: {e}")
        
        # Sort: by category, then by name
        scripts.sort(key=lambda s: (s.category, s.name))
        
        logger.info(f"Discovered {len(scripts)} batch scripts")
        return scripts
    
    def parse_script(self, script_path: Path) -> BatchScript:
        """
        Parse a single batch script
        
        Args:
            script_path: Path to .bat file
            
        Returns:
            BatchScript object with metadata
        """
        name = script_path.stem
        # Create human-readable display name
        display_name = name.replace('-', ' ').replace('_', ' ').title()
        description = ""
        category = self._determine_category(script_path)
        requires_admin = True  # All Windows optimization scripts need admin
        estimated_time = self._estimate_time(category)
        requires_restart = False
        risk_level = self._determine_risk_level(category, script_path)
        tags = self._extract_tags(category, script_path)
        
        # Try to extract description from comments
        try:
            with open(script_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:30]  # Check first 30 lines
                
                desc_lines = []
                for line in lines:
                    line = line.strip()
                    
                    # Look for description in comments
                    if line.startswith('::') or line.startswith('REM'):
                        comment = line[2:].strip() if line.startswith('::') else line[3:].strip()
                        if comment and not comment.startswith('='):
                            desc_lines.append(comment)
                    
                    # Check if restart required
                    if 'restart' in line.lower() or 'reboot' in line.lower():
                        requires_restart = True
                    
                    # Check for admin requirement patterns
                    if 'net session' in line.lower() or 'runas' in line.lower():
                        requires_admin = True
        
        except Exception as e:
            logger.warning(f"Failed to read script content: {script_path}: {e}")
        
        # Build description from first meaningful comment lines
        if desc_lines:
            # Take first 2 meaningful lines for description
            description = ' — '.join(desc_lines[:2])
        
        if not description:
            description = display_name
        
        return BatchScript(
            path=script_path,
            name=display_name,
            description=description,
            category=category,
            requires_admin=requires_admin,
            estimated_time=estimated_time,
            requires_restart=requires_restart,
            risk_level=risk_level,
            tags=tags,
        )
    
    def _determine_category(self, script_path: Path) -> str:
        """Determine script category from path and filename"""
        path_str = str(script_path).lower()
        filename = script_path.stem.lower()
        
        # Check parent directory first (most reliable)
        parent_dir = script_path.parent.name.lower()
        
        if parent_dir == 'profiles':
            return 'profile'
        elif parent_dir == 'backup':
            return 'backup'
        elif parent_dir == 'safety':
            return 'safety'
        elif parent_dir == 'validation':
            return 'validation'
        elif parent_dir == 'logging':
            return 'logging'
        
        # For 'core' directory, determine sub-category from filename
        if parent_dir == 'core' or 'core' in path_str:
            if 'power' in filename:
                return 'power'
            elif 'bcdedit' in filename:
                return 'bcdedit'
            elif 'service' in filename:
                return 'services'
            elif 'network' in filename:
                return 'network'
            elif 'registry' in filename:
                return 'registry'
            elif 'gpu' in filename:
                return 'gpu'
            elif 'storage' in filename:
                return 'storage'
            elif 'maintenance' in filename:
                return 'maintenance'
            elif 'system' in filename or 'detect' in filename:
                return 'system'
            else:
                return 'other'
        
        # Root-level scripts
        if 'optimizer' in filename:
            return 'other'
        
        return 'other'

    def _determine_risk_level(self, category: str, script_path: Path) -> str:
        """
        Determine risk level based on category and script name

        Risk levels:
        - LOW: Backup, safety, logging, validation, system detection
        - MEDIUM: Power, network, registry, GPU, storage, maintenance
        - HIGH: BCDEdit, services, extreme profiles

        Args:
            category: Script category
            script_path: Path to script for additional checks

        Returns:
            "LOW", "MEDIUM", or "HIGH"
        """
        filename = script_path.stem.lower()
        
        # LOW risk categories
        if category in ['backup', 'safety', 'validation', 'logging', 'system']:
            return 'LOW'

        # HIGH risk categories
        if category in ['bcdedit', 'services']:
            return 'HIGH'

        # Profile risk depends on type
        if category == 'profile':
            if 'extreme' in filename:
                return 'HIGH'
            elif 'competitive' in filename:
                return 'MEDIUM'
            return 'LOW'

        # MEDIUM risk (most tweaks)
        if category in ['power', 'network', 'registry', 'gpu', 'storage', 'maintenance', 'other']:
            # Enhanced scripts may have higher risk
            if 'enhanced' in filename or 'aggressive' in filename:
                return 'MEDIUM'
            if 'extreme' in filename:
                return 'HIGH'
            return 'MEDIUM'

        return 'MEDIUM'
    
    def _estimate_time(self, category: str) -> int:
        """Estimate execution time in seconds based on category"""
        time_map = {
            'power': 15,
            'bcdedit': 10,
            'services': 30,
            'network': 20,
            'registry': 15,
            'gpu': 20,
            'storage': 45,
            'maintenance': 60,
            'system': 10,
            'profile': 60,
            'backup': 30,
            'safety': 20,
            'validation': 45,
            'logging': 5,
        }
        return time_map.get(category, 30)
    
    def _extract_tags(self, category: str, script_path: Path) -> List[str]:
        """Extract tags from category and filename for filtering"""
        tags = [category]
        filename = script_path.stem.lower()
        
        # Add tags based on filename keywords
        tag_keywords = {
            'enhanced': 'enhanced',
            'advanced': 'advanced',
            'safe': 'safe',
            'extreme': 'extreme',
            'competitive': 'competitive',
            'optimizer': 'optimize',
            'manager': 'manager',
            'detect': 'detection',
            'benchmark': 'benchmark',
            'restore': 'restore',
            'backup': 'backup',
            'rollback': 'rollback',
            'flight': 'recorder',
            'validator': 'validate',
        }
        
        for keyword, tag in tag_keywords.items():
            if keyword in filename:
                tags.append(tag)
        
        return list(set(tags))
    
    @staticmethod
    def get_category_meta(category: str) -> Dict[str, str]:
        """
        Get display metadata for a category
        
        Args:
            category: Category name
            
        Returns:
            Dict with 'icon', 'color', 'dim', 'label' keys
        """
        return CATEGORY_META.get(category, CATEGORY_META["other"])
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get list of all known category names"""
        return list(CATEGORY_META.keys())
    
    def get_scripts_by_category(self, category: str) -> List[BatchScript]:
        """Get scripts filtered by category"""
        all_scripts = self.discover_scripts()
        return [s for s in all_scripts if s.category == category]
    
    def get_category_counts(self) -> Dict[str, int]:
        """Get count of scripts per category"""
        scripts = self.discover_scripts()
        counts: Dict[str, int] = {}
        for s in scripts:
            counts[s.category] = counts.get(s.category, 0) + 1
        return counts
    
    def validate_script(self, script: BatchScript) -> bool:
        """
        Validate a batch script for safety.

        Checks that the script file exists, is readable, and does not contain
        any patterns that could cause irreversible system damage.

        Args:
            script: BatchScript to validate

        Returns:
            True if the script passes all safety checks, False otherwise
        """
        import re

        # Check file exists
        if not script.path.exists():
            logger.error(f"Script not found: {script.path}")
            return False

        # Check file is readable and free of dangerous content
        try:
            with open(script.path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            content_lower = content.lower()

            # =====================================================================
            # TIER 1: Always block - destructive operations
            # =====================================================================
            always_dangerous_patterns = [
                # Disk / filesystem destruction
                'format c:',
                'format d:',
                'format e:',
                'format f:',
                'del /s /q c:\\windows',
                'del /f /s /q c:\\',
                'rd /s /q c:\\',
                'rd /s /q c:\\windows',
                'rmdir /s /q c:\\',
                'rmdir /s /q c:\\windows',
                # Partitioning tool (interactive; also scriptable destructively)
                'diskpart',
                # Boot store DESTRUCTION (not modification)
                # /delete removes boot entries - VERY DANGEROUS
                # /deletevalue only removes a single value - SAFE (used for rollback)
                'bcdedit /delete ',
                'bcdedit /delete{',
                # Secure wipe of drive free space
                'cipher /w:',
                # Service permanent deletion
                'sc delete ',
                'sc delete"',
                # Driver deletion
                'pnputil /delete-driver',
                'pnputil -d ',
                # Shadow copy / backup deletion
                'vssadmin delete shadows',
                'wbadmin delete',
                # Boot sector modification
                'bootsect /force',
                'bootsect /mbr',
                'bootrec /fixmbr',
                'bootrec /rebuildbcd',
                # Registry hive unload (can cause instability)
                'reg unload ',
                # Windows feature removal
                'dism /remove-package',
                'dism /disable-feature',
                # PowerShell destructive equivalents
                'remove-item -recurse',
                'remove-item -force',
                # System shutdown / power-off (unattended)
                'shutdown /s',
                'shutdown /r',
                'shutdown /p',
                'shutdown /h',
                # Process termination of critical OS processes
                'taskkill /f /im csrss',
                'taskkill /f /im svchost',
                'taskkill /f /im lsass',
                'taskkill /f /im winlogon',
                # Ownership / ACL abuse on system paths
                'takeown /f c:\\windows',
                'icacls c:\\windows /grant',
            ]

            for pattern in always_dangerous_patterns:
                if pattern in content_lower:
                    logger.error(
                        f"Dangerous pattern detected in {script.path}: '{pattern}'"
                    )
                    return False

            # =====================================================================
            # TIER 2: Context-aware checks for reg delete
            # =====================================================================
            # Block reg delete that deletes ENTIRE KEYS (no /v flag)
            # Pattern: reg delete "path" /f  (no /v before /f)
            # Allow: reg delete "path" /v "value" /f  (specific value only)

            # Find all reg delete commands
            reg_delete_pattern = r'reg\s+delete\s+["\']?([^"\'>\s]+)["\']?([^>\n]*)'
            for match in re.finditer(reg_delete_pattern, content_lower):
                registry_path = match.group(1)
                flags = match.group(2)

                # Check if this is deleting an entire key (no /v flag)
                has_value_flag = '/v' in flags

                if not has_value_flag:
                    # Deleting entire key - check if it's a critical path
                    logger.error(
                        f"Registry key deletion (no /v flag) in {script.path}: "
                        f"'reg delete {registry_path}'"
                    )
                    return False

                # Even with /v, block certain critical paths
                critical_paths = [
                    'hklm\\software\\microsoft\\windows\\currentversion\\run',
                    'hklm\\software\\microsoft\\windows\\currentversion\\runonce',
                    'hklm\\system\\setup',
                    'hklm\\software\\microsoft\\windows nt\\currentversion\\winlogon',
                    'hklm\\software\\microsoft\\windows nt\\currentversion\\image file execution options',
                ]

                for critical in critical_paths:
                    if critical in registry_path:
                        logger.error(
                            f"Critical registry path modification in {script.path}: "
                            f"'{registry_path}'"
                        )
                        return False

        except Exception as e:
            logger.error(f"Failed to read script: {script.path}: {e}")
            return False

        return True

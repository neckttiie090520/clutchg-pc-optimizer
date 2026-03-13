# ClutchG - Technical Specification Document

## Project Overview

**Name**: ClutchG  
**Type**: Windows PC Optimization Launcher  
**Purpose**: User-friendly Python GUI for managing batch optimization scripts  
**Target Users**: Gamers, PC enthusiasts, non-technical users wanting performance optimization

---

## Technology Stack

### Programming Language
- **Python 3.11+** - Modern Python with type hints support

### GUI Framework
- **CustomTkinter 5.2+** - Modern, themed Tkinter wrapper
  - Clean, gaming-oriented aesthetics
  - Built-in dark/light themes
  - Easy styling and customization
  - Lightweight distribution

### Key Libraries

#### Core Dependencies
```python
customtkinter>=5.2.0      # Modern GUI framework
Pillow>=10.0.0            # Image handling
psutil>=5.9.0             # System information
WMI>=1.5.1                # Windows Management Instrumentation (Windows-only)
pywin32>=306              # Windows API access
```

> **หมายเหตุ (v2.0.2):** GPUtil ถูกลบออกจาก dependencies แล้ว
> `system_info.py` ใช้ 3-strategy สำหรับ storage detection: WMI `Get-PhysicalDisk` → psutil fallback

#### Optional Dependencies
```python
colorama>=0.4.6           # Colored console output
jsonschema>=4.19.0        # Config validation
appdirs>=1.4.4            # Cross-platform app directories
```

### Development Tools
```python
# Development dependencies
pytest>=7.4.0             # Testing framework
black>=23.7.0             # Code formatting
mypy>=1.5.0               # Type checking
pyinstaller>=5.13.0       # Executable packaging
```

---

## Project Structure Detail

```
clutchg/
├── src/
│   ├── main.py                          # Entry point
│   │   └── if __name__ == "__main__": run_app()
│   │
│   ├── app.py                           # Main application controller
│   │   └── class ClutchGApp:
│   │       ├── __init__(self)
│   │       ├── run(self) → None
│   │       ├── setup_ui(self) → None
│   │       └── switch_view(self, view: str) → None
│   │
│   ├── gui/                             # GUI layer
│   │   ├── base_view.py                 # Abstract base view
│   │   │   └── class BaseView(ABC)
│   │   │
│   │   ├── dashboard.py                 # Main dashboard
│   │   │   └── class DashboardView(BaseView)
│   │   │
│   │   ├── profiles.py                  # Profile selection
│   │   │   └── class ProfilesView(BaseView)
│   │   │
│   │   ├── scripts.py                   # Script manager
│   │   │   └── class ScriptsView(BaseView)
│   │   │
│   │   ├── backup.py                    # Backup/restore
│   │   │   └── class BackupView(BaseView)
│   │   │
│   │   ├── settings.py                  # Settings panel
│   │   │   └── class SettingsView(BaseView)
│   │   │
│   │   └── components/                  # Reusable components
│   │       ├── card.py                  # Card widget
│   │       │   └── class Card(ctk.CTkFrame)
│   │       │
│   │       ├── progress.py              # Progress indicator
│   │       │   └── class ProgressCard(ctk.CTkFrame)
│   │       │
│   │       ├── notification.py          # Toast notifications
│   │       │   └── class Notification(ctk.CTkToplevel)
│   │       │
│   │       └── console.py               # Console output widget
│   │           └── class ConsoleOutput(ctk.CTkTextbox)
│   │
│   ├── core/                            # Business logic
│   │   ├── batch_executor.py
│   │   │   └── class BatchExecutor:
│   │   │       ├── execute(path, args, elevated) → ExecutionResult
│   │   │       ├── execute_async(path, on_output, on_complete)
│   │   │       └── cancel() → None
│   │   │
│   │   ├── batch_parser.py
│   │   │   └── class BatchParser:
│   │   │       ├── discover_scripts(directory) → List[BatchScript]
│   │   │       ├── parse_script(path) → BatchScript
│   │   │       └── validate_script(script) → bool
│   │   │
│   │   ├── system_info.py
│   │   │   └── class SystemDetector:
│   │   │       ├── detect_all() → SystemProfile
│   │   │       ├── detect_os() → OSInfo
│   │   │       ├── detect_cpu() → CPUInfo
│   │   │       ├── detect_gpu() → GPUInfo
│   │   │       ├── detect_ram() → RAMInfo
│   │   │       ├── calculate_tier(system) → str
│   │   │       └── recommend_profile(system) → str
│   │   │
│   │   ├── profile_manager.py
│   │   │   └── class ProfileManager:
│   │   │       ├── load_profiles() → Dict[str, Profile]
│   │   │       ├── get_profile(name) → Profile
│   │   │       ├── apply_profile(profile) → ExecutionResult
│   │   │       └── get_active_profile() → Optional[Profile]
│   │   │
│   │   ├── backup_manager.py
│   │   │   └── class BackupManager:
│   │   │       ├── create_backup(name) → BackupInfo
│   │   │       ├── list_backups() → List[BackupInfo]
│   │   │       ├── restore_backup(backup_id) → bool
│   │   │       ├── delete_backup(backup_id) → bool
│   │   │       └── create_restore_point() → bool
│   │   │
│   │   └── config.py
│   │       └── class ConfigManager:
│   │           ├── load_config() → Config
│   │           ├── save_config(config) → None
│   │           └── reset_to_defaults() → None
│   │
│   ├── models/                          # Data models
│   │   ├── batch_script.py
│   │   │   └── @dataclass BatchScript:
│   │   │       ├── path: Path
│   │   │       ├── name: str
│   │   │       ├── description: str
│   │   │       ├── category: str
│   │   │       ├── requires_admin: bool
│   │   │       └── estimated_time: int
│   │   │
│   │   ├── profile.py
│   │   │   └── @dataclass Profile:
│   │   │       ├── name: str
│   │   │       ├── description: str
│   │   │       ├── risk_level: RiskLevel (enum)
│   │   │       ├── expected_fps_gain: Tuple[int, int]
│   │   │       ├── scripts: List[str]
│   │   │       └── warnings: List[str]
│   │   │
│   │   ├── system_profile.py
│   │   │   └── @dataclass SystemProfile:
│   │   │       ├── os: OSInfo
│   │   │       ├── cpu: CPUInfo
│   │   │       ├── gpu: GPUInfo
│   │   │       ├── ram: RAMInfo
│   │   │       ├── storage: StorageInfo
│   │   │       ├── tier: SystemTier (enum)
│   │   │       └── form_factor: FormFactor (enum)
│   │   │
│   │   └── execution_result.py
│   │       └── @dataclass ExecutionResult:
│   │           ├── success: bool
│   │           ├── output: str
│   │           ├── errors: str
│   │           ├── return_code: int
│   │           └── duration: float
│   │
│   └── utils/                           # Utility modules
│       ├── logger.py
│       │   └── class Logger:
│       │       ├── setup_logging() → None
│       │       ├── log_execution(result) → None
│       │       └── get_logs(filter) → List[LogEntry]
│       │
│       ├── registry.py
│       │   └── class RegistryHelper:
│       │       ├── backup_key(key_path) → bytes
│       │       ├── restore_key(key_path, data) → bool
│       │       └── export_registry(keys) → Path
│       │
│       └── admin.py
│           └── class AdminChecker:
│               ├── is_admin() → bool
│               ├── request_elevation() → bool
│               └── run_as_admin(script) → None
│
├── assets/
│   ├── icons/
│   │   ├── app.ico                      # Application icon
│   │   ├── dashboard.png                # Dashboard icon
│   │   ├── profiles.png                 # Profiles icon
│   │   ├── scripts.png                  # Scripts icon
│   │   ├── backup.png                   # Backup icon
│   │   └── settings.png                 # Settings icon
│   │
│   ├── images/
│   │   ├── logo.png                     # App logo
│   │   └── splash.png                   # Splash screen (optional)
│   │
│   └── themes/
│       ├── dark.json                    # Dark theme config
│       └── light.json                   # Light theme config
│
├── batch_scripts/                       # Symlink to existing bat/ folder
│   └── [links to c:/Users/nextzus/Documents/thesis/bat/src/]
│
├── config/
│   ├── default_config.json              # Default configuration
│   ├── profiles.json                    # Profile definitions
│   └── script_categories.json           # Script categorization
│
├── data/                                # Runtime data (created at runtime)
│   ├── backups/                         # Backup storage
│   ├── logs/                            # Application logs
│   └── cache/                           # Temporary cache
│
├── tests/
│   ├── test_batch_executor.py
│   ├── test_system_info.py
│   ├── test_profile_manager.py
│   └── test_backup_manager.py
│
├── docs/
│   ├── USER_GUIDE.md                    # User documentation
│   ├── DEVELOPER_GUIDE.md               # Developer documentation
│   └── API.md                           # Internal API documentation
│
├── requirements.txt                     # Production dependencies
├── requirements-dev.txt                 # Development dependencies
├── pyproject.toml                       # Project metadata
├── build.py                             # Build script
├── README.md                            # Project readme
└── LICENSE                              # License file
```

---

## Configuration Schema

### default_config.json
```json
{
  "version": "1.0.0",
  "theme": "dark",
  "auto_backup": true,
  "confirm_actions": true,
  "log_level": "INFO",
  "batch_scripts_dir": "./batch_scripts",
  "backup_dir": "./data/backups",
  "max_backups": 10,
  "default_profile": "SAFE",
  "window_size": {
    "width": 1000,
    "height": 700
  },
  "startup_checks": {
    "check_admin": true,
    "detect_system": true,
    "verify_scripts": true
  }
}
```

### profiles.json
```json
{
  "SAFE": {
    "name": "SAFE",
    "display_name": "Safe Mode",
    "description": "Minimal optimizations with maximum safety",
    "icon": "🛡️",
    "risk_level": "LOW",
    "expected_fps_gain": [2, 5],
    "scripts": [
      "core/power-manager.bat",
      "profiles/safe-profile.bat"
    ],
    "warnings": [
      "A system restart is recommended after applying changes"
    ],
    "requires_restart": false
  },
  "COMPETITIVE": {
    "name": "COMPETITIVE",
    "display_name": "Competitive Mode",
    "description": "Balanced performance optimizations",
    "icon": "⚔️",
    "risk_level": "MEDIUM",
    "expected_fps_gain": [5, 10],
    "scripts": [
      "core/power-manager.bat",
      "core/bcdedit-manager.bat",
      "core/service-manager.bat",
      "core/network-manager.bat",
      "profiles/competitive-profile.bat"
    ],
    "warnings": [
      "BCDEdit changes require system restart",
      "Some services will be disabled"
    ],
    "requires_restart": true
  },
  "EXTREME": {
    "name": "EXTREME",
    "display_name": "Extreme Mode",
    "description": "Aggressive performance optimizations",
    "icon": "🔥",
    "risk_level": "HIGH",
    "expected_fps_gain": [10, 15],
    "scripts": [
      "core/power-manager.bat",
      "core/bcdedit-manager.bat",
      "core/service-manager.bat",
      "core/network-manager.bat",
      "profiles/extreme-profile.bat"
    ],
    "warnings": [
      "⚠️ EXTREME profile applies aggressive optimizations",
      "May cause system instability on some configurations",
      "BCDEdit changes require system restart",
      "Extensive service disabling may break functionality",
      "Recommended for advanced users only"
    ],
    "requires_restart": true,
    "requires_confirmation": true
  }
}
```

---

## Key Algorithms

### System Tier Calculation

```python
def calculate_tier(system: SystemProfile) -> str:
    """
    Calculate system tier based on hardware score
    
    Score breakdown:
    - CPU: 0-30 points
    - GPU: 0-30 points
    - RAM: 0-20 points
    - Storage: 0-10 points
    - System: 0-10 points
    Total: 0-100 points
    """
    
    total_score = (
        system.cpu.score +
        system.gpu.score +
        system.ram.score +
        system.storage.score +
        system.system.score
    )
    
    if total_score >= 80:
        return "enthusiast"
    elif total_score >= 60:
        return "high"
    elif total_score >= 40:
        return "mid"
    else:
        return "entry"
```

### Profile Recommendation

```python
def recommend_profile(system: SystemProfile) -> str:
    """Recommend optimization profile based on system"""
    
    # Laptop restrictions
    if system.form_factor == FormFactor.LAPTOP:
        # Laptops should stick to SAFE
        return "SAFE"
    
    # Desktop recommendations by tier
    if system.tier == "enthusiast":
        # Recommend COMPETITIVE, not EXTREME
        # User can manually switch to EXTREME
        return "COMPETITIVE"
    elif system.tier in ["high", "mid"]:
        return "COMPETITIVE"
    else:
        return "SAFE"
```

---

## Error Handling Strategy

### Exception Hierarchy
```python
class ClutchGException(Exception):
    """Base exception for ClutchG"""
    pass

class ExecutionError(ClutchGException):
    """Batch script execution failed"""
    pass

class BackupError(ClutchGException):
    """Backup/restore operation failed"""
    pass

class PermissionError(ClutchGException):
    """Insufficient privileges"""
    pass

class ValidationError(ClutchGException):
    """Configuration/script validation failed"""
    pass
```

### Error Handling Pattern
```python
try:
    result = batch_executor.execute(script_path)
    if not result.success:
        # Show error to user
        show_notification(
            "Execution Failed", 
            result.errors, 
            type="error"
        )
        # Log to file
        logger.error(f"Script {script_path} failed: {result.errors}")
        # Offer rollback
        offer_rollback_dialog()
except ExecutionError as e:
    handle_execution_error(e)
except PermissionError as e:
    request_admin_privileges()
except Exception as e:
    # Unexpected error
    logger.critical(f"Unexpected error: {e}")
    show_crash_dialog(e)
```

---

## Security Considerations

### Admin Privileges
- **Check on startup**: Verify admin rights before allowing any operations
- **UAC prompts**: Use proper Windows UAC elevation
- **User confirmation**: Always confirm before running elevated scripts

### Script Validation
```python
def validate_script(script: BatchScript) -> bool:
    """
    Validate batch script before execution
    - File exists and is readable
    - Not in blacklist of dangerous commands
    - Has proper header/metadata
    """
    
    # Check file exists
    if not script.path.exists():
        return False
    
    # Read script content
    content = script.path.read_text(encoding='utf-8')
    
    # Check for dangerous commands
    dangerous_patterns = [
        r'format\s+[a-z]:',  # format drives
        r'del\s+/s\s+/q\s+c:\\windows',  # delete Windows
        r'rmdir\s+/s\s+/q\s+c:\\',  # remove system directories
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            logger.warning(f"Dangerous pattern detected in {script.path}")
            return False
    
    return True
```

### Backup Safety
- **Always backup before changes**: Create restore point and registry backup
- **Verify backup integrity**: Check backup files after creation
- **Keep multiple backups**: Maintain rolling backup history
- **Clear rollback path**: One-click restore functionality

---

## Performance Considerations

### Startup Performance
- Lazy load GUI components
- Cache system detection results
- Async script discovery
- Minimal startup dependencies

### Execution Performance
- Use subprocess for script execution
- Stream output in real-time
- Non-blocking UI during execution
- Cancel long-running operations

### Memory Management
- Limit log file sizes
- Cleanup old backups automatically
- Don't load all scripts into memory
- Use generators for large datasets

---

## Testing Strategy

> **สถานะ (v2.0.2):** Test suite ใช้งานจริงแล้ว — 285 unit tests, 23 integration tests, 64 E2E tests (total 372)
> Unit tests ผ่าน 100%, integration tests ผ่าน 100%, E2E skipped ใน headless CI

### Unit Tests
```python
# tests/test_system_info.py
def test_detect_os():
    detector = SystemDetector()
    os_info = detector.detect_os()
    assert os_info.platform == 'windows'
    assert os_info.version is not None

# tests/test_batch_executor.py
def test_execute_simple_script():
    executor = BatchExecutor()
    result = executor.execute(Path('test_script.bat'))
    assert result.success
    assert result.return_code == 0
```

### Integration Tests
- Test full profile application
- Test backup and restore cycle
- Test UI interactions with backend

### Manual Testing Checklist
- ✅ Run on Windows 10
- ✅ Run on Windows 11
- ✅ Test without admin privileges
- ✅ Test all three profiles
- ✅ Test backup/restore
- ✅ Test theme switching
- ✅ Test error scenarios

---

## Build & Distribution

### PyInstaller Configuration
```python
# build.py
import PyInstaller.__main__

PyInstaller.__main__.run([
    'src/main.py',
    '--name=ClutchG',
    '--onefile',
    '--windowed',  # No console window
    '--icon=assets/icons/app.ico',
    '--add-data=assets;assets',
    '--add-data=config;config',
    '--add-data=batch_scripts;batch_scripts',
    '--hidden-import=win32timezone',  # WMI dependency
    '--uac-admin',  # Request admin on startup
])
```

### Distribution Package
```
ClutchG_v1.0.0/
├── ClutchG.exe              # Main executable
├── README.txt               # Quick start guide
├── LICENSE.txt              # License info
├── batch_scripts/           # Included batch scripts
│   └── [all .bat files]
└── docs/                    # Documentation
    └── USER_GUIDE.pdf
```

---

## Future Enhancements (v2.0)

### Planned Features
- **Benchmark integration**: Before/after FPS testing
- **Cloud sync**: Backup profiles to cloud
- **Community profiles**: Share and download profiles
- **Auto-update**: Automatic update checking
- **Telemetry (opt-in)**: Anonymous usage statistics
- **Multi-language**: Support Thai, Chinese, etc.
- **Scheduler**: Schedule optimizations

### Technical Improvements
- **Plugin system**: Allow third-party extensions
- **API exposure**: REST API for external tools
- **Advanced logging**: Detailed execution traces
- **Performance monitoring**: Track system metrics over time

---

## Conclusion

ClutchG is designed to be a **simple, user-friendly, and safe** launcher for Windows batch optimization scripts. By focusing on essential features and avoiding over-engineering, the project achieves a balance between functionality and maintainability.

**Core Principles**:
- 🎯 User-friendly interface
- 🛡️ Safety first approach
- 📊 Transparent operations
- ⚡ Performance focused
- 🚫 No over-engineering

The implementation plan ensures a solid foundation while keeping complexity manageable for a single developer or small team.

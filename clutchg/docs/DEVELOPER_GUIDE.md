# ClutchG Developer Guide

## 📁 Project Structure

```
clutchg/
├── src/                    # Source code
│   ├── main.py            # Launcher entry point
│   ├── app_minimal.py     # Main application class
│   │
│   ├── gui/               # UI components
│   │   ├── views/         # View modules
│   │   │   ├── dashboard_minimal.py
│   │   │   ├── profiles_minimal.py
│   │   │   ├── scripts_minimal.py
│   │   │   ├── backup_restore_center.py
│   │   │   ├── settings_minimal.py
│   │   │   └── help_minimal.py
│   │   ├── components/    # Reusable widgets
│   │   │   ├── glass_card.py
│   │   │   ├── enhanced_button.py
│   │   │   ├── enhanced_sidebar.py
│   │   │   ├── execution_dialog.py
│   │   │   ├── toast.py
│   │   │   └── timeline.py
│   │   ├── theme.py       # Theme constants
│   │   └── style.py       # Font styling
│   │
│   ├── core/              # Business logic
│   │   ├── batch_parser.py      # Script discovery
│   │   ├── batch_executor.py    # Script execution
│   │   ├── profile_manager.py   # Profile management
│   │   ├── tweak_registry.py    # Tweak database
│   │   ├── backup_manager.py    # Backup system
│   │   ├── system_info.py       # Hardware detection
│   │   ├── action_catalog.py    # Quick actions
│   │   └── help_manager.py      # Contextual help
│   │
│   ├── models/            # Data models
│   └── utils/             # Utilities
│       ├── admin.py       # Admin privileges
│       └── logger.py      # Logging setup
│
├── assets/                # Icons, images
├── config/                # Configuration files
├── data/                  # Runtime data (backups, logs)
├── docs/                  # Documentation
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── conftest.py       # Shared fixtures
├── build.py               # PyInstaller build script
└── requirements.txt       # Dependencies
```

---

## 🛠️ Development Setup

```bash
# Clone and enter directory
cd c:\Users\nextzus\Documents\thesis\bat\clutchg

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run from source
cd src
python app_minimal.py
```

---

## 📦 Dependencies

```
customtkinter>=5.2.0  # Modern GUI framework
Pillow>=10.0.0        # Image handling
psutil>=5.9.0         # System information
pywin32>=306          # Windows API access
```

---

## 🏗️ Architecture

### Core Components

**BatchExecutor** - Runs batch files with monitoring
```python
executor = BatchExecutor(
    on_output=lambda line: print(line),
    on_progress=lambda pct: update_bar(pct)
)
result = executor.execute(script_path)
```

**SystemDetector** - Hardware detection
```python
detector = SystemDetector()
system = detector.detect_all()
# Returns: SystemProfile with OS, CPU, GPU, RAM, tier
```

**ProfileManager** - Profile application
```python
manager = ProfileManager(scripts_dir)
profile = manager.get_profile("COMPETITIVE")
result = manager.apply_profile(profile)
```

**BackupManager** - Backup/restore
```python
backup_mgr = BackupManager()
backup = backup_mgr.create_backup("Pre_Optimization")
backup_mgr.restore_registry(backup.id)
```

---

## 🎨 Adding New Views

1. Create view in `src/gui/`:
```python
import customtkinter as ctk

class MyView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        # Build UI...
```

2. Register in `app_minimal.py`:
```python
from gui.my_view import MyView

# In switch_view():
elif view_name == "my_view":
    self.current_view = MyView(self.main_frame, self)
```

3. Add navigation button in sidebar.

---

## 🔧 Adding New Profiles

Edit `core/profile_manager.py`:
```python
'CUSTOM': Profile(
    name='CUSTOM',
    display_name='Custom Mode',
    description='Your custom optimization',
    icon='⭐',
    risk_level=RiskLevel.MEDIUM,
    expected_fps_gain=(3, 7),
    scripts=[
        'core/your-script.bat',
    ],
    warnings=['Custom warning'],
    requires_restart=True,
    requires_confirmation=False
),
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# Test core functionality
python test_core.py

# Test with coverage
pytest --cov=src tests/
```

---

## 📦 Building

```bash
# Build executable
python build.py

# Output: dist/ClutchG.exe
```

---

## 🔍 Logging

Logs are stored in `data/logs/`.

```python
from utils.logger import get_logger
logger = get_logger(__name__)

logger.info("Starting operation")
logger.error("Something failed")
```

---

## 🛡️ Security Notes

- Always check admin privileges
- Validate batch scripts before execution
- Create backups before applying changes
- Log all operations

---

## 📝 Code Style

- Use type hints
- Follow PEP 8
- Document with docstrings
- Handle exceptions gracefully

---

**Questions?** Check the repository issues.

# ClutchG - Quick Reference Guide

## 🎯 What is ClutchG?

**ClutchG** is a user-friendly Python application that provides a modern GUI for running Windows optimization batch scripts. Think of it as a launcher/control panel for the existing batch optimizer tools.

### Key Features
- ✅ Modern, gaming-style UI
- ✅ One-click optimization profiles
- ✅ Auto-detection of system hardware
- ✅ Safe backup/restore system
- ✅ Real-time execution monitoring
- ✅ No over-engineering - simple and effective

---

## 📚 Quick Start for Users

### Installation
1. Download `ClutchG.exe`
2. Right-click → "Run as Administrator"
3. Follow the setup wizard
4. Done!

### First Use
1. **Dashboard** - View your system info
2. **Profiles** - Choose SAFE/COMPETITIVE/EXTREME
3. **Click "Optimize Now"** - Apply selected profile
4. **Restart if needed** - Follow on-screen instructions

### Profile Guide

| Profile | Best For | Risk | FPS Gain |
|---------|----------|------|----------|
| 🛡️ **SAFE** | Beginners, Laptops | Low | +2-5% |
| ⚔️ **COMPETITIVE** | Gamers, Mid-High PCs | Medium | +5-10% |
| 🔥 **EXTREME** | Enthusiasts, High-end | High | +10-15% |

---

## 🛠️ Quick Start for Developers

### Setup Development Environment

```bash
# Clone repository
cd c:\Users\nextzus\Documents\thesis\bat

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install customtkinter pillow psutil pywin32

# (Optional) Install dev dependencies
pip install pytest black mypy
```

### Run from Source

```bash
cd clutchg/src
python main.py
```

### Project Structure (Simplified)

```
clutchg/
├── src/
│   ├── main.py           # Entry point
│   ├── app.py            # Main app
│   ├── gui/              # All UI components
│   ├── core/             # Business logic
│   ├── models/           # Data models
│   └── utils/            # Helpers
├── assets/               # Icons, images
├── batch_scripts/        # Batch files
└── config/               # Configuration
```

---

## 🔧 Tech Stack Summary

### Core
- **Python 3.11+** - Programming language
- **CustomTkinter** - Modern GUI framework
- **psutil** - System information
- **WMI** - Windows hardware detection

### Optional
- **PyInstaller** - Build executable
- **pytest** - Testing
- **black** - Code formatting

---

## 📋 Implementation Phases

### Phase 1: Core (Week 1)
- [x] Project structure
- [ ] System detection
- [ ] Basic GUI shell
- [ ] Dashboard view

### Phase 2: Integration (Week 2)
- [ ] Batch executor
- [ ] Profile manager
- [ ] Execution monitoring
- [ ] Real-time output

### Phase 3: Safety (Week 3)
- [ ] Backup system
- [ ] Restore functionality
- [ ] Rollback capability
- [ ] Logging

### Phase 4: Polish (Week 4)
- [ ] Themes
- [ ] Settings panel
- [ ] Documentation
- [ ] Distribution

---

## 🎨 Design Philosophy

### Keep It Simple
- ❌ No complex databases
- ❌ No cloud integration
- ❌ No microservices
- ✅ JSON configuration
- ✅ Local file storage
- ✅ Direct subprocess execution

### User-Friendly
- One-click actions
- Clear visual feedback
- Safety warnings
- Easy rollback
- Helpful tooltips

### Modern Aesthetic
- Dark theme by default
- Card-based layout
- Smooth animations
- Gaming-oriented colors
- Clean typography

---

## 🔐 Safety Features

### Before Every Change
1. ✅ Create Windows restore point
2. ✅ Backup affected registry keys
3. ✅ Save current configuration
4. ✅ Show confirmation dialog

### During Execution
1. ✅ Real-time output monitoring
2. ✅ Error detection
3. ✅ Cancel capability
4. ✅ Detailed logging

### After Changes
1. ✅ Verification checks
2. ✅ Success/failure notification
3. ✅ Offer restart if needed
4. ✅ Show applied tweaks

---

## 📊 Example Code Snippets

### System Detection
```python
from core.system_info import SystemDetector

detector = SystemDetector()
system = detector.detect_all()

print(f"OS: {system.os.version}")
print(f"CPU: {system.cpu.name}")
print(f"GPU: {system.gpu.name}")
print(f"Tier: {system.tier}")
```

### Execute Batch Script
```python
from core.batch_executor import BatchExecutor

executor = BatchExecutor(
    on_output=lambda line: print(line),
    on_progress=lambda pct: print(f"{pct}%")
)

result = executor.execute(
    Path("batch_scripts/power-manager.bat"),
    elevated=True
)

if result.success:
    print("✅ Success!")
else:
    print(f"❌ Error: {result.errors}")
```

### Apply Profile
```python
from core.profile_manager import ProfileManager

manager = ProfileManager(batch_scripts_dir)
profile = manager.get_profile("COMPETITIVE")

# Create backup first
backup_manager.create_backup("pre_competitive")

# Apply profile
result = manager.apply_profile(profile)

if result.success:
    print("Profile applied successfully!")
```

---

## 🧪 Testing

### Run Tests
```bash
# All tests
pytest

# Specific test
pytest tests/test_system_info.py

# With coverage
pytest --cov=src tests/
```

### Manual Testing Checklist
- [ ] Launch app as admin
- [ ] System detection works
- [ ] All three profiles apply successfully
- [ ] Backup/restore functionality
- [ ] Theme switching
- [ ] Error handling
- [ ] Windows 10 compatibility
- [ ] Windows 11 compatibility

---

## 📦 Building Distribution

### Create Executable
```bash
python build.py
```

This creates:
- `dist/ClutchG.exe` - Standalone executable
- `dist/ClutchG/` - Folder with all dependencies

### Distribution Package
```
ClutchG_v1.0.0.zip
├── ClutchG.exe
├── README.txt
├── LICENSE.txt
├── batch_scripts/
└── docs/
```

---

## 🐛 Common Issues

### "Not running as administrator"
- **Solution**: Right-click → "Run as Administrator"

### "Batch script not found"
- **Solution**: Check `batch_scripts_dir` in config
- Ensure scripts are copied/linked correctly

### "System detection failed"
- **Solution**: Install `pywin32` and `WMI` packages
- May require `pip install pywin32` with admin rights

### GUI doesn't appear
- **Solution**: Check if CustomTkinter is installed
- Try `pip install --upgrade customtkinter`

---

## 📝 Configuration

### Default Location
- Windows: `%APPDATA%\ClutchG\config.json`
- Portable: `./config/default_config.json`

### Key Settings
```json
{
  "theme": "dark",           // "dark" or "light"
  "auto_backup": true,       // Create backup before changes
  "confirm_actions": true,   // Show confirmation dialogs
  "default_profile": "SAFE", // Default selected profile
  "max_backups": 10          // Keep last N backups
}
```

---

## 🚀 Next Steps

### For Users
1. ✅ Review the [implementation plan](implementation_plan.md)
2. ✅ Check the [UI mockups](#mockups) above
3. ✅ Provide feedback on features
4. ⏳ Wait for development to begin

### For Developers
1. ✅ Read [technical spec](clutchg_technical_spec.md)
2. ⏳ Setup development environment
3. ⏳ Implement Phase 1 (Core)
4. ⏳ Test on target systems

---

## 📖 Additional Resources

### Documentation
- [Implementation Plan](implementation_plan.md) - Full project plan
- [Technical Spec](clutchg_technical_spec.md) - Detailed technical documentation
- [Task List](task.md) - Development tasks

### Existing Batch Scripts
- Location: `c:/Users/nextzus/Documents/thesis/bat/src/`
- Documentation: `c:/Users/nextzus/Documents/thesis/bat/docs/`
- Profiles: SAFE, COMPETITIVE, EXTREME

### Libraries
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Modern tkinter
- [psutil](https://github.com/giampaolo/psutil) - System info
- [PyInstaller](https://pyinstaller.org/) - Executable packaging

---

## 💡 Design Inspiration

### Similar Apps
- **Razer Cortex** - Gaming optimization
- **NVIDIA GeForce Experience** - Driver optimization
- **MSI Afterburner** - Hardware monitoring
- **Chris Titus Tech WinUtil** - Windows tweaking

### What We Learned
- ✅ Dashboard-first design
- ✅ One-click operations
- ✅ Clear visual feedback
- ✅ Profile presets over checkboxes
- ✅ Smart auto-recommendations

---

## ✨ Key Differentiators

### vs. Command-Line Batch Scripts
- ✅ No need to use terminal
- ✅ Visual feedback
- ✅ Easy profile switching
- ✅ Built-in backup/restore

### vs. Other GUI Optimizers
- ✅ Uses proven batch scripts from research
- ✅ Modular, extensible design
- ✅ Not over-engineered
- ✅ Open source, transparent
- ✅ Safety-first approach

---

## 🎯 Success Criteria

### Minimum Viable Product (v1.0)
- [x] Launch on Windows 10/11
- [ ] Detect system hardware
- [ ] Show dashboard with system info
- [ ] Display 3 profile choices
- [ ] Execute batch scripts
- [ ] Create/restore backups
- [ ] Show execution progress
- [ ] Log all operations
- [ ] Request admin privileges

### Future Enhancements (v2.0+)
- [ ] Benchmark testing
- [ ] Custom profiles
- [ ] Scheduled optimizations
- [ ] Cloud backup
- [ ] Multi-language
- [ ] Plugin system

---

**Ready to build ClutchG!** 🚀

# ClutchG PC Optimizer v2.0

**Modern, Evidence-Based Windows Optimization Tool**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Quick Start

### Windows (Recommended)
```powershell
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
.\setup_and_test.bat
```

### Manual Installation
```powershell
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
pip install -r requirements.txt
python src\app_minimal.py
```

📖 **[Full Quick Start Guide →](QUICKSTART.md)**

---

## ✨ Features

### Safety First
- ✅ **Risk-Labeled UI** - Traffic-light colors (🟢 LOW 🟡 MEDIUM 🔴 HIGH)
- ✅ **Granular Rollback** - Per-tweak undo capability
- ✅ **Flight Recorder** - Tracks all system changes
- ✅ **Restore Center** - Visual timeline of all operations

### User-Friendly
- ✅ **One-Click Optimize** - Smart profile recommendations
- ✅ **Contextual Help** - "?" buttons everywhere
- ✅ **Bilingual** - English / Thai support
- ✅ **Modern UI** - Clean CustomTkinter interface

### Evidence-Based
- ✅ **Realistic Gains** - 5-15% improvement (not 200% hype)
- ✅ **Documented Tweaks** - Every change explained
- ✅ **Backed by Research** - Based on 28+ tool analysis
- ✅ **Never Compromises Security** - No Defender/UAC disabling

---

## 📸 Key Features

### 🎯 Smart Profile Recommendation
- Analyzes CPU, GPU, RAM automatically
- Recommends SAFE/COMPETITIVE/EXTREME based on hardware
- Considers laptop vs desktop, gaming GPU, user experience level

### 🎨 Risk-Labeled UI
- **Border strips** (4px) show risk level at a glance
- **Risk badges** with icons (🛡️ LOW, ⚠️ MEDIUM, 🔥 HIGH)
- **Color-coded buttons** and tooltips
- **Bilingual help** (English/Thai)

### ⏱️ Restore Center
- **Horizontal timeline** of all operations
- **Per-tweak change list** with before/after values
- **One-click restore** to any snapshot
- **Download rollback scripts** for manual recovery

---

## Architecture

```
clutchg/
├── src/
│   ├── app_minimal.py              # Main app controller
│   ├── core/                       # Business logic
│   │   ├── config.py               # Configuration manager
│   │   ├── system_info.py          # Hardware detection
│   │   ├── profile_manager.py      # Profile management
│   │   ├── profile_recommender.py  # Smart recommendations
│   │   ├── flight_recorder.py      # Change tracking
│   │   ├── batch_parser.py         # Script parser + safety validator
│   │   ├── tweak_registry.py       # Tweak database
│   │   ├── action_catalog.py       # Quick Actions catalog
│   │   └── backup_manager.py       # Backup / restore
│   ├── gui/                        # UI layer
│   │   ├── theme.py                # Theme + icon provider
│   │   ├── views/                  # Page views
│   │   │   ├── dashboard_minimal.py
│   │   │   ├── profiles_minimal.py
│   │   │   ├── scripts_minimal.py
│   │   │   ├── backup_restore_center.py
│   │   │   ├── help_minimal.py
│   │   │   └── settings_minimal.py
│   │   └── components/             # Reusable UI
│   │       ├── enhanced_button.py
│   │       ├── enhanced_sidebar.py
│   │       ├── glass_card.py
│   │       ├── timeline.py
│   │       ├── toast.py
│   │       └── view_transition.py
│   └── utils/                      # Shared helpers
│       ├── logger.py
│       └── admin.py
├── tests/
│   ├── unit/                       # Unit tests (307+ cases)
│   ├── integration/                # Integration tests
│   └── e2e/                        # E2E tests (pywinauto)
├── requirements.txt                # Runtime dependencies
├── requirements-test.txt           # Test dependencies
├── setup_and_test.bat              # Setup script
└── QUICKSTART.md                   # Usage guide
```

---

## 🎯 Optimization Profiles

### SAFE Profile (Recommended)
**Best for:** Daily use, beginners, stability-focused users

**Expected:** 2-5% FPS improvement

**Tweaks:**
- ✅ Ultimate Performance power plan
- ✅ HAGS (Hardware-Accelerated GPU Scheduling)
- ✅ Storage Sense automation
- ✅ Safe network optimizations

---

### COMPETITIVE Profile (Gaming)
**Best for:** Gamers, performance enthusiasts

**Expected:** 5-10% FPS improvement

**Tweaks:**
- ✅ All SAFE optimizations
- ✅ Service optimization (with safety whitelist)
- ✅ Full network tweaks (TCP disabled)
- ✅ GPU power management

---

### EXTREME Profile (Advanced)
**Best for:** Advanced users only

**Expected:** 10-15% FPS improvement

**Tweaks:**
- ✅ All COMPETITIVE optimizations
- ✅ Advanced BCDEdit tweaks
- ⚠️ Aggressive service disabling
- ⚠️ May break some Windows features

---

## 🛡️ Safety Principles

### NEVER Do (Based on Research)
- ❌ Disable Windows Defender
- ❌ Disable Windows Update permanently
- ❌ Disable DEP/ASLR/CFG
- ❌ Modify registry ACLs
- ❌ Disable UAC
- ❌ Delete system files

### ALWAYS Do
- ✅ Create backups before changes
- ✅ Log every modification
- ✅ Validate before applying
- ✅ Provide rollback
- ✅ Document risks

---

## 📊 Performance Comparison

| Tool | Safety | Effectiveness | Transparency |
|------|--------|--------------|-------------|
| **ClutchG** | 10/10 | 8/10 (realistic) | 10/10 |
| WinUtil | 9.5/10 | 9/10 | 9/10 |
| Other tools | 3/10 avg | 4/10 | 2/10 |

**Source:** Analysis of 23 Windows optimization repositories

---

## 🔧 Development

### Setup
```bash
# Clone repository
git clone <repo-url>
cd clutchg

# Install dependencies
pip install -r requirements.txt

# Run app
python src/app_minimal.py
```

### Running Tests
```powershell
cd clutchg

# Full unit + integration suite (381 tests)
pytest tests/unit tests/integration

# Unit tests only
pytest tests/unit -m unit

# Integration tests only
pytest tests/integration -m integration

# E2E tests (requires pywinauto + --app-path)
pytest tests/e2e --app-path src/main.py

# Skip slow tests
pytest --skip-slow

# With coverage report
pytest tests/unit tests/integration --cov=src --cov-report=html
```

### Project Status
- ✅ **Phase 1** - Bug Fixes (validate_script patterns, E2E fixtures, integration assertions, font warning, backup stub)
- ✅ **Phase 2** - MVP Strip-Down (removed 5 unused components, locked theme, cleaned settings)
- ✅ **Phase 3** - Test Coverage (381 tests: config, theme, security, localization, tweak_registry)
- ✅ **Phase 4** - Documentation Sync

---

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get started in 5 minutes
- **[Fixes & Testing](FIXES_AND_TEST.md)** - Recent fixes and troubleshooting
- **[Evidence-Based Implementation](../docs/evidence-based-implementation-summary.md)** - Research backing

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Follow evidence-based principles
4. Test thoroughly
5. Submit a pull request

---

## ⚖️ License

MIT License - See [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- **Research** - Based on analysis of 23 Windows optimization tools
- **Inspiration** - WinUtil, BCDEditTweaks, and other safe tools
- **Framework** - Built with CustomTkinter

---

## ⚠️ Disclaimer

This software modifies Windows settings. Always:
- ✅ Create backups before applying changes
- ✅ Read the documentation
- ✅ Understand the risks
- ❢ The author is not liable for system issues

---

**Made with ❤️ for evidence-based Windows optimization**

**Version:** 1.0.0
**Last Updated:** 2026-03-23

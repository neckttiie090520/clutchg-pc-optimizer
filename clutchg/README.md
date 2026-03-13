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

## 🏗️ Architecture

```
clutchg/
├── src/
│   ├── app_minimal.py          # Main app controller
│   ├── core/                    # Business logic
│   │   ├── config.py            # Configuration
│   │   ├── system_info.py       # Hardware detection
│   │   ├── profile_manager.py   # Profile management
│   │   ├── profile_recommender.py # Smart recommendations
│   │   ├── flight_recorder.py   # Change tracking
│   │   └── batch_parser.py      # Script parser
│   ├── gui/                     # UI layer
│   │   ├── theme.py             # Theme configuration
│   │   ├── views/               # Views
│   │   │   ├── dashboard_minimal.py
│   │   │   ├── profiles_minimal.py
│   │   │   ├── scripts_minimal.py
│   │   │   ├── restore_center_minimal.py
│   │   │   └── ...
│   │   └── components/          # Reusable UI
│   │       ├── risk_badge.py    # Risk indicator
│   │       ├── context_help_button.py
│   │       ├── timeline.py      # Timeline visualization
│   │       └── ...
│   └── data/                    # Runtime data
│       ├── help_content.json    # Bilingual help
│       └── risk_explanations.json
├── requirements.txt             # Dependencies
├── setup_and_test.bat          # Setup script
└── QUICKSTART.md               # Usage guide
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

**Source:** Analysis of 28 Windows optimization repositories

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
```bash
cd src
python test_imports.py      # Test imports
python test_app_init.py      # Test app init
```

### Project Status
- ✅ **Phase 10** - Quick Wins & Core Safety (COMPLETE)
- 🔜 **Phase 11** - Advanced Features (Planning)
- 🔜 **Phase 12** - Strategic Expansion (Future)

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

- **Research** - Based on analysis of 28 Windows optimization tools
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

**Version:** 2.0.0
**Last Updated:** 2025-02-02

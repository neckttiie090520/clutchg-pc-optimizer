<h1 align="center">
  <br>
  <img src="img/C.GG-Photoroom.png" alt="ClutchG" width="120">
  <br>
  ClutchG PC Optimizer
  <br>
</h1>

<p align="center">
  <strong>Evidence-based Windows optimization for competitive gaming</strong>
</p>

<p align="center">
  <a href="#features">Features</a> &middot;
  <a href="#screenshots">Screenshots</a> &middot;
  <a href="#quick-start">Quick Start</a> &middot;
  <a href="#profiles">Profiles</a> &middot;
  <a href="#research">Research</a> &middot;
  <a href="README-TH.md">ภาษาไทย</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D4?logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-477%20passed-2ea44f" alt="Tests">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
</p>

---

## What is ClutchG?

ClutchG is a Windows PC optimization tool built from real research, not myths. We analyzed **23 open-source optimizer repositories** on GitHub (50,000+ lines of code), surveyed over **200 optimization techniques**, and classified **56 vetted tweaks** into 10 categories with a 3-tier risk framework (LOW / MEDIUM / HIGH) to separate what actually works from what's placebo or dangerous.

The result: a modular batch optimizer with a modern Python GUI that applies only evidence-backed tweaks -- safely, transparently, and reversibly.

### Key Principles

| | Principle | What it means |
|---|-----------|--------------|
| **Evidence** | Every tweak backed by technical documentation | No "trust me bro" optimizations |
| **Safety** | Never disables Defender, UAC, DEP, or Windows Update | Security is non-negotiable |
| **Reversible** | Auto-backup before every change, per-tweak rollback | Undo anything, anytime |
| **Transparent** | All actions logged to flight recorder | Full audit trail |
| **Honest** | Realistic 5-15% gains, not 200% | We don't exaggerate |

---

## Features

- **3 Optimization Profiles** -- SAFE, COMPETITIVE, EXTREME with risk-appropriate tweaks
- **56 Vetted Tweaks** across 10 categories: telemetry, input/latency, power, GPU, network, services, memory, boot/BCDEdit, visual effects, cleanup/debloat
- **Auto Hardware Detection** -- identifies CPU, GPU, RAM and recommends the right profile
- **Tweak Encyclopedia** -- every tweak has full documentation: what it does, why it helps, limitations, risk level, and expected gain
- **Flight Recorder** -- logs every change with before/after registry values
- **Restore Center** -- visual timeline of all changes with per-tweak rollback
- **Modern Dark Theme** -- Windows 11 / Sun Valley aesthetic with Figtree typography

---

## Screenshots

<p align="center">
  <img src="UX/UI design/latest/01-dashboard.png" width="720" alt="Dashboard">
  <br><em>Dashboard with hardware detection and profile recommendation</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/02-tweaks-quick-fix.png" width="720" alt="Tweaks - Quick Fix">
  <br><em>Quick Fix tab with one-click optimization actions</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/03-tweaks-profiles.png" width="720" alt="Tweaks - Profiles">
  <br><em>Profile-based optimization with SAFE, COMPETITIVE, and EXTREME presets</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/04-tweaks-custom.png" width="720" alt="Tweaks - Custom">
  <br><em>Custom tweak builder with per-tweak risk levels and controls</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/05-tweaks-education.png" width="720" alt="Tweaks - Education">
  <br><em>Tweak encyclopedia with risk levels, categories, and detailed explanations</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/06-backup.png" width="720" alt="Backup">
  <br><em>Backup and restore center with timeline view</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/07-docs.png" width="720" alt="Documentation">
  <br><em>Built-in help system with documentation and guides</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/08-settings.png" width="720" alt="Settings">
  <br><em>Settings with theme and profile configuration</em>
</p>

---

## Quick Start

### Option A: Use the GUI (Recommended)

```powershell
# Clone the repository
git clone https://github.com/neckttiie090520/clutchg-pc-optimizer.git
cd clutchg-pc-optimizer

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r clutchg\requirements.txt

# Run ClutchG
python clutchg\src\main.py
```

### Option B: Use Batch Scripts Directly

```batch
:: Open Command Prompt as Administrator
cd src
optimizer.bat
```

### Build Standalone Executable

```powershell
cd clutchg
python build.py
# Output: clutchg\dist\ClutchG.exe
```

---

## Profiles

| | Profile | Risk | Target User | Expected Gain |
|---|---------|------|-------------|---------------|
| | **SAFE** | Minimal | Everyone | 2-5% FPS |
| | **COMPETITIVE** | Low | Gamers | 5-10% FPS |
| | **EXTREME** | Medium | Experts only | 10-15% FPS |

### SAFE

Power plan optimization, HAGS, Storage Sense, telemetry services only. Nothing that can break functionality.

### COMPETITIVE

Adds network stack tuning (Nagle's Algorithm, TCP optimization), Xbox/telemetry service management, GPU power management. Still protected by safety whitelist.

### EXTREME

Aggressive service management, BCDEdit boot configuration tweaks, full network stack optimization. Some Windows features may stop working. Understand the tradeoffs before using.

---

## Project Structure

```
clutchg-pc-optimizer/
├── src/                              # Batch Optimizer Engine
│   ├── optimizer.bat                 # Entry point (v2.0, requires admin)
│   ├── core/                         # 16 optimization modules
│   ├── profiles/                     # SAFE / COMPETITIVE / EXTREME
│   ├── safety/                       # Validator, rollback, flight recorder
│   ├── backup/                       # Registry backup, restore points
│   ├── logging/                      # Structured logging
│   ├── ui/                           # Menu system
│   └── validation/                   # Input & benchmark validation
│
├── clutchg/                          # Python GUI Application
│   ├── src/
│   │   ├── main.py                   # Entry point
│   │   ├── core/                     # Business logic (15 modules)
│   │   │   ├── tweak_registry.py     # Central knowledge base (56 tweaks)
│   │   │   ├── profile_manager.py    # Profile ↔ tweak mapping
│   │   │   ├── batch_parser.py       # Discovers tweaks from .bat scripts
│   │   │   ├── action_catalog.py     # User-facing action packs
│   │   │   ├── flight_recorder.py    # Change logging with before/after
│   │   │   └── ...                   # backup, config, system info, etc.
│   │   ├── gui/views/               # 8 view screens
│   │   ├── gui/components/          # 12 reusable components
│   │   └── gui/theme.py             # Dark theme system (Sun Valley)
│   ├── tests/                        # 477 tests (unit + integration + E2E)
│   │   ├── unit/                     # 16 test files
│   │   ├── integration/              # 2 test files
│   │   └── e2e/                      # Page Object Model structure
│   └── build.py                      # PyInstaller build script
│
├── docs/                             # Research & Documentation
│   ├── 01-research-overview.md       # Methodology
│   ├── 02-repo-analysis/             # 23 individual repo analyses
│   ├── 03-tweak-taxonomy.md          # Complete tweak classification
│   ├── 04-risk-classification.md     # Risk assessment matrix
│   ├── 05-windows-internals.md       # Technical deep-dive
│   ├── 06-performance-impact.md      # Realistic benchmarks
│   ├── 07-best-practices.md          # Recommended approach
│   ├── 10-complete-repo-ranking.md   # Full 23-repo ranking with scores
│   ├── 15-user-guide-th.md           # User guide (Thai)
│   ├── 16-user-guide-en.md           # User guide (English)
│   └── iso29110-clutchg/             # 10 ISO 29110 work products
│
└── UX/                               # UI design mockups & screenshots
```

---

## Research

This project started as academic research for a master's thesis in Software Engineering at Chiang Mai University (CMU). We analyzed 23 Windows optimization repositories and scored them on a 5-dimension framework (Safety, Effectiveness, Code Quality, Transparency, Reversibility).

### Key Findings

| Finding | Number |
|---------|--------|
| Repositories analyzed | 23 |
| Optimization techniques surveyed | 200+ |
| Techniques that passed evidence screening | 45 (22.5%) |
| Tweaks implemented in ClutchG | 56 |
| Repos graded F (Fail) | 11 (47.8%) |
| Repos safe for general use (A or above) | 2 (8.7%) |
| Repos that disable Windows Defender | 16 (69.6%) |
| Repos with no backup mechanism | 20 (87.0%) |

### Top-Ranked Repositories

| Rank | Repository | Score | Grade |
|------|-----------|-------|-------|
| 1 | WinUtil (ChrisTitusTech) | 9.5 | A+ |
| 2 | BCDEditTweaks (dubbyOW) | 9.0 | A |
| 3 | Win11-Latency-Opt (NicholasBly) | 8.0 | A- |
| 4 | FR33THY Ultimate Guide | 7.5 | B |
| 5 | win10-latency-opt (denis-g) | 7.5 | B |

### What Actually Works

| Technique | Impact | Evidence |
|-----------|--------|----------|
| GPU driver settings | 2-15% FPS | Vendor-documented, game-dependent |
| Power plan optimization | 2-5% | P-state/C-state management |
| Safe BCDEdit tweaks | 1-4% | Latency-sensitive games |
| Background app reduction | 1-3% | CPU/RAM contention reduction |

### Common Myths Debunked

| Myth | Reality |
|------|---------|
| "Windows reserves 20% bandwidth for QoS" | Only affects tagged traffic, not games |
| "Timer resolution services boost FPS" | Per-process since Windows 10 2004 |
| "Disabling 100 services = faster" | Breaks features, minimal actual gain |
| "Network registry tweaks reduce ping" | ISP and routing matter, not registry |

### Dangerous Patterns Found in Open-Source Optimizers

| Pattern | Prevalence |
|---------|-----------|
| Disables Windows Defender | 16/23 (69.6%) |
| Disables Windows Update | 12/23 (52.2%) |
| Removes exploit mitigations | 10/23 (43.5%) |
| No backup mechanism | 20/23 (87.0%) |
| Deletes system files | 9/23 (39.1%) |

### Never Do These

These are **not included** in any ClutchG profile because they compromise security without worthwhile gains:

- Disable Windows Defender
- Disable DEP / ASLR / CFG
- Disable Driver Signature Enforcement
- Disable Windows Update permanently
- Disable UAC

Full research documents are in [`docs/`](docs/).

---

## Testing

```powershell
cd clutchg

# Install test dependencies
pip install -r requirements-test.txt

# Run full suite
pytest

# Unit tests only
pytest tests\unit -m unit

# Integration tests only
pytest tests\integration -m integration

# With coverage
pytest --cov=src tests/
```

**Current baseline:** 477 passed, 64 skipped (E2E tests skip without display).

CI runs unit and integration tests automatically on `windows-latest` via GitHub Actions.

---

## System Requirements

- **OS:** Windows 10 22H2+ or Windows 11
- **Python:** 3.11+ (for GUI)
- **Admin rights** required for optimization
- **Dependencies:** customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi, tkextrafont

---

## Documentation

| Document | Description |
|----------|-------------|
| [Research Overview](docs/01-research-overview.md) | Methodology and scope |
| [Repo Analysis](docs/02-repo-analysis/) | 23 individual tool analyses |
| [Tweak Taxonomy](docs/03-tweak-taxonomy.md) | Complete classification system (10 categories) |
| [Risk Classification](docs/04-risk-classification.md) | Risk assessment matrix |
| [Windows Internals](docs/05-windows-internals.md) | Technical deep-dive |
| [Performance Impact](docs/06-performance-impact.md) | Realistic expectations |
| [Best Practices](docs/07-best-practices.md) | Recommended approach |
| [Complete Ranking](docs/10-complete-repo-ranking.md) | Full 23-repo scoring and tiers |
| [User Guide (TH)](docs/15-user-guide-th.md) | Thai user guide |
| [User Guide (EN)](docs/16-user-guide-en.md) | English user guide |
| [ISO 29110 Work Products](docs/iso29110-clutchg/) | Software lifecycle documents (10 work products) |

---

## Disclaimer

This software modifies Windows system settings. While extensively researched and tested, results vary by hardware and configuration. Always:

1. Create backups before making changes
2. Start with the SAFE profile
3. Measure performance before and after
4. Understand what each tweak does before enabling it

The authors are not liable for any system issues resulting from use of this software.

---

## License

[MIT](LICENSE)

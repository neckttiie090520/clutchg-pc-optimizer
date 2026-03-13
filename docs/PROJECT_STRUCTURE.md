# 🏗️ โครงสร้างโปรเจค ClutchG Windows Optimizer

> **เวอร์ชัน:** 2.1
> **ปรับปรุงล่าสุด:** 12 มีนาคม 2026
> **วัตถุประสงค์:** เอกสารอ้างอิงหลัก - อ่านครั้งเดียวเข้าใจระบบทั้งหมด

---

## 📋 สารบัญด่วน

| ต้องการอะไร? | ไปที่หัวข้อ |
|--------------|-------------|
| ดูโครงสร้างโฟลเดอร์ทั้งหมด | [🌳 Tree โครงสร้างโปรเจค](#-tree-โครงสร้างโปรเจค) |
| เข้าใจ Data Flow ระหว่าง GUI และ Batch | [🔄 Data/Control Flow](#-datacontrol-flow--clutchg--batch-optimizer) |
| รู้จุดเสี่ยงและข้อควรระวัง | [⚠️ จุดเสี่ยงและข้อควรระวัง](#️-จุดเสี่ยงและข้อควรระวัง) |
| หา Entry Point ของแต่ละส่วน | [🚀 Entry Points](#-entry-points) |
| ดู Execution Paths ต่างๆ | [📍 Execution Paths](#-execution-paths) |
| รู้ว่าแก้อะไรที่ไหนเมื่อต้องการ X | [🔧 What to Edit When You Need X](#-what-to-edit-when-you-need-x) |
| ดูความรับผิดชอบแต่ละโฟลเดอร์ | [👥 Ownership/Responsibility](#-ownershipresponsibility-by-folder) |

---

## 🎯 ภาพรวมโปรเจค (One-Liner)

```
ClutchG = Python GUI (CustomTkinter) + Batch Optimizer Scripts
         └── จัดการ Windows Optimization ผ่าน UI ที่ปลอดภัย มี Backup/Rollback ครบถ้วน
```

### สถาปัตยกรรม 2-Layer

```
┌─────────────────────────────────────────────────────────────────┐
│                    🖥️ LAYER 1: GUI (ClutchG)                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Dashboard  │  │  Profiles   │  │Scripts/Opt. │  ...        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         ▼                ▼                ▼                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              Core Managers (12 classes)                  │   │
│  │  ConfigManager • ProfileManager • BackupManager         │   │
│  │  TweakRegistry • FlightRecorder • BatchExecutor • ...   │   │
│  └────────────────────────────┬────────────────────────────┘   │
└───────────────────────────────┼─────────────────────────────────┘
                                │ subprocess / file I/O
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  ⚙️ LAYER 2: Batch Optimizer                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Profiles   │  │   Core      │  │   Safety    │             │
│  │ (3 levels)  │  │ (15 modules)│  │(backup/log) │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🌳 Tree โครงสร้างโปรเจค

```
bat/                                    # Root Directory
│
├── 📂 clutchg/                         # 🐍 Python GUI Application
│   ├── 📂 src/                         # Source Code
│   │   ├── 🎯 app_minimal.py           # ⭐ GUI Entry Point
│   │   ├── 📄 main.py                  # CLI Entry Point
│   │   ├── 📄 app.py                   # Legacy App
│   │   │
│   │   ├── 📂 core/                    # Business Logic (12 Managers)
│   │   │   ├── config.py               # ConfigManager
│   │   │   ├── system_info.py          # SystemDetector
│   │   │   ├── profile_manager.py      # ProfileManager
│   │   │   ├── profile_recommender.py  # ProfileRecommender
│   │   │   ├── batch_parser.py         # BatchParser
│   │   │   ├── batch_executor.py       # BatchExecutor
│   │   │   ├── tweak_registry.py       # TweakRegistry (62K!)
│   │   │   ├── action_catalog.py       # ActionCatalog
│   │   │   ├── flight_recorder.py      # FlightRecorder
│   │   │   ├── backup_manager.py       # BackupManager
│   │   │   ├── help_manager.py         # HelpManager
│   │   │   └── benchmark_database.py   # BenchmarkDatabase
│   │   │
│   │   ├── 📂 gui/                     # UI Layer
│   │   │   ├── theme.py                # Theme System
│   │   │   ├── style.py                # Style Definitions
│   │   │   ├── icons.py                # Icon Mapping
│   │   │   │
│   │   │   ├── 📂 views/               # 6 Main Views
│   │   │   │   ├── dashboard_minimal.py    # Dashboard
│   │   │   │   ├── profiles_minimal.py     # Profiles
│   │   │   │   ├── scripts_minimal.py      # Optimization Center
│   │   │   │   ├── backup_minimal.py       # Backup
│   │   │   │   ├── help_minimal.py         # Help
│   │   │   │   └── settings_minimal.py     # Settings
│   │   │   │
│   │   │   └── 📂 components/          # 18 Reusable Widgets
│   │   │       ├── toast.py            # Notifications
│   │   │       ├── execution_dialog.py # Progress Dialog
│   │   │       ├── risk_badge.py       # Risk Indicators
│   │   │       ├── stat_card.py        # Hardware Stats
│   │   │       └── ... (14 more)
│   │   │
│   │   ├── 📂 utils/                   # Utilities
│   │   │   ├── admin.py                # Admin Privileges
│   │   │   └── logger.py               # Logging
│   │   │
│   │   └── 📂 data/                    # Runtime Data Files
│   │       ├── help_content.json       # Help Content (EN/TH)
│   │       └── risk_explanations.json  # Risk Explanations
│   │
│   ├── 📂 config/                      # Configuration
│   │   ├── default_config.json         # Default Settings
│   │   └── user_config.json            # User Settings (git-ignored)
│   │
│   ├── 📂 data/                        # Runtime Data
│   │   ├── backups/                    # Registry Backups
│   │   ├── flight_recorder/            # Change Logs
│   │   └── logs/                       # Application Logs
│   │
│   └── 📂 tests/                       # Test Suite (372 tests)
│       ├── conftest.py                 # 12 shared fixtures
│       ├── unit/                       # Unit Tests (285 tests, 12 files)
│       │   ├── test_profile_manager.py         # 11 tests
│       │   ├── test_batch_parser.py             # 18 tests
│       │   ├── test_system_detection.py         # 12 tests
│       │   ├── test_action_catalog.py           # 5 tests
│       │   ├── test_benchmark_database.py       # 22 tests
│       │   ├── test_execution_dialog.py         # 3 tests
│       │   ├── test_core_coverage.py            # 54 tests
│       │   ├── test_admin.py                    # 16 tests (Security Audit)
│       │   ├── test_backup_manager.py           # 35 tests (Security Audit)
│       │   ├── test_flight_recorder.py          # 36 tests (Security Audit)
│       │   ├── test_tweak_registry_integrity.py # 61 tests (Security Audit)
│       │   └── test_help_system.py              # 12 tests (Security Audit)
│       ├── integration/                # Integration Tests (23 tests)
│       └── e2e/                        # E2E UI Tests (64 tests)
│
├── 📂 src/                             # ⚙️ Batch Optimizer
│   ├── 🎯 optimizer.bat                # ⭐ Batch Entry Point
│   │
│   ├── 📂 core/                        # Core Modules (15 .bat)
│   │   ├── system-detect.bat           # Hardware Detection
│   │   ├── power-manager.bat           # Power Plans
│   │   ├── bcdedit-manager.bat         # Boot Config
│   │   ├── service-manager.bat         # Windows Services
│   │   ├── network-optimizer.bat       # Network Tweaks
│   │   ├── gpu-optimizer.bat           # GPU Settings
│   │   ├── telemetry-blocker.bat       # Disable Telemetry
│   │   ├── debloater.bat               # Remove Bloatware
│   │   └── ... (7 more)
│   │
│   ├── 📂 profiles/                    # Optimization Profiles
│   │   ├── safe-profile.bat            # 🟢 SAFE
│   │   ├── competitive-profile.bat     # 🟡 COMPETITIVE
│   │   └── extreme-profile.bat         # 🔴 EXTREME
│   │
│   ├── 📂 safety/                      # Safety Mechanisms
│   │   ├── validator.bat               # Pre-flight Checks
│   │   ├── rollback.bat                # Rollback System
│   │   └── flight-recorder.bat         # Change Tracking
│   │
│   ├── 📂 backup/                      # Backup Utilities
│   │   ├── backup-registry.bat         # Export Registry
│   │   └── restore-point.bat           # System Restore
│   │
│   ├── 📂 logging/                     # Logging System
│   │   └── logger.bat                  # Audit Trail
│   │
│   └── 📂 validation/                  # Validation Tools
│       └── benchmark-runner.bat        # Performance Tests
│
├── 📂 docs/                            # 📚 Research Documentation
│   ├── 01-research-overview.md         # Research Overview
│   ├── 02-repo-analysis/               # 28 Repo Analyses
│   ├── 03-tweak-taxonomy.md            # Tweak Categories
│   ├── 04-risk-classification.md       # Risk Levels
│   └── ... (12 more docs)
│
├── 📂 THESIS_DOCS/                     # 🎓 Thesis Documentation
│   ├── 03-SYSTEM-ANALYSIS/             # System Analysis
│   ├── 05-ARCHITECTURE-DESIGN/         # Architecture
│   ├── 07-TESTING-QUALITY/             # Testing
│   └── ... (7 more chapters)
│
├── 📂 windows-optimizer-research/      # 🔬 Research Repos (28)
│   └── repos/                          # Cloned Repositories
│
└── 📄 README.md, AGENTS.md, ...        # Root Documents
```

---

## 🔄 Data/Control Flow – ClutchG ↔ Batch Optimizer

### Flow Diagram หลัก

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERACTION                                │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GUI LAYER (CustomTkinter)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Dashboard   │  │  Profiles    │  │Scripts/Opt.  │  │   Backup     │    │
│  │    View      │  │    View      │  │    View      │  │    View      │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CORE MANAGERS LAYER                                  │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ ProfileManager  │  │ BatchExecutor   │  │ BackupManager   │             │
│  │                 │  │                 │  │                 │             │
│  │ • load_profile()│  │ • execute()     │  │ • create()      │             │
│  │ • apply()       │  │ • validate()    │  │ • restore()     │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
│           │                    │                    │                       │
│  ┌────────┴────────┐  ┌────────┴────────┐  ┌────────┴────────┐             │
│  │ TweakRegistry   │  │ FlightRecorder  │  │ ConfigManager   │             │
│  │                 │  │                 │  │                 │             │
│  │ • get_tweaks()  │  │ • record()      │  │ • load_config() │             │
│  │ • validate()    │  │ • get_history() │  │ • save_config() │             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  │ subprocess.run()
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BATCH OPTIMIZER LAYER                                │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      optimizer.bat (Entry)                           │   │
│  └─────────────────────────────┬───────────────────────────────────────┘   │
│                                │                                            │
│          ┌─────────────────────┼─────────────────────┐                     │
│          ▼                     ▼                     ▼                     │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐            │
│  │ safety/       │     │ profiles/     │     │ core/         │            │
│  │               │     │               │     │               │            │
│  │ • validator   │     │ • safe        │     │ • power-mgr   │            │
│  │ • rollback    │     │ • competitive │     │ • network-opt │            │
│  │ • flight-rec  │     │ • extreme     │     │ • gpu-opt     │            │
│  └───────────────┘     └───────────────┘     │ • debloater   │            │
│                                              │ • ... (11)    │            │
│                                              └───────────────┘            │
│                                │                                            │
│                                ▼                                            │
│                        ┌───────────────┐                                    │
│                        │ backup/       │                                    │
│                        │ • registry    │                                    │
│                        │ • restore-pt  │                                    │
│                        └───────────────┘                                    │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         WINDOWS SYSTEM                                       │
│                                                                              │
│  Registry • Services • Power Plans • Network • GPU • Storage • etc.        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interaction Sequence (Apply Profile)

```
USER: Click "Apply SAFE Profile"
        │
        ▼
┌───────────────────────────────────────┐
│ ProfilesView._on_apply_click()        │
│ └── Show confirmation dialog          │
└───────────────┬───────────────────────┘
                │ [CONFIRM]
                ▼
┌───────────────────────────────────────┐
│ BackupManager.create_backup()         │
│ └── Export registry to JSON           │
│ └── Create restore point              │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ FlightRecorder.record_pending()       │
│ └── Store: timestamp, profile, tweaks │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ ProfileManager.apply_profile("safe")  │
│ └── BatchExecutor.execute(            │
│         "src/profiles/safe-profile.bat│
│     )                                 │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ BATCH: safe-profile.bat               │
│ ├── CALL core/power-manager.bat       │
│ ├── CALL core/network-optimizer.bat   │
│ ├── CALL core/service-manager.bat     │
│ └── CALL logging/logger.bat           │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ FlightRecorder.record_result()        │
│ └── Store: success/fail, changes      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ ToastManager.show("Profile Applied!") │
└───────────────────────────────────────┘
```

---

## ⚠️ จุดเสี่ยงและข้อควรระวัง

### 🔴 จุดที่ต้องรันด้วย Admin Privileges

| Operation | ไฟล์/Module | เหตุผล |
|-----------|-------------|--------|
| Registry modification | `src/core/*.bat`, `BackupManager` | ต้องเขียน HKLM |
| Service management | `service-manager.bat` | ต้อง start/stop services |
| Power plan creation | `power-manager.bat` | ต้องสร้าง power scheme |
| BCD edit | `bcdedit-manager.bat` | ต้องแก้ boot config |
| System restore point | `restore-point.bat` | ต้องสร้าง restore |
| Telemetry blocking | `telemetry-blocker.bat` | ต้องแก้ services/registry |

### 🟡 Operations ที่ต้อง Backup ก่อนเสมอ

| Operation | Backup Type | ไฟล์ที่รับผิดชอบ |
|-----------|-------------|------------------|
| Apply Profile | Registry + Restore Point | `BackupManager`, `restore-point.bat` |
| Run Quick Action | Registry | `BackupManager` |
| Modify Services | Registry | `BackupManager` |
| GPU Optimization | Registry | `BackupManager` |
| Network Optimization | Registry | `BackupManager` |

### 🔵 จุดเสี่ยงตาม Risk Level

| Risk Level | หมวด Tweaks | ความเสี่ยง | ต้องการ Confirmation |
|------------|-------------|------------|---------------------|
| 🟢 LOW | Visual effects, Power settings | ต่ำ - Reversible | No (optional) |
| 🟡 MEDIUM | Services, Network, GPU | กลาง - May affect stability | Yes |
| 🔴 HIGH | BCD, Registry core, System files | สูง - May brick system | Yes + Warning |
| ⛔ CRITICAL | Disable Defender, UAC, DEP | ต้องห้าม - Security risk | **BLOCKED** |

### 🚫 สิ่งที่ห้ามทำ (Project Rules)

```python
# ❌ ห้ามปิด:
# - Windows Defender
# - UAC (User Account Control)
# - DEP/ASLR/CFG
# - Windows Update (completely)

# ❌ ห้ามลบ:
# - System files
# - Critical registry keys
# - Required services

# ✅ ต้องทำเสมอ:
# - Backup ก่อนแก้ Registry
# - Log ทุก operation
# - Provide rollback path
```

---

## 🚀 Entry Points

### Entry Points Summary

| Type | File | Command | Notes |
|------|------|---------|-------|
| 🖥️ GUI | [`clutchg/src/app_minimal.py`](clutchg/src/app_minimal.py) | `python app_minimal.py` | Main GUI application |
| 📋 CLI | [`clutchg/src/main.py`](clutchg/src/main.py) | `python main.py` | CLI interface |
| ⚙️ Batch | [`src/optimizer.bat`](src/optimizer.bat) | `optimizer.bat` (Admin) | Direct batch execution |

### GUI Entry: `clutchg/src/app_minimal.py`

```python
# Entry point: ClutchGApp class
class ClutchGApp:
    def __init__(self, test_mode: bool = False, config_path: Optional[str] = None):
        # 1. Load Configuration
        self.config_manager = ConfigManager(config_dir)
        self.config = self.config_manager.load_config()
        
        # 2. Initialize Theme
        theme_manager.set_theme(saved_theme, saved_accent)
        
        # 3. Initialize Core Managers
        self.profile_manager = ProfileManager(self.batch_scripts_dir)
        self.help_manager = HelpManager()
        self.action_catalog = ActionCatalog()
        
        # 4. Detect System
        self.system_detector = SystemDetector()
        
        # 5. Setup UI
        self.setup_ui()
```

### CLI Entry: `clutchg/src/main.py`

```python
# Entry point: main() function
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", choices=["safe", "competitive", "extreme"])
    parser.add_argument("--backup", action="store_true")
    # ...
```

### Batch Entry: `src/optimizer.bat`

```batch
@echo off
:: Entry point: Main menu
:: Must run as Administrator

:: 1. Check admin
net session >nul 2>&1 || (
    echo ERROR: Run as Administrator!
    exit /b 1
)

:: 2. Initialize
call safety/validator.bat

:: 3. Show menu
:menu
echo [1] Apply SAFE Profile
echo [2] Apply COMPETITIVE Profile
echo [3] Apply EXTREME Profile
echo [4] Rollback
echo [5] Exit
```

---

## 📍 Execution Paths

### 1. Profile Application Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROFILE APPLICATION FLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

USER selects profile
        │
        ▼
┌───────────────────┐
│ Pre-flight Check  │
│ (validator.bat)   │
│ • Admin?          │
│ • OS compatible?  │
│ • Hardware OK?    │
└─────────┬─────────┘
          │ [PASS]
          ▼
┌───────────────────┐
│ System Detection  │
│ (system-detect)   │
│ • Export OS_VER   │
│ • Export CPU/GPU  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Create Backup     │
│ • Registry export │
│ • Restore point   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Apply Profile     │
│ [X]-profile.bat   │
└─────────┬─────────┘
          │
          ├──────────────────────────────────────┐
          │                                      │
          ▼                                      ▼
┌───────────────────┐                  ┌───────────────────┐
│ power-manager.bat │                  │ network-opt.bat   │
└───────────────────┘                  └───────────────────┘
          │                                      │
          ├──────────────────────────────────────┤
          │                                      │
          ▼                                      ▼
┌───────────────────┐                  ┌───────────────────┐
│ gpu-optimizer.bat │                  │ service-manager   │
└───────────────────┘                  └───────────────────┘
          │                                      │
          └──────────────────┬───────────────────┘
                             │
                             ▼
                    ┌───────────────────┐
                    │ Log all changes   │
                    │ (logger.bat)      │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Show summary      │
                    └───────────────────┘
```

### 2. Backup/Restore Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BACKUP/RESTORE FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

BACKUP:
┌───────────────────┐
│ User clicks       │
│ "Create Backup"   │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ BackupManager     │
│ .create_backup()  │
└─────────┬─────────┘
          │
          ├──────────────────────────────────────┐
          │                                      │
          ▼                                      ▼
┌───────────────────┐                  ┌───────────────────┐
│ Export Registry   │                  │ Create Restore    │
│ to JSON file      │                  │ Point             │
│ (backup-registry) │                  │ (restore-point)   │
└───────────────────┘                  └───────────────────┘
          │                                      │
          └──────────────────┬───────────────────┘
                             │
                             ▼
                    ┌───────────────────┐
                    │ Update index      │
                    │ backup_index.json │
                    └───────────────────┘


RESTORE:
┌───────────────────┐
│ User selects      │
│ backup point      │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Show confirmation │
│ + risk warning    │
└─────────┬─────────┘
          │ [CONFIRM]
          ▼
┌───────────────────┐
│ BackupManager     │
│ .restore(backup)  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Import Registry   │
│ from JSON         │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Log restore       │
│ operation         │
└───────────────────┘
```

### 3. Rollback Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ROLLBACK FLOW                                      │
└─────────────────────────────────────────────────────────────────────────────┘

USER clicks "Rollback"
        │
        ▼
┌───────────────────┐
│ Load change log   │
│ (flight_recorder) │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Show timeline     │
│ of changes        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ User selects      │
│ restore point     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ ⚠️ Warning: This  │
│ will revert ALL   │
│ changes after X   │
└─────────┬─────────┘
          │ [CONFIRM]
          ▼
┌───────────────────┐
│ rollback.bat      │
│ • Revert registry │
│ • Restart services│
│ • Log rollback    │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Prompt restart    │
│ (some changes     │
│ need reboot)      │
└───────────────────┘
```

---

## 👥 Ownership/Responsibility by Folder

### Responsibility Matrix

| Folder | Owner | หน้าที่หลัก | ไฟล์สำคัญ |
|--------|-------|-------------|-----------|
| `clutchg/src/core/` | Backend Logic | Business logic, state management | All 12 managers |
| `clutchg/src/gui/views/` | UI/UX | User interface, interactions | 6 view files |
| `clutchg/src/gui/components/` | UI Components | Reusable widgets | 18 components |
| `clutchg/src/utils/` | Infrastructure | Logging, admin checks | admin.py, logger.py |
| `src/core/` | Batch Logic | System modifications | 15 .bat files |
| `src/profiles/` | Optimization | Profile definitions | 3 profiles |
| `src/safety/` | Safety | Validation, rollback | 3 safety files |
| `src/backup/` | Data Protection | Backup/restore | 2 backup files |
| `docs/` | Documentation | Research docs | 16+ markdown files |
| `THESIS_DOCS/` | Thesis | Academic documentation | 10 chapters |

### Module Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPENDENCY GRAPH                                     │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  app_minimal.py │
                    │   (Entry)       │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ ConfigManager   │ │ SystemDetector  │ │ ProfileManager  │
└─────────────────┘ └─────────────────┘ └────────┬────────┘
                                               │
                              ┌────────────────┼────────────────┐
                              │                │                │
                              ▼                ▼                ▼
                    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
                    │ BatchExecutor   │ │ TweakRegistry│ │ FlightRecorder  │
                    └────────┬────────┘ └─────────────┘ └─────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ optimizer.bat   │
                    │ (Batch Layer)   │
                    └─────────────────┘
```

---

## 🔧 What to Edit When You Need X

### Quick Reference Table

| ต้องการ | แก้ไฟล์ไหน | โฟลเดอร์ | หมายเหตุ |
|---------|-----------|----------|---------|
| **เพิ่ม Tweak ใหม่** | `tweak_registry.py` | `clutchg/src/core/` | เพิ่มใน dict TWEAKS |
| | `*.bat` (new or existing) | `src/core/` | Implement tweak logic |
| **เพิ่มหน้า GUI ใหม่** | `new_view_minimal.py` | `clutchg/src/gui/views/` | Create view class |
| | `app_minimal.py` | `clutchg/src/` | Register in sidebar |
| **เพิ่ม Profile ใหม่** | `new-profile.bat` | `src/profiles/` | Define tweaks |
| | `profile_manager.py` | `clutchg/src/core/` | Register profile |
| **เพิ่ม Help Topic** | `help_content.json` | `clutchg/src/data/` | Add EN/TH content |
| **เปลี่ยน Theme/Colors** | `theme.py` | `clutchg/src/gui/` | Modify COLORS dict |
| **เพิ่ม Backup Type** | `backup_manager.py` | `clutchg/src/core/` | Add backup method |
| | `backup-*.bat` | `src/backup/` | Implement in batch |
| **แก้ Batch Script** | `*.bat` | `src/core/` | Core modules |
| | `*.bat` | `src/profiles/` | Profile scripts |
| **เพิ่ม Quick Action** | `action_catalog.py` | `clutchg/src/core/` | Add to ACTIONS |
| **เพิ่ม Component** | `new_component.py` | `clutchg/src/gui/components/` | Create widget |
| **เปลี่ยน Risk Level** | `risk_explanations.json` | `clutchg/src/data/` | Update definitions |
| | `tweak_registry.py` | `clutchg/src/core/` | Update risk field |
| **เพิ่ม Test** | `test_*.py` | `clutchg/tests/unit/` | Unit test |
| | `test_*.py` | `clutchg/tests/integration/` | Integration test |

### Detailed Examples

#### 1. เพิ่ม Tweak ใหม่

```python
# clutchg/src/core/tweak_registry.py

TWEAKS = {
    # ... existing tweaks ...
    
    "my_new_tweak": {
        "id": "my_new_tweak",
        "name": "My New Tweak",
        "name_th": "ทวีคใหม่ของฉัน",
        "category": "performance",
        "risk": "low",
        "description": "Does something cool",
        "description_th": "ทำอะไรบางอย่างที่เจ๋ง",
        "registry_changes": [
            {
                "path": r"HKLM\SOFTWARE\MyApp",
                "value": "EnableFeature",
                "data": 1,
                "type": "REG_DWORD"
            }
        ],
        "batch_script": "my-tweak.bat",  # Optional
        "requires_restart": False
    }
}
```

```batch
:: src/core/my-tweak.bat
@echo off
call logging/logger.bat "INFO" "Applying my new tweak"
reg add "HKLM\SOFTWARE\MyApp" /v EnableFeature /t REG_DWORD /d 1 /f
call logging/logger.bat "SUCCESS" "My new tweak applied"
```

#### 2. เพิ่มหน้า GUI ใหม่

```python
# clutchg/src/gui/views/my_view_minimal.py

import customtkinter as ctk
from gui.theme import COLORS

class MyView(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg_primary"])
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        # Add widgets here
        label = ctk.CTkLabel(self, text="My New View")
        label.pack(pady=20)
```

```python
# clutchg/src/app_minimal.py - Add to setup_ui()

from gui.views.my_view_minimal import MyView

# In sidebar setup:
self.sidebar.add_nav_item(
    "my_view",
    icon="star",
    label="My View",
    view_class=MyView
)
```

#### 3. เพิ่ม Profile ใหม่

```batch
:: src/profiles/gaming-profile.bat

@echo off
setlocal enabledelayedexpansion

:: Log start
call logging/logger.bat "INFO" "Starting GAMING profile"

:: Apply tweaks
call core/power-manager.bat :set_high_performance
call core/gpu-optimizer.bat :enable_game_mode
call core/network-optimizer.bat :optimize_gaming
call core/service-manager.bat :disable_xbox_bar

:: Log completion
call logging/logger.bat "SUCCESS" "GAMING profile applied"
```

---

## 📊 สรุป Metrics

### Code Statistics

| Component | ไฟล์ | ขนาดรวม |
|-----------|------|---------|
| Python Core | 12 | ~200 KB |
| Python GUI Views | 9 | ~180 KB |
| Python Components | 18 | ~140 KB |
| Batch Core | 15 | ~120 KB |
| Batch Profiles | 3 | ~27 KB |
| Batch Safety/Backup | 5 | ~25 KB |
| Documentation | 30+ | ~500 KB |

### Feature Coverage

| Feature | Status | Implementation |
|---------|--------|----------------|
| Profile Application | ✅ | `ProfileManager` + batch profiles |
| Backup/Restore | ✅ | `BackupManager` + batch backup |
| Rollback | ✅ | `FlightRecorder` + rollback.bat |
| Quick Actions | ✅ | `ActionCatalog` + `TweakRegistry` |
| Help System | ✅ | `HelpManager` + JSON content |
| Theme System | ✅ | `theme.py` + multiple themes |
| Localization | ✅ | EN/TH in JSON files |
| Risk Indicators | ✅ | `RiskBadge` + risk_explanations.json |

---

## 🔗 เอกสารที่เกี่ยวข้อง

| เอกสาร | ที่อยู่ | วัตถุประสงค์ |
|---------|--------|--------------|
| Thesis Overview | [`THESIS_DOCS/README.md`](../THESIS_DOCS/README.md) | ภาพรวมวิทยานิพนธ์ |
| Architecture Design | [`THESIS_DOCS/05-ARCHITECTURE-DESIGN/`](../THESIS_DOCS/05-ARCHITECTURE-DESIGN/README.md) | การออกแบบสถาปัตยกรรม |
| Testing & Quality | [`THESIS_DOCS/07-TESTING-QUALITY/`](../THESIS_DOCS/07-TESTING-QUALITY/README.md) | การทดสอบ |
| Developer Guide | [`THESIS_DOCS/CLUTCHG_DEVELOPER_GUIDE.md`](../THESIS_DOCS/CLUTCHG_DEVELOPER_GUIDE.md) | คู่มือนักพัฒนา |
| User Guide | [`THESIS_DOCS/CLUTCHG_USER_GUIDE.md`](../THESIS_DOCS/CLUTCHG_USER_GUIDE.md) | คู่มือผู้ใช้ |
| Safety & Rollback | [`THESIS_DOCS/SAFETY_AND_ROLLBACK.md`](../THESIS_DOCS/SAFETY_AND_ROLLBACK.md) | ความปลอดภัย |
| Risk Classification | [`docs/04-risk-classification.md`](04-risk-classification.md) | ระดับความเสี่ยง |
| Tweak Taxonomy | [`docs/03-tweak-taxonomy.md`](03-tweak-taxonomy.md) | หมวดหมู่ Tweaks |

---

## 📝 Assumptions

1. **โครงสร้างอาจเปลี่ยนแปลง**: เอกสารนี้อิงจากสถานะปัจจุบันของโปรเจค
2. **Entry points**: `app_minimal.py` เป็น GUI entry หลัก, `main.py` เป็น CLI entry
3. **Batch scripts**: ต้องรันด้วย Administrator privileges
4. **Python version**: ใช้ Python 3.8+ กับ CustomTkinter
5. **Windows version**: รองรับ Windows 10/11 เท่านั้น

---

**เอกสารนี้ปรับปรุงเมื่อ:** 12 มีนาคม 2026
**เวอร์ชัน:** 2.1
**ผู้สร้าง:** Documentation Specialist (Code Mode)

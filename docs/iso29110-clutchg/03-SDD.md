# 03 — เอกสารการออกแบบซอฟต์แวร์ (Software Design Document)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O3 (Software Design)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.0 | **วันที่:** 2026-03-04 | **อ้างอิง SRS:** v3.0
> **อ้างอิง:** ISO/IEC 42010:2011, Gang of Four Design Patterns

---

## 1. ภาพรวมสถาปัตยกรรม (Architecture Overview)

### 1.1 Architectural Style
**Hybrid Layered Architecture** — ผสมระหว่าง Python GUI Application กับ Windows Batch Script Engine

Design Decisions:
- **Batch scripts** ทำ system-level changes (registry, services, bcdedit) เพราะ:
  - .bat มี native reg/sc/bcdedit commands
  - ไม่ต้อง compile, แก้ไขง่าย
  - สามารถ validate/review ได้ง่าย
- **Python GUI** จัดการ orchestration, UI, safety logic เพราะ:
  - CustomTkinter ให้ modern UI บน Windows
  - Python มี ecosystem สำหรับ system info (psutil, WMI, GPUtil)
  - Type safety ด้วย dataclass + type hints

### 1.2 Layer Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Presentation Layer (GUI)                       │
│  ┌───────────┬────────────┬──────────┬───────────┬─────────────┐ │
│  │ Dashboard │  Profiles  │ Scripts  │  Backup   │ Help/Settings│ │
│  │   View    │    View    │  View    │  Center   │    View     │ │
│  └─────┬─────┴─────┬──────┴────┬─────┴─────┬─────┴──────┬──────┘ │
│        │           │           │           │            │         │
│  ┌─────┴───────────┴───────────┴───────────┴────────────┴──────┐ │
│  │           GUI Components (Reusable Widgets)                  │ │
│  │  RiskBadge · Toast · Timeline · Sidebar · ExecutionDialog    │ │
│  └──────────────────────────┬───────────────────────────────────┘ │
├─────────────────────────────┼────────────────────────────────────┤
│                    Business Logic Layer (Core)                    │
│  ┌──────────────────────────┼───────────────────────────────────┐ │
│  │  ┌──────────────┐  ┌────┴──────┐  ┌──────────────────────┐  │ │
│  │  │  ProfileMgr  │  │  Tweak    │  │  SystemDetector      │  │ │
│  │  │  (528 lines) │  │ Registry  │  │  + BenchmarkDB       │  │ │
│  │  │              │  │(1013 lines)│  │  + ProfileRecommender│  │ │
│  │  └──────┬───────┘  └───────────┘  └──────────────────────┘  │ │
│  │         │                                                     │ │
│  │  ┌──────┴───────┐  ┌─────────────┐  ┌────────────────────┐  │ │
│  │  │ BatchParser  │  │ BackupMgr   │  │  FlightRecorder    │  │ │
│  │  │ + Executor   │  │ (373 lines) │  │  (589 lines)       │  │ │
│  │  │ (20KB)       │  │             │  │                    │  │ │
│  │  └──────┬───────┘  └──────┬──────┘  └─────────┬──────────┘  │ │
│  └─────────┼────────────────┼────────────────────┼──────────────┘ │
├────────────┼────────────────┼────────────────────┼───────────────┤
│            │   Infrastructure Layer              │                │
│  ┌─────────┴──────┐ ┌──────┴──────┐  ┌──────────┴─────────────┐ │
│  │  Batch Scripts  │ │  Registry   │  │  JSON Storage          │ │
│  │  (.bat files)   │ │  (Windows)  │  │  (config, backups,     │ │
│  │  src/core/      │ │  HKLM/HKCU  │  │   flight_records)      │ │
│  └────────────────┘ └─────────────┘  └────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

### 1.3 Design Patterns Used

| Pattern | ที่ใช้ | วัตถุประสงค์ | อ้างอิง |
|---------|-------|------------|---------|
| **Singleton** | TweakRegistry, FlightRecorder | ใช้ instance เดียวทั้ง app | GoF, 1994 |
| **Observer** (Callback) | on_output, on_progress, on_tweak_status | Real-time UI updates ระหว่าง apply | GoF, 1994 |
| **Strategy** | Profile presets (SAFE/COMPETITIVE/EXTREME) | เลือก strategy ต่างกัน | GoF, 1994 |
| **Template Method** | start_recording → record → finish_recording | Structured recording workflow | GoF, 1994 |
| **Data Transfer Object** | Tweak, Profile, SystemProfile, TweakChange, BackupInfo | Type-safe data passing | Fowler, PoEAA |
| **Repository** | TweakRegistry (get_all, get_by_id, get_by_category, filter) | Centralized data access | Evans, DDD |
| **Facade** | ProfileManager, ClutchGApp | Simplify complex subsystem access | GoF, 1994 |
| **Command** | rollback_command field in TweakChange | Encapsulate undo operations | GoF, 1994 |

---

## 2. โครงสร้างคอมโพเนนต์โดยละเอียด (Detailed Component Design)

### 2.1 Core Layer

#### 2.1.1 TweakRegistry (`core/tweak_registry.py` — 1013 lines, 62.6KB)
**หน้าที่:** Central knowledge base ของ tweaks ทั้งหมด — single source of truth

```
TweakRegistry (Singleton)
├── _tweaks: Dict[str, Tweak]          # 48 tweaks indexed by ID
├── get_all_tweaks() → List[Tweak]
├── get_tweak(id) → Optional[Tweak]
├── get_tweaks_by_category(cat) → List[Tweak]
├── get_tweaks_for_preset(preset) → List[Tweak]
├── get_compatible_tweaks(profile) → List[Tweak]     # Filter by OS + hardware
├── suggest_preset(profile) → Dict                    # Auto-recommend
├── get_category_stats() → Dict[str, int]
├── get_risk_distribution() → Dict[str, int]
└── build_custom_preset(ids) → Dict                   # Validate + build

Constants:
├── TWEAK_CATEGORIES: Dict[str, {icon, color, label}]  # 10 categories
└── _build_tweaks() → List[Tweak]                      # Factory function
```

**Algorithm: get_compatible_tweaks()**
```
Input: SystemProfile (OS version, GPU vendor, CPU vendor)
for each tweak in registry:
    if tweak.compatible_os does not contain OS version → skip
    if tweak requires GPU vendor and doesn't match → skip
    if tweak requires CPU vendor and doesn't match → skip
    → add to compatible list
Output: List[Tweak] (filtered)
```

#### 2.1.2 ProfileManager (`core/profile_manager.py` — 528 lines, 19KB)
**หน้าที่:** Orchestrate profile loading, tweak execution, preset management

```
ProfileManager
├── __init__(batch_scripts_dir: Path)
├── profiles: Dict[str, Profile]
├── registry: TweakRegistry
│
├── _load_profiles()                  # Build SAFE/COMPETITIVE/EXTREME
├── get_profile(name) → Profile
├── get_all_profiles() → List[Profile]
├── apply_profile(profile, callbacks...) → bool   # Main execution
├── apply_tweaks(tweak_ids, callbacks...) → bool  # Individual tweaks
├── verify_scripts(profile) → bool
│
├── save_custom_preset(name, tweak_ids)
├── load_custom_presets() → Dict
├── export_preset_to_file(name, ids, path)
└── import_preset_from_file(path) → Dict
```

**Main Algorithm: apply_profile()**
```
1. Create backup (BackupManager.create_backup)
2. Start flight recording (FlightRecorder.start_recording)
3. Get tweaks from registry for this profile
4. For each tweak (i / total):
   a. Get batch script path + function name
   b. Validate script exists
   c. on_progress(i / total * 100)
   d. BatchExecutor.execute(script, function)
   e. on_tweak_status(tweak.name, "done")
   f. Record change in FlightRecorder
5. Finish recording (FlightRecorder.finish_recording)
6. Return success status
```

#### 2.1.3 FlightRecorder (`core/flight_recorder.py` — 616 lines, ~21KB)
**หน้าที่:** บันทึกทุกการเปลี่ยนแปลงเพื่อ per-tweak rollback (rewritten v2.1 — security hardened)

```
FlightRecorder (Singleton)
├── storage_dir: Path
├── logs_dir: Path / "change_logs/"       # JSON files
├── snapshots_dir: Path / "registry_snapshots/"  # .reg files
├── current_snapshot: Optional[SystemSnapshot]
│
├── start_recording(type, profile) → SystemSnapshot
│   └── _capture_registry_snapshot(id, "before")  # reg export
├── record_change(name, category, key_path, old, new, ...) → TweakChange
│   └── _generate_rollback_command(category, key, old, type) → str
├── record_registry_change(name, key, value, old, new, ...) → TweakChange
├── finish_recording(success, error) → SystemSnapshot
│   └── _capture_registry_snapshot(id, "after")
│
├── get_snapshot(id) → SystemSnapshot       (Load JSON)
├── list_snapshots(limit=50) → List         (Newest first)
├── compare_snapshots(before, after) → List[TweakChange]
├── generate_rollback_script(id) → Path     (.bat file)
└── cleanup_old_snapshots(keep_days=30)
```

**Algorithm: _generate_rollback_command()**
```
Input: ChangeCategory, key_path, old_value, value_type
if category == REGISTRY:
    parse key_path → root_key, subkey, value_name
    return: reg add "HKLM\subkey" /v value_name /t REG_DWORD /d old_value /f
else:
    return: generic comment "# Rollback: path → old_value"
```

#### 2.1.4 BackupManager (`core/backup_manager.py` — 373 lines, 13.6KB)
**หน้าที่:** Create/restore/manage registry backups + Windows restore points

```
BackupManager
├── backup_dir: Path / "data/backups/"
├── index_file: Path / "backup_index.json"
├── backups: List[BackupInfo]
│
├── create_backup(name, profile, restore_point, registry) → BackupInfo
│   ├── _create_restore_point(name) → bool
│   │   ├── Method 1: PowerShell Checkpoint-Computer
│   │   └── Method 2: WMIC fallback
│   ├── _backup_registry(path) → bool
│   │   └── Export 6 registry keys to .reg files:
│   │       ├── HKLM\SYSTEM\CurrentControlSet\Services
│   │       ├── HKLM\SYSTEM\CurrentControlSet\Control\Power
│   │       ├── HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer
│   │       ├── HKLM\SOFTWARE\Policies\Microsoft\Windows
│   │       ├── HKCU\Control Panel\Desktop
│   │       └── HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer
│   └── _cleanup_old_backups(max=10)
│
├── restore_registry(backup_id) → bool       (reg import *.reg)
├── delete_backup(backup_id) → bool
└── get_all_backups() → List[BackupInfo]
```

#### 2.1.5 SystemDetector (`core/system_info.py` — 381 lines, 11.5KB)
**หน้าที่:** Hardware detection + scoring สำหรับ profile recommendation

```
SystemDetector
├── wmi_conn: Optional[WMI]
├── benchmark_db: BenchmarkDatabase
│
├── detect_all() → SystemProfile
│   ├── detect_os() → OSInfo
│   ├── detect_cpu() → CPUInfo          # cpuinfo → psutil → WMI
│   ├── detect_gpu() → GPUInfo          # nvidia-smi → WMI → psutil fallback
│   ├── detect_ram() → RAMInfo          # psutil
│   ├── detect_storage() → StorageInfo  # WMI Get-PhysicalDisk → psutil fallback
│   ├── detect_form_factor() → str      # battery check
│   └── calculate_tier(score) → str     # entry/mid/high/enthusiast
│
└── recommend_profile(system) → str     # Laptop→SAFE, Desktop→score-based

Score Calculation:
  total_score = cpu.score(0-30) + gpu.score(0-30) + ram.score(0-20) + storage.score(0-10)
  tier = enthusiast(≥70) | high(50-69) | mid(30-49) | entry(<30)
```

### 2.2 Presentation Layer (GUI)

#### 2.2.1 ClutchGApp — Main Controller (`app_minimal.py` — 324 lines)

```
ClutchGApp
├── config_manager: ConfigManager
├── system_detector: SystemDetector
├── profile_manager: ProfileManager
├── help_manager: HelpManager
├── action_catalog: ActionCatalog
├── toast: ToastManager
│
├── __init__(test_mode, config_path)
│   ├── Load config (theme, accent, language)
│   ├── Init managers
│   ├── Setup CTk window (1000×700)
│   ├── Start async system detection
│   └── Show welcome overlay (first run)
│
├── setup_ui()
│   ├── Create EnhancedSidebar (left column)
│   ├── Create main_frame (right column)
│   ├── Init ViewTransition manager
│   └── Load initial view (dashboard)
│
├── switch_view(name, immediate)      # View router
│   ├── "dashboard" → DashboardView
│   ├── "profiles" → ProfilesView
│   ├── "scripts" → ScriptsView
│   ├── "backup" → BackupRestoreCenter
│   ├── "help" → HelpView
│   └── "settings" → SettingsView
│
├── switch_theme(theme, accent)       # Theme hot-swap
└── run()                             # mainloop()
```

#### 2.2.2 View Size Analysis

| View | File Size | Lines (est.) | Complexity | หน้าที่ |
|------|----------|-------------|-----------|---------|
| Scripts | 63.5KB | ~1800 | สูงสุด | 48 tweaks, 10 categories, checkboxes, apply |
| Backup/Restore | 35.7KB | ~1000 | สูง | Timeline, per-tweak undo, snapshot details |
| Dashboard | 25.8KB | ~730 | ปานกลาง | System cards, score display, detection |
| Help | 23.3KB | ~660 | ปานกลาง | Content rendering, bilingual, search |
| Backup (Legacy) | 18.6KB | ~530 | ปานกลาง | Simple backup list |
| Welcome | 12.7KB | ~360 | ต่ำ | First-run overlay |
| Settings | 12KB | ~340 | ต่ำ | Theme/accent/language selectors |
| Profiles | 10.7KB | ~300 | ต่ำ | 3 profile cards |

---

## 3. Sequence Diagrams

### 3.1 Apply Profile Sequence

```
User          ProfilesView    ProfileManager    BackupManager    FlightRecorder    BatchExecutor
  │    Click      │                │                │                │                │
  │   "Apply"     │                │                │                │                │
  │──────────────►│                │                │                │                │
  │               │  apply_profile │                │                │                │
  │               │───────────────►│                │                │                │
  │               │                │  create_backup │                │                │
  │               │                │───────────────►│                │                │
  │               │                │  ◄── BackupInfo│                │                │
  │               │                │                │                │                │
  │               │                │  start_recording                │                │
  │               │                │────────────────────────────────►│                │
  │               │                │                                 │ reg export     │
  │               │                │  ◄── SystemSnapshot             │ (before)       │
  │               │                │                                 │                │
  │               │                │  FOR EACH tweak (1..N):         │                │
  │               │                │     on_progress(i/N*100)        │                │
  │  ◄───progress─┤                │                                 │                │
  │               │                │     execute(script, function)   │                │
  │               │                │─────────────────────────────────────────────────►│
  │               │                │                                 │    subprocess  │
  │               │                │  ◄── output ─────────────────────────────────────│
  │               │                │     record_change(before,after) │                │
  │               │                │────────────────────────────────►│                │
  │               │                │                                 │                │
  │               │                │  finish_recording               │                │
  │               │                │────────────────────────────────►│                │
  │               │                │                                 │ reg export     │
  │               │                │                                 │ (after)        │
  │               │                │                                 │ save JSON      │
  │               │  ◄── success   │                                 │                │
  │  Toast ◄──────┤                │                                 │                │
  │ "Applied!"    │                │                                 │                │
```

### 3.2 Rollback Per-Tweak Sequence

```
User          RestoreCenter     FlightRecorder
  │    Click       │                 │
  │  "Undo tweak"  │                 │
  │───────────────►│                 │
  │                │  get_snapshot(id)│
  │                │────────────────►│
  │                │  ◄── snapshot   │
  │                │                 │
  │                │  tweak.rollback_command
  │                │  subprocess.run("reg add ... /d old_value /f")
  │                │                 │
  │  Toast ◄───────┤                 │
  │  "Undone!"     │                 │
```

### 3.3 System Detection Sequence

```
ClutchGApp           SystemDetector       nvidia-smi    psutil    WMI    BenchmarkDB
    │  threading.Thread  │                    │           │        │         │
    │───────────────────►│                    │           │        │         │
    │                    │  nvidia-smi query  │           │        │         │
    │                    │───────────────────►│           │        │         │
    │                    │  ◄── GPU name,VRAM │           │        │         │
    │                    │                    │           │        │         │
    │                    │  cpu_count, freq   │           │        │         │
    │                    │──────────────────────────────►│        │         │
    │                    │  ◄── cores,threads │           │        │         │
    │                    │                    │           │        │         │
    │                    │  Win32_Processor   │           │        │         │
    │                    │────────────────────────────────────────►│         │
    │                    │  ◄── CPU name      │           │        │         │
    │                    │                    │           │        │         │
    │                    │  get_cpu_score(name)│          │        │         │
    │                    │─────────────────────────────────────────────────►│
    │                    │  ◄── score, matched│           │        │         │
    │                    │                    │           │        │         │
    │  window.after(0)   │                    │           │        │         │
    │  ◄── SystemProfile │                    │           │        │         │
    │  _on_detection_complete                 │           │        │         │
    │  refresh_dashboard  │                   │           │        │         │
```

---

## 4. Data Storage Design

### 4.1 Configuration (`config/config.json`)
```json
{
  "version": "1.0.0",
  "language": "en",
  "theme": "dark",
  "accent": "cyan",
  "auto_backup": true,
  "active_profile": "SAFE",
  "custom_presets": {
    "MyGaming": ["tel_diagtrack", "inp_mouse_accel", "gpu_hags"]
  },
  "welcome_shown": true,
  "window_size": {"width": 1000, "height": 700}
}
```

### 4.2 Flight Record (`data/flight_recorder/change_logs/20260304_221530.json`)
```json
{
  "snapshot_id": "20260304_221530",
  "timestamp": "2026-03-04T22:15:30",
  "operation_type": "profile_applied",
  "profile": "SAFE",
  "tweaks": [
    {
      "name": "Disable DiagTrack Service",
      "category": "service",
      "key_path": "HKLM\\SYSTEM\\CurrentControlSet\\Services\\DiagTrack\\Start",
      "old_value": "2",
      "new_value": "4",
      "value_type": "REG_DWORD",
      "risk_level": "LOW",
      "timestamp": "2026-03-04T22:15:31",
      "profile": "SAFE",
      "can_rollback": true,
      "rollback_command": "reg add \"HKLM\\SYSTEM\\...\\DiagTrack\" /v Start /t REG_DWORD /d 2 /f"
    }
  ],
  "pre_snapshot_path": "registry_snapshots/20260304_221530_before_HKLM.reg",
  "post_snapshot_path": "registry_snapshots/20260304_221530_after_HKLM.reg",
  "success": true
}
```

### 4.3 Backup Index (`data/backups/backup_index.json`)
```json
[
  {
    "id": "20260304_221500",
    "name": "Before SAFE Profile",
    "created_at": "2026-03-04T22:15:00",
    "profile": "SAFE",
    "has_restore_point": true,
    "has_registry_backup": true,
    "description": "Auto backup before applying SAFE profile",
    "size_bytes": 524288
  }
]
```

---

## 5. Error Handling Strategy

| Layer | Error Type | Handling | User Feedback |
|-------|-----------|---------|---------------|
| **GUI** | Widget creation failure | Try/except, fallback text | Toast warning |
| **Core** | Script not found | verify_scripts() before apply | Error dialog |
| **Core** | Registry write failure | Log error, continue next tweak | Toast + per-tweak status |
| **Core** | WMI connection failure | Graceful fallback (psutil, nvidia-smi) | "Detection partial" |
| **Batch** | Admin rights missing | IsUserAnAdmin() check | UAC prompt |
| **Batch** | BCDEdit failure | Log, don't crash | Warning in output |
| **Safety** | Backup creation failure | Proceed with warning (not blocking) | Toast warning |
| **Safety** | Restore point failure | Try WMIC fallback | Log warning |

---

## 6. Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| GUI Framework | CustomTkinter | ≥5.2.0 | Modern tkinter wrapper |
| Language | Python | 3.11+ | Type hints, dataclass, match |
| System Detection | psutil | ≥5.9.0 | CPU/RAM/Storage/Battery |
| System Detection | py-cpuinfo | ≥9.0.0 | CPU brand name |
| System Detection | WMI | ≥1.5.1 | Windows Management Instrumentation |
| Windows API | pywin32 | ≥306 | Registry read/write |
| Image | Pillow | ≥10.0.0 | Image processing |
| Backend | Windows .bat | N/A | System-level optimization |
| Testing | pytest | latest | Unit/Integration/E2E |
| Testing | pytest-cov | latest | Code coverage |
| Icons | Material Symbols | Outlined | Google font icons |
| Data | JSON | N/A | Config, backups, flight records |

---

## 7. บันทึกการแก้ไข

| เวอร์ชัน | วันที่ | คำอธิบาย |
|---------|-------|---------|
| 1.0 | 2025-01-15 | Batch optimizer architecture |
| 2.0 | 2025-06-01 | GUI architecture (ClutchG) |
| 3.0 | 2026-03-04 | ISO29110 SDD, class diagrams, sequence diagrams, design patterns, data storage, error handling |
| 3.1 | 2026-03-12 | อัปเดต: GPUtil ถูกลบออก, FlightRecorder rewritten (616 lines), storage detection 3-strategy, security hardening notes |

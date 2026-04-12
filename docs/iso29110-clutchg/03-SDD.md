# 03 — เอกสารการออกแบบซอฟต์แวร์ (Software Design Document)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O3 (Software Design)
> **ETVX:** Entry=SRS v3.1 approved → Task=Design architecture, components, data model → Verify=SDD review → Exit=Approved SDD
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.4 | **วันที่:** 2026-04-12 | **อ้างอิง SRS:** v3.3
> **อ้างอิง:** ISO/IEC 42010:2011, Gang of Four Design Patterns, SE 701 (Architecture & OO Design)

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
│  │ Dashboard │ Optimize   │  Backup  │   Help    │  Settings   │ │
│  │   View    │ Center View│  Center  │   View    │    View     │ │
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
│  │  │              │  │(1013 lines)│  │  + RecommendationSvc │  │ │
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
| **Strategy** (Dual-path) | RecommendationService primary/fallback | เลือก recommendation path ตาม data sufficiency | GoF, 1994 |
| **Template Method** | start_recording → record → finish_recording | Structured recording workflow | GoF, 1994 |
| **Data Transfer Object** | Tweak, Profile, SystemProfile, TweakChange, BackupInfo | Type-safe data passing | Fowler, PoEAA |
| **Repository** | TweakRegistry (get_all, get_by_id, get_by_category, filter) | Centralized data access | Evans, DDD |
| **Facade** | ProfileManager, ClutchGApp | Simplify complex subsystem access | GoF, 1994 |
| **Command** | rollback_command field in TweakChange | Encapsulate undo operations | GoF, 1994 |

### 1.4 Architecture Pattern Comparison

การเลือก Layered Architecture พิจารณาจากการเปรียบเทียบ 7 รูปแบบสถาปัตยกรรม (อ้างอิง SE 701 — Architecture Patterns):

| Pattern | เหมาะกับ ClutchG? | เหตุผล |
|---------|-------------------|--------|
| **Layered (N-tier)** | ใช่ (เลือกใช้) | แยก Presentation/Business/Infrastructure ชัดเจน ตรงกับ desktop app ที่มี GUI + system operations |
| **Monolithic** | บางส่วน | ทั้ง app อยู่ใน process เดียว แต่มี layer separation ภายใน |
| **Microservices** | ไม่เหมาะ | Desktop app, solo developer, ไม่ต้อง scale independently |
| **MVC** | บางส่วน | Views แยกจาก Core แต่ใช้ App Controller แทน Controller แยก — เป็น variant ของ MVC |
| **Client-Server** | ไม่เหมาะ | ไม่มี server component, ทำงาน offline ทั้งหมด |
| **Event-Driven** | บางส่วน | GUI ใช้ callback/observer pattern สำหรับ real-time updates ขณะ apply tweaks |
| **SOA** | ไม่เหมาะ | ไม่มี service bus, ไม่ต้อง interoperate กับระบบอื่น |

> **สรุป:** Layered Architecture ตอบโจทย์ desktop optimizer ที่ต้องแยก UI ออกจาก system-level operations ผ่าน subprocess — ให้ทั้ง testability (Core test ได้โดยไม่ต้อง GUI) และ maintainability (แก้ไข batch scripts ได้โดยไม่กระทบ Python)

---

## 2. โครงสร้างคอมโพเนนต์โดยละเอียด (Detailed Component Design)

### 2.1 Core Layer

#### 2.1.1 TweakRegistry (`core/tweak_registry.py` — 1013 lines, 62.6KB)
**หน้าที่:** Central knowledge base ของ tweaks ทั้งหมด — single source of truth

```
TweakRegistry (Singleton)
├── _tweaks: Dict[str, Tweak]          # 56 tweaks indexed by ID
├── get_all_tweaks() → List[Tweak]
├── get_tweak(id) → Optional[Tweak]
├── get_tweaks_by_category(cat) → List[Tweak]
├── get_tweaks_for_preset(preset) → List[Tweak]
├── get_compatible_tweaks(profile) → List[Tweak]     # Filter by OS + hardware
├── suggest_preset(profile) → Dict                    # Auto-recommend (delegates to RecommendationService)
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
└── recommend_profile(system) → str     # Laptop→SAFE, Desktop→score-based (delegates to RecommendationService)

Score Calculation:
  total_score = cpu.score(0-30) + gpu.score(0-30) + ram.score(0-20) + storage.score(0-10)
  tier = enthusiast(≥70) | high(50-69) | mid(30-49) | entry(<30)
```

#### 2.1.6 RecommendationService (`core/recommendation_service.py` — 188 lines, ~6KB)
**หน้าที่:** Unified dual-path profile recommendation — single authority แทน 2 ระบบเดิม (Phase 11 Refactor)

```
RecommendationService
├── recommend_preset(profile: SystemProfile) → Recommendation
│   ├── _has_sufficient_data(profile) → bool       # Evidence gate (4 conditions)
│   ├── _primary_recommendation(profile) → Recommendation   # Score-based
│   └── _fallback_recommendation(profile) → Recommendation  # Conservative heuristic
│
├── Recommendation (dataclass):
│   ├── preset: str            # "SAFE" | "COMPETITIVE" | "EXTREME"
│   ├── reason: str            # Human-readable explanation
│   ├── source: str            # "primary" | "fallback"
│   ├── total_score: Optional[int]
│   └── confidence: float      # 0.3 (fallback) – 0.9 (score-based)
│
└── Legacy delegation:
    ├── TweakRegistry.suggest_preset() → calls recommend_preset()
    └── SystemDetector.recommend_profile() → calls recommend_preset()
```

**Algorithm: recommend_preset()**
```
Input: SystemProfile (from SystemDetector.detect_all())

Step 1 — Evidence Gate (_has_sufficient_data):
  IF total_score is None or 0 → insufficient
  IF form_factor == "unknown" → insufficient
  IF ram_gb <= 0 → insufficient
  IF NOT cpu.benchmark_matched AND NOT gpu.benchmark_matched → insufficient

Step 2a — Primary Path (sufficient data, confidence 0.7–0.9):
  IF score ≥ 80 AND desktop AND ram ≥ 16GB → EXTREME (confidence 0.9)
  IF score ≥ 50 AND ram ≥ 8GB → COMPETITIVE (confidence 0.8)
  ELSE → SAFE (confidence 0.7)

Step 2b — Fallback Path (insufficient data, confidence 0.3–0.5):
  IF laptop → SAFE always (confidence 0.5)
  IF desktop AND tier in {mid, high, enthusiast} → COMPETITIVE (confidence 0.4)
  ELSE → SAFE (confidence 0.3)
  NOTE: Fallback NEVER returns EXTREME

Output: Recommendation (preset, reason, source, total_score, confidence)
```

**Design Rationale:**
- **Single Authority:** เดิมมี 2 ระบบ (SystemDetector.recommend_profile + TweakRegistry.suggest_preset) ที่อาจขัดแย้งกัน — รวมเป็นหนึ่งเดียว
- **Evidence Gate:** ป้องกัน EXTREME recommendation เมื่อข้อมูล hardware ไม่สมบูรณ์
- **`benchmark_matched` field:** เพิ่มใน CPUInfo/GPUInfo dataclass เพื่อระบุว่า CPU/GPU ตรงกับ PassMark database หรือไม่
- **Fallback ไม่แนะนำ EXTREME:** ถ้าข้อมูลไม่พอ จะแนะนำ conservative เพื่อความปลอดภัย

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
│   ├── "scripts" → ScriptsView (Optimize Center)
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
| Scripts | 63.5KB | ~1800 | สูงสุด | 56 tweaks, 10 categories, checkboxes, apply |
| Backup/Restore | 35.7KB | ~1000 | สูง | Timeline, per-tweak undo, snapshot details |
| Dashboard | 25.8KB | ~730 | ปานกลาง | System cards, score display, detection |
| Help | 23.3KB | ~660 | ปานกลาง | Content rendering, bilingual, search |
| Backup (Legacy) | 18.6KB | ~530 | ปานกลาง | Simple backup list |
| Welcome | 12.7KB | ~360 | ต่ำ | First-run overlay |
| Settings | 12KB | ~340 | ต่ำ | Theme/accent/language selectors |
| Profiles | 10.7KB | ~300 | ต่ำ | 3 profile cards |

### 2.3 Coupling & Cohesion Analysis (อ้างอิง SE 701)

> **หลักการ:** Low Coupling + High Cohesion = Good Design (Stevens et al., 1974)

#### 2.3.1 Cohesion — Core Layer

| Module | ไฟล์ | LOC | หน้าที่ | Cohesion Level | เหตุผล |
|--------|------|-----|---------|---------------|--------|
| TweakRegistry | `core/tweak_registry.py` | 1013 | Central knowledge base ของ 56 tweaks | **Functional** | ทุก method เกี่ยวกับ tweak data access |
| ProfileManager | `core/profile_manager.py` | 528 | จัดการ preset profiles | **Functional** | ทุก method เกี่ยวกับ profile mapping |
| FlightRecorder | `core/flight_recorder.py` | 589 | บันทึก before/after ของ changes | **Sequential** | start → record → finish flow |
| BackupManager | `core/backup_manager.py` | 373 | สร้าง/จัดการ backups | **Functional** | ทุก method เกี่ยวกับ backup operations |
| BatchParser | `core/batch_parser.py` | ~450 | Parse .bat metadata + call structure | **Functional** | ทุก method เกี่ยวกับ parsing |
| BatchExecutor | `core/batch_executor.py` | ~200 | Execute .bat scripts | **Functional** | ทุก method เกี่ยวกับ execution |
| ConfigManager | `core/config.py` | ~120 | อ่าน/เขียน JSON config | **Functional** | ทุก method เกี่ยวกับ configuration |
| SystemDetector | `core/system_info.py` | ~381 | ตรวจจับ hardware/OS info | **Informational** | รวบรวม system data หลายประเภท |
| HelpManager | `core/help_manager.py` | ~100 | จัดการ help content | **Functional** | ทุก method เกี่ยวกับ help data |
| BenchmarkDB | `core/benchmark_database.py` | ~450 | Hardware scoring database | **Functional** | ทุก method เกี่ยวกับ benchmark data |
| ActionCatalog | `core/action_catalog.py` | ~300 | กำหนด optimization actions | **Functional** | ทุก method เกี่ยวกับ action definitions |
| RecommendationService | `core/recommendation_service.py` | ~188 | Unified dual-path profile recommendation | **Functional** | ทุก method เกี่ยวกับ recommendation logic |
| SystemSnapshot | `core/system_snapshot.py` | ~150 | สร้าง snapshot ของ system state | **Sequential** | capture → store → retrieve flow |

**สรุป:** Core modules 12/14 ตัวมี **Functional Cohesion** (ระดับสูงสุด), 2 ตัวมี Sequential/Informational (ยังอยู่ในระดับดี)

#### 2.3.2 Cohesion — GUI Layer

| View | ไฟล์ | หน้าที่ | Cohesion Level |
|------|------|---------|---------------|
| DashboardView | `gui/views/dashboard_minimal.py` | แสดง system overview + quick actions | **Functional** |
| ScriptsView | `gui/views/scripts_minimal.py` | แสดง/จัดการ tweak scripts | **Functional** |
| ProfilesView | `gui/views/profiles_minimal.py` | เลือก/แสดง profiles | **Functional** |
| BackupView | `gui/views/backup_minimal.py` | จัดการ backup operations | **Functional** |
| RestoreCenter | `gui/views/restore_center.py` | Timeline + per-tweak rollback | **Functional** |
| HelpView | `gui/views/help_minimal.py` | แสดง help content | **Functional** |
| SettingsView | `gui/views/settings_minimal.py` | จัดการ settings | **Functional** |
| WelcomeView | `gui/views/welcome_minimal.py` | First-time setup wizard | **Functional** |

#### 2.3.3 Coupling Analysis

| Module Pair | Coupling Type | ระดับ | รายละเอียด |
|-------------|-------------|-------|-----------|
| Views → Core | **Data Coupling** | LOW | Views เรียก Core methods ด้วย parameters เท่านั้น |
| Core → Views | **ไม่มี** | NONE | Core ไม่ import หรือเรียก Views เลย (กฎเหล็ก) |
| Views → App Controller | **Stamp Coupling** | LOW | Views ใช้ app reference สำหรับ navigation |
| Core ↔ Core | **Data Coupling** | LOW-MED | ProfileManager ใช้ TweakRegistry, FlightRecorder ใช้ BackupManager |
| Python → Batch Scripts | **External Coupling** | LOW | สื่อสารผ่าน subprocess + stdout parsing เท่านั้น |
| GUI Components → Views | **Data Coupling** | LOW | Components รับ data ผ่าน constructor parameters |

**กฎ Coupling ของ ClutchG:**
```
Views ──────────► Core Modules       (อนุญาต)
Core Modules ──✗─► Views             (ห้ามเด็ดขาด)
GUI Components ◄── Views             (อนุญาต — Views สร้าง Components)
```

> **อ้างอิง:** `AGENTS.md` — "Views call Core, never the reverse"

### 2.4 SOLID Principles Assessment

| หลักการ | ย่อ | ClutchG ปฏิบัติ | หลักฐาน |
|---------|-----|----------------|---------|
| **Single Responsibility** | SRP | ดี | แต่ละ Core module มีหน้าที่เดียว เช่น TweakRegistry จัดการ tweak data เท่านั้น, BackupManager จัดการ backup เท่านั้น |
| **Open/Closed** | OCP | ปานกลาง | เพิ่ม tweak ใหม่ได้โดยไม่แก้ logic (เพิ่มใน `_build_tweaks()`) แต่เพิ่ม category ใหม่ต้องแก้ constant `TWEAK_CATEGORIES` |
| **Liskov Substitution** | LSP | ไม่เกี่ยวข้อง | ไม่มี class inheritance ที่ซับซ้อน — ใช้ dataclass + composition แทน inheritance |
| **Interface Segregation** | ISP | ดี | Views เรียกเฉพาะ method ที่จำเป็นจาก Core — ไม่มี "fat interface" ที่บังคับ implement method ไม่จำเป็น |
| **Dependency Inversion** | DIP | ปานกลาง | Core modules ไม่ขึ้นกับ GUI (ดี) แต่ ProfileManager ผูกกับ TweakRegistry concrete class โดยตรง — ไม่ผ่าน abstract interface |

> **หมายเหตุ:** ClutchG เป็น desktop app ขนาดกลาง (solo developer) จึงเน้น SRP และ ISP มากกว่า LSP/DIP ซึ่งเหมาะกับ large-scale systems ที่มี team หลายคน

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
| Icons | Tabler Icons | v3.41.1 | Bundled icon font (tabler-icons.ttf) |
| Data | JSON | N/A | Config, backups, flight records |

---

## 7. Deployment & Infrastructure View

### 7.1 Deployment Overview

ClutchG เป็น standalone desktop application ที่ทำงานบนเครื่อง Windows 10/11 โดยตรง ไม่มี server-side component หรือ network dependency

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT ENVIRONMENT                          │
│  ┌──────────────────┐    ┌──────────────────┐                       │
│  │  Python 3.11+    │    │  Git Repository   │                      │
│  │  clutchg/src/    │    │  bat/ (root)      │                      │
│  │  - main.py       │    │  - src/ (batch)   │                      │
│  │  - core/         │    │  - clutchg/       │                      │
│  │  - gui/          │    │  - docs/          │                      │
│  └────────┬─────────┘    └──────────────────┘                       │
│           │                                                         │
│           ▼                                                         │
│  ┌──────────────────┐                                               │
│  │  PyInstaller     │  python build.py                              │
│  │  --onefile       │  → clutchg/dist/ClutchG.exe                   │
│  │  --windowed      │  (includes: Python runtime, CustomTkinter,    │
│  │  --uac-admin     │   bundled fonts, icons, batch scripts)        │
│  └────────┬─────────┘                                               │
└───────────┼─────────────────────────────────────────────────────────┘
            │
            ▼ Distribution (USB / file share / direct copy)
┌─────────────────────────────────────────────────────────────────────┐
│                    TARGET ENVIRONMENT                                │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Windows 10/11 (x64)                                         │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  ClutchG.exe (runs as Administrator)                     │ │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │ │   │
│  │  │  │ GUI Layer│  │Core Layer│  │Batch     │              │ │   │
│  │  │  │(CTk/Tk)  │→ │(Python)  │→ │Engine    │              │ │   │
│  │  │  └──────────┘  └──────────┘  └────┬─────┘              │ │   │
│  │  └───────────────────────────────────┼─────────────────────┘ │   │
│  │                                      ▼                       │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Windows OS APIs                                         │ │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │ │   │
│  │  │  │ Registry │ │ Services │ │ BCDEdit  │ │ PowerShell │ │ │   │
│  │  │  │ (winreg) │ │ (sc.exe) │ │          │ │            │ │ │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  │                                                               │   │
│  │  ┌─────────────────────────────────────────────────────────┐ │   │
│  │  │  Local File System (%LOCALAPPDATA%\ClutchG\)             │ │   │
│  │  │  config.json | flight_record.json | backup/ | logs/      │ │   │
│  │  └─────────────────────────────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Prerequisites:                                                     │
│  - Windows 10 v1903+ or Windows 11                                 │
│  - .NET Framework 4.7.2+ (for PowerShell integration)              │
│  - Administrator privileges (for system-level tweaks)              │
│  - 50 MB disk space (exe + data files)                             │
│  - No network required (fully offline capable)                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 7.2 Build Process

| ขั้นตอน | เครื่องมือ | รายละเอียด |
|---------|-----------|-----------|
| 1. Development | Python 3.11+, VS Code | เขียนและทดสอบ code ใน `clutchg/src/` |
| 2. Testing | pytest | รัน 496+ tests (unit/integration/E2E) |
| 3. Build | PyInstaller (`build.py`) | Compile เป็น single `.exe` — `--onefile --windowed --uac-admin` |
| 4. Bundle | PyInstaller spec | รวม: Python runtime, CustomTkinter, Pillow, psutil, pywin32, bundled fonts (Figtree, Tabler Icons), data files (help_content.json, risk_explanations.json), batch scripts |
| 5. Artifact | `clutchg/dist/ClutchG.exe` | ~45 MB standalone executable |
| 6. Distribution | Manual copy | USB drive / file share — ไม่มี installer, ไม่มี auto-update |

### 7.3 Runtime Environment Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 v1903 (19H1) | Windows 11 23H2 |
| **Architecture** | x86-64 only | x86-64 |
| **RAM** | 4 GB | 8 GB+ |
| **Disk Space** | 50 MB (app) + 100 MB (backups) | 500 MB+ (backup history) |
| **.NET Framework** | 4.7.2 | 4.8+ |
| **Display** | 1024×768 | 1920×1080 |
| **Privilege** | Administrator (for system tweaks) | Administrator |
| **Network** | Not required | Not required |

### 7.4 Deployment Constraints

| ข้อจำกัด | รายละเอียด |
|----------|-----------|
| **No Installer** | ใช้ portable `.exe` — ไม่ต้อง install, ไม่แก้ไข Program Files |
| **No Auto-Update** | ไม่มีระบบ update อัตโนมัติ — ผู้ใช้ต้อง download version ใหม่เอง |
| **Single User** | ไม่รองรับ multi-user concurrent access |
| **No Cloud** | ไม่มี telemetry, ไม่ส่งข้อมูลออก internet, ทำงาน offline 100% |
| **UAC Prompt** | ผู้ใช้ต้องกด "Yes" ที่ UAC prompt ทุกครั้งที่เปิดโปรแกรม |

---

## 8. Security Architecture

### 8.1 Security Design Philosophy

ClutchG ใช้หลัก **Defense in Depth** — มีกลไกป้องกันหลายชั้น ป้องกันการกระทำที่อาจทำให้ระบบปฏิบัติการเสียหายหรือไม่ปลอดภัย

### 8.2 Never-Disable Policy (6 Protected Features)

| # | Protected Feature | Service/Component | เหตุผลที่ห้ามปิด |
|---|-------------------|-------------------|------------------|
| 1 | **Windows Defender** | WinDefend, WdNisSvc | ป้องกัน malware — ปิดแล้วเครื่องเสี่ยงทันที |
| 2 | **User Account Control (UAC)** | Registry: EnableLUA | ป้องกัน unauthorized privilege escalation |
| 3 | **Data Execution Prevention (DEP)** | BCDEdit: nx | ป้องกัน buffer overflow attacks |
| 4 | **Address Space Layout Randomization (ASLR)** | Registry: MoveImages | ป้องกัน memory-based exploits |
| 5 | **Control Flow Guard (CFG)** | System-level | ป้องกัน ROP/JOP attacks |
| 6 | **Windows Update** | wuauserv | ป้องกัน unpatched vulnerabilities |

**Implementation:** Hardcoded blocklist ใน `core/tweak_registry.py` — ทุก tweak ถูกตรวจสอบก่อน execute ว่าไม่แตะ protected features เหล่านี้

### 8.3 Dangerous Pattern Detection (18 Patterns)

ระบบตรวจจับคำสั่งอันตรายก่อนส่งไปยัง `subprocess`:

| # | Pattern Category | ตัวอย่าง | Action |
|---|-----------------|---------|--------|
| 1-3 | **Destructive File Ops** | `format`, `del /f /s /q`, `rd /s /q` | BLOCK + log critical |
| 4-6 | **System Corruption** | `sfc /scannow` disable, `dism` delete, `bcdedit /delete` | BLOCK + alert |
| 7-9 | **Security Disable** | `netsh advfirewall set allprofiles state off`, Defender disable | BLOCK (Never-Disable) |
| 10-12 | **Boot Destruction** | `bcdedit /deletevalue {bootmgr}`, MBR overwrite | BLOCK + log critical |
| 13-15 | **Permission Abuse** | `takeown /f C:\Windows`, `icacls * /grant Everyone:F` | BLOCK |
| 16-18 | **Network Exposure** | Firewall disable, Remote Desktop force-enable, port forwarding | BLOCK |

**Implementation:** Regex-based scanner ใน batch scripts (`safety/validator.bat`) — ทุก command ผ่าน validation ก่อน execute

### 8.4 Input Sanitization

| มาตรการ | รายละเอียด |
|---------|-----------|
| **No User-Supplied Shell Input** | GUI ไม่มี free-text input ที่ส่งเข้า shell commands โดยตรง |
| **Parameterized Paths** | ใช้ `pathlib.Path` สร้าง file paths — ไม่ใช้ string concatenation |
| **Tweak ID Validation** | ทุก tweak ID ต้องมีใน TweakRegistry — ไม่รับ arbitrary IDs |
| **Profile Validation** | Profile names ถูกจำกัดเป็น SAFE/COMPETITIVE/EXTREME — ไม่รับ custom names ใน production |

### 8.5 Privilege Management

```
┌──────────────────────────────────────────────────────┐
│  Application Launch                                   │
│  ├─ Check: IsUserAnAdmin()?                           │
│  │  ├─ YES → Proceed normally                         │
│  │  └─ NO → Show warning dialog                       │
│  │         ├─ System tweaks: DISABLED (greyed out)    │
│  │         └─ View/Info features: ENABLED             │
│  │                                                    │
│  For each system operation:                           │
│  ├─ Verify admin rights again                         │
│  ├─ Check Never-Disable blocklist                     │
│  ├─ Run Dangerous Pattern scanner                     │
│  ├─ Create backup (registry/BCD/services)             │
│  ├─ Verify backup created successfully                │
│  ├─ Execute operation via subprocess                  │
│  ├─ Log to flight record                              │
│  └─ Verify operation result                           │
└──────────────────────────────────────────────────────┘
```

### 8.6 Audit Trail (Flight Recorder)

| คุณสมบัติ | รายละเอียด |
|----------|-----------|
| **Coverage** | บันทึกทุก operation: apply, revert, backup, restore, config change |
| **Format** | JSON structured log — machine-readable, human-inspectable |
| **Immutability** | Append-only — ไม่มี function สำหรับลบ/แก้ไข entries เดิม |
| **Fields per Entry** | timestamp, session_id, action, tweak_id, category, risk_level, backup_path, status, error_message (ถ้ามี) |
| **Retention** | ไม่จำกัด — เก็บทุก session ตั้งแต่ first run |
| **Location** | `%LOCALAPPDATA%\ClutchG\flight_record.json` |

### 8.7 Security Testing Summary

| Test Category | จำนวน Tests | Coverage |
|---------------|------------|----------|
| Safety validation (Never-Disable) | 11 tests (UT-SA-01~11) | ทุก protected feature |
| Dangerous pattern detection | 8 tests (UT-SA-03~08) | 18 patterns ทั้งหมด |
| Input validation | 5 tests (UT-SA-09~11) | Edge cases, malformed input |
| Backup integrity | 3 tests (IT-01~03) | Create, verify, restore cycle |
| **รวม** | **27 tests** | **ครอบคลุม security requirements ทั้งหมด** |

> **อ้างอิง:** ดูผลทดสอบโดยละเอียดใน 05-Test-Record.md §7.3 (Safety Audit Defects DEF-SA-01~11)

---

## 9. สรุปการประเมินสถาปัตยกรรม (Architecture Evaluation)

> **อ้างอิง:** `docs/se-academic/02-architecture-evaluation.md` — วิเคราะห์ตามเกณฑ์ SE 701

### 7.1 จุดแข็ง

| จุดแข็ง | หลักฐาน |
|---------|---------|
| **Low Coupling** ระหว่าง layers | Core ไม่ import Views เลย — สื่อสารผ่าน callback parameters |
| **High Cohesion** ใน Core modules | 12/14 modules มี Functional Cohesion (ระดับสูงสุด) |
| **Separation of Concerns** | 3 layers ชัดเจน: Presentation / Business / Infrastructure |
| **Testability** | Core test ได้โดยไม่ต้อง GUI (496+ tests passed) |
| **Design Patterns ที่เหมาะสม** | 9 patterns ตอบโจทย์ design problems เฉพาะ — ไม่ over-engineer |

### 7.2 จุดที่ควรปรับปรุง

| จุดอ่อน | รายละเอียด | ข้อเสนอ |
|---------|-----------|---------|
| TweakRegistry ขนาดใหญ่ | 1013 LOC — รวม data + logic ไว้ด้วยกัน | แยก tweak definitions เป็น JSON/YAML แล้ว load เข้า registry |
| SystemDetector cohesion | Informational cohesion — รวม hardware info หลายประเภท | อาจแยกเป็น CPU/GPU/RAM detectors (แต่ complexity เพิ่ม) |
| App Controller รับภาระมาก | `app_minimal.py` ทำทั้ง routing, state, theme switching | อาจแยก state management ออกเป็น module ต่างหาก |

### 7.3 คะแนนประเมิน

| เกณฑ์ (SE 701) | คะแนน (1-5) | เหตุผล |
|----------------|-------------|--------|
| Coupling | 4/5 | Low coupling ดี แต่ Core modules บางตัวผูกกัน (ProfileManager → TweakRegistry) |
| Cohesion | 5/5 | ทุก module มี Functional cohesion หรือสูงกว่า (12/14 Functional) |
| Separation of Concerns | 5/5 | 3 layers แยกชัดเจน กฎ "Core ห้ามเรียก Views" บังคับใช้จริง |
| Testability | 4/5 | Core testable ดี (496+ tests) แต่ GUI testing ต้อง mock มาก + E2E ต้องมี display |
| Pattern Usage | 5/5 | ใช้ 9 patterns ที่เหมาะสม (เพิ่ม dual-path Strategy สำหรับ recommendation) ไม่มี pattern ที่ใส่มาโดยไม่จำเป็น |
| **รวม** | **23/25** | **สถาปัตยกรรมคุณภาพดี — เหมาะสมกับ desktop optimizer ที่ solo developer พัฒนา** |

---

## 10. บันทึกการแก้ไข

| เวอร์ชัน | วันที่ | คำอธิบาย |
|---------|-------|---------|
| 1.0 | 2025-01-15 | Batch optimizer architecture |
| 2.0 | 2025-06-01 | GUI architecture (ClutchG) |
| 3.0 | 2026-03-04 | ISO29110 SDD, class diagrams, sequence diagrams, design patterns, data storage, error handling |
| 3.1 | 2026-03-12 | อัปเดต: GPUtil ถูกลบออก, FlightRecorder rewritten (616 lines), storage detection 3-strategy, security hardening notes |
| 3.2 | 2026-04-06 | เสริม SE 701: Architecture Pattern Comparison (§1.4), Coupling & Cohesion Analysis (§2.3), SOLID Assessment (§2.4), Architecture Evaluation Summary (§7) |
| 3.3 | 2026-04-10 | Phase 11 Recommendation Refactor: เพิ่ม §2.1.6 RecommendationService, อัปเดต layer diagram, rename ProfileRecommender→RecommendationService, เพิ่ม dual-path Strategy pattern, อัปเดต tweaks 48→56, tests 445→496+, views 6→5, icons Material Symbols→Tabler Icons |
| 3.4 | 2026-04-12 | เพิ่ม §7 Deployment & Infrastructure View (build process, runtime requirements, deployment constraints), §8 Security Architecture (Never-Disable Policy, 18 dangerous patterns, input sanitization, privilege management, flight recorder audit trail) |

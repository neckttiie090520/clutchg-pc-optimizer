# 02 — เอกสารความต้องการซอฟต์แวร์ (Software Requirements Specification)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O2 (Software Requirements Specification)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.0 | **วันที่:** 2026-03-04 | **ผู้จัดทำ:** nextzus
> **อ้างอิง:** IEEE 830-1998, ISO/IEC 25010:2011

---

## 1. บทนำ (Introduction)

### 1.1 วัตถุประสงค์ของเอกสาร
เอกสาร SRS ฉบับนี้ระบุความต้องการซอฟต์แวร์อย่างครบถ้วนสำหรับ **ClutchG PC Optimizer** ซึ่งเป็นเครื่องมือ optimization สำหรับ Windows 10/11 ที่ออกแบบตามหลัก **Evidence-Based Optimization** โดยเน้น 3 หลักการสำคัญ:
1. **Safety-First** — ทุกการเปลี่ยนแปลงต้อง reversible และมี backup
2. **Evidence-Based** — ทุก tweak ต้องมี evidence จาก 28 repos ที่วิเคราะห์
3. **Transparency** — ผู้ใช้ต้องเข้าใจก่อน apply (risk label, detailed explanation)

### 1.2 ขอบเขต (Scope)
ClutchG เป็น desktop application ที่ให้ผู้ใช้ optimize Windows 10/11 ผ่าน GUI ที่ปลอดภัย โดยมี:
- **48 optimization tweaks** จัดกลุ่มใน 10 categories
- **3 preset profiles** (SAFE/COMPETITIVE/EXTREME) จัด risk level ชัดเจน
- **Backup & Rollback system** ที่ track per-tweak changes
- **GUI** (Python/CustomTkinter) แยก 3 layers: GUI / Core / Batch

### 1.3 คำจำกัดความ คำย่อ และตัวย่อ

| ศัพท์ | คำนิยาม |
|------|---------|
| **Tweak** | การเปลี่ยนแปลง Windows setting เดี่ยวๆ ประกอบด้วย registry/service/bcdedit/network/power changes |
| **Profile** | กลุ่มของ tweaks ที่จัดเตรียมไว้ล่วงหน้า มี 3 ระดับ: SAFE, COMPETITIVE, EXTREME |
| **Risk Level** | ระดับความเสี่ยงของ tweak: LOW (🟢), MEDIUM (🟡), HIGH (🔴) |
| **Flight Recorder** | ระบบบันทึก before/after values ของทุกการเปลี่ยนแปลง เพื่อ rollback |
| **SystemSnapshot** | ภาพรวมของ system state ณ จุดเวลาหนึ่ง เก็บ changes ทั้งหมดในหนึ่ง session |
| **TweakChange** | data object เก็บข้อมูลการเปลี่ยนแปลงเดี่ยว: name, key_path, old_value, new_value, rollback_command |
| **Rollback** | การย้อนกลับการเปลี่ยนแปลง ทำได้ทั้ง per-tweak (ทีละรายการ) หรือ per-snapshot (ทั้ง session) |
| **BenchmarkDB** | ฐานข้อมูล hardware scores สำหรับคำนวณ system profile recommendation |
| **DPC Latency** | Deferred Procedure Call latency — ค่า latency ของ kernel interrupt handling |
| **HAGS** | Hardware-Accelerated GPU Scheduling — GPU จัดการ VRAM scheduling เอง |
| **VBS** | Virtualization-Based Security — security layer ที่ใช้ hypervisor |
| **MMCSS** | Multimedia Class Scheduler Service — Windows scheduler สำหรับ multimedia threads |

### 1.4 เอกสารอ้างอิง
1. ISO/IEC 29110-5-1-2:2016 — Software Engineering Lifecycle Profiles
2. IEEE 830-1998 — Recommended Practice for SRS
3. ISO/IEC 25010:2011 — Systems and Software Quality Models
4. `docs/01-research-overview.md` — 28 Repository Analysis
5. `docs/03-tweak-taxonomy.md` — Tweak Taxonomy & Classification
6. `docs/04-risk-classification.md` — Risk Classification Framework
7. `docs/09-final-architecture.md` — Architecture Design Document

---

## 2. คำอธิบายโดยรวม (Overall Description)

### 2.1 มุมมองผลิตภัณฑ์ (Product Perspective)
ClutchG เป็นส่วนหนึ่งของ **Batch Optimizer Research Project** ที่วิเคราะห์ 28 open-source Windows optimization tools จาก GitHub แล้วสังเคราะห์ tweaks ที่มี evidence จริง ออกมาเป็น tool ที่ปลอดภัยและโปร่งใส

```
Research (28 repos) → Taxonomy (48 tweaks) → Risk Classification → Architecture Design
                                                                         ↓
                                                            ClutchG Application
                                                     ┌──────────────────────────────┐
                                                     │  GUI (CustomTkinter)          │
                                                     │  Core (Python Business Logic) │
                                                     │  Batch (Windows .bat scripts) │
                                                     └──────────────────────────────┘
```

### 2.2 ฟังก์ชันหลัก (Product Functions)
1. **System Detection** — ตรวจจับ CPU/GPU/RAM/Storage อัตโนมัติ + คะแนน + tier
2. **Profile Management** — เลือก SAFE/COMPETITIVE/EXTREME หรือ custom preset
3. **Tweak Execution** — Apply tweaks ทีละตัวหรือทั้ง profile ด้วยสิทธิ์ Admin
4. **Safety & Rollback** — Backup registry ก่อนเปลี่ยน + Flight Recorder + Restore Center
5. **GUI** — 6 views: Dashboard, Profiles, Scripts, Backup Center, Help, Settings
6. **Preset I/O** — Export/Import custom presets เป็น JSON

### 2.3 ผู้ใช้งาน (User Characteristics)

| ประเภท | ความรู้เทคนิค | Profile แนะนำ | Tweaks ที่เข้าถึง | ลักษณะการใช้งาน |
|--------|-------------|--------------|-----------------|----------------|
| **Beginner** | ต่ำ — ใช้ Windows ทั่วไป | SAFE (🟢) | 17 tweaks (LOW risk) | เลือก profile แล้ว apply ทีเดียว |
| **Gamer** | ปานกลาง — เข้าใจ settings | COMPETITIVE (🟡) | 35 tweaks | ใช้ profile + ปรับบาง tweaks |
| **Power User** | สูง — เข้าใจ registry/services | EXTREME (🔴) | 48 tweaks ทั้งหมด | เลือก tweaks ทีละตัว |

### 2.4 ข้อจำกัด (Constraints)
1. **สิทธิ์ Administrator** — จำเป็นสำหรับ registry/service/bcdedit changes
2. **Windows 10/11 เท่านั้น** — ใช้ Windows-specific APIs (pywin32, WMI, PowerShell)
3. **Python 3.11+** — ใช้ modern type hints, match statements
4. **ผลลัพธ์แตกต่างตาม hardware** — FPS gains อ้างอิงค่า range (2-15%)
5. **บาง tweaks ต้อง restart** — 15/48 tweaks ต้อง restart หลัง apply
6. **ไม่รองรับ ARM-based Windows** — ทดสอบเฉพาะ x64

### 2.5 สมมติฐาน (Assumptions)
1. ผู้ใช้มี Windows 10 (1903+) หรือ Windows 11 ติดตั้งบนเครื่อง
2. ผู้ใช้สามารถ Run as Administrator ได้
3. Python 3.11+ ติดตั้งแล้ว (หรือใช้ bundled executable)
4. เครื่องมี internet สำหรับ download dependencies ครั้งแรก

---

## 3. ความต้องการเชิงหน้าที่ (Functional Requirements)

### 3.1 FR-SD: System Detection (ตรวจจับระบบ)

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-SD-01 | ตรวจจับ CPU: ชื่อ, vendor (Intel/AMD), cores, threads, base clock | Must | แสดง CPU info ถูกต้อง ±5% | `core/system_info.py` L172-222 |
| FR-SD-02 | ตรวจจับ GPU: ชื่อ, vendor (NVIDIA/AMD/Intel), VRAM, driver version | Must | แสดง GPU info, ใช้ nvidia-smi → WMI fallback | `core/system_info.py` L224-283 |
| FR-SD-03 | ตรวจจับ RAM: ขนาด (GB, rounded up), type, speed | Must | แสดง RAM ≥ physical RAM | `core/system_info.py` L285-303 |
| FR-SD-04 | ตรวจจับ Storage: ประเภท (SSD/HDD/NVMe), ขนาดรวม | Should | ระบุ SSD/HDD ได้ถูกต้อง | `core/system_info.py` L305-334 |
| FR-SD-05 | คำนวณ System Score (0-100) จาก CPU(30) + GPU(30) + RAM(20) + Storage(10) | Should | Score = sum of sub-scores | `core/system_info.py` L115-148 |
| FR-SD-06 | จำแนก Tier: entry (<30), mid (30-49), high (50-69), enthusiast (≥70) | Should | Tier ตรงตามช่วง score | `core/system_info.py` L349-358 |
| FR-SD-07 | แนะนำ Profile ตาม Tier + Form Factor (laptop→SAFE) | Should | Laptop = SAFE เสมอ | `core/system_info.py` L360-380 |
| FR-SD-08 | ตรวจจับ Form Factor: desktop/laptop (จาก battery) | Could | มี battery = laptop | `core/system_info.py` L336-347 |
| FR-SD-09 | การตรวจจับเป็น async (threading) ไม่ block UI | Must | UI ตอบสนองระหว่าง scan | `app_minimal.py` L117-145 |

### 3.2 FR-PM: Profile Management (จัดการโปรไฟล์)

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-PM-01 | มี 3 preset profiles: SAFE (🟢 LOW, 2-5%), COMPETITIVE (🟡 MED, 5-10%), EXTREME (🔴 HIGH, 10-15%) | Must | ทั้ง 3 profiles โหลดได้ | `core/profile_manager.py` L61-128 |
| FR-PM-02 | SAFE: 17 tweaks (LOW risk ทั้งหมด) | Must | นับ tweaks = 17 | `core/tweak_registry.py` (preset_safe=True) |
| FR-PM-03 | COMPETITIVE: 35 tweaks (LOW + MEDIUM) | Must | นับ tweaks = 35 | `core/tweak_registry.py` |
| FR-PM-04 | EXTREME: 48 tweaks ทั้งหมด (รวม HIGH) | Must | นับ tweaks = 48 | `core/tweak_registry.py` |
| FR-PM-05 | แสดง risk level, expected FPS gain, warnings ของแต่ละ profile | Must | ข้อมูลตรงกับ Profile dataclass | `core/profile_manager.py` L28-40 |
| FR-PM-06 | Apply profile: backup → execute tweaks → record changes | Must | สร้าง backup ก่อน apply | `core/profile_manager.py` L146-257 |
| FR-PM-07 | แสดง per-tweak progress (0-100%) ระหว่าง apply | Should | Progress callback ทำงาน | `core/profile_manager.py` L284-419 |
| FR-PM-08 | ผู้ใช้สร้าง custom preset ได้ (เลือก tweaks เอง) | Should | Save/load custom presets | `core/profile_manager.py` L421-451 |
| FR-PM-09 | Export custom preset เป็น JSON file | Could | JSON มี name + tweak_ids | `core/profile_manager.py` L453-490 |
| FR-PM-10 | Import custom preset จาก JSON file + validate tweak_ids | Could | Unknown tweaks แจ้งเตือน | `core/profile_manager.py` L492-527 |
| FR-PM-11 | Verify ว่า batch scripts ทุกตัวใน profile มีอยู่จริง | Must | verify_scripts() = True | `core/profile_manager.py` L263-278 |

### 3.3 FR-TW: Tweak Registry (ฐานข้อมูล Tweaks)

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-TW-01 | เก็บ tweaks ทั้ง 48 ตัว ใน TweakRegistry (Singleton) | Must | len(registry) = 48 | `core/tweak_registry.py` L884-1012 |
| FR-TW-02 | แต่ละ tweak มี 17 fields: id, name, category, description, what_it_does, why_it_helps, limitations, warnings, risk_level, expected_gain, requires_admin, requires_restart, reversible, compatible_os, compatible_hardware, registry_keys, bat_script/bat_function, preset_* | Must | Tweak dataclass ครบ 17 fields | `core/tweak_registry.py` L13-36 |
| FR-TW-03 | จัดกลุ่มเป็น 10 categories พร้อม icon + color | Must | 10 categories ตาม TWEAK_CATEGORIES | `core/tweak_registry.py` L39-51 |
| FR-TW-04 | Filter tweaks by category, preset, OS compatibility, hardware | Must | get_tweaks_by_category(), get_compatible_tweaks() | `core/tweak_registry.py` L899-933 |
| FR-TW-05 | คำนวณ risk distribution: LOW/MEDIUM/HIGH | Should | get_risk_distribution() ถูกต้อง | `core/tweak_registry.py` L968-973 |
| FR-TW-06 | แนะนำ preset ตาม system_profile | Should | suggest_preset() คืน preset + reason | `core/tweak_registry.py` L935-959 |
| FR-TW-07 | Build custom preset + validate tweak_ids | Should | build_custom_preset() คืน max_risk, requires_restart | `core/tweak_registry.py` L975-1001 |

#### รายละเอียด Tweak Categories (ข้อมูลจริง 48 tweaks)

| Category | จำนวน | Risk Distribution | ตัวอย่าง Tweaks |
|----------|-------|-------------------|----------------|
| **Telemetry & Privacy** | 8 | LOW: 8 | DiagTrack, Advertising ID, Cortana, Activity History, Xbox DVR, Copilot |
| **Input & Latency** | 6 | LOW: 6 | Mouse Acceleration, Keyboard, MMCSS, Menu Delay, Data Queue, Priority |
| **Power Management** | 7 | LOW: 3, MED: 3, HIGH: 1 | Ultimate Performance, Hibernate, Throttling, EPP, CPPC, Spectre (HIGH) |
| **GPU & Graphics** | 8 | LOW: 4, MED: 2, HIGH: 1 | HAGS, NVIDIA Telemetry, MSI Mode, DirectX, Fullscreen, VBS (HIGH) |
| **Network** | 6 | LOW: 3, MED: 3 | Nagle, TCP Global, DNS, NetBIOS, Window Size, Throttling |
| **Services** | 5 | LOW: 2, MED: 3 | Telemetry Svc, Xbox Svc, Search Indexer, SysMain, Print Spooler |
| **Memory** | 4 | MED: 4 | SvcHost Split, Paging Executive, Large Cache, Page Combining |
| **Boot (BCDEdit)** | 5 | LOW: 3, MED: 1, HIGH: 1 | Dynamic Tick, TSC Sync, x2APIC, ConfigAccess, Hypervisor (HIGH) |
| **Visual Effects** | 4 | LOW: 4 | Animations, Transparency, Full Drag, Visual FX=Best Perf |
| **Cleanup & Debloat** | 3 | LOW: 2, MED: 1 | Bloatware Remove, OneDrive Auto-Start, NTFS Optimize |
| **รวม** | **48** | LOW: 29, MED: 16, HIGH: 3 | — |

### 3.4 FR-SF: Safety & Rollback

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-SF-01 | **Auto Backup**: สร้าง registry backup ก่อนทุกการเปลี่ยนแปลง | Must | BackupManager.create_backup() เรียกก่อน apply | `core/backup_manager.py` L73-140 |
| FR-SF-02 | Backup 6 registry keys: Services, Power, Explorer, Policies, Desktop, User Explorer | Must | 6 .reg files ถูกสร้าง | `core/backup_manager.py` L209-248 |
| FR-SF-03 | สร้าง Windows System Restore Point (PowerShell → WMIC fallback) | Should | Checkpoint-Computer ทำงาน | `core/backup_manager.py` L142-207 |
| FR-SF-04 | จำกัด backup ไม่เกิน 10 ชุด (auto cleanup) | Should | cleanup ลบของเก่า | `core/backup_manager.py` L261-281 |
| FR-SF-05 | **Flight Recorder**: บันทึก TweakChange ทุกตัว (name, category, key_path, old_value, new_value, value_type, risk_level, rollback_command) | Must | TweakChange มีครบ 13 fields | `core/flight_recorder.py` L37-76 |
| FR-SF-06 | **SystemSnapshot**: รวม TweakChange ทั้งหมดในหนึ่ง session พร้อม pre/post registry snapshot | Must | SystemSnapshot.to_dict() serialize ได้ | `core/flight_recorder.py` L79-123 |
| FR-SF-07 | **Per-Tweak Rollback**: undo ทีละ tweak ด้วย rollback_command ที่ auto-generate | Must | reg add command สร้างถูกต้อง | `core/flight_recorder.py` L521-540 |
| FR-SF-08 | **Snapshot Rollback**: undo ทั้ง session (reverse order) | Must | tweaks reversed ถูกต้อง | `core/flight_recorder.py` L411-463 |
| FR-SF-09 | **Generate Rollback Script**: สร้าง .bat file สำหรับ manual recovery | Should | .bat file มี rollback commands ครบ | `core/flight_recorder.py` L411-463 |
| FR-SF-10 | Snapshot history: list ได้สูงสุด 50 snapshots (newest first) | Should | list_snapshots(limit=50) | `core/flight_recorder.py` L360-383 |
| FR-SF-11 | Compare snapshots: เปรียบเทียบ before/after | Could | compare_snapshots() คืน diff | `core/flight_recorder.py` L385-409 |
| FR-SF-12 | Cleanup old snapshots (>30 days) | Could | cleanup_old_snapshots(keep_days=30) | `core/flight_recorder.py` L542-570 |
| FR-SF-13 | **Never-Disable Policy**: ห้ามปิด Defender, Windows Update, UAC, DEP, ASLR, CFG | Must | ไม่มี tweak ที่ปิด features เหล่านี้ | Policy (ไม่มีในโค้ด = ปลอดภัย) |

### 3.5 FR-UI: User Interface

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-UI-01 | **Dashboard View**: แสดง CPU, GPU, RAM, Storage + system score + tier | Must | ข้อมูลแสดงครบหลัง detection | `gui/views/dashboard_minimal.py` (25.8KB) |
| FR-UI-02 | **Profiles View**: แสดง 3 profiles + risk badge + expected FPS gain | Must | 3 profile cards พร้อม badge | `gui/views/profiles_minimal.py` (10.7KB) |
| FR-UI-03 | **Scripts View**: แสดง tweaks แยก 10 categories + checkbox + risk badge + "?" help | Must | 48 tweaks แสดงครบ, filter ได้ | `gui/views/scripts_minimal.py` (63.5KB) |
| FR-UI-04 | **Backup & Restore Center**: timeline UI + per-tweak rollback + download script | Must | Timeline + undo buttons ทำงาน | `gui/views/backup_restore_center.py` (35.7KB) |
| FR-UI-05 | **Help View**: คำอธิบาย tweak (EN/TH bilingual) + risk info | Must | Content โหลดจาก JSON | `gui/views/help_minimal.py` (23.3KB) |
| FR-UI-06 | **Settings View**: Theme (dark/light), Accent Color (5 สี), Language (EN/TH) | Should | เปลี่ยน theme แล้ว UI refresh | `gui/views/settings_minimal.py` (12KB) |
| FR-UI-07 | **Welcome Overlay**: First-run guide สำหรับผู้ใช้ใหม่ | Could | แสดงครั้งแรก + ปิดได้ | `gui/views/welcome_overlay.py` (12.7KB) |
| FR-UI-08 | **Risk Badge**: แสดง risk level (🛡️ LOW green / ⚠️ MEDIUM yellow / 🔥 HIGH red) | Must | สีตรงกับ risk level | `gui/components/risk_badge.py` |
| FR-UI-09 | **Toast Notification**: แจ้งเตือน success/warning/info/error | Should | Toast แสดงและ auto-dismiss | `gui/components/toast.py` |
| FR-UI-10 | **Enhanced Sidebar**: Navigation + active state indicator | Must | Active view highlighted | `gui/components/enhanced_sidebar.py` |
| FR-UI-11 | **View Transition**: Animated switching between views | Could | Smooth transition ≤300ms | `gui/components/view_transition.py` |
| FR-UI-12 | **Execution Dialog**: Progress bar + per-tweak status + output log | Should | แสดง progress 0-100% | `gui/components/execution_dialog.py` |
| FR-UI-13 | **Context Help Button**: ปุ่ม "?" ข้าง tweak แต่ละตัว | Should | คลิกแล้วแสดง what_it_does | `gui/components/context_help_button.py` |

### 3.6 FR-BS: Batch Script Execution

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-BS-01 | Parse batch scripts: แยก functions, commands, comments | Must | BatchParser.parse() คืน list of scripts | `core/batch_parser.py` (13.7KB) |
| FR-BS-02 | Execute batch scripts ด้วยสิทธิ์ Admin + capture output | Must | subprocess.run() + capture_output=True | `core/batch_executor.py` (6.2KB) |
| FR-BS-03 | แสดง output แบบ real-time (stream) | Should | on_output callback ทำงาน | `core/batch_executor.py` |
| FR-BS-04 | Validate scripts ก่อน execute (file exists, syntax) | Must | File.exists() + basic check | `core/profile_manager.py` L263-278 |

---

## 4. ความต้องการไม่เชิงหน้าที่ (Non-Functional Requirements)

### 4.1 คุณภาพตาม ISO/IEC 25010

| รหัส | คุณลักษณะ | ความต้องการ | Metric / Acceptance |
|------|----------|-----------|-------------------|
| NFR-01 | **Security** | ห้ามปิด Windows security features: Defender, Update, UAC, DEP, ASLR, CFG | ไม่มี tweak ใดที่ปิด features เหล่านี้ |
| NFR-02 | **Security** | ทุก tweak ที่เป็น HIGH risk ต้องมี ⚠️ warning message ≥2 ข้อ | HIGH tweaks (3 ตัว) มี warnings ≥2 |
| NFR-03 | **Reliability** | ทุก tweak ต้องมี rollback mechanism (reversible=True) | reversible=True ทุก 48 tweaks |
| NFR-04 | **Reliability** | Auto backup ก่อนทุก apply operation | BackupManager.create_backup() เรียกก่อน execute |
| NFR-05 | **Usability** | Risk level แสดงด้วย traffic light: 🟢🟡🔴 + icon + color code | 3 สีตรงกับ LOW/MEDIUM/HIGH |
| NFR-06 | **Usability** | รองรับ 2 ภาษา (EN/TH) สำหรับ help content | Help JSON มี en/th keys |
| NFR-07 | **Usability** | แต่ละ tweak มีคำอธิบาย: what_it_does + why_it_helps + limitations | 48 tweaks มี 3 field explanations ครบ |
| NFR-08 | **Performance** | UI ไม่ค้างระหว่าง system detection (async threading) | detect_all() รันใน background thread |
| NFR-09 | **Performance** | FPS gains อ้างอิงค่า realistic ranges, ไม่ overclaim | SAFE: 2-5%, COMPETITIVE: 5-10%, EXTREME: 10-15% |
| NFR-10 | **Portability** | รองรับ Windows 10 (1903+) และ Windows 11 | compatible_os: ["10", "11"] per tweak |
| NFR-11 | **Portability** | Hardware-specific tweaks filter ตาม GPU vendor + CPU vendor | get_compatible_tweaks() กรอง hardware |
| NFR-12 | **Maintainability** | Modular architecture: 3 layers แยกชัดเจน (GUI/Core/Batch) | ไม่มี GUI code ใน core/ |
| NFR-13 | **Maintainability** | Tweak Registry เป็น single source of truth (62KB, 1013 lines) | เพิ่ม tweak = เพิ่ม Tweak() ใน registry |
| NFR-14 | **Testability** | Unit test coverage ≥ 70% | pytest-cov report ≥ 70% |
| NFR-15 | **Testability** | รองรับ test markers: unit, integration, e2e, admin, slow | conftest.py pytest_configure() |
| NFR-16 | **Transparency** | ทุก tweak แสดง registry_keys ที่จะเปลี่ยน | Tweak.registry_keys populated |
| NFR-17 | **Transparency** | ทุก tweak แสดง expected_gain + limitations + warnings | 3 fields populated ทั้ง 48 tweaks |

---

## 5. Data Dictionary

### 5.1 Tweak Data Model

```python
@dataclass
class Tweak:
    id: str                          # Unique ID, e.g. "tel_diagtrack"
    name: str                        # Display name, e.g. "Disable DiagTrack"
    category: str                    # Category key, e.g. "telemetry"
    description: str                 # 1-line summary
    what_it_does: str                # Detailed technical explanation
    why_it_helps: str                # Performance reasoning with evidence
    limitations: str                 # What breaks or won't work
    warnings: List[str]              # Risk warning messages
    risk_level: str                  # "LOW" | "MEDIUM" | "HIGH"
    expected_gain: str               # e.g. "1-3% less CPU usage"
    requires_admin: bool = True      # Needs admin rights
    requires_restart: bool = False   # Needs restart after apply
    reversible: bool = True          # Can be undone
    compatible_os: List[str]         # ["10", "11"]
    compatible_hardware: Dict        # {"gpu_vendor": "NVIDIA"}
    registry_keys: List[str]         # Registry paths affected
    bat_script: str                  # Batch script filename
    bat_function: str                # Function name in .bat
    preset_safe: bool = False        # Included in SAFE
    preset_competitive: bool = False # Included in COMPETITIVE
    preset_extreme: bool = False     # Included in EXTREME
```

### 5.2 System Profile Data Model

```python
@dataclass
class SystemProfile:
    os: OSInfo            # platform, version, build, architecture
    cpu: CPUInfo           # name, vendor, cores, threads, base_clock, score(0-30)
    gpu: GPUInfo           # name, vendor, vram, driver_version, score(0-30)
    ram: RAMInfo           # total_gb, type, speed, score(0-20)
    storage: StorageInfo   # primary_type, total_gb, score(0-10)
    form_factor: str       # "desktop" | "laptop"
    tier: str              # "entry" | "mid" | "high" | "enthusiast"
    total_score: int       # 0-100
```

### 5.3 Flight Recorder Data Model

```python
@dataclass
class TweakChange:
    name: str                    # "Enable HAGS"
    category: ChangeCategory     # REGISTRY | SERVICE | BCDEDIT | NETWORK | POWER | FILE
    key_path: str                # "HKLM\\...\\HwSchMode"
    old_value: str               # "0"
    new_value: str               # "2"
    value_type: str              # "REG_DWORD"
    risk_level: RiskLevel        # LOW | MEDIUM | HIGH
    timestamp: datetime
    profile: str                 # "SAFE"
    description: str
    success: bool = True
    error_message: str = ""
    can_rollback: bool = True
    rollback_command: str         # 'reg add "..." /v HwSchMode /t REG_DWORD /d 0 /f'

@dataclass
class SystemSnapshot:
    snapshot_id: str              # "20260304_221530"
    timestamp: datetime
    operation_type: str           # "profile_applied"
    profile: str                  # "SAFE"
    tweaks: List[TweakChange]
    pre_snapshot_path: str        # Path to .reg before
    post_snapshot_path: str       # Path to .reg after
    success: bool
    error_message: str
```

---

## 6. Use Cases

### UC-01: Apply Optimization Profile

| รายการ | รายละเอียด |
|--------|-----------|
| **Actor** | Gamer (ผู้ใช้ทั่วไป) |
| **Precondition** | 1. ClutchG เปิดอยู่ 2. สิทธิ์ Admin 3. System detection เสร็จแล้ว |
| **Main Flow** | 1. ผู้ใช้เปิดหน้า Profiles → 2. เลือก COMPETITIVE → 3. อ่าน risk/warnings → 4. กด Apply → 5. ระบบสร้าง backup (FR-SF-01) → 6. FlightRecorder เริ่ม recording (FR-SF-05) → 7. Apply 35 tweaks พร้อม progress bar (FR-PM-07) → 8. FlightRecorder บันทึก changes → 9. แสดง Toast "Profile applied!" |
| **Postcondition** | Tweaks ถูก apply + backup พร้อม rollback |
| **Alternative** | 4a. ผู้ใช้กด Cancel → กลับหน้า Profiles |
| **Exception** | 7a. Batch script ล้มเหลว → บันทึก error + แจ้ง Toast warning |

### UC-02: Rollback Per-Tweak

| รายการ | รายละเอียด |
|--------|-----------|
| **Actor** | Power User |
| **Precondition** | มี snapshot อย่างน้อย 1 รายการ |
| **Main Flow** | 1. หน้า Backup Center → 2. เลือก snapshot จาก timeline → 3. ดู tweaks ที่เปลี่ยน (before/after) → 4. กด "Undo" ข้าง tweak ที่ต้องการ → 5. ระบบ execute rollback_command → 6. อัพเดต timeline |
| **Postcondition** | Tweak ถูก undo กลับเป็นค่าเดิม |

### UC-03: Create Custom Preset

| รายการ | รายละเอียด |
|--------|-----------|
| **Actor** | Power User |
| **Precondition** | หน้า Scripts เปิดอยู่ |
| **Main Flow** | 1. เลือก tweaks ทีละตัว (checkbox) → 2. ดู risk + warnings → 3. กด "Save as Preset" → 4. ตั้งชื่อ preset → 5. ระบบ validate + save → 6. Preset พร้อมใช้ |
| **Extension** | Export เป็น JSON (FR-PM-09), Import จาก JSON (FR-PM-10) |

---

## 7. Interface Requirements

### 7.1 ข้อกำหนด GUI

| ส่วน | ข้อกำหนด |
|------|---------|
| **Window Size** | 1000×700 pixels (default) |
| **Framework** | CustomTkinter (tkinter wrapper) |
| **Theme** | Dark mode (default) / Light mode |
| **Accent Colors** | Cyan, Purple, Green, Orange, Pink |
| **Icons** | Google Material Symbols Outlined font |
| **Typography** | System font + Material Symbols |
| **Navigation** | Enhanced Sidebar (left) + View Container (right) |

### 7.2 External Interfaces

| Interface | Protocol | รายละเอียด |
|-----------|---------|-----------|
| **Windows Registry** | pywin32 / reg.exe | Read/Write registry keys |
| **Windows Services** | sc.exe / PowerShell | Start/Stop/Disable services |
| **BCDEdit** | bcdedit.exe | Boot configuration |
| **PowerShell** | subprocess | Restore points, WMI queries |
| **File System** | pathlib / json | Config, backup, flight records |

---

## 8. บันทึกการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | คำอธิบาย |
|---------|-------|---------|---------|
| 1.0 | 2025-01-15 | nextzus | Batch optimizer requirements (ยังไม่มี GUI) |
| 2.0 | 2025-06-01 | nextzus | เพิ่ม GUI requirements, ClutchG architecture |
| 2.5 | 2025-10-01 | nextzus | เพิ่ม safety system, flight recorder |
| 3.0 | 2026-03-04 | nextzus | ปรับปรุง ISO29110, 48 tweaks ครบ, data dictionary, use cases |

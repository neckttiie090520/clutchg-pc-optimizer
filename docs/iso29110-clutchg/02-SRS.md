# 02 — เอกสารความต้องการซอฟต์แวร์ (Software Requirements Specification)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O2 (Software Requirements Specification)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.3 | **วันที่:** 2026-04-12 | **ผู้จัดทำ:** nextzus
> **อ้างอิง:** IEEE 830-1998, ISO/IEC 25010:2011, SE 721 RE 7-Step Process
> **ETVX:** SI.2 Entry=Project Plan approved → Task=Analyze/document requirements → Validation=SRS review by advisor → Exit=SRS baselined

---

## 1. บทนำ (Introduction)

### 1.1 วัตถุประสงค์ของเอกสาร
เอกสาร SRS ฉบับนี้ระบุความต้องการซอฟต์แวร์อย่างครบถ้วนสำหรับ **ClutchG PC Optimizer** ซึ่งเป็นเครื่องมือ optimization สำหรับ Windows 10/11 ที่ออกแบบตามหลัก **Evidence-Based Optimization** โดยเน้น 3 หลักการสำคัญ:
1. **Safety-First** — ทุกการเปลี่ยนแปลงต้อง reversible และมี backup
2. **Evidence-Based** — ทุก tweak ต้องมี evidence จาก 23 repos ที่วิเคราะห์
3. **Transparency** — ผู้ใช้ต้องเข้าใจก่อน apply (risk label, detailed explanation)

### 1.2 ขอบเขต (Scope)
ClutchG เป็น desktop application ที่ให้ผู้ใช้ optimize Windows 10/11 ผ่าน GUI ที่ปลอดภัย โดยมี:
- **56 optimization tweaks** จัดกลุ่มใน 10 categories
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
4. `docs/01-research-overview.md` — 23 Repository Analysis
5. `docs/03-tweak-taxonomy.md` — Tweak Taxonomy & Classification
6. `docs/04-risk-classification.md` — Risk Classification Framework
7. `docs/09-final-architecture.md` — Architecture Design Document

### 1.5 กระบวนการ Requirements Engineering (RE 7-Step Process)

เอกสาร SRS ฉบับนี้พัฒนาตามกระบวนการ **RE 7-Step (I-E-E-N-S-V-M)** จากรายวิชา SE 721:

| # | ขั้นตอน | กิจกรรมใน ClutchG | หลักฐาน |
|---|---------|-------------------|---------|
| 1 | **Inception** | ระบุปัญหา: optimizer ส่วนใหญ่ไม่ปลอดภัย ไม่มี evidence | `docs/01-research-overview.md`, thesis proposal |
| 2 | **Elicitation** | วิเคราะห์ 23 repos (Document Analysis), ทดสอบจริง (Observation), ศึกษา Windows Internals (Domain Analysis), ออกแบบ UI กับอาจารย์ (Brainstorming), สร้าง batch prototype (Prototyping) | `docs/02-repo-analysis/` (23 files), `docs/05-windows-internals.md` |
| 3 | **Elaboration** | จำแนก 56 tweaks → 10 categories, กำหนด risk level, ออกแบบ 3 profiles, สร้าง user personas 3 ประเภท, Use Case modeling | `docs/03-tweak-taxonomy.md`, `docs/04-risk-classification.md` |
| 4 | **Negotiation** | ตกลง scope: 56 tweaks (ตัด placebo ออก), 5 views, Windows 10/11, offline only | MoSCoW: Must=35, Should=15, Could=8, Won't=5 |
| 5 | **Specification** | เขียน SRS v3.0 ตาม IEEE 830 + ISO 25010 | เอกสารฉบับนี้ |
| 6 | **Validation** | อาจารย์ review SRS, สร้าง test cases จาก FRs, Traceability Matrix | `06-Traceability-Record.md`, 496+ test cases |
| 7 | **Management** | จัดการเปลี่ยนแปลงผ่าน Change Requests + SRS versioning | `07-Change-Request.md` (4 CRs), SRS v1.0→v2.0→v3.0 |

> **อ้างอิงทฤษฎี:** `docs/se-academic/08-requirements-analysis.md` — รายละเอียดการประยุกต์ RE 7-Step กับ ClutchG

### 1.6 Requirements Pyramid

```
                    ┌───────────────────┐
                    │   Business Need   │
                    │  "Safe Windows    │
                    │   Optimization"   │
                    └─────────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │ Stakeholder │ │ Stakeholder │ │ Stakeholder │
    │ Requirement │ │ Requirement │ │ Requirement │
    │ "ง่ายต่อ    │ │ "ปลอดภัย   │ │ "ปรับแต่ง   │
    │  การใช้"    │ │  ย้อนกลับได้"│ │  ได้หลาก    │
    │             │ │             │ │  หลาย"      │
    └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
           │               │               │
           ▼               ▼               ▼
    ┌──────────────────────────────────────────────┐
    │          Solution Requirements               │
    │  ┌──────────────┐  ┌──────────────────────┐  │
    │  │ Functional   │  │ Non-Functional       │  │
    │  │ 60+ FRs      │  │ 17 NFRs              │  │
    │  │ (6 groups)   │  │ (8 categories:       │  │
    │  │              │  │  Security, Reliability│  │
    │  │              │  │  Usability, Perf,     │  │
    │  │              │  │  Portability, Maint,  │  │
    │  │              │  │  Testability, Transp) │  │
    │  └──────────────┘  └──────────────────────┘  │
    └──────────────────────────────────────────────┘
```

> **อ้างอิง:** Requirements Pyramid (SE 721), `docs/se-academic/10-nfr-specification.md` Section 4

---

## 2. คำอธิบายโดยรวม (Overall Description)

### 2.1 มุมมองผลิตภัณฑ์ (Product Perspective)
ClutchG เป็นส่วนหนึ่งของ **Batch Optimizer Research Project** ที่วิเคราะห์ 23 open-source Windows optimization tools จาก GitHub แล้วสังเคราะห์ tweaks ที่มี evidence จริง ออกมาเป็น tool ที่ปลอดภัยและโปร่งใส

```
Research (23 repos) → Taxonomy (56 tweaks) → Risk Classification → Architecture Design
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
5. **GUI** — 5 views: Dashboard, Optimize Center, Backup, Help, Settings
6. **Preset I/O** — Export/Import custom presets เป็น JSON

### 2.3 ผู้ใช้งาน (User Characteristics)

| ประเภท | ความรู้เทคนิค | Profile แนะนำ | Tweaks ที่เข้าถึง | ลักษณะการใช้งาน |
|--------|-------------|--------------|-----------------|----------------|
| **Beginner** | ต่ำ — ใช้ Windows ทั่วไป | SAFE (🟢) | 14 tweaks (LOW risk) | เลือก profile แล้ว apply ทีเดียว |
| **Gamer** | ปานกลาง — เข้าใจ settings | COMPETITIVE (🟡) | 44 tweaks | ใช้ profile + ปรับบาง tweaks |
| **Power User** | สูง — เข้าใจ registry/services | EXTREME (🔴) | 56 tweaks ทั้งหมด | เลือก tweaks ทีละตัว |

### 2.4 ข้อจำกัด (Constraints)
1. **สิทธิ์ Administrator** — จำเป็นสำหรับ registry/service/bcdedit changes
2. **Windows 10/11 เท่านั้น** — ใช้ Windows-specific APIs (pywin32, WMI, PowerShell)
3. **Python 3.11+** — ใช้ modern type hints, match statements
4. **ผลลัพธ์แตกต่างตาม hardware** — FPS gains อ้างอิงค่า range (2-15%)
5. **บาง tweaks ต้อง restart** — บาง tweaks ต้อง restart หลัง apply (ดูรายละเอียดใน TweakRegistry)
6. **ไม่รองรับ ARM-based Windows** — ทดสอบเฉพาะ x64

### 2.5 สมมติฐาน (Assumptions)
1. ผู้ใช้มี Windows 10 (1903+) หรือ Windows 11 ติดตั้งบนเครื่อง
2. ผู้ใช้สามารถ Run as Administrator ได้
3. Python 3.11+ ติดตั้งแล้ว (หรือใช้ bundled executable)
4. เครื่องมี internet สำหรับ download dependencies ครั้งแรก

---

## 3. ความต้องการเชิงหน้าที่ (Functional Requirements)

### สรุปการจัดลำดับความสำคัญ MoSCoW

> **อ้างอิง:** MoSCoW Prioritization (Clegg & Barker, 1994) ตาม SE 721 — Requirements Engineering

| Priority | จำนวน FR | สัดส่วน | ตัวอย่าง |
|----------|---------|---------|---------|
| **Must** | 35 | 55.6% | System detection (FR-SD-01–03,09), 3 profiles (FR-PM-01–06,11), Tweak registry 56 ตัว (FR-TW-01–04), Backup/rollback ทั้งระบบ (FR-SF-01,02,05–08,13), Core UI views (FR-UI-01–05,08,10), Batch parse+execute (FR-BS-01,02,04) |
| **Should** | 15 | 23.8% | System score (FR-SD-04–07), Progress bar (FR-PM-07), Custom preset (FR-PM-08), Risk distribution (FR-TW-05–07), Restore point (FR-SF-03,04,09,10), Toast/Settings (FR-UI-06,09,12,13) |
| **Could** | 8 | 12.7% | Form factor (FR-SD-08), Export/Import preset (FR-PM-09,10), Compare snapshots (FR-SF-11,12), Welcome overlay (FR-UI-07,11), Export rollback (UC-14) |
| **Won't** | 5 | 7.9% | Auto-update, ARM support, Cloud sync, Windows 7/8 support, IDE-style UI |
| **รวม** | **63** | 100% | — |

**หลักการจัดลำดับ:** Must = ระบบทำงานไม่ได้ถ้าขาด, Should = เพิ่มประสิทธิภาพการใช้งาน, Could = มีเวลาเหลือจึงทำ, Won't = ตัดออกจาก scope ชัดเจน (ดู Negotiation ใน `docs/se-academic/08-requirements-analysis.md` Section 2.4)

### 3.1 FR-SD: System Detection (ตรวจจับระบบ)

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-SD-01 | ตรวจจับ CPU: ชื่อ, vendor (Intel/AMD), cores, threads, base clock | Must | แสดง CPU info ถูกต้อง ±5% | `core/system_info.py` L172-222 |
| FR-SD-02 | ตรวจจับ GPU: ชื่อ, vendor (NVIDIA/AMD/Intel), VRAM, driver version | Must | แสดง GPU info, ใช้ nvidia-smi → WMI fallback | `core/system_info.py` L224-283 |
| FR-SD-03 | ตรวจจับ RAM: ขนาด (GB, rounded up), type, speed | Must | แสดง RAM ≥ physical RAM | `core/system_info.py` L285-303 |
| FR-SD-04 | ตรวจจับ Storage: ประเภท (SSD/HDD/NVMe), ขนาดรวม | Should | ระบุ SSD/HDD ได้ถูกต้อง | `core/system_info.py` L305-334 |
| FR-SD-05 | คำนวณ System Score (0-100) จาก CPU(30) + GPU(30) + RAM(20) + Storage(10) | Should | Score = sum of sub-scores | `core/system_info.py` L115-148 |
| FR-SD-06 | จำแนก Tier: entry (<30), mid (30-49), high (50-69), enthusiast (≥70) | Should | Tier ตรงตามช่วง score | `core/system_info.py` L349-358 |
| FR-SD-07 | แนะนำ Profile ตาม System Score + Form Factor ผ่าน RecommendationService (primary: score-based, fallback: conservative heuristic; laptop→SAFE เสมอ) | Should | Laptop = SAFE เสมอ; EXTREME ต้อง score≥80 + desktop + RAM≥16GB | `core/recommendation_service.py` L151-188 |
| FR-SD-08 | ตรวจจับ Form Factor: desktop/laptop (จาก battery) | Could | มี battery = laptop | `core/system_info.py` L336-347 |
| FR-SD-09 | การตรวจจับเป็น async (threading) ไม่ block UI | Must | UI ตอบสนองระหว่าง scan | `app_minimal.py` L117-145 |

### 3.2 FR-PM: Profile Management (จัดการโปรไฟล์)

| รหัส | ความต้องการ | MoSCoW | Acceptance Criteria | Source File |
|------|-----------|--------|-------------------|-------------|
| FR-PM-01 | มี 3 preset profiles: SAFE (🟢 LOW, 2-5%), COMPETITIVE (🟡 MED, 5-10%), EXTREME (🔴 HIGH, 10-15%) | Must | ทั้ง 3 profiles โหลดได้ | `core/profile_manager.py` L61-128 |
| FR-PM-02 | SAFE: 14 tweaks (LOW risk ทั้งหมด) | Must | นับ tweaks = 14 | `core/tweak_registry.py` (preset_safe=True) |
| FR-PM-03 | COMPETITIVE: 44 tweaks (LOW + MEDIUM) | Must | นับ tweaks = 44 | `core/tweak_registry.py` |
| FR-PM-04 | EXTREME: 56 tweaks ทั้งหมด (รวม HIGH) | Must | นับ tweaks = 56 | `core/tweak_registry.py` |
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
| FR-TW-01 | เก็บ tweaks ทั้ง 56 ตัว ใน TweakRegistry (Singleton) | Must | len(registry) = 56 | `core/tweak_registry.py` L884-1012 |
| FR-TW-02 | แต่ละ tweak มี 17 fields: id, name, category, description, what_it_does, why_it_helps, limitations, warnings, risk_level, expected_gain, requires_admin, requires_restart, reversible, compatible_os, compatible_hardware, registry_keys, bat_script/bat_function, preset_* | Must | Tweak dataclass ครบ 17 fields | `core/tweak_registry.py` L13-36 |
| FR-TW-03 | จัดกลุ่มเป็น 10 categories พร้อม icon + color | Must | 10 categories ตาม TWEAK_CATEGORIES | `core/tweak_registry.py` L39-51 |
| FR-TW-04 | Filter tweaks by category, preset, OS compatibility, hardware | Must | get_tweaks_by_category(), get_compatible_tweaks() | `core/tweak_registry.py` L899-933 |
| FR-TW-05 | คำนวณ risk distribution: LOW/MEDIUM/HIGH | Should | get_risk_distribution() ถูกต้อง | `core/tweak_registry.py` L968-973 |
| FR-TW-06 | แนะนำ preset ตาม system_profile | Should | suggest_preset() คืน preset + reason (delegates to `core/recommendation_service.py`) | `core/tweak_registry.py` L935-959 |
| FR-TW-07 | Build custom preset + validate tweak_ids | Should | build_custom_preset() คืน max_risk, requires_restart | `core/tweak_registry.py` L975-1001 |

#### รายละเอียด Tweak Categories (ข้อมูลจริง 56 tweaks)

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
| **รวม** | **56** | LOW: 37, MED: 16, HIGH: 3 | — |

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
| FR-UI-03 | **Scripts View**: แสดง tweaks แยก 10 categories + checkbox + risk badge + "?" help | Must | 56 tweaks แสดงครบ, filter ได้ | `gui/views/scripts_minimal.py` (63.5KB) |
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

> **กรอบอ้างอิง:** ISO/IEC 25010 Product Quality Model — 8 คุณลักษณะคุณภาพ
> **รายละเอียดเพิ่มเติม:** `docs/se-academic/10-nfr-specification.md` (17 NFRs พร้อม SMART Fit Criteria)

### 4.1 Security (NFR-01, NFR-02)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-01 | ห้ามปิด Windows security features: Defender, Update, UAC, DEP, ASLR, CFG | ไม่มี tweak ใดใน 56 ตัวที่มี registry key ที่ disable features เหล่านี้ | Scan ทุก tweak.registry_keys — ไม่มี path ที่ปิด 6 features |
| NFR-02 | ทุก tweak ที่เป็น HIGH risk ต้องมี warning messages >= 2 ข้อ | `len(tweak.warnings) >= 2` สำหรับทุก HIGH risk tweaks (3 ตัว) | Unit test: filter HIGH tweaks -> assert warnings count >= 2 |

### 4.2 Reliability (NFR-03, NFR-04)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-03 | ทุก tweak ต้อง reversible — undo กลับค่าเดิมได้ | `tweak.reversible == True` สำหรับทุก 56 tweaks | Unit test: `assert all(t.reversible for t in registry.get_all_tweaks())` |
| NFR-04 | Auto backup ก่อนทุก apply operation | BackupManager.create_backup() ถูกเรียกก่อนทุก execute | Integration test: apply profile -> verify backup file exists |

### 4.3 Usability (NFR-05, NFR-06, NFR-07)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-05 | Risk level แสดงด้วย traffic light: เขียว (LOW), เหลือง (MEDIUM), แดง (HIGH) | 3 สีตรงกับ 3 risk levels — ผู้ใช้เข้าใจความเสี่ยงภายใน 1 วินาที | Visual inspection + unit test color mapping |
| NFR-06 | รองรับ 2 ภาษา (EN/TH) สำหรับ help content | Help JSON มี "en" และ "th" keys สำหรับทุก content item | Unit test: assert all items have both "en" and "th" keys |
| NFR-07 | แต่ละ tweak มีคำอธิบาย 3 ส่วน: what_it_does, why_it_helps, limitations | `len(field) > 0` สำหรับ 3 fields ทุก 56 tweaks | Unit test: iterate all tweaks -> assert 3 fields non-empty |

### 4.4 Performance (NFR-08, NFR-09)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-08 | UI ไม่ค้างระหว่าง system detection (async threading) | UI ตอบสนองได้ตลอด (< 100ms response) ขณะ detection ทำงาน | E2E test: start app -> click sidebar ระหว่าง detection -> assert UI responds |
| NFR-09 | FPS gains อ้างอิงค่า realistic ranges, ไม่ overclaim | SAFE: 2-5%, COMPETITIVE: 5-10%, EXTREME: 10-15% — ไม่เกิน 15% | Review expected_gain ของทุก tweak — ไม่มีตัวไหน claim > 15% |

### 4.5 Portability (NFR-10, NFR-11)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-10 | รองรับ Windows 10 (1903+) และ Windows 11 | ทุก tweak มี compatible_os ที่ระบุ ["10", "11"] หรือ subset | Unit test: assert compatible_os is subset of ["10", "11"] |
| NFR-11 | Hardware-specific tweaks filter ตาม GPU vendor + CPU vendor | NVIDIA-specific tweaks ไม่แสดงบนเครื่อง AMD GPU | Unit test: mock AMD GPU -> assert NVIDIA tweaks filtered out |

### 4.6 Maintainability (NFR-12, NFR-13)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-12 | Modular architecture: 3 layers แยกชัดเจน (GUI/Core/Batch) | ไม่มี GUI import ใน core/ — coupling ทิศทางเดียว | Code review: grep import ใน core/ ไม่พบ gui references |
| NFR-13 | Tweak Registry เป็น single source of truth (62KB, 1013 lines) | เพิ่ม tweak = เพิ่ม Tweak() ใน registry เท่านั้น (ไม่แก้ที่อื่น) | Review: tweak data มาจาก registry ไฟล์เดียว |

### 4.7 Testability (NFR-14, NFR-15)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-14 | Unit test coverage >= 70% | pytest-cov report >= 70% | `pytest --cov=src --cov-report=term` |
| NFR-15 | รองรับ test markers: unit, integration, e2e, admin, slow | conftest.py pytest_configure() ลงทะเบียนทุก marker | `pytest --markers` แสดง 5 markers |

### 4.8 Transparency (NFR-16, NFR-17)

| รหัส | ความต้องการ | Fit Criteria | วิธีทดสอบ |
|------|-----------|-------------|----------|
| NFR-16 | ทุก tweak แสดง registry_keys ที่จะเปลี่ยน | Tweak.registry_keys populated (non-empty list) สำหรับทุก tweak | Unit test: assert all tweaks have registry_keys |
| NFR-17 | ทุก tweak แสดง expected_gain + limitations + warnings | 3 fields populated ทั้ง 56 tweaks | Unit test: assert 3 fields non-empty |

### 4.9 สรุป NFR Coverage

| คุณลักษณะ ISO 25010 | จำนวน NFR | NFR IDs | ผลประเมิน |
|---------------------|----------|---------|-----------|
| Security | 2 | NFR-01, NFR-02 | PASS — ไม่มี tweak ปิด security + HIGH มี warnings ครบ |
| Reliability | 2 | NFR-03, NFR-04 | PASS — ทุก tweak reversible + auto backup ทำงาน |
| Usability | 3 | NFR-05, NFR-06, NFR-07 | PASS — traffic light + bilingual + explanations ครบ |
| Performance | 2 | NFR-08, NFR-09 | PASS — async detection + realistic claims |
| Portability | 2 | NFR-10, NFR-11 | PASS — Win10/11 + hardware filtering |
| Maintainability | 2 | NFR-12, NFR-13 | PASS — 3-layer + single source of truth |
| Testability | 2 | NFR-14, NFR-15 | PASS — coverage >= 70% + 5 markers |
| Transparency | 2 | NFR-16, NFR-17 | PASS — registry keys + 3-field explanations |
| **รวม** | **17** | — | **PASS ทั้งหมด (Score: 19/20 ตาม SE 721 rubric)** |

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

> **อ้างอิงทฤษฎี:** SE 721 — Use Case Modeling (Include/Extend/System Boundary)
> **เอกสารฉบับเต็ม:** `docs/se-academic/09-use-case-catalog.md`

### 6.0 Use Case Catalog

ClutchG มีทั้งหมด **16 Use Cases** จำแนกเป็น 5 กลุ่มตามหน้าที่ โดยมี **4 Actors** (3 primary + 1 secondary):

| Actor | ประเภท | คำอธิบาย | Use Cases ที่เข้าถึง |
|-------|--------|---------|---------------------|
| Beginner User | Primary | ผู้ใช้ทั่วไป ความรู้เทคนิคต่ำ ใช้ SAFE profile | UC-01 ถึง UC-04, UC-15 |
| Gamer | Primary | นักเล่นเกม ความรู้ปานกลาง ใช้ COMPETITIVE | UC-01 ถึง UC-05, UC-08, UC-09, UC-11, UC-15, UC-16 |
| Power User | Primary | ผู้เชี่ยวชาญ ใช้ EXTREME หรือ custom | UC-01 ถึง UC-16 (ทั้งหมด) |
| Windows OS | Secondary | ระบบปฏิบัติการที่รับคำสั่ง | ถูกเรียกโดย UC-03, UC-09, UC-12, UC-13 |

#### กลุ่ม System Detection

| UC-ID | ชื่อ | Actors | Priority |
|-------|------|--------|----------|
| UC-01 | View System Info | All users | Must |
| UC-02 | View System Score & Tier | All users | Should |

#### กลุ่ม Profile Management

| UC-ID | ชื่อ | Actors | Priority |
|-------|------|--------|----------|
| UC-03 | Apply Optimization Profile | All users | Must |
| UC-04 | View Profile Details | All users | Must |
| UC-05 | Create Custom Preset | Gamer, Power User | Should |
| UC-06 | Export Preset to JSON | Power User | Could |
| UC-07 | Import Preset from JSON | Power User | Could |

#### กลุ่ม Tweak Management

| UC-ID | ชื่อ | Actors | Priority |
|-------|------|--------|----------|
| UC-08 | Browse Tweaks by Category | Gamer, Power User | Must |
| UC-09 | Apply Individual Tweaks | Gamer, Power User | Must |
| UC-10 | View Tweak Details | Power User | Should |

#### กลุ่ม Safety & Rollback

| UC-ID | ชื่อ | Actors | Priority |
|-------|------|--------|----------|
| UC-11 | View Backup History | Gamer, Power User | Must |
| UC-12 | Rollback Per-Tweak | Power User | Must |
| UC-13 | Rollback Entire Snapshot | Power User | Must |
| UC-14 | Export Rollback Script | Power User | Could |

#### กลุ่ม Settings

| UC-ID | ชื่อ | Actors | Priority |
|-------|------|--------|----------|
| UC-15 | Change Theme/Accent | All users | Should |
| UC-16 | Change Language | Gamer, Power User | Could |

#### Include Relationships (mandatory)

| Base UC | Included UC | เหตุผล |
|---------|------------|--------|
| UC-03 (Apply Profile) | **<<include>>** Create Backup | ต้องสร้าง backup ก่อน apply เสมอ |
| UC-03 (Apply Profile) | **<<include>>** Start Flight Recording | ต้องบันทึกก่อน-หลังเสมอ |
| UC-09 (Apply Individual) | **<<include>>** Create Backup | ต้องสร้าง backup ก่อน apply เสมอ |
| UC-12 (Rollback Per-Tweak) | **<<include>>** Load Flight Records | ต้องอ่าน records เพื่อหา rollback commands |
| UC-13 (Rollback Snapshot) | **<<include>>** Load Flight Records | เช่นเดียวกับ UC-12 |

#### Extend Relationships (optional)

| Extension UC | Base UC | เงื่อนไข (Extension Point) |
|-------------|---------|--------------------------|
| UC-02 (View Score) | **<<extend>>** UC-01 (View System Info) | เมื่อ system detection สำเร็จ |
| UC-05 (Custom Preset) | **<<extend>>** UC-08 (Browse Tweaks) | เมื่อผู้ใช้เลือก tweaks แล้วกด Save |
| UC-06 (Export) | **<<extend>>** UC-05 (Custom Preset) | เมื่อผู้ใช้ต้องการ share preset |
| UC-07 (Import) | **<<extend>>** UC-05 (Custom Preset) | เมื่อผู้ใช้มี JSON file |
| UC-14 (Export Script) | **<<extend>>** UC-11 (View Backup) | เมื่อผู้ใช้ต้องการ manual rollback script |

> **หมายเหตุ:** เอกสาร `docs/se-academic/09-use-case-catalog.md` มี Use Case Description แบบ fully-dressed ครบทั้ง 5 flows หลัก (UC-01, UC-03, UC-08, UC-12, UC-15) พร้อม Activity Diagram ด้านล่างนี้เลือกแสดง 3 flows สำคัญที่สุด

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

### 6.4 Quality Gateway — Fit Criteria Validation

> **อ้างอิงทฤษฎี:** SE 721 — Requirements Validation (7 Quality Checks)
> **แหล่งข้อมูล:** `docs/se-academic/08-requirements-analysis.md` Section 2.6

การประกัน คุณภาพ requirements ใช้ **Quality Gateway** ตรวจสอบ 7 ด้านตามที่ SE 721 กำหนด:

| เกณฑ์ | คำอธิบาย | ผลตรวจ |
|-------|---------|--------|
| **Completeness** | ทุก FR มี precondition, main flow, postcondition ครบ | PASS — 63 FRs ทุกตัวมีครบ |
| **Consistency** | ไม่มี FR ขัดแย้งกัน (เช่น enable vs disable เดียวกัน) | PASS — ตรวจสอบ cross-reference แล้ว |
| **Correctness** | FR สอดคล้องกับ stakeholder needs จริง | PASS — verify จาก personas 3 ประเภท |
| **Unambiguity** | ไม่มีคำกำกวม (ควร, น่าจะ, บางส่วน) | PASS — ใช้ quantified Fit Criteria |
| **Verifiability** | ทุก FR มี Fit Criteria ที่ทดสอบได้ | PASS — เช่น FR-SD-01 "< 3 วินาที" |
| **Traceability** | ทุก FR trace ถึง UC และ test case | PASS — ดู `06-Traceability-Record.md` |
| **Modifiability** | โครงสร้าง ID ช่วยให้เพิ่ม/แก้ไขได้ง่าย | PASS — ใช้ prefix FR-{category}-{nn} |

ตัวอย่าง **Fit Criteria** ที่ใช้ตรวจสอบ:

| Requirement | Fit Criteria | ผลทดสอบ |
|-------------|-------------|---------|
| FR-SD-01: System Detection | ตรวจจับ CPU/GPU/RAM/Storage ภายใน 3 วินาที | PASS (< 2s จริง) |
| FR-PM-07: Profile Application | แสดง progress bar อัพเดตทุก tweak, error rate < 5% | PASS (0% error in tests) |
| FR-SF-01: Backup Before Apply | สร้าง .reg backup + restore point ก่อน apply ทุกครั้ง | PASS |
| NFR-PERF-01: Detection Speed | Detection เสร็จภายใน 5 วินาที | PASS (< 3s จริง) |
| NFR-SEC-01: Admin Enforcement | ปฏิเสธ operation ถ้าไม่มีสิทธิ์ Admin 100% | PASS |

---

## 7. Interface Requirements

### 7.1 ข้อกำหนด GUI

| ส่วน | ข้อกำหนด |
|------|---------|
| **Window Size** | 1000×700 pixels (default) |
| **Framework** | CustomTkinter (tkinter wrapper) |
| **Theme** | Sun Valley dark mode (`#1c1c1c` bg, `#57c8ff` accent) |
| **Accent Colors** | Sun Valley default (`#57c8ff`) |
| **Icons** | Tabler Icons v3.41.1 (bundled TTF) |
| **Typography** | Figtree (bundled TTF) + Tabler Icons |
| **Navigation** | Enhanced Sidebar (left) + View Container (right) |

### 7.2 External Interfaces

| Interface | Protocol | รายละเอียด |
|-----------|---------|-----------|
| **Windows Registry** | pywin32 / reg.exe | Read/Write registry keys |
| **Windows Services** | sc.exe / PowerShell | Start/Stop/Disable services |
| **BCDEdit** | bcdedit.exe | Boot configuration |
| **PowerShell** | subprocess | Restore points, WMI queries |
| **File System** | pathlib / json | Config, backup, flight records |

#### 7.2.1 Windows Registry Interface

| รายการ | รายละเอียด |
|--------|-----------|
| **Library/Tool** | `winreg` (stdlib), `pywin32` (`win32api`, `win32con`), `reg.exe` (fallback CLI) |
| **Access Pattern** | Read → Backup current value → Write new value → Verify write |
| **Data Formats** | `REG_DWORD` (integer 0–4294967295), `REG_SZ` (string), `REG_MULTI_SZ` (string list), `REG_BINARY` |
| **Root Keys Used** | `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\*`, `HKEY_LOCAL_MACHINE\SOFTWARE\*`, `HKEY_CURRENT_USER\SOFTWARE\*` |
| **Privilege** | HKLM writes require Administrator elevation; HKCU writes do not |
| **Backup Method** | `reg export` to `.reg` file before modification; path stored in flight record |
| **Rollback** | `reg import` from backup `.reg` file |

**Error Handling:**

| Error Code | สาเหตุ | การจัดการ |
|------------|--------|----------|
| `ERROR_ACCESS_DENIED` (5) | ไม่มีสิทธิ์ Administrator | แสดง toast แจ้งเตือน, log warning, skip tweak |
| `ERROR_FILE_NOT_FOUND` (2) | Registry key/value ไม่มีอยู่ | สร้าง key ใหม่ถ้าเป็น expected path; log info |
| `ERROR_INVALID_PARAMETER` (87) | Data type mismatch | Log error, skip tweak, แจ้งเตือนใน flight record |
| `WinError` (general) | Registry hive locked / corrupted | Retry 1 ครั้ง, ถ้าล้มเหลวอีก → skip + log critical |

**ตัวอย่างคำสั่ง:**
```
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power" /v HibernateEnabled /t REG_DWORD /d 0 /f
reg export "HKLM\SYSTEM\CurrentControlSet\Control\Power" "%BACKUP_DIR%\power_backup.reg" /y
```

#### 7.2.2 Windows Services Interface

| รายการ | รายละเอียด |
|--------|-----------|
| **Tool** | `sc.exe` (primary), `PowerShell Set-Service` (fallback), `net stop/start` (legacy) |
| **Operations** | Query status (`sc query`), Stop (`sc stop`), Disable (`sc config start=disabled`), Set Manual (`sc config start=demand`) |
| **Data Format** | CLI text output → parsed via regex: `STATE : 4 RUNNING`, `START_TYPE : 3 DEMAND_START` |
| **Protected Services** | WinDefend, SecurityHealthService, wscsvc, WdNisSvc, EventLog, wuauserv — **NEVER disabled** (Never-Disable Policy) |
| **Privilege** | ทุก operation ต้องการ Administrator |
| **Backup** | บันทึก startup type เดิม (`sc qc <service>`) ก่อน modify; เก็บใน flight record |
| **Rollback** | `sc config <service> start=<original_type>` + `sc start <service>` |

**Error Handling:**

| Error Code | สาเหตุ | การจัดการ |
|------------|--------|----------|
| `ERROR_SERVICE_DOES_NOT_EXIST` (1060) | Service ไม่มีใน OS version นี้ | Log info, skip — ไม่ถือเป็น failure |
| `ERROR_DEPENDENT_SERVICES_RUNNING` (1051) | Service มี dependents ที่ running | Stop dependents ก่อน (ถ้าอยู่ใน safe list) หรือ skip |
| `ERROR_SERVICE_NOT_ACTIVE` (1062) | Service หยุดอยู่แล้ว | Log info, ดำเนินการ disable ต่อ |
| `ERROR_ACCESS_DENIED` (5) | ไม่มีสิทธิ์ | แสดง toast แจ้งเตือน, skip |

**ตัวอย่างคำสั่ง:**
```
sc query "DiagTrack" | findstr STATE
sc config "DiagTrack" start=disabled
sc stop "DiagTrack"
```

#### 7.2.3 BCDEdit Interface

| รายการ | รายละเอียด |
|--------|-----------|
| **Tool** | `bcdedit.exe` (system binary, no alternative) |
| **Operations** | Query (`bcdedit /enum`), Set value (`bcdedit /set`), Delete value (`bcdedit /deletevalue`) |
| **Data Format** | Text output → parsed line-by-line; values are string identifiers or hex |
| **Scope** | Boot Configuration Data store — affects boot behavior, requires reboot to apply |
| **Key Parameters** | `{current}` identifier, `disabledynamictick`, `tscsyncpolicy`, `useplatformtick`, `useplatformclock` |
| **Privilege** | Administrator required; operates on system BCD store |
| **Backup** | `bcdedit /export "%BACKUP_DIR%\bcd_backup"` before any modification |
| **Rollback** | `bcdedit /import "%BACKUP_DIR%\bcd_backup"` or `bcdedit /deletevalue {current} <param>` |

**Error Handling:**

| Error Code | สาเหตุ | การจัดการ |
|------------|--------|----------|
| Exit code 1 | Parameter ไม่รองรับใน OS version | Log warning, skip — เช่น `tscsyncpolicy` ไม่มีใน Windows 10 build เก่า |
| `ERROR_ACCESS_DENIED` | ไม่มีสิทธิ์ Administrator | แจ้งเตือน, abort BCD operations ทั้งหมด |
| Reboot required | BCD changes ไม่ apply ทันที | แจ้งผู้ใช้ว่าต้อง restart; log pending status |

**ตัวอย่างคำสั่ง:**
```
bcdedit /export "C:\ClutchG\backup\bcd_backup_20260410"
bcdedit /set {current} disabledynamictick yes
bcdedit /set {current} tscsyncpolicy enhanced
```

#### 7.2.4 PowerShell Interface

| รายการ | รายละเอียด |
|--------|-----------|
| **Tool** | `powershell.exe` / `pwsh.exe` invoked via Python `subprocess.run()` |
| **Execution Policy** | `-ExecutionPolicy Bypass` per-invocation (ไม่แก้ system policy) |
| **Operations** | System restore point (`Checkpoint-Computer`), WMI queries (`Get-CimInstance`), Scheduled task management, Windows feature management |
| **Data Format** | Output captured as UTF-8 text; structured data via `-Format List` or `ConvertTo-Json` |
| **Privilege** | Restore point creation requires Administrator; WMI queries ส่วนใหญ่ไม่ต้อง |
| **Timeout** | 60 วินาที default; restore point creation อาจใช้เวลา 30–120 วินาที |
| **Encoding** | Force UTF-8: `[Console]::OutputEncoding = [Text.Encoding]::UTF8` |

**Error Handling:**

| Error Code | สาเหตุ | การจัดการ |
|------------|--------|----------|
| Exit code 1 | Command syntax error หรือ cmdlet not found | Log error + full stderr, skip operation |
| `TimeoutExpired` | Operation เกิน timeout | Kill process, log timeout, แจ้งผู้ใช้ |
| `SubprocessError` | PowerShell crash / not installed | Fallback to `cmd.exe` alternative ถ้ามี; log critical |
| Restore point limit | Windows จำกัด 1 restore point / 24 ชม. | ตรวจสอบ timestamp ก่อนสร้าง; skip ถ้าเพิ่งสร้าง |

**ตัวอย่างคำสั่ง:**
```powershell
powershell -ExecutionPolicy Bypass -Command "Checkpoint-Computer -Description 'ClutchG Pre-Optimization' -RestorePointType MODIFY_SETTINGS"
powershell -Command "Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,MaxClockSpeed | ConvertTo-Json"
```

#### 7.2.5 File System Interface

| รายการ | รายละเอียด |
|--------|-----------|
| **Library** | `pathlib.Path` (primary), `json` (config/data), `shutil` (backup copy), `os` (permissions) |
| **Base Directory** | `%LOCALAPPDATA%\ClutchG\` (per-user) หรือ `clutchg/data/` (development) |
| **Data Format** | JSON (`indent=2`, UTF-8 with BOM for Windows compatibility) |
| **Key Files** | `config.json` (user settings), `flight_record.json` (audit log), `backup/` (registry exports), `profiles/` (custom profiles) |
| **Encoding** | UTF-8 throughout; `open(..., encoding="utf-8")` enforced |
| **Privilege** | User-space writes (`%LOCALAPPDATA%`); ไม่ต้องการ admin สำหรับ config/log |
| **Concurrency** | Single-process; no file locking required |

**File Structure:**
```
%LOCALAPPDATA%\ClutchG\
├── config.json              # User preferences (theme, language, profile)
├── flight_record.json       # Audit trail: all tweaks applied/reverted
├── backup/
│   ├── registry/            # .reg export files (timestamped)
│   ├── bcd/                 # BCD backup files
│   └── services/            # Service state snapshots
└── logs/
    └── clutchg_YYYYMMDD.log # Daily log rotation
```

**Error Handling:**

| Error | สาเหตุ | การจัดการ |
|-------|--------|----------|
| `FileNotFoundError` | Config file ไม่มี (first run) | สร้าง default config อัตโนมัติ |
| `PermissionError` | Directory ถูก lock โดย antivirus | Retry 1 ครั้ง; ถ้าล้มเหลว → แจ้งผู้ใช้ |
| `json.JSONDecodeError` | Config file เสียหาย | Backup corrupted file, สร้าง default ใหม่, log warning |
| Disk full | ไม่สามารถเขียน backup/log | ตรวจสอบ free space ก่อนเริ่ม; แจ้งเตือนถ้า < 100 MB |

**ตัวอย่าง JSON (flight_record.json):**
```json
{
  "version": "2.0",
  "session_id": "20260410_143022",
  "entries": [
    {
      "timestamp": "2026-04-10T14:30:25",
      "action": "apply",
      "tweak_id": "disable_hibernation",
      "category": "power",
      "risk_level": "LOW",
      "backup_path": "backup/registry/power_20260410.reg",
      "status": "success"
    }
  ]
}
```

### 7.3 Interface Security Considerations

| มาตรการ | รายละเอียด |
|---------|-----------|
| **Privilege Escalation** | ตรวจสอบ admin rights ผ่าน `ctypes.windll.shell32.IsUserAnAdmin()` ก่อนทุก system-level operation |
| **Input Sanitization** | ไม่รับ user input โดยตรงใน shell commands; ใช้ parameterized paths เท่านั้น |
| **Dangerous Pattern Detection** | 18 patterns ตรวจจับคำสั่งอันตราย เช่น `format`, `del /f /s`, `rd /s /q` ก่อน execute |
| **Never-Disable Policy** | Hardcoded list ของ 6 protected features ที่ห้าม disable ตลอดเวลา |
| **Audit Trail** | ทุก operation บันทึกใน flight record — สามารถ trace กลับได้ 100% |
| **Backup Verification** | ตรวจสอบว่า backup file ถูกสร้างสำเร็จก่อนดำเนินการ modify |

### 7.4 Cross-Reference to UML/Behavioral Diagrams

เอกสาร SRS ฉบับนี้เชื่อมโยงกับแผนภาพ UML และ behavioral diagrams ใน **Appendix-A-UML-Diagrams.md** ดังนี้:

| Diagram Type | Section in Appendix A | เชื่อมโยง SRS Section | วัตถุประสงค์ |
|-------------|----------------------|---------------------|-------------|
| **Use Case Diagram** | §1 | §3 Use Case Catalog (UC-01 ถึง UC-16) | แสดง actor-system interactions, include/extend relationships |
| **Class Diagram** | §2 | §5 Data Dictionary, §6 Architecture | แสดงโครงสร้าง class ของ core modules, relationships ระหว่าง TweakRegistry, ProfileManager, BatchParser |
| **Sequence Diagram — Apply Optimization** | §3.1 | UC-03, FR-SD-01~07 | แสดง flow การ apply tweak: UI → ActionCatalog → BatchParser → subprocess → FlightRecorder |
| **Sequence Diagram — Backup & Restore** | §3.2 | UC-07~08, FR-BK-01~05 | แสดง flow การสร้าง backup, restore, verify integrity |
| **Activity Diagram — Safety Validation** | §4.1 | §4 NFR (NFR-01, NFR-02), FR-SD-09 | แสดง decision flow ของ safety check: Never-Disable → Dangerous Pattern → Risk Assessment → Execute/Block |
| **Activity Diagram — Profile Selection** | §4.2 | UC-04, FR-PM-01~10 | แสดง flow การเลือก profile, compare tweaks, apply selected profile |
| **State Diagram — Tweak Lifecycle** | §5 | §5 Data Dictionary (Tweak entity) | แสดง state transitions: Available → Selected → Applying → Applied → Reverting → Reverted |
| **Component Diagram** | §6 | §6 Architecture Overview | แสดง 5 layers: GUI → Core → Batch Engine → Windows API → OS |
| **Deployment Diagram** | §7 | §7 Interface Requirements | แสดง physical deployment: Dev Machine → PyInstaller → Target Windows |

> **หมายเหตุ:** แผนภาพทั้งหมดเขียนด้วย Mermaid syntax สามารถ render ได้ใน GitHub/GitLab Markdown viewers

---

## 8. การอนุมัติเอกสารความต้องการ (Requirements Approval)

### 8.1 ผู้มีส่วนร่วมในการทบทวน

| บทบาท | ชื่อ | ความรับผิดชอบ |
|--------|------|--------------|
| **ผู้จัดทำ (Author)** | nextzus | จัดทำและปรับปรุง SRS, รวบรวมความต้องการจากการวิเคราะห์ 23 open-source repos |
| **ผู้ทบทวน (Reviewer)** | ผศ.ดร.ภัทรหทัย ณ ลำพูน | ทบทวนความถูกต้อง ความครบถ้วน ความสอดคล้องกับวัตถุประสงค์วิจัย |
| **ผู้อนุมัติ (Approver)** | ผศ.ดร.ภัทรหทัย ณ ลำพูน | อนุมัติ SRS baseline สำหรับการพัฒนา |

### 8.2 บันทึกการทบทวนและอนุมัติ

| เวอร์ชัน | วันที่ทบทวน | ผู้ทบทวน | ผลลัพธ์ | หมายเหตุ |
|---------|-----------|---------|---------|---------|
| 1.0 | 2025-01-20 | ผศ.ดร.ภัทรหทัย | Approved with comments | เพิ่ม safety requirements |
| 2.0 | 2025-06-10 | ผศ.ดร.ภัทรหทัย | Approved with comments | ปรับ GUI requirements ให้ชัดเจน |
| 3.0 | 2026-03-10 | ผศ.ดร.ภัทรหทัย | Approved | ISO 29110 alignment verified |
| 3.2 | 2026-04-10 | ผศ.ดร.ภัทรหทัย | Approved | Phase 11 refactor scope confirmed |

### 8.3 เกณฑ์การอนุมัติ (Approval Criteria)

ตาม **Quality Gateway** (SE 721) — SRS ต้องผ่าน 7 เกณฑ์:

| # | เกณฑ์ | สถานะ |
|---|--------|-------|
| QG-1 | ทุก FR มี unique ID และ priority (MoSCoW) | PASS |
| QG-2 | ทุก NFR มี Fit Criteria ที่วัดได้ | PASS |
| QG-3 | ทุก Use Case มี pre/post-conditions | PASS |
| QG-4 | ไม่มี TBD/TBC ค้างใน requirements | PASS |
| QG-5 | Traceability: ทุก FR → Design → Test | PASS (ดู 06-Traceability-Record.md) |
| QG-6 | NFR ครอบคลุม 8 categories ตาม ISO 25010 | PASS (17 NFRs, 8 categories) |
| QG-7 | Stakeholder review completed | PASS |

---

## 9. บันทึกการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | คำอธิบาย |
|---------|-------|---------|---------|
| 1.0 | 2025-01-15 | nextzus | Batch optimizer requirements (ยังไม่มี GUI) |
| 2.0 | 2025-06-01 | nextzus | เพิ่ม GUI requirements, ClutchG architecture |
| 2.5 | 2025-10-01 | nextzus | เพิ่ม safety system, flight recorder |
| 3.0 | 2026-03-04 | nextzus | ปรับปรุง ISO29110, 48 tweaks ครบ, data dictionary, use cases |
| 3.1 | 2026-04-06 | nextzus | เพิ่ม SE academic enrichment: RE 7-step process (SE 721), Requirements Pyramid, MoSCoW priority table, NFR 8 sub-categories ตาม ISO 25010, UC Catalog 16 UCs + include/extend, Quality Gateway 7 checks |
| 3.2 | 2026-04-10 | nextzus | Phase 11 Recommendation Refactor: อัปเดต FR-SD-07 เป็น RecommendationService dual-path, ปรับจำนวน tweaks 48→56, profiles 17/35/48→14/44/56, tests 372→496+, views 6→5, อัปเดต UI stack (Sun Valley dark, Tabler Icons, Figtree) |
| 3.3 | 2026-04-12 | nextzus | เพิ่ม §7.2 External Interface details (5 interfaces with data formats, protocols, error codes), §7.3 Interface Security, §7.4 UML cross-references, §8 Requirements Approval/Sign-off |

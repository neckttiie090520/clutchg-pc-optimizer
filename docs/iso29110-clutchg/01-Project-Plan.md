# 01 — แผนโครงงาน (Project Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — PM.O1 (Project Plan)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.1 | **วันที่:** 2026-04-12 | **ผู้จัดทำ:** nextzus
> **อ้างอิง:** PMBOK Guide 7th Ed, ISO/IEC 29110 PM Process, SE 781/725 PM Sessions
> **ETVX:** PM.1 Entry=Thesis proposal approved → Task=Create Plan+CM → Validation=Advisor review → Exit=Plan baselined

---

## 1. ข้อมูลทั่วไป (Project Information)

| รายการ | รายละเอียด |
|--------|-----------|
| ชื่อโครงงาน | ClutchG PC Optimizer — Evidence-Based Windows Optimization Tool |
| ประเภท | Independent Study (IS) / โครงงานวิศวกรรมซอฟต์แวร์ |
| ผู้จัดทำ | nextzus |
| อาจารย์ที่ปรึกษา | ผศ.ดร.ภัทรหทัย ณ ลำพูน |
| สาขาวิชา | วิศวกรรมซอฟต์แวร์ (Software Engineering) |
| สถาบัน | CAMT, มหาวิทยาลัยเชียงใหม่ |
| เวอร์ชัน SE Lifecycle | ISO/IEC 29110 Basic Profile |
| วิธีการพัฒนา | Incremental + Iterative (Phase-based) |

---

## 2. วัตถุประสงค์โครงงาน (Project Objectives)

### 2.1 Research Objectives
1. **RO-1:** วิเคราะห์ open-source Windows optimization tools (23 repos) เพื่อหา tweaks ที่มี evidence
2. **RO-2:** สร้าง taxonomy + risk classification framework สำหรับ Windows tweaks
3. **RO-3:** ประเมินประสิทธิภาพและความปลอดภัยของ tweaks ที่คัดเลือก

### 2.2 Development Objectives
4. **DO-1:** พัฒนา evidence-based optimization framework (Batch + Python GUI)
5. **DO-2:** ออกแบบ safety system ที่ rollback ได้ครบวงจร (Backup → Flight Recorder → Restore Center)
6. **DO-3:** สร้าง GUI ที่แสดง risk level ชัดเจนและเข้าใจง่าย

### 2.3 Documentation Objectives
7. **DocO-1:** จัดทำ ISO29110 Work Products ครบตามมาตรฐาน
8. **DocO-2:** เขียน Thesis ตามโครงสร้าง 7 บท

---

## 3. ขอบเขตโครงงาน (Project Scope)

### 3.1 ในขอบเขต (In Scope)
| # | Deliverable | คำอธิบาย |
|---|------------|---------|
| 1 | Research Analysis | วิเคราะห์ 23 repos → taxonomy 48 tweaks, 10 categories |
| 2 | Batch Optimizer | .bat scripts สำหรับ optimization (9 core scripts) |
| 3 | ClutchG GUI | Python GUI (6 views, 13 core modules, 7 components) |
| 4 | Safety System | BackupManager + FlightRecorder + Restore Center |
| 5 | Test Suite | Unit (285) + Integration (23) + E2E (64) tests — 372 total collected |
| 6 | ISO29110 Docs | 10 work products ใน docs/iso29110-clutchg/ |
| 7 | Thesis | 7 chapters ใน thesis/THESIS_DOCS/ |

### 3.2 นอกขอบเขต (Out of Scope)
- Linux / macOS support
- Cloud-based optimization
- Hardware overclocking
- ปิด Defender / Windows Update / UAC (Never-Disable Policy)
- Mobile application
- Real-time FPS measurement

---

## 4. Work Breakdown Structure (WBS)

> **อ้างอิง:** SE 781 WBS decomposition — 3 ระดับ ครอบคลุม 7 กลุ่มงาน
> **หลักการ:** 100% Rule — WBS ต้องครอบคลุมงานทั้งหมด ไม่ขาดไม่เกิน

### 4.1 WBS Hierarchy (Level 1-3)

```
ClutchG PC Optimizer (IS Project)
│
├── 1.0 Research & Analysis
│   ├── 1.1 Repository Analysis (23 repos)
│   ├── 1.2 Tweak Taxonomy (48 tweaks, 10 categories)
│   └── 1.3 Risk Classification (LOW/MEDIUM/HIGH)
│
├── 2.0 Requirements
│   ├── 2.1 SRS Document (60+ FRs, 17 NFRs)
│   ├── 2.2 Use Case Modeling (16 UCs)
│   └── 2.3 Traceability Matrix
│
├── 3.0 Design
│   ├── 3.1 Architecture Design (Hybrid Layered)
│   ├── 3.2 Detailed Design (13 core modules)
│   ├── 3.3 UML Diagrams (13 diagrams)
│   └── 3.4 UI/UX Design (3 phases)
│
├── 4.0 Implementation
│   ├── 4.1 Batch Optimizer
│   │   ├── 4.1.1 Core Scripts (17 modules)
│   │   ├── 4.1.2 Profiles (3 presets)
│   │   └── 4.1.3 Safety Scripts (validator, rollback)
│   │
│   ├── 4.2 Python GUI
│   │   ├── 4.2.1 Core Layer (13 managers)
│   │   ├── 4.2.2 GUI Views (8 views)
│   │   ├── 4.2.3 GUI Components (12 widgets)
│   │   └── 4.2.4 Theme & Styling
│   │
│   └── 4.3 Integration
│       ├── 4.3.1 BatchParser integration
│       └── 4.3.2 BatchExecutor integration
│
├── 5.0 Testing
│   ├── 5.1 Unit Testing (285 cases)
│   ├── 5.2 Integration Testing (23 cases)
│   ├── 5.3 E2E Testing (64 cases)
│   ├── 5.4 Security Audit (28 items)
│   └── 5.5 Regression Testing
│
├── 6.0 Documentation
│   ├── 6.1 ISO 29110 Work Products (10 docs)
│   ├── 6.2 Research Documents (16 docs)
│   ├── 6.3 User Guides (TH + EN)
│   └── 6.4 Thesis Chapters (8 chapters)
│
└── 7.0 Delivery
    ├── 7.1 Build & Package (PyInstaller)
    ├── 7.2 Final IS Document
    └── 7.3 Thesis Defense
```

### 4.2 WBS Dictionary (Level 2)

| WBS | Work Package | Duration | Deliverable | Predecessor |
|-----|-------------|----------|------------|-------------|
| 1.1 | Repository Analysis | 2 months | 23 repo analysis docs | — |
| 1.2 | Tweak Taxonomy | 1 month | Taxonomy document | 1.1 |
| 1.3 | Risk Classification | 0.5 month | Risk framework | 1.2 |
| 2.1 | SRS Document | 1 month | SRS v3.0 | 1.3 |
| 2.2 | Use Case Modeling | included in 2.1 | 16 UCs | 1.3 |
| 3.1 | Architecture Design | 1 month | SDD + Architecture doc | 2.1 |
| 4.1 | Batch Optimizer | 2 months | 17 .bat scripts + 3 profiles | 3.1 |
| 4.2 | Python GUI | 6 months | ClutchG app | 4.1 |
| 5.1 | Unit Testing | 1 month | 285 test cases | 4.2 |
| 5.4 | Security Audit | 0.25 month | 28-item audit report | 5.1 |
| 6.1 | ISO 29110 WPs | 2 months | 10 documents | 5.1 |
| 7.1 | Build & Package | 1 month | ClutchG.exe + IS document | 6.1 |

---

## 5. กำหนดการโครงงาน (Project Schedule)

| Phase | WBS | กิจกรรม | Duration | Start | End | Deliverables | Status |
|-------|-----|---------|----------|-------|-----|-------------|--------|
| 1 | 1.1-1.4 | Research & Analysis | 8 weeks | 2025-01 | 2025-02 | 01-research-overview, 23 repos analyzed | ✅ |
| 2 | 1.4 | Taxonomy & Risk | 4 weeks | 2025-03 | 2025-03 | 03-tweak-taxonomy, 04-risk-classification | ✅ |
| 3 | 2.1-2.4 | Architecture Design | 4 weeks | 2025-04 | 2025-04 | 09-final-architecture | ✅ |
| 4 | 3.1-3.4 | Batch Optimizer | 8 weeks | 2025-05 | 2025-06 | src/*.bat, profiles, safety scripts | ✅ |
| 5 | 4.1-4.2 | GUI Foundation | 8 weeks | 2025-07 | 2025-08 | app_minimal.py, core managers | ✅ |
| 6 | 4.1 | Safety System | 4 weeks | 2025-09 | 2025-09 | backup_manager, flight_recorder | ✅ |
| 7 | 4.3 | UI Views | 4 weeks | 2025-10 | 2025-10 | 6 views complete | ✅ |
| 8 | 5.1-5.4 | Testing | 4 weeks | 2025-11 | 2025-11 | 49 tests (unit+int+e2e) | ✅ |
| 9 | 4.3-4.4 | Restore Center | 4 weeks | 2025-12 | 2025-12 | backup_restore_center, timeline | ✅ |
| 10 | 4.4 | Quick Wins & Polish | 4 weeks | 2026-01 | 2026-01 | Toast, theme, welcome | ✅ |
| 11 | 6.1-6.4 | Documentation | 8 weeks | 2026-02 | 2026-03 | ISO29110 WPs, Thesis | ✅ |
| 11a | 5.1-5.4 | Security Audit & Test Expansion | 1 week | 2026-03 | 2026-03 | 28-item audit, +160 tests, 0 defects | ✅ |
| 12 | 7.1-7.3 | Final Delivery | 4 weeks | 2026-04 | 2026-04 | Final IS document | ⏳ |

**Total Duration:** ~15 months (Jan 2025 — Apr 2026)

### 5.2 Critical Path Method (CPM)

> **อ้างอิง:** SE 781 — Critical Path คือ longest path ผ่าน project network; กิจกรรมบน critical path มี float = 0

#### Project Network

```
        ┌──────┐     ┌──────┐     ┌──────┐
Start──►│ 1.1  │────►│ 1.2  │────►│ 1.3  │
        │ Repo │     │ Tax  │     │ Risk │
        │ 2mo  │     │ 1mo  │     │ 0.5mo│
        └──────┘     └──────┘     └──┬───┘
                                      │
                                      ▼
                                 ┌──────┐     ┌──────┐
                                 │ 2.1  │────►│ 3.1  │
                                 │ SRS  │     │ Arch │
                                 │ 1mo  │     │ 1mo  │
                                 └──────┘     └──┬───┘
                                                  │
                          ┌───────────────────────┤
                          ▼                       ▼
                     ┌──────┐               ┌──────┐
                     │ 4.1  │──────────────►│ 4.2  │
                     │ Batch│               │ GUI  │
                     │ 2mo  │               │ 6mo  │
                     └──────┘               └──┬───┘
                                                │
                          ┌─────────────────────┤
                          ▼                     ▼
                     ┌──────┐              ┌──────┐
                     │ 5.x  │              │ 6.x  │
                     │ Test │              │ Docs │
                     │ 1.5mo│              │ 2mo  │
                     └──┬───┘              └──┬───┘
                        │                     │
                        └──────────┬──────────┘
                                   ▼
                              ┌──────┐
                              │ 7.x  │
                              │Deliver│
                              │ 1mo  │
                              └──────┘──► End
```

#### Path Analysis

| Path | Activities | Duration |
|------|-----------|----------|
| **Path A** | 1.1 → 1.2 → 1.3 → 2.1 → 3.1 → 4.1 → 4.2 → 5.x → 7.x | 16 months |
| **Path B (Critical)** | 1.1 → 1.2 → 1.3 → 2.1 → 3.1 → 4.1 → 4.2 → 6.x → 7.x | **16.5 months** |
| Path C | 1.1 → 1.2 → 1.3 → 2.1 → 3.1 → 4.2 → 5.x → 7.x | 14 months |

**Critical Path: Path B** (16.5 months) — Research → SRS → Architecture → Batch → GUI → Documentation → Delivery

**หมายเหตุ:** Timeline จริง = 15 เดือน เพราะบางกิจกรรม overlap (testing + documentation ทำคู่กัน)

#### Float Analysis

| Activity | Float | หมายเหตุ |
|----------|-------|---------|
| 1.1 Repo Analysis | 0 | Critical — เลื่อนไม่ได้ |
| 1.2 Taxonomy | 0 | Critical |
| 2.1 SRS | 0 | Critical |
| 3.1 Architecture | 0 | Critical |
| 4.1 Batch Optimizer | 0 | Critical |
| 4.2 Python GUI | 0 | Critical |
| 5.x Testing | 0.5 mo | Near-critical — มี buffer เล็กน้อย |
| 6.x Documentation | 0 | Critical |
| 7.x Delivery | 0 | Critical |

---

## 6. Triple Constraint

> **อ้างอิง:** SE 781 — Iron Triangle: Scope, Time, Cost สัมพันธ์กัน เปลี่ยน 1 ด้าน → กระทบอีก 2 ด้าน (Quality อยู่ตรงกลาง)

| Constraint | กำหนด | จริง | Variance |
|-----------|-------|------|----------|
| **Scope** | 48 tweaks, 3 profiles, GUI, safety system, ISO 29110 docs | ครบตามแผน + 4 CRs (เพิ่ม scope) | +4 CRs (scope creep ที่ควบคุมได้) |
| **Time** | 15 เดือน (Jan 2025 — Apr 2026) | 14/15 เดือนเสร็จ 99% | On schedule |
| **Cost** | 0 THB (solo developer, open-source tools) | 0 THB | On budget |
| **Quality** | 100% test pass, 0 HIGH defects, 60%+ coverage | 100% pass, 0 defects, 65%+ | Meets/Exceeds |

### Trade-off Decisions

| สถานการณ์ | Trade-off | ผลลัพธ์ |
|----------|----------|---------|
| CR-001: Restore Center | Scope ↑ (เพิ่ม feature) → Time ↑ (1 เดือน) | คุ้มค่า — UX ดีขึ้นมาก |
| CR-004: Security Audit | Scope ↑ (เพิ่ม 160 tests) → Time ↑ (2 สัปดาห์) | จำเป็น — Quality ↑ (B+ → A-) |
| No Auto-update | Scope ↓ (ตัด feature) → Time saved | ถูกต้อง — เกิน thesis scope |
| No ARM support | Scope ↓ → Time saved | ถูกต้อง — ไม่มี hardware ทดสอบ |

---

## 7. EVM Baseline

> **อ้างอิง:** SE 781 — Earned Value Management tracks cost/schedule performance
> **BAC (Budget at Completion):** 1,300 hours

| Metric | Formula | Value | สถานะ |
|--------|---------|-------|-------|
| **PV** | 14/15 × 1,300 | 1,213 hours | — |
| **EV** | 99% × 1,300 | 1,287 hours | — |
| **AC** | Actual hours | 1,280 hours | — |
| **CV** | EV − AC | **+7 hours** | Under budget |
| **SV** | EV − PV | **+74 hours** | Ahead of schedule |
| **CPI** | EV / AC | **1.005** | Efficient (> 1.0) |
| **SPI** | EV / PV | **1.061** | Ahead (> 1.0) |
| **EAC** | BAC / CPI | **1,294 hours** | จะเสร็จใต้ budget |
| **TCPI** | (BAC − EV) / (BAC − AC) | **0.65** | เหลือน้อย ทำสบาย |

**ดูรายละเอียด EVM Phase-by-Phase Tracking ที่ `docs/se-academic/14-risk-register-evm.md`**
**ดูรายละเอียด Progress Status ที่ `08-Progress-Status-Record.md`**

---

## 8. ทรัพยากร (Resources)

### 8.1 ทีมงาน

| บทบาท | ชื่อ | ความรับผิดชอบ | Effort |
|--------|------|-------------|--------|
| Project Manager | nextzus | วางแผน, ติดตาม, reporting | 10% |
| Researcher | nextzus | วิเคราะห์ repos, evidence validation | 20% |
| Developer | nextzus | Batch + Python GUI development | 40% |
| Tester | nextzus | Unit/Integration/E2E testing | 15% |
| Technical Writer | nextzus | ISO29110 WPs + Thesis | 15% |

### 8.2 ซอฟต์แวร์

| รายการ | เวอร์ชัน | ใช้ใน |
|---------|---------|------|
| Python | 3.11+ (tested: 3.12, 3.14) | Core + GUI |
| customtkinter | ≥5.2.0 | GUI framework |
| psutil | ≥5.9.0 | System detection |
| pywin32 | ≥306 | Windows API |
| py-cpuinfo | ≥9.0.0 | CPU detection |
| wmi | ≥1.5.1 | WMI queries |
| Pillow | ≥10.0.0 | Image processing |
| pytest + plugins | latest | Testing |
| VS Code | latest | Development |
| Git | latest | Version control |

---

## 9. การจัดการความเสี่ยง (Risk Management)

> **อ้างอิง:** SE 781 — 4 ขั้นตอน: Identify → Analyze → Respond (AMTA) → Monitor
> **AMTA:** Avoid, Mitigate, Transfer, Accept

### 9.1 Risk Register (Probability × Impact Scoring)

| ID | ความเสี่ยง | หมวด | P (1-5) | I (1-5) | Score | Priority | กลยุทธ์ (AMTA) | สถานะ |
|----|-----------|------|---------|---------|-------|----------|---------------|-------|
| R-01 | Tweaks ทำให้ Windows เสียหาย | Technical | 4 | 5 | 20 | Critical | **Mitigate** — Safety Rules 6 ข้อ, ห้ามปิด Defender/UAC/DEP, ทุก tweak reversible | ✅ Resolved |
| R-02 | ผู้ใช้ไม่สามารถ rollback ได้ | Technical | 3 | 5 | 15 | High | **Mitigate** — FlightRecorder (before/after), auto backup, per-tweak rollback | ✅ Resolved |
| R-03 | Windows Update เปลี่ยน registry paths | External | 3 | 4 | 12 | High | **Mitigate** — compatible_os field, ตรวจ OS version ก่อน apply | ✅ Resolved |
| R-04 | Solo developer ไม่สามารถทำเสร็จทันเวลา | Schedule | 3 | 4 | 12 | High | **Mitigate** — ใช้ AI agents ช่วยเขียน code + docs, ตัด scope ที่ไม่จำเป็น | ✅ Resolved |
| R-05 | CustomTkinter ไม่ stable บาง Windows versions | Technical | 2 | 4 | 8 | Medium | **Accept** (Active) — ทดสอบบน Win10 + Win11, document known issues | ⚠️ Monitor |
| R-06 | Security vulnerabilities ใน code | Technical | 3 | 4 | 12 | High | **Mitigate** — Security audit + 160 new tests, fix 7 P1-P3 bugs | ✅ Resolved |
| R-07 | ผู้ใช้ไม่เข้าใจ risk level ของ tweaks | Usability | 3 | 3 | 9 | Medium | **Mitigate** — Traffic light risk display, 3-field explanation per tweak | ✅ Resolved |
| R-08 | Batch scripts ไม่ทำงานบน Windows 11 | Technical | 2 | 4 | 8 | Medium | **Mitigate** — System detection ก่อน apply, OS-specific tweak filtering | ✅ Resolved |
| R-09 | Library dependency ถูก deprecate (GPUtil) | External | 3 | 3 | 9 | Medium | **Avoid** — ลบ GPUtil dependency, ใช้ WMI query แทน | ✅ Resolved |
| R-10 | Thesis defense ไม่ผ่าน | Academic | 1 | 5 | 5 | Medium | **Mitigate** — จัดทำเอกสารครบ 10 WPs, ISO 29110 compliance, ทดสอบครบ | ⚠️ Monitor |

### 9.2 Risk Matrix (5×5)

```
Impact ↑
  5  │  R-10        R-04,R-03,R-06   R-01
     │                                R-02
  4  │              R-08,R-05
     │
  3  │              R-07,R-09
     │
  2  │
     │
  1  │
     └──────────────────────────────────────► Probability
        1         2         3         4    5
```

**Risk Zone:** แดง (15-25): R-01, R-02 | ส้ม (9-14): R-03, R-04, R-06, R-07, R-09 | เหลือง (5-8): R-05, R-08, R-10

### 9.3 EMV Analysis (Expected Monetary Value — แปลงเป็นชั่วโมง)

| Risk | Prob | Impact (hrs) | EMV (hrs) | Mitigation Cost (hrs) | Decision |
|------|------|-------------|-----------|----------------------|----------|
| R-01 | 0.4 | 200 | 80 | 40 (safety system) | Mitigate (40 < 80) |
| R-02 | 0.3 | 160 | 48 | 30 (FlightRecorder) | Mitigate (30 < 48) |
| R-04 | 0.3 | 120 | 36 | 20 (AI assistance) | Mitigate (20 < 36) |
| R-06 | 0.3 | 100 | 30 | 16 (security audit) | Mitigate (16 < 30) |
| R-09 | 0.3 | 40 | 12 | 8 (pre-emptive remove) | Avoid (8 < 12) |
| **Total** | | | **206** | **114** | **Net savings: 92 hrs** |

### 9.4 Risk Resolution Summary

- Resolved: 8/10 (80%) | Monitoring: 2/10 (20%) | Open: 0/10 (0%)
- ใช้กลยุทธ์ AMTA: Avoid (1), Mitigate (8), Accept (1)
- ดูรายละเอียดที่ `docs/se-academic/14-risk-register-evm.md`

---

## 10. เกณฑ์คุณภาพ (Quality Criteria — PM.O7)

| # | เกณฑ์ | Target | วิธีวัด | สถานะ |
|---|-------|--------|--------|-------|
| Q-01 | Unit test coverage | ≥ 70% | pytest-cov report | ✅ ~75% |
| Q-02 | Test pass rate (P0 safety) | 100% | Integration test results | ✅ 100% |
| Q-03 | ไม่ปิด Windows security | 0 violations | Code review + grep | ✅ Pass |
| Q-04 | ทุก tweak มี rollback | 48/48 reversible | TweakRegistry check | ✅ 48/48 |
| Q-05 | ทุก tweak มี risk label | 48/48 labeled | TweakRegistry check | ✅ 48/48 |
| Q-06 | ทุก tweak มี evidence | 48/48 documented | what_it_does + why_it_helps | ✅ 48/48 |
| Q-07 | ISO29110 Work Products | 10/10 complete | docs/iso29110-clutchg/ | ✅ 10/10 |
| Q-08 | No HIGH severity defects | 0 open | Defect tracking | ✅ 0 open |
| Q-09 | Security audit findings resolved | 0 open | Audit report (CR-004) | ✅ 0 open |

---

## 11. การสื่อสาร (Communication Plan)

| ช่องทาง | ความถี่ | ผู้เข้าร่วม | เนื้อหา |
|---------|--------|-----------|---------|
| Progress Report | รายเดือน | nextzus, Advisor | Phase progress, % complete, risks |
| IS Meeting | ตามนัด | nextzus, Advisor | Demo, review, feedback |
| Git Commit | รายวัน | nextzus | Code changes, documentation |
| ISO29110 WP Review | Per phase | nextzus, Advisor | Work product sign-off |

---

## 12. Delivery & Acceptance

### 12.1 Deliverables

| # | Deliverable | Format | ที่ตั้ง |
|---|------------|--------|-------|
| 1 | Source Code | Git repo | `clutchg/src/`, `src/` |
| 2 | Test Suite | Git repo | `clutchg/tests/` |
| 3 | ISO29110 Work Products | Markdown | `docs/iso29110-clutchg/` |
| 4 | Thesis Document | Markdown + PDF | `thesis/THESIS_DOCS/` |
| 5 | User Guides | Markdown | `clutchg/README.md`, `QUICKSTART.md` |
| 6 | Research Documents | Markdown | `docs/` |

### 12.2 Acceptance Criteria
1. Source code compiles and runs without error
2. Test suite passes (≥ 95% pass rate)
3. ISO29110 Work Products complete (10/10)
4. Thesis review approved by advisor
5. No HIGH severity defects open

---

## 13. PMBOK Process Groups Mapping

> **อ้างอิง:** SE 781 — PMBOK 5 Process Groups (I-P-E-M&C-C) ประยุกต์กับ ClutchG
> **รายละเอียดเพิ่มเติม:** `docs/se-academic/13-project-management.md` Section 1.2

### 13.1 Initiating

| กิจกรรม | หลักฐาน ClutchG |
|---------|----------------|
| ระบุ Stakeholders | ผู้ใช้ 3 กลุ่ม (Beginner/Gamer/Power User), อาจารย์ที่ปรึกษา |
| สร้าง Project Charter | แบบขออนุมัติหัวข้อ (`docs/แบบขออนุมัติหัวข้อฯ.pdf`) |
| กำหนด scope เบื้องต้น | "Safe Windows optimizer based on 23-repo research" |
| ได้รับอนุมัติ | อาจารย์ที่ปรึกษา approve thesis proposal |

### 13.2 Planning

| กิจกรรม | หลักฐาน ClutchG |
|---------|----------------|
| สร้าง Project Plan | `docs/iso29110-clutchg/01-Project-Plan.md` (เอกสารนี้) |
| กำหนด WBS | 7 กลุ่มงาน, 3 ระดับ (ดู Section 4) |
| สร้าง Schedule + CPM | 12 phases, Critical Path B = 16.5 เดือน (ดู Section 5) |
| กำหนด Risk Plan | 10 risks, P×I scoring, AMTA strategies (ดู Section 9) |
| กำหนด CM Plan | `docs/iso29110-clutchg/09-Configuration-Plan.md` |
| กำหนด Test Plan | `docs/iso29110-clutchg/04-Test-Plan.md` |

### 13.3 Executing

| กิจกรรม | หลักฐาน ClutchG |
|---------|----------------|
| พัฒนา Batch Optimizer | `src/core/` — 17 modules, 3 profiles |
| พัฒนา Python GUI | `clutchg/src/` — 13 core + 8 views + 12 components |
| เขียน Tests | `clutchg/tests/` — 372 test cases |
| จัดทำเอกสาร ISO 29110 | `docs/iso29110-clutchg/` — 10 work products |
| จัดทำ thesis chapters | `thesis/thesis-chapters/` — 8 chapters |

### 13.4 Monitoring & Controlling

| กิจกรรม | หลักฐาน ClutchG |
|---------|----------------|
| Track progress vs plan | `docs/iso29110-clutchg/08-Progress-Status-Record.md` |
| Process Change Requests | 4 CRs (`docs/iso29110-clutchg/07-Change-Request.md`) |
| Update Traceability Matrix | `docs/iso29110-clutchg/06-Traceability-Record.md` |
| Security Audit & Corrective Action | `clutchg/docs/BUG_FIX_REPORT_2026-03-24.md` |
| EVM Tracking | CPI = 1.005, SPI = 1.061 (ดู Section 7) |

### 13.5 Closing

| กิจกรรม | หลักฐาน ClutchG | สถานะ |
|---------|----------------|-------|
| ส่งมอบผลิตภัณฑ์ | `clutchg/dist/ClutchG.exe` | อยู่ระหว่างดำเนินการ |
| ส่ง thesis document | Thesis chapters + IS document | อยู่ระหว่างดำเนินการ |
| Lessons learned | ดู §14 Lessons Learned | ✅ บันทึกแล้ว |
| Archive records | Git repository complete | Ready |

---

## 14. Lessons Learned

> **อ้างอิง:** SE 781 — Closing Process Group (Lessons Learned Documentation)
> บันทึกบทเรียนที่ได้จากการดำเนินโครงงาน ClutchG ตลอด 15 เดือน เพื่อเป็นประโยชน์สำหรับโครงงานในอนาคต

### 14.1 Research & Methodology

| หมวด | บทเรียน | ผลกระทบ |
|------|---------|---------|
| Systematic Literature Review | การวิเคราะห์ 23 repositories (50,000+ lines) ก่อนเริ่มพัฒนาช่วยให้เข้าใจ landscape ของ Windows optimization tools ได้ครอบคลุม สามารถแยก evidence-based tweaks ออกจาก myths/placebos ได้ตั้งแต่ต้น | ลดเวลา design rework เพราะมี taxonomy ชัดเจนก่อนเขียนโค้ด |
| Risk Classification Framework | การสร้าง 3-tier risk framework (LOW/MEDIUM/HIGH) ตั้งแต่ phase วิจัย ทำให้การตัดสินใจด้าน safety มีเกณฑ์ชัดเจน ไม่ต้องตัดสินใจแบบ ad hoc ระหว่างพัฒนา | ทุก tweak มี risk level ที่ตรวจสอบได้ ลดโอกาสเกิดปัญหาด้าน safety |
| Evidence-Based Approach | การกำหนดว่าทุก tweak ต้องมี technical justification ที่บันทึกไว้ ป้องกันการเพิ่ม placebo tweaks ที่พบบ่อยใน open-source optimizers | สร้างความน่าเชื่อถือของซอฟต์แวร์ แตกต่างจาก competitors ที่โฆษณาเกินจริง |

### 14.2 Architecture & Design Decisions

| หมวด | บทเรียน | ผลกระทบ |
|------|---------|---------|
| Safety-First Architecture | การออกแบบ Never-Disable Policy ตั้งแต่ต้น (ห้ามปิด Defender, UAC, DEP, ASLR, CFG, Windows Update) ช่วยลดความเสี่ยง และเป็นจุดแข็งในการ defense | ไม่มี safety incident ตลอดการพัฒนาและทดสอบ |
| Layered Architecture | การแยก Core (business logic) ออกจาก GUI (views) ทำให้ทดสอบ business logic ได้โดยไม่ต้องมี GUI ส่งผลให้ coverage สูงขึ้น | Unit tests ครอบคลุม 85–92% สำหรับ key modules โดยไม่ต้อง display |
| Tweak Registry as Single Source | การรวม tweak metadata ทั้งหมดไว้ใน `tweak_registry.py` แทนที่จะกระจายในหลายไฟล์ ทำให้ maintain ง่ายและ consistency สูง | เพิ่ม tweaks จาก 20 → 56 ได้โดยไม่ต้องแก้ไขหลายจุด |
| GPUtil Removal (CR-002) | Library ภายนอก (GPUtil) หยุดอัปเดตและมี compatibility issues — การ refactor ใช้ WMI + psutil fallback แทนลด dependency risk | ลด dependency จาก 7 เหลือ 6 packages, เพิ่มความเสถียร |

### 14.3 Testing Strategy

| หมวด | บทเรียน | ผลกระทบ |
|------|---------|---------|
| Early Test Investment | การเขียน test framework ตั้งแต่ Phase 4 (ไม่ใช่ Phase 8 ตามแผนเดิม) ช่วยจับ bugs ได้เร็วขึ้น DRE สะสม = 100% pre-release | ไม่มี defect หลุดไป production |
| Security Audit as Separate Phase | การทำ Security Audit (CR-004) แยกเป็น Phase 11a เพิ่ม 160 security tests ที่ไม่อยู่ในแผนเดิม ใช้เวลาเกิน 8 ชม. แต่คุ้มค่า | พบและแก้ 11 security-related defects ก่อน release |
| E2E Limitation in Headless | E2E tests 64 ชุดต้อง skip ในสภาพแวดล้อมที่ไม่มี display ส่งผลให้ overall coverage ต่ำกว่าที่ควร ควรวางแผน headless testing strategy ตั้งแต่ต้น | Coverage รายงานต่ำกว่าจริง (~65% vs ~80% ถ้ารวม E2E) |
| Recommendation Refactor (Phase 11b) | การ refactor แยก RecommendationService ออกจาก SystemDetector ช่วยให้ test ง่ายขึ้นมาก (18 tests สำหรับ recommendation logic แยกจาก hardware detection) | SRP compliance ดีขึ้น, coverage recommendation_service = 92% |

### 14.4 ISO 29110 Compliance

| หมวด | บทเรียน | ผลกระทบ |
|------|---------|---------|
| Document-First vs Code-First | การเขียน SRS/SDD ก่อนเริ่ม coding (Waterfall-like documentation) ช่วยให้ traceability ชัดเจน แต่ต้อง update เอกสารบ่อยเมื่อ design เปลี่ยน | Trade-off: traceability 88.1% แต่ revision history ยาว (SRS v3.2, SDD v3.3) |
| ETVX Model | การใช้ ETVX (Entry-Task-Verification-Exit) headers ในทุกเอกสาร ISO ช่วยให้ตรวจสอบ completeness ของแต่ละ work product ได้ง่าย | ISO auditor สามารถตรวจ criteria ได้โดยตรงจาก header |
| Solo Developer + ISO 29110 | ISO 29110 ออกแบบสำหรับ VSE (1–25 คน) แต่ solo developer ต้องรับทุกบทบาท (PM, developer, tester, CM) ทำให้ overhead เอกสารสูง | บทเรียน: ใช้ template ที่ปรับให้เหมาะกับ 1-person team, merge roles ที่ซ้อนทับ |

### 14.5 Solo Developer Challenges

| หมวด | บทเรียน | ผลกระทบ |
|------|---------|---------|
| No Peer Review | ไม่มี code review จากคนอื่น ต้องใช้ static analysis + comprehensive tests แทน | ใช้ test suite เป็น safety net แทน human review |
| Scope Creep | Feature freeze หลัง v2.0 มีความสำคัญ — ป้องกันไม่ให้เพิ่ม features ใหม่โดยไม่จำเป็นในช่วง documentation phase | 4 CRs ทั้งหมดเป็น corrective/improvement ไม่ใช่ new features |
| Time Management | EVM tracking (CPI=1.005, SPI=1.061) ช่วยให้เห็นสถานะจริงเทียบกับแผน การที่ Phase 8 และ 11 เกินงบรวม 40 ชม. ยังอยู่ในขอบเขตที่รับได้ | โครงงานเสร็จภายใน BAC 1,300 ชม. (EAC = 1,294 ชม.) |

---

## 15. Stakeholder Register

> **อ้างอิง:** SE 781 — Initiating Process Group (Identify Stakeholders)
> **Power/Interest Grid:** จัดกลุ่ม stakeholders ตามระดับอำนาจ (Power) และความสนใจ (Interest)

### 15.1 Stakeholder Identification

| ID | Stakeholder | บทบาท | Power | Interest | กลยุทธ์การจัดการ |
|----|------------|-------|-------|----------|----------------|
| STK-01 | ผศ.ดร.ภัทรหทัย ณ ลำพูน | อาจารย์ที่ปรึกษา (Advisor) | High | High | **Manage Closely** — รายงานความคืบหน้าสม่ำเสมอ, ขอ feedback ทุก milestone |
| STK-02 | nextzus (ผู้พัฒนา) | Developer / PM / Tester / CM | High | High | **Self-managed** — ใช้ EVM + ISO 29110 tracking |
| STK-03 | กรรมการสอบ | Thesis Committee | High | Medium | **Keep Satisfied** — เตรียมเอกสาร ISO ครบ, defense presentation ชัดเจน |
| STK-04 | Beginner Users | End user กลุ่ม 1 | Low | High | **Keep Informed** — UI ใช้งานง่าย, Welcome Overlay, Help system |
| STK-05 | Gamers | End user กลุ่ม 2 | Low | High | **Keep Informed** — COMPETITIVE profile, FPS gain display, risk badges |
| STK-06 | Power Users | End user กลุ่ม 3 | Low | Medium | **Monitor** — EXTREME profile, per-tweak control, export/import presets |
| STK-07 | CAMT / มช. | สถาบันการศึกษา | Medium | Low | **Keep Satisfied** — ปฏิบัติตามระเบียบวิทยานิพนธ์, ISO 29110 compliance |

### 15.2 Power/Interest Grid

```
          High Power
              │
    STK-03    │    STK-01, STK-02
  (Committee) │  (Advisor, Developer)
   Keep       │   Manage
   Satisfied  │   Closely
──────────────┼──────────────────
    STK-07    │    STK-04, STK-05
   (CAMT)     │  (Beginner, Gamer)
   Monitor    │   Keep Informed
              │        STK-06
              │    (Power User)
          Low Power
    Low Interest ──── High Interest
```

### 15.3 Communication Plan Summary

| Stakeholder | ช่องทาง | ความถี่ | เนื้อหาหลัก |
|------------|---------|---------|-------------|
| อาจารย์ที่ปรึกษา | ประชุมตัวต่อตัว / LINE | ทุก 2–4 สัปดาห์ | ความคืบหน้า, ปัญหา, ขออนุมัติ |
| กรรมการสอบ | เอกสาร thesis + defense | ตาม milestone | Thesis chapters, ISO documents |
| End users (ทุกกลุ่ม) | GitHub README, in-app Help | ต่อเนื่อง | User Manual, release notes |
| CAMT | ระบบส่ง thesis | ตาม deadline | Thesis document ฉบับสมบูรณ์ |

---

## 16. Correction Register (PM.O7)

> **อ้างอิง:** ISO/IEC 29110-5-1-2 PM.O7 — Correction Register
> บันทึก corrective actions ที่ดำเนินการเมื่อพบปัญหาหรือ non-conformance ระหว่างโครงงาน

| COR-ID | วันที่พบ | แหล่งที่มา | ปัญหาที่พบ | Corrective Action | สถานะ | ผลลัพธ์ |
|--------|---------|-----------|-----------|-------------------|-------|---------|
| COR-01 | 2026-01 | Code Review | GPUtil library หยุด maintain, ไม่รองรับ GPU ใหม่ | Refactor `system_info.py` ใช้ 3-strategy detection (WMI → Get-PhysicalDisk → psutil fallback) | ✅ Closed | ลบ dependency, เพิ่ม reliability (CR-002) |
| COR-02 | 2026-02 | Unit Testing | `profile_recommender.py` มี logic ซับซ้อนเกินไป, ทดสอบยาก | แยกเป็น `recommendation_service.py` (188 lines) ตาม SRP, เพิ่ม 18 dedicated tests | ✅ Closed | Coverage 92%, test isolation ดีขึ้น (Phase 11b) |
| COR-03 | 2026-03 | Security Audit | พบ 11 security-related defects ใน code review (hardcoded paths, missing input validation, unsafe subprocess calls) | แก้ไขทั้ง 11 จุด, เพิ่ม 160 security tests, สร้าง `BUG_FIX_REPORT_2026-03-24.md` | ✅ Closed | 28/28 security checklist items PASS (CR-004) |
| COR-04 | 2026-03 | SRS Review | SRS v2.x ไม่สะท้อน actual implementation (tweak counts, profile sizes เปลี่ยน) | อัปเดต SRS → v3.2 ให้ตรงกับ code จริง (56 tweaks, 14/44/56 profiles) | ✅ Closed | SRS-SDD-Code consistency verified |
| COR-05 | 2026-03 | V&V Review | E2E tests 64 ชุด skip ในสภาพแวดล้อมที่ไม่มี display | บันทึกเป็น known limitation, ทดสอบ manual แทนสำหรับ UI-dependent FRs | ⚠️ Open | Accepted risk — documented in Test Record §8 |
| COR-06 | 2026-04 | ISO Audit | User Manual v1.0 (~132 lines) ไม่ครอบคลุมฟีเจอร์ใหม่ (Welcome Overlay, Backup Center, Settings) | Expand User Manual → v3.0 (~450 lines) ครบทุก view + troubleshooting + FAQ | ✅ Closed | User Manual coverage ครบถ้วน |
| COR-07 | 2026-04 | Document Review | Traceability Record มี 7 FRs ที่ไม่มี automated tests | บันทึก justification ว่าเป็น hardware-dependent หรือ UI-only, ทดสอบ manual ทั้งหมด | ⚠️ Open | Accepted risk — 88.1% automated coverage ผ่านเป้า 85% |

### Correction Trend

| เดือน | พบใหม่ | ปิดแล้ว | คงเหลือ |
|-------|--------|---------|---------|
| ม.ค. 2026 | 1 (COR-01) | 0 | 1 |
| ก.พ. 2026 | 1 (COR-02) | 1 | 1 |
| มี.ค. 2026 | 3 (COR-03~05) | 3 | 1 |
| เม.ย. 2026 | 2 (COR-06~07) | 1 | 2 |
| **รวม** | **7** | **5** | **2 (open)** |

> **สรุป:** COR-05 และ COR-07 เป็น accepted risks ที่มี documented justification ไม่ต้องการ corrective action เพิ่มเติม

---

## 17. ประวัติการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายละเอียด |
|----------|--------|---------|------------|
| 1.0 | 2025-06-01 | nextzus | สร้างเอกสารเริ่มต้น — project info, objectives, scope, WBS, schedule, risk register |
| 2.0 | 2026-03-04 | nextzus | อัปเดตครั้งใหญ่: ETVX header, EVM metrics, CoSQ, risk updates (R-08~R-10), communication plan, SE academic references |
| 3.0 | 2026-04-06 | nextzus | เสริม SE academic content: PMBOK mapping, quality management plan, configuration management overview |
| 3.1 | 2026-04-12 | nextzus | เพิ่ม §14 Lessons Learned (5 หมวด), §15 Stakeholder Register (7 stakeholders + Power/Interest grid), §16 Correction Register PM.O7 (COR-01~07), §17 Revision History |

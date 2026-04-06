# 09 — แผนการกำหนดค่า (Configuration Management Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — PM.O2/PM.O3
> **Version:** 2.0
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่:** 2026-03-12
> **ETVX Compliance:** Entry = Project Plan approved; Task = PM.2.2 Configuration Management; Verification = CI audit checklist; Exit = Baselines established, CIs tracked
> **ทฤษฎีอ้างอิง:** SE 702 — Software Process Management (ICSA Framework, Baseline Management, FCA/PCA Audit)
> **เอกสารที่เกี่ยวข้อง:** Project Plan v3.0 (`01`), SRS v3.1 (`02`), SDD v3.2 (`03`), Test Plan v3.0 (`04`), Test Record v2.1 (`05`), Traceability v2.0 (`06`), Change Request v2.1 (`07`), Progress Status v3.0 (`08`)

---

## 1. ขอบเขต Configuration Management

### 1.1 วัตถุประสงค์
1. ระบุ Configuration Items (CI) ทั้งหมดในโครงงาน
2. กำหนดนโยบาย versioning, branching, baseline
3. กำหนดสิทธิ์การเข้าถึงและแก้ไข
4. รักษา repository integrity ตลอดโครงงาน

### 1.2 กรอบทฤษฎี ICSA (SE 702)

Configuration Management (CM) ประกอบด้วย 4 กิจกรรมหลัก ตามกรอบ **ICSA** (Pressman & Maxim, 2020):

| กิจกรรม | วัตถุประสงค์ | Section ที่เกี่ยวข้อง |
|---------|------------|---------------------|
| **Identification** | ระบุ Configuration Items (CI) ทั้งหมด กำหนด naming convention และ priority | §2 |
| **Control** | ควบคุมการเปลี่ยนแปลง CI ผ่าน change control process — approve/reject | §3 (Version Control), อ้างอิง `07-Change-Request.md` |
| **Status Accounting** | บันทึกสถานะของ CI ทุกเวอร์ชัน ติดตาม baseline และ milestone | §7 |
| **Audit** | ตรวจสอบว่า CI ตรงกับ baseline ที่กำหนด ผ่าน FCA/PCA | §8 |

```
   Identification ──► Control ──► Status Accounting ──► Audit
        │                │               │                │
   ระบุ 34 CIs     4 CRs ผ่าน      Version tracking    FCA + PCA
   Naming conv.    Change Control   9 Baselines         8 audit items
```

**Baseline** = จุดอ้างอิงที่ "freeze" configuration ณ เวลาหนึ่ง — การเปลี่ยนแปลงหลัง baseline ต้องผ่าน change control process (ดู Section 3.4)

---

## 2. Configuration Items (CI)

### 2.1 CI Naming Convention

```
CI-{CATEGORY}-{NUMBER}

CATEGORY:
  CORE  = Python core modules (business logic)
  GUI   = GUI views/components (presentation layer)
  BAT   = Batch scripts (optimization engine)
  TEST  = Test files (quality assurance)
  DOC   = Documentation (ISO 29110 WPs, thesis, research)
  DEP   = Dependencies (requirements files)
```

### 2.2 Priority Classification

| Priority | จำนวน | เกณฑ์การจัดลำดับ |
|----------|-------|----------------|
| **สูง** | 18 CIs | Core modules, safety-critical components, test infrastructure |
| **ปานกลาง** | 10 CIs | Supporting modules, documentation, secondary views |
| **ต่ำ** | 6 CIs | Configuration files, helper modules |

### 2.3 Source Code CIs

| CI-ID        | ประเภท        | ที่ตั้ง                                          | LOC (est.) | ความสำคัญ | หมายเหตุ                                      |
| ------------ | ------------- | ------------------------------------------------ | ---------- | --------- | --------------------------------------------- |
| CI-CORE-01   | Python Module | `clutchg/src/core/tweak_registry.py`             | 1013       | สูง       | Central tweak database, 48 tweaks             |
| CI-CORE-02   | Python Module | `clutchg/src/core/profile_manager.py`            | 528        | สูง       | Profile orchestration                         |
| CI-CORE-03   | Python Module | `clutchg/src/core/flight_recorder.py`            | 616        | สูง       | Change tracking + rollback (rewritten CR-004) |
| CI-CORE-04   | Python Module | `clutchg/src/core/backup_manager.py`             | 373        | สูง       | Backup + restore points                       |
| CI-CORE-05   | Python Module | `clutchg/src/core/system_info.py`                | 381        | ปานกลาง   | HW detection                                  |
| CI-CORE-06   | Python Module | `clutchg/src/core/batch_parser.py`               | 450        | ปานกลาง   | .bat parsing                                  |
| CI-CORE-07   | Python Module | `clutchg/src/core/batch_executor.py`             | 200        | ปานกลาง   | .bat execution                                |
| CI-CORE-08   | Python Module | `clutchg/src/core/benchmark_database.py`         | 450        | ปานกลาง   | HW scoring                                    |
| CI-CORE-09   | Python Module | `clutchg/src/core/config.py`                     | 120        | ต่ำ       | App config                                    |
| CI-CORE-10   | Python Module | `clutchg/src/core/help_manager.py`               | 100        | ต่ำ       | Help content                                  |
| CI-GUI-01    | Python Module | `clutchg/src/app_minimal.py`                     | 324        | สูง       | Main controller                               |
| CI-GUI-02    | Python Module | `clutchg/src/gui/views/scripts_minimal.py`       | ~1800      | สูง       | Largest view (63.5KB)                         |
| CI-GUI-03    | Python Module | `clutchg/src/gui/views/backup_restore_center.py` | ~1000      | สูง       | Timeline + rollback                           |
| CI-GUI-04    | Python Module | `clutchg/src/gui/views/dashboard_minimal.py`     | ~730       | ปานกลาง   | System info display                           |
| CI-BAT-01~09 | Batch Scripts | `clutchg/src/core/*.bat`                         | 9 files    | สูง       | System optimization scripts                   |

### 2.4 Test CIs

| CI-ID | ประเภท | ที่ตั้ง | Tests | ความสำคัญ |
|-------|--------|-------|-------|----------|
| CI-TEST-01 | Pytest Config | `clutchg/tests/conftest.py` | 12 fixtures | สูง |
| CI-TEST-02 | Unit Tests | `clutchg/tests/unit/` | 285 tests, 12 files | สูง |
| CI-TEST-03 | Integration Tests | `clutchg/tests/integration/` | 23 tests, 5 files | สูง |
| CI-TEST-04 | E2E Tests | `clutchg/tests/e2e/` | 64 tests | ปานกลาง |
| CI-TEST-05 | Security Audit Tests | `clutchg/tests/unit/test_admin.py`, `test_backup_manager.py`, `test_flight_recorder.py`, `test_tweak_registry_integrity.py`, `test_help_system.py` | 160 tests (5 files) | สูง |

### 2.5 Documentation CIs

| CI-ID | ประเภท | ที่ตั้ง | Pages | ความสำคัญ |
|-------|--------|-------|-------|----------|
| CI-DOC-01 | ISO29110 WPs | `docs/iso29110-clutchg/` | 10 documents | สูง |
| CI-DOC-02 | Thesis | `thesis/THESIS_DOCS/` | 7 chapters | สูงมาก |
| CI-DOC-03 | Research | `docs/` | 15+ documents | ปานกลาง |
| CI-DOC-04 | User Guides | `clutchg/README.md`, `QUICKSTART.md` | 2 files | ปานกลาง |

### 2.6 Dependencies CI

| CI-ID | ประเภท | ที่ตั้ง | ความสำคัญ |
|-------|--------|-------|----------|
| CI-DEP-01 | Requirements | `clutchg/requirements.txt` | สูง |
| CI-DEP-02 | Test Requirements | `clutchg/requirements-dev.txt` | ปานกลาง |

**รวม CI ทั้งหมด: 34 items** (CORE=10, GUI=4, BAT=9, TEST=5, DOC=4, DEP=2)

---

## 3. Version Control

### 3.1 Repository Structure

```
bat/ (Git root)
├── clutchg/                    # Main ClutchG application
│   ├── src/                    # Source code
│   │   ├── core/               # Business logic (13 modules)
│   │   ├── gui/                # GUI (views + components)
│   │   └── utils/              # Utilities (logger, etc.)
│   ├── tests/                  # Test suite
│   ├── config/                 # App configuration
│   ├── data/                   # Runtime data (gitignored)
│   └── requirements.txt
├── src/                        # Batch optimizer scripts
├── docs/                       # Research + ISO29110 docs
├── thesis/                     # Thesis writing
│   └── THESIS_DOCS/            # Thesis chapters
├── research/                   # Research material
│   └── notion/                 # Notion export (reference)
└── .gitignore
```

### 3.2 Branching Strategy
- **main** — stable release (tagged: v1.0, v2.0)
- **develop** — development integration
- **feature/* ** — feature branches (e.g., `feature/restore-center`)
- **docs/* ** — documentation branches

### 3.3 Versioning Policy

| Component | Format | ตัวอย่าง | เงื่อนไข Increment |
|-----------|--------|---------|------------------|
| Application | SemVer (MAJOR.MINOR.PATCH) | v2.0.0 | MAJOR: architecture change, MINOR: feature, PATCH: bugfix |
| ISO29110 Docs | Version number | v3.0 | Major revision = +1.0 |
| Thesis | Draft number | Draft 3.0 | Per revision |

### 3.4 Baselines

| Baseline | วันที่ | เนื้อหา | Tag |
|----------|------|---------|-----|
| BL-1: Research Complete | 2025-02-28 | 28 repos analyzed, taxonomy created | v0.1 |
| BL-2: Architecture Complete | 2025-04-30 | Hybrid architecture finalized | v0.5 |
| BL-3: Batch Optimizer Complete | 2025-06-30 | All .bat scripts + profiles | v1.0 |
| BL-4: GUI Alpha | 2025-08-31 | Core managers + basic views | v1.5 |
| BL-5: GUI Beta (Safety) | 2025-09-30 | Backup + FlightRecorder | v1.7 |
| BL-6: GUI RC (All views) | 2025-10-31 | 6 views + tests | v2.0-rc |
| BL-7: Release | 2025-12-31 | Full app + Restore Center | v2.0 |
| BL-8: Documentation | 2026-03-04 | ISO29110 WPs v3.0 + Thesis Draft 3.0 | v2.0.1 |
| BL-9: Security Audit Complete | 2026-03-12 | 28 audit items resolved, 285 unit tests, GPUtil removed | v2.0.2 |

---

## 4. Access Control

| ที่ตั้ง | สิทธิ์ | ผู้มีสิทธิ์ |
|--------|-------|-----------|
| Git Repository (main) | Read + Write | nextzus |
| Git Repository (main) | Read | Advisor |
| data/ (runtime) | .gitignored | — |
| data/backups/ | Write (app) | ClutchG process |
| data/flight_recorder/ | Write (app) | ClutchG process |

---

## 5. Build & Release

### 5.1 Development Build
```powershell
cd clutchg
pip install -r requirements.txt
python src/main.py
```

### 5.2 Test Execution
```powershell
pytest tests/ -v --cov=src/core --cov-report=html
```

### 5.3 Release Checklist
- [ ] All P0 (safety) tests pass
- [ ] Coverage ≥ 70%
- [ ] ISO29110 WPs updated
- [ ] README updated
- [ ] Git tag created
- [ ] Advisor review complete

---

## 6. Continuous Integration (CI/CD)

### 6.1 Pipeline Overview

| รายการ | รายละเอียด |
|--------|-----------|
| Platform | GitHub Actions |
| Workflow file | `.github/workflows/ci.yml` |
| Runner | `windows-latest` (จำเป็นเนื่องจาก dependencies: `pywin32`, `wmi`, `psutil`) |
| Trigger | Push ไปยัง `main`/`develop`, Pull Request ไปยัง `main` |
| Path filter | เฉพาะการเปลี่ยนแปลงภายใน `clutchg/` และ `.github/workflows/` |

### 6.2 Jobs & Scope

| Job | Scope | Markers | หมายเหตุ |
|-----|-------|---------|---------|
| Unit Tests | `tests/unit/` | `-m unit` | 259 เมธอด, coverage report generated |
| Integration Tests | `tests/integration/` | `-m integration` | 23 เมธอด |

### 6.3 Excluded from CI

| ประเภท | เหตุผล |
|--------|-------|
| E2E Tests (`-m e2e`) | ต้องการ desktop session + CustomTkinter GUI display ซึ่ง CI runner ไม่มี |
| Admin Tests (`-m admin`) | ต้องการสิทธิ์ Administrator เต็มรูปแบบ |

### 6.4 Artifacts

| Artifact | Path | Retention |
|----------|------|-----------|
| HTML Coverage Report | `clutchg/htmlcov/` | 14 วัน |
| JUnit XML Results | `clutchg/test-results/` | 14 วัน |

---

## 7. Status Accounting (ICSA — S)

> **ICSA Activity:** Status Accounting — บันทึกสถานะของ CI ทุกเวอร์ชัน ติดตาม baseline, milestone, และ work product versions

### 7.1 Work Product Version Tracking

| Work Product | Version History | Current | ไฟล์ | Lines (est.) |
|-------------|----------------|---------|------|-------------|
| Project Plan | v1.0 → v2.0 → v3.0 | **v3.0** | `01-Project-Plan.md` | ~470 |
| SRS | v1.0 → v2.0 → v3.0 → v3.1 | **v3.1** | `02-SRS.md` | ~604 |
| SDD | v1.0 → v2.0 → v3.0 → v3.2 | **v3.2** | `03-SDD.md` | ~610 |
| Test Plan | v1.0 → v2.0 → v3.0 | **v3.0** | `04-Test-Plan.md` | ~543 |
| Test Record | v1.0 → v2.0 → v2.1 | **v2.1** | `05-Test-Record.md` | ~474 |
| Traceability Record | v1.0 → v2.0 | **v2.0** | `06-Traceability-Record.md` | ~230 |
| Change Request | v1.0 → v2.0 → v2.1 | **v2.1** | `07-Change-Request.md` | ~460 |
| Progress Status | v1.0 → v2.0 → v2.3 → v3.0 | **v3.0** | `08-Progress-Status-Record.md` | ~250 |
| Configuration Plan | v1.0 → v2.0 | **v2.0** | `09-Configuration-Plan.md` | (this doc) |
| User Manual | v1.0 | **v1.0** | `10-User-Manual.md` | ~132 |

### 7.2 Milestone Status

| Milestone | Plan | Actual | Variance | Baseline Tag |
|-----------|------|--------|----------|-------------|
| M1: Research Complete | Feb 2025 | Feb 2025 | On time | BL-1 (v0.1) |
| M2: Architecture Approved | Apr 2025 | Apr 2025 | On time | BL-2 (v0.5) |
| M3: Batch Optimizer v1.0 | Jun 2025 | Jun 2025 | On time | BL-3 (v1.0) |
| M4: GUI Alpha | Aug 2025 | Aug 2025 | On time | BL-4 (v1.5) |
| M5: Safety System Complete | Sep 2025 | Sep 2025 | On time | BL-5 (v1.7) |
| M6: All Views Complete | Oct 2025 | Oct 2025 | On time | BL-6 (v2.0-rc) |
| M7: Test Suite Pass | Nov 2025 | Nov 2025 | On time | — |
| M8: Full Release | Dec 2025 | Dec 2025 | On time | BL-7 (v2.0) |
| M9: Documentation Complete | Mar 2026 | Mar 2026 | On time | BL-8 (v2.0.1) |
| M10: Security Audit Complete | Mar 2026 | Mar 2026 | On time | BL-9 (v2.0.2) |

### 7.3 Source Code Metrics

| Metric | ค่า |
|--------|-----|
| Source Code (Python) | ~12,000 lines (clutchg/src/) |
| Source Code (Batch) | ~3,500 lines (src/) |
| Test Code | ~8,000 lines (clutchg/tests/) |
| Documentation | ~5,200 lines (10 ISO WPs + appendix) |
| Total Project | ~56,000 lines (all files) |
| Test Cases | 445 collected (285 unit, 23 integration, 64 E2E, 73 skipped) |
| Open Defects | 0 HIGH, 0 MEDIUM |

**อ้างอิง:** `08-Progress-Status-Record.md` §3-§5

---

## 8. Configuration Audit (ICSA — A)

> **ICSA Activity:** Audit — ตรวจสอบว่า CI ตรงกับ baseline ที่กำหนด แบ่งเป็น Functional Configuration Audit (FCA) และ Physical Configuration Audit (PCA)

### 8.1 Functional Configuration Audit (FCA)

**วัตถุประสงค์:** ตรวจสอบว่าซอฟต์แวร์ทำงานตามที่ระบุใน SRS — ผลลัพธ์ตรงกับ requirements

| เกณฑ์ | วิธีตรวจ | ผลลัพธ์ | สถานะ |
|-------|---------|---------|-------|
| Functional Requirements ครบถ้วน | Traceability Matrix (`06`) | 59/67 FRs traced to test cases (88.1%) | PASS |
| Test suite passes | `pytest` | 308 passed, 0 failed (unit + integration) | PASS |
| Coverage meets target | `.coveragerc` (target ≥ 60%) | ~65%+ achieved | PASS |
| Safety requirements verified | Security audit tests | 160 security tests, 0 failures | PASS |
| No HIGH/MEDIUM open defects | Defect tracking | 0 HIGH, 0 MEDIUM open | PASS |

**อ้างอิง:** `06-Traceability-Record.md`, `05-Test-Record.md`

### 8.2 Physical Configuration Audit (PCA)

**วัตถุประสงค์:** ตรวจสอบว่า deliverables ตรงกับ design documentation — โครงสร้างจริงสอดคล้องกับ SDD

| เกณฑ์ | วิธีตรวจ | ผลลัพธ์ | สถานะ |
|-------|---------|---------|-------|
| Source files ตรง SDD | Manual review vs SDD §2 | Module structure matches architecture diagram | PASS |
| Build produces executable | `python build.py` | `ClutchG.exe` generated successfully | PASS |
| Documents match current code | Version comparison | All 10 WPs updated (see §7.1) | PASS |
| Dependencies match requirements.txt | `pip freeze` comparison | All packages listed, no extras | PASS |
| CI naming consistent | CI-ID audit | 34 CIs, no duplicates, all categorized | PASS |
| Git repository intact | `git fsck` | No corrupted objects | PASS |

**อ้างอิง:** `03-SDD.md` §2, `requirements.txt`

### 8.3 Audit Checklist Summary

| # | รายการตรวจ | FCA/PCA | สถานะ |
|---|-----------|---------|-------|
| 1 | ทุก CI มี ID ที่ไม่ซ้ำกัน | PCA | PASS |
| 2 | ทุก CI ระบุ priority classification | PCA | PASS |
| 3 | ทุก Change Request มี impact analysis | FCA | PASS |
| 4 | Version ของเอกสารเป็นปัจจุบัน | PCA | PASS |
| 5 | Git repository intact (no corruption) | PCA | PASS |
| 6 | Build reproducible | PCA | PASS |
| 7 | Test suite passes (308 tests) | FCA | PASS |
| 8 | No uncommitted critical changes | PCA | PASS |
| 9 | FRs traced to test cases (88.1%) | FCA | PASS |
| 10 | Safety tests pass (160 tests) | FCA | PASS |

**ผลการ Audit: 10/10 PASS** — ไม่พบ non-conformance

---

## 9. ICSA Mapping กับ Git Operations

| ICSA Activity | Git Operation | ตัวอย่างใน ClutchG |
|--------------|-------------|-------------------|
| **Identification** | File naming + `.gitignore` | CI naming convention (`CI-{CAT}-{NUM}`), `.gitignore` excludes `thesis/`, `data/` |
| **Control** | `git add`, `git commit`, CR process | Commit แต่ละ change แยก, 4 CRs ผ่าน formal change control |
| **Status Accounting** | `git log`, `git diff`, `git tag` | Version tracking ผ่าน tags (v0.1 → v2.0.2), 9 baselines |
| **Audit** | `git diff --stat`, `git show`, `git fsck` | Compare current vs baseline, integrity check |

---

## 10. ICSA Compliance Summary

| ICSA Activity | ดำเนินการ? | หลักฐาน | SE 702 Score |
|--------------|-----------|---------|-------------|
| **Identification** | Yes | 34 CIs ระบุครบ พร้อม naming convention + priority classification | Full |
| **Control** | Yes | 4 CRs ผ่าน formal change control, CCB process (ดู `07-Change-Request.md`) | Full |
| **Status Accounting** | Yes | Progress Status Record v3.0, version tracking ทุก WP, 10 milestones tracked | Full |
| **Audit** | Yes | FCA (test pass + traceability) + PCA (build verification + structure check), 10/10 PASS | Full |

### จุดแข็งและข้อจำกัด

| จุดแข็ง | ข้อจำกัด |
|---------|---------|
| CI ระบุครบ 34 items พร้อม priority | Solo developer — ไม่มี peer review สำหรับ commits |
| ISO 29110 CM plan formal ครบ ICSA | Single-branch workflow — ไม่มี feature branch isolation |
| Change Requests มี impact analysis | ไม่มี automated version bumping |
| FCA/PCA audit ผ่านครบ 10 ข้อ | CI/CD ครอบคลุมเฉพาะ unit + integration (E2E ต้อง manual) |
| 9 baselines tagged ใน Git | — |

---

## 11. Revision History

| Version | วันที่ | ผู้แก้ไข | รายละเอียดการเปลี่ยนแปลง |
|---------|-------|---------|------------------------|
| v1.0 | 2026-03-12 | nextzus | ฉบับแรก — CI inventory (33 items), version control, access control, build/release, CI/CD |
| v2.0 | 2026-04-06 | nextzus | เพิ่ม ICSA framework (§1.2), CI naming convention (§2.1), priority classification (§2.2), CI count แก้เป็น 34, Status Accounting (§7), FCA/PCA Audit (§8), ICSA-to-Git mapping (§9), ICSA compliance summary (§10), cross-refs to all WPs |

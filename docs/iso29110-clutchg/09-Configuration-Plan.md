# 09 — แผนการกำหนดค่า (Configuration Management Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — PM.O2/PM.O3
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่:** 2026-03-12

---

## 1. ขอบเขต Configuration Management

### 1.1 วัตถุประสงค์
1. ระบุ Configuration Items (CI) ทั้งหมดในโครงงาน
2. กำหนดนโยบาย versioning, branching, baseline
3. กำหนดสิทธิ์การเข้าถึงและแก้ไข
4. Contact repository integrity ตลอดโครงงาน

---

## 2. Configuration Items (CI)

### 2.1 Source Code CIs

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

### 2.2 Test CIs

| CI-ID | ประเภท | ที่ตั้ง | Tests | ความสำคัญ |
|-------|--------|-------|-------|----------|
| CI-TEST-01 | Pytest Config | `clutchg/tests/conftest.py` | 12 fixtures | สูง |
| CI-TEST-02 | Unit Tests | `clutchg/tests/unit/` | 285 tests, 12 files | สูง |
| CI-TEST-03 | Integration Tests | `clutchg/tests/integration/` | 23 tests, 5 files | สูง |
| CI-TEST-04 | E2E Tests | `clutchg/tests/e2e/` | 64 tests | ปานกลาง |
| CI-TEST-05 | Security Audit Tests | `clutchg/tests/unit/test_admin.py`, `test_backup_manager.py`, `test_flight_recorder.py`, `test_tweak_registry_integrity.py`, `test_help_system.py` | 160 tests (5 files) | สูง |

### 2.3 Documentation CIs

| CI-ID | ประเภท | ที่ตั้ง | Pages | ความสำคัญ |
|-------|--------|-------|-------|----------|
| CI-DOC-01 | ISO29110 WPs | `docs/iso29110-clutchg/` | 10 documents | สูง |
| CI-DOC-02 | Thesis | `THESIS_DOCS/` | 7 chapters | สูงมาก |
| CI-DOC-03 | Research | `docs/` | 15+ documents | ปานกลาง |
| CI-DOC-04 | User Guides | `clutchg/README.md`, `QUICKSTART.md` | 2 files | ปานกลาง |

### 2.4 Dependencies CI

| CI-ID | ประเภท | ที่ตั้ง | ความสำคัญ |
|-------|--------|-------|----------|
| CI-DEP-01 | Requirements | `clutchg/requirements.txt` | สูง |
| CI-DEP-02 | Test Requirements | `clutchg/requirements-dev.txt` | ปานกลาง |

**รวม CI ทั้งหมด: 33 items**

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
├── THESIS_DOCS/                # Thesis chapters
├── notion/                     # Notion export (reference)
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

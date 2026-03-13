# 04 — แผนการทดสอบ (Test Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O5 (Software Testing)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 2.0 | **วันที่:** 2026-03-04 | **อ้างอิง SRS:** v3.0
> **อ้างอิง:** IEEE 829-2008, ISTQB Foundation

---

## 1. ขอบเขตการทดสอบ (Test Scope)

### 1.1 วัตถุประสงค์
1. ยืนยันว่า functional requirements (60+ FRs) ทำงานถูกต้อง
2. ยืนยันว่า safety mechanisms (backup, rollback) ทำงานครบวงจร
3. ตรวจสอบว่า UI navigation, display, interaction ทำงานปกติ
4. วัด code coverage ≥ 70%

### 1.2 สิ่งที่ทดสอบ (Items Under Test)
| Component | ไฟล์ | LOC (est.) | Priority |
|-----------|------|-----------|----------|
| TweakRegistry | `core/tweak_registry.py` | ~1013 | สูง |
| ProfileManager | `core/profile_manager.py` | ~528 | สูง |
| FlightRecorder | `core/flight_recorder.py` | ~589 | สูง |
| BackupManager | `core/backup_manager.py` | ~373 | สูง |
| SystemDetector | `core/system_info.py` | ~381 | ปานกลาง |
| BatchParser | `core/batch_parser.py` | ~450 | ปานกลาง |
| BatchExecutor | `core/batch_executor.py` | ~200 | ปานกลาง |
| ConfigManager | `core/config.py` | ~120 | ต่ำ |
| HelpManager | `core/help_manager.py` | ~100 | ต่ำ |
| BenchmarkDB | `core/benchmark_database.py` | ~450 | ปานกลาง |

### 1.3 สิ่งที่ไม่ทดสอบ
- Batch script (.bat) internals — ทดสอบเฉพาะ parsing + execution interface
- Hardware-specific behavior — ใช้ mock data
- ผลลัพธ์ FPS จริง — อยู่นอกขอบเขตของ unit/integration test

---

## 2. กลยุทธ์การทดสอบ (Test Strategy)

### 2.1 Test Pyramid

```
              ╱╲
             ╱E2E╲                64 tests (pywinauto)
            ╱──────╲              Full app lifecycle
           ╱Integration╲         23 tests (pytest)
          ╱──────────────╲        Multi-component workflows
         ╱  Unit Tests    ╲      285 tests (pytest)
        ╱──────────────────╲     Isolated function tests
       ╱  Static Analysis   ╲   Type hints + linting
      ╱──────────────────────╲
```

### 2.2 Risk-Based Testing Priority
เนื่องจาก ClutchG เปลี่ยนแปลง Windows system settings:

| Priority | Area | เหตุผล |
|----------|------|-------|
| P0 (Critical) | Safety: Backup → Apply → Rollback | ถ้าพังไม่ได้ rollback = ผู้ใช้เสียหาย |
| P1 (High) | Core Logic: Profile loading, tweak execution | Business logic หลัก |
| P2 (Medium) | System Detection: CPU/GPU/RAM accuracy | ผลต่อ recommendation |
| P3 (Low) | UI: Navigation, display, theme | ไม่กระทบ data integrity |

### 2.3 Test Types

| ประเภท | เครื่องมือ | ขอบเขต | Isolation |
|--------|----------|--------|-----------|
| **Unit** | pytest | Single function/class | Full isolation (mock I/O) |
| **Integration** | pytest | Multi-component workflow | Partial (temp dir, mock registry) |
| **E2E** | pywinauto + pytest | Full application | Real app, mock admin |
| **Manual** | Human tester | Visual, UX | Real system |

---

## 3. สภาพแวดล้อมการทดสอบ (Test Environment)

### 3.1 Hardware/Software

| รายการ | ข้อกำหนด |
|--------|---------|
| OS | Windows 10 22H2 / Windows 11 23H2 |
| Python | 3.11+ (ทดสอบกับ 3.12, 3.14 nightly) |
| RAM | ≥ 8 GB |
| Admin | ไม่จำเป็นสำหรับ unit/integration (มี mock) |

### 3.2 Test Framework Configuration

`pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    unit: Unit tests (fast, no external deps)
    integration: Integration tests (business logic workflows)
    e2e: End-to-end UI tests (full application)
    admin: Tests requiring administrator privileges
    slow: Tests that take >10 seconds
addopts = --strict-markers
```

### 3.3 Test Fixtures (`conftest.py` — 272 lines)

| Fixture | Scope | หน้าที่ |
|---------|-------|---------|
| `project_root` | session | ให้ path ของ project root |
| `src_dir` | session | ให้ path ของ source directory |
| `test_config_dir` | session | สร้าง temp config dir (isolated) |
| `app_path` | session | Path to main.py |
| `temp_output_dir` | function | Temp dir สำหรับ test output |
| `screenshot_dir` | function | Dir สำหรับ screenshot on failure |
| `log_dir` | function | Dir สำหรับ test logs |
| `test_timestamp` | function | Timestamp string |
| `require_admin` | function | Skip test ถ้าไม่ได้ admin |
| `test_config` | function | Default test config dict |
| `screenshot_on_failure` | function (autouse) | Auto-capture screenshot on E2E failure |

### 3.4 Screenshot on Failure (Automatic)
```python
# conftest.py — pytest hook
@pytest.fixture(autouse=True)
def screenshot_on_failure(request, screenshot_dir, test_timestamp):
    yield
    if test failed and "app_instance" in fixtures:
        window.capture_as_image().save(f"failure_{test_name}_{timestamp}.png")
```

---

## 4. Test Cases — รายละเอียด

### 4.1 Unit Tests (`tests/unit/`)

#### UT-PM: Profile Manager Tests (`test_profile_manager.py` — 6.1KB)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-PM-01 | test_profile_loading | FR-PM-01 | โหลด profiles ทั้ง 3 ตัว | profiles dict มี 3 keys |
| UT-PM-02 | test_safe_profile_exists | FR-PM-02 | SAFE profile มี tweaks | SAFE.scripts ≥ 1 |
| UT-PM-03 | test_competitive_profile | FR-PM-03 | COMPETITIVE มี tweaks > SAFE | COMP.scripts > SAFE.scripts |
| UT-PM-04 | test_extreme_profile | FR-PM-04 | EXTREME = ทั้งหมด | EXTREME.scripts ≥ COMP.scripts |
| UT-PM-05 | test_profile_risk_levels | FR-PM-05 | Risk level ตรง | SAFE=LOW, COMP=MEDIUM, EXTREME=HIGH |
| UT-PM-06 | test_custom_preset_save | FR-PM-08 | Save + load custom preset | Preset มี tweak_ids ครบ |
| UT-PM-07 | test_script_verification | FR-PM-11 | verify_scripts() | True if all scripts exist |

#### UT-BP: Batch Parser Tests (`test_batch_parser.py` — 7.7KB)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-BP-01 | test_parse_basic | FR-BS-01 | Parse .bat ได้ | Return BatchScript objects |
| UT-BP-02 | test_parse_comments | FR-BS-01 | Skip comments (::, REM) | Comments ไม่อยู่ใน commands |
| UT-BP-03 | test_parse_registry | FR-BS-01 | Extract reg add commands | Registry commands ถูก |
| UT-BP-04 | test_parse_service | FR-BS-01 | Extract sc config commands | Service commands ถูก |
| UT-BP-05 | test_parse_empty | FR-BS-01 | Handle empty file | Return empty list |
| UT-BP-06 | test_parse_malformed | FR-BS-04 | Handle broken syntax | Error, no crash |

#### UT-SD: System Detection Tests (`test_system_detection.py` — 5.6KB)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-SD-01 | test_cpu_detection | FR-SD-01 | CPU name + cores | name ≠ "Unknown", cores > 0 |
| UT-SD-02 | test_gpu_detection | FR-SD-02 | GPU name | name ≠ "Unknown" |
| UT-SD-03 | test_ram_detection | FR-SD-03 | RAM total | total_gb ≥ 4 |
| UT-SD-04 | test_score_range | FR-SD-05 | Total score 0-100 | 0 ≤ score ≤ 100 |
| UT-SD-05 | test_tier_calculation | FR-SD-06 | Tier from score | tier ∈ {entry,mid,high,enthusiast} |
| UT-SD-06 | test_form_factor | FR-SD-08 | Detect desktop/laptop | result ∈ {desktop, laptop} |

#### UT-AC: Action Catalog Tests (`test_action_catalog.py` — 3KB)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-AC-01 | test_catalog_load | FR-TW-01 | Load catalog | catalog ≠ None |
| UT-AC-02 | test_catalog_validate | FR-TW-02 | Validate entries | errors = [] |

#### UT-BM: Benchmark Database Tests (`test_benchmark_database.py` — 11.9KB)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-BM-01 | test_benchmark_load | FR-SD-05 | Load DB | DB ≠ None |
| UT-BM-02 | test_cpu_score_query | FR-SD-05 | Query CPU score | 0 ≤ score ≤ 30 |
| UT-BM-03 | test_gpu_score_query | FR-SD-05 | Query GPU score | 0 ≤ score ≤ 30 |
| UT-BM-04 | test_score_range | FR-SD-05 | Boundary check | Scores in valid range |
| UT-BM-05 | test_categories | FR-SD-05 | Category listing | ≥ 1 category |

#### UT-FR: Flight Recorder Tests (`test_flight_recorder.py` — 36 tests)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-FR-01~36 | TestFlightRecorder, TestTweakChange, TestSystemSnapshot | FR-SF-05~12 | Full FlightRecorder lifecycle, serialization, rollback generation | All scenarios pass |

#### UT-BK: Backup Manager Tests (`test_backup_manager.py` — 35 tests)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-BK-01~35 | TestBackupManager, TestBackupInfo | FR-SF-01~04 | create, list, delete, restore, cleanup, BackupInfo serialization | All pass |

#### UT-TW: Tweak Registry Integrity Tests (`test_tweak_registry_integrity.py` — 61 tests)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-TW-01~61 | TestTweakRegistryIntegrity, parametrized | FR-TW-01~07, NFR-01~03 | 48 tweaks complete, risk distribution, dangerous patterns absent from bat files | All pass |

#### UT-AD: Admin Utils Tests (`test_admin.py` — 16 tests)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-AD-01~16 | TestAdminUtils | NFR-01 | is_admin(), request_elevation(), subprocess quoting, logger usage | All pass |

#### UT-HS: Help System Tests (`test_help_system.py` — 12 tests)

| Test ID | Test Function | FR | คำอธิบาย | Expected |
|---------|--------------|-----|---------|----------|
| UT-HS-01~12 | TestHelpSystem | FR-UI-05, NFR-06 | Help content load, bilingual, search | All pass |

### 4.2 Integration Tests (`tests/integration/`)

| Test ID | ไฟล์ | FR | คำอธิบาย | Workflow |
|---------|------|-----|---------|---------|
| IT-BR-01 | test_backup_restore.py | FR-SF-01~04 | Backup → Apply → Restore cycle | Create backup → verify files → restore → verify restored |
| IT-BR-02 | test_backup_restore.py | FR-SF-03 | Restore point creation | Call _create_restore_point → verify |
| IT-CI-01 | test_clutchg_integration.py | FR-PM-06 | Profile apply integration | Load profile → execute → verify |
| IT-CI-02 | test_config_integration.py | FR-UI-06 | Config save/load cycle | Save config → reload → verify values |
| IT-CI-03 | test_config_integration.py | FR-UI-06 | Theme persistence | Switch theme → save → reload → verify |
| IT-FR-01 | test_flight_recorder_integration.py | FR-SF-05~06 | Flight recorder full workflow | start → record N changes → finish → load → verify |
| IT-FR-02 | test_flight_recorder_integration.py | FR-SF-07 | Rollback command generation | Record change → verify rollback_command format |
| IT-FR-03 | test_flight_recorder_integration.py | FR-SF-09 | Generate rollback .bat | Generate script → verify .bat content |
| IT-HS-01 | test_help_system_integration.py | FR-UI-05 | Help content loading | Load JSON → verify structure |
| IT-HS-02 | test_help_system_integration.py | NFR-06 | Bilingual content | Access en + th keys |

### 4.3 E2E Tests (`tests/e2e/`)

| Test ID | ไฟล์ | FR | คำอธิบาย | Steps |
|---------|------|-----|---------|-------|
| E2E-NAV-01~06 | test_navigation.py | FR-UI-01~06 | View navigation | Launch → click sidebar → verify view |
| E2E-NAV-07~10 | test_navigation_comprehensive.py | FR-UI-07~10 | Full navigation | All views + transitions |
| E2E-PRF-01 | test_profiles.py | FR-PM-01~03 | Profile display | Launch → Profiles → verify 3 cards |
| E2E-PRF-02 | test_profiles.py | FR-UI-08 | Risk badge display | Verify 🟢🟡🔴 badges |
| E2E-PRF-03 | test_profiles.py | FR-PM-06 | Profile apply flow | Select → Apply → verify (admin) |
| E2E-SET-01~03 | test_settings.py | FR-UI-06 | Settings workflow | Theme/accent/language change |
| E2E-SCR-01 | test_scripts.py | FR-UI-03 | Scripts category display | Verify 10 categories |
| E2E-SCR-02 | test_scripts.py | FR-TW-05 | Scripts apply flow | Select tweaks → Apply (admin) |

---

## 5. เกณฑ์ผ่าน/ไม่ผ่าน (Pass/Fail Criteria)

### 5.1 Entry Criteria (เริ่มทดสอบ)
1. Source code compile/import ได้ไม่มี error
2. Dependencies ติดตั้งครบ (requirements.txt)
3. Test fixtures ทำงาน (conftest.py import ได้)

### 5.2 Exit Criteria (ผ่านการทดสอบ)

| ระดับ | เกณฑ์ Pass | เกณฑ์ Fail |
|-------|---------|----------|
| **Unit** | Pass rate ≥ 95%, Coverage ≥ 70% | Pass rate < 90% |
| **Integration** | Pass rate = 100% สำหรับ P0 (Safety) paths | P0 test fail ใดๆ |
| **E2E** | Critical paths (NAV, PRF-01) ผ่าน | Navigation/display broken |
| **Overall** | No HIGH severity defects open | Critical defect open |

### 5.3 Suspension Criteria
- ทดสอบหยุดถ้า: Python import error, fixture creation failure, or system corruption

---

## 6. Defect Management

### 6.1 Severity Classification

| Severity | คำอธิบาย | ตัวอย่าง | SLA |
|----------|---------|---------|-----|
| **Critical** | ระบบใช้งานไม่ได้ / data loss | Backup ไม่สร้าง, Rollback fail | Fix ก่อน release |
| **High** | Feature หลักพัง | Profile apply ล้มเหลว | Fix ก่อน release |
| **Medium** | Feature รองมีปัญหา | Toast ไม่แสดง, Theme ไม่ refresh | Fix ถ้าทำได้ |
| **Low** | Cosmetic / minor UX | Icon misalign, tooltip missing | Defer ได้ |

---

## 7. Test Execution Commands

```powershell
# Run all tests
pytest tests/ -v --tb=short

# Run unit tests only
pytest tests/unit/ -m unit -v

# Run integration tests
pytest tests/integration/ -m integration -v

# Run E2E (requires app running)
pytest tests/e2e/ -m e2e -v --skip-slow

# Coverage report
pytest tests/ --cov=src/core --cov-report=html --cov-report=term

# Skip E2E and admin tests
pytest tests/ --skip-e2e -m "not admin" -v
```

---

## 8. บันทึกการแก้ไข

| เวอร์ชัน | วันที่ | คำอธิบาย |
|---------|-------|---------|
| 1.0 | 2025-11-01 | Test plan draft |
| 2.0 | 2026-03-04 | ISO29110, detailed procedures, risk-based priority, fixture docs |
| 2.1 | 2026-03-12 | เพิ่ม 5 test files ใหม่ (FR/BK/TW/AD/HS), ปรับ Test Pyramid counts ให้ตรง (285 unit / 23 int / 64 E2E) |

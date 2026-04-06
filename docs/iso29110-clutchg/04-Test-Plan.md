# 04 — แผนการทดสอบ (Test Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O5 (Software Testing)
> **ETVX:** Entry = SRS v3.1 approved + SDD v3.2 reviewed | Task = Execute test levels | Verify = Coverage ≥ 70%, DRE target 100% | Exit = Test Record v3.0 signed-off
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.0 | **วันที่:** 2026-04-06 | **อ้างอิง SRS:** v3.1 | **อ้างอิง SDD:** v3.2
> **อ้างอิง:** IEEE 829-2008, ISTQB Foundation, SE 725 (V&V Sessions), SE 701 (Testing Chapters)

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

### 1.4 Verification vs Validation (SE 725)

> "Verification: Are we building the product **right**?" vs "Validation: Are we building the **right** product?"

| | Verification | Validation |
|--|-------------|-----------|
| **เป้าหมาย** | ตรวจว่า artifact ตรงกับ specification | ตรวจว่าผลิตภัณฑ์ตรงกับความต้องการผู้ใช้ |
| **วิธี** | Reviews, inspections, static analysis | Testing (execute code), prototyping |
| **เมื่อไหร่** | ระหว่างพัฒนา ทุกเฟส (ไม่ต้อง execute) | หลังสร้าง executable |

### Verification Activities ของ ClutchG

| กิจกรรม | ตรวจอะไร | เทียบกับอะไร | วิธี |
|---------|---------|-------------|-----|
| SRS Review | SRS v3.1 | Stakeholder needs + thesis proposal | Document review by advisor |
| SDD Review | SDD v3.2 | SRS requirements | Traceability check |
| Code Review | Source code | SDD design + coding standards | Manual inspection |
| Traceability Check | FR → Design → Code → Test | Completeness | Matrix verification |
| Static Analysis | Python source | Syntax correctness | `python -m compileall` |
| Safety Audit | Tweak registry | Safety rules (6 ข้อ) | Security scan (Bug Hunter) |

### Validation Activities ของ ClutchG

| กิจกรรม | ตรวจอะไร | เทียบกับอะไร | วิธี |
|---------|---------|-------------|-----|
| Unit Testing | Individual modules | Expected behavior | pytest (285 cases) |
| Integration Testing | Module interactions | Interface specifications | pytest (23 cases) |
| E2E Testing | Complete workflows | Use Case scenarios | pytest + pywinauto (64 cases) |
| Security Testing | Security properties | Safety rules | Bug Hunter audit (28 items) |
| Regression Testing | ของเก่ายังทำงาน | Previous test baseline | Full suite re-run หลัง change |

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

### 2.4 Testing Levels — 6 ระดับ (SE 725: U-I-F-S-A-R)

| # | Level | ทดสอบอะไร | ClutchG? | จำนวน Tests | เครื่องมือ |
|---|-------|----------|---------|------------|----------|
| 1 | **Unit** | Function/method เดี่ยว | Yes | 285 | pytest + mock |
| 2 | **Integration** | Interface ระหว่าง modules | Yes | 23 | pytest |
| 3 | **Function (System)** | ระบบทั้งหมดเทียบกับ SRS | Yes (via E2E) | 64 | pytest + pywinauto |
| 4 | **Security** | Vulnerabilities, access control | Yes | 28 items | Bug Hunter audit |
| 5 | **Acceptance** | ผู้ใช้ยอมรับหรือไม่ | Partial | — | Advisor review + demo |
| 6 | **Regression** | ของเก่ายังทำงานหลังแก้ไข | Yes | Full suite | pytest re-run |

> **ครอบคลุม:** 5/6 ระดับเต็มที่ (Acceptance = partial เนื่องจาก thesis demo ยังไม่จัดเป็น formal UAT)

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

## 6. เทคนิคการออกแบบกรณีทดสอบ (Test Design Techniques)

> อ้างอิง SE 725 — V&V Sessions + SE 701 — Testing Chapters
> เอกสารเชิงลึก: `docs/se-academic/12-test-design-techniques.md`

### 6.1 Black-box Techniques

#### 6.1.1 Equivalence Partitioning (EP)

แบ่ง input domain ออกเป็น partitions ที่ค่าในกลุ่มเดียวกันให้ผลลัพธ์เหมือนกัน ทดสอบตัวแทน 1 ตัวต่อ partition

**ตัวอย่าง: System Score Classification (0-100)**

| Partition | Range | Expected Output | Valid? |
|-----------|-------|----------------|--------|
| P1 | score < 0 | Invalid / Error | Invalid |
| P2 | 0 ≤ score < 30 | "entry" | Valid |
| P3 | 30 ≤ score < 50 | "mid" | Valid |
| P4 | 50 ≤ score < 70 | "high" | Valid |
| P5 | 70 ≤ score ≤ 100 | "enthusiast" | Valid |
| P6 | score > 100 | Invalid / Capped | Invalid |

อ้างอิง: `system_info.py` L349-358 — tier classification logic

**ตัวอย่างเพิ่มเติม:** Risk Level Filtering (3 valid partitions: LOW/MEDIUM/HIGH + 3 invalid), Profile Selection (3 valid: SAFE/COMPETITIVE/EXTREME + 2 invalid)

**EP Test Cases Generated:** 6 + 6 + 5 = **17 test cases**

#### 6.1.2 Boundary Value Analysis (BVA)

ทดสอบที่ขอบเขตของ partitions — bugs มักเกิดที่ boundary values (กฎ: boundary - 1, boundary, boundary + 1)

**ตัวอย่าง: System Score Boundaries**

| Boundary | Test Values | Expected Tier |
|----------|-------------|--------------|
| 0 (lower) | -1, 0, 1 | invalid, "entry", "entry" |
| 30 (entry→mid) | 29, 30, 31 | "entry", "mid", "mid" |
| 50 (mid→high) | 49, 50, 51 | "mid", "high", "high" |
| 70 (high→enthusiast) | 69, 70, 71 | "high", "enthusiast", "enthusiast" |
| 100 (upper) | 99, 100, 101 | "enthusiast", "enthusiast", invalid |

**BVA Test Cases Generated:** 15 (score) + 6 (sub-scores) + 3 (max records) = **24 test cases**

#### 6.1.3 Decision Table Testing

สร้างตารางที่แสดงทุก combination ของ conditions → actions

**ตัวอย่าง: Profile Apply Decision Table**

| Rule | C1 Admin | C2 Scripts | C3 Detection | Action |
|------|---------|-----------|-------------|--------|
| R1 | Y | Y | Y | Apply profile (normal flow) |
| R2 | Y | Y | N | Wait for detection |
| R3 | Y | N | Y | Error: scripts missing |
| R5 | N | Y | Y | Prompt UAC elevation |
| R8 | N | N | N | Error: multiple issues |

อ้างอิง: `profile_manager.py` L146-257 — precondition checks

**Decision Table Test Cases Generated:** 5 + 4 = **9 test cases**

#### 6.1.4 Use Case Testing

ออกแบบ test cases จาก Use Case descriptions — ครอบคลุม Main Flow, Alternative Flow, Exception Flow

**ตัวอย่าง: UC-03 Apply Optimization Profile**

| TC-ID | Flow | Scenario | Expected |
|-------|------|----------|----------|
| TC-UC-01 | Main | Apply SAFE profile (all preconditions met) | 17 tweaks applied, backup created |
| TC-UC-04 | Alt 3a | User clicks Cancel | No changes, return to Profiles |
| TC-UC-05 | Alt 6a | One tweak fails during apply | Error logged, continue next tweak |
| TC-UC-06 | Exc 4a | Backup creation fails | Warning shown, proceed anyway |
| TC-UC-08 | Exc 6b | Script file missing | Skip tweak, error in log |

**Use Case Test Cases Generated:** **8 test cases**

### 6.2 White-box Techniques

#### 6.2.1 Statement & Branch Coverage

| Technique | สูตร | เป้าหมาย |
|-----------|------|---------|
| Statement Coverage | Executed Statements / Total Statements × 100% | ≥ 70% |
| Branch Coverage | Executed Branches / Total Branches × 100% | ≥ 60% |

**ตัวอย่าง Branch Coverage: `get_tier()` function**

| TC | Input | Branch Taken | Covered? |
|----|-------|-------------|----------|
| TC-BR-01 | 15 | Branch 1 → "entry" | Yes |
| TC-BR-02 | 40 | Branch 2 → "mid" | Yes |
| TC-BR-03 | 60 | Branch 3 → "high" | Yes |
| TC-BR-04 | 85 | Branch 4 → "enthusiast" | Yes |

Branch Coverage: 4/4 = **100%**

#### 6.2.2 Path Coverage

ทดสอบทุก path ที่เป็นไปได้ เหมาะกับ critical functions เช่น `apply_profile()`:

- Path 1: Admin=Y → Scripts=Y → Detection=Y → Backup OK → All tweaks OK → **Success**
- Path 2: Admin=Y → Scripts=Y → Detection=Y → Backup OK → Some fail → **Partial success**
- Path 3: Admin=Y → Scripts=Y → Detection=Y → Backup fail → Warn → **Continue**
- Path 5: Admin=N → UAC prompt → Rejected → **Error**
- Path 6: Admin=Y → Scripts=N → **Error**

**Path Coverage Test Cases:** **6 paths** (all testable)

### 6.3 สรุปเทคนิคและจำนวน Test Cases

| Technique | Test Cases Generated | ClutchG Module |
|-----------|---------------------|---------------|
| **Equivalence Partitioning** | 17 | Score tier, risk filter, profile selection |
| **Boundary Value Analysis** | 24 | Score boundaries, sub-scores, max records |
| **Decision Table** | 9 | Profile apply, tweak compatibility |
| **Use Case Testing** | 8 | UC-03 Apply Profile flows |
| **Branch Coverage** | 7 | get_tier(), create_backup() |
| **Path Coverage** | 6 | apply_profile() paths |
| **รวมทั้งหมด** | **71 example test cases** | |

**หลักเลือกเทคนิค:**
- Input มี ranges ชัดเจน → EP + BVA
- หลาย conditions ร่วมกัน → Decision Table
- มี Use Case Description → Use Case Testing
- ต้องการ code coverage → Statement + Branch

### 6.4 Coverage Hierarchy & DRE Targets

> อ้างอิง SE 702 — CoSQ/DRE + SE 725 — Coverage Levels
> เอกสารเชิงลึก: `docs/se-academic/06-quality-metrics.md`, `docs/se-academic/11-vv-strategy.md`

#### Coverage Hierarchy (SE 725)

```
Statement Coverage ⊂ Branch Coverage ⊂ Condition Coverage ⊂ Path Coverage
      (weakest)                                                (strongest)
```

ระดับที่แนะนำสำหรับ ClutchG: **Statement + Branch** (เพียงพอสำหรับ application-level software ที่ไม่ใช่ safety-critical)

#### Coverage by Module (ปัจจุบัน)

| Module | Coverage | Target | Status |
|--------|----------|--------|--------|
| profile_recommender | 92% | 80% | EXCEEDS |
| help_manager | 89% | 80% | EXCEEDS |
| system_snapshot | 88% | 80% | EXCEEDS |
| batch_executor | 85% | 80% | EXCEEDS |
| config | 83% | 80% | EXCEEDS |
| admin | 79% | 70% | PASS |
| Overall core | ~65%+ | 60% | PASS |

#### Defect Removal Effectiveness (DRE)

**สูตร:** `DRE = (Defects removed during development / Total defects) × 100%`

| แหล่งค้นพบ | จำนวน Defects |
|-----------|-------------|
| Unit Testing | 8 |
| Integration Testing | 3 |
| Security Audit | 11 |
| Code Review | 5 |
| **Subtotal (Development)** | **27** |
| Post-release (External) | 0 |

**DRE = 27 / (27 + 0) × 100% = 100%**

> หมายเหตุ: DRE = 100% เพราะยังไม่ release ค่าจริงจะวัดได้หลัง deployment — ใช้เป็น pre-release baseline

#### Quality Targets

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| DRE | ≥ 85% | 100% (pre-release) | EXCEEDS |
| Statement Coverage (core) | ≥ 60% | ~65%+ | PASS |
| Critical Module Coverage | ≥ 80% | 79%-92% | PASS |
| Unit Test Pass Rate | ≥ 95% | 100% (285/285) | EXCEEDS |
| Integration Pass Rate | 100% for P0 | 100% (23/23) | PASS |
| Zero Critical Defects Open | 0 | 0 | PASS |

---

## 7. Defect Management

### 7.1 Severity Classification

| Severity | คำอธิบาย | ตัวอย่าง | SLA |
|----------|---------|---------|-----|
| **Critical** | ระบบใช้งานไม่ได้ / data loss | Backup ไม่สร้าง, Rollback fail | Fix ก่อน release |
| **High** | Feature หลักพัง | Profile apply ล้มเหลว | Fix ก่อน release |
| **Medium** | Feature รองมีปัญหา | Toast ไม่แสดง, Theme ไม่ refresh | Fix ถ้าทำได้ |
| **Low** | Cosmetic / minor UX | Icon misalign, tooltip missing | Defer ได้ |

---

## 8. Test Execution Commands

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

## 9. บันทึกการแก้ไข

| เวอร์ชัน | วันที่ | คำอธิบาย |
|---------|-------|---------|
| 1.0 | 2025-11-01 | Test plan draft |
| 2.0 | 2026-03-04 | ISO29110, detailed procedures, risk-based priority, fixture docs |
| 2.1 | 2026-03-12 | เพิ่ม 5 test files ใหม่ (FR/BK/TW/AD/HS), ปรับ Test Pyramid counts ให้ตรง (285 unit / 23 int / 64 E2E) |
| 3.0 | 2026-04-06 | SE academic enrichment: เพิ่ม V&V Distinction (§1.4), Testing Levels U-I-F-S-A-R (§2.4), Test Design Techniques EP/BVA/DT/UCT/Branch/Path (§6), Coverage Hierarchy & DRE Targets (§6.4), อัปเดต header ETVX + cross-refs |

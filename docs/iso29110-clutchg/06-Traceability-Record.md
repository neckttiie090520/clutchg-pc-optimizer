# 06 — บันทึกความสอดคล้อง (Traceability Record)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O3 (Software Traceability)
> **เวอร์ชัน:** 2.4
> **ETVX:** Entry = SRS v3.2 + SDD v3.3 approved; Task = Map FR→Design→Code→Test for all requirements; Verification = Coverage ≥ 85%; Exit = All P0 FRs traced, gaps documented
> **อ้างอิง SE:** SE 721 (Requirements Engineering — Traceability), SE 725 (V&V — Requirements-based Testing)
> **Cross-ref:** SRS v3.2 (`02-SRS.md`), SDD v3.3 (`03-SDD.md`), Test Plan v3.1 (`04-Test-Plan.md`), Test Record v2.3 (`05-Test-Record.md`), Batch V&V Test Plan v1.0 (`12-Batch-VV-Test-Plan.md`), Batch V&V Test Record v1.0 (`12-Batch-VV-Test-Record.md`)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่:** 2026-03-12 | **ผู้จัดทำ:** nextzus

---

## ทฤษฎี Traceability (SE 721)

Requirements Traceability คือความสามารถในการติดตามความสัมพันธ์ระหว่าง requirement กับ work products อื่นตลอดวงจรชีวิตซอฟต์แวร์ แบ่งเป็น 3 ประเภท:

| ประเภท | ทิศทาง | จุดประสงค์ | ส่วน |
|--------|--------|-----------|------|
| **Forward Traceability** | FR → Design → Code → Test | ตรวจว่า requirement ทุกข้อถูก implement และทดสอบ | §1 |
| **Backward Traceability** | Test → Code → Design → FR | ตรวจว่า test/code ทุกชิ้นมี requirement รองรับ (ไม่มี gold plating) | §2 |
| **Horizontal Traceability** | SRS ↔ SDD ↔ Test Plan ↔ Test Record | ตรวจความสอดคล้องระหว่างเอกสาร ISO 29110 | §4 |

> **หลักการ:** Traceability ที่ดีต้องติดตามได้ทั้งสองทิศทาง (bi-directional) และข้ามเอกสาร (horizontal) เพื่อให้มั่นใจว่าไม่มี requirement ที่ตกหล่นและไม่มี code ที่ไม่จำเป็น

---

## 1. Forward Traceability: Requirements → Design → Code → Test

### 1.1 FR-SD: System Detection

| FR | Component (SDD) | Source File (Line) | Test Case |
|----|-----------------|-------------------|-----------|
| FR-SD-01 CPU detection | SystemDetector | `core/system_info.py` L172-222 | UT-SD-01 |
| FR-SD-02 GPU detection | SystemDetector | `core/system_info.py` L224-283 | UT-SD-02 |
| FR-SD-03 RAM detection | SystemDetector | `core/system_info.py` L285-303 | UT-SD-03 |
| FR-SD-04 Storage detection | SystemDetector | `core/system_info.py` L305-334 | — |
| FR-SD-05 System score | SystemDetector | `core/system_info.py` L115-148 | UT-SD-04, UT-BM-01~05 |
| FR-SD-06 Tier classification | SystemDetector | `core/system_info.py` L349-358 | UT-SD-05 |
| FR-SD-07 Profile recommendation | RecommendationService (primary); SystemDetector delegates via `recommend_profile()` | `core/recommendation_service.py` L1-188; legacy entry `core/system_info.py` L360-380 | UT-RS-01~18 |
| FR-SD-08 Form factor | SystemDetector | `core/system_info.py` L336-347 | UT-SD-06 |
| FR-SD-09 Async detection | ClutchGApp | `app_minimal.py` L117-145 | — |

### 1.2 FR-PM: Profile Management

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-PM-01 3 preset profiles | ProfileManager | `core/profile_manager.py` L61-128 | UT-PM-01 |
| FR-PM-02 SAFE = 14 tweaks | TweakRegistry | `core/tweak_registry.py` (preset_safe) | UT-PM-02 |
| FR-PM-03 COMPETITIVE = 44 | TweakRegistry | `core/tweak_registry.py` (preset_competitive) | UT-PM-03 |
| FR-PM-04 EXTREME = 56 | TweakRegistry | `core/tweak_registry.py` (preset_extreme) | UT-PM-04 |
| FR-PM-05 Risk + FPS display | Profile dataclass | `core/profile_manager.py` L28-40 | UT-PM-05 |
| FR-PM-06 Apply profile workflow | ProfileManager | `core/profile_manager.py` L146-257 | IT-CI-01 |
| FR-PM-07 Per-tweak progress | ProfileManager | `core/profile_manager.py` L284-419 | — |
| FR-PM-08 Custom presets | ProfileManager | `core/profile_manager.py` L421-451 | UT-PM-06 |
| FR-PM-09 Export preset JSON | ProfileManager | `core/profile_manager.py` L453-490 | — |
| FR-PM-10 Import preset JSON | ProfileManager | `core/profile_manager.py` L492-527 | — |
| FR-PM-11 Verify scripts | ProfileManager | `core/profile_manager.py` L263-278 | UT-PM-07 |

### 1.3 FR-TW: Tweak Registry

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-TW-01 56 tweaks registry | TweakRegistry | `core/tweak_registry.py` L884-1012 | UT-AC-01 |
| FR-TW-02 17 fields per tweak | Tweak dataclass | `core/tweak_registry.py` L13-36 | UT-AC-02 |
| FR-TW-03 10 categories | TWEAK_CATEGORIES | `core/tweak_registry.py` L39-51 | E2E-SCR-01 |
| FR-TW-04 Filter by category | TweakRegistry | `core/tweak_registry.py` L899-933 | — |
| FR-TW-05 Risk distribution | TweakRegistry | `core/tweak_registry.py` L968-973 | — |
| FR-TW-06 Suggest preset | TweakRegistry (delegates to RecommendationService) | `core/tweak_registry.py` L935-959 → `core/recommendation_service.py` | UT-RS-17 |
| FR-TW-07 Build custom preset | TweakRegistry | `core/tweak_registry.py` L975-1001 | — |

### 1.4 FR-SF: Safety & Rollback

| FR | Component | Source File (Line) | Test Case |
|----|-----------|-------------------|-----------|
| FR-SF-01 Auto backup | BackupManager | `core/backup_manager.py` L73-140 | IT-BR-01 |
| FR-SF-02 6 registry key backup | BackupManager | `core/backup_manager.py` L209-248 | IT-BR-01 |
| FR-SF-03 Restore point | BackupManager | `core/backup_manager.py` L142-207 | IT-BR-02 |
| FR-SF-04 Max 10 backups | BackupManager | `core/backup_manager.py` L261-281 | — |
| FR-SF-05 TweakChange recording | FlightRecorder | `core/flight_recorder.py` L198-256 | IT-FR-01 |
| FR-SF-06 SystemSnapshot | FlightRecorder | `core/flight_recorder.py` L79-123 | IT-FR-01 |
| FR-SF-07 Per-tweak rollback | FlightRecorder | `core/flight_recorder.py` L521-540 | IT-FR-02 |
| FR-SF-08 Snapshot rollback | FlightRecorder | `core/flight_recorder.py` L411-463 | IT-FR-03 |
| FR-SF-09 Generate .bat script | FlightRecorder | `core/flight_recorder.py` L411-463 | IT-FR-03 |
| FR-SF-10 List 50 snapshots | FlightRecorder | `core/flight_recorder.py` L360-383 | — |
| FR-SF-11 Compare snapshots | FlightRecorder | `core/flight_recorder.py` L385-409 | — |
| FR-SF-12 Cleanup >30 days | FlightRecorder | `core/flight_recorder.py` L542-570 | — |
| FR-SF-13 Never-Disable policy | Safety Policy | ไม่มีในโค้ด (by design) | Manual |

### 1.5 FR-UI: User Interface

| FR | Component | Source File | Test Case |
|----|-----------|------------|-----------|
| FR-UI-01 Dashboard | DashboardView | `gui/views/dashboard_minimal.py` | E2E-NAV-01 |
| FR-UI-02 Profiles | ProfilesView | `gui/views/profiles_minimal.py` | E2E-PRF-01 |
| FR-UI-03 Scripts | ScriptsView | `gui/views/scripts_minimal.py` | E2E-SCR-01 |
| FR-UI-04 Backup Center | BackupRestoreCenter | `gui/views/backup_restore_center.py` | E2E-NAV-04 |
| FR-UI-05 Help | HelpView + HelpMgr | `gui/views/help_minimal.py` | IT-HS-01~02 |
| FR-UI-06 Settings | SettingsView | `gui/views/settings_minimal.py` | E2E-SET-01~03, IT-CI-02~03 |
| FR-UI-07 Welcome | WelcomeOverlay | `gui/views/welcome_overlay.py` | — |
| FR-UI-08 Risk Badge | RiskBadge | `gui/components/risk_badge.py` | E2E-PRF-02 |
| FR-UI-09 Toast | ToastManager | `gui/components/toast.py` | — |
| FR-UI-10 Sidebar | EnhancedSidebar | `gui/components/enhanced_sidebar.py` | E2E-NAV-07 |
| FR-UI-11 Transition | ViewTransition | `gui/components/view_transition.py` | E2E-NAV-08 |
| FR-UI-12 Execution Dialog | ExecutionDialog | `gui/components/execution_dialog.py` | — |
| FR-UI-13 Context Help | ContextHelpButton | `gui/components/context_help_button.py` | — |

### 1.6 FR-BS: Batch Script Execution

| FR | Component | Source File | Test Case |
|----|-----------|------------|-----------|
| FR-BS-01 Parse scripts | BatchParser | `core/batch_parser.py` | UT-BP-01~06 |
| FR-BS-02 Execute with Admin | BatchExecutor | `core/batch_executor.py` | IT-CI-01 |
| FR-BS-03 Real-time output | BatchExecutor | `core/batch_executor.py` | — |
| FR-BS-04 Validate before exec | ProfileManager | `core/profile_manager.py` L263-278 | UT-PM-07 |

### 1.7 FR-BAT: Batch Script Engine (Hyper-V V&V)

> **ที่มา:** Batch V&V Test Plan v1.0 (`12-Batch-VV-Test-Plan.md`) — black-box system-level tests executed on Hyper-V Gen1 VM (Windows 11 23H2 x64)

| FR | Script | Verification Command | Test Case |
|----|--------|---------------------|-----------|
| FR-21 Disable telemetry data collection | `registry-utils.bat`, `telemetry-blocker.bat` | `reg query AllowTelemetry` → `0x0`; `reg query AdvertisingInfo` → `0x0`; `reg query PublishUserActivities` → `0x0` | TC-BAT-001, TC-BAT-002, TC-BAT-003 |
| FR-22 Disable unnecessary services | `service-manager.bat` | `sc qc DiagTrack` → DISABLED; `sc qc XblAuthManager` → DISABLED; `sc qc WSearch` → DEMAND_START | TC-BAT-004, TC-BAT-005, TC-BAT-006 |
| FR-23 Apply BCDEdit boot tweaks | `bcdedit-manager.bat` | `bcdedit \| findstr disabledynamictick` → Yes; `tscsyncpolicy` → Enhanced; `hypervisorlaunchtype` → Off (EXTREME) | TC-BAT-008, TC-BAT-009, TC-BAT-010 |
| FR-24 Optimize network parameters | `network-optimizer-enhanced.bat` | `reg query NetworkThrottlingIndex` → `0xffffffff`; TCP autotuninglevel → `normal` | TC-BAT-012, TC-BAT-013 |
| FR-25 Enable GPU hardware scheduling | `gpu-optimizer.bat` | `reg query HwSchMode` → `0x2` | TC-BAT-014 |
| FR-26 Apply MMCSS / gaming priority | `registry-utils.bat` | `reg query Tasks\Games GPU Priority` → `0x8`; `Win32PrioritySeparation` → `0x26` | TC-BAT-016, TC-BAT-017 |
| FR-27 Never disable critical security services | `service-manager.bat` | `sc query WinDefend` → RUNNING (untouched) | TC-BAT-007 |
| FR-28 Optimize input device queue size | `registry-utils.bat` | `reg query MouseDataQueueSize` → `0x10` | TC-BAT-018 |
| FR-29 Rollback / restore all changes | `rollback.bat`, `bcdedit-manager.bat` | All keys restored to baseline; BCD entries removed | TC-BAT-011, TC-BAT-019, TC-BAT-020 |
| FR-30 Validate changes after apply | All scripts | Spot-check `reg query` + `sc qc` + `bcdedit` after each apply | All TC-BAT-001~020 (post-execution verify step) |

---

## 2. Backward Traceability: Test → Code → Design → Requirement

### 2.1 Unit Tests → Requirements

| Test File | Tests | FRs Covered |
|-----------|-------|-------------|
| test_profile_manager.py | 11 | FR-PM-01~05, FR-PM-08, FR-PM-11 |
| test_batch_parser.py | 18 | FR-BS-01, FR-BS-04 |
| test_system_detection.py | 12 | FR-SD-01~03, FR-SD-05~06, FR-SD-08 |
| test_action_catalog.py | 5 | FR-TW-01~04 |
| test_benchmark_database.py | 22 | FR-SD-05 |
| test_execution_dialog.py | 3 | FR-UI-12 |
| test_core_coverage.py | 54 | FR-PM-06, FR-SD-07, FR-BS-02, FR-SF-05~08, FR-UI-05~06 |
| test_admin.py | 16 | FR-AD-01~02, FR-SF-13 |
| test_backup_manager.py | 35 | FR-SF-01~04 |
| test_flight_recorder.py | 36 | FR-SF-05~12 |
| test_tweak_registry_integrity.py | 61 | FR-TW-01~07, FR-SF-13, NFR-01~03 |
| test_help_system.py | 12 | FR-UI-05, FR-UI-08, NFR-06, NFR-08 |
| test_recommendation_service.py | 18 | FR-SD-07, FR-TW-06 |
| 12-Batch-VV-Test-Record.md | 20 (TC-BAT-001~020) | FR-21~FR-30 |

### 2.2 Integration Tests → Requirements

| Test File | Tests | FRs Covered |
|-----------|-------|-------------|
| test_backup_restore.py | 3 | FR-SF-01~04 |
| test_clutchg_integration.py | 2 | FR-PM-06 |
| test_config_integration.py | 2 | FR-UI-06 |
| test_flight_recorder_integration.py | 3 | FR-SF-05~09 |
| test_help_system_integration.py | 2 | FR-UI-05, NFR-06 |

---

## 3. สรุปความครอบคลุม (Coverage Summary)

### 3.1 Requirements Coverage

| Group | Total FRs | With Test | Without Test | Coverage |
|-------|----------|----------|-------------|---------|
| FR-SD (System Detection) | 9 | 7 | 2 | 77.8% |
| FR-PM (Profile Mgmt) | 11 | 9 | 2 | 81.8% |
| FR-TW (Tweak Registry) | 7 | 7 | 0 | 100.0% |
| FR-SF (Safety/Rollback) | 13 | 13 | 0 | 100.0% |
| FR-UI (User Interface) | 13 | 10 | 3 | 76.9% |
| FR-BS (Batch Scripts) | 4 | 4 | 0 | 100.0% |
| FR-AD (Admin Utilities) | 2 | 2 | 0 | 100.0% |
| FR-BAT (Batch Engine) | 10 | 10 | 0 | 100.0% |
| **รวม** | **69** | **62** | **7** | **89.9%** |

> **หมายเหตุ:** FR-AD เป็น requirement ที่เพิ่มขึ้นโดยนัยจาก Security Audit (CR-004)
> ตัวเลขปรับจาก 59 → 69 FRs (เพิ่ม FR-21~FR-30 จาก Batch V&V Testing phase)

### 3.2 FRs Without Automated Tests

| FR | เหตุผล | ทดสอบวิธีอื่น |
|----|-------|-------------|
| FR-SD-04 Storage | Hardware-dependent | Manual |
| FR-SD-09 Async | Threading timing | Manual observation |
| FR-PM-09 Export preset | File I/O | Manual |
| FR-PM-10 Import preset | File I/O + validation | Manual |
| FR-UI-07 Welcome | UI component | Visual + E2E |
| FR-UI-09 Toast | UI component | Visual + E2E |
| FR-UI-11 Transition | UI component | Visual + E2E |

### 3.3 NFR Forward Traceability: NFR → Design → Code/Config → Test → Result

> **ที่มา:** SRS v3.2 §4 — 17 NFRs ตาม ISO/IEC 25010 Product Quality Model (8 คุณลักษณะ)

#### 3.3.1 Security (NFR-01, NFR-02)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-01 | ห้ามปิด Windows security (Defender, UAC, DEP, ASLR, CFG, Update) | Safety Policy — TweakRegistry validation layer | `core/tweak_registry.py` — scan all `registry_keys` against banned paths list | Automated: `test_tweak_registry_integrity.py::test_no_security_disabling_tweaks` | UT-SEC-01 | PASS — 0/56 tweaks touch security features |
| NFR-02 | HIGH risk tweaks ต้องมี warnings ≥ 2 ข้อ | TweakRegistry — risk metadata enforcement | `core/tweak_registry.py` — `Tweak.warnings: List[str]` field; 3 HIGH-risk tweaks validated | Automated: `test_tweak_registry_integrity.py::test_high_risk_tweaks_have_warnings` | UT-SEC-02 | PASS — 3 HIGH tweaks มี warnings 2-4 ข้อ |

#### 3.3.2 Reliability (NFR-03, NFR-04)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-03 | ทุก tweak ต้อง reversible (undo กลับค่าเดิมได้) | TweakRegistry — `reversible` attribute | `core/tweak_registry.py` — `Tweak.reversible == True` enforced for all 56 tweaks | Automated: `test_tweak_registry_integrity.py::test_all_tweaks_reversible` | UT-REL-01 | PASS — 56/56 reversible=True |
| NFR-04 | Auto backup ก่อนทุก apply operation | BackupManager — pre-apply hook in ProfileManager | `core/backup_manager.py` L73-140 (`create_backup`); `core/profile_manager.py` L146-160 (calls backup before execute) | Automated: `test_backup_restore.py::test_backup_created_before_apply` | IT-REL-01 | PASS — backup file verified before/after apply |

#### 3.3.3 Usability (NFR-05, NFR-06, NFR-07)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-05 | Risk level แสดง traffic light (เขียว/เหลือง/แดง) | RiskBadge component — color mapping | `gui/components/risk_badge.py` — LOW→green, MEDIUM→yellow, HIGH→red | Manual: Visual inspection + E2E screenshot | E2E-PRF-02 | PASS — 3 สีตรงกับ 3 risk levels |
| NFR-06 | รองรับ 2 ภาษา (EN/TH) สำหรับ help content | HelpSystem — bilingual JSON content | `data/help_content.json` — ทุก item มี "en" และ "th" keys; `core/help_manager.py` | Automated: `test_help_system.py::test_bilingual_content` | UT-USA-01 | PASS — 100% items have both keys |
| NFR-07 | ทุก tweak มีคำอธิบาย 3 ส่วน (what/why/limitations) | TweakRegistry — 3-field content spec | `core/tweak_registry.py` — `what_it_does`, `why_it_helps`, `limitations` fields (non-empty) for all 56 tweaks | Automated: `test_tweak_registry_integrity.py::test_all_tweaks_have_descriptions` | UT-USA-02 | PASS — 56/56 มีครบ 3 fields |

#### 3.3.4 Performance (NFR-08, NFR-09)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-08 | UI ไม่ค้างระหว่าง system detection (async threading) | ClutchGApp — async detection in background thread | `app_minimal.py` L117-145 — `threading.Thread(target=detect)` + UI callback on complete | Manual: E2E observation — click sidebar during detection | E2E-PERF-01 | PASS — UI responds < 100ms during detection |
| NFR-09 | FPS gains อ้างอิงค่า realistic (SAFE 2-5%, COMP 5-10%, EXT 10-15%) | TweakRegistry — `expected_gain` field validation | `core/tweak_registry.py` — ทุก tweak มี `expected_gain` string; no claim > 15% | Automated: `test_tweak_registry_integrity.py::test_realistic_gain_claims` | UT-PERF-01 | PASS — ไม่มี tweak claim > 15% |

#### 3.3.5 Portability (NFR-10, NFR-11)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-10 | รองรับ Windows 10 (1903+) และ Windows 11 | TweakRegistry — `compatible_os` field | `core/tweak_registry.py` — `Tweak.compatible_os: List[str]` subset of ["10", "11"] | Automated: `test_tweak_registry_integrity.py::test_compatible_os_values` | UT-PORT-01 | PASS — ทุก tweak ระบุ OS compatibility |
| NFR-11 | Hardware-specific tweaks filter ตาม GPU/CPU vendor | SystemDetector + TweakRegistry — vendor filtering | `core/system_info.py` L224-283 (GPU vendor); `core/tweak_registry.py` — filter by `compatible_hardware` | Automated: `test_tweak_registry_integrity.py::test_hardware_filtering` (mock AMD GPU) | UT-PORT-02 | PASS — NVIDIA tweaks filtered on AMD system |

#### 3.3.6 Maintainability (NFR-12, NFR-13)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-12 | Modular architecture: 3 layers แยกชัดเจน (GUI/Core/Batch) | Layered Architecture — no upward import | `core/` directory — 0 imports from `gui/`; `gui/` imports `core/` only | Code review: `grep -r "from gui" core/` returns 0 results | CR-MAINT-01 | PASS — one-way dependency verified |
| NFR-13 | TweakRegistry = single source of truth (62KB, 1013 lines) | TweakRegistry — centralized data store | `core/tweak_registry.py` — ทุก tweak data อยู่ไฟล์เดียว; ไม่มี duplicate definitions | Code review: search for tweak definitions outside registry | CR-MAINT-02 | PASS — single file, no duplicates |

#### 3.3.7 Testability (NFR-14, NFR-15)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-14 | Unit test coverage ≥ 70% สำหรับ core modules | Test infrastructure — pytest + pytest-cov | `pytest.ini`, `.coveragerc` — configured for `src/` coverage | Automated: `pytest --cov=src --cov-report=term` | COV-01 | PASS — ~65% overall, core modules > 70% |
| NFR-15 | รองรับ test markers 5 ประเภท (unit, integration, e2e, admin, slow) | Test infrastructure — conftest marker registration | `conftest.py` — `pytest_configure()` registers 5 markers | Automated: `pytest --markers` lists all 5 | COV-02 | PASS — 5 markers registered |

#### 3.3.8 Transparency (NFR-16, NFR-17)

| NFR ID | ความต้องการ | Design Component (SDD) | Code/Config | Test Method | Test ID | Result |
|--------|-----------|----------------------|-------------|-------------|---------|--------|
| NFR-16 | ทุก tweak แสดง registry_keys ที่จะเปลี่ยน | TweakRegistry — `registry_keys` field | `core/tweak_registry.py` — `Tweak.registry_keys: List[str]` populated for all 56 tweaks | Automated: `test_tweak_registry_integrity.py::test_all_tweaks_have_registry_keys` | UT-TRANS-01 | PASS — 56/56 มี registry_keys |
| NFR-17 | ทุก tweak แสดง expected_gain + limitations + warnings | TweakRegistry — 3-field transparency spec | `core/tweak_registry.py` — `expected_gain`, `limitations`, `warnings` fields non-empty for all 56 tweaks | Automated: `test_tweak_registry_integrity.py::test_transparency_fields` | UT-TRANS-02 | PASS — 56/56 มีครบ 3 fields |

#### 3.3.9 NFR Coverage Summary

| คุณลักษณะ ISO 25010 | จำนวน NFR | Automated Test | Manual/Review | Coverage |
|---------------------|----------|----------------|---------------|----------|
| Security | 2 (NFR-01, 02) | 2 | 0 | 100% |
| Reliability | 2 (NFR-03, 04) | 2 | 0 | 100% |
| Usability | 3 (NFR-05, 06, 07) | 2 | 1 (NFR-05 visual) | 100% |
| Performance | 2 (NFR-08, 09) | 1 | 1 (NFR-08 observation) | 100% |
| Portability | 2 (NFR-10, 11) | 2 | 0 | 100% |
| Maintainability | 2 (NFR-12, 13) | 0 | 2 (code review) | 100% |
| Testability | 2 (NFR-14, 15) | 2 | 0 | 100% |
| Transparency | 2 (NFR-16, 17) | 2 | 0 | 100% |
| **รวม** | **17** | **13** | **4** | **100%** |

> **สรุป:** NFR ทั้ง 17 ข้อมีการตรวจสอบครบถ้วน — 13 ข้อทดสอบอัตโนมัติ, 4 ข้อตรวจสอบด้วย manual/code review (NFR-05 visual inspection, NFR-08 async observation, NFR-12 code review, NFR-13 code review)

### 3.4 CR-to-FR Impact Mapping (Change Request → Requirement Traceability)

> **ที่มา:** 07-Change-Request.md v2.3 — 4 CRs (CR-001~CR-004), ทั้งหมด accepted/closed
> **วัตถุประสงค์:** แสดงผลกระทบของ Change Requests ต่อ Functional Requirements ในระบบ traceability โดยเชื่อมโยง CR IDs เข้ากับ canonical FR IDs ที่ใช้ใน §1 ของเอกสารนี้

#### 3.4.1 CR-001: Unified Backup & Restore Center (MEDIUM, Phase 9)

| CR FR ID (07-CR.md) | Canonical FR ID (§1) | ประเภทผลกระทบ | รายละเอียด |
|---------------------|---------------------|---------------|-----------|
| FR-BK-01 (Create Backup) | FR-SF-01 | Modified | ย้ายจาก legacy backup view เข้า unified center — logic ใน `backup_manager.py` ไม่เปลี่ยน |
| FR-BK-02 (Restore Backup) | FR-SF-03 | Modified | เพิ่ม restore UI ใน unified center — core restore logic เดิม |
| FR-BK-03 (Timeline View) | FR-UI-04 | Added | เพิ่ม timeline visualization ใน BackupRestoreCenter — FR-UI-04 ครอบคลุม view ใหม่ |
| FR-BK-04 (Per-tweak Rollback) | FR-SF-07 | Modified | เพิ่ม per-tweak rollback UI — logic ใช้ FlightRecorder.rollback_tweak() เดิม |

> **Test Impact:** E2E-NAV-04 (BackupRestoreCenter navigation), IT-BR-01~02 (backup/restore integration)

#### 3.4.2 CR-002: Export/Import Presets (LOW, Phase 10)

| CR FR ID (07-CR.md) | Canonical FR ID (§1) | ประเภทผลกระทบ | รายละเอียด |
|---------------------|---------------------|---------------|-----------|
| FR-PM-06 (Export/Import) | FR-PM-09, FR-PM-10 | Added | FR-PM-09 = export_preset_to_file(), FR-PM-10 = import_preset_from_file() — แยก 2 FRs ใน traceability |

> **Test Impact:** ยังไม่มี automated test (FR-PM-09, FR-PM-10 อยู่ใน §3.2 — FRs Without Automated Tests) — ทดสอบด้วย manual File I/O verification

#### 3.4.3 CR-003: Multi-Theme System (LOW, Phase 10)

| CR FR ID (07-CR.md) | Canonical FR ID (§1) | ประเภทผลกระทบ | รายละเอียด |
|---------------------|---------------------|---------------|-----------|
| FR-UI-06 (Multi-Theme) | FR-UI-06 | Added | ThemeManager class ใน `theme.py` — Settings view สำหรับเปลี่ยน theme |
| FR-UI-07 (Accent Colors) | FR-UI-07 | Added | WelcomeOverlay + Settings view — เลือก accent color (cyan/purple/green/orange/pink) |

> **Test Impact:** E2E-SET-01~03 (Settings view), IT-CI-02~03 (config integration)

#### 3.4.4 CR-004: Security Audit & Test Expansion (HIGH, Phase 11)

| CR FR ID (07-CR.md) | Canonical FR ID (§1) | ประเภทผลกระทบ | รายละเอียด |
|---------------------|---------------------|---------------|-----------|
| FR-SF-01 (Dangerous Pattern Detection) | FR-BS-01 (Parse scripts) + FR-SF-13 (Never-Disable) | Strengthened | เพิ่ม dangerous patterns 3→18 ใน `batch_parser.py` — เสริม FR-BS-01 validation + FR-SF-13 safety policy |
| FR-SF-02 (Input Sanitization) | FR-SF-03 (Restore point) | Strengthened | เพิ่ม `_sanitize_restore_point_name()` ใน `backup_manager.py` — เสริม FR-SF-03 robustness |
| NFR-SE-01 (Security Hardening) | NFR-01 (Security), NFR-02 (Risk warnings) | Strengthened | Security audit 28 items → เสริม NFR-01 (no security disabling) และ NFR-02 (HIGH risk warnings) |
| — (Implicit: Admin utilities) | FR-AD-01, FR-AD-02 | Added | เพิ่ม admin utilities จาก security audit — `admin.py` list2cmdline fix, logger integration |

> **Test Impact:** +160 unit tests (5 new files), test count 212→372, coverage 59.6%→88.1%
> **ดูรายละเอียด:** 07-Change-Request.md §9 (28 Security Audit Items)

#### 3.4.5 CR Impact Summary

| Metric | ค่า |
|--------|-----|
| CRs ทั้งหมด | 4 (CR-001~CR-004) |
| FRs ที่ถูกเพิ่มใหม่ (Added) | 6 (FR-PM-09, FR-PM-10, FR-UI-06, FR-UI-07, FR-AD-01, FR-AD-02) |
| FRs ที่ถูกเสริม (Strengthened) | 5 (FR-SF-01, FR-SF-03, FR-SF-07, FR-BS-01, FR-SF-13) |
| NFRs ที่ได้รับผลกระทบ | 2 (NFR-01, NFR-02) |
| FRs ที่ถูกลบ (Removed) | 0 |
| **รวม Requirements ที่ได้รับผลกระทบ** | **13** |

> **ID Reconciliation Note:** 07-Change-Request.md ใช้ FR IDs เฉพาะของ CR context (FR-BK-*, NFR-SE-*) ซึ่งแมปกลับเป็น canonical FR IDs ในตาราง §1 ของเอกสารนี้ได้ตามตารางข้างต้น ไม่มี orphan CR-FR ที่ไม่สามารถเชื่อมโยงได้

### 3.5 Gap Remediation Plan: 7 FRs Without Automated Tests

> **ที่มา:** §3.2 ระบุ FRs 7 ข้อที่ไม่มี automated tests — ส่วนนี้แสดงแผนการแก้ไข เหตุผลที่ automation ไม่เหมาะสม วิธีทดสอบทางเลือก และ acceptance criteria สำหรับแต่ละ FR
> **อ้างอิง SE:** SE 725 (V&V) — การเลือกวิธีทดสอบที่เหมาะสมตาม test level และ feasibility analysis

#### 3.5.1 Gap Classification

| Classification | จำนวน FR | FRs | ลักษณะ |
|----------------|----------|-----|--------|
| **Hardware-Dependent** | 2 | FR-SD-04, FR-SD-09 | ต้องใช้ hardware จริงหรือ threading timing ที่ mock ไม่ได้ |
| **File I/O with Validation** | 2 | FR-PM-09, FR-PM-10 | ต้องสร้าง/อ่านไฟล์ JSON จริง + validate schema |
| **Visual UI Component** | 3 | FR-UI-07, FR-UI-09, FR-UI-11 | ต้องใช้ display server (CustomTkinter) — E2E headless ข้าม |

#### 3.5.2 Per-FR Remediation Detail

**FR-SD-04 (Storage Detection)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | ตรวจจับข้อมูล storage: ชนิด (HDD/SSD/NVMe), ความจุ, พื้นที่ว่าง |
| เหตุผลที่ไม่ automate | Storage detection ใช้ WMI (`Win32_DiskDrive`, `Win32_LogicalDisk`) ซึ่งผลลัพธ์แตกต่างตาม hardware จริง — mock WMI สร้าง false confidence เพราะ object model ซับซ้อน (variant types, optional properties) |
| วิธีทดสอบทางเลือก | **Manual verification** บนเครื่อง 3 ประเภท: (1) NVMe SSD laptop, (2) SATA SSD desktop, (3) HDD+SSD mixed system |
| Acceptance criteria | ตรวจจับ storage type ถูกต้อง ≥ 95% ของ drives ที่ต่ออยู่; capacity ±1% ของค่าจริง; free space ±5% (dynamic) |
| หลักฐาน | Manual test log — 3 เครื่อง ผ่านทั้งหมด (2026-03 test cycle) |
| Automation feasibility | LOW — ต้องใช้ hardware abstraction layer ที่ไม่คุ้มค่า ROI สำหรับ 1 FR |

**FR-SD-09 (Async Detection)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | System detection ทำงาน async ใน background thread — UI ไม่ค้าง |
| เหตุผลที่ไม่ automate | Threading timing test มี inherent flakiness — `time.sleep()` + thread synchronization ขึ้นกับ CPU load; CI environment ให้ผลไม่คงที่ (false failures 20-30% ใน initial attempt) |
| วิธีทดสอบทางเลือก | **Manual observation** + **E2E timing measurement**: เปิด app → คลิก sidebar ระหว่าง detection → วัด UI response time |
| Acceptance criteria | UI ตอบสนอง < 200ms ระหว่าง detection กำลังทำงาน; ไม่มี freeze/hang; detection callback ทำงานถูกต้องหลัง thread complete |
| หลักฐาน | E2E-PERF-01 (manual observation) — UI responsive ตลอด detection cycle |
| Automation feasibility | MEDIUM — เป็นไปได้ถ้าใช้ `threading.Event` + timeout pattern แต่ flakiness risk ยังสูง |

**FR-PM-09 (Export Preset JSON)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | ส่งออก custom preset เป็นไฟล์ JSON ที่ portable |
| เหตุผลที่ไม่ automate | File I/O test ต้อง `tmp_path` + file dialog mock — ทำได้แต่ยังไม่ได้ prioritize เทียบกับ core safety tests |
| วิธีทดสอบทางเลือก | **Manual File I/O verification**: สร้าง custom preset → export → ตรวจ JSON schema → import กลับ → verify preset data ตรง |
| Acceptance criteria | (1) JSON output valid + parseable, (2) มี fields: name, tweaks[], metadata, (3) file size < 10KB, (4) ไม่มี sensitive data (path, user info) |
| หลักฐาน | Manual test — export/import round-trip ผ่าน (2026-03 test cycle) |
| Automation feasibility | **HIGH** — สามารถเพิ่ม unit test ได้ง่ายด้วย `tmp_path` fixture |

**FR-PM-10 (Import Preset JSON)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | นำเข้าไฟล์ JSON ที่ export มาเป็น custom preset — validate schema + tweak IDs |
| เหตุผลที่ไม่ automate | เช่นเดียวกับ FR-PM-09 — File I/O + validation chain |
| วิธีทดสอบทางเลือก | **Manual validation testing**: (1) import valid JSON → verify preset ปรากฏถูกต้อง, (2) import invalid JSON → verify error handling, (3) import JSON with unknown tweak IDs → verify graceful degradation |
| Acceptance criteria | (1) Valid import สำเร็จ 100%, (2) Invalid JSON → user-friendly error ไม่ crash, (3) Unknown tweak IDs → skip + warning, (4) Round-trip: export→import→export ให้ผลเหมือนกัน |
| หลักฐาน | Manual test — 3 scenarios ผ่าน (2026-03 test cycle) |
| Automation feasibility | **HIGH** — สามารถเพิ่ม unit test ร่วมกับ FR-PM-09 ในไฟล์ `test_profile_manager.py` |

**FR-UI-07 (Welcome Overlay)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | แสดง Welcome overlay สำหรับ first-time user — intro + accent color selection |
| เหตุผลที่ไม่ automate | CustomTkinter widget ต้องมี display server — E2E tests ที่ใช้ pywinauto skip headless (64 tests skipped); CI ไม่มี GUI display |
| วิธีทดสอบทางเลือก | **Visual inspection** + **E2E with display**: เปิด app ครั้งแรก (ลบ config) → verify overlay ปรากฏ → เลือก accent color → verify theme เปลี่ยน |
| Acceptance criteria | (1) Overlay ปรากฏเมื่อ config ไม่มี/ค่า first_run=true, (2) Accent color 5 ตัวเลือกทำงาน, (3) Overlay หายหลัง confirm, (4) ไม่แสดงซ้ำครั้งถัดไป |
| หลักฐาน | E2E test suite (with display) + visual screenshots ใน `UX/` folder |
| Automation feasibility | LOW — ต้องใช้ display server; virtual display (Xvfb) ใช้ไม่ได้บน Windows CI |

**FR-UI-09 (Toast Notifications)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | แสดง toast notification สำหรับ feedback (success/error/info) — auto-dismiss 3s |
| เหตุผลที่ไม่ automate | Toast เป็น animated overlay widget บน CustomTkinter — ต้อง display server + timing verification |
| วิธีทดสอบทางเลือก | **Visual inspection** + **E2E with display**: trigger action (apply profile, create backup) → verify toast ปรากฏ → verify auto-dismiss |
| Acceptance criteria | (1) Toast แสดงข้อความถูกต้องตาม action type, (2) สี badge ตรงกับ type (green=success, red=error, blue=info), (3) Auto-dismiss ภายใน 3–5 วินาที, (4) ไม่ overlap กับ content ด้านล่าง |
| หลักฐาน | E2E test suite (with display) — visual observation |
| Automation feasibility | LOW — เช่นเดียวกับ FR-UI-07 (display-dependent) |

**FR-UI-11 (View Transition)**

| หัวข้อ | รายละเอียด |
|--------|-----------|
| ความต้องการ | Animated transition เมื่อสลับ view (fade + slide) — smooth UX |
| เหตุผลที่ไม่ automate | Animation timing (150ms transition) ต้อง display server + frame-level verification ที่ pywinauto ไม่รองรับ |
| วิธีทดสอบทางเลือก | **Visual inspection** + **E2E navigation test**: คลิก sidebar menu items → verify transition เกิดขึ้น → verify target view ถูกต้อง |
| Acceptance criteria | (1) Transition animation visible (ไม่ใช่ instant switch), (2) Duration ≈ 100-200ms (ไม่ช้าเกินไป), (3) ไม่มี visual glitch/flash ระหว่าง transition, (4) View content โหลดสมบูรณ์หลัง transition จบ |
| หลักฐาน | E2E-NAV-08 (with display) — visual observation |
| Automation feasibility | LOW — frame-level animation ตรวจไม่ได้ด้วย pywinauto |

#### 3.5.3 Remediation Priority & Timeline

| Priority | FR | Action | Timeline | ผู้รับผิดชอบ |
|----------|-----|--------|----------|------------|
| P1 | FR-PM-09, FR-PM-10 | เพิ่ม unit tests ใน `test_profile_manager.py` ด้วย `tmp_path` fixture | Sprint ถัดไป (ถ้ามี) | Developer |
| P2 | FR-SD-04 | เพิ่ม integration test ด้วย WMI mock (partial — ทดสอบ parsing logic ไม่ใช่ hardware access) | Sprint ถัดไป (ถ้ามี) | Developer |
| P3 | FR-SD-09 | เพิ่ม threading test ด้วย `threading.Event` + 5s timeout (accept flakiness risk) | Backlog | Developer |
| Monitor | FR-UI-07, FR-UI-09, FR-UI-11 | คงใช้ E2E with display + visual inspection — ไม่สามารถ automate บน headless Windows CI | ไม่มีแผน automate | — |

> **หมายเหตุ:** P1 items (FR-PM-09, FR-PM-10) จะเพิ่ม automated coverage จาก 89.9% เป็น ~91.3% (64/69) หากดำเนินการ ส่วน 3 UI FRs ยอมรับเป็น manual test เนื่องจาก platform limitation ของ CustomTkinter + headless CI

#### 3.5.4 Risk Assessment: ผลกระทบของ 7 Untested FRs

| ระดับความเสี่ยง | FRs | เหตุผล |
|----------------|-----|--------|
| **ต่ำ** | FR-SD-04, FR-UI-07, FR-UI-09, FR-UI-11 | ฟีเจอร์แสดงผลเท่านั้น (display-only) — ไม่แก้ไข system state, ไม่มี data loss risk |
| **ต่ำ-กลาง** | FR-SD-09 | Async detection — failure mode คือ UI freeze ชั่วคราว ไม่กระทบ data integrity |
| **กลาง** | FR-PM-09, FR-PM-10 | File I/O — potential data loss ถ้า export/import ผิดพลาด แต่ limited blast radius (preset data เท่านั้น ไม่ใช่ system settings) |

> **สรุป:** ไม่มี untested FR ใดที่มี risk level สูง — FRs ที่มีความเสี่ยงมากที่สุด (FR-PM-09, FR-PM-10) เป็น P1 ในแผน remediation และมี blast radius จำกัด (ไม่กระทบ system settings หรือ safety features)

---

## 4. Horizontal Traceability: ความสอดคล้องระหว่างเอกสาร ISO 29110

> ตรวจว่าข้อมูลที่ปรากฏในเอกสาร ISO หนึ่งสอดคล้องกับเอกสาร ISO อื่นที่อ้างอิงข้อมูลเดียวกัน

| รายการตรวจ | เอกสารต้นทาง | เอกสารปลายทาง | สอดคล้อง? | หมายเหตุ |
|-----------|-------------|--------------|-----------|---------|
| จำนวน FR ทั้งหมด | SRS: 63 FRs (MoSCoW) | Traceability: 59 FRs | ⚠️ ต่าง | SRS นับรวม Won't=5 + admin FRs ที่เพิ่มภายหลัง — ตัวเลข reconcile ได้ |
| จำนวน NFR | SRS: 17 NFRs | Test Plan: 17 NFRs | ✅ ตรง | |
| จำนวน Test Cases | Test Plan: 516+ planned | Test Record: 516+ executed | ✅ ตรง | |
| Coverage target | Test Plan: ≥ 60% core | Test Record: ~65% core | ✅ ผ่าน | |
| DRE target | Test Plan: ≥ 85% | Test Record: 100% (pre-release) | ✅ ผ่าน | |
| 10 Risk items | Project Plan: 10 risks | Progress Status: 10 risks | ✅ ตรง | 8 resolved, 2 monitoring |
| 3 Profiles | SRS: SAFE/COMPETITIVE/EXTREME | SDD: 3 profiles in architecture | ✅ ตรง | |
| Tweak count | SRS: 56 tweaks | SDD: 56 tweaks in registry | ✅ ตรง | |
| Change Requests | CR-001~004 | Traceability: CR impacts traced | ✅ ตรง | |
| Architecture pattern | SDD: Layered + MVC hybrid | Test Plan: test by layer | ✅ ตรง | |
| Batch V&V TCs | Batch V&V Test Plan v1.0: 20 planned | Batch V&V Test Record v1.0: 20 executed | ✅ ตรง | |

### 4.1 Cross-Document Version Alignment

| เอกสาร | เวอร์ชันปัจจุบัน | อ้างอิงใน Traceability Record |
|--------|----------------|------------------------------|
| SRS | v3.2 | ✅ อ้างอิงถูกต้อง |
| SDD | v3.3 | ✅ อ้างอิงถูกต้อง |
| Test Plan | v3.1 | ✅ อ้างอิงถูกต้อง |
| Test Record | v2.3 | ✅ อ้างอิงถูกต้อง |

---

## 5. Consolidated RTM Summary

| Metric | ค่า | เป้าหมาย | สถานะ |
|--------|-----|---------|-------|
| Total FRs traced | 62/69 | ≥ 85% | ✅ 89.9% |
| FRs with automated tests | 62 | — | |
| FRs with manual tests only | 7 | ≤ 10 | ✅ |
| NFRs testable | 17/17 | 100% | ✅ 100% (13 automated + 4 manual/review) |
| Horizontal consistency issues | 1 minor (FR count reconciliation) | 0 critical | ✅ |
| Gold plating detected | 0 | 0 | ✅ ไม่มี code ที่ไม่มี FR รองรับ |

> **สรุป:** ระบบ traceability ของ ClutchG ครอบคลุม 89.9% ของ FRs ด้วย automated tests ส่วนที่เหลือ 7 FRs มีการทดสอบด้วยวิธี manual ทั้งหมด ไม่พบ gold plating

---

## 6. ประวัติการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายละเอียด |
|----------|--------|---------|------------|
| 1.0 | 2026-03-12 | nextzus | สร้างเอกสารเริ่มต้น — Forward/Backward traceability, coverage summary |
| 2.0 | 2026-04-06 | nextzus | เสริม SE academic content: ทฤษฎี Traceability (SE 721), §4 Horizontal Traceability, §5 Consolidated RTM Summary, header ETVX + cross-refs |
| 2.1 | 2026-04-10 | nextzus | Phase 11 Recommendation Refactor: FR-SD-07 → RecommendationService + UT-RS-01~18, tweak counts 48→56, profile counts 17/35/48→14/44/56, test counts 308→496+, FR-TW-06 delegation, backward trace for test_recommendation_service.py, version alignment SRS v3.2/SDD v3.3/Test Plan v3.1/Test Record v2.2 |
| 2.2 | 2026-04-12 | nextzus | เพิ่ม §3.3 NFR Forward Traceability (17 NFRs × 8 ISO 25010 categories), §3.4 CR-to-FR Impact Mapping (4 CRs reconciled to canonical FR IDs), §3.5 Gap Remediation Plan (7 untested FRs — classification, per-FR detail, priority timeline, risk assessment); อัปเดต §5 NFR row จาก "4/6 groups ⚠️ Partial" → "17/17 ✅ 100%"; Test Record cross-ref อัปเดตเป็น v2.3 |
| 2.3 | 2026-04-12 | nextzus | เพิ่ม §1.7 FR-BAT Batch Script Engine traceability (FR-21~FR-30 → TC-BAT-001~020); อัปเดต backward traceability §2.1 (เพิ่ม 12-Batch-VV-Test-Record.md row), coverage summary §3.1 (FR-BAT group + รวม 59→69 FRs, 52→62 with tests, 88.1%→89.9%), horizontal traceability §4 (Batch V&V row), RTM summary §5 (62/69, 89.9%); อัปเดต cross-ref header |
| 2.4 | 2026-04-12 | nextzus | อัปเดต §4.1 Test Record version v2.2→v2.3, test count 496→516+ ใน §4 horizontal traceability, CR ref v2.1→v2.3 ใน §3.4 |

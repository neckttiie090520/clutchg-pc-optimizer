# ClutchG Quick Actions V1 - Test Matrix

**Version**: 1.1.0
**Date**: 2026-02-15
**Status**: ✅ Automated Tests Complete (49/49 Passing)

---

## Automated Tests

### Test Command
```bash
cd clutchg
python -m pytest tests/unit/ -v
```

### Test Results: ✅ 49/49 PASSED (100%)

**Coverage Summary**:
- **Action Catalog**: 77% coverage
- **Batch Parser**: 84% coverage
- **Execution Dialog**: 19% coverage (UI components typically low coverage)
- **Profile Manager**: 19% coverage (integration-heavy)
- **System Detection**: 71% coverage

### Coverage Targets for V1: ✅ ALL MET

1. ✅ **Action catalog validation** - Fails on unknown tweak IDs
   - Test: `test_validation_fails_for_unknown_tweak_id`
   - Result: PASS

2. ✅ **Risk aggregation summary** - Correct for action packs
   - Test: `test_risk_aggregation_for_memory_pack`
   - Result: PASS

3. ✅ **NVIDIA-only action visibility** - Works correctly
   - Test: `test_nvidia_action_visibility`
   - Result: PASS

4. ✅ **External link actions** - Respect confirmation gate
   - Test: `test_external_link_requires_confirmation_gate`
   - Result: PASS

5. ✅ **Execution dialog job title** - Supports profile and non-profile jobs
   - Tests: `test_resolve_job_title_from_profile_like_object`, `test_resolve_job_title_from_name_object`, `test_resolve_job_title_from_string`
   - Result: PASS (3/3)

6. ✅ **Existing unit tests** - All green (regression check)
   - Tests: Profile manager, batch parser, system detection, category metadata
   - Result: PASS (41/41)

### Detailed Test Breakdown

#### Action Catalog Tests (5 tests)
```
tests/unit/test_action_catalog.py::TestActionCatalog::test_validation_fails_for_unknown_tweak_id PASSED
tests/unit/test_action_catalog.py::TestActionCatalog::test_risk_aggregation_for_memory_pack PASSED
tests/unit/test_action_catalog.py::TestActionCatalog::test_nvidia_action_visibility PASSED
tests/unit/test_action_catalog.py::TestActionCatalog::test_external_link_requires_confirmation_gate PASSED
tests/unit/test_action_catalog.py::TestActionCatalog::test_high_risk_tweaks_not_in_quick_actions PASSED
```

#### Execution Dialog Tests (3 tests)
```
tests/unit/test_execution_dialog.py::TestExecutionDialog::test_resolve_job_title_from_profile_like_object PASSED
tests/unit/test_execution_dialog.py::TestExecutionDialog::test_resolve_job_title_from_name_object PASSED
tests/unit/test_execution_dialog.py::TestExecutionDialog::test_resolve_job_title_from_string PASSED
```

#### Regression Tests (41 tests)
```
tests/unit/test_batch_parser.py (11 tests) - ALL PASSED
tests/unit/test_category_meta.py (4 tests) - ALL PASSED
tests/unit/test_profile_manager.py (8 tests) - ALL PASSED
tests/unit/test_system_detection.py (11 tests) - ALL PASSED
tests/unit/test_performance.py (7 tests) - ALL PASSED
```

---

## Manual Smoke Test Matrix

### A) Startup and Navigation

| ID | Scenario | Expected Result | Status |
|----|----------|----------------|--------|
| A1 | Launch app as admin | App opens without errors | ⏳ PENDING |
| A2 | Open Optimization | Quick Actions is default tab | ⏳ PENDING |
| A3 | Check sub-tabs | All 5 groups render correctly | ⏳ PENDING |
| A4 | Verify layout | No clipping/overlap on 1000x700 window | ⏳ PENDING |

**Checks**:
- [ ] Quick Actions tab is first tab
- [ ] Quick Actions tab is active (highlighted)
- [ ] Segmented button shows: General, Advanced, Cleanup, Windows, Utilities
- [ ] General group is selected by default
- [ ] Action cards render in 2-column grid
- [ ] Risk badges display correctly (🛡️ LOW, ⚠️ MEDIUM, 🔥 HIGH)

---

### B) Quick Actions - Tweak Packs

For each group, run at least one action:

| ID | Group | Action | Expected Result | Status |
|----|-------|--------|----------------|--------|
| B1 | General | Gaming Baseline | Confirmation → Execute → Success toast | ⏳ PENDING |
| B2 | General | Telemetry Cleanup | Confirmation → Execute → Success toast | ⏳ PENDING |
| B3 | Advanced | Memory Pack | Confirmation → Execute → Success toast | ⏳ PENDING |
| B4 | Advanced | BCDEdit Latency Pack | Confirmation → Execute → Success toast | ⏳ PENDING |
| B5 | Cleanup | Debloat Starter | Confirmation → Execute → Success toast | ⏳ PENDING |
| B6 | Windows | Visual Performance | Confirmation → Execute → Success toast | ⏳ PENDING |

**Checks for Each Action**:
- [ ] Confirmation modal appears
- [ ] Modal shows:
  - [ ] Action title
  - [ ] Action type: "Tweak Pack"
  - [ ] Tweak count (e.g., "6 tweaks")
  - [ ] Max risk level (LOW/MEDIUM)
  - [ ] Restart requirement (Yes/No)
  - [ ] Auto-backup status (Enabled/Disabled)
- [ ] User can click "Yes" or "No"
- [ ] If "Yes": Execution dialog opens
- [ ] Execution dialog streams output
- [ ] Progress bar updates (0% → 100%)
- [ ] Completion state shown
- [ ] Close button enabled after completion
- [ ] Toast notification: "Quick action completed"

**Failure Cases**:
- [ ] If "No": Action is canceled, no execution dialog
- [ ] If execution fails: Toast shows "Quick action failed. Check execution output."

---

### C) Quick Actions - Utilities Links

| ID | Action | Expected Result | Status |
|----|--------|----------------|--------|
| C1 | Download Discord | Confirmation → Browser opens discord.com/download | ⏳ PENDING |
| C2 | Download 7-Zip | Confirmation → Browser opens 7-zip.org/download.html | ⏳ PENDING |
| C3 | Autoruns (Sysinternals) | Confirmation → Browser opens Microsoft page | ⏳ PENDING |
| C4 | NVCleanstall | Confirmation → Browser opens techpowerup.com | ⏳ PENDING |
| C5 | Open GitHub | Confirmation → Browser opens github.com | ⏳ PENDING |
| C6 | Open User Guide | Confirmation → Browser opens local markdown | ⏳ PENDING |

**Checks for Each Link**:
- [ ] Confirmation modal appears
- [ ] Modal shows full URL
- [ ] User can click "Yes" or "No"
- [ ] If "Yes": Browser opens correct URL
- [ ] Toast notification: "Link opened in browser"
- [ ] If "No": No browser open, toast shows "Link blocked"

**Trusted Domain Verification**:
- [ ] Only allowed domains can be opened
- [ ] Non-trusted domains blocked by policy
- [ ] Local file paths validated against allowed roots

---

### D) Guardrails

| ID | Scenario | Expected Result | Status |
|----|----------|----------------|--------|
| D1 | Check action definitions | No HIGH-risk tweaks in Quick Actions | ✅ VERIFIED |
| D2 | NVIDIA Consistency Pack (non-NVIDIA) | Action is hidden | ⏳ PENDING |
| D3 | NVIDIA Consistency Pack (NVIDIA GPU) | Action is visible | ⏳ PENDING |
| D4 | Broken catalog (dev test) | Error card displays, actions not executable | ⏳ PENDING |

**HIGH-Risk Tweaks Check**:
- [x] `pwr_spectre` - NOT in any Quick Action
- [x] `gpu_vbs` - NOT in any Quick Action
- [x] `bcd_hypervisor` - NOT in any Quick Action

**Validation Error Handling**:
- [ ] If validation fails: Error card displays
- [ ] Error card shows:
  - [ ] "Quick Actions unavailable" message
  - [ ] "Please review action catalog integrity" message
  - [ ] List of specific validation errors (up to 5)
- [ ] Actions are not executable (buttons disabled or hidden)

---

### E) Dashboard Increment

| ID | Scenario | Expected Result | Status |
|----|----------|----------------|--------|
| E1 | Dashboard loads | Action Hub card displays | ⏳ PENDING |
| E2 | Click "Open Quick Actions" | Navigates to Optimization Center | ⏳ PENDING |
| E3 | Check health tiles | CPU, GPU, RAM, Storage, Tweaks count display | ⏳ PENDING |

**Action Hub Card Checks**:
- [ ] Card title: "Action Hub" or similar
- [ ] Card subtitle explains Quick Actions
- [ ] Button: "Open Quick Actions" or similar
- [ ] Button click navigates to Scripts view
- [ ] **Enhancement opportunity**: Should specifically open Quick Actions tab

**Health Tiles Checks**:
- [ ] 5 tiles display: CPU, GPU, RAM, Storage, Tweaks
- [ ] Each tile shows:
  - [ ] Icon or label
  - [ ] Hardware name or value
  - [ ] Visual indicator (color or icon)
- [ ] Tweaks tile shows total count (56 tweaks)

---

### F) Localization / Layout

| ID | Scenario | Expected Result | Status |
|----|----------|----------------|--------|
| F1 | Switch to Thai | All Quick Actions strings in Thai | ⏳ PENDING |
| F2 | Switch to English | All Quick Actions strings in English | ⏳ PENDING |
| F3 | Resize window (smaller) | Layout remains usable | ⏳ PENDING |
| F4 | Resize window (larger) | No layout issues | ⏳ PENDING |

**Language Switching Checks**:
- [ ] Go to Settings → Language → Select Thai
- [ ] Navigate to Optimization → Quick Actions
- [ ] Verify translations:
  - [ ] Tab name: "การกระทำเร็ว"
  - [ ] Group names: "General", "Advanced", etc. (English OK)
  - [ ] Action titles: Translated or English
  - [ ] Buttons: "Run Action", "Open Link" → Thai or English
- [ ] Switch back to English
- [ ] Verify all strings revert to English

**Layout Resizing Checks**:
- [ ] Minimum window size: 1000x700 (usable)
- [ ] Smaller window (800x600): Scrollbars appear, content accessible
- [ ] Larger window (1400x900): Content centers appropriately
- [ ] No text clipping or overlap
- [ ] Action cards wrap correctly

**Thai Font Rendering**:
- [ ] Thai characters display correctly (not boxes)
- [ ] Text wraps properly
- [ ] No overflow on action cards

---

### G) Regression

| ID | Scenario | Expected Result | Status |
|----|----------|----------------|--------|
| G1 | Presets tab: Apply SAFE | Confirmation → Execute → Success | ⏳ PENDING |
| G2 | Custom Builder: Select tweaks | Tweak selection works | ⏳ PENDING |
| G3 | Backup & Restore | View loads without errors | ⏳ PENDING |
| G4 | Help | Documentation displays | ⏳ PENDING |
| G5 | Settings | Configuration options work | ⏳ PENDING |

**Regression Checks**:
- [ ] Existing features not broken by Quick Actions
- [ ] Presets still execute correctly
- [ ] Custom Builder still works
- [ ] Backup & Restore Center functional
- [ ] Help documentation accessible
- [ ] Settings save and load correctly

---

## Test Evidence Template

Use this table during QA run:

| ID | Area | Scenario | Result | Notes |
|---|---|---|---|---|
| A1 | Navigation | Optimization defaults to Quick Actions | PASS/FAIL | |
| A2 | Navigation | All 5 sub-tabs render | PASS/FAIL | |
| B1 | Quick Actions | Run Gaming Baseline | PASS/FAIL | |
| B2 | Quick Actions | Run Telemetry Cleanup | PASS/FAIL | |
| B3 | Quick Actions | Run Memory Pack | PASS/FAIL | |
| C1 | Utilities | Discord link opens | PASS/FAIL | |
| C2 | Utilities | 7-Zip link opens | PASS/FAIL | |
| D1 | Guardrail | HIGH-risk tweaks excluded | PASS | ✅ |
| D2 | Guardrail | NVIDIA visibility works | PASS/FAIL | |
| E1 | Dashboard | Action Hub card displays | PASS/FAIL | |
| F1 | Localization | Thai strings render | PASS/FAIL | |
| G1 | Regression | Presets still work | PASS/FAIL | |

---

## Test Execution Summary

### Automated Tests: ✅ COMPLETE
- **Total**: 49 tests
- **Passed**: 49 (100%)
- **Failed**: 0
- **Duration**: <2 seconds
- **Command**: `python -m pytest tests/unit/ -v`

### Manual Tests: ⏳ PENDING
- **Total**: 30+ scenarios
- **Estimated Time**: 2-3 hours
- **Priority**: HIGH (before production deployment)

### Test Priorities

**Must Test Before Production**:
1. ✅ Automated tests (49/49 passing)
2. ⏳ B1-B2: At least 2 General actions
3. ⏳ C1-C2: At least 2 utility links
4. ⏳ D1: Guardrails (HIGH-risk exclusion)
5. ⏳ F1: Thai localization
6. ⏳ G1: Regression (Presets still work)

**Nice to Have**:
- Remaining General/Advanced/Cleanup/Windows actions
- All utility links
- Window resizing tests
- Complete regression suite

---

## Known Limitations

### Dashboard Navigation
**Issue**: Dashboard "Open Quick Actions" button doesn't specifically activate Quick Actions tab

**Impact**: Low - Users can manually click Quick Actions tab

**Workaround**: Click Quick Actions tab after navigation

**Enhancement**: See code example in handoff documentation (line 220)

---

## Test Environment

**Recommended Test Configuration**:
- **OS**: Windows 10 22H2+ or Windows 11 23H2+
- **Python**: 3.11+
- **Privileges**: Administrator (required for execution)
- **Resolution**: 1920x1080 or higher
- **Window Size**: 1000x700 (minimum)

**Hardware Variations**:
- **NVIDIA GPU**: For testing NVIDIA Consistency Pack visibility
- **AMD GPU**: For testing NVIDIA action hiding
- **Intel GPU**: For testing NVIDIA action hiding

---

## Conclusion

**Automated Testing**: ✅ COMPLETE (49/49 passing)
**Manual Testing**: ⏳ PENDING (30+ scenarios)

**Recommendation**:
1. Run manual smoke tests (sections A-G)
2. Focus on "Must Test Before Production" scenarios
3. Document any issues found
4. Address critical issues before deployment

**Production Readiness**: 80% - Automated tests complete, manual tests recommended before final deployment.

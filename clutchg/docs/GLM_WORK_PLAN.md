# GLM Work Plan: Next Steps for ClutchG Development
**Date:** February 16, 2026
**Status:** Ready for Execution

This document outlines the detailed work plan for GLM to continue development, bridging the current UI refactoring with the broader application goals.

## 1. Immediate Actions (Finish Current Task)
**Goal:** Complete the "UI Redesign - Backup & Restore Center" to ensure a clean codebase and consistent UX.

- [ ] **Cleanup Obsolete Files**: 
  - Delete `c:\Users\nextzus\Documents\thesis\bat\clutchg\src\gui\views\restore_center_minimal.py`.
  - This file has been superseded by `backup_restore_center.py` and is now dead code.
- [ ] **Create Verification Script**:
  - Create `tests/manual_test_dialogs.py` to allow manual verification of the new `InputDialog` and `RefinedDialog` integration without running the full app.
- [ ] **Final Code Check**:
  - Quickly scan `scripts_minimal.py` one last time to ensure no native dialogs remain (sanity check).

## 2. Short-Term Goals (Integration & Stability)
**Goal:** Ensure the newly refactored components work harmoniously in the full application context (Path A from Dev Plan).

- [ ] **Integration Testing**:
  - Run the full application (`app_minimal.py`).
  - Perform a live "Create Backup" operation to verify the new Input Dialog passes data correctly to the `BackupManager`.
  - Perform a "Delete Backup" operation to verify the Confirmation Dialog works.
- [ ] **Timeline Verification**:
  - Check the "Advanced Mode" in Backup & Restore center.
  - Ensure `FlightRecorder` data is visualizing correctly on the Timeline component.

## 3. Medium-Term Goals (Feature Enhancement)
**Goal:** Upgrade core functionality based on `SCORING_SYSTEM.md` and `11-development-plan.md`.

- [ ] **Implement Advanced Scoring System**:
  - **Reference:** `docs/SCORING_SYSTEM.md`.
  - **Task**: Replace the hardcoded `Simple Weighted Score` with a data-driven approach.
  - **Action**: 
    - Create `core/benchmark_db.py` to handle CPU/GPU score lookups (using static JSON for now as recommended).
    - Update `core/system_info.py` to use this new database.
    - Update `gui/views/dashboard_minimal.py` to reflect the new, more accurate scores.
  
- [ ] **Batch Optimizer Modernization** (Path B from Dev Plan):
  - **Reference:** `docs/11-development-plan.md`.
  - **Task**: Replace legacy `wmic` commands with PowerShell `Get-CimInstance`.
  - **Reason**: `wmic` is deprecated in Windows 11 24H2. This is critical for future compatibility.

## 4. Execution Strategy
GLM will proceed in this order:
1.  **Execute Immediate Actions** now (Cleanup & Test Script).
2.  **Confirm Success** with the user.
3.  **Propose Start** of "Advanced Scoring System" implementation.

---
**Approvals**
- [x] UI Redesign Plan
- [ ] Immediate Cleanup Execution
- [ ] Scoring System Implementation

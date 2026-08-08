# 13 — Current Evidence Addendum

> **Standard context:** ISO/IEC 29110-5-1-2 — Project Management and Software Implementation evidence control  
> **Project:** ClutchG PC Optimizer  
> **Evidence date:** 2026-07-30  
> **Status:** `AUTOMATED_VERIFIED / EXTERNAL_VERIFICATION_REQUIRED / HUMAN_SIGN_OFF_REQUIRED`

## 1. Purpose

This addendum records the current executable evidence without rewriting historical work products. Earlier Test Records, remediation reports, and Hyper-V results remain valid only for the source baseline identified in those records. When a current claim conflicts with an older count, this addendum and its raw command output take precedence for the 2026-07-30 working tree.

## 2. Current automated baseline

Command executed from `clutchg`:

```text
python -m pytest tests/unit tests/integration --skip-slow --skip-e2e -q --tb=short
```

Result:

```text
765 collected
762 passed, 3 skipped, 0 failed
80.91 seconds
TOTAL Python coverage: 39%
backup_manager.py: 80%
batch_executor.py: 87%
```

Supporting checks:

- `python -m compileall clutchg/src -q` — passed.
- `git diff --check` on the current remediation/evidence files — passed; Windows LF-to-CRLF notices are warnings, not test failures.
- Bug Hunter targeted regression gate — 77 passed.
- Bug Hunter JSON consistency gate — passed.

Canonical evidence:

- `.bug-hunter/findings.json`
- `.bug-hunter/skeptic.json`
- `.bug-hunter/referee.json`
- `.bug-hunter/report.md`
- `docs/defense-readiness/01-current-evidence-matrix-2026-07-30.md`

## 3. Corrective-maintenance findings closed in this baseline

| Finding | Corrective control | Regression evidence |
|---|---|---|
| Registry restore accepted wildcard files and partial success | Fixed six-file contract, preflight completeness, success only when every import succeeds | `clutchg/tests/unit/test_backup_manager.py` restore tests |
| Same-second backup ID collision | Atomic unique directory allocation with deterministic suffix | `test_same_second_backups_get_unique_ids_and_directories` |
| Backup GUI reported failed recovery artifacts as success | Both backup views require `backup.success` | `test_backup_views_require_successful_recovery_artifacts` |
| Batch output result could omit lines drained after process exit | Reader threads drain before result construction in success, timeout, and error paths | `test_execute_drains_reader_threads_before_building_result` |

## 4. Interpretation limits

`AUTOMATED_VERIFIED` means that unit, integration, static-contract, compilation, and patch-integrity checks passed in their stated scope. It does not prove:

- real privileged Registry, service, power, BCDEdit, or rollback behavior on the current source;
- compatibility across all Windows versions or hardware;
- performance improvement on user hardware;
- a real Authenticode-signed CI release;
- installer upgrade and relaunch behavior in a disposable VM;
- usability or acceptance by representative users.

The measured total coverage is **39%**. Any requirement or thesis statement claiming `>=70%` or `>=85%` must either define and reproduce a different scoped metric or remain an unresolved target. It must not be reported as a current result.

## 5. Historical versus current evidence

| Evidence | Classification | Allowed use |
|---|---|---|
| `docs/iso29110-clutchg/12-Batch-VV-Test-Record.md`, 20/20 on 2026-04-12 | `HISTORICAL_VERIFIED` | Shows prior Hyper-V V&V method and result for that baseline; not proof for post-remediation source |
| `REMEDIATION_REPORT_2026-05-30.md`, 756 passed / 3 skipped | Historical automated baseline | Shows corrective-maintenance progression |
| This addendum, 762 passed / 3 skipped | Current automated baseline | Current automated claim for the working tree tested on 2026-07-30 |
| Fresh Sandbox/VM results for current source | `EXTERNAL_VERIFICATION_REQUIRED` | Required before current privileged-runtime claim |
| Advisor/UAT/final-PDF approval | `HUMAN_SIGN_OFF_REQUIRED` | Required before institutional or acceptance claim |

## 6. Open external gates

1. Freeze a reviewed source baseline with commit/tag or archive SHA-256.
2. Run default, no-GPU, and no-network Windows Sandbox configurations; retain text, JSON, and summary artifacts.
3. Run one low-risk apply → verify → rollback cycle in a disposable environment and compare before/after state.
4. Resolve every WARN/SKIP with owner and reviewer disposition; no P0 safety case may be skipped.
5. Provision controlled signing credentials and run a version-parity CI tag build.
6. Retain hashes and Authenticode status/subject for the application and installer.
7. Perform installer upgrade/relaunch smoke testing in a disposable VM.
8. Obtain researcher and advisor sign-off on the final evidence matrix, thesis text, and PDF formatting.

Execution details and evidence templates are in:

- `docs/iso29110-clutchg/04a-Sandbox-VV-Plan.md`
- `docs/defense-readiness/03-human-validation-checklist-2026-07-30.md`
- `docs/defense-readiness/04-github-project-backlog-draft-2026-07-30.md`

## 7. ISO/SDLC disposition

| SDLC / ISO concern | Current disposition |
|---|---|
| Requirements and traceability | Existing records present; source lines, test counts, and coverage claims require refresh against this baseline |
| Design | Layered architecture remains the design model; diagrams used in defense require current-source review |
| Construction | Corrective and preventive maintenance implemented with focused regressions |
| Integration and testing | Automated host-safe gate passed; privileged runtime and acceptance remain external/human gates |
| Configuration management | Working tree is not yet an immutable official baseline |
| Delivery | Real signed release and installer smoke test are not yet verified |
| Maintenance | Historical audit → remediation → current rebaseline provides an auditable corrective-maintenance trail |

## 8. Approval block

| Role | Name | Decision | Date | Signature/reference |
|---|---|---|---|---|
| Researcher |  |  |  |  |
| Technical reviewer |  |  |  |  |
| Advisor |  |  |  |  |

No document or automated result guarantees a defense outcome. Final acceptance belongs to the advisor, committee, and institution.

# 13 — Regression and Validation Report (2026-08-06)

> **Standard context:** ISO/IEC 29110-5-1-2 — Software Implementation: Verification, Testing, Product Delivery
> **Project:** ClutchG PC Optimizer
> **Scope of this report:** the closing validation pass over the remediation recorded in
> [12 — Audit Handoff](12-audit-handoff-2026-08-05.md). It re-runs the broad suites, re-scans every path
> the remediation touched, and states what is still not verified.
> **Verdict:** `AUTOMATED_VERIFIED` for the static, unit, integration, and read-only-runtime scope.
> `EXTERNAL_VERIFICATION_REQUIRED` for two privileged mutations and for the packaged signed installer.

---

## 1. Environment and revision

Every figure below was produced in this environment. A figure quoted without one of these commands is not
evidence.

| Field | Value |
|---|---|
| Date | 2026-08-06 |
| Platform | `Windows-11-10.0.22631-SP0` |
| Python | 3.14.2 (MSC v.1944, 64-bit) |
| pytest | 9.0.2 |
| Branch | `audit/project-verification-2026-07-29` |
| Revision under test | `8359915` |
| Commits ahead of `main` | 23 |
| Working tree | not frozen — figures identify this revision's content, not a signed release baseline |

---

## 2. Broad validation

| Suite | Command | Result |
|---|---|---|
| Unit | `cd clutchg && python -m pytest tests/unit -q` | **1055 passed, 0 failed** |
| Integration | `cd clutchg && python -m pytest tests/integration -q` | **23 passed, 0 failed** |
| Combined | `cd clutchg && python -m pytest tests/unit tests/integration -q` | **1078 passed, 0 failed** |
| E2E | `cd clutchg && python -m pytest tests/e2e --collect-only -q` | **64 collected, 0 run** — needs a live desktop session |
| Syntax | `python -m compileall -q clutchg/src` | clean, no output |

### 2.1 Coverage — two scopes, not interchangeable

| Scope | Command | Result |
|---|---|---|
| Core business logic | `cd clutchg && python -m pytest tests/unit tests/integration -c /dev/null -o addopts="" --cov=src/core --cov-report=term` | **81%** against the ISO target of ≥70% |
| Repository-wide | `cd clutchg && python -m pytest tests/unit tests/integration` | **40%** |

The repository-wide figure is diluted by `src/gui/**`, where CustomTkinter view modules need a live desktop
session. `pytest.ini` hard-codes `--cov=src` in `addopts`, so a naive run always prints the lower number —
the `-c /dev/null -o addopts=""` prefix is required to measure the core layer. **Do not quote 40% against the
≥70% target, and do not quote 81% as whole-repository coverage.**

Per-module core coverage at this revision:

| Module | Cover | Module | Cover |
|---|---|---|---|
| `tweak_registry` | 100% | `flight_recorder` | 89% |
| `recommendation_service` | 97% | `batch_executor` | 88% |
| `benchmark_database` | 95% | `config` | 85% |
| `help_manager` | 95% | `action_catalog` | 84% |
| `profile_recommender` | 92% | `profile_manager` | 83% |
| `batch_parser` | 91% | `backup_manager` | 82% |
| `system_snapshot` | 89% | | |

Three modules sit below 80% and all three are bounded by privileged or platform-specific code paths:
`updater` 66% (Authenticode / WinVerifyTrust and installer handoff), `system_info` 64% (WMI hardware probes),
`paths` 63% (PyInstaller frozen-mode branches). These are recorded `EXTERNAL_VERIFICATION_REQUIRED`. They were
deliberately **not** closed with mocks, because a mock in these positions asserts the mock rather than the
behaviour.

---

## 3. Targeted re-scan of the remediated paths

Each remediation slice was re-run against its own regression set at this revision.

| Remediated area | Test modules | Result |
|---|---|---|
| Action contracts, dispatch integrity, audit regressions, batch safety transactions, profile/batch contracts, plan-mode gating, recovery-mechanism contract | `test_batch_dispatch_integrity`, `test_action_catalog`, `test_action_catalog_extra`, `test_audit_regressions`, `test_batch_safety_transactions`, `test_profile_batch_contracts`, `test_plan_mode_gating`, `test_recovery_mechanism_contract` | **242 passed** |
| Command injection, backup-ID hardening, persistence locking and atomicity | `-k "injection or hardening or lock or atomic"` across `tests/unit` | **131 passed, 916 deselected** |
| Truthfulness guards | `test_iso_metric_currency`, `test_registry_claim_fidelity`, `test_traceability_record_fidelity` | **118 passed** |

The truthfulness guards matter more than their count suggests: each recomputes ground truth from the
repository rather than trusting a hand-written claim, and each carries a companion test proving it can fail
(`test_every_registry_declaring_tweak_is_actually_compared`,
`test_the_ceiling_is_tight_enough_to_actually_fail`, `TestGuardDiscriminates`). **A passing contract test is
evidence only once it has been shown to reject a synthetic violation.**

`test_iso_metric_currency` was extended during this pass to scan the defense-readiness pack as well as the ISO
work products. Until then it guarded only `docs/iso29110-clutchg/**`, so the figures quoted in this very report
and in the handoff could have gone stale silently — the pack a panel actually reads was the one part not
covered. Two new cases pin the extension: one asserts each listed defense document resolves under
`docs/defense-readiness` and exists, the other confirms the scanner still flags an injected violation. Verified
by mutation: appending a table row claiming a unit-test total of four nines fails
`test_no_recorded_total_exceeds_the_collectable_suite` with `ceiling 1224`. The dated 2026-07-30 documents are
deliberately excluded — they are a snapshot of that round and legitimately carry the figures of the day.

Extending the guard added 8 tests, which changed the totals in §2 — the guard immediately caught its own
report. It then caught this section too: an earlier draft spelled that mutation example out as a literal
figure, and the scanner correctly read it as a claim. The example is described in words above for that reason.
Both catches are the intended behaviour, and the reason the figures in §2 were re-measured after the change
rather than carried over.

---

## 4. Read-only runtime validation

Static tests cannot prove that capture and restore round-trip real machine state. Four layers now do, without
a VM.

| Layer | Proves | Result |
|---|---|---|
| Plan-mode execution | Dispatch, argument validation, manifest shape, control flow, the full 19-component backup plan and 18-component restore plan | both engines `rc=0`, `state=COMMITTED` / `state=COMPLETED`, nothing written to `BACKUPS_DIR` |
| Scratch-key round-trip | `reg add` / `reg delete` genuinely restore captured value state (15 of 19 components) | **3 of 3 cases PASS** |
| Scratch-scheme round-trip | `powercfg /getactivescheme` capture and `/setactive` restore | **PARTIAL** — reactivation verified; `/export` needs `SeBackupPrivilege` |
| Service capture round-trip | `sc qc` / `sc query` / `reg query` capture writes a state file the restore parser accepts, whose start type maps to a legal `sc config` argument | **PARTIAL** — `sc config` needs elevation |

Harness result at this revision:

```
clutchg\tests\vv\verify-recovery-mechanism.bat %TEMP%\clutchg-vv-state

CASE|existing_value|PASS|restored=0x7
CASE|absent_value|PASS|value-removed-key-kept
CASE|absent_key|PASS|key-removed
CASE|power_scheme|PARTIAL|export-needs-elevation|guid-capture-and-reactivate-verified
CASE|service_capture|PARTIAL|sc-config-needs-elevation|capture-round-trips-to-arg-disabled
RESULT|passed=3|partial=2|failed=0
```

The harness copies the capture and restore blocks from `backup-registry.bat` and `rollback.bat` **verbatim**,
then drives them against a scratch key it creates and deletes (`HKCU\Software\ClutchG-VV-Scratch`) and a
throwaway power scheme it duplicates and deletes. No real Windows setting is touched, so it is safe on a
development machine. The scratch key was confirmed absent before and after; the active scheme and scheme count
were confirmed unchanged.

Two things keep this from being theatre. It is **mutation-tested** — replacing `/d "!VALUE_DATA!"` with `/d 0`
in the restore makes case 1 fail with `data=0x0|expected=0x7`. And because a verbatim copy can fossilise,
`tests/unit/test_recovery_mechanism_contract.py` (21 cases) asserts every capture and restore statement still
appears in **both** the harness and the shipped engine, that the harness writes only to the scratch key, and
that the two elevation-bounded cases increment `CASES_PARTIAL` and never `CASES_PASSED`.

One cosmetic artefact: the harness emits `The system cannot find the drive specified.` on stderr from the
unelevated `/export` attempt. It survives redirection because CMD emits it directly. Exit status and machine
state are both verifiably correct, so it is noise rather than a failure.

---

## 5. Residual risk register

Stated plainly so a reviewer does not discover them instead.

| ID | Risk | Status | What would close it |
|---|---|---|---|
| R-01 | `bcdedit /import` has never executed against a real boot configuration | `EXTERNAL_VERIFICATION_REQUIRED` | Disposable Windows Sandbox/VM run with before/after BCD store evidence and the committed backup ID, `manifest.ini`, `journal.log` retained |
| R-02 | `sc config` has never executed to return a service to its recorded start type. Capture is verified; restore is not | `EXTERNAL_VERIFICATION_REQUIRED` | Same VM run, with before/after start types for the affected services |
| R-03 | 64 E2E tests collected, never run | `EXTERNAL_VERIFICATION_REQUIRED` | A live Windows desktop session with `pywinauto` |
| R-04 | Packaged installer signing and release provenance unverified. The updater's SHA-256 re-check before launch is a tamper guard, **not** independent provenance | `EXTERNAL_VERIFICATION_REQUIRED` | CI build with the provisioned publisher certificate, signature evidence retained |
| R-05 | Journaled batch transactions accumulate without bound. `_cleanup_old_backups` prunes only `backup_index.json` entries | **Deliberately open — a decision, not a bug** | A visible, configurable retention policy, or an explicit "Clean up old recovery data" action with its consequence stated. Silently deleting the artifact that makes an older change reversible would weaken the product's own reversibility guarantee |
| R-06 | `max_backups` config key is read by nothing; `_cleanup_old_backups` uses a hard-coded `DEFAULT_INDEX_RETENTION`. A value of `-5` is accepted without complaint | Open, low severity | Part of the R-05 retention decision, not a separate cleanup |
| R-07 | Findings were verified by one reviewer, not two. Sub-agent dispatch failed on quota errors mid-audit; the two affected lenses (GUI/threading, batch-engine semantics) were then covered by direct review and both produced findings | Open | A second independent reviewer over §3–§6 of the handoff. Treat the findings as verified and the *absence* of further findings as less certain |
| R-08 | `updater` 66%, `system_info` 64%, `paths` 63% core coverage | `EXTERNAL_VERIFICATION_REQUIRED` | Real Authenticode verification, real WMI probes, a real frozen build. Not mocks |
| R-09 | Working tree is not frozen and the branch is not merged. PR #13 into `develop` is mergeable | Human gate | Review and merge, then tag `v1.0.4` — the release workflow cross-checks all four version surfaces and fails the build on any mismatch |

---

## 6. What this report does and does not license

**Defensible at this revision:** the remediation is implemented and regression-covered; the recovery mechanism
round-trips real registry values and reactivates a real power scheme; the service capture produces a state file
the restore parser accepts; plan mode is proven not to mutate the host; command injection at the batch boundary
is closed by refusal rather than escaping; core-layer coverage is 81% against a ≥70% target.

**Not defensible at this revision:** any claim of full runtime validation, any claim of release or signing
validation, any claim that BCD or service restore has executed, and any use of 40% and 81% as if they were the
same measurement.

The single remaining technical gate is the disposable-VM run covering R-01 and R-02. Everything else on the
critical path is a human decision — merge, tag, advisor review, mock defence.

---

## 7. Reproduction

```powershell
# broad
cd clutchg
python -m pytest tests/unit -q
python -m pytest tests/integration -q
python -m pytest tests/e2e --collect-only -q

# coverage, both scopes
python -m pytest tests/unit tests/integration -c /dev/null -o addopts="" --cov=src/core --cov-report=term
python -m pytest tests/unit tests/integration

# targeted re-scan
python -m pytest tests/unit/test_batch_dispatch_integrity.py tests/unit/test_action_catalog.py `
  tests/unit/test_action_catalog_extra.py tests/unit/test_audit_regressions.py `
  tests/unit/test_batch_safety_transactions.py tests/unit/test_profile_batch_contracts.py `
  tests/unit/test_plan_mode_gating.py tests/unit/test_recovery_mechanism_contract.py -q --no-cov
python -m pytest tests/unit -q --no-cov -k "injection or hardening or lock or atomic"
python -m pytest tests/unit/test_iso_metric_currency.py tests/unit/test_registry_claim_fidelity.py `
  tests/unit/test_traceability_record_fidelity.py -q --no-cov

# syntax, from the repository root
cd ..
python -m compileall -q clutchg/src

# read-only runtime V&V — safe on a development machine
clutchg\tests\vv\verify-recovery-mechanism.bat $env:TEMP\clutchg-vv-state
```

---

## 8. Approval block

| Role | Name | Decision | Date | Signature / reference |
|---|---|---|---|---|
| Researcher | | | | |
| Technical reviewer | | | | |
| Advisor | | | | |

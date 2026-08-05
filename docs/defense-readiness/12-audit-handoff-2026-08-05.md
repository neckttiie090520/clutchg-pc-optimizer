# 12 — Audit Handoff Record (2026-08-05)

> **Standard context:** ISO/IEC 29110-5-1-2 — Verification, Corrective Maintenance, Project Closure
> **Project:** ClutchG PC Optimizer
> **Session scope:** end-to-end audit against SE / SDLC / ISO 29110, adversarial bug hunt, three scrutiny passes
> **Evidence status:** `AUTOMATED_VERIFIED` for static and unit scope; `EXTERNAL_VERIFICATION_REQUIRED` for privileged Windows mutation, rollback, and packaged-installer behaviour
> **Repository state:** committed and pushed as 8 commits on `audit/project-verification-2026-07-29`, released as **v1.0.4**, open for review as PR #13 into `develop` (mergeable). Not yet merged.

---

## 1. What this session actually established

The audit found one dominant defect class and one security defect. Neither was a crash; both were claims the implementation did not support.

**Defect class — truthfulness drift.** User-facing metadata and ISO work products asserted capabilities and measurements the engine did not deliver. Individually harmless; collectively fatal at a defence, because a panel that spot-checks any single claim against the code finds it wrong.

**Security defect — command injection at the batch boundary.** Introduced during this session's own remediation work, then found and closed by the bug hunt. Detailed in §3.

The transferable finding is methodological and is the strongest thing to present at the defence: **the same defect class reproduced three times — in the product, in the guard written to catch it, and in the repair of that guard.** Each recurrence was caught only by attacking the previous fix, never by trusting its passing result.

---

## 2. Verified state as of this handoff

| Measure | Value | How to reproduce |
|---|---|---|
| Unit tests | 1043 passed, 0 failed | `cd clutchg && python -m pytest tests/unit -q` |
| Integration tests | 23 passed, 0 failed | `cd clutchg && python -m pytest tests/integration -q` |
| Combined | 1066 passed, 0 failed | `cd clutchg && python -m pytest tests/unit tests/integration -q` |
| E2E | 64 collected, 0 run | Requires a live Windows desktop session; CI intentionally excludes |
| Core-layer coverage | 81% (target ≥ 70%) | `cd clutchg && python -m pytest tests/unit tests/integration -c /dev/null -o addopts="" --cov=src/core --cov-report=term` |
| Repository-wide coverage | 39% | `cd clutchg && python -m pytest tests/unit tests/integration` |
| Syntax | clean | `python -m compileall -q clutchg/src` |
| Tweak registry | 44 records — LOW 34, MEDIUM 9, HIGH 1 | `core/tweak_registry.py` |
| Audited executable contracts | 3 | `core/action_catalog.py` |

**The two coverage figures are different scopes and must not be interchanged.** The ≥70% ISO target applies to the core business-logic layer, which is at 81%. The repository-wide 39% is diluted by `src/gui/**`, where CustomTkinter view modules require a live desktop session. Note that `pytest.ini` hard-codes `--cov=src` in `addopts`, so a naive run always produces the lower, misleading number — the `-c /dev/null -o addopts=""` prefix is required to measure the core layer.

Three core modules sit below 80% and all three are bounded by privileged or platform-specific paths: `updater` 66% (Authenticode / WinVerifyTrust and installer handoff), `system_info` 64% (WMI hardware probes), `paths` 63% (PyInstaller frozen-mode branches). These are recorded as `EXTERNAL_VERIFICATION_REQUIRED`. They were deliberately **not** closed with mocks, because a mock in these positions asserts the mock rather than the behaviour.

---

## 3. Security correction — command injection at the batch interface

**Mechanism.** Windows executes `.bat` targets through `cmd.exe`, which acts on shell metacharacters *before* the batch script's first line runs. Verified empirically on Python 3.14.2: `subprocess.run([abs_path_to_bat, "a&whoami"])` with no `shell=True` still executes `whoami`. A batch script's own input validation therefore cannot defend its interface — `:validate_backup_id` in `src/safety/rollback.bat` runs after the split has already happened.

**Exposure.** `%APPDATA%\ClutchG\backups` is writable by an unprivileged user; the application requests elevation (`ClutchG.spec`, `uac_admin=True`); `&` is legal in an NTFS directory name. A directory named `2026-01-01_00-00-00&<command>` containing a valid `manifest.ini` was discoverable, and its name was passed verbatim as the restore argument. This crosses a real privilege boundary: content an unprivileged process controls becomes a command in an elevated one.

**Controls added**, each independently sufficient:

| Boundary | Control | Location |
|---|---|---|
| Discovery | Only exact timestamp-shaped directory names are recognised | `core/backup_manager.py` — `JOURNALED_BACKUP_ID_PATTERN` |
| Restore | Shape re-checked immediately before reaching `cmd.exe` | `core/backup_manager.py::_restore_journaled_backup` |
| Execution | Any argument **or script path** containing `& \| < > ^ " ' \`` newline or NUL is refused | `core/batch_executor.py::_argument_is_shell_safe` |

Design notes worth defending: the guard **refuses rather than escapes**, because every legitimate caller passes a label, a fixed keyword, or a timestamp — refusal rejects no valid input. The pattern uses `\A`/`\Z` rather than `^`/`$`, because `$` also matches before a trailing newline (a hole found by challenging the first version of the fix). The **script path** is validated as well as the arguments, because it is the first token on the command line and splits identically.

**Regression coverage:** `TestBatchArgumentInjection` (11 cases), `TestScriptPathInjection` (2), `TestJournaledBackupIdHardening` (12). Each asserts the process is *never spawned*, not merely that the call returns failure.

**Audited and found already sound, left unchanged:** `_sanitize_restore_point_name` (strips rather than escapes PowerShell metacharacters, so it fails safe); all `reg.exe` invocations (list argv, no shell); the updater handoff (`INSTALLER_NAME_PATTERN.fullmatch`, ACL-locked ProgramData staging, SHA-256 re-verification immediately before launch).

---

## 4. Recovery reachability correction

Two defects meant a committed backup was not a usable recovery capability.

1. **Root divergence.** The batch engine defaulted its backup root to `%SCRIPT_DIR%..\backups` — inside the program directory when frozen, and removed on uninstall — while the Restore Center read `%APPDATA%\ClutchG\backups`. `BatchExecutor` now pins `BACKUPS_DIR` for every batch launch so both writer and reader agree.
2. **Format divergence.** Journaled transactions store `registry-values\*.state` with a component manifest; the Python index format stores `registry\*.reg`. `restore_registry` would have attempted `reg import` and always failed. Journaled transactions are now discovered from `manifest.ini` and routed to `safety\rollback.bat`; an uncommitted (`state=FAILED`) transaction is refused rather than partially restored.

---

## 5. Truthfulness guards now standing

Three static contract tests recompute ground truth from the repository rather than trusting hand-written claims:

| Guard | Asserts |
|---|---|
| `test_registry_claim_fidelity.py` | Every declared registry key is actually written by the routed batch label; declared hive matches written hive |
| `test_traceability_record_fidelity.py` | Every test file cited in the traceability record exists |
| `test_iso_metric_currency.py` | No superseded metric is stated as current; recorded totals cannot exceed a tight collectable ceiling |

**Every one of these was subsequently attacked, and three of the four had a real weakness.** This history is the honest part of the record:

- `_written_keys` shipped with a broken escape (`\[^"]+`), so its helper-call branch matched nothing. Because the engine writes most values through `call :reg_set "HIVE\..."` wrappers rather than bare `reg add`, the guard silently compared **13 of 28** records and reported the other 15 as passing — including `inp_priority_sep`, the very record the guard was cited as having verified.
- After repair it still dropped `pwr_epp` (its label uses `powercfg`, writes no registry key), and the coverage floor had been written as `>= declaring - 2`, letting 27-of-28 pass with margin. Both fixed: the floor is exact and the drop-if-no-keys branch is gone.
- `test_iso_metric_currency` used a `20 ×` ceiling against a ratio of roughly 1.3 — about 14× headroom, unfalsifiable — and exempted *any* line containing `→`, so a stale claim beside a legitimate progression was waved through.

Each guard now carries a companion test proving it can fail: `test_every_registry_declaring_tweak_is_actually_compared`, `test_the_ceiling_is_tight_enough_to_actually_fail`, `TestGuardDiscriminates`.

**Rule to carry forward: a passing contract test is evidence only once you have shown it rejects a synthetic violation.**

### 5.1 Batch-engine lens — component symmetry verified, one overstatement found

The `components=` manifest (`src/backup/backup-registry.bat:157`) declares nineteen components: fifteen exact registry values plus `services`, `bcd`, `power_scheme`, `system_info`. Each of the fifteen is captured by `:backup_registry_value` and restored by `:restore_registry_value` in matching order; each of the remaining four has a corresponding `:restore_*` label. **No component is backed up without being restorable, and none is restored that was never captured** — there is no reversibility hole in the journaled path.

One defect: `:restore_system_info_component` called `record_restore_result "system_info" 0`, incrementing `RESTORE_SUCCESS` and journaling `SUCCESS` — but `systeminfo.txt` is a diagnostic capture with nothing to write back, so the label restored nothing. The restore journal claimed one more component recovered than the engine recovered. Now journals `REFERENCE_ONLY` / `REFERENCE_MISSING` and does not count toward the success total.

The two journals are deliberately distinct: backup validation (`rollback.bat:207`) requires `RESULT|system_info|SUCCESS` in `journal.log`, where the capture genuinely succeeded; the restore path writes `restore-journal.log`. Conflating them would either weaken backup validation or resurrect the overstatement. Both pinned by `test_system_info_is_journaled_as_reference_not_as_restored_state` and `test_backup_journal_verification_is_unaffected_by_restore_journal`.

### 5.2 GUI/threading lens — model is correct, invariant now pinned

Tkinter allows widget access only from the main thread, and profile/tweak application runs on `threading.Thread(daemon=True)` workers. All four worker bodies (`profiles_minimal.py:411`, `scripts_minimal.py:925`, `:1836`, `:3094`) touch only `ExecutionDialog` callbacks and `app.toast.*`. Every one of the five worker-facing callbacks — `add_output`, `set_progress`, `add_tweak_status`, `show_result`, `show_diff` — tests `threading.current_thread() is not threading.main_thread()` and re-posts through `after(0, ...)` before touching a widget; `ToastManager` marshals via `parent.after(0, callback, *args)`. **No unguarded cross-thread widget access exists.**

This invariant breaks silently — a new callback omitting the guard yields intermittent corruption, not a clean failure — so `TestThreadMarshallingInvariant` asserts it statically for all five. Mutation-tested: removing the guard from `show_diff` makes it fail.

### 5.3 Persistence durability — three silent-data-loss sites

A `/bug-hunter` scan of the core layer found that every JSON persistence path overwrote its target in place, and **every reader fails open** — swallowing a parse error and returning empty or defaults. A partial write therefore causes silent loss rather than a visible failure:

| File | Reader on truncated JSON | Consequence |
|---|---|---|
| `backup_index.json` | returns `[]` | **Every index-format backup becomes invisible to the Restore Center** while still on disk. Verified: writing `[{"id": "20260101_120000", "name": "impor` recovers 0 entries. |
| `user_config.json` | falls back to defaults | Language, theme, and confirmation preferences silently reset. |
| `custom_presets.json` | `except: pass`, then overwrites | **Every other saved preset discarded**, nothing logged. |

All three now write to a temporary file in the same directory, `fsync`, then `os.replace` — atomic on Windows for a same-volume rename — with a `finally` that removes the temp file on failure. `save_custom_preset` additionally *refuses* to overwrite a file it could not parse, rather than treating it as empty.

Scrutiny of that fix found three more defects, each of which is the interesting part of the record:

1. **`ConfigManager.save_config` had no lock.** `updater.py:1016` writes from a background thread while `settings_minimal.py:475` writes from the GUI thread through the same manager. Two concurrent `os.replace` calls on Windows make one fail with `PermissionError`; the method returns `False` and logs, so the user's setting vanishes. Measured: **32 of 240 concurrent saves dropped before the lock, 0 of 240 after.**
2. **`BackupManager` locked the file write but not the list mutation.** `delete_backup` and `_cleanup_old_backups` performed a read-modify-write on `self.backups` outside `_index_lock`, so two concurrent deletes could each start from a stale snapshot — leaving **an index entry whose directory had already been removed**, i.e. a backup the UI offers that cannot be restored. Both now hold the lock across the whole mutation, and `_save_index` was split into a locking wrapper plus `_write_index_unlocked` so the non-reentrant lock is never acquired twice.
3. **`reset_to_defaults` deleted the config file outside the lock**, able to interleave with a save.

**A test-quality correction worth stating.** One new test asserted the lock by grepping the source for `with self._write_lock:` — which would pass against a no-op lock. It was replaced with one that observes `_write_lock.locked()` from inside the write, and mutation-tested: substituting a no-op lock makes it fail. A separate pre-existing test had to be repaired rather than deleted, because it patched `builtins.open`, which the atomic path no longer calls — it would have passed without exercising the failure branch at all.

Also found and deliberately left: the `max_backups` config key is read by nothing (`_cleanup_old_backups` uses a hard-coded limit, now named `DEFAULT_INDEX_RETENTION`), and a value of `-5` is accepted without complaint. Honouring the key is part of the retention decision in §7.2, not a cleanup.

---

## 6. Registry records corrected

Seven records asserted behaviour the engine does not implement. All were corrected to describe what the routed label actually does, and fabricated performance figures were removed.

| Record | Claimed | Actual |
|---|---|---|
| `gpu_dwm` | `HKLM\...\Dwm` | `HKCU\...\DWM` (per-user) |
| `net_netbios` | "Disable NetBIOS over TCP/IP" | `EnableLMHOSTS=0` only; NetBIOS stays enabled |
| `inp_data_queue` | mouclass **and** kbdclass | mouclass only in `:apply_mouse` |
| `inp_priority_sep` | written by `input-optimizer.bat:apply_latency` | written by `registry-utils.bat:apply_gaming_tweaks` |
| `vis_visual_fx` | `VisualFXSetting=3`, "5-10% on low-end GPUs" | Those strings appear nowhere in `src/` |
| `pwr_epp` | `...\Power\PowerSettings`, "1-3% FPS" | `powercfg /setacvalueindex`; no registry write |
| `tel_diagtrack` | `...\Services\DiagTrack` | **Record was correct** — `sc config` persists there; the guard was too narrow |

---

## 7. Work that is genuinely yours — not automatable

These cannot be closed by tooling and are the gate to defence readiness.

### 7.1 Privileged runtime verification

Verification now stands in three layers. The first two are complete; the third is what remains.

| Layer | Proves | Status |
|---|---|---|
| Static contract tests | Component symmetry, plan-mode gating, claim fidelity, no injectable argument | **Complete** — 1066 tests |
| Plan-mode execution | Dispatch, validation, manifest shape, control flow, the full 19/18-component plans | **Complete** — both engines rc=0, nothing mutated |
| Scratch-key round-trip | `reg add`/`reg delete` genuinely restore captured value state (15 of 19 components) | **Complete** — 3/3 cases pass |
| Scratch-scheme round-trip | `powercfg /getactivescheme` capture and `/setactive` restore (1 further component) | **Complete** — reactivation verified; `/export` needs elevation |
| VM privileged run | `bcdedit /import` and `sc config` against real machine state (2 components) | **Outstanding** |

What the VM run still needs to cover, now narrowed to two components:

1. In a disposable Windows Sandbox or VM, run each of the three audited actions.
2. Preserve the committed backup ID, `manifest.ini`, `journal.log`, and before/after evidence for the BCD store and the affected services' start types.
3. Restore the exact backup leaf and confirm both return to their recorded state. (Registry values and the power scheme are already verified — see below.)
4. Test cancellation and an injected command failure *after* snapshot commit.
5. Record exact counts, durations, and environment.

**Plan mode is proven safe, and both engines now run cleanly under it.** The batch engine accepts `CLUTCHG_DRY_RUN=1` / `--plan`, which prints intended operations instead of performing them. That is only trustworthy if *every* mutating command sits behind the guard — a single unguarded `reg add` would turn a rehearsal into a real system change. `tests/unit/test_plan_mode_gating.py` asserts the property by parsing `backup-registry.bat`, `rollback.bat`, and `flight-recorder.bat` with paren-depth tracking, and confirms zero mutating commands (`reg add/delete/import`, `sc config`, `sc start/stop`, `bcdedit /import|/set`, `powercfg /setactive|/set*valueindex`, `net start/stop`) are reachable when `PLAN_MODE==1`. The detector is self-tested against a deliberately unguarded fixture (must flag) and a correct one (must pass).

Verified 2026-08-05 by executing both engines through `subprocess.run` — the same call shape `BatchExecutor` uses:

```
backup   → rc=0   PLAN|END|state=COMMITTED|success=19|failed=0        (no directory created)
rollback → rc=0   PLAN|END_RESTORE|state=COMPLETED|success=18|failed=0
```

No parse errors, no label-resolution errors, and nothing written to `BACKUPS_DIR`.

**Attempting that run exposed three defects that every static check had passed.** This is the strongest argument in the record for why runtime verification is not optional:

| Defect | Symptom | Cause | Scope |
|---|---|---|---|
| LF line endings | `The system cannot find the batch label specified - create_backup` | CMD mis-parses these scripts stored LF-only; converting to CRLF fixed it with no other change | **14 files**, including every safety-critical one |
| Unescaped `(s)` in `echo` inside a block | `. was unexpected at this time`, exit 255 — returned by a transaction that had *already committed* | CMD closes the block at the bare `)` then chokes on the remainder | 13 sites; 2 in the safety engine, 11 cosmetic in `simple-suggest.bat` |
| Bare `find` | Restore hung until killed, emitting `find: '/v': No such file` | GNU `find` shadows `find.exe` whenever Git Bash is on PATH; different switches, walks the filesystem | 2 sites (`rollback.bat`, `maintenance-manager.bat`) |

Notably the first two meant a **committed** backup transaction still reported failure, and the third made restore hang — all three sat in the recovery path this audit exists to certify, and none was visible to any static or unit check. Each is now pinned by a regression test that runs against every shipped `.bat` file rather than a fixture.

**What plan mode still does not establish — and what now does.** Plan mode proves dispatch, argument validation, manifest shape, control flow, and the full 19-component backup plan and 18-component restore plan. It never calls `reg add`, so it cannot prove the capture/restore pair actually round-trips a value.

That claim is now verified independently, without a VM. `clutchg/tests/vv/verify-recovery-mechanism.bat` copies the capture block from `backup-registry.bat::backup_registry_value` and the restore block from `rollback.bat::restore_registry_value` **verbatim**, then drives them against a scratch key it creates and deletes — `HKCU\Software\ClutchG-VV-Scratch`. No real Windows setting is touched, so it is safe on a development machine. Result (2026-08-05):

```
CASE|existing_value|PASS|restored=0x7          value was 0x7, mutated to 999, restored to 0x7
CASE|absent_value|PASS|value-removed-key-kept  value absent, added, then removed; key preserved
CASE|absent_key|PASS|key-removed               key absent, created, then removed entirely
CASE|power_scheme|PARTIAL|export-needs-elevation|guid-capture-and-reactivate-verified
RESULT|passed=3|partial=1|failed=0
```

All three registry recovery cases the engine implements round-trip correctly against the real registry. The scratch key was confirmed absent before the run and absent after.

**The power scheme is verified the same way.** `powercfg /duplicatescheme` creates a throwaway scheme, the harness activates it, then runs the engine's real capture (`getactivescheme` → `active_power_guid.txt`) and restore (read the file, shape-check the GUID, `setactive`). The original scheme is reactivated and the copy deleted; the active scheme and scheme count were both confirmed unchanged after the run. Only `powercfg /export` of the `.pow` blob is out of reach — it needs `SeBackupPrivilege` and fails `0x522` unelevated — so that one step is reported `PARTIAL` rather than counted as a pass. Failure to reactivate the original scheme is still a hard failure even in that path, which a contract test asserts.

Two things make this trustworthy rather than theatre. It was **mutation-tested**: replacing `/d "!VALUE_DATA!"` with `/d 0` in the restore makes case 1 fail with `data=0x0|expected=0x7`, so the harness can detect a broken mechanism. And because a verbatim copy can fossilise, `tests/unit/test_recovery_mechanism_contract.py` asserts every capture and restore statement — registry and power scheme alike — still appears in **both** the harness and the shipped engine, and that the harness writes only to the scratch key. Seventeen cases, itself mutation-tested by introducing drift and confirming the contract fails.

**What genuinely still needs a VM.** Two components remain: `bcdedit /import` restoring the boot configuration, and `sc config` returning a service to its recorded start type. Both mutate machine-wide state with no safe scratch equivalent — `sc create` needs elevation, so a throwaway service cannot be made here. Note also one cosmetic artefact: the harness emits `The system cannot find the drive specified.` on stderr from the unelevated `/export` attempt. It survives redirection because CMD emits it directly; exit status and machine state are both verifiably correct, so it is noise rather than a failure.

To reproduce:

```
clutchg\tests\vv\verify-recovery-mechanism.bat %TEMP%\clutchg-vv-state
```

And for plan mode, from an elevated `cmd.exe`:

```
set CLUTCHG_DRY_RUN=1
set BACKUPS_DIR=%APPDATA%\ClutchG\backups
src\backup\backup-registry.bat create_backup --plan
```

Expected output is a `PLAN|BEGIN|…` line, one `PLAN|BACKUP|…` line per component, and `PLAN|END|state=COMMITTED`, with no directory created under `BACKUPS_DIR`.

### 7.2 Journaled backup retention — a decision, not a bug fix

`_cleanup_old_backups` prunes only entries in `backup_index.json`, keeping ten. Batch-written journaled transactions are not in that index and no batch script implements retention, so they accumulate without bound. Each holds a services export, BCD export, power-scheme export, `systeminfo` dump, and one `.state` file per captured value.

Deliberately **not** fixed. The product's non-negotiable constraint is that every change is reversible; silently deleting the artifact that makes an older change reversible weakens exactly that guarantee. Reasonable options: a retention policy the user can see and configure, or an explicit "Clean up old recovery data" action with its consequence stated. Verified 2026-08-05: `_cleanup_old_backups(max_backups=1)` against one journaled and one index-managed backup removes neither journaled directory.

### 7.3 Remaining human gates

- **GitHub Project creation** — blocked on token scope. Run `gh auth refresh -h github.com -s project`, then the automation in `docs/defense-readiness/09-github-sdlc-governance-2026-07-30.md`.
- **Chapter synchronisation** — `output/chapters/` is canonical despite older mtimes. Do **not** run `sync-chapters.ps1` before merging, or newer content is overwritten.
- **Participant data, ethics determination, statistical/power review** — see `docs/defense-readiness/11-human-action-register-2026-07-30.md`.
- **Baseline freeze and final DOCX/PDF regeneration.**
- **Advisor review and mock defence sign-off.**

---

## 8. Known limitations of this audit

Stated plainly so they are not discovered by a reviewer instead.

1. **Sub-agent dispatch was unreliable; the affected lenses were then covered directly.** Multiple dispatched review agents terminated on API quota errors or stopped without reporting. The two substantive lenses they were meant to cover — GUI/threading and batch-engine semantics — were subsequently completed by direct review (see §5.1 and §5.2) and both produced findings. What did *not* happen is the independent-corroboration layer: every finding in this record was verified by reading code and running read-only probes, but by one reviewer rather than two. Treat the findings as verified and the *absence* of further findings as less certain.
2. **Privileged execution is partial.** See §7.1. Plan mode and the scratch-key round-trip are real executions, so registry restore is no longer a static-analysis claim. The three machine-wide components — BCD, service start types, power scheme — remain unexecuted and are still static claims.
3. **E2E suite unexercised.** 64 tests require a desktop session and were collected, not run.
4. **Two exploit-demonstration commands were blocked** by the permission classifier and were not retried. The evidence already gathered was sufficient; working around the denial would have been the wrong move.
5. **Awaiting review, not merged.** The work is committed in eight reviewable slices and pushed; PR #13 into `develop` is mergeable. Merging is a human decision. The branch was cut from `main` rather than `develop`, so `develop`'s auto-update commit (`6061e48`) conflicted with the updater hardening in this audit — resolved by taking the audit side after verifying function-by-function that it is a strict superset (`develop`'s `_spawn_relauncher` is the same relauncher, split into `_create_relauncher_script` + `_spawn_relauncher_script`), plus twelve functions `develop` lacks including Authenticode verification and the ACL-locked staging directory. `src/__init__.py` was resolved to import from the canonical `version.py` rather than either side's hard-coded literal.

---

## 9. Suggested next actions, in order

1. Review PR #13 and §7.2's retention decision, then merge into `develop`.
2. Run the Sandbox/VM verification in §7.1 and attach evidence. **This is the remaining gate** — now scoped to the BCD, service, and power-scheme components only; the registry path is verified.
3. Tag `v1.0.4` on `develop` once merged — the release workflow cross-checks all four version surfaces and will fail the build on any mismatch.
4. `gh auth refresh -h github.com -s project` and create the Project.
5. Advisor review and mock defence.

Optional but worthwhile: a second independent reviewer over §3–§6 when agent dispatch is stable. The lenses are covered, but by one reviewer — see §8.1.

---

## 10. Approval block

| Role | Name | Decision | Date | Signature / reference |
|---|---|---|---|---|
| Researcher | | | | |
| Technical reviewer | | | | |
| Advisor | | | | |

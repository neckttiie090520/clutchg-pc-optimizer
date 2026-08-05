# 14 — Audited Tweak Execution Correction Record

> **Standard context:** ISO/IEC 29110-5-1-2 — Software Implementation, Verification, Configuration Control, and Corrective Maintenance  
> **Project:** ClutchG PC Optimizer  
> **Correction date:** 2026-08-02 (extended 2026-08-04 — see §6.1 and §6.2)  
> **Evidence status:** `AUTOMATED_VERIFIED` for static/unit scope; `EXTERNAL_VERIFICATION_REQUIRED` for privileged Windows mutation and rollback

## 1. Problem statement

The Optimization Center displayed registry entries and Quick Action packs as executable even though the fail-closed execution boundary accepted only four audited contracts. Direct resolution of every built-in Quick Action pack showed that all nine packs were rejected before backup or execution.

The failure was safe in the narrow sense—no unaudited mutation occurred—but the UI and ISO records overstated implemented capability. The defect affected requirement UC-09 (Apply Individual Tweaks), Quick Actions, custom selection, tweak-count claims, and registry-to-batch traceability.

## 2. Reproduction

The execution path was traced as follows:

```text
ScriptsView._run_quick_tweak_pack()
  -> ProfileManager.apply_tweaks()
  -> TweakExecutionCatalog.resolve()
  -> reject any tweak ID without an audited contract
```

A direct resolver probe over all built-in `tweak_pack` actions produced:

```text
9 Quick Action packs checked
0 resolvable
9 rejected before backup or mutation
```

The existing regression suite still passed because it validated catalog structure and fail-closed rejection, but did not assert that built-in Quick Actions were actually resolvable.

## 3. Competing hypotheses and disposition

| Hypothesis | Evidence sought | Result |
|---|---|---|
| Batch scripts or labels were missing | Compare every catalog script/label against files and dispatcher routes | Partly confirmed: 20 registry entries named absent labels and 2 more named unreachable labels |
| `resolve()` parsed valid dispatchers incorrectly | Compare parser behavior with real dispatcher spellings and direct calls | Rejected as primary cause: parser correctly resolved the four declared contracts; the remaining IDs had no contract |
| Quick Actions bypassed `TweakExecutionCatalog` | Trace GUI → core execution path | Rejected: both Quick Actions and custom selection call `ProfileManager.apply_tweaks()`, which always calls `resolve()` |
| Registry metadata was documentation-only and harmless | Check every consumer of `bat_script`/`bat_function` and preset membership | Partly rejected: metadata did not dispatch runtime calls directly, but it drove visible UI claims and preset descriptions |
| Existing rollback labels made all contracts reversible | Compare every apply mutation with module reset behavior and transaction artifacts | Rejected: module-local reset was partial for Xbox DVR and informational only for Copilot/Recall |

## 4. Root cause

The system contained three concepts that had been treated as if they were identical:

1. **Tweak knowledge records** — explanatory metadata in `tweak_registry.py`.
2. **Profile membership metadata** — `preset_safe`, `preset_competitive`, and `preset_extreme` flags used for previews and recommendations.
3. **Audited executable contracts** — exact script/label/effect/recovery mappings enforced by `TweakExecutionCatalog`.

Only the third concept is sufficient to authorize a system mutation. The UI exposed records from the first concept as selectable without checking the third. Quick Action validation checked that tweak IDs existed and were not HIGH risk, but did not prove the packs could resolve.

The earlier count of 56 also included records for behavior that was absent, unreachable, security-reducing, or not reversible. This allowed metadata completeness to be reported as implementation completeness.

## 5. Corrective design

The correction preserves the fail-closed boundary and separates learning content from executable capability.

### 5.1 Execution admission

- Built-in Quick Action packs must resolve completely through `TweakExecutionCatalog` during catalog validation.
- Custom-selection toggles are enabled only for standard audited contracts that do not require a separate explicit-consent flow.
- Unsupported entries remain visible only when they describe implemented/reachable engine behavior; the UI marks non-selectable entries as **Learn Only**.
- Imported or stale selections are intersected with the audited selectable set before execution.

### 5.2 Recovery contract

Contract reversibility is based on exact transaction artifacts, not on the mere existence of a reset label.

| Contract | Persistent scope | Exact recovery evidence |
|---|---|---|
| Disable Xbox Capture | 10 Game DVR/Game Bar registry values | 10 named registry-value components captured before execution and restored by exact backup leaf ID |
| Disable Copilot & Recall | 5 Copilot/Windows AI/taskbar values | 5 named registry-value components captured before execution and restored by exact backup leaf ID |
| Disable Hypervisor | BCD `hypervisorlaunchtype` | Full BCD export/import component; explicit consent required |

Irreversible AppX removal is not eligible for standard execution. Security-mitigation disabling is not implemented.

### 5.3 Registry correction

Records are removed when the engine does not implement the described behavior, the label is unreachable, the change reduces required Windows security, or no defensible rollback path exists. Surviving records must name an existing reachable script label.

Historical documents may retain the earlier 56-candidate count in dated revision history. Current requirements, design, UI, and traceability must use the audited current count and distinguish registry records from executable contracts.

The corrected registry contains **44 implemented/reachable knowledge records**: LOW 34, MEDIUM 9, HIGH 1; current metadata memberships are SAFE 13, COMPETITIVE 38, EXTREME 44. These metadata memberships are not proof that profile execution applies each item individually.

## 6. Verification evidence

Host-safe commands executed from `clutchg`:

```text
python -m pytest tests/unit tests/integration -q
962 passed in 66.71s   (measured 2026-08-05: 939 unit + 23 integration)

python -m compileall -q clutchg/src
passed
```

The batch-integrity suite now verifies:

- legal CMD dispatch guards;
- no routes to absent labels;
- called batch modules and accepted arguments agree;
- no unreachable mutating labels;
- no security-mitigation-disabling commands;
- no scratch batch files under the discoverable engine tree;
- every registry script exists;
- every declared registry label exists and is reachable.

The action-catalog suite now verifies that every built-in tweak pack resolves to at least one audited action with no preflight errors.

### 6.1 Recovery reachability correction

Two recovery paths were repaired after the execution-admission work, because a committed backup that the user cannot reach is not a recovery capability.

1. **Recovery root divergence.** The batch engine defaulted its backup root to a directory beside the scripts (`%SCRIPT_DIR%..\backups`). In a packaged install that path is inside the program directory and is removed on uninstall, while the Restore Center reads `%APPDATA%\ClutchG\backups`. Committed transactions were therefore invisible to the restore UI. `BatchExecutor` now pins `BACKUPS_DIR` to the writable data root for every batch launch, so both writers and the reader agree on one location.
2. **Restore-format divergence.** Journaled transactions store exact value state under `registry-values\*.state` with a component manifest, whereas the Python index format stores `registry\*.reg`. `BackupManager.restore_registry` would have attempted `reg import` and always failed. Journaled transactions are now discovered from `manifest.ini` on disk and routed to `safety\rollback.bat`, and an uncommitted (`state=FAILED`) transaction is refused rather than partially restored.

Regression tests: `tests/unit/test_backup_manager.py::TestJournaledBackupDiscovery` (5 cases), `::TestJournaledRestoreRouting` (2 cases), `tests/unit/test_batch_executor_extra.py::TestRecoveryRootPinning` (2 cases).

### 6.1.1 Command-injection boundary at the batch interface

Routing journaled restores to `safety\rollback.bat` introduced a new attack surface that the adversarial bug hunt found and closed. Windows executes `.bat` targets through `cmd.exe`, which acts on shell metacharacters **before** the script can validate its own arguments. `:validate_backup_id` in `rollback.bat` therefore cannot defend the interface — by the time it runs, `cmd.exe` has already split the command line.

The exposure was concrete rather than theoretical:

- `%APPDATA%\ClutchG\backups` is writable by an unprivileged user (`core/paths.py::_appdata_base`).
- The application requests elevation (`ClutchG.spec`, `uac_admin=True`).
- Directory names containing `&` are legal on NTFS.
- A directory named `2026-01-01_00-00-00&<command>` holding a valid `manifest.ini` was discoverable, and its name was passed verbatim as the restore argument — so the tail would have run with administrator privileges. This crosses a real privilege boundary: content an unprivileged process controls becomes a command in an elevated one.

Three defences were added, each independently sufficient:

| Boundary | Control | Location |
|---|---|---|
| Discovery | Only exact timestamp-shaped directory names are recognised as transactions | `core/backup_manager.py` — `JOURNALED_BACKUP_ID_PATTERN` |
| Restore | The ID shape is re-checked immediately before it reaches `cmd.exe` | `core/backup_manager.py::_restore_journaled_backup` |
| Execution | Any argument **or script path** containing `& \| < > ^ " ' \`` or a newline/NUL is refused rather than escaped | `core/batch_executor.py::_argument_is_shell_safe` |

The pattern uses `\A`/`\Z` rather than `^`/`$`, because `$` also matches immediately before a trailing newline — a weakness found by challenging the first version of the fix. Refusing rather than escaping is deliberate: every legitimate caller passes a label, a fixed keyword, or a timestamp, so there is no valid input this rejects.

The script path is validated as well as the arguments, because it is the first token on the command line and splits identically.

Regression tests: `tests/unit/test_batch_executor_extra.py::TestBatchArgumentInjection` (11 cases), `::TestScriptPathInjection` (2 cases), `tests/unit/test_backup_manager.py::TestJournaledBackupIdHardening` (12 cases). Each asserts the process is **never spawned**, not merely that the call fails.

Audited and found already sound, so left unchanged: `_sanitize_restore_point_name` (strips PowerShell metacharacters before interpolation, and strips rather than escapes, so it fails safe); all `reg.exe` invocations (list argv, no shell); and the updater handoff (`INSTALLER_NAME_PATTERN.fullmatch`, ACL-locked staging directory, SHA-256 re-verification immediately before launch).

### 6.2 Registry claim fidelity contract

The registry corrections in §5.3 removed records the engine does not implement, but did not prevent a surviving record from misdescribing the change it routes to. `tests/unit/test_registry_claim_fidelity.py` now parses each routed label and asserts that every declared registry key is actually written by that label, and that a record never claims a machine-wide hive for a per-user write.

Introducing the contract exposed four further claim defects, all corrected:

| Record | Claimed | Engine actually writes | Correction |
|---|---|---|---|
| `gpu_dwm` | `HKLM\SOFTWARE\Microsoft\Windows\Dwm` | `HKCU\SOFTWARE\Microsoft\Windows\DWM` | Re-scoped to per-user; name and expected gain made truthful |
| `net_netbios` | "Disable NetBIOS over TCP/IP" | `EnableLMHOSTS=0` only | Renamed to "Disable LMHOSTS Lookup"; states NetBIOS stays enabled |
| `inp_data_queue` | mouclass **and** kbdclass parameters | mouclass only in `:apply_mouse` | Keyboard queue moved to `inp_keyboard`, which does write it |
| `inp_priority_sep` | `PriorityControl` via `input-optimizer.bat:apply_latency` | written by `registry-utils.bat:apply_gaming_tweaks` | Route corrected to the label that performs the write |

This contract is the standing guard for the defect class, not just for these four instances.

### 6.2.1 The guard was itself defective — found by scrutinising it

The first version of `_written_keys` in `test_registry_claim_fidelity.py` carried a broken escape in its helper-call pattern (`\[^"]+` instead of `[\\][^"]*`), so that branch matched nothing. The engine writes most registry values through `call :reg_set "HIVE\..."` / `call :reg_add "HIVE\..."` wrappers rather than a bare `reg add`, which meant the guard silently compared only **13 of the 28** records that declare registry keys — and reported the other 15 as passing. One of those 15 was `inp_priority_sep`, the very record §6.2 claims the guard verified.

This matters more than the individual defects: a contract test that passes by *seeing nothing* is worse than no test, because it manufactures false assurance. Repairing the pattern raised coverage from 13 to 27 records and immediately surfaced two further defects:

| Record | Claimed | Reality | Resolution |
|---|---|---|---|
| `tel_diagtrack` | `HKLM\SYSTEM\CurrentControlSet\Services\DiagTrack` | No `reg add`; the script calls `sc config DiagTrack start= disabled` | **Record was correct** — the Service Control Manager persists to that key. The guard's model of "written" was too narrow, so `_service_keys` was added |
| `vis_visual_fx` | "Best Performance Visual Settings", `VisualFXSetting=3`, `…\Explorer\VisualEffects`, "5-10% on low-end GPUs" | `VisualFXSetting` and `VisualEffects` appear **nowhere** in `src/`; the label sets `DisallowShaking` and three ContentDeliveryManager values | Record rewritten to describe what the label does, with the fabricated gain removed |
| `pwr_epp` | `HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings`, "1-3% FPS improvement" | The label uses `powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PERFEPP`; no registry key is written | `registry_keys` emptied, mechanism described accurately, fabricated gain removed |

Two additional guards now prevent the failure mode from recurring: `test_every_registry_declaring_tweak_is_actually_compared` asserts an **exact** floor — every record that declares a registry key and routes to a real label must be compared — and `_registry_tweaks` no longer drops a tweak whose label writes no keys, so such a record fails loudly instead of vanishing.

**The defect class recurred a third time, inside the repair.** A final scrutiny pass found that the repaired guard still compared 27 of 28 records: `pwr_epp` declared `HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings` but its label `:apply_epp_performance` uses `powercfg /setacvalueindex` and writes no registry key at all, so `_registry_tweaks` silently dropped it — and the coverage floor had been written as `>= len(declaring) - 2`, which let 27-of-28 pass with margin. Both were fixed: the floor is now exact, the drop-if-no-keys branch is gone, and `pwr_epp`'s record was corrected to declare no registry keys and to describe the powercfg mechanism it actually uses (its fabricated "1-3% FPS improvement" was removed at the same time). Twenty-seven records now declare registry keys and all twenty-seven are compared.

This is recorded rather than smoothed over because it is the most defensible thing in the correction: the same defect class reproduced three times — in the product, in the guard built to catch it, and in the repair of that guard. Each recurrence was caught by attacking the previous fix rather than by trusting its green result.

The same scrutiny pass found two defects in `test_iso_metric_currency.py`. Its collectable ceiling used a `20 ×` multiplier against a collected-to-defined ratio measured at roughly 1.3, giving about 14× headroom — it could not have failed on any realistic overstatement. And `_is_history_line` exempted **any** line containing `→`, so a stale current-state claim sitting beside a legitimate progression was waved through. The multiplier is now 1.5 with a companion test asserting the bound is tight enough to reject a doubled claim, and progressions are stripped per-token rather than exempting the whole line. `TestGuardDiscriminates` pins both behaviours. The ratio is deliberately not hard-coded in a comment as a measured figure, because that number drifts as tests are added — the bound is asserted algebraically instead.

**Method note for the defence.** Every guard added in this correction was subsequently attacked, and three of the four had a real weakness. The transferable lesson is that a passing contract test is evidence only once you have shown it can fail — verify the guard against a synthetic violation before trusting its green result.

### 6.4 Batch-engine and GUI lenses — the passes that had been missing

Earlier iterations of this audit noted that the batch-engine and GUI/threading lenses had not received an independent review. Both were completed on 2026-08-05.

**Component symmetry is intact.** The `components=` manifest in `backup-registry.bat:157` declares nineteen components: fifteen exact registry values plus `services`, `bcd`, `power_scheme`, and `system_info`. Each of the fifteen values is captured by `:backup_registry_value` and restored by `:restore_registry_value` in the same order, and each of the four remaining components has a matching `:restore_*` label. There is no component that is backed up but never restored, and none restored that was never backed up — so no reversibility hole exists in the journaled path.

**One overstatement found, in the safety engine itself.** `:restore_system_info_component` called `record_restore_result "system_info" 0`, which incremented `RESTORE_SUCCESS` and wrote `RESULT|system_info|SUCCESS` to the restore journal. But `systeminfo.txt` is a diagnostic capture with nothing to write back — the label restored nothing. The restore journal therefore claimed one more component recovered than the engine recovered. It now writes `REFERENCE_ONLY` (or `REFERENCE_MISSING`) and does not count toward the success total.

Note the two journals are distinct and must not be conflated: backup validation at `rollback.bat:207` requires `RESULT|system_info|SUCCESS` in `journal.log`, where the capture genuinely did succeed; the restore path writes to `restore-journal.log`. Tests pin both: `test_system_info_is_journaled_as_reference_not_as_restored_state` and `test_backup_journal_verification_is_unaffected_by_restore_journal`.

**The GUI threading model is correct.** Tkinter permits widget access only from the main thread, and profile/tweak application runs on `threading.Thread(daemon=True)` workers. All four worker bodies (`profiles_minimal.py:411`, `scripts_minimal.py:925`, `:1836`, `:3094`) touch only `ExecutionDialog` callbacks and `app.toast.*`. Every one of the five worker-facing dialog callbacks — `add_output`, `set_progress`, `add_tweak_status`, `show_result`, `show_diff` — checks `threading.current_thread() is not threading.main_thread()` and re-posts itself through `after(0, ...)` before touching a widget, and `ToastManager` marshals through `parent.after(0, callback, *args)`. No unguarded cross-thread widget access was found.

Because that invariant is easy to break silently — a new callback omitting the guard produces intermittent corruption rather than a clean failure — `TestThreadMarshallingInvariant` now asserts it statically for all five callbacks. The check was mutation-tested: removing the guard from `show_diff` makes it fail.

### 6.5 Persistence durability — non-atomic writes to recovery-critical files

A `/bug-hunter` scan of the core layer found that both persistence paths overwrote their target file in place. An interruption partway through left truncated JSON, and both readers swallow the resulting parse error:

| File | Reader behaviour on truncated JSON | Consequence |
|---|---|---|
| `backup_index.json` | `_load_index` logs and returns `[]` | **Every index-format backup becomes invisible to the Restore Center.** The recovery artifacts still exist on disk but nothing can find them. Verified 2026-08-05 by writing `[{"id": "20260101_120000", "name": "impor` and reloading: 0 entries recovered. |
| `user_config.json` | `load_config` warns and falls back to defaults | Every user setting — language, theme, confirmation preferences — silently reset. |

Both now write to a temporary file in the same directory (`tempfile.mkstemp`), `flush`, `fsync`, and `os.replace` onto the target. `os.replace` maps to `MoveFileEx` with `MOVEFILE_REPLACE_EXISTING` on Windows and is atomic for a same-volume rename, so a reader sees either the previous file or the new one, never a partial one. A `finally` block removes the temporary file on any failure, and the previous file is left byte-identical.

A scrutiny pass on that fix found a further defect: `ConfigManager.save_config` had no lock, while `updater.py:1016` calls it from a background thread and `settings_minimal.py:475` from the GUI thread through the same manager. Two concurrent `os.replace` calls on Windows make one fail with `PermissionError`, so `save_config` returns `False` and logs — the user's setting is lost with no visible error. Measured before the fix: **32 of 240 concurrent saves silently dropped.** After adding `_write_lock`: **0 of 240.** The post-fix half of that measurement is reproducible from the suite (`TestConfigWriteIsSerialised`); the pre-fix figure was measured once against the unlocked code and is recorded as a one-time observation, not a repeatable assertion.

A second scrutiny pass then found that `BackupManager` held `_index_lock` only around the **file write**, leaving the read-modify-write of `self.backups` unguarded in `delete_backup` and `_cleanup_old_backups`. Two concurrent deletes could each rebuild the list from a stale snapshot, so one deletion was lost from the index while its directory had already been removed — **the index would list a backup that cannot be restored**, which is precisely the failure class §4 exists to close. Both methods now hold the lock across the whole mutation, and `_save_index` was split into a locking wrapper plus `_write_index_unlocked` so the lock is never acquired twice (a nested acquisition of a non-reentrant `Lock` would deadlock on every backup). Verified after the fix: six concurrent deletes over twelve backups produced **zero index entries without a matching directory**.

Two related gaps were closed at the same time. `ConfigManager.reset_to_defaults` deleted the config file outside the lock, so it could interleave with a save; it now holds `_write_lock`. And `ProfileManager.save_custom_preset` had the same silent-loss shape in a third location: it swallowed a read failure with a bare `except: pass`, then wrote back only the new entry — **discarding every other saved preset with nothing logged**. It now refuses to overwrite a file it could not parse, logs the reason, and writes atomically.

Regression tests: `test_backup_manager.py::TestIndexWriteIsAtomic` (4 cases), `::TestIndexMutationIsSerialised` (3 cases), `test_core_coverage.py::TestConfigWriteIsAtomic` (3 cases), `::TestConfigWriteIsSerialised` (2 cases), `test_profile_manager.py::TestCustomPresetPersistence` (4 cases).

Two test-quality corrections came out of the same scrutiny. One pre-existing test (`test_save_returns_false_on_permission_error`) had to be repaired rather than deleted: it patched `builtins.open`, which the atomic path no longer calls, so it would have passed without exercising the failure branch at all — it now injects at `tempfile.mkstemp`. And a test that asserted the lock by grepping the source for `with self._write_lock:` was replaced: a source-text match would pass against a no-op lock. It now observes `_write_lock.locked()` from inside the write and asserts the lock is released afterwards. Mutation-tested — substituting a no-op lock makes it fail.

Also noted and deliberately **not** changed: the `max_backups` key in the default config is read by nothing — `_cleanup_old_backups` uses a hard-coded limit, now named `DEFAULT_INDEX_RETENTION`. Wiring the key up would change how much recovery history is kept, which is the retention decision in §6.6, not a code cleanup. Neither is `-5` rejected as a value, which is a further reason to settle the policy before honouring the key.

### 6.6 Open item — journaled backup retention

`BackupManager._cleanup_old_backups` prunes only entries tracked in `backup_index.json`; it keeps at most ten. Batch-written journaled transactions are not in that index, and no batch script implements retention, so committed recovery transactions accumulate without bound. Each transaction contains a services export, a BCD export, a power-scheme export, a `systeminfo` dump, and one `.state` file per captured registry value.

This is recorded rather than fixed. Automatically deleting recovery artifacts is a safety-relevant design decision — the product's non-negotiable constraint is that every change is reversible, and silently discarding the artifact that makes an older change reversible weakens exactly that guarantee. The decision belongs to the researcher, and the reasonable options are a retention policy the user can see and configure, or an explicit "Clean up old recovery data" action in the Restore Center with its consequence stated. Verified 2026-08-04: `_cleanup_old_backups(max_backups=1)` against a directory holding one journaled transaction and one index-managed backup removes neither journaled directory.

## 7. Remaining verification gates

The correction has not executed privileged mutations on the host. Before release or thesis claims of runtime validation:

1. Run each standard audited action in a disposable Windows Sandbox or VM.
2. Preserve the committed backup ID, manifest, journal, and before/after registry evidence.
3. Restore the exact backup leaf and verify all captured values return to their original existence/data state.
4. Test cancellation and injected command failures after snapshot commit.
5. Re-run the full Python unit/integration suite and record its exact count, duration, and coverage.
6. Obtain technical-reviewer and advisor sign-off.

## 8. Requirement and defense interpretation

A defensible thesis statement is:

> ClutchG separates its tweak knowledge base from its mutation authority. A tweak can be documented without being executable. Execution is admitted only when an audited script target, effect scope, consent rule, and exact recovery component are available. Unsupported selections fail before backup and before system mutation.

Do not claim that every registry entry can be applied individually. Do not use the historical 56-record count as current implementation evidence. Profile execution remains module-based and must not be equated with registry preset-count metadata unless an explicit profile-to-tweak contract map is produced.

## 9. Approval block

| Role | Name | Decision | Date | Signature/reference |
|---|---|---|---|---|
| Researcher |  |  |  |  |
| Technical reviewer |  |  |  |  |
| Advisor |  |  |  |  |

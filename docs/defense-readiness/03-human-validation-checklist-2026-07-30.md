# Human-Only Validation and Sign-off Checklist

**Baseline:** 2026-07-30  
**Owner:** ผู้วิจัย (human-in-the-loop)  
**Rule:** ห้ามรัน privileged batch mutation บน host; ใช้ disposable Sandbox/VM เท่านั้น

เอกสารนี้แยกงานที่ automation ช่วยเตรียมได้ออกจากงานที่ต้องให้มนุษย์ดำเนินการ ตรวจผล และรับผิดชอบ

## 0. Freeze the evidence baseline

- [ ] Review all modified/untracked files; separate product changes from local tools/research artifacts
- [ ] Resolve secrets/PII scan; do not include certificates, credentials or personal paths
- [ ] Create a named branch and reviewed commit (do not commit from an unreviewed dirty tree)
- [ ] Record commit SHA, `git status`, Python version, Windows build and dependency lock state
- [ ] If commit is not possible, create a source archive and record SHA-256
- [ ] Copy raw full pytest output and coverage report into a dated evidence directory
- [ ] Record the three skipped test node IDs and reviewer disposition

**Exit evidence:** Planned artifact pattern: `tests/sandbox/results/baseline_<timestamp>.json` (ยังไม่มีและต้องสร้างในรอบทดสอบ), source SHA/commit, clean-or-explained status, reviewer/date

## 1. Requirements and document reconciliation

For every thesis/ISO numeric claim:

- [ ] Search current thesis chapters, SRS, SDD, Test Plan/Record, Traceability, README and slides
- [ ] Normalize test count to a dated/specified command scope
- [ ] State total coverage as 39% unless a newer reproducible run supersedes it
- [ ] Treat 70%/85% as unmet target or formally change requirement through change request
- [ ] Define research corpus: primary repositories vs supporting documents
- [ ] Normalize active tweak/category/profile counts from executable registry output
- [ ] Remove/qualify universal FPS or latency claims without raw benchmark evidence
- [ ] Update source line references or replace brittle lines with symbol/file references
- [ ] Mark historical records with source version/date rather than deleting them

**Exit evidence:** signed claim-to-evidence matrix; no unresolved `CONFLICT` on defense slides

## 2. Current-source Windows Sandbox V&V

### Preconditions

- [ ] Explicit permission to enable/use Windows Sandbox
- [ ] Host restart completed if feature was enabled
- [ ] Source baseline/hash recorded
- [ ] Prior result files archived, not overwritten
- [ ] No credentials, production data or signing certificate mapped
- [ ] Reviewer confirms all mutations occur inside disposable environment

### Execute

From `tests\sandbox`, run in order:

```cmd
launch-tests.bat default
launch-tests.bat nogpu
launch-tests.bat nonet
```

For each configuration:

- [ ] Retain `vv-results_<timestamp>.txt`
- [ ] Retain `vv-results_<timestamp>.json`
- [ ] Retain `vv-summary_<timestamp>.txt`
- [ ] Record source SHA, Windows build and config name
- [ ] Confirm `FAIL = 0`
- [ ] Review every WARN/SKIP; assign owner/rationale/disposition
- [ ] Confirm no P0 safety or transaction test was skipped

**Do not** run `tests/sandbox/run-all-tests.bat` directly on the host.

## 3. Apply → verify → rollback experiment

Use a fresh disposable snapshot and a low-risk representative action first.

- [ ] Capture before-state for exact registry/service/power/BCD targets
- [ ] Capture Defender, Windows Update and UAC safety invariants
- [ ] Create backup; retain backup ID, manifest/journal and result
- [ ] Apply selected action/profile
- [ ] Verify exact expected state and return/result consistency
- [ ] Run cancellation-before-admission scenario; verify no backup/mutation starts
- [ ] Run cancellation-during-process scenario; verify active tree stops and no next action starts
- [ ] Restore using only the backup produced by the run
- [ ] Compare restored state to before-state
- [ ] Recheck safety invariants
- [ ] Destroy/revert the disposable environment

**Exit criteria:** no hidden failure, no out-of-scope mutation, restored state matches accepted tolerance, reviewer signs result

## 4. Historical Hyper-V evidence disposition

`12-Batch-VV-Test-Record.md` reports 20/20 on 2026-04-12.

- [ ] Identify the commit/archive corresponding to that test
- [ ] Link raw screenshots/logs if they exist
- [ ] Mark it `HISTORICAL_VERIFIED`, not current-source verification
- [ ] Compare changed safety-critical files since that baseline
- [ ] Use current Sandbox run to revalidate affected flows

If raw artifacts or source mapping cannot be recovered, retain the record as narrative history but do not use it as the sole defense proof

## 5. Hardware benchmark (only if performance is a thesis result)

- [ ] Define CPU/GPU/RAM/storage/driver/Windows build
- [ ] Define workload and metric before collecting data
- [ ] Use baseline and treatment on equivalent state
- [ ] Use warm-up and repeated runs (recommended at least 5 per condition)
- [ ] Record raw observations, median/mean, spread and outliers
- [ ] Control background processes and power/thermal state
- [ ] Separate VM results from bare-metal results
- [ ] Report negative/no-effect outcomes
- [ ] Avoid generalizing beyond tested configurations

**Exit evidence:** CSV/raw logs, protocol, analysis notebook/script, plots, researcher interpretation

## 6. UAT and usability validation

- [ ] Define representative user tasks and acceptance criteria
- [ ] Obtain consent; do not collect unnecessary personal data
- [ ] Record participant code, environment, task success, time/errors and qualitative feedback
- [ ] Separate researcher demo from independent UAT
- [ ] Log issues and disposition through change requests
- [ ] Obtain reviewer/advisor sign-off for acceptance claims

## 7. Controlled signed release

Requires explicit release authorization.

- [ ] Review and approve final version/tag
- [ ] Provision signing secrets in GitHub Actions—not in repository
- [ ] Trigger controlled tag build
- [ ] Retain CI run URL and logs
- [ ] Verify tag = Python version = PE FileVersion/ProductVersion = Inno AppVersion
- [ ] Retain SHA-256 for `ClutchG.exe` and exact installer
- [ ] Verify Authenticode status and exact publisher subject for both
- [ ] Confirm exactly one expected installer asset is published
- [ ] In disposable VM, install prior version then upgrade
- [ ] Verify successful handoff, app relaunch and final version
- [ ] Test failure path: invalid/missing signature must fail closed

Do not publish production release merely to create thesis evidence; use draft/pre-release if appropriate and approved

## 8. Participant study and research-validity gate

ใช้ [`11-human-action-register-2026-07-30.md`](11-human-action-register-2026-07-30.md) เป็น execution source สำหรับ owner, prerequisite, status และ retained exit evidence ของ H-04 ถึง H-21; checklist ด้านล่างใช้ตรวจความครบถ้วน ไม่แทน action register

- [ ] Researcher and advisor choose one synchronized canonical chapter set before editing
- [ ] Obtain written CMU/advisor/ethics-office review, exemption, or non-review determination before participant work
- [ ] Researcher and advisor align the title and objectives with the measured construct (player skill versus system/game performance)
- [ ] Resolve permanent Machine A/B treatment confounding, or narrow the causal claim and document the limitation
- [ ] Randomize/counterbalance difficulty order, or document fixed-order bias as a limitation
- [ ] Statistician/advisor validates interaction power, repeated-measures model, assumption checks, fallback analysis, confidence intervals and multiplicity handling
- [ ] Reconcile counterbalanced versus fixed A–B wording and participant-session timing
- [ ] Collect participant data and retain consent, raw CapFrameX/LatencyMon/resource logs, environment metadata and exclusions
- [ ] Do not replace `[TBD]` cells with inferred or synthetic values
- [ ] Mark the 2026-04-12 Hyper-V 20/20 result as historical unless source mapping or fresh revalidation is retained

## 9. Thesis and defense human review

- [ ] Researcher rewrites findings in their own academic voice
- [ ] Verify every citation against the original source
- [ ] Check university formatting and A4 layout using the designated thesis tools
- [ ] Remove unsupported superlatives and “100% safe/complete” language
- [ ] Include limitations and threats to validity
- [ ] Include responsible AI/tool-use disclosure consistent with university policy
- [ ] Advisor reviews evidence matrix, results chapter and limitations
- [ ] Run mock defense; record unanswered questions and revise
- [ ] Render final PDF and inspect pagination, figures, tables, fonts and Thai/English line breaking manually

## 10. Sign-off table

| Gate | Researcher | Reviewer/advisor | Date | Evidence URI/path | Result |
|---|---|---|---|---|---|
| Baseline frozen |  |  |  |  |  |
| Numeric claims reconciled |  |  |  |  |  |
| Sandbox default |  |  |  |  |  |
| Sandbox no-GPU |  |  |  |  |  |
| Sandbox no-network |  |  |  |  |  |
| Apply/rollback |  |  |  |  |  |
| Benchmark |  |  |  |  | N/A allowed with rationale |
| UAT |  |  |  |  |  |
| Signed release |  |  |  |  | N/A until authorized |
| Thesis final PDF |  |  |  |  |  |

## Definition of defense-ready

ใช้คำว่า “defense-ready” ได้เมื่อ:

1. ไม่มี P0 contradiction ระหว่าง thesis/slides กับ current evidence
2. Source baseline ถูก freeze และทุก result ผูกกับ hash/commit
3. Current-source privileged safety flow มี fresh disposable-environment evidence หรือถูกประกาศเป็น limitation ที่อาจารย์ยอมรับ
4. Coverage requirement ถูกทำให้ผ่านหรือ change-controlled อย่างโปร่งใส
5. Human/advisor sign-off ครบตาม scope ที่ตกลง

ไม่มี checklist ใดรับประกันผลสอบ 100%; final judgment เป็นของคณะกรรมการ

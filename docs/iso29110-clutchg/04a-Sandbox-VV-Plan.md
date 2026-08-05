# 04a — แผนการทดสอบด้วย Windows Sandbox (Controlled Sandbox V&V Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O5 (Software Testing)  
> **โครงงาน:** ClutchG PC Optimizer v1.0.3  
> **เวอร์ชันเอกสาร:** 1.1  
> **วันที่ปรับฐานหลักฐาน:** 2026-05-30  
> **เอกสารแม่:** `04-Test-Plan.md`  
> **สถานะรวม:** `INFRASTRUCTURE_AUTOMATED_VERIFIED / RUNTIME_BLOCKED_EXTERNAL`

## 1. วัตถุประสงค์และขอบเขต

เอกสารนี้กำหนดการ V&V ระดับ batch script บน Windows จริงในสภาพแวดล้อมแบบทำลายทิ้งได้ (disposable Windows Sandbox) เพื่อปิดช่องว่างที่ pytest ไม่สามารถยืนยันได้ ได้แก่ การเปลี่ยนแปลง registry/service/power/BCDEdit จริง การสร้างและกู้คืน backup และผลของ rollback หลัง mutation

การทดสอบแบ่งเป็นสองชั้นที่ต้องไม่สรุปรวมกัน:

1. **Static infrastructure verification** — ตรวจ `.wsb`, launcher, harness, mapped-folder permission และรูปแบบผลลัพธ์ด้วย pytest โดยไม่เปิด Sandbox หรือ execute privileged scripts
2. **Runtime validation** — เปิด Windows Sandbox และ execute `tests/sandbox/run-all-tests.bat` จริง ซึ่งอาจเปลี่ยนระบบภายใน Sandbox และต้องมีผลลัพธ์ที่ตรวจสอบย้อนกลับได้

### 1.1 สิ่งที่ครอบคลุม

- ความครบถ้วนและโครงสร้างของ batch scripts
- system detection, logger และ validator บน Windows
- safety constraints: Defender, Windows Update และ UAC
- backup-before-mutation และ backup/restore cycle
- core module load/dispatch
- profile application, cancellation และ rollback
- result containment: ผลลัพธ์ต้องเขียนกลับเฉพาะ `tests/sandbox/results/`

### 1.2 สิ่งที่ไม่สรุปจากแผนนี้

- ประสิทธิภาพ FPS/latency บน hardware จริง
- compatibility ทุก Windows release
- ความถูกต้องของ certificate signing จริง
- production release publication
- การผ่าน runtime V&V ก่อนมีไฟล์ผลลัพธ์จาก Sandbox

## 2. Evidence Baseline

### 2.1 Automated Python gate

คำสั่งที่ใช้จาก repository root (เปลี่ยน working directory ก่อน เพื่อให้ `--cov=src` ชี้ไปที่ Python source ที่ถูกต้อง):

```bash
cd clutchg
python -m pytest tests/unit tests/integration \
  --skip-slow --skip-e2e -q --tb=short
```

ผลล่าสุดหลัง remediation และ Sandbox contract tests:

```text
759 collected; 756 passed, 3 skipped, 0 failed in 80.14s
TOTAL coverage: 39%
```

สถานะ: **AUTOMATED_VERIFIED**

หมายเหตุ: ไม่เปลี่ยน `pytest.ini` และไม่เพิ่ม dependency; การรัน static-only subsets อาจไม่มี Python coverage ตามปกติ จึงใช้ผล coverage จาก full suite นี้เป็นหลักฐาน

### 2.2 Sandbox infrastructure contract

ไฟล์ทดสอบ: `clutchg/tests/unit/test_sandbox_vv_contract.py`

ผลล่าสุด:

```text
5 passed
```

สิ่งที่ยืนยันแบบ static:

- `.wsb` ทั้งสามไฟล์เป็น portable templates; `launch-tests.bat` derive `%REPO_ROOT%` จากตำแหน่ง script แล้ว materialize path แบบ XML-escaped ลง temporary `.wsb`
- `src/` และ test harness เป็น read-only
- `tests/sandbox/results/` เป็น write-enabled เพียง mapped folder เดียว
- default/no-GPU เปิด network; no-network ปิด network
- vGPU ปิดทุก configuration
- launcher ตรวจ `WindowsSandbox.exe` และตรวจจับ result file ใหม่
- runner สร้าง text, JSON และ CSV summary evidence

สถานะ: **INFRASTRUCTURE_AUTOMATED_VERIFIED**

### 2.3 Runtime evidence

ณ baseline นี้ `tests/sandbox/results/` ยังไม่มี `vv-results_*` หรือ `vv-summary_*` จากการรันหลัง remediation

สถานะ: **RUNTIME_BLOCKED_EXTERNAL**

เหตุผล: ต้องเปิด Windows Sandbox ซึ่งเป็น privileged/outward system action, อาจต้อง enable Windows optional feature และ restart host จึงไม่ถือว่า “ผ่าน” จาก static checks

## 3. Test Environment

### 3.1 Repository and mapped paths

| Purpose | Host | Sandbox | Permission |
|---|---|---|---|
| Batch source | `%REPO_ROOT%\src` | `C:\ClutchG\src` | Read-only |
| Harness | `%REPO_ROOT%\tests\sandbox` | `C:\ClutchG\tests` | Read-only |
| Evidence | `%REPO_ROOT%\tests\sandbox\results` | `C:\ClutchG\results` | Read-write |

### 3.2 Configurations

| Configuration | File | Network | vGPU | Purpose |
|---|---|---:|---:|---|
| Default | `clutchg-test.wsb` | Enable | Disable | Standard batch V&V |
| No GPU | `clutchg-test-nogpu.wsb` | Enable | Disable | GPU graceful degradation |
| No Network | `clutchg-test-nonet.wsb` | Disable | Disable | Network graceful degradation |

### 3.3 Preconditions

1. Working tree under test is reviewed and identified by commit or archive hash
2. Windows Sandbox feature is enabled
3. Host is restarted if the feature was just enabled
4. `tests/sandbox/results/` is empty or prior evidence is archived
5. No production credentials, signing certificate or personal data is mapped into Sandbox
6. Reviewer accepts that privileged mutations occur only inside disposable Sandbox

Enable command (requires explicit administrator approval and restart):

```powershell
Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online -NoRestart
```

## 4. Infrastructure and Execution Flow

```text
Host: tests/sandbox/launch-tests.bat <default|nogpu|nonet>
  ├─ validates requested .wsb
  ├─ verifies WindowsSandbox.exe exists
  ├─ records existing summary count
  ├─ launches disposable Sandbox
  └─ waits for a new vv-summary_*.txt

Sandbox LogonCommand
  └─ C:\ClutchG\tests\run-all-tests.bat
       ├─ executes 12 controlled test groups
       ├─ writes vv-results_<timestamp>.txt
       ├─ writes vv-results_<timestamp>.json
       └─ writes vv-summary_<timestamp>.txt
```

Harness files:

- `tests/sandbox/launch-tests.bat`
- `tests/sandbox/run-all-tests.bat`
- `tests/sandbox/clutchg-test.wsb`
- `tests/sandbox/clutchg-test-nogpu.wsb`
- `tests/sandbox/clutchg-test-nonet.wsb`

## 5. Runtime Test Groups

| Group | Scope | Blocking condition |
|---|---|---|
| 1. File Structure | Required batch files and profiles | Missing required source file |
| 2. System Detection | OS/build/CPU output | Crash or invalid mandatory output |
| 3. Logger | Init and structured log writes | Cannot create/write contained log |
| 4. Validator | Admin/OS/VM validation | Unsafe validation bypass |
| 5. Backup | Backup folder and artifacts | Mutation possible without usable backup |
| 6. Safety Constraints | Defender/WU/UAC runtime + source signatures | Any safety rule violation |
| 7. Service Manager | Dispatch and critical-service protection | Critical service disabled or targeted |
| 8. Core Modules | 13 module load/dispatch tests | Crash, hang or uncontrolled mutation |
| 9. Rollback | Normal/extreme rollback containment | Restore escapes selected backup or reports false success |
| 10. Flight Recorder | Snapshot/list behavior | Missing/invalid journal evidence |
| 11. Backup-Restore Cycle | Create → mutate test state → restore | State not restored or errors hidden |
| 12. Profiles | SAFE/COMPETITIVE/EXTREME contracts | Missing flags, unsafe default or false success |

Detailed IDs remain implemented in `tests/sandbox/run-all-tests.bat`; the harness source is the execution-controlled test procedure.

## 6. Critical Runtime Scenarios

### 6.1 Safety invariants

The following are release-blocking:

- Defender must not be disabled
- Windows Update must not be disabled
- UAC `EnableLUA` must not be set to 0
- restore must not accept an untrusted path outside the controlled backup root
- backup failure must abort mutation
- cancellation before admission must start no backup or mutation
- cancellation during execution must stop the active process and prevent the next action

### 6.2 Profile transaction sequence

For each profile in a fresh Sandbox:

1. Capture before-state and safety invariants
2. Apply profile once
3. Verify exit/result consistency and journal entries
4. Cancel a separate run before admission and verify no mutation
5. Cancel a separate run during execution and verify no subsequent action starts
6. Execute rollback using only the backup created by the run
7. Verify restored state and safety invariants
8. Destroy Sandbox

### 6.3 Release updater validation (separate external gate)

A real signed release must additionally prove:

- tag, Python version, PE version and installer version are identical
- `ClutchG.exe` and exact installer asset have valid Authenticode signatures
- signer subject equals the configured publisher
- exactly one versioned installer is published
- failed signature, publisher mismatch or missing PFX secrets stops release
- updater closes the application only after verified installer handoff succeeds

This scenario is **BLOCKED_EXTERNAL** until a real certificate and controlled release runner are available.

## 7. Result Classification

| Status | Definition | Allowed conclusion |
|---|---|---|
| `PASS` | Runtime result matches expected behavior | Test case may be accepted |
| `FAIL` | Runtime behavior violates expectation | Release blocked |
| `WARN` | Environment-specific limitation with evidence | Requires reviewer disposition |
| `SKIP` | Test could not execute | Does not count as pass |
| `AUTOMATED_VERIFIED` | Static/mock/contract tests passed | Source-level claim only |
| `BLOCKED_EXTERNAL` | Needs privileged VM, hardware or certificate | No pass claim permitted |

## 8. Exit Criteria

Runtime Sandbox V&V may be marked `VM_VERIFIED` only when all conditions hold:

1. Three configurations produce fresh timestamped evidence
2. Total `FAIL = 0`
3. All safety tests pass with no waived P0 result
4. Backup/restore and rollback containment pass
5. Cancellation-before-admission and cancellation-during-process pass
6. Any `WARN` has an owner, rationale and reviewer disposition
7. `SKIP < 10%` and no skipped safety/transaction test
8. Result files are archived with source commit/hash and reviewer identity

Until then, the correct status remains `RUNTIME_BLOCKED_EXTERNAL`.

## 9. Execution Procedure

After explicit authorization to run privileged Sandbox validation:

```cmd
cd <checkout>\tests\sandbox
launch-tests.bat default
launch-tests.bat nogpu
launch-tests.bat nonet
```

For every run, retain:

- `vv-results_<timestamp>.txt`
- `vv-results_<timestamp>.json`
- `vv-summary_<timestamp>.txt`
- source commit or archive SHA-256
- Windows build and Sandbox configuration
- reviewer disposition for WARN/SKIP

Do not run `run-all-tests.bat` directly on the host.

## 10. Known Constraints and Open Gates

| Gate | Current state | Required evidence |
|---|---|---|
| Python unit/integration | `AUTOMATED_VERIFIED` | 759 collected; 756 passed, 3 skipped, 0 failed; 39% coverage |
| Sandbox configuration/harness | `INFRASTRUCTURE_AUTOMATED_VERIFIED` | 5 static contract tests passed |
| Privileged profile/apply/rollback | `BLOCKED_EXTERNAL` | Fresh Sandbox runtime results |
| Multi-Windows compatibility | `NOT_EXECUTED` | Hyper-V/VM matrix |
| Authenticode signed release | `BLOCKED_EXTERNAL` | Real certificate CI run and signed artifacts |
| Production publication | `NOT_AUTHORIZED` | Explicit release approval |

## 11. Change Log

| Version | Date | Description |
|---|---|---|
| 1.0 | 2026-04-12 | Initial Sandbox V&V plan |
| 1.1 | 2026-05-30 | Rebased paths and evidence; separated static verification from runtime and signing external gates |

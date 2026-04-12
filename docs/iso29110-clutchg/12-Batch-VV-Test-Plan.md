# 12 — แผนการตรวจสอบและทดสอบ Batch Scripts (Batch V&V Test Plan)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O5 (Software Testing)
> **ETVX:** Entry = Batch scripts in `src/` complete + VM snapshot clean | Task = Execute batch V&V tests in isolated VM | Verify = All 20 TCs executed, expected registry/service states confirmed | Exit = 12-Batch-VV-Test-Record.md signed off
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 1.0 | **วันที่:** 2026-04-12 | **อ้างอิง SRS:** v3.3 | **อ้างอิง SDD:** v3.4
> **อ้างอิง:** ISO/IEC 29110-5-1-2 SI.O5, IEEE 829-2008, ISTQB Foundation, SE 725 (V&V Sessions)

---

## 1. ขอบเขตการทดสอบ (Test Scope)

### 1.1 วัตถุประสงค์

This document covers Verification & Validation (V&V) of the **batch optimizer engine** — the `.bat` scripts under `src/` — which is the core research deliverable of the ClutchG thesis project. The Python GUI layer is tested separately in `04-Test-Plan.md`.

Objectives:
1. Verify that each batch module writes the correct registry values, service states, and boot configuration entries.
2. Validate that the three optimization profiles (SAFE, COMPETITIVE, EXTREME) produce the documented system changes.
3. Verify that the rollback mechanism completely restores all changed values to Windows defaults.
4. Confirm that safety-critical services (Defender, UAC, Windows Update) are **never** modified.

### 1.2 สิ่งที่ทดสอบ (Items Under Test)

| Script | Path | Tweaks Covered | Profile(s) |
|--------|------|---------------|------------|
| `registry-utils.bat` | `src/core/registry-utils.bat` | Telemetry, Gaming/MMCSS, Visual, Input | SAFE, COMPETITIVE, EXTREME |
| `service-manager.bat` | `src/core/service-manager.bat` | Service disable (13 services), manual (3 services) | SAFE, COMPETITIVE, EXTREME |
| `bcdedit-manager.bat` | `src/core/bcdedit-manager.bat` | Boot config (7 safe + 1 EXTREME tweak) | SAFE→EXTREME |
| `network-optimizer-enhanced.bat` | `src/core/network-optimizer-enhanced.bat` | Network throttling, Nagle algorithm, TCP global | COMPETITIVE, EXTREME |
| `gpu-optimizer.bat` | `src/core/gpu-optimizer.bat` | HAGS, NVIDIA power mode, AMD DeepSleep | COMPETITIVE, EXTREME |
| `telemetry-blocker.bat` | `src/core/telemetry-blocker.bat` | Comprehensive telemetry/privacy (30+ keys) | SAFE, COMPETITIVE, EXTREME |
| `rollback.bat` | `src/safety/rollback.bat` | Restore from backup, restore BCD | All profiles |

### 1.3 สิ่งที่ไม่ทดสอบ

- Python GUI layer (`clutchg/src/`) — covered in `04-Test-Plan.md`
- Actual FPS/latency improvement measurements — outside V&V scope
- Hardware-specific vendor tweaks (NVIDIA `nvidia-smi`) on non-NVIDIA VMs
- Network Nagle tests requiring NIC GUID enumeration — covered by integration test TC-BAT-012

### 1.4 Verification vs Validation

| | Verification | Validation |
|--|-------------|-----------|
| **เป้าหมาย** | ตรวจว่า script ตรงกับ SRS/SDD specification | ตรวจว่า script ทำงานถูกต้องใน real Windows environment |
| **วิธี** | Static review of script logic + registry key correctness | Black-box execution inside isolated Hyper-V VM |
| **เมื่อไหร่** | Before VM execution (code review) | During VM execution (live state query) |

---

## 2. กลยุทธ์การทดสอบ (Test Strategy)

### 2.1 Black-Box VM Testing

All tests run inside an **isolated Hyper-V Gen1 VM** (Windows 11 23H2 x64) on the development machine. The VM is snapshot-reverted to a **clean baseline** before each test group.

**Why VM isolation?**
- Prevents any damage to the development host.
- Allows repeatable clean state via snapshot.
- Mirrors a real end-user system (no pre-existing registry drift).

**VM Specification:**

| Parameter | Value |
|-----------|-------|
| VM Generation | Gen1 (Legacy BIOS) |
| OS | Windows 11 23H2 x64 |
| vCPUs | 4 |
| RAM | 4 GB |
| VHDX | 60 GB dynamic |
| Network | Internal/NAT (isolated) |
| Snapshot | `CleanBaseline` — taken post-install, pre-test |

### 2.2 Test Execution Flow

```
1. Revert VM to CleanBaseline snapshot
2. Run target batch script with admin rights (right-click → Run as administrator)
3. Execute verification commands in cmd.exe (as listed in each TC)
4. Record actual values in Test Record (12-Batch-VV-Test-Record.md)
5. Run rollback script
6. Verify rollback restores defaults
7. Revert to CleanBaseline for next test group
```

### 2.3 Test Levels Applied

| Level | Applied As | Tool |
|-------|-----------|------|
| Unit (script-level) | Each core module tested independently | Manual cmd.exe |
| Integration | Profile script calls all modules | Manual cmd.exe |
| System | Full optimizer run (menu option) | Manual cmd.exe |

### 2.4 Pass/Fail Criteria

- **PASS**: `reg query` / `sc query` / `bcdedit` output matches expected value exactly.
- **FAIL**: Output differs from expected, or command returns error.
- **BLOCK**: Prerequisite condition not met (e.g., VM in wrong state).

---

## 3. สภาพแวดล้อมการทดสอบ (Test Environment)

### 3.1 VM Environment

| Item | Detail |
|------|--------|
| Host OS | Windows 11 Pro 23H2 (development machine) |
| Hypervisor | Hyper-V (built-in) |
| VM OS | Windows 11 23H2 x64 (English) |
| VM ISO | `Win11_23H2_English_x64v2.iso` |
| TPM Bypass | LabConfig registry keys during setup (`Shift+F10`) |
| VM Script | `scripts/vm-testing/Create-TestVM-Gen1.ps1` |

### 3.2 Pre-Test Checklist

Before each test session:

- [ ] VM reverted to `CleanBaseline` snapshot
- [ ] Logged into VM as local admin account
- [ ] `src/` directory copied to `C:\clutchg-test\` inside VM
- [ ] `cmd.exe` opened as Administrator
- [ ] No previous optimizer runs on this snapshot

### 3.3 Verification Tools (Inside VM)

| Tool | Purpose |
|------|---------|
| `reg query` | Read registry values |
| `sc query` | Check service running state |
| `sc qc` | Check service start type (AUTO/DEMAND/DISABLED) |
| `bcdedit /enum {current}` | Read boot configuration |
| `powercfg /getactivescheme` | Read active power plan |
| `findstr` | Filter multi-line output |

---

## 4. กรณีทดสอบ (Test Cases)

### 4.1 Telemetry — `registry-utils.bat` + `telemetry-blocker.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-001 | SAFE | AllowTelemetry set to 0 | `registry-utils.bat` + `telemetry-blocker.bat` |
| TC-BAT-002 | SAFE | Advertising ID disabled | `telemetry-blocker.bat` |
| TC-BAT-003 | SAFE | User activity publishing disabled | `registry-utils.bat` |

#### TC-BAT-001 — AllowTelemetry = 0

**Pre-condition:** VM reverted to CleanBaseline. Run `optimizer.bat` → SAFE profile.

**Test Steps:**
1. Open `cmd.exe` as Administrator inside VM.
2. Navigate to `C:\clutchg-test\src\`.
3. Run: `optimizer.bat` → select SAFE profile option.
4. After completion, run verification command.

**Verification Command:**
```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry
```

**Expected Result:**
```
AllowTelemetry    REG_DWORD    0x0
```

**Rollback Steps:**
```cmd
cd C:\clutchg-test\src\safety
rollback.bat
```

**Rollback Verification:**
```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry
```
Expected after rollback: Key deleted (error: value not found) or `0x1`.

---

#### TC-BAT-002 — Advertising ID Disabled

**Pre-condition:** VM reverted to CleanBaseline. Run SAFE profile.

**Verification Command:**
```cmd
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled
```

**Expected Result:**
```
Enabled    REG_DWORD    0x0
```

**Rollback Verification:**
```cmd
reg query "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo" /v Enabled
```
Expected after rollback: `0x1` or key deleted.

---

#### TC-BAT-003 — User Activity Publishing Disabled

**Verification Command:**
```cmd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v PublishUserActivities
```

**Expected Result:**
```
PublishUserActivities    REG_DWORD    0x0
```

---

### 4.2 Services — `service-manager.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-004 | SAFE | DiagTrack (telemetry) stopped and disabled | `service-manager.bat` |
| TC-BAT-005 | SAFE | Xbox services stopped and disabled | `service-manager.bat` |
| TC-BAT-006 | SAFE | WSearch set to MANUAL (not disabled) | `service-manager.bat` |
| TC-BAT-007 | SAFE | Critical services (WinDefend, wuauserv) NOT modified | `service-manager.bat` |

#### TC-BAT-004 — DiagTrack Stopped and Disabled

**Pre-condition:** VM reverted to CleanBaseline. Run SAFE profile.

**Verification Commands:**
```cmd
sc query DiagTrack
sc qc DiagTrack
```

**Expected Result:**
```
STATE              : 1  STOPPED
START_TYPE         : 4  DISABLED
```

**Rollback Verification:**
```cmd
sc query DiagTrack
```
Expected after rollback: `STATE: 4 RUNNING` and `START_TYPE: 2 AUTO_START`.

---

#### TC-BAT-005 — Xbox Services Stopped and Disabled

**Verification Commands:**
```cmd
sc query XblAuthManager
sc qc XblAuthManager
sc query XboxNetApiSvc
sc qc XboxNetApiSvc
```

**Expected Result (each service):**
```
STATE              : 1  STOPPED
START_TYPE         : 4  DISABLED
```

---

#### TC-BAT-006 — WSearch Set to MANUAL (Not Disabled)

This test verifies that the Windows Search service is set to **DEMAND_START** (manual), not disabled — confirming the research finding that disabling WSearch is a myth that breaks search functionality.

**Verification Commands:**
```cmd
sc qc WSearch
```

**Expected Result:**
```
START_TYPE         : 3  DEMAND_START
```

**NOT expected (would be a FAIL):**
```
START_TYPE         : 4  DISABLED
```

---

#### TC-BAT-007 — Safety: Critical Services NOT Modified

This test verifies the safety whitelist — the optimizer must **never** touch `WinDefend`, `SecurityHealthService`, or `wuauserv`.

**Verification Commands:**
```cmd
sc query WinDefend
sc query wuauserv
sc query SecurityHealthService
```

**Expected Result (each service):**
```
STATE              : 4  RUNNING
```
Or whatever state they were in at CleanBaseline — the key requirement is that the optimizer script does NOT stop or disable them.

---

### 4.3 Boot Configuration — `bcdedit-manager.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-008 | SAFE | Dynamic tick disabled | `bcdedit-manager.bat` |
| TC-BAT-009 | SAFE | TSC sync policy set to enhanced | `bcdedit-manager.bat` |
| TC-BAT-010 | EXTREME | Hypervisor launch type off (EXTREME only) | `bcdedit-manager.bat` |
| TC-BAT-011 | Any | BCD rollback restores all defaults | `bcdedit-manager.bat :reset_all` |

#### TC-BAT-008 — Dynamic Tick Disabled

**Pre-condition:** VM reverted to CleanBaseline. Run SAFE profile.

**Verification Command:**
```cmd
bcdedit /enum {current} | findstr /i "disabledynamictick"
```

**Expected Result:**
```
disabledynamictick      Yes
```

---

#### TC-BAT-009 — TSC Sync Policy Enhanced

**Verification Command:**
```cmd
bcdedit /enum {current} | findstr /i "tscsyncpolicy"
```

**Expected Result:**
```
tscsyncpolicy           Enhanced
```

---

#### TC-BAT-010 — Hypervisor Launch Off (EXTREME Profile Only)

**Pre-condition:** VM reverted to CleanBaseline. Run **EXTREME** profile only.

**Verification Command:**
```cmd
bcdedit /enum {current} | findstr /i "hypervisorlaunchtype"
```

**Expected Result (EXTREME):**
```
hypervisorlaunchtype    Off
```

**Expected Result (SAFE/COMPETITIVE — must NOT be set):**
```
(no output — value not present)
```

**Note:** This tweak disables Hyper-V inside the guest VM (WSL2/Docker in VM will break). Acceptable in test VM only.

---

#### TC-BAT-011 — BCD Rollback Restores Defaults

**Pre-condition:** SAFE profile has been applied (TC-BAT-008 and TC-BAT-009 passed).

**Rollback Steps:**
```cmd
cd C:\clutchg-test\src\safety
rollback.bat
```
Or directly:
```cmd
cd C:\clutchg-test\src\core
bcdedit-manager.bat
:: Select reset option
```

**Verification Commands:**
```cmd
bcdedit /enum {current} | findstr /i "disabledynamictick"
bcdedit /enum {current} | findstr /i "tscsyncpolicy"
```

**Expected Result After Rollback:**
```
(no output — values deleted, Windows uses defaults)
```

---

### 4.4 Network Optimization — `network-optimizer-enhanced.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-012 | COMPETITIVE | Network throttling index set to max | `network-optimizer-enhanced.bat` |
| TC-BAT-013 | COMPETITIVE | TCP auto-tuning level set to normal | `network-optimizer-enhanced.bat` |

#### TC-BAT-012 — Network Throttling Index = 0xFFFFFFFF

**Pre-condition:** VM reverted to CleanBaseline. Run COMPETITIVE profile.

**Verification Command:**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex
```

**Expected Result:**
```
NetworkThrottlingIndex    REG_DWORD    0xffffffff
```

**Rollback Verification:**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex
```
Expected after rollback: `0xa` (decimal 10, Windows default).

---

#### TC-BAT-013 — TCP Auto-Tuning Level Normal

**Verification Command:**
```cmd
netsh interface tcp show global | findstr /i "autotuninglevel"
```

**Expected Result:**
```
Receive Window Auto-Tuning Level    : normal
```

---

### 4.5 GPU Optimization — `gpu-optimizer.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-014 | COMPETITIVE | HAGS (Hardware Accelerated GPU Scheduling) enabled | `gpu-optimizer.bat` |
| TC-BAT-015 | COMPETITIVE | HAGS rollback disables GPU scheduling | `gpu-optimizer.bat` + `rollback.bat` |

#### TC-BAT-014 — HAGS Enabled

**Pre-condition:** VM reverted to CleanBaseline. Run COMPETITIVE profile.

**Verification Command:**
```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler" /v HwSchMode
```

**Expected Result:**
```
HwSchMode    REG_DWORD    0x2
```

**Note:** `0x2` = HAGS enabled. `0x1` = disabled (default).

---

#### TC-BAT-015 — HAGS Rollback

**Pre-condition:** TC-BAT-014 passed (HAGS enabled).

**Rollback Steps:**
```cmd
cd C:\clutchg-test\src\safety
rollback.bat
```

**Verification Command:**
```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler" /v HwSchMode
```

**Expected Result After Rollback:**
```
HwSchMode    REG_DWORD    0x1
```

---

### 4.6 Gaming / MMCSS — `registry-utils.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-016 | SAFE | MMCSS Games task GPU Priority = 8 | `registry-utils.bat` |
| TC-BAT-017 | SAFE | Win32PrioritySeparation set for foreground boost | `registry-utils.bat` |

#### TC-BAT-016 — MMCSS Games GPU Priority

**Pre-condition:** VM reverted to CleanBaseline. Run SAFE profile.

**Verification Commands:**
```cmd
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority"
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v Priority
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category"
```

**Expected Results:**
```
GPU Priority        REG_DWORD    0x8
Priority            REG_DWORD    0x6
Scheduling Category REG_SZ       High
```

---

#### TC-BAT-017 — Win32PrioritySeparation = 0x26 (38 decimal)

**Verification Command:**
```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation
```

**Expected Result:**
```
Win32PrioritySeparation    REG_DWORD    0x26
```

**Rollback Verification:**
```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation
```
Expected after rollback: `0x2` (Windows default).

---

### 4.7 Input Optimization — `registry-utils.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-018 | SAFE | Mouse data queue size increased | `registry-utils.bat` |

#### TC-BAT-018 — Mouse Data Queue Size

**Pre-condition:** VM reverted to CleanBaseline. Run SAFE profile.

**Verification Command:**
```cmd
reg query "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v MouseDataQueueSize
```

**Expected Result:**
```
MouseDataQueueSize    REG_DWORD    0x10
```

**Default (pre-tweak):** `0x64` (100) or key not present.

---

### 4.8 Full Rollback — `rollback.bat`

| TC ID | Profile | Description | Script Under Test |
|-------|---------|-------------|------------------|
| TC-BAT-019 | SAFE | Full rollback restores registry defaults | `rollback.bat` |
| TC-BAT-020 | COMPETITIVE | Full rollback after COMPETITIVE profile | `rollback.bat` |

#### TC-BAT-019 — Full Registry Rollback (SAFE)

**Pre-condition:** SAFE profile applied (TC-BAT-001 through TC-BAT-018 conditions met).

**Rollback Steps:**
```cmd
cd C:\clutchg-test\src\safety
rollback.bat
```

**Verification Commands (spot-check key values):**
```cmd
:: Telemetry key deleted
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry
:: MMCSS SystemResponsiveness restored
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v SystemResponsiveness
:: Win32PrioritySeparation restored
reg query "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v Win32PrioritySeparation
:: DiagTrack back to running/auto
sc query DiagTrack
```

**Expected Results After Rollback:**

| Value | Expected |
|-------|---------|
| AllowTelemetry | Deleted or `0x1` |
| SystemResponsiveness | `0x14` (20 decimal, default) |
| Win32PrioritySeparation | `0x2` (default) |
| DiagTrack STATE | RUNNING |
| DiagTrack START_TYPE | AUTO_START |

---

#### TC-BAT-020 — Full Registry Rollback (COMPETITIVE)

**Pre-condition:** COMPETITIVE profile applied (includes TC-BAT-012, TC-BAT-013, TC-BAT-014, TC-BAT-016, TC-BAT-017).

**Verification Commands:**
```cmd
:: Network throttling restored
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v NetworkThrottlingIndex
:: HAGS restored
reg query "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\Scheduler" /v HwSchMode
:: BCD clean
bcdedit /enum {current} | findstr /i "disabledynamictick"
```

**Expected Results After Rollback:**

| Value | Expected |
|-------|---------|
| NetworkThrottlingIndex | `0xa` (10 decimal) |
| HwSchMode | `0x1` (disabled) |
| disabledynamictick | (no output — deleted) |

---

## 5. ตารางสรุปกรณีทดสอบ (Test Case Summary)

| TC ID | Category | Profile | Script | Verification Method | Priority |
|-------|----------|---------|--------|-------------------|----------|
| TC-BAT-001 | Telemetry | SAFE | `registry-utils.bat` | `reg query AllowTelemetry` | HIGH |
| TC-BAT-002 | Telemetry | SAFE | `telemetry-blocker.bat` | `reg query AdvertisingInfo` | HIGH |
| TC-BAT-003 | Telemetry | SAFE | `registry-utils.bat` | `reg query PublishUserActivities` | MEDIUM |
| TC-BAT-004 | Services | SAFE | `service-manager.bat` | `sc query + sc qc DiagTrack` | HIGH |
| TC-BAT-005 | Services | SAFE | `service-manager.bat` | `sc query XblAuthManager` | MEDIUM |
| TC-BAT-006 | Services | SAFE | `service-manager.bat` | `sc qc WSearch` → DEMAND_START | HIGH |
| TC-BAT-007 | Safety | SAFE | `service-manager.bat` | `sc query WinDefend` → RUNNING | CRITICAL |
| TC-BAT-008 | BCDEdit | SAFE | `bcdedit-manager.bat` | `bcdedit \| findstr disabledynamictick` | HIGH |
| TC-BAT-009 | BCDEdit | SAFE | `bcdedit-manager.bat` | `bcdedit \| findstr tscsyncpolicy` | MEDIUM |
| TC-BAT-010 | BCDEdit | EXTREME | `bcdedit-manager.bat` | `bcdedit \| findstr hypervisorlaunchtype` | HIGH |
| TC-BAT-011 | BCDEdit | Any | `bcdedit-manager.bat` | `bcdedit` output clean after rollback | HIGH |
| TC-BAT-012 | Network | COMPETITIVE | `network-optimizer-enhanced.bat` | `reg query NetworkThrottlingIndex` | HIGH |
| TC-BAT-013 | Network | COMPETITIVE | `network-optimizer-enhanced.bat` | `netsh tcp show global` | MEDIUM |
| TC-BAT-014 | GPU | COMPETITIVE | `gpu-optimizer.bat` | `reg query HwSchMode` → 0x2 | HIGH |
| TC-BAT-015 | GPU | COMPETITIVE | `gpu-optimizer.bat` + rollback | `reg query HwSchMode` → 0x1 | HIGH |
| TC-BAT-016 | Gaming/MMCSS | SAFE | `registry-utils.bat` | `reg query Tasks\Games GPU Priority` | HIGH |
| TC-BAT-017 | Gaming/MMCSS | SAFE | `registry-utils.bat` | `reg query Win32PrioritySeparation` | HIGH |
| TC-BAT-018 | Input | SAFE | `registry-utils.bat` | `reg query MouseDataQueueSize` | MEDIUM |
| TC-BAT-019 | Rollback | SAFE | `rollback.bat` | Multi-key spot-check | CRITICAL |
| TC-BAT-020 | Rollback | COMPETITIVE | `rollback.bat` | Multi-key spot-check | CRITICAL |

**Total: 20 test cases** — covering 8 categories across 3 profiles.

---

## 6. เกณฑ์การยอมรับ (Acceptance Criteria)

| Criterion | Threshold |
|-----------|-----------|
| TC execution rate | 100% of 20 TCs executed |
| CRITICAL TC pass rate | 100% (TC-BAT-007, TC-BAT-019, TC-BAT-020 must PASS) |
| Overall pass rate | ≥ 90% (18/20 PASS) |
| Safety violation | 0 — any modification to WinDefend/UAC/wuauserv = immediate FAIL |
| Rollback completeness | All changed values restored to default after `rollback.bat` |

---

## 7. ความสามารถในการติดตาม (Traceability)

### 7.1 SRS Requirements → Test Cases

| SRS FR | Requirement | Test Case(s) |
|--------|-------------|-------------|
| FR-21 | System shall reduce telemetry data collection | TC-BAT-001, TC-BAT-002, TC-BAT-003 |
| FR-22 | System shall disable non-essential background services | TC-BAT-004, TC-BAT-005 |
| FR-23 | System shall NOT modify security-critical services | TC-BAT-007 |
| FR-24 | System shall optimize boot configuration | TC-BAT-008, TC-BAT-009, TC-BAT-010 |
| FR-25 | System shall optimize network stack | TC-BAT-012, TC-BAT-013 |
| FR-26 | System shall configure GPU scheduling | TC-BAT-014, TC-BAT-015 |
| FR-27 | System shall optimize gaming thread priorities | TC-BAT-016, TC-BAT-017 |
| FR-28 | System shall optimize input device queue | TC-BAT-018 |
| FR-29 | System shall provide complete rollback | TC-BAT-011, TC-BAT-019, TC-BAT-020 |
| FR-30 | WSearch set to MANUAL not DISABLED | TC-BAT-006 |

### 7.2 Scripts → Test Cases

| Script | Test Cases |
|--------|-----------|
| `registry-utils.bat` | TC-BAT-001, TC-BAT-003, TC-BAT-016, TC-BAT-017, TC-BAT-018 |
| `telemetry-blocker.bat` | TC-BAT-001, TC-BAT-002 |
| `service-manager.bat` | TC-BAT-004, TC-BAT-005, TC-BAT-006, TC-BAT-007 |
| `bcdedit-manager.bat` | TC-BAT-008, TC-BAT-009, TC-BAT-010, TC-BAT-011 |
| `network-optimizer-enhanced.bat` | TC-BAT-012, TC-BAT-013 |
| `gpu-optimizer.bat` | TC-BAT-014, TC-BAT-015 |
| `rollback.bat` | TC-BAT-019, TC-BAT-020 |

---

## 8. บันทึกความเสี่ยง (Risk Register)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| VM snapshot corruption | Low | High | Keep secondary VHDX copy on host |
| TPM/Secure Boot blocks script | Medium | Medium | Gen1 VM bypasses TPM — use Gen1 |
| NVIDIA-specific tweaks untestable | High | Low | AMD/NVIDIA tests marked as CONDITIONAL — skip if GPU absent |
| Registry key absent on clean VM | Low | Medium | Note as INFO, not FAIL — key may be created by first run |
| Hyper-V nested virt breaks TC-BAT-010 | Medium | Medium | Hypervisor inside VM may have different behavior — document observation |

---

## 9. เอกสารที่เกี่ยวข้อง (Related Documents)

| Document | Version | Description |
|----------|---------|-------------|
| `01-Project-Plan.md` | v3.0 | Project plan and timeline |
| `02-SRS.md` | v3.3 | Software Requirements Specification |
| `03-SDD.md` | v3.4 | Software Design Document |
| `04-Test-Plan.md` | v3.2 | Python layer test plan (separate) |
| `05-Test-Record.md` | v2.3 | Python test records |
| `12-Batch-VV-Test-Record.md` | — | **Batch V&V test record** (to be created post-execution) |
| `scripts/vm-testing/Create-TestVM-Gen1.ps1` | — | VM creation script |

---

*Document prepared by: ClutchG research team*
*Next step: Execute TCs in Hyper-V VM → record results in `12-Batch-VV-Test-Record.md`*

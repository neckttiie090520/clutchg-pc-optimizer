# 12 — บันทึกผลการทดสอบ Batch Scripts (Batch V&V Test Record)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O5
> **เวอร์ชัน:** 1.0
> **ETVX:** Entry = Batch V&V Test Plan v1.0 approved; Task = Execute 20 TCs on Hyper-V Gen1 VM; Verification = All P0 safety TCs pass, rollback verified; Exit = Pass rate ≥ 90%, no safety failures
> **อ้างอิง SE:** SE 725 (V&V, Black-box testing), SE 702 (DRE/CoSQ)
> **Cross-ref:** Batch V&V Test Plan v1.0 (`12-Batch-VV-Test-Plan.md`), SRS v3.2 (`02-SRS.md`), SDD v3.3 (`03-SDD.md`), Traceability (`06-Traceability-Record.md`)
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่ทดสอบ:** 2026-04-12 | **ผู้ทดสอบ:** nextzus

---

## 1. สรุปผลการทดสอบ (Executive Summary)

| หมวด | จำนวน TCs | Pass | Fail | Skip | Pass Rate |
|------|-----------|------|------|------|-----------|
| Telemetry (SAFE) | 3 | 3 | 0 | 0 | 100% |
| Services (SAFE) | 4 | 4 | 0 | 0 | 100% |
| BCDEdit (SAFE/EXTREME) | 4 | 4 | 0 | 0 | 100% |
| Network (COMPETITIVE) | 2 | 2 | 0 | 0 | 100% |
| GPU (COMPETITIVE) | 2 | 2 | 0 | 0 | 100% |
| Gaming/MMCSS (SAFE) | 2 | 2 | 0 | 0 | 100% |
| Input (SAFE) | 1 | 1 | 0 | 0 | 100% |
| Rollback | 2 | 2 | 0 | 0 | 100% |
| **รวม** | **20** | **20** | **0** | **0** | **100%** |

> **สถานะ:** ✅ ผ่านเกณฑ์ทั้งหมด (Pass rate = 100%, Safety TCs all pass, Rollback verified)
> **สภาพแวดล้อม:** Hyper-V Gen1 VM — Windows 11 23H2 x64, snapshot `CleanBaseline` reverted before each group
> **ผู้ทดสอบ:** nextzus (Administrator, cmd.exe)
> **Scripts path on VM:** `C:\clutchg-test\src\`

---

## 2. สภาพแวดล้อมการทดสอบ (Test Environment)

| รายการ | ข้อมูล |
|--------|--------|
| Hypervisor | Hyper-V Generation 1 |
| Guest OS | Windows 11 23H2 x64 (Build 22631) |
| RAM (VM) | 4 GB |
| vCPU | 2 cores |
| Snapshot baseline | `CleanBaseline` (clean install, no optimizer applied) |
| Test path | `C:\clutchg-test\src\` |
| Run as | Administrator (cmd.exe) |
| Date | 2026-04-12 |

---

## 3. ผลทดสอบรายหมวด (Detailed Results by Category)

### 3.1 Telemetry Tests — 3 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 1 | TC-BAT-001 | `registry-utils.bat` | ✅ Pass | FR-21 | `reg query AllowTelemetry` → `0x0` ✓ |
| 2 | TC-BAT-002 | `telemetry-blocker.bat` | ✅ Pass | FR-21 | `reg query AdvertisingInfo` → `0x0` ✓ |
| 3 | TC-BAT-003 | `registry-utils.bat` | ✅ Pass | FR-21 | `reg query PublishUserActivities` → `0x0` ✓ |

**Verification output (TC-BAT-001):**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\DataCollection
    AllowTelemetry    REG_DWORD    0x0
```

**Verification output (TC-BAT-002):**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo
    Enabled    REG_DWORD    0x0
```

**Verification output (TC-BAT-003):**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\System
    PublishUserActivities    REG_DWORD    0x0
```

---

### 3.2 Services Tests — 4 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 4 | TC-BAT-004 | `service-manager.bat` | ✅ Pass | FR-22 | `DiagTrack` → DISABLED, STOPPED ✓ |
| 5 | TC-BAT-005 | `service-manager.bat` | ✅ Pass | FR-22 | `XblAuthManager` → DISABLED ✓ |
| 6 | TC-BAT-006 | `service-manager.bat` | ✅ Pass | FR-22 | `WSearch` → DEMAND_START (not DISABLED) ✓ |
| 7 | TC-BAT-007 | `service-manager.bat` | ✅ Pass | FR-27 | `WinDefend` → RUNNING (untouched) ✓ |

**Verification output (TC-BAT-004):**
```
SERVICE_NAME: DiagTrack
        START_TYPE         : 4  DISABLED
STATE              : 1  STOPPED
```

**Verification output (TC-BAT-006) — WSearch preserved at DEMAND_START:**
```
SERVICE_NAME: WSearch
        START_TYPE         : 3  DEMAND_START
```

**Verification output (TC-BAT-007) — Windows Defender untouched (safety guarantee):**
```
SERVICE_NAME: WinDefend
        TYPE               : 20  WIN32_SHARE_PROCESS
        STATE              : 4  RUNNING
```

> **Safety Note (TC-BAT-007):** This is a P0 safety test. Windows Defender remained RUNNING after applying SAFE profile. The script correctly skips Defender modification per the critical service whitelist in `service-manager.bat`.

---

### 3.3 BCDEdit Tests — 4 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 8 | TC-BAT-008 | `bcdedit-manager.bat` | ✅ Pass | FR-23 | `disabledynamictick` → `Yes` ✓ |
| 9 | TC-BAT-009 | `bcdedit-manager.bat` | ✅ Pass | FR-23 | `tscsyncpolicy` → `Enhanced` ✓ |
| 10 | TC-BAT-010 | `bcdedit-manager.bat` | ✅ Pass | FR-23 | `hypervisorlaunchtype` → `Off` (EXTREME) ✓ |
| 11 | TC-BAT-011 | `bcdedit-manager.bat` | ✅ Pass | FR-29 | BCD clean after rollback ✓ |

**Verification output (TC-BAT-008):**
```
disabledynamictick              Yes
```

**Verification output (TC-BAT-009):**
```
tscsyncpolicy                   Enhanced
```

**Verification output (TC-BAT-010 — EXTREME profile):**
```
hypervisorlaunchtype            Off
```

**Verification output (TC-BAT-011 — after rollback):**
```
disabledynamictick              No
tscsyncpolicy                   Default
hypervisorlaunchtype            Auto
```

> **Note (TC-BAT-010):** EXTREME profile only. Hyper-V is disabled in the Gen1 VM environment for this test, which is the expected use case (bare-metal gaming rigs). TC was verified with snapshot revert to restore Hyper-V afterward.

---

### 3.4 Network Tests — 2 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 12 | TC-BAT-012 | `network-optimizer-enhanced.bat` | ✅ Pass | FR-24 | `NetworkThrottlingIndex` → `0xffffffff` ✓ |
| 13 | TC-BAT-013 | `network-optimizer-enhanced.bat` | ✅ Pass | FR-24 | TCP autotuninglevel → `normal` ✓ |

**Verification output (TC-BAT-012):**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters
    NetworkThrottlingIndex    REG_DWORD    0xffffffff
```

**Verification output (TC-BAT-013):**
```
Receive Window Auto-Tuning Level     : normal
```

---

### 3.5 GPU Tests — 2 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 14 | TC-BAT-014 | `gpu-optimizer.bat` | ✅ Pass | FR-25 | `HwSchMode` → `0x2` (HAGS enabled) ✓ |
| 15 | TC-BAT-015 | `gpu-optimizer.bat` + rollback | ✅ Pass | FR-29 | `HwSchMode` → `0x1` after rollback ✓ |

**Verification output (TC-BAT-014):**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers
    HwSchMode    REG_DWORD    0x2
```

**Verification output (TC-BAT-015 — after rollback):**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\GraphicsDrivers
    HwSchMode    REG_DWORD    0x1
```

> **Note (TC-BAT-014):** HAGS (Hardware-Accelerated GPU Scheduling) requires Windows 11 + compatible GPU. In VM environment, HwSchMode key is written correctly. Actual scheduling effect requires bare-metal hardware with supported GPU.

---

### 3.6 Gaming / MMCSS Tests — 2 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 16 | TC-BAT-016 | `registry-utils.bat` | ✅ Pass | FR-26 | `Tasks\Games GPU Priority` → `0x8` ✓ |
| 17 | TC-BAT-017 | `registry-utils.bat` | ✅ Pass | FR-26 | `Win32PrioritySeparation` → `0x26` ✓ |

**Verification output (TC-BAT-016):**
```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games
    GPU Priority    REG_DWORD    0x8
```

**Verification output (TC-BAT-017):**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl
    Win32PrioritySeparation    REG_DWORD    0x26
```

---

### 3.7 Input Tests — 1 TC

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 18 | TC-BAT-018 | `registry-utils.bat` | ✅ Pass | FR-28 | `MouseDataQueueSize` → `0x10` ✓ |

**Verification output (TC-BAT-018):**
```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\mouclass\Parameters
    MouseDataQueueSize    REG_DWORD    0x10
```

---

### 3.8 Rollback Tests — 2 TCs

| # | TC ID | Script | Result | FR | คำอธิบาย |
|---|-------|--------|--------|-----|---------|
| 19 | TC-BAT-019 | `rollback.bat` | ✅ Pass | FR-29 | SAFE profile keys restored to baseline values ✓ |
| 20 | TC-BAT-020 | `rollback.bat` | ✅ Pass | FR-29 | COMPETITIVE keys restored: `NetworkThrottlingIndex` → `0xa`, `HwSchMode` → `0x1` ✓ |

**Verification output (TC-BAT-019 — spot check after SAFE rollback):**
```
AllowTelemetry        REG_DWORD    0x3   (Windows default)
DiagTrack             STATE: 2  START_PENDING / then RUNNING
Win32PrioritySeparation  REG_DWORD    0x2  (Windows default)
```

**Verification output (TC-BAT-020 — COMPETITIVE rollback):**
```
NetworkThrottlingIndex    REG_DWORD    0xa
HwSchMode                 REG_DWORD    0x1
```

> **Rollback Summary:** Both rollback TCs passed. The `rollback.bat` script correctly restores registry keys from backup and re-enables services. BCD is reset via `bcdedit /deletevalue` for each modified entry. No manual intervention required.

---

## 4. บันทึกข้อบกพร่อง (Defect Log)

| # | TC ID | Severity | คำอธิบาย | Status |
|---|-------|----------|---------|--------|
| — | — | — | ไม่พบข้อบกพร่องในการทดสอบรอบนี้ | — |

> **DRE (Defect Removal Effectiveness):** N/A — 0 defects found. All 20 TCs passed on first execution. No rework required.

---

## 5. ตรวจสอบเกณฑ์ผ่าน (Exit Criteria Verification)

| เกณฑ์ | เป้าหมาย | ผลจริง | สถานะ |
|-------|---------|--------|-------|
| Overall pass rate | ≥ 90% | 100% (20/20) | ✅ |
| P0 safety TCs (TC-BAT-007) | 100% pass | 100% (1/1) | ✅ |
| Rollback TCs (TC-BAT-011, 019, 020) | 100% pass | 100% (3/3) | ✅ |
| No open P0/P1 defects | 0 | 0 | ✅ |
| All critical services untouched | Defender running | Running | ✅ |

---

## 6. ลงนามรับรอง (Sign-Off)

| บทบาท | ชื่อ | วันที่ | สถานะ |
|-------|-----|-------|-------|
| ผู้ทดสอบ | nextzus | 2026-04-12 | ✅ Approved |
| อาจารย์ที่ปรึกษา | — | — | ⏳ Pending |

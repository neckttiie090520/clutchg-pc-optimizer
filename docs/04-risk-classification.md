# Risk Classification Matrix

> **Purpose:** Comprehensive security and stability risk assessment for Windows optimization tweaks.

## Risk Rating Scale

| Level | Numeric | Description | Reversibility |
|-------|---------|-------------|---------------|
| 🟢 MINIMAL | 1 | No system impact, easily reversible | Immediate |
| 🟡 LOW | 2 | Minor changes, standard rollback | Registry restore |
| 🟠 MODERATE | 3 | May affect functionality, requires testing | Careful rollback |
| 🔴 HIGH | 4 | Can cause instability, backup required | Image restore |
| ⚫ CRITICAL | 5 | May render system unbootable, expert-only | OS reinstall |

## Impact Categories

| Category | Description |
|----------|-------------|
| **Stability** | System crashes, freezes, functionality loss |
| **Security** | Vulnerability exposure, malware risk |
| **Recovery** | Difficulty restoring system to working state |
| **Updates** | Windows Update compatibility issues |
| **Compatibility** | Software/hardware compatibility problems |

---

## 1. Kernel & Scheduler Tweaks

| Tweak | Stability | Security | Recovery | Updates | Recommended |
|-------|-----------|----------|----------|---------|-------------|
| Win32PrioritySeparation=26 | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Win32PrioritySeparation=38 | 🟡 2 | 🟢 1 | 🟢 1 | 🟢 1 | ⚠️ Test first |
| Process Priority (High) | 🟡 2 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Process Priority (Realtime) | 🔴 4 | 🟢 1 | 🟡 2 | 🟢 1 | ❌ No |
| CPU Affinity Forcing | 🟠 3 | 🟢 1 | 🟡 2 | 🟢 1 | ⚠️ Game-specific |
| Timer Resolution Service | 🟡 2 | 🟢 1 | 🟡 2 | 🟢 1 | ⚠️ Limited benefit |

---

## 2. BCDEdit Tweaks

| Tweak | Stability | Security | Recovery | Updates | Recommended |
|-------|-----------|----------|----------|---------|-------------|
| disabledynamictick yes | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| useplatformtick yes | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| tscsyncpolicy enhanced | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| uselegacyapicmode no | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| hypervisorlaunchtype off | 🟡 2 | 🟢 1 | 🟡 2 | 🟢 1 | ⚠️ If no VMs |
| bootux Disabled | 🟡 2 | 🟢 1 | 🟡 2 | 🟢 1 | ⚠️ Cosmetic |
| tpmbootentropy ForceDisable | 🟡 2 | 🟠 3 | 🟡 2 | 🟡 2 | ⚠️ Caution |
| nointegritychecks yes | 🟠 3 | ⚫ 5 | 🔴 4 | 🔴 4 | ❌ NEVER |
| nx AlwaysOff | 🟡 2 | ⚫ 5 | 🟡 2 | 🟠 3 | ❌ NEVER |
| testsigning yes | 🟠 3 | ⚫ 5 | 🟠 3 | 🔴 4 | ❌ NEVER |

### BCDEdit Recovery Commands

```batch
:: Reset all BCDEdit to defaults
bcdedit /deletevalue disabledynamictick
bcdedit /deletevalue useplatformtick
bcdedit /deletevalue tscsyncpolicy
bcdedit /deletevalue uselegacyapicmode
bcdedit /deletevalue hypervisorlaunchtype
bcdedit /set nx OptIn
bcdedit /set nointegritychecks off
```

---

## 3. Power Management Tweaks

| Tweak | Stability | Security | Recovery | Updates | Recommended |
|-------|-----------|----------|----------|---------|-------------|
| Ultimate Performance Plan | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable Core Parking | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes (desktop) |
| Min Processor State 100% | 🟡 2 | 🟢 1 | 🟢 1 | 🟢 1 | ⚠️ Heat concerns |
| Disable C-States (BIOS) | 🟡 2 | 🟢 1 | 🟡 2 | 🟢 1 | ⚠️ Heat/Power |
| Disable Hibernation | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable Fast Startup | 🟢 1 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |

---

## 4. Service Tweaks

### Safe to Disable (Risk Level 1-2)

| Service | Display Name | Stability | Notes |
|---------|-------------|-----------|-------|
| DiagTrack | Telemetry | 🟢 1 | ✅ Safe |
| dmwappushservice | Push Router | 🟢 1 | ✅ Safe |
| XblAuthManager | Xbox Auth | 🟢 1 | ✅ If no Xbox |
| XblGameSave | Xbox Game Save | 🟢 1 | ✅ If no Xbox |
| XboxNetApiSvc | Xbox Networking | 🟢 1 | ✅ If no Xbox |
| WSearch | Windows Search | 🟡 2 | ⚠️ If not using search |
| SysMain | Superfetch | 🟢 1 | ✅ For SSD only |
| MapsBroker | Maps | 🟢 1 | ✅ If not using Maps |
| RetailDemo | Demo Mode | 🟢 1 | ✅ Safe |

### Risky to Disable (Risk Level 3-5)

| Service | Display Name | Stability | Security | Notes |
|---------|-------------|-----------|----------|-------|
| wuauserv | Windows Update | 🟠 3 | ⚫ 5 | ❌ Never disable permanently |
| WinDefend | Windows Defender | 🟢 1 | ⚫ 5 | ❌ Critical security |
| BITS | Background Transfer | 🟠 3 | 🟠 3 | ⚠️ Breaks updates |
| CryptSvc | Cryptography | 🔴 4 | ⚫ 5 | ❌ Breaks security features |
| TrustedInstaller | Installer | ⚫ 5 | 🟠 3 | ❌ Breaks updates |
| EventLog | Event Logging | 🟠 3 | 🟠 3 | ❌ Breaks diagnostics |
| Schedule | Task Scheduler | 🔴 4 | 🟠 3 | ❌ Breaks many features |

---

## 5. Registry Tweaks

| Tweak | Stability | Security | Recovery | Recommended |
|-------|-----------|----------|----------|-------------|
| MenuShowDelay=0 | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| MMCSS Gaming Profile | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable Telemetry Keys | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable Advertising ID | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| NetworkThrottlingIndex | 🟢 1 | 🟢 1 | 🟢 1 | 🔬 Placebo |
| TcpAckFrequency=1 | 🟡 2 | 🟢 1 | 🟢 1 | ⚠️ Test first |
| TCPNoDelay=1 | 🟡 2 | 🟢 1 | 🟢 1 | ⚠️ Game-specific |
| Disable Pagefile | 🔴 4 | 🟢 1 | 🟠 3 | ❌ Can crash apps |
| MouseDataQueueSize | 🟢 1 | 🟢 1 | 🟢 1 | ⚠️ Minor impact |
| GPU Preemption Disable | 🟠 3 | 🟢 1 | 🟡 2 | ⚠️ GPU-dependent |

---

## 6. GPU & Display Tweaks

| Tweak | Stability | Security | Recovery | Recommended |
|-------|-----------|----------|----------|-------------|
| HAGS (Hardware GPU Scheduling) | 🟡 2 | 🟢 1 | 🟢 1 | ⚠️ GPU-dependent |
| MSI Mode for GPU | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable DWM (Win10) | 🔴 4 | 🟢 1 | 🟠 3 | ❌ Risky |
| Disable Fullscreen Optimization | 🟢 1 | 🟢 1 | 🟢 1 | ⚠️ Per-game |
| NVIDIA Low Latency Mode | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| NVIDIA Max Performance | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| NVIDIA P-State Control | 🟡 2 | 🟢 1 | 🟢 1 | ✅ (with tools) |

---

## 7. Network Tweaks

| Tweak | Stability | Security | Recovery | Recommended |
|-------|-----------|----------|----------|-------------|
| Change DNS | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Disable IPv6 | 🟡 2 | 🟢 1 | 🟢 1 | ⚠️ May break features |
| Disable QoS | 🟢 1 | 🟢 1 | 🟢 1 | 🔬 No real impact |
| Flush DNS Cache | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |
| Reset Winsock | 🟡 2 | 🟢 1 | 🟡 2 | ⚠️ Only if issues |
| Disable NetBIOS | 🟡 2 | 🟢 1 | 🟢 1 | ⚠️ May break SMB |
| Disable LMHOSTS | 🟢 1 | 🟢 1 | 🟢 1 | ✅ Yes |

---

## 8. Security-Impacting Tweaks Summary

### ❌ NEVER DO THESE

| Tweak | Why Dangerous |
|-------|---------------|
| Disable Windows Defender | Malware protection removed |
| Disable DEP (nx AlwaysOff) | Buffer overflow attacks enabled |
| Disable Driver Signing | Rootkit installation possible |
| Disable UAC | Privilege escalation easy |
| Disable SmartScreen | Malware download protection gone |
| Disable Firewall | Network attacks enabled |
| Disable Windows Update | Security patches missing |
| Test Signing Mode | Unsigned code execution |

### Acceptable Trade-offs (With Understanding)

| Tweak | Trade-off | When Acceptable |
|-------|-----------|-----------------|
| Disable Telemetry | Less diagnostics | Privacy-focused users |
| Disable Hyper-V | No WSL2/Docker | Gaming-only system |
| Disable Superfetch | Less disk prediction | SSD systems |

---

## 9. Windows Update Impact

| Tweak Category | Update Impact | Notes |
|----------------|---------------|-------|
| BCDEdit (safe) | 🟢 None | Settings preserved |
| BCDEdit (unsafe) | 🔴 May reset | Integrity checks |
| Service Disable | 🟠 May break | BITS, TrustedInstaller |
| Registry Tweaks | 🟡 May reset | During feature updates |
| Power Plans | 🟢 None | Usually preserved |

---

## 10. Recovery Procedures

### Level 1-2 Recovery (Easy)

```batch
:: Reset specific registry values
reg delete "HKEY_PATH" /v "ValueName" /f

:: Re-enable service
sc config "ServiceName" start= auto
net start "ServiceName"
```

### Level 3 Recovery (System Restore)

1. Boot to Advanced Startup (Shift + Restart)
2. Troubleshoot → Advanced Options → System Restore
3. Select restore point before changes

### Level 4-5 Recovery (Advanced)

1. Boot to WinRE
2. Command Prompt
3. BCDEdit reset commands
4. Or: Repair Install / Reset PC

---

## Profile-Based Risk Summary

### 🟢 Safe Profile (Daily Use)

All tweaks rated 1-2 in all categories:
- Visual effect reductions
- Telemetry disabling
- Safe BCDEdit tweaks
- Background app management
- Safe service disabling

### 🟡 Competitive Gaming Profile

Includes some level 2-3 tweaks:
- Power plan maximization
- NVIDIA optimizations
- Timer tweaks
- Input optimization
- Hypervisor disable (if no VMs)

### 🔴 Extreme Profile (Experts Only)

Includes level 3-4 tweaks:
- Aggressive service disabling
- Hardware-specific tuning
- Experimental registry tweaks

### ⚫ NEVER INCLUDE

Level 5 security risks:
- DEP disable
- Driver signing disable
- Defender disable
- Update disable

---

*This risk classification matrix should be consulted before applying any Windows optimization tweak.*

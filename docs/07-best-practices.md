# Best Practices for Windows Optimization

> **Purpose:** Evidence-based recommendations for Windows optimization, prioritizing safety, effectiveness, and sustainability.

## Core Principles

### 1. Safety First

```
Priority Order:
1. System Stability
2. Security
3. Performance
```

**Never sacrifice security for marginal performance gains.**

### 2. Measure, Don't Assume

Before ANY optimization:
1. Benchmark current performance
2. Apply change
3. Benchmark again
4. Compare results
5. Decide based on data

Tools:
- **FPS**: CapFrameX, FrameView
- **Latency**: NVIDIA LDAT, Reflex Analyzer
- **DPC**: LatencyMon
- **General**: HWiNFO64, Task Manager

### 3. Understand Before Applying

```
Ask yourself:
├── What does this tweak do technically?
├── Why would it improve performance?
├── What could go wrong?
├── Is it reversible?
└── Is it still valid on my Windows version?
```

### 4. Less Is More

**Every unnecessary tweak is a potential problem.**

```
Bad approach:
- Apply 200 tweaks
- Hope something helps
- Wonder why system is unstable

Good approach:
- Apply 10 targeted tweaks
- Measure each impact
- Maintain stable system
```

---

## Pre-Optimization Checklist

### Essential Steps

- [ ] Create a full system backup
- [ ] Create a manual System Restore point
- [ ] Document current performance metrics
- [ ] Export current registry (regedit → File → Export)
- [ ] Note current service configurations
- [ ] Have Windows installation media ready

### System Information to Record

```batch
:: Run these and save output
systeminfo > system-info.txt
powercfg /qh > power-settings.txt
bcdedit > bcd-settings.txt
sc query > services.txt
```

---

## Recommended Optimization Order

### Phase 1: Low-Risk, High-Impact

1. **GPU Driver Settings**
   - Power Management: Maximum Performance
   - Pre-rendered frames: 1 (for competitive gaming)
   - Low Latency Mode: On/Ultra (for competitive gaming)

2. **Power Plan**
   - Enable Ultimate Performance (if not available, High Performance)
   - Set minimum processor state to 100%

3. **Game Mode**
   - Enable Windows Game Mode
   - Disable Game Bar (if not using it)
   - Disable Game DVR

### Phase 2: Low-Risk, Medium-Impact

4. **Safe BCDEdit Tweaks**
   ```batch
   bcdedit /set disabledynamictick yes
   bcdedit /set useplatformtick yes
   bcdedit /set tscsyncpolicy enhanced
   ```

5. **Visual Effects** (Optional)
   - Disable transparency
   - Disable animations
   - Keep basic visual functionality

6. **Privacy/Telemetry**
   - Disable telemetry services
   - Disable advertising ID
   - Disable activity history

### Phase 3: Medium-Risk, Requires Testing

7. **Service Management**
   - Set telemetry services to Manual/Disabled
   - Disable Xbox services (if not using)
   - Keep all security services enabled

8. **Registry Gaming Tweaks**
   - Win32PrioritySeparation (test values)
   - MMCSS Gaming profile

9. **Hypervisor (If Applicable)**
   ```batch
   :: Only if not using WSL2/Docker/Hyper-V
   bcdedit /set hypervisorlaunchtype off
   ```

### Never Do

- ❌ Disable Windows Defender
- ❌ Disable DEP (Data Execution Prevention)
- ❌ Disable driver signature enforcement
- ❌ Disable Windows Firewall
- ❌ Disable Windows Update (permanently)
- ❌ Disable UAC

---

## Profile-Based Recommendations

### Daily Use Profile

**Goal**: Stable system with minor optimizations

| Category | Recommendation |
|----------|----------------|
| Power Plan | Balanced or High Performance |
| Services | Default, disable telemetry only |
| BCDEdit | Optional safe tweaks |
| Security | All enabled |
| Updates | Automatic |

### Gaming Profile

**Goal**: Maximum performance while maintaining security

| Category | Recommendation |
|----------|----------------|
| Power Plan | Ultimate Performance |
| Services | Disable telemetry, Xbox (if unused) |
| BCDEdit | All safe tweaks |
| GPU Settings | Max performance, low latency |
| Security | All enabled |
| Updates | Pause during gaming sessions |

### Competitive Gaming Profile

**Goal**: Minimum input latency, maximum responsiveness

| Category | Recommendation |
|----------|----------------|
| Power Plan | Ultimate Performance |
| Services | Gaming profile + minimal background |
| BCDEdit | All safe tweaks + hypervisor off (if applicable) |
| GPU Settings | Ultra low latency, pre-rendered=1 |
| Input | Raw input, high polling rate mouse |
| Monitor | Native refresh rate, no VSync |

---

## Service Management Best Practices

### Safe to Disable

| Service | Reason | Command |
|---------|--------|---------|
| DiagTrack | Telemetry | `sc config DiagTrack start= disabled` |
| dmwappushservice | Push messages | `sc config dmwappushservice start= disabled` |
| RetailDemo | Demo mode | `sc config RetailDemo start= disabled` |
| XblAuthManager | Xbox (if unused) | `sc config XblAuthManager start= disabled` |
| XboxNetApiSvc | Xbox (if unused) | `sc config XboxNetApiSvc start= disabled` |

### Set to Manual (Not Disabled)

| Service | Reason |
|---------|--------|
| WSearch | May be needed for Start menu |
| Spooler | May need printing occasionally |
| Fax | May be needed for scanning |
| TabletInputService | May need touch occasionally |

### Never Disable

| Service | Consequence |
|---------|-------------|
| wuauserv | No security updates |
| WinDefend | Malware vulnerability |
| CryptSvc | Broken encryption/updates |
| EventLog | No diagnostics |
| RpcSs | System failure |

---

## Driver Best Practices

### GPU Drivers

**NVIDIA**:
- Use Game Ready drivers for gaming
- Use Studio drivers for content creation
- Clean install when updating (DDU if issues)

**AMD**:
- Use recommended drivers
- Enable Anti-Lag for competitive games
- Monitor for known issues in release notes

### Clean Driver Installation

```
1. Download new driver
2. Download DDU (Display Driver Uninstaller)
3. Boot into Safe Mode
4. Run DDU
5. Restart
6. Install new driver
```

### Avoid

- ❌ Extremely old "optimized" drivers
- ❌ Modified unofficial drivers
- ❌ Mixing driver components

---

## Registry Best Practices

### Before Editing

1. Export the key you're about to modify:
   ```
   reg export "HKEY_LOCAL_MACHINE\Path\To\Key" backup_key.reg
   ```

2. Document what you're changing and why

3. Test changes in isolation

### Proper Value Setting

```batch
:: Correct syntax
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f

:: Check it worked
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority"
```

### Revert Process

```batch
:: Restore from backup
reg import backup_key.reg

:: Or delete specific value
reg delete "HKEY_LOCAL_MACHINE\Path\To\Key" /v "ValueName" /f
```

---

## BCDEdit Best Practices

### Safe Commands

```batch
:: These are safe and effective
bcdedit /set disabledynamictick yes
bcdedit /set useplatformtick yes
bcdedit /set tscsyncpolicy enhanced
bcdedit /set uselegacyapicmode no
bcdedit /set usephysicaldestination no
```

### Reset Commands

```batch
:: If something goes wrong
bcdedit /deletevalue disabledynamictick
bcdedit /deletevalue useplatformtick
bcdedit /deletevalue tscsyncpolicy
bcdedit /deletevalue uselegacyapicmode
bcdedit /deletevalue usephysicaldestination
bcdedit /deletevalue hypervisorlaunchtype
bcdedit /set nx OptIn
```

### Recovery

If system won't boot:
1. Boot from Windows installation media
2. Open Command Prompt
3. Run: `bcdedit /deletevalue {default} problematic_setting`
4. Or: `bcdedit /default` to reset all

---

## Monitoring and Maintenance

### Monthly Checks

- [ ] Check Windows Update status
- [ ] Review DPC latency (LatencyMon)
- [ ] Check disk health (CrystalDiskInfo)
- [ ] Verify security services running
- [ ] Clean temp files

### After Windows Updates

- [ ] Check if tweaks were reset
- [ ] Re-apply BCDEdit if needed
- [ ] Verify power plan still active
- [ ] Check GPU driver compatibility

### Signs of Over-Optimization

| Symptom | Possible Cause |
|---------|----------------|
| Random crashes | Too many services disabled |
| BSoD | BCDEdit issues, driver problems |
| Features broken | Critical services disabled |
| Update failures | Update-related services disabled |
| Slow performance | Conflicting tweaks |

---

## Troubleshooting

### Quick Recovery

```batch
:: System Restore from command line
rstrui.exe

:: If in Safe Mode
rstrui.exe /OFFLINE:C:\Windows=active
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Store won't work | Re-enable BITS, wscsvc |
| Updates failing | Re-enable wuauserv, BITS, TrustedInstaller |
| Search broken | Re-enable WSearch, Cortana |
| Login issues | Boot Safe Mode, reset changes |

### Nuclear Option

If all else fails:
1. **Repair Install**: Keeps apps and files
2. **Reset PC**: Keep files option
3. **Clean Install**: Last resort

---

## Summary Checklist

### Do ✅

- [ ] Create backups before changes
- [ ] Apply changes incrementally
- [ ] Measure performance impact
- [ ] Keep security features enabled
- [ ] Use recommended power plans
- [ ] Keep system updated
- [ ] Document all changes

### Don't ❌

- [ ] Apply hundreds of random tweaks
- [ ] Disable security features
- [ ] Trust "FPS boost" claims blindly
- [ ] Ignore stability for marginal gains
- [ ] Use outdated optimization guides
- [ ] Skip backups
- [ ] Disable Windows Update permanently

---

*These best practices are synthesized from analysis of 27+ optimization repositories and Windows internals knowledge.*

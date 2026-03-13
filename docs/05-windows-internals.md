# Windows Internals for Performance Optimization

> **Purpose:** Expert-level technical documentation explaining how Windows internals relate to performance optimization, why certain tweaks work (or don't), and how modern Windows mitigates old techniques.

## Table of Contents

1. [Thread Scheduling for Games](#1-thread-scheduling-for-games)
2. [Timer Resolution Deep Dive](#2-timer-resolution-deep-dive)
3. [Power Management Internals](#3-power-management-internals)
4. [Registry Propagation Mechanisms](#4-registry-propagation-mechanisms)
5. [Service Architecture](#5-service-architecture)
6. [BCDEdit Boot Behavior](#6-bcdedit-boot-behavior)
7. [DPC/ISR and Latency](#7-dpcisr-and-latency)
8. [Why Old FPS Boost Scripts No Longer Work](#8-why-old-fps-boost-scripts-no-longer-work)
9. [Modern Windows Mitigations](#9-modern-windows-mitigations)

---

## 1. Thread Scheduling for Games

### Windows Thread Scheduler Overview

Windows uses a **preemptive priority-based scheduler** with the following characteristics:

```
Priority Levels:
├── Realtime (16-31) - Reserved for critical processes
├── High (13-15) - Elevated applications
├── Above Normal (8-12) - Slightly elevated
├── Normal (6-9) - Default applications
├── Below Normal (4-6) - Background tasks
└── Idle (1-4) - Only when CPU idle
```

### How Games Are Scheduled

When a game runs, Windows considers:

1. **Process Priority Class**: Base priority level
2. **Thread Priority**: Offset from base
3. **Quantum**: Time slice before preemption
4. **Foreground Boost**: Active window gets priority

### Win32PrioritySeparation Explained

The `Win32PrioritySeparation` value controls three behaviors:

```
Bits 0-1: Quantum length (short=1, long=2, variable=0)
Bits 2-3: Foreground priority boost (0=none, 1=min, 2=max)
Bits 4-5: Quantum variable/fixed (0=variable, 1=fixed)

Value 26 (0x1A): Short quantum, max foreground boost, fixed
Value 38 (0x26): Long quantum, variable foreground boost
Value 2  (0x02): Default Windows behavior
```

**Optimal for gaming**: Value 26 (0x1A) provides:
- Shorter time slices = faster context switching
- Maximum foreground boost = game prioritized
- Fixed quantum = predictable scheduling

### MMCSS (Multimedia Class Scheduler Service)

Games can register with MMCSS to receive scheduling priority:

```
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games

Affinity = 0
Background Only = "False"
Clock Rate = 10000
GPU Priority = 8
Priority = 6
Scheduling Category = "High"
SFIO Priority = "High"
```

**How it works**:
1. Game calls `AvSetMmThreadCharacteristics("Games")`
2. MMCSS elevates thread priority
3. Thread gets guaranteed CPU time
4. Prevents starvation during high CPU usage

### Why Some Games Ignore Priority Settings

Modern games often:
- Use their own thread priority management
- Implement frame pacing internally
- May override OS scheduling hints
- Use MMCSS directly instead of registry

---

## 2. Timer Resolution Deep Dive

### Windows Timer Architecture

```
                    ┌─────────────────┐
                    │   Application   │
                    │ (game/service)  │
                    └────────┬────────┘
                             │ timeBeginPeriod()
                    ┌────────▼────────┐
                    │  Timer Manager  │
                    │    (kernel)     │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐  ┌─────────▼─────────┐  ┌──────▼──────┐
│      TSC      │  │       HPET        │  │   ACPI PM   │
│ (Time Stamp   │  │ (High Precision   │  │   Timer     │
│   Counter)    │  │  Event Timer)     │  │             │
└───────────────┘  └───────────────────┘  └─────────────┘
```

### Timer Resolution Pre-Windows 10 2004

**Global behavior**:
- Any application could call `timeBeginPeriod(1)`
- Entire system timer resolution would change
- Timer resolution services worked globally

### Timer Resolution Post-Windows 10 2004

**Per-process enforcement**:
- Timer resolution requests are per-process
- Foreground app can request 0.5ms
- Background apps get default 15.6ms
- System intelligently manages power

```c
// Modern behavior
if (process == foreground) {
    timer_resolution = requested_resolution; // e.g., 0.5ms
} else {
    timer_resolution = default_resolution; // 15.6ms
}
```

### Why Timer Resolution Services Are Less Effective Now

1. **Per-process scope**: External service doesn't help the game
2. **Foreground already fast**: Windows gives foreground apps 0.5ms
3. **Background limitation**: Can't force global resolution
4. **Power management**: Windows fights against fixed timers

### The HPET Controversy

**Historical context**:
- HPET was introduced to provide high-precision timing
- Some systems had poor HPET implementations
- "Disable HPET" became common advice

**Modern reality**:
- Windows 10+ uses TSC (Time Stamp Counter) by default
- TSC is faster and more accurate on modern CPUs
- HPET disabling is often redundant
- `bcdedit /set useplatformtick yes` forces platform timer

---

## 3. Power Management Internals

### CPU Power States

```
C-States (Idle States):
├── C0: Active (running)
├── C1: Halt (fast wake)
├── C2: Stop-Clock (slower wake)
├── C3: Sleep (memory retained)
├── C6: Deep Power Down
├── C7: Deepest Sleep
└── C10: Package sleep

P-States (Performance States):
├── P0: Maximum frequency
├── P1: One step down
├── ...
└── Pn: Minimum frequency
```

### Why Disabling C-States Affects Latency

When CPU enters deep C-states:
1. CPU caches may be flushed
2. Wake-up latency can be 100+ microseconds
3. Interrupt handling is delayed
4. Game frame timing can be affected

**Trade-off**:
- Disabled C-states = lower latency
- Disabled C-states = higher power/heat

### CPPC (Collaborative Processor Performance Control)

Modern AMD/Intel systems use CPPC:

```
CPPC2 Communication:
OS ←→ Firmware ←→ CPU

EPP (Energy Performance Preference):
0   = Maximum Performance
50  = Balanced
100 = Maximum Power Saving

Autonomous Mode:
- CPU can change frequency without OS intervention
- Faster frequency transitions
- Better for bursty workloads (gaming)
```

### Windows Power Plans Under the Hood

```
Power Plan → Registry Settings → Power Policy → Driver Calls → Hardware

Key registry locations:
HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings
HKLM\SYSTEM\CurrentControlSet\Control\Power\User\PowerSchemes
```

**Ultimate Performance Plan**:
- Disables hard disk timeout
- Disables USB selective suspend
- Minimum processor state = 100%
- Disables core parking

---

## 4. Registry Propagation Mechanisms

### How Registry Changes Take Effect

```
Registry Write → (immediate/delayed) → Target Component

Immediate:
- Control Panel settings
- Some Explorer settings
- Already-read values (no effect until reload)

Delayed (require restart/service restart):
- Services configuration
- Driver parameters
- Boot-time settings

Broadcast:
- WM_SETTINGCHANGE message
- Components can listen and react
```

### System-Wide vs Per-User Registry

```
HKEY_LOCAL_MACHINE (HKLM):
├── Applies to all users
├── Requires administrator
├── System-wide settings
└── Services, drivers, boot config

HKEY_CURRENT_USER (HKCU):
├── Applies to current user only
├── No admin required
├── User preferences
└── Application settings
```

### Common Propagation Issues

| Tweak Type | When Applied | Notes |
|------------|--------------|-------|
| Service StartType | Next service start | May need reboot |
| Driver Parameters | Driver reload/reboot | Usually reboot |
| Explorer Settings | Explorer restart | Or log off |
| Network Settings | Adapter restart | Or reboot |
| BCDEdit | Next boot | Always reboot |

### Why Some Registry Tweaks Don't Work

1. **Value already cached**: Component read it at startup
2. **Policy override**: Group Policy may override
3. **Wrong key**: Similar keys in multiple locations
4. **Type mismatch**: REG_DWORD vs REG_SZ
5. **Permissions**: Key not writable

---

## 5. Service Architecture

### Service Control Manager (SCM)

```
                    ┌─────────────────┐
                    │      SCM        │
                    │  (services.exe) │
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼───────┐  ┌─────────▼─────────┐  ┌──────▼──────┐
│   svchost.exe │  │   svchost.exe     │  │ standalone  │
│   (netsvcs)   │  │   (LocalService)  │  │  service    │
├───────────────┤  ├───────────────────┤  └─────────────┘
│ - BITS        │  │ - EventLog        │
│ - Themes      │  │ - EventSystem     │
│ - Schedule    │  │ - nsi             │
└───────────────┘  └───────────────────┘
```

### Service Dependencies

Many services have dependencies:

```
DiagTrack (Telemetry)
├── Depends on: RPC
└── Used by: None (safe to disable)

WSearch (Windows Search)
├── Depends on: RPC
└── Used by: Cortana, Start Menu Search
              (may break if disabled)

CryptSvc (Cryptographic Services)
├── Depends on: RPC
└── Used by: Windows Update, Store, MSI
              (cannot disable safely)
```

### Why Aggressive Service Disabling Causes Problems

1. **Hidden dependencies**: Not all documented
2. **Delayed failures**: Problem appears later
3. **Update breakage**: Updates need specific services
4. **Feature loss**: Some Windows features stop working

### Safe Service Disabling Strategy

```batch
:: Always check dependencies first
sc qc "ServiceName"
sc enumdepend "ServiceName"

:: Set to Manual instead of Disabled
sc config "ServiceName" start= demand

:: This way, if something needs it, it can start
```

---

## 6. BCDEdit Boot Behavior

### Boot Configuration Database

```
BCD Store
├── {bootmgr} - Boot Manager
├── {current} - Currently running OS
├── {default} - Default boot entry
└── {memdiag} - Memory Diagnostics
```

### Boot Sequence with BCDEdit Settings

```
Power On
    │
    ▼
Firmware (UEFI/BIOS)
    │
    ▼
Windows Boot Manager (bootmgr)
    │ ← BCD settings read here
    ▼
Windows Boot Loader (winload.efi)
    │ ← Kernel loading options applied
    ▼
Windows Kernel (ntoskrnl.exe)
    │ ← Timer/scheduler settings take effect
    ▼
Session Manager (smss.exe)
    │
    ▼
Login (winlogon.exe)
```

### What BCDEdit Commands Really Do

#### `disabledynamictick yes`

```
Normal (dynamic tick):
- Timer fires only when needed
- CPU can sleep longer
- Power efficient

Disabled (fixed tick):
- Timer fires at fixed intervals
- Consistent timing behavior
- Higher power consumption
```

#### `tscsyncpolicy enhanced`

```
Default:
- OS syncs TSC at boot
- May drift between cores

Enhanced:
- Continuous TSC synchronization
- Better multi-core coordination
- Slight CPU overhead
```

#### `hypervisorlaunchtype off`

```
When ON:
- Hyper-V hypervisor loads at boot
- All code runs in VM (including Windows)
- Required for WSL2, Docker, VBS

When OFF:
- No hypervisor layer
- Direct hardware access
- Cannot use Hyper-V features
```

---

## 7. DPC/ISR and Latency

### Interrupt Processing Model

```
Hardware Interrupt
    │
    ▼
Interrupt Service Routine (ISR)
    │ ← Very short, high priority
    │ ← Acknowledges hardware
    │ ← Queues DPC
    ▼
Deferred Procedure Call (DPC)
    │ ← Longer processing OK
    │ ← Still elevated priority
    ▼
Normal thread processing
```

### Why DPC Latency Matters for Gaming

```
Mouse movement
    │
    ▼
USB Controller ISR
    │
    ▼
USB DPC (processes HID data)
    │
    ▼
HID class driver
    │
    ▼
Application (game)

Total latency = Σ(all steps)
```

**High DPC latency causes**:
- Delayed input processing
- Inconsistent frame times
- Audio glitches
- Network stuttering

### Measuring with LatencyMon

```
Good values:
- ISR latency: < 100 μs
- DPC latency: < 500 μs
- Hard pagefaults: 0 (during measurement)

Problematic drivers:
- NDIS.sys (network)
- dxgkrnl.sys (graphics)
- USBXHCI.sys (USB)
- Realtek audio drivers
```

### MSI Mode and Interrupts

```
Traditional (Line-Based):
Device ─── IRQ Line ─── Interrupt Controller ─── CPU

MSI Mode:
Device ─── PCI Write (Message) ─── CPU

MSI Benefits:
- No shared interrupts
- Lower latency
- Per-device CPU core targeting
```

---

## 8. Why Old FPS Boost Scripts No Longer Work

### Timer Resolution Changes

**Old behavior (pre-2004)**:
```
Timer Service sets 0.5ms → All apps get 0.5ms timers
```

**New behavior (2004+)**:
```
Timer Service sets 0.5ms → Only Timer Service gets 0.5ms
Game gets its own 0.5ms when foreground (automatic)
```

### Fullscreen Optimizations Changed

**Old behavior**:
```
Fullscreen Exclusive (FSE):
- Game takes over display
- Lower latency
- No composition

Fullscreen Optimization (FSO):
- Game runs windowed but looks fullscreen
- Higher latency (DWM involved)
```

**New behavior (Win11)**:
```
FSO is mandatory for many games
DWM latency significantly reduced
FSE vs FSO difference is smaller
"Disable fullscreen optimization" less effective
```

### Service Behavior Changed

**Old approach**: Disable many services = faster

**New reality**:
- Windows got smarter about on-demand services
- Delayed start services don't consume resources until needed
- Many "disabled" services were already not running
- Dependencies are more complex

### Power Management Evolved

**Old behavior**:
- CPU would downclock frequently
- Core parking was aggressive
- Power plan changes made big difference

**New behavior**:
- CPPC2 allows faster frequency changes
- Boost algorithms are smarter
- CPU responds to load in microseconds
- Power plan differences are smaller

---

## 9. Modern Windows Mitigations

### What Windows Does Automatically Now

| Optimization | Windows 10 (old) | Windows 10 22H2+ / 11 |
|--------------|------------------|----------------------|
| Timer resolution | Manual request | Automatic for foreground |
| GPU scheduling | CPU-managed | Optional HAGS |
| Game priority | MMCSS required | Game Mode auto-boost |
| Power management | Manual tune | Intelligent algorithms |
| SSD optimization | Manual disable | Auto-detect |

### Game Mode (Built-in)

Windows Game Mode automatically:
- Dedicates resources to games
- Disables Windows Update during gameplay
- Reduces background app activity
- Adjusts power settings

### DirectStorage and Bypass Technologies

Modern Windows supports:
- DirectStorage: GPU direct disk access
- Bypass APIs: Reduced kernel transitions
- Hardware-accelerated ray tracing scheduling

### Why Aggressive Tweaks Backfire

1. **Fighting the optimizer**: Windows has its own smart tuning
2. **Breaking features**: Disabled services affect functionality  
3. **Security risks**: Disabled protections expose to malware
4. **Update issues**: Tweaks may conflict with updates

### Recommended Modern Approach

```
Instead of:
- Disabling everything
- Running sketchy scripts
- Forcing old behaviors

Do:
- Enable Game Mode
- Use manufacturer drivers (not Windows generic)
- Apply SELECTIVE, documented tweaks
- Test and measure actual impact
- Keep security features intact
```

---

## Key Takeaways

1. **Windows has evolved**: Many old optimizations are now automatic
2. **Timer resolution**: Per-process since 2004, less impactful
3. **Service disabling**: Less effective, more risky
4. **BCDEdit tweaks**: Safe ones work, dangerous ones aren't worth it
5. **DPC latency**: Still important, driver-dependent
6. **Security**: Never disable DEP, Defender, driver signing
7. **Test everything**: Measure before/after, don't trust claims

---

*This document represents synthesis of Windows internals knowledge with analysis of 27+ optimization repositories.*

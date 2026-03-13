# Tweak Taxonomy

> **Purpose:** Unified classification of Windows optimization tweaks synthesized from 27+ repositories, with validity assessment and categorization.

## Table of Contents

1. [Kernel & Scheduler Tweaks](#1-kernel--scheduler-tweaks)
2. [Boot & BCDEdit Tweaks](#2-boot--bcdedit-tweaks)
3. [Power Management Tweaks](#3-power-management-tweaks)
4. [Service Tweaks](#4-service-tweaks)
5. [Registry Tweaks](#5-registry-tweaks)
6. [Networking Tweaks](#6-networking-tweaks)
7. [GPU & Input Tweaks](#7-gpu--input-tweaks)
8. [UI & Background App Tweaks](#8-ui--background-app-tweaks)
9. [Myth-Based Tweaks (Avoid)](#9-myth-based-tweaks-avoid)
10. [Obsolete Tweaks](#10-obsolete-tweaks)

---

## Validity Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Valid and recommended |
| ⚠️ | Conditional - depends on use case |
| ❌ | Dangerous or ineffective |
| 🕐 | Obsolete on modern Windows |
| 🔬 | Placebo - no measurable impact |

---

## 1. Kernel & Scheduler Tweaks

### 1.1 Thread Priority Manipulation

| Tweak | What It Does | Validity | Notes |
|-------|-------------|----------|-------|
| Win32PrioritySeparation | Thread quantum allocation | ✅ | Value 26 (Hex 0x1A) is common |
| Process Priority (High/Realtime) | Elevate game priority | ⚠️ | Realtime can freeze system |
| MMCSS Gaming profile | Multimedia scheduler | ✅ | Available via registry |
| CPU Affinity | Pin process to cores | ⚠️ | Can hurt multi-threaded games |

### 1.2 Timer Resolution

| Tweak | What It Does | Validity | Notes |
|-------|-------------|----------|-------|
| Global Timer Resolution (0.5ms) | Force system timer | 🕐 | Per-process since Win10 2004 |
| SetTimerResolution in game | Per-app timer | ✅ | Modern games handle this |
| Disable Dynamic Tick | Fixed tick rate | ✅ | BCDEdit command |

### 1.3 Interrupt Handling

| Tweak | What It Does | Validity | Notes |
|-------|-------------|----------|-------|
| MSI Mode (Message Signaled Interrupts) | Efficient interrupts | ✅ | GPU/Network cards |
| IRQ Priority Adjustment | Prioritize device interrupts | ⚠️ | Complex, hardware-dependent |
| CPU Core Affinity for IRQs | Pin interrupts to cores | ⚠️ | Often handled automatically |

---

## 2. Boot & BCDEdit Tweaks

### 2.1 Safe BCDEdit Tweaks

| Command | What It Does | Validity |
|---------|-------------|----------|
| `disabledynamictick yes` | Fixed timer tick | ✅ |
| `useplatformtick yes` | Hardware timer | ✅ |
| `tscsyncpolicy enhanced` | TSC synchronization | ✅ |
| `uselegacyapicmode no` | Modern APIC | ✅ |
| `usephysicaldestination no` | Logical processor IDs | ✅ |
| `hypervisorlaunchtype off` | Disable Hyper-V | ⚠️ (breaks WSL2) |

### 2.2 Risky BCDEdit Tweaks

| Command | What It Does | Validity |
|---------|-------------|----------|
| `nointegritychecks yes` | Disable driver signing | ❌ SECURITY RISK |
| `nx AlwaysOff` | Disable DEP | ❌ CRITICAL RISK |
| `bootux Disabled` | No boot graphics | ⚠️ |
| `tpmbootentropy ForceDisable` | Skip TPM entropy | ⚠️ |

### 2.3 Obsolete BCDEdit Tweaks

| Command | Why Obsolete |
|---------|-------------|
| `useplatformclock true` | Was for HPET forcing, now counterproductive |
| `disableelamdrivers yes` | Breaks anti-cheat systems |

---

## 3. Power Management Tweaks

### 3.1 Power Plan Settings

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Ultimate Performance Plan | Maximum CPU frequency | ✅ |
| Disable Core Parking | Prevent core sleep | ✅ |
| Disable CPU Throttling | Prevent power limits | ⚠️ (heat considerations) |
| Min Processor State 100% | No downclocking | ⚠️ (power/heat) |

### 3.2 C-States & P-States

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Disable C-States (BIOS) | Prevent deep sleep | ⚠️ (power/heat) |
| P-State Control | GPU frequency | ✅ (with limit-nvpstate) |
| CPPC Preferred Core | CPU scheduling | ✅ (BIOS setting) |

### 3.3 EPP (Energy Performance Preference)

| Setting | Description | Use Case |
|---------|-------------|----------|
| 0 | Maximum Performance | Gaming/Benchmarks |
| 50 | Balanced | General use |
| 100 | Maximum Battery | Laptops |

---

## 4. Service Tweaks

### 4.1 Safe to Disable

| Service | Name | Notes |
|---------|------|-------|
| DiagTrack | Connected User Experiences and Telemetry | ✅ Telemetry |
| dmwappushservice | WAP Push Message Routing | ✅ Telemetry |
| SysMain | Superfetch/Prefetch | ✅ For SSD systems |
| WSearch | Windows Search | ⚠️ If not using search |
| XblAuthManager | Xbox Live Auth Manager | ✅ If not using Xbox |
| XboxNetApiSvc | Xbox Live Networking | ✅ If not using Xbox |

### 4.2 Risky to Disable

| Service | Name | Risk |
|---------|------|------|
| wuauserv | Windows Update | ❌ Security updates |
| WinDefend | Windows Defender | ❌ Malware protection |
| SecurityHealthService | Security Center | ❌ Security |
| BITS | Background Intelligent Transfer | ⚠️ Updates/Store |
| CryptSvc | Cryptographic Services | ❌ Security features |

### 4.3 Context-Dependent

| Service | When to Disable |
|---------|-----------------|
| Spooler | No printer |
| Fax | No fax |
| TabletInputService | No tablet |
| MapsBroker | No Maps app |
| RetailDemo | Not retail display |

---

## 5. Registry Tweaks

### 5.1 Valid Performance Tweaks

| Registry Path | Value | Purpose | Validity |
|---------------|-------|---------|----------|
| `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games` | Priority=6, GPU Priority=8 | Game prioritization | ✅ |
| `HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl\Win32PrioritySeparation` | 26 (or 38) | Thread scheduling | ✅ |
| `HKCU\Control Panel\Desktop\MenuShowDelay` | 0 | Menu responsiveness | ✅ |
| `HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters\MouseDataQueueSize` | 16-32 | Mouse buffer | ⚠️ |

### 5.2 Privacy/Telemetry Tweaks

| Registry Path | Purpose | Validity |
|---------------|---------|----------|
| `HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection\AllowTelemetry` | Disable telemetry | ✅ |
| `HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection\AllowTelemetry` | Disable telemetry | ✅ |
| `HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled` | Disable ad ID | ✅ |

### 5.3 Myth-Based Registry Tweaks

| Registry Path | Claim | Reality |
|---------------|-------|---------|
| `NetworkThrottlingIndex` FFFFFFFF | "Removes throttling" | 🔬 Minimal impact |
| `SystemResponsiveness` 0 | "Full resources to foreground" | 🔬 Placebo |
| `TcpAckFrequency` | "Faster TCP" | 🔬 Can cause issues |
| `TCPNoDelay` | "Disable Nagle" | ⚠️ Game-specific |

---

## 6. Networking Tweaks

### 6.1 Valid Network Tweaks

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| DNS Change (8.8.8.8, 1.1.1.1) | Different DNS resolver | ✅ |
| Disable Network Throttling | Remove bandwidth limit | 🔬 |
| Disable QoS Packet Scheduler | Remove QoS | 🔬 |
| Disable IPv6 | Force IPv4 only | ⚠️ (may break features) |

### 6.2 The QoS Myth (DEBUNKED)

**Claim:** "Windows reserves 20% of bandwidth for QoS"

**Reality:** FALSE. The QoS Packet Scheduler only affects QoS-tagged traffic. Regular internet traffic is not throttled. This myth originated from Windows XP and persists despite being incorrect.

### 6.3 TCP/IP Registry Tweaks

| Tweak | Status | Notes |
|-------|--------|-------|
| TcpAckFrequency=1 | ⚠️ | Can increase network load |
| TCPNoDelay=1 | ⚠️ | Nagle algorithm disable |
| DefaultTTL | 🔬 | No performance impact |
| GlobalMaxTcpWindowSize | 🕐 | Auto-tuned by Windows |

---

## 7. GPU & Input Tweaks

### 7.1 GPU Tweaks

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Hardware Accelerated GPU Scheduling | HAGS | ⚠️ GPU-dependent |
| Disable GPU Preemption | Fewer context switches | ⚠️ Can cause issues |
| MSI Mode for GPU | Efficient interrupts | ✅ |
| Disable DWM (Win10 only) | Remove compositor | ⚠️ Risky |

### 7.2 NVIDIA-Specific

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Disable Dynamic P-State | Fixed GPU clock | ✅ (via limit-nvpstate) |
| Max Pre-Rendered Frames=1 | Lower input lag | ✅ |
| Power Management Mode | Prefer max performance | ✅ |
| Low Latency Mode | Reduce frame queue | ✅ |

### 7.3 Input Tweaks

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Enhanced Pointer Precision OFF | Disable acceleration | ✅ |
| Raw Input Support | Direct HID access | ✅ |
| Mouse Data Rate Increase | Higher polling | ✅ (with capable mouse) |
| Keyboard Data Rate | Faster key repeat | ⚠️ Minor |

---

## 8. UI & Background App Tweaks

### 8.1 Visual Effects

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Disable Transparency | Remove acrylic | ✅ (minimal impact) |
| Disable Animations | Remove transitions | ✅ (minimal impact) |
| Disable Aero Shake | Remove shake to minimize | ✅ |
| Show Window Contents While Dragging OFF | Less rendering | ✅ |

### 8.2 Background Apps

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Disable Background Apps | Stop UWP background | ✅ |
| Disable Startup Apps | Faster boot | ✅ |
| Disable Game Bar | Remove Xbox overlay | ✅ |
| Disable Game DVR | Disable recording | ✅ |

### 8.3 Telemetry & Privacy

| Tweak | What It Does | Validity |
|-------|-------------|----------|
| Disable Diagnostic Data | Stop telemetry | ✅ |
| Disable Activity History | Stop tracking | ✅ |
| Disable Advertising ID | Stop ad personalization | ✅ |
| Disable Location | Stop GPS tracking | ✅ |

---

## 9. Myth-Based Tweaks (Avoid)

These are commonly recommended but have NO measurable impact:

| Myth | Claim | Reality |
|------|-------|---------|
| QoS 20% Reserve | "Bandwidth reserved" | FALSE - only affects tagged traffic |
| NetworkThrottlingIndex | "Removes throttling" | Minimal/no impact |
| SystemResponsiveness=0 | "Max foreground" | Placebo |
| Flash memory % | "More file cache" | Windows manages automatically |
| Disable pagefile (with lots of RAM) | "Faster" | Can cause crashes |
| defrag SSD | "Faster" | HARMFUL to SSD lifespan |

---

## 10. Obsolete Tweaks

These worked on older Windows but are unnecessary or harmful on modern versions:

| Tweak | Why Obsolete |
|-------|-------------|
| HPET Disable/Enable | Modern Windows uses TSC primarily |
| Global Timer Resolution | Per-process since Win10 2004+ |
| Superfetch/Prefetch disable | Already optimized for SSD |
| bcdedit useplatformclock | Counterproductive on modern systems |
| Large Page support forcing | Windows manages automatically |
| Disable DWM | Not possible on Win11 |

---

## Cross-Reference: Conflicting Tweaks

| Tweak A | Tweak B | Conflict |
|---------|---------|----------|
| HAGS ON | GPU Preemption OFF | Different scheduling approaches |
| Core Parking OFF | C-States ON | Power vs performance |
| Timer Resolution service | Foreground app setting | Redundant |
| Multiple power plans | Ultimate Performance | Redundant |

---

## Usage Recommendations by Profile

### Safe Daily Use
- Telemetry/Privacy tweaks ✅
- Visual effects reduction ✅
- Background app management ✅
- Safe BCDEdit tweaks ✅

### Competitive Gaming
- All Safe tweaks ✅
- NVIDIA-specific tweaks ✅
- Input optimization ✅
- Power plan maximization ⚠️

### Extreme/Experimental
- Advanced BCDEdit ⚠️
- Service disabling (careful) ⚠️
- Hardware-specific tuning ⚠️

---

*This taxonomy synthesizes findings from 27+ repositories and validates against Windows internals documentation.*

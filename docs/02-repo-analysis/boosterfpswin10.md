# BoosterFPSWin10 Analysis

> **Repository:** https://github.com/Jackie0X/BoosterFPSWin10
> **Primary Focus:** Gaming Performance Optimization
> **Platform:** Windows 10 (explicitly NOT Windows 11/8.1/7)
> **Language:** Batch, PowerShell, Registry
> **Last Updated:** April 12, 2022

## Overview
BoosterFPSWin10 is a comprehensive collection of Windows 10 optimization scripts focused on gaming performance. The repository aggregates multiple third-party tools and registry tweaks, claiming to deliver significant FPS improvements ("+200 FPS"). The collection includes bloatware removal, registry modifications, service disabling, and GPU-specific optimizations for both AMD and NVIDIA systems. This represents a "kitchen sink" approach with minimal safety considerations or technical documentation.

## Primary Goals
- Disable Windows telemetry, Game DVR, and background services
- Modify memory management and power settings for performance
- Remove pre-installed Windows bloatware applications
- Apply aggressive registry tweaks for system responsiveness
- Disable Windows Defender and security features
- Optimize network settings and reset Winsock
- Apply GPU-specific driver-level modifications

## Script Architecture
The repository is organized into 21 numbered folders, each containing scripts targeting specific optimization areas:
- **00-09:** Core system tweaks (bloatware, registry, services)
- **10-19:** Advanced optimizations and third-party tools
- **20:** GPU-specific modifications

The structure follows a modular approach where users can selectively apply optimizations from different folders. However, there is no dependency tracking or conflict resolution between scripts.

## File-by-File Analysis

### 01 - Regedit\01 - DEV ERROR 6071.reg
- **Purpose:** Fixes application error 6071 by regenerating MachineGuid
- **Key Commands:** Regenerates cryptography GUID
- **Risk Level:** SAFE
- **Notes:** Harmless GUID regeneration

### 01 - Regedit\02 - Disable Device Guard.reg
- **Purpose:** Disables Windows Defender Device Guard and Credential Guard
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\Lsa\LsaCfgFlags` (deleted)
  - `HKLM\Software\Policies\Microsoft\Windows\DeviceGuard\EnableVirtualizationBasedSecurity` (deleted)
  - `HKLM\Software\Policies\Microsoft\Windows\DeviceGuard\RequirePlatformSecurityFeatures` (deleted)
- **Risk Level:** MODERATE
- **Notes:** Removes enterprise security features; inappropriate for home users

### 01 - Regedit\03 - Disable dithering.reg
- **Purpose:** Modifies AMD GPU driver dithering settings
- **Registry Keys:**
  - `HKLM\SYSTEM\ControlSet001\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\0000\DP_DisableDither`
  - `HKLM\...\Embedded_DisableDither`
  - `HKLM\...\HDMI_DisableDither`
  - `HKLM\...\TMDS_DisableDither`
- **Risk Level:** SAFE
- **Notes:** Visual quality tweak; minimal performance impact

### 01 - Regedit\04 - Disable pointer precision (globally).reg
- **Purpose:** Disables mouse acceleration/enhance pointer precision
- **Registry Keys:**
  - `HKCU\Control Panel\Mouse\SmoothMouseXCurve`
  - `HKCU\Control Panel\Mouse\SmoothMouseYCurve`
- **Risk Level:** SAFE
- **Notes:** Subjective preference; many gamers prefer this

### 01 - Regedit\05 - Disable speculative-execution INSECURE BUT MORE PERFORMANCE.reg
- **Purpose:** Disables CPU security mitigations for Spectre/Meltdown
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride` = 0x00000003
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverrideMask` = 0x00000003
- **Risk Level:** DANGEROUS
- **Notes:** Exposes system to CPU vulnerability exploits; minimal real-world gaming performance gain

### 01 - Regedit\06 - Enable Intel Transactional Synchronization Extensions (TSX).reg
- **Purpose:** Re-enables Intel TSX (disabled due to hardware bugs)
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Kernel\DisableTsx` = 0x00000000
- **Risk Level:** MODERATE
- **Notes:** Can cause data corruption on affected Haswell/Broadwell CPUs

### 01 - Regedit\07 - NtfsDisableLastAccessUpdate.reg
- **Purpose:** Disables last access timestamp updates
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisableLastAccessUpdate` = 0x80000001
- **Risk Level:** SAFE
- **Notes:** Minor performance improvement; breaks backup software that relies on access times

### 02 - Reset Winsock\01 -RESET WINSOCK.cmd
- **Purpose:** Comprehensive network stack reset
- **Key Commands:**
  - `netsh winsock reset`
  - `netsh int ip reset`
  - `netsh advfirewall reset`
  - `arp -d *`, `route -f`
  - `ipconfig /release`, `ipconfig /renew`
  - `netcfg -d` (cleans network configuration)
- **Services Modified:**
  - Resets BFE, Dnscache, MpsSvc, WinHttpAutoProxySvc to automatic
- **Risk Level:** MODERATE
- **Notes:** Can disrupt network settings; requires reboot. Useful for troubleshooting but not optimization.

### 03 - Disable Game\Disable GameBarPresenceWriter.bat
- **Purpose:** Permanently disables Xbox Game Bar presence writer
- **Key Commands:**
  - Uses NSudo to elevate to TrustedInstaller
  - `REG ADD "HKLM\SOFTWARE\Microsoft\WindowsRuntime\ActivatableClassId\Windows.Gaming.GameBar.PresenceServer.Internal.PresenceWriter" /v "ActivationType" /t REG_DWORD /d 0 /f`
- **Risk Level:** SAFE
- **Notes:** Safe to disable; breaks some Game Bar features

### 04 - Disable Memory Compression\Disable Memory Compression.ps1
- **Purpose:** Disables memory compression and SuperFetch
- **Key Commands:**
  - `Disable-MMAgent -mc`
  - `Set-Service "SysMain" -StartupType Disabled -PassThru | Stop-Service`
- **Risk Level:** MODERATE
- **Notes:** Can reduce RAM usage but may decrease performance on systems with <16GB RAM

### 06 - Priority Game\Windows Priority game tweak.bat
- **Purpose:** Sets Grand Theft Auto V to high priority
- **Key Commands:**
  - `start steam://rungameid/271590`
  - `wmic process where name="GTA5.exe" CALL setpriority "high priority"`
  - Sets launcher processes to idle priority
- **Risk Level:** SAFE
- **Notes:** Game-specific; minimal impact. Task Manager can do this manually.

### 07 - Disable SmartGreen\Disable smartscreen.bat
- **Purpose:** Disables Windows SmartScreen by modifying file permissions
- **Key Commands:**
  - `takeown /f "%systemroot%\System32\smartscreen.exe" /a`
  - `icacls %systemroot%\System32\smartscreen.exe" /inheritance:r /remove *S-1-5-32-544 *S-1-5-11 *S-1-5-32-545 *S-1-5-18`
  - `taskkill /im smartscreen.exe /f`
- **Risk Level:** DANGEROUS
- **Notes:** Completely disables malware protection; significantly reduces system security

### 11 - Regedit FPS\01 - Disable Full Screen Opt.reg
- **Purpose:** Disables Game DVR and fullscreen optimizations
- **Registry Keys:**
  - `HKCU\Software\Microsoft\GameBar\AllowAutoGameMode` = 0
  - `HKCU\System\GameConfigStore\GameDVR_Enabled` = 0
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR\AllowGameDVR` = 0
- **Risk Level:** SAFE
- **Notes:** Safe for gaming; can slightly improve performance

### 11 - Regedit FPS\02 - CPU Optimization.reg
- **Purpose:** Disables system responsiveness and network throttling
- **Registry Keys:**
  - `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\NetworkThrottlingIndex` = 0xFFFFFFFF
  - `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\SystemResponsiveness` = 0
- **Risk Level:** MODERATE
- **Notes:** Prioritizes multimedia over system responsiveness; may make UI feel sluggish

### 11 - Regedit FPS\04 - Disable Defender.reg
- **Purpose:** Disables Windows Defender real-time protection
- **Registry Keys:**
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\DisableAntiSpyware` = 1
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection\DisableBehaviorMonitoring` = 1
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection\DisableOnAccessProtection` = 1
  - `HKLM\SOFTWARE\Policies\Microsoft\Windows Defender\Real-Time Protection\DisableScanOnRealtimeEnable` = 1
- **Risk Level:** DANGEROUS
- **Notes:** Completely disables antivirus protection; Microsoft may override these settings

### 11 - Regedit FPS\06 - Disable MMCSS.reg
- **Purpose:** Disables Multimedia Class Scheduler Service
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Services\MMCSS\Start` = 4 (disabled)
- **Risk Level:** MODERATE
- **Notes:** Can break audio/video streaming; questionable gaming benefit

### 11 - Regedit FPS\07 - Memory Optimization.reg
- **Purpose:** Aggressive memory management tweaks
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\LargeSystemCache` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\DisablePagingExecutive` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\IoPageLockLimit` = 0x00100000
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Executive\AdditionalCriticalWorkerThreads` = 32
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Executive\AdditionalDelayedWorkerThreads` = 32
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride` = 3 (spectre/meltdown disabled)
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverrideMask` = 3
- **Risk Level:** MODERATE
- **Notes:** Forces more aggressive caching; disables security mitigations; values are arbitrary

### 14 - QuickBooster\01 - QuickBoost.bat
- **Purpose:** Downloads and executes remote script from internet
- **Key Commands:**
  - `powershell -c "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/SanGraphic/QuickBoost/main/Script.bat' -OutFile QuickBoostScript.bat`
  - `move /y QuickBoostScript.bat C:\Windows`
  - `call C:\Windows\QuickBoostScript.bat`
- **Risk Level:** DANGEROUS
- **Notes:** Downloads arbitrary code from internet without verification; executes as Administrator

### 16 - BAT Tweaks FPS\02 - DWMdisablerBYdreamjow.bat
- **Purpose:** Disables Desktop Window Manager by replacing system files
- **Key Commands:**
  - Takes ownership of system files (dwm.exe, UIAnimation.dll, etc.)
  - Renames and deletes critical Windows UI components
  - Replaces dwm.exe with rundll32.exe
- **Risk Level:** DANGEROUS
- **Notes:** Breaks Windows UI; can prevent system from booting; extremely dangerous

### 16 - BAT Tweaks FPS\04 - Memory Tweaks.bat
- **Purpose:** Applies numerous memory and filesystem registry tweaks
- **Registry Keys:**
  - `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\ContigFileAllocSize` = 1536
  - `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\DontVerifyRandomDrivers` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisableEncryption` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisable8dot3NameCreation` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\DisablePagingExecutive` = 1
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\LargeSystemCache` = 0
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\SystemPages` = 0xFFFFFFFF
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\EnablePrefetcher` = 0
  - `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\EnableSuperfetch` = 0
  - `HKLM\SYSTEM\CurrentControlSet\Control\svchost\SplitThresholdInKB` (calculated)
- **Risk Level:** MODERATE
- **Notes:** Disables driver verification, encryption, and prefetch; contradictory LargeSystemCache settings

### 18 - Powershell\01 - Services Disable.txt
- **Purpose:** Disables 200+ Windows services via registry
- **Services Modified:**
  - Disables diagnostic services, update services, telemetry, search, Xbox services
  - Sets many services to disabled (4), manual (3), or automatic (2)
  - Notable services disabled: BITS, DiagTrack, WSearch, Xbox services, Print Spooler
- **Risk Level:** MODERATE to HIGH
- **Notes:** Overly aggressive; breaks Windows Update, printing, search functionality

### 20 - AMD Tweaks\01.reg
- **Purpose:** AMD GPU driver optimizations
- **Registry Keys:**
  - `HKLM\SYSTEM\ControlSet001\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}\0000\DisableSAMUPowerGating` = 1
  - `DisableUVDPowerGatingDynamic` = 1
  - `DisableVCEPowerGating` = 1
  - `KMD_DeLagEnabled` = 1
  - `EnableUlps` = 0 (Ultra Low Power State)
- **Risk Level:** MODERATE
- **Notes:** Disables power saving features; increases power consumption and heat

### 20 - AMD Tweaks\02.reg
- **Purpose:** Additional AMD GPU driver modifications
- **Registry Keys:**
  - `DisableDrmdmaPowerGating` = 1
  - `DisableeRecord` = 1
  - `KMD_SDIEnable` = 0
  - `KMD_GameManagerSupport` = 0
  - `DalDisableHDCP` = 1 (disables HDMI copy protection)
  - `DalForceMaxDisplayClock` = 1
  - `KMD_EnableGDIAcceleration` = 1
  - `PP_ThermalAutoThrottlingEnable` = 0
- **Risk Level:** MODERATE
- **Notes:** Disables HDCP (breaks protected content); disables thermal throttling (can cause overheating)

### 13 - Tweakcentral.net\Learix FPS.bat
- **Purpose:** Interactive menu-driven optimizer with multiple functions
- **Key Features:**
  - Menu system with colored text
  - Clean temp files
  - Registry tweaks (power, multimedia, filesystem)
  - Service priority manipulation
  - Appx package removal
  - BCDEdit modifications
- **Key Commands:**
  - `bcdedit /set useplatformclock false`
  - `bcdedit /set IncreaseUserVA 0`
  - Deletes temp files and folders
  - Modifies registry keys for power, CPU, memory
  - Removes Windows Store apps
  - Sets svchost.exe to realtime priority
- **Risk Level:** MODERATE to DANGEROUS
- **Notes:** Sets svchost to realtime (can cause system freeze); dangerous cleaner operations; BCDEdit changes require reboot

## Tweak Categories

### Registry Modifications
1. **Power Management:**
   - Disable power throttling
   - Processor power management (min/max state = 0%)
   - Disable hibernation
   - Disable fast startup

2. **Memory Management:**
   - Disable memory compression
   - Disable SuperFetch/Prefetch
   - Disable paging executive
   - Modify I/O page lock limits
   - Large system cache modifications

3. **Multimedia System:**
   - Disable Game DVR
   - Modify SystemResponsiveness = 0
   - Disable MMCSS
   - GPU Priority = 8
   - SFIO Priority = High

4. **Filesystem:**
   - Disable NTFS last access updates
   - Disable NTFS 8.3 name creation
   - ContigFileAllocSize = 1536
   - Disable driver verification

5. **CPU Mitigations:**
   - Disable speculative execution mitigations (FeatureSettingsOverride = 3)

6. **Network:**
   - Disable Nagle's algorithm (TCPNoDelay = 1)
   - Winsock reset

### Services Disabled
- Windows Update related (wuauserv, UsoSvc, WaaSMedicSvc)
- Telemetry (DiagTrack, dmwappushservice)
- Windows Search (WSearch)
- Xbox services
- Print Spooler
- Windows Defender (Mpssvc - via registry)
- SuperFetch (SysMain)
- Diagnostic services

### BCDEdit Changes
- `bcdedit /set useplatformclock false`
- `bcdedit /set IncreaseUserVA 0`

### GPU-Specific
- **AMD:** Power gating disabled, thermal throttling disabled, HDCP disabled, max display clock forced
- **NVIDIA:** Referenced but files not present in this repo

## Dangerous Commands

### CRITICAL SECURITY RISKS

1. **Disable Speculative Execution Mitigations** (01 - Regedit\05)
   - Disables CPU security patches for Spectre/Meltdown
   - **Impact:** System vulnerable to hardware exploits
   - **Performance gain:** <1% in most games

2. **Disable Windows Defender** (11 - Regedit FPS\04, 15 - Disable Defender)
   - Completely disables antivirus
   - **Impact:** No real-time malware protection
   - **Recommendation:** Use third-party AV if disabled

3. **Disable SmartScreen** (07 - Disable SmartGreen)
   - Removes app reputation checks
   - **Impact:** Increased risk from downloaded malware

4. **Download and Execute Remote Script** (14 - QuickBooster\01)
   - Downloads arbitrary bat file from GitHub
   - **Impact:** Code execution attack vector
   - **Recommendation:** NEVER use

### SYSTEM STABILITY RISKS

5. **Replace DWM with Rundll32** (16 - BAT Tweaks FPS\02)
   - Deletes and replaces critical Windows UI component
   - **Impact:** Breaks Windows interface; may prevent boot
   - **Recommendation:** NEVER use

6. **Disable MMCSS Service** (11 - Regedit FPS\06)
   - `MMCSS\Start = 4` (disabled)
   - **Impact:** Breaks audio/video streaming
   - **Gaming benefit:** Minimal to none

7. **Set svchost.exe to Realtime Priority** (Learix FPS.bat)
   - `wmic process where name="svchost.exe" CALL setpriority "realtime"`
   - **Impact:** Can freeze system; causes kernel priority inversion
   - **Recommendation:** EXTREMELY dangerous

8. **Disable Thermal Throttling** (20 - AMD Tweaks\02)
   - `PP_ThermalAutoThrottlingEnable = 0`
   - **Impact:** GPU may overheat; reduces hardware lifespan
   - **Recommendation:** Use custom fan curve instead

9. **Disable Driver Verification** (16 - BAT Tweaks FPS\04)
   - `DontVerifyRandomDrivers = 1`
   - **Impact:** Allows unsigned drivers; security risk
   - **Gaming benefit:** None for signed drivers

### DATA LOSS RISKS

10. **Aggressive Temp File Cleaning** (Learix FPS.bat)
    - Deletes entire temp folders: `del /s /f /q c:\windows\temp\*.*`
    - **Impact:** May delete in-use files; breaks running applications
    - **Recommendation:** Use Windows Disk Cleanup instead

## Outdated/Placebo Tweaks

### Debunked or Ineffective

1. **NetworkThrottlingIndex = 0xFFFFFFFF**
   - Myth: "Throttles network for games"
   - Reality: Affects multimedia streaming, not gaming
   - **Verdict:** Placebo

2. **SystemResponsiveness = 0**
   - Myth: "Improves gaming responsiveness"
   - Reality: Makes UI sluggish; no FPS gain
   - **Verdict:** Net negative

3. **DisablePagingExecutive = 1**
   - Myth: "Keeps kernel in memory for speed"
   - Reality: Windows 10 already does this efficiently
   - **Verdict:** Placebo on modern systems

4. **LargeSystemCache = 1**
   - Myth: "Improves caching"
   - Reality: Can reduce available RAM; contradictory settings (07 sets to 1, 04 sets to 0)
   - **Verdict:** Inconsistent implementation

5. **Disable SuperFetch/Prefetch**
   - Myth: "Frees up RAM"
   - Reality: SuperFetch is smart; disabling hurts app launch times
   - **Verdict:** Harmful on systems with >8GB RAM

6. **SecondLevelDataCache = CPU L2 Cache Size**
   - Myth: "Manually setting cache improves performance"
   - Reality:** Windows detects this automatically; manual setting ignored
   - **Verdict:** Placebo

7. **ClearPageFileAtShutdown = 0**
   - Myth: "Slows shutdown"
   - Reality:** Default is already 0; pointless change
   - **Verdict:** Placebo

8. **NtfsDisable8dot3NameCreation = 1**
   - Myth: "Improves filesystem performance"
   - Reality:** Breaks legacy apps; negligible performance gain
   - **Verdict:** Outdated tweak

9. **Mouse Acceleration Tweaks**
   - Subjective preference, not performance
   - **Verdict:** User choice, not optimization

10. **VsyncIdleTimeout = 0**
    - May cause tearing; games handle vsync internally
    - **Verdict:** Questionable benefit

### Contradictory Settings
- `LargeSystemCache` set to both 0 and 1 in different scripts
- `svchost` priority set to both realtime and low

## Good Practices

### Positive Aspects

1. **Modular Structure**
   - Users can choose which optimizations to apply
   - Numbered folders help with organization

2. **Comments in Registry Files**
   - Some registry files include explanatory comments
   - Links to documentation provided in some cases

3. **Safety Warnings in README**
   - Warns about Windows Store deletion
   - Mentions Xbox incompatibility
   - States scripts should be studied before use

4. **No Auto-Run Main Script**
   - Doesn't automatically apply everything
   - Requires user to navigate folders

5. **Credit Given**
   - README credits original authors
   - Links to external resources provided

### However, Major Issues Remain
- No undo functionality
- No safety checks before applying dangerous tweaks
- No explanation of risks
- Conflicting tweaks between scripts
- Downloads code from internet without verification

## Overall Assessment

### Engineering Quality: 3/10
- **Pros:** Modular organization, some comments, clear folder structure
- **Cons:** Contradictory settings, arbitrary values, no testing methodology, copies code from internet without verification, no error handling

### Safety Focus: 2/10
- **Pros:** Some warnings in README, modular approach lets users choose
- **Cons:** Multiple critical security vulnerabilities, system-breaking modifications, no safety checks, disables all security features, downloads remote code, sets critical processes to realtime priority

### Documentation Quality: 4/10
- **Pros:** README explains each folder, some registry comments, credits sources
- **Cons:** No technical explanations, no risk assessments, no installation/uninstall guides, missing documentation for many scripts, no explanation of what tweaks actually do

### Real-World Effectiveness: 4/10
- **Effective tweaks:** Game DVR disable (1-3% gain), power settings (variable), some service disabling
- **Placebo tweaks:** Network throttling, memory caching, most filesystem tweaks
- **Dangerous tweaks with minimal benefit:** CPU mitigations (0-1% gain), thermal throttling disable, SmartScreen disable
- **Expected FPS gain:** 0-5% in reality, not the claimed "+200 FPS"

### Recommendation: AVOID

**Summary:**
This repository represents the "shotgun approach" to Windows optimization - throw every tweak at the wall and see what sticks. While some tweaks are legitimate (Game DVR disable, power settings), the collection includes numerous dangerous, contradictory, and placebo modifications.

**Critical Issues:**
1. Downloads and executes code from internet without verification
2. Disables all Windows security features
3. Includes system-breaking file modifications
4. Sets svchost.exe to realtime priority (can freeze system)
5. Disables CPU security mitigations for minimal gain
6. No undo functionality or safety mechanisms

**Who Should Use This:**
- **No one** - The risks far outweigh any minimal performance benefits
- Especially dangerous for inexperienced users who may not understand what each script does

**Better Alternatives:**
1. **For general optimization:** Use built-in Windows Game Mode, disable Game DVR manually
2. **For advanced users:** Manually apply specific tweaks after researching them
3. **For bloatware removal:** Use O&O ShutUp10 or W10Privacy (with proper backups)
4. **For GPU optimization:** Use GPU vendor software (AMD Adrenalin, NVIDIA GeForce Experience)

**Final Verdict:**
This repository is a prime example of why "optimizer scripts" have a bad reputation. It mixes a few good tweaks with many dangerous ones, provides no safety net, and makes absurd performance claims. The combination of disabling security features, downloading remote code, and modifying critical system files makes this suitable only for virtual machine testing, never on a production system.

**Use Case Scenarios:**
- **Production System:** NEVER use
- **Gaming PC:** Use individual safe tweaks only (Game DVR disable, power settings)
- **Test VM:** Only if you want to analyze what breaks
- **Learning:** Good example of what NOT to do

The repository would benefit from:
1. Removing all dangerous scripts
2. Adding undo/restore functionality
3. Documenting each tweak with sources and benchmarks
4. Removing contradictory settings
5. Safety checks before applying changes
6. Removing remote code download
7. Honest performance expectations

As it stands, this repository does more harm than good.

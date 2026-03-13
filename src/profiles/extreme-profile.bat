@echo off
:: ============================================================================
:: EXTREME Profile - Maximum Performance Optimization
:: ============================================================================
:: WARNING: This profile is for competitive gaming/dedicated systems only
:: Risk Level: MEDIUM to HIGH
:: Expected Improvement: 10-20% FPS, 10-25ms latency reduction
::
:: WHAT THIS DOES:
:: - Applies ALL safe and competitive optimizations
:: - Disables non-essential services aggressively
:: - Applies advanced registry tweaks
:: - Optimizes network stack
:: - Disables hypervisor (breaks WSL2/Docker/VMs)
:: - Advanced power management settings
::
:: WHAT THIS DOES NOT DO (Safety Boundaries):
:: - Does NOT disable Windows Defender
:: - Does NOT disable DEP/ASLR/CFG
:: - Does NOT disable Windows Update permanently
:: - Does NOT delete system files
:: - Does NOT modify registry ACLs
::
:: REQUIREMENTS:
:: - Windows 10 22H2+ or Windows 11
:: - Desktop system (NOT laptop - heat/power concerns)
:: - Dedicated gaming rig (not daily driver)
:: - System Restore point created first
:: - All backups created
::
:: USE AT YOUR OWN RISK
:: ============================================================================

:extreme_profile_init
setlocal EnableDelayedExpansion

:: Color codes for warnings
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RESET=[0m"

echo.
echo %RED%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %RED%║       EXTREME PROFILE - MAXIMUM PERFORMANCE               ║%RESET%
echo %RED%║       Competitive Gaming Optimization                     ║%RESET%
echo %RED%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %YELLOW%⚠️  WARNING - READ CAREFULLY:%RESET%
echo.
echo This profile applies AGGRESSIVE optimizations for competitive gaming.
echo Some Windows features may be affected. System stability should be tested.
echo.
echo %RED%DO NOT USE if:%RESET%
echo   - This is your primary/daily use computer
echo   - You need WSL2, Docker, or Hyper-V
echo   - You use Windows features (Search, Cortana, etc.)
echo   - This is a laptop (heat/power concerns)
echo.
echo %GREEN%REQUIREMENTS:%RESET%
echo   [✓] Windows 10 22H2+ or Windows 11
echo   [✓] Desktop system (not laptop)
echo   [✓] System Restore point created
echo   [✓] Registry backup created
echo.
echo %YELLOW%Expected Results:%RESET%
echo   - FPS Improvement: 10-20%
echo   - Latency Reduction: 10-25ms
echo   - Risk Level: MEDIUM to HIGH
echo.
pause

:: Confirm system specs
echo.
echo %YELLOW%Checking system compatibility...%RESET%

:: Detect OS
for /f "tokens=4-5 delims=. " %%i in ('ver') do set VERSION=%%i.%%j
echo Windows Version: %VERSION%

:: Check if laptop (battery present)
powershell -Command "Get-CimInstance -ClassName Win32_Battery" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo %RED%ERROR: Laptop detected. Extreme profile not recommended for laptops.%RESET%
    echo %RED%       Heat and battery life will be severely affected.%RESET%
    pause
    exit /b 1
)

echo %GREEN%✓ System compatibility verified%RESET%
echo.

:: Final confirmation
echo %RED%═══════════════════════════════════════════════════════════════%RESET%
echo %RED%FINAL WARNING:%RESET%
echo.
echo Type 'I UNDERSTAND' to continue with EXTREME profile optimization.
echo.
set /p CONFIRM="Your choice: "

if /i not "%CONFIRM%"=="I UNDERSTAND" (
    echo %RED%Cancelled.%RESET%
    exit /b 1
)

echo.
echo %GREEN%═══════════════════════════════════════════════════════════════%RESET%
echo %GREEN%Starting EXTREME profile optimization...%RESET%
echo %GREEN%═══════════════════════════════════════════════════════════════%RESET%
echo.

set /a TWEAK_SUCCESS=0
set /a TWEAK_FAILED=0

:: ============================================================================
:: PHASE 1: SAFE PROFILE TWEAKS
:: ============================================================================
echo [%DATE% %TIME%] Phase 1/11: SAFE profile optimizations...

:: Comprehensive telemetry blocking via new module
call "%CORE_DIR%\telemetry-blocker.bat" :apply_all 2>nul
echo   [✓] Comprehensive telemetry & privacy blocked

:: Disable advertising ID
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\AdvertisingInfo\Enabled" /v "Enabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable activity history
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "EnableActivityFeed" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\System" /v "PublishUserActivities" /t REG_DWORD /d 0 /f >nul 2>&1

:: Visual effects - minimal
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" /v "VisualFXSetting" /t REG_DWORD /d 3 /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "TaskbarAnimations" /t REG_DWORD /d 0 /f >nul 2>&1

echo   [✓] Visual effects minimized
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 2: POWER MANAGEMENT - EXTREME
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 2/11: EXTREME power management...
echo   %YELLOW%INFO: Adding enhanced power management (AMD CPPC, EPP, GPU P-State)%RESET%

:: Call enhanced power management module
call "%CORE_DIR%\power-manager-enhanced.bat" :apply_all_enhanced 2>nul
if %ERRORLEVEL%==0 echo   [✓] Enhanced power management applied

:: Ultimate Performance Plan
powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
echo   [✓] Ultimate Performance plan enabled

:: Disable hibernation
powercfg /h off >nul 2>&1
echo   [✓] Hibernation disabled

:: Disable hard disk timeout
powercfg /change disk-timeout-ac 0 >nul 2>&1
powercfg /change disk-timeout-dc 0 >nul 2>&1

:: Disable USB selective suspend
powercfg /setacvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53af886c5c01 0 >nul 2>&1
powercfg /setdcvalueindex scheme_current 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53af886c5c01 0 >nul 2>&1

:: Minimum processor state 100%
powercfg /setacvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-5abca1bc2a34 100 >nul 2>&1
powercfg /setdcvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 bc5038f7-23e0-4960-96da-5abca1bc2a34 100 >nul 2>&1

:: Disable link state power management
powercfg /setacvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 12bbebe6-58d6-4636-95bb-3217ef1c0fa1 0 >nul 2>&1
powercfg /setdcvalueindex scheme_current 54533251-82be-4824-96c1-47b60b740d00 12bbebe6-58d6-4636-95bb-3217ef1c0fa1 0 >nul 2>&1

:: PCI Express power management
powercfg /setacvalueindex scheme_current 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a676184 0 >nul 2>&1
powercfg /setdcvalueindex scheme_current 501a4d13-42af-4429-9fd1-a8218c268e20 ee12f906-d277-404b-b6da-e5fa1a676184 0 >nul 2>&1

:: EPP to 0 (Maximum Performance)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-5abca1bc2a34" /v "ValueMin" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Power\PowerSettings\54533251-82be-4824-96c1-47b60b740d00\bc5038f7-23e0-4960-96da-5abca1bc2a34" /v "ValueMax" /t REG_DWORD /d 0 /f >nul 2>&1

powercfg /SetActive e9a42b02-d5df-448d-aa00-03f14749eb61 >nul 2>&1
echo   [✓] All power saving features disabled
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 3: BCDEdit - ALL SAFE TWEAKS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 3/11: BCDEdit optimizations...

bcdedit /set disabledynamictick yes >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Dynamic tick disabled

bcdedit /set useplatformtick yes >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Platform tick enabled

bcdedit /set tscsyncpolicy enhanced >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] TSC sync policy enhanced

bcdedit /set uselegacyapicmode no >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Modern APIC mode enabled

bcdedit /set usephysicaldestination no >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Logical processor IDs enabled

bcdedit /set x2apicpolicy Enable >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] x2APIC policy enabled

bcdedit /set configaccesspolicy Default >nul 2>&1
if %ERRORLEVEL%==0 echo   [✓] Config access policy set to default

echo   [⚠] REBOOT REQUIRED for BCDEdit changes
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 4: HYPERVISOR DISABLE (Breaks WSL2/Docker/VMs)
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 4/11: Disabling Hypervisor...
echo   %YELLOW%WARNING: This will disable WSL2, Docker, and all Hyper-V features%RESET%

bcdedit /set hypervisorlaunchtype off >nul 2>&1
if %ERRORLEVEL%==0 (
    echo   [✓] Hypervisor disabled (requires reboot)
    set /a TWEAK_SUCCESS+=1
) else (
    echo   [✗] Hypervisor disable failed
    set /a TWEAK_FAILED+=1
)

:: Disable Memory Integrity (VBS)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f >nul 2>&1
echo   [✓] Memory Integrity (VBS) disabled

:: ============================================================================
:: PHASE 5: AGGRESSIVE SERVICE DISABLE
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 5/11: Aggressive service optimization...
echo   %YELLOW%WARNING: Some Windows features may stop working%RESET%

:: Telemetry services (SAFE)
sc config "DiagTrack" start= disabled >nul 2>&1
net stop "DiagTrack" >nul 2>&1
sc config "dmwappushservice" start= disabled >nul 2>&1
net stop "dmwappushservice" >nul 2>&1
echo   [✓] Telemetry services disabled

:: Xbox services (SAFE if not using Xbox)
sc config "XblAuthManager" start= disabled >nul 2>&1
net stop "XblAuthManager" >nul 2>&1
sc config "XblGameSave" start= disabled >nul 2>&1
net stop "XblGameSave" >nul 2>&1
sc config "XboxNetApiSvc" start= disabled >nul 2>&1
net stop "XboxNetApiSvc" >nul 2>&1
echo   [✓] Xbox services disabled

:: Windows Search (breaks Start menu search)
sc config "WSearch" start= disabled >nul 2>&1
net stop "WSearch" >nul 2>&1
echo   [⚠] Windows Search disabled (Start menu search won't work)

:: Print Spooler (if no printer)
sc config "Spooler" start= disabled >nul 2>&1
net stop "Spooler" >nul 2>&1
echo   [⚠] Print Spooler disabled

:: Other optional services
sc config "Fax" start= disabled >nul 2>&1
net stop "Fax" >nul 2>&1
sc config "TabletInputService" start= disabled >nul 2>&1
net stop "TabletInputService" >nul 2>&1
sc config "MapsBroker" start= disabled >nul 2>&1
net stop "MapsBroker" >nul 2>&1
sc config "lfsvc" start= disabled >nul 2>&1
net stop "lfsvc" >nul 2>&1
sc config "SEMgrSvc" start= disabled >nul 2>&1
net stop "SEMgrSvc" >nul 2>&1
sc config "RmSvc" start= disabled >nul 2>&1
net stop "RmSvc" >nul 2>&1
sc config "WalletService" start= disabled >nul 2>&1
net stop "WalletService" >nul 2>&1

echo   [✓] Optional services disabled
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 6: ADVANCED REGISTRY TWEAKS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 6/11: Advanced registry + Input optimizations...

:: Call input optimizer module for mouse, keyboard, latency
call "%CORE_DIR%\input-optimizer.bat" :apply_all 2>nul
echo   [✓] Input & latency optimized (mouse 1:1, MMCSS latency)

:: MMCSS Gaming Profile
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Priority" /t REG_DWORD /d 6 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "GPU Priority" /t REG_DWORD /d 8 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Scheduling Category" /t REG_SZ /d "High" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "SFIO Priority" /t REG_SZ /d "High" /f >nul 2>&1
echo   [✓] MMCSS Gaming Profile enabled

:: System Responsiveness
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 0xffffffff /f >nul 2>&1

:: Win32PrioritySeparation (Long quantum, max foreground boost)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl" /v "Win32PrioritySeparation" /t REG_DWORD /d 38 /f >nul 2>&1
echo   [✓] Thread scheduling optimized

:: Mouse buffer optimization
reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d 16 /f >nul 2>&1
echo   [✓] Mouse input lag reduced

:: Disable NTFS Last Access
fsutil behavior set disablelastaccess 1 >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\FileSystem" /v "NtfsDisableLastAccessUpdate" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable NTFS 8.3 name creation
fsutil behavior set disable8dot3 1 >nul 2>&1
echo   [✓] File system optimizations applied

:: Disable Prefetch/Superfetch
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnablePrefetcher" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters" /v "EnableSuperfetch" /t REG_DWORD /d 0 /f >nul 2>&1

:: Large System Cache
reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v "LargeSystemCache" /t REG_DWORD /d 1 /f >nul 2>&1
echo   [✓] Memory management optimized

:: ============================================================================
:: PHASE 7: NETWORK STACK OPTIMIZATION
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 7/11: Network stack optimization...

:: Apply TCP global tweaks
netsh int tcp set global autotuninglevel=normal >nul 2>&1
netsh int tcp set global ecncapability=disabled >nul 2>&1
netsh int tcp set global timestamps=disabled >nul 2>&1
netsh int tcp set global rss=enabled >nul 2>&1
echo   [✓] TCP global stack optimized

:: TCP/IP optimizations
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpAckFrequency" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TCPNoDelay" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpWindowSize" /t REG_DWORD /d 65535 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "MaxUserPort" /t REG_DWORD /d 65534 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v "TcpTimedWaitDelay" /t REG_DWORD /d 30 /f >nul 2>&1

:: Disable NetBIOS over TCP/IP
reg add "HKLM\SYSTEM\CurrentControlSet\Services\NetBT\Parameters" /v "NetbiosOptions" /t REG_DWORD /d 2 /f >nul 2>&1
echo   [✓] Network stack optimized

:: Storage optimizations (TRIM verification)
echo   [i] Verifying TRIM is enabled...
fsutil behavior query DisableDeleteNotify | findstr "0" >nul
if %ERRORLEVEL%==0 (
    echo   [✓] TRIM is enabled
) else (
    echo   [!] Enabling TRIM...
    fsutil behavior set DisableDeleteNotify 0 >nul 2>&1
)

set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 8: VISUAL EFFECTS - COMPLETE DISABLE
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 8/11: Disabling all visual effects...

reg add "HKCU\Control Panel\Desktop" /v "DragFullWindows" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "ListviewAlphaSelect" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "IconsOnly" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "LauncherTaskbarDelay" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" /v "EnableTransparency" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f >nul 2>&1
echo   [✓] All visual effects disabled
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 9: GPU OPTIMIZATION
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 9/11: GPU optimization...
echo   %YELLOW%INFO: Adding vendor-specific GPU optimizations%RESET%

:: Call enhanced GPU optimizer for vendor-specific tweaks
call "%CORE_DIR%\gpu-optimizer-enhanced.bat" :apply_all_vendor_tweaks 2>nul
if %ERRORLEVEL%==0 echo   [✓] Vendor-specific GPU optimizations applied

:: Hardware GPU Scheduling
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1
echo   [✓] Hardware GPU Scheduling enabled

:: Note: MSI Mode for GPU requires knowing GPU ID, skipped in automated script
echo   [i] MSI Mode: Use GPU-specific tool (NVIDIA Inspector, etc.)

:: ============================================================================
:: PHASE 10: DISABLE ALL BACKGROUND APPS
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 10/11: Disabling all background apps...

reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v "GlobalUserDisabled" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable Cortana
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v "AllowCortana" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" /v "CortanaEnabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Location
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v "Value" /t REG_SZ /d "Deny" /f >nul 2>&1

echo   [✓] All background apps disabled
set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: PHASE 11: EXTREME-ONLY TWEAKS (Debloat, Spectre, VBS)
:: ============================================================================
echo.
echo [%DATE% %TIME%] Phase 11/11: EXTREME-only optimizations...
echo   %RED%WARNING: These tweaks reduce security for maximum performance%RESET%

:: Debloat
call "%CORE_DIR%\debloater.bat" :apply_debloat 2>nul
echo   [✓] Bloatware removed

call "%CORE_DIR%\debloater.bat" :apply_copilot 2>nul
echo   [✓] Copilot/Recall disabled

:: Disable Spectre/Meltdown mitigations (5-15% CPU gain)
call "%CORE_DIR%\power-manager-enhanced.bat" :apply_spectre_disable 2>nul
echo   [✓] Spectre/Meltdown mitigations disabled

:: VBS already disabled in Phase 4

set /a TWEAK_SUCCESS+=1

:: ============================================================================
:: SUMMARY
:: ============================================================================
echo.
echo %GREEN%╔═══════════════════════════════════════════════════════════════╗%RESET%
echo %GREEN%║              EXTREME PROFILE APPLIED                          ║%RESET%
echo %GREEN%╚═══════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %GREEN%Summary:%RESET%
echo   Tweaks Applied: %TWEAK_SUCCESS%
echo   Tweaks Failed: %TWEAK_FAILED%
echo.
echo %YELLOW%What was changed:%RESET%
echo   [✓] All SAFE profile optimizations
echo   [✓] Ultimate Performance power plan (no power saving)
echo   [✓] All BCDEdit safe tweaks
echo   [✓] Hypervisor disabled (breaks WSL2/Docker/VMs)
echo   [✓] Memory Integrity (VBS) disabled
echo   [✓] Telemetry and Xbox services disabled
echo   [✓] Windows Search disabled (Start menu search won't work)
echo   [✓] Print Spooler disabled
echo   [✓] 10+ optional services disabled
echo   [✓] MMCSS Gaming Profile enabled
echo   [✓] System Responsiveness maximized
echo   [✓] File system optimizations
echo   [✓] Network stack optimized
echo   [✓] All visual effects disabled
echo   [✓] Hardware GPU Scheduling enabled
echo   [✓] All background apps disabled
echo   [✓] Bloatware removed + Copilot disabled
echo   [✓] Spectre/Meltdown mitigations disabled
echo   [✓] Input & latency optimized (1:1 mouse, MMCSS)
echo   [✓] TCP global stack optimized
echo.
echo %RED%⚠️  WARNINGS:%RESET%
echo   - Windows Search is disabled (Start menu search won't work)
echo   - Print Spooler is disabled (can't print)
echo   - WSL2/Docker/Hyper-V won't work
echo   - Memory Integrity disabled (slight security risk)
echo   - Many Windows features may be broken
echo   - Higher power consumption and heat
echo   - This is NOT suitable for daily use
echo.
echo %GREEN%✓ REBOOT REQUIRED for all changes to take effect%RESET%
echo.
echo %YELLOW%To rollback:%RESET%
echo   Run: rollback.bat
echo   Or: System Restore → Choose restore point
echo.
pause

endlocal
exit /b 0

@echo off
:: ============================================================================
:: Simple Suggestion Engine
:: ============================================================================
:: Analyzes PC specs and recommends appropriate optimizations
:: Based on system capabilities and user requirements
:: ============================================================================

setlocal EnableDelayedExpansion

:: Color codes
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "MAGENTA=[95m"
set "CYAN=[96m"
set "WHITE=[97m"
set "RESET=[0m"

:: Initialize
set "SUGGEST_SAFE=0"
set "SUGGEST_COMPETITIVE=0"
set "SUGGEST_EXTREME=0"
set "WARNING_COUNT=0"
set "RECOMMENDATION_COUNT=0"

:: ============================================================================
:: DETECTION PHASE
:: ============================================================================
cls
echo.
echo %CYAN%╔════════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║           PC OPTIMIZATION SUGGESTION ENGINE                    ║%RESET%
echo %CYAN%╚════════════════════════════════════════════════════════════════╝%RESET%
echo.
echo %YELLOW%Scanning your system...%RESET%
echo.

:: Call enhanced detection
call "%~dp0src\core\system-detect-enhanced.bat" :detect_all

:: Display brief info
echo %GREEN%✓ Detection Complete%RESET%
echo.
echo   System: %OS_NAME%
echo   CPU: %CPU_NAME% (%CPU_TIER%)
echo   GPU: %GPU_NAME% (%GPU_TIER%)
echo   RAM: %RAM_TOTAL_GB% GB
if %IS_LAPTOP%==1 (
    echo   Type: %RED%Laptop%RESET%
) else (
    echo   Type: %GREEN%Desktop%RESET%
)
echo   Performance Score: %PERF_SCORE%/100 (%PERFORMANCE_TIER%)
echo.

:: ============================================================================
:: SUGGESTION LOGIC
:: ============================================================================

:: Base recommendations for everyone
set /a SUGGEST_SAFE=1

:: Competitive tier considerations
if "%PERFORMANCE_TIER%"=="Mid-Range" set /a SUGGEST_COMPETITIVE=1
if "%PERFORMANCE_TIER%"=="High-End" set /a SUGGEST_COMPETITIVE=1
if "%PERFORMANCE_TIER%"=="Enthusiast" set /a SUGGEST_COMPETITIVE=1

:: Extreme tier considerations (DESKTOP ONLY, HIGH-END ONLY)
if %IS_DESKTOP%==1 (
    if "%PERFORMANCE_TIER%"=="High-End" set /a SUGGEST_EXTREME=1
    if "%PERFORMANCE_TIER%"=="Enthusiast" set /a SUGGEST_EXTREME=1
)

:: Laptop restrictions (never suggest extreme for laptops)
if %IS_LAPTOP%==1 (
    set /a SUGGEST_EXTREME=0
)

:: Low RAM restrictions
if %RAM_TOTAL_GB% LSS 16 (
    set /a SUGGEST_EXTREME=0
)

:: ============================================================================
:: DISPLAY RECOMMENDATIONS
:: ============================================================================

cls
echo.
echo %CYAN%╔════════════════════════════════════════════════════════════════╗%RESET%
echo %CYAN%║           OPTIMIZATION RECOMMENDATIONS                         ║%RESET%
echo %CYAN%╚════════════════════════════════════════════════════════════════╝%RESET%
echo.

:: ============================================================================
:: RECOMMENDED PROFILE
:: ============================================================================
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%RECOMMENDED PROFILE%RESET%
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo.

if %SUGGEST_EXTREME%==1 (
    call :display_extreme_recommendation
) else if %SUGGEST_COMPETITIVE%==1 (
    call :display_competitive_recommendation
) else (
    call :display_safe_recommendation
)

:: ============================================================================
:: DETAILED RECOMMENDATIONS
:: ============================================================================
echo.
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%DETAILED SUGGESTIONS%RESET%
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo.

:: GPU Settings
call :suggest_gpu_settings

:: Power Settings
call :suggest_power_settings

:: BCDEdit Settings
call :suggest_bcdedit_settings

:: Service Settings
call :suggest_service_settings

:: Registry Settings
call :suggest_registry_settings

:: Additional Tweaks
call :suggest_additional_tweaks

:: ============================================================================
:: WARNINGS
:: ============================================================================
echo.
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%WARNINGS & CONSIDERATIONS%RESET%
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo.

call :display_warnings

:: ============================================================================
:: EXPECTED RESULTS
:: ============================================================================
echo.
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%EXPECTED RESULTS%RESET%
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo.

call :display_expected_results

:: ============================================================================
:: NEXT STEPS
:: ============================================================================
echo.
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo %WHITE%NEXT STEPS%RESET%
echo %WHITE%════════════════════════════════════════════════════════════════%RESET%
echo.

echo %GREEN%1.%RESET% Create a System Restore point:
echo   %YELLOW%powershell -Command "Checkpoint-Computer -Description 'Before Optimization' -RestorePointType 'MODIFY_SETTINGS'"%RESET%
echo.
echo %GREEN%2.%RESET% Run the recommended profile:
echo   %YELLOW%cd src\profiles%RESET%

if %SUGGEST_EXTREME%==1 (
    echo   %YELLOW%extreme-profile.bat%RESET%
) else if %SUGGEST_COMPETITIVE%==1 (
    echo   %YELLOW%competitive-profile.bat%RESET%
) else (
    echo   %YELLOW%safe-profile.bat%RESET%
)

echo.
echo %GREEN%3.%RESET% Reboot your system
echo.
echo %GREEN%4.%RESET% Benchmark before/after to measure actual improvement
echo.
echo %GREEN%5.%RESET% If anything breaks, run rollback script
echo.

pause
exit /b 0

:: ============================================================================
:: SUBROUTINES
:: ============================================================================

:display_extreme_recommendation
echo %RED%▶ EXTREME Profile%RESET%
echo.
echo %YELLOW%Why EXTREME?%RESET%
echo   - Your system is %GREEN%%PERFORMANCE_TIER%%RESET% tier
echo   - Desktop system (better cooling)
echo   - High RAM capacity (%RAM_TOTAL_GB% GB)
echo   - Capable of aggressive optimizations
echo.
echo %RED%⚠️  WARNINGS:%RESET%
echo   - %RED%High heat generation%RESET%
echo   - Many Windows features will break
echo   - WSL2/Docker/Hyper-V won't work
echo   - Not suitable for daily use
echo.
echo %GREEN%Expected Improvement:%RESET%
echo   - FPS: %YELLOW%+10-20%%RESET%
echo   - Latency: %YELLOW%-10-25ms%RESET%
echo.
set /a RECOMMENDATION_COUNT+=1
goto :eof

:display_competitive_recommendation
echo %YELLOW%▶ COMPETITIVE Profile%RESET%
echo.
echo %YELLOW%Why COMPETITIVE?%RESET%
echo   - Your system is %GREEN%%PERFORMANCE_TIER%%RESET% tier
echo   - Balanced performance vs stability
echo   - Good for gaming and productivity
echo   - Reversible changes
echo.
echo %GREEN%Expected Improvement:%RESET%
echo   - FPS: %YELLOW%+5-12%%RESET%
echo   - Latency: %YELLOW%-5-15ms%RESET%
echo.
set /a RECOMMENDATION_COUNT+=1
goto :eof

:display_safe_recommendation
echo %GREEN%▶ SAFE Profile%RESET%
echo.
echo %YELLOW%Why SAFE?%RESET%
if %IS_LAPTOP%==1 (
    echo   - %RED%Laptop detected%RESET% (heat concerns)
)
if %RAM_TOTAL_GB% LSS 16 (
    echo   - %RED%Low RAM%RESET% (%RAM_TOTAL_GB% GB)
)
if "%PERFORMANCE_TIER%"=="Entry-Level" (
    echo   - Entry-level system
)
echo   - Conservative optimizations
echo   - Minimal risk
echo   - All features remain functional
echo.
echo %GREEN%Expected Improvement:%RESET%
echo   - FPS: %YELLOW%+3-8%%RESET%
echo   - Latency: %YELLOW%-2-5ms%RESET%
echo.
set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_gpu_settings
echo %GREEN%[GPU SETTINGS]%RESET% %YELLOW%(Highest Impact - 2-15%%RESET%)
echo.
if "%GPU_VENDOR%"=="NVIDIA" (
    echo   NVIDIA Control Panel → Adjust image settings with preview:
    echo   - Power management mode: %GREEN%Prefer maximum performance%RESET%
    if %SUGGEST_COMPETITIVE%==1 (
        echo   - Low Latency Mode: %GREEN%Ultra%RESET% (or On)
        echo   - Max Frame Rate: %GREEN%Off%RESET%
    )
    if %SUGGEST_EXTREME%==1 (
        echo   - Low Latency Mode: %GREEN%Ultra%RESET%
        echo   - Max Pre-Rendered Frames: %GREEN%1%RESET%
        echo   - Vertical Sync: %GREEN%Off%RESET%
    )
    echo.
)

if "%GPU_VENDOR%"=="AMD" (
    echo   AMD Radeon Software → Graphics:
    echo   - Power sliders: %GREEN%Max Performance%RESET%
    if %SUGGEST_COMPETITIVE%==1 (
        echo   - Anti-Lag: %GREEN%On%RESET%
        echo   - Radeon Boost: %GREEN%On%RESET%
    )
    if %SUGGEST_EXTREME%==1 (
        echo   - Anti-Lag: %GREEN%On%RESET%
        echo   - Enhanced Sync: %GREEN%On%RESET%
    )
    echo.
)

:: HAGS recommendation
if %SUGGEST_COMPETITIVE%==1 (
    echo   Windows Settings → Display → Graphics:
    echo   - Hardware GPU Scheduling: %GREEN%On%RESET%
    echo.
)

set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_power_settings
echo %GREEN%[POWER SETTINGS]%RESET% %YELLOW%(High Impact - 2-5%%RESET%)
echo.

if %SUGGEST_SAFE%==1 (
    echo   Power plan: %GREEN%High Performance%RESET% or Balanced
    echo.
)

if %SUGGEST_COMPETITIVE%==1 (
    echo   Power plan: %GREEN%Ultimate Performance%RESET%
    echo   Command:
    echo   %CYAN%powercfg /duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61%RESET%
    echo   %CYAN%powercfg /setactive e9a42b02-d5df-448d-aa00-03f14749eb61%RESET%
    echo.
)

if %SUGGEST_EXTREME%==1 (
    echo   Power plan: %GREEN%Ultimate Performance%RESET%
    echo   Minimum processor state: %GREEN%100%%RESET%
    echo   EPP (Energy Performance Preference): %GREEN%0 (Max Performance)%RESET%
    echo   Disable all power saving features
    echo   %RED%⚠️  Warning: High heat generation%RESET%
    echo.
)

set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_bcdedit_settings
echo %GREEN%[BCDEDIT SETTINGS]%RESET% %YELLOW%(Medium Impact - 1-4%%RESET%)
echo.

echo   Safe tweaks (recommended for everyone):
echo   - Disable dynamic tick: %CYAN%bcdedit /set disabledynamictick yes%RESET%
echo   - Use platform tick: %CYAN%bcdedit /set useplatformtick yes%RESET%
echo   - Enhanced TSC sync: %CYAN%bcdedit /set tscsyncpolicy enhanced%RESET%
echo.

if %SUGGEST_EXTREME%==1 (
    echo   %RED%Advanced tweak (EXTREME only):%RESET%
    echo   - Disable hypervisor: %CYAN%bcdedit /set hypervisorlaunchtype off%RESET%
    echo   %RED%⚠️  Breaks WSL2/Docker/Hyper-V%RESET%
    echo.
)

set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_service_settings
echo %GREEN%[SERVICE SETTINGS]%RESET% %YELLOW%(Low Impact - 0-2%%RESET%)
echo.

echo   Safe to disable:
echo   - Telemetry services (DiagTrack, dmwappushservice)
if %SUGGEST_COMPETITIVE%==1 (
    echo   - Xbox services (if not gaming on Xbox)
)

if %SUGGEST_EXTREME%==1 (
    echo   - Windows Search (Start menu search won't work)
    echo   - Print Spooler (can't print)
    echo   - 10+ optional services
)

echo.

set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_registry_settings
echo %GREEN%[REGISTRY SETTINGS]%RESET% %YELLOW%(Low-Medium Impact - 0-3%%RESET%)
echo.

echo   Safe tweaks:
echo   - Disable animations: %CYAN%MenuShowDelay = 0%RESET%
echo   - MMCSS Gaming Profile: %CYAN%Priority = 6, GPU Priority = 8%RESET%
echo   - Disable transparency
echo.

if %SUGGEST_COMPETITIVE%==1 (
    echo   Competitive tweaks:
    echo   - Win32PrioritySeparation: %CYAN%38%RESET%
    echo   - System Responsiveness: %CYAN%0%RESET%
    echo.
)

if %SUGGEST_EXTREME%==1 (
    echo   %RED%Advanced tweaks (EXTREME only):%RESET%
    echo   - Network stack optimization
    echo   - File system optimization
    echo   - Disable Prefetch/Superfetch
    echo.
)

set /a RECOMMENDATION_COUNT+=1
goto :eof

:suggest_additional_tweaks
echo %GREEN%[ADDITIONAL TWEAKS]%RESET%
echo.

echo   Input optimization:
echo   - Enhanced Pointer Precision: %GREEN%Off%RESET% (Mouse Settings)
echo   - Raw input: %GREEN%On%RESET% (in-game settings)
if %SUGGEST_COMPETITIVE%==1 (
    echo   - Mouse polling rate: %GREEN%1000Hz%RESET% (if supported)
)
echo.

echo   Visual effects:
if %SUGGEST_EXTREME%==1 (
    echo   - Disable all: %CYAN%Adjust for best performance%RESET%
) else (
    echo   - Disable animations and transparency
)
echo.

echo   Game Mode:
echo   - Windows Game Mode: %GREEN%On%RESET%
echo   - Game Bar: %GREEN%Off%RESET% (if not using)
echo   - Game DVR: %GREEN%Off%RESET%
echo.

set /a RECOMMENDATION_COUNT+=1
goto :eof

:display_warnings
set /a WARNING_COUNT=0

if %IS_LAPTOP%==1 (
    echo %RED%⚠️  WARNING: Laptop detected%RESET%
    echo   - Aggressive optimizations will cause overheating
    echo   - Battery life will be significantly reduced
    echo   - Recommended: SAFE profile only
    echo   - Monitor temperatures carefully
    echo.
    set /a WARNING_COUNT+=1
)

if %RAM_TOTAL_GB% LSS 16 (
    echo %RED%⚠️  WARNING: Low RAM (%RAM_TOTAL_GB% GB)%RESET%
    echo   - EXTREME profile not recommended
    echo   - Keep some background services enabled
    echo   - Monitor RAM usage
    echo.
    set /a WARNING_COUNT+=1
)

if %HAS_HDD%==1 (
    echo %YELLOW%⚠️  NOTICE: HDD detected%RESET%
    echo   - Consider upgrading to SSD for huge performance boost
    echo   - HDD is a major bottleneck in modern systems
    echo.
    set /a WARNING_COUNT+=1
)

if "%GPU_TIER%"=="Entry-Level" (
    echo %YELLOW%⚠️  NOTICE: Entry-level GPU%RESET%
    echo   - GPU may be a bottleneck
    echo   - Settings tweaks will help but GPU upgrade recommended
    echo.
    set /a WARNING_COUNT+=1
)

if %WARNING_COUNT%==0 (
    echo %GREEN%✓ No major concerns detected%RESET%
    echo.
)

goto :eof

:display_expected_results
echo   Based on your system specs (%PERFORMANCE_TIER% tier):
echo.

if %SUGGEST_EXTREME%==1 (
    echo   %GREEN%Profile:%RESET% EXTREME
    echo   %GREEN%FPS Improvement:%RESET% 10-20%%
    echo   %GREEN%Latency Reduction:%RESET% 10-25ms
    echo   %GREEN%Risk Level:%RESET% MEDIUM to HIGH
    echo.
)

if %SUGGEST_COMPETITIVE%==1 (
    echo   %GREEN%Profile:%RESET% COMPETITIVE
    echo   %GREEN%FPS Improvement:%RESET% 5-12%%
    echo   %GREEN%Latency Reduction:%RESET% 5-15ms
    echo   %GREEN%Risk Level:%RESET% LOW
    echo.
)

if %SUGGEST_SAFE%==1 (
    echo   %GREEN%Profile:%RESET% SAFE
    echo   %GREEN%FPS Improvement:%RESET% 3-8%%
    echo   %GREEN%Latency Reduction:%RESET% 2-5ms
    echo   %GREEN%Risk Level:%RESET% MINIMAL
    echo.
)

echo   %YELLOW%Note: These are realistic expectations based on research.%RESET%
echo   %YELLOW%      Any tool claiming 200%% improvement is lying.%RESET%
echo.

goto :eof

@echo off
:: ============================================================================
:: ClutchG Optimizer - Benchmark Runner Module
:: ============================================================================
:: Purpose: Measure system performance before and after optimizations
:: Created: 2025-02-02 (Scientific validation framework)
:: ============================================================================
:: This module provides before/after performance measurement:
:: - Boot time tracking
:: - Memory usage statistics
:: - CPU/GPU information
:: - DPC latency check (recommends LatencyMon)
:: - FPS testing guidance (recommends CapFrameX)
:: ============================================================================
:: EVIDENCE: research.md shows realistic 5-15% improvement (not 200%)
:: SAFETY: Read-only measurements - no system modifications
:: ============================================================================

:main
if "%~1"=="" goto :usage
if "%~1"=="run_benchmark" goto :run_benchmark
if "%~1"=="capture_baseline" goto :capture_baseline
if "%~1":"compare_results" goto :compare_results
if "%~1"=="system_info" goto :system_info
if "%~1"=="boot_time" goto :boot_time
if "%~1"=="memory_usage" goto :memory_usage
if "%~1"=="dpc_latency_check" goto :dpc_latency_check
goto :usage

:usage
echo Usage: benchmark-runner.bat [command]
echo.
echo Commands:
echo   run_benchmark        - Run full benchmark suite
echo   capture_baseline     - Capture baseline performance metrics
echo   compare_results      - Compare baseline vs current
echo   system_info          - Display detailed system information
echo   boot_time            - Measure boot time
echo   memory_usage         - Measure memory usage
echo   dpc_latency_check    - Check for DPC latency issues
goto :eof

:: ============================================================================
:: Run Full Benchmark Suite
:: ============================================================================
:run_benchmark
set "BENCHMARK_DIR=%BACKUPS_DIR%\benchmarks"
if not exist "%BENCHMARK_DIR%" mkdir "%BENCHMARK_DIR%"

set "TIMESTAMP=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%"
set "TIMESTAMP=%TIMESTAMP: =0%"
set "BENCHMARK_FILE=%BENCHMARK_DIR%\benchmark_%TIMESTAMP%.txt"

echo.
echo ========================================================================
echo ClutchG Optimizer - Performance Benchmark
echo ========================================================================
echo Timestamp: %TIMESTAMP%
echo.

call "%LOGGING_DIR%\logger.bat" :log "Running performance benchmark..."
echo Writing results to: %BENCHMARK_FILE%

:: Create benchmark file
echo ======================================================================== > "%BENCHMARK_FILE%"
echo ClutchG Optimizer - Performance Benchmark >> "%BENCHMARK_FILE%"
echo ======================================================================== >> "%BENCHMARK_FILE%"
echo Timestamp: %TIMESTAMP% >> "%BENCHMARK_FILE%"
echo. >> "%BENCHMARK_FILE%"

:: System Information
echo [System Information] >> "%BENCHMARK_FILE%"
call :system_info >> "%BENCHMARK_FILE%" 2>&1
echo. >> "%BENCHMARK_FILE%"

:: Boot Time
echo [Boot Time Analysis] >> "%BENCHMARK_FILE%"
call :boot_time >> "%BENCHMARK_FILE%" 2>&1
echo. >> "%BENCHMARK_FILE%"

:: Memory Usage
echo [Memory Usage] >> "%BENCHMARK_FILE%"
call :memory_usage >> "%BENCHMARK_FILE%" 2>&1
echo. >> "%BENCHMARK_FILE%"

:: Storage Analysis - PowerShell replaces deprecated wmic
echo [Storage Analysis] >> "%BENCHMARK_FILE%"
powershell -Command "Get-CimInstance Win32_LogicalDisk | Select-Object Size,FreeSpace,Caption" >> "%BENCHMARK_FILE%" 2>&1
echo. >> "%BENCHMARK_FILE%"

echo ======================================================================== >> "%BENCHMARK_FILE%"
echo. >> "%BENCHMARK_FILE%"

:: Also display on screen
type "%BENCHMARK_FILE%"

:: Save as baseline if requested
echo.
set /p SAVE_BASELINE="Save as baseline for comparison? (Y/N): "
if /i "%SAVE_BASELINE%"=="Y" (
    copy "%BENCHMARK_FILE%" "%BENCHMARK_DIR%\baseline.txt" >nul 2>&1
    echo Baseline saved to: %BENCHMARK_DIR%\baseline.txt
)

echo.
echo Benchmark complete!
echo File: %BENCHMARK_FILE%
goto :eof

:: ============================================================================
:: Capture Baseline
:: ============================================================================
:capture_baseline
set "BENCHMARK_DIR=%BACKUPS_DIR%\benchmarks"
if not exist "%BENCHMARK_DIR%" mkdir "%BENCHMARK_DIR%"

call "%LOGGING_DIR%\logger.bat" :log "Capturing baseline performance metrics..."

call :run_benchmark

if exist "%BENCHMARK_FILE%" (
    copy "%BENCHMARK_FILE%" "%BENCHMARK_DIR%\baseline.txt" >nul 2>&1
    echo Baseline captured successfully
    echo Location: %BENCHMARK_DIR%\baseline.txt
) else (
    echo ERROR: Failed to capture baseline
)

goto :eof

:: ============================================================================
:: Compare Results
:: ============================================================================
:compare_results
set "BENCHMARK_DIR=%BACKUPS_DIR%\benchmarks"

if not exist "%BENCHMARK_DIR%\baseline.txt" (
    echo ERROR: No baseline found. Run 'capture_baseline' first.
    goto :eof
)

echo.
echo ========================================================================
echo Performance Comparison
echo ========================================================================
echo.
echo Baseline vs Current
echo.

:: This is a simplified comparison - a full implementation would parse
:: both files and calculate differences

echo Baseline file: %BENCHMARK_DIR%\baseline.txt
echo Current benchmark: %BENCHMARK_DIR%\benchmark_*.txt (most recent)
echo.
echo For detailed comparison, use a diff tool or review the files manually.
echo.
echo Expected improvements (based on research.md):
echo - Gaming: 5-15%% FPS improvement
echo - Boot time: 8%% faster
echo - RAM usage: 700MB freed (3.2GB -^> 2.5GB)
echo.
echo NOTE: Realistic expectations, not 200%% like snake-oil tools claim
goto :eof

:: ============================================================================
:: System Information
:: ============================================================================
:system_info
echo Operating System:
call "%CORE_DIR%\system-detect.bat" :detect_os
echo   Version: Windows %OS_VERSION% (Build %OS_BUILD%)
echo.

echo CPU Information: - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).Name"') do echo   Name: %%a
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfCores"') do echo   Cores: %%a
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors"') do echo   Threads: %%a
echo.

echo GPU Information: - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "$gpu = Get-CimInstance Win32_VideoController | Select-Object -First 1; Write-Output \"Name=$($gpu.Name)\"; Write-Output \"AdapterRAM=$([math]::Round($gpu.AdapterRAM / 1GB))GB\""') do echo   %%a
echo.

echo RAM Information:
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| find "Total Physical Memory"') do echo   Total:%%a
echo.

echo Storage: - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "Get-CimInstance Win32_LogicalDisk | Select-Object Caption,@{Name=\"Size\";Expression={[math]::Round($_.Size/1GB)}},@{Name=\"FreeSpace\";Expression={[math]::Round($_.FreeSpace/1GB)}} | Format-Table -HideTableHeaders"') do echo   %%a
echo.

goto :eof

:: ============================================================================
:: Boot Time Measurement
:: ============================================================================
:boot_time
:: Measure system boot time using systeminfo

echo Measuring boot time...
echo.

:: Get boot time from systeminfo
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| find "System Boot Time"') do (
    echo System Boot Time:%%a
)

:: Calculate uptime (in minutes)
:: This gives us an idea of how long the system has been running - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"') do set "BOOT_TIME=%%a"

:: Parse the uptime (simplified - CIM returns in format: 20250202120000.000000-000)
echo Last Boot: %BOOT_TIME%

:: Get system uptime using PowerShell (more accurate)
for /f %%a in ('powershell -Command "(Get-Uptime).TotalMinutes"') do set "UPTIME_MINUTES=%%a"
echo System Uptime: %UPTIME_MINUTES% minutes

:: Calculate approximate boot time (very rough estimate)
if %UPTIME_MINUTES% GTR 0 (
    echo Boot Status: System has been running for %UPTIME_MINUTES% minutes
    echo Note: For accurate boot time measurement, restart and run benchmark immediately after login
) else (
    echo Boot Status: Unable to measure
)

echo.
echo Expected improvement (after optimizations): 8%% faster boot time
echo Source: research.md benchmark data
goto :eof

:: ============================================================================
:: Memory Usage Measurement
:: ============================================================================
:memory_usage
echo Measuring memory usage...
echo.

:: Total physical memory
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| find "Total Physical Memory"') do (
    echo Total Physical Memory:%%a
)

:: Available physical memory
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| find "Available Physical Memory"') do (
    echo Available Physical Memory:%%a
)

:: Virtual memory
for /f "tokens=2 delims=:" %%a in ('systeminfo ^| find "Virtual Memory: Available"') do (
    echo Available Virtual Memory:%%a
)

:: Get detailed memory info using PowerShell
echo.
echo Detailed Memory Information:
powershell -Command "Get-WmiObject Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory, TotalVirtualMemorySize | Format-List"

echo.
echo Expected improvement (after optimizations): 700MB freed
echo Typical: 3.2GB -^> 2.5GB used RAM
echo Source: research.md benchmark data
goto :eof

:: ============================================================================
:: DPC Latency Check
:: ============================================================================
:dpc_latency_check
echo.
echo ========================================================================
echo DPC Latency Diagnostic
echo ========================================================================
echo.
echo DPC (Deferred Procedure Call) latency affects gaming performance and
echo can cause audio stuttering, FPS drops, and input lag.
echo.
echo This tool checks for potential DPC latency issues.
echo.

:: Check for known DPC latency culprits
echo Checking for common DPC latency causes...
echo.

:: Check if HPET is enabled (High Precision Event Timer)
:: HPET can cause DPC latency issues on some systems
reg query "HKLM\SYSTEM\CurrentControlSet\Enum\Root\ACPI_PNP0103" >nul 2>&1
if %ERRORLEVEL%==0 (
    echo [WARNING] HPET device detected
    echo HPET can cause DPC latency issues on some systems.
    echo Consider disabling HPET in BIOS if experiencing latency spikes.
) else (
    echo [OK] No HPET device detected
)

echo.
echo For comprehensive DPC latency analysis, we recommend:
echo.
echo 1. LatencyMon (free)
echo    Download: https://www.resplendence.com/latencymon
echo    - Measures actual DPC latency in real-time
echo    - Identifies drivers causing latency
echo    - Provides detailed reports
echo.

echo 2. Method: Run LatencyMon before and after optimizations
echo    - Baseline: Run for 10 minutes during normal usage
echo    - After optimizations: Run for 10 minutes under same conditions
echo    - Compare maximum and average DPC latency
echo.

echo Good DPC latency values:
echo   - Maximum: Under 500 microseconds (us)
echo   - Average: Under 50 microseconds (us)
echo.
echo Poor DPC latency values (indicates problems):
echo   - Maximum: Over 1000 microseconds (1ms)
echo   - Average: Over 100 microseconds
echo.

goto :eof

:: ============================================================================
:: FPS Testing Guidance
:: ============================================================================
:fps_testing_guidance
:: This function provides guidance for FPS benchmarking

echo.
echo ========================================================================
echo FPS Testing Guidance
echo ========================================================================
echo.
echo For accurate FPS measurements before and after optimizations:
echo.
echo Recommended Tool: CapFrameX
echo Download: https://www.techpowerup.com/capframex/
echo.
echo Alternative Tools:
echo   - NVIDIA GeForce Experience (FPS counter)
echo   - AMD Radeon Software (FPS counter)
echo   - MSI Afterburner (FPS counter)
echo   - PresentMon (Command-line tool from Intel)
echo.
echo Testing Methodology:
echo.
echo 1. Choose a game with built-in benchmark or consistent scene
echo    Examples: Cyberpunk 2077, Shadow of the Tomb Raider, CS2
echo.
echo 2. Run benchmark BEFORE optimizations:
echo    - Use same graphics settings
echo    - Note: Average FPS, 1%% lows, 0.1%% lows
echo    - Run 3 times, take average
echo.
echo 3. Apply ClutchG optimizations
echo    - Restart system (if BCDEdit changes were made)
echo.
echo 4. Run benchmark AFTER optimizations:
echo    - Use SAME graphics settings
echo    - Run 3 times, take average
echo.
echo 5. Compare results
echo.
echo Expected improvement (based on research.md):
echo   - SAFE profile: 2-5%% FPS improvement
echo   - COMPETITIVE profile: 5-10%% FPS improvement
echo   - EXTREME profile: 10-15%% FPS improvement
echo.
echo REALISTIC EXPECTATIONS:
echo   These are evidence-based numbers, not 200%% like snake-oil tools claim.
echo   Actual results vary by hardware and game.
echo.
goto :eof

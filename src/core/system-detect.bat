@echo off
:: ============================================
:: System Detection Module
:: Detects OS version, CPU, GPU, and system type
:: ============================================

if "%~1"==":detect_all" goto :detect_all
goto :eof

:detect_all
call :detect_os
call :detect_cpu
call :detect_gpu
call :detect_system_type
goto :eof

:detect_os
:: Get Windows version
for /f "tokens=4-5 delims=. " %%i in ('ver') do (
    set "OS_VERSION_RAW=%%i.%%j"
)

:: Get build number
for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul ^| findstr CurrentBuild') do (
    set "OS_BUILD=%%a"
)

:: Determine Windows version
if "%OS_BUILD%" geq "22000" (
    set "OS_VERSION=11"
) else (
    set "OS_VERSION=10"
)

:: Get edition
for /f "tokens=3*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v EditionID 2^>nul ^| findstr EditionID') do (
    set "OS_EDITION=%%a"
)

:: Export for use by other modules
set "OS_VERSION=%OS_VERSION%"
set "OS_BUILD=%OS_BUILD%"
set "OS_EDITION=%OS_EDITION%"

goto :eof

:detect_cpu
:: Get CPU name - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"') do (
    set "CPU_NAME=%%a"
)

:: Detect vendor
echo %CPU_NAME% | findstr /i "Intel" >nul
if %ERRORLEVEL%==0 (
    set "CPU_VENDOR=Intel"
) else (
    echo %CPU_NAME% | findstr /i "AMD" >nul
    if %ERRORLEVEL%==0 (
        set "CPU_VENDOR=AMD"
    ) else (
        set "CPU_VENDOR=Unknown"
    )
)

:: Get core count - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfCores"') do (
    set "CPU_CORES=%%a"
)

:: Get thread count - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors"') do (
    set "CPU_THREADS=%%a"
)

goto :eof

:detect_gpu
:: Get GPU name - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name"') do (
    set "GPU_NAME=%%a"
)

:: Detect vendor
echo %GPU_NAME% | findstr /i "NVIDIA GeForce Quadro" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=NVIDIA"
    goto :gpu_done
)

echo %GPU_NAME% | findstr /i "AMD Radeon" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=AMD"
    goto :gpu_done
)

echo %GPU_NAME% | findstr /i "Intel" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=Intel"
    goto :gpu_done
)

set "GPU_VENDOR=Unknown"

:gpu_done
goto :eof

:detect_system_type
:: Check for battery (laptop detection) - PowerShell replaces deprecated wmic
powershell -Command "Get-CimInstance Win32_Battery" >nul 2>&1
if %ERRORLEVEL%==0 (
    set "SYSTEM_TYPE=Laptop"
) else (
    set "SYSTEM_TYPE=Desktop"
)
goto :eof

:: ============================================
:: Utility Functions
:: ============================================

:is_win11
if "%OS_BUILD%" geq "22000" exit /b 0
exit /b 1

:is_win10_2004_plus
if "%OS_BUILD%" geq "19041" exit /b 0
exit /b 1

:check_feature
:: Check if a Windows feature is available
:: Usage: call :check_feature "FeatureName"
dism /online /get-featureinfo /featurename:%~1 >nul 2>&1
exit /b %ERRORLEVEL%

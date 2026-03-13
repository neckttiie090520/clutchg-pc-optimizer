@echo off
:: ============================================================================
:: Enhanced System Detection Module
:: ============================================================================
:: Detects all system components and provides detailed specs
:: Used by suggestion engine to recommend optimizations
:: ============================================================================

:detect_all
call :detect_os
call :detect_cpu
call :detect_gpu
call :detect_ram
call :detect_storage
call :detect_system_type
call :detect_network
call :detect_cooling
call :calculate_performance_score
goto :eof

:: ============================================================================
:: OS Detection
:: ============================================================================
:detect_os
set "OS_VERSION=Unknown"
set "OS_BUILD=0"
set "OS_NAME=Unknown"

:: Get OS version
for /f "tokens=4-5 delims=. " %%i in ('ver') do set "VERSION=%%i.%%j"

:: Check for Windows 11
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild >nul 2>&1
if %ERRORLEVEL%==0 (
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuild 2^>nul ^| findstr CurrentBuild') do set "OS_BUILD=%%b"
    for /f "tokens=2*" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v DisplayVersion 2^>nul ^| findstr DisplayVersion') do set "DISPLAY_VERSION=%%b"

    if %OS_BUILD% GEQ 22000 (
        set "OS_VERSION=11"
        set "OS_NAME=Windows 11 %DISPLAY_VERSION% (Build %OS_BUILD%)"
    ) else if %OS_BUILD% GEQ 19044 (
        set "OS_VERSION=10"
        set "OS_NAME=Windows 10 22H2 (Build %OS_BUILD%)"
    ) else (
        set "OS_VERSION=10"
        set "OS_NAME=Windows 10 (Build %OS_BUILD%)"
    )
)

:: Verify minimum requirements
if %OS_BUILD% LSS 19045 (
    set "OS_COMPATIBLE=0"
) else (
    set "OS_COMPATIBLE=1"
)

goto :eof

:: ============================================================================
:: CPU Detection
:: ============================================================================
:detect_cpu
set "CPU_VENDOR=Unknown"
set "CPU_NAME=Unknown"
set "CPU_CORES=0"
set "CPU_THREADS=0"
set "CPU_MAX_CLOCK=0"
set "CPU_ARCH=x64"

:: Get CPU info (PowerShell - replaces deprecated wmic)
for /f "tokens=*" %%a in ('powershell -Command "Get-CimInstance Win32_Processor | Select-Object -ExpandProperty Name"') do set "CPU_NAME=%%a"
set "CPU_NAME=%CPU_NAME: =%"

:: Get cores and threads (PowerShell - replaces deprecated wmic)
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfCores"') do set "CPU_CORES=%%a"
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_Processor).NumberOfLogicalProcessors"') do set "CPU_THREADS=%%a"

:: Get max clock speed (PowerShell - replaces deprecated wmic)
for /f "tokens=*" %%a in ('powershell -Command "[int](Get-CimInstance Win32_Processor).MaxClockSpeed"') do set "CPU_MAX_CLOCK=%%a"
set /a CPU_MAX_CLOCK_MHZ=%CPU_MAX_CLOCK% / 1000

:: Detect vendor
echo %CPU_NAME% | findstr /i "Intel" >nul
if %ERRORLEVEL%==0 set "CPU_VENDOR=Intel"

echo %CPU_NAME% | findstr /i "AMD" >nul
if %ERRORLEVEL%==0 set "CPU_VENDOR=AMD"

:: Detect CPU tier/performance
call :detect_cpu_tier

goto :eof

:detect_cpu_tier
:: Classify CPU by performance tier
set "CPU_TIER=Low-End"

:: Intel CPU classification
if "%CPU_VENDOR%"=="Intel" (
    echo %CPU_NAME% | findstr /i "i9" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=Enthusiast"

    echo %CPU_NAME% | findstr /i "i7" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=High-End"

    echo %CPU_NAME% | findstr /i "i5" >nul
    if %ERRORLEVEL%==0 (
        if %CPU_MAX_CLOCK_MHZ% GEQ 3000 (
            set "CPU_TIER=Mid-Range"
        ) else (
            set "CPU_TIER=Entry-Level"
        )
    )

    echo %CPU_NAME% | findstr /i "i3" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=Entry-Level"
)

:: AMD CPU classification
if "%CPU_VENDOR%"=="AMD" (
    echo %CPU_NAME% | findstr /i "Ryzen 9" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=Enthusiast"

    echo %CPU_NAME% | findstr /i "Ryzen 7" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=High-End"

    echo %CPU_NAME% | findstr /i "Ryzen 5" >nul
    if %ERRORLEVEL%==0 (
        if %CPU_MAX_CLOCK_MHZ% GEQ 3000 (
            set "CPU_TIER=Mid-Range"
        ) else (
            set "CPU_TIER=Entry-Level"
        )
    )

    echo %CPU_NAME% | findstr /i "Ryzen 3" >nul
    if %ERRORLEVEL%==0 set "CPU_TIER=Entry-Level"
)

:: Threadripper/EPYC
echo %CPU_NAME% | findstr /i "Threadripper EPYC" >nul
if %ERRORLEVEL%==0 set "CPU_TIER=Enthusiast"

goto :eof

:: ============================================================================
:: GPU Detection
:: ============================================================================
:detect_gpu
set "GPU_VENDOR=Unknown"
set "GPU_NAME=Unknown"
set "GPU_VRAM=0"
set "GPU_TIER=Entry-Level"

:: Get GPU info (first GPU) - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_VideoController | Select-Object -First 1).Name"') do set "GPU_NAME=%%a"

:gpu_found
set "GPU_NAME=%GPU_NAME: =%"

:: Detect GPU vendor
echo %GPU_NAME% | findstr /i "NVIDIA NVidia GeForce RTX GTX" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=NVIDIA"
    call :detect_nvidia_tier
)

echo %GPU_NAME% | findstr /i "AMD Radeon RX" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=AMD"
    call :detect_amd_tier
)

echo %GPU_NAME% | findstr /i "Intel Iris Arc" >nul
if %ERRORLEVEL%==0 (
    set "GPU_VENDOR=Intel"
    set "GPU_TIER=Entry-Level"
)

:: Get VRAM - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-CimInstance Win32_VideoController | Select-Object -First 1).AdapterRAM / 1GB)"') do set /a GPU_VRAM_GB=%%a

goto :eof

:detect_nvidia_tier
:: NVIDIA GPU tier classification
echo %GPU_NAME% | findstr /i "RTX 4090 4080" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Enthusiast"

echo %GPU_NAME% | findstr /i "RTX 4070 4060 3090 3080" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=High-End"

echo %GPU_NAME% | findstr /i "RTX 3070 3060 2080 2070" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Mid-Range"

echo %GPU_NAME% | findstr /i "GTX" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Entry-Level"

goto :eof

:detect_amd_tier
:: AMD GPU tier classification
echo %GPU_NAME% | findstr /i "RX 7900" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Enthusiast"

echo %GPU_NAME% | findstr /i "RX 7800 7700 7600 6900 6800 6700" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=High-End"

echo %GPU_NAME% | findstr /i "RX 6600 6500" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Mid-Range"

echo %GPU_NAME% | findstr /i "RX 550 560" >nul
if %ERRORLEVEL%==0 set "GPU_TIER=Entry-Level"

goto :eof

:: ============================================================================
:: RAM Detection
:: ============================================================================
:detect_ram
set "RAM_TOTAL_GB=0"
set "RAM_SPEED_MHZ=0"
set "RAM_TYPE=Unknown"

:: Get total RAM - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "[math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB)"') do set /a RAM_TOTAL_GB=%%a

:: Get RAM speed - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1).Speed"') do set "RAM_SPEED_MHZ=%%a"

:ram_speed_found

:: Get RAM type - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "$mem = Get-CimInstance Win32_PhysicalMemory | Select-Object -First 1; if($mem.SMBIOSMemoryType) {$mem.SMBIOSMemoryType} else {0}"') do set /a RAM_TYPE_CODE=%%a
if !RAM_TYPE_CODE!==24 set "RAM_TYPE=DDR3"
if !RAM_TYPE_CODE!==26 set "RAM_TYPE=DDR4"
if !RAM_TYPE_CODE!==34 set "RAM_TYPE=DDR5"

goto :eof

:: ============================================================================
:: Storage Detection
:: ============================================================================
:detect_storage
set "HAS_SSD=0"
set "HAS_NVME=0"
set "HAS_HDD=0"

:: Check for NVMe SSD - PowerShell replaces deprecated wmic
powershell -Command "Get-CimInstance Win32_DiskDrive | Select-Object -ExpandProperty InterfaceType" | findstr /i "NVMe" >nul
if %ERRORLEVEL%==0 (
    set "HAS_NVME=1"
    set "HAS_SSD=1"
) else (
    :: Check for SSD (using media type) - PowerShell replaces deprecated wmic
    powershell -Command "Get-CimInstance Win32_DiskDrive | Select-Object -ExpandProperty MediaType" | findstr /i "SSD" >nul
    if %ERRORLEVEL%==0 (
        set "HAS_SSD=1"
    )

    :: Check for HDD - PowerShell replaces deprecated wmic
    powershell -Command "Get-CimInstance Win32_DiskDrive | Select-Object -ExpandProperty MediaType" | findstr /i "Fixed hard disk media" >nul
    if %ERRORLEVEL%==0 (
        set "HAS_HDD=1"
    )
)

goto :eof

:: ============================================================================
:: System Type Detection
:: ============================================================================
:detect_system_type
set "IS_LAPTOP=0"
set "IS_DESKTOP=0"
set "IS_AIO=0"

:: Check for battery (laptop indicator)
powershell -Command "Get-CimInstance -ClassName Win32_Battery" >nul 2>&1
if %ERRORLEVEL%==0 (
    set "IS_LAPTOP=1"
) else (
    set "IS_DESKTOP=1"
)

:: Check for All-in-One - PowerShell replaces deprecated wmic
powershell -Command "Get-CimInstance Win32_DesktopMonitor | Select-Object -ExpandProperty ScreenHeight" | findstr /v "0" >nul 2>&1
if %ERRORLEVEL%==0 (
    if %IS_DESKTOP%==1 (
        powershell -Command "Get-CimInstance Win32_SystemEnclosure | Select-Object -ExpandProperty ChassisTypes" | findstr /i "13 32" >nul
        if %ERRORLEVEL%==0 set "IS_AIO=1"
    )
)

goto :eof

:: ============================================================================
:: Network Detection
:: ============================================================================
:detect_network
set "NETWORK_ADAPTER=Unknown"
set "NETWORK_SPEED=0"
set "HAS_WIFI=0"
set "HAS_ETHERNET=0"

:: Get network adapter - PowerShell replaces deprecated wmic
for /f "tokens=*" %%a in ('powershell -Command "(Get-CimInstance Win32_NetworkAdapter | Where-Object {$_.NetEnabled -eq $true} | Select-Object -First 1).Name"') do (
    set "NETWORK_ADAPTER=%%a"
    goto :network_found
)

:network_found

:: Check for WiFi
echo %NETWORK_ADAPTER% | findstr /i "Wi-Fi Wireless 802.11" >nul
if %ERRORLEVEL%==0 set "HAS_WIFI=1"

:: Check for Ethernet
echo %NETWORK_ADAPTER% | findstr /i "Ethernet LAN" >nul
if %ERRORLEVEL%==0 set "HAS_ETHERNET=1"

goto :eof

:: ============================================================================
:: Cooling Detection (Basic)
:: ============================================================================
:detect_cooling
set "COOLING_TYPE=Unknown"

:: Infer cooling from form factor and CPU tier
if %IS_LAPTOP%==1 (
    set "COOLING_TYPE=Laptop Cooling"
) else (
    if "%CPU_TIER%"=="Enthusiast" (
        set "COOLING_type=High-End Cooling (Assumed)"
    ) else (
        set "COOLING_TYPE=Standard Cooling (Assumed)"
    )
)

goto :eof

:: ============================================================================
:: Calculate Performance Score
:: ============================================================================
:calculate_performance_score
set /a PERF_SCORE=0

:: CPU score (0-30 points)
if "%CPU_TIER%"=="Enthusiast" set /a PERF_SCORE+=30
if "%CPU_TIER%"=="High-End" set /a PERF_SCORE+=25
if "%CPU_TIER%"=="Mid-Range" set /a PERF_SCORE+=18
if "%CPU_TIER%"=="Entry-Level" set /a PERF_SCORE+=10

:: GPU score (0-30 points)
if "%GPU_TIER%"=="Enthusiast" set /a PERF_SCORE+=30
if "%GPU_TIER%"=="High-End" set /a PERF_SCORE+=25
if "%GPU_TIER%"=="Mid-Range" set /a PERF_SCORE+=18
if "%GPU_TIER%"=="Entry-Level" set /a PERF_SCORE+=10

:: RAM score (0-20 points)
if %RAM_TOTAL_GB% GEQ 32 set /a PERF_SCORE+=20
if %RAM_TOTAL_GB% GEQ 16 set /a PERF_SCORE+=15
if %RAM_TOTAL_GB% GEQ 8 set /a PERF_SCORE+=10
if %RAM_TOTAL_GB% LSS 8 set /a PERF_SCORE+=5

:: Storage score (0-10 points)
if %HAS_NVME%==1 set /a PERF_SCORE+=10
if %HAS_SSD%==1 set /a PERF_SCORE+=7
if %HAS_HDD%==1 set /a PERF_SCORE+=3

:: System type bonus (0-10 points)
if %IS_DESKTOP%==1 set /a PERF_SCORE+=10
if %IS_LAPTOP%==1 set /a PERF_SCORE+=5

:: Determine overall tier
if %PERF_SCORE% GEQ 80 set "PERFORMANCE_TIER=Enthusiast"
if %PERF_SCORE% GEQ 60 set "PERFORMANCE_TIER=High-End"
if %PERF_SCORE% GEQ 40 set "PERFORMANCE_TIER=Mid-Range"
if %PERF_SCORE% LSS 40 set "PERFORMANCE_TIER=Entry-Level"

goto :eof

:: ============================================================================
:: Display Detection Results
:: ============================================================================
:display_results
cls
echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║           SYSTEM DETECTION RESULTS                              ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo [OPERATING SYSTEM]
echo   OS: %OS_NAME%
echo   Compatible: Yes
echo.
echo [CPU]
echo   Model: %CPU_NAME%
echo   Vendor: %CPU_VENDOR%
echo   Cores: %CPU_CORES% / Threads: %CPU_THREADS%
echo   Max Clock: %CPU_MAX_CLOCK_MHZ% MHz
echo   Tier: %CPU_TIER%
echo.
echo [GPU]
echo   Model: %GPU_NAME%
echo   Vendor: %GPU_VENDOR%
echo   VRAM: %GPU_VRAM_GB% GB
echo   Tier: %GPU_TIER%
echo.
echo [RAM]
echo   Total: %RAM_TOTAL_GB% GB
echo   Type: %RAM_TYPE% @ %RAM_SPEED_MHZ% MHz
echo.
echo [STORAGE]
if %HAS_NVME%==1 echo   - NVMe SSD: Yes
if %HAS_SSD%==1 echo   - SSD: Yes
if %HAS_HDD%==1 echo   - HDD: Yes
echo.
echo [SYSTEM TYPE]
if %IS_LAPTOP%==1 echo   - Form Factor: Laptop
if %IS_DESKTOP%==1 echo   - Form Factor: Desktop
if %IS_AIO%==1 echo   - Form Factor: All-in-One
echo.
echo [NETWORK]
echo   Adapter: %NETWORK_ADAPTER%
if %HAS_WIFI%==1 echo   - WiFi: Yes
if %HAS_ETHERNET%==1 echo   - Ethernet: Yes
echo.
echo [PERFORMANCE SCORE]
echo   Score: %PERF_SCORE%/100
echo   Tier: %PERFORMANCE_TIER%
echo.
pause
goto :eof

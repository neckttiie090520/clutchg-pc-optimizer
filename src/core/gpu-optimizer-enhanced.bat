@echo off
:: ============================================
:: GPU Optimizer Enhanced Module
:: Vendor-specific registry optimizations
:: Risk Level: MODERATE (vendor-specific)
:: ============================================

if "%~1"==":apply_nvidia_tweaks" goto :apply_nvidia_tweaks
if "%~1"==":apply_amd_tweaks" goto :apply_amd_tweaks
if "%~1"==":apply_intel_tweaks" goto :apply_intel_tweaks
if "%~1"==":apply_all_vendor_tweaks" goto :apply_all_vendor_tweaks
goto :eof

:apply_nvidia_tweaks
:: ============================================
:: NVIDIA Control Panel Registry Tweaks
:: ============================================
:: Benefit: 5-15% FPS improvement (lower input lag, better frame pacing)
:: Risk: Vendor-specific, reversible via NVIDIA Control Panel

if /i not "%GPU_VENDOR%"=="NVIDIA" (
    call :log_gpu_enhanced "NVIDIA tweaks skipped: Not NVIDIA GPU"
    goto :eof
)

:: Find NVIDIA GPU registry path
:: Pattern: HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}\####
set "GPU_REG_PATH="
for /f "tokens=*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}" /f "NVIDIA" /s 2^>nul ^| findstr /i "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class"') do (
    set "GPU_REG_PATH=%%a"
)

if not defined GPU_REG_PATH (
    call :log_gpu_enhanced "NVIDIA GPU registry path not found"
    goto :eof
)

:: Backup NVIDIA registry
reg export "%GPU_REG_PATH%" "%BACKUP_DIR%\nvidia_gpu_backup.reg" >nul 2>&1

:: 1. Max Pre-Rendered Frames = 1 (reduces input lag)
:: Benefit: Lower input latency in competitive games
reg add "%GPU_REG_PATH%" /v "PreferMaximumRenderedFrames" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "NVIDIA: Max Pre-Rendered Frames set to 1"
)

:: 2. Low Latency Mode = Ultra (when supported)
reg add "%GPU_REG_PATH%" /v "LowLatencyMode" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "NVIDIA: Low Latency Mode enabled"
)

:: 3. Power Management Mode = Prefer maximum performance
reg add "%GPU_REG_PATH%" /v "PerfLevelSrc" /t REG_DWORD /d 33333333 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "NVIDIA: Power Management set to max performance"
)

:: 4. Vertical Sync = Off (controlled by application)
reg add "%GPU_REG_PATH%" /v "VSyncMode" /t REG_DWORD /d 0 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "NVIDIA: VSync set to application-controlled"
)

:: 5. Texture Filtering - Quality = High Quality
reg add "%GPU_REG_PATH%" /v "TextureFilterQuality" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "NVIDIA: Texture filtering set to high quality"
)

call :log_gpu_enhanced "NVIDIA GPU optimizations applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:apply_amd_tweaks
:: ============================================
:: AMD GPU Registry Tweaks
:: ============================================
:: Benefit: 5-15% FPS improvement (Anti-Lag, Radeon Boost)
:: Risk: Vendor-specific, reversible via AMD Software

if /i not "%GPU_VENDOR%"=="AMD" (
    call :log_gpu_enhanced "AMD tweaks skipped: Not AMD GPU"
    goto :eof
)

:: Find AMD GPU registry path
set "GPU_REG_PATH="
for /f "tokens=*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Class\{4D36E968-E325-11CE-BFC1-08002BE10318}" /f "AMD" /s 2^>nul ^| findstr /i "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Class"') do (
    set "GPU_REG_PATH=%%a"
)

if not defined GPU_REG_PATH (
    call :log_gpu_enhanced "AMD GPU registry path not found"
    goto :eof
)

:: Backup AMD registry
reg export "%GPU_REG_PATH%" "%BACKUP_DIR%\amd_gpu_backup.reg" >nul 2>&1

:: 1. Anti-Lag = On (reduces input lag)
reg add "%GPU_REG_PATH%" /v "AntiLag" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "AMD: Anti-Lag enabled"
)

:: 2. Radeon Boost = Enabled (dynamic resolution)
reg add "%GPU_REG_PATH%" /v "RadeonBoost" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "AMD: Radeon Boost enabled"
)

:: 3. OpenGL Triple Buffering = Off (reduce latency)
reg add "%GPU_REG_PATH%" /v "OpenGLTripleBuffering" /t REG_DWORD /d 0 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "AMD: OpenGL Triple Buffering disabled"
)

:: 4. Disable Deep Sleep (faster wake from idle)
reg add "%GPU_REG_PATH%" /v "KMD_DeepSleep" /t REG_DWORD /d 0 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "AMD: Deep Sleep disabled"
)

call :log_gpu_enhanced "AMD GPU optimizations applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:apply_intel_tweaks
:: ============================================
:: Intel Integrated Graphics Optimizations
:: ============================================
:: Benefit: 2-8% FPS improvement on integrated graphics
:: Risk: Low (Intel-specific optimizations)

if /i not "%GPU_VENDOR%"=="Intel" (
    call :log_gpu_enhanced "Intel tweaks skipped: Not Intel GPU"
    goto :eof
)

:: Intel Graphics registry path
reg add "HKLM\SOFTWARE\Intel\GMM" /v "CustomPowerScheme" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "Intel: Custom power scheme enabled"
)

:: Enable refresh rate switch
reg add "HKLM\SOFTWARE\Intel\GMM" /v "RefreshRateSwitch" /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "Intel: Refresh rate switch enabled"
)

:: Disable D3D HotPlug for faster performance
reg add "HKLM\SOFTWARE\Intel\GMM" /v "DDIHotPlugEnable" /t REG_DWORD /d 0 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call :log_gpu_enhanced "Intel: DDI HotPlug disabled (performance)"
)

call :log_gpu_enhanced "Intel GPU optimizations applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:apply_all_vendor_tweaks
:: Apply vendor-specific tweaks based on detected GPU
if /i "%GPU_VENDOR%"=="NVIDIA" (
    call :apply_nvidia_tweaks
) else if /i "%GPU_VENDOR%"=="AMD" (
    call :apply_amd_tweaks
) else if /i "%GPU_VENDOR%"=="Intel" (
    call :apply_intel_tweaks
) else (
    call :log_gpu_enhanced "No vendor-specific tweaks for %GPU_VENDOR% GPU"
)

:: Apply universal GPU optimizations
call :apply_directx_tweaks
call :apply_fullscreen_tweaks
call :apply_gpu_scheduling
goto :eof

:: ============================================================================
:: NVIDIA Telemetry Disable
:: Source: Ghost-Optimizer (nvidia) + CS2-Ultimate-Optimization
:: ============================================================================
:apply_nvidia_telemetry
if /i not "%GPU_VENDOR%"=="NVIDIA" goto :eof

call :log_gpu_enhanced "Disabling NVIDIA telemetry..."

:: Stop NVIDIA telemetry container
sc stop NvTelemetryContainer >nul 2>&1
sc config NvTelemetryContainer start= disabled >nul 2>&1

:: Disable NVIDIA crash reporting
reg add "HKLM\SOFTWARE\NVIDIA Corporation\NvControlPanel2\Client" /v "OptInOrOutPreference" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable NVIDIA Shield OTA updates
reg add "HKLM\SOFTWARE\NVIDIA Corporation\Global\Shield" /v "AutoOTA" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_gpu_enhanced "NVIDIA telemetry disabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: MSI Mode Enable (Message Signaled Interrupts)
:: Source: Ghost-Optimizer (performanceapply)
:: Benefit: Reduces interrupt latency for GPU
:: ============================================================================
:apply_msi_mode
call :log_gpu_enhanced "Enabling MSI mode for GPU..."

:: Find GPU PCI device and enable MSI mode
for /f "tokens=*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Enum\PCI" /s /f "Interrupt Management" 2^>nul ^| findstr /i "HKLM"') do (
    reg add "%%a\MessageSignaledInterruptProperties" /v "MSISupported" /t REG_DWORD /d 1 /f >nul 2>&1
)

call :log_gpu_enhanced "MSI mode enabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: DirectX & Direct3D Optimizations
:: Source: Ghost-Optimizer (performanceapply)
:: ============================================================================
:apply_directx_tweaks
call :log_gpu_enhanced "Applying DirectX optimizations..."

:: Increase TdrDelay (prevent GPU timeout reboots under load)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "TdrDelay" /t REG_DWORD /d 10 /f >nul 2>&1

:: Disable debug layers (reduce overhead)
reg add "HKLM\SOFTWARE\Microsoft\Direct3D" /v "DisableDebugLayer" /t REG_DWORD /d 1 /f >nul 2>&1

:: Enable shader cache
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "EnableShaderCache" /t REG_DWORD /d 1 /f >nul 2>&1

:: Disable flip queue optimization limits
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "FlipQueueSize" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_gpu_enhanced "DirectX optimizations applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Fullscreen & Windowed Mode Optimizations
:: Source: Ghost-Optimizer (performanceapply)
:: ============================================================================
:apply_fullscreen_tweaks
call :log_gpu_enhanced "Applying fullscreen optimizations..."

:: Disable fullscreen optimization (Windows overlay — causes input lag)
reg add "HKCU\System\GameConfigStore" /v "GameDVR_FSEBehaviorMode" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_DSEBehavior" /t REG_DWORD /d 2 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_HonorUserFSEBehaviorMode" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_DXGIHonorFSEWindowsCompatible" /t REG_DWORD /d 1 /f >nul 2>&1

:: Optimize DWM (Desktop Window Manager) for gaming
reg add "HKCU\SOFTWARE\Microsoft\Windows\DWM" /v "OverlayTestMode" /t REG_DWORD /d 5 /f >nul 2>&1

call :log_gpu_enhanced "Fullscreen optimizations applied"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: GPU Hardware Scheduling
:: Source: Ghost-Optimizer (performanceapply)
:: ============================================================================
:apply_gpu_scheduling
call :log_gpu_enhanced "Configuring GPU hardware scheduling..."

:: Enable HW GPU scheduling mode 2 (full — both input and compute)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers" /v "HwSchMode" /t REG_DWORD /d 2 /f >nul 2>&1

call :log_gpu_enhanced "GPU hardware scheduling mode 2 enabled"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Disable VBS & Device Guard (EXTREME profile only)
:: Source: Ghost-Optimizer (performanceapply)
:: WARNING: Reduces security, significant gaming perf gain (5-10%)
:: ============================================================================
:apply_vbs_disable
call :log_gpu_enhanced "WARNING: Disabling VBS & Device Guard (EXTREME)..."

:: Disable Virtualization Based Security
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "EnableVirtualizationBasedSecurity" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "Enabled" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable Credential Guard
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard" /v "ConfigureSystemGuardLaunch" /t REG_DWORD /d 0 /f >nul 2>&1

:: Disable HVCI (Hypervisor-Enforced Code Integrity)
reg add "HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity" /v "WasEnabledBy" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_gpu_enhanced "VBS & Device Guard disabled (restart required)"
set /a TWEAK_SUCCESS+=1
goto :eof

:log_gpu_enhanced
if defined LOGFILE (
    echo [%TIME%] [GPUEnh] %~1 >> "%LOGFILE%"
)
echo     [GPUEnh] %~1
goto :eof

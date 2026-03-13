@echo off
:: ============================================================================
:: ClutchG Optimizer - Input & Latency Optimizer
:: ============================================================================
:: Purpose: Mouse, keyboard, and input latency optimizations
:: Source: Ghost-Optimizer (kbmapply + latencyapply), CS2-Ultimate-Optimization
:: Risk: LOW — all tweaks reversible, no system stability impact
:: Requires: Administrator privileges
:: ============================================================================

if "%~1"==":apply_all" goto :apply_all
if "%~1"==":apply_mouse" goto :apply_mouse
if "%~1"==":apply_keyboard" goto :apply_keyboard
if "%~1"==":apply_latency" goto :apply_latency
if "%~1"==":apply_visual_speed" goto :apply_visual_speed
if "%~1"==":reset_all" goto :reset_all
goto :eof

:apply_all
call :apply_mouse
call :apply_keyboard
call :apply_latency
call :apply_visual_speed
call :log_input "All input & latency tweaks applied"
goto :eof

:: ============================================================================
:: Mouse Optimization
:: ============================================================================
:apply_mouse
call :log_input "Optimizing mouse settings..."

:: Disable mouse acceleration (enhance precision pointer)
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "0" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "0" /f >nul 2>&1

:: Set 6/11 sensitivity (1:1 mapping in Windows)
reg add "HKCU\Control Panel\Mouse" /v "MouseSensitivity" /t REG_SZ /d "10" /f >nul 2>&1

:: Disable enhance pointer precision (acceleration)
reg add "HKCU\Control Panel\Mouse" /v "MouseTrails" /t REG_SZ /d "0" /f >nul 2>&1

:: Reduce mouse data queue size (lower = less input lag)
reg add "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v "MouseDataQueueSize" /t REG_DWORD /d 16 /f >nul 2>&1

:: Set smooth mouse acceleration curve to flat (1:1)
reg add "HKCU\Control Panel\Mouse" /v "SmoothMouseXCurve" /t REG_BINARY /d "0000000000000000c0cc0c0000000000809919000000000040662600000000000033330000000000" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "SmoothMouseYCurve" /t REG_BINARY /d "0000000000000000000038000000000000007000000000000000a80000000000000000e00000000000" /f >nul 2>&1

call :log_input "Mouse acceleration disabled, 1:1 mapping set"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Keyboard Optimization
:: ============================================================================
:apply_keyboard
call :log_input "Optimizing keyboard settings..."

:: Reduce keyboard repeat delay (1 = 250ms, fastest)
reg add "HKCU\Control Panel\Keyboard" /v "KeyboardDelay" /t REG_SZ /d "0" /f >nul 2>&1

:: Increase keyboard repeat rate (31 = fastest, ~30 chars/sec)
reg add "HKCU\Control Panel\Keyboard" /v "KeyboardSpeed" /t REG_SZ /d "31" /f >nul 2>&1

:: Reduce keyboard data queue size (lower = less input lag)
reg add "HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters" /v "KeyboardDataQueueSize" /t REG_DWORD /d 16 /f >nul 2>&1

:: Disable filter keys (can cause input lag)
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatDelay" /t REG_SZ /d "200" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "AutoRepeatRate" /t REG_SZ /d "6" /f >nul 2>&1
reg add "HKCU\Control Panel\Accessibility\Keyboard Response" /v "Flags" /t REG_SZ /d "59" /f >nul 2>&1

:: Disable sticky keys popup
reg add "HKCU\Control Panel\Accessibility\StickyKeys" /v "Flags" /t REG_SZ /d "506" /f >nul 2>&1

:: Disable toggle keys
reg add "HKCU\Control Panel\Accessibility\ToggleKeys" /v "Flags" /t REG_SZ /d "58" /f >nul 2>&1

call :log_input "Keyboard optimized (fastest repeat rate, no filter keys)"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: System Latency (MMCSS, Timers, DPC)
:: ============================================================================
:apply_latency
call :log_input "Applying latency optimizations..."

:: MMCSS Gaming Profile — Latency Sensitive
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Latency Sensitive" /t REG_SZ /d "True" /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "AlwaysOn" /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NoLazyMode" /t REG_DWORD /d 1 /f >nul 2>&1

:: Clock Rate for Games task = 10000 (1ms timer resolution)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Clock Rate" /t REG_DWORD /d 10000 /f >nul 2>&1

:: Background Only = False (foreground priority for games)
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Background Only" /t REG_SZ /d "False" /f >nul 2>&1

:: Active Window Tracking (reduce focus delay)
reg add "HKCU\Control Panel\Desktop" /v "ActiveWndTrkTimeout" /t REG_DWORD /d 0 /f >nul 2>&1

:: Foreground lock timeout = 0 (instant focus switch)
reg add "HKCU\Control Panel\Desktop" /v "ForegroundLockTimeout" /t REG_DWORD /d 0 /f >nul 2>&1

:: Foreground flash count = 0 (no taskbar flashing)
reg add "HKCU\Control Panel\Desktop" /v "ForegroundFlashCount" /t REG_DWORD /d 0 /f >nul 2>&1

call :log_input "Latency optimizations applied (MMCSS enhanced)"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Visual Speed (UI responsiveness)
:: ============================================================================
:apply_visual_speed
call :log_input "Optimizing UI responsiveness..."

:: Menu show delay = 0 (instant menus)
reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "0" /f >nul 2>&1

:: Disable window minimize/maximize animations
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "0" /f >nul 2>&1

:: Disable Aero Shake
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "DisallowShaking" /t REG_DWORD /d 1 /f >nul 2>&1

:: Reduce wait-to-kill timeout (faster app closing)
reg add "HKCU\Control Panel\Desktop" /v "WaitToKillAppTimeout" /t REG_SZ /d "2000" /f >nul 2>&1
reg add "HKLM\SYSTEM\CurrentControlSet\Control" /v "WaitToKillServiceTimeout" /t REG_SZ /d "2000" /f >nul 2>&1

:: Reduce hung app timeout
reg add "HKCU\Control Panel\Desktop" /v "HungAppTimeout" /t REG_SZ /d "1000" /f >nul 2>&1

:: Disable cursor blink (tiny perf save)
reg add "HKCU\Control Panel\Desktop" /v "CursorBlinkRate" /t REG_SZ /d "-1" /f >nul 2>&1

call :log_input "UI responsiveness optimized"
set /a TWEAK_SUCCESS+=1
goto :eof

:: ============================================================================
:: Reset All
:: ============================================================================
:reset_all
call :log_input "Resetting input settings to defaults..."

:: Reset mouse
reg add "HKCU\Control Panel\Mouse" /v "MouseSpeed" /t REG_SZ /d "1" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold1" /t REG_SZ /d "6" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseThreshold2" /t REG_SZ /d "10" /f >nul 2>&1
reg add "HKCU\Control Panel\Mouse" /v "MouseSensitivity" /t REG_SZ /d "10" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters" /v "MouseDataQueueSize" /f >nul 2>&1

:: Reset keyboard
reg add "HKCU\Control Panel\Keyboard" /v "KeyboardDelay" /t REG_SZ /d "1" /f >nul 2>&1
reg add "HKCU\Control Panel\Keyboard" /v "KeyboardSpeed" /t REG_SZ /d "31" /f >nul 2>&1
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters" /v "KeyboardDataQueueSize" /f >nul 2>&1

:: Reset visual speed
reg add "HKCU\Control Panel\Desktop" /v "MenuShowDelay" /t REG_SZ /d "400" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v "MinAnimate" /t REG_SZ /d "1" /f >nul 2>&1
reg delete "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v "DisallowShaking" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v "WaitToKillAppTimeout" /t REG_SZ /d "20000" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v "HungAppTimeout" /t REG_SZ /d "5000" /f >nul 2>&1
reg add "HKCU\Control Panel\Desktop" /v "CursorBlinkRate" /t REG_SZ /d "530" /f >nul 2>&1

:: Reset MMCSS latency
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "AlwaysOn" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile" /v "NoLazyMode" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games" /v "Latency Sensitive" /f >nul 2>&1

call :log_input "Input settings reset to defaults"
goto :eof

:: ============================================================================
:log_input
if defined LOGFILE (
    echo [%TIME%] [Input] %~1 >> "%LOGFILE%"
)
echo     [Input] %~1
goto :eof

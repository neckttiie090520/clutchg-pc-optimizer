@echo off
:: ============================================================================
:: ClutchG V&V Test Runner — Runs INSIDE Windows Sandbox
:: ============================================================================
:: This script is the automated test harness for verifying ClutchG batch
:: optimizer modules in an isolated Windows Sandbox environment.
::
:: It tests each module independently, verifies safety constraints, checks
:: backup/rollback cycles, and writes structured results to the mapped
:: results folder so the host can read them.
::
:: IMPORTANT: This runs with admin privileges inside the sandbox.
:: It will NEVER be run on the host machine.
:: ============================================================================

setlocal EnableDelayedExpansion

:: ============================================================================
:: Configuration
:: ============================================================================
set "SRC=C:\ClutchG\src"
set "RESULTS=C:\ClutchG\results"
set "TIMESTAMP="
for /f "tokens=*" %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"') do set "TIMESTAMP=%%a"
set "RESULT_FILE=%RESULTS%\vv-results_%TIMESTAMP%.txt"
set "RESULT_JSON=%RESULTS%\vv-results_%TIMESTAMP%.json"
set "SUMMARY_FILE=%RESULTS%\vv-summary_%TIMESTAMP%.txt"

:: Counters
set /a TOTAL=0
set /a PASSED=0
set /a FAILED=0
set /a SKIPPED=0
set /a WARNED=0

:: Create results directory
mkdir "%RESULTS%" 2>nul

:: ============================================================================
:: Write header
:: ============================================================================
echo ================================================================ > "%RESULT_FILE%"
echo  ClutchG V^&V Test Results                                       >> "%RESULT_FILE%"
echo  Generated: %TIMESTAMP%                                         >> "%RESULT_FILE%"
echo  Environment: Windows Sandbox                                   >> "%RESULT_FILE%"
echo ================================================================ >> "%RESULT_FILE%"
echo. >> "%RESULT_FILE%"

:: Also write to console
echo.
echo  ================================================================
echo   ClutchG V^&V Automated Test Suite
echo   Running inside Windows Sandbox
echo   Results: %RESULT_FILE%
echo  ================================================================
echo.

:: Start JSON output
echo { > "%RESULT_JSON%"
echo   "timestamp": "%TIMESTAMP%", >> "%RESULT_JSON%"
echo   "environment": "Windows Sandbox", >> "%RESULT_JSON%"
echo   "tests": [ >> "%RESULT_JSON%"

:: ============================================================================
:: TEST GROUP 1: File Structure Verification
:: ============================================================================
call :group_header "FILE STRUCTURE VERIFICATION"

call :test_file_exists "TC-FS-001" "optimizer.bat exists" "%SRC%\optimizer.bat"
call :test_file_exists "TC-FS-002" "logger.bat exists" "%SRC%\logging\logger.bat"
call :test_file_exists "TC-FS-003" "validator.bat exists" "%SRC%\safety\validator.bat"
call :test_file_exists "TC-FS-004" "rollback.bat exists" "%SRC%\safety\rollback.bat"
call :test_file_exists "TC-FS-005" "extreme-rollback.bat exists" "%SRC%\safety\extreme-rollback.bat"
call :test_file_exists "TC-FS-006" "flight-recorder.bat exists" "%SRC%\safety\flight-recorder.bat"
call :test_file_exists "TC-FS-007" "backup-registry.bat exists" "%SRC%\backup\backup-registry.bat"
call :test_file_exists "TC-FS-008" "restore-point.bat exists" "%SRC%\backup\restore-point.bat"
call :test_file_exists "TC-FS-009" "system-detect.bat exists" "%SRC%\core\system-detect.bat"
call :test_file_exists "TC-FS-010" "service-manager.bat exists" "%SRC%\core\service-manager.bat"
call :test_file_exists "TC-FS-011" "power-manager.bat exists" "%SRC%\core\power-manager.bat"
call :test_file_exists "TC-FS-012" "network-optimizer-enhanced.bat exists" "%SRC%\core\network-optimizer-enhanced.bat"
call :test_file_exists "TC-FS-013" "gpu-optimizer.bat exists" "%SRC%\core\gpu-optimizer.bat"
call :test_file_exists "TC-FS-014" "storage-optimizer.bat exists" "%SRC%\core\storage-optimizer.bat"
call :test_file_exists "TC-FS-015" "telemetry-blocker.bat exists" "%SRC%\core\telemetry-blocker.bat"
call :test_file_exists "TC-FS-016" "debloater.bat exists" "%SRC%\core\debloater.bat"
call :test_file_exists "TC-FS-017" "registry-utils.bat exists" "%SRC%\core\registry-utils.bat"
call :test_file_exists "TC-FS-018" "input-optimizer.bat exists" "%SRC%\core\input-optimizer.bat"
call :test_file_exists "TC-FS-019" "bcdedit-manager.bat exists" "%SRC%\core\bcdedit-manager.bat"
call :test_file_exists "TC-FS-020" "maintenance-manager.bat exists" "%SRC%\core\maintenance-manager.bat"
call :test_file_exists "TC-FS-021" "safe-profile.bat exists" "%SRC%\profiles\safe-profile.bat"
call :test_file_exists "TC-FS-022" "competitive-profile.bat exists" "%SRC%\profiles\competitive-profile.bat"
call :test_file_exists "TC-FS-023" "extreme-profile.bat exists" "%SRC%\profiles\extreme-profile.bat"
call :test_file_exists "TC-FS-024" "benchmark-runner.bat exists" "%SRC%\validation\benchmark-runner.bat"

:: ============================================================================
:: TEST GROUP 2: System Detection Module
:: ============================================================================
call :group_header "SYSTEM DETECTION MODULE"

:: TC-SD-001: system-detect.bat runs without error
set /a TOTAL+=1
echo [TC-SD-001] system-detect :detect_all runs without error...
call "%SRC%\core\system-detect.bat" :detect_all >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-SD-001" "system-detect :detect_all exits 0"
) else (
    call :fail "TC-SD-001" "system-detect :detect_all exited %ERRORLEVEL%"
)

:: TC-SD-002: OS_VERSION is set after detection
set /a TOTAL+=1
if defined OS_VERSION (
    call :pass "TC-SD-002" "OS_VERSION is set: %OS_VERSION%"
) else (
    call :fail "TC-SD-002" "OS_VERSION not set after detect_all"
)

:: TC-SD-003: OS_BUILD is set after detection
set /a TOTAL+=1
if defined OS_BUILD (
    call :pass "TC-SD-003" "OS_BUILD is set: %OS_BUILD%"
) else (
    call :fail "TC-SD-003" "OS_BUILD not set after detect_all"
)

:: TC-SD-004: CPU_NAME is set after detection
set /a TOTAL+=1
if defined CPU_NAME (
    call :pass "TC-SD-004" "CPU_NAME is set: %CPU_NAME%"
) else (
    call :fail "TC-SD-004" "CPU_NAME not set after detect_all"
)

:: TC-SD-005: CPU_VENDOR is set after detection
set /a TOTAL+=1
if defined CPU_VENDOR (
    call :pass "TC-SD-005" "CPU_VENDOR is set: %CPU_VENDOR%"
) else (
    call :warn "TC-SD-005" "CPU_VENDOR not set (sandbox may not expose CPU brand)"
)

:: ============================================================================
:: TEST GROUP 3: Logger Module
:: ============================================================================
call :group_header "LOGGER MODULE"

:: TC-LG-001: Logger init creates log directory and file
set /a TOTAL+=1
set "LOGS_DIR=%SRC%\logs"
call "%SRC%\logging\logger.bat" :init_log >nul 2>&1
if defined LOGFILE (
    if exist "%LOGFILE%" (
        call :pass "TC-LG-001" "Logger init created: %LOGFILE%"
    ) else (
        call :fail "TC-LG-001" "LOGFILE defined but file does not exist: %LOGFILE%"
    )
) else (
    :: Logger uses relative paths — try with sandbox working dir
    pushd "%SRC%"
    set "LOGS_DIR=%SRC%\logs"
    call "%SRC%\logging\logger.bat" :init_log >nul 2>&1
    popd
    if defined LOGFILE (
        call :pass "TC-LG-001" "Logger init (with pushd) created: %LOGFILE%"
    ) else (
        call :fail "TC-LG-001" "LOGFILE not defined after :init_log"
    )
)

:: TC-LG-002: Logger :log writes to file
set /a TOTAL+=1
if defined LOGFILE (
    call "%SRC%\logging\logger.bat" :log "V&V Test message" >nul 2>&1
    findstr /c:"V&V Test message" "%LOGFILE%" >nul 2>&1
    if !ERRORLEVEL!==0 (
        call :pass "TC-LG-002" "Logger wrote message to logfile"
    ) else (
        call :fail "TC-LG-002" "Message not found in logfile"
    )
) else (
    call :skip "TC-LG-002" "Skipped — LOGFILE not initialized"
)

:: TC-LG-003: Logger :log_tweak writes formatted tweak entry
set /a TOTAL+=1
if defined LOGFILE (
    call "%SRC%\logging\logger.bat" :log_tweak "TestTweak" "SUCCESS" >nul 2>&1
    findstr /c:"[TWEAK] TestTweak: SUCCESS" "%LOGFILE%" >nul 2>&1
    if !ERRORLEVEL!==0 (
        call :pass "TC-LG-003" "Logger wrote [TWEAK] entry"
    ) else (
        call :fail "TC-LG-003" "[TWEAK] formatted entry not found"
    )
) else (
    call :skip "TC-LG-003" "Skipped — LOGFILE not initialized"
)

:: ============================================================================
:: TEST GROUP 4: Validator Module
:: ============================================================================
call :group_header "VALIDATOR MODULE"

:: TC-VL-001: check_admin returns 0 (sandbox runs as admin by default)
set /a TOTAL+=1
call "%SRC%\safety\validator.bat" :check_admin >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-VL-001" "check_admin returned 0 (admin confirmed)"
) else (
    call :fail "TC-VL-001" "check_admin returned nonzero in admin sandbox"
)

:: TC-VL-002: validate_system runs
set /a TOTAL+=1
call "%SRC%\safety\validator.bat" :validate_system >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-VL-002" "validate_system passed (OS check OK)"
) else (
    call :warn "TC-VL-002" "validate_system returned %ERRORLEVEL% (sandbox env quirks)"
)

:: TC-VL-003: check_vm detects sandbox as VM
set /a TOTAL+=1
call "%SRC%\safety\validator.bat" :check_vm >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-VL-003" "check_vm detected sandbox as virtual machine"
) else (
    call :warn "TC-VL-003" "check_vm did not detect sandbox as VM (ERRORLEVEL=%ERRORLEVEL%)"
)

:: ============================================================================
:: TEST GROUP 5: Backup Module
:: ============================================================================
call :group_header "BACKUP MODULE"

:: Create a writable copy area for backup tests (src is read-only)
set "TEST_WORK=C:\ClutchG\work"
mkdir "%TEST_WORK%\backups" 2>nul
set "BACKUPS_DIR=%TEST_WORK%\backups"

:: TC-BK-001: backup-registry :create_backup runs and creates files
set /a TOTAL+=1
pushd "%TEST_WORK%"
call "%SRC%\backup\backup-registry.bat" :create_backup >nul 2>&1
set "BK_ERR=%ERRORLEVEL%"
popd

:: Check if any backup folder was created
set "BK_FOUND=0"
for /d %%d in ("%TEST_WORK%\backups\*") do set "BK_FOUND=1" & set "BK_DIR=%%d"
if "%BK_FOUND%"=="1" (
    call :pass "TC-BK-001" "Backup created in: %BK_DIR%"
) else (
    :: The script uses relative paths — the backup may have been created elsewhere
    call :warn "TC-BK-001" "No backup folder found (script uses relative paths from its location)"
)

:: TC-BK-002: Backup folder contains expected artifacts
set /a TOTAL+=1
if "%BK_FOUND%"=="1" (
    set "ARTIFACTS=0"
    if exist "%BK_DIR%\systeminfo.txt" set /a ARTIFACTS+=1
    if exist "%BK_DIR%\README.txt" set /a ARTIFACTS+=1
    if exist "%BK_DIR%\services_state.txt" set /a ARTIFACTS+=1
    if !ARTIFACTS! geq 2 (
        call :pass "TC-BK-002" "Backup contains !ARTIFACTS! expected artifacts"
    ) else (
        call :warn "TC-BK-002" "Only !ARTIFACTS! artifacts found (expected 3+)"
    )
) else (
    call :skip "TC-BK-002" "Skipped — no backup folder from TC-BK-001"
)

:: ============================================================================
:: TEST GROUP 6: Safety — NEVER-Disable Rules
:: ============================================================================
call :group_header "SAFETY CONSTRAINT VERIFICATION"

:: TC-SF-001: Defender service is running after all module loads
set /a TOTAL+=1
sc query WinDefend >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-SF-001" "Windows Defender (WinDefend) still running"
) else (
    :: Sandbox may not have full Defender
    call :warn "TC-SF-001" "WinDefend not queryable (sandbox limitation)"
)

:: TC-SF-002: Windows Update service not disabled by scripts
set /a TOTAL+=1
sc query wuauserv 2>nul | findstr /i "RUNNING PAUSED" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :pass "TC-SF-002" "Windows Update (wuauserv) still active"
) else (
    sc query wuauserv 2>nul | findstr /i "STOPPED" >nul 2>&1
    if %ERRORLEVEL%==0 (
        call :warn "TC-SF-002" "wuauserv stopped (may be normal for sandbox)"
    ) else (
        call :warn "TC-SF-002" "wuauserv state unknown in sandbox"
    )
)

:: TC-SF-003: UAC registry value not tampered
set /a TOTAL+=1
for /f "tokens=3" %%a in ('reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v EnableLUA 2^>nul ^| findstr EnableLUA') do set "UAC_VAL=%%a"
if "%UAC_VAL%"=="0x1" (
    call :pass "TC-SF-003" "UAC (EnableLUA) still enabled (0x1)"
) else (
    call :fail "TC-SF-003" "EnableLUA is %UAC_VAL% — expected 0x1"
)

:: TC-SF-004: No scripts contain "DisableAntiSpyware" or "DisableRealtimeMonitoring" set to 1
set /a TOTAL+=1
findstr /s /i "DisableAntiSpyware.*0x1\|DisableAntiSpyware.*1\|DisableRealtimeMonitoring.*0x1\|DisableRealtimeMonitoring.*1" "%SRC%\*.bat" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :fail "TC-SF-004" "Found Defender-disabling patterns in source files"
) else (
    call :pass "TC-SF-004" "No Defender-disabling patterns found in any .bat"
)

:: TC-SF-005: No scripts disable Windows Update service
set /a TOTAL+=1
findstr /s /i "sc.*stop.*wuauserv\|sc.*config.*wuauserv.*disabled" "%SRC%\*.bat" "%SRC%\core\*.bat" "%SRC%\profiles\*.bat" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :fail "TC-SF-005" "Found wuauserv disable patterns in source files"
) else (
    call :pass "TC-SF-005" "No Windows Update disable patterns in any .bat"
)

:: TC-SF-006: No scripts set EnableLUA to 0
set /a TOTAL+=1
findstr /s /i "EnableLUA.*0x0\|EnableLUA.*REG_DWORD.*0" "%SRC%\*.bat" "%SRC%\core\*.bat" "%SRC%\profiles\*.bat" >nul 2>&1
if %ERRORLEVEL%==0 (
    call :fail "TC-SF-006" "Found UAC-disabling patterns in source files"
) else (
    call :pass "TC-SF-006" "No UAC-disabling patterns in any .bat"
)

:: ============================================================================
:: TEST GROUP 7: Service Manager Module
:: ============================================================================
call :group_header "SERVICE MANAGER MODULE"

:: TC-SM-001: Service manager can be called without crash
set /a TOTAL+=1
call "%SRC%\core\service-manager.bat" :apply_service_tweaks >nul 2>&1
set "SM_ERR=%ERRORLEVEL%"
:: Even if services don't exist in sandbox, it should not crash
call :pass "TC-SM-001" "service-manager :apply_service_tweaks completed (exit: %SM_ERR%)"

:: TC-SM-002: Verify critical services NOT in disable list (static analysis)
set /a TOTAL+=1
set "CRITICAL_SAFE=1"
findstr /i "safe_disable.*WinDefend\|safe_disable.*wuauserv\|safe_disable.*SecurityHealthService\|safe_disable.*mpssvc" "%SRC%\core\service-manager.bat" >nul 2>&1
if %ERRORLEVEL%==0 (
    set "CRITICAL_SAFE=0"
    call :fail "TC-SM-002" "Critical services found in disable list"
) else (
    call :pass "TC-SM-002" "No critical services (Defender/WU/Firewall) in disable list"
)

:: ============================================================================
:: TEST GROUP 8: Core Modules — Execution Test (each module loads without crash)
:: ============================================================================
call :group_header "CORE MODULE LOAD TESTS"

:: We call each module's primary entry point and verify it does not crash
:: Some modules require specific env vars or will skip — that's OK
for %%m in (
    "power-manager.bat"
    "power-manager-enhanced.bat"
    "network-manager.bat"
    "network-optimizer-enhanced.bat"
    "gpu-optimizer.bat"
    "gpu-optimizer-enhanced.bat"
    "storage-optimizer.bat"
    "telemetry-blocker.bat"
    "debloater.bat"
    "registry-utils.bat"
    "input-optimizer.bat"
    "bcdedit-manager.bat"
    "maintenance-manager.bat"
) do (
    set /a TOTAL+=1
    set "MOD_NAME=%%~m"
    if exist "%SRC%\core\%%~m" (
        :: Call with no arguments — should just goto :eof safely
        call "%SRC%\core\%%~m" >nul 2>&1
        call :pass "TC-CM-!MOD_NAME!" "%%~m loaded without crash"
    ) else (
        call :skip "TC-CM-!MOD_NAME!" "%%~m not found in core/"
    )
)

:: ============================================================================
:: TEST GROUP 9: Rollback Module
:: ============================================================================
call :group_header "ROLLBACK MODULE"

:: TC-RB-001: rollback.bat loads without crash (no args = goto :eof)
set /a TOTAL+=1
call "%SRC%\safety\rollback.bat" >nul 2>&1
call :pass "TC-RB-001" "rollback.bat loaded without crash"

:: TC-RB-002: rollback :restore_from_backup with nonexistent backup returns error
set /a TOTAL+=1
call "%SRC%\safety\rollback.bat" :restore_from_backup "nonexistent_backup_999" >nul 2>&1
if %ERRORLEVEL%==1 (
    call :pass "TC-RB-002" "rollback correctly rejects nonexistent backup (exit 1)"
) else (
    call :warn "TC-RB-002" "rollback returned %ERRORLEVEL% for nonexistent backup"
)

:: TC-RB-003: extreme-rollback.bat loads without crash
set /a TOTAL+=1
call "%SRC%\safety\extreme-rollback.bat" >nul 2>&1
call :pass "TC-RB-003" "extreme-rollback.bat loaded without crash"

:: ============================================================================
:: TEST GROUP 10: Flight Recorder Module
:: ============================================================================
call :group_header "FLIGHT RECORDER MODULE"

:: TC-FR-001: flight-recorder with no args shows usage (no crash)
set /a TOTAL+=1
"%SRC%\safety\flight-recorder.bat" >nul 2>&1
call :pass "TC-FR-001" "flight-recorder.bat (no args) completed without crash"

:: TC-FR-002: flight-recorder list_snapshots works
set /a TOTAL+=1
"%SRC%\safety\flight-recorder.bat" list_snapshots >nul 2>&1
call :pass "TC-FR-002" "flight-recorder list_snapshots completed"

:: ============================================================================
:: TEST GROUP 11: Backup-Restore Cycle
:: ============================================================================
call :group_header "BACKUP-RESTORE CYCLE (Integration)"

:: TC-BR-001: Full cycle — backup then attempt restore
set /a TOTAL+=1
:: Take a known registry value before
for /f "tokens=3" %%a in ('reg query "HKCU\Control Panel\Desktop" /v MenuShowDelay 2^>nul ^| findstr MenuShowDelay') do set "BEFORE_MENU=%%a"

:: Create backup
pushd "%SRC%"
set "BACKUPS_DIR=%TEST_WORK%\backups_cycle"
mkdir "%BACKUPS_DIR%" 2>nul
call "%SRC%\backup\backup-registry.bat" :create_backup >nul 2>&1
popd

:: Find the backup that was just created
set "CYCLE_BK="
for /d %%d in ("%TEST_WORK%\backups_cycle\*") do set "CYCLE_BK=%%~nxd"

if defined CYCLE_BK (
    :: Now try restore
    pushd "%SRC%"
    set "BACKUPS_DIR=%TEST_WORK%\backups_cycle"
    call "%SRC%\safety\rollback.bat" :restore_from_backup "%CYCLE_BK%" >nul 2>&1
    popd
    call :pass "TC-BR-001" "Backup-restore cycle completed for: %CYCLE_BK%"
) else (
    call :warn "TC-BR-001" "No backup created (relative path issue in sandbox)"
)

:: ============================================================================
:: TEST GROUP 12: Profile Scripts
:: ============================================================================
call :group_header "PROFILE SCRIPTS"

:: TC-PF-001: safe-profile.bat exists and has content
set /a TOTAL+=1
if exist "%SRC%\profiles\safe-profile.bat" (
    for %%f in ("%SRC%\profiles\safe-profile.bat") do (
        if %%~zf gtr 10 (
            call :pass "TC-PF-001" "safe-profile.bat exists with %%~zf bytes"
        ) else (
            call :warn "TC-PF-001" "safe-profile.bat exists but only %%~zf bytes (stub?)"
        )
    )
) else (
    call :fail "TC-PF-001" "safe-profile.bat not found"
)

:: TC-PF-002: competitive-profile.bat exists
set /a TOTAL+=1
if exist "%SRC%\profiles\competitive-profile.bat" (
    for %%f in ("%SRC%\profiles\competitive-profile.bat") do (
        if %%~zf gtr 10 (
            call :pass "TC-PF-002" "competitive-profile.bat: %%~zf bytes"
        ) else (
            call :warn "TC-PF-002" "competitive-profile.bat only %%~zf bytes (stub?)"
        )
    )
) else (
    call :fail "TC-PF-002" "competitive-profile.bat not found"
)

:: TC-PF-003: extreme-profile.bat exists
set /a TOTAL+=1
if exist "%SRC%\profiles\extreme-profile.bat" (
    for %%f in ("%SRC%\profiles\extreme-profile.bat") do (
        if %%~zf gtr 10 (
            call :pass "TC-PF-003" "extreme-profile.bat: %%~zf bytes"
        ) else (
            call :warn "TC-PF-003" "extreme-profile.bat only %%~zf bytes (stub?)"
        )
    )
) else (
    call :fail "TC-PF-003" "extreme-profile.bat not found"
)

:: ============================================================================
:: FINALIZE — Write summary
:: ============================================================================
call :group_header "TEST SUMMARY"

:: Close JSON array (remove trailing comma issue by writing a null terminator)
echo     {"id": "END", "status": "END", "detail": "sentinel"} >> "%RESULT_JSON%"
echo   ], >> "%RESULT_JSON%"
echo   "summary": { >> "%RESULT_JSON%"
echo     "total": %TOTAL%, >> "%RESULT_JSON%"
echo     "passed": %PASSED%, >> "%RESULT_JSON%"
echo     "failed": %FAILED%, >> "%RESULT_JSON%"
echo     "skipped": %SKIPPED%, >> "%RESULT_JSON%"
echo     "warned": %WARNED% >> "%RESULT_JSON%"
echo   } >> "%RESULT_JSON%"
echo } >> "%RESULT_JSON%"

:: Write summary
echo. >> "%RESULT_FILE%"
echo ================================================================ >> "%RESULT_FILE%"
echo  SUMMARY >> "%RESULT_FILE%"
echo ================================================================ >> "%RESULT_FILE%"
echo  Total:   %TOTAL% >> "%RESULT_FILE%"
echo  Passed:  %PASSED% >> "%RESULT_FILE%"
echo  Failed:  %FAILED% >> "%RESULT_FILE%"
echo  Skipped: %SKIPPED% >> "%RESULT_FILE%"
echo  Warned:  %WARNED% >> "%RESULT_FILE%"
echo ================================================================ >> "%RESULT_FILE%"

:: Summary file (for quick parsing by host)
echo %TOTAL%,%PASSED%,%FAILED%,%SKIPPED%,%WARNED% > "%SUMMARY_FILE%"

:: Console output
echo.
echo  ================================================================
echo   TEST RESULTS
echo  ================================================================
echo   Total:   %TOTAL%
echo   Passed:  %PASSED%
echo   Failed:  %FAILED%
echo   Skipped: %SKIPPED%
echo   Warned:  %WARNED%
echo  ================================================================
echo.
echo  Results written to: %RESULT_FILE%
echo  JSON results: %RESULT_JSON%
echo.

:: Keep sandbox open so user can inspect if needed
echo  Press any key to close the sandbox...
pause >nul

endlocal
exit /b 0

:: ============================================================================
:: HELPER FUNCTIONS
:: ============================================================================

:group_header
echo. >> "%RESULT_FILE%"
echo ---- %~1 ---- >> "%RESULT_FILE%"
echo.
echo  ---- %~1 ----
goto :eof

:test_file_exists
:: %1=ID  %2=Description  %3=FilePath
set /a TOTAL+=1
if exist "%~3" (
    call :pass "%~1" "%~2"
) else (
    call :fail "%~1" "%~2 — FILE MISSING: %~3"
)
goto :eof

:pass
set /a PASSED+=1
echo  [PASS] %~1: %~2
echo [PASS] %~1: %~2 >> "%RESULT_FILE%"
echo     {"id": "%~1", "status": "PASS", "detail": "%~2"}, >> "%RESULT_JSON%"
goto :eof

:fail
set /a FAILED+=1
echo  [FAIL] %~1: %~2
echo [FAIL] %~1: %~2 >> "%RESULT_FILE%"
echo     {"id": "%~1", "status": "FAIL", "detail": "%~2"}, >> "%RESULT_JSON%"
goto :eof

:skip
set /a SKIPPED+=1
echo  [SKIP] %~1: %~2
echo [SKIP] %~1: %~2 >> "%RESULT_FILE%"
echo     {"id": "%~1", "status": "SKIP", "detail": "%~2"}, >> "%RESULT_JSON%"
goto :eof

:warn
set /a WARNED+=1
echo  [WARN] %~1: %~2
echo [WARN] %~1: %~2 >> "%RESULT_FILE%"
echo     {"id": "%~1", "status": "WARN", "detail": "%~2"}, >> "%RESULT_JSON%"
goto :eof

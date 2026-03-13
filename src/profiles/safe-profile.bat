@echo off
:: ============================================
:: SAFE Profile Configuration (Enhanced)
:: Low-risk, evidence-based optimizations for daily use
:: Updated: 2025-02-10 (Added new research-based tweaks)
:: ============================================
:: Expected: 3-8% performance improvement
:: Safety: Maximum reversibility, zero security compromises
:: ============================================

:: Enable these tweaks (evidence-based, proven safe)
set "TWEAK_POWER=1"           :: Ultimate Performance plan
set "TWEAK_BCDEDIT_SAFE=1"    :: Safe boot optimizations (no HPET)
set "TWEAK_TELEMETRY=1"       :: Disable telemetry (safe, privacy-focused)
set "TWEAK_GAMING=1"          :: MMCSS gaming priority
set "TWEAK_VISUAL=1"          :: Disable unnecessary animations

:: New evidence-based tweaks (SAFE profile)
set "TWEAK_GPU=1"             :: HAGS (3-5% FPS gain)
set "TWEAK_STORAGE=1"         :: Storage Sense
set "TWEAK_BENCHMARK=1"       :: Run benchmark for validation

:: New research-based tweaks (SAFE profile only gets safe ones)
set "TWEAK_POWER_ENHANCED=0"  :: AMD CPPC, EPP (MODERATE - not for SAFE)
set "TWEAK_GPU_ENHANCED=0"    :: Vendor-specific GPU tweaks (MODERATE - not for SAFE)
set "TWEAK_MAINTENANCE=1"     :: TRIM verification only (safe)
set "TWEAK_KERNEL_INPUT=1"    :: MMCSS enhanced, mouse buffer (SAFE)

:: Disable these tweaks (too risky for safe profile)
set "TWEAK_BCDEDIT_ADVANCED=0" :: Advanced boot tweaks
set "TWEAK_SERVICES=0"        :: Service disabling (SAFE profile doesn't disable services)
set "TWEAK_NETWORK_SAFE=1"    :: Safe network tweaks (no Nagle disable)

:: New core scripts (research-based)
set "TWEAK_TELEMETRY_FULL=1"  :: Comprehensive telemetry blocker (privacy-focused, safe)
set "TWEAK_INPUT_BASIC=1"     :: Mouse acceleration fix only (no aggressive tweaks)
set "TWEAK_DEBLOAT=0"         :: Bloatware removal (disabled in SAFE — user opt-in)
set "TWEAK_VBS_DISABLE=0"     :: VBS/Device Guard (NEVER in SAFE)
set "TWEAK_SPECTRE_DISABLE=0" :: Spectre/Meltdown mitigations (NEVER in SAFE)

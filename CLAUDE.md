# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Windows PC optimization research project** with two components:

1. **Research + Batch Optimizer** - Academic research analyzing 28 Windows optimization repositories (50,000+ lines of code) to identify safe, effective tweaks versus dangerous myths, plus a production-ready modular batch script optimizer

2. **ClutchG (Python GUI)** - Modern Python/CustomTkinter GUI application that provides a user-friendly interface for managing batch optimization scripts

**Key Principle:** Safety-first, evidence-based optimization. Never compromise security for marginal performance gains.

**⚠️ CRITICAL SAFETY RULE:** This codebase contains analysis of potentially dangerous Windows optimizations. When working with this code:
- **NEVER propose or implement tweaks that disable Windows Defender, UAC, DEP, ASLR, or security features**
- **ALWAYS verify tweaks are evidence-based** (check `docs/03-tweak-taxonomy.md` and `docs/04-risk-classification.md`)
- **NEVER exaggerate performance claims** - Realistic improvement is 5-15%, not 200%
- **If you're unsure about a tweak's safety, assume it's UNSAFE** and consult the research documentation

---

## Repository Structure

### `/docs` - Research Documentation
- Research documents analyzing 28+ Windows optimization repositories
- Tweak taxonomy and risk classification
- Architecture and best practices documentation

### `/src` - Batch Optimizer Implementation
- Batch script optimizer with modular architecture
- Core modules: system detection, power management, BCDEdit, services, registry, network, GPU, storage, input, telemetry
- Enhanced modules: network-optimizer-enhanced, gpu-optimizer-enhanced, power-manager-enhanced, system-detect-enhanced
- Profile-based configurations (SAFE, COMPETITIVE, EXTREME)
- Safety systems: validation, rollback, backup, logging

### `/clutchg` - Python GUI Application

```
clutchg/
├── src/
│   ├── app_minimal.py           # Main app controller
│   ├── main.py                  # Entry point
│   ├── core/                    # Business logic
│   │   ├── config.py            # Configuration management (JSON-based)
│   │   ├── system_info.py       # Hardware detection (psutil/pywin32)
│   │   ├── profile_manager.py   # Profile management
│   │   ├── profile_recommender.py # Smart profile recommendations
│   │   ├── batch_parser.py      # Batch script parsing
│   │   ├── batch_executor.py    # Batch script execution
│   │   ├── tweak_registry.py    # Tweak database and metadata
│   │   ├── action_catalog.py    # Quick Actions static catalog (421 lines)
│   │   ├── flight_recorder.py   # Change tracking and audit trail
│   │   ├── benchmark_database.py # Performance benchmarking data
│   │   ├── help_manager.py      # Help content (bilingual: EN/TH)
│   │   └── backup_manager.py    # Backup/restore functionality
│   ├── gui/                     # UI layer
│   │   ├── theme.py             # Multi-theme system (dark/zinc/light/modern)
│   │   ├── views/               # View classes
│   │   │   ├── dashboard_minimal.py
│   │   │   ├── profiles_minimal.py
│   │   │   ├── scripts_minimal.py  # Quick Actions (default tab), Presets, Custom Builder
│   │   │   ├── restore_center_minimal.py  # Timeline-based restore UI
│   │   │   ├── backup_minimal.py
│   │   │   ├── help_minimal.py
│   │   │   ├── settings_minimal.py
│   │   │   └── welcome_overlay.py
│   │   └── components/          # Reusable UI components
│   │       ├── toast.py         # Toast notifications
│   │       ├── execution_dialog.py
│   │       ├── inline_help.py   # Help content boxes
│   │       ├── risk_badge.py    # Risk indicator component (LOW/MEDIUM/HIGH)
│   │       ├── context_help_button.py  # Contextual help button
│   │       ├── timeline.py      # Timeline visualization for restore center
│   │       ├── stat_card.py     # Compact hardware stat display (Sparkle Beta style)
│   │       ├── enhanced_toggle.py  # Modern toggle switches (QuickBoost style)
│   │       ├── refined_dialog.py    # Enhanced confirmation dialogs
│   │       ├── circular_progress.py  # Circular progress ring (240px, static)
│   │       ├── glass_card.py    # Glassmorphism cards (ProfileCard, HardwareCard)
│   │       ├── enhanced_button.py   # Modern buttons (primary/outline/ghost)
│   │       ├── enhanced_sidebar.py   # Collapsible sidebar with NavButton
│   │       ├── icon_provider.py      # Material Symbols icon management
│   │       └── tooltip.py
│   ├── data/                    # Runtime data
│   │   ├── help_content.json    # Help documentation (EN/TH)
│   │   └── risk_explanations.json # Risk level explanations for each tweak
│   ├── config/                  # Configuration files
│   │   ├── default_config.json  # Default settings
│   │   └── user_config.json     # User overrides (auto-created)
│   ├── tests/                   # Test suite
│   │   ├── conftest.py          # Pytest configuration and fixtures
│   │   ├── unit/                # Unit tests (fast, isolated)
│   │   ├── integration/         # Integration tests (business logic)
│   │   └── e2e/                 # End-to-end UI tests
│   ├── test_*.py                # Quick smoke tests
│   ├── requirements.txt         # Python dependencies
│   ├── pytest.ini               # Pytest configuration
│   └── setup_and_test.bat       # Automated setup and test script
└── docs/                        # ClutchG-specific docs
    ├── GLM-UI-V1-HANDOFF.md     # Quick Actions feature documentation
    ├── GLM-UI-V1-TEST-MATRIX.md # Test scenarios for Quick Actions
    ├── GLM-UI-V1-CHANGELOG.md   # Implementation changelog
    ├── clutchg_technical_spec.md
    └── clutchg_quick_reference.md
```

### `/windows-optimizer-research` - Raw Research Data
- `repos/` - All 28 cloned repositories
- `analysis/` - Space for extracted tweak databases
- `taxonomy/` - Space for cross-repo comparisons

---

## Running the Applications

### Batch Optimizer (CLI)

```batch
cd src
optimizer.bat  # Must run as Administrator
```

**Requirements:**
- Windows 10 22H2+ (Build 19045) or Windows 11 23H2+ (Build 22631+)
- Administrator privileges

### ClutchG (Python GUI)

#### Quick Start (Automated Setup)
```batch
cd clutchg
setup_and_test.bat  # Install deps, test, and launch
```

#### Manual Setup
```bash
# Install dependencies
cd clutchg
pip install -r requirements.txt

# Run the GUI (requires Administrator)
cd src
python app_minimal.py
# OR
python main.py
```

**Dependencies:**
- Python 3.11+
- customtkinter>=5.2.0
- Pillow>=10.0.0
- psutil>=5.9.0
- pywin32>=306

---

## Testing ClutchG

### Running All Tests
```bash
cd clutchg
pytest
```

### Running Specific Test Categories
```bash
# Unit tests only (fast, no external dependencies)
pytest -m unit

# Integration tests (business logic workflows)
pytest -m integration

# End-to-end UI tests (full application)
pytest -m e2e

# Skip slow tests (>10 seconds)
pytest --skip-slow

# Skip E2E tests
pytest --skip-e2e
```

### Running with Coverage
```bash
# Generate terminal and HTML coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html

# View HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### Test Markers
Tests are categorized using pytest markers:
- `unit` - Fast, isolated unit tests
- `integration` - Business logic workflow tests
- `e2e` - Full UI automation tests
- `slow` - Tests taking >10 seconds
- `admin` - Tests requiring administrator privileges
- `requires_network` - Tests requiring network access

### Quick Smoke Tests
```bash
cd clutchg/src
python test_imports.py      # Test module imports
python test_app_init.py      # Test app initialization
```

### Automated Testing Script
The `setup_and_test.bat` script handles:
1. Python version check
2. Dependency installation
3. Import testing
4. App initialization testing
5. Launching the application

---

## ClutchG Configuration

### Config Directory Structure

```
clutchg/config/
├── default_config.json    # Default settings (version-controlled)
└── user_config.json       # User overrides (auto-created, git-ignored)
```

### Configuration Management

**ConfigManager** (`core/config.py`) provides:
- JSON-based config persistence
- Default value loading
- User override support
- Config validation
- Thread-safe access

### Key Config Settings

```json
{
  "version": "1.0.0",
  "language": "en",
  "theme": "dark",
  "auto_backup": true,
  "confirm_actions": true,
  "log_level": "INFO",
  "batch_scripts_dir": "../src",
  "backup_dir": "./data/backups",
  "max_backups": 10,
  "default_profile": "SAFE",
  "window_size": {
    "width": 1200,
    "height": 700
  },
  "startup_checks": {
    "check_admin": true,
    "detect_system": true,
    "verify_scripts": true
  }
}
```

### Modifying Configuration

1. **Add new setting:**
   - Add default to `config/default_config.json`
   - Add validation in `core/config.py` if needed
   - Access via `app.config["key"]`

2. **Add settings UI:**
   - Edit `gui/views/settings_minimal.py`
   - Use `ConfigManager.save_config()` to persist

---

## Architecture Overview

### Optimizer Design Philosophy

The optimizer uses a **profile-based approach** with three tiers:
1. **SAFE** - Conservative, proven tweaks only (minimal risk)
2. **COMPETITIVE** - Balanced performance vs safety (low risk)
3. **EXTREME** - Aggressive optimizations (medium risk, advanced users only)

**Why Batch Scripts?**
- Universal executability (no dependencies)
- Full transparency (users can read every command)
- No false-positive antivirus flags
- No compilation required

### Module Architecture

```
optimizer.bat (main entry point)
│
├── core/ (functional modules)
│   ├── system-detect.bat / system-detect-enhanced.bat
│   ├── power-manager.bat / power-manager-enhanced.bat
│   ├── bcdedit-manager.bat
│   ├── service-manager.bat
│   ├── registry-utils.bat
│   ├── network-manager.bat / network-optimizer-enhanced.bat
│   ├── gpu-optimizer.bat / gpu-optimizer-enhanced.bat
│   ├── storage-optimizer.bat
│   ├── input-optimizer.bat
│   ├── telemetry-blocker.bat
│   ├── debloater.bat
│   └── maintenance-manager.bat
│
├── profiles/ (tweak configurations)
│   ├── safe-profile.bat
│   ├── competitive-profile.bat
│   └── extreme-profile.bat
│
├── safety/ (validation and rollback)
│   ├── validator.bat        - Admin check, system validation
│   └── rollback.bat         - Revert all changes
│
├── backup/ (backup systems)
│   ├── backup-registry.bat  - Registry export before changes
│   └── restore-point.bat    - System restore point creation
│
└── logging/
    └── logger.bat           - Change audit trail
```

### Data Flow

```
User Selection → System Detection → Backup Creation → Conflict Check
                                                ↓
Tweak Execution (sequential with validation) → Logging → Summary Report
```

### ClutchG Application Architecture

ClutchG uses a **view-based architecture** with CustomTkinter:

**Main Controller (`app_minimal.py`):**
- `ClutchGApp` class manages the application lifecycle
- `switch_view(view_name)` handles navigation between views
- `refresh_current_view()` rebuilds current view (used for language changes)
- Creates sidebar navigation with icon-based `NavButton` widgets

**View Pattern:**
- Each view is a `ctk.CTkFrame` subclass in `gui/views/`
- Views receive `parent` frame and `app` reference on init
- Views implement `refresh_language()` for i18n support
- Common pattern: `_ui(key)` and `_font(size, weight)` helper methods

**Internationalization (i18n):**
- Language stored in `app.config["language"]` ("en" or "th")
- Views define `UI_STRINGS` dict with EN/TH translations
- `_font()` switches between "Inter" (EN) and "Tahoma" (TH)
- `HelpManager` loads language-specific help content from JSON

**Key Managers:**
- `ConfigManager` - JSON-based config persistence
- `SystemDetector` - Hardware detection using `psutil`
- `ProfileManager` - Loads and applies optimization profiles
- `ProfileRecommender` - Analyzes hardware to recommend best profile
- `BatchParser` - Parses batch scripts to extract tweak metadata
- `BatchExecutor` - Executes batch scripts with error handling
- `TweakRegistry` - Central database of all tweaks with risk levels
- `FlightRecorder` - Tracks all system changes for audit trail and rollback
- `HelpManager` - Bilingual help content management
- `ToastManager` - Non-blocking notifications

**Data Flow:**
```
User Action → View → Core Manager → Config/System Change → View Refresh
```

**Risk-Based UI System:**
- All tweaks labeled LOW/MEDIUM/HIGH risk via `TweakRegistry`
- `risk_badge.py` component displays risk with icons (🛡️ LOW, ⚠️ MEDIUM, 🔥 HIGH)
- `risk_explanations.json` provides detailed risk information per tweak
- Views show 4px colored border strips indicating risk level (green/yellow/red)

**FlightRecorder Pattern:**
- All system changes tracked before execution
- Records: timestamp, tweak name, before/after values, result status
- Enables Restore Center's timeline visualization
- Per-tweak rollback capability via stored change history

**Theme System:**
- Multi-theme support: `dark`, `zinc`, `light`, `modern` (Tokyo Night-inspired)
- Default theme: `modern` with Tokyo Night colors
- Accent presets: `tokyo_blue` (default), `tokyo_purple`, `white`, `zinc`, `blue`, etc.
- Theme manager provides color caching and runtime theme switching
- All components use `theme_manager.get_colors()` for dynamic theming

**UI Component Library:**
- **StatCard** - Compact hardware stats (60px height, icon+value+label layout)
- **EnhancedToggle** - Modern toggle switches (44x24px, green=on/gray=off)
- **RefinedDialog** - Enhanced confirmation dialogs with drop shadows
- **CircularProgress** - Progress ring (240px default, static rendering)
- **GlassCard** - Glassmorphism cards (ProfileCard, HardwareCard)
- **EnhancedButton** - Modern buttons (primary/outline/ghost variants)
- **EnhancedSidebar** - Collapsible sidebar with icon-based navigation
- **RiskBadge** - Risk level indicators with icons

**Quick Actions Feature (V1):**
- Located in `Optimization Center` as the **default tab**
- Static catalog in `core/action_catalog.py` (421 lines, 11 actions)
- Five groups: General, Advanced, Cleanup, Windows, Utilities
- Safety validation: HIGH-risk tweaks excluded, NVIDIA-aware filtering
- Confirmation dialogs always shown before execution
- Dashboard integration via Action Hub card

**Icon System:**
- Primary: Material Symbols Outlined (Google)
- Fallback: Segoe MDL2 Assets (Windows)
- Managed by `icon_provider.py`
- Access via `ICON("icon_name")` or `ICON_FONT()`

---

## Key Files by Task

### Batch Optimizer Tasks

**Available core modules:**
- `system-detect.bat` / `system-detect-enhanced.bat` - OS version, CPU/GPU detection
- `power-manager.bat` / `power-manager-enhanced.bat` - Power plan operations
- `bcdedit-manager.bat` - Boot configuration tweaks
- `service-manager.bat` - Service control
- `registry-utils.bat` - Registry operations
- `network-manager.bat` / `network-optimizer-enhanced.bat` - Network optimization
- `gpu-optimizer.bat` / `gpu-optimizer-enhanced.bat` - GPU driver optimizations
- `storage-optimizer.bat` - Storage and filesystem optimizations
- `input-optimizer.bat` - Mouse/keyboard input latency
- `telemetry-blocker.bat` - Disable telemetry safely
- `debloater.bat` - Remove Windows bloatware
- `maintenance-manager.bat` - System maintenance tasks

**Add new tweak category:**
- Create `src/core/[category]-manager.bat` or `[category]-enhanced.bat`
- Implement tweak logic with error handling pattern
- Add to `src/profiles/[profile].bat` where appropriate
- Add detection logic to `system-detect.bat` if hardware-specific

**Modify profile behavior:**
- `src/profiles/[profile].bat` - Edit profile configuration

**Change safety/validation:**
- `src/safety/validator.bat` - Add validation checks
- `src/safety/rollback.bat` - Add rollback logic

**Add logging:**
- Use `call "%LOGGING_DIR%\logger.bat" :log_tweak "Name" "STATUS"`

### ClutchG Tasks

**Add new view:**
- Create `src/gui/views/[name]_minimal.py`
- Add to `switch_view()` in `src/app_minimal.py`
- Follow view pattern with `_ui()`, `_font()`, `refresh_language()`

**Add new Quick Action:**
- Edit `src/core/action_catalog.py` to add action definition
- Specify: id, title, description, kind (tweak_pack/external_link), group, risk_level
- For tweak_packs: Add list of tweak_ids (must exist in tweak_registry.py)
- For external_links: Add url (must be in TRUSTED_DOMAINS whitelist)
- Add helper text for user guidance
- Validation runs automatically on app startup

**Add to restore center:**
- Changes tracked automatically via `FlightRecorder`
- Restore Center (`restore_center_minimal.py`) displays timeline of all operations
- Use timeline component (`gui/components/timeline.py`) for visualization
- Per-tweak restore via stored before/after values

**Add new settings:**
- Add default to `config/default_config.json`
- Edit `src/core/config.py` for validation if needed
- Add UI in `src/gui/views/settings_minimal.py`

**Add help content:**
- Edit `src/data/help_content.json` (add EN and TH content)
- Handle in `src/core/help_manager.py`

**Add tweak to registry:**
- Update `src/core/tweak_registry.py` with tweak metadata
- Add risk level (LOW/MEDIUM/HIGH), description, and technical details
- Register with appropriate profile(s)

**Add to flight recorder:**
- Call `flight_recorder.record_change()` before executing system modifications
- Pass: tweak name, before_value, after_value, status

**Add to batch parser:**
- Extend `batch_parser.py` to recognize new script patterns
- Extract metadata: description, risk level, category

**Modify theme:**
- Edit `src/gui/theme.py` (COLORS, SIZES constants)
- Themes: `dark`, `zinc`, `light`, `modern`
- Accents: `tokyo_blue`, `tokyo_purple`, `white`, `zinc`, etc.

**Use UI Components:**
- **StatCard**: Display hardware stats compactly
  ```python
  from gui.components.stat_card import StatCard
  StatCard(parent, icon="🖥️", value="8", label="CPU Cores")
  ```
- **EnhancedToggle**: Replace CTkSwitch/CTkCheckBox
  ```python
  from gui.components.enhanced_toggle import EnhancedToggle
  EnhancedToggle(parent, text="Enable", state=True, command=lambda v: handle_toggle(v))
  ```
- **RefinedDialog**: Replace tkinter.messagebox
  ```python
  from gui.components.refined_dialog import show_confirmation
  confirmed = show_confirmation(parent, "Confirm Action", "Are you sure?", risk_level="MEDIUM")
  ```
- **GlassCard**: Create glassmorphism cards
  ```python
  from gui.components.glass_card import GlassCard
  card = GlassCard(parent, corner_radius=12, padding=20)
  ```

**Add/rename UI strings:**
- Update `UI_STRINGS` dict in relevant view
- Ensure both "en" and "th" translations exist

### Testing Tasks

**Add unit test:**
- Create `tests/unit/test_[feature].py`
- Use fixtures from `tests/conftest.py`
- Mark with `@pytest.mark.unit`

**Add integration test:**
- Create `tests/integration/test_[workflow].py`
- Test business logic workflows
- Mark with `@pytest.mark.integration`

**Add E2E test:**
- Create `tests/e2e/tests/test_[feature].py`
- Test full UI interactions
- Mark with `@pytest.mark.e2e`

**Modify test fixtures:**
- Edit `tests/conftest.py` for shared fixtures
- Available fixtures: `project_root`, `src_dir`, `test_config_dir`, `app_path`, `temp_output_dir`, `screenshot_dir`, `log_dir`, `test_timestamp`, `require_admin`, `test_config`
- Add custom command line options via `pytest_addoption()` in conftest.py
- `screenshot_on_failure` hook automatically captures screenshots on test failure for E2E tests

---

## Module Interaction Patterns

### Calling Convention

All modules use **label-based calling** with `call`:

```batch
call "%CORE_DIR%\system-detect.bat" :detect_all
call "%LOGGING_DIR%\logger.bat" :log "Message"
call "%CORE_DIR%\power-manager.bat" :enable_ultimate_performance
```

### Variable Sharing

Core modules export variables for use by other modules:
- `OS_VERSION` - "10" or "11"
- `OS_BUILD` - Build number (e.g., "22621")
- `CPU_VENDOR` - "Intel", "AMD", or "Unknown"
- `CPU_CORES`, `CPU_THREADS` - Core and thread counts
- `GPU_NAME` - Primary GPU model

### Error Handling Pattern

```batch
command_here
if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log_tweak "TweakName" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call "%LOGGING_DIR%\logger.bat" :log_tweak "TweakName" "FAILED"
    set /a TWEAK_FAILED+=1
)
```

### ClutchG View Pattern

**Creating a New View:**

```python
# gui/views/myview_minimal.py
import customtkinter as ctk
from typing import TYPE_CHECKING
from gui.theme import COLORS, SIZES

if TYPE_CHECKING:
    from app_minimal import ClutchGApp

class MyView(ctk.CTkFrame):
    """My custom view"""

    UI_STRINGS = {
        "en": {"title": "My View", "description": "..."},
        "th": {"title": "มุมมองของฉัน", "description": "..."},
    }

    def __init__(self, parent, app: 'ClutchGApp'):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        # Build UI...
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _font(self, size: int, weight: str = "normal") -> ctk.CTkFont:
        family = "Tahoma" if self.app.config.get("language") == "th" else "Inter"
        return ctk.CTkFont(family=family, size=size, weight=weight)

    def _ui(self, key: str) -> str:
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)

    def refresh_language(self):
        """Rebuild UI with new language"""
        for widget in self.winfo_children():
            widget.destroy()
        # Rebuild UI...
```

**Adding View to Navigation:**

```python
# app_minimal.py - in switch_view()
elif view_name == "myview":
    from gui.views.myview_minimal import MyView
    self.current_view = MyView(self.main_frame, self)
```

**CustomTkinter Constraints:**
- `bind_all()` not allowed on widgets - use root window or individual widget `bind()`
- Always use `self.grid_rowconfigure()` and `self.grid_columnconfigure()` for responsive layouts
- Theme colors accessed via `COLORS["key"]` dict

---

## Critical Safety Rules

### NEVER Do These (Based on Research)

The analysis of 28 repositories identified these dangerous practices:

1. **Disable Windows Defender** - Leaves system unprotected
2. **Disable Windows Update permanently** - Misses critical security patches
3. **Disable DEP/ASLR/CFG** - Removes exploit protections
4. **Delete system files** - Irreversible damage
5. **Disable UAC** - Allows silent malware elevation
6. **Modify registry ACLs** - Locks Windows out of its own settings

### Always Do These

1. **Create backups before changes** - Automatic in `backup/` modules
2. **Log every modification** - Use `logger.bat :log_tweak`
3. **Validate before applying** - Check system type, OS version, hardware
4. **Provide rollback** - Every change should be reversible
5. **Document risks** - Warn users about potential side effects

### Quick Actions Safety Rules

**Quick Actions intentionally EXCLUDES these HIGH-risk security tweaks:**
- `pwr_spectre` - Spectre/Meltdown mitigations
- `gpu_vbs` - Virtualization-Based Security
- `bcd_hypervisor` - Hypervisor enforcement

These remain available in **Custom Builder** for advanced users who understand the risks.

**Quick Actions validation runs on app startup:**
- All tweak IDs must exist in `tweak_registry.py`
- No HIGH-risk tweaks allowed
- External URLs must be in trusted domain whitelist
- NVIDIA-only actions hidden on non-NVIDIA systems

**Trusted domains for external links:**
- discord.com, 7-zip.org, learn.microsoft.com
- techpowerup.com, steampowered.com, github.com

---

## Research-Based Insights

### What Actually Works (Evidence-Based)

From analysis of 28 repositories:

1. **GPU Driver Settings** - 2-15% FPS improvement (vendor-specific)
2. **Power Plan Optimization** - 2-5% improvement (Ultimate Performance plan)
3. **Safe BCDEdit Tweaks** - 1-4% improvement (timer, tick settings)
4. **Background App Reduction** - 1-3% improvement (GameDVR disable)

### Common Myths Debunked

1. **"Windows reserves 20% bandwidth for QoS"** - FALSE (only affects tagged traffic)
2. **"Timer resolution services boost FPS"** - OBSOLETE (per-process since Win10 2004)
3. **"Disabling 100 services = faster"** - RISKY (breaks functionality)
4. **"Network registry tweaks reduce ping"** - PLACEBO (minimal real impact)

### Tool Quality Reality

**Alarming Finding:** 60.7% of repositories analyzed received a failing grade (F).

**Only Safe for General Use:**
- **WinUtil** (9.5/10) - Gold standard, safety-first
- **BCDEditTweaks** (9.0/10) - Best boot optimization

**Avoid Completely:**
- Windows (TairikuOokami) - Creates backdoors, author warns against use
- EchoX - Deprecated, removes security protections
- Ancels-Performance-Batch - Creates vulnerabilities
- Unlimited-PC-Tips - Deletes Windows Start Menu

See `docs/10-complete-repo-ranking.md` for complete analysis.

---

## Development Workflow

### Adding a New Batch Tweak

1. **Research the tweak** - Verify it's evidence-based, not a myth
2. **Assess risk** - Use docs/04-risk-classification.md as reference
3. **Add to appropriate core module** - Implement with error handling
4. **Add to profile(s)** - Include in profiles where appropriate
5. **Add logging** - Use `:log_tweak` for audit trail
6. **Test thoroughly** - Verify on Windows 10 and Windows 11

### Adding a New ClutchG Feature

1. **Design the feature** - Consider UI/UX, i18n, accessibility
2. **Create/update view** - Follow view pattern, add translations
3. **Update core managers** - Add business logic to appropriate manager
4. **Add configuration** - Update default_config.json if needed
5. **Add tests** - Unit tests for logic, integration for workflows, E2E for UI
6. **Test thoroughly** - Both languages, both themes, all views
7. **Update documentation** - Add help content if user-facing

### Example: Adding a Registry Tweak

```batch
:: In core/registry-utils.bat

:enable_some_feature
reg add "HKLM\SOFTWARE\Path\To\Key" /v ValueName /t REG_DWORD /d 1 /f >nul 2>&1
if %ERRORLEVEL%==0 (
    call "%LOGGING_DIR%\logger.bat" :log_tweak "Enable SomeFeature" "SUCCESS"
    set /a TWEAK_SUCCESS+=1
) else (
    call "%LOGGING_DIR%\logger.bat" :log_tweak "Enable SomeFeature" "FAILED"
    set /a TWEAK_FAILED+=1
)
goto :eof
```

### Testing Changes

**Batch Optimizer:**
1. Create System Restore point manually
2. Run optimizer with test profile
3. Check logs in `src/logs/optimizer_*.log`
4. Verify changes took effect
5. Test rollback functionality

**ClutchG:**
1. Run unit tests: `pytest -m unit`
2. Run integration tests: `pytest -m integration`
3. Run E2E tests: `pytest -m e2e`
4. Test language switching (EN ↔ TH)
5. Verify theme toggle (dark ↔ light)
6. Check all views load without errors
7. Test navigation between views
8. Verify system detection accuracy

---

## Documentation Conventions

### Repository Analysis Format

When analyzing a new repository (in `docs/02-repo-analysis/`), follow this structure:

```markdown
# [Repository Name] Analysis

> **Repository:** [URL]
> **Primary Focus:** [Gaming/Latency/etc]
> **Platform:** Windows 10/11
> **Language:** [Batch/PowerShell/Mixed]

## Overview
[2-3 sentences about purpose and philosophy]

## Tweak Categories
[Organize by type: Registry, Services, Network, etc.]

## Dangerous Commands
[List any DANGEROUS or risky commands with explanations]

## Overall Assessment
- **Engineering Quality:** X/10
- **Safety Focus:** X/10
- **Recommendation:** USE / CAUTION / AVOID
```

### Risk Assessment Labels

Use these consistently:
- **SAFE** - Reversible, no system impact
- **MODERATE** - May affect functionality, test before deploying
- **DANGEROUS** - Can cause instability, expert-only
- **CRITICAL** - May render system unbootable, never use

---

## Important Constraints

### Windows Version Compatibility

- **Minimum:** Windows 10 22H2 (Build 19045)
- **Primary Target:** Windows 11 23H2+ (Build 22631+)
- **Always detect OS version** before applying version-specific tweaks

### Hardware Detection

Before applying hardware-specific tweaks:
```batch
call "%CORE_DIR%\system-detect.bat" :detect_all

:: Example: NVIDIA-specific optimizations
if "%GPU_VENDOR%"=="NVIDIA" (
    call "%CORE_DIR%\power-manager.bat" :nvidia_optimizations
) else (
    call "%LOGGING_DIR%\logger.bat" :log "Skipped NVIDIA tweaks (not detected)"
)
```

---

## Logging and Audit Trail

### Batch Optimizer Logging

All changes are logged to `src/logs/optimizer_[timestamp].log` with:
- Start/end timestamp
- Computer name and user
- Individual tweak results (SUCCESS/FAILED/SKIPPED)
- Summary statistics

**Review logs after every run** to verify changes applied correctly.

### ClutchG Logging

Configurable log levels via `app.config["log_level"]`:
- DEBUG - Detailed debugging information
- INFO - General informational messages
- WARNING - Warning messages for potential issues
- ERROR - Error messages for failures

---

## Rollback Process

If something goes wrong:

### Batch Optimizer Rollback

1. **Immediate Rollback:**
   ```batch
   cd src
   optimizer.bat
   # Select option [6] Restore from Backup
   ```

2. **Manual Registry Restore:**
   ```batch
   reg import "src\backups\registry_[timestamp].reg"
   ```

3. **System Restore:**
   - Windows creates restore point automatically
   - Use System Restore if all else fails

### ClutchG Rollback

1. **Restore from Backup:**
   - Use Backup view to restore registry backups
   - Backups stored in `clutchg/data/backups/`

2. **Config Reset:**
   - Delete `config/user_config.json` to reset to defaults
   - App will recreate with defaults on next launch

---

## Troubleshooting Common Issues

### ClutchG Issues

**Language switch not working:**
- Ensure views implement `refresh_language()` method
- Check `app.refresh_current_view()` is called after language change
- Verify `UI_STRINGS` dict has both "en" and "th" keys

**CustomTkinter `bind_all` error:**
- `bind_all()` not allowed on widgets in CustomTkinter
- Use individual widget `bind()` instead
- Or bind to root window: `self.app.window.bind_all()`

**Missing module error:**
- Run `pip install -r requirements.txt` from `clutchg/` directory
- Ensure Python 3.11+ is installed

**Config not persisting:**
- Check write permissions on `config/` directory
- Verify `ConfigManager.save_config()` is being called
- Check for JSON syntax errors in config files

### Batch Optimizer Issues

**Access denied errors:**
- Must run as Administrator
- Right-click → "Run as administrator"

**Script not found:**
- Ensure you're running from correct directory
- Check batch_scripts_dir path in ClutchG config

**Changes not applying:**
- Check logs for error messages
- Verify OS version compatibility
- Ensure system meets hardware requirements

---

## Key Documents for Reference

### Batch Optimizer Research
When working with this codebase, always reference:

- **`docs/03-tweak-taxonomy.md`** - Understand what tweaks actually do
- **`docs/04-risk-classification.md`** - Assess risk before implementing
- **`docs/07-best-practices.md`** - Follow safety guidelines
- **`docs/09-final-architecture.md`** - Understand system design
- **`docs/10-complete-repo-ranking.md`** - Learn from others' mistakes

### ClutchG Technical Documentation
- **`docs/clutchg_technical_spec.md`** - Complete technical specification for ClutchG
- **`clutchg/README.md`** - ClutchG project overview
- **`clutchg/docs/clutchg_quick_reference.md`** - Quick reference guide
- **`docs/GLM-UI-V1-HANDOFF.md`** - Quick Actions V1 feature documentation (Feb 2026)
- **`docs/GLM-UI-V1-TEST-MATRIX.md`** - Test scenarios for Quick Actions (30+ cases)
- **`docs/GLM-UI-V1-CHANGELOG.md`** - Implementation changelog for Quick Actions

### Research Data Location

All raw repository clones are in `windows-optimizer-research/repos/`. When referencing specific repositories in documentation or code:

```batch
:: Example reference
:: Based on analysis of: github.com/dubbyOW/BCDEditTweaks
:: See: docs/02-repo-analysis/bcdedit-tweaks.md
```

This maintains traceability back to original research.

---

## Ethical Guidelines

This project is built on **honest, evidence-based optimization**:

1. **Never exaggerate claims** - Realistic improvement is 5-15%, not 200%
2. **Never compromise security** - No disabling Defender, DEP, or protections
3. **Always provide warnings** - Users must understand risks
4. **Always enable rollback** - Every change must be reversible
5. **Document everything** - Transparency builds trust

If you're tempted to add a "dangerous but effective" tweak, **don't**. The research proves that safety-focused tools (WinUtil) are superior to aggressive ones.

---

## Development Commands Reference

```bash
# Batch Optimizer
cd src
optimizer.bat                    # Run optimizer

# ClutchG - Setup
cd clutchg
pip install -r requirements.txt   # Install deps
setup_and_test.bat               # Automated setup and test

# ClutchG - Run
cd src
python app_minimal.py             # Run GUI (main controller)
python main.py                    # Run GUI (alternative entry point)

# ClutchG - Testing
pytest                            # Run all tests
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m e2e                     # E2E tests only
pytest --skip-slow                # Skip slow tests
pytest --cov=src                  # Run with coverage

# ClutchG - Quick Tests
cd clutchg/src
python test_imports.py            # Test module imports
python test_app_init.py           # Test app initialization
```

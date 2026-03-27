# Repository Guidelines

## Purpose
- `src/`: Windows batch optimizer scripts.
- `clutchg/`: Python GUI app that discovers, validates, and runs those scripts.
- `windows-optimizer-research/`: Reference material only (not editable product code).
- `docs/`: Design, architecture, and implementation notes for risky behavior changes.

## Project Structure
**Batch (`src/`):**
- `optimizer.bat` - entry point
- `core/` - power, services, registry, network, GPU, storage, maintenance modules
- `profiles/` - `safe-profile.bat`, `competitive-profile.bat`, `extreme-profile.bat`
- `safety/` - admin validation, rollback, flight-recorder
- `backup/` - restore point and registry backup helpers
- `logging/logger.bat` - batch-side logging

**Python GUI (`clutchg/`):**
- `src/main.py` - launcher
- `src/core/` - non-UI business logic (batch_parser, action_catalog, profile_manager, etc.)
- `src/gui/` - views, widgets, theme, UI composition
- `src/utils/` - shared helpers (logger, admin checks)
- `tests/` - `unit/`, `integration/`, `e2e/` with page objects in `tests/e2e/pages/`

**Other:**
- `scripts/` - standalone Python tooling for Notion/document import

## Setup Commands
```bash
python -m venv venv
venv\Scripts\activate
pip install -r clutchg\requirements.txt        # GUI runtime deps
pip install -r clutchg\requirements-test.txt   # Test deps (pytest, pywinauto)
pip install -r scripts\requirements.txt        # Document tools (when working in scripts/)
```

## Run Commands
```bash
src\optimizer.bat                    # Batch optimizer directly
python clutchg\src\main.py           # GUI from repo root
python src\main.py                   # GUI from inside clutchg/
python src\main.py --test-mode       # GUI in test-friendly mode
python test_core.py                  # Legacy ad-hoc core smoke test
```

## Build Commands
```bash
cd clutchg && python build.py        # Builds to clutchg\dist\ClutchG.exe
```
`build.py` auto-installs PyInstaller if missing. Output includes batch scripts copied to `dist\batch_scripts\`.

## Test Commands
Pytest config: `clutchg\pytest.ini`. Coverage config: `clutchg\.coveragerc`.

```bash
cd clutchg
pytest                                    # Full suite with coverage
pytest --cov=src tests/                   # Explicit coverage
pytest tests\unit -m unit                  # Unit tests only
pytest tests\integration -m integration    # Integration tests only
pytest tests\e2e -m e2e --app-path src\main.py  # E2E tests
pytest --skip-slow                        # Skip slow tests
pytest --skip-e2e                         # Skip E2E tests
pytest -n auto                            # Parallel execution (pytest-xdist)

# Run a single test file
pytest tests\unit\test_action_catalog.py -v

# Run tests matching a pattern
pytest tests\unit\test_action_catalog.py -k test_risk_aggregation -v

# Run a single test node
pytest tests\unit\test_action_catalog.py::TestActionCatalog::test_risk_aggregation_for_memory_pack -v
```

HTML coverage output: `clutchg\htmlcov\`.

## Lint And Validation
No repo-managed lint configuration for Ruff, Black, Flake8, isort, Pylint, or mypy. Match surrounding style instead.

When asked to "lint," use project-native checks:
```bash
pytest                                    # Primary validation
python -m compileall clutchg\src          # Python syntax sanity
python test_core.py                       # Runtime smoke test
```
Batch scripts: validate by reading call flow; test on Windows with admin rights when safe.

## Python Style Guidelines
- PEP 8 with 4-space indentation.
- Triple-quoted docstrings for modules, classes, and public functions.
- Type hints on public functions, methods, fixtures, and dataclass fields.
- Use `from __future__ import annotations` at top of modules with complex types.
- Prefer `Path` over raw string path concatenation.
- Prefer dataclasses and enums for structured data.

**Imports:**
```python
from pathlib import Path
from typing import List, Dict, Optional

from core.batch_parser import BatchParser    # Absolute imports from clutchg/src
from utils.logger import get_logger
```
Order: standard library, third-party, local modules. One import per line.

**Naming:**
- `snake_case` for functions, methods, variables, filenames
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants and enum-like identifiers
- Preserve domain naming where values are intentionally uppercase (`SAFE`, `COMPETITIVE`, `EXTREME`)

**JSON:** Use `indent=2` for human readability unless file uses another format.

## Python Error Handling
```python
logger = get_logger(__name__)

# Prefer specific exceptions
try:
    result = risky_operation()
except FileNotFoundError:
    logger.error("Config not found")
    return None

# Return None/False/structured result for expected failures
# Raise only when caller should handle

# Silent except only for cleanup/teardown
```
For Windows subprocess: capture output when diagnosis matters; include timeouts.

## Testing Conventions
- Fixtures and CLI flags in `clutchg\tests\conftest.py`.
- Markers: `unit`, `integration`, `e2e`, `slow`, `admin`, `requires_network`.
- Keep unit tests isolated; use `tmp_path`, temp dirs, mocks.
- Mark Windows/admin-sensitive tests explicitly.
- E2E tests use page objects in `tests\e2e\pages\`.

## Batch Script Style Guidelines
```batch
@echo off
setlocal EnableDelayedExpansion

set "VAR=value"          # Quote assignments
"%VAR%"                  # Quote usage

call "file.bat" :label   # Label dispatch
goto :eof
```
- Filenames: kebab-case (`system-detect.bat`).
- Uppercase env vars for shared state.
- Section banners: `:: =====`.
- Log via `src\logging\logger.bat`.
- Always check admin rights before privileged operations.

## Safety Rules
- Never disable Windows Defender, UAC, DEP, ASLR, CFG, or Windows Update.
- No placebo tweaks without documented technical justification.
- Prefer evidence-based, reversible changes with visible logging.
- Validate OS/hardware compatibility before version/vendor-specific changes.
- Document risk and rollback impact for BCDEdit, services, registry, restore points.

## Change Strategy For Agents
- Keep GUI code in `clutchg/src/gui/`, non-UI logic in `clutchg/src/core/`.
- Don't mix UI rendering with execution/business logic.
- Edit tests: smallest suite first, broaden if needed.
- Edit batch scripts: inspect all callers and called labels before renaming.
- Keep research artifacts and production code separate.
- Prefer small, reviewable changes over broad refactors.

## Verification Expectations
- Python changes: run narrowest meaningful pytest command first (single file or test).
- Shared logic changes: follow with marker group or full `pytest` run.
- GUI-only changes: note if verification limited by desktop/admin constraints.
- Batch changes: provide manual verification steps if cannot safely execute.

## Commit Guidance
Use concise imperative messages: `Add backup validation before profile apply`.

Include in PR descriptions when relevant:
- Risk level
- Affected modules
- Manual verification notes

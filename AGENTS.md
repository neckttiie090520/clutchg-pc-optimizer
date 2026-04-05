# Repository Guidelines

## Purpose
- `src/`: Windows batch optimizer scripts.
- `clutchg/`: Python GUI app (CustomTkinter) that discovers, validates, and runs those scripts.
- `windows-optimizer-research/`: Reference material only — not editable product code.
- `docs/`: Design, architecture, and implementation notes.
- `scripts/`: Standalone Python tooling for document import.

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
- `src/core/` - non-UI business logic (batch_parser, action_catalog, profile_manager, help_manager, etc.)
- `src/gui/` - views (minimal.py), components, theme, icons, style
- `src/data/` - JSON content files (help_content.json, risk_explanations.json)
- `src/utils/` - shared helpers (logger, admin checks)
- `tests/` - `unit/`, `integration/`, `e2e/` with page objects in `tests/e2e/pages/`

## Setup
```bash
python -m venv venv
venv\Scripts\activate
pip install -r clutchg\requirements.txt        # GUI runtime deps
pip install -r clutchg\requirements-test.txt   # Test deps (pytest, pywinauto)
```

## Run & Build
```bash
python clutchg\src\main.py              # GUI from repo root
python clutchg\src\main.py --test-mode  # GUI in test-friendly mode
cd clutchg && python build.py           # Builds to clutchg\dist\ClutchG.exe
```

## Test Commands
Pytest config: `clutchg\pytest.ini`. Coverage config: `clutchg\.coveragerc`. All test commands run from inside `clutchg/`.

```bash
pytest                                              # Full suite with coverage
pytest tests\unit -m unit                            # Unit tests only
pytest tests\integration -m integration              # Integration tests only
pytest tests\e2e -m e2e --app-path src\main.py       # E2E tests
pytest --skip-slow --skip-e2e                        # Skip slow/e2e tests
pytest -n auto                                      # Parallel (pytest-xdist)

# Single test file
pytest tests\unit\test_action_catalog.py -v

# Pattern match
pytest tests\unit\test_action_catalog.py -k test_risk_aggregation -v

# Single test node
pytest tests\unit\test_action_catalog.py::TestActionCatalog::test_risk_aggregation_for_memory_pack -v
```

HTML coverage output: `clutchg\htmlcov\`.

## Lint & Validation
No Ruff, Black, Flake8, isort, Pylint, or mypy config. Match surrounding style.

```bash
pytest                                    # Primary validation
python -m compileall clutchg/src          # Python syntax sanity
```

Batch scripts: validate by reading call flow; test on Windows with admin rights.

## Python Style
- PEP 8, 4-space indent. No inline comments unless requested.
- Triple-quoted docstrings for modules, classes, and public functions.
- Type hints on public functions, methods, fixtures, and dataclass fields.
- Use `from __future__ import annotations` in modules with complex types.
- Prefer `Path` over raw string concatenation.
- Prefer dataclasses and enums for structured data.

**Imports:**
```python
from pathlib import Path
from typing import List, Dict, Optional

from core.batch_parser import BatchParser    # Absolute imports from clutchg/src
from utils.logger import get_logger
```
Order: stdlib → third-party → local. One import per line.

**Naming:** `snake_case` (functions/vars/files), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants/enum values). Preserve domain naming where intentionally uppercase (`SAFE`, `COMPETITIVE`, `EXTREME`).

**JSON:** `indent=2` unless file uses another format.

**Error Handling:**
```python
logger = get_logger(__name__)
# Specific exceptions. Return None/False for expected failures.
# Raise only when caller should handle. Silent except only for cleanup.
```

## Testing Conventions
- Fixtures and CLI flags in `clutchg\tests\conftest.py`.
- Markers: `unit`, `integration`, `e2e`, `slow`, `admin`, `requires_network`.
- Unit tests: isolated with `tmp_path`, temp dirs, mocks.
- E2E tests use page objects in `tests\e2e\pages\`.

## Batch Script Style
```batch
@echo off
setlocal EnableDelayedExpansion
set "VAR=value"          # Quote assignments
"%VAR%"                  # Quote usage
call "file.bat" :label   # Label dispatch
goto :eof
```
- Kebab-case filenames (`system-detect.bat`). Uppercase env vars for shared state.
- Section banners: `:: =====`. Log via `src\logging\logger.bat`.
- Always check admin rights before privileged operations.

## Safety Rules
- Never disable Windows Defender, UAC, DEP, ASLR, CFG, or Windows Update.
- No placebo tweaks without documented technical justification.
- Prefer evidence-based, reversible changes with visible logging.
- Validate OS/hardware compatibility before version/vendor-specific changes.

## Agent Change Strategy
- GUI code in `clutchg/src/gui/`, non-UI logic in `clutchg/src/core/`. Don't mix UI rendering with business logic.
- Tests: narrowest suite first, broaden if needed.
- Batch scripts: inspect all callers and called labels before renaming.
- Prefer small, reviewable changes over broad refactors.

## Verification
- Python changes: run single-file pytest first, then broader suite if shared logic changed.
- GUI-only changes: note if verification limited by desktop/admin constraints.
- Batch changes: provide manual verification steps.

## Commit Style
Concise, casual Thai/English mixed: `เขียนหน้า Help ใหม่: 9 topics, แก้ข้อมูลผิด + เพิ่ม FAQ`

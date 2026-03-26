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
- Create a virtual environment from the repo root:
  - `python -m venv venv`
  - `venv\Scripts\activate`
- Install GUI runtime dependencies:
  - `pip install -r clutchg\requirements.txt`
- Install GUI test dependencies when running pytest suites:
  - `pip install -r clutchg\requirements-test.txt`
- Install document-tool dependencies when working in `scripts/`:
  - `pip install -r scripts\requirements.txt`

## Run Commands
- Run the batch optimizer manually:
  - `src\optimizer.bat`
- Run the GUI from source from inside `clutchg\src`:
  - `python main.py`
- Run the GUI from the `clutchg` directory without changing folders:
  - `python src\main.py`
- Run the GUI in test-friendly mode:
  - `python src\main.py --test-mode`
- Run the legacy ad-hoc core smoke test:
  - `python test_core.py`

## Build Commands
- Build the Windows executable from `clutchg\`:
  - `python build.py`
- Build output is expected at `clutchg\dist\ClutchG.exe`.
- `build.py` installs `pyinstaller` on demand if it is missing.

## Test Commands
- Pytest configuration lives in `clutchg\pytest.ini`.
- Run the full automated suite from `clutchg\`:
  - `pytest`
- Run with explicit coverage output:
  - `pytest --cov=src tests/`
- Run only unit tests:
  - `pytest tests\unit -m unit`
- Run only integration tests:
  - `pytest tests\integration -m integration`
- Run only end-to-end tests:
  - `pytest tests\e2e -m e2e --app-path src\main.py`
- Skip slow tests:
  - `pytest --skip-slow`
- Skip E2E tests:
  - `pytest --skip-e2e`
- Run a single file:
  - `pytest tests\unit\test_action_catalog.py -v`
- Run a single test function:
  - `pytest tests\unit\test_action_catalog.py -k test_risk_aggregation_for_memory_pack -v`
- Run a single node directly:
  - `pytest tests\unit\test_action_catalog.py::TestActionCatalog::test_risk_aggregation_for_memory_pack -v`
- HTML coverage output is written to `clutchg\htmlcov\`.

## Lint And Validation
- No repo-managed lint configuration was found for Ruff, Black, Flake8, isort, Pylint, or mypy.
- No root `pyproject.toml`, `ruff.toml`, `.flake8`, or `.editorconfig` was found.
- Do not invent a formatter switch for the repo; match the surrounding style instead.
- When asked to "lint," use the strongest available project-native checks:
  - `pytest`
  - targeted import/runtime smoke checks such as `python test_core.py`
- For Python-only syntax sanity after edits, a safe optional check is:
  - `python -m compileall src`
- Batch scripts have no automated lint step; validate by reading call flow carefully and, when safe, testing on Windows with admin rights.

## Python Style Guidelines
- Follow PEP 8 with 4-space indentation.
- Keep module and public class/function docstrings; the codebase uses triple-quoted docstrings heavily.
- Use type hints on public functions, methods, fixtures, and dataclass fields.
- Use `from __future__ import annotations` at the top of modules with complex type hints.
- Prefer `Path` over raw string path concatenation.
- Prefer dataclasses and enums for structured data already modeled that way.
- Keep functions focused and named after one responsibility.
- Preserve the current absolute-import style relative to `clutchg/src`, for example:
  - `from core.batch_parser import BatchParser`
  - `from utils.logger import get_logger`
- Order imports as: standard library, third-party, local modules.
- Keep one import per line unless the existing file consistently groups short imports.
- Use `snake_case` for functions, methods, variables, and Python filenames.
- Use `PascalCase` for classes.
- Use `UPPER_SNAKE_CASE` for constants and enum-like identifiers.
- Preserve existing domain naming where values are intentionally uppercase, such as profile names `SAFE`, `COMPETITIVE`, and `EXTREME`.
- When writing JSON, preserve human readability with `indent=2` unless the file already uses another format.
- Use UTF-8 only when needed for user-facing symbols or explicit export behavior; otherwise keep edits ASCII-friendly.

## Python Error Handling
- Log operational failures with `logger = get_logger(__name__)`.
- Prefer specific exceptions over bare `except:`.
- Return `None`, `False`, or a structured result object for expected operational failure paths when the surrounding code already follows that pattern.
- Raise exceptions only when the caller is clearly expected to handle them.
- For Windows subprocess calls, capture output when diagnosis matters and include timeouts for slow system operations.
- Silent exception handling is only acceptable for best-effort cleanup, test teardown, or optional UI automation capture.

## Testing Conventions
- Shared pytest fixtures and custom CLI flags live in `clutchg\tests\conftest.py`.
- Existing markers are `unit`, `integration`, `e2e`, `slow`, `admin`, and `requires_network`.
- Keep unit tests isolated from real system state.
- Use `tmp_path`, temp config directories, and mocks instead of touching user data.
- Mark Windows/admin-sensitive tests explicitly.
- Follow the current pattern of placing focused tests near the relevant layer under `tests/unit/`, `tests/integration/`, or `tests/e2e/`.
- E2E tests use page objects under `clutchg\tests\e2e\pages\` and should stay readable over clever.

## Batch Script Style Guidelines
- Start scripts with `@echo off`.
- Use `setlocal EnableDelayedExpansion` when variables need delayed expansion.
- Keep label-based dispatch patterns, for example `call "file.bat" :label` and `goto :eof`.
- Quote path variables and arguments consistently: `set "VAR=value"` and `"%VAR%"`.
- Keep filenames descriptive and kebab-case, matching the current convention such as `system-detect.bat`.
- Use uppercase environment variable names for shared state.
- Separate large sections with comment banners like the existing `:: =====` blocks.
- Log each tweak or major step through `src\logging\logger.bat` or equivalent wrapper flow.
- Preserve reversibility: create backups, restore points, or snapshots before risky changes.
- Check admin rights before any privileged operation.

## Safety Rules
- Do not add tweaks that disable Windows Defender, UAC, DEP, ASLR, CFG, or Windows Update.
- Do not introduce placebo tweaks without documented technical justification.
- Prefer evidence-based, reversible changes with visible logging.
- Validate OS/hardware compatibility before applying version- or vendor-specific changes.
- If a change affects BCDEdit, services, registry, or restore points, mention risk and rollback impact in your notes.

## Change Strategy For Agents
- Keep GUI code in `clutchg/src/gui/` and non-UI logic in `clutchg/src/core/`.
- Avoid mixing UI rendering decisions with execution/business logic.
- When editing tests, update the smallest relevant suite first, then broaden if needed.
- When editing batch scripts, inspect all callers and called labels before renaming variables or labels.
- Keep research artifacts and production code separate.
- Prefer small, reviewable changes over broad refactors unless the task explicitly requests restructuring.

## Verification Expectations
- For Python changes, run the narrowest meaningful pytest command first, ideally a single file or single test.
- For shared Python logic changes, follow with the relevant marker group or full `pytest` run when practical.
- For GUI-only changes, mention whether verification was limited by desktop/admin constraints.
- For batch changes, provide manual verification steps if you cannot safely execute them in the current environment.

## Commit Guidance
- Use concise imperative commit messages, for example `Add backup validation before profile apply`.
- Include risk level, affected modules, and manual verification notes in PR descriptions when relevant.

# Repository Guidelines

## What Is This Project?

**ClutchG** — a Thai university thesis project (independent study) that researches Windows PC optimization, then builds a real tool from the findings.

**Three deliverables:**
1. **Research** — Analyzed 28 open-source Windows optimizer repos (50,000+ lines), classified 48 tweaks into 10 categories, built a risk framework (LOW/MEDIUM/HIGH), and separated evidence-based tweaks from myths/placebos.
2. **Batch Optimizer** (`src/`) — Modular `.bat` scripts that apply the vetted tweaks. Three profiles: SAFE, COMPETITIVE, EXTREME. Every change is logged, reversible, and requires admin.
3. **ClutchG GUI** (`clutchg/`) — Python/CustomTkinter desktop app that discovers, explains, and runs those batch scripts with a modern dark UI.

**Thesis documentation** follows ISO 29110 (Very Small Entity profile) for software lifecycle work products.

---

## Project Principles

| Principle | Rule |
|-----------|------|
| Safety-first | NEVER disable Defender, UAC, DEP, ASLR, CFG, or Windows Update |
| Evidence-based | No placebo tweaks — every tweak must have documented technical justification |
| Reversible | All changes can be rolled back; backup before modify |
| Honest claims | Realistic gains are 5–15%, not 200% |
| Logged | Every action is flight-recorded for auditability |

---

## Repository Map (Quick)

```
bat/                                  ← Git root
├── src/                              ← Batch optimizer scripts (the engine)
├── clutchg/                          ← Python GUI app (the interface)
├── docs/                             ← All documentation (research, ISO, design, guides)
├── research/                         ← Raw research material & cloned repos
├── thesis/                           ← Thesis chapters & structured THESIS_DOCS (gitignored)
├── UX/                               ← UI screenshots, design references, mockups
├── scripts/                          ← Standalone Python tooling (Notion import, icon tools)
├── img/                              ← Miscellaneous images
├── skills/                           ← AI agent skill definitions
├── psi/                              ← Agent handoff inbox
├── AGENTS.md                         ← This file — universal AI context
├── CLAUDE.md                         ← Claude-specific extended context
├── mapping.md                        ← Full file/folder location map
├── README.md / README-TH.md         ← Project READMEs (EN/TH)
└── [AI tool configs]                 ← .agents/, .claude/, .opencode/, etc.
```

> **Full directory map:** See `mapping.md` for every file and folder with descriptions.

---

## Batch Optimizer (`src/`)

Entry point: `src/optimizer.bat` (v2.0, 549 lines). Requires admin rights.

| Folder | What's Inside |
|--------|--------------|
| `core/` | 17 modules — power, services, registry, network, GPU, storage, maintenance, input, telemetry, debloater, bcdedit, system-detect |
| `profiles/` | `safe-profile.bat`, `competitive-profile.bat`, `extreme-profile.bat` |
| `safety/` | `validator.bat`, `rollback.bat`, `extreme-rollback.bat`, `flight-recorder.bat` |
| `backup/` | `backup-registry.bat`, `restore-point.bat` |
| `logging/` | `logger.bat` — batch-side structured logging |
| `validation/` | `benchmark-runner.bat` |

**Naming:** kebab-case filenames, UPPER_SNAKE env vars, label dispatch with `call "file.bat" :label`.

---

## Python GUI (`clutchg/`)

Entry point: `python clutchg/src/main.py` (supports `--test-mode`).
Build: `cd clutchg && python build.py` → `clutchg/dist/ClutchG.exe`.

### Source (`clutchg/src/`)

| Layer | Path | Modules | Purpose |
|-------|------|---------|---------|
| Entry | `main.py` | 1 | Argparse, admin check, launches app |
| App | `app_minimal.py` | 1 | Main ClutchGApp controller, view routing |
| Core | `core/` | 13 | Business logic — parsing, profiles, backup, config, system info, tweak registry |
| GUI | `gui/views/` | 8 | Dashboard, Scripts, Profiles, Backup, RestoreCenter, Help, Settings, Welcome |
| GUI | `gui/components/` | 12 | Sidebar, buttons, cards, dialogs, toast, tooltip, progress, timeline |
| GUI | `gui/` | 5 | theme.py, style.py, icons.py, font_loader.py, font_installer.py |
| Data | `data/` | 2 | help_content.json, risk_explanations.json |
| Utils | `utils/` | 3+pkg | admin.py, logger.py, tkinter_capture/ |
| Assets | `assets/` | 4 PNG | CPU, GPU, RAM icons + app icon |
| Fonts | `fonts/` | 4 TTF | Figtree Regular/Bold, Material Symbols, Tabler Icons |

### Key Domain Concepts

**Tweak Registry** (`core/tweak_registry.py`) — Central knowledge base. Each `Tweak` dataclass has: id, name, category, description, what_it_does, why_it_helps, limitations, warnings, risk_level, expected_gain, preset flags (safe/competitive/extreme), registry keys, bat_script reference. ~48 tweaks across 10 categories.

**Profiles** — SAFE (low-risk only), COMPETITIVE (medium-risk gaming focus), EXTREME (all tweaks including high-risk). Profile manager maps tweaks to profiles and tracks which are applied.

**Batch Parser** (`core/batch_parser.py`) — Reads `.bat` files from `src/`, extracts tweak metadata and call structure. The GUI doesn't hardcode tweak lists — it discovers them from the batch scripts.

**Action Catalog** (`core/action_catalog.py`) — Defines available optimization actions with risk aggregation. Maps user-facing "packs" to underlying tweaks.

### Tests (`clutchg/tests/`)

| Suite | Location | Count | Pattern |
|-------|----------|-------|---------|
| Unit | `tests/unit/` | 15 files | Isolated, `tmp_path`, mocks |
| Integration | `tests/integration/` | 2 files | Cross-module workflows |
| E2E | `tests/e2e/` | 4 files | Page objects in `tests/e2e/pages/` |

**Current baseline: 477 passed, 64 skipped (E2E skipped without display).**

Config: `clutchg/pytest.ini`, `clutchg/.coveragerc`. Markers: `unit`, `integration`, `e2e`, `slow`, `admin`, `requires_network`.

---

## Documentation (`docs/`)

### Research Series (16 docs)
Numbered `01-` through `16-`: research overview, 28 repo analyses (`02-repo-analysis/`), tweak taxonomy, risk classification, Windows internals, performance impact, best practices, architecture decisions, development plan, user guides (TH/EN).

### ISO 29110 (`docs/iso29110-clutchg/`)
10 work products: Project Plan, SRS, SDD, Test Plan, Test Record, Traceability Matrix, Change Requests, Progress Status, Configuration Plan, User Manual. Plus UML appendix.

### Design Docs
Architecture, UI/UX redesign plan, design mockups (HTML), design specs (MD), suggestion guide, implementation evidence summary.

### Generic ISO Templates (`docs/iso29110/`)
Reusable ISO 29110 templates and process guides (not ClutchG-specific).

---

## Thesis (`thesis/`) — Gitignored

**`thesis/THESIS_DOCS/`** — 10 structured sections: Literature Review, Research Methodology, System Analysis, Requirements Engineering, Architecture Design, Implementation, Testing & Quality, Design Thinking, Models & Technical, Deliverables.

**`thesis/thesis-chapters/`** — 8 markdown chapters: abstracts (TH/EN), introduction through testing results.

---

## Design Decisions (Persist Across Sessions)

| Decision | Choice |
|----------|--------|
| Theme | Dark — Windows 11 / Sun Valley style (`#1c1c1c` bg, `#57c8ff` accent) |
| Font | Figtree (bundled TTF) |
| Icon font | Tabler Icons (`tabler-icons.ttf` v3.41.1) — the ONLY icon source |
| Buttons | Title Case only — no ALL CAPS |
| Commit style | Casual Thai/English mixed |
| No emojis | All emojis replaced with Tabler icons or plain text. Test `test_no_emojis_in_views` enforces this. |
| DPI scaling | All `wraplength` must use `bind_dynamic_wraplength()` from `gui/style.py` — never static values |

### Theme Constants
```python
SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24}
RADIUS  = {"sm": 4, "md": 6, "lg": 10, "full": 999}
COLORS["accent"] = "#57c8ff"
COLORS["bg_card"] = "#2d2d2d"
COLORS["border"] = "#3d3d3d"
```

---

## Setup & Commands

### Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r clutchg\requirements.txt        # Runtime: customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi, tkextrafont
pip install -r clutchg\requirements-test.txt   # Test: pytest, pytest-cov, pytest-html, pytest-xdist, pytest-timeout, pywinauto
```

### Run
```bash
python clutchg\src\main.py              # GUI (from repo root)
python clutchg\src\main.py --test-mode  # Test-friendly mode
cd clutchg && python build.py           # Build → clutchg\dist\ClutchG.exe
```

### Test (run from `clutchg/`)
```bash
pytest                                              # Full suite + coverage
pytest tests\unit -m unit                            # Unit only
pytest tests\integration -m integration              # Integration only
pytest tests\e2e -m e2e --app-path src\main.py       # E2E only
pytest --skip-slow --skip-e2e                        # Fast run
pytest -n auto                                      # Parallel
pytest tests\unit\test_action_catalog.py -v          # Single file
pytest tests\unit\test_X.py -k test_name -v          # Pattern match
```

### Validation
```bash
pytest                                    # Primary validation
python -m compileall clutchg/src          # Syntax check
```

No linter config (no Ruff/Black/Flake8/mypy). Match surrounding style.

---

## Code Style

### Python
- PEP 8, 4-space indent, no inline comments unless requested
- Triple-quoted docstrings for modules, classes, public functions
- Type hints on public functions, methods, fixtures, dataclass fields
- `from __future__ import annotations` for complex types
- Prefer `Path` over string concatenation
- Prefer dataclasses and enums for structured data
- Imports: stdlib → third-party → local, one per line
- Naming: `snake_case` (functions/vars/files), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants)
- Preserve domain names: `SAFE`, `COMPETITIVE`, `EXTREME`
- JSON: `indent=2`
- Error handling: specific exceptions, return `None`/`False` for expected failures, raise only when caller should handle

### Batch
```batch
@echo off
setlocal EnableDelayedExpansion
set "VAR=value"          :: Quote assignments
"%VAR%"                  :: Quote usage
call "file.bat" :label   :: Label dispatch
goto :eof
```
- Kebab-case filenames, uppercase env vars, section banners `:: =====`
- Log via `src\logging\logger.bat`
- Always check admin rights before privileged operations

---

## Safety Rules (Non-Negotiable)

1. **NEVER** disable Windows Defender, UAC, DEP, ASLR, CFG, or Windows Update
2. **NEVER** add placebo tweaks without documented evidence
3. **NEVER** exaggerate performance claims (5–15% realistic, not 200%)
4. All changes must be **reversible** with visible logging
5. Validate **OS/hardware compatibility** before vendor-specific changes
6. If unsure about a tweak's safety → assume **UNSAFE**

---

## Agent Change Strategy

| Area | Rule |
|------|------|
| GUI code | `clutchg/src/gui/` only. Don't mix UI rendering with business logic in `core/`. |
| Business logic | `clutchg/src/core/` only. Views call core, never the reverse. |
| Tests | Narrowest suite first → broaden if shared logic changed |
| Batch scripts | Inspect ALL callers and called labels before renaming anything |
| Change size | Small, reviewable changes. No broad refactors without a plan. |
| Verification | Python: pytest first. GUI-only: note if display/admin limited. Batch: manual verification steps. |
| Commits | Casual Thai/English mixed: `แก้ UI ทั้งระบบ: dynamic wraplength + DPI-aware layout` |

---

## Known LSP Errors (Ignore — Type-Checking Noise)

These are pre-existing type-checker warnings, not bugs:
- `scripts_minimal.py` lines 364, 568, 569, ~2498, ~2518
- `theme.py`, `app_minimal.py`, `settings_minimal.py`, `batch_parser.py` — various
- `glass_card.py` lines 116–117 (`bind` add parameter)
- `help_minimal.py` line 116 (font weight/slant)
- `refined_dialog.py` line ~330 (`show` override return type)
- `style.py` line 25 (font weight)

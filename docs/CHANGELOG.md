# ClutchG — Changelog

> All notable changes to the ClutchG PC Optimizer project.
>
> Period: 13 March 2026 — 10 April 2026
> Commits: 86 (initial commit `c48a8e3` through `f24f7a1`)

---

## Table of Contents

1. [Phase 1 — Initial Release & Foundation](#phase-1--initial-release--foundation)
2. [Phase 2 — UX/UI Audit & Bug Fixes](#phase-2--uxui-audit--bug-fixes)
3. [Phase 3 — Font System & Theme Overhaul](#phase-3--font-system--theme-overhaul)
4. [Phase 4 — View Redesigns (All 8 Views)](#phase-4--view-redesigns-all-8-views)
5. [Phase 5 — Icon Font Migration](#phase-5--icon-font-migration)
6. [Phase 6 — CI/CD Pipeline](#phase-6--cicd-pipeline)
7. [Phase 7 — UI Polish & DPI Fixes](#phase-7--ui-polish--dpi-fixes)
8. [Phase 8 — Project Reorganization & Documentation](#phase-8--project-reorganization--documentation)
9. [Phase 9 — Thesis Diagrams (18 Diagrams)](#phase-9--thesis-diagrams-18-diagrams)
10. [Phase 10 — ISO 29110 Academic Documents](#phase-10--iso-29110-academic-documents)
11. [Phase 11 — Recommendation System Refactor](#phase-11--recommendation-system-refactor)
12. [Appendix A — Commit Log](#appendix-a--commit-log)

---

## Phase 1 — Initial Release & Foundation

**Date:** 13 March 2026
**Commits:** `c48a8e3`, `5632515`

The initial commit that established the entire project structure with 229 files and ~77,000 lines of code.

### Batch Optimizer (`src/`)
- `optimizer.bat` v2.0 — main entry point (549 lines), admin rights required
- 17 core modules: power, services, registry, network, GPU, storage, maintenance, input, telemetry, debloater, bcdedit, system-detect (basic + enhanced variants)
- 3 optimization profiles: `safe-profile.bat`, `competitive-profile.bat`, `extreme-profile.bat`
- Safety infrastructure: `validator.bat`, `rollback.bat`, `extreme-rollback.bat`, `flight-recorder.bat`
- Backup system: `backup-registry.bat`, `restore-point.bat`
- Structured logging: `logger.bat`
- Benchmark runner: `benchmark-runner.bat`

### Python GUI (`clutchg/`)
- Main app with CustomTkinter dark theme (Tokyo Night)
- 13 core modules: action_catalog, backup_manager, batch_executor, batch_parser, benchmark_database, config, flight_recorder, help_manager, profile_manager, profile_recommender, system_info, system_snapshot, tweak_registry
- 8 GUI views: Dashboard, Scripts, Profiles, Backup, RestoreCenter, Help, Settings, Welcome
- 12 GUI components: sidebar, buttons, cards, dialogs, toast, tooltip, progress, timeline, etc.
- Complete test suite: unit (12 files), integration (2 files), E2E (4 files with page objects)
- Build system: `build.py` for PyInstaller packaging

### Research & Documentation
- 16 research documents (overview, 28 repo analyses, taxonomy, risk classification, Windows internals, performance impact, best practices, architecture, development plan, user guides TH/EN)
- ISO 29110 work products: SRS, SDD, Test Plan, Test Record, Traceability, Change Request, Configuration Plan, User Manual, UML Appendix
- Thai README (`README-TH.md`)
- CI pipeline skeleton (`.github/workflows/ci.yml`)

---

## Phase 2 — UX/UI Audit & Bug Fixes

**Date:** 24–26 March 2026
**Commits:** `ca2f306`, `051d920`, `fc05f2a`

### Code Cleanup (`ca2f306`)
- Removed unused GUI components: `context_help_button.py`, `enhanced_toggle.py`, `glassmorphism.py`, `risk_badge.py`, `stat_card.py`
- Updated `batch_parser.py` with improved parsing logic
- Simplified `settings_minimal.py`
- Added new test files: `test_coverage_expansion.py`, `test_profile_manager.py`, `test_tweak_registry_coverage.py`
- Added E2E conftest with proper fixtures

### UX/UI Audit — 14 Issues Resolved (`051d920`, `fc05f2a`)
- **CRIT-01/02/03**: Critical usability issues fixed
- **HIGH-01 through HIGH-07**: High-priority layout and interaction fixes
- **MED-04**: Button height normalization
- **MED-05/06/07/09**: Medium-priority help nav links, spacing, and visual fixes
- **LOW-01/02/03/05**: Minor polish items
- Bug fix report generated with full details
- Bug Hunter adversarial scan run (findings, skeptic review, referee verdicts)

---

## Phase 3 — Font System & Theme Overhaul

**Date:** 27 March 2026
**Commits:** `09dda65`, `105769f`, `f07bdb3`, `1f182aa`

### Bundled Font System
- **Figtree** font family bundled as TTF (Regular + Bold)
- New `font_loader.py` module for runtime font registration via `tkextrafont`
- All font references migrated from Inter/Tahoma to Figtree
- Build script updated to include font files in PyInstaller bundle

### Theme Overhaul
- **Replaced Tokyo Night** theme with **Sun Valley (Windows 11 dark)** style
- New color palette: `#1c1c1c` background, `#57c8ff` accent, `#2d2d2d` cards
- Spacing tokens: xs=4, sm=8, md=12, lg=16, xl=24
- Radius tokens: sm=4, md=6, lg=10, full=999
- Config system updated with new theme constants
- `app_minimal.py` and `main.py` refactored for new theme system

---

## Phase 4 — View Redesigns (All 8 Views)

**Date:** 27 March — 5 April 2026
**Commits:** 30+ commits across 3 design phases

### Phase 4a — Scripts, Backup, Help (27 Mar)
| Commit | View | Changes |
|--------|------|---------|
| `e8498fc` | Dashboard | Score ring, hardware cards, reference screenshots added |
| `5822928` | Scripts | Tab-based layout, profile cards, custom split-pane, all emoji removed |
| `e3a7d0a` | Backup | Stripe pattern removed, wording updated, cleaner layout |
| `c95bb1a` | Help | Compound icons, myths section added, all emoji removed |
| `036e687` | Help Content | Icon keys added to `help_content.json`, emoji replaced |
| `4674a4a` | Sidebar | Navigation labels updated to gamer tone |

### Phase 4b — Profiles, Settings, Welcome (28 Mar)
| Commit | View | Changes |
|--------|------|---------|
| `4991da0` | App | App icon added to assets, sidebar logo, window titlebar |
| `a467e28` | Profiles | Stats grid cards, compare panel, no stripe pattern |
| `ccfd5df` | Settings | Section icons, toggle switches, about panel with app icon |
| `8d79da9` | Welcome | App logo, dot navigation, skip button top-right |
| `eb96035` | Build | PNG-to-ICO conversion added to build script |

### Phase 4c — Full Redesign Iterations (28 Mar — 5 Apr)
- **Dashboard**: Score ring + recommendation card side-by-side layout (`509a2e2`), 1x3 hardware grid (`f2ec681`), plain subtitle header
- **Scripts/Tweaks**: Profiles tab hero layout with recommended card, 2-col secondary grid, filter chips with canvas scroll, detail panel with dynamic wraplength, dropdown filter (`2b16134`)
- **Backup/Restore Center**: Complete redesign with stack-push icons (`2f1e330`)
- **Help/Docs**: 9 topics bilingual, FAQ section, custom tweaks guide (`d7f77b8`)
- **Profiles**: Hero card (recommended) + secondary grid, accent Apply buttons, stats grid fixes (`0b9fe75`, `a3e797c`, `c6a763b`)
- **Settings**: Theme/language options removed, logo replaces icon (`fb8aabb`)
- **Welcome**: Dot navigation, multi-step overlay with animations (`f2ec681`)

### Design Documentation
- Phase 1 mockup (HTML) + spec: sidebar + dashboard (`ebdd8c9`)
- Phase 2 mockup (HTML) + spec: scripts, backup, help (`ebdd8c9`)
- Phase 3 mockup (HTML) + spec: profiles, settings, welcome (`aec3c04`)
- UX redesign reference screenshots (14 images)

---

## Phase 5 — Icon Font Migration

**Date:** 28 March — 3 April 2026
**Commits:** 10+ commits

### Migration Path: Segoe MDL2 → Material Symbols → Tabler Icons

| Stage | Date | What Changed |
|-------|------|-------------|
| Segoe MDL2 → Material Symbols | 28 Mar | Help view (`36126a3`), Scripts/Tweaks view (`faf9729`), icon_provider codepoints fixed (`b73ea1e`) |
| Material Symbols font bundled | 2 Apr | `MaterialSymbolsOutlined.ttf` added, font_loader updated (`42ed76f`) |
| Material Symbols → **Tabler Icons** | 3 Apr | Complete migration to `tabler-icons.ttf` v3.41.1 (`b0d2d7f`) |
| Full codebase cleanup | 3 Apr | All 11 files migrated, 0 legacy icon codes remaining (`2a293ae`) |

### Final State
- **Tabler Icons v3.41.1** is the sole icon font source
- `icons.py` contains all icon codepoint mappings
- Hardware cards (CPU/GPU/RAM) use PNG images instead of font icons (`822c9b2`, `ec50352`, `08a026a`)
- Design decision enforced: no emojis anywhere (test `test_no_emojis_in_views` validates)

---

## Phase 6 — CI/CD Pipeline

**Date:** 27 March 2026
**Commit:** `684e935`

> **Note:** This was never documented in any project documentation until now.

### GitHub Actions CI Pipeline (`.github/workflows/ci.yml`)

**Trigger:** Push to `main`/`develop` branches, PRs to `main` (only when `clutchg/` or `.github/workflows/` files change)

**Environment:** `windows-latest`, Python 3.11 with pip caching

**Pipeline Steps:**
1. **Checkout** repository (`actions/checkout@v4`)
2. **Python 3.11** setup with dependency caching (`actions/setup-python@v5`)
3. **Install** runtime dependencies (`clutchg/requirements.txt`)
4. **Install** test dependencies (`clutchg/requirements-test.txt`)
5. **Unit tests** with coverage (`pytest tests/unit -m unit --cov=src`)
6. **Integration tests** (`pytest tests/integration -m integration`)
7. **Upload** HTML coverage report (artifact, 14-day retention)
8. **Upload** JUnit XML test results (artifact, 14-day retention)
9. **Syntax check** (`python -m compileall clutchg/src`) — added in `684e935`
10. **Coverage summary** in PR step summary

**Excluded from CI:**
- E2E tests (require desktop session + CustomTkinter GUI display)
- Admin-only tests (require elevated privileges)

---

## Phase 7 — UI Polish & DPI Fixes

**Date:** 2–5 April 2026
**Commits:** 15+ commits

### DPI-Aware Layout (`2b16134`)
- **Dynamic wraplength** system: `bind_dynamic_wraplength()` in `gui/style.py`
- All static `wraplength` values replaced with dynamic binding across every view
- Hero card redesigned with proper DPI scaling
- Dropdown filter for tweak categories
- Toast notification with dynamic height calculation

### Bug Fixes
| Commit | Fix |
|--------|-----|
| `f97527d` | Theme cache bug — `set_theme` no longer clears COLORS dict |
| `bd759d6` | Sidebar logo path + collapse with `grid_propagate(False)` |
| `4684a7e` | Sidebar collapse — `minsize` + `sticky=ns` to lock column width |
| `b753202` | Tab bar width — changed to fit-content |
| `ca54a9e` | Config default theme set to modern/sunvalley |
| `3e76428` | Score font 28px for 120px ring — prevent number overflow |
| `e643447` | Alignment fixes: `anchor=w`, `sticky=ew`, `fill=x` across all views + Profiles tab crash (KeyError) |
| `03a4a21` | Tweaks page alignment: 5 anchor fixes + edu card wraplength + detail modal |

### Component Improvements
- Circular progress: font/sizing fixes
- Glass card: container improvements
- Enhanced button: style refinements
- Timeline: layout updates
- View transition: animation fixes
- Filter chips: flow layout wrap for multiple rows (`f7830e1`)
- Detail panel: wraplength from actual panel width (`e63e13f`)

---

## Phase 8 — Project Reorganization & Documentation

**Date:** 5 April 2026
**Commits:** `4461914`, `d0ba59b`, `14cf768`, `64988d6`

### File Organization (`4461914`)
Moved scattered files into proper directories:
- `docs/` — all documentation
- `img/` — miscellaneous images
- `research/` — raw research material & cloned repos
- `thesis/` — thesis chapters & structured documents
- `UX/` — UI screenshots, design references, mockups
- `scripts/` — standalone Python tooling
- `psi/` — agent handoff inbox
- Updated all path references across documents

### Documentation Rewrite
| File | What Changed |
|------|-------------|
| `AGENTS.md` | Complete rewrite — universal AI context document (`d0ba59b`) |
| `mapping.md` | New file — full directory map with every file and folder (`d0ba59b`) |
| `README.md` | Complete rewrite — English project README (`14cf768`) |
| `README-TH.md` | Complete rewrite — Thai project README (`14cf768`) |
| `LICENSE` | Added MIT license (`14cf768`) |
| `.gitignore` | Updated — removed AI tool files from tracking (`14cf768`) |

### UX Directory Restructure (`64988d6`)
- Consolidated into `UX/UI design/` directory
- Latest screenshots used in README

---

## Phase 9 — Thesis Diagrams (18 Diagrams)

**Date:** 6–7 April 2026
**Commits:** `2d66fa5` through `6088edc` (12 commits)

All diagrams created in draw.io format with PNG exports. English only, thesis-ready white theme.

| # | Diagram | Description |
|---|---------|-------------|
| 01 | Architecture Overview | System layers, module boundaries |
| 02 | Execution Flow | Batch optimizer pipeline start-to-finish |
| 03 | GUI Navigation | View hierarchy and sidebar routing |
| 04 | Tweak Lifecycle | Discovery → validation → apply → verify → rollback |
| 05 | Risk Framework | LOW/MEDIUM/HIGH classification with entity relationships |
| 06 | Module Dependencies | Import graph between core/gui/utils modules |
| 07 | Use Case Diagram | Actor-system interaction boundaries |
| 08a | Class Diagram (Simplified) | Key classes for thesis body |
| 08b | Class Diagram (Data Models) | Full data models for appendix |
| 09 | Sequence Diagram | Optimization flow message passing |
| 10 | Deployment Diagram | Component-to-environment mapping |
| 11 | Conceptual Framework | Research model and relationships |
| 12 | Gantt Chart | Project timeline and milestones |
| 13 | State Diagram | Application state transitions |
| 14 | PC Score Scoring Flow | Hardware scoring formulas and thresholds |
| 15 | Recommendation Decision Tree | Unified recommendation logic flow |
| 16 | Technology Stack | Languages, frameworks, tools |
| 16b | Tech Stack Architecture View | Layered architecture with technology mapping |

### Diagram Infrastructure
- `docs/diagrams/drawio/` — source `.drawio` files
- `docs/diagrams/img/` — exported `.png` files
- `docs/diagrams/README.md` — gallery index with descriptions and image previews
- Multiple polish passes: font fixes, legend fixes, edge routing, layout balancing (`ea45e4f`, `4af3dd0`, `4055385`, `028426b`, `1766751`)

---

## Phase 10 — ISO 29110 Academic Documents

**Date:** 6 April 2026
**Commits:** `b93e59e`, `80e7d57`

### SE Academic Enhancement (`b93e59e`)
Updated all 9 ISO 29110 documents with software engineering academic content:
- `02-SRS.md` — Software Requirements Specification
- `03-SDD.md` — Software Design Description
- `04-Test-Plan.md` — Test Plan
- `05-Test-Record.md` — Test Record
- `06-Traceability-Record.md` — Traceability Matrix
- `07-Change-Request.md` — Change Request Log
- `09-Configuration-Plan.md` — Configuration Management Plan
- `10-User-Manual.md` — User Manual
- `Appendix-A-UML-Diagrams.md` — UML Diagram Appendix

### Project Management Documents (`80e7d57`)
- `01-Project-Plan.md` — added to repo
- `08-Progress-Status.md` — added to repo
- Updated ISO 29110 README

---

## Phase 11 — Recommendation System Refactor

**Date:** 8–10 April 2026
**Status:** Code complete, uncommitted

### Architecture Change
Created unified recommendation service to replace dual-authority pattern.

| Change | Detail |
|--------|--------|
| **New file** | `clutchg/src/core/recommendation_service.py` — single `recommend_preset()` entry point |
| **New field** | `benchmark_matched: bool` on `CPUInfo` and `GPUInfo` dataclasses |
| **4-condition gate** | `_has_sufficient_data()`: total_score numeric, form_factor known, RAM > 0, at least one benchmark matched |
| **Primary path** | Score-based: ≥80 + desktop + 16GB → EXTREME, ≥50 + 8GB → COMPETITIVE, else → SAFE |
| **Fallback path** | Conservative heuristic: laptop → SAFE, desktop + mid/high/enthusiast → COMPETITIVE, else → SAFE. **Never returns EXTREME.** |
| **Updated callers** | `dashboard_minimal.py`, `scripts_minimal.py` — both use unified service |
| **Legacy compat** | `tweak_registry.suggest_preset()` delegates to unified service |
| **Tests** | 32 new tests in `test_recommendation_service.py` |
| **Test baseline** | 445 → 477 passed (64 skipped E2E) |

### Diagram Update
- Diagram 15 (Recommendation Decision Tree) rewritten to match unified flow
- `docs/diagrams/README.md` section 15 and index table updated

### Documentation Updates
- `mapping.md` updated: date, core modules 13→14, new files listed, test baseline, diagrams section added

---

## Appendix A — Commit Log

Full chronological commit history (83 commits):

```
c48a8e3  2026-03-13  Initial commit: ClutchG PC Optimizer v2.0
5632515  2026-03-13  Add Thai README (README-TH.md)
ca2f306  2026-03-24  Update ClutchG: Remove unused components, update tests, and add new test files
051d920  2026-03-26  fix: UX/UI audit fixes — 14 issues resolved
fc05f2a  2026-03-26  fix: remaining UX audit fixes — MED-04 button heights, MED-09 help nav links
09dda65  2026-03-27  feat: add bundled Figtree font system with font_loader
105769f  2026-03-27  feat: replace Tokyo Night theme with Sun Valley (Windows 11 dark)
f07bdb3  2026-03-27  refactor: update font references from Inter/Tahoma to Figtree
1f182aa  2026-03-27  refactor: update app_minimal and main.py for new theme system
e8498fc  2026-03-27  feat: add UX redesign reference screenshots and update dashboard
ebdd8c9  2026-03-27  docs: add Phase 1-2 design mockups and Phase 2 implementation spec
036e687  2026-03-27  feat: add icon keys and replace emoji in help_content
4674a4a  2026-03-27  refactor: update sidebar nav labels to gamer tone
5822928  2026-03-27  feat: overhaul ScriptsView - tabs, profiles, custom split-pane, no emoji
e3a7d0a  2026-03-27  feat: overhaul backup views - remove stripes, update wording
c95bb1a  2026-03-27  feat: overhaul HelpView - compound icons, myths section, no emoji
59eea46  2026-03-27  chore: update AGENTS.md formatting
684e935  2026-03-27  chore: add syntax check to CI pipeline
aec3c04  2026-03-28  docs: add Phase 3 mockup, spec, and app icon source
4991da0  2026-03-28  feat: add app icon to assets, sidebar logo, and window titlebar
a467e28  2026-03-28  feat: overhaul ProfilesView - stats grid cards, compare panel, no stripes
ccfd5df  2026-03-28  feat: overhaul SettingsView - section icons, switches, about with app icon
8d79da9  2026-03-28  feat: overhaul WelcomeOverlay - app logo, dot nav, skip top-right
eb96035  2026-03-28  feat: add PNG to ICO conversion in build script
9757255  2026-03-28  phase1 theme + component cleanup
964c9f1  2026-03-28  phase1 sidebar: settings button + divider
9203e2f  2026-03-28  phase1 dashboard + admin bypass for test-mode
36126a3  2026-03-28  fix icon font in Docs view — Segoe MDL2 → Material Symbols Outlined
faf9729  2026-03-28  migrate Tweaks view icons from Segoe MDL2 to Material Symbols Outlined
b73ea1e  2026-03-28  fix Material Symbols codepoints in icon_provider
1cf9bcd  2026-03-28  sidebar: logo frame + ClutchG name label, fix refresh_colors crash
18e82b4  2026-03-28  docs: reformat ISO 29110 markdown tables + update project structure
4744baf  2026-03-28  fix icon fonts + welcome overlay colors + profiles stats + scripts pills
412972f  2026-03-29  phase 1 cleanup: theme tokens, icon split, sidebar destroy, font fix
2f1e330  2026-03-29  phase 2: redesign backup, scripts text/tone, help layout+content
f2ec681  2026-03-30  phase 3: profiles/settings/welcome redesign + theme fix + dashboard grid
3e76428  2026-03-30  fix: score font 28px for 120px ring
ca54a9e  2026-04-02  fix config default theme to modern/sunvalley
509a2e2  2026-04-02  redesign dashboard layout: score ring + rec card side-by-side
8a847b8  2026-04-02  fix P1 UI polish: outline run btn, tweak row col weights, help wraplength
f97527d  2026-04-02  fix theme cache bug: set_theme no longer clears COLORS
b753202  2026-04-02  fix tab bar Tweaks — fit-content width
bd759d6  2026-04-02  fix sidebar — logo path + grid_propagate(False)
4684a7e  2026-04-02  fix sidebar collapse — minsize + sticky=ns
fa00b57  2026-04-02  fix sidebar collapse + redesign Profiles tab
a3e797c  2026-04-02  fix Profiles stats grid layout
0b9fe75  2026-04-02  Profiles tab: hero layout + audit fixes
c6a763b  2026-04-02  Profiles tab: reduce card size + fix inline icons
42ed76f  2026-04-02  bundle Material Symbols font + reduce preset card size
23f96ae  2026-04-02  UX audit iteration 2: hero 2-col + FPS dominant + star badge
0bccfec  2026-04-02  hero card compact + fix star badge font
b0d2d7f  2026-04-03  swap icon font: Material Symbols → Tabler Icons (v3.41.1)
2a293ae  2026-04-03  migrate all icons to Tabler — 0 legacy codes remaining
fb8aabb  2026-04-03  settings: Tabler icons, remove theme/language, logo + backup stack-push
822c9b2  2026-04-03  dashboard: PNG hardware images instead of font icons
02db077  2026-04-03  redesign Custom Tweaks tab: adaptive layout, compact rows, search/filter
ec50352  2026-04-03  new hardware icon set (SVGRepo) + tint for dark theme
08a026a  2026-04-03  enlarge hardware icons 20→28px
9f7e9e3  2026-04-03  UX audit rounds 2-3: filter chips + full-height + sidebar pill-style
d7f77b8  2026-04-03  rewrite Help/Docs: 9 topics, bilingual, fix incorrect info + FAQ
56ba746  2026-04-04  detail panel: fix scroll clipping, reduce font, add padding, remove emoji
ebd905c  2026-04-04  filter chips: Canvas scroll instead of plain frame
e63e13f  2026-04-04  detail panel: dynamic wraplength from inner width
f7830e1  2026-04-04  filter chips: flow layout wrap + detail panel wraplength from real width
2b16134  2026-04-05  dynamic wraplength system-wide, hero card, dropdown filter, DPI-aware
4461914  2026-04-05  reorganize project root: docs/, img/, research/, thesis/, UX/, scripts/
d0ba59b  2026-04-05  rewrite AGENTS.md + create mapping.md
14cf768  2026-04-05  rewrite README EN/TH, add LICENSE, update .gitignore
e643447  2026-04-05  alignment fixes system-wide: anchor=w, sticky=ew, fill=x + Profiles crash
03a4a21  2026-04-05  alignment Tweaks page: 5 anchor fixes + edu card + detail modal
64988d6  2026-04-05  restructure UX/ directory + latest screenshots in README
2d66fa5  2026-04-06  diagrams batch 1: architecture, execution, GUI nav, tweak lifecycle, risk, deps
d0cd7f9  2026-04-06  diagrams batch 2: use case, class diagram, sequence diagram
93999b5  2026-04-06  diagrams batch 3: deployment, conceptual framework, gantt, state
ea45e4f  2026-04-06  fix font and legend in remaining diagrams
4af3dd0  2026-04-06  fix P1 diagrams: entity bug, actor edges, title font, HTML stereotype
c8633cd  2026-04-06  split class diagram into 08a (simplified) + 08b (data models)
4055385  2026-04-06  fix edge routing in diagram 08a
f69041b  2026-04-06  add diagrams README for GitHub gallery
7382d52  2026-04-06  organize diagram folder: separate drawio/ and img/
412198e  2026-04-06  remove audit report from repo
028426b  2026-04-06  fix overlapping edges in diagram 06
1766751  2026-04-06  move Windows OS actor outside system boundary in diagram 07
b93e59e  2026-04-06  add SE academic content to 9 ISO 29110 documents
80e7d57  2026-04-06  add Project Plan, Progress Status, README to repo
6088edc  2026-04-07  add diagrams 14-16 + update README gallery to 16 diagrams
cfb02e1  2026-04-10  refactor recommendation system: unified recommend_preset() + benchmark_matched gate
6fd00b3  2026-04-10  update diagram 15 (new recommendation flow) + add 16b tech stack + fix README gallery
f24f7a1  2026-04-10  add CHANGELOG + update mapping.md + add ISO doc 11 (PC Score System)
```

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total commits | 86 |
| Date range | 13 Mar — 10 Apr 2026 (29 days) |
| Files in initial commit | 229 |
| Lines in initial commit | ~77,000 |
| Test baseline (initial) | ~300 tests |
| Test baseline (current) | 477 passed, 64 skipped |
| Diagrams created | 18 (draw.io + PNG) |
| ISO 29110 documents | 11 |
| Views redesigned | 8/8 (100%) |
| Icon migrations | 2 (Segoe MDL2 → Material Symbols → Tabler) |
| Theme changes | 1 (Tokyo Night → Sun Valley/Windows 11 dark) |
| Font changes | 1 (Inter/Tahoma → Figtree bundled) |

# Project File Map — ClutchG

> ทุกไฟล์และโฟลเดอร์ในโปรเจกต์: อยู่ที่ไหน คืออะไร ทำอะไร
> Every file and folder in this project: where it lives, what it is, what it does.

**Git root:** `C:\Users\nextzus\Documents\thesis\bat\`
**Last updated:** 2026-04-05

---

## Root Files

| File | What It Is |
|------|-----------|
| `AGENTS.md` | Universal AI agent context — project overview, rules, style, safety |
| `CLAUDE.md` | Claude-specific extended context (1,088 lines, detailed code paths) |
| `mapping.md` | This file — full project location map |
| `README.md` | Project README (English) |
| `README-TH.md` | Project README (Thai) |
| `opencode.json` | OpenCode CLI configuration |
| `.gitignore` | Git ignore rules (130 lines) |
| `.kilocodemodes` | Kilocode modes config |
| `skills-lock.json` | AI skills dependency lock |
| `.coverage` | pytest coverage data (stale) |
| `nul` | 0-byte artifact from batch script bug — kept |
| `capture_ui.py` | Root-level UI capture script (old, prefer `scripts/capture_ui_views.py`) |

---

## `src/` — Batch Optimizer Scripts

The engine. Modular `.bat` scripts for Windows optimization. Requires admin.

| Path | Purpose |
|------|---------|
| `optimizer.bat` | **Main entry point** (v2.0, 549 lines). Initializes paths, checks admin, dispatches to profiles |
| `simple-suggest.bat` | Simplified suggestion/recommendation script |

### `src/core/` — 17 Optimization Modules

| File | What It Optimizes |
|------|-------------------|
| `system-detect.bat` | Hardware & OS detection |
| `system-detect-enhanced.bat` | Extended hardware detection (CPU, GPU, RAM details) |
| `power-manager.bat` | Power plan tweaks (High Performance, timer resolution) |
| `power-manager-enhanced.bat` | Advanced power management (core parking, C-states) |
| `service-manager.bat` | Disables non-essential Windows services |
| `network-manager.bat` | TCP/IP, Nagle, network throttling tweaks |
| `network-optimizer-enhanced.bat` | Advanced network (RSS, RSC, offloading) |
| `gpu-optimizer.bat` | GPU scheduling, hardware acceleration |
| `gpu-optimizer-enhanced.bat` | NVIDIA/AMD-specific GPU tweaks |
| `storage-optimizer.bat` | SSD/HDD optimization (TRIM, prefetch, superfetch) |
| `maintenance-manager.bat` | Cleanup, temp files, scheduled maintenance |
| `registry-utils.bat` | Registry read/write helper functions |
| `bcdedit-manager.bat` | Boot Configuration Data (BCD) tweaks |
| `debloater.bat` | Remove bloatware & preinstalled apps |
| `input-optimizer.bat` | Mouse/keyboard latency reduction |
| `telemetry-blocker.bat` | Disable Windows telemetry & data collection |
| `test.bat` | Test helper script |

### `src/profiles/` — Preset Configurations

| File | Risk Level | What's Included |
|------|-----------|-----------------|
| `safe-profile.bat` | LOW only | Conservative tweaks, no reboots needed |
| `competitive-profile.bat` | LOW + MEDIUM | Gaming-focused, some service disabling |
| `extreme-profile.bat` | ALL | Everything including HIGH-risk BCD edits |

### `src/safety/` — Protection & Rollback

| File | Purpose |
|------|---------|
| `validator.bat` | Pre-run system validation and compatibility checks |
| `rollback.bat` | Undo SAFE/COMPETITIVE profile changes |
| `extreme-rollback.bat` | Undo EXTREME profile changes (BCD, services) |
| `flight-recorder.bat` | Log every change for audit trail |

### `src/backup/` — Backup Helpers

| File | Purpose |
|------|---------|
| `backup-registry.bat` | Export registry keys before modification |
| `restore-point.bat` | Create Windows System Restore point |

### `src/logging/` — Logging

| File | Purpose |
|------|---------|
| `logger.bat` | Structured batch-side logging (timestamps, levels) |

### `src/validation/` — Benchmarking

| File | Purpose |
|------|---------|
| `benchmark-runner.bat` | Run before/after benchmarks to measure impact |

### `src/ui/` — (Empty, deprecated)
Placeholder only (`.gitkeep`). Batch-side UI replaced by Python GUI.

### `src/backup_wmic/` — (Empty, deprecated)
Old WMIC-based backup approach, superseded by `src/backup/`.

---

## `clutchg/` — Python GUI Application

The interface. CustomTkinter desktop app for managing the batch optimizer.

### Root Files

| File | Purpose |
|------|---------|
| `build.py` | Build script → `dist/ClutchG.exe` |
| `pytest.ini` | Pytest configuration (markers, coverage settings) |
| `.coveragerc` | Coverage config (source=src, omit tests) |
| `requirements.txt` | Runtime deps: customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi, tkextrafont |
| `requirements-test.txt` | Test deps: pytest, pytest-cov, pytest-html, pytest-xdist, pytest-timeout, pywinauto |
| `README.md` | ClutchG overview |
| `QUICKSTART.md` | Quick start guide |
| `HANDOFF.md` | Development phase handoff notes |
| `BUG_FIX_REPORT_2026-03-24.md` | Bug fix documentation |
| `FIXES_AND_TEST.md` | Fixes and test reference |
| `install_material_icons.py` | Material icons font installer (legacy) |
| `setup_and_test.bat` | Windows batch setup + test runner |
| `setup_and_test.ps1` | PowerShell setup + test runner |

### `clutchg/src/` — Application Source

| File | Purpose |
|------|---------|
| `main.py` | **Entry point** — argparse (`--test-mode`), admin check, launches ClutchGApp |
| `app_minimal.py` | Main app controller, view routing, sidebar integration |
| `__init__.py` | Package init |

### `clutchg/src/core/` — Business Logic (13 modules)

| Module | Role |
|--------|------|
| `tweak_registry.py` | Central knowledge base — 48 `Tweak` dataclasses with full metadata |
| `action_catalog.py` | User-facing optimization "packs" with risk aggregation |
| `batch_parser.py` | Parse `.bat` files → discover tweaks, extract call structure |
| `batch_executor.py` | Execute batch scripts with output capture and error handling |
| `profile_manager.py` | SAFE/COMPETITIVE/EXTREME profile mapping and state tracking |
| `profile_recommender.py` | Recommend profiles based on system hardware |
| `backup_manager.py` | Create/restore registry backups, manage backup index |
| `flight_recorder.py` | Audit log — track every change, registry snapshots |
| `benchmark_database.py` | Store and query benchmark results |
| `system_info.py` | Hardware/OS detection (CPU, GPU, RAM, disk via psutil/pywin32) |
| `system_snapshot.py` | Full system state snapshots for comparison |
| `config.py` | JSON-based app configuration (load/save/defaults) |
| `help_manager.py` | Load and serve help content from JSON |

### `clutchg/src/gui/` — UI Layer

| File | Purpose |
|------|---------|
| `theme.py` | Color theme definitions (dark theme, Sun Valley style) |
| `style.py` | Widget styles, `bind_dynamic_wraplength()` DPI helper |
| `icons.py` | Tabler Icons codepoint constants |
| `font_loader.py` | Load bundled Figtree & icon fonts at startup |
| `font_installer.py` | System font installation logic |

### `clutchg/src/gui/views/` — 8 Views

| View | Screen | Lines |
|------|--------|-------|
| `dashboard_minimal.py` | Home — system info cards, quick actions | ~500 |
| `scripts_minimal.py` | Tweaks browser — categories, filters, detail panel | ~3,400 |
| `profiles_minimal.py` | Profile picker — SAFE/COMPETITIVE/EXTREME cards | ~400 |
| `backup_minimal.py` | Backup management — create, list, status | ~470 |
| `backup_restore_center.py` | Restore center — restore backups, timeline | ~660 |
| `help_minimal.py` | Help & docs — 9 topics, FAQ, search | ~950 |
| `settings_minimal.py` | Settings — theme, language, config | ~440 |
| `welcome_overlay.py` | First-launch welcome — onboarding flow | ~530 |

### `clutchg/src/gui/components/` — 12 Reusable Components

| Component | What It Does |
|-----------|-------------|
| `enhanced_sidebar.py` | Left navigation sidebar (collapse/expand, icons, active state) |
| `enhanced_button.py` | Custom button variants (primary, secondary, danger, ghost) |
| `glass_card.py` | Card with glassmorphism hover effect |
| `circular_progress.py` | Animated circular progress indicator |
| `execution_dialog.py` | Modal dialog during script execution (progress, log output) |
| `refined_dialog.py` | Styled dialog base class (confirm, alert, info) |
| `toast.py` | Toast notification popup (auto-dismiss) |
| `tooltip.py` | Hover tooltip |
| `icon_provider.py` | Load and render Tabler Icons from font |
| `inline_help.py` | Contextual help tooltip on info-icon click |
| `timeline.py` | Visual timeline component (flight recorder history) |
| `view_transition.py` | Animated transitions between views |

### `clutchg/src/data/` — Static Content

| File | Content |
|------|---------|
| `help_content.json` | Help system content (9+ topics, FAQ entries) |
| `risk_explanations.json` | Risk level explanations (LOW/MEDIUM/HIGH descriptions) |

### `clutchg/src/utils/` — Utilities

| Module | Purpose |
|--------|---------|
| `admin.py` | Check if running with admin privileges |
| `logger.py` | Python-side logging setup |
| `tkinter_capture/` | UI testing tools — widget walker, screenshot, client |

### `clutchg/src/assets/` — Image Assets

| File | What |
|------|------|
| `cpu_icon.png` | CPU icon for dashboard |
| `gpu_icon.png` | GPU icon for dashboard |
| `ram_icon.png` | RAM icon for dashboard |
| `clutchg_icon.png` | Application icon |

### `clutchg/src/fonts/` — Bundled Fonts

| File | Font |
|------|------|
| `Figtree-Regular.ttf` | Main UI font (regular weight) |
| `Figtree-Bold.ttf` | Main UI font (bold weight) |
| `MaterialSymbolsOutlined.ttf` | Material Symbols (legacy, not primary) |
| `tabler-icons.ttf` | **Tabler Icons v3.41.1** — the ONLY icon source |

### `clutchg/config/` — App Configuration

| File | Note |
|------|------|
| `default_config.json` | Default settings (tracked in git) |
| `user_config.json` | User overrides (gitignored) |

### `clutchg/data/` — Runtime Data (gitignored)

| Path | Content |
|------|---------|
| `backups/` | Registry backup snapshots + `backup_index.json` |
| `flight_recorder/` | Change logs + registry snapshots |
| `logs/` | Timestamped log files (`.log`) |

---

## `clutchg/tests/` — Test Suite

**Baseline: 445 passed, 64 skipped** (E2E skipped without display).

### `tests/unit/` — 15 Unit Test Files

| Test File | What It Tests |
|-----------|--------------|
| `test_tweak_registry_integrity.py` | Tweak data validation (all 48 tweaks) |
| `test_tweak_registry_coverage.py` | Every tweak mapped to correct profiles |
| `test_action_catalog.py` | Action packs & risk aggregation |
| `test_batch_parser.py` | Batch script parsing accuracy |
| `test_profile_manager.py` | Profile selection, apply, state tracking |
| `test_backup_manager.py` | Backup create/restore/index operations |
| `test_flight_recorder.py` | Audit log integrity, snapshot operations |
| `test_benchmark_database.py` | Benchmark storage and retrieval |
| `test_system_detection.py` | System info collection |
| `test_help_system.py` | Help content loading and serving |
| `test_admin.py` | Admin privilege checking |
| `test_execution_dialog.py` | Execution dialog component |
| `test_bug_fixes.py` | Regression tests for specific bugs |
| `test_core_coverage.py` | Core module coverage expansion |
| `test_coverage_expansion.py` | Additional coverage for uncovered paths |

### `tests/integration/` — 2 Integration Tests

| File | Scope |
|------|-------|
| `test_clutchg_integration.py` | Cross-module workflows |
| `test_backup_restore.py` | Full backup/restore end-to-end |
| `INTEGRATION_TEST_REPORT.md` | Test results documentation |

### `tests/e2e/` — E2E Tests (Page Object Pattern)

| Path | Purpose |
|------|---------|
| `conftest.py` | E2E-specific fixtures |
| `fixtures/app_fixture.py` | Application launch/teardown |
| `pages/base_page.py` | Base page object |
| `pages/dashboard_page.py` | Dashboard page interactions |
| `pages/profiles_page.py` | Profiles page interactions |
| `pages/scripts_page.py` | Scripts page interactions |
| `pages/backup_page.py` | Backup page interactions |
| `pages/settings_page.py` | Settings page interactions |
| `tests/test_navigation.py` | Basic navigation flow |
| `tests/test_navigation_comprehensive.py` | Full navigation coverage |
| `tests/test_profiles.py` | Profile selection E2E |
| `tests/test_settings.py` | Settings modification E2E |

---

## `docs/` — Documentation (42 entries)

### Research Series (01–16)

| File | Topic |
|------|-------|
| `01-research-overview.md` | Research methodology and scope |
| `02-repo-analysis/` | **28 individual repo analyses** (one .md per analyzed optimizer) |
| `03-tweak-taxonomy.md` | 48 tweaks classified into 10 categories |
| `04-risk-classification.md` | LOW/MEDIUM/HIGH risk framework |
| `05-windows-internals.md` | Windows kernel, scheduler, memory internals |
| `06-performance-impact.md` | Measured performance impact per tweak |
| `07-best-practices.md` | Optimizer design best practices |
| `08-design-your-own-optimizer.md` | Guide: building a Windows optimizer |
| `09-final-architecture.md` | ClutchG architecture decisions |
| `10-complete-repo-ranking.md` | Ranking of all 28 analyzed repos |
| `11-development-plan.md` | Development roadmap and milestones |
| `12-extension-research.md` | Future research directions |
| `13-testing-procedures.md` | Testing methodology |
| `14-testing-checklist.md` | Pre-release testing checklist |
| `15-user-guide-th.md` | User guide (Thai) |
| `16-user-guide-en.md` | User guide (English) |

### Architecture & Design

| File | Content |
|------|---------|
| `ARCHITECTURE.md` | System architecture overview |
| `PROJECT_STRUCTURE.md` | Project structure reference |
| `clutchg_technical_spec.md` | Technical specification |
| `clutchg_quick_reference.md` | Developer quick reference |
| `clutchg_ux_audit.md` | UX audit findings and fixes |
| `evidence-based-implementation-summary.md` | Evidence for each implemented tweak |
| `EXTREME-TWEAKS.md` | Extreme profile tweak documentation |
| `HANDOFF.md` | Development phase handoff |
| `SUGGESTION-GUIDE.md` | How ClutchG suggestions work |

### UI Redesign

| File | Content |
|------|---------|
| `UI-UX-REDESIGN-PLAN.md` | Full redesign plan |
| `REDESIGN-IMPLEMENTATION-GUIDE.md` | Implementation details |
| `REDESIGN-PROGRESS.md` | Progress tracker |
| `REDESIGN-QUICK-START.md` | Quick start for redesign work |
| `REDESIGN-SUMMARY-TH.md` | Summary in Thai |
| `design-mockups/` | 3 HTML mockups (phase 1–3) |
| `design-specs/` | 3 markdown specs (phase 1–3) |

### ISO 29110 — ClutchG (`docs/iso29110-clutchg/`)

| File | Work Product |
|------|-------------|
| `01-Project-Plan.md` | Project plan (gitignored — contains personal info) |
| `02-SRS.md` | Software Requirements Specification |
| `03-SDD.md` | Software Design Description |
| `04-Test-Plan.md` | Test plan |
| `05-Test-Record.md` | Test execution records |
| `06-Traceability-Record.md` | Requirements → Design → Test traceability |
| `07-Change-Request.md` | Change request log |
| `08-Progress-Status-Record.md` | Progress status reports |
| `09-Configuration-Plan.md` | Configuration management plan |
| `10-User-Manual.md` | User manual |
| `Appendix-A-UML-Diagrams.md` | UML class/sequence/activity diagrams |
| `README.md` | ISO document set overview |

### ISO 29110 — Generic Templates (`docs/iso29110/`)

| Path | Content |
|------|---------|
| `templates/` | Reusable ISO 29110 document templates |
| `forms/` | Process forms |
| `examples/` | Filled-in examples |
| `pm-process/` | Project Management process guide |
| `si-process/` | Software Implementation process guide |
| `work-products.md` | Work product definitions |
| `service-delivery.md` | Service delivery process |
| `README.md` | Template set overview |

### Academic Files (gitignored)

| File | Content |
|------|---------|
| `_proposal_extract_1.txt` | Proposal text extraction |
| `_proposal_extract_2.txt` | Proposal text extraction |
| `_proposal_extract_3.txt` | Proposal text extraction |
| `proposal-vs-current-state.md` | Proposal vs implementation comparison |
| `notion-imports/` | Converted Notion exports (raw, extracted, final) |
| `*.pdf` (3 files) | Thai university forms — topic approval, proposal forms |

---

## `clutchg/docs/` — ClutchG-Specific Docs (14 files)

| File | Content |
|------|---------|
| `DEVELOPER_GUIDE.md` | Developer setup and contribution guide |
| `USER_GUIDE.md` | End-user guide |
| `UI_REDESIGN_PLAN.md` | UI redesign plan (references UX/design-reference/) |
| `SCORING_SYSTEM.md` | Tweak scoring methodology |
| `TH_EN_LOCALIZATION_GUIDELINE.md` | Bilingual content guidelines |
| `GLM_WORK_PLAN.md` | GLM (Quick Actions) implementation plan |
| `GLM-UI-V1-HANDOFF.md` | Quick Actions V1 feature handoff |
| `GLM-UI-V1-TEST-MATRIX.md` | Quick Actions test scenarios (30+ cases) |
| `GLM-UI-V1-CHANGELOG.md` | Quick Actions implementation changelog |
| `phase10-handoff.md` | Phase 10 testing strategy and next steps |
| `project-description-prompt.md` | AI prompt for project context |
| `deepresearch-prompt.md` | Deep research prompt template |
| `deepresearch-full-prompt.md` | Full deep research prompt |
| `BUG_FIX_REPORT_2026-03-24.md` | Bug fix documentation |

---

## `thesis/` — Thesis Writing (gitignored)

### `thesis/THESIS_DOCS/` — 10 Structured Sections

| Folder | Section |
|--------|---------|
| `00-METADATA/` | Title, abstract, acknowledgments |
| `01-LITERATURE-REVIEW/` | Related work and literature survey |
| `02-RESEARCH-METHODOLOGY/` | Research design and methods |
| `03-SYSTEM-ANALYSIS/` | System requirements analysis |
| `04-REQUIREMENTS-ENGINEERING/` | Functional/non-functional requirements |
| `05-ARCHITECTURE-DESIGN/` | Architecture and design patterns |
| `06-IMPLEMENTATION/` | Implementation details and code explanations |
| `07-TESTING-QUALITY/` | Testing strategy, results, quality metrics |
| `08-DESIGN-THINKING/` | Design thinking process documentation |
| `09-MODELS-TECHNICAL/` | Technical models and diagrams |
| `10-DELIVERABLES/` | Final deliverable summaries |

Plus: `images/`, README, structure guide, overview/developer/user docs.

### `thesis/thesis-chapters/` — 8 Markdown Chapters

| File | Chapter |
|------|---------|
| `00-abstract-thai.md` | Thai abstract |
| `00-abstract-english.md` | English abstract |
| `01-introduction.md` | Chapter 1: Introduction |
| `02-literature-review.md` | Chapter 2: Literature Review |
| `03-methodology.md` | Chapter 3: Research Methodology |
| `04-implementation.md` | Chapter 4: Implementation |
| `05-results.md` | Chapter 5: Results |
| `06-testing-results.md` | Chapter 6: Testing Results |

---

## `research/` — Raw Research Material (mostly gitignored)

| Path | Content | Gitignored? |
|------|---------|------------|
| `windows-optimizer-research/` | Analysis of 28+ repos: `analysis/`, `architecture/`, `docs/`, `repos/`, `taxonomy/` | `repos/` yes (~1GB) |
| `tkinter-GUI-awesome/` | 38+ cloned GUI reference repos | Partially |
| `awesome-ai-research-writing-main/` | Cloned AI research writing reference | Yes |
| `Ideas and research/` | Raw research notes and PDFs | Yes |
| `notion/` | Raw Notion database exports | Yes |
| `repos.txt` | List of all researched repository URLs | No |

---

## `UX/` — UI/UX Design Assets (24 entries)

| Path | Content |
|------|---------|
| `01-dashboard-home.png` through `11-settings.png` | Current UI screenshots (numbered by view) |
| `design-reference/` | 13 reference screenshots from other apps |
| `Redesign/` | 14 redesign mockup PNGs + `redesign_guideline.md` |
| `live/` | Live-captured screenshots + `manifest.json` + `current/` + phase mockups |
| `UI captured/` | Previously captured UI states |
| `3/` | Date-based capture subfolder |
| `capture_all.py` | Script to capture all views automatically |
| `capture_views.py` | View-specific capture script |
| `INDEX.md` | UX asset index |
| `test_shot.png`, `test_visible.png`, `test2.png` | Test screenshots |

---

## `scripts/` — Standalone Python Tooling (gitignored)

| File | Purpose |
|------|---------|
| `capture_ui_views.py` | Automated UI view capture |
| `convert_notion_to_md.py` | Convert Notion export → markdown |
| `download_notion.py` / `_v2.py` / `_v3.py` | Notion API downloaders |
| `download_notion_debug.py` | Debug version of downloader |
| `import_notion.py` | Notion content importer |
| `run_import.py` | Import runner |
| `extract_text.py` | PDF/text extraction tool |
| `icon-tools/` | Icon finder, picker generator, icon data JSON, HTML picker |
| `utils/` | Shared utilities — `file_utils.py`, `notion_utils.py`, `pdf_utils.py` |
| `requirements.txt` | Script-specific dependencies |
| `README.md` | Scripts documentation |

---

## `skills/` — AI Agent Skills

| Path | Content |
|------|---------|
| `windows-optimizer-expert.md` | Windows optimizer domain expert skill definition |
| `windows-optimizer-expert.json` | Skill metadata |
| `bug-hunter/` | Full bug-hunting toolkit (agents, docs, prompts, templates, schemas) |
| `INSTALLATION.md` | Skill installation guide |
| `QUICK_REFERENCE.md` | Skills quick reference |
| `README.md` | Skills overview |

---

## `img/` — Miscellaneous Images (gitignored)

12 PNG files: UUID-named screenshots, `C.GG-Photoroom.png` (logo), `image.png`.

---

## `psi/` — Agent Handoff Inbox

| Path | Content |
|------|---------|
| `psi/inbox/handoff/` | Session handoff files for AI agent continuity |

---

## Hidden / Config Directories

| Directory | Purpose | Tracked? |
|-----------|---------|----------|
| `.git/` | Git repository | N/A |
| `.github/workflows/ci.yml` | GitHub Actions CI | Yes |
| `.agents/` | AI agent config (skills, prompts) | Gitignored |
| `.claude/` | Claude AI skills & config | Partially |
| `.opencode/` | OpenCode skills & config | Gitignored |
| `.codex/` | Codex configuration | Gitignored |
| `.kilocode/` | Kilocode config (has `mcp.json`) | Gitignored |
| `.windsurf/` | Windsurf configuration | Gitignored |
| `.factory/` | Factory configuration | Gitignored |
| `.letta/` | Letta configuration | Gitignored |
| `.benchmarks/` | Benchmark data storage | Gitignored |
| `.bug-hunter/` | Bug hunter runtime data | Gitignored |
| `.superpowers/` | Superpowers skill config | Gitignored |

---

## Quick Reference: Key Entry Points

| What | Command / Path |
|------|---------------|
| Run GUI | `python clutchg\src\main.py` (from repo root) |
| Run GUI (test mode) | `python clutchg\src\main.py --test-mode` |
| Build EXE | `cd clutchg && python build.py` |
| Run batch optimizer | `src\optimizer.bat` (admin CMD) |
| Run all tests | `cd clutchg && pytest` |
| Run unit tests | `cd clutchg && pytest tests\unit -m unit` |
| Run integration tests | `cd clutchg && pytest tests\integration -m integration` |
| Run E2E tests | `cd clutchg && pytest tests\e2e -m e2e --app-path src\main.py` |
| Check syntax | `python -m compileall clutchg/src` |

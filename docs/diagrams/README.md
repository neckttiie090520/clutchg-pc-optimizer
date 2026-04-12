# ClutchG PC Optimizer — Thesis Diagrams

All UML and supplementary diagrams for the ClutchG independent study thesis.
Drawn in [draw.io](https://app.diagrams.net/), exported as PNG at 2x scale with 20px border.

---

## Diagram Index

| # | Diagram | Type | Thesis Section |
|---|---------|------|----------------|
| 01 | [System Architecture Overview](#01-system-architecture-overview) | Architecture | Ch.3 System Design |
| 02 | [Batch Optimizer Execution Flow](#02-batch-optimizer-execution-flow) | Flowchart | Ch.3 System Design |
| 03 | [GUI Navigation Flow](#03-gui-navigation-flow) | Flowchart | Ch.3 System Design |
| 04 | [Tweak Lifecycle](#04-tweak-lifecycle) | Activity | Ch.3 System Design |
| 05 | [Risk Classification Framework](#05-risk-classification-framework) | Custom / Entity | Ch.2 Literature Review |
| 06 | [Module Dependency Map](#06-module-dependency-map) | Component | Ch.3 System Design |
| 07 | [Use Case Diagram](#07-use-case-diagram) | UML Use Case | Ch.3 Requirements |
| 08 | [Class Diagram (Full)](#08-class-diagram-full) | UML Class | Appendix |
| 08a | [Class Diagram (Simplified)](#08a-class-diagram-simplified) | UML Class | Ch.3 System Design |
| 08b | [Class Diagram — Data Models](#08b-class-diagram-data-models) | UML Class | Appendix |
| 09 | [Sequence Diagram](#09-sequence-diagram) | UML Sequence | Ch.3 System Design |
| 10 | [Deployment Diagram](#10-deployment-diagram) | UML Deployment | Ch.3 System Design |
| 11 | [Conceptual Framework](#11-conceptual-framework) | Custom | Ch.1 Introduction |
| 12 | [Project Timeline (Gantt Chart)](#12-project-timeline-gantt-chart) | Gantt | Ch.1 / Project Plan |
| 13 | [Tweak State Diagram](#13-tweak-state-diagram) | UML State | Ch.3 System Design |
| 14 | [PC Score Scoring Flow](#14-pc-score-scoring-flow) | Activity | Ch.3 System Design |
| 15 | [Unified Preset Recommendation Flow](#15-unified-preset-recommendation-flow) | Flowchart | Ch.3 System Design |
| 16 | [Tech Stack](#16-tech-stack) | Tech Stack | Ch.3 System Design |
| 16b | [Tech Stack — Architecture View](#16b-tech-stack-architecture-view) | Tech Stack | Ch.3 System Design |

---

## 01 — System Architecture Overview

**Source:** [`drawio/01-system-architecture-overview.drawio`](drawio/01-system-architecture-overview.drawio)

High-level view of the entire ClutchG system showing the three main layers:
- **ClutchG GUI** (Python/CustomTkinter) — the user-facing desktop application
- **Batch Optimizer Engine** (`src/`) — modular `.bat` scripts organized by function
- **Windows OS** — the target system being optimized

Shows how the GUI discovers and invokes batch scripts, how scripts interact with Windows subsystems (Registry, Services, Power, Network, etc.), and where safety mechanisms (backup, rollback, flight recorder) sit in the pipeline.

![01-system-architecture-overview](img/01-system-architecture-overview.png)

---

## 02 — Batch Optimizer Execution Flow

**Source:** [`drawio/02-batch-optimizer-execution-flow.drawio`](drawio/02-batch-optimizer-execution-flow.drawio)

Step-by-step flowchart of what happens when a user runs an optimization profile through the batch engine:
1. Admin rights check
2. System detection (OS version, hardware)
3. Backup creation (registry + restore point)
4. Profile loading (SAFE / COMPETITIVE / EXTREME)
5. Module execution with validation
6. Flight recorder logging
7. Result summary

Covers error paths and rollback triggers.

![02-batch-optimizer-execution-flow](img/02-batch-optimizer-execution-flow.png)

---

## 03 — GUI Navigation Flow

**Source:** [`drawio/03-gui-navigation-flow.drawio`](drawio/03-gui-navigation-flow.drawio)

Shows how users navigate through the ClutchG desktop application. Maps the sidebar navigation to each view:
- Dashboard (system info, quick actions)
- Scripts (browse/run batch modules)
- Profiles (SAFE/COMPETITIVE/EXTREME selection)
- Backup & Restore
- Help
- Settings

Includes view transitions, dialog popups, and the Welcome screen first-run flow.

![03-gui-navigation-flow](img/03-gui-navigation-flow.png)

---

## 04 — Tweak Lifecycle

**Source:** [`drawio/04-tweak-lifecycle.drawio`](drawio/04-tweak-lifecycle.drawio)

Activity diagram tracing a single tweak from research to deployment:
1. Research & evidence gathering
2. Risk classification (LOW/MEDIUM/HIGH)
3. Registration in TweakRegistry
4. Profile assignment
5. Batch script implementation
6. GUI discovery via BatchParser
7. User applies tweak
8. Logging & rollback availability

![04-tweak-lifecycle](img/04-tweak-lifecycle.png)

---

## 05 — Risk Classification Framework

**Source:** [`drawio/05-risk-classification-framework.drawio`](drawio/05-risk-classification-framework.drawio)

Visualizes the three-tier risk model used to classify all 48 tweaks:
- **LOW** risk — safe for all users, minimal system impact
- **MEDIUM** risk — gaming-focused, may affect non-gaming workflows
- **HIGH** risk — aggressive changes, potential stability trade-offs

Shows classification criteria (reversibility, scope of change, failure impact) and how risk levels map to profiles (SAFE = LOW only, COMPETITIVE = LOW+MEDIUM, EXTREME = all).

![05-risk-classification-framework](img/05-risk-classification-framework.png)

---

## 06 — Module Dependency Map

**Source:** [`drawio/06-module-dependency-map.drawio`](drawio/06-module-dependency-map.drawio)

Component diagram showing how batch modules in `src/core/` depend on each other and on shared infrastructure (`logger.bat`, `flight-recorder.bat`, `validator.bat`). Groups modules by category:
- Power & Performance
- Services & Telemetry
- Network & Input
- Storage & Maintenance
- GPU & Display

![06-module-dependency-map](img/06-module-dependency-map.png)

---

## 07 — Use Case Diagram

**Source:** [`drawio/07-use-case-diagram.drawio`](drawio/07-use-case-diagram.drawio)

UML Use Case diagram with two actors:
- **User** — views system info, selects profiles, applies tweaks, creates backups, restores settings
- **System (Windows OS)** — executes registry changes, manages services, creates restore points

Use cases cover the full workflow: view dashboard, browse tweaks, apply profile, backup/restore, view help, change settings. Includes `<<include>>` and `<<extend>>` relationships.

![07-use-case-diagram](img/07-use-case-diagram.png)

---

## 08 — Class Diagram (Full)

**Source:** [`drawio/08-class-diagram.drawio`](drawio/08-class-diagram.drawio)

Complete UML class diagram showing all classes in `clutchg/src/` with attributes, methods, and relationships. Contains all core, GUI, and utility classes. Best viewed at full zoom or printed on A3.

> This is the reference version for the appendix. For the thesis body, use 08a (simplified) below.

![08-class-diagram](img/08-class-diagram.png)

---

## 08a — Class Diagram (Simplified)

**Source:** [`drawio/08a-class-diagram-simplified.drawio`](drawio/08a-class-diagram-simplified.drawio)

Simplified class diagram for the thesis body chapter. Shows the key architectural classes grouped into:
- **App Layer** — `ClutchGApp` (main controller)
- **Core Business Logic** — `ProfileManager`, `TweakRegistry`, `BatchExecutor`, `BatchParser`, `BackupManager`, `SystemDetector`, `ActionCatalog`, `FlightRecorder`, `ConfigManager`

Relationships: composition ("owns"), usage ("uses"), dependency arrows. Omits GUI view classes and data model details (those are in 08b).

![08a-class-diagram-simplified](img/08a-class-diagram-simplified.png)

---

## 08b — Class Diagram — Data Models

**Source:** [`drawio/08b-class-diagram-datamodels.drawio`](drawio/08b-class-diagram-datamodels.drawio)

UML class diagram focusing on data structures and enums:
- `Tweak` dataclass (id, name, category, risk_level, expected_gain, etc.)
- `RiskLevel` enum (LOW, MEDIUM, HIGH)
- `TweakCategory` enum (10 categories)
- `ProfileType` enum (SAFE, COMPETITIVE, EXTREME)
- `BackupEntry`, `SystemInfo`, `ActionResult` dataclasses

Shows field types, enum values, and relationships between data models.

![08b-class-diagram-datamodels](img/08b-class-diagram-datamodels.png)

---

## 09 — Sequence Diagram

**Source:** [`drawio/09-sequence-diagram.drawio`](drawio/09-sequence-diagram.drawio)

UML sequence diagram showing the message flow when a user applies an optimization profile:

`User` -> `ClutchGApp` -> `ProfileManager` -> `BackupManager` -> `BatchExecutor` -> `Windows OS`

Covers: profile selection, backup creation, tweak iteration, batch script execution, result collection, flight recorder logging, and UI feedback.

![09-sequence-diagram](img/09-sequence-diagram.png)

---

## 10 — Deployment Diagram

**Source:** [`drawio/10-deployment-diagram.drawio`](drawio/10-deployment-diagram.drawio)

UML deployment diagram showing the physical runtime environment:
- **User's PC** node containing:
  - `ClutchG.exe` (Python/CustomTkinter, packaged via PyInstaller)
  - Batch scripts (`src/`)
  - Windows subsystems (Registry, Services, PowerCfg, etc.)
- Artifacts: `.bat` files, `.json` configs, log files, registry backups

Shows `<<artifact>>` and `<<execute>>` stereotypes.

![10-deployment-diagram](img/10-deployment-diagram.png)

---

## 11 — Conceptual Framework

**Source:** [`drawio/11-conceptual-framework.drawio`](drawio/11-conceptual-framework.drawio)

High-level research framework connecting:
- **Input:** 23 open-source optimizer repos analyzed, 50,000+ lines reviewed
- **Process:** Tweak classification, risk framework, evidence-based filtering
- **Output:** ClutchG tool (batch engine + GUI), thesis documentation

Shows the relationship between research methodology, the tool's design decisions, and the expected outcomes (5-15% performance improvement, safety-first approach).

![11-conceptual-framework](img/11-conceptual-framework.png)

---

## 12 — Project Timeline (Gantt Chart)

**Source:** [`drawio/12-gantt-chart.drawio`](drawio/12-gantt-chart.drawio)

Gantt chart showing the project schedule across phases:
- Literature review & repo analysis
- System design & architecture
- Batch engine implementation
- GUI development
- Testing & quality assurance
- Thesis writing & documentation
- ISO 29110 work products

![12-gantt-chart](img/12-gantt-chart.png)

---

## 13 — Tweak State Diagram

**Source:** [`drawio/13-state-diagram.drawio`](drawio/13-state-diagram.drawio)

UML state diagram for a tweak's runtime lifecycle:
- **Registered** — tweak exists in TweakRegistry
- **Selected** — user chose it (via profile or manual)
- **Validating** — safety checks running
- **Applying** — batch script executing
- **Applied** — change active on system
- **Failed** — error during application
- **Rolled Back** — user or system reverted the change

Shows transitions, guards, and error recovery paths.

![13-state-diagram](img/13-state-diagram.png)

---

## 14 — PC Score Scoring Flow

**Source:** [`drawio/14-pc-score-scoring-flow.drawio`](drawio/14-pc-score-scoring-flow.drawio)

Activity diagram showing the complete PC Score calculation pipeline:

1. App startup spawns a **daemon thread** (non-blocking)
2. `SystemDetector.detect_all()` runs parallel hardware detection (CPU, GPU, RAM, Storage)
3. CPU and GPU names go through **BenchmarkDatabase fuzzy matching** (3-stage: exact → regex key parts → difflib cutoff=0.5)
4. Raw PassMark scores are **normalized** to component weights: CPU (0–30), GPU (0–30), RAM (0–20), Storage (0–10)
5. Total score = sum of all components (max ~90 practical)
6. **Tier classification**: Entry (<30), Mid (30–49), High (50–69), Enthusiast (70+)
7. `SystemProfile` is built and returned via `window.after(0)` callback to the GUI main thread
8. Dashboard displays the circular score ring with tier-colored badge

Color coding: Blue = hardware detection, Orange = fuzzy matching, Green = scoring/normalization, Purple = GUI thread.

![14-pc-score-scoring-flow](img/14-pc-score-scoring-flow.png)

---

## 15 — Unified Preset Recommendation Flow

**Source:** [`drawio/15-recommendation-decision-tree.drawio`](drawio/15-recommendation-decision-tree.drawio)

Flowchart showing the single authoritative recommendation path in ClutchG. All callers — Dashboard, Scripts view, and legacy delegate methods — enter through `recommend_preset(profile)`.

**Null-profile guard:** If no `SystemProfile` is provided, the function returns `SAFE` immediately.

**Evidence sufficiency gate:** The profile must pass four checks before the score-based path is used:
1. `total_score` is numeric (not None)
2. `form_factor` is known (not "unknown")
3. RAM is positive (> 0 GB)
4. At least one of CPU or GPU has `benchmark_matched = True`

If any check fails, the flow drops to the **fallback heuristic** branch.

**Primary path (score-based):**
- Score ≥ 80 + desktop + RAM ≥ 16 GB → **EXTREME**
- Score ≥ 50 + RAM ≥ 8 GB → **COMPETITIVE**
- Otherwise → **SAFE**

**Fallback path (conservative heuristic):**
- Laptop → **SAFE**
- Desktop with mid / high / enthusiast tier → **COMPETITIVE**
- Otherwise → **SAFE**
- **Fallback never returns EXTREME.**

Both Dashboard and Scripts view consume the same `recommend_preset()` result. The legacy methods `SystemDetector.recommend_profile()` and `TweakRegistry.suggest_preset()` delegate to it internally.

![15-recommendation-decision-tree](img/15-recommendation-decision-tree.png)

---

## 16 — Tech Stack

**Source:** [`drawio/16-tech-stack.drawio`](drawio/16-tech-stack.drawio)

Layered technology stack diagram showing all tools, libraries, and subsystems that make up ClutchG, organized into 6 horizontal tiers:

1. **GUI Layer** (blue) — Python 3, CustomTkinter, Tkinter, Pillow, tkextrafont, Figtree font, Tabler Icons
2. **Core Logic** (green) — psutil, py-cpuinfo, WMI, pywin32, difflib, JSON, dataclasses
3. **Batch Engine** (orange) — CMD/Batch, PowerShell, reg.exe, sc.exe, powercfg, bcdedit, netsh, fsutil
4. **Windows Subsystems** (pink) — Registry, Services (SCM), Power Plans, Network (TCP/IP), BCD Store, NTFS, GPU (NVIDIA/AMD), AppX/UWP
5. **Safety & Logging** (light purple) — System Restore, reg export, Flight Recorder, Structured Logger, Validator, Rollback Engine
6. **DevOps & Testing** (purple) — PyInstaller, pytest, pywinauto, pytest-cov, pytest-xdist, Git, nvidia-smi

Inter-layer arrows show the interaction types: calls, invokes, modifies, protects, builds & tests.

![16-tech-stack](img/16-tech-stack.png)

---

## 16b — Tech Stack — Architecture View

**Source:** [`drawio/16b-tech-stack-architecture-view.drawio`](drawio/16b-tech-stack-architecture-view.drawio)

Alternative architecture-aligned view of the same technology stack, using a C4-inspired bounded-context layout instead of horizontal tiers. Technologies are grouped into 6 zones arranged in a 2-column grid:

1. **User Interface / GUI** (blue) — Python 3, CustomTkinter, Tkinter, Pillow, tkextrafont, Figtree, Tabler Icons
2. **Core Logic / Application Services** (green) — psutil, py-cpuinfo, WMI, pywin32, difflib, JSON, dataclasses
3. **Batch Execution Engine** (orange) — CMD/Batch, PowerShell, reg.exe, sc.exe, powercfg, bcdedit, netsh, fsutil
4. **Windows Subsystems (OS Targets)** (pink) — Registry, Services (SCM), Power Plans, Network (TCP/IP), BCD Store, NTFS, GPU Subsystem, AppX/UWP
5. **Safety, Logging & Recovery** (yellow) — System Restore, reg export, Flight Recorder, Structured Logger, Validator, Rollback Engine
6. **DevOps & Testing** (purple) — PyInstaller, pytest, pywinauto, pytest-cov, pytest-xdist, Git, nvidia-smi

Each technology card distinguishes **Main Technology** (bold border) from **Secondary / Utility** (light border). Inter-zone arrows show architectural relationships: calls, invokes, modifies, protects, builds & tests.

### Comparison: 16 vs 16b

| Aspect | 16 (Row-Based) | 16b (Architecture View) |
|--------|----------------|------------------------|
| Layout | 6 horizontal rows, top-to-bottom flow | 2-column grid, 6 bounded-context zones |
| Visual metaphor | Layer cake / stack | Architecture map / C4-inspired containers |
| Technology logos | Embedded brand logos (base64 PNG) | Native draw.io shapes only (CLI-safe) |
| Emphasis | What technologies exist, organized by layer | How technologies relate to architectural responsibilities |
| Arrows | Vertical inter-layer arrows | Cross-zone directional arrows with labels |
| Best for | Quick tech inventory, visual appeal with logos | Architectural reasoning, system comprehension |

**Thesis recommendation:** Use **16** (row-based with logos) in Chapter 3 for visual appeal and readability — it's more immediately scannable for a reader. Use **16b** (architecture view) in the appendix or SDD document where architectural context matters more. The two complement each other well.

![16b-tech-stack-architecture-view](img/16b-tech-stack-architecture-view.png)

---

## Design Conventions

All diagrams follow these rules:

| Rule | Value |
|------|-------|
| Font | Segoe UI |
| Title size | 16pt bold |
| Color coding | Blue = View/Info, Green = Optimize/Business, Orange = Backup/Safety, Red = Security, Yellow = Components, Purple = Settings/Infrastructure |
| Export | PNG, scale 2x, 20px border |
| Source format | `.drawio` (editable in draw.io desktop or web) |
| Legend | Included in each diagram where color coding is used |

## How to Edit

1. Open any `.drawio` file from [`drawio/`](drawio/) in [draw.io](https://app.diagrams.net/) (web) or the desktop app
2. Edit as needed
3. Export: `File > Export as > PNG` with scale 2x and 20px border
4. Save the PNG to [`img/`](img/)
5. Or via CLI:
   ```
   "C:\Program Files\draw.io\draw.io.exe" --export --format png --scale 2 --border 20 --output img/<name>.png drawio/<name>.drawio
   ```

## Folder Structure

```
docs/diagrams/
  README.md          <- This file (diagram gallery)
  drawio/            <- Editable source files (.drawio)
  img/               <- Exported PNG images
```

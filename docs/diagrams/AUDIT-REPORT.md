# Audit Report — docs/diagrams/

> **ผู้ตรวจ:** Cascade (AI Agent)
> **วันที่:** 2026-04-06
> **ขอบเขต:** 13 diagrams (drawio + PNG) ใน `docs/diagrams/`
> **เกณฑ์ตรวจ:** SE 701 (Architecture, OO Design), SE 702 (ISO 29110), SE 721 (Use Cases), SE 725 (V&V), SE 781 (PM)

---

## สรุปผลตรวจ

| สถานะ | จำนวน |
|-------|-------|
| PASS (ไม่มีปัญหา) | 7 |
| WARN (ปัญหาเล็กน้อย) | 4 |
| FAIL (ต้องแก้ไข) | 2 |

---

## Diagram 01 — System Architecture Overview

**ประเภท UML:** Layered Architecture Diagram (HLD)
**เกณฑ์:** SE 701 — Architecture Patterns, Coupling/Cohesion

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Layers ถูกต้อง | PASS | 4 layers: Presentation → Business Logic → Batch Engine → Windows OS |
| Layer dependency ทิศทางเดียว (top-down) | PASS | ลูกศรชี้ลงเท่านั้น — imports, delegates, OS API calls |
| Components ครบ | WARN | **แสดง "7 Views" แต่ ClutchG มี 8 views** (Dashboard, Scripts, Profiles, Backup, Restore, Help, Settings, Welcome) |
| Color-coded legend | PASS | Legend ครบ 7 สี + readable |
| Safety components highlighted | PASS | Safety Scripts + Backup Scripts เน้นสีแยก |

**Verdict: WARN**
- แก้ "7 Views" → "8 Views" (เพิ่ม Welcome view)

---

## Diagram 02 — Batch Optimizer Execution Flow

**ประเภท UML:** Activity Diagram
**เกณฑ์:** SE 701 — SDLC, SE 721 — Activity Diagrams, SE 725 — V&V

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| มี Initial/Final node | PASS | Black circle start + end |
| Decision nodes ถูกต้อง | PASS | Diamond shapes สำหรับ Admin?, Profile?, Benchmark? |
| Safety flow ครบ | PASS | 6 steps: snapshot → restore point → backup → apply → benchmark → summary |
| Admin check ก่อน execute | PASS | กรณี No Admin → show error → exit |
| EXTREME confirmation | PASS | มี Y/N confirmation ก่อน apply EXTREME |
| Legend | PASS | ครบ 8 สี categorized |

**Verdict: PASS**
- Activity diagram คุณภาพดี ครอบคลุมทุก flow path

---

## Diagram 03 — GUI Navigation Flow

**ประเภท:** Navigation Flow Diagram
**เกณฑ์:** SE 701 — Architecture, SE 721 — UI Requirements

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Views ครบ | WARN | **แสดง 7 Views แต่ต้องเป็น 8** — ขาด Welcome view ใน row (แม้มี Welcome Overlay ข้างล่าง) |
| Layer separation แสดง | PASS | GUI → Core → Batch Engine แบ่งชัดเจน |
| Entry point ถูกต้อง | PASS | main.py → App Controller → navigate(view) |
| Default view ระบุ | PASS | "Dashboard is default view" |
| Welcome flow | PASS | "first launch" → Welcome Overlay (first run only) |

**Verdict: WARN**
- View count ใน header ควรเป็น "8 Views" (รวม Welcome) หรือระบุชัดว่า Welcome เป็น overlay ไม่ใช่ view เต็ม

---

## Diagram 04 — Tweak Lifecycle

**ประเภท:** Process Flow / Lifecycle Diagram
**เกณฑ์:** SE 701 — Design, SE 702 — Process, Domain Knowledge

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| 7 phases ครบ | PASS | Discovery → Classification → Validation → Backup → Execution → Logging → Rollback |
| Rollback loop-back | PASS | เส้นประ "Rollback restores to Backup state" |
| Risk levels แสดง | PASS | Legend: LOW (SAFE), MEDIUM (COMPETITIVE), HIGH (EXTREME) |
| Evidence-based flow | PASS | Phase 1 "Research 28 repos, Identify 48 tweaks" |
| Safety-first | PASS | Phase 3 "Verify safety rules" ก่อน execute |

**Verdict: PASS**
- Lifecycle diagram ครอบคลุมดีเยี่ยม

---

## Diagram 05 — Risk Classification Framework

**ประเภท:** Decision Tree / Flowchart
**เกณฑ์:** SE 781 — Risk Management, SE 701 — Safety, Domain Knowledge

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Safety gate แรก | PASS | "Modifies security features?" → Yes → REJECTED |
| Evidence gate | PASS | "Evidence-based & reversible?" → No → REJECTED (myth/placebo) |
| 3-tier classification | PASS | System stability impact → Minimal/Moderate/Significant → LOW/MEDIUM/HIGH |
| Profile mapping | PASS | LOW→SAFE, MEDIUM→COMPETITIVE, HIGH→EXTREME |
| Cumulative note | PASS | "Profiles are cumulative: COMPETITIVE includes all SAFE tweaks..." |
| HTML entity bug | WARN | **"&amp;amp;" ปรากฏใน decision node** — ควรเป็น "&" ใน "Evidence-based & reversible?" |

**Verdict: WARN**
- แก้ HTML entity `&amp;amp;` → `&amp;` ใน drawio source ให้ render เป็น "&" ที่ถูกต้อง

---

## Diagram 06 — Module Dependency Map

**ประเภท:** Component Dependency Diagram
**เกณฑ์:** SE 701 — Coupling/Cohesion, Architecture

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Dependency direction ถูกต้อง | PASS | Top-down: Views → Components → Infrastructure; AppController → ProfileManager → TweakRegistry |
| Hub/Root identified | PASS | profile_manager (HUB), tweak_registry (ROOT) |
| Line styles differentiated | PASS | Solid = direct, Dashed = lazy, Dotted = TYPE_CHECKING |
| Leaf modules ครบ | PASS | 8 leaf modules listed |
| Batch Engine boundary | PASS | subprocess.run() crossing boundary |
| No circular dependencies | PASS | ไม่มีลูกศรย้อนกลับขึ้น |

**Verdict: PASS**
- Dependency map คุณภาพดี แสดง coupling ชัดเจน

---

## Diagram 07 — Use Case Diagram

**ประเภท UML:** Use Case Diagram
**เกณฑ์:** SE 721 — Use Case Modeling (Include/Extend)

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| System boundary | PASS | "ClutchG PC Optimizer" rectangle |
| Actors ถูกต้อง | WARN | **มี 2 actors (User, Windows OS) แต่ SRS + Appendix-A กำหนด 3 primary actors** (Beginner, Gamer, Power User) — diagram รวมเป็น "User" เดียว |
| Use Cases ครบ | PASS | 13 UCs visible (Appendix-A มี 16 แต่บางตัวรวมกัน เช่น Export/Import) |
| <<include>> ถูกทิศ | PASS | "Select & Apply Profile" --<<include>>--> "Create Backup" — ลูกศรจาก base ไป included |
| <<extend>> ถูกทิศ | PASS | "Scan System Hardware" --<<extend>>--> "View Dashboard" — ลูกศรจาก extension ไป base |
| Color-coded categories | PASS | View/Info (blue), Optimize (green), Backup/Recovery (orange), Settings (purple), Security (red) |

**Verdict: WARN**
- **ข้อเสนอ:** แยก Actor "User" ออกเป็น 3 actors ตาม SRS (Beginner, Gamer, Power User) เพื่อแสดงว่าแต่ละ actor เข้าถึง UCs ต่างกัน (SE 721 best practice)
- หรือเพิ่ม annotation note ว่า "User represents 3 user types — see SRS Section 2.3"

---

## Diagram 08 — Class Diagram

**ประเภท UML:** Class Diagram
**เกณฑ์:** SE 701 — OO Design, Class Relationships

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| 3-layer separation | PASS | Controller, Core/Business Logic, Data/Dataclass layers visible |
| Class compartments (name/attributes/methods) | PASS | ทุก class มี 3 ส่วนครบ |
| Relationship types ถูกต้อง | PASS | Association, Composition, Dependency แยกสัญลักษณ์ชัด |
| Dataclass DTO แสดง | PASS | Tweak, SystemProfile, TweakChange, SystemSnapshot |
| Legend | PASS | Association, Composition, Dependency, Safety/Critical, Enum labels |
| Readability | WARN | **ภาพ PNG ความละเอียดต่ำ — text อ่านยาก** เพราะ diagram ใหญ่มาก (2MB PNG) แต่ compress ลง viewport เล็ก |

**Verdict: PASS** (with readability note)
- **ข้อเสนอ:** Export PNG ที่ scale ใหญ่ขึ้น หรือแยก class diagram เป็น 2-3 sub-diagrams ตาม layer

---

## Diagram 08a — Class Diagram (Simplified)

**ประเภท UML:** Class Diagram
**เกณฑ์:** SE 701 — OO Design, Class Relationships

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Scope reduction เหมาะสม | PASS | แยกเฉพาะ Controller + Core Business Logic ออกจาก data models |
| Class compartments (name/attributes/methods) | PASS | ทุก class สำคัญยังคงโครงสร้าง 3 ส่วนครบ |
| ความสัมพันธ์หลักของระบบ | PASS | `ClutchGApp`, `ProfileManager`, `TweakRegistry`, `BatchExecutor`, `BatchParser` ยังเชื่อมกันครบ |
| Note แยก data models | PASS | มี reference ไป Diagram 8b ชัดเจน |
| Legend | PASS | composition, dependency, association, singleton, data model summary ครบ |
| A4 / thesis suitability | PASS | เหมาะกับ body chapter มากกว่า Diagram 08 เดิมอย่างชัดเจน |
| Connector density | WARN | กลุ่มเส้นรอบ `ClutchGApp` และ `ProfileManager` ยังแน่นเล็กน้อย |

**Verdict: PASS**
- เหมาะใช้แทน Diagram 08 เดิมในบทหลักของ thesis
- ถ้าจะ polish เพิ่ม ให้คลายเส้นรอบ `ProfileManager / TweakRegistry / BatchExecutor`

---

## Diagram 08b — Class Diagram — Data Models

**ประเภท UML:** Class Diagram
**เกณฑ์:** SE 701 — OO Design, Data Modeling

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Data models coverage | PASS | `Tweak`, `Profile`, `ExecutionResult`, `BackupInfo`, `SystemProfile`, `BatchScript`, `TweakChange`, `SystemSnapshot`, `ActionDefinition` ครบ |
| Enum relationships | PASS | `RiskLevel`, `ChangeCategory`, `ActionKind` ถูกแยกและโยงสัมพันธ์ชัด |
| Nested sub-model grouping | PASS | `OSInfo`, `CPUInfo`, `GPUInfo`, `RAMInfo`, `StorageInfo` ถูกสรุปรวมอย่างเหมาะสม |
| Legend | PASS | แยก dataclass, enum, sub-model group, contains, uses ครบ |
| Information detail | PASS | เหมาะสำหรับ reference / appendix |
| A4 / thesis suitability | WARN | รายละเอียด fields ยังเยอะ ถ้าใส่ใน body chapter จะเริ่มแน่น |
| Connector routing | WARN | เส้น dashed ไป enum หลายเส้นวิ่งอ้อมด้านขวาค่อนข้างแน่น |

**Verdict: PASS / WARN**
- เหมาะมากสำหรับ appendix หรือภาคผนวกเชิงเทคนิค
- ถ้าจะใช้ในบทหลัก ควรใช้เฉพาะเวอร์ชัน simplified หรือ crop บางส่วน

---

## Diagram 09 — Sequence Diagram

**ประเภท UML:** Sequence Diagram
**เกณฑ์:** SE 701 — OO Design, SE 725 — V&V

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Lifelines ครบ | PASS | User, ProfilesView, ExecutionDialog, ProfileManager, BackupManager, BatchExecutor, Windows OS — 7 participants |
| Message numbering | PASS | 1-12 numbered messages |
| Activation bars | PASS | แสดง activation ของแต่ละ lifeline |
| Loop fragment | PASS | "loop [for each script in profile.scripts]" |
| Opt fragment | PASS | "opt [on error & auto_backup]" — restore_registry |
| Return messages | PASS | Dashed arrows สำหรับ return values |
| Worker Thread annotation | PASS | "Worker Thread (daemon=True)" |
| Safety pattern (backup-before-apply) | PASS | Step 6: create_backup ก่อน Step 8: execute |

**Verdict: PASS**
- Sequence diagram คุณภาพดีมาก ครอบคลุม combined fragments (loop, opt)

---

## Diagram 10 — Deployment Diagram

**ประเภท UML:** Deployment Diagram
**เกณฑ์:** SE 701 — Deployment, SE 702 — SI.6 Delivery

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Node stereotypes | FAIL | **HTML entities render เป็น raw text** — "`<b>&laquo;device&raquo;</b>`" แสดงเป็น `<b>&laquo;device&raquo;` แทนที่จะเป็น **<<device>>** |
| Components ครบ | PASS | ClutchG.exe, batch_scripts/, assets/, config.json, backups/, logs/, snapshots/ |
| External systems | PASS | Windows Registry, Windows Services, Power Plan/BCD, UAC/Admin |
| Build process | PASS | "cd clutchg && python build.py" + PyInstaller command |
| Communication paths | PASS | reg add/delete, sc.exe, powercfg/bcdedit, read/write |
| %APPDATA% storage | PASS | config, backups, logs, snapshots แยกจาก installation |

**Verdict: FAIL**
- **ต้องแก้ไข:** HTML entity rendering — stereotypes (`<<device>>`, `<<directory>>`, `<<system>>`) แสดงเป็น raw `&laquo;` text ใน PNG export
- **สาเหตุ:** drawio source ใช้ `&amp;laquo;` ภายใน `value` attribute ที่เปิด HTML mode — ต้องแก้ให้ render ถูกต้อง
- **วิธีแก้:** เปลี่ยน `&amp;laquo;` เป็น `\u00AB` (Unicode) หรือใช้ `&lt;&lt;` แทน หรือ re-export PNG จาก draw.io ที่ render HTML correctly

---

## Diagram 11 — Conceptual Framework

**ประเภท:** Conceptual Framework Diagram (thesis)
**เกณฑ์:** SE 701/702 — Overall, Research Methodology

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| 4 layers ครบ | PASS | Theoretical Foundations → Research Process → System Design → Expected Outcomes |
| Theoretical foundations | PASS | Windows Internals, PC Optimization, Software Engineering, ISO 29110 |
| Research process | PASS | 28 repos, 48 tweaks, Risk framework |
| System design | PASS | 3-Tier Profile, Batch Engine, Safety Mechanisms, ISO 29110 WPs |
| Expected outcomes | PASS | Safe Optimization, User-Friendly GUI, Reversible Changes, Academic Quality |
| Flow direction | PASS | Top-down: Theory → Research → Design → Product → Outcomes |

**Verdict: PASS**
- Conceptual framework เหมาะสำหรับบทที่ 2-3 ของ thesis

---

## Diagram 12 — Gantt Chart

**ประเภท:** Gantt Chart (Project Timeline)
**เกณฑ์:** SE 781 — Schedule Management, CPM

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Phases ครบ | PASS | 6 phase groups + milestones |
| Color-coded by type | PASS | Research (blue), Design (green), Implementation (orange), Testing (red), Documentation (purple) |
| Milestones | PASS | SRS/SDD Complete, Alpha Release, Final Submission |
| Timeline scale | FAIL | **แสดง "Month 1-5" แต่โครงงานจริง 15 เดือน** (Jan 2025 — Mar 2026) — ไม่ตรงกับ Progress Status Record |
| Overlap visibility | PASS | Testing overlaps Implementation, Documentation overlaps Implementation |
| Sub-tasks | PASS | แยก sub-tasks เช่น "Repo analysis (28 repos)", "Unit + Integration tests" |

**Verdict: FAIL**
- **ต้องแก้ไข:** Timeline scale ไม่ตรงกับความเป็นจริง
  - Gantt แสดง 5 เดือน แต่โครงงานจริง 15 เดือน (Phase 1-12 ตาม `08-Progress-Status-Record.md`)
  - **ข้อเสนอ:** ปรับ timeline เป็น Jan 2025 — Apr 2026 (15 months) หรืออย่างน้อยแสดง 12 phases ตาม progress record
  - ปรับ milestone dates ให้ตรง: M1 Feb 2025, M2 Apr 2025, ..., M8 Mar 2026

---

## Diagram 13 — Tweak State Diagram

**ประเภท UML:** State Machine Diagram
**เกณฑ์:** SE 701 — OO Design, State Modeling

| เกณฑ์ | ผลลัพธ์ | หมายเหตุ |
|-------|---------|---------|
| Initial state (black dot) | PASS | → Registered |
| States ครบ | PASS | Registered → Selected → Applying → Applied / Failed → Rolled Back |
| Transitions labeled | PASS | "User selects", "Execute", "Success", "Error", "Rollback", "Retry", "Re-select", "Deselect" |
| Self-transition | PASS | Registered ↔ Selected (Deselect loop) |
| Error recovery | PASS | Failed → Retry → Selected; Failed → Rollback → Rolled Back |
| Final state | WARN | **ไม่มี final state (concentric circles)** — ตาม UML 2.5 state diagram ควรมี final node |
| State descriptions | PASS | ทุก state มี description text ด้านล่าง |

**Verdict: PASS** (minor: ไม่มี final state แต่ไม่ผิด เพราะ tweaks สามารถ cycle ได้)

---

## สรุปผลตรวจทั้งหมด

| # | Diagram | ประเภท UML | Verdict | ปัญหาหลัก |
|---|---------|-----------|---------|----------|
| 01 | System Architecture | Layered Arch | WARN | View count: 7 → 8 |
| 02 | Batch Execution Flow | Activity | PASS | — |
| 03 | GUI Navigation Flow | Navigation | WARN | View count: 7 → 8 |
| 04 | Tweak Lifecycle | Process Flow | PASS | — |
| 05 | Risk Classification | Decision Tree | WARN | `&amp;` entity bug |
| 06 | Module Dependency | Component Dep | PASS | — |
| 07 | Use Case Diagram | Use Case | WARN | Actors: 1 → 3 (SE 721) |
| 08 | Class Diagram | Class | PASS | PNG readability (minor) |
| 09 | Sequence Diagram | Sequence | PASS | — |
| 10 | Deployment Diagram | Deployment | FAIL | HTML entity rendering bug |
| 11 | Conceptual Framework | Framework | PASS | — |
| 12 | Gantt Chart | Gantt | FAIL | Timeline: 5mo → 15mo |
| 13 | State Diagram | State Machine | PASS | — |

---

## ข้อเสนอแนะเพิ่มเติม

### Diagrams ที่ขาด (SE Academic Perspective)

| Diagram ที่ควรมี | เหตุผล (SE Course) | Priority |
|----------------|-------------------|----------|
| **ER Diagram / Data Model** | SE 701 — แสดง data structure relationships (Tweak, Profile, Snapshot) | Medium |
| **Component Diagram** (UML) | SE 701 — แสดง component interfaces + ports (ต่างจาก dependency map) | Low |
| **Activity Diagram: GUI flows** | SE 721 — แสดง user workflows เช่น Rollback flow, Custom Preset flow | Medium |
| **Package Diagram** | SE 701 — แสดง package structure (clutchg.src.core, clutchg.src.gui) | Low |

### Quality Score

| เกณฑ์ | คะแนน (1-5) | เหตุผล |
|-------|-------------|--------|
| ครบถ้วน (Coverage) | 4/5 | 13 diagrams ครอบคลุม 7 UML types + 2 non-UML |
| ความถูกต้อง (Correctness) | 4/5 | 2 FAIL items ต้องแก้ |
| ความสอดคล้องกัน (Consistency) | 3/5 | View count ไม่ตรงกัน (7 vs 8), timeline ไม่ตรง |
| คุณภาพ visual | 5/5 | สวยงาม สีสม่ำเสมอ legend ครบ |
| UML compliance | 4/5 | ส่วนใหญ่ถูกต้องตาม UML 2.5 |
| **รวม** | **20/25** | **ดี — แก้ 2 FAIL + 4 WARN จะได้ 24/25** |

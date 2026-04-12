# Appendix A — แผนภาพ UML (UML Diagrams)

> **โครงงาน:** ClutchG PC Optimizer v2.0
> **วันที่:** 2026-04-06
> **อ้างอิง:** UML 2.5.1, SRS v3.3, SDD v3.4, Test Plan v3.2 | SE 701 OO Design

---

## 1. User Diagram (Context Diagram)

แสดงผู้มีส่วนเกี่ยวข้องกับระบบ ClutchG ทั้งหมด

```mermaid
graph TB
    subgraph External Actors
        BEG["Beginner User<br/>ใช้ SAFE Profile"]
        GAM["Gamer<br/>ใช้ COMPETITIVE Profile"]
        PWR["Power User<br/>ใช้ EXTREME / Custom"]
        ADV["Advisor<br/>ตรวจสอบเอกสาร"]
    end

    subgraph ClutchG System
        CG["ClutchG PC Optimizer<br/>Desktop Application"]
    end

    subgraph External Systems
        WIN["Windows OS<br/>Registry, Services, BCDEdit"]
        GPU_DRV["GPU Driver<br/>nvidia-smi, WMI"]
        FS["File System<br/>Config, Backups, Logs"]
        PS["PowerShell<br/>Restore Points"]
    end

    BEG -->|"เลือก Profile → Apply"| CG
    GAM -->|"เลือก Profile / Tweaks"| CG
    PWR -->|"Custom Preset + Rollback"| CG
    ADV -.->|"Review ISO29110 WPs"| CG

    CG -->|"reg add / sc config / bcdedit"| WIN
    CG -->|"query GPU info"| GPU_DRV
    CG -->|"read/write JSON"| FS
    CG -->|"Checkpoint-Computer"| PS

    CG -->|"แสดงผล + Toast"| BEG
    CG -->|"แสดงผล + Progress"| GAM
    CG -->|"Rollback + Script Export"| PWR
```

---

## 2. Use Case Diagram

แสดง Use Cases ทั้งหมดจัดกลุ่มตามฟังก์ชัน พร้อมความสัมพันธ์ Include/Extend

```mermaid
graph LR
    subgraph Actors
        BEG["Beginner"]
        GAM["Gamer"]
        PWR["Power User"]
    end

    subgraph "ClutchG PC Optimizer"
        subgraph "System Detection"
            UC01["UC-01<br/>View System Info"]
            UC02["UC-02<br/>View System Score & Tier"]
        end

        subgraph "Profile Management"
            UC03["UC-03<br/>Apply Optimization Profile"]
            UC04["UC-04<br/>View Profile Details"]
            UC05["UC-05<br/>Create Custom Preset"]
            UC06["UC-06<br/>Export Preset to JSON"]
            UC07["UC-07<br/>Import Preset from JSON"]
        end

        subgraph "Tweak Management"
            UC08["UC-08<br/>Browse Tweaks by Category"]
            UC09["UC-09<br/>Apply Individual Tweaks"]
            UC10["UC-10<br/>View Tweak Details"]
        end

        subgraph "Safety & Rollback"
            UC11["UC-11<br/>View Backup History"]
            UC12["UC-12<br/>Rollback Per-Tweak"]
            UC13["UC-13<br/>Rollback Entire Snapshot"]
            UC14["UC-14<br/>Export Rollback Script"]
        end

        subgraph "Settings"
            UC15["UC-15<br/>Change Theme/Accent"]
            UC16["UC-16<br/>Change Language"]
        end
    end

    BEG --> UC01
    BEG --> UC02
    BEG --> UC03
    BEG --> UC04
    BEG --> UC15

    GAM --> UC01
    GAM --> UC03
    GAM --> UC04
    GAM --> UC05
    GAM --> UC08
    GAM --> UC09
    GAM --> UC11
    GAM --> UC15
    GAM --> UC16

    PWR --> UC01
    PWR --> UC03
    PWR --> UC05
    PWR --> UC06
    PWR --> UC07
    PWR --> UC08
    PWR --> UC09
    PWR --> UC10
    PWR --> UC11
    PWR --> UC12
    PWR --> UC13
    PWR --> UC14
    PWR --> UC15
    PWR --> UC16

    %% Include relationships
    UC03 -.->|"include"| UC01
    UC03 -.->|"include"| UC11
    UC09 -.->|"include"| UC08
    UC12 -.->|"include"| UC11
    UC13 -.->|"include"| UC11

    %% Extend relationships
    UC05 -.->|"extend"| UC03
    UC06 -.->|"extend"| UC05
    UC07 -.->|"extend"| UC05
    UC14 -.->|"extend"| UC13
    UC10 -.->|"extend"| UC08
```

> **Include (5):** UC-03→UC-01 (ต้อง detect ระบบก่อน apply), UC-03→UC-11 (สร้าง backup ทุกครั้ง), UC-09→UC-08 (browse ก่อน apply), UC-12→UC-11 (ดู history ก่อน rollback), UC-13→UC-11 (ดู history ก่อน rollback)
>
> **Extend (5):** UC-05←UC-03 (สร้าง custom preset จากหน้า profile), UC-06←UC-05 (export ต่อจาก save), UC-07←UC-05 (import เข้า preset), UC-14←UC-13 (export script หลัง rollback), UC-10←UC-08 (ดูรายละเอียด tweak จาก browse)

---

## 3. Use Case Descriptions

### UC-01: View System Info

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-01 |
| **ชื่อ** | View System Info |
| **Actor** | Beginner, Gamer, Power User |
| **คำอธิบาย** | ผู้ใช้เปิดโปรแกรมแล้วดูข้อมูล Hardware ของเครื่อง (CPU, GPU, RAM, Storage) พร้อมคะแนนและ tier |
| **Trigger** | เปิดโปรแกรม (auto-detect) หรือกดปุ่ม Refresh |
| **Precondition** | โปรแกรมเปิดอยู่ |
| **Main Flow** | 1. ระบบเริ่ม system detection (background thread)<br/>2. ตรวจจับ CPU (cpuinfo → psutil → WMI fallback)<br/>3. ตรวจจับ GPU (nvidia-smi → WMI fallback)<br/>4. ตรวจจับ RAM (psutil)<br/>5. ตรวจจับ Storage (psutil)<br/>6. คำนวณ score: CPU(0-30) + GPU(0-30) + RAM(0-20) + Storage(0-10) = 0-100<br/>7. จำแนก tier: entry/mid/high/enthusiast<br/>8. แสดงผลบน Dashboard พร้อม icon + score bar |
| **Postcondition** | Dashboard แสดง CPU, GPU, RAM, Storage, Score, Tier |
| **Alternative** | 2a. cpuinfo ไม่พร้อม → ใช้ WMI<br/>3a. nvidia-smi ไม่มี → ใช้ WMI (Win32_VideoController) |
| **Exception** | 2b. ตรวจจับล้มเหลวทั้งหมด → แสดง "Unknown" + score = 0 |
| **NFR** | NFR-08 (async threading ไม่ block UI) |
| **Source** | `core/system_info.py` L100-380, `app_minimal.py` L117-145 |

---

### UC-03: Apply Optimization Profile

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-03 |
| **ชื่อ** | Apply Optimization Profile |
| **Actor** | Beginner (SAFE), Gamer (COMPETITIVE), Power User (EXTREME) |
| **คำอธิบาย** | ผู้ใช้เลือก optimization profile แล้ว apply ให้ระบบทำ tweaks ทั้งหมดใน profile |
| **Trigger** | กดปุ่ม "Apply" บนหน้า Profiles |
| **Precondition** | 1. สิทธิ์ Administrator<br/>2. System detection เสร็จแล้ว<br/>3. Batch scripts มีครบ (verify_scripts=True) |
| **Main Flow** | 1. ผู้ใช้เข้าหน้า Profiles → เห็น 3 cards (SAFE [LOW] / COMPETITIVE [MEDIUM] / EXTREME [HIGH])<br/>2. ผู้ใช้เลือก profile → อ่าน risk level, expected FPS, warnings<br/>3. ผู้ใช้กด "Apply"<br/>4. **ระบบสร้าง backup** (BackupManager.create_backup):<br/>   - Export 6 registry keys เป็น .reg<br/>   - สร้าง Windows Restore Point (PowerShell → WMIC fallback)<br/>5. **FlightRecorder เริ่ม recording** (start_recording)<br/>   - Capture registry snapshot (reg export → _before.reg)<br/>6. **Apply tweaks ทีละตัว** (for each tweak in profile):<br/>   - แสดง progress bar (on_progress callback)<br/>   - Execute .bat script + function (subprocess)<br/>   - บันทึก TweakChange: {name, key_path, old_value, new_value, rollback_command}<br/>   - แสดง per-tweak status [PASS]/[FAIL] (on_tweak_status callback)<br/>7. **FlightRecorder จบ recording** (finish_recording)<br/>   - Capture registry snapshot (reg export → _after.reg)<br/>   - Save JSON (change_logs/{id}.json)<br/>8. แสดง Toast notification "Profile applied successfully!" |
| **Postcondition** | 1. Tweaks ถูก apply<br/>2. Backup + Restore Point พร้อม<br/>3. FlightRecord JSON บันทึกครบ (rollback ready) |
| **Alternative** | 3a. ผู้ใช้กด Cancel → กลับหน้า Profiles ไม่มีอะไรเปลี่ยน<br/>6a. Tweak บางตัว fail → บันทึก error, ทำตัวต่อไป |
| **Exception** | 4a. Backup creation fail → แจ้ง warning, proceed (ไม่ block)<br/>5a. Restore Point fail → ลอง WMIC fallback → log warning<br/>6b. Script file ไม่มี → skip tweak + error log |
| **Business Rules** | - SAFE: 14 tweaks (LOW risk เท่านั้น)<br/>- COMPETITIVE: 44 tweaks (LOW + MEDIUM)<br/>- EXTREME: 56 tweaks ทั้งหมด (รวม HIGH 3 ตัว) |
| **NFR** | NFR-03 (reversible), NFR-04 (auto backup), NFR-09 (realistic FPS claim) |
| **Source** | `core/profile_manager.py` L146-257, `core/backup_manager.py` L73-140, `core/flight_recorder.py` L160-334 |

---

### UC-05: Create Custom Preset

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-05 |
| **ชื่อ** | Create Custom Preset |
| **Actor** | Gamer, Power User |
| **คำอธิบาย** | ผู้ใช้เลือก tweaks ทีละตัวจาก 56 tweaks แล้ว save เป็น custom preset |
| **Trigger** | เปิดหน้า Scripts → เลือก tweaks → กด Save Preset |
| **Precondition** | หน้า Scripts เปิดอยู่ |
| **Main Flow** | 1. ผู้ใช้เข้าหน้า Scripts → เห็น 10 categories<br/>2. เลือก tweaks (checkbox) → ดู risk badge + warnings<br/>3. กด "Save as Preset" → ใส่ชื่อ preset<br/>4. ระบบ validate: build_custom_preset(ids) → {tweaks, max_risk, requires_restart, warnings}<br/>5. Save preset ใน config.json<br/>6. แสดง Toast "Preset saved!" |
| **Postcondition** | Preset บันทึกใน config + พร้อมใช้จากหน้า Profiles |
| **Extension** | UC-06: Export ไป JSON file<br/>UC-07: Import จาก JSON file |
| **Source** | `core/tweak_registry.py` L975-1001, `core/profile_manager.py` L421-527 |

---

### UC-12: Rollback Per-Tweak

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-12 |
| **ชื่อ** | Rollback Per-Tweak |
| **Actor** | Power User |
| **คำอธิบาย** | ผู้ใช้ undo ทีละ tweak จาก Backup Center โดยเลือก tweak ที่ต้องการ revert |
| **Trigger** | กดปุ่ม "Undo" ข้าง tweak ในหน้า Backup & Restore Center |
| **Precondition** | มี snapshot อย่างน้อย 1 รายการ (FlightRecorder) |
| **Main Flow** | 1. ผู้ใช้เข้าหน้า Backup Center → เห็น timeline ของ snapshots<br/>2. เลือก snapshot → เห็นรายการ TweakChange (before/after values)<br/>3. กด "Undo" ข้าง tweak ที่ต้องการ<br/>4. ระบบ execute rollback_command:<br/>   `reg add "HKLM\...\key" /v ValueName /t REG_DWORD /d old_value /f`<br/>5. อัพเดต UI (สถานะ tweak → "Reverted")<br/>6. แสดง Toast "Tweak reverted" |
| **Postcondition** | Registry value กลับเป็นค่าเดิม (old_value) |
| **Alternative** | UC-13: Rollback ทั้ง snapshot (reversed order) |
| **Exception** | 4a. reg add fail (Access Denied) → แจ้ง error<br/>4b. Registry key ถูกเปลี่ยนโดย process อื่น → แจ้ง warning |
| **Source** | `core/flight_recorder.py` L521-540, `gui/views/backup_restore_center.py` |

---

### UC-08: Browse Tweaks by Category

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-08 |
| **ชื่อ** | Browse Tweaks by Category |
| **Actor** | Gamer, Power User |
| **คำอธิบาย** | ผู้ใช้เรียกดู tweaks ทั้ง 56 ตัว จัดกลุ่มตาม 10 categories |
| **Trigger** | คลิก sidebar "Scripts" |
| **Precondition** | ไม่มี |
| **Main Flow** | 1. ระบบแสดง 10 categories: Telemetry(8), Input(6), Power(7), GPU(8), Network(6), Services(5), Memory(4), Boot(5), Visual(4), Cleanup(3)<br/>2. แต่ละ category มี icon + color + count<br/>3. ผู้ใช้ expand category → เห็น tweaks ในกลุ่ม<br/>4. แต่ละ tweak แสดง: name, risk badge (LOW/MEDIUM/HIGH), checkbox, "?" help button<br/>5. กด "?" → popup: what_it_does, why_it_helps, limitations, warnings, expected_gain |
| **Postcondition** | ผู้ใช้เข้าใจ tweak ก่อนเลือก |
| **Source** | `core/tweak_registry.py` L39-51, L884-933, `gui/views/scripts_minimal.py` |

---

### UC-15: Change Theme/Accent

| รายการ | รายละเอียด |
|--------|-----------|
| **Use Case ID** | UC-15 |
| **ชื่อ** | Change Theme and Accent Color |
| **Actor** | ทุก Actor |
| **คำอธิบาย** | ผู้ใช้เปลี่ยน theme (dark/light) และ accent color (5 สี) |
| **Trigger** | เข้าหน้า Settings |
| **Main Flow** | 1. เข้า Settings → เห็น Theme toggle (Dark/Light) + Accent picker (Cyan, Purple, Green, Orange, Pink)<br/>2. เลือก theme หรือ accent → ระบบ refresh UI ทันที (hot-swap)<br/>3. บันทึกใน config.json |
| **Postcondition** | UI เปลี่ยนสี + persist ข้าม session |
| **Source** | `gui/views/settings_minimal.py`, `app_minimal.py` L260-280 |

---

## 4. Activity Diagrams

### 4.1 Activity Diagram: Apply Profile Workflow

```mermaid
flowchart TD
    START(("Start"))
    A1["User opens Profiles view"]
    A2["User selects profile<br/>SAFE / COMPETITIVE / EXTREME"]
    A3["User clicks Apply"]
    
    D1{"Admin rights?"}
    A4["Show UAC prompt"]
    D2{"UAC approved?"}
    A5["Show error: Admin required"]
    
    B1["Create Backup<br/>BackupManager.create_backup()"]
    B2["Export 6 registry keys → .reg"]
    B3{"Create Restore Point?"}
    B4["PowerShell: Checkpoint-Computer"]
    D3{"PowerShell success?"}
    B5["WMIC fallback"]
    B6["Log warning: no restore point"]
    
    F1["FlightRecorder.start_recording()"]
    F2["Capture registry BEFORE snapshot"]
    
    L1["Get tweaks from TweakRegistry<br/>for selected profile"]
    L2["FOR EACH tweak i = 1..N"]
    L3["Update progress bar: i/N × 100%"]
    L4["BatchExecutor.execute<br/>script + function"]
    D4{"Execution success?"}
    L5["Record TweakChange<br/>name, old→new, rollback_cmd"]
    L6["Show PASS on tweak"]
    L7["Record error<br/>success=false"]
    L8["Show FAIL on tweak"]
    D5{"More tweaks?"}
    
    F3["FlightRecorder.finish_recording()"]
    F4["Capture registry AFTER snapshot"]
    F5["Save snapshot JSON"]
    
    T1["Show Toast: Profile applied!"]
    END(("End"))
    
    START --> A1 --> A2 --> A3 --> D1
    D1 -->|"Yes"| B1
    D1 -->|"No"| A4 --> D2
    D2 -->|"Yes"| B1
    D2 -->|"No"| A5 --> END
    
    B1 --> B2 --> B3
    B3 -->|"Yes"| B4 --> D3
    B3 -->|"No"| F1
    D3 -->|"Yes"| F1
    D3 -->|"No"| B5 --> F1
    
    F1 --> F2 --> L1 --> L2 --> L3 --> L4 --> D4
    D4 -->|"Yes"| L5 --> L6 --> D5
    D4 -->|"No"| L7 --> L8 --> D5
    D5 -->|"Yes"| L2
    D5 -->|"No"| F3 --> F4 --> F5 --> T1 --> END
```

### 4.2 Activity Diagram: Rollback Workflow

```mermaid
flowchart TD
    START(("Start"))
    A1["User opens Backup Center"]
    A2["Load snapshots from FlightRecorder<br/>list_snapshots(limit=50)"]
    A3["Display timeline UI<br/>newest first"]
    A4["User selects a snapshot"]
    A5["Show TweakChange list<br/>name, before→after, risk"]
    
    D1{"Rollback type?"}
    
    subgraph "Per-Tweak Rollback"
        R1["User clicks Undo on specific tweak"]
        R2["Execute rollback_command<br/>reg add ... /d old_value /f"]
        D2{"Success?"}
        R3["Mark tweak as Reverted"]
        R4["Show error message"]
    end
    
    subgraph "Full Snapshot Rollback"
        S1["User clicks Rollback All"]
        S2["Confirm dialog: Are you sure?"]
        D3{"Confirmed?"}
        S3["FOR EACH tweak in REVERSED order"]
        S4["Execute rollback_command"]
        S5["Record results"]
        S6["Show summary: N/M tweaks reverted"]
    end
    
    subgraph "Export Script"
        E1["User clicks Export .bat"]
        E2["generate_rollback_script(id)"]
        E3["Save rollback_{id}.bat"]
        E4["Show Toast: Script exported"]
    end
    
    END(("End"))
    
    START --> A1 --> A2 --> A3 --> A4 --> A5 --> D1
    D1 -->|"Per-Tweak"| R1 --> R2 --> D2
    D2 -->|"Yes"| R3 --> END
    D2 -->|"No"| R4 --> END
    D1 -->|"Full Snapshot"| S1 --> S2 --> D3
    D3 -->|"Yes"| S3 --> S4 --> S5 --> S6 --> END
    D3 -->|"No"| END
    D1 -->|"Export"| E1 --> E2 --> E3 --> E4 --> END
```

### 4.3 Activity Diagram: System Detection

```mermaid
flowchart TD
    START(("Start"))
    A1["App launches → Start background thread"]
    
    subgraph "CPU Detection"
        C1["Try cpuinfo library"]
        DC1{"cpuinfo available?"}
        C2["Get brand_raw, frequency"]
        C3["Try WMI: Win32_Processor"]
        DC2{"WMI available?"}
        C4["CPU name from WMI"]
        C5["CPU = Unknown"]
        C6["Detect vendor: Intel / AMD / Apple"]
        C7["BenchmarkDB.get_cpu_score()<br/>→ score 0-30"]
    end
    
    subgraph "GPU Detection"
        G1["Try nvidia-smi query"]
        DG1{"nvidia-smi success?"}
        G2["Parse name + VRAM"]
        G3["Try WMI: Win32_VideoController"]
        DG2{"WMI found discrete GPU?"}
        G4["Get GPU name + VRAM from WMI"]
        G5["GPU = Unknown"]
        G6["Detect vendor: NVIDIA / AMD / Intel"]
        G7["BenchmarkDB.get_gpu_score()<br/>→ score 0-30"]
    end
    
    subgraph "RAM & Storage"
        M1["psutil.virtual_memory()<br/>→ total_gb (rounded up)"]
        M2["RAM score = min(20, total_gb / 2)"]
        S1["psutil.disk_partitions()<br/>→ C: drive usage"]
        S2["Storage score: SSD/NVMe=10, HDD=5"]
    end
    
    subgraph "Score Calculation"
        SC1["total = cpu.score + gpu.score<br/>+ ram.score + storage.score"]
        SC2{"total ≥ 70?"}
        SC3["Tier = enthusiast"]
        SC4{"total ≥ 50?"}
        SC5["Tier = high"]
        SC6{"total ≥ 30?"}
        SC7["Tier = mid"]
        SC8["Tier = entry"]
    end
    
    R1["Build SystemProfile"]
    R2["Callback: _on_detection_complete()"]
    R3["Refresh Dashboard UI"]
    END(("End"))
    
    START --> A1 --> C1 --> DC1
    DC1 -->|"Yes"| C2 --> C6
    DC1 -->|"No"| C3 --> DC2
    DC2 -->|"Yes"| C4 --> C6
    DC2 -->|"No"| C5 --> C6
    C6 --> C7 --> G1
    
    G1 --> DG1
    DG1 -->|"Yes"| G2 --> G6
    DG1 -->|"No"| G3 --> DG2
    DG2 -->|"Yes"| G4 --> G6
    DG2 -->|"No"| G5 --> G6
    G6 --> G7 --> M1 --> M2 --> S1 --> S2
    
    S2 --> SC1 --> SC2
    SC2 -->|"Yes"| SC3 --> R1
    SC2 -->|"No"| SC4
    SC4 -->|"Yes"| SC5 --> R1
    SC4 -->|"No"| SC6
    SC6 -->|"Yes"| SC7 --> R1
    SC6 -->|"No"| SC8 --> R1
    
    R1 --> R2 --> R3 --> END
```

---

## 5. System Diagram (Component Architecture)

```mermaid
graph TB
    subgraph "Presentation Layer"
        APP["ClutchGApp<br/>app_minimal.py<br/>(Main Controller)"]
        SB["EnhancedSidebar"]
        VT["ViewTransition"]
        
        subgraph "Views"
            V1["DashboardView<br/>25.8KB"]
            V2["ProfilesView<br/>10.7KB"]
            V3["ScriptsView<br/>63.5KB"]
            V4["BackupRestoreCenter<br/>35.7KB"]
            V5["HelpView<br/>23.3KB"]
            V6["SettingsView<br/>12KB"]
            V7["WelcomeOverlay<br/>12.7KB"]
        end
        
        subgraph "Components"
            W1["RiskBadge"]
            W2["Toast"]
            W3["ExecutionDialog"]
            W4["ContextHelpButton"]
        end
    end
    
    subgraph "Business Logic Layer"
        subgraph "Core Managers"
            PM["ProfileManager<br/>528 lines"]
            TR["TweakRegistry<br/>1234 lines<br/>56 tweaks"]
            SD["SystemDetector<br/>381 lines"]
            BM["BackupManager<br/>373 lines"]
            FR["FlightRecorder<br/>589 lines"]
            BP["BatchParser<br/>450 lines"]
            BE["BatchExecutor<br/>200 lines"]
            CM["ConfigManager<br/>120 lines"]
            HM["HelpManager<br/>100 lines"]
            BD["BenchmarkDB<br/>450 lines"]
            AC["ActionCatalog"]
            RS["RecommendationService<br/>188 lines"]
            SS["SystemSnapshot"]
        end
    end
    
    subgraph "Infrastructure Layer"
        subgraph "Batch Scripts"
            BS1["telemetry-blocker.bat"]
            BS2["input-optimizer.bat"]
            BS3["power-manager.bat"]
            BS4["gpu-optimizer.bat"]
            BS5["network-optimizer.bat"]
            BS6["service-manager.bat"]
            BS7["bcdedit-manager.bat"]
            BS8["debloater.bat"]
            BS9["storage-optimizer.bat"]
        end
        
        subgraph "Data Storage"
            JSON1["config/config.json"]
            JSON2["data/backups/backup_index.json"]
            JSON3["data/flight_recorder/change_logs/*.json"]
            REG["data/flight_recorder/registry_snapshots/*.reg"]
        end
        
        subgraph "Windows OS"
            WREG["Windows Registry<br/>HKLM / HKCU"]
            WSVC["Windows Services<br/>sc.exe"]
            WBCD["BCDEdit<br/>bcdedit.exe"]
            WPS["PowerShell<br/>Checkpoint-Computer"]
        end
    end
    
    APP --> SB
    APP --> VT
    APP --> V1 & V2 & V3 & V4 & V5 & V6
    
    V1 --> SD
    V2 --> PM
    V3 --> TR
    V4 --> FR & BM
    V5 --> HM
    V6 --> CM
    
    PM --> TR
    PM --> BM
    PM --> FR
    PM --> BP
    PM --> BE
    
    SD --> BD
    SD --> RS
    
    TR --> AC
    
    BE --> BS1 & BS2 & BS3 & BS4 & BS5 & BS6 & BS7 & BS8 & BS9
    
    BM --> JSON2
    FR --> JSON3 & REG
    CM --> JSON1
    
    BS1 & BS2 & BS3 & BS4 & BS5 & BS6 --> WREG
    BS6 --> WSVC
    BS7 --> WBCD
    BM --> WPS
```

---

## 6. Sequence Diagrams

### 6.1 Sequence Diagram: Apply Optimization Profile (Full Detail)

```mermaid
sequenceDiagram
    actor User
    participant PV as ProfilesView
    participant PM as ProfileManager
    participant TR as TweakRegistry
    participant BM as BackupManager
    participant FR as FlightRecorder
    participant BE as BatchExecutor
    participant WIN as Windows OS

    User->>PV: Click "Apply COMPETITIVE"
    PV->>PM: apply_profile("COMPETITIVE", callbacks)
    
    Note over PM: Step 1: Create Backup
    PM->>BM: create_backup("Before COMPETITIVE")
    BM->>WIN: reg export HKLM\Services → services.reg
    BM->>WIN: reg export HKLM\Power → power.reg
    BM->>WIN: reg export HKLM\Explorer → explorer.reg
    BM->>WIN: reg export HKLM\Policies → policies.reg
    BM->>WIN: reg export HKCU\Desktop → desktop.reg
    BM->>WIN: reg export HKCU\Explorer → user_explorer.reg
    BM->>WIN: PowerShell Checkpoint-Computer
    BM-->>PM: BackupInfo(id, has_restore_point=true)
    
    Note over PM: Step 2: Start Recording
    PM->>FR: start_recording("profile_applied", "COMPETITIVE")
    FR->>WIN: reg export HKLM → before_HKLM.reg
    FR-->>PM: SystemSnapshot(id=20260304_221530)
    
    Note over PM: Step 3: Get Tweaks
    PM->>TR: get_tweaks_for_preset("competitive")
    TR-->>PM: List[Tweak] (44 tweaks)
    
    Note over PM: Step 4: Execute Tweaks (loop 44x)
    loop For each tweak (1..44)
        PM->>PV: on_progress(i/44 * 100)
        PV->>User: Update progress bar
        
        PM->>BE: execute("input-optimizer.bat", ":apply_mouse")
        BE->>WIN: subprocess.run(bat script)
        WIN-->>BE: output + exit_code
        BE-->>PM: ExecutionResult(success, output)
        
        PM->>FR: record_change("Mouse Accel", REGISTRY, key, "1", "0")
        FR->>FR: generate_rollback: reg add ... /d 1 /f
        FR-->>PM: TweakChange
        
        PM->>PV: on_tweak_status("Mouse Accel", "done")
        PV->>User: Show [PASS] next to tweak
    end
    
    Note over PM: Step 5: Finish Recording
    PM->>FR: finish_recording(success=true)
    FR->>WIN: reg export HKLM → after_HKLM.reg
    FR->>FR: save JSON → change_logs/20260304_221530.json
    FR-->>PM: SystemSnapshot(44 tweaks recorded)
    
    PM-->>PV: success=true
    PV->>User: Toast "COMPETITIVE profile applied! 44 tweaks done"
```

### 6.2 Sequence Diagram: Per-Tweak Rollback

```mermaid
sequenceDiagram
    actor User
    participant RC as BackupRestoreCenter
    participant FR as FlightRecorder
    participant WIN as Windows OS

    User->>RC: Open Backup Center
    RC->>FR: list_snapshots(limit=50)
    FR-->>RC: List[SystemSnapshot]
    RC->>User: Display timeline (newest first)
    
    User->>RC: Select snapshot "20260304_221530"
    RC->>FR: get_snapshot("20260304_221530")
    FR-->>RC: SystemSnapshot(44 tweaks)
    RC->>User: Show 44 TweakChanges with before/after values
    
    User->>RC: Click "Undo" on "Disable Mouse Acceleration"
    
    Note over RC: Execute rollback command
    RC->>WIN: reg add "HKCU\Control Panel\Mouse" /v MouseSpeed /t REG_SZ /d 1 /f
    WIN-->>RC: Success
    
    RC->>User: Show "Mouse Acceleration restored"
    RC->>User: Toast "Tweak reverted successfully"
```

### 6.3 Sequence Diagram: System Detection

```mermaid
sequenceDiagram
    participant APP as ClutchGApp
    participant SD as SystemDetector
    participant CI as cpuinfo
    participant NS as nvidia-smi
    participant PS as psutil
    participant WMI as WMI
    participant BD as BenchmarkDB
    participant RS as RecommendationService
    participant DV as DashboardView

    APP->>APP: threading.Thread(target=_detect_system)
    APP->>SD: detect_all()
    
    Note over SD: CPU Detection (fallback chain)
    SD->>CI: get_cpu_info()
    CI-->>SD: brand_raw="Intel Core i7-13700K"
    SD->>PS: cpu_count(logical=False), cpu_freq()
    PS-->>SD: cores=16, threads=24, freq=5.4GHz
    SD->>BD: get_cpu_score("Intel Core i7-13700K")
    BD-->>SD: score=27, matched="i7-13700K"
    
    Note over SD: GPU Detection (fallback chain)
    SD->>NS: nvidia-smi --query-gpu=name,memory
    NS-->>SD: "GeForce RTX 4070, 12288 MiB"
    SD->>BD: get_gpu_score("GeForce RTX 4070")
    BD-->>SD: score=24, vram=12GB
    
    Note over SD: RAM Detection
    SD->>PS: virtual_memory().total
    PS-->>SD: 34359738368 (32GB)
    SD->>SD: score = min(20, 32/2) = 16
    
    Note over SD: Storage Detection
    SD->>PS: disk_partitions() + disk_usage("C:")
    PS-->>SD: 1TB SSD
    SD->>SD: score = 10 (SSD)
    
    Note over SD: Score Calculation
    SD->>SD: total = 27 + 24 + 16 + 10 = 77
    SD->>SD: tier = "enthusiast" (≥70)
    
    Note over SD,RS: Unified Recommendation
    SD->>RS: recommend_preset(profile)
    RS->>RS: _has_sufficient_data() → True (both benchmark_matched)
    RS->>RS: Primary path: score=77 ≥ 50 → COMPETITIVE
    RS-->>SD: Recommendation(preset=COMPETITIVE, source=primary, confidence=0.7)
    
    SD-->>APP: SystemProfile(score=77, tier=enthusiast)
    APP->>DV: window.after(0, update_dashboard)
    DV->>DV: Display CPU, GPU, RAM, Storage cards
    DV->>DV: Display score=77, tier=Enthusiast
```

### 6.4 Sequence Diagram: Export/Import Custom Preset

```mermaid
sequenceDiagram
    actor User
    participant SV as ScriptsView
    participant PM as ProfileManager
    participant TR as TweakRegistry
    participant FS as File System

    Note over User,FS: Export Preset
    User->>SV: Select 12 tweaks via checkboxes
    User->>SV: Click "Save as Preset" → name="MyGaming"
    SV->>TR: build_custom_preset(["tel_diagtrack", "inp_mouse_accel", ...])
    TR-->>SV: {tweaks: 12, max_risk: "MEDIUM", requires_restart: true}
    SV->>PM: save_custom_preset("MyGaming", tweak_ids)
    PM->>FS: Write to config.json → custom_presets.MyGaming
    PM-->>SV: Success
    SV->>User: Toast "Preset saved!"
    
    User->>SV: Click "Export"
    SV->>PM: export_preset_to_file("MyGaming", ids, path)
    PM->>FS: Write MyGaming.json
    PM-->>SV: File saved
    SV->>User: Toast "Exported to MyGaming.json"
    
    Note over User,FS: Import Preset
    User->>SV: Click "Import" → select file
    SV->>PM: import_preset_from_file("MyGaming.json")
    PM->>FS: Read JSON file
    PM->>TR: validate tweak_ids (check each exists)
    TR-->>PM: {valid: 12, unknown: 0}
    PM->>FS: Save to config.json
    PM-->>SV: {name: "MyGaming", count: 12}
    SV->>User: Toast "Imported MyGaming (12 tweaks)"
```

---

## 7. Class Diagram (Core Domain)

```mermaid
classDiagram
    class Tweak {
        +str id
        +str name
        +str category
        +str description
        +str what_it_does
        +str why_it_helps
        +str limitations
        +List~str~ warnings
        +str risk_level
        +str expected_gain
        +bool requires_admin
        +bool requires_restart
        +bool reversible
        +List~str~ compatible_os
        +Dict compatible_hardware
        +List~str~ registry_keys
        +str bat_script
        +str bat_function
        +bool preset_safe
        +bool preset_competitive
        +bool preset_extreme
    }
    
    class TweakRegistry {
        -Dict _tweaks
        +get_all_tweaks() List~Tweak~
        +get_tweak(id) Tweak
        +get_tweaks_by_category(cat) List~Tweak~
        +get_tweaks_for_preset(preset) List~Tweak~
        +get_compatible_tweaks(profile) List~Tweak~
        +suggest_preset(profile) Dict
        +get_category_stats() Dict
        +get_risk_distribution() Dict
        +build_custom_preset(ids) Dict
    }
    
    class TweakChange {
        +str name
        +ChangeCategory category
        +str key_path
        +str old_value
        +str new_value
        +str value_type
        +RiskLevel risk_level
        +datetime timestamp
        +str profile
        +bool success
        +bool can_rollback
        +str rollback_command
        +to_dict() Dict
        +from_dict(data)$ TweakChange
    }
    
    class SystemSnapshot {
        +str snapshot_id
        +datetime timestamp
        +str operation_type
        +str profile
        +List~TweakChange~ tweaks
        +str pre_snapshot_path
        +str post_snapshot_path
        +bool success
        +to_dict() Dict
        +from_dict(data)$ SystemSnapshot
    }
    
    class FlightRecorder {
        -Path storage_dir
        -Path logs_dir
        -Path snapshots_dir
        -SystemSnapshot current_snapshot
        +start_recording(type, profile) SystemSnapshot
        +record_change(...) TweakChange
        +record_registry_change(...) TweakChange
        +finish_recording(success) SystemSnapshot
        +get_snapshot(id) SystemSnapshot
        +list_snapshots(limit) List~SystemSnapshot~
        +compare_snapshots(before, after) List~TweakChange~
        +generate_rollback_script(id) Path
        +cleanup_old_snapshots(days)
    }
    
    class BackupManager {
        -Path backup_dir
        -Path index_file
        -List~BackupInfo~ backups
        +create_backup(name, profile) BackupInfo
        +restore_registry(id) bool
        +delete_backup(id) bool
        +get_all_backups() List~BackupInfo~
    }
    
    class BackupInfo {
        +str id
        +str name
        +str created_at
        +str profile
        +bool has_restore_point
        +bool has_registry_backup
        +str description
        +int size_bytes
    }
    
    class ProfileManager {
        -Dict profiles
        -TweakRegistry registry
        +get_profile(name) Profile
        +apply_profile(profile, callbacks) bool
        +apply_tweaks(ids, callbacks) bool
        +verify_scripts(profile) bool
        +save_custom_preset(name, ids)
        +export_preset_to_file(name, ids, path)
        +import_preset_from_file(path) Dict
    }
    
    class SystemDetector {
        -WMI wmi_conn
        -BenchmarkDB benchmark_db
        +detect_all() SystemProfile
        +detect_cpu() CPUInfo
        +detect_gpu() GPUInfo
        +detect_ram() RAMInfo
        +detect_storage() StorageInfo
        +detect_form_factor() str
        +calculate_tier(score) str
        +recommend_profile(system) str
    }
    
    class SystemProfile {
        +OSInfo os
        +CPUInfo cpu
        +GPUInfo gpu
        +RAMInfo ram
        +StorageInfo storage
        +str form_factor
        +str tier
        +int total_score
    }

    class Recommendation {
        +str preset
        +str reason
        +str source
        +int total_score
        +float confidence
    }

    class RecommendationService {
        +recommend_preset(profile) Recommendation
        -_primary_path(profile) Recommendation
        -_fallback_path(profile) Recommendation
        -_has_sufficient_data(profile) bool
    }

    TweakRegistry "1" --> "*" Tweak : contains
    FlightRecorder "1" --> "*" SystemSnapshot : manages
    SystemSnapshot "1" --> "*" TweakChange : contains
    ProfileManager "1" --> "1" TweakRegistry : uses
    ProfileManager "1" --> "1" BackupManager : uses
    ProfileManager "1" --> "1" FlightRecorder : uses
    BackupManager "1" --> "*" BackupInfo : manages
    SystemDetector "1" --> "1" SystemProfile : creates
    SystemDetector "1" --> "1" RecommendationService : delegates recommend
    RecommendationService "1" --> "1" Recommendation : returns
    TweakRegistry "1" --> "1" SystemProfile : filters by
```

---

## 8. State Machine Diagram: Tweak Lifecycle

แสดงวงจรชีวิตของ Tweak ตั้งแต่ค้นพบจาก Registry จนถึงการ Rollback

> **อ้างอิง SE 701:** State Machine Diagram (UML 2.5.1) ใช้แสดงสถานะและการเปลี่ยนสถานะของ object ภายในระบบ

```mermaid
stateDiagram-v2
    [*] --> Registered : TweakRegistry.init()

    Registered --> Compatible : SystemDetector confirms OS/HW match
    Registered --> Incompatible : OS/HW mismatch detected

    Incompatible --> [*] : Filtered out (not shown to user)

    Compatible --> Selected : User checks tweak / Profile auto-select
    Compatible --> Compatible : User browses (no state change)

    Selected --> Validating : User clicks Apply
    Selected --> Compatible : User unchecks tweak

    Validating --> Applying : Validator passes (admin + scripts OK)
    Validating --> Selected : Validation fails (no admin / missing script)

    Applying --> Applied : BatchExecutor returns success
    Applying --> Failed : BatchExecutor returns error

    Applied --> RollingBack : User clicks Undo / Rollback All
    Applied --> Applied : System reboot (tweak persists)

    Failed --> Selected : User retries
    Failed --> [*] : User dismisses error

    RollingBack --> Reverted : reg add old_value succeeds
    RollingBack --> RollbackFailed : reg add fails (access denied)

    Reverted --> Compatible : Ready for re-apply
    RollbackFailed --> Applied : Tweak still active (manual fix needed)

    note right of Registered
        56 tweaks loaded from
        TweakRegistry at startup
    end note

    note right of Applied
        FlightRecorder saves
        TweakChange with
        rollback_command
    end note

    note right of Reverted
        Registry restored to
        old_value from snapshot
    end note
```

**สถานะ (States):**

| State | คำอธิบาย | ข้อมูลที่บันทึก |
|-------|---------|---------------|
| Registered | Tweak อยู่ใน TweakRegistry | id, name, category, risk_level |
| Compatible | ตรวจแล้วรองรับ OS/HW ของเครื่อง | compatible_os, compatible_hardware |
| Incompatible | ไม่รองรับ (กรองออก) | filter_reason |
| Selected | ผู้ใช้เลือก (หรือ profile auto-select) | preset flag (safe/competitive/extreme) |
| Validating | กำลังตรวจ admin rights + script availability | verify_scripts() result |
| Applying | กำลัง execute batch script | subprocess PID, progress % |
| Applied | Apply สำเร็จ | TweakChange: old→new, rollback_command |
| Failed | Apply ล้มเหลว | error message, exit code |
| RollingBack | กำลัง revert registry value | rollback_command executing |
| Reverted | Rollback สำเร็จ | restored old_value confirmed |
| RollbackFailed | Rollback ล้มเหลว | error (access denied / key changed) |

---

## 9. Package Diagram: Layer Architecture

แสดงโครงสร้าง package แบบ 3 ชั้น ตาม Layered Architecture ของ ClutchG

> **อ้างอิง SE 701:** Package Diagram ใช้แสดง logical grouping ของ modules และ dependency direction ระหว่างชั้น — dependency ต้องชี้ลงเท่านั้น (Presentation → Business Logic → Infrastructure)

```mermaid
graph TB
    subgraph "Presentation Layer (clutchg/src/gui/)"
        subgraph "Views (gui/views/)"
            V_DASH["dashboard_minimal.py"]
            V_PROF["profiles_minimal.py"]
            V_SCRP["scripts_minimal.py"]
            V_BACK["backup_restore_center.py"]
            V_HELP["help_minimal.py"]
            V_SETS["settings_minimal.py"]
            V_WELC["welcome_overlay.py"]
        end
        subgraph "Components (gui/components/)"
            C_SIDE["enhanced_sidebar.py"]
            C_RISK["risk_badge.py"]
            C_TOST["toast.py"]
            C_EXEC["execution_dialog.py"]
            C_PROG["progress_bar.py"]
            C_CARD["glass_card.py"]
        end
        subgraph "Theme & Style (gui/)"
            T_THM["theme.py"]
            T_STL["style.py"]
            T_ICN["icons.py"]
            T_FNT["font_loader.py"]
        end
    end

    subgraph "Business Logic Layer (clutchg/src/core/)"
        subgraph "Domain Models"
            M_TWK["tweak_registry.py (Tweak dataclass)"]
            M_ACT["action_catalog.py"]
        end
        subgraph "Managers"
            MGR_PRF["profile_manager.py"]
            MGR_BAK["backup_manager.py"]
            MGR_FLR["flight_recorder.py"]
            MGR_CFG["config_manager.py"]
        end
        subgraph "Detection & Analysis"
            DET_SYS["system_info.py"]
            DET_BDB["benchmark_db.py"]
            DET_REC["recommendation_service.py"]
        end
        subgraph "Script Interface"
            SCR_PAR["batch_parser.py"]
            SCR_EXE["batch_executor.py"]
        end
    end

    subgraph "Infrastructure Layer"
        subgraph "Batch Scripts (src/core/)"
            BAT_TEL["telemetry-blocker.bat"]
            BAT_INP["input-optimizer.bat"]
            BAT_PWR["power-manager.bat"]
            BAT_GPU["gpu-optimizer.bat"]
            BAT_NET["network-optimizer.bat"]
            BAT_SVC["service-manager.bat"]
        end
        subgraph "Data Files"
            DAT_CFG["config/config.json"]
            DAT_BKP["data/backups/*.json"]
            DAT_FLR["data/flight_recorder/*.json"]
            DAT_HLP["data/help_content.json"]
        end
        subgraph "Windows OS APIs"
            WIN_REG["Registry (reg.exe)"]
            WIN_SVC["Services (sc.exe)"]
            WIN_BCD["BCDEdit (bcdedit.exe)"]
            WIN_PS["PowerShell"]
        end
    end

    %% Presentation → Business Logic
    V_DASH --> DET_SYS
    V_PROF --> MGR_PRF
    V_SCRP --> M_TWK
    V_BACK --> MGR_FLR
    V_BACK --> MGR_BAK
    V_HELP --> MGR_CFG
    V_SETS --> MGR_CFG

    %% Business Logic internal
    MGR_PRF --> M_TWK
    MGR_PRF --> MGR_BAK
    MGR_PRF --> MGR_FLR
    MGR_PRF --> SCR_EXE
    DET_SYS --> DET_BDB
    DET_SYS --> DET_REC
    M_TWK --> M_ACT
    SCR_EXE --> SCR_PAR

    %% Business Logic → Infrastructure
    SCR_EXE --> BAT_TEL & BAT_INP & BAT_PWR & BAT_GPU & BAT_NET & BAT_SVC
    MGR_BAK --> DAT_BKP
    MGR_FLR --> DAT_FLR
    MGR_CFG --> DAT_CFG

    BAT_TEL & BAT_INP & BAT_PWR --> WIN_REG
    BAT_SVC --> WIN_SVC
    MGR_BAK --> WIN_PS
```

**Dependency Rules:**

| กฎ | รายละเอียด | การปฏิบัติใน ClutchG |
|----|-----------|-------------------|
| Top-down only | Presentation → Business → Infrastructure | Views import core modules เท่านั้น ไม่มี core import gui |
| No circular | ห้าม dependency วน | ตรวจสอบแล้วไม่มี circular imports |
| Stable dependencies | ชั้นล่างเปลี่ยนน้อยกว่าชั้นบน | core/ เปลี่ยน ~20 ครั้ง vs gui/ เปลี่ยน ~80 ครั้ง |
| Interface boundary | ชั้นบนเรียกผ่าน public API | Views ใช้ manager methods ไม่เข้าถึง internal state |

---

## 10. Deployment Diagram

แสดง Physical Deployment Topology ของระบบ ClutchG บน Windows Desktop Environment ตาม UML 2.5.1 Deployment Diagram notation

> **อ้างอิง:** SDD v3.4 §7 Deployment View, Configuration Plan v2.2 §6 Release Process

### 10.1 Deployment Topology

```mermaid
graph TB
    subgraph NODE_PC["<<device>><br/>Windows 10/11 Desktop<br/>x64, RAM ≥ 4 GB, Admin Rights"]

        subgraph ENV_PYTHON["<<execution environment>><br/>Python 3.12 Runtime"]
            ART_MAIN["<<artifact>><br/>main.py<br/>(Entry Point)"]
            ART_APP["<<artifact>><br/>app_minimal.py<br/>(App Controller)"]

            subgraph COMP_GUI["<<component>><br/>GUI Layer — CustomTkinter"]
                ART_VIEWS["<<artifact>><br/>gui/views/<br/>8 Views"]
                ART_COMP["<<artifact>><br/>gui/components/<br/>12 Components"]
                ART_THEME["<<artifact>><br/>theme.py + style.py<br/>(Dark Theme Engine)"]
            end

            subgraph COMP_CORE["<<component>><br/>Core Business Logic"]
                ART_TWEAKREG["<<artifact>><br/>tweak_registry.py<br/>(56 Tweaks × 10 Categories)"]
                ART_RECSVC["<<artifact>><br/>recommendation_service.py<br/>(RecommendationService)"]
                ART_PROFILE["<<artifact>><br/>profile_manager.py<br/>(SAFE/COMPETITIVE/EXTREME)"]
                ART_PARSER["<<artifact>><br/>batch_parser.py<br/>(Script Discovery)"]
                ART_BACKUP["<<artifact>><br/>backup_manager.py<br/>(JSON Backup Store)"]
                ART_SYSINFO["<<artifact>><br/>system_info.py<br/>(Hardware Detection)"]
            end
        end

        subgraph ENV_CMD["<<execution environment>><br/>cmd.exe (Administrator)"]
            ART_OPT["<<artifact>><br/>optimizer.bat v2.0<br/>(Entry Point, 549 lines)"]

            subgraph COMP_BATCH["<<component>><br/>Batch Script Engine — src/"]
                ART_CORE17["<<artifact>><br/>core/ — 17 Modules<br/>(power, services, registry,<br/>network, GPU, storage, etc.)"]
                ART_PROFILES["<<artifact>><br/>profiles/<br/>safe / competitive / extreme"]
                ART_SAFETY["<<artifact>><br/>safety/<br/>validator, rollback,<br/>flight-recorder"]
                ART_BKSCRIPT["<<artifact>><br/>backup/<br/>backup-registry, restore-point"]
                ART_LOG["<<artifact>><br/>logging/logger.bat<br/>(Structured Logging)"]
            end
        end

        subgraph ENV_OS["<<execution environment>><br/>Windows OS Services"]
            ART_REG["<<artifact>><br/>Windows Registry<br/>(HKLM\\SYSTEM, HKCU\\Software)"]
            ART_SVC["<<artifact>><br/>Windows Services<br/>(sc.exe config)"]
            ART_PS["<<artifact>><br/>PowerShell 5.1+<br/>(Appx removal, restore points)"]
            ART_WMI["<<artifact>><br/>WMI / CIM<br/>(Hardware queries)"]
        end

        subgraph ENV_FS["<<datastore>><br/>Local File System"]
            ART_BKJSON["<<artifact>><br/>backup/*.json<br/>(Registry Snapshots)"]
            ART_FLIGHT["<<artifact>><br/>logs/flight-recorder.log<br/>(Audit Trail)"]
            ART_CONFIG["<<artifact>><br/>config.json<br/>(User Preferences)"]
            ART_FONTS["<<artifact>><br/>fonts/<br/>Figtree TTF, Tabler Icons TTF"]
            ART_DATA["<<artifact>><br/>data/<br/>help_content.json,<br/>risk_explanations.json"]
        end
    end

    %% Dependencies
    ART_MAIN --> ART_APP
    ART_APP --> COMP_GUI
    ART_APP --> COMP_CORE
    ART_VIEWS --> ART_THEME
    ART_VIEWS --> ART_COMP
    ART_RECSVC --> ART_TWEAKREG
    ART_RECSVC --> ART_SYSINFO
    ART_PROFILE --> ART_TWEAKREG
    ART_PARSER --> ART_OPT
    ART_BACKUP --> ART_BKJSON
    ART_SYSINFO --> ART_WMI

    ART_OPT --> ART_CORE17
    ART_OPT --> ART_PROFILES
    ART_OPT --> ART_SAFETY
    ART_CORE17 --> ART_REG
    ART_CORE17 --> ART_SVC
    ART_SAFETY --> ART_BKSCRIPT
    ART_BKSCRIPT --> ART_PS
    ART_LOG --> ART_FLIGHT

    COMP_GUI --> ART_FONTS
    COMP_GUI --> ART_DATA
    COMP_CORE --> ART_CONFIG

    style NODE_PC fill:#1a1a2e,stroke:#57c8ff,stroke-width:2px,color:#e0e0e0
    style ENV_PYTHON fill:#16213e,stroke:#4a9eff,stroke-width:1px,color:#e0e0e0
    style ENV_CMD fill:#1a1a2e,stroke:#ff6b6b,stroke-width:1px,color:#e0e0e0
    style ENV_OS fill:#0f3460,stroke:#e94560,stroke-width:1px,color:#e0e0e0
    style ENV_FS fill:#1a1a2e,stroke:#4ecdc4,stroke-width:1px,color:#e0e0e0
    style COMP_GUI fill:#162447,stroke:#57c8ff,stroke-width:1px,color:#e0e0e0
    style COMP_CORE fill:#162447,stroke:#57c8ff,stroke-width:1px,color:#e0e0e0
    style COMP_BATCH fill:#1a1a2e,stroke:#ff6b6b,stroke-width:1px,color:#e0e0e0
```

### 10.2 Deployment Specifications

| Node / Environment | Specification | หมายเหตุ |
|---|---|---|
| **Windows Desktop** | Windows 10 v1903+ / Windows 11, x64, RAM ≥ 4 GB | ต้องมีสิทธิ์ Administrator สำหรับ batch scripts |
| **Python 3.12 Runtime** | CPython 3.12+, venv isolated | Dependencies: customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi, tkextrafont |
| **cmd.exe (Administrator)** | Elevated Command Prompt | optimizer.bat ตรวจสอบ admin rights ก่อนทำงาน |
| **Windows Registry** | HKLM\SYSTEM, HKLM\SOFTWARE, HKCU\Software | Backup ก่อนแก้ไขทุกครั้ง → backup/*.json |
| **Windows Services** | sc.exe, net stop/start | เฉพาะ services ที่ผ่าน safety validation เท่านั้น |
| **PowerShell 5.1+** | System.Management.Automation | ใช้สำหรับ Appx removal, system restore points |
| **WMI / CIM** | Win32_Processor, Win32_VideoController, etc. | Hardware detection สำหรับ benchmark matching |
| **Local File System** | %USERPROFILE%, %TEMP%, application directory | flight-recorder.log, backup JSON, config.json |

### 10.3 Artifact Manifest

| Artifact | Type | ขนาด | Deploy Path |
|---|---|---|---|
| `main.py` | Python Script | Entry point | `clutchg/src/main.py` |
| `ClutchG.exe` | PyInstaller Executable | ~45 MB | `clutchg/dist/ClutchG.exe` |
| `optimizer.bat` | Batch Script | 549 lines | `src/optimizer.bat` |
| `core/*.bat` | Batch Modules | 17 files | `src/core/` |
| `profiles/*.bat` | Profile Scripts | 3 files | `src/profiles/` |
| `safety/*.bat` | Safety Scripts | 4 files | `src/safety/` |
| `backup/*.bat` | Backup Scripts | 2 files | `src/backup/` |
| `fonts/*.ttf` | Font Assets | 4 files (Figtree + Tabler) | `clutchg/src/fonts/` |
| `data/*.json` | Static Data | 2 files | `clutchg/src/data/` |
| `config.json` | User Config | Runtime-generated | Application directory |
| `backup/*.json` | Registry Snapshots | Runtime-generated | Application directory |
| `flight-recorder.log` | Audit Log | Runtime-generated | `logs/` |

### 10.4 Communication Protocols

| Connection | Protocol / Mechanism | ทิศทาง | หมายเหตุ |
|---|---|---|---|
| GUI → Batch Scripts | `subprocess.run()` via cmd.exe | Synchronous | batch_parser.py discovers scripts at startup |
| GUI → Registry | `winreg` (Python stdlib) | Read-only | อ่านค่า current settings เท่านั้น ไม่แก้ไขโดยตรง |
| Batch → Registry | `reg add` / `reg delete` | Read/Write | ผ่าน safety/validator.bat ก่อนทุกครั้ง |
| Batch → Services | `sc config` / `net stop` | Write | เฉพาะ services ใน whitelist |
| GUI → WMI | `wmi` Python package | Read-only | Hardware detection สำหรับ system_info |
| Batch → File System | `echo >>`, `type`, `copy` | Read/Write | Logging, backup, config |
| GUI → File System | Python `pathlib` / `json` | Read/Write | Config, backup JSON, log reading |

### 10.5 Deployment Constraints

| ข้อจำกัด | รายละเอียด | ผลกระทบ |
|---|---|---|
| **DC-01** Administrator Required | Batch scripts ต้องรันด้วยสิทธิ์ admin | main.py ตรวจสอบ admin check ตั้งแต่ startup |
| **DC-02** Windows Only | ไม่รองรับ macOS / Linux | ใช้ Windows-specific APIs: winreg, pywin32, WMI |
| **DC-03** Single Machine | ไม่มี network deployment | Desktop standalone application เท่านั้น |
| **DC-04** No Auto-Update | ไม่มีระบบ update อัตโนมัติ | Manual update ผ่าน GitHub releases |
| **DC-05** Antivirus Compatibility | บาง AV อาจ flag batch scripts | ลงนาม code signing หรือ whitelist แนะนำ |
| **DC-06** Python Version Lock | ต้องใช้ Python 3.12+ | PyInstaller bundle รวม runtime ไว้แล้ว |

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-03-04 | Initial UML diagrams: Context, Use Case, Activity, Component, Sequence, Class |
| v2.0 | 2026-04-06 | SE 701 enrichment: Include/Extend relationships, emoji removal, State Machine diagram, Package diagram, dependency rules |
| v3.0 | 2026-04-10 | Phase 11b Unified Recommendation Refactor: tweak counts 48→56, profile counts 17/35/48→14/44/56, RecommendationService replaces ProfileRecommender in Component/Class/Sequence/Package diagrams, Recommendation dataclass + evidence gate added to Class diagram, benchmark_matched fields, all COMPETITIVE tweak references 35→44 |
| v3.1 | 2026-04-12 | Added §10 Deployment Diagram: deployment topology (mermaid), specifications, artifact manifest, communication protocols, deployment constraints |

---

**จบ Appendix A — UML Diagrams**

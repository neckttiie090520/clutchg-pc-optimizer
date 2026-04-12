# 10 — คู่มือผู้ใช้ (User Manual)

> **มาตรฐาน:** ISO/IEC 29110 — SI.O6 (Software Implementation — Output 6)
> **ETVX:** Entry = SDD v3.3 approved, SRS v3.2 baselined | Task = SI.5 Software Delivery | Verify = QA walkthrough | Exit = User Manual released
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 3.0 | **วันที่:** 2026-04-12
> **อ้างอิง:** SRS v3.2, SDD v3.3, Test Plan v3.1 | ISO/IEC 29110:2016 SI.O6, SE 701 Deployment & Maintenance

---

## 1. ข้อกำหนดระบบ (System Requirements)

### 1.1 ข้อกำหนดขั้นต่ำ (Minimum Requirements)

| รายการ | ข้อกำหนดขั้นต่ำ | หมายเหตุ |
|--------|---------------|---------|
| OS | Windows 10 (version 1903+) / Windows 11 | ต้องเป็น 64-bit edition |
| Python | 3.11 หรือสูงกว่า | สำหรับ development mode เท่านั้น |
| RAM | 4 GB ขึ้นไป | แนะนำ 8 GB สำหรับ E2E testing |
| พื้นที่ดิสก์ | 200 MB | รวม virtual environment และ dependencies |
| สิทธิ์ | **Administrator** | จำเป็นสำหรับ registry modification และ service management |
| Display | 900 x 600 px ขึ้นไป | ขนาดหน้าต่างเริ่มต้น 1000 x 700 px |
| .NET Framework | 4.7.2+ | สำหรับ PowerShell restore point creation |

### 1.2 ข้อกำหนดเพิ่มเติมสำหรับ Executable Mode

| รายการ | ข้อกำหนด |
|--------|---------|
| ไฟล์ | `ClutchG.exe` (สร้างด้วย `python build.py`) |
| Runtime | ไม่ต้องติดตั้ง Python (embedded ใน executable) |
| Antivirus | อาจต้อง whitelist ไฟล์ exe (false positive จาก PyInstaller) |

---

## 2. การติดตั้ง (Installation)

### วิธีที่ 1: Automated Setup (แนะนำ)
```powershell
cd clutchg
.\setup_and_test.bat
```
สคริปต์จะดำเนินการดังนี้:
1. สร้าง Python virtual environment (`venv/`)
2. ติดตั้ง dependencies จาก `requirements.txt`
3. รัน test suite เพื่อยืนยันว่าระบบพร้อมใช้งาน
4. แสดงผลสรุป (จำนวน tests passed/skipped)

### วิธีที่ 2: Manual Installation
```powershell
cd clutchg
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python src\main.py
```

### วิธีที่ 3: Build Executable
```powershell
cd clutchg
python build.py
# ผลลัพธ์: clutchg\dist\ClutchG.exe
```
หลังจาก build สำเร็จ สามารถคัดลอก `ClutchG.exe` ไปรันบนเครื่องอื่นได้โดยไม่ต้องติดตั้ง Python

> **หมายเหตุ:** ไอคอนใช้ฟอนต์ Tabler Icons (tabler-icons.ttf v3.41.1) ที่รวมมากับโปรแกรมแล้ว ไม่ต้องติดตั้งเพิ่มเติม ฟอนต์หลัก Figtree ก็รวมมาในแพ็กเกจเช่นกัน

---

## 3. เริ่มต้นใช้งาน (Getting Started)

### 3.1 การเปิดโปรแกรมครั้งแรก (First Launch)

เมื่อเปิดโปรแกรมครั้งแรก ระบบจะแสดง **Welcome Overlay** เป็น modal 5 ขั้นตอน:

| ขั้นตอน | หัวข้อ | เนื้อหา |
|---------|--------|---------|
| 1 | Welcome to ClutchG | แนะนำหลักการ: Evidence-based tweaks, Full backup, One-click rollback |
| 2 | Home | ภาพรวมหน้า Dashboard |
| 3 | Choose a Profile | แนะนำ 3 profiles: Safe / Competitive / Extreme |
| 4 | Automatic Backups | ระบบ backup อัตโนมัติ: Restore point, Registry backup, Change log |
| 5 | You're All Set | พร้อมใช้งาน |

**ปุ่มนำทาง:** Back, Next, Skip (ข้ามทั้งหมด), Get Started (ขั้นตอนที่ 5)

Welcome overlay จะแสดงเพียงครั้งเดียว หากต้องการดูอีกครั้งให้ reset config ในหน้า Settings

### 3.2 โครงสร้างหน้าจอหลัก

โปรแกรมแบ่งออกเป็น 2 ส่วน:

1. **Sidebar (แถบนำทางด้านซ้าย)**
   - ความกว้าง: 60 px (collapsed) / 210 px (expanded)
   - สลับโหมดด้วยปุ่ม hamburger (☰) / close (✕)
   - รายการเมนู: Dashboard, Optimize, Backup, Help, Settings
   - Active item แสดง highlight pill + accent icon + แถบสีด้านซ้าย
   - เมื่อ collapsed จะแสดง tooltip เมื่อ hover

2. **Content Area (พื้นที่เนื้อหาด้านขวา)**
   - แสดงเนื้อหาของ view ที่เลือก
   - Scrollable สำหรับเนื้อหาที่ยาว

---

## 4. รายละเอียดแต่ละหน้า (View Details)

### 4.1 หน้า Dashboard

**วัตถุประสงค์:** แสดงข้อมูลระบบ, คะแนนฮาร์ดแวร์, และกิจกรรมล่าสุด

**องค์ประกอบหลัก:**

| องค์ประกอบ | รายละเอียด |
|-----------|-----------|
| Header | "Dashboard" + subtitle "System Ready" หรือ "Initializing..." |
| ปุ่ม **Scan System** | มุมขวาบน — รัน hardware detection ใหม่ |
| System Score ring | วงกลมแสดงคะแนน 0-100 (เขียว ≥80, ฟ้า ≥50, แดง <50) |
| Recommendation card | แนะนำ profile ที่เหมาะสม + ปุ่ม **"Apply Optimization"** → นำไปหน้า Tweaks |
| Hardware cards (3 การ์ด) | CPU (ชื่อ, cores, ความเร็ว), GPU (ชื่อ, VRAM), RAM (ขนาด, ความเร็ว) |
| Recent Activity | แสดง 3 กิจกรรมล่าสุดจาก FlightRecorder (ชื่อ, timestamp, สถานะ) |

**ขั้นตอนการใช้งาน:**
1. เปิดโปรแกรม → ระบบตรวจจับฮาร์ดแวร์อัตโนมัติ (async)
2. ดูคะแนน System Score เพื่อประเมินระดับเครื่อง
3. อ่าน Recommendation card เพื่อดู profile ที่แนะนำ
4. คลิก **"Apply Optimization"** เพื่อไปยังหน้า Tweaks หรือคลิก **"Scan System"** เพื่อตรวจจับใหม่

**ระดับคะแนน System Score:**

| คะแนน | Tier | คำแนะนำ |
|--------|------|---------|
| 70+ | Enthusiast | เหมาะกับ EXTREME profile |
| 50–69 | High | เหมาะกับ COMPETITIVE profile |
| 30–49 | Mid | เหมาะกับ SAFE หรือ COMPETITIVE profile |
| <30 | Entry | แนะนำ SAFE profile เท่านั้น |

**สูตรคำนวณ:** CPU (30 คะแนน) + GPU (30 คะแนน) + RAM (20 คะแนน) + Storage (10 คะแนน) + OS Bonus (10 คะแนน)

### 4.2 หน้า Optimize (Tweaks)

**วัตถุประสงค์:** ศูนย์กลางการ optimize ทั้งหมด — แบ่งเป็น 4 แท็บ

#### แท็บ 1: Quick Fix

- **คำอธิบาย:** "One-click packs. Pick one, hit run, done."
- **ตัวกรอง:** General, Advanced, Cleanup, Windows, Utilities
- **Action cards:** แสดง 2 คอลัมน์ ประกอบด้วย:
  - ชื่อ pack, คำอธิบาย, helper text
  - Risk badge (LOW/MEDIUM/HIGH), จำนวน tweaks ในชุด
  - ปุ่ม **"Run"** (สำหรับ tweak packs) หรือ **"Open"** (สำหรับ external links)

**ขั้นตอนการใช้ Quick Fix:**
1. เลือกกลุ่มจากตัวกรอง (General, Advanced, ...)
2. อ่านคำอธิบายของแต่ละ pack
3. คลิก **"Run"** → แสดง confirmation dialog (ชื่อ pack + risk level)
4. ยืนยัน → ระบบแสดง ExecutionDialog:
   - Progress bar แสดงความคืบหน้า
   - Before/after system snapshot
   - Diff แสดงการเปลี่ยนแปลง
5. เสร็จสมบูรณ์ → แสดง toast notification (สีเขียว = สำเร็จ, สีแดง = ผิดพลาด)
6. Restart ถ้าจำเป็น (ระบบจะแจ้ง)

#### แท็บ 2: Profiles

- **Compare toggle:** ปุ่มเปิด/ปิดตารางเปรียบเทียบ profiles
- **Hero card:** Profile ที่แนะนำ (full-width) พร้อม "Recommended" pill
- **Secondary cards:** Profiles ที่เหลือ (2 คอลัมน์)

**รายละเอียด 3 Profiles:**

| Profile | FPS Gain | Risk | Services Disabled | Registry Changes | BCDEdit | Restart |
|---------|---------|------|-------------------|-----------------|---------|---------|
| **Safe** | +3–5% | LOW | 0 | 4 | 0 | No |
| **Competitive** | +8–15% | MEDIUM | 6 | 12 | 2 | Maybe |
| **Extreme** | +15–25% | HIGH | 14 | 22 | 5 | Yes |

**ขั้นตอนการ Apply Profile:**
1. เลือก profile → คลิก **"Apply"**
2. อ่าน warning dialog (แสดง risk level และรายละเอียด)
3. ยืนยัน → ระบบสร้าง backup อัตโนมัติ (ถ้า Auto Backup เปิดอยู่)
4. ExecutionDialog แสดงความคืบหน้าทีละ tweak
5. แสดงผลสรุป (before/after snapshot)
6. Restart ถ้าจำเป็น

#### แท็บ 3: Custom Builder

- **Selection bar:** แสดง "{N} tweaks selected" + ปุ่ม Import, Export, Clear All, Apply {N} Tweaks
- **Search + Filter:** ช่องค้นหา, Risk chips (All/Low/Med/High), Category dropdown
- **รายการ Tweaks (ซ้าย):** จัดกลุ่มตาม category (พับได้), แต่ละรายการมี:
  - Toggle switch เปิด/ปิด
  - ชื่อ tweak, expected gain, risk badge
  - สัญลักษณ์ restart (ถ้าต้อง restart)
  - ลิงก์ "Details ›" → แสดง detail panel
- **Detail panel (ขวา, 380 px):** ข้อมูลเต็มของ tweak:
  - What it does, Why it helps, Expected gain
  - Limitations, Warnings
  - Registry keys ที่เกี่ยวข้อง
  - Meta: reversible?, OS ที่รองรับ, ต้อง admin?

**ขั้นตอนการสร้าง Custom Preset:**
1. ค้นหาหรือกรอง tweaks ที่ต้องการ
2. เปิด toggle switch ทีละรายการ
3. คลิก "Details ›" เพื่อดูรายละเอียดก่อนเลือก
4. กด **"Export"** → บันทึกเป็นไฟล์ .json
5. กด **"Apply {N} Tweaks"** → confirmation → ExecutionDialog → toast

**Import Preset:**
1. คลิก **"Import"** → เลือกไฟล์ .json
2. ระบบเลือก tweaks ตามไฟล์ที่นำเข้า
3. ตรวจสอบ selection → กด Apply

#### แท็บ 4: Info (Education Encyclopedia)

- **Search bar:** ค้นหา tweaks (pill-shaped)
- **Category filter pills:** แสดงจำนวน tweaks ต่อ category
- **Education cards:** แสดงข้อมูลทุก tweak:
  - ชื่อ, คำอธิบาย, risk level, expected gain
  - ปุ่ม **"Learn More"** → modal (600 x 520) แสดงข้อมูลเต็ม + ปุ่ม **"Close"**

**10 Categories ของ Tweaks:**

| Category | ตัวอย่าง Tweaks |
|----------|----------------|
| Power | Ultimate Power Plan, Disable Power Throttling |
| GPU | GPU Scheduling, Fullscreen Optimization |
| Network | TCP Optimization, Nagle Algorithm |
| Services | Disable SysMain, Disable DiagTrack |
| Registry | Game Priority, Mouse Input |
| Storage | Disable Defrag Schedule, TRIM Optimization |
| System | Visual Effects, Background Apps |
| Telemetry | Disable Telemetry, Advertising ID |
| Maintenance | Disable Scheduled Tasks, Windows Tips |
| Input | Keyboard Response, Mouse Precision |

### 4.3 หน้า Backup & Restore Center

**วัตถุประสงค์:** จัดการ backups และ rollback การเปลี่ยนแปลง

**องค์ประกอบหลัก:**

| องค์ประกอบ | รายละเอียด |
|-----------|-----------|
| Header | "{N} backups · Last: {date}" หรือ "No backups yet" |
| ปุ่ม **New Backup** | สร้าง backup ใหม่ → ใส่ชื่อ (default: "Backup_YYYYMMDD_HHMM") |
| Info banner | "Auto-backup is on" — แจ้งว่า registry snapshots สร้างอัตโนมัติ |
| Backup cards | แสดงข้อมูลแต่ละ backup: ชื่อ, วันที่, ประเภท |

**ประเภท Backup:**

| Badge | สี | ความหมาย |
|-------|-----|---------|
| RESTORE POINT | เขียว | มี Windows System Restore Point |
| REGISTRY | ฟ้า | มี Registry snapshot พร้อม per-tweak values |
| REGISTRY ONLY | เทา | มีเฉพาะ Registry snapshot (ไม่มี restore point) |

**ขั้นตอนการสร้าง Backup:**
1. คลิก **"New Backup"**
2. ใส่ชื่อ backup (หรือใช้ชื่อ default)
3. ยืนยัน → ระบบสร้าง restore point (PowerShell) + registry snapshot
4. แสดง toast notification "Backup created successfully"

**ขั้นตอนการ Restore:**
1. เลือก backup card ที่ต้องการ
2. คลิก **"Restore"**
3. อ่าน confirmation dialog
4. ยืนยัน → ระบบ restore registry values → toast "Restart required"
5. Restart เครื่อง

**ขั้นตอนการลบ Backup:**
1. เลือก backup card
2. คลิก **"Delete"** (ปุ่มสีแดง)
3. ยืนยันใน confirmation dialog
4. ระบบลบข้อมูล backup → refresh รายการ → toast

**สถานะพิเศษ:**
- **Empty state:** "No backups yet" + ปุ่ม **"Create Backup"**
- **Error state:** แสดงรายละเอียด error + ปุ่ม **"Retry"**

### 4.4 หน้า Help (Docs)

**วัตถุประสงค์:** คู่มือใช้งานภายในแอป (in-app documentation)

**โครงสร้าง:**
- **Sidebar (200 px ด้านซ้าย):** "Topics" label + search + ปุ่ม **"Clear"** + 9 หัวข้อ
- **Content area (ด้านขวา):** แสดงเนื้อหาตามหัวข้อที่เลือก

**9 หัวข้อ Help:**

| หัวข้อ | เนื้อหา |
|--------|---------|
| Getting Started | ขั้นตอนเริ่มต้น, key points, ลิงก์ไปหน้าต่างๆ |
| Profiles | ภาพรวม + รายละเอียดแต่ละ profile |
| Scripts | Categories + script cards (effects, reversibility) |
| Backup | วิธีสร้าง/restore/ลบ backup |
| Safety | Warning boxes + รายการ "Never Touched" (DEP, UAC, Defender, ASLR, CFG) + Myth/Fact cards |
| Troubleshooting | Problem cards พร้อม solutions |
| About | Version, features, disclaimer, credits |
| FAQ | ถาม-ตอบ |
| Custom Tweaks | วิธีสร้าง/import/export custom presets |

**การค้นหา:** พิมพ์คำค้น → ค้นหาแบบ real-time ข้าม topics ทั้งหมด → แสดง results พร้อม snippets + ปุ่ม **"Open"**

### 4.5 หน้า Settings

**วัตถุประสงค์:** ตั้งค่าพฤติกรรมของแอป

#### Safety Section (Shield Icon)

| การตั้งค่า | ประเภท | ค่าเริ่มต้น | คำอธิบาย |
|-----------|--------|-----------|---------|
| Auto Backup | Switch | ON | สร้าง restore point อัตโนมัติก่อน apply profile |
| Confirm Actions | Switch | ON | ถามยืนยันก่อนรัน tweaks ทุกครั้ง |
| Flight Recorder | Switch | ON | บันทึกทุกการเปลี่ยนแปลง (before/after) สำหรับ rollback |

#### About Section (Info Icon)

- Logo + "ClutchG PC Optimizer" + "v1.0.0 · Windows 10/11"
- Tagline: "A Windows optimizer built for gamers who want real performance gains, not snake oil."
- ลิงก์ **"GitHub"** → เปิด repository ใน browser
- ลิงก์ **"Docs"** → นำไปหน้า Help

**หมายเหตุ:** ทุกการเปลี่ยนแปลง settings จะ auto-save ทันที

---

## 5. การใช้งานขั้นสูง (Advanced Usage)

### 5.1 Custom Presets — Import/Export

**Export:**
1. ไปหน้า Optimize → แท็บ Custom Builder
2. เลือก tweaks ที่ต้องการ (toggle switch)
3. คลิก **"Export"** → เลือกที่บันทึกไฟล์ → ได้ไฟล์ `.json`

**รูปแบบไฟล์ Preset (.json):**
```json
{
  "name": "My Gaming Preset",
  "tweaks": ["power_ultimate", "gpu_scheduling", "disable_sysmain"],
  "created": "2026-04-12T10:30:00"
}
```

**Import:**
1. ไปหน้า Optimize → แท็บ Custom Builder
2. คลิก **"Import"** → เลือกไฟล์ `.json`
3. ระบบจะเลือก tweaks ตามไฟล์ → ตรวจสอบ → กด Apply

**ข้อควรรู้:**
- Preset files สามารถแชร์ระหว่างเครื่องได้
- Tweak IDs ต้องตรงกัน (ถ้า version ต่างกันอาจมี ID ที่ไม่รู้จัก)
- ระบบจะข้าม tweaks ที่ไม่รู้จักและแจ้งเตือน

### 5.2 Batch Script Mode

สำหรับผู้ใช้ขั้นสูงที่ต้องการรัน batch scripts โดยตรง:

```powershell
# รัน optimizer หลัก (ต้อง admin)
cd src
.\optimizer.bat

# รัน profile เฉพาะ
cd src\profiles
.\safe-profile.bat
.\competitive-profile.bat
.\extreme-profile.bat

# สร้าง backup ด้วยมือ
cd src\backup
.\backup-registry.bat
.\restore-point.bat

# Rollback
cd src\safety
.\rollback.bat
```

### 5.3 Test Mode

สำหรับ developers หรือการทดสอบ:
```powershell
python clutchg\src\main.py --test-mode
```
Test mode ทำให้ UI ทำงานโดยไม่ต้อง admin rights (mock operations)

---

## 6. ข้อควรระวัง (Safety Guidelines)

### 6.1 สิ่งที่ ClutchG ไม่ทำ (Never-Do List)

ClutchG ออกแบบตามหลัก **Safety-First** — จะไม่แก้ไขส่วนต่อไปนี้:

| ส่วนที่ไม่แตะต้อง | เหตุผล |
|------------------|--------|
| Windows Defender | จำเป็นสำหรับความปลอดภัย |
| Windows Update (ถาวร) | ต้องรับ security patches ต่อเนื่อง |
| DEP (Data Execution Prevention) | ป้องกัน buffer overflow attacks |
| ASLR (Address Space Layout Randomization) | ป้องกัน memory-based attacks |
| CFG (Control Flow Guard) | ป้องกัน control flow hijacking |
| UAC (User Account Control) | ป้องกันการรัน malware โดยไม่ตั้งใจ |
| Registry ACLs | ป้องกัน unauthorized access |
| System files | ป้องกัน OS corruption |

### 6.2 ก่อนใช้งาน (Pre-Optimization Checklist)

1. **สร้าง Windows Restore Point ด้วยตนเองก่อนเสมอ** (แม้ว่า Auto Backup จะเปิดอยู่)
2. อ่านคำเตือนของแต่ละ tweak ก่อนเลือก
3. เริ่มจาก **SAFE profile ก่อน** → สังเกตผล → ค่อยลอง COMPETITIVE/EXTREME
4. ทดสอบเสถียรภาพ 24-48 ชั่วโมงหลัง apply ก่อนไป profile ถัดไป
5. เก็บ `.json` preset ไว้เสมอเพื่อง่ายต่อการ reproduce
6. ตรวจสอบว่า Flight Recorder เปิดอยู่ (Settings → Safety)

### 6.3 หลังใช้งาน (Post-Optimization)

1. Restart เครื่องถ้าระบบแจ้ง
2. ทดสอบโปรแกรมที่ใช้บ่อย (เกม, productivity apps)
3. ถ้าพบปัญหา → ใช้ Restore Center เพื่อ rollback ทันที
4. ถ้า rollback ไม่สำเร็จ → ใช้ Windows System Restore Point

---

## 7. การแก้ปัญหา (Troubleshooting)

### 7.1 ปัญหาทั่วไป

| ปัญหา | สาเหตุ | แนวทางแก้ไข |
|--------|--------|-----------|
| ไอคอนไม่แสดงหรือแสดงเป็นสี่เหลี่ยม | Font Tabler Icons โหลดไม่สำเร็จ | ตรวจสอบว่า `fonts/tabler-icons.ttf` อยู่ใน directory, restart โปรแกรม |
| "Administrator rights required" | ไม่ได้รันด้วยสิทธิ์ admin | คลิกขวาที่ ClutchG.exe → **Run as Administrator** |
| Profile ไม่ apply | Batch scripts หาไม่เจอ | ตรวจสอบว่า `src/` directory อยู่ครบ, ตรวจสอบ path ใน config |
| ต้องการ undo | ต้องการย้อนค่าเดิม | ไปหน้า Backup → เลือก snapshot → **Restore** |
| Windows ไม่ปกติหลัง apply | Tweak ขัดกับ hardware/software | ใช้ Windows System Restore Point ที่สร้างไว้ก่อน apply |
| โปรแกรมเปิดช้า | Hardware detection ใช้เวลา | รอ system detection เสร็จ (แสดง "Initializing..."), ปกติ 2-5 วินาที |
| Export/Import preset ไม่ทำงาน | ไฟล์ JSON ผิดรูปแบบ | ตรวจสอบ JSON syntax, ตรวจสอบว่า tweak IDs ตรงกับ version ปัจจุบัน |
| Toast notification ไม่หายไป | UI glitch | คลิก toast เพื่อปิด หรือ restart โปรแกรม |

### 7.2 ปัญหาเฉพาะ Profile

| Profile | ปัญหาที่อาจเกิด | แนวทาง |
|---------|----------------|--------|
| SAFE | ไม่มี (low risk) | — |
| COMPETITIVE | บาง services หยุดทำงาน | ตรวจสอบว่า services ที่ปิดไม่กระทบงานหลัก |
| EXTREME | ต้อง restart, อาจมีปัญหากับ peripherals | ทดสอบทุก device หลัง restart, rollback ถ้ามีปัญหา |

### 7.3 Emergency Recovery

หากไม่สามารถเปิดโปรแกรม ClutchG ได้หลัง apply:
1. Boot เข้า Windows (Safe Mode ถ้าจำเป็น)
2. เปิด `src\safety\rollback.bat` ด้วย admin (คลิกขวา → Run as Administrator)
3. หรือใช้ Windows System Restore (Settings → System → Recovery → Open System Restore)
4. เลือก restore point ที่สร้างก่อน apply ClutchG

---

## 8. ถาม-ตอบ (FAQ)

### ทั่วไป

**Q: ClutchG เพิ่ม FPS ได้จริงเท่าไหร่?**
A: ขึ้นอยู่กับฮาร์ดแวร์และสถานะระบบเดิม ผลลัพธ์จริงอยู่ที่ 5–15% (SAFE 2-5%, COMPETITIVE 5-10%, EXTREME 10-15%) — ไม่ใช่ 200% ตามที่โปรแกรมอื่นอ้าง

**Q: ต้อง restart ทุกครั้งไหม?**
A: SAFE profile ไม่ต้อง restart, COMPETITIVE อาจต้อง, EXTREME ต้อง restart เพื่อให้ BCDEdit changes มีผล

**Q: สามารถใช้ร่วมกับ optimizer อื่นได้ไหม?**
A: ไม่แนะนำ เพราะ tweaks อาจขัดกัน ให้ใช้ ClutchG ตัวเดียวและ rollback tweaks จาก optimizer อื่นก่อน

**Q: รองรับ Windows Server ไหม?**
A: ไม่รองรับ — ออกแบบสำหรับ Windows 10/11 Desktop edition เท่านั้น

### Backup & Restore

**Q: Backup เก็บอะไรบ้าง?**
A: Registry values ที่ถูกเปลี่ยนแปลง (before/after), Windows System Restore Point, และ change log ของทุก operation

**Q: สามารถ rollback ทีละ tweak ได้ไหม?**
A: ได้ — ไปหน้า Backup → เลือก snapshot → แสดง per-tweak rollback options พร้อม before/after values

**Q: ถ้าลบ backup แล้วจะ restore ได้ไหม?**
A: ไม่ได้ — เมื่อลบ backup แล้วข้อมูล registry snapshot จะหายไป ใช้ Windows System Restore Point แทน

### Custom Presets

**Q: สามารถแชร์ preset กับเพื่อนได้ไหม?**
A: ได้ — export เป็น .json แล้วส่งให้เพื่อน import แต่ tweak IDs ต้องตรงกัน (ใช้ ClutchG version เดียวกัน)

**Q: import preset แล้วมี tweaks ที่ไม่รู้จัก จะเกิดอะไร?**
A: ระบบจะข้าม tweaks ที่ไม่รู้จักและแสดง warning toast

---

## 9. การถอนการติดตั้ง (Uninstallation)

### 9.1 ก่อนถอนการติดตั้ง

1. **Rollback ทุก tweak ที่ apply ไว้** → ไปหน้า Backup → Restore snapshot ล่าสุด
2. Restart เครื่องหลัง rollback
3. ตรวจสอบว่าระบบกลับสู่สถานะปกติ

### 9.2 ขั้นตอนการถอน

**สำหรับ Development Mode (Python):**
```powershell
cd clutchg
deactivate                    # ออกจาก virtual environment
rmdir /s /q venv              # ลบ virtual environment
cd ..
rmdir /s /q clutchg           # ลบทั้ง directory
```

**สำหรับ Executable Mode:**
1. ลบ `ClutchG.exe`
2. ลบ folder `src/` (batch scripts)
3. ลบ folder `logs/` (ถ้ามี)

### 9.3 ล้าง Configuration

ClutchG เก็บ config ไว้ที่:
- `clutchg/config/` — application settings
- `clutchg/backups/` — registry backup snapshots
- `clutchg/logs/` — flight recorder logs

ลบ directories เหล่านี้เพื่อล้าง configuration ทั้งหมด

> **สำคัญ:** ถ้ายังไม่ได้ rollback tweaks ก่อนลบ — tweak values จะยังคงอยู่ใน Windows Registry ต้อง restore ด้วยมือหรือใช้ Windows System Restore Point

---

## 10. อภิธานศัพท์ (Glossary)

| คำศัพท์ | ความหมาย |
|---------|---------|
| **Tweak** | การปรับแต่งค่า Windows เพื่อเพิ่มประสิทธิภาพ เช่น การแก้ registry หรือปิด service |
| **Profile** | ชุดของ tweaks ที่จัดกลุ่มตามระดับความเสี่ยง (SAFE / COMPETITIVE / EXTREME) |
| **Preset** | ชุด tweaks ที่ผู้ใช้กำหนดเอง (custom) สามารถ export/import เป็น JSON ได้ |
| **FlightRecorder** | ระบบบันทึกการเปลี่ยนแปลง (before/after) ของทุก tweak เพื่อรองรับ rollback |
| **Snapshot** | จุดบันทึกสถานะ ณ เวลาที่ apply profile ประกอบด้วยรายการ TweakChange ทั้งหมด |
| **Rollback** | การย้อนค่ากลับเป็นค่าเดิมก่อน apply tweak |
| **Restore Point** | จุดกู้คืน Windows ที่สร้างโดย PowerShell (Checkpoint-Computer) |
| **Registry** | ฐานข้อมูลกลางของ Windows ที่เก็บค่า configuration ของระบบและโปรแกรม |
| **Risk Level** | ระดับความเสี่ยงของ tweak: LOW (ปลอดภัย), MEDIUM (ระวัง), HIGH (เฉพาะผู้เชี่ยวชาญ) |
| **Batch Script** | ไฟล์ .bat ที่รันคำสั่ง Windows เพื่อ apply tweaks (อยู่ใน `src/`) |
| **System Score** | คะแนนฮาร์ดแวร์ 0-100 คำนวณจาก CPU(30) + GPU(30) + RAM(20) + Storage(10) + OS(10) |
| **Tier** | ระดับเครื่อง: entry (<30), mid (30-49), high (50-69), enthusiast (70+) |
| **ExecutionDialog** | หน้าต่างแสดงความคืบหน้าขณะ apply tweaks พร้อม before/after snapshot |
| **Toast** | การแจ้งเตือนชั่วคราวที่แสดงมุมล่างของหน้าจอ (success/error/warning/info) |
| **BCDEdit** | เครื่องมือ Windows สำหรับแก้ไข Boot Configuration Data (ใช้ใน EXTREME profile) |
| **DRE** | Defect Removal Effectiveness — เมตริกวัดประสิทธิภาพการกำจัดข้อบกพร่อง (SE 702) |

---

## 11. ข้อมูลเพิ่มเติม (Additional Resources)

| เอกสาร | ที่อยู่ | เนื้อหา |
|--------|--------|---------|
| Quick Start Guide | `clutchg/QUICKSTART.md` | คู่มือเริ่มต้นแบบย่อ |
| Developer Guide | SDD v3.3 | สถาปัตยกรรม, class diagrams, module reference |
| Safety Documentation | Test Plan v3.1 §6 | Test design techniques, safety verification |
| Test Results | Test Record v2.2 | ผลการทดสอบทั้งหมด (496+ collected, 432+ passed) |
| Change History | Change Request v2.1 | ประวัติการเปลี่ยนแปลง 4 CRs |
| Traceability | Traceability v2.1 | ตาราง FR → SDD → Test → Result |
| Research Docs | `docs/01-*.md` through `docs/16-*.md` | งานวิจัยพื้นฐาน 16 เอกสาร |

---

## 12. ประวัติการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายการแก้ไข |
|----------|--------|---------|------------|
| 1.0 | 2026-03-04 | nextzus | สร้างเอกสารเริ่มต้น: ข้อกำหนดระบบ, การติดตั้ง, คู่มือใช้งาน 6 หน้า, ข้อควรระวัง, แก้ปัญหา |
| 2.0 | 2026-04-06 | nextzus | เพิ่ม ETVX header, แก้เส้นทางติดตั้ง (ไม่ hardcode), แก้ entry point เป็น main.py, แก้ icon font เป็น Tabler Icons, ลบ emojis, เพิ่มอภิธานศัพท์ 12 คำ, เพิ่มวิธี build executable, อัพเดตข้อมูลอ้างอิง |
| 3.0 | 2026-04-12 | nextzus | Major expansion: เพิ่มรายละเอียด Welcome Overlay 5 ขั้นตอน, โครงสร้างหน้าจอ, รายละเอียด 4 แท็บ Optimize (Quick Fix, Profiles, Custom Builder, Info), ขั้นตอน step-by-step ทุกหน้า, System Score สูตรคำนวณ, FAQ 10 คำถาม, Custom Presets (import/export พร้อม JSON format), Batch Script Mode, Test Mode, Emergency Recovery, การถอนการติดตั้ง, อภิธานศัพท์เพิ่ม 4 คำ (ExecutionDialog, Toast, BCDEdit, DRE), อัปเดต version refs (SRS v3.2, SDD v3.3, Test Plan v3.1), อัปเดต test counts (496+ collected, 432+ passed) |

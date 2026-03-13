# ClutchG PC Optimizer

[English](README.md) | **ภาษาไทย**

ซอฟต์แวร์ปรับแต่ง Windows สำหรับลดความหน่วง (latency) และเพิ่ม FPS ในเกมยิงมุมมองบุคคลที่หนึ่ง พัฒนาจากการวิเคราะห์เครื่องมือปรับแต่ง Windows 28 ตัวบน GitHub แล้วคัดเฉพาะเทคนิคที่มีหลักฐานรองรับ ไม่ปิดระบบรักษาความปลอดภัยของ Windows และย้อนกลับได้ทุกการเปลี่ยนแปลง

## สารบัญ

- [ภาพรวมโปรเจกต์](#ภาพรวมโปรเจกต์)
- [โครงสร้างระบบ](#โครงสร้างระบบ)
- [ความต้องการของระบบ](#ความต้องการของระบบ)
- [การติดตั้งและใช้งาน](#การติดตั้งและใช้งาน)
- [โปรไฟล์การปรับแต่ง](#โปรไฟล์การปรับแต่ง)
- [ผลลัพธ์ที่คาดหวังได้จริง](#ผลลัพธ์ที่คาดหวังได้จริง)
- [ระบบความปลอดภัย](#ระบบความปลอดภัย)
- [การทดสอบ](#การทดสอบ)
- [สิ่งที่ห้ามทำเด็ดขาด](#สิ่งที่ห้ามทำเด็ดขาด)
- [ความเชื่อที่ไม่จริง](#ความเชื่อที่ไม่จริง)
- [การพัฒนาต่อ](#การพัฒนาต่อ)
- [สัญญาอนุญาต](#สัญญาอนุญาต)

---

## ภาพรวมโปรเจกต์

ClutchG ประกอบด้วยสองส่วนหลักที่ทำงานร่วมกัน

**Batch Optimizer** (`src/`) คือชุดสคริปต์ batch ที่แก้ไขค่า Windows โดยตรง ครอบคลุมการจัดการพลังงาน, BCDEdit, services, registry, network, GPU, storage และ maintenance  สคริปต์เหล่านี้ทำงานผ่าน Command Prompt ในโหมด Administrator

**ClutchG GUI** (`clutchg/`) คือแอปพลิเคชัน Python ที่สร้างด้วย CustomTkinter ทำหน้าที่เป็นหน้าจอควบคุมสำหรับสคริปต์ batch  ตรวจจับฮาร์ดแวร์อัตโนมัติ แนะนำโปรไฟล์ที่เหมาะสม แสดงระดับความเสี่ยงด้วยรหัสสี และมีศูนย์ย้อนกลับ (Restore Center) สำหรับเรียกคืนค่าเดิม  รองรับทั้งภาษาไทยและอังกฤษ

### หลักการออกแบบ

| หลักการ | รายละเอียด |
|---------|-----------|
| อิงหลักฐาน | ทุกเทคนิคมีคำอธิบายทางเทคนิคและแหล่งอ้างอิง |
| ปลอดภัย | ไม่ปิด Windows Defender, UAC, DEP หรือ Windows Update |
| ย้อนกลับได้ | สร้าง restore point และ backup registry ก่อนแก้ไขทุกครั้ง |
| โปร่งใส | เปิดซอร์สโค้ดทั้งหมด บันทึกทุกการเปลี่ยนแปลงลง flight recorder |
| รองรับ Windows 10 22H2+ และ Windows 11 | ตรวจรุ่น OS ก่อนใช้เทคนิคเฉพาะเวอร์ชัน |

---

## โครงสร้างระบบ

```
clutchg-pc-optimizer/
├── src/                            # Batch Optimizer
│   ├── optimizer.bat               # จุดเริ่มต้นหลัก
│   ├── core/                       # โมดูลหลัก (17 ไฟล์)
│   │   ├── power-manager.bat       # จัดการ power plan
│   │   ├── bcdedit-manager.bat     # ปรับค่า boot configuration
│   │   ├── service-manager.bat     # จัดการ Windows services
│   │   ├── registry-utils.bat      # แก้ไข registry
│   │   ├── network-manager.bat     # ปรับแต่ง network stack
│   │   ├── gpu-optimizer.bat       # ปรับค่า GPU
│   │   ├── storage-optimizer.bat   # ปรับแต่ง storage
│   │   ├── system-detect.bat       # ตรวจจับฮาร์ดแวร์
│   │   └── ...                     # enhanced variants, debloater, input, maintenance
│   ├── profiles/                   # โปรไฟล์ 3 ระดับ
│   │   ├── safe-profile.bat
│   │   ├── competitive-profile.bat
│   │   └── extreme-profile.bat
│   ├── safety/                     # ระบบตรวจสอบและย้อนกลับ
│   ├── backup/                     # สำรองข้อมูล registry และ restore point
│   └── logging/                    # บันทึก log
│
├── clutchg/                        # ClutchG GUI Application
│   ├── src/
│   │   ├── main.py                 # จุดเริ่มต้น GUI
│   │   ├── core/                   # business logic (13 โมดูล)
│   │   │   ├── config.py           # ตั้งค่าแอป
│   │   │   ├── system_info.py      # ตรวจจับฮาร์ดแวร์
│   │   │   ├── profile_manager.py  # จัดการโปรไฟล์
│   │   │   ├── profile_recommender.py # แนะนำโปรไฟล์ตามฮาร์ดแวร์
│   │   │   ├── flight_recorder.py  # บันทึกทุกการเปลี่ยนแปลง
│   │   │   ├── batch_parser.py     # แยกวิเคราะห์สคริปต์ batch
│   │   │   └── ...
│   │   ├── gui/                    # UI layer
│   │   │   ├── theme.py            # ธีมและสี
│   │   │   ├── views/              # หน้าจอ 6 หน้า
│   │   │   └── components/         # คอมโพเนนต์ 15 ตัว
│   │   ├── models/                 # โครงสร้างข้อมูล
│   │   ├── data/                   # ข้อมูล help content (TH/EN)
│   │   └── utils/                  # ตัวช่วย (logger, admin check)
│   ├── tests/                      # ชุดทดสอบ (346 test methods)
│   │   ├── unit/                   # 259 unit tests
│   │   ├── integration/            # 23 integration tests
│   │   └── e2e/                    # 64 E2E tests
│   ├── requirements.txt            # dependencies สำหรับรัน
│   ├── requirements-test.txt       # dependencies สำหรับทดสอบ
│   ├── build.py                    # สร้างไฟล์ .exe ด้วย PyInstaller
│   └── pytest.ini                  # ตั้งค่า pytest
│
├── docs/                           # เอกสารงานวิจัย
│   ├── 01-research-overview.md     # ขอบเขตและวิธีวิจัย
│   ├── 02-repo-analysis/           # วิเคราะห์เครื่องมือรายตัว
│   ├── 03-tweak-taxonomy.md        # จัดหมวดเทคนิคทั้งหมด
│   ├── 04-risk-classification.md   # จัดระดับความเสี่ยง
│   ├── 05-windows-internals.md     # เจาะลึก Windows internals
│   ├── 06-performance-impact.md    # ผลกระทบต่อ performance จริง
│   └── 07-best-practices.md        # แนวปฏิบัติที่แนะนำ
│
└── .github/workflows/ci.yml       # GitHub Actions CI pipeline
```

---

## ความต้องการของระบบ

### สำหรับ Batch Optimizer
- Windows 10 22H2 ขึ้นไป หรือ Windows 11
- สิทธิ์ Administrator

### สำหรับ ClutchG GUI
- Python 3.11 ขึ้นไป
- Windows 10 22H2 ขึ้นไป หรือ Windows 11
- Dependencies: customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi

---

## การติดตั้งและใช้งาน

### ใช้ Batch Optimizer โดยตรง

```batch
:: เปิด Command Prompt ในโหมด Administrator
:: ไปที่โฟลเดอร์ src
cd src
optimizer.bat
```

เลือกโปรไฟล์ที่ต้องการ ระบบจะสร้าง restore point อัตโนมัติก่อนเริ่มปรับแต่ง

### ใช้ ClutchG GUI

```powershell
# สร้าง virtual environment
python -m venv venv
venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r clutchg\requirements.txt

# รันแอป
python clutchg\src\main.py
```

### สร้างไฟล์ .exe

```powershell
cd clutchg
python build.py
# ผลลัพธ์: clutchg\dist\ClutchG.exe
```

---

## โปรไฟล์การปรับแต่ง

### SAFE (แนะนำสำหรับผู้เริ่มต้น)

เหมาะกับการใช้งานทั่วไปและผู้ที่ต้องการความเสถียร  ปรับเฉพาะค่าที่ Microsoft จัดให้เป็นตัวเลือกอยู่แล้ว

| หมวด | สิ่งที่ปรับ | ความเสี่ยง |
|------|-----------|-----------|
| Power | เปิด Ultimate Performance power plan | ต่ำมาก |
| GPU | เปิด HAGS (Hardware-Accelerated GPU Scheduling) | ต่ำมาก |
| Storage | เปิด Storage Sense อัตโนมัติ | ต่ำมาก |
| Services | ปิดเฉพาะ telemetry services | ต่ำ |

ผลลัพธ์ที่คาดหวัง: FPS เพิ่มขึ้นประมาณ 2-5%

### COMPETITIVE (สำหรับเล่นเกม)

เหมาะกับเกมเมอร์ที่ต้องการ performance เพิ่มเติม  ปรับ service และ network เพิ่ม แต่ยังมี safety whitelist ป้องกันการปิด service ที่สำคัญ

| หมวด | สิ่งที่ปรับ | ความเสี่ยง |
|------|-----------|-----------|
| Power | ทุกอย่างใน SAFE | ต่ำ |
| Services | ปิด Xbox, telemetry และ service ที่ไม่จำเป็น | ต่ำ |
| Network | ปรับ TCP stack, ปิด Nagle's Algorithm | ต่ำ |
| GPU | จัดการ GPU power management | ต่ำ |

ผลลัพธ์ที่คาดหวัง: FPS เพิ่มขึ้นประมาณ 5-10%

### EXTREME (สำหรับผู้เชี่ยวชาญเท่านั้น)

ปรับแต่งเชิงรุก  อาจทำให้ฟีเจอร์บางอย่างของ Windows ใช้งานไม่ได้ ต้องเข้าใจผลกระทบก่อนใช้

| หมวด | สิ่งที่ปรับ | ความเสี่ยง |
|------|-----------|-----------|
| ทุกอย่างใน COMPETITIVE | + | ปานกลาง |
| BCDEdit | ปรับ boot configuration ขั้นสูง | ปานกลาง |
| Services | ปิด service เชิงรุก | ปานกลาง |

ผลลัพธ์ที่คาดหวัง: FPS เพิ่มขึ้นประมาณ 10-15% แต่มีความเสี่ยงที่ฟีเจอร์บาง Windows จะหยุดทำงาน

---

## ผลลัพธ์ที่คาดหวังได้จริง

ตัวเลขต่อไปนี้มาจากการวิเคราะห์เปรียบเทียบเครื่องมือ 28 ตัว ไม่ใช่ตัวเลขที่โฆษณาเกินจริง

| เทคนิค | ผลกระทบต่อ FPS | หมายเหตุ |
|--------|---------------|---------|
| ปรับค่า GPU driver | 2-15% | ขึ้นอยู่กับ GPU รุ่นและเกม |
| Power plan optimization | 2-5% | ได้ผลดีกับ CPU ที่รองรับ P-state/C-state |
| BCDEdit tweaks ที่ปลอดภัย | 1-4% | เห็นผลชัดในเกมที่ไวต่อ latency |
| ลด background apps | 1-3% | ลด CPU/RAM contention |

**รวมทั้งหมด**: คาดหวังได้ 5-15% ตามสเปคเครื่องและเกมที่เล่น  ไม่มีเครื่องมือไหนเพิ่ม FPS ได้ 200% อย่างที่หลายตัวอ้าง

---

## ระบบความปลอดภัย

ClutchG ออกแบบระบบความปลอดภัยเป็น 4 ชั้น

### 1. ก่อนปรับแต่ง
- ตรวจสิทธิ์ Administrator ก่อนเริ่มงาน
- ตรวจรุ่น OS และฮาร์ดแวร์ เพื่อใช้เฉพาะเทคนิคที่เข้ากันได้
- สร้าง System Restore Point อัตโนมัติ
- สำรอง registry keys ที่จะแก้ไข

### 2. ระหว่างปรับแต่ง
- FlightRecorder บันทึกทุกการเปลี่ยนแปลงพร้อมค่าก่อน/หลัง
- Validator ตรวจสอบความถูกต้องของค่าก่อนเขียน
- Logger บันทึกทุกขั้นตอนลงไฟล์ log

### 3. หลังปรับแต่ง
- Restore Center แสดง timeline ของการเปลี่ยนแปลงทั้งหมด
- ย้อนกลับได้ทีละรายการ (per-tweak rollback)
- ดาวน์โหลด rollback script สำหรับกู้คืนด้วยตนเองได้

### 4. UI Layer
- แสดงระดับความเสี่ยงด้วยรหัสสี (เขียว = ต่ำ, ส้ม = ปานกลาง, แดง = สูง)
- ปุ่ม "?" ให้คำอธิบายทุกเทคนิค รองรับทั้งไทยและอังกฤษ
- แนะนำโปรไฟล์อัตโนมัติจากข้อมูลฮาร์ดแวร์จริง

---

## การทดสอบ

ชุดทดสอบอัตโนมัติประกอบด้วย 346 test methods แบ่งเป็น

| ประเภท | จำนวน | ขอบเขต |
|--------|------|--------|
| Unit tests | 259 | ทดสอบ module แต่ละตัวแยกจากระบบจริง |
| Integration tests | 23 | ทดสอบการทำงานร่วมกันระหว่าง module |
| E2E tests | 64 | ทดสอบ GUI แบบ end-to-end ผ่าน pywinauto |

Code coverage อยู่ที่ประมาณ 89%

### รันชุดทดสอบ

```powershell
cd clutchg

# ติดตั้ง test dependencies
pip install -r requirements-test.txt

# รันทั้งหมด
pytest

# รันเฉพาะ unit tests
pytest tests\unit -m unit

# รันพร้อม coverage report
pytest --cov=src tests/
```

### CI/CD

GitHub Actions รันชุดทดสอบ unit และ integration อัตโนมัติบน `windows-latest` ทุกครั้งที่ push หรือเปิด pull request  E2E tests ไม่รันบน CI เนื่องจากต้องการ desktop session

---

## สิ่งที่ห้ามทำเด็ดขาด

ClutchG ไม่มีเทคนิคต่อไปนี้อยู่ในโปรไฟล์ใด ๆ เพราะส่งผลเสียต่อความปลอดภัยโดยไม่ได้ performance คุ้มค่า

- ปิด Windows Defender
- ปิด DEP (Data Execution Prevention)
- ปิด ASLR หรือ CFG
- ปิด Driver Signature Enforcement
- ปิด Windows Update ถาวร
- ปิด UAC (User Account Control)
- แก้ไข ACL ของ registry

---

## ความเชื่อที่ไม่จริง

จากการวิเคราะห์เครื่องมือ 28 ตัว พบว่ามีเทคนิคหลายตัวที่แพร่หลายแต่ไม่ได้ผลจริง

| ความเชื่อ | ความจริง |
|-----------|---------|
| Windows สำรอง bandwidth 20% สำหรับ QoS | ไม่จริง  QoS จำกัดเฉพาะ traffic ที่ tag ไว้เท่านั้น ไม่กระทบเกม |
| Timer resolution service เพิ่ม FPS | ล้าสมัยแล้ว  Windows 10 2004 เป็นต้นมาจัดการ timer resolution แบบ per-process |
| ปิด service 100 ตัวทำให้เร็วขึ้น | เสี่ยงเกินไป  service หลายตัวที่ปิดทำให้ฟีเจอร์พังโดยไม่ได้ performance เพิ่ม |
| แก้ registry เกี่ยวกับ network ลด ping | ผลน้อยมากจนวัดไม่ได้  ปัจจัยหลักคือ ISP, routing และ server location |

---

## การพัฒนาต่อ

### สำหรับนักพัฒนา

```powershell
# Clone
git clone https://github.com/neckttiie090520/clutchg-pc-optimizer.git
cd clutchg-pc-optimizer

# สร้าง virtual environment
python -m venv venv
venv\Scripts\activate

# ติดตั้ง dependencies ทั้งรันและทดสอบ
pip install -r clutchg\requirements.txt
pip install -r clutchg\requirements-test.txt

# รันแอป
python clutchg\src\main.py

# รันชุดทดสอบ
cd clutchg
pytest
```

### โครงสร้างโค้ดสำคัญ

- โลจิกทางธุรกิจอยู่ใน `clutchg/src/core/` แยกจาก GUI
- หน้าจอ GUI อยู่ใน `clutchg/src/gui/views/`
- คอมโพเนนต์ที่ใช้ซ้ำอยู่ใน `clutchg/src/gui/components/`
- เอกสารงานวิจัยอยู่ใน `docs/`
- สคริปต์ batch อยู่ใน `src/core/` จัดเป็นโมดูลตามหมวดเทคนิค

---

## สัญญาอนุญาต

MIT License

---

## ข้อจำกัดความรับผิดชอบ

ซอฟต์แวร์นี้แก้ไขค่าระบบของ Windows  แม้จะผ่านการวิจัยและทดสอบแล้ว ผลลัพธ์อาจแตกต่างกันตามฮาร์ดแวร์และการตั้งค่าของแต่ละเครื่อง ผู้ใช้ควร

1. สำรองข้อมูลก่อนปรับแต่งทุกครั้ง
2. เริ่มจากโปรไฟล์ SAFE ก่อน
3. วัดผลก่อนและหลังเพื่อเปรียบเทียบ
4. อ่านคำอธิบายของแต่ละเทคนิคก่อนเปิดใช้

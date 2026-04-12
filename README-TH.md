<h1 align="center">
  <br>
  <img src="img/C.GG-Photoroom.png" alt="ClutchG" width="120">
  <br>
  ClutchG PC Optimizer
  <br>
</h1>

<p align="center">
  <strong>ซอฟต์แวร์ปรับแต่ง Windows จากงานวิจัยจริง ไม่ใช่ความเชื่อ</strong>
</p>

<p align="center">
  <a href="#จุดเด่น">จุดเด่น</a> &middot;
  <a href="#ภาพหน้าจอ">ภาพหน้าจอ</a> &middot;
  <a href="#เริ่มต้นใช้งาน">เริ่มต้นใช้งาน</a> &middot;
  <a href="#โปรไฟล์">โปรไฟล์</a> &middot;
  <a href="#งานวิจัย">งานวิจัย</a> &middot;
  <a href="README.md">English</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-0078D4?logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/python-3.11+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/tests-477%20passed-2ea44f" alt="Tests">
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="License">
</p>

---

## ClutchG คืออะไร?

ClutchG เป็นเครื่องมือปรับแต่ง Windows ที่สร้างจากการวิจัยเปรียบเทียบ **เครื่องมือปรับแต่ง 23 ตัว** แบบ open-source บน GitHub (โค้ดรวมกว่า 50,000 บรรทัด) สำรวจเทคนิคปรับแต่งกว่า **200 รายการ** และจำแนก **56 เทคนิคที่ผ่านการคัดกรอง** ออกเป็น 10 หมวด พร้อมจัดระดับความเสี่ยง 3 ชั้น (ต่ำ / ปานกลาง / สูง) เพื่อแยกเทคนิคที่ได้ผลจริงออกจากเทคนิคหลอกหรือเทคนิคอันตราย

ผลลัพธ์คือ batch optimizer แบบ modular พร้อม GUI สมัยใหม่ ที่ปรับแต่งเฉพาะเทคนิคที่มีหลักฐานรองรับ -- ปลอดภัย โปร่งใส และย้อนกลับได้ทุกขั้นตอน

### หลักการออกแบบ

| | หลักการ | รายละเอียด |
|---|---------|-----------|
| **หลักฐาน** | ทุกเทคนิคมีเอกสารทางเทคนิครองรับ | ไม่มีเทคนิค "เชื่อเถอะ" |
| **ปลอดภัย** | ไม่ปิด Defender, UAC, DEP หรือ Windows Update | ไม่ยอมแลกความปลอดภัย |
| **ย้อนกลับ** | backup อัตโนมัติก่อนทุกการเปลี่ยนแปลง rollback ทีละรายการได้ | ย้อนกลับได้ทุกอย่าง ทุกเมื่อ |
| **โปร่งใส** | ทุก action ถูกบันทึกลง flight recorder | ตรวจสอบย้อนหลังได้เสมอ |
| **ซื่อตรง** | ผลลัพธ์จริง 5-15% ไม่ใช่ 200% | ไม่โฆษณาเกินจริง |

---

## จุดเด่น

- **3 โปรไฟล์** -- SAFE, COMPETITIVE, EXTREME จัดเทคนิคตามระดับความเสี่ยง
- **56 เทคนิคที่ผ่านการคัดกรอง** ครอบคลุม 10 หมวด: telemetry, input/latency, power, GPU, network, services, memory, boot/BCDEdit, visual effects, cleanup/debloat
- **ตรวจจับฮาร์ดแวร์อัตโนมัติ** -- ระบุ CPU, GPU, RAM แล้วแนะนำโปรไฟล์ที่เหมาะสม
- **สารานุกรมเทคนิค** -- ทุกเทคนิคมีเอกสารครบ: ทำอะไร ทำไมถึงช่วย ข้อจำกัด ระดับความเสี่ยง และผลลัพธ์ที่คาดหวัง
- **Flight Recorder** -- บันทึกทุกการเปลี่ยนแปลงพร้อมค่าก่อน/หลัง
- **Restore Center** -- ดู timeline การเปลี่ยนแปลงทั้งหมด ย้อนกลับทีละรายการได้
- **ธีมมืดสมัยใหม่** -- สไตล์ Windows 11 / Sun Valley พร้อมฟอนต์ Figtree

---

## ภาพหน้าจอ

<p align="center">
  <img src="UX/UI design/latest/01-dashboard.png" width="720" alt="Dashboard">
  <br><em>หน้า Dashboard แสดงข้อมูลฮาร์ดแวร์และแนะนำโปรไฟล์</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/02-tweaks-quick-fix.png" width="720" alt="Tweaks - Quick Fix">
  <br><em>Quick Fix ปรับแต่งอย่างรวดเร็วด้วยคลิกเดียว</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/03-tweaks-profiles.png" width="720" alt="Tweaks - Profiles">
  <br><em>เลือกโปรไฟล์ SAFE, COMPETITIVE หรือ EXTREME ตามระดับความเสี่ยง</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/04-tweaks-custom.png" width="720" alt="Tweaks - Custom">
  <br><em>สร้างชุดปรับแต่งเอง เลือกเทคนิคทีละตัวพร้อมดูระดับความเสี่ยง</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/05-tweaks-education.png" width="720" alt="Tweaks - Education">
  <br><em>สารานุกรมเทคนิค แสดงระดับความเสี่ยง หมวดหมู่ และคำอธิบายละเอียด</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/06-backup.png" width="720" alt="Backup">
  <br><em>ศูนย์สำรองข้อมูลและย้อนกลับ พร้อม timeline</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/07-docs.png" width="720" alt="Documentation">
  <br><em>ระบบช่วยเหลือในตัว พร้อมเอกสารและคู่มือ</em>
</p>

<p align="center">
  <img src="UX/UI design/latest/08-settings.png" width="720" alt="Settings">
  <br><em>ตั้งค่าธีมและโปรไฟล์</em>
</p>

---

## เริ่มต้นใช้งาน

### วิธี A: ใช้ GUI (แนะนำ)

```powershell
# Clone repository
git clone https://github.com/neckttiie090520/clutchg-pc-optimizer.git
cd clutchg-pc-optimizer

# สร้าง virtual environment
python -m venv venv
venv\Scripts\activate

# ติดตั้ง dependencies
pip install -r clutchg\requirements.txt

# เปิด ClutchG
python clutchg\src\main.py
```

### วิธี B: ใช้ Batch Scripts โดยตรง

```batch
:: เปิด Command Prompt ในโหมด Administrator
cd src
optimizer.bat
```

### สร้างไฟล์ .exe

```powershell
cd clutchg
python build.py
# ผลลัพธ์: clutchg\dist\ClutchG.exe
```

---

## โปรไฟล์

| | โปรไฟล์ | ความเสี่ยง | เหมาะกับ | ผลลัพธ์ที่คาดหวัง |
|---|---------|-----------|---------|-----------------|
| | **SAFE** | ต่ำมาก | ทุกคน | FPS เพิ่ม 2-5% |
| | **COMPETITIVE** | ต่ำ | เกมเมอร์ | FPS เพิ่ม 5-10% |
| | **EXTREME** | ปานกลาง | ผู้เชี่ยวชาญเท่านั้น | FPS เพิ่ม 10-15% |

### SAFE

ปรับ power plan, เปิด HAGS, เปิด Storage Sense, ปิดเฉพาะ telemetry services ไม่มีอะไรที่ทำให้ฟีเจอร์พัง

### COMPETITIVE

เพิ่มการปรับ network stack (Nagle's Algorithm, TCP optimization), จัดการ Xbox/telemetry services, ปรับ GPU power management ยังมี safety whitelist ป้องกันการปิด service สำคัญ

### EXTREME

จัดการ service เชิงรุก, ปรับ BCDEdit boot configuration, ปรับ network stack เต็มรูปแบบ ฟีเจอร์บางอย่างของ Windows อาจหยุดทำงาน ต้องเข้าใจผลกระทบก่อนใช้

---

## โครงสร้างโปรเจกต์

```
clutchg-pc-optimizer/
├── src/                              # Batch Optimizer Engine
│   ├── optimizer.bat                 # จุดเริ่มต้น (v2.0, ต้องมีสิทธิ์ admin)
│   ├── core/                         # โมดูลปรับแต่ง 16 ตัว
│   ├── profiles/                     # SAFE / COMPETITIVE / EXTREME
│   ├── safety/                       # ตรวจสอบ, ย้อนกลับ, flight recorder
│   ├── backup/                       # สำรอง registry, restore point
│   ├── logging/                      # บันทึก log
│   ├── ui/                           # ระบบเมนู
│   └── validation/                   # ตรวจสอบ input และ benchmark
│
├── clutchg/                          # แอปพลิเคชัน GUI (Python)
│   ├── src/
│   │   ├── main.py                   # จุดเริ่มต้น
│   │   ├── core/                     # business logic (15 โมดูล)
│   │   │   ├── tweak_registry.py     # ฐานความรู้กลาง (56 เทคนิค)
│   │   │   ├── profile_manager.py    # จับคู่โปรไฟล์กับเทคนิค
│   │   │   ├── batch_parser.py       # ค้นหาเทคนิคจากไฟล์ .bat
│   │   │   ├── action_catalog.py     # ชุด action สำหรับผู้ใช้
│   │   │   ├── flight_recorder.py    # บันทึกการเปลี่ยนแปลงพร้อมค่าก่อน/หลัง
│   │   │   └── ...                   # backup, config, system info ฯลฯ
│   │   ├── gui/views/               # หน้าจอ 8 หน้า
│   │   ├── gui/components/          # คอมโพเนนต์ 12 ตัว
│   │   └── gui/theme.py             # ระบบธีมมืด (Sun Valley)
│   ├── tests/                        # ชุดทดสอบ 477 tests (unit + integration + E2E)
│   │   ├── unit/                     # ไฟล์ทดสอบ 16 ไฟล์
│   │   ├── integration/              # ไฟล์ทดสอบ 2 ไฟล์
│   │   └── e2e/                      # โครงสร้าง Page Object Model
│   └── build.py                      # สร้างไฟล์ .exe ด้วย PyInstaller
│
├── docs/                             # เอกสารวิจัยและเทคนิค
│   ├── 01-research-overview.md       # วิธีวิจัย
│   ├── 02-repo-analysis/             # วิเคราะห์เครื่องมือ 23 ตัว
│   ├── 03-tweak-taxonomy.md          # จัดหมวดเทคนิคทั้งหมด (10 หมวด)
│   ├── 04-risk-classification.md     # เมทริกซ์ประเมินความเสี่ยง
│   ├── 05-windows-internals.md       # เจาะลึก Windows internals
│   ├── 06-performance-impact.md      # ผลลัพธ์จริง
│   ├── 07-best-practices.md          # แนวทางที่แนะนำ
│   ├── 10-complete-repo-ranking.md   # จัดอันดับเครื่องมือ 23 ตัว พร้อมคะแนน
│   ├── 15-user-guide-th.md           # คู่มือผู้ใช้ (ไทย)
│   ├── 16-user-guide-en.md           # คู่มือผู้ใช้ (อังกฤษ)
│   └── iso29110-clutchg/             # เอกสาร ISO 29110 (10 work products)
│
└── UX/                               # ต้นแบบและภาพหน้าจอ UI
```

---

## งานวิจัย

โปรเจกต์นี้เริ่มจากงานวิจัยวิทยานิพนธ์ปริญญาโท สาขาวิศวกรรมซอฟต์แวร์ มหาวิทยาลัยเชียงใหม่ วิเคราะห์เครื่องมือปรับแต่ง Windows 23 ตัว แบบ open-source และให้คะแนนตามกรอบประเมิน 5 ด้าน (ความปลอดภัย, ประสิทธิภาพ, คุณภาพโค้ด, ความโปร่งใส, ความสามารถในการย้อนกลับ)

### ผลการวิจัยสำคัญ

| รายการ | จำนวน |
|--------|-------|
| เครื่องมือที่วิเคราะห์ | 23 |
| เทคนิคปรับแต่งที่สำรวจ | 200+ |
| เทคนิคที่ผ่านการคัดกรองด้วยหลักฐาน | 45 (22.5%) |
| เทคนิคที่นำมาใช้ใน ClutchG | 56 |
| เครื่องมือที่ได้เกรด F (ไม่ผ่าน) | 11 (47.8%) |
| เครื่องมือที่ปลอดภัยสำหรับผู้ใช้ทั่วไป (เกรด A ขึ้นไป) | 2 (8.7%) |
| เครื่องมือที่ปิด Windows Defender | 16 (69.6%) |
| เครื่องมือที่ไม่มีระบบ backup | 20 (87.0%) |

### เครื่องมือที่ได้คะแนนสูงสุด

| อันดับ | เครื่องมือ | คะแนน | เกรด |
|--------|-----------|-------|------|
| 1 | WinUtil (ChrisTitusTech) | 9.5 | A+ |
| 2 | BCDEditTweaks (dubbyOW) | 9.0 | A |
| 3 | Win11-Latency-Opt (NicholasBly) | 8.0 | A- |
| 4 | FR33THY Ultimate Guide | 7.5 | B |
| 5 | win10-latency-opt (denis-g) | 7.5 | B |

### เทคนิคที่ได้ผลจริง

| เทคนิค | ผลกระทบ | หลักฐาน |
|--------|---------|---------|
| ปรับค่า GPU driver | FPS เพิ่ม 2-15% | เอกสาร vendor ขึ้นอยู่กับเกม |
| ปรับ Power plan | เพิ่ม 2-5% | จัดการ P-state/C-state |
| BCDEdit tweaks ที่ปลอดภัย | เพิ่ม 1-4% | เกมที่ไวต่อ latency |
| ลด background apps | เพิ่ม 1-3% | ลด CPU/RAM contention |

### ความเชื่อที่ไม่จริง

| ความเชื่อ | ความจริง |
|-----------|---------|
| "Windows สำรอง bandwidth 20% สำหรับ QoS" | จำกัดเฉพาะ traffic ที่ tag ไว้ ไม่กระทบเกม |
| "Timer resolution service เพิ่ม FPS" | ล้าสมัย Windows 10 2004 จัดการแบบ per-process แล้ว |
| "ปิด service 100 ตัว = เร็วขึ้น" | ฟีเจอร์พัง ได้ performance น้อยมาก |
| "แก้ registry เกี่ยวกับ network ลด ping" | ปัจจัยหลักคือ ISP และ routing ไม่ใช่ registry |

### รูปแบบอันตรายที่พบในเครื่องมือ open-source

| รูปแบบ | สัดส่วนที่พบ |
|--------|-------------|
| ปิด Windows Defender | 16/23 (69.6%) |
| ปิด Windows Update | 12/23 (52.2%) |
| ลบ exploit mitigations | 10/23 (43.5%) |
| ไม่มีระบบ backup | 20/23 (87.0%) |
| ลบไฟล์ระบบ | 9/23 (39.1%) |

### สิ่งที่ ClutchG ไม่ทำเด็ดขาด

เทคนิคเหล่านี้ **ไม่อยู่ใน** โปรไฟล์ใด เพราะลดความปลอดภัยโดยไม่คุ้มค่า:

- ปิด Windows Defender
- ปิด DEP / ASLR / CFG
- ปิด Driver Signature Enforcement
- ปิด Windows Update ถาวร
- ปิด UAC

เอกสารวิจัยฉบับเต็มอยู่ใน [`docs/`](docs/)

---

## การทดสอบ

```powershell
cd clutchg

# ติดตั้ง test dependencies
pip install -r requirements-test.txt

# รันทั้งหมด
pytest

# เฉพาะ unit tests
pytest tests\unit -m unit

# เฉพาะ integration tests
pytest tests\integration -m integration

# พร้อม coverage
pytest --cov=src tests/
```

**สถานะปัจจุบัน:** 477 passed, 64 skipped (E2E tests ข้ามเมื่อไม่มี display)

CI รัน unit และ integration tests อัตโนมัติบน `windows-latest` ผ่าน GitHub Actions

---

## ความต้องการของระบบ

- **OS:** Windows 10 22H2 ขึ้นไป หรือ Windows 11
- **Python:** 3.11+ (สำหรับ GUI)
- **สิทธิ์ Administrator** สำหรับการปรับแต่ง
- **Dependencies:** customtkinter, Pillow, psutil, pywin32, py-cpuinfo, wmi, tkextrafont

---

## เอกสาร

| เอกสาร | คำอธิบาย |
|--------|---------|
| [Research Overview](docs/01-research-overview.md) | วิธีวิจัยและขอบเขต |
| [Repo Analysis](docs/02-repo-analysis/) | วิเคราะห์เครื่องมือ 23 ตัว |
| [Tweak Taxonomy](docs/03-tweak-taxonomy.md) | ระบบจัดหมวดเทคนิค (10 หมวด) |
| [Risk Classification](docs/04-risk-classification.md) | เมทริกซ์ประเมินความเสี่ยง |
| [Windows Internals](docs/05-windows-internals.md) | เจาะลึกเทคนิค |
| [Performance Impact](docs/06-performance-impact.md) | ผลลัพธ์จริง |
| [Best Practices](docs/07-best-practices.md) | แนวทางที่แนะนำ |
| [Complete Ranking](docs/10-complete-repo-ranking.md) | จัดอันดับเครื่องมือ 23 ตัว พร้อมคะแนน |
| [คู่มือผู้ใช้ (ไทย)](docs/15-user-guide-th.md) | คู่มือผู้ใช้ภาษาไทย |
| [User Guide (EN)](docs/16-user-guide-en.md) | คู่มือผู้ใช้ภาษาอังกฤษ |
| [ISO 29110 Work Products](docs/iso29110-clutchg/) | เอกสารวงจรชีวิตซอฟต์แวร์ (10 work products) |

---

## ข้อจำกัดความรับผิดชอบ

ซอฟต์แวร์นี้แก้ไขค่าระบบ Windows แม้ผ่านการวิจัยและทดสอบแล้ว ผลลัพธ์อาจต่างกันตามฮาร์ดแวร์และการตั้งค่าของแต่ละเครื่อง ผู้ใช้ควร:

1. สำรองข้อมูลก่อนทุกครั้ง
2. เริ่มจากโปรไฟล์ SAFE
3. วัดผลก่อนและหลัง
4. อ่านคำอธิบายของแต่ละเทคนิคก่อนเปิดใช้

ผู้พัฒนาไม่รับผิดชอบต่อปัญหาที่อาจเกิดขึ้นจากการใช้ซอฟต์แวร์นี้

---

## สัญญาอนุญาต

[MIT](LICENSE)
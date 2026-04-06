# 10 — คู่มือผู้ใช้ (User Manual)

> **มาตรฐาน:** ISO/IEC 29110 — SI.O6 (Software Implementation — Output 6)
> **ETVX:** Entry = SDD v3.2 approved, SRS v3.1 baselined | Task = SI.5 Software Delivery | Verify = QA walkthrough | Exit = User Manual released
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 2.0 | **วันที่:** 2026-04-06
> **อ้างอิง:** SRS v3.1, SDD v3.2, Test Plan v3.0 | ISO/IEC 29110:2016 SI.O6, SE 701 Deployment & Maintenance

---

## 1. ข้อกำหนดระบบ (System Requirements)

| รายการ | ข้อกำหนดขั้นต่ำ |
|--------|---------------|
| OS | Windows 10 (version 1903+) / Windows 11 |
| Python | 3.11 หรือสูงกว่า |
| RAM | 4 GB ขึ้นไป |
| พื้นที่ดิสก์ | 200 MB |
| สิทธิ์ | **Administrator** |

---

## 2. การติดตั้ง (Installation)

### วิธีที่ 1: Automated Setup (แนะนำ)
```powershell
cd clutchg
.\setup_and_test.bat
```

### วิธีที่ 2: Manual Installation
```powershell
cd clutchg
pip install -r requirements.txt
python src\main.py
```

### วิธีที่ 3: Build Executable
```powershell
cd clutchg
python build.py
# ผลลัพธ์: clutchg\dist\ClutchG.exe
```

> **หมายเหตุ:** ไอคอนใช้ฟอนต์ Tabler Icons (tabler-icons.ttf v3.41.1) ที่รวมมากับโปรแกรมแล้ว ไม่ต้องติดตั้งเพิ่มเติม

---

## 3. การใช้งาน (Usage Guide)

### 3.1 หน้า Dashboard
แสดงข้อมูลระบบ:
- **CPU**: ชื่อ, จำนวน cores, ความเร็ว
- **GPU**: ชื่อ, VRAM
- **RAM**: ขนาด, ความเร็ว
- **Storage**: ขนาดรวม, ประเภท (SSD/HDD)
- **System Score**: คะแนนรวมและ profile แนะนำ

### 3.2 หน้า Profiles
เลือก optimization profile:

| Profile | Risk | FPS Gain | เหมาะสำหรับ |
|---------|------|---------|------------|
| **SAFE** | Low | 2-5% | ผู้ใช้ทั่วไป, มือใหม่ |
| **COMPETITIVE** | Medium | 5-10% | เกมเมอร์ |
| **EXTREME** | High | 10-15% | ผู้เชี่ยวชาญเท่านั้น |

**ขั้นตอน:**
1. คลิกเลือก profile ที่ต้องการ
2. อ่านคำเตือนและ expected effects
3. คลิก **"Apply"**
4. ระบบจะ backup ก่อนทำการเปลี่ยนแปลง
5. รอให้ process เสร็จสมบูรณ์
6. **Restart** (ถ้าจำเป็น)

### 3.3 หน้า Scripts
เลือก tweaks ทีละตัว:
- จัดกลุ่มตาม category (Power, GPU, Network, Services, etc.)
- แต่ละ tweak มี risk badge (LOW/MEDIUM/HIGH)
- คลิก **"?"** เพื่อดูคำอธิบาย
- เลือก checkbox แล้วกด **"Apply Selected"**

### 3.4 หน้า Backup & Restore Center
จัดการ backups และ rollback:
- **Timeline**: แสดงประวัติ operations ทั้งหมด
- **Rollback Per-Tweak**: undo ทีละรายการพร้อม before/after values
- **Rollback Snapshot**: undo ทั้ง session
- **Download Script**: ดาวน์โหลด .bat สำหรับ manual recovery

### 3.5 หน้า Help
คำอธิบายทุก tweak:
- รองรับ 2 ภาษา (EN/TH)
- มีข้อมูล risk level, expected impact, คำเตือน

### 3.6 หน้า Settings
ตั้งค่าแอปพลิเคชัน:
- **Theme**: Dark / Light
- **Accent Color**: Cyan, Purple, Green, Orange, Pink
- **Language**: English / ไทย

---

## 4. ข้อควรระวัง

### สิ่งที่ ClutchG **ไม่ทำ** (Never-Do)
- ปิด Windows Defender
- ปิด Windows Update ถาวร
- ปิด DEP/ASLR/CFG
- แก้ไข Registry ACLs
- ปิด UAC
- ลบ system files

### ก่อนใช้งาน
- สร้าง Windows Restore Point ก่อนเสมอ
- อ่านคำเตือนของแต่ละ tweak
- เริ่มจาก SAFE profile ก่อนลอง COMPETITIVE/EXTREME
- ใช้ Restore Center เพื่อ undo ถ้ามีปัญหา

---

## 5. การแก้ปัญหา (Troubleshooting)

| ปัญหา | แนวทางแก้ไข |
|--------|-----------|
| ไอคอนไม่แสดง | รัน `python install_material_icons.py`, restart ClutchG |
| ต้อง Admin rights | คลิกขวา → Run as Administrator |
| Profile ไม่ apply | ตรวจสอบว่า batch scripts อยู่ใน `src/` |
| ต้องการ undo | ไปหน้า Backup & Restore → เลือก snapshot → Rollback |
| Windows ไม่ปกติ | ใช้ System Restore Point ที่สร้างไว้ |

---

## 6. อภิธานศัพท์ (Glossary)

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
| **System Score** | คะแนนฮาร์ดแวร์ 0-100 คำนวณจาก CPU(30) + GPU(30) + RAM(20) + Storage(10) |
| **Tier** | ระดับเครื่อง: entry (<30), mid (30-49), high (50-69), enthusiast (70+) |

---

## 7. ข้อมูลเพิ่มเติม

- **Quick Start Guide**: `clutchg/QUICKSTART.md`
- **Developer Guide**: ดู SDD v3.2 และ source code ใน `clutchg/src/`
- **Safety Documentation**: ดู Test Plan v3.0 Section 6 (Test Design Techniques)
- **Testing**: ดู Test Record v2.1

---

## 8. ประวัติการแก้ไข (Revision History)

| เวอร์ชัน | วันที่ | ผู้แก้ไข | รายการแก้ไข |
|----------|--------|---------|------------|
| 1.0 | 2026-03-04 | nextzus | สร้างเอกสารเริ่มต้น: ข้อกำหนดระบบ, การติดตั้ง, คู่มือใช้งาน 6 หน้า, ข้อควรระวัง, แก้ปัญหา |
| 2.0 | 2026-04-06 | nextzus | เพิ่ม ETVX header, แก้เส้นทางติดตั้ง (ไม่ hardcode), แก้ entry point เป็น main.py, แก้ icon font เป็น Tabler Icons, ลบ emojis, เพิ่มอภิธานศัพท์ 12 คำ, เพิ่มวิธี build executable, อัพเดตข้อมูลอ้างอิง |

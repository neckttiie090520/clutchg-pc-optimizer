# 10 — คู่มือผู้ใช้ (User Manual)

> **มาตรฐาน:** ISO/IEC 29110 — SI.O6
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 1.0 | **วันที่:** 2026-03-04

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
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
.\setup_and_test.bat
```

### วิธีที่ 2: Manual Installation
```powershell
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
pip install -r requirements.txt
python src\app_minimal.py
```

### ติดตั้ง Material Symbols Font (ไอคอน)
```powershell
python install_material_icons.py
```

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
| 🟢 **SAFE** | Low | 2-5% | ผู้ใช้ทั่วไป, มือใหม่ |
| 🟡 **COMPETITIVE** | Medium | 5-10% | เกมเมอร์ |
| 🔴 **EXTREME** | High | 10-15% | ผู้เชี่ยวชาญเท่านั้น |

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
- แต่ละ tweak มี risk badge (🛡️/⚠️/🔥)
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

## 4. ข้อควรระวัง ⚠️

### สิ่งที่ ClutchG **ไม่ทำ** (Never-Do)
- ❌ ปิด Windows Defender
- ❌ ปิด Windows Update ถาวร
- ❌ ปิด DEP/ASLR/CFG
- ❌ แก้ไข Registry ACLs
- ❌ ปิด UAC
- ❌ ลบ system files

### ก่อนใช้งาน
- ✅ สร้าง Windows Restore Point ก่อนเสมอ
- ✅ อ่านคำเตือนของแต่ละ tweak
- ✅ เริ่มจาก SAFE profile ก่อนลอง COMPETITIVE/EXTREME
- ✅ ใช้ Restore Center เพื่อ undo ถ้ามีปัญหา

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

## 6. ข้อมูลเพิ่มเติม

- **Quick Start Guide**: `clutchg/QUICKSTART.md`
- **Developer Guide**: `THESIS_DOCS/CLUTCHG_DEVELOPER_GUIDE.md`
- **Safety Documentation**: `THESIS_DOCS/SAFETY_AND_ROLLBACK.md`
- **Testing**: `THESIS_DOCS/TESTING_AND_VALIDATION.md`

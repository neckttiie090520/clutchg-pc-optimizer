# 🚀 ClutchG - Quick Start Guide

## วิธีการติดตั้งและรัน (3 ขั้นตอน)

### วิธีที่ 1: ใช้ Setup Script (แนะนำ) ⭐

**Windows:**
```powershell
# ไปที่ clutchg directory
cd C:\Users\nextzus\Documents\thesis\bat\clutchg

# รัน setup script (ครั้งเดียวเสร็จ!)
.\setup_and_test.bat
```

**หรือใช้ PowerShell:**
```powershell
.\setup_and_test.ps1
```

---

### วิธีที่ 2: ติดตั้งแบบ Manual

```powershell
# 1. ไปที่ clutchg directory
cd C:\Users\nextzus\Documents\thesis\bat\clutchg

# 2. ติดตั้ง dependencies
pip install -r requirements.txt

# 3. รัน app
python src\app_minimal.py
```

---

### วิธีที่ 3: ทดสอบก่อน (ถ้ากลัวว่ามีปัญหา)

```powershell
cd C:\Users\nextzus\Documents\thesis\bat\clutchg\src

# ทดสอบ imports
python test_imports.py

# ทดสอบ app initialization (ไม่เปิด window)
python test_app_init.py

# ถ้าผ่านทั้งหมด ค่อยรัน app จริง
python app_minimal.py
```

---

## ✅ Checklist ก่อนรัน

- [ ] Python 3.11+ ติดตั้งแล้ว
- [ ] รันจาก clutchg directory (ไม่ใช่ src)
- [ ] requirements.txt มีอยู่ใน clutchg/
- [ ] ติดตั้ง dependencies ครบถ้วน

---

## 📦 Dependencies ที่ต้องการ

```
customtkinter>=5.2.0
Pillow>=10.0.0
psutil>=5.9.0
pywin32>=306
py-cpuinfo>=9.0.0
wmi>=1.5.1
GPUtil>=1.4.0
```

---

## 🐛 ถ้าเจอ Error

### Error: ModuleNotFoundError
```powershell
# ติดตั้ง dependencies ใหม่
pip install -r requirements.txt
```

### Error: AttributeError
```powershell
# รัน test scripts เพื่อดู error ละเอียด
python src\test_imports.py
python src\test_app_init.py
```

### Error: UnicodeDecodeError
```powershell
# ตั้งค่า environment variable
set PYTHONIOENCODING=utf-8
python src\app_minimal.py
```

---

## 🎯 หลังจากเปิด App

1. **Dashboard** - ดูสถานะระบบและ "Optimize Now" button
2. **Profiles** - เลือก SAFE / COMPETITIVE / EXTREME profile
3. **Scripts** - ดู scripts ทั้งหมดพร้อม risk labels
4. **Backup** - (เรุ่งที่สร้าง)
5. **Settings** - ตั้งค่าภาษา (EN/TH) และอื่นๆ

---

## 📝 Notes

- **Admin privileges:** บาง features ต้องการ Run as Administrator
- **Recommendation system:** แนะนำ profile อัตโนมัติตาม hardware
- **Risk levels:** สีเขียว (LOW), สีส้ม (MEDIUM), สีแดง (HIGH)
- **Bilingual:** รองรับภาษาไทยและอังกฤษ

---

## 🔧 Troubleshooting

**App ไม่เปิด:**
1. ตรวจสอบ Python version: `python --version`
2. ติดตั้ง dependencies ใหม่: `pip install -r requirements.txt`
3. รัน test scripts: `python src\test_imports.py`

**Fonts ไม่แสดง:**
- ติดตั้งฟอนต์ Inter: https://fonts.google.com/specimen/Inter

**System detection ไม่ทำงาน:**
- ตรวจสอบว่ารันเป็น Administrator หรือไม่

---

## ✨ Features ที่เพิ่มมา (Phase 10)

### ✅ เสร็จแล้ว
- 🎨 Risk-labeled UI (สีจรางแจ้งความเสี่ยง)
- ❓ Contextual help (ปุ่ม ? ทุกที่)
- ⚡ One-click "Optimize Now" button
- 📅 Timeline visualization
- 🔄 Flight recorder (track การเปลี่ยนแปลง)
- ↩️ Restore center (ย้อนกลับรายละเอียด)
- 🌏 Bilingual support (EN/TH)

### 🔜 รอดำเนินการ (Phase 11+)
- Performance benchmarking
- Power-user mode
- CLI interface
- Microsoft Store release

---

**ขอบคุณที่ใช้ ClutchG! 🎉**

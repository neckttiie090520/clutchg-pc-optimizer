# การแก้ไขและทดสอบ ClutchG App

## ปัญหาที่แก้ไขแล้ว ✅

### 1. Missing Dependencies
**ไฟล์:** `requirements.txt`
**เพิ่ม:**
- py-cpuinfo>=9.0.0
- wmi>=1.5.1
- GPUtil>=1.4.0

### 2. corner_radius Tuple Error
**ปัญหา:** CustomTkinter ไม่รองรับ tuple `corner_radius=(...)`
**แก้ไข 4 ไฟล์:**
- `dashboard_minimal.py` line 243
- `profiles_minimal.py` line 188
- `scripts_minimal.py` line 161
- `timeline.py` line 365

**เปลี่ยนจาก:** `corner_radius=(SIZES["card_radius"], 0, 0, SIZES["card_radius"])`
**เป็น:** `corner_radius=SIZES["card_radius"]`

### 3. SystemProfile Attribute Error
**ปัญหา:** `SystemProfile` ไม่มี attribute `is_laptop`
**แก้ไข:** `dashboard_minimal.py` line 216

**เปลี่ยนจาก:** `"is_laptop": system.is_laptop if system else False`
**เป็น:** `"is_laptop": system.form_factor == "laptop" if system else False`

---

## วิธีทดสอบ

### วิธีที่ 1: ติดตั้ง Dependencies และรัน
```powershell
# ไปที่ clutchg directory
cd C:\Users\nextzus\Documents\thesis\bat\clutchg

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน app
python src\app_minimal.py
```

### วิธีที่ 2: ทดสอบ Imports ก่อน
```powershell
cd C:\Users\nextzus\Documents\thesis\bat\clutchg\src

# ทดสอบ imports
python test_imports.py

# ทดสอบการสร้าง app
python test_app_init.py
```

### วิธีที่ 3: ถ้ายัง error
สร้าง screenshot หรือ copy error message มาให้ผม:
```powershell
python src\app_minimal.py 2>&1 | tee error_log.txt
```

---

## Checklists

- [x] requirements.txt updated with all dependencies
- [x] corner_radius tuples fixed (4 files)
- [x] SystemProfile.is_laptop → form_factor fixed
- [x] All new components created
- [x] Test scripts created

---

## Files Modified

1. `requirements.txt` - Added dependencies
2. `dashboard_minimal.py` - Fixed corner_radius + is_laptop
3. `profiles_minimal.py` - Fixed corner_radius
4. `scripts_minimal.py` - Fixed corner_radius
5. `timeline.py` - Fixed corner_radius

## Files Created for Testing

1. `test_imports.py` - Test all imports
2. `test_app_init.py` - Test app initialization

---

## Expected Behavior

เมื่อรัน `python src\app_minimal.py` ควร:
1. ไม่มี import errors
2. ไม่มี AttributeError
3. ไม่มี TypeError
4. App window เปิดขึ้นมาแสดง dashboard
5. มี "Optimize Now" button แสดง recommendation

---

## ถ้ายัง Error

ให้ copy error message มาและระบุ:
1. Full error traceback
2. ไฟล์และ line ที่ error
3. Python version (`python --version`)

แล้วผมจะช่วยแก้ไขต่อไป

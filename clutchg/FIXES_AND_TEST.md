# การแก้ไขและทดสอบ ClutchG App

## ปัญหาที่แก้ไขล่าสุด (Session 2026-03-23) ✅

### BUG-1: validate_script() trailing space patterns
**ไฟล์:** `src/core/batch_parser.py`
**ปัญหา:** `shutdown /p` และ `shutdown /h` ไม่ถูก block เพราะ pattern มี trailing space
**แก้ไข:** ลบ trailing space ออกจาก `always_dangerous_patterns` (shutdown /s, /r, /p, /h)

### BUG-1b: bcdedit /deletevalue ถูก mark ผิดว่า dangerous
**ไฟล์:** `tests/unit/test_tweak_registry_integrity.py`
**แก้ไข:** ลบ test case `bcdedit /deletevalue` ออก — เป็น safe rollback operation ไม่ใช่ dangerous

### BUG-3: Integration tests return bool แทน assert
**ไฟล์:** `tests/integration/test_clutchg_integration.py`
**ปัญหา:** 6 tests คืน `True`/`False` แทนใช้ `assert` → pytest ไม่ detect failure
**แก้ไข:** เปลี่ยนทุก `return True/False` เป็น `assert` statements

### BUG-3b: Forbidden emojis ใน scripts_minimal.py
**ไฟล์:** `src/gui/views/scripts_minimal.py`
**ปัญหา:** section labels ใน `_show_tweak_detail()` ใช้ emoji (⚠️ 📊 🚀)
**แก้ไข:** เปลี่ยนเป็น plain text

### BUG-4: Material Symbols font warning block UI
**ไฟล์:** `src/app_minimal.py`
**ปัญหา:** `messagebox.showwarning()` block main thread ก่อน app แสดงผล
**แก้ไข:** เปลี่ยนเป็น non-blocking `self.toast.warning()` + logger

### BUG-5: _show_loading() stub ใน backup page
**ไฟล์:** `src/gui/views/backup_restore_center.py`
**ปัญหา:** `self.app.cursor("watch")` ไม่ valid — `app` ไม่มี method `cursor()`
**แก้ไข:** เปลี่ยนเป็น `self.app.window.config(cursor="watch")` + `update_idletasks()`

### BUG-2: E2E fixture infrastructure
**ไฟล์:** `tests/e2e/conftest.py` (สร้างใหม่)
**ปัญหา:** ไม่มี `conftest.py` ใน e2e directory → fixtures `app_window`/`app_instance` ไม่ถูก discover
**แก้ไข:** สร้าง `conftest.py` ที่ skip tests อัตโนมัติเมื่อไม่มี `--app-path`

## Phase 2: MVP Strip-Down ✅

### ลบ unused components
ลบ 5 ไฟล์ที่ไม่ได้ใช้:
- `src/gui/components/glassmorphism.py`
- `src/gui/components/stat_card.py`
- `src/gui/components/risk_badge.py`
- `src/gui/components/context_help_button.py`
- `src/gui/components/enhanced_toggle.py`

### Clean settings_minimal.py
- ลบ import `ACCENT_PRESETS`, `SIZES` ที่ไม่ได้ใช้
- ลบ dead methods: `create_theme_setting`, `create_accent_color_setting`, `change_theme`, `change_accent_color`
- เปิดใช้ Language section ที่ถูก comment ออก
- ลบ stale UI_STRINGS keys

## Phase 3: Test Coverage ✅

เพิ่ม 74 tests ใหม่ใน `tests/unit/test_coverage_expansion.py`:
- **ConfigManager** (8 tests): load/save/reset/defaults/corrupt/missing dir
- **BatchParser validate_script** (12 tests): edge cases, end-of-line, bcdedit allowed
- **ThemeManager** (15 tests): colors, score colors, risk colors, ICON/ICON_FONT
- **TweakRegistry** (8 tests): presets, field integrity, risk levels, forbidden patterns
- **Localization** (6 tests): EN/TH key parity for all views
- **Security** (25 tests): parametrized blocked/allowed patterns + case-insensitive

**ผลรวม: 381 tests, 0 failed**

---

## ปัญหาที่แก้ไขแล้ว ✅ (Session เก่า)

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

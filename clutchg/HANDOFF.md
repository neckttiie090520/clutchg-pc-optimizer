# ClutchG Handoff Document [ARCHIVED]

> **⚠️ ARCHIVED:** This document reflects status as of 2026-02-10.  
> **Current Status (2026-03-24):** All issues listed below have been resolved.
> - Backup & Restore: Fixed (error handling, layout)
> - Scripts: Fixed (path resolution - finds 27 scripts)
> - Profiles: Fixed (text wrapping, button visibility)
> - Theme: Locked to Dark only (multi-theme removed)
> - Tests: 381+ passing, coverage expanded

---

**วันที่:** 2026-02-10  
**สถานะ ณ วันนั้น:** ⚠️ UI ใช้งานได้บางส่วน — มีหลายหน้าที่ยังไม่ทำงานจริง  
**Python:** 3.14 (GPUtil ใช้ไม่ได้ → ใช้ nvidia-smi แทน)

---

## 📋 สรุปโปรเจค

**ClutchG** เป็น Python-based PC Optimizer GUI สำหรับ Windows  
ใช้ CustomTkinter สร้าง UI แบบ Glassmorphism เพื่อเป็น launcher สำหรับ batch scripts

```
cd c:\Users\nextzus\Documents\thesis\bat\clutchg\src
python app_minimal.py
```

---

## 🖥️ สถานะ UI ปัจจุบัน (2026-02-10)

### ✅ หน้าที่ทำงานได้

| หน้า | สถานะ | หมายเหตุ |
|------|--------|----------|
| **Dashboard** | ✅ ใช้ได้ | Score ring, hardware cards, dynamic profile badge |
| **Settings** | ✅ ใช้ได้ | Theme, accent, language (EN/TH), safety options |
| **Help** | ✅ ใช้ได้ | Sidebar navigation, search, quick links |

### ❌ หน้าที่มีปัญหา (ต้องแก้ไข)

| หน้า | สถานะ | ปัญหา |
|------|--------|-------|
| **Backup & Restore** | ❌ หน้าว่างเปล่า | UI renders แล้วไม่แสดงอะไรเลย |
| **Scripts** | ⚠️ ใช้ได้บางส่วน | เจอแค่ 1 script, card styling ผิด (สีอ่อน) |
| **Profiles** | ⚠️ ใช้ได้บางส่วน | ข้อความถูกตัด, ไม่มีปุ่ม APPLY NOW |

---

## 🔥 งาน UI ที่ต้องทำต่อ (เรียงตามความสำคัญ)

### 1. 🚨 Backup & Restore — หน้าว่างเปล่า

**ไฟล์:** `src/gui/views/backup_restore_center.py`  
**ปัญหา:** หน้า render แล้วว่างเปล่าไม่มีอะไรเลย

**สาเหตุที่เป็นไปได้:**
- `BackupManager.get_all_backups()` อาจ throw error แบบ silent
- `show_simple_empty_state()` ใช้ `.place()` ซึ่งอาจไม่แสดงใน grid layout
- `refresh_simple_mode()` ล้าง children แล้วไม่สร้างใหม่สำเร็จ

**สิ่งที่ต้องทำ:**
- [ ] Debug `refresh_simple_mode()` — เพิ่ม print/log ดูว่า error ที่ไหน
- [ ] ตรวจ `show_simple_empty_state()` (L347) — `.place()` อาจต้องเปลี่ยนเป็น `.pack()`
- [ ] ตรวจ compatibility กับ CustomTkinter version (คล้ายปัญหา `selected_text_color`)
- [ ] ทดสอบทั้ง Simple mode และ Advanced mode

---

### 2. ⚠️ Profiles — ข้อความถูกตัดและไม่มีปุ่ม Apply

**ไฟล์:** `src/gui/views/profiles_minimal.py`  
**ปัญหา:**
- Description text ของ profile ถูกตัดหาย (ไม่ wrap)
- ไม่เห็นปุ่ม "APPLY NOW" (อาจหลุดออกจาก viewport)
- Card ไม่ scroll ได้

**สิ่งที่ต้องทำ:**
- [ ] เพิ่ม `wraplength` ให้ description labels
- [ ] ตรวจสอบว่า APPLY NOW button ยังอยู่ภายใน visible area
- [ ] ใส่ `CTkScrollableFrame` ให้ profile cards container
- [ ] ทดสอบกับหน้าจอขนาดต่างๆ (resize window)

---

### 3. ⚠️ Scripts — ค้นเจอแค่ 1 Script + Card Styling ผิด

**ไฟล์:** `src/gui/views/scripts_minimal.py`  
**ปัญหา:**
- เจอแค่ `optimizer.bat` (1 ไฟล์) แต่ `bat/src/` มี scripts หลายตัว
- Script cards ใช้สี light ซึ่งไม่เข้ากับ dark theme

**สาเหตุ:**
- Path: `clutchg/src` → `bat/src` ถูกต้อง แต่ `BatchParser.discover_scripts()` อาจ filter ผิด
- `GlassCard` สร้างไม่ได้เพราะ `fg_color` conflict (แก้แล้ว) แต่ card ที่เหลือยังใช้ default styling

**สิ่งที่ต้องทำ:**
- [ ] Debug `BatchParser.discover_scripts()` — ตรวจว่าเจอ scripts กี่ตัว
- [ ] ตรวจ path resolution: `clutchg/src → thesis/bat/src`
- [ ] ถ้า `bat/src/` มี subdirectories ต้องให้ parser scan recursive
- [ ] แก้ card styling ให้เข้ากับ dark theme

---

### 4. 🎨 UI Improvements ทั่วไป

**สิ่งที่ควรปรับปรุง:**
- [ ] Profile cards — เพิ่ม hover glow effect ให้ชัดเจนกว่านี้
- [ ] Sidebar toggle — ทำงานได้แล้วแต่ animation ยังไม่ smooth มาก
- [ ] Dashboard "Recent Activity" — ยังไม่มีข้อมูลจริง ให้แสดง empty state
- [ ] Dashboard "APPLY OPTIMIZATION" button — ข้อความไม่แสดงบน gradient button
- [ ] Toast notifications — ตรวจว่าทำงานจริงในทุกหน้า

---

## ✅ Bugs ที่แก้ไขแล้ว (2026-02-10)

| # | ไฟล์ | Bug | แก้ไข |
|---|------|-----|-------|
| 1 | `dashboard_minimal.py` | Missing `create_content()`, duplicate labels, duplicate RAM | Rewrote entire file |
| 2 | `execution_dialog.py` | `show_result(None)` crash | Added null guard |
| 3 | `settings_minimal.py` | Duplicate `change_theme()` method | Removed duplicate |
| 4 | `app_minimal.py` | Font check creates orphan window | Moved after `self.window` |
| 5 | `profiles_minimal.py` | "Strip Windows Defender" text | → "BCDEdit Tweaks" |
| 6 | `scripts_minimal.py` | Wrong path (5 levels), main thread execution | Fixed path + threading |
| 7 | `test_system_detection.py` | Invalid tier "ultra" | → "enthusiast" |
| 8 | `enhanced_sidebar.py` | `toggle_sidebar()` was empty | Animated expand/collapse |
| 9 | `scripts_minimal.py` | Duplicate `fg_color` in GlassCard | Removed kwarg |
| 10 | `backup_restore_center.py` | Invalid `selected_text_color`, `unselected_color` | Removed kwargs |

---

## 📁 Key Files

| ไฟล์ | หน้าที่ |
|------|---------|
| `src/app_minimal.py` | Main app controller, view switching |
| `src/core/system_info.py` | Hardware detection (CPU/GPU/RAM/Storage) |
| `src/core/profile_manager.py` | Profile loading and application |
| `src/core/batch_parser.py` | Script discovery and parsing |
| `src/core/batch_executor.py` | Script execution engine |
| `src/core/backup_manager.py` | Backup creation/restore |
| `src/core/flight_recorder.py` | System change timeline |
| `src/gui/theme.py` | Colors, fonts, spacing, icons |
| `src/gui/style.py` | Font/button style helpers |
| `src/gui/views/dashboard_minimal.py` | Dashboard view |
| `src/gui/views/profiles_minimal.py` | **⚠️ ต้องแก้** Profiles view |
| `src/gui/views/scripts_minimal.py` | **⚠️ ต้องแก้** Scripts view |
| `src/gui/views/settings_minimal.py` | Settings view |
| `src/gui/views/help_minimal.py` | Help/docs view |
| `src/gui/views/backup_restore_center.py` | **❌ ต้องแก้** Backup & Restore |
| `src/gui/components/glass_card.py` | GlassCard + ProfileCard components |
| `src/gui/components/enhanced_sidebar.py` | Collapsible sidebar |
| `src/gui/components/enhanced_button.py` | Primary/outline/danger buttons |
| `src/gui/components/execution_dialog.py` | Script execution dialog |

---

## ⚠️ ข้อควรระวัง

1. **Python 3.14** — `GPUtil` ใช้ไม่ได้ (ไม่มี `distutils`) → ใช้ `nvidia-smi` แทน
2. **CustomTkinter compatibility** — บาง kwargs ไม่รองรับ (`selected_text_color`, `unselected_color`)
3. **ต้อง run จาก `src/` directory** — path resolution ขึ้นกับ working directory
4. **GlassCard ห้ามส่ง `fg_color`** — มันตั้งค่าเองภายใน, ส่งซ้ำจะ error
5. **Scripts path** — จาก `clutchg/src/gui/views/` ต้องขึ้น 3 levels แล้วไป `thesis/bat/src`

---

## 📊 System Detection (ของเครื่องจริง)

| Component | Value |
|-----------|-------|
| CPU | AMD Ryzen 7 7800X3D 8-Core |
| GPU | NVIDIA GeForce RTX 5060 |
| RAM | 32GB |
| Storage | SSD |
| Score | 51 |
| Tier | Mid |
| Recommended | COMPETITIVE |

---

## 🔗 เอกสารที่เกี่ยวข้อง

- Developer Guide: `clutchg/docs/DEVELOPER_GUIDE.md`
- Scoring System: `clutchg/docs/SCORING_SYSTEM.md`
- UI Redesign Plan: `docs/UI-UX-REDESIGN-PLAN.md`
- Redesign Progress: `docs/REDESIGN-PROGRESS.md`

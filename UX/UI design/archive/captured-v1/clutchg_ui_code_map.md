# ClutchG — UI-to-Code Mapping
**สำหรับ UX/UI Design Audit Handoff**  
วันที่: 2026-03-25 | เวอร์ชั่น: v1.0.0 | Framework: CustomTkinter (Python)

---

## คำชี้แจง
เอกสารนี้ mapping แต่ละ UI screen ที่ถ่ายไว้ใน `UX/UI captured/` กับ source code files ที่เกี่ยวข้อง เพื่อให้นัก UX/UI Design Audit สามารถเปิด code ที่ตรงกับส่วนนั้น ๆ ได้โดยตรง

**Framework:** Python + [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)  
**Shared Design System:** `clutchg/src/gui/theme.py` (COLORS, SPACING, RADIUS, SIZES)  
**Font/Style System:** `clutchg/src/gui/style.py`

---

## 📋 ภาพรวม Screen Inventory

| # | Screenshot | Screen | Source File (Primary) |
|---|---|---|---|
| 1 | `01_dashboard.png` | Dashboard — ภาพรวม | `views/dashboard_minimal.py` |
| 2 | `02_optimization_quick_actions.png` | Optimization Center — Quick Actions tab | `views/scripts_minimal.py` |
| 3 | `03_optimization_presets.png` | Optimization Center — Presets tab | `views/scripts_minimal.py` |
| 4 | `04_optimization_custom_builder.png` | Optimization Center — Custom Builder tab | `views/scripts_minimal.py` |
| 5 | `05_optimization_encyclopedia.png` | Optimization Center — Encyclopedia tab | `views/scripts_minimal.py` |
| 6 | `06_backup_simple_mode.png` | Backup & Restore — Simple Mode | `views/backup_restore_center.py` |
| 7 | `07_backup_advanced_timeline.png` | Backup & Restore — Advanced Mode (Timeline) | `views/backup_restore_center.py` + `components/timeline.py` |
| 8 | `08_help_documentation.png` | Help & Documentation | `views/help_minimal.py` |
| 9 | `09_settings.png` | Settings | `views/settings_minimal.py` |
| 10 | `10_execution_dialog.png` | Execution Dialog (Running tweaks) | `components/execution_dialog.py` |
| 11 | `11_dialog_delete_backup.png` | Backup & Restore — Delete Backup Dialog | `views/backup_restore_center.py` → `components/refined_dialog.py` |
| 12 | `12_dialog_create_backup.png` | Backup & Restore — Create Backup Dialog | `views/backup_restore_center.py` → `components/refined_dialog.py` |
| 13 | `13_dialog_restore_backup.png` | Backup & Restore — Restore Backup Dialog | `views/backup_restore_center.py` → `components/refined_dialog.py` |
| 14 | `14_encyclopedia_tweak_detail.png` | Encyclopedia + Tweak Detail Dialog | `views/scripts_minimal.py` → `_show_education_tab()` |

---

## 🖥️ Screen 1 — Dashboard

**Screenshot:** `UX/UI captured/01_dashboard.png`

![Dashboard](UX/UI%20captured/01_dashboard.png)

**Primary Source:** [`clutchg/src/gui/views/dashboard_minimal.py`](clutchg/src/gui/views/dashboard_minimal.py)  
**Class:** `DashboardView(ctk.CTkFrame)`

### UI Element → Code Mapping

| UI Element | Method/Class | Lines (approx.) |
|---|---|---|
| ส่วนหัว "Dashboard" + "System Ready" badge | `create_header()` | L130–168 |
| วงกลม Circular Progress (System Score: 51) | `create_left_panel()` → `CircularProgress(...)` | L186–261 |
| Label "SYSTEM SCORE" + Mode Badge | `create_left_panel()` | L232–256 |
| แถบ Component Score (CPU/GPU/RAM/Storage) | `create_component_scores()` | L277–345 |
| การ์ด "Recommended Optimization" + ปุ่ม | `create_quick_actions()` | L373–418 |
| System Snapshot tiles (CPU/RAM/GPU) | `create_health_tiles()` | L420–487 |
| Recent Activity list | `create_recent_activity()` | L488–537 |
| Footer (version string) | `create_footer()` | L539–545 |

### Components ที่ใช้
- `GlassCard` — [`components/glass_card.py`](clutchg/src/gui/components/glass_card.py)
- `CircularProgress` — [`components/circular_progress.py`](clutchg/src/gui/components/circular_progress.py)
- `EnhancedButton.primary()` / `.outline()` — [`components/enhanced_button.py`](clutchg/src/gui/components/enhanced_button.py)

### UX Issues ที่ควร Audit
- Score ring ใช้สี `info` (blue) เมื่อ score 50–79 แต่ไม่มี label อธิบายว่าคือ "ค่าเฉลี่ย"
- Component score bar ถูก `place()` ทับ widget track — อาจ layout แตกที่ขนาด window บางขนาด (`L336–337`)
- Mode badge ไม่ responsive — ขยาย text อาจ overflow (`L242–256`)

---

## 🎯 Screen 2 — Optimization Center: Quick Actions

**Screenshot:** `UX/UI captured/02_optimization_quick_actions.png`

![Quick Actions](UX/UI%20captured/image%20copy.png)

**Primary Source:** [`clutchg/src/gui/views/scripts_minimal.py`](clutchg/src/gui/views/scripts_minimal.py)  
**Class:** `ScriptsView(ctk.CTkFrame)`, Tab: `_show_quick_actions_tab()`

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| Header "Optimization Center" + stats | `_create_header()` | L338–359 |
| Tab Bar (Quick Actions / Presets / Custom Builder / Encyclopedia) | `_create_tab_bar()` | L364–443 |
| Subtitle text | `_show_quick_actions_tab()` | L505–516 |
| Sub-group buttons (General/Advanced/Cleanup/Windows/Utilities) | `_show_quick_actions_tab()` | L546–601 |
| Action Card (เช่น "Gaming Baseline") | `_create_quick_action_card()` | L670–748 |
| Risk badge + tweak count | `_create_quick_action_card()` | L710–729 |
| "Run Action" button | `_create_quick_action_card()` | L736–746 |

### UX Issues ที่ควร Audit
- Sub-group buttons ใช้ `expand=True` + `fill="x"` ทีละ button — ความกว้างแต่ละ button ไม่เท่ากันเมื่อ label สั้นยาวต่างกัน
- Cards ถูก layout แบบ 2-column grid แต่ถ้า action น้อยกว่า 2 จะเห็น เซลล์ว่างด้านขวา

---

## 🎯 Screen 3 — Optimization Center: Presets

**Screenshot:** `UX/UI captured/03_optimization_presets.png`

![Presets](UX/UI%20captured/image%20copy%202.png)

**Primary Source:** [`clutchg/src/gui/views/scripts_minimal.py`](clutchg/src/gui/views/scripts_minimal.py)  
**Method:** `_show_presets_tab()`

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| Preset Card (Safe/Competitive/Extreme) | `_build_preset_card()` | (ค้นหา `_build_preset_card` ใน file) |
| "★ RECOMMENDED FOR YOU ★" badge | `_build_preset_card()` — `recommended` key | ใน `PRESET_INFO` / `_get_preset_info()` L288–321 |
| Risk badge (LOW RISK / MEDIUM / HIGH RISK) | `get_risk_display()` | L32–53 |
| FPS gain badge (+2-5% FPS) | `_build_preset_card()` — `fps` key | `PRESET_INFO` L77–108 |
| "View Tweaks" button | `_build_preset_card()` | - |
| "Apply Safe Mode" button | `_build_preset_card()` | - |
| Left color accent bar | card `border_color` per profile color | L84–107 |

### UX Issues ที่ควร Audit
- "Extreme Mode" แสดง risk badge ผิด: แสดง "LOW RISK" แทน "HIGH RISK" (เห็นในภาพ) — น่าจะเป็น bug ใน badge rendering vs ข้อมูล `PRESET_INFO`
- Recommended badge ใช้ unicode ★ — อาจไม่ render บาง font ที่ไม่ใช่ Inter

---

## 🔧 Screen 4 — Optimization Center: Custom Builder

**Screenshot:** `UX/UI captured/04_optimization_custom_builder.png`

![Custom Builder](UX/UI%20captured/image%20copy%203.png)

**Primary Source:** [`clutchg/src/gui/views/scripts_minimal.py`](clutchg/src/gui/views/scripts_minimal.py)  
**Method:** `_show_custom_tab()`

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| Sticky header ("0 tweaks selected" + Import/Export/Clear All/Apply) | `_show_custom_tab()` | (ค้นหา `_show_custom_tab` ใน file) |
| Category header (เช่น "Telemetry & Privacy (8)") | `_show_custom_tab()` — loop categories | - |
| Tweak row toggle (CTkSwitch) | `_show_custom_tab()` — per tweak | - |
| Risk badge per tweak row | `get_risk_display()` | L32–53 |
| Benefit text (เช่น "1-2% less background CPU") | Tweak registry data | `core/tweak_registry.py` |
| ℹ️ Info button | `_show_custom_tab()` | - |

### Component ที่ใช้จาก Registry
**Tweak data:** [`clutchg/src/core/tweak_registry.py`](clutchg/src/core/tweak_registry.py)  
**Action Catalog:** [`clutchg/src/core/action_catalog.py`](clutchg/src/core/action_catalog.py)

### UX Issues ที่ควร Audit
- Toggle switches เล็กมาก (ไม่มี label รับรู้ state ON/OFF ชัดเจน)
- Sticky header ด้วย "0 tweaks selected" ควรมี visual feedback ชัดกว่านี้เมื่อมีการเลือก
- Info button (ℹ️) เปิด dialog แยก — อาจ disrupt flow

---

## 📚 Screen 5 — Optimization Center: Encyclopedia

**Screenshot:** `UX/UI captured/05_optimization_encyclopedia.png`

![Encyclopedia](UX/UI%20captured/image%20copy%204.png)

**Primary Source:** [`clutchg/src/gui/views/scripts_minimal.py`](clutchg/src/gui/views/scripts_minimal.py)  
**Method:** `_show_education_tab()`

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| Search bar ("Search tweaks...") | `_show_education_tab()` — CTkEntry | - |
| Category filter chips (All (56) / Telemetry & Privacy…) | `_show_education_tab()` — loop | - |
| Tweak row (ชื่อ + คำอธิบาย + risk badge + benefit + "Learn More") | `_show_education_tab()` — per tweak | - |
| "Learn More" link → dialog | → `_show_tweak_detail_dialog()` | - |

### UX Issues ที่ควร Audit
- Category chips scrollable แบบ horizontal — ไม่มี scroll indicator ว่ามี item มากกว่าที่เห็น
- กด "Learn More" เปิด CTkToplevel dialog ใหม่ — ไม่มี animation/transition

---

## 💾 Screen 6 — Backup & Restore: Simple Mode

**Screenshot:** `UX/UI captured/06_backup_simple_mode.png`

![Backup Simple](UX/UI%20captured/image%20copy%205.png)

**Primary Source:** [`clutchg/src/gui/views/backup_restore_center.py`](clutchg/src/gui/views/backup_restore_center.py)  
**Class:** `BackupRestoreCenter`, Mode: `simple`

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| Header "Backup & Restore" + subtitle | `create_header()` | L168–251 |
| Toggle "Simple / Advanced" | `create_header()` → `self.mode_buttons` | L199–220 |
| "Create Backup" button | `create_header()` → `EnhancedButton.primary()` | L229–236 |
| Help icon button | `create_header()` | L239–251 |
| Backup Card (Pre_Custom_Tweaks + badges) | `create_backup_card()` | L391–510 |
| "RESTORE POINT" badge (green) | `create_backup_card()` | L453–462 |
| "REGISTRY" badge (cyan) | `create_backup_card()` | L464–473 |
| "Restore" button (green) | `EnhancedButton.success()` | L495–501 |
| "Delete" button (red) | `EnhancedButton.danger()` | L503–510 |

### UX Issues ที่ควร Audit
- Backup card สูงคงที่ 80px (`L401–402`) — ถ้า backup name ยาว text อาจถูก clip
- ไม่มี empty space ที่ defined layout เมื่อ backup list มีรายการมาก (ขึ้นอยู่กับ CTkScrollableFrame)

---

## 📅 Screen 7 — Backup & Restore: Advanced Mode (Timeline)

**Screenshot:** `UX/UI captured/07_backup_advanced_timeline.png`

![Backup Advanced](UX/UI%20captured/image%20copy%206.png)

**Primary Source:** [`clutchg/src/gui/views/backup_restore_center.py`](clutchg/src/gui/views/backup_restore_center.py) → `refresh_advanced_mode()`  
**Timeline Component:** [`clutchg/src/gui/components/timeline.py`](clutchg/src/gui/components/timeline.py)

### UI Element → Code Mapping

| UI Element | Method | Lines (approx.) |
|---|---|---|
| "Backup Timeline" heading | Timeline component | `timeline.py` |
| Legend dots (Manual/Auto/Profile/Restore) | Timeline component | `timeline.py` |
| Timeline axis + nodes | Timeline component | `timeline.py` |
| Empty state icon + text ("No timeline history yet") | `show_timeline_empty_state()` | L669–701 |

### UX Issues ที่ควร Audit
- Empty state ใช้ icon แบบ unicode glyph ซึ่งอาจไม่ render ถ้าไม่มี Segoe MDL2 Assets
- Timeline ว่างเปล่า — ไม่มี CTA button ให้ user ลองใช้ profile ก่อน

---

## ❓ Screen 8 — Help & Documentation

**Screenshot:** `UX/UI captured/08_help_documentation.png`

![Help](UX/UI%20captured/image%20copy%207.png)

**Primary Source:** [`clutchg/src/gui/views/help_minimal.py`](clutchg/src/gui/views/help_minimal.py)

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| Topics sidebar (left panel) | List of help topics เป็น CTkButton ด้านซ้าย |
| Search + Clear | CTkEntry + CTkButton |
| Content panel (right) | CTkScrollableFrame + rich text labels |
| Active topic highlight ("Getting Started") | Button fg_color = accent |

### UX Issues ที่ควร Audit
- ไม่มี hyperlink ที่ clickable ภายใน content (links แสดงเป็น text สี teal เฉยๆ)
- Font size ใน content panel เล็กสำหรับ reading เนื้อหาจำนวนมาก
- ไม่มี "back" navigation หรือ breadcrumb

---

## ⚙️ Screen 9 — Settings

**Screenshot:** `UX/UI captured/09_settings.png`

![Settings](UX/UI%20captured/image%20copy%208.png)

**Primary Source:** [`clutchg/src/gui/views/settings_minimal.py`](clutchg/src/gui/views/settings_minimal.py)

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| "LANGUAGE" section | CTkLabel section header + CTkOptionMenu |
| Language dropdown (English) | `CTkOptionMenu` |
| "SAFETY" section | CTkLabel + checkboxes |
| Auto-create backup checkbox | `CTkCheckBox` |
| Show confirmation dialogs checkbox | `CTkCheckBox` |
| "ABOUT" section | Static labels (version + description) |

### UX Issues ที่ควร Audit
- Settings page มีเพียง 3 sections — ดูบางมาก (lots of whitespace ด้านล่าง)
- ไม่มี Theme toggle (dark/light) แม้ `theme.py` มีระบบ theme อยู่
- Section headers เป็น ALL CAPS text ขนาดเล็ก — contrast ต่ำ

---

## ⚡ Screen 10 — Execution Dialog

**Screenshot:** `UX/UI captured/10_execution_dialog.png`

![Execution Dialog](UX/UI%20captured/image%20copy%209.png)

**Primary Source:** [`clutchg/src/gui/components/execution_dialog.py`](clutchg/src/gui/components/execution_dialog.py)  
**Class:** `ExecutionDialog(ctk.CTkToplevel)`

### UI Element → Code Mapping

| UI Element | Method/Attr | Notes |
|---|---|---|
| Dialog title "Running Custom (1 tweaks)" | `__init__` title param | - |
| Green progress bar (100%) | `CTkProgressBar` | `add_output()` ต่อ step |
| "Cancel" button (ระหว่าง run) | - | disabled หลัง complete |
| "Execution Output" collapsible area | `CTkButton` toggle | - |
| Output log text area | `CTkTextbox` | monospace font |
| Log entries (📷 Taking snapshot… ✅ Complete…) | `add_output()` method | - |

### UX Issues ที่ควร Audit
- Progress bar ไม่แสดง % ตัวเลข — user ไม่รู้ว่าเหลือเท่าไหร่
- Output text ใช้ unicode emoji (📷 ✅) — อาจ render ไม่ตรงกัน font

---

## 🗑️ Screen 11 — Delete Backup Dialog

**Screenshot:** `UX/UI captured/11_dialog_delete_backup.png`

![Delete Dialog](UX/UI%20captured/image%20copy%2010.png)

**Primary Source:** [`clutchg/src/gui/components/refined_dialog.py`](clutchg/src/gui/components/refined_dialog.py)  
**Called from:** `backup_restore_center.py` → `delete_backup()` (L767–789)

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| Dialog title "Delete Backup" + red dot | `show_confirmation()` → `risk_level="HIGH"` |
| Body text "Delete 'Pre_Custom_Tweaks'?" | `delete_dialog_msg` localization string |
| "This action cannot be undone." warning | Hard-coded in string |
| "Cancel" button | `show_confirmation()` cancel path |
| "Delete" button (teal/accent) | `show_confirmation()` confirm path |

### UX Issues ที่ควร Audit
- ปุ่ม "Delete" ใช้สี accent (teal) ซึ่ง **ไม่ตรง** กับ risk_level="HIGH" — ควรเป็นสีแดง
- Dialog ใช้ `CTkToplevel` (native window) ทำให้ไม่ match กับ glass/dark design ของ app หลัก
- ไม่มี animation เปิด/ปิด dialog

---

## 📥 Screen 12 — Create Backup Dialog

**Screenshot:** `UX/UI captured/12_dialog_create_backup.png`

![Create Backup Dialog](UX/UI%20captured/image%20copy%2011.png)

**Primary Source:** [`clutchg/src/gui/components/refined_dialog.py`](clutchg/src/gui/components/refined_dialog.py)  
**Called from:** `backup_restore_center.py` → `create_backup()` (L707–717)  
**Function:** `show_input()`

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| Title "Create Backup" + green dot | `show_input()` |
| Prompt "Enter a name for this backup:" | `create_dialog_prompt` string |
| Input field (pre-filled timestamp) | `CTkEntry` with placeholder |
| "Cancel" + "Confirm" buttons | `show_input()` |

### UX Issues ที่ควร Audit
- Input field ใช้ placeholder เป็น default name แต่ placeholder text จางมาก — ควรใช้เป็น default value แทน
- Dialog ไม่ validate ชื่อซ้ำ ก่อน confirm

---

## ♻️ Screen 13 — Restore Backup Dialog

**Screenshot:** `UX/UI captured/13_dialog_restore_backup.png`

![Restore Dialog](UX/UI%20captured/image%20copy%2012.png)

**Primary Source:** [`clutchg/src/gui/components/refined_dialog.py`](clutchg/src/gui/components/refined_dialog.py)  
**Called from:** `backup_restore_center.py` → `restore_backup()` (L744–765)

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| Title "Restore Backup" + yellow dot | `show_confirmation()` → `risk_level="MEDIUM"` |
| Body text (backup name + warning) | `restore_dialog_msg` string |
| "Cancel" + "Restore" buttons | `show_confirmation()` |

---

## 📖 Screen 14 — Encyclopedia + Tweak Detail Dialog

**Screenshot:** `UX/UI captured/14_encyclopedia_tweak_detail.png`

![Encyclopedia + Detail](UX/UI%20captured/image%20copy%2013.png)

**Primary Source:**
- Encyclopedia list: `scripts_minimal.py` → `_show_education_tab()`
- Detail dialog: `scripts_minimal.py` → `_show_tweak_detail_dialog()` (หรือ `show_info()` จาก `refined_dialog.py`)

### UI Element → Code Mapping

| UI Element | Notes |
|---|---|
| "Disable DiagTrack Service" dialog title | ชื่อ tweak จาก `tweak_registry.py` |
| Risk badge "LOW RISK" + Category tag | Tweak metadata |
| "Restart Required" badge | Tweak `requires_restart` field |
| Description section headers (teal) | Static labels ใน dialog |
| "Description", "What It Does", "Why It Helps", "Limitations", "Expected Gain" sections | Tweak documentation fields |
| "Close" button | `CTkButton` ปิด Toplevel |

### UX Issues ที่ควร Audit
- Dialog เปิดบน desktop ไม่ใช่ centered ต่อ main window
- Section headers สี teal (accent) — ทำให้อ่าน text ด้านล่างยากขึ้น (contrast ต่ำกับ dark background)
- ขนาด dialog ไม่ responsive — อาจเล็กเกินไปถ้า content ยาว

---

## 🧭 Sidebar Navigation

**Screenshot:** ปรากฏใน screenshot ทุกอัน (ซ้ายมือ)

**Primary Source:** [`clutchg/src/gui/components/enhanced_sidebar.py`](clutchg/src/gui/components/enhanced_sidebar.py)  
**Class:** `EnhancedSidebar(ctk.CTkFrame)`

### Navigation Items

| Icon | Label | Nav Key | View Class |
|---|---|---|---|
| Home icon (🏠) | Dashboard | `dashboard` | `DashboardView` |
| Curly braces `{}` | Optimization | `scripts` | `ScriptsView` |
| Copy icon | Backup & Restore | `backup` | `BackupRestoreCenter` |
| `?` | Help | `help` | `HelpView` (help_minimal.py) |
| Gear icon | Settings | `settings` | `SettingsView` (settings_minimal.py) |

### Sidebar Behaviors

| Feature | Code Location |
|---|---|
| Collapse/Expand animation (60→210px) | `toggle_sidebar()` L312–353 |
| Active indicator (teal left bar) | `update_active_state()` L181–206 |
| Glow animation บน active item | `animate_glow()` L208–294 |
| Tooltip เมื่อ collapsed | `ToolTipBinder(btn, label)` L161 |
| Toggle button (☰ / ✕) | `create_toggle_button()` L296–310 |

### UX Issues ที่ควร Audit
- Sidebar collapsed-width 60px คับแน่น — icon 36px + padding กระทบ mobile/small window
- ☰ toggle button อยู่ล่างสุด — ไม่ใช่ standard placement (มักจะอยู่บนสุด)
- Sidebar ไม่มี label ชัดเจนตอน collapsed (เฉพาะ tooltip on hover)

---

## 🎨 Shared Design System

**File:** [`clutchg/src/gui/theme.py`](clutchg/src/gui/theme.py)

| Token | Value (Dark Mode) |
|---|---|
| Accent | `#00BCD4` (teal/cyan) |
| Background Primary | `#0D1117` |
| Background Secondary | `#131c2e` |
| Card Background | `#161b22` |
| Text Primary | `#E6EDF3` |
| Text Secondary | `#8B949E` |
| Success | `#10B981` (green) |
| Warning | `#F59E0B` (amber) |
| Danger | `#EF4444` (red) |
| Risk LOW | `#34D399` |
| Risk MEDIUM | `#FBBF24` |
| Risk HIGH | `#F87171` |

**Font Stack:** Inter (primary), Tahoma (Thai language fallback)  
**Font loading:** [`clutchg/src/gui/font_installer.py`](clutchg/src/gui/font_installer.py)

---

## 🔑 Key Files Summary

```
clutchg/src/
├── app_minimal.py               # Root app, window setup, view routing
├── gui/
│   ├── theme.py                 # COLORS, SPACING, RADIUS, SIZES, NAV_ICONS
│   ├── style.py                 # font() helper
│   ├── font_installer.py        # Inter font loading
│   ├── icons.py                 # Icon unicode mapping
│   ├── views/
│   │   ├── dashboard_minimal.py      # Screen 1
│   │   ├── scripts_minimal.py        # Screens 2–5, 14
│   │   ├── backup_restore_center.py  # Screens 6–7, 11–13
│   │   ├── help_minimal.py           # Screen 8
│   │   └── settings_minimal.py       # Screen 9
│   └── components/
│       ├── enhanced_sidebar.py       # Sidebar (all screens)
│       ├── execution_dialog.py       # Screen 10
│       ├── refined_dialog.py         # Dialog system (screens 11–14)
│       ├── glass_card.py             # GlassCard widget
│       ├── enhanced_button.py        # EnhancedButton variants
│       ├── circular_progress.py      # Score ring
│       ├── timeline.py               # Timeline (screen 7)
│       ├── toast.py                  # Toast notifications
│       └── tooltip.py                # Hover tooltips
└── core/
    ├── tweak_registry.py         # Tweak data source
    ├── action_catalog.py         # Quick Actions data
    ├── backup_manager.py         # Backup CRUD
    └── flight_recorder.py        # Timeline event log
```

---

## 📝 สรุป UX Issues รวม (Priority Order)

| Priority | Issue | Screen | File |
|---|---|---|---|
| 🔴 HIGH | Delete dialog ปุ่มสี accent แทนสีแดง | Screen 11 | `refined_dialog.py` |
| 🔴 HIGH | Extreme Mode แสดง risk badge ผิด | Screen 3 | `scripts_minimal.py` |
| 🟡 MED | Progress bar ไม่แสดง % ตัวเลข | Screen 10 | `execution_dialog.py` |
| 🟡 MED | Sidebar toggle button อยู่ล่างสุด | All | `enhanced_sidebar.py` |
| 🟡 MED | Component score bar ใช้ `place()` + อาจ overlap | Screen 1 | `dashboard_minimal.py` |
| 🟡 MED | Encyclopedia category chips ไม่มี scroll indicator | Screen 5 | `scripts_minimal.py` |
| 🟢 LOW | Settings page ว่างมาก, ขาด theme toggle | Screen 9 | `settings_minimal.py` |
| 🟢 LOW | Help &amp; Docs ขาด clickable hyperlinks | Screen 8 | `help_minimal.py` |
| 🟢 LOW | Dialogs ไม่ centered ต่อ main window | Screens 11–14 | `refined_dialog.py` |
| 🟢 LOW | Input dialog ใช้ placeholder แทน default value | Screen 12 | `refined_dialog.py` |

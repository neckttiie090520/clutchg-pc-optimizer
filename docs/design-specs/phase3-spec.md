# Phase 3 Design Spec — Profiles · Settings · Welcome Overlay

> **Status:** Pending approval
> **Mockup:** `docs/design-mockups/phase3-profiles-settings-welcome.html` (approved)
> **Scope:** 3 views (ProfilesView, SettingsView, WelcomeOverlay) + app icon integration + sidebar logo + build icon

---

## 0. Global Rules (apply to every task)

| Rule | Detail |
|------|--------|
| No emoji | All icons via Material Symbols Outlined or Segoe MDL2 Assets — never emoji |
| No colored left-stripes | Cards use plain `border` only; no accent_color stripe patterns |
| DeAI tone | Short, nerd+gamer-friendly copy. No corporate buzzwords. |
| Font | Figtree for all text, Segoe MDL2 Assets for nav icons |
| Theme tokens | All colors from `theme.py` Sun Valley palette — no hardcoded hex outside theme |
| App icon | Use `C.GG-Photoroom.png` everywhere a logo/icon placeholder exists |

---

## 1. App Icon Integration (Foundation — do first)

### 1.1 Copy Icon to Assets

**Source:** `C.GG-Photoroom.png` (repo root)
**Destination:** `clutchg/src/assets/icon.png`

Create `clutchg/src/assets/` directory if it doesn't exist. Copy the PNG there so all code references a stable path inside the package.

### 1.2 Sidebar Logo

**File:** `clutchg/src/gui/components/enhanced_sidebar.py`
**Location:** `create_navigation()` method, lines 69-72

**Current:**
```python
self.logo_label = ctk.CTkLabel(
    self, text="C", font=font("title"), text_color=colors["accent"]
)
self.logo_label.pack(pady=14)
```

**New:** Replace the text "C" label with a `CTkImage`-based logo loaded from `assets/icon.png`.

```python
from PIL import Image
from pathlib import Path

# Load app icon
icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
if icon_path.exists():
    logo_image = ctk.CTkImage(
        light_image=Image.open(icon_path),
        dark_image=Image.open(icon_path),
        size=(32, 32)
    )
    self.logo_label = ctk.CTkLabel(self, image=logo_image, text="")
else:
    # Fallback: text "C" if icon not found
    self.logo_label = ctk.CTkLabel(
        self, text="C", font=font("title"), text_color=colors["accent"]
    )
self.logo_label.pack(pady=14)
```

When sidebar is expanded, show the logo at 32x32 with "ClutchG" text beside it. When collapsed, show 32x32 icon only (text hidden — same pattern as nav labels).

### 1.3 Build System — Window Icon

**File:** `clutchg/build.py`

Add `--icon` flag to the PyInstaller command using an `.ico` version of the app icon. We need to generate or provide `clutchg/src/assets/icon.ico`.

**Approach:** Add a pre-build step in `build.py` that converts `icon.png` → `icon.ico` using Pillow (already a dependency), then pass `--icon=src/assets/icon.ico` to PyInstaller.

```python
# In build() function, before PyInstaller cmd:
from PIL import Image
icon_png = src_dir / "assets" / "icon.png"
icon_ico = src_dir / "assets" / "icon.ico"
if icon_png.exists() and not icon_ico.exists():
    img = Image.open(icon_png)
    img.save(icon_ico, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

# Add to cmd list (before entry point):
if icon_ico.exists():
    cmd.insert(-1, f"--icon={icon_ico}")
```

### 1.4 Window Icon at Runtime

**File:** `clutchg/src/app_minimal.py`
**Location:** After `self.window.title("ClutchG")` (~line 49)

Set the window icon so the taskbar and title bar show the real logo:

```python
icon_path = Path(__file__).parent / "assets" / "icon.png"
if icon_path.exists():
    from PIL import Image
    self.window.iconphoto(False, ctk.CTkImage(
        light_image=Image.open(icon_path),
        dark_image=Image.open(icon_path),
        size=(32, 32)
    ))
```

Note: `iconphoto` requires a `tkinter.PhotoImage` or compatible. Use `ImageTk.PhotoImage` from Pillow:

```python
from PIL import Image, ImageTk
icon_path = Path(__file__).parent / "assets" / "icon.png"
if icon_path.exists():
    icon_img = Image.open(icon_path)
    self._icon_photo = ImageTk.PhotoImage(icon_img.resize((32, 32)))
    self.window.iconphoto(False, self._icon_photo)
```

Store reference in `self._icon_photo` to prevent garbage collection.

---

## 2. ProfilesView Overhaul

**File:** `clutchg/src/gui/views/profiles_minimal.py`

### 2.1 View Title

- Current: `"Optimization Profiles"` → New: **`"Profiles"`**
- Current hero_title: long sentence → New: **`"Pick a profile. Start with Safe if unsure."`**
- Current hero_subtitle: long sentence → New: **`"Each profile bundles specific Windows 11 tweaks. All changes are logged and reversible."`**

Update `UI_STRINGS["en"]` and `UI_STRINGS["th"]` accordingly.

### 2.2 Profile Card Redesign — Stats Grid

**Current `ProfileCard`** (in `glass_card.py`) shows:
- Large icon (42px Segoe MDL2)
- Profile name (20px bold)
- Separator line
- Description text
- Bullet-point features list
- Risk badge
- Apply button

**New layout** (per mockup):

```
┌─────────────────────────────┐
│  [icon-in-circle]           │
│  SAFE                       │
│  For everyday use...        │
│                             │
│  ┌─────┬─────┬─────┬─────┐ │
│  │Tweak│ Gain│ Risk│Rstrt│ │
│  │  12 │ +8% │ LOW │  No │ │
│  └─────┴─────┴─────┴─────┘ │
│                             │
│  ████░░░░░░  (risk bar)     │
│                             │
│  [Preview]  [Apply Safe]    │
└─────────────────────────────┘
```

**Changes to `ProfileCard` (`glass_card.py`):**

1. **Icon-in-circle:** Wrap the icon in a colored circle frame (`fg_color=glow_color`, `corner_radius=9999`, 48x48). Icon itself is white text on colored bg. This replaces the naked icon.

2. **Remove features bullet list.** Replace with a **stats grid** (2×4 grid):
   - Row 1 (labels): `Tweaks` | `Gain` | `Risk` | `Restart` — muted text, 10px
   - Row 2 (values): `12` | `+8%` | `LOW` | `No` — primary text, 13px bold
   - Risk value colored by risk level (green/yellow/red)

3. **Add thin risk bar** below stats grid:
   - Full-width frame, height=4px, corner_radius=2
   - Filled portion colored by risk level, remainder `bg_tertiary`
   - Safe: 20% filled green, Competitive: 50% filled yellow, Extreme: 90% filled red

4. **Button row:** Two buttons side by side:
   - "Preview" — outline button (ghost style), opens detail dialog
   - "Apply [Name]" — primary button colored by risk level:
     - Safe: `success` green
     - Competitive: `warning` yellow (text: dark)
     - Extreme: `danger` red

5. **Remove separator line** (the thin 40px horizontal rule)

**New `ProfileCard.__init__` parameters:**
```python
def __init__(self, master, profile_name, profile_icon, description,
             risk_level, stats, glow_color, on_apply, on_preview=None, **kwargs):
```
Where `stats` is a dict: `{"tweaks": 12, "gain": "+8%", "risk": "LOW", "restart": "No"}`

**Profile stats data** (add to `profiles_minimal.py`):
```python
PROFILE_STATS = {
    "SAFE":        {"tweaks": 12, "gain": "+8%",  "risk": "LOW",    "restart": "No"},
    "COMPETITIVE": {"tweaks": 24, "gain": "+18%", "risk": "MEDIUM", "restart": "Yes"},
    "EXTREME":     {"tweaks": 35, "gain": "+30%", "risk": "HIGH",   "restart": "Yes"},
}
```

### 2.3 Compare Panel (Collapsible)

Below the 3-column card grid, add a collapsible "Compare Profiles" panel.

**Toggle button:** Text link style — `"Compare Profiles"` with expand/collapse icon (Segoe MDL2 chevron). Clicking toggles a comparison table.

**Comparison table layout:**

| | Safe | Competitive | Extreme |
|---|---|---|---|
| Tweaks | 12 | 24 | 35 |
| Expected Gain | +8% | +18% | +30% |
| Risk Level | LOW | MEDIUM | HIGH |
| Restart Required | No | Yes | Yes |
| Reversible | Yes | Mostly | Partial |

Render as a grid of `CTkLabel` cells inside a `GlassCard`. Headers bold, values normal. Risk cells colored.

**State:** `self.compare_visible = False`, toggled by button click.

### 2.4 UI_STRINGS Updates

Add/update these keys in both `en` and `th`:

```python
# EN additions
"title": "Profiles",
"hero_title": "Pick a profile. Start with Safe if unsure.",
"hero_subtitle": "Each profile bundles specific Windows 11 tweaks. All changes are logged and reversible.",
"preview": "Preview",
"apply_btn": "Apply {name}",
"compare_title": "Compare Profiles",
"stat_tweaks": "Tweaks",
"stat_gain": "Gain",
"stat_risk": "Risk",
"stat_restart": "Restart",
"stat_reversible": "Reversible",
"yes": "Yes",
"no": "No",
"mostly": "Mostly",
"partial": "Partial",
```

### 2.5 Remove Old Feature Strings

Remove `safe_feat1/2/3`, `comp_feat1/2/3`, `ext_feat1/2/3` from `UI_STRINGS` — no longer used.

### 2.6 Hardcoded "Apply" Fix

Line 246 has `confirm_text="Apply"` — change to `confirm_text=self._ui("apply_btn").format(name=name)`.

---

## 3. SettingsView Overhaul

**File:** `clutchg/src/gui/views/settings_minimal.py`

### 3.1 Section Headers — Add Icons

**Current:** Section headers are plain uppercase text labels.

**New:** Each section header gets an icon (Segoe MDL2) + uppercase title.

| Section | Icon | Segoe MDL2 codepoint |
|---------|------|---------------------|
| Appearance | palette | `\ue790` |
| Language | translate | `\ue775` |
| Safety | shield | `\ue81e` |
| About | info | `\ue897` |

**Implementation:** Modify `create_section()` to accept an `icon` parameter:

```python
def create_section(self, parent, title, icon_char, creators):
    # ... inside the section card:
    header_frame = ctk.CTkFrame(section, fg_color="transparent")
    header_frame.pack(anchor="w", padx=SPACING["lg"], pady=(SPACING["md"], SPACING["sm"]))
    
    ctk.CTkLabel(
        header_frame,
        text=icon_char,
        font=ctk.CTkFont(family="Segoe MDL2 Assets", size=14),
        text_color=COLORS["text_secondary"]
    ).pack(side="left", padx=(0, 8))
    
    ctk.CTkLabel(
        header_frame,
        text=title.upper(),
        font=self._font(10, "bold"),
        text_color=COLORS["text_primary"]
    ).pack(side="left")
```

Update all `create_section()` calls to pass the icon:
```python
self.create_section(content, self._ui("appearance"), "\ue790", [self.create_appearance_setting])
self.create_section(content, self._ui("language"), "\ue775", [self.create_language_setting])
self.create_section(content, self._ui("safety"), "\ue81e", [self.create_safety_settings])
self.create_section(content, self._ui("about"), "\ue897", [self.create_about])
```

### 3.2 Setting Rows — Label + Description Layout

**Current:** Each setting is just a label + control on one line.

**New:** Each row has:
- Left side: **Label** (13px, primary) + **Description** (11px, secondary) stacked vertically
- Right side: Control widget (dropdown, switch)

**Implementation:** Create a helper `_setting_row()`:

```python
def _setting_row(self, parent, label, description, control_creator):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_columnconfigure(1, weight=0)
    
    # Left: label + description
    text_frame = ctk.CTkFrame(frame, fg_color="transparent")
    text_frame.grid(row=0, column=0, sticky="w")
    
    ctk.CTkLabel(text_frame, text=label, font=self._font(13),
                 text_color=COLORS["text_primary"]).pack(anchor="w")
    ctk.CTkLabel(text_frame, text=description, font=self._font(11),
                 text_color=COLORS["text_secondary"]).pack(anchor="w")
    
    # Right: control
    control_creator(frame)
```

### 3.3 Safety — Switch Instead of Checkbox

**Current:** Uses `CTkCheckBox` for auto_backup and confirm_actions.

**New:** Use `CTkSwitch` for a modern toggle appearance:

```python
self.auto_backup_var = ctk.BooleanVar(value=self.config.get("auto_backup", True))
ctk.CTkSwitch(
    control_frame,
    text="",
    variable=self.auto_backup_var,
    fg_color=COLORS["bg_tertiary"],
    progress_color=COLORS["accent"],
    button_color=COLORS["text_primary"],
    button_hover_color=COLORS["accent_hover"],
    command=self.save_config
).grid(row=0, column=1, sticky="e")
```

### 3.4 Flight Recorder Toggle (New)

Add a new toggle in the Safety section:

- **Label:** `"Flight Recorder"`
- **Description EN:** `"Log every tweak, rollback, and profile apply to a local file"`
- **Description TH:** `"บันทึกทุกการปรับแต่ง, ย้อนกลับ, และการใช้ Profile ลงไฟล์"`
- **Config key:** `"flight_recorder"` (default: `True`)
- **Control:** `CTkSwitch`

Add to `UI_STRINGS`, `save_config()`, and config load.

### 3.5 About Section — App Icon + Rich Info

**Current:** Just `app_name` + `app_description` text labels.

**New layout:**

```
┌──────────────────────────────────────┐
│  ABOUT                               │
│                                      │
│  [icon.png 48x48]  ClutchG PC Opt.   │
│                    v1.0.0 · Win 10/11│
│                    A Windows optimizer│
│                    built for gamers...│
│                                      │
│  [GitHub link]  [Docs link]          │
└──────────────────────────────────────┘
```

**Implementation:**

```python
def create_about(self, parent):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=SPACING["lg"], pady=SPACING["sm"])
    
    # Row with icon + text
    row = ctk.CTkFrame(frame, fg_color="transparent")
    row.pack(fill="x")
    
    # App icon
    icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
    if icon_path.exists():
        from PIL import Image
        app_icon = ctk.CTkImage(
            light_image=Image.open(icon_path),
            dark_image=Image.open(icon_path),
            size=(48, 48)
        )
        ctk.CTkLabel(row, image=app_icon, text="").pack(side="left", padx=(0, SPACING["md"]))
    
    # Text block
    text_block = ctk.CTkFrame(row, fg_color="transparent")
    text_block.pack(side="left", fill="x")
    
    ctk.CTkLabel(text_block, text="ClutchG PC Optimizer",
                 font=self._font(14, "bold"),
                 text_color=COLORS["text_primary"]).pack(anchor="w")
    ctk.CTkLabel(text_block, text=f"v{self.app.get_version()} · Windows 10/11",
                 font=self._font(11),
                 text_color=COLORS["text_secondary"]).pack(anchor="w")
    ctk.CTkLabel(text_block, text=self._ui("about_tagline"),
                 font=self._font(11),
                 text_color=COLORS["text_secondary"]).pack(anchor="w")
    
    # Links row
    links = ctk.CTkFrame(frame, fg_color="transparent")
    links.pack(anchor="w", pady=(SPACING["sm"], 0))
    
    # GitHub link
    github_btn = ctk.CTkButton(links, text="\ue774  GitHub",  # Segoe MDL2 OpenInNew
                                font=self._font(11),
                                fg_color="transparent",
                                text_color=COLORS["accent"],
                                hover_color=COLORS["bg_hover"],
                                height=24, width=80,
                                command=lambda: self._open_url("https://github.com/neckttiie090520/clutchg-pc-optimizer"))
    github_btn.pack(side="left", padx=(0, SPACING["sm"]))
    
    # Docs link
    docs_btn = ctk.CTkButton(links, text="\ue897  Docs",  # Segoe MDL2 Help
                              font=self._font(11),
                              fg_color="transparent",
                              text_color=COLORS["accent"],
                              hover_color=COLORS["bg_hover"],
                              height=24, width=60,
                              command=lambda: self.app.switch_view("help"))
    docs_btn.pack(side="left")
```

Add `_open_url()` helper:
```python
def _open_url(self, url):
    import webbrowser
    webbrowser.open(url)
```

### 3.6 UI_STRINGS Updates

Add/update both `en` and `th`:

```python
# EN
"title": "Settings",
"appearance": "Appearance",
"appearance_desc": "Choose your visual theme",
"theme": "Theme",
"language": "Language",
"language_desc": "Interface language (app restarts view)",
"safety": "Safety",
"auto_backup": "Auto Backup",
"auto_backup_desc": "Create backup before applying profiles",
"confirm_actions": "Confirm Actions",
"confirm_actions_desc": "Show confirmation dialogs before changes",
"flight_recorder": "Flight Recorder",
"flight_recorder_desc": "Log every tweak, rollback, and profile apply to a local file",
"about": "About",
"about_tagline": "A Windows optimizer built for gamers who want real performance gains, not snake oil.",
"app_name": "ClutchG PC Optimizer",

# TH
"appearance_desc": "เลือกธีมที่ชอบ",
"language_desc": "ภาษาของแอป (รีเฟรชหน้า)",
"auto_backup": "Auto Backup",
"auto_backup_desc": "สร้าง Backup อัตโนมัติก่อนใช้ Profile",
"confirm_actions": "Confirm Actions",
"confirm_actions_desc": "แสดงกล่องยืนยันก่อนเปลี่ยนแปลง",
"flight_recorder": "Flight Recorder",
"flight_recorder_desc": "บันทึกทุกการปรับแต่งและ rollback ลงไฟล์",
"about_tagline": "โปรแกรม Optimize Windows สำหรับเกมเมอร์ที่ต้องการผลลัพธ์จริง ไม่ใช่ snake oil",
```

### 3.7 Toast Messages — Localize

**Current:** Hardcoded English toast messages in `change_theme()` and `change_language()`.

**New:** Use `UI_STRINGS` keys:
```python
"toast_theme": "Theme → {value}",
"toast_language": "Language → {value}",
```

---

## 4. WelcomeOverlay Overhaul

**File:** `clutchg/src/gui/views/welcome_overlay.py`

### 4.1 App Logo on Step 1

**Current:** Step 1 has no visual — just title + content text.

**New:** Add the app icon above the step 1 title:

```python
# In setup_ui(), before header_label:
icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
if icon_path.exists():
    from PIL import Image
    logo = ctk.CTkImage(
        light_image=Image.open(icon_path),
        dark_image=Image.open(icon_path),
        size=(64, 64)
    )
    self.logo_label = ctk.CTkLabel(self, image=logo, text="")
    self.logo_label.grid(row=0, column=0, padx=40, pady=(30, 10), sticky="w")
    # Shift header to row 1
    self.header_label.grid(row=1, ...)
```

Only show on step 0 (Welcome). Hide on other steps:
```python
def show_step(self, step):
    ...
    if hasattr(self, 'logo_label'):
        if step == 0:
            self.logo_label.grid()
        else:
            self.logo_label.grid_remove()
```

### 4.2 Update Nav References

**Current content references old names:**
- `"Go to Profiles tab"` → `"Go to Profiles"`  (stays — Profiles is correct now)
- `"Click the Help button"` → `"Click Docs in the sidebar"`

Update `UI_STRINGS` step 5 content:

```python
# EN
"step5_content": "You're all set!\n\n1. Go to Profiles\n2. Choose a profile\n3. Click Apply\n4. Wait for completion\n5. Restart if prompted\n\nNeed help? Click Docs in the sidebar.",

# TH
"step5_content": "พร้อมแล้ว!\n\n1. ไปที่ Profiles\n2. เลือก Profile\n3. กด Apply\n4. รอให้เสร็จ\n5. Restart ถ้าถูกถาม\n\nต้องการความช่วยเหลือ? กด Docs ในแถบด้านข้าง",
```

### 4.3 Replace Unicode Arrows with Proper Text

**Current:** `"← Back"`, `"Next →"`, `"Get Started →"`

**New:** Remove the Unicode arrows. Use plain text only (the buttons have enough visual distinction from styling):

```python
"back_btn": "Back",
"next_btn": "Next",
"get_started": "Get Started",

# TH
"back_btn": "ย้อนกลับ",
"next_btn": "ถัดไป",
"get_started": "เริ่มใช้งาน",
```

### 4.4 Dot Progress Indicators

**Current:** Text-only `"Step 1 of 5"`.

**New:** Add dot indicators above the text progress. One dot per step, filled dot = current, empty = other.

```python
# In setup_ui():
self.dots_frame = ctk.CTkFrame(self, fg_color="transparent")
self.dots_frame.grid(row=N, column=0, pady=(5, 0))  # row adjusted for logo

self.dots = []
for i in range(self.total_steps):
    dot = ctk.CTkFrame(self.dots_frame, width=8, height=8,
                       corner_radius=4, fg_color=COLORS["bg_tertiary"])
    dot.pack(side="left", padx=3)
    self.dots.append(dot)

# In show_step():
for i, dot in enumerate(self.dots):
    if i == step:
        dot.configure(fg_color=COLORS["accent"])
    elif i < step:
        dot.configure(fg_color=COLORS["text_muted"])
    else:
        dot.configure(fg_color=COLORS["bg_tertiary"])
```

### 4.5 Skip Button Position

**Current:** Skip button is in the bottom navigation bar next to Back/Next.

**New:** Move Skip to top-right corner of the overlay:

```python
# In setup_ui() — add skip at top-right
self.skip_btn = ctk.CTkButton(
    self,
    text=self._ui("skip_btn"),
    width=100,
    fg_color="transparent",
    text_color=COLORS["text_muted"],
    hover_color=COLORS["bg_hover"],
    command=self.close
)
self.skip_btn.place(relx=1.0, x=-20, y=15, anchor="ne")
```

Remove skip_btn from the bottom `btn_frame`.

### 4.6 Step 5 Highlight — Success Color

**Current:** All highlight boxes use `accent` (sky blue) background.

**New:** Step 5 (final step) uses `success` (green) background:

```python
# In show_step():
if step == self.total_steps - 1:
    self.highlight_box.configure(fg_color=COLORS["success"])
else:
    self.highlight_box.configure(fg_color=COLORS["accent"])
```

### 4.7 Grid Row Adjustment

Adding the logo at the top shifts all rows. Update grid layout:

```
Row 0: Logo (step 0 only)
Row 1: Header (title)
Row 2: Content text (weight=1)
Row 3: Highlight box
Row 4: Dots + progress text
Row 5: Navigation buttons (Back/Next)
```

---

## 5. Implementation Order

Tasks should be implemented in this order (dependencies flow downward):

1. **App icon setup** (§1.1) — copy PNG to assets, no dependencies
2. **Sidebar logo** (§1.2) — depends on §1
3. **Window icon** (§1.4) — depends on §1
4. **ProfilesView title + UI_STRINGS** (§2.1, 2.4, 2.5) — independent
5. **ProfileCard redesign: stats grid + risk bar + buttons** (§2.2) — biggest task
6. **Compare panel** (§2.3) — depends on §5
7. **SettingsView section headers with icons** (§3.1) — independent
8. **SettingsView row layout + switches + flight recorder** (§3.2, 3.3, 3.4, 3.6, 3.7) — depends on §7
9. **SettingsView About section with app icon** (§3.5) — depends on §1
10. **WelcomeOverlay: logo + nav refs + arrows + dots + skip + step5 color** (§4) — depends on §1
11. **Build system icon** (§1.3) — depends on §1, do last

---

## 6. Files Modified

| File | Changes |
|------|---------|
| `C.GG-Photoroom.png` → `clutchg/src/assets/icon.png` | Copy app icon |
| `clutchg/src/gui/components/enhanced_sidebar.py` | Replace "C" text with CTkImage logo |
| `clutchg/src/gui/components/glass_card.py` | Redesign `ProfileCard`: stats grid, risk bar, two buttons, icon-in-circle |
| `clutchg/src/gui/views/profiles_minimal.py` | New title, hero text, PROFILE_STATS data, compare panel, UI_STRINGS overhaul |
| `clutchg/src/gui/views/settings_minimal.py` | Section icons, row layout, switches, flight recorder, about with icon+links, toast localization |
| `clutchg/src/gui/views/welcome_overlay.py` | App logo step 1, dot indicators, skip top-right, step 5 green, nav refs, remove arrows |
| `clutchg/src/app_minimal.py` | Window icon via iconphoto |
| `clutchg/build.py` | PNG→ICO conversion, --icon flag |

---

## 7. Testing Checklist

After implementation, verify:

- [ ] `pytest tests/unit -m unit` — no regressions
- [ ] `python -m compileall clutchg/src` — no syntax errors
- [ ] Manual: Sidebar shows app icon (32x32) instead of "C" text
- [ ] Manual: Profiles view title says "Profiles"
- [ ] Manual: Profile cards show stats grid (Tweaks/Gain/Risk/Restart)
- [ ] Manual: Profile cards show thin colored risk bar
- [ ] Manual: Profile cards have Preview + Apply buttons (Apply colored by risk)
- [ ] Manual: Compare panel expands/collapses below cards
- [ ] Manual: Settings sections have icon + uppercase title headers
- [ ] Manual: Safety toggles use switches not checkboxes
- [ ] Manual: Flight Recorder toggle appears in Safety section
- [ ] Manual: About section shows app icon + version + tagline + GitHub/Docs links
- [ ] Manual: Welcome overlay step 1 shows app icon
- [ ] Manual: Welcome overlay has dot progress indicators
- [ ] Manual: Welcome overlay Skip button is top-right
- [ ] Manual: Welcome step 5 highlight box is green
- [ ] Manual: No emoji visible anywhere
- [ ] Manual: Window icon/taskbar shows app icon

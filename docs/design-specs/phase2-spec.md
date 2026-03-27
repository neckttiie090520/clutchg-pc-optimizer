# Phase 2 Design Spec — Tweaks · Backup · Docs

> **Status:** Pending approval
> **Mockup:** `docs/design-mockups/phase2-scripts-backup-help.html` (v2, approved)
> **Scope:** 3 views (ScriptsView, BackupView, HelpView) + icon system + sidebar wording + help data

---

## 0. Global Rules (apply to every task)

| Rule | Detail |
|------|--------|
| No emoji | All icons rendered via Material Symbols Outlined or Segoe MDL2 Assets font — never emoji characters |
| No colored left-stripes | Cards use plain `border` only; recommended card gets `border-color: success` (2 px) |
| DeAI tone | Short, nerd+gamer-friendly copy. No corporate buzzwords. |
| Font | Figtree for all text (already set), Material Symbols Outlined for icons |
| Theme tokens | All colors from `theme.py` Sun Valley palette — no hardcoded hex outside theme |

---

## 1. Sidebar Wording Update

**File:** `clutchg/src/gui/components/enhanced_sidebar.py`
**Location:** `create_navigation()` method, `items` list (~line 160)

### Current → New

| nav key | Current label | New label |
|---------|---------------|-----------|
| `dashboard` | Dashboard | **Home** |
| `scripts` | Optimization | **Tweaks** |
| `backup` | Backup & Restore | **Backup** |
| `help` | Help | **Docs** |

Settings button label stays "Settings" (bottom button, separate creation in `app_minimal.py`).

### Implementation
Edit the `items` list:
```python
items = [
    ("dashboard",  "Home",    NAV_ICONS.get("dashboard", "\ue8b0")),
    ("scripts",    "Tweaks",  NAV_ICONS.get("scripts",   "\ue86f")),
    ("backup",     "Backup",  NAV_ICONS.get("backup",    "\ue1d7")),
    ("help",       "Docs",    NAV_ICONS.get("help",      "\ue88b")),
]
```

---

## 2. ScriptsView — Rename + Tab Rework

**File:** `clutchg/src/gui/views/scripts_minimal.py`

### 2.1 View Title
- Current: `"Optimization Center"` → New: **`"Tweaks"`**
- Subtitle stays: `"47 tweaks · 8 categories"` (dynamic)

**Location:** `_create_header()` method + `UI_STRINGS` dict (both `"en"` and `"th"`).

### 2.2 Tab Names

| tab key | Current label | New label | Icon (Material Symbols) |
|---------|---------------|-----------|------------------------|
| `quick_actions` | Quick Actions | **Quick Fix** | `bolt` (`\ue929`) |
| `presets` | Presets | **Profiles** | `tune` (`\ue429`) |
| `custom` | Custom Builder | **Custom** | `build` (`\ue869`) |
| `education` | Encyclopedia | **Glossary** | `menu_book` (`\ue8ca`) |

**Location:** `_create_tab_bar()` method. Tab icons currently use Segoe MDL2 codepoints (`\ue768`, `\ue762`, `\ue70f`, `\ue82d`). Replace with Material Symbols codepoints to match the icon font used project-wide via `icons.py`.

Also update `UI_STRINGS["en"]` and `UI_STRINGS["th"]` entries for tab names.

### 2.3 Profiles Tab (formerly Presets)

**Remove colored left-stripe bars** from preset cards.

**Current structure** in `_create_preset_card()`:
- GlassCard with `accent_color` parameter → creates a 4px colored left stripe
- `"RECOMMENDED FOR YOU"` badge (green background, white text)

**New structure:**
- GlassCard without `accent_color` (or set to `None`/transparent)
- Recommended card: `border_color=COLORS["success"]`, `border_width=2`
- Replace `"RECOMMENDED FOR YOU"` badge with quieter text badge: `"RECOMMENDED"` using `success_dim` bg + `success` text (same as `badge-low` style but with "RECOMMENDED" text)
- Profile names shortened: "Safe Mode" → **"Safe"**, "Competitive Mode" → **"Competitive"**, "Extreme Mode" → **"Extreme"**
- Button text: "Apply Safe Mode" → **"Apply Safe"**, etc.

**Location:** `_create_preset_card()` + `PRESET_INFO` dict + `UI_STRINGS`.

### 2.4 Quick Fix Tab (formerly Quick Actions)

- Button text: "Run Action" → **"Run"**
- Button text: "Open Link" → **"Open"**
- Description tone: tighten to short punchy sentences (see mockup v2 for reference wording)

**Location:** `_create_quick_action_card()` + `UI_STRINGS`.

### 2.5 Custom Tab — Split-Pane Layout

**This is the biggest structural change in Phase 2.**

**Current:** Full-width tweak list with toggles. No detail panel. Info button opens a modal dialog (`_show_tweak_detail()`).

**New:** Split-pane grid layout:
- **Left (flex 1):** Existing tweak list with category sections + toggle rows
- **Right (320px fixed):** Detail/glossary panel showing selected tweak info

**Layout implementation:**
```
┌─────────────────────────────────────┬──────────────────┐
│  Selection bar (full width)         │                  │
├─────────────────────────────────────┤  Detail Panel    │
│  ⚡ Power (4)                       │                  │
│  [toggle] Ultimate Performance...   │  USB Selective   │
│  [toggle] Disable CPU Throttling    │  Suspend         │
│  [toggle] USB Selective Suspend ◄───┤  ──────────      │
│                                     │  What it does    │
│  🌐 Network (3)                     │  ...             │
│  [toggle] TCP Nagle Disable         │  Impact          │
│  [toggle] DNS-over-HTTPS            │  Risk: LOW       │
│  [toggle] QoS Packet Scheduler      │  Effect: ...     │
│                                     │  Trade-off: ...  │
│                                     │  ──────────      │
│                                     │  Reversal        │
│                                     │  ...             │
└─────────────────────────────────────┴──────────────────┘
```

**New state variable:** `self.detail_tweak_id: Optional[str] = None`

**New method:** `_show_inline_detail(tweak)` — populates the right panel with:
1. Tweak name (title)
2. Category + type label (e.g. "Power · Registry tweak")
3. "What it does" section — full description
4. Impact table: Risk badge, Effect text, Trade-off text
5. Reversal instructions
6. Registry/command path (monospace, muted)

**Empty state:** When no tweak clicked, panel shows centered icon + "Select a tweak" + helper text.

**Clicking a tweak row** calls `_show_inline_detail(tweak)` (in addition to existing toggle behavior). The clicked row gets a highlight style (`detail-active`: `bg_active` + `accent_dim` border).

**Info button (ℹ)** on each tweak row: keep for opening the full modal, but most users will use the inline panel.

**Implementation approach:**
1. Wrap `_show_custom_tab()` content in a 2-column grid frame
2. Left column: existing `_create_selection_bar()` + `_create_category_section()` calls
3. Right column: new `self.detail_panel` frame (sticky top)
4. Add click handler to tweak rows that calls `_show_inline_detail()`

### 2.6 Glossary Tab (formerly Encyclopedia)

- Category headers: replace emoji with Material Symbols icon label
- Current: `&#x26A1;` (⚡ emoji) → use `bolt` icon in Material Symbols font
- Current: `&#x1F310;` (🌐 emoji) → use `lan` icon in Material Symbols font
- Expand arrow: replace `&#xE2C4;` with `expand_more` Material Symbols glyph

**Location:** `_show_education_tab()` + `_create_edu_card()` methods.

### 2.7 Emoji Cleanup in ScriptsView

Remove all remaining emoji from `scripts_minimal.py`:

| Current emoji | Location | Replacement |
|---------------|----------|-------------|
| `"📸"` | snapshot messages | Text only: `"[snap]"` |
| `"📥"` | import button | Material Symbols `download` icon label |
| `"📤"` | export button | Material Symbols `upload` icon label |
| `"🔄"` | restart indicator | Material Symbols `refresh` icon label |
| `"💡"` | recommendation tip | Material Symbols `lightbulb` icon label |
| `"★"` | recommended badge | Text badge `"RECOMMENDED"` (no symbol) |

---

## 3. BackupView — Strip & Clean

**File:** `clutchg/src/gui/views/backup_minimal.py`
(Also check `clutchg/src/gui/views/backup_restore_center.py` — the actual routed view)

### 3.1 View Title
Already "Backup" — keep as-is.

### 3.2 Info Banner — Remove Stripe

**Current:** `create_info_box()` creates a GlassCard with `accent_color` (green left stripe).

**New:** Replace with a plain card containing:
- Left: Material Symbols `shield` icon (success color, 20px)
- Right: Title + description text
- No `accent_color` / no left stripe

**Wording update:**
- Current title: `"Backup & Safety"`
- New title: **`"Auto-backup is on"`**
- Current desc: "ClutchG automatically creates backups before applying profiles..."
- New desc: **`"ClutchG snapshots your registry before every profile apply. You can also create manual backups here."`**

### 3.3 Backup Cards — Remove Stripes + Emoji

**Current:** Each `create_backup_card()` has:
- A colored left stripe (`indicator_frame`, 4px wide, green/warning)
- Status icon: `"✓"` or `"◉"` plain text

**New:**
- Remove left stripe entirely
- Replace status icons with Material Symbols in icon box:
  - Has restore point: `check_circle` icon (success color)
  - Registry only: `inventory_2` icon (text-tertiary color)
- Button text: add Material Symbols icons inline
  - Restore button: `restore` icon + "Restore"
  - Delete button: `delete` icon + "Delete"

### 3.4 Empty State — Neutral Icon

**Current:** Uses `"💾"` emoji (size 42) + green-tinted background.

**New:**
- Icon: Material Symbols `backup` glyph (36px, `text-tertiary` color)
- Background: `bg_hover` (neutral gray, not success-dim)
- Wording: "Create one before applying any tweaks. Takes a few seconds, saves hours of pain."
- CTA button: `add` icon + "Create Backup"

### 3.5 Error State

**Current:** Uses `"❌"` emoji.

**New:** Material Symbols `error` glyph (danger color).

### 3.6 Create Backup Button

**Current:** "+ Create Backup"

**New:** Material Symbols `add` icon + **"New Backup"**

---

## 4. HelpView → Docs View

**File:** `clutchg/src/gui/views/help_minimal.py`

### 4.1 View Title
- Current: `"Help & Documentation"` → New: **`"Docs"`**

**Location:** `_create_header()` (if exists) + `UI_STRINGS`.

### 4.2 Topic Sidebar — Replace Emoji with Icon Labels

**Current:** Topic buttons render `f"{topic.icon} {topic.title}"` as a single text string. The `topic.icon` comes from `help_content.json` (emoji strings).

**Problem:** You can't just swap in a Material Symbols codepoint and concatenate it — the icon needs its own font family. The icon and title text need separate labels (or a compound widget).

**New approach:** In `create_sidebar()`, for each topic button:
1. Create a small frame (horizontal pack) instead of a single button
2. Left: `CTkLabel` with Material Symbols font → icon glyph
3. Right: `CTkLabel` with Figtree font → topic title
4. Bind click to both labels + frame

**Icon mapping (for sidebar):**

| topic_id | Current icon | New Material Symbols glyph |
|----------|-------------|---------------------------|
| `getting_started` | 🚀 | `rocket_launch` |
| `dashboard` | 📊 | `bar_chart` |
| `profiles` | ⚙️ | `tune` |
| `optimization_center` | 🧩 | `extension` |
| `quick_actions` | ⚡ | `bolt` |
| `scripts` | 📜 | `description` |
| `backup` | 💾 | `backup` |
| `safety` | ⚠️ | `shield` |
| `troubleshooting` | 🔧 | `build` |
| `settings` | ⚙️ | `settings` |
| `risk_levels` | ⚠️ | `warning` |
| `profile_recommendations` | 🎯 | `target` |
| `about` | ℹ️ | `info` |

**Where to store mapping:** Add these keys to `IconProvider.ICONS` dict in `icon_provider.py`. Then the sidebar renders using `get_icon(topic_icon_key)` + `get_icon_font()`.

### 4.3 help_content.json — Icon Field Update

**File:** `clutchg/src/data/help_content.json`

Change all `"icon"` fields from emoji strings to icon key strings that map to `IconProvider.ICONS`:

```json
"getting_started": {
  "en": { "title": "Getting Started", "icon": "rocket_launch", ... }
}
```

This means `HelpManager.get_topic()` returns `HelpTopic(icon="rocket_launch")` instead of `HelpTopic(icon="🚀")`. The rendering code in `help_minimal.py` must then look up the glyph via `get_icon()`.

### 4.4 Topic Content Title — Same Pattern

**Current:** `help_topic_title` renders `f"{topic.icon} {topic.title}"` at top of content area.

**New:** Same compound-widget approach as sidebar: icon label (Material Symbols font) + title label (Figtree).

### 4.5 Inline Emoji in Content Renderers

| Location | Current | Replacement |
|----------|---------|-------------|
| `_render_safety()` myths | `ICON('error')` / `ICON('success')` | Keep — already uses icon provider |
| `_render_safety()` who_should_use | `"💡"` prefix | Material Symbols `lightbulb` icon label |
| `_render_troubleshooting()` | `"🔧"` problem prefix | Material Symbols `build` icon label |

### 4.6 Wording Updates (UI_STRINGS)

| Key | Current (EN) | New (EN) |
|-----|-------------|----------|
| header | Help & Documentation | Docs |
| Quick Start step 1 | "Go to Optimize and pick a preset" | "Go to Tweaks → Profiles and pick one" |
| Quick Start step 4 | "Check Dashboard to see..." | "Check Home for your updated score" |

Update `UI_STRINGS["th"]` equivalents accordingly.

### 4.7 View Link Resolution

**Current:** `_resolve_view_link()` maps `"optimization center"` → `"scripts"`.

**New:** Also map `"tweaks"` → `"scripts"` (since users will now see "Tweaks" in sidebar).

---

## 5. Icon Provider — New Keys

**File:** `clutchg/src/gui/components/icon_provider.py`

Add the following entries to `ICONS` dict (help content icons):

```python
# Help topics
"rocket_launch": "\ue559",   # Getting Started
"bar_chart":     "\ue26b",   # Dashboard topic
"tune":          "\ue429",   # Profiles topic
"extension":     "\ue87b",   # Optimization Center topic
"bolt":          "\ue929",   # Quick Actions / Power
"description":   "\ue873",   # Scripts topic
"shield":        "\ue914",   # Safety topic
"target":        "\uf2c4",   # Profile recommendations
"lightbulb":     "\ue0a3",   # Tips
"lan":           "\ue639",   # Network category
"build":         "\ue869",   # Troubleshooting / Custom tab
"menu_book":     "\ue8ca",   # Glossary tab
"download":      "\ue2c4",   # Import
"upload":        "\ue2c6",   # Export
"play_arrow":    "\ue037",   # Run button
"open_in_new":   "\ue89e",   # External link
"expand_more":   "\ue5cf",   # Glossary expand
"add":           "\ue145",   # Create/New (may already exist)
"restore":       "\ue855",   # Restore button (may already exist)
"check_circle":  "\ue86c",   # Backup with restore point
"inventory_2":   "\ue1d7",   # Registry-only backup
"refresh":       "\ue5d5",   # Restart indicator
```

Check for existing entries to avoid duplicates. Some of these (`add`, `restore`, `network`) already exist — just verify codepoints match.

Also ensure `icons.py` `MATERIAL_ICONS` dict has matching entries (these two dicts should stay in sync).

---

## 6. Myth Cards — Text Prefix Instead of Emoji

**Current:** `_render_safety()` uses `ICON('error')` and `ICON('success')` for myth/fact.

**New:** Keep the icon approach but change the label prefix:
- Myth line: `"MYTH: "` + myth text (danger color)
- Fact line: `"FACT: "` + fact text (success color)

This avoids the check/cross emoji pattern.

---

## 7. Implementation Order

Tasks should be implemented in this order (dependencies flow downward):

1. **Icon Provider keys** (§5) — no dependencies, unlocks everything
2. **help_content.json icon fields** (§4.3) — depends on §5
3. **Sidebar wording** (§1) — independent
4. **ScriptsView title + tab names + UI_STRINGS** (§2.1, 2.2) — independent
5. **ScriptsView Profiles tab: remove stripes + wording** (§2.3) — depends on §4
6. **ScriptsView Quick Fix tab wording** (§2.4) — independent
7. **ScriptsView emoji cleanup** (§2.7) — depends on §5
8. **ScriptsView Custom tab split-pane** (§2.5) — biggest task, independent
9. **ScriptsView Glossary tab icon cleanup** (§2.6) — depends on §5
10. **BackupView cleanup** (§3) — depends on §5
11. **HelpView → Docs: title + sidebar icons + content renderers** (§4) — depends on §5, §4.3
12. **Myth card text prefix** (§6) — depends on §4

---

## 8. Files Modified

| File | Changes |
|------|---------|
| `clutchg/src/gui/components/icon_provider.py` | Add ~15 new icon keys |
| `clutchg/src/gui/icons.py` | Sync new keys if missing |
| `clutchg/src/gui/components/enhanced_sidebar.py` | Update nav item labels |
| `clutchg/src/gui/views/scripts_minimal.py` | Title, tab names, profiles (no stripe), quick fix wording, custom split-pane, glossary icons, emoji removal |
| `clutchg/src/gui/views/backup_minimal.py` | Remove stripes, emoji→icon, wording |
| `clutchg/src/gui/views/backup_restore_center.py` | Check if wraps BackupView — may need same changes |
| `clutchg/src/gui/views/help_minimal.py` | Title→Docs, sidebar icon labels, content title icons, inline emoji removal, view link map |
| `clutchg/src/data/help_content.json` | All `"icon"` fields: emoji→key strings |
| `clutchg/src/core/help_manager.py` | Default icon fallback: `"ℹ️"` → `"info"` |

---

## 9. Testing Checklist

After implementation, verify:

- [ ] `pytest tests/unit -m unit` — no regressions
- [ ] Manual: sidebar shows "Home / Tweaks / Backup / Docs"
- [ ] Manual: Tweaks view title says "Tweaks", tabs say "Quick Fix / Profiles / Custom / Glossary"
- [ ] Manual: Profile cards have no colored left stripe; Safe has green border
- [ ] Manual: Custom tab shows split-pane with detail panel on right
- [ ] Manual: Clicking a tweak row populates the detail panel
- [ ] Manual: Backup cards have no colored left stripe; use icon-box instead
- [ ] Manual: Backup empty state uses neutral gray icon, not emoji
- [ ] Manual: Docs view title says "Docs"; sidebar topics use Material Symbols icons
- [ ] Manual: No emoji visible anywhere in the app
- [ ] Manual: Myth cards use "MYTH:" / "FACT:" text prefix
- [ ] `python -m compileall clutchg/src` — no syntax errors

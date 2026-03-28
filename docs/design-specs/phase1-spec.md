# Phase 1 Design Spec — Components · Sidebar · Dashboard

> **Status:** Pending approval
> **Mockup:** `docs/design-mockups/phase1-sidebar-dashboard.html` (approved)
> **Scope:** Theme token cleanup, 8 component fixes, sidebar refactor, dashboard cleanup

---

## 0. Global Rules (apply to every task)

| Rule | Detail |
|------|--------|
| No emoji | All icons via Segoe MDL2 Assets — never emoji characters |
| No colored left-stripes | Cards use plain `border` only |
| DeAI tone | Short, nerd+gamer-friendly copy |
| Font | Figtree for all text, Segoe MDL2 Assets for icons |
| Theme tokens | All colors from `theme.py` Sun Valley palette — no hardcoded hex outside theme |
| Don't fix LSP errors | Pre-existing CTkFont type annotation mismatches are known and harmless at runtime |

---

## 1. Theme Token Cleanup

**File:** `clutchg/src/gui/theme.py` (611 lines)

### 1.1 Unify SIZES radius vs RADIUS dict

Two radius systems exist with **conflicting values**:

| Key | SIZES (line 439) | RADIUS (line 468) |
|-----|------------------|-------------------|
| sm  | 6                | 4                 |
| md  | 8                | 6                 |
| lg  | 10               | 10                |
| xl  | 12               | 14                |
| full| 9999             | 9999              |

**Fix:** Keep RADIUS as the canonical source. Remove `radius_sm`, `radius_md`, `radius_lg`, `radius_xl`, `radius_full` from SIZES. Keep `card_radius` and `button_radius` in SIZES as convenience aliases that reference RADIUS values:

```python
# In SIZES dict — remove these keys:
#   radius_sm, radius_md, radius_lg, radius_xl, radius_full

# Keep these convenience aliases, updated to match RADIUS:
"card_radius": 14,   # == RADIUS["xl"]
"button_radius": 6,  # == RADIUS["md"]
```

Then grep all callers of `SIZES["radius_*"]` and replace with `RADIUS["sm"]` / `RADIUS["md"]` / etc.

### 1.2 Convert rgba() glass tokens to hex

CustomTkinter does not support `rgba()` strings — these tokens are non-functional. Convert all 12 occurrences (3 per theme × 4 themes) to hex:

| Theme | Token | rgba() | Hex replacement |
|-------|-------|--------|-----------------|
| dark | glass_light | rgba(255,255,255,0.05) | `#ffffff0d` |
| dark | glass_medium | rgba(255,255,255,0.08) | `#ffffff14` |
| dark | glass_strong | rgba(255,255,255,0.12) | `#ffffff1f` |
| zinc | glass_light | rgba(255,255,255,0.03) | `#ffffff08` |
| zinc | glass_medium | rgba(255,255,255,0.05) | `#ffffff0d` |
| zinc | glass_strong | rgba(255,255,255,0.1) | `#ffffff1a` |
| light | glass_light | rgba(0,0,0,0.03) | `#00000008` |
| light | glass_medium | rgba(0,0,0,0.05) | `#0000000d` |
| light | glass_strong | rgba(0,0,0,0.08) | `#00000014` |
| modern | glass_light | rgba(255,255,255,0.04) | `#ffffff0a` |
| modern | glass_medium | rgba(255,255,255,0.07) | `#ffffff12` |
| modern | glass_strong | rgba(255,255,255,0.11) | `#ffffff1c` |

**Note:** CustomTkinter may not support 8-digit hex (with alpha). If not, use the nearest opaque hex on the theme's background. For the modern (Sun Valley) theme that we actually use:
- `glass_light` → `#222222` (bg_primary `#1c1c1c` + 4% white)
- `glass_medium` → `#252525` (bg_primary + 7% white)
- `glass_strong` → `#292929` (bg_primary + 11% white)

Test whether CTk accepts `#ffffff0a` first. If it does, use the alpha hex. If not, use the pre-blended opaque values for each theme.

### 1.3 Deprecate duplicate tokens

- **`body_medium` font** (line 412): Identical to `body` (line 411) — both `("Figtree", 14, "normal")`. Remove `body_medium`. Grep callers and replace with `body`.
- **`text_dim` color**: In the dark theme it's identical to `text_muted`. In other themes they differ slightly. Since the modern (Sun Valley) theme is the active one and has `text_dim: #404040` vs `text_muted: #595959`, keep both — they serve different purposes (dim = near-invisible, muted = deemphasized). **No change needed for `text_dim`.**

---

## 2. Component Fixes

### 2.1 glass_card.py — Apply padding parameter

**File:** `clutchg/src/gui/components/glass_card.py` (437 lines)
**Line:** 24 (`__init__`, `padding: int = SPACING["md"]`)

The `padding` parameter is accepted but never applied. Store it and use it:

```python
# In __init__, after super().__init__():
self._padding = padding
self.configure(padx=padding, pady=padding)
```

**Scope:** Only the `GlassCard` base class (lines 1-115). Do NOT touch `ProfileCard` (lines 117+) — it was redesigned in Phase 3.

### 2.2 enhanced_button.py — Height 40→32 + remove dead code

**File:** `clutchg/src/gui/components/enhanced_button.py` (423 lines)

1. Change default `height` from `40` to `32` on all 8 factory methods: `primary()`, `success()`, `warning()`, `danger()`, `info()`, `outline()`, `ghost()`, `solid()`.
2. Remove the dead `apply_focus_style()` function (lines 28-48, 21 lines). It is never called anywhere.

### 2.3 circular_progress.py — Fix font Inter→Figtree

**File:** `clutchg/src/gui/components/circular_progress.py` (268 lines)
**Line 57:** `value_font = ("Inter", 56, "bold")`

Change to: `value_font = ("Figtree", 56, "bold")`

### 2.4 gradient.py — Fix font + remove dead classes

**File:** `clutchg/src/gui/components/gradient.py` (325 lines)

1. **Remove `GradientFrame` class** (lines 27-138) — dead code, zero importers.
2. **Remove `GradientButton` class** (lines 140-298) — dead code, zero importers.
3. **Keep `GradientLabel` class** (lines 300-325) — imported by `dashboard_minimal.py`. Fix its font fallback from `"Inter"` to `"Figtree"` if any (check line 189, 196 — these are inside the classes being removed, so they'll go away).

After removal, `gradient.py` should contain only `GradientLabel` (~25 lines). If `GradientLabel` itself is also unused (confirmed: it IS imported by dashboard but never actually used — see §4.2), then remove the entire file and the import. Verify first.

### 2.5 Module-level COLORS in 5 components

These 5 files import `COLORS` at module level. The `COLORS` dict is updated in-place by `ThemeManager`, so existing references will point to current values. However, widgets created with stale values at construction time won't auto-update.

**Assessment:** Since ClutchG only uses the "modern" (Sun Valley) theme and doesn't support runtime theme switching, this is a **low priority cosmetic issue**, not a functional bug. Skip this task — it's unnecessary churn for zero user-visible benefit.

**Decision: SKIP §2.5.** Mark as "won't fix — no runtime theme switching."

Files affected (no changes):
- `execution_dialog.py` (299 lines)
- `inline_help.py` (91 lines)
- `timeline.py` (497 lines)
- `toast.py` (110 lines)
- `tooltip.py` (76 lines)

### 2.6 view_transition.py — Add safety reset for transitioning flag

**File:** `clutchg/src/gui/components/view_transition.py` (247 lines)

The `self.transitioning` flag can get stuck `True` if the fade animation fails mid-step (widget destroyed, TclError). Add a try/except around the animation step:

```python
# In _fade_in / _fade_out step function, wrap with:
try:
    # existing animation step code
except (tk.TclError, Exception):
    self.transitioning = False
    if callback:
        callback()
```

Also add a **timeout safety net** — if `transitioning` has been True for >3 seconds, force-reset it in `show_view()`:

```python
# At top of show_view(), after the transitioning check:
if self.transitioning:
    # Safety: force-reset if stuck for >3s
    import time
    if hasattr(self, '_transition_start') and time.time() - self._transition_start > 3:
        self.transitioning = False
    else:
        return
# Set timestamp when starting:
self._transition_start = time.time()
```

### 2.7 icon_provider.py — Standardize on Segoe MDL2

**File:** `clutchg/src/gui/components/icon_provider.py` (255 lines)

The ICONS dict contains a **mix** of Material Symbols codepoints and Segoe MDL2 codepoints. Since Windows is the only target platform and the sidebar/nav already uses Segoe MDL2 via `NAV_ICONS` in `theme.py`, standardize the `IconProvider.ICONS` dict to use **Segoe MDL2 Assets codepoints only**.

**Implementation:** Go through each icon key in `ICONS` dict and verify/replace the codepoint with the correct Segoe MDL2 Assets value. Key mappings needed:

| Icon key | Current (mixed) | Segoe MDL2 codepoint |
|----------|-----------------|---------------------|
| grid_view | \ue871 (Material) | \ue80a |
| tune | \ue429 (Material) | \ue713 |
| terminal | \ueb8e (Material) | \ue756 |
| school | \ue80c (Material) | \ue7be |
| (etc.) | ... | ... |

The full mapping requires looking up each icon in the [Segoe MDL2 Assets reference](https://learn.microsoft.com/en-us/windows/apps/design/style/segoe-ui-symbol-font). Do this icon-by-icon during implementation.

Also update `get_icon_font()` to simply return `("Segoe MDL2 Assets",)` without Material Symbols fallback chain — simplify the method.

---

## 3. Sidebar Refactor

**File:** `clutchg/src/gui/components/enhanced_sidebar.py` (407 lines)
**File:** `clutchg/src/app_minimal.py` (312 lines)

### 3.1 Move Settings into sidebar's create_navigation()

**Problem:** `app_minimal.py` `_add_settings_button()` (lines 191-218) injects a settings button directly into the sidebar's `nav_container` with `label: None`, `indicator: None`, `frame: None`. This causes crashes in `refresh_colors()` which calls `.configure()` on `None`.

**Fix:**

1. **In `enhanced_sidebar.py` `create_navigation()`:** Add Settings as a proper nav item at the bottom, separated by a 1px divider:

```python
# After creating the main nav items loop, add:

# Divider before Settings
divider = ctk.CTkFrame(self.nav_container, height=1,
    fg_color=colors["border"])
divider.pack(fill="x", padx=12, pady=(8, 8))

# Settings nav item (same structure as other items)
self._create_nav_button("settings", "Settings", "\ue713", colors)
```

The `_create_nav_button` helper (or inline code) must create the same dict structure as other nav items: `{"button": btn, "label": lbl, "indicator": ind, "frame": frame}`.

2. **In `app_minimal.py`:** Remove the entire `_add_settings_button()` method and its call. The sidebar now owns the Settings button.

3. **Settings icon:** Use Segoe MDL2 `\ue713` (Settings gear). Currently it uses `\ue8b8` (from `NAV_ICONS` theme.py) with Material Symbols font — switch to Segoe MDL2 matching other nav items.

### 3.2 Nav label alignment

Current sidebar labels are already updated: Home, Tweaks, Backup, Docs, Settings. These are correct per the approved Phase 2 spec. No change needed.

---

## 4. Dashboard Cleanup

**File:** `clutchg/src/gui/views/dashboard_minimal.py` (750 lines)

### 4.1 Remove dead methods

Delete these 3 methods that are never called:

| Method | Lines | Size |
|--------|-------|------|
| `_score_grade()` | 415-424 | 10 lines |
| `create_component_scores()` | 443-511 | 69 lines |
| `create_health_tiles()` | 586-667 | 82 lines |

Total: ~161 lines removed.

### 4.2 Remove unused GradientLabel import

**Line 23:** `from gui.components.gradient import GradientLabel`

Remove this import. `GradientLabel` is never referenced in the file beyond the import line.

After this + §2.4 (removing dead classes from gradient.py), check if `gradient.py` has any remaining callers. If `GradientLabel` was the only export and it's now unused everywhere, delete `gradient.py` entirely.

### 4.3 Header layout — move Scan System to header

**Current:** Both "Apply Optimization" and "Scan System" buttons are inside the Quick Actions card (right panel).

**Mockup wants:** "Scan System" as a secondary/outline button in the header row (top-right), next to the status badge.

**Implementation:**
- In `_create_header()`: add a "Scan System" outline button to the right side of the header frame.
- In the Quick Actions card: remove the duplicate "Scan System" button, keep only "Apply Optimization" as the primary CTA.

---

## 5. Task Order (implementation sequence)

| Order | Section | File(s) | Risk |
|-------|---------|---------|------|
| 1 | §1.1 Unify radius | theme.py + callers | Low — token rename |
| 2 | §1.2 Convert rgba() glass | theme.py | Low — token values |
| 3 | §1.3 Remove body_medium | theme.py + callers | Low — font alias |
| 4 | §2.1 glass_card padding | glass_card.py | Low — additive |
| 5 | §2.2 enhanced_button height + dead code | enhanced_button.py | Low — default change |
| 6 | §2.3 circular_progress font | circular_progress.py | Low — string change |
| 7 | §2.4 gradient.py cleanup | gradient.py | Low — dead code removal |
| 8 | §2.6 view_transition safety | view_transition.py | Low — error handling |
| 9 | §2.7 icon_provider standardize | icon_provider.py | Medium — codepoint mapping |
| 10 | §3.1 Sidebar Settings refactor | enhanced_sidebar.py + app_minimal.py | Medium — structural |
| 11 | §4.1-4.2 Dashboard dead code | dashboard_minimal.py + gradient.py | Low — deletion |
| 12 | §4.3 Dashboard header layout | dashboard_minimal.py | Medium — layout change |

**Skipped:** §2.5 (module-level COLORS in 5 components) — won't fix, no runtime theme switching.

---

## 6. Verification

After all tasks:
1. `python -m compileall clutchg/src` — syntax check
2. `pytest tests/unit -m unit` — all 381+ tests pass
3. Visual check — launch app, verify sidebar, dashboard, icon rendering

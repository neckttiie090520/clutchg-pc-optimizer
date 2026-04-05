# ClutchG UI Redesign Guidelines (Minimal Hybrid Style)

## 1. Design Concept & Direction
This redesign logic unifies three distinct operating system aesthetics into a seamless, high-end desktop application interface. The goal is a professional, production-grade flat interface without generic "AI 3D slop."

* **Linux Ubuntu:** Structural layout, grid precision, functional hierarchy, and data readability.
* **Windows 11:** Mica-like acrylic backgrounds, subtle 1px component borders, switch toggles, and centered elegance.
* **macOS:** Deep and soft drop shadows for elevation, traffic-light button accents, and flawless typographic spacing (using San Francisco or Inter).

## 2. Core Theme Tokens
The overarching theme is a "Deep Dark" aesthetic designed to reduce eye strain while looking extremely premium.

* **Main Background:** `#1A1B26` (Deep blue-gray)
* **Card/Surface Background:** `#24283B` (Elevated dark gray layer)
* **Text Main (Primary):** `#C0CAF5` (Soft blue-white for comfortable contrast)
* **Text Muted (Secondary):** `#565F89`
* **Accents:** 
   * **Primary Action:** `#7AA2F7` (Windows 11 inspired bright blue)
   * **Secondary/System action:** `#BB9AF7` (Lavender/purple)
   * **Destructive:** macOS inspired traffic-light red or standard flat red for Delete dialogs.

## 3. Topography & Iconography
* **Font Family:** Inter or Roboto. Drop native Windows fonts like Segoe UI unless explicitly styling for native Windows 11 components.
* **Hierarchy:** Clear distinction using font weights rather than excessive colors. Headers should be `Semi-Bold`, data points `Medium`, and descriptions `Regular`.
* **Icons:** Clean, stroke-based minimal icons. Maintain consistent `2px` stroke weights across all iconography.

## 4. Component Rules

### **4.1. The Dashboard (Circular & Grid Based)**
* Instead of text arrays, the dashboard prioritizes a large **Performance Score Arc**.
* Use a **4-Grid Layout** (CPU, GPU, RAM, Storage) directly pulled from `UI_REDESIGN_PLAN.md`.
* Cards maintain a consistent `border-radius: 8px` to `12px` (macOS softness).

### **4.2. Cards & Windows (Elevation)**
* Modal dialogs (`Execution Dialog`, `Delete/Create Backup`) must float above the main interface. 
* Use macOS-style deep shadow arrays to establish depth, rather than solid borders alone.
* On inner components (like the custom builder list), use Windows 11's 1px subtle separation lines.

### **4.3. Navigation & Actions**
* The Sidebar must NOT have harsh separation lines. It should blend smoothly with the main view.
* Replace checkboxes with large, tactile toggle switches (Win11/iOS inspired).
* Maintain standard macOS spacing for primary action buttons (Cancel on left, Primary Action on right).

## 5. Reviewing the Redesigned Screens
All 14 generated mockups in this `Redesign` folder follow these exact guidelines. You will notice:
- The `01_dashboard.png` acts as a striking hero component.
- The `05_optimization_encyclopedia.png` focuses heavily on typography and reading comfort.
- The Backup dialogs (`11`, `12`, `13`) feel native and trustworthy.

*See `UI_REDESIGN_PLAN.md` for the technical mapping constraints when implementing these visuals in CustomTkinter (`ctk`).*

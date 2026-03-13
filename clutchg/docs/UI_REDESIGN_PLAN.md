# แผนงานออกแบบ UI/UX สำหรับ ClutchG (UI Redesign Plan)

เอกสารฉบับนี้วิเคราะห์งานออกแบบจากไฟล์ Reference ในโฟลเดอร์ `UI-research-idea` และเสนอแนวทางการนำมาพัฒนา ClutchG ให้มีความทันสมัยและน่าใช้งานในระดับสากล

---

## 2. บทวิเคราะห์ Reference และแนวทางพัฒนา (Visual Analysis & Adaptation)

### 2.1 Reference: VoltAir (จากไฟล์ `image copy 11.png`)
**วิจารณ์ (Critique):**
*   **Performance Score:** จุดเด่นที่สุดคือวงกลมแสดงคะแนน Performance ตรงกลาง ทำให้ผู้ใช้เข้าใจสถานะเครื่องทันทีโดยไม่ต้องอ่านตัวเลขเยอะๆ เป็นจิตวิทยาที่ทำให้ user อยากกด "Optimize" ให้เลขมันเต็ม
*   **Information Hierarchy:** แบ่ง System Info ออกเป็นกลุ่มชัดเจน แต่ไม่รก ใช้ Grid 2 columns (ซ้าย Performance, ขวา System Spec) ที่สมดุล
*   **Cleanliness:** พื้นที่ว่าง (White space) ค่อนข้างเยอะ ทำให้ดูสบายตา ไม่รู้สึกอึดอัดเหมือนเครื่องมือ System info สมัยก่อน

**การนำมาใช้ (Action Plan):**
*   **Dashboard Redesign:** เปลี่ยนหน้า Dashboard เดิมที่เป็น Text ธรรมดา ให้มี "Hero Section" เป็น Performance Score (ใช้ `canvas` วาด Arc หรือ `customtkinter` progress bar แบบวงกลม)
*   **Card Layout:** ใช้ `CTkFrame` ทำกรอบ System Info แยกเป็นส่วนๆ และใส่ Corner Radius ให้โค้งมน
*   **Implementation:**
    ```python
    # Concept Code for Score
    self.score_canvas = ctk.CTkCanvas(self, width=200, height=200, bg=self.cget("bg_color")[1], highlightthickness=0)
    # วาด arc สีฟ้าบนพื้นหลังสีเทาเข้ม
    ```

### 2.2 Reference: Sparkle Beta (จากไฟล์ `image copy 10.png`)
**วิจารณ์ (Critique):**
*   **Component Cards:** ชอบตรงที่แยก Hardware (CPU, GPU, Memory, Storage) เป็นการ์ดแยกกันชัดเจน พร้อมไอคอนประจำหมวด ทำให้กวาดสายตาหาง่ายมาก
*   **Sidebar Navigation:** เมนูด้านซ้ายดู Clean มาก มีแค่ Icon กับ Text ไม่มีเส้นขอบรกๆ และไฮไลท์หน้าที่เลือกด้วยสีฟ้า (Accent Color) ที่เด่น
*   **Personalization:** มีข้อความ "Good to see you, [User]" สร้างความรู้สึกเป็นกันเอง

**การนำมาใช้ (Action Plan):**
*   **Hardware Cards:** สร้าง Custom Widget ชื่อ `InfoCard` ที่รับ icon, title, subtitle, และ detail มาแสดงผล เพื่อให้โค้ดสะอาดและ reusable
*   **Sidebar Upgrade:** ปรับ `EnhancedSidebar` ของเดิมของเรา ให้ตัดเส้นขอบออก และใช้สีพื้นหลังที่โปร่งใสขึ้นเมื่อไม่ได้เลือก (Transparent by default)
*   **Implementation:**
    - ใช้ `grid(row=0, column=0, ...)` แบ่ง 2x2 สำหรับการ์ด CPU/GPU/RAM/Storage บนหน้าจอ Desktop

### 2.3 Reference: QuickBoost (จากไฟล์ `image copy 2.png`)
**วิจารณ์ (Critique):**
*   **Action Oriented:** หน้านี้เน้นปุ่มกด (Toggles/Buttons) ที่ชัดเจน ปุ่มใหญ่กดง่าย เหมาะกับหน้า "Advanced Tweaks"
*   **Color Coding:** ใช้สีม่วงอ่อน (Lavender) สำหรับปุ่มที่ Action ได้ ทำให้แยกออกจากพื้นหลังสีเทาเข้มได้ชัดเจน

**การนำมาใช้ (Action Plan):**
*   **Toggle Style:** ในหน้า Settings หรือ Tweaks ควรใช้ปุ่มสไตล์ `Switch` หรือ `SegmentedButton` แทน Checkbox เล็กๆ เพื่อให้ดู Modern ขึ้น
*   **Grouping:** จัดกลุ่ม Tweak (เช่น Memory, BCD, GPU) และใส่ Header ให้ชัดเจน

### 2.4 Reference: Advanced Filters (จากไฟล์ `image copy 12.png`)
**วิจารณ์ (Critique):**
*   **Depth & Layer:** มีการใช้ Popup/Modal ที่ลอยอยู่เหนือพื้นหลัง (Drop Shadow) และสีพื้นหลังที่เข้มตัดกัน
*   **Controls:** Design ของ Dropdown และ Filter ดูมีความละเอียด (Refined) เส้นขอบบางเฉียบ (1px border)

**การนำมาใช้ (Action Plan):**
*   **Confirmation Dialogs:** เวลา User กด Optimize ควรมี Popup ยืนยันที่สวยงามแบบนี้ ไม่ใช่แค่ MessageBox ของ Windows เดิมๆ ใช้ `CTkToplevel` ทำ Custom Dialog

---

## 3. สรุปแนวทางเทคนิค (Technical Implementation Strategy)

เพื่อให้ได้หน้าตาแบบ Reference เราต้องปรับปรุง Codebase ปัจจุบันดังนี้:

### 3.1 Design System Setup
สร้างไฟล์ `src/gui/design_system.py` เพื่อกำหนดค่ากลาง:
*   **Colors:**
    *   `BG_DARK`: `#1a1b26` (Background หลัก)
    *   `BG_CARD`: `#24283b` (พื้นหลัง Card)
    *   `ACCENT_PRIMARY`: `#7aa2f7` (สีฟ้าสำหรับปุ่มหลัก/Highlight)
    *   `ACCENT_SECONDARY`: `#bb9af7` (สีม่วงสำหรับปุ่มรอง)
    *   `TEXT_MAIN`: `#c0caf5`
    *   `TEXT_MUTED`: `#565f89`
*   **Typography:** เลิกใช้ฟอนต์ Default, เปลี่ยนไปใช้ฟอนต์อย่าง **Roboto** หรือ **Inter** (ถ้ามี) หรือ Segoe UI Variable

### 3.2 Custom Components
ต้องสร้าง Class ใหม่ๆ แทนที่จะใช้ `ctk` ดิบๆ ทุกที่:
1.  **`GlassCard(ctk.CTkFrame)`:** มี Background สีจางๆ + Blur effect (ถ้าทำได้) หรือ Gradient
2.  **`StatCard`:** สำหรับโชว์ CPU/RAM แบบ Sparkle (Icon + Value)
3.  **`ActionCard`:** สำหรับปุ่ม Tweak แบบ QuickBoost

### 3.3 Layout Structure
*   **Main Container:** ใช้ Grid Layout ที่มีความยืดหยุ่น (Responsive)
*   **Sidebar:** Fixed width ด้านซ้าย (250px)
*   **Content:** Expand เต็มพื้นที่ที่เหลือ (Weight=1)

---

## 4. แผนการทำงาน (Next Steps)

1.  **[Foundation]** สร้างไฟล์ Theme ใหม่ (`clutchg_theme.json`) หรือ `design_system.py`
2.  **[Navigation]** Redesign Sidebar ใหม่ให้ Minimal ตาม Reference "Sparkle"
3.  **[Dashboard]** รื้อหน้า Dashboard เดิม:
    *   ใส่ Performance Circle (VoltAir style)
    *   ทำ 4-Grid Cards สำหรับ Hardware Specs (Sparkle style)
4.  **[Tweaks]** ปรับหน้า Tweak ให้ปุ่มใหญ่กดง่าย (QuickBoost style)

เอกสารนี้ใช้เป็นแนวทางตั้งต้นสำหรับการพัฒนา UI/UX ในเฟสถัดไป เพื่อให้ ClutchG แข่งขันได้ทั้งประสิทธิภาพและความสวยงาม

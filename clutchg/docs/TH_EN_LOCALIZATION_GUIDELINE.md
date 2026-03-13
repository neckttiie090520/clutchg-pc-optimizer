# ClutchG Localization Guideline (TH+ENG Strategy)

> **Philosophy:** "Make it easy for Thai users to understand, while keeping technical accuracy."

## 1. Core Concept: TH+ENG (ภาษาไทยคำอังกฤษคำ)

The target audience is Thai PC users who are familiar with basic computer terms. 
- **Start with Thai**: The sentence structure, grammar, and explanations should be in Thai.
- **Use English for Techncial Terms**: Do *not* translate standard UI terms or technical jargon into obscure Thai words. Keep them in English.

### Why?
- **Clarity**: "Restore Driver" is clearer than "กู้คืนตัวขับเคลื่อนอุปกรณ์".
- **Consistency**: Windows itself uses these English terms often, or users learn them from tutorials.
- **Professionalism**: It looks more modern and tech-savvy.

---

## 2. Terminology Glossary (คำศัพท์ที่ควรใช้)

| Category | English Term (Keep as ENG) | **Do NOT Use (Classic Thai)** | **Correct Usage Example within Thai Sentence** |
| :--- | :--- | :--- | :--- |
| **Actions** | Backup | สำรองข้อมูล | "กรุณาสร้าง **Backup** ก่อนเริ่มใช้งาน" |
| | Restore | กู้คืน / ย้อนกลับ | "สามารถ **Restore** เพื่อกลับไปค่าเดิมได้" |
| | Optimize | ปรับปรุงประสิทธิภาพ | "คลิกเพื่อ **Optimize** ระบบของคุณ" |
| | Apply | นำไปใช้ / ตกลง | "กดปุ่ม **Apply** เพื่อเริ่มการตั้งค่า" |
| | Scan | สแกน / ตรวจสอบ | "กำลัง **Scan** ข้อมูลฮาร์ดแวร์..." |
| | Clean | ล้าง / ทำความสะอาด | "**Clean** ไฟล์ขยะออกจากระบบ" |
| | Tweaks | การปรับแต่ง | "รวม **Tweaks** ที่จำเป็นสำหรับเกมเมอร์" |
| **System** | Profile | รูปแบบ / โปรไฟล์ | "เลือก **Profile** ที่ต้องการใช้งาน" |
| | Performance | ประสิทธิภาพ | "เพิ่ม **Performance** ให้สูงสุด" |
| | Services | บริการ | "ปิด **Services** ที่ไม่จำเป็น" |
| | Registry | รีจิสทรี | "แก้ไขค่า **Registry** เพื่อลดความหน่วง" |
| | Latency | ความหน่วง | "ลดค่า **Latency** ของเมาส์และคีย์บอร์ด" |
| | Dashboard | แดชบอร์ด / แผงควบคุม | "กลับไปที่หน้า **Dashboard**" |

---

## 3. Explaining Features (การอธิบายฟีเจอร์)

Every feature must have a clear Thai explanation that explains **"What it does"** and **"Why it's good"**.

### Example 1: Safe Mode (โหมดปลอดภัย)
*   ❌ **Bad (Too Formal):** "โหมดนี้จะทำการคืนค่าการตั้งค่าทั้งหมดกลับสู่สถานะเริ่มต้นของโรงงานเพื่อความปลอดภัย"
*   ✅ **Good (TH+ENG):** "โหมด **Safe** จะคืนค่า Settings ทั้งหมดให้เป็นค่าเริ่มต้นของ Windows เหมาะสำหรับใช้เมื่อระบบมีปัญหา หรือต้องการยกเลิกการปรับแต่งทั้งหมด"

### Example 2: Gaming Profile (โหมดเกมมิ่ง)
*   ❌ **Bad:** "เพิ่มความเร็วในการประมวลผลสำหรับเกม"
*   ✅ **Good (TH+ENG):** "ปรับจูน Windows เพื่อการเล่นเกมโดยเฉพาะ ปิด Services ที่ไม่จำเป็น และลด Latency เพื่อให้ได้ FPS สูงสุด"

### Example 3: Debloat (ลบแอปขยะ)
*   ❌ **Bad:** "ลบโปรแกรมที่ติดตั้งมาพร้อมกับเครื่อง"
*   ✅ **Good (TH+ENG):** "ลบแอปขยะ (Bloatware) ที่แถมมากับ Windows ออก เพื่อประหยัดพื้นที่และลดการใช้ RAM"

---

## 4. Implementation Guide for Developers

We will use a Dictionary-based approach for localization in Python files (`src/gui/views/*.py`).

### Step 1: Define `UI_STRINGS` Class Variable
Add a dictionary to your View class:

```python
class DashboardView(ctk.CTkFrame):
    UI_STRINGS = {
        "en": {
            "title": "Dashboard",
            "score": "System Score",
            "rec_action": "Recommended Optimization",
            "apply_btn": "APPLY OPTIMIZATION"
        },
        "th": {
            "title": "Dashboard",
            "score": "คะแนนของระบบ",
            "rec_action": "การ Optimize ที่แนะนำ",  # TH+ENG style
            "apply_btn": "เริ่มการ OPTIMIZE"       # Clear Action
        }
    }
```

### Step 2: Helper Method
Ensure your class has the `_ui` helper method (or inherits it):

```python
    def _ui(self, key: str) -> str:
        lang = self.app.config.get("language", "en")
        return self.UI_STRINGS.get(lang, self.UI_STRINGS["en"]).get(key, key)
```

### Step 3: Replace Hardcoded Strings
Replace `"Dashboard"` with `self._ui("title")`.

```python
# Before
ctk.CTkLabel(self, text="Dashboard", ...)

# After
ctk.CTkLabel(self, text=self._ui("title"), ...)
```

---

## 5. Tone of Voice (น้ำเสียง)
- **Friendly but Expert**: เหมือนเพื่อนที่เก่งคอมพิวเตอร์แนะนำเพื่อน
- **Concise**: สั้น กระชับ ได้ใจความ ไม่เวิ่นเว้อ
- **Encouraging**: ให้ความมั่นใจว่าการปรับแต่งนี้ปลอดภัย (e.g., "ไม่ต้องกังวล เรามีระบบ Backup")

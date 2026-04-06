# Visual Audit Report — docs/diagrams/

> **ผู้ตรวจ:** Cascade
> **วันที่:** 2026-04-06
> **ขอบเขต:** PNG diagrams ใน `docs/diagrams/`
> **มุมมองที่ใช้ตรวจ:** visual hierarchy, readability, color consistency, whitespace, alignment, label clarity, export quality, thesis-readiness

---

## 1. Executive Summary

ภาพรวมของชุด diagram นี้ถือว่า **คุณภาพดีในระดับ thesis-ready draft** โดยมีจุดแข็งชัดเจนด้านการใช้สีอย่างสม่ำเสมอ, การจัดกลุ่มองค์ประกอบ, และการทำ legend ที่ช่วยให้ผู้อ่านเข้าใจได้เร็ว อย่างไรก็ตาม ยังมีประเด็น visual สำคัญที่ควรแก้ก่อนใช้ในเล่มวิทยานิพนธ์/เอกสารส่งอาจารย์ ได้แก่

- **ความคมชัดและการอ่านตัวอักษรของ diagram ใหญ่** โดยเฉพาะ Class Diagram
- **ความสม่ำเสมอของ title/subtitle naming** บางภาพมี prefix `Diagram X:` บางภาพไม่มี
- **การ render HTML entities ผิด** ในบาง diagram ทำให้ภาพดูไม่ professional
- **ความหนาแน่นของข้อมูล** บางภาพแน่นเกินไปเมื่อดูในขนาดหน้ากระดาษจริง

---

## 2. Visual Score Summary

| เกณฑ์ | คะแนน (1-5) | หมายเหตุ |
|-------|-------------|---------|
| **Visual Consistency** | 4/5 | สี, เส้น, legend, rounded boxes ค่อนข้างสม่ำเสมอ |
| **Readability** | 3/5 | ส่วนใหญ่ดี แต่บางภาพ text เล็กเกิน โดยเฉพาะ diagram 08 |
| **Hierarchy** | 4/5 | ลำดับชั้นของข้อมูลชัดในเกือบทุกภาพ |
| **Layout & Spacing** | 4/5 | spacing ค่อนข้างสะอาด มี white space ดี |
| **Export Quality** | 3/5 | PNG บางภาพคมดี บางภาพถูกย่อจนอ่านยาก |
| **Thesis Presentation Quality** | 4/5 | พร้อมใช้ได้หลายภาพ แต่ควร polish อีกเล็กน้อย |
| **รวม** | **22/30** | **Good — ควรเก็บงาน visual อีก 1 รอบ** |

---

## 3. System-Level Visual Findings

### จุดแข็งของทั้งชุด

- **Color system ชัดเจน**
  - ฟ้า = presentation/info
  - เขียว = business/design/positive flow
  - ส้ม = execution/implementation
  - แดง = risk/error/security
  - ม่วง = documentation/validation/utility
- **ใช้ rounded rectangles สม่ำเสมอ** ทำให้ชุดภาพดูเป็น family เดียวกัน
- **legend มีหลายภาพ** ช่วยลด ambiguity
- **titles ใหญ่ อ่านง่าย** และภาพส่วนใหญ่มี subtitle ช่วยอธิบาย context
- **white background + pastel palette** เหมาะกับงานวิชาการมากกว่า dark diagram style

### ปัญหาระดับระบบ

- **Typography scale ยังไม่คงที่**
  - บางภาพ title ใหญ่และ subtitle พอดี
  - บางภาพ body text เล็กเกินเมื่อ export PNG
- **Naming style ไม่สม่ำเสมอ**
  - บางภาพใช้ `Diagram X:`
  - บางภาพใช้แค่ชื่อ เช่น `GUI Navigation Flow`, `Tweak State Diagram`
- **Stroke weight และ arrow emphasis ไม่เท่ากันบางภาพ**
  - บางภาพ flow ชัดมาก
  - บางภาพลูกศรบางจน hierarchy ของ path ไม่เด่น
- **Connector routing ยังไม่คงที่**
  - บางภาพเส้นตัดกันหรือไปซ้อนกันบริเวณ node กลาง
  - บางภาพมีหลายเส้น converge จุดเดียวจนอ่านลำดับ flow ยาก
- **Canvas size/export scale ไม่สม่ำเสมอ**
  - หลายภาพอ่านง่ายทันที
  - บางภาพเมื่อเปิดใน IDE แล้ว text เล็กมาก

---

## 3.1 Line / Connector Audit

### ภาพรวม

- **เส้นส่วนใหญ่ใช้ได้ดี** ในภาพที่เป็น linear flow หรือ layered flow เช่น Diagram 01, 04, 11, 13
- ปัญหาหลักเกิดในภาพที่มี **many-to-one connections**, **system boundary ใหญ่**, หรือ **หลาย semantic line styles อยู่ร่วมกัน**
- ประเด็นที่พบมี 4 แบบหลัก
  - **Line crossing** — เส้นตัดกันโดยไม่ช่วยความเข้าใจ
  - **Line overlap** — เส้นวิ่งทับ/ชิดกันมากจนเหมือนเป็นเส้นเดียว
  - **Congested hub** — หลายเส้นไหลเข้าจุดเดียวกันจน node กลางแน่นเกิน
  - **Weak hierarchy** — เส้นสำคัญกับเส้นรองน้ำหนักใกล้กันเกินไป

### ภาพที่มีปัญหาชัด

| Diagram | ปัญหาเส้น | ระดับ |
|--------|-----------|-------|
| **02** | บริเวณ merge node กลางภาพและเส้น return loop ด้านซ้ายเริ่มแน่น | Medium |
| **06** | หลายเส้น converge แถว `GUI Infrastructure`, `leaf modules`, `tweak_registry` | Medium |
| **07** | actor association lines จากฝั่ง `User` ซ้อนและตัดกันมากที่สุดในชุด | High |
| **09** | loop frame, callback line, return line, opt fragment วางใกล้กันมากช่วงกึ่งกลางล่าง | Medium |
| **10** | เส้นไม่ใช่ปัญหาหลัก แต่ arrow weight บางบางเส้นยังไม่เสถียร | Low |

### ภาพที่เส้นจัดการได้ดี

| Diagram | จุดเด่น |
|--------|---------|
| **01** | vertical layer arrows ตรงและไม่ตัดกัน |
| **04** | linear lifecycle flow ชัด, rollback line เด่นแต่ไม่รก |
| **11** | conceptual connectors คุม spacing ดี |
| **13** | state transitions อ่านง่าย, rollback line แยกตัวชัด |

### แนวทางแก้เชิง visual

- **เลี่ยงการให้หลายเส้นจบที่ edge จุดเดียวกัน**
  - ขยับ anchor point ให้คนละระดับ
- **ใช้ orthogonal routing ให้มากขึ้น**
  - โดยเฉพาะ use case และ dependency diagrams
- **แยกเส้นหลักกับเส้นรองด้วยน้ำหนักเส้น**
  - main flow หนากว่า
  - callback / include / lazy import บางกว่า แต่ยังมองเห็นได้
- **หลีกเลี่ยงการวาง label บนทางแยกของเส้น**
  - label ควรอยู่บน segment ที่โล่ง
- **ถ้าหลีกเลี่ยง crossing ไม่ได้ ให้จัด crossing angle ชัดเจน**
  - ตัดกัน 90° ดีกว่าตัดเฉียงชิดๆ

---

## 4. Per-Diagram Visual Audit

## Diagram 01 — System Architecture Overview

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดีมาก |
| Readability | ดี |
| Layout | ดีมาก |
| Color | ดีมาก |

### Findings

- **แข็งแรงมากเรื่อง hierarchy** — layer stack จากบนลงล่างชัดเจน
- **alignment ดี** กล่องแต่ละ layer จัดแบบกึ่ง-grid ทำให้อ่านง่าย
- **subtitle ไม่แย่ง title** ใช้ขนาดพอดี
- **legend วางล่างสุดเหมาะสม** และไม่รบกวนเนื้อหา
- **จุดที่ควรปรับ** คือ box spacing ด้านในบางกล่องยังเหลือพื้นที่ไม่เท่ากัน แต่เป็น minor issue

### Verdict

- **Visual: PASS**
- **พร้อมใช้ใน thesis ได้ทันที**

---

## Diagram 02 — Batch Optimizer Execution Flow

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดี |
| Readability | ดี |
| Layout | ดี |
| Flow Clarity | ดีมาก |

### Findings

- **flow จากบนลงล่างชัดเจน** เหมาะกับ activity diagram
- ใช้ **decision diamonds + branch colors** ได้ดี
- **เส้น dashed area return to main menu** ทำให้เข้าใจ loop behavior ได้
- อย่างไรก็ตาม **diagram มีความสูงมาก** ทำให้เมื่อย่อดูทั้งภาพ ตัวหนังสือช่วงกลาง-ล่างเริ่มเล็ก
- callout ด้านขวา (`TWEAK_FLAG=...`) มีประโยชน์ แต่ **visual weight เบาไปนิด** เมื่อเทียบกับกล่องหลัก
- บริเวณ **merge node ก่อนเข้าสู่ขั้น backup/apply** มีเส้นหลายทิศมาชนกันค่อนข้างแน่น ทำให้จุดเปลี่ยน flow ต้องเพ่งเล็กน้อย

### Verdict

- **Visual: PASS**
- ถ้าจะใช้ในเล่ม แนะนำ export ความละเอียดสูงขึ้นอีกเล็กน้อย และคลายความแน่นของเส้นรอบ merge node

---

## Diagram 03 — GUI Navigation Flow

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดี |
| Readability | ดีมาก |
| Layout | ดีมาก |
| Balance | ดี |

### Findings

- เป็นหนึ่งในภาพที่ **อ่านง่ายที่สุด**
- left-to-right entry flow (`main.py` → `App Controller` → views) ชัดเจน
- กล่อง 7 views วางเป็นแถวเดียว ทำให้สแกนได้เร็ว
- **negative space ดี** ภาพไม่แน่นเกิน
- กล่อง `Theme + Style + Icons + Fonts` และ shared components ทำหน้าที่เป็น support blocks ได้ดี
- หากจะ polish เพิ่ม อาจทำให้ **arrow labels สีสอดคล้องกับ target layer มากขึ้น**

### Verdict

- **Visual: PASS**
- พร้อมใช้งานมาก

---

## Diagram 04 — Tweak Lifecycle

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดีมาก |
| Readability | ดีมาก |
| Layout | ดีมาก |
| Narrative Flow | ดีมาก |

### Findings

- ภาพนี้ **เล่าเรื่องได้ดีมาก** เพราะใช้ linear timeline ซ้ายไปขวา
- กล่องแต่ละ phase spacing สวย อ่านง่าย
- dashed red rollback arrow ด้านล่างช่วยดึง attention ได้เหมาะสม
- lower legend strip เรื่อง risk levels ใช้ได้ดีและไม่แย่ง focus
- เป็นภาพที่ **เหมาะกับบทอธิบาย methodology/process มาก**

### Verdict

- **Visual: STRONG PASS**
- หนึ่งในภาพที่ดีที่สุดของชุดนี้

---

## Diagram 05 — Risk Classification Framework

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดี |
| Readability | ดี |
| Color semantics | ดีมาก |
| Professional finish | ปานกลาง |

### Findings

- การใช้สี **เขียว/ส้ม/แดง** ตรงกับ semantic meaning ดีมาก
- decision tree แนวตั้งอ่านง่าย
- terminal boxes (`REJECTED`, `LOW Risk`, `MEDIUM Risk`, `HIGH Risk`) เด่นพอดี
- แต่มี **render bug ของข้อความ `&amp;`** ซึ่งกระทบความ professional ของภาพโดยตรง
- footnote ด้านล่างตัวเอียงดี แต่จางไปนิดเมื่อดูย่อ

### Verdict

- **Visual: WARN**
- ถ้าแก้ entity bug จะดีขึ้นทันทีมาก

---

## Diagram 06 — Module Dependency Map

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดี |
| Readability | ดี |
| Network clarity | ดี |
| Density | ปานกลาง |

### Findings

- ใช้ line styles หลายแบบแล้ว **ยังคุมภาพไม่เละ** ถือว่าดี
- `profile_manager (HUB)` และ `tweak_registry (ROOT)` เด่นพอเหมาะ
- กลุ่ม leaf modules เป็น long horizontal box ช่วยลด clutter
- อย่างไรก็ตาม dependency diagram ลักษณะนี้มี **cognitive load สูงกว่าภาพอื่น** ตามธรรมชาติ
- เส้น dashed/dotted บางเส้นค่อนข้างอ่อน ถ้าพิมพ์ขาวดำอาจหาย
- จุดที่ควรระวังคือบริเวณ **GUI Infrastructure → tweak_registry** และ **leaf modules** มีเส้นวิ่งเข้าใกล้กันหลายชุด ทำให้ distinction ระหว่าง direct/lazy/type-checking ลดลงเมื่อมองไกลๆ

### Verdict

- **Visual: PASS**
- แนะนำเพิ่ม contrast ของ dashed/dotted lines ถ้าจะพิมพ์ และแยก anchor ของเส้นที่ converge กัน

---

## Diagram 07 — Use Case Diagram

| ด้าน | ประเมิน |
|------|--------|
| Readability | ดี |
| UML legibility | ดี |
| Balance | ปานกลาง |
| Composition | ปานกลาง |

### Findings

- use cases มีสีแยก category ดี
- actors ซ้าย-ขวาชัดเจน
- แต่ **left-heavy มาก** เพราะ use cases วางกองทางซ้าย ขณะที่ฝั่งขวาค่อนข้างโล่ง
- system boundary ใหญ่เกิน content จริง ทำให้ด้านล่างและขวาดู empty
- เส้น association จำนวนมากจาก actor ฝั่งซ้ายทำให้ visual noise สูง
- ภาพยังใช้งานได้ แต่ **ยังไม่ elegant เท่าภาพอื่น**
- เป็นภาพที่ **ปัญหาเส้นชัดที่สุด** เพราะ actor `User` เชื่อมหลาย use cases จากจุดเดียว ทำให้เส้นซ้อนกันและมี crossing โดยไม่สร้างความหมายเพิ่ม

### Verdict

- **Visual: WARN**
- ถ้าจัดกลุ่ม use cases เป็น 2-3 clusters และกระจาย anchor ของ actor associations จะสวยและอ่านง่ายขึ้นมาก

---

## Diagram 08 — Class Diagram

| ด้าน | ประเมิน |
|------|--------|
| Information richness | ดีมาก |
| Readability | ต่ำ |
| Export quality | ต่ำ |
| Thesis usability | ปานกลาง |

### Findings

- เนื้อหาดีและครบมาก แต่ **ภาพแน่นเกิน + ตัวหนังสือเล็กเกิน**
- เมื่อดูจาก PNG ใน IDE แล้ว class names และ attributes จำนวนมากอ่านลำบาก
- ปัญหานี้ไม่ใช่ design structure แต่เป็น **export/readability problem**
- line colors และ grouping ดีอยู่แล้ว แต่ประโยชน์ลดลงเพราะต้อง zoom มาก
- ใน thesis จริง หากแปะเต็มหน้า A4 ก็มีโอกาสยังอ่านยาก

### Verdict

- **Visual: FAIL-ish / High WARN**
- ควรแก้โดย
  - export scale ใหญ่ขึ้นมาก
  - หรือแยกเป็น `08a-controller-core-class-diagram` และ `08b-dataclass-diagram`
  - หรือทำ version simplified สำหรับเล่ม และ full version ไว้ appendix

---

## Diagram 08a — Class Diagram (Simplified)

| ด้าน | ประเมิน |
|------|--------|
| Readability | ดี |
| A4 suitability | ดีมาก |
| Layout | ดี |
| Connector clarity | ปานกลาง |

### Findings

- การ split จาก Diagram 08 เดิมช่วยให้ภาพ **อ่านได้จริงในระดับ thesis body**
- hierarchy ระหว่าง `Controller` กับ `Core Business Logic` ชัดเจน
- note block ที่อ้างไป Diagram 8b ทำหน้าที่ดี ช่วยลดความแน่นของภาพหลัก
- class boxes มีขนาดพอดีขึ้นและไม่แน่นเกินเหมือนภาพเดิม
- จุดที่ยังต้องระวังคือ **เส้นจาก `ClutchGApp` ลงหลาย core modules** และเส้นรอบ `ProfileManager / TweakRegistry / BatchExecutor` ยังแน่นเล็กน้อย

### Verdict

- **Visual: PASS**
- เหมาะใช้เป็นภาพหลักในบทมากกว่า Diagram 08 เดิมอย่างชัดเจน

---

## Diagram 08b — Class Diagram — Data Models

| ด้าน | ประเมิน |
|------|--------|
| Readability | ปานกลาง |
| A4 suitability | ปานกลาง |
| Information density | สูง |
| Connector clarity | ปานกลาง |

### Findings

- เป็นการแยก domain/data detail ออกมาที่ **ถูกทางมาก**
- กลุ่ม dataclass หลักและ enum ถูกจัดวางเป็นโซนซ้าย-ขวา อ่าน logic ได้ดี
- legend ช่วยอธิบาย relation แบบ `contains` และ `uses` ได้ชัด
- อย่างไรก็ตาม field list ของ `Tweak`, `TweakChange`, `ActionDefinition` ยังเยอะพอที่จะทำให้ภาพแน่นเมื่อย่อใส่ A4
- เส้น dashed ไป enums ทางขวาวิ่งอ้อมค่อนข้างเยอะ จึงเริ่มมี visual clutter บริเวณขอบขวา

### Verdict

- **Visual: PASS / WARN**
- เหมาะมากสำหรับ appendix มากกว่าการเป็นภาพหลักใน body chapter

---

## Diagram 09 — Sequence Diagram

| ด้าน | ประเมิน |
|------|--------|
| Flow readability | ดี |
| UML clarity | ดีมาก |
| Spacing | ดี |
| Detail level | ดี |

### Findings

- sequence direction ชัดเจนมาก
- activation bars, loop, opt fragment ดูเป็นระบบ
- message numbering ช่วยให้อธิบายในเอกสารได้ง่าย
- สีของ participant headers ช่วยแยก role ได้ดี
- บาง return labels เล็กไปนิด แต่ยังอยู่ในเกณฑ์ดี
- ช่วงกลางล่างของภาพมี **loop fragment, callback progress line, และ opt fragment** อยู่ใกล้กัน ทำให้บาง segment ดูเบียดกัน แม้ยังไม่ถึงขั้นอ่านไม่ออก

### Verdict

- **Visual: PASS**
- ใช้ในรายงานหรือ thesis ได้ดี แต่ควรขยับ fragment spacing อีกเล็กน้อยถ้าจะ polish รอบสุดท้าย

---

## Diagram 10 — Deployment Diagram

| ด้าน | ประเมิน |
|------|--------|
| Layout | ดี |
| Readability | ดี |
| Professional finish | ต่ำ |
| Semantics | ดี |

### Findings

- โครงสร้าง visual ดี: install folder, appdata, system targets ถูกจัด zone ชัดเจน
- สีแยก node types ดีและเข้าใจเร็ว
- build process note box วางตำแหน่งดี
- แต่ **HTML render bug รุนแรงทางสายตา** เพราะ node stereotype แสดงเป็น literal text เช่น `<b>&laquo;device&raquo;...` ทำให้ภาพดูเหมือน export พัง
- แม้เนื้อหาถูก แต่ **visual credibility ลดลงทันที**

### Verdict

- **Visual: FAIL**
- ควรแก้ก่อนใช้งานจริงแน่นอน

---

## Diagram 11 — Conceptual Framework

| ด้าน | ประเมิน |
|------|--------|
| Hierarchy | ดีมาก |
| Readability | ดีมาก |
| Balance | ดีมาก |
| Thesis suitability | ดีมาก |

### Findings

- เป็นภาพที่เหมาะกับงานวิทยานิพนธ์มากที่สุดภาพหนึ่ง
- top-down conceptual layering ทำได้ดี
- กล่องแต่ละระดับมี spacing และ balance ดี
- center block `ClutchG PC Optimizer` ทำหน้าที่เป็น visual anchor ดีมาก
- expected outcomes ด้านล่างจัดสมดุลสวย
- เส้น dashed relation ไม่รกเกินไป

### Verdict

- **Visual: STRONG PASS**
- เหมาะมากสำหรับบทแนวคิดหรือกรอบแนวคิดการวิจัย

---

## Diagram 12 — Gantt Chart

| ด้าน | ประเมิน |
|------|--------|
| Readability | ดี |
| Color usage | ดี |
| Hierarchy | ดี |
| Presentation trustworthiness | ปานกลาง |

### Findings

- visual style สะอาด อ่านง่าย
- timeline bar colors ชัดและสอดคล้องกับ legend
- row grouping ดี
- milestone diamonds เด่นพอเหมาะ
- ในเชิงภาพถือว่า **ดู professional** แต่ปัญหาหลักคือ **content-timeline ไม่ตรง reality** ซึ่งกระทบ credibility มากกว่า visual craft
- หากมอง purely visual อย่างเดียวถือว่าดี แต่ในงาน thesis visual ที่สวยแต่ข้อมูลไม่ตรงถือว่าต้องแก้

### Verdict

- **Visual: PASS / Content-Credibility FAIL**
- แนะนำแก้ทั้งข้อมูลและ export ใหม่

---

## Diagram 13 — Tweak State Diagram

| ด้าน | ประเมิน |
|------|--------|
| Readability | ดีมาก |
| Flow clarity | ดีมาก |
| Visual balance | ดี |
| Simplicity | ดีมาก |

### Findings

- ภาพนี้อ่านง่ายมากและมี state semantics ชัดเจน
- สีแต่ละ state ให้ความหมายได้ดี
- transition labels อ่านได้สบาย
- spacing รอบ states ดี ไม่แน่น
- rollback transition สีม่วงช่วยดึงสายตาอย่างเหมาะสม

### Verdict

- **Visual: PASS**
- ใช้ประกอบอธิบาย lifecycle/stateful behavior ได้ดีมาก

---

## 5. Priority Fix List

## P1 — ควรแก้ทันที

- **Diagram 10**
  - แก้ HTML render bug ของ stereotypes
- **Diagram 08**
  - เพิ่ม readability โดย re-export หรือแยกภาพ
- **Diagram 05**
  - แก้ entity bug ในข้อความ decision node
- **Diagram 07**
  - ลดเส้นซ้อนจาก actor `User` โดยจัด clusters หรือแยก actors/anchor points

## P2 — ควรปรับก่อนส่ง thesis

- **Diagram 02, 06, 09**
  - จัด route ของเส้นใหม่เพื่อลด convergence และ crossing
- **Diagram 12**
  - แก้ timeline ให้ตรงกับ project จริง แล้ว export ใหม่
- **Diagram 01, 03**
  - ทำ naming และ count ให้ consistent กับทั้ง repository

## P3 — polishing รอบสุดท้าย

- ทำ **title convention** ให้เหมือนกันทุกภาพ
- ปรับ **font sizes ขั้นต่ำ** สำหรับ body text ให้คงที่
- export PNG ใหม่ด้วย **higher resolution / scale** ให้สม่ำเสมอ
- ตรวจภาพทั้งหมดในขนาด A4 print preview

---

## 6. Recommended Visual Standards

เพื่อให้ชุด diagram ดูเป็นระบบเดียวกันมากขึ้น แนะนำมาตรฐานดังนี้

### Typography

- **Title:** 18–20 pt
- **Subtitle:** 10–11 pt
- **Node title:** 12–13 pt
- **Body text:** อย่างน้อย 10–11 pt หลัง export จริง
- **Legend text:** 9–10 pt

### Layout

- margin รอบ canvas อย่างน้อย 24–32 px
- spacing ระหว่าง major groups อย่างน้อย 20–24 px
- หลีกเลี่ยงกล่องที่กว้างมากแต่ข้อความน้อย
- หลีกเลี่ยง giant system boundary ที่มี empty space เยอะ

### Connectors

- ใช้ **orthogonal connectors** เป็น default ใน diagram ที่มีหลายความสัมพันธ์
- แยก **main flow** กับ **secondary flow** ด้วย stroke weight และ dash pattern
- หลีกเลี่ยงการให้เส้นมากกว่า 3 เส้น converge ที่ node edge จุดเดียว
- ถ้าต้อง crossing ให้ตัดกันแบบชัดเจน ไม่วิ่งเฉียดขนานกันใกล้ๆ
- label ของเส้นควรวางบน segment ที่โล่ง ไม่ทับกับ fragment box หรือ arrow head

### Export

- export PNG ที่ **scale 2x หรือ 3x** สำหรับภาพที่มี text เยอะ
- ภาพใหญ่มากควรมี
  - **summary version** สำหรับ body chapter
  - **full detail version** สำหรับ appendix

### Consistency

- ใช้ prefix naming แบบเดียวกันทั้งหมด เช่น `Diagram X: ...`
- ใช้ palette เดิมทั้งชุด
- ใช้ stroke thickness คงที่สำหรับ node borders และ arrows

---

## 7. Final Verdict

ชุดภาพ `docs/diagrams/` มีพื้นฐาน visual ที่ดีมากและสะท้อนว่ามีการออกแบบอย่างตั้งใจ ไม่ใช่ diagram แบบโยนข้อมูลใส่ภาพเฉยๆ จุดแข็งที่สุดคือ **color semantics, structural clarity, และ thesis-friendly white background**

อย่างไรก็ตาม ถ้าจะยกระดับจาก **good draft** ไปเป็น **final thesis quality** ควรเก็บงานอีกรอบใน 3 เรื่องหลัก:

- **แก้ render bugs**
- **เพิ่ม readability ของภาพใหญ่**
- **ทำ consistency ของ naming / export scale / typography**
- **จัด route ของเส้นในภาพที่มี many-to-one relationships**

ถ้าแก้ 4 เรื่องนี้ ชุดภาพจะขึ้นไปอยู่ระดับ **พร้อมส่งอาจารย์และพร้อมใช้ในเล่มฉบับ final** ได้สบาย

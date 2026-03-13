# Extension Research – Synthesis & Actionable Plan
วันที่: 2 กุมภาพันธ์ 2026
แหล่งข้อมูล: Ideas and research\research.md

## วัตถุประสงค์
สรุปและจัดระเบียบข้อเสนอจาก research.md ให้ใช้งานได้จริง โดยคงหลักการ:
- Safety-first (ไม่แตะ Defender/UAC/DEP/ASLR/CFG/Windows Update)
- Evidence-based (หลีกเลี่ยง placebo/ล้าสมัย)
- Reversible + Transparent (ย้อนกลับได้และอธิบายได้)
- ไม่ over‑engineer (เพิ่มเฉพาะสิ่งที่คุ้มค่า)

---

## ภาพรวม (Executive Summary แบบย่อ)
- โครงการมีพื้นฐานแข็งแรง: งานวิจัยครบ, แยกโมดูล, มีโปรไฟล์ SAFE/COMPETITIVE/EXTREME, มีระบบ Backup/Restore และ Logging
- ความเชื่อมั่นของผู้ใช้คือ “ตัวชี้วัด” สำคัญที่สุด จึงต้องเน้นความโปร่งใสและความย้อนกลับได้
- แนวโน้มตลาด: ผู้ใช้ต้องการ “เครื่องมือช่วยควบคุมแบบอธิบายได้” ไม่ใช่ “ตัวเร่งที่เป็นกล่องดำ”

---

## แนวทางต่อยอด (จัดกลุ่มตาม Impact/Effort/Risk)

### 1) Quick Wins (High Impact, Low Effort)
สิ่งที่ทำได้เร็วและให้ผลกับผู้ใช้ทันที
- **Dry‑Run / Preview Changes**: แสดงรายการ tweak ที่จะถูกปรับก่อนกด Apply
- **Before/After Summary**: สรุปสิ่งที่เปลี่ยนไปหลัง Apply (ลดความกลัว)
- **Recent Activity Panel**: แสดงโปรไฟล์ล่าสุด, เวลา backup ล่าสุด, log ล่าสุด
- **Log Viewer (Read‑Only)**: เปิดอ่าน log จาก UI ได้ทันที
- **Contextual Help/Tooltip**: ปุ่ม “What this does” อธิบายผลกระทบรายจุด

> หมายเหตุ: บาง tweak ที่ถูกเสนอใน research.md (เช่น NetworkThrottlingIndex, SystemResponsiveness) ต้องถูกจัดเป็น **Advanced/Opt‑in** เท่านั้น และผ่านการ audit ก่อนนำเข้าค่าเริ่มต้น

### 2) Strategic Investments (High Impact, Medium/High Effort)
- **GUI ที่โปร่งใส**: ใช้ ClutchG เป็นตัวควบคุมหลัก พร้อม risk tags
- **ย้ายบางโมดูลไป PowerShell**: เพิ่มความยืดหยุ่น, error handling, linting, CI
- **Benchmark Suite (Optional)**: ก่อน/หลังการปรับ พร้อมรายงานสรุป
- **Community Profiles (Curated)**: แชร์โปรไฟล์ได้ แต่ต้องมีการรีวิว
- **Opt‑in Telemetry**: รวบรวมข้อมูลเชิงเทคนิคแบบไม่ระบุตัวตน เพื่อปรับปรุงคุณภาพ

### 3) Research Opportunities (เชิงวิชาการ/นวัตกรรม)
- **Safety Classification Framework**: ระบบให้เกรด “ความเสี่ยงของสคริปต์” อัตโนมัติ
- **Windows 11 24H2/AI Features**: วิเคราะห์ผลกระทบ Copilot/NPU, HAGS
- **Cross‑OS Study**: เปรียบเทียบแนวคิด optimization ระหว่าง Windows/Linux/macOS
- **เผยแพร่เชิงวิชาการ**: ทำเป็นเอกสารวิจัย/บทความที่มี methodology ชัด

### 4) Moonshots (High Risk/High Reward)
- **AI‑assisted Dynamic Tuning**: ปรับโปรไฟล์ตาม workload แบบ real‑time
- **Crowdsourced Performance DB**: เก็บผลการ tweak จากผู้ใช้เพื่อสรุปผลจริง

---

## “Do NOT Do” (ย้ำห้ามทำ)
- ปิด Windows Defender / Windows Update / UAC / DEP / ASLR / CFG
- Registry Cleaner หรือ tweak แบบ “ล้าง registry”
- Tweak ที่พิสูจน์ว่าเป็น placebo (เว้นแต่ทำเป็น Advanced/Experimental)
- ปิดบริการที่กระทบ core functionality โดยไม่มี warning และ opt‑in

---

## แนวทาง Validation (แนะนำการทดสอบ)
- **Benchmark A/B**: ก่อน/หลัง tweak อย่างน้อย 3 รอบ
- **Latency/DPC Monitoring**: ใช้ LatencyMon ในกลุ่มผู้ใช้ทดลอง
- **Rollback Test**: ตรวจว่าย้อนกลับได้ทุกครั้ง
- **Help Accuracy Test**: ตรวจว่าข้อความอธิบายตรงกับสิ่งที่โค้ดทำจริง

---

## Roadmap สั้น (Phase 10–12 จาก research.md)

### Phase 10: Safety Foundation
- Pre‑flight checks (pending reboot, restore point, backup success)
- Dry‑Run + Before/After Summary
- Help/Tooltip ครอบคลุม tweak สำคัญ

### Phase 11: Performance & Transparency
- Benchmark module แบบเบา (optional)
- Expert Mode + Advanced tweaks (opt‑in)
- เพิ่ม help search + FAQ

### Phase 12: Ecosystem & Advanced
- Profile‑as‑Code + Import/Export
- Community profile (curated)
- พิจารณา AI/Automation ระยะยาว

---

## Checklist ก่อนนำไปใช้จริง
- [ ] Tweak audit: จับคู่กับ docs/03, docs/04, docs/06
- [ ] ตัด tweak ที่ขัดกับ evidence หรือย้ายไป Advanced
- [ ] ทดสอบบน Win10 22H2 และ Win11 23H2/24H2
- [ ] Sync เอกสาร/Help ให้ตรงกับโค้ด

---

## สรุป
เอกสารต้นฉบับมีแนวคิดครบมาก แต่เพื่อ “ไม่ over‑engineer” ควรเริ่มจาก:
1) ความโปร่งใส + ความปลอดภัย + การย้อนกลับได้
2) ปรับโปรไฟล์ให้สอดคล้องกับงานวิจัยหลัก
3) ค่อยเพิ่มฟีเจอร์วัดผลและ community เมื่อระบบนิ่งแล้ว

เอกสารนี้สรุปเฉพาะส่วนที่นำไปใช้ได้จริงและสอดคล้องกับแนวทางความปลอดภัยของโครงการ

# ClutchG Testing Checklist
**ชีตกรอกการทดสอบ ClutchG**

> **Version:** 1.0
> **Date:** 6 February 2026
> **Tester:** ___________________
> **Test Date:** ___________________
> **Build Version:** ___________________

---

## 📋 Instructions (วิธีใช้)

1. ทำเครื่องหมาย ☑️ ใน checkbox เมื่อทดสอบผ่าน
2. เขียนหมายเหตุถ้าพบปัญหา
3. ระบุ severity ของ bugs ที่พบ (Critical/High/Medium/Low)
4. แนบ screenshots/logs เมื่อจำเป็น

---

## 🎯 Overall Progress

| Category | Total | Passed | Failed | Skipped |
|----------|-------|--------|--------|---------|
| Installation & First Run | 5 | 0 | 0 | 0 |
| Dashboard | 3 | 0 | 0 | 0 |
| Profiles | 8 | 0 | 0 | 0 |
| Scripts | 4 | 0 | 0 | 0 |
| Backup & Restore (Simple) | 6 | 0 | 0 | 0 |
| Backup & Restore (Advanced) | 7 | 0 | 0 | 0 |
| Help | 4 | 0 | 0 | 0 |
| Settings | 4 | 0 | 0 | 0 |
| Navigation | 4 | 0 | 0 | 0 |
| Error Scenarios | 5 | 0 | 0 | 0 |
| Performance | 5 | 0 | 0 | 0 |
| **TOTAL** | **55** | **0** | **0** | **0** |

---

## 1️⃣ Installation & First Run (5 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 1.1 | Install Python dependencies ครบถ้วน | ☐ | | |
| 1.2 | Run app ครั้งแรก ไม่ crash | ☐ | | |
| 1.3 | Welcome overlay แสดงผล | ☐ | | |
| 1.4 | Next/Back buttons ทำงาน | ☐ | | |
| 1.5 | Skip tutorial ได้ | ☐ | | |

**Bugs Found:**
-

---

## 2️⃣ Dashboard View (3 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 2.1 | System detection ทำงาน (CPU/GPU/RAM) | ☐ | | |
| 2.2 | Performance score คำนวณได้ | ☐ | | |
| 2.3 | Refresh button ทำงาน | ☐ | | |

**Bugs Found:**
-

---

## 3️⃣ Profiles View (8 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 3.1 | 3 profile cards แสดง (SAFE/COMPETITIVE/EXTREME) | ☐ | | |
| 3.2 | Icons แสดงถูกต้อง | ☐ | | |
| 3.3 | Apply SAFE profile สำเร็จ | ☐ | | |
| 3.4 | Apply COMPETITIVE profile สำเร็จ | ☐ | | |
| 3.5 | Apply EXTREME มี warnings แสดง | ☐ | | |
| 3.6 | Cancel EXTREME warning ไม่ apply | ☐ | | |
| 3.7 | Confirm EXTREME warning apply สำเร็จ | ☐ | | |
| 3.8 | Apply failed แสดง error message | ☐ | | |

**Bugs Found:**
-

---

## 4️⃣ Scripts View (4 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 4.1 | Scripts list แสดงใน grid | ☐ | | |
| 4.2 | Icons แสดงตาม risk level | ☐ | | |
| 4.3 | Search filter ทำงาน | ☐ | | |
| 4.4 | Run script สำเร็จ | ☐ | | |

**Bugs Found:**
-

---

## 5️⃣ Backup & Restore Center - Simple Mode (6 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 5.1 | เปิดมาที่ Simple mode เป็น default | ☐ | | |
| 5.2 | Create backup สำเร็จ | ☐ | | |
| 5.3 | Backup แสดงใน list | ☐ | | |
| 5.4 | Restore from backup สำเร็จ | ☐ | | |
| 5.5 | Delete backup สำเร็จ | ☐ | | |
| 5.6 | Toast notifications แสดง | ☐ | | |

**Bugs Found:**
-

---

## 6️⃣ Backup & Restore Center - Advanced Mode (7 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 6.1 | Switch to Advanced mode | ☐ | | |
| 6.2 | Timeline แสดงแนวนอน | ☐ | | |
| 6.3 | Filter timeline by type | ☐ | | |
| 6.4 | Click timeline item | ☐ | | |
| 6.5 | Details panel แสดง | ☐ | | |
| 6.6 | Undo tweak สำเร็จ | ☐ | | |
| 6.7 | Switch back to Simple mode | ☐ | | |

**Bugs Found:**
-

---

## 7️⃣ Help View (4 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 7.1 | Help categories แสดงทั้งหมด | ☐ | | |
| 7.2 | Search help ทำงาน | ☐ | | |
| 7.3 | Click help item แสดง content | ☐ | | |
| 7.4 | Myth-busting section แสดง icons ถูกต้อง | ☐ | | |

**Bugs Found:**
-

---

## 8️⃣ Settings View (4 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 8.1 | Switch language TH → EN | ☐ | | |
| 8.2 | Switch language EN → TH | ☐ | | |
| 8.3 | Switch theme Dark → Light | ☐ | | |
| 8.4 | Change accent color | ☐ | | |

**Bugs Found:**
-

---

## 9️⃣ Navigation (4 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 9.1 | คลิก Dashboard → ไปหน้า Dashboard | ☐ | | |
| 9.2 | คลิก Profiles → ไปหน้า Profiles | ☐ | | |
| 9.3 | คลิก Scripts → ไปหน้า Scripts | ☐ | | |
| 9.4 | Active state highlighting | ☐ | | |

**Bugs Found:**
-

---

## 🔟 Error Scenarios (5 tests)

| # | Test Case | Status | Notes | Bugs |
|---|-----------|--------|-------|------|
| 10.1 | ไม่มี admin rights - แสดง warning | ☐ | | |
| 10.2 | Disk full - แสดง error | ☐ | | |
| 10.3 | Registry access denied - แสดง error | ☐ | | |
| 10.4 | Profile apply failed - แสดง partial success | ☐ | | |
| 10.5 | Network error - handle gracefully | ☐ | | |

**Bugs Found:**
-

---

## 1️⃣1️⃣ Performance (5 tests)

| # | Test Case | Expected | Actual | Status | Notes |
|---|-----------|----------|--------|--------|-------|
| 11.1 | Load 100 backups | < 2s | ___s | ☐ | |
| 11.2 | Export large registry | < 30s | ___s | ☐ | |
| 11.3 | Memory after 100 switches | < 50MB increase | ___MB | ☐ | |
| 11.4 | App startup time | < 3s | ___s | ☐ | |
| 11.5 | Timeline render 1000 items | < 1s | ___s | ☐ | |

**Bugs Found:**
-

---

## 📊 Test Summary

### Overall Results
- **Total Tests:** 55
- **Passed:** ___ (___%)
- **Failed:** ___ (___%)
- **Skipped:** ___ (___%)

### By Severity

| Severity | Count | List |
|----------|-------|------|
| **Critical** | ___ | |
| **High** | ___ | |
| **Medium** | ___ | |
| **Low** | ___ | |

### Test Execution Details
- **Start Time:** _____________
- **End Time:** _____________
- **Total Duration:** _____________
- **Tester Name:** _____________

---

## 🐛 Bug Report Summary

### Critical Bugs (Blocker)

| ID | Description | Steps to Reproduce | Expected | Actual |
|----|-------------|-------------------|----------|---------|
| C1 | | | | |

### High Priority Bugs

| ID | Description | Steps to Reproduce | Expected | Actual |
|----|-------------|-------------------|----------|---------|
| H1 | | | | |

### Medium Priority Bugs

| ID | Description | Steps to Reproduce | Expected | Actual |
|----|-------------|-------------------|----------|---------|
| M1 | | | | |

### Low Priority Bugs (Cosmetic)

| ID | Description | Steps to Reproduce | Expected | Actual |
|----|-------------|-------------------|----------|---------|
| L1 | | | | |

---

## ✅ Sign-off

### Tester Approval
- [ ] **Ready for Release** - All critical/high bugs fixed
- [ ] **Ready with Caveats** - Minor issues acceptable
- [ ] **Not Ready** - Critical bugs present

**Tester Signature:** ___________________
**Date:** ___________________

### Lead Approval
**Approved By:** ___________________
**Date:** ___________________
**Comments:**
_________________________________________
_________________________________________
_________________________________________

---

## 📎 Attachments

- [ ] Screenshots of failures
- [ ] Log files
- [ ] Performance metrics
- [ ] Memory dumps (if applicable)

---

## 📝 Notes

**Environment:**
- OS: Windows 10 _____ / Windows 11 _____ (Build: ________)
- Python Version: _____________
- ClutchG Version: _____________
- Admin Rights: Yes / No

**Special Configurations:**
_________________________________________

**Workarounds Used:**
_________________________________________

**Suggestions for Improvement:**
_________________________________________

---

**This checklist is part of ClutchG Testing Suite**
**Version:** 1.0 | **Last Updated:** 6 February 2026

---

## 🖨️ Quick Print Instructions

1. Go to File → Print
2. Set orientation to Landscape
3. Enable "Print headers and footers"
4. Check "Background graphics" for checkboxes
5. Print and fill manually during testing

**Digital Usage:**
- Open in Markdown editor that supports checkboxes (Typora, Obsidian, VS Code)
- Use ✅ emoji or x to mark checkboxes
- Save copy as `testing-checklist-[DATE]-[TESTER].md`

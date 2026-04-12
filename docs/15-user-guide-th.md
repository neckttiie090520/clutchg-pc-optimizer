# คู่มือการใช้งาน ClutchG
**ClutchG User Manual (Thai)**

> **Version:** 1.0
> **วันที่:** 6 กุมภาพันธ์ 2026
> **ภาษา:** ไทย
> **สำหรับ:** Windows 10 22H2+ และ Windows 11 23H2+

---

## 📋 สารบัญ (Table of Contents)

1. [เกี่ยวกับ ClutchG](#1-เกี่ยวกับ-clutchg)
2. [การติดตั้ง](#2-การติดตั้ง)
3. [การใช้งานครั้งแรก](#3-การใช้งานครั้งแรก)
4. [คำศัพท์สำคัญ](#4-คำศัพท์สำคัญ)
5. [Dashboard Overview](#5-dashboard-overview)
6. [Optimization Profiles](#6-optimization-profiles)
7. [Script Library](#7-script-library)
8. [Backup & Restore Center](#8-backup--restore-center)
9. [Help & Documentation](#9-help--documentation)
10. [Settings](#10-settings)
11. [การแก้ปัญหา](#11-การแก้ปัญหา)
12. [คำถามที่พบบ่อย (FAQ)](#12-คำถามที่พบบ่อย-faq)
13. [ข้อมูลเพิ่มเติม](#13-ข้อมูลเพิ่มเติม)

---

## 1. เกี่ยวกับ ClutchG

### 1.1 ClutchG คืออะไร?

**ClutchG** เป็นเครื่องมือ optimize Windows PC สำหรับเกมและ performance ที่ออกแบบมาเพื่อ:

- ✅ **เพิ่มประสิทธิภาพการเล่นเกม** (FPS improvement)
- ✅ **ลด latency** (ping, input lag)
- ✅ **ปรับปรุง system responsiveness**
- ✅ **ทำอย่างปลอดภัย** - ทุกการเปลี่ยนแปลงย้อนกลับได้
- ✅ **อิงความจริง** - พัฒนาจากการวิจัย 23 repositories

### 1.2 หลักการสำคัญ

**Safety-First Philosophy:**
- ❌ **ไม่ปิด** Windows Defender
- ❌ **ไม่ปิด** Windows Update
- ❌ **ไม่ปิด** DEP/ASLR/CFG (security features)
- ✅ **ทุก tweak ย้อนกลับได้**
- ✅ **มี backup อัตโนมัติ** ก่อน apply
- ✅ **บันทึกทุก operation** ไว้ตรวจสอบ

### 1.3 ควรใช้เมื่อไหร่?

**ใช้ ClutchG ถ้า:**
- เล่นเกมแล้ว FPS ไม่สูงพอ
- Ping สูงหรือ input lag
- Windows รู้สึก sluggish
- ต้องการทำความสะอาด bloatware

**ไม่ควรใช้ถ้า:**
- PC ใช้งานทั่วไป (เกมไม่ได้เป็นหลัก)
- ไม่คุ้นเคยกับการ optimize PC
- ไม่มีพื้นที่ disk เหลืออย่างน้อย 500 MB

### 1.4 System Requirements

**ขั้นต่ำ:**
- Windows 10 22H2 (Build 19045) หรือใหม่กว่า
- Windows 11 23H2 (Build 22631) แนะนำ
- RAM 4 GB+
- Disk space 500 MB+ สำหรับ backups
- Python 3.11+
- Administrator rights

**แนะนำ:**
- RAM 8 GB+
- SSD disk
- CPU 4 cores+ (Intel/AMD)
- Dedicated GPU (NVIDIA/AMD)

---

## 2. การติดตั้ง

### 2.1 ติดตั้ง Python Dependencies

**Step 1:** เปิด Command Prompt หรือ PowerShell

**Step 2:** นำทางไปยังโฟลเดอร์ ClutchG:
```bash
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
```

**Step 3:** ติดตั้ง dependencies:
```bash
pip install -r requirements.txt
```

**Dependencies ที่ติดตั้ง:**
- `customtkinter>=5.2.0` - UI framework
- `Pillow>=10.0.0` - Image processing
- `psutil>=5.9.0` - System info
- `pywin32>=306` - Windows API

### 2.2 ติดตั้ง Material Symbols Font (Optional)

ClutchG ใช้ **Material Symbols Outlined** font สำหรับ icons

**ถ้า icons ไม่แสดง:**
1. Download font: https://fonts.google.com/icons
2. Install font (คลิกขวา → Install)
3. Restart ClutchG

**Fallback:**
- Windows จะใช้ **Segoe MDL2 Assets** แทนอัตโนมัติ
- Icons จะยังแสดงผลถูกต้อง

### 2.3 รัน Application

**Option 1: รันด้วย Python**
```bash
cd clutchg\src
python app_minimal.py
```

**Option 2: รันด้วย main.py**
```bash
cd clutchg\src
python main.py
```

**⚠️ สำคัญ:** ต้องรัน **เป็น Administrator**

**วิธีรันเป็น Administrator:**
1. คลิกขวาที่ Command Prompt
2. เลือก "Run as administrator"
3. Navigate และรัน application

### 2.4 ตรวจสอบการติดตั้ง

**เมื่อเปิดครั้งแรก:**
- ควรเห็น **Welcome overlay** หน้าต่างแนะนำ
- ควรเห็น **Dashboard** พร้อม system info
- ควรเห็น **sidebar** ด้านซ้าย

**ถ้า icons แสดงเป็น squares:**
- Material Symbols font ไม่ได้ติดตั้ง
- ClutchG จะ fallback ไป Segoe MDL2 Assets
- ถ้ายังไม่ได้ ติดตั้ง font ตาม section 2.2

---

## 3. การใช้งานครั้งแรก

### 3.1 Welcome Overlay

เมื่อเปิด ClutchG ครั้งแรก คุณจะเห็น **Welcome overlay** - หน้าต่างแนะนำการใช้งาน

**5 ขั้นตอนใน Welcome:**

**Step 1: Welcome**
- แนะนำ ClutchG
- อธิบาย philosophy (safe, evidence-based)

**Step 2: Dashboard Overview**
- อธิบาย Performance Score
- Hardware detection

**Step 3: Choose Your Profile**
- **SAFE** - สำหรับผู้เริ่มต้น
- **COMPETITIVE** - สำหรับเกมเมอร์
- **EXTREME** - สำหรับผู้เชี่ยวชาญ

**Step 4: Automatic Backups**
- อธิบายว่าทุกการ optimize มี backup
- System restore points
- Registry backups

**Step 5: Ready to Optimize!**
- อธิบายขั้นตอนการ apply profile
- แนะนำให้ไปที่ Profiles tab

**ปุ่ม:**
- **← Back** - ย้อนกลับ
- **Next →** - ถัดไป
- **Skip Tutorial** - ข้าม tutorial

### 3.2 System Detection

ClutchG จะ detect hardware อัตโนมัติ:

**ที่ตรวจสอบ:**
- **CPU** - Vendor (Intel/AMD), cores, threads
- **GPU** - Primary GPU model
- **RAM** - Total, available, usage %
- **OS** - Windows version, build number

**ข้อมูลนี้ใช้เพื่อ:**
- แสดงใน Dashboard
- คำนวณ Performance Score
- Apply tweaks ที่เหมาะสมกับ hardware

### 3.3 Performance Score

**Performance Score** คือคะแนน 0-100 ที่บ่งบอก potential ของ PC คุณ

**คำนวณจาก:**
- CPU cores/threads
- RAM capacity
- GPU model (ถ้ามี)
- SSD หรือ HDD

**ความหมาย:**
- **90-100** - High-end gaming PC
- **70-89** - Mid-range gaming PC
- **50-69** - Entry-level gaming PC
- **0-49** - Office/Basic PC

**⚠️ หมายเหตุ:** Score ไม่ใช่ FPS จริง แต่เป็น potential score

---

## 4. คำศัพท์สำคัญ

### 4.1 Technical Terms

| คำศัพท์ | ความหมาย |
|---------|----------|
| **Tweak** | การปรับแต่ง registry/settings เล็กๆ |
| **Profile** | ชุดของ tweaks ที่รวมกันเพื่อวัตถุประสงค์เดียว |
| **Backup** | สำเนาของ registry/settings ก่อนเปลี่ยน |
| **Restore** | คืนค่า settings จาก backup |
| **Registry** |ฐานข้อมูล settings ของ Windows |
| **System Restore Point** - จุดคืนค่าระบบของ Windows |
| **Timeline** | การแสดงประวัติ tweaks แบบ visual |
| **Flight Recorder** | ระบบบันทึก tweaks ทุกตัวแบบละเอียด |

### 4.2 Risk Levels

**LOW RISK (🟢):**
- Tweak ปลอดภัย 100%
- ไม่กระทบ functionality
- เหมาะสำหรับทุกคน

**MEDIUM RISK (🟡):**
- Tweak อาจกระทบบาง features
- แนะนำให้ทดลอง
- ต้องมี backup

**HIGH RISK (🔴):**
- Tweak กระทบ functionality หลายอย่าง
- สำหรับผู้เชี่ยวชาญเท่านั้น
- ต้องเข้าใจ consequences

---

## 5. Dashboard Overview

### 5.1 Dashboard คืออะไร?

Dashboard คือหน้าหลักที่แสดงภาพรวมของระบบคุณ

**Components:**
1. **System Info Card** - Hardware summary
2. **Performance Score** - คะแนนประสิทธิภาพ
3. **Quick Actions** - ปุ่มลัด
4. **Recent Activity** - tweaks ล่าสุด

### 5.2 System Info Card

**แสดง:**
- **CPU** - Vendor, cores, threads
- **GPU** - Model name
- **RAM** - Total GB, used GB
- **OS** - Windows version

**Refresh:**
- กด **Refresh button** เพื่อตรวจสอบใหม่
- ใช้เมื่อ upgrade hardware

### 5.3 Performance Score

**แสดง:**
- คะแนน 0-100 พร้อมสี
- 🟢 90-100 (Excellent)
- 🟡 70-89 (Good)
- 🟠 50-69 (Fair)
- 🔴 0-49 (Poor)

**เคล็ดลับ:**
- Score ไม่ใช่ FPS จริง
- แต่บอก potential ของ hardware

### 5.4 Quick Actions

**ปุ่มลัด:**
- **Create Backup** - สร้าง backup ทันที
- **View Timeline** - ดูประวัติ tweaks
- **System Info** - ดู hardware details

---

## 6. Optimization Profiles

### 6.1 Profiles คืออะไร?

**Profiles** คือชุดของ tweaks ที่ออกแบบมาเพื่อวัตถุประสงค์เฉพาะ

ClutchG มี 3 profiles:

### 6.2 SAFE Profile (🛡️ LOW RISK)

**สำหรับ:**
- ผู้เริ่มต้น
- ผู้ใช้ทั่วไป
- คนที่รัก stability

**ทำอะไร:**
- ✅ ปิด bloatware
- ✅ ปิด unnecessary services
- ✅ ปรับ privacy settings
- ✅ Disable GameDVR
- ✅ ปรับ power plan

**ไม่ทำ:**
- ❌ ไม่ปิด Windows Defender
- ❌ ไม่ปิด Windows Update
- ❌ ไม่ยุ่งกับ security features

**Expected Improvement:**
- FPS: +2-5%
- Responsiveness: +1-3%

**เหมาะกับ:**
- ทุกคนที่ไม่แน่ใจ
- Office PCs
- คนที่ต้องการความเสถียร

### 6.3 COMPETITIVE Profile (⚡ MEDIUM RISK)

**สำหรับ:**
- เกมเมอร์
- คนที่ต้องการ low latency
- คนที่เข้าใจความเสี่ยง

**ทำอะไร:**
- ทุกอย่างใน SAFE +
- ✅ Network optimization
- ✅ Disable telemetry
- ✅ Aggressive power settings
- ✅ Memory optimization
- ✅ Gaming service tweaks

**Expected Improvement:**
- FPS: +5-10%
- Ping: -5-15ms
- Input lag: -5-10ms

**เหมาะกับ:**
- เกมเมอร์ competitive
- คนที่เล่น FPS games (CS2, Valorant)
- คนที่ต้องการ edge ในการแข่ง

### 6.4 EXTREME Profile (🔥 HIGH RISK)

**สำหรับ:**
- Benchmarkers
- Enthusiasts
- คนที่เข้าใจ consequences

**Warnings ก่อนใช้:**
- ⚠️ อาจทำให้บาง features หายไป
- ⚠️ ไม่แนะนำสำหรับ daily driver
- ⚠️ ต้องมี backup เสมอ

**ทำอะไร:**
- ทุกอย่างใน COMPETITIVE +
- ✅ ปิด Windows Defender (ถ้ามี antivirus อื่น)
- ✅ Disable Windows Update automatic
- ✅ Aggressive memory cleaning
- ✅ Strip down Windows features

**Expected Improvement:**
- FPS: +10-15%
- System resources: -10-20% usage

**เหมาะกับ:**
- Benchmark rigs
- ทดสอบ performance
- ไม่เหมาะ daily driver

### 6.5 การ Apply Profile

**Step 1:** ไปที่ **Profiles tab** ใน sidebar

**Step 2:** เลือก profile ที่ต้องการ

**Step 3:** อ่าน descriptions และ risks

**Step 4:** กด **Apply** button

**Step 5:** **Confirmation Dialog**
- ถ้ามี warnings จะแสดง
- อ่านและเข้าใจ warnings
- กด **Yes** ถ้าตกลง หรือ **No** ถ้าไม่

**Step 6:** **Execution Dialog**
- จะแสดง progress
- แสดง tweaks ที่ apply
- แสดง results (SUCCESS/FAILED)

**Step 7:** **Finish**
- Toast notification แสดงผล
- Backup สร้างอัตโนมัติก่อน apply

### 6.6 หลังจาก Apply Profile

**ตรวจสอบ:**
1. PC restart ถ้าจำเป็น
2. Test เล่นเกม
3. Check ว่าไม่มี issues

**ถ้ามีปัญหา:**
- ไปที่ **Backup & Restore Center**
- Restore จาก backup ล่าสุด
- PC จะกลับสู่สถานะเดิม

---

## 7. Script Library

### 7.1 Scripts คืออะไร?

**Scripts** คือ batch scripts ที่ทำ tweaks เฉพาะทาง

**แตกต่างจาก Profiles:**
- Profiles = ชุด tweaks หลายอย่าง
- Scripts = tweak เดียวหรือกลุ่ม tweaks ที่เฉพาะเจาะจง

### 7.2 ใช้ Scripts เมื่อไหร่?

**ใช้ scripts ถ้า:**
- ต้องการ tweak เฉพาะทาง
- ไม่ต้องการ apply ทั้ง profile
- ต้องการ control รายละเอียด

**ตัวอย่าง:**
- Disable GameDVR อย่างเดียว
- Optimize network อย่างเดียว
- Clear cache อย่างเดียว

### 7.3 การใช้ Script Library

**Step 1:** ไปที่ **Scripts tab** ใน sidebar

**Step 2:** เห็นรายการ scripts ทั้งหมดใน grid

**Step 3:** **Search** (ถ้าจำชื่อไม่ได้)
- พิมพ์ใน search box
- List จะกรองตาม query

**Step 4:** เลือก script ที่ต้องการ

**Step 5:** อ่าน details:
- **Name** - ชื่อ script
- **Filename** - ชื่อไฟล์จริง
- **Risk Level** - LOW/MEDIUM/HIGH

**Step 6:** กด **RUN** button

**Step 7:** **Execution Dialog**
- แสดง output
- แสดง progress
- แสดง result

### 7.4 Risk Indicators

**🟢 LOW (Green):**
- ปลอดภัย 100%
- ไม่กระทบ system

**🟡 MEDIUM (Yellow):**
- อาจกระทบบาง features
- แนะนำให้อ่าน descriptions

**🔴 HIGH (Red):**
- กระทบ functionality
- สำหรับผู้เชี่ยวชาญ

---

## 8. Backup & Restore Center

### 8.1 รู้จักกับ Backup & Restore Center

Backup & Restore Center เป็นจุดรวมจัดการ backups ทั้งหมด

**2 Modes:**
1. **Simple Mode** - จัดการ backups แบบง่าย
2. **Advanced Mode** - Timeline visualization พร้อม Flight Recorder

### 8.2 Simple Mode (ค่าเริ่มต้น)

**คืออะไร:**
- แสดงรายการ backups เป็น cards
- เหมาะสำหรับผู้ใช้ทั่วไป

**ทำอะไรได้:**
- ✅ Create backup
- ✅ View backup details
- ✅ Restore from backup
- ✅ Delete backup

**การใช้งาน:**

**Create Backup:**
1. กด **Create Backup** button
2. ใส่ชื่อ backup
3. กด **OK**
4. Backup สร้างสำเร็จ
5. Toast notification แสดง

**View Backup Details:**
1. คลิกที่ backup card
2. Details แสดง:
   - Type (Manual/Auto)
   - Size
   - Date created
   - Registry backup size

**Restore from Backup:**
1. คลิก **Restore** button บน backup card
2. Confirmation dialog แสดง
3. กด **Yes** เพื่อยืนยัน
4. Restore ดำเนินการ
5. Toast notification แสดงผล

**Delete Backup:**
1. คลิก **Delete** button
2. Confirmation dialog แสดง
3. กด **Yes** เพื่อยืนยัน
4. Backup ถูกลบ

### 8.3 Advanced Mode (Timeline)

**คืออะไร:**
- Visual timeline ของ tweaks ทั้งหมด
- ใช้ Flight Recorder ในการ track
- เหมาะสำหรับผู้เชี่ยวชาญ

**ทำอะไรได้:**
- ✅ ดู timeline ของ tweaks ทั้งหมด
- ✅ Filter by type (manual, auto, profile_applied, restore)
- ✅ Click เพื่อดู details
- ✅ Undo individual tweaks

**การใช้งาน:**

**Switch to Advanced Mode:**
1. คลิก mode toggle → **Advanced**
2. Simple mode ซ่อน
3. Timeline แสดงแนวนอน

**Timeline Visualization:**
- **แนวนอน** - เรียงตาม chronological order
- **สี** - บ่งบอก status
  - 🟢 Green = SUCCESS
  - 🔴 Red = FAILED
- **ขนาด** - บ่งบอก complexity

**Filter Timeline:**
1. เลือก filter type
   - All
   - Manual
   - Auto (จาก profile)
   - Profile Applied
   - Restore
2. Timeline กรองตาม type

**Click Timeline Item:**
1. คลิกที่ item บน timeline
2. Details panel แสดง:
   - Tweak name
   - Category
   - Risk level
   - Status
   - Timestamp
   - Undo command (ถ้ามี)

**Undo Tweak:**
1. คลิก timeline item
2. กด **Undo** button
3. Confirmation dialog
4. Tweak ย้อนกลับสำเร็จ

### 8.4 Automatic Backups

**เมื่อไหร่ที่ auto backup:**
- ✅ ก่อน apply profile
- ✅ ก่อน run script
- ✅ Manual backup ตาม schedule (ถ้า set)

**ประเภท backups:**
1. **System Restore Point** - Windows restore point
2. **Registry Backup** - Export registry เป็น .reg file
3. **Configuration Snapshot** - JSON config

**Storage Location:**
```
clutchg/
└── data/
    └── backups/
        ├── registry_20250206_143022.reg
        ├── snapshot_20250206_143022.json
        └── timeline_20250206_143022.json
```

### 8.5 Best Practices

**ควรทำ:**
- ✅ Create backup ก่อน apply major changes
- ✅ Delete old backups บางส่วน (ประหยัด space)
- ✅ Name backups ให้มีความหมาย
- ✅ Test restore สม่ำเสมอ

**ไม่ควรทำ:**
- ❌ Delete ทุก backups
- ❌ Ignore backup warnings
- ❌ Restore โดยไม่เข้าใจ consequences

---

## 9. Help & Documentation

### 9.1 Help Tab

**คืออะไร:**
- Knowledge base แบบ bilingual (TH/EN)
- คำถามที่พบบ่อย
- Myth-busting section

**Categories:**
1. **Getting Started** - สำหรับผู้เริ่มต้น
2. **Profiles** - อธิบายแต่ละ profile
3. **Backups** - การจัดการ backups
4. **Troubleshooting** - แก้ปัญหา
5. **Myth-Busting** - พรางความจริง

### 9.2 การใช้งาน

**Search:**
1. พิมพ์คำค้นใน search box
2. Results กรองตาม query
3. Click เพื่อดู content

**Browse Categories:**
1. Click บน category card
2. Content แสดงใน detail panel
3. Click topics เพื่อ expand

### 9.3 Myth-Busting Section

**ทำไมต้อง Myth-Busting?**
เพราะมีข้อมูลผิดๆ เกี่ยวกับ optimization เยอะมาก

**Myths ที่ Debunk:**
1. ❌ "Windows จอง bandwidth 20% ไว้" → ✅ เท็จ
2. ❌ "Timer resolution boosts FPS" → ✅ เก่า (ใช้ได้แค่ Win7)
3. ❌ "Disable 100 services = เร็วขึ้น" → ✅ อันตราย

**ใน Help Tab:**
- 📕 สีแดง = Myth (เท็จ)
- 📗 สีเขียว = Fact (จริง)

---

## 10. Settings

### 10.1 Settings Tab

**คืออะไร:**
- จัดการ application settings
- Language, theme, accent colors

### 10.2 Language (ภาษา)

**ตัวเลือก:**
- 🇬🇧 **English** - ภาษาอังกฤษ
- 🇹🇭 **Thai** - ภาษาไทย

**การเปลี่ยน:**
1. เลือกภาษาใน Settings
2. ทุก views เปลี่ยนทันที
3. Restart ไม่จำเป็น

**สิ่งที่เปลี่ยน:**
- UI labels
- Help content
- Button text
- Error messages

### 10.3 Theme (ธีม)

**ตัวเลือก:**
- 🌙 **Dark** - สีมืด (default)
- ☀️ **Light** - สีสว่าง

**การเปลี่ยน:**
1. เลือก theme ใน Settings
2. ทุก views เปลี่ยนทันที

**สิ่งที่เปลี่ยน:**
- Background colors
- Text colors
- Card colors
- Border colors

### 10.4 Accent Colors

**ตัวเลือก:**
- 🔵 **Blue** - สีน้ำเงิน (default)
- 🟣 **Purple** - สีม่วง
- 🔷 **Cyan** - สีฟ้า
- 🟢 **Green** - สีเขียว
- 🩷 **Pink** - สีชมพู

**การเปลี่ยน:**
1. เลือกสีใน Settings
2. ทันที apply ทั้ง app

**สิ่งที่เปลี่ยน:**
- Active navigation highlighting
- Button primary colors
- Progress bars
- Status indicators

---

## 11. การแก้ปัญหา

### 11.1 ปัญหาที่พบบ่อย

**Problem 1: Application ไม่เปิด**

**Symptoms:**
- ดับเบิลคลิก แล้วไม่มีอะไรเกิดขึ้น
- Error message: "Access Denied"

**Solution:**
1. ปิด application ทิ้ง
2. คลิกขวาที่ Command Prompt
3. เลือก "Run as administrator"
4. Navigate และรันอีกครั้ง

---

**Problem 2: Icons แสดงเป็น squares**

**Symptoms:**
- Icons ไม่แสดง
- แสดงเป็น squares ว่างๆ

**Solution:**
1. Download Material Symbols font
2. Install font
3. Restart ClutchG
4. ถ้ายังไม่ได้ → ClutchG จะ fallback ไป Segoe MDL2 Assets

---

**Problem 3: Apply Profile ไม่สำเร็จ**

**Symptoms:**
- Execution dialog แสดง FAILED
- Toast error notification

**Possible Causes:**
1. **ไม่มี admin rights** → รันเป็น admin
2. **Registry access denied** → Check Windows permissions
3. **Disk full** → ลบ files เก่าๆ
4. **Antivirus block** → ตั้งค่า antivirus ให้อนุญาต

**Solution:**
1. Check error message ใน execution dialog
2. Fix ตาม cause
3. Try apply อีกครั้ง

---

**Problem 4: Restore ไม่สำเร็จ**

**Symptoms:**
- Restore failed
- Error message: "Cannot import registry"

**Solution:**
1. Check ว่า backup file ยังอยู่
2. Check disk space
3. Try manual restore:
   ```bash
   reg import "path\to\backup.reg"
   ```
4. Use System Restore ถ้า registry restore ล้มเหลว

---

**Problem 5: Performance Score ไม่เปลี่ยน**

**Symptoms:**
- Upgrade hardware แต่ score เท่าเดิม

**Solution:**
1. Click **Refresh** button
2. System detector จะ scan ใหม่
3. Score ควร update

---

**Problem 6: Timeline ไม่แสดง**

**Symptoms:**
- Advanced mode ว่างเปล่า
- Timeline ไม่มี items

**Solution:**
1. Check ว่าเคย apply tweaks หรือยัง
2. ถ้าไม่เคย → Normal (ไม่มี history)
3. Apply profile หรือ run script → Timeline จะเริ่มบันทึก

---

**Problem 7: Memory Leak**

**Symptoms:**
- Application ช้าลงเรื่อยๆ
- Memory usage สูงขึ้นเรื่อยๆ

**Solution:**
1. Restart ClutchG
2. Report issue พร้อม log files
3. ชั่วคราว → Switch views ไม่เกิน 50 ครั้งต่อ session

---

### 11.2 Log Files

**Location:**
```
clutchg/
└── logs/
    ├── clutchg_20250206_143022.log
    ├── error_20250206_143022.log
    └── backup_20250206_143022.log
```

**การใช้:**
- Attach log files เมื่อรายงาน bugs
- Check logs ถ้ามี issues

---

### 11.3 การรายงาน Bug

**Template:**
```markdown
### Bug Report

**Environment:**
- Windows Version: [เช่น Windows 11 23H2]
- Python Version: [เช่น 3.11.5]
- ClutchG Version: [เช่น 1.0.0]

**Summary:**
[สรุปปัญหาใน 1 ประโยค]

**Steps to Reproduce:**
1. [ขั้นตอนที่ 1]
2. [ขั้นตอนที่ 2]

**Expected Behavior:**
[ที่คาดหวัง]

**Actual Behavior:**
[ที่เกิดขึ้นจริง]

**Attachments:**
- Screenshots
- Log files
```

---

## 12. คำถามที่พบบ่อย (FAQ)

### 12.1 General Questions

**Q1: ClutchG ปลอดภัยหรือไม่?**
**A:** ใช่ ออกแบบมาเพื่อความปลอดภัยเป็นหลัก:
- ทุกการเปลี่ยนแปลงย้อนกลับได้
- มี backup อัตโนมัติ
- ไม่ปิด Windows Defender
- ไม่ปิด security features

---

**Q2: ClutchG ใช้ได้ฟรีหรือไม่?**
**A:** ใช่ 100% ฟรีและ open-source

---

**Q3: ใช้ ClutchG ได้บน Windows 10 หรือไม่?**
**A:** ได้ แต่ต้องเป็น Windows 10 22H2 (Build 19045) ขึ้นไป
- Windows 11 23H2+ แนะนำ

---

**Q4: ต้องมีพื้นที่ disk เท่าไหร่?**
**A:** อย่างน้อย 500 MB สำหรับ backups
- แนะนำ 2 GB+ ถ้าจะเก็บ backups หลายชุด

---

### 12.2 Usage Questions

**Q5: ควรเลือก Profile ไหน?**
**A:**
- **ผู้เริ่มต้น** → SAFE
- **เกมเมอร์** → COMPETITIVE
- **Benchmarkers** → EXTREME

---

**Q6: Apply Profile แล้วต้อง restart ไหม?**
**A:** บาง tweaks ต้อง restart:
- Power plan changes
- Service changes
- Registry changes

Execution dialog จะแจ้งว่าต้อง restart หรือไม่

---

**Q7: สามารถ apply หลาย profiles ได้ไหม?**
**A:** ไม่แนะนำ
- เลือก profile เดียว แล้วใช้ต่อเนื่อง
- ถ้าต้องการเปลี่ยน → restore ก่อน แล้ว apply profile ใหม่

---

**Q8: Scripts กับ Profiles ต่างกันอย่างไร?**
**A:**
- **Profiles** = ชุด tweaks หลายอย่าง
- **Scripts** = tweak เดียวหรือกลุ่ม tweaks เฉพาะทาง

ใช้ scripts ถ้าต้องการ control รายละเอียด

---

**Q9: Backup ไว้ที่ไหน?**
**A:**
```
clutchg/data/backups/
```
- Registry backups (.reg files)
- Snapshots (.json)
- Timeline data (.json)

---

**Q10: ควรลบ backups เก่าๆ หรือไม่?**
**A:** ควร
- เก็บไว้ 5-10 backups ล่าสุด
- ลบที่เก่ากว่า เพื่อประหยัด space
- แต่อย่าลบทั้งหมด

---

### 12.3 Performance Questions

**Q11: จะได้ FPS เพิ่มเท่าไหร่?**
**A:** ขึ้นกับ profile:
- **SAFE** → +2-5%
- **COMPETITIVE** → +5-10%
- **EXTREME** → +10-15%

ไม่รับประกัน เพราะขึ้นกับ hardware/game

---

**Q12: Ping จะลดเท่าไหร่?**
**A:**
- **COMPETITIVE** → -5-15ms (average)
- **EXTREME** → -10-20ms (average)

ขึ้นกับ network/ISP

---

**Q13: ClutchG ทำให้ boot ช้าลงไหม?**
**A:** ไม่
- เปิด/ปิด services ที่ไม่กระทบ boot time
- อาจเร็วขึ้นเล็กน้อย (disable bloatware)

---

### 12.4 Safety Questions

**Q14: ถ้า apply profile แล้วมีปัญหาทำไง?**
**A:**
1. ไปที่ Backup & Restore Center
2. Restore จาก backup ล่าสุด
3. PC จะกลับสู่สถานะเดิม

---

**Q15: Restore ล้มเหลวทำไง?**
**A:**
1. ใช้ System Restore ของ Windows
2. Manual import registry backup
3. Reinstall ClutchG และ restore ใหม่

---

**Q16: ClutchG ส่งข้อมูลไปที่ไหนไหม?**
**A:** ไม่
- 100% offline
- ไม่มี telemetry
- ไม่มี internet connection ที่จำเป็น

---

## 13. ข้อมูลเพิ่มเติม

### 13.1 Links

**Official Documentation:**
- [Development Plan (TH)](11-development-plan.md)
- [Testing Procedures](13-testing-procedures.md)
- [Testing Checklist](14-testing-checklist.md)
- [Technical Spec](clutchg_technical_spec.md)

**External Resources:**
- [CustomTkinter Docs](https://customtkinter.tomschimansky.com/)
- [Material Symbols](https://fonts.google.com/icons)

### 13.2 Credits

**Development:**
- Architecture based on research of 23 Windows optimization repositories
- UI framework: CustomTkinter
- Icon font: Material Symbols Outlined (Google)

**Safety Philosophy:**
- Inspired by WinUtil (9.5/10 safety score)
- Evidence-based tweaks only
- Never compromise security for performance

### 13.3 License

This project is open-source and available under the MIT License.

### 13.4 Version History

**Version 1.0 (6 February 2026):**
- Initial release
- 3 optimization profiles (SAFE, COMPETITIVE, EXTREME)
- Unified Backup & Restore Center
- Bilingual support (TH/EN)
- Modern glassmorphism UI

---

## 📞 การติดต่อ

ถ้าพบบั๊ก หรือมีคำถาม:

1. **Check:** อ่าน troubleshooting section ก่อน
2. **Search:** ค้นใน Help tab
3. **Report:** สร้าง issue พร้อม log files

---

**เอกสารนี้เป็นส่วนหนึ่งของ ClutchG Project**
**Version:** 1.0 | **Last Updated:** 6 กุมภาพันธ์ 2026
**ภาษา:** ไทย

---

## 🎓 Quick Reference

**Hotkeys (ถ้ามี):**
- `Ctrl+B` - Create backup
- `Ctrl+T` - View timeline
- `Ctrl+S` - Open settings

**คำสั่ง Bash:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run app (as admin)
cd clutchg\src
python app_minimal.py
```

**คำสั่ง Batch:**
```batch
# Manual registry restore
reg import "clutchg\data\backups\backup.reg"

# Create system restore point
powershell -Command "Checkpoint-Computer -Description 'Before ClutchG' -RestorePointType 'MODIFY_SETTINGS'"
```

---

**End of Document**

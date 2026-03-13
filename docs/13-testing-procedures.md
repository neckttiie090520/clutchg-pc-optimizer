# ขั้นตอนการทดสอบ ClutchG Application
**Testing Procedures**

> **เวอร์ชัน:** 1.0
> **วันที่:** 6 กุมภาพันธ์ 2026
> **สถานะ:** Draft
> **ภาษา:** ไทย

---

## ภาพรวม (Overview)

เอกสารนี้อธิบายขั้นตอนการทดสอบ ClutchG application ทั้งในส่วนของ Unit Testing, Integration Testing, Manual Testing และ Performance Testing การทดสอบมีวัตถุประสงค์เพื่อให้มั่นใจว่า:

- ✅ ฟีเจอร์ทั้งหมดทำงานได้ตามที่ออกแบบ
- ✅ ไม่มี bugs หรือ errors ที่ทำให้ application crash
- ✅ User experience เป็นไปอย่างราบรื่น
- ✅ การเปลี่ยนแปลงทั้งหมดสามารถย้อนกลับได้ (reversible)

---

## ส่วนที่ 1: Unit Testing (การทดสอบหน่วย)

Unit testing คือการทดสอบแต่ละ component แยกกัน เพื่อให้แน่ใจว่าแต่ละส่วนทำงานถูกต้อง

### 1.1 การทดสอบ Core Managers

#### 1.1.1 BackupManager

**ไฟล์:** `clutchg/src/core/backup_manager.py`

**Test Cases:**

```python
def test_create_backup():
    """ทดสอบการสร้าง backup"""
    # Arrange
    mgr = BackupManager()
    name = "test_backup"

    # Act
    backup = mgr.create_backup(name)

    # Assert
    assert backup is not None
    assert backup.name == name
    assert backup.path.exists()
    assert backup.registry_backup.exists()

def test_get_all_backups():
    """ทดสอบการดึงรายการ backups ทั้งหมด"""
    # Arrange
    mgr = BackupManager()
    mgr.create_backup("backup1")
    mgr.create_backup("backup2")

    # Act
    backups = mgr.get_all_backups()

    # Assert
    assert len(backups) >= 2
    assert any(b.name == "backup1" for b in backups)

def test_restore_backup():
    """ทดสอบการ restore จาก backup"""
    # Arrange
    mgr = BackupManager()
    backup = mgr.create_backup("test_restore")

    # Act
    success = mgr.restore_backup(backup.id)

    # Assert
    assert success == True

def test_delete_backup():
    """ทดสอบการลบ backup"""
    # Arrange
    mgr = BackupManager()
    backup = mgr.create_backup("test_delete")

    # Act
    mgr.delete_backup(backup.id)

    # Assert
    assert not backup.path.exists()
```

**การรัน:**
```bash
cd clutchg/tests/unit
python -m pytest test_backup_manager.py -v
```

#### 1.1.2 FlightRecorder

**ไฟล์:** `clutchg/src/core/flight_recorder.py`

**Test Cases:**

```python
def test_record_tweak():
    """ทดสอบการบันทึก tweak"""
    # Arrange
    recorder = FlightRecorder()
    tweak = {
        "name": "DisableGameDVR",
        "category": "gaming",
        "risk": "LOW"
    }

    # Act
    recorder.record_tweak(tweak, "SUCCESS")

    # Assert
    snapshots = recorder.get_all_snapshots()
    assert len(snapshots) > 0

def test_get_timeline_data():
    """ทดสอบการดึงข้อมูล timeline"""
    # Arrange
    recorder = FlightRecorder()
    recorder.record_tweak({"name": "Tweak1"}, "SUCCESS")

    # Act
    timeline = recorder.get_timeline_data()

    # Assert
    assert len(timeline) > 0
    assert "timestamp" in timeline[0]

def test_undo_tweak():
    """ทดสอบการย้อนกลับ tweak"""
    # Arrange
    recorder = FlightRecorder()
    recorder.record_tweak(
        {"name": "Tweak1", "undo_command": "reg delete ..."},
        "SUCCESS"
    )

    # Act
    success = recorder.undo_tweak(timeline[0]["id"])

    # Assert
    assert success == True
```

**การรัน:**
```bash
cd clutchg/tests/unit
python -m pytest test_flight_recorder.py -v
```

#### 1.1.3 ProfileManager

**ไฟล์:** `clutchg/src/core/profile_manager.py`

**Test Cases:**

```python
def test_load_profiles():
    """ทดสอบการโหลด profiles"""
    # Arrange
    mgr = ProfileManager()

    # Act
    profiles = mgr.get_all_profiles()

    # Assert
    assert len(profiles) == 3
    assert any(p.name == "SAFE" for p in profiles)
    assert any(p.name == "COMPETITIVE" for p in profiles)
    assert any(p.name == "EXTREME" for p in profiles)

def test_apply_profile():
    """ทดสอบการ apply profile"""
    # Arrange
    mgr = ProfileManager()
    profile = mgr.get_profile("SAFE")

    # Act
    results = []
    mgr.apply_profile(
        profile,
        on_progress=lambda p: results.append(f"Progress: {p}"),
        on_output=lambda line: results.append(line)
    )

    # Assert
    assert len(results) > 0
    assert any("SUCCESS" in r for r in results)

def test_profile_warnings():
    """ทดสอบการแสดง warnings"""
    # Arrange
    mgr = ProfileManager()
    profile = mgr.get_profile("EXTREME")

    # Assert
    assert len(profile.warnings) > 0
    assert any("ไม่แนะนำ" in w for w in profile.warnings)
```

**การรัน:**
```bash
cd clutchg/tests/unit
python -m pytest test_profile_manager.py -v
```

#### 1.1.4 SystemDetector

**ไฟล์:** `clutchg/src/core/system_info.py`

**Test Cases:**

```python
def test_detect_cpu():
    """ทดสอบการตรวจจับ CPU"""
    # Arrange
    detector = SystemDetector()

    # Act
    cpu = detector.get_cpu_info()

    # Assert
    assert cpu["vendor"] in ["Intel", "AMD", "Unknown"]
    assert cpu["cores"] > 0
    assert cpu["threads"] > 0

def test_detect_gpu():
    """ทดสอบการตรวจจับ GPU"""
    # Arrange
    detector = SystemDetector()

    # Act
    gpu = detector.get_gpu_info()

    # Assert
    assert len(gpu) > 0
    assert "name" in gpu[0]

def test_detect_ram():
    """ทดสอบการตรวจจับ RAM"""
    # Arrange
    detector = SystemDetector()

    # Act
    ram = detector.get_ram_info()

    # Assert
    assert ram["total_gb"] > 0
    assert ram["free_gb"] > 0
```

**การรัน:**
```bash
cd clutchg/tests/unit
python -m pytest test_system_detector.py -v
```

### 1.2 การทดสอบ UI Components

#### 1.2.1 GlassCard Component

**ไฟล์:** `clutchg/src/gui/components/glass_card.py`

**Test Cases:**

```python
def test_glass_card_creation():
    """ทดสอบการสร้าง GlassCard"""
    # Arrange
    root = ctk.CTk()

    # Act
    card = GlassCard(root, corner_radius=12)

    # Assert
    assert card.cget("corner_radius") == 12
    assert card.cget("fg_color") == COLORS["bg_card"]

    root.destroy()
```

#### 1.2.2 IconProvider

**ไฟล์:** `clutchg/src/gui/components/icon_provider.py`

**Test Cases:**

```python
def test_get_icon():
    """ทดสอบการดึง icon"""
    # Arrange
    provider = IconProvider()

    # Act
    backup_icon = provider.get_icon("backup")

    # Assert
    assert backup_icon is not None
    assert len(backup_icon) == 1  # Single character

def test_icon_fallback():
    """ทดสอบ fallback mechanism"""
    # Arrange
    provider = IconProvider()

    # Act
    icon = provider.get_icon("nonexistent")

    # Assert
    assert icon == "?"  # Fallback to question mark
```

**การรัน:**
```bash
cd clutchg/tests/unit
python -m pytest test_icon_provider.py -v
```

---

## ส่วนที่ 2: Integration Testing (การทดสอบการทำงานร่วมกัน)

Integration testing คือการทดสอบการทำงานร่วมกันของหลาย components

### 2.1 Backup & Restore Center Integration

**ไฟล์:** `clutchg/tests/integration/test_backup_restore_integration.py`

**Test Cases:**

```python
def test_create_and_restore_flow():
    """ทดสอบ flow การสร้างและ restore backup"""
    # Arrange
    app = ClutchGApp()
    view = BackupRestoreCenter(app.main_frame, app)

    # Act - Create backup
    view.create_backup()

    # Assert - Backup created
    backups = view.backup_mgr.get_all_backups()
    assert len(backups) > 0

    # Act - Restore
    view.restore_backup(backups[0].id)

    # Assert - Restore successful
    assert view.last_restore_success == True

def test_simple_advanced_mode_switch():
    """ทดสอบการสลับ mode"""
    # Arrange
    app = ClutchGApp()
    view = BackupRestoreCenter(app.main_frame, app)

    # Act - Switch to advanced
    view.switch_mode("advanced")

    # Assert
    assert view.current_mode == "advanced"
    assert view.simple_container.winfo_ismapped() == False
    assert view.advanced_container.winfo_ismapped() == True

    # Act - Switch back to simple
    view.switch_mode("simple")

    # Assert
    assert view.current_mode == "simple"
```

**การรัน:**
```bash
cd clutchg/tests/integration
python -m pytest test_backup_restore_integration.py -v
```

### 2.2 Profile Application Integration

**ไฟล์:** `clutchg/tests/integration/test_profile_integration.py`

**Test Cases:**

```python
def test_apply_profile_flow():
    """ทดสอบ flow การ apply profile"""
    # Arrange
    app = ClutchGApp()
    view = ProfilesView(app.main_frame, app)

    # Act - Click apply on SAFE profile
    view.apply_profile("SAFE")

    # Assert
    assert app.profile_manager.last_applied == "SAFE"
    assert app.toast.last_message == "Profile applied successfully"

def test_profile_with_warnings():
    """ทดสอบ profile ที่มี warnings"""
    # Arrange
    app = ClutchGApp()
    view = ProfilesView(app.main_frame, app)

    # Act - Try to apply EXTREME
    with patch('tkinter.messagebox.askyesno', return_value=False):
        view.apply_profile("EXTREME")

    # Assert - Should not apply
    assert app.profile_manager.last_applied != "EXTREME"
```

**การรัน:**
```bash
cd clutchg/tests/integration
python -m pytest test_profile_integration.py -v
```

### 2.3 Timeline + FlightRecorder Integration

**ไฟล์:** `clutchg/tests/integration/test_timeline_integration.py`

**Test Cases:**

```python
def test_timeline_displays_snapshots():
    """ทดสอบว่า timeline แสดง snapshots ถูกต้อง"""
    # Arrange
    recorder = FlightRecorder()
    recorder.record_tweak({"name": "Tweak1"}, "SUCCESS")
    recorder.record_tweak({"name": "Tweak2"}, "FAILED")

    app = ClutchGApp()
    view = BackupRestoreCenter(app.main_frame, app)
    view.switch_mode("advanced")

    # Act
    timeline_data = view.timeline.get_data()

    # Assert
    assert len(timeline_data) == 2
    assert timeline_data[0]["status"] == "SUCCESS"
    assert timeline_data[1]["status"] == "FAILED"

def test_timeline_click_shows_details():
    """ทดสอบการคลิก timeline เพื่อดู details"""
    # Arrange
    app = ClutchGApp()
    view = BackupRestoreCenter(app.main_frame, app)
    view.switch_mode("advanced")

    # Act - Simulate click
    view.timeline.on_item_click(timeline_data[0]["id"])

    # Assert
    assert view.details_panel.is_visible
    assert view.details_panel.current_data["name"] == "Tweak1"
```

**การรัน:**
```bash
cd clutchg/tests/integration
python -m pytest test_timeline_integration.py -v
```

---

## ส่วนที่ 3: Manual Testing Checklist (ทดสอบด้วยมือ)

Manual testing คือการทดสอบโดยใช้งานจริง ตาม checklist นี้

### 3.1 Installation & First Run

- [ ] **ติดตั้ง Python dependencies ครบถ้วน**
  - รัน `pip install -r requirements.txt`
  - ไม่มี error messages

- [ ] **รัน application ครั้งแรก**
  - รัน `python app_minimal.py` หรือ `python main.py`
  - Application เปิดขึ้นมาโดยไม่ crash

- [ ] **Welcome overlay แสดงผล**
  - Overlay แสดงขึ้นมาอัตโนมัติ
  - สามารถกด Next/Back ได้
  - สามารถ Skip tutorial ได้
  - Icons แสดงผลถูกต้อง (ไม่เป็น squares)

### 3.2 Dashboard View

- [ ] **System detection ทำงาน**
  - CPU, GPU, RAM แสดงผลถูกต้อง
  - Performance score คำนวณได้
  - Hardware info ตรงกับระบบจริง

- [ ] **Refresh ทำงาน**
  - กด Refresh button
  - ข้อมูลอัปเดตใหม่

### 3.3 Profiles View

- [ ] **Profile cards แสดงผล**
  - SAFE, COMPETITIVE, EXTREME cards แสดงทั้ง 3
  - Icons แสดงถูกต้อง
  - Descriptions แสดงเป็นภาษาที่เลือก (TH/EN)

- [ ] **Apply SAFE profile**
  - กด Apply บน SAFE profile
  - มี confirmation dialog
  - มี execution dialog
  - Progress bar ทำงาน
  - มี backup สร้างอัตโนมัติ
  - Toast notification แสดง success

- [ ] **Apply COMPETITIVE profile**
  - เหมือนด้านบน แต่ใช้ COMPETITIVE

- [ ] **Apply EXTREME profile**
  - มี warnings แสดงก่อน
  - ถ้ากด No ไม่ apply
  - ถ้ากด Yes ทำการ apply

- [ ] **Apply profile ไม่สำเร็จ**
  - Simulate error (เช่นไม่มี admin rights)
  - Error message แสดงชัดเจน
  - Toast notification แสดง error

### 3.4 Scripts View

- [ ] **Scripts list แสดงผล**
  - Scripts ทั้งหมดแสดงใน grid
  - Icons แสดงถูกต้องตาม risk level
  - Search filter ทำงาน

- [ ] **Run script**
  - กด RUN บน script
  - Execution dialog แสดง
  - Output แสดงใน dialog
  - Result แสดง success/failed

- [ ] **Search filter**
  - พิมพ์ใน search box
  - List กรองตาม query
  - Clear search = แสดงทั้งหมด

### 3.5 Backup & Restore Center (Simple Mode)

- [ ] **Simple mode default**
  - เปิดมาที่ Simple mode เป็นค่าเริ่มต้น
  - Backup list แสดง

- [ ] **Create backup**
  - กด Create Backup button
  - มี dialog ให้ตั้งชื่อ
  - Backup สร้างสำเร็จ
  - Toast notification แสดง success
  - Backup ปรากฏใน list

- [ ] **View backup details**
  - คลิกที่ backup card
  - Details แสดง (type, size, date)

- [ ] **Restore from backup**
  - คลิก Restore button
  - มี confirmation dialog
  - Restore สำเร็จ
  - Toast notification แสดง

- [ ] **Delete backup**
  - คลิก Delete button
  - มี confirmation dialog
  - Backup หายไปจาก list

### 3.6 Backup & Restore Center (Advanced Mode)

- [ ] **Switch to Advanced mode**
  - คลิก mode toggle → Advanced
  - Simple mode ซ่อน
  - Timeline แสดง

- [ ] **Timeline visualization**
  - Timeline แสดงแนวนอน
  - Items แสดงตาม chronological order
  - Colors แสดง status (success/failed)

- [ ] **Filter timeline**
  - เลือก filter by type (manual, auto, etc.)
  - Timeline กรองตาม type

- [ ] **Click timeline item**
  - คลิกที่ item
  - Details panel แสดง
  - แสดง tweak details

- [ ] **Undo tweak from timeline**
  - คลิก item
  - กด Undo button
  - Tweak ย้อนกลับสำเร็จ

- [ ] **Switch back to Simple mode**
  - คลิก mode toggle → Simple
  - Advanced mode ซ่อน
  - Simple mode แสดง

### 3.7 Help View

- [ ] **Help categories**
  - Categories แสดงทั้งหมด
  - Icons แสดงถูกต้อง

- [ ] **Search help**
  - พิมพ์ใน search box
  - Results กรองตาม query

- [ ] **Click help item**
  - คลิกที่ item
  - Content แสดงใน detail panel
  - Content เป็นภาษาที่เลือก

- [ ] **Myth-busting section**
  - Myths แสดงถูกต้อง
  - Facts แสดงถูกต้อง
  - Icons แสดง (error, success)

### 3.8 Settings View

- [ ] **Language switch (TH ↔ EN)**
  - เลือกภาษาไทย
  - ทุก views เปลี่ยนเป็นไทย
  - เลือก English
  - ทุก views เปลี่ยนเป็นอังกฤษ

- [ ] **Theme switch (Dark ↔ Light)**
  - เลือก Light theme
  - ทุก views เปลี่ยนเป็นสว่าง
  - เลือก Dark theme
  - ทุก views เปลี่ยนเป็นมืด

- [ ] **Accent color change**
  - เลือก accent color (Cyan, Purple, etc.)
  - UI elements เปลี่ยนสีตาม

### 3.9 Navigation

- [ ] **Sidebar navigation**
  - คลิก Dashboard → ไปหน้า Dashboard
  - คลิก Profiles → ไปหน้า Profiles
  - คลิก Scripts → ไปหน้า Scripts
  - คลิก Backup & Restore → ไปหน้า Backup & Restore Center
  - คลิก Help → ไปหน้า Help

- [ ] **Active state highlighting**
  - หน้าไหน active ไฮไลต์สี accent
  - Active indicator แสดง

- [ ] **Glow animation**
  - Active button มี glow animation
  - Animation smooth

### 3.10 Error Scenarios

- [ ] **ไม่มี admin rights**
  - รัน app แบบไม่ใช่ admin
  - Warning แสดงตอนเริ่ม
  - Features ที่ต้องการ admin disabled

- [ ] **Disk เต็ม**
  - Simulate disk full
  - Error message แสดงชัดเจน
  - App ไม่ crash

- [ ] **Registry access denied**
  - Simulate registry access denied
  - Error message แสดงชัดเจน
  - Rollback ทำงาน

- [ ] **Profile apply failed**
  - Simulate profile apply failed
  - Partial success report
  - Failed tweaks แสดงรายการ

### 3.11 Performance & UI

- [ ] **Loading states**
  - ระหว่าง operations มี loading indicator
  - CircularProgress ทำงาน

- [ ] **Toast notifications**
  - Success toast แสดง (สีเขียว)
  - Error toast แสดง (สีแดง)
  - Warning toast แสดง (สีเหลือง)
  - Toast หายไปเองหลัง 3 วินาที

- [ ] **View transitions**
  - สลับ views นุ่มนวล
  - ไม่มี flickering

- [ ] **Responsive layout**
  - Resize window
  - Layout adapt ตามขนาด
  - Scrollbars แสดงเมื่อจำเป็น

---

## ส่วนที่ 4: Performance Testing (การทดสอบประสิทธิภาพ)

Performance testing คือการทดสอบว่า app ทำงานได้ดีแค่ไหนกับข้อมูลจำนวนมาก

### 4.1 Large Backup Count

**Test Scenario:**
```python
def test_100_backups():
    """ทดสอบกับ backups 100 รายการ"""
    # Arrange
    mgr = BackupManager()

    # Act - Create 100 backups
    for i in range(100):
        mgr.create_backup(f"backup_{i}")

    # Measure
    start_time = time.time()
    backups = mgr.get_all_backups()
    load_time = time.time() - start_time

    # Assert
    assert len(backups) == 100
    assert load_time < 2.0  # ควรโหลดภายใน 2 วินาที
```

**การรัน:**
```bash
cd clutchg/tests/performance
python test_large_backups.py
```

### 4.2 Large Registry Export

**Test Scenario:**
```python
def test_large_registry_export():
    """ทดสอบ export registry ขนาดใหญ่"""
    # Arrange
    mgr = BackupManager()

    # Act - Create backup with large registry
    start_time = time.time()
    backup = mgr.create_backup("large_backup")
    export_time = time.time() - start_time

    # Measure file size
    file_size = backup.registry_backup.stat().st_size / (1024 * 1024)  # MB

    # Assert
    assert export_time < 30.0  # ควร export ภายใน 30 วินาที
    assert file_size < 50  # ไม่ควรเกิน 50 MB
```

### 4.3 Memory Usage

**Test Scenario:**
```python
def test_memory_leak():
    """ทดสอบ memory leak"""
    # Arrange
    app = ClutchGApp()

    # Measure initial memory
    process = psutil.Process()
    initial_mem = process.memory_info().rss / (1024 * 1024)  # MB

    # Act - Switch views 100 times
    for i in range(100):
        app.switch_view("dashboard")
        app.switch_view("profiles")
        app.switch_view("scripts")

    # Measure final memory
    final_mem = process.memory_info().rss / (1024 * 1024)  # MB
    mem_increase = final_mem - initial_mem

    # Assert
    assert mem_increase < 50  # เพิ่มไม่เกิน 50 MB
```

### 4.4 Startup Time

**Test Scenario:**
```python
def test_startup_time():
    """ทดสอบเวลาเปิด app"""
    # Act
    start_time = time.time()
    app = ClutchGApp()
    startup_time = time.time() - start_time

    # Assert
    assert startup_time < 3.0  # ควรเปิดภายใน 3 วินาที

    app.destroy()
```

### 4.5 Timeline Rendering

**Test Scenario:**
```python
def test_timeline_with_1000_items():
    """ทดสอบ timeline กับ 1000 items"""
    # Arrange
    recorder = FlightRecorder()

    # Act - Add 1000 tweaks
    for i in range(1000):
        recorder.record_tweak({"name": f"Tweak_{i}"}, "SUCCESS")

    # Measure rendering time
    start_time = time.time()
    timeline = Timeline(recorder.get_timeline_data())
    render_time = time.time() - start_time

    # Assert
    assert render_time < 1.0  # ควร render ภายใน 1 วินาที
```

---

## ส่วนที่ 5: Test Coverage Goals (เป้าหมายการครอบคลุม)

### 5.1 Target Coverage

| ประเภท | เป้าหมาย | ปัจจุบัน | สถานะ |
|-------|----------|----------|--------|
| Unit Tests | 80%+ | TBD | ⏳ |
| Integration Tests | 60%+ | TBD | ⏳ |
| Manual Tests | 100% | TBD | ⏳ |

### 5.2 Critical Paths (เส้นทางสำคัญที่ต้อง test 100%)

1. **Create Backup → View → Restore**
   - ✅ Create backup สำเร็จ
   - ✅ Backup แสดงใน list
   - ✅ Restore สำเร็จ
   - ✅ System กลับสู่สถานะเดิม

2. **Apply Profile**
   - ✅ เลือก profile
   - ✅ Confirm warnings
   - ✅ Backup สร้างอัตโนมัติ
   - ✅ Tweak apply สำเร็จ
   - ✅ Rollback ถ้า fail

3. **Timeline → Undo**
   - ✅ Timeline แสดง tweaks
   - ✅ Click เพื่อดู details
   - ✅ Undo สำเร็จ
   - ✅ System กลับสู่สถานะเดิม

---

## ส่วนที่ 6: Continuous Testing (การทดสอบอย่างต่อเนื่อง)

### 6.1 Pre-commit Checks

ก่อน commit code ใหม่:

```bash
# 1. Run unit tests
cd clutchg
python -m pytest tests/unit/ -v

# 2. Run integration tests
python -m pytest tests/integration/ -v

# 3. Check code style
flake8 src/

# 4. Run type checker
mypy src/

# 5. Manual smoke test
cd src
python app_minimal.py
# ทดสอบฟีเจอร์ที่แก้ไข
```

### 6.2 Pre-release Checklist

ก่อน release version ใหม่:

- [ ] Unit tests ผ่านทั้งหมด
- [ ] Integration tests ผ่านทั้งหมด
- [ ] Manual testing checklist ผ่านครบ
- [ ] Performance tests ผ่าน
- [ ] ไม่มี critical bugs
- [ ] Documentation อัปเดตแล้ว
- [ ] Changelog เขียนแล้ว
- [ ] Test บน Windows 10 และ Windows 11
- [ ] Test กับ Python 3.11, 3.12

---

## ส่วนที่ 7: Bug Reporting Template (รูปแบบการรายงาน bug)

เมื่อพบ bug ให้รายงานตาม template นี้:

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
3. [ขั้นตอนที่ 3]

**Expected Behavior:**
[ที่คาดหวังให้เกิด]

**Actual Behavior:**
[ที่เกิดขึ้นจริง]

**Screenshots/Logs:**
[แนบ screenshot หรือ log file]

**Severity:**
- [ ] Critical (app crash)
- [ ] High (feature ใช้ไม่ได้)
- [ ] Medium (feature ใช้ได้แต่มีปัญหา)
- [ ] Low (cosmetic issues)
```

---

## ส่วนที่ 8: Test Execution Schedule (กำหนดการทดสอบ)

### 8.1 Daily Tests (ทุกวัน)

- Run unit tests
- Smoke test ฟีเจอร์หลัก
- Check ว่าไม่มี regressions

### 8.2 Weekly Tests (ทุกสัปดาห์)

- Run integration tests
- Manual testing ของฟีเจอร์ใหม่
- Performance sanity check

### 8.3 Release Tests (ก่อน release)

- Full test suite (unit + integration)
- Complete manual testing checklist
- Performance tests
- Cross-version testing (Win10/Win11)

---

## เอกสารอ้างอิง (References)

- `09-final-architecture.md` - Architecture specification
- `clutchg_technical_spec.md` - Technical spec ของ ClutchG
- `14-testing-checklist.md` - Testing checklist แบบย่อ
- `11-development-plan.md` - แผนพัฒนา (ภาษาไทย)

---

**เอกสารนี้เป็นส่วนหนึ่งของ ClutchG Project**
**Version:** 1.0 | **Last Updated:** 6 กุมภาพันธ์ 2026

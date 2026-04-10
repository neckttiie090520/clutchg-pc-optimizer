# 11 — ระบบคะแนนเครื่อง (PC Score System)

> **มาตรฐาน:** ISO/IEC 29110-5-1-2 — SI.O3 (Software Design) — เอกสารประกอบ
> **ETVX:** Entry=SDD v3.2 + SRS v3.1 → Task=อธิบายการทำงานระบบ PC Score → Verify=ตรงกับ source code → Exit=เอกสารอ้างอิง
> **โครงงาน:** ClutchG PC Optimizer v2.0
> **เวอร์ชัน:** 1.0 | **วันที่:** 2026-04-06 | **ผู้จัดทำ:** nextzus
> **อ้างอิง:** 02-SRS.md (FR-SD-05 ~ FR-SD-07), 03-SDD.md §2.1.5, Appendix-A-UML-Diagrams.md

---

## สารบัญ (Table of Contents)

1. [บทนำ (Introduction)](#1-บทนำ-introduction)
2. [สถาปัตยกรรมระบบ (System Architecture)](#2-สถาปัตยกรรมระบบ-system-architecture)
3. [แหล่งข้อมูล Benchmark (Benchmark Data Source)](#3-แหล่งข้อมูล-benchmark-benchmark-data-source)
4. [อัลกอริทึมการให้คะแนน (Scoring Algorithm)](#4-อัลกอริทึมการให้คะแนน-scoring-algorithm)
5. [Fuzzy Matching Engine](#5-fuzzy-matching-engine)
6. [การจำแนก Tier (Tier Classification)](#6-การจำแนก-tier-tier-classification)
7. [การแนะนำ Profile (Profile Recommendation)](#7-การแนะนำ-profile-profile-recommendation)
8. [การแสดงผล GUI (GUI Presentation)](#8-การแสดงผล-gui-gui-presentation)
9. [Data Flow ทั้งระบบ (End-to-End Flow)](#9-data-flow-ทั้งระบบ-end-to-end-flow)
10. [Traceability (ความสอดคล้องกับ SRS)](#10-traceability-ความสอดคล้องกับ-srs)
11. [ข้อจำกัดและข้อควรรู้ (Limitations & Notes)](#11-ข้อจำกัดและข้อควรรู้-limitations--notes)

---

## 1. บทนำ (Introduction)

### 1.1 วัตถุประสงค์

ระบบ PC Score เป็นฟีเจอร์หลักของ ClutchG ที่ **ให้คะแนนเครื่องคอมพิวเตอร์ตาม spec hardware** (CPU, GPU, RAM, Storage) เพื่อ:

1. แสดงภาพรวมความสามารถของเครื่องเป็นตัวเลข 0–100
2. จำแนกเครื่องเป็น Tier (Entry / Mid / High / Enthusiast)
3. แนะนำ Optimization Profile ที่เหมาะสม (SAFE / COMPETITIVE / EXTREME)

### 1.2 ไฟล์ที่เกี่ยวข้อง (Related Files)

| Layer | ไฟล์ | LOC | หน้าที่ |
|-------|------|-----|---------|
| Data | `core/benchmark_database.py` | ~450 | ฐานข้อมูล PassMark scores + fuzzy matching |
| Core | `core/system_info.py` | ~434 | Hardware detection + scoring + tier calculation |
| Core | `core/tweak_registry.py` | L1158-1183 | `suggest_preset()` — แนะนำ profile จาก score |
| App | `app_minimal.py` | L134-161 | Async detection thread + callback |
| GUI | `gui/views/dashboard_minimal.py` | L192-234 | วงแหวนคะแนน (Circular Score Ring) |
| GUI | `gui/views/scripts_minimal.py` | L1089-1188 | แสดง recommendation hero card |
| GUI | `gui/theme.py` | L578-586 | ฟังก์ชันกำหนดสี `get_score_color()` |
| GUI | `gui/components/circular_progress.py` | ~266 | Circular progress ring widget |

---

## 2. สถาปัตยกรรมระบบ (System Architecture)

### 2.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                          │
│  ┌──────────────────────┐    ┌────────────────────────────────┐    │
│  │  DashboardView       │    │  ScriptsView                   │    │
│  │  • CircularProgress  │    │  • Recommendation Hero Card    │    │
│  │  • Score Ring (120px)│    │  • "Score: XX — reason"        │    │
│  └──────────┬───────────┘    └──────────────┬─────────────────┘    │
│             │                               │                      │
├─────────────┼───────────────────────────────┼──────────────────────┤
│             ▼           App Controller      ▼                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  ClutchGApp                                              │      │
│  │  • detect_system() → threading.Thread                    │      │
│  │  • _on_detection_complete(profile) → refresh dashboard   │      │
│  │  • system_profile: SystemProfile                         │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                      │
├─────────────────────────────┼──────────────────────────────────────┤
│                             ▼          Core Layer                  │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │  SystemDetector                                          │      │
│  │  • detect_all() → SystemProfile                          │      │
│  │  • detect_cpu() → CPUInfo (score 0-30)                   │      │
│  │  • detect_gpu() → GPUInfo (score 0-30)                   │      │
│  │  • detect_ram() → RAMInfo (score 0-20)                   │      │
│  │  • detect_storage() → StorageInfo (score 0-10)           │      │
│  │  • calculate_tier(score) → str                           │      │
│  │  • recommend_profile(system) → str                       │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                      │
│  ┌──────────────────────────▼───────────────────────────────┐      │
│  │  BenchmarkDatabase (Singleton)                           │      │
│  │  • CPU_DATABASE: 88+ entries (PassMark CPU Mark)         │      │
│  │  • GPU_DATABASE: 70+ entries (PassMark G3D Mark)         │      │
│  │  • get_cpu_score(name) → (normalized, raw, matched)      │      │
│  │  • get_gpu_score(name) → (normalized, raw, vram, matched)│      │
│  │  • _fuzzy_match(name, candidates) → best_match           │      │
│  └──────────────────────────┬───────────────────────────────┘      │
│                             │                                      │
├─────────────────────────────┼──────────────────────────────────────┤
│                             ▼     Hardware Detection Layer         │
│  ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌──────────────────┐     │
│  │ py-cpuinfo │ │  psutil  │ │   WMI   │ │   nvidia-smi     │     │
│  │ (CPU name) │ │(cores,   │ │(CPU/GPU │ │(GPU name, VRAM,  │     │
│  │            │ │ RAM, disk│ │ details)│ │ driver version)  │     │
│  └────────────┘ └──────────┘ └─────────┘ └──────────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Design Rationale

- **Benchmark-based scoring** — ใช้ข้อมูล PassMark จริงแทนสูตรง่ายๆ (เช่น cores × 3) ทำให้แยกแยะ CPU/GPU ที่มี core count ใกล้กันแต่ performance ต่างกันได้
- **Fuzzy matching** — ชื่อ hardware จาก driver/WMI มักไม่ตรงกับชื่อใน database พอดี จึงต้อง match แบบ approximate
- **Singleton BenchmarkDatabase** — โหลดครั้งเดียว ใช้ซ้ำตลอด session
- **Async detection** — การตรวจจับ hardware (โดยเฉพาะ WMI, nvidia-smi) ใช้เวลา 2-5 วินาที จึงทำใน background thread

---

## 3. แหล่งข้อมูล Benchmark (Benchmark Data Source)

### 3.1 CPU Database

- **Source:** PassMark CPU Mark (ข้อมูล 2024-2025)
- **จำนวน:** 88+ entries
- **Format:** `"CPU Name": (PassMark Score, Tier)`
- **Score Range:** 3,500 (Celeron G6900) — 65,000 (Ryzen 9 9950X / i9-14900KS)
- **Coverage:**

| ตระกูล | รุ่นที่ครอบคลุม |
|--------|---------------|
| AMD Ryzen | 3000, 5000, 7000, 9000 series |
| Intel Core | 10th — 14th Generation |
| Laptop CPUs | Ryzen Mobile, Intel H/U/P series |
| Budget | Celeron, Pentium, Athlon |

### 3.2 GPU Database

- **Source:** PassMark G3D Mark
- **จำนวน:** 70+ entries
- **Format:** `"GPU Name": (G3D Mark Score, VRAM GB, Tier)`
- **Score Range:** 1,500 (Intel UHD 630/730) — 55,000 (RTX 5090)
- **Coverage:**

| Vendor | รุ่นที่ครอบคลุม |
|--------|---------------|
| NVIDIA | RTX 50/40/30/20 series, GTX 16/10 series |
| AMD | RX 7000, 6000, 5000 series |
| Intel | Arc A-series, Integrated UHD |

### 3.3 ค่าสูงสุดสำหรับ Normalization

| Component | Max Reference Score | Source |
|-----------|-------------------|--------|
| CPU | 65,000 (`CPU_MAX_SCORE`) | PassMark CPU Mark — flagship desktop CPUs |
| GPU | 55,000 (`GPU_MAX_SCORE`) | PassMark G3D Mark — flagship GPUs |

---

## 4. อัลกอริทึมการให้คะแนน (Scoring Algorithm)

### 4.1 สูตรหลัก (Master Formula)

```
Total Score = CPU Score + GPU Score + RAM Score + Storage Score
            = (0-30)   + (0-30)   + (0-20)   + (0-10)
            = 0-90 (practical max)
```

> **หมายเหตุ:** Dataclass ระบุ total_score เป็น 0-100 แต่ในทางปฏิบัติคะแนนสูงสุดที่เป็นไปได้คือ 90 (30+30+20+10)

### 4.2 CPU Score (0-30) — Benchmark-Based

**ไฟล์:** `core/benchmark_database.py` L243-262

```python
def get_cpu_score(self, cpu_name: str) -> Tuple[int, int, str]:
    matched_name = self._fuzzy_match(cpu_name, list(self.cpu_data.keys()))
    if matched_name:
        raw_score, tier = self.cpu_data[matched_name]
        normalized = min(30, int((raw_score / self.CPU_MAX_SCORE) * 30))
        return (normalized, raw_score, matched_name)
    return (15, 0, "Unknown CPU")  # Default fallback
```

**สูตร:**
```
CPU Score = min(30, floor((PassMark_CPU_Mark / 65,000) × 30))
```

- PassMark < 65,000 → คะแนนตามสัดส่วน
- PassMark ≥ 65,000 → ได้ 30 เต็ม
- ไม่พบใน database → ได้ 15 (mid-range default)

### 4.3 GPU Score (0-30) — Benchmark-Based

**ไฟล์:** `core/benchmark_database.py` L264-283

```python
def get_gpu_score(self, gpu_name: str) -> Tuple[int, int, int, str]:
    matched_name = self._fuzzy_match(gpu_name, list(self.gpu_data.keys()))
    if matched_name:
        raw_score, vram, tier = self.gpu_data[matched_name]
        normalized = min(30, int((raw_score / self.GPU_MAX_SCORE) * 30))
        return (normalized, raw_score, vram, matched_name)
    return (10, 0, 0, "Unknown GPU")  # Default fallback
```

**สูตร:**
```
GPU Score = min(30, floor((PassMark_G3D_Mark / 55,000) × 30))
```

- ไม่พบใน database → ได้ 10 (lower default เพราะ GPU ที่ไม่รู้จักมักเป็น integrated)

### 4.4 RAM Score (0-20) — Capacity-Based

**ไฟล์:** `core/system_info.py` L291-292

```python
score = min(20, int(total_gb / 2))
```

**สูตร:**
```
RAM Score = min(20, floor(total_gb / 2))
```

| RAM (GB) | Score |
|----------|-------|
| 4 | 2 |
| 8 | 4 |
| 16 | 8 |
| 32 | 16 |
| 40+ | 20 (max) |

> **หมายเหตุ:** ไม่ได้พิจารณา DDR type หรือ speed ในการคำนวณ — ใช้เฉพาะขนาด

### 4.5 Storage Score (0-10) — Type-Based

**ไฟล์:** `core/system_info.py` L382

```python
score = 10 if primary_type in ["nvme", "ssd"] else (5 if primary_type == "hdd" else 3)
```

| ประเภท Storage | Score |
|---------------|-------|
| NVMe / SSD | 10 |
| HDD | 5 |
| Unknown | 3 |

---

## 5. Fuzzy Matching Engine

### 5.1 ปัญหาที่แก้

ชื่อ hardware จากระบบ (เช่น WMI, nvidia-smi) มักไม่ตรงกับชื่อใน database:

| แหล่งข้อมูล | ชื่อที่ได้ | ชื่อใน Database |
|-------------|----------|----------------|
| WMI | `AMD Ryzen 7 7800X3D 8-Core Processor` | `AMD Ryzen 7 7800X3D` |
| nvidia-smi | `NVIDIA GeForce RTX 4070` | `GeForce RTX 4070` |
| cpuinfo | `12th Gen Intel(R) Core(TM) i7-12700K` | `Intel Core i7-12700K` |

### 5.2 ขั้นตอน 3 ระดับ (Three-Stage Matching)

**ไฟล์:** `core/benchmark_database.py` L285-350

```
Stage 1: Exact Match (case-insensitive)
    ↓ ไม่เจอ
Stage 2: Key Parts Match (regex-based model number extraction)
    ↓ ไม่เจอ
Stage 3: difflib.get_close_matches(cutoff=0.5)
    ↓ ไม่เจอ
Return: None (ใช้ default score)
```

**Stage 1 — Exact Match:**
- เปรียบเทียบ string ทั้งหมดแบบ case-insensitive
- เร็วที่สุด, ใช้ได้กับชื่อที่ตรงเป๊ะ

**Stage 2 — Key Parts Match:**
- ดึง model number ด้วย regex (เช่น `7800X3D`, `RTX 4070`, `i7-12700K`)
- จับคู่ vendor keyword (AMD/Intel/NVIDIA) + model number
- แก้ปัญหา prefix/suffix ที่ต่างกัน

**Stage 3 — Fuzzy Match:**
- ใช้ `difflib.get_close_matches()` จาก Python standard library
- cutoff = 0.5 (ต้องคล้ายกัน ≥ 50%)
- ทนทานต่อ typo และ naming variation

---

## 6. การจำแนก Tier (Tier Classification)

**ไฟล์:** `core/system_info.py` L403-412

```python
def calculate_tier(self, total_score: int) -> str:
    if total_score >= 70:
        return "enthusiast"
    elif total_score >= 50:
        return "high"
    elif total_score >= 30:
        return "mid"
    else:
        return "entry"
```

| ช่วงคะแนน | Tier | คำอธิบาย |
|-----------|------|---------|
| 70-90 | Enthusiast | เครื่องระดับสูง ปรับแต่งได้เต็มที่ |
| 50-69 | High | เครื่องแรงพอสมควร เหมาะกับ gaming optimization |
| 30-49 | Mid | เครื่องระดับกลาง ปรับแต่งอย่างระวัง |
| 0-29 | Entry | เครื่องระดับเริ่มต้น ใช้เฉพาะ SAFE tweaks |

---

## 7. การแนะนำ Profile (Profile Recommendation)

### 7.1 SystemDetector.recommend_profile()

**ไฟล์:** `core/system_info.py` L414-434

```python
def recommend_profile(self, system: SystemProfile) -> str:
    if system.form_factor == "laptop":
        return "SAFE"           # Laptop ใช้ SAFE เสมอ (ป้องกัน thermal)
    if system.tier == "enthusiast":
        return "COMPETITIVE"    # ไม่แนะนำ EXTREME อัตโนมัติ
    elif system.tier in ["high", "mid"]:
        return "COMPETITIVE"
    else:
        return "SAFE"
```

### 7.2 TweakRegistry.suggest_preset()

**ไฟล์:** `core/tweak_registry.py` L1158-1183

```python
def suggest_preset(self, system_profile) -> Dict[str, Any]:
    total_score = getattr(system_profile, "total_score", 50)
    form_factor = getattr(system_profile, "form_factor", "desktop")
    ram_gb = getattr(system_profile.ram, "total_gb", 16)

    if total_score >= 80 and form_factor == "desktop" and ram_gb >= 16:
        preset = "extreme"
    elif total_score >= 50 and ram_gb >= 8:
        preset = "competitive"
    else:
        preset = "safe"

    return {"preset": preset, "reason": reason, "total_score": total_score, ...}
```

### 7.3 ตารางสรุป Recommendation Logic

| เงื่อนไข | ผลลัพธ์ |
|----------|---------|
| Laptop (มี battery) | **SAFE** เสมอ (ไม่สนใจ score) |
| Desktop + Score ≥ 80 + RAM ≥ 16GB | **EXTREME** |
| Desktop + Score ≥ 50 + RAM ≥ 8GB | **COMPETITIVE** |
| Desktop + Score < 50 หรือ RAM < 8GB | **SAFE** |

> **Safety note:** ระบบไม่เคยแนะนำ EXTREME ให้ laptop และไม่แนะนำ EXTREME อัตโนมัติจาก `recommend_profile()` — จะแนะนำได้จาก `suggest_preset()` เท่านั้นเมื่อเข้าเงื่อนไขครบ

---

## 8. การแสดงผล GUI (GUI Presentation)

### 8.1 Dashboard — วงแหวนคะแนน (Circular Score Ring)

**ไฟล์:** `gui/views/dashboard_minimal.py` L192-234

```
┌─────────────────────────────────────┐
│         ┌─────────┐                 │
│         │   ╭───╮ │                 │
│         │   │75 │ │  ← CircularProgress widget    │
│         │   ╰───╯ │     120px diameter             │
│         │  SYSTEM  │     12px ring thickness        │
│         │  SCORE   │     Figtree 28pt bold          │
│         └─────────┘                 │
│                                     │
│  CPU: AMD Ryzen 7 7800X3D          │
│  GPU: RTX 4070                      │
│  RAM: 32 GB DDR5                    │
│  Storage: NVMe SSD                  │
└─────────────────────────────────────┘
```

**สีของวงแหวนตาม score:**

| Score | สี (Dashboard) | หมายเหตุ |
|-------|----------------|---------|
| ≥ 80 | `success` (green) | Excellent |
| ≥ 50 | `info` (blue/accent) | Good |
| < 50 | `danger` (red) | Low |

### 8.2 get_score_color() — 4-Tier Color System

**ไฟล์:** `gui/theme.py` L578-586

```python
def get_score_color(score: int) -> str:
    if score >= 80: return "#22C55E"  # Excellent (green)
    if score >= 60: return "#57c8ff"  # Good (blue/accent)
    if score >= 40: return "#F59E0B"  # Average (amber)
    return "#EF4444"                   # Low (red)
```

| ช่วงคะแนน | สี | Hex | ชื่อ |
|-----------|-----|-----|------|
| 80-100 | 🟢 Green | `#22C55E` | Excellent |
| 60-79 | 🔵 Blue | `#57c8ff` | Good |
| 40-59 | 🟡 Amber | `#F59E0B` | Average |
| 0-39 | 🔴 Red | `#EF4444` | Low |

### 8.3 Scripts View — Recommendation Card

**ไฟล์:** `gui/views/scripts_minimal.py` L1181-1182

แสดงข้อความแนะนำ profile พร้อมคะแนน:

- EN: `"Recommended for your system (Score: {score}) — {reason}"`
- TH: `"แนะนำสำหรับเครื่องของคุณ (คะแนน: {score}) — {reason}"`

---

## 9. Data Flow ทั้งระบบ (End-to-End Flow)

### 9.1 Sequence Diagram

```
User                ClutchGApp           SystemDetector    BenchmarkDB     Hardware APIs
 │  เปิดแอป           │                      │                │              │
 │──────────────────►│                      │                │              │
 │                   │  detect_system()     │                │              │
 │                   │  (daemon thread)     │                │              │
 │                   │─────────────────────►│                │              │
 │                   │                      │  nvidia-smi    │              │
 │                   │                      │─────────────────────────────►│
 │                   │                      │  ◄── GPU name, VRAM          │
 │                   │                      │                │              │
 │                   │                      │  cpuinfo/WMI   │              │
 │                   │                      │─────────────────────────────►│
 │                   │                      │  ◄── CPU name, cores         │
 │                   │                      │                │              │
 │                   │                      │  get_cpu_score(name)         │
 │                   │                      │───────────────►│              │
 │                   │                      │  ◄── (15, 34543, "Ryzen 7") │
 │                   │                      │                │              │
 │                   │                      │  get_gpu_score(name)         │
 │                   │                      │───────────────►│              │
 │                   │                      │  ◄── (12, 23500, 8, "RTX")  │
 │                   │                      │                │              │
 │                   │                      │  RAM: min(20, 32/2) = 16    │
 │                   │                      │  Storage: NVMe → 10         │
 │                   │                      │  Total: 15+12+16+10 = 53    │
 │                   │                      │  Tier: "high"               │
 │                   │                      │                │              │
 │                   │  ◄── SystemProfile   │                │              │
 │                   │  window.after(0)     │                │              │
 │                   │  _on_detection_complete               │              │
 │                   │                      │                │              │
 │  ◄── Dashboard   │                      │                │              │
 │  Score Ring: 53  │                      │                │              │
 │  Tier: High      │                      │                │              │
 │  Color: Blue     │                      │                │              │
```

### 9.2 ลำดับเหตุการณ์ (Step-by-Step)

| ขั้นตอน | ที่ไหน | ทำอะไร |
|---------|--------|--------|
| 1 | `app_minimal.py` L134 | `detect_system()` สร้าง daemon thread |
| 2 | `system_info.py` `detect_all()` | เรียก detect methods ทั้ง 5 ตัว |
| 3 | `system_info.py` `detect_cpu()` | ใช้ cpuinfo → psutil → WMI fallback chain |
| 4 | `benchmark_database.py` `get_cpu_score()` | Fuzzy match ชื่อ CPU → normalize คะแนน |
| 5 | `system_info.py` `detect_gpu()` | ใช้ nvidia-smi → WMI fallback |
| 6 | `benchmark_database.py` `get_gpu_score()` | Fuzzy match ชื่อ GPU → normalize คะแนน |
| 7 | `system_info.py` `detect_ram()` | ใช้ psutil → `min(20, total_gb/2)` |
| 8 | `system_info.py` `detect_storage()` | ใช้ WMI Get-PhysicalDisk → psutil fallback |
| 9 | `system_info.py` L125-131 | รวมคะแนน: `cpu + gpu + ram + storage` |
| 10 | `system_info.py` `calculate_tier()` | จำแนก tier จาก total_score |
| 11 | `app_minimal.py` L150 | `window.after(0)` กลับ main thread |
| 12 | `dashboard_minimal.py` L192 | แสดง CircularProgress + score + tier |

---

## 10. Traceability (ความสอดคล้องกับ SRS)

| SRS Requirement | คำอธิบาย | Source File | ส่วนในเอกสารนี้ |
|-----------------|---------|-------------|----------------|
| FR-SD-05 | คำนวณ System Score (0-100) จาก CPU(30)+GPU(30)+RAM(20)+Storage(10) | `core/system_info.py` L115-148 | §4 Scoring Algorithm |
| FR-SD-06 | จำแนก Tier: entry/mid/high/enthusiast | `core/system_info.py` L349-358 | §6 Tier Classification |
| FR-SD-07 | แนะนำ Profile ตาม Tier + Form Factor | `core/system_info.py` L360-380 | §7 Profile Recommendation |
| FR-UI-01 | Dashboard แสดง system score + tier | `gui/views/dashboard_minimal.py` L192-234 | §8 GUI Presentation |
| UC-02 | View System Score & Tier | ทั้งระบบ | §9 End-to-End Flow |

---

## 11. ข้อจำกัดและข้อควรรู้ (Limitations & Notes)

### 11.1 ข้อจำกัดของระบบปัจจุบัน

| ข้อจำกัด | รายละเอียด | ผลกระทบ |
|----------|-----------|---------|
| Static database | ฐานข้อมูล benchmark ฝังใน source code ไม่ auto-update | Hardware รุ่นใหม่หลัง 2025 อาจไม่มีใน database |
| RAM scoring ไม่ดู type/speed | DDR4-2400 กับ DDR5-6000 ได้คะแนนเท่ากันถ้าขนาดเท่ากัน | คะแนน RAM ไม่สะท้อน performance ที่แท้จริง |
| Max score = 90 | สูตรรวม 30+30+20+10 = 90 ไม่ถึง 100 | ไม่มีเครื่องไหนจะได้ 100 คะแนน |
| Fuzzy match cutoff 0.5 | อาจ match ผิดถ้าชื่อ hardware คล้ายกันมาก | ควรตรวจสอบ matched_name ที่ return กลับมา |
| Laptop → SAFE เสมอ | ไม่พิจารณาว่า laptop บาง spec สูงมาก | Gaming laptop ถูกจำกัดที่ SAFE |

### 11.2 Color Threshold Inconsistency

Dashboard score ring ใช้ 3 ระดับสี (80/50) แต่ `get_score_color()` ใช้ 4 ระดับ (80/60/40):

| ตำแหน่ง | Thresholds | จำนวนระดับ |
|---------|-----------|-----------|
| Dashboard ring | 80, 50 | 3 (green/blue/red) |
| `get_score_color()` | 80, 60, 40 | 4 (green/blue/amber/red) |
| CircularProgress component | 80, 60, 40 | 4 (มี helper ของตัวเอง) |

### 11.3 score_context ยังไม่ได้ใช้

ข้อความ `"Score out of 100 — higher is better"` / `"คะแนนจาก 100 — ยิ่งสูงยิ่งดี"` กำหนดใน `UI_STRINGS` ของ Dashboard แต่ยังไม่ได้แสดงผลใน UI ปัจจุบัน

---

## ตัวอย่างการคำนวณ (Calculation Examples)

### ตัวอย่าง 1: เครื่อง Mid-Range Gaming

```
Hardware: AMD Ryzen 5 5600X + RTX 3060 + 16GB DDR4 + NVMe SSD

CPU:  PassMark 22,182  → min(30, floor((22182/65000) × 30)) = min(30, 10) = 10
GPU:  G3D Mark 17,000  → min(30, floor((17000/55000) × 30)) = min(30, 9)  = 9
RAM:  16 GB            → min(20, floor(16/2))                = min(20, 8)  = 8
SSD:  NVMe             → 10
────────────────────────────────────────────────────────────────────────
TOTAL = 10 + 9 + 8 + 10 = 37
Tier  = "mid" (30-49)
Profile = SAFE (37 < 50)
Color = Red (#EF4444) ← get_score_color
```

### ตัวอย่าง 2: เครื่อง Enthusiast

```
Hardware: Intel i9-14900KS + RTX 4090 + 64GB DDR5 + NVMe SSD

CPU:  PassMark 65,000  → min(30, floor((65000/65000) × 30)) = 30
GPU:  G3D Mark 39,000  → min(30, floor((39000/55000) × 30)) = min(30, 21) = 21
RAM:  64 GB            → min(20, floor(64/2))                = min(20, 32) = 20
SSD:  NVMe             → 10
────────────────────────────────────────────────────────────────────────
TOTAL = 30 + 21 + 20 + 10 = 81
Tier  = "enthusiast" (≥70)
Profile = EXTREME (81 ≥ 80, desktop, RAM ≥ 16GB)
Color = Green (#22C55E)
```

### ตัวอย่าง 3: Laptop พื้นฐาน

```
Hardware: Intel i5-1235U + Intel UHD + 8GB DDR4 + SSD

CPU:  PassMark 13,500  → min(30, floor((13500/65000) × 30)) = min(30, 6) = 6
GPU:  G3D Mark 1,500   → min(30, floor((1500/55000) × 30))  = min(30, 0) = 0
RAM:  8 GB             → min(20, floor(8/2))                 = min(20, 4) = 4
SSD:  SSD              → 10
────────────────────────────────────────────────────────────────────────
TOTAL = 6 + 0 + 4 + 10 = 20
Tier  = "entry" (<30)
Profile = SAFE (laptop → SAFE เสมอ ไม่สนใจ score)
Color = Red (#EF4444)
```

---

*เอกสารนี้สร้างจาก source code จริง (ตรวจสอบวันที่ 2026-04-06) เพื่อใช้เป็นเอกสารประกอบ 03-SDD.md §2.1.5 และ 02-SRS.md FR-SD-05~07*

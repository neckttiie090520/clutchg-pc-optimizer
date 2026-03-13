# ClutchG Scoring System

## Current Scoring Method

ปัจจุบัน ClutchG ใช้การคำนวณแบบ **Simple Weighted Score** ดังนี้:

### Score Breakdown (Total: 0-100)

| Component | Max Score | Calculation |
|-----------|-----------|-------------|
| **CPU** | 30 | `min(30, (cores * 3) + (threads * 0.5))` |
| **GPU** | 30 | `min(30, vram_gb * 3)` |
| **RAM** | 20 | `min(20, total_gb / 2)` |
| **Storage** | 20 | `min(20, score based on type)` |

### Example: Your System (Score: 75)

```
CPU:  AMD Ryzen 7 7800X3D (8C/16T)
      = (8 * 3) + (16 * 0.5) = 24 + 8 = 32 → capped at 30

GPU:  RTX 5060 (8GB VRAM)  
      = 8 * 3 = 24 score

RAM:  32GB
      = 32 / 2 = 16 score

Storage: SSD/NVMe
      = 10 score (could be higher)

TOTAL = 30 + 24 + 16 + 10 = 80 (แต่อาจมีการปรับ)
```

### Tier Classification

| Score Range | Tier |
|-------------|------|
| 0-30 | Entry |
| 31-50 | Mid |
| 51-75 | High |
| 76-100 | Enthusiast |

---

## ปัญหาของวิธีปัจจุบัน

1. **ไม่อิงข้อมูลจริง** - ใช้สูตรง่ายๆ ไม่ได้อ้างอิง benchmark จริง
2. **ไม่รู้จัก hardware รุ่นใหม่** - ไม่มี database ของ CPU/GPU
3. **ไม่แม่นยำ** - Ryzen 7 7800X3D กับ i3-10100 ได้คะแนนใกล้กัน (ถ้า core count ใกล้กัน)

---

## Hardware Benchmark Data Sources

### 1. PassMark (Recommended)

**URL:** https://www.passmark.com/products/pt_go/

**ข้อมูลที่มี:**
- CPU Benchmark scores (10,000+ CPUs)
- GPU Benchmark scores (3,000+ GPUs)
- Updated daily

**วิธีใช้:**
```python
# Licensed CSV data (ต้องซื้อ license)
# Sample: passmark.com -> Hardware Benchmark Charts -> Export

# หรือใช้ Kaggle datasets (free):
# https://www.kaggle.com/datasets/alanjo/cpu-benchmarks
```

**Sample Data:**
```csv
cpuName,cpuMark,cpuValue,socket
AMD Ryzen 7 7800X3D,34543,23.47,AM5
Intel Core i7-14700K,59782,20.12,FCLGA1700
AMD Ryzen 9 7950X,63326,18.83,AM5
```

---

### 2. Geekbench Browser

**URL:** https://browser.geekbench.com/

**ข้อมูลที่มี:**
- Single-core & Multi-core scores
- User-submitted results
- Cross-platform (Mac, Windows, Linux, Mobile)

**Python Library (Unofficial):**
```bash
pip install geekbench-browser
```

```python
# https://github.com/lkubb/geekbench-browser
from geekbench import GeekbenchBrowser
gb = GeekbenchBrowser()
results = gb.search("AMD Ryzen 7 7800X3D")
```

---

### 3. UL Solutions API (3DMark/PCMark)

**URL:** https://benchmarks.ul.com/api/

**ข้อมูลที่มี:**
- Gaming benchmarks
- GPU performance
- System requirements

**API Example:**
```python
import requests
api = "https://benchmarks.ul.com/api/v1"
response = requests.get(f"{api}/cpus")
```

---

### 4. Kaggle Datasets (Free)

**CPU Benchmarks:**
- https://www.kaggle.com/datasets/alanjo/cpu-benchmarks
- https://www.kaggle.com/datasets/iliassekkaf/computerparts

**GPU Benchmarks:**
- https://www.kaggle.com/datasets/alanjo/graphics-card-benchmarks

**Usage:**
```python
import pandas as pd

# Download and load
cpu_df = pd.read_csv("cpu_benchmark.csv")

# Lookup score
def get_cpu_score(cpu_name):
    matches = cpu_df[cpu_df['cpuName'].str.contains(cpu_name, case=False)]
    if not matches.empty:
        return matches.iloc[0]['cpuMark']
    return None

score = get_cpu_score("Ryzen 7 7800X3D")
print(f"PassMark Score: {score}")  # ~34543
```

---

## Proposed Improved Scoring System

### Implementation Plan

```python
# 1. Download benchmark data
# 2. Create local database/JSON
# 3. Fuzzy match hardware names
# 4. Normalize scores to 0-100

class BenchmarkDatabase:
    def __init__(self):
        self.cpu_data = self.load_cpu_benchmarks()
        self.gpu_data = self.load_gpu_benchmarks()
    
    def load_cpu_benchmarks(self):
        # Load from CSV or JSON
        return {
            "AMD Ryzen 7 7800X3D": {"score": 34543, "tier": "enthusiast"},
            "Intel Core i7-14700K": {"score": 59782, "tier": "enthusiast"},
            "AMD Ryzen 5 5600X": {"score": 22182, "tier": "high"},
            # ... more CPUs
        }
    
    def get_cpu_score(self, cpu_name: str) -> int:
        # Fuzzy matching
        from difflib import get_close_matches
        names = list(self.cpu_data.keys())
        matches = get_close_matches(cpu_name, names, n=1, cutoff=0.6)
        
        if matches:
            raw_score = self.cpu_data[matches[0]]["score"]
            # Normalize to 0-30 scale
            # Top CPU ~ 65000, so: (score / 65000) * 30
            return min(30, int((raw_score / 65000) * 30))
        return 15  # Default mid score
```

---

## Creating Your Own Benchmark Database

### Step 1: Download Data

```bash
# From Kaggle
kaggle datasets download -d alanjo/cpu-benchmarks
kaggle datasets download -d alanjo/graphics-card-benchmarks
```

### Step 2: Create JSON Database

```python
import pandas as pd
import json

# CPU
cpu_df = pd.read_csv("cpu_benchmark.csv")
cpu_db = {}
for _, row in cpu_df.iterrows():
    cpu_db[row['cpuName']] = {
        "score": row['cpuMark'],
        "value": row.get('cpuValue', 0),
        "cores": row.get('cores', 0)
    }

with open("cpu_database.json", "w") as f:
    json.dump(cpu_db, f)

# GPU
gpu_df = pd.read_csv("gpu_benchmark.csv")
gpu_db = {}
for _, row in gpu_df.iterrows():
    gpu_db[row['gpuName']] = {
        "score": row['G3Dmark'],
        "vram": row.get('vram', 0)
    }

with open("gpu_database.json", "w") as f:
    json.dump(gpu_db, f)
```

### Step 3: Integrate with ClutchG

```python
# In system_info.py
class SystemDetector:
    def __init__(self):
        self.benchmark_db = BenchmarkDatabase()
    
    def detect_cpu(self) -> CPUInfo:
        name = get_cpu_info()['brand_raw']
        
        # Use benchmark data for score
        score = self.benchmark_db.get_cpu_score(name)
        
        return CPUInfo(
            name=name,
            score=score,  # Real benchmark score!
            ...
        )
```

---

## Summary: Recommended Approach

| Method | Pros | Cons | Cost |
|--------|------|------|------|
| **Kaggle CSV** | Free, easy | May be outdated | Free |
| **PassMark License** | Official, daily updates | Expensive | $$$ |
| **Geekbench Scrape** | Multi-platform | Unofficial, ToS | Free |
| **Build Custom** | Full control | Time-consuming | Free |

### Quick Start Recommendation:

1. Download Kaggle datasets (free)
2. Create `cpu_database.json` and `gpu_database.json`
3. Use fuzzy matching for CPU/GPU lookup
4. Normalize scores to 0-100 scale

---

*Created: 2026-01-31*

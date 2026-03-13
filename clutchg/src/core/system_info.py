"""
System Information Detector
Detects hardware and system information for profile recommendations
"""

import platform
import subprocess
from dataclasses import dataclass

from utils.logger import get_logger

logger = get_logger(__name__)

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import wmi
    HAS_WMI = True
except ImportError:
    HAS_WMI = False

try:
    from cpuinfo import get_cpu_info
    HAS_CPUINFO = True
except ImportError:
    HAS_CPUINFO = False

# Benchmark database for hardware scoring
from core.benchmark_database import get_benchmark_db


@dataclass
class OSInfo:
    """Operating system information"""
    platform: str  # 'windows', 'linux', 'mac'
    version: str
    build: str
    architecture: str  # 'x64', 'arm64'


@dataclass
class CPUInfo:
    """CPU information"""
    name: str
    vendor: str  # 'intel', 'amd', 'other'
    cores: int
    threads: int
    base_clock: float  # MHz
    score: int  # 0-30


@dataclass
class GPUInfo:
    """GPU information"""
    name: str
    vendor: str  # 'nvidia', 'amd', 'intel', 'other'
    vram: int  # GB
    driver_version: str
    score: int  # 0-30


@dataclass
class RAMInfo:
    """RAM information"""
    total_gb: int
    type: str  # 'ddr3', 'ddr4', 'ddr5', 'unknown'
    speed: int  # MHz
    score: int  # 0-20


@dataclass
class StorageInfo:
    """Storage information"""
    primary_type: str  # 'hdd', 'ssd', 'nvme'
    total_gb: int
    score: int  # 0-10


@dataclass
class SystemProfile:
    """Complete system profile"""
    os: OSInfo
    cpu: CPUInfo
    gpu: GPUInfo
    ram: RAMInfo
    storage: StorageInfo
    form_factor: str  # 'desktop', 'laptop', 'unknown'
    tier: str  # 'entry', 'mid', 'high', 'enthusiast'
    total_score: int  # 0-100


class SystemDetector:
    """Detects system hardware and generates profile"""
    
    def __init__(self):
        """Initialize system detector"""
        self.wmi_conn = None
        if HAS_WMI:
            try:
                self.wmi_conn = wmi.WMI()
            except Exception:
                pass

        # Initialize benchmark database
        self.benchmark_db = get_benchmark_db()
    
    def detect_all(self) -> SystemProfile:
        """
        Detect all system information
        
        Returns:
            Complete system profile
        """
        os_info = self.detect_os()
        cpu_info = self.detect_cpu()
        gpu_info = self.detect_gpu()
        ram_info = self.detect_ram()
        storage_info = self.detect_storage()
        form_factor = self.detect_form_factor()
        
        # Calculate scores
        total_score = (
            cpu_info.score +
            gpu_info.score +
            ram_info.score +
            storage_info.score
        )
        
        tier = self.calculate_tier(total_score)
        
        return SystemProfile(
            os=os_info,
            cpu=cpu_info,
            gpu=gpu_info,
            ram=ram_info,
            storage=storage_info,
            form_factor=form_factor,
            tier=tier,
            total_score=total_score
        )
    
    def detect_os(self) -> OSInfo:
        """Detect operating system information"""
        system = platform.system().lower()
        
        if 'windows' in system:
            platform_name = 'windows'
            version = platform.version()
            build = platform.win32_ver()[1] if hasattr(platform, 'win32_ver') else 'unknown'
        else:
            platform_name = system
            version = platform.version()
            build = 'unknown'
        
        architecture = platform.machine()
        
        return OSInfo(
            platform=platform_name,
            version=version,
            build=build,
            architecture=architecture
        )
    
    def detect_cpu(self) -> CPUInfo:
        """Detect CPU information using cpuinfo library"""
        name = "Unknown CPU"
        cores = psutil.cpu_count(logical=False) if HAS_PSUTIL else 0
        threads = psutil.cpu_count(logical=True) if HAS_PSUTIL else 0
        base_clock = 0.0
        
        # Use cpuinfo for accurate CPU brand name
        if HAS_CPUINFO:
            try:
                info = get_cpu_info()
                name = info.get('brand_raw', 'Unknown CPU')
                # Get frequency if available
                if HAS_PSUTIL:
                    freq = psutil.cpu_freq()
                    if freq:
                        base_clock = freq.current / 1000  # MHz to GHz
            except Exception as e:
                logger.warning(f"cpuinfo error: {e}")
        
        # Fallback to WMI
        if name == "Unknown CPU" and self.wmi_conn:
            try:
                for cpu in self.wmi_conn.Win32_Processor():
                    name = cpu.Name or "Unknown CPU"
                    break
            except Exception:
                pass
        
        # Determine vendor
        vendor = 'other'
        name_lower = name.lower()
        if 'intel' in name_lower:
            vendor = 'intel'
        elif 'amd' in name_lower or 'ryzen' in name_lower:
            vendor = 'amd'
        elif 'apple' in name_lower or 'arm' in name_lower:
            vendor = 'apple'

        # Calculate score using benchmark database
        cpu_score, raw_score, matched_name = self.benchmark_db.get_cpu_score(name)
        score = cpu_score

        return CPUInfo(
            name=name,
            vendor=vendor,
            cores=cores,
            threads=threads,
            base_clock=base_clock,
            score=score
        )
    
    def detect_gpu(self) -> GPUInfo:
        """Detect GPU information using nvidia-smi or WMI fallback"""
        name = "Unknown GPU"
        vendor = "other"
        vram = 0
        driver_version = "unknown"
        
        # Try nvidia-smi directly (most reliable for NVIDIA)
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(',')
                if len(parts) >= 2:
                    name = parts[0].strip()
                    vram = int(float(parts[1].strip()) / 1024)  # MiB to GB
        except Exception as e:
            logger.warning(f"nvidia-smi error: {e}")
        
        # Fallback to WMI
        if name == "Unknown GPU" and self.wmi_conn:
            try:
                for gpu in self.wmi_conn.Win32_VideoController():
                    gpu_name = gpu.Name or "Unknown GPU"
                    is_discrete = any(x in gpu_name.lower() for x in ['nvidia', 'geforce', 'rtx', 'gtx', 'radeon'])
                    if is_discrete or name == "Unknown GPU":
                        name = gpu_name
                        if hasattr(gpu, 'AdapterRAM') and gpu.AdapterRAM:
                            vram = int(gpu.AdapterRAM / (1024**3))
                        driver_version = gpu.DriverVersion or "unknown"
                        if is_discrete:
                            break
            except Exception as e:
                logger.warning(f"WMI GPU error: {e}")
        
        # Determine vendor
        name_lower = name.lower()
        if 'nvidia' in name_lower or 'geforce' in name_lower or 'rtx' in name_lower or 'gtx' in name_lower:
            vendor = 'nvidia'
        elif 'amd' in name_lower or 'radeon' in name_lower:
            vendor = 'amd'
        elif 'intel' in name_lower:
            vendor = 'intel'

        # Calculate score using benchmark database
        gpu_score, raw_score, gpu_vram_db, matched_name = self.benchmark_db.get_gpu_score(name)
        score = gpu_score
        # Update VRAM from database if more accurate
        if gpu_vram_db > 0:
            vram = gpu_vram_db

        return GPUInfo(
            name=name,
            vendor=vendor,
            vram=vram,
            driver_version=driver_version,
            score=score
        )
    
    def detect_ram(self) -> RAMInfo:
        """Detect RAM information"""
        import math
        total_bytes = psutil.virtual_memory().total if HAS_PSUTIL else 0
        total_gb = math.ceil(total_bytes / (1024**3))  # Always round UP
        
        # RAM type detection is complex, default to unknown
        ram_type = "unknown"
        speed = 0
        
        # Calculate score (0-20)
        score = min(20, int(total_gb / 2))
        
        return RAMInfo(
            total_gb=total_gb,
            type=ram_type,
            speed=speed,
            score=score
        )
    
    def detect_storage(self) -> StorageInfo:
        """Detect primary storage type (NVMe / SSD / HDD) and capacity.

        Detection strategy (in priority order):
        1. WMI Win32_DiskDrive — checks MediaType ("SSD"/"HDD") and model
           name for NVMe keyword.
        2. PowerShell Get-PhysicalDisk — checks MediaType field.
        3. psutil disk_partitions — capacity only; type falls back to "unknown".
        """
        primary_type = "unknown"
        total_gb = 0

        # --- Strategy 1: WMI Win32_DiskDrive ---
        if HAS_WMI and self.wmi_conn:
            try:
                for disk in self.wmi_conn.Win32_DiskDrive():
                    model = (disk.Model or "").lower()
                    media = (disk.MediaType or "").lower()

                    if "nvme" in model or "nvme" in media:
                        primary_type = "nvme"
                    elif "ssd" in model or "solid" in media:
                        primary_type = "ssd"
                    elif "hdd" in model or "fixed hard disk" in media:
                        primary_type = "hdd"

                    # Take size from the first disk that has a size
                    if primary_type != "unknown":
                        try:
                            size_bytes = int(disk.Size or 0)
                            total_gb = int(size_bytes / (1024 ** 3))
                        except (ValueError, TypeError):
                            pass
                        break  # Use the first classified disk as primary
            except Exception as e:
                logger.debug(f"WMI disk detection error: {e}")

        # --- Strategy 2: PowerShell Get-PhysicalDisk (fallback) ---
        if primary_type == "unknown":
            try:
                result = subprocess.run(
                    [
                        "powershell", "-NoProfile", "-NonInteractive",
                        "-Command",
                        "Get-PhysicalDisk | Select-Object -First 1 MediaType,Size | "
                        "ConvertTo-Json -Compress",
                    ],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode == 0 and result.stdout.strip():
                    import json as _json
                    disk_data = _json.loads(result.stdout.strip())
                    media = str(disk_data.get("MediaType", "")).lower()
                    if "nvme" in media or "4" in media:  # MediaType 4 == NVMe in PS
                        primary_type = "nvme"
                    elif "ssd" in media or "3" in media:  # MediaType 3 == SSD
                        primary_type = "ssd"
                    elif "hdd" in media or "2" in media:  # MediaType 2 == HDD
                        primary_type = "hdd"
                    if total_gb == 0:
                        try:
                            total_gb = int(int(disk_data.get("Size", 0)) / (1024 ** 3))
                        except (ValueError, TypeError):
                            pass
            except Exception as e:
                logger.debug(f"PowerShell disk detection error: {e}")

        # --- Strategy 3: psutil — capacity only ---
        if HAS_PSUTIL and total_gb == 0:
            try:
                for partition in psutil.disk_partitions():
                    if "C:" in partition.mountpoint or partition.mountpoint == "/":
                        usage = psutil.disk_usage(partition.mountpoint)
                        total_gb = int(usage.total / (1024 ** 3))
                        break
            except Exception:
                pass

        logger.debug(f"Storage detected: type={primary_type}, size={total_gb} GB")

        # Calculate score (0-10)
        score = 10 if primary_type in ["nvme", "ssd"] else (5 if primary_type == "hdd" else 3)

        return StorageInfo(
            primary_type=primary_type,
            total_gb=total_gb,
            score=score
        )
    
    def detect_form_factor(self) -> str:
        """Detect if desktop or laptop"""
        # Check battery presence as indicator
        if HAS_PSUTIL:
            try:
                battery = psutil.sensors_battery()
                if battery is not None:
                    return "laptop"
            except Exception:
                pass
        
        return "desktop"
    
    def calculate_tier(self, total_score: int) -> str:
        """Calculate system tier from total score"""
        if total_score >= 70:
            return "enthusiast"
        elif total_score >= 50:
            return "high"
        elif total_score >= 30:
            return "mid"
        else:
            return "entry"
    
    def recommend_profile(self, system: SystemProfile) -> str:
        """
        Recommend optimization profile
        
        Args:
            system: System profile
            
        Returns:
            Recommended profile name ('SAFE', 'COMPETITIVE', 'EXTREME')
        """
        # Laptop restriction
        if system.form_factor == "laptop":
            return "SAFE"
        
        # Desktop recommendations
        if system.tier == "enthusiast":
            return "COMPETITIVE"  # Not EXTREME by default
        elif system.tier in ["high", "mid"]:
            return "COMPETITIVE"
        else:
            return "SAFE"

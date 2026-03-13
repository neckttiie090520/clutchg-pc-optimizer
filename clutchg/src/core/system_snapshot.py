"""
System Snapshot
Captures system state before/after optimization for comparison.
Uses lightweight WMI-free queries for speed.
"""

import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SystemSnapshot:
    """Snapshot of system state at a point in time"""
    timestamp: str = ""
    services_running: int = 0
    services_stopped: int = 0
    startup_items: int = 0
    scheduled_tasks_enabled: int = 0
    network_interfaces: int = 0
    power_plan: str = ""
    visual_effects_level: str = ""  # "best_appearance" | "balanced" | "best_performance"
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, d: dict) -> "SystemSnapshot":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


@dataclass
class SnapshotDiff:
    """Difference between two snapshots"""
    services_stopped_delta: int = 0  # positive = more stopped = good
    startup_items_delta: int = 0     # negative = fewer = good
    tasks_disabled_delta: int = 0    # negative = fewer enabled = good
    power_plan_changed: bool = False
    power_plan_before: str = ""
    power_plan_after: str = ""
    
    @property
    def summary_lines(self) -> List[str]:
        """Human-readable summary"""
        lines = []
        if self.services_stopped_delta > 0:
            lines.append(f"🔧 {self.services_stopped_delta} service(s) stopped")
        elif self.services_stopped_delta < 0:
            lines.append(f"🔧 {abs(self.services_stopped_delta)} service(s) started")
            
        if self.startup_items_delta < 0:
            lines.append(f"⚡ {abs(self.startup_items_delta)} startup item(s) removed")
        elif self.startup_items_delta > 0:
            lines.append(f"⚡ {self.startup_items_delta} startup item(s) added")
        
        if self.tasks_disabled_delta < 0:
            lines.append(f"📋 {abs(self.tasks_disabled_delta)} scheduled task(s) disabled")
            
        if self.power_plan_changed:
            lines.append(f"🔋 Power plan: {self.power_plan_before} → {self.power_plan_after}")
        
        if not lines:
            lines.append("No measurable changes detected")
        
        return lines


class SystemSnapshotManager:
    """Takes and compares system snapshots"""
    
    SNAPSHOT_DIR = Path(__file__).parent.parent / "config" / "snapshots"
    
    def __init__(self):
        self.SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    
    def take_snapshot(self) -> SystemSnapshot:
        """Capture current system state"""
        snap = SystemSnapshot(timestamp=datetime.now().isoformat())
        
        # Count running/stopped services
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-Service | Where-Object {$_.Status -eq 'Running'}).Count"],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            snap.services_running = int(result.stdout.strip() or "0")
            
            result2 = subprocess.run(
                ["powershell", "-Command",
                 "(Get-Service | Where-Object {$_.Status -eq 'Stopped'}).Count"],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            snap.services_stopped = int(result2.stdout.strip() or "0")
        except Exception as e:
            logger.warning(f"Failed to count services: {e}")
        
        # Count startup items
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_StartupCommand).Count"],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            snap.startup_items = int(result.stdout.strip() or "0")
        except Exception as e:
            logger.warning(f"Failed to count startup items: {e}")
        
        # Count enabled scheduled tasks
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-ScheduledTask | Where-Object {$_.State -eq 'Ready'}).Count"],
                capture_output=True, text=True, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            snap.scheduled_tasks_enabled = int(result.stdout.strip() or "0")
        except Exception as e:
            logger.warning(f"Failed to count scheduled tasks: {e}")
        
        # Active power plan
        try:
            result = subprocess.run(
                ["powercfg", "/getactivescheme"],
                capture_output=True, text=True, timeout=10,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            # Output like: "Power Scheme GUID: ... (High performance)"
            line = result.stdout.strip()
            if "(" in line and ")" in line:
                snap.power_plan = line.split("(")[-1].rstrip(")")
            else:
                snap.power_plan = line
        except Exception as e:
            logger.warning(f"Failed to get power plan: {e}")
        
        logger.info(f"Snapshot taken: {snap.services_running} running, "
                     f"{snap.services_stopped} stopped, "
                     f"{snap.startup_items} startup items")
        return snap
    
    def compare(self, before: SystemSnapshot, after: SystemSnapshot) -> SnapshotDiff:
        """Compare two snapshots and return differences"""
        return SnapshotDiff(
            services_stopped_delta=after.services_stopped - before.services_stopped,
            startup_items_delta=after.startup_items - before.startup_items,
            tasks_disabled_delta=after.scheduled_tasks_enabled - before.scheduled_tasks_enabled,
            power_plan_changed=before.power_plan != after.power_plan,
            power_plan_before=before.power_plan,
            power_plan_after=after.power_plan,
        )
    
    def save_snapshot(self, snap: SystemSnapshot, label: str = "snapshot") -> Path:
        """Save snapshot to file"""
        filename = f"{label}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = self.SNAPSHOT_DIR / filename
        filepath.write_text(json.dumps(snap.to_dict(), indent=2), encoding="utf-8")
        logger.info(f"Snapshot saved: {filepath}")
        return filepath
    
    def load_snapshot(self, filepath: Path) -> Optional[SystemSnapshot]:
        """Load snapshot from file"""
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return SystemSnapshot.from_dict(data)
        except Exception as e:
            logger.error(f"Failed to load snapshot: {e}")
            return None

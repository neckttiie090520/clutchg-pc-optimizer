"""
Tweak Registry — Central knowledge base of all optimization tweaks
Every tweak has rich metadata: description, what it does, limitations, warnings, etc.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Tweak:
    """Single optimization tweak with full documentation"""

    id: str
    name: str
    category: str
    description: str  # Short 1-line
    what_it_does: str  # Full technical explanation
    why_it_helps: str  # Performance reasoning
    limitations: str  # What breaks or won't work
    warnings: List[str]  # Risk warnings
    risk_level: str  # LOW / MEDIUM / HIGH
    expected_gain: str  # e.g. "1-3% less CPU usage"
    requires_admin: bool = True
    requires_restart: bool = False
    reversible: bool = True
    compatible_os: List[str] = field(default_factory=lambda: ["10", "11"])
    compatible_hardware: Dict[str, str] = field(default_factory=dict)
    registry_keys: List[str] = field(default_factory=list)
    bat_script: str = ""
    bat_function: str = ""
    preset_safe: bool = False
    preset_competitive: bool = False
    preset_extreme: bool = False


# Category display metadata — all Tabler Icons codepoints
TWEAK_CATEGORIES = {
    "telemetry": {"icon": "\uebe4", "color": "#8B5CF6", "label": "Telemetry & Privacy"},
    "input": {"icon": "\uef26", "color": "#06B6D4", "label": "Input & Latency"},
    "power": {"icon": "\uf4a9", "color": "#F59E0B", "label": "Power Management"},
    "gpu": {"icon": "\uf50d", "color": "#10B981", "label": "GPU & Graphics"},
    "network": {"icon": "\uf09f", "color": "#3B82F6", "label": "Network"},
    "services": {"icon": "\uf56e", "color": "#EF4444", "label": "Services"},
    "memory": {"icon": "\uefce", "color": "#EC4899", "label": "Memory"},
    "boot": {"icon": "\uebcb", "color": "#F97316", "label": "Boot (BCDEdit)"},
    "visual": {"icon": "\uea2d", "color": "#A855F7", "label": "Visual Effects"},
    "cleanup": {"icon": "\ueb8c", "color": "#64748B", "label": "Cleanup & Debloat"},
}


def _build_tweaks() -> List[Tweak]:
    """Build the complete tweak database"""
    return [
        # ================================================================
        # TELEMETRY & PRIVACY (8 tweaks)
        # ================================================================
        Tweak(
            id="tel_diagtrack",
            name="Disable DiagTrack Service",
            category="telemetry",
            description="Stop Windows diagnostic data collection service",
            what_it_does="Disables the Connected User Experiences and Telemetry service (DiagTrack) which continuously collects and sends diagnostic data to Microsoft servers.",
            why_it_helps="Frees CPU cycles and network bandwidth used for telemetry data collection and transmission. Reduces background disk I/O.",
            limitations="Microsoft won't receive crash reports. Some Windows troubleshooting features may not work.",
            warnings=["Windows Update still works normally"],
            risk_level="LOW",
            expected_gain="1-2% less background CPU",
            requires_restart=True,
            registry_keys=["HKLM\\SYSTEM\\CurrentControlSet\\Services\\DiagTrack"],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_telemetry",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_advertising",
            name="Disable Advertising ID",
            category="telemetry",
            description="Stop personalized ads tracking across apps",
            what_it_does="Disables the unique advertising identifier that Windows assigns to track your app usage for targeted advertising.",
            why_it_helps="Reduces background tracking processes. Privacy improvement with minimal performance impact.",
            limitations="You'll see generic ads instead of personalized ones in supported apps.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Privacy improvement",
            registry_keys=[
                "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo"
            ],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_privacy",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_cortana",
            name="Disable Cortana",
            category="telemetry",
            description="Turn off Cortana voice assistant and web search",
            what_it_does="Disables Cortana integration and prevents Bing web search results from appearing in Start menu search.",
            why_it_helps="Eliminates background Cortana process (~50-100MB RAM). Start menu search becomes faster (local only).",
            limitations="Voice assistant won't work. Start menu search is local-only (no web results).",
            warnings=["Bing search in Start menu will be disabled"],
            risk_level="LOW",
            expected_gain="50-100MB RAM freed",
            registry_keys=[
                "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search"
            ],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_privacy",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_activity",
            name="Disable Activity History",
            category="telemetry",
            description="Stop tracking app usage and browsing history",
            what_it_does="Disables Windows Timeline/Activity History that logs which apps and files you open, and syncs this to Microsoft servers.",
            why_it_helps="Reduces background logging I/O and cloud sync. Minor performance gain, major privacy gain.",
            limitations="Windows Timeline feature won't show history. Cross-device activity sync disabled.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Privacy improvement",
            registry_keys=["HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System"],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_privacy",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_xbox_dvr",
            name="Disable Xbox Game Bar & DVR",
            category="telemetry",
            description="Turn off game recording and overlay features",
            what_it_does="Disables Xbox Game Bar overlay, background game recording (DVR), and broadcast features. Game Mode is kept enabled.",
            why_it_helps="Eliminates 2-5% FPS overhead from background recording. Reduces GPU memory usage by ~200MB. Less input lag from overlay.",
            limitations="Can't use Win+G overlay, game clips, or Xbox social features. Use OBS/ShadowPlay instead.",
            warnings=["Game Mode stays ON (it helps performance)"],
            risk_level="LOW",
            expected_gain="2-5% FPS improvement",
            registry_keys=[
                "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR",
                "HKCU\\System\\GameConfigStore",
            ],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_xbox_dvr",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_ads_suggestions",
            name="Disable Ads & Suggestions",
            category="telemetry",
            description="Remove Windows Spotlight, tips, and app suggestions",
            what_it_does="Disables lock screen Spotlight ads, Start menu app suggestions, Settings tips, and 'Get Even More Out of Windows' prompts.",
            why_it_helps="Reduces background content download. Cleaner UI without promotional distractions.",
            limitations="Lock screen will show your chosen wallpaper instead of rotating Spotlight images.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Cleaner experience",
            registry_keys=[
                "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager"
            ],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_ads",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_location",
            name="Disable Location Tracking",
            category="telemetry",
            description="Prevent apps from accessing your location",
            what_it_does="Disables the Windows location service that allows apps to access your geographic position via GPS, Wi-Fi, or IP geolocation.",
            why_it_helps="Reduces background location polling. Privacy improvement.",
            limitations="Weather app, Maps, and location-based apps won't know your location. You can still manually set location.",
            warnings=["Find My Device won't work if laptop is lost"],
            risk_level="LOW",
            expected_gain="Privacy improvement",
            registry_keys=[
                "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location"
            ],
            bat_script="core/telemetry-blocker.bat",
            bat_function=":apply_privacy",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="tel_copilot",
            name="Disable Windows Copilot & Recall",
            category="telemetry",
            description="Turn off AI assistant and screen recording features",
            what_it_does="Disables Windows Copilot sidebar and Recall (AI screenshot feature in Windows 11 24H2+). Prevents background AI processing.",
            why_it_helps="Saves RAM and CPU from AI model loading. Recall uses significant disk space for screenshots.",
            limitations="Copilot AI assistant unavailable. Recall timeline search won't work.",
            warnings=["Windows 11 only feature"],
            risk_level="LOW",
            expected_gain="200-500MB RAM freed",
            compatible_os=["11"],
            registry_keys=[
                "HKCU\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot"
            ],
            bat_script="core/debloater.bat",
            bat_function=":apply_copilot",
            preset_competitive=True,
            preset_extreme=True,
        ),
        # ================================================================
        # INPUT & LATENCY (6 tweaks)
        # ================================================================
        Tweak(
            id="inp_mouse_accel",
            name="Disable Mouse Acceleration",
            category="input",
            description="Enable 1:1 mouse movement (raw input)",
            what_it_does="Sets EnhancedPointerPrecision to OFF and applies a flat 1:1 acceleration curve. Mouse movement becomes linear and predictable.",
            why_it_helps="Critical for FPS gaming — muscle memory works correctly. Eliminates variable sensitivity that changes with mouse speed.",
            limitations="Mouse may feel 'different' at first. You may need to adjust DPI on your mouse software.",
            warnings=["Adjust your mouse DPI after applying"],
            risk_level="LOW",
            expected_gain="More consistent aim",
            registry_keys=["HKCU\\Control Panel\\Mouse"],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_mouse",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="inp_keyboard",
            name="Optimize Keyboard Response",
            category="input",
            description="Set fastest key repeat rate and shortest delay",
            what_it_does="Sets KeyboardDelay to 0 (shortest) and KeyboardSpeed to 31 (fastest repeat). Keys respond instantly when held.",
            why_it_helps="Faster key repeat for gaming (movement keys) and typing. Reduces perceived input lag.",
            limitations="Keys may repeat too fast for some users when held down.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Faster key response",
            registry_keys=["HKCU\\Control Panel\\Keyboard"],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_keyboard",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="inp_mmcss",
            name="MMCSS Latency Optimization",
            category="input",
            description="Prioritize gaming threads in Windows scheduler",
            what_it_does="Configures Multimedia Class Scheduler Service: SystemResponsiveness=0 (max foreground priority), NoLazyMode=1, NetworkThrottling=disabled.",
            why_it_helps="Ensures game threads get maximum CPU time. Reduces DPC latency by 2-5ms. Eliminates network throttling during games.",
            limitations="Background tasks (downloads, updates) may be slower while gaming.",
            warnings=["Background downloads may slow during gameplay"],
            risk_level="LOW",
            expected_gain="2-5ms latency reduction",
            registry_keys=[
                "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile"
            ],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_latency",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="inp_menu_delay",
            name="Instant Menu & UI Response",
            category="input",
            description="Remove all menu show delays and animation waits",
            what_it_does="Sets MenuShowDelay=0, HungAppTimeout=1000, WaitToKillAppTimeout=2000, AutoEndTasks=1. Menus appear instantly, hung apps close faster.",
            why_it_helps="UI feels snappier. Right-click menus appear instantly. Shutdown/restart is faster.",
            limitations="No smooth menu fade-in animation.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Snappier UI feel",
            registry_keys=["HKCU\\Control Panel\\Desktop"],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_ui",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="inp_data_queue",
            name="Hardware Data Queue Optimization",
            category="input",
            description="Optimize mouse and keyboard buffer sizes",
            what_it_does="Sets MouseDataQueueSize=20 and KeyboardDataQueueSize=20. Smaller buffers = less buffering delay between hardware and OS.",
            why_it_helps="Reduces input lag by minimizing the buffer between your mouse/keyboard and Windows. Source: QuickBoost.",
            limitations="Very rarely, extremely fast mouse movements might miss samples. Negligible in practice.",
            warnings=[],
            risk_level="LOW",
            expected_gain="~1ms input lag reduction",
            requires_restart=True,
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Services\\mouclass\\Parameters",
                "HKLM\\SYSTEM\\CurrentControlSet\\Services\\kbdclass\\Parameters",
            ],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_mouse",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="inp_priority_sep",
            name="Foreground Process Priority Boost",
            category="input",
            description="Maximize CPU priority for active window",
            what_it_does="Sets Win32PrioritySeparation=38 (long quantum, max foreground boost). The game you're actively playing gets maximum CPU scheduling priority.",
            why_it_helps="Active game gets 3x more CPU time than background processes. Reduces frame drops caused by background activity.",
            limitations="Background tasks run slower while a game is in focus.",
            warnings=[],
            risk_level="LOW",
            expected_gain="1-3% smoother gameplay",
            registry_keys=["HKLM\\SYSTEM\\CurrentControlSet\\Control\\PriorityControl"],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_latency",
            preset_competitive=True,
            preset_extreme=True,
        ),
        # ================================================================
        # POWER MANAGEMENT (7 tweaks)
        # ================================================================
        Tweak(
            id="pwr_ultimate",
            name="Ultimate Performance Power Plan",
            category="power",
            description="Activate hidden high-performance power scheme",
            what_it_does="Enables the Ultimate Performance power plan (hidden by default). Disables core parking, keeps CPU at max frequency, eliminates power-saving latency.",
            why_it_helps="CPU doesn't throttle or park cores. Eliminates 5-15ms wake-from-idle latency. Consistent frame times.",
            limitations="Higher power consumption (10-30W more). More heat output. Not suitable for laptops on battery.",
            warnings=["Increases power consumption", "Desktop recommended"],
            risk_level="LOW",
            expected_gain="3-5% FPS, consistent frametimes",
            registry_keys=[],
            bat_script="core/power-manager.bat",
            bat_function=":apply_ultimate",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_hibernate",
            name="Disable Hibernation & Fast Startup",
            category="power",
            description="Clean boot every time, save disk space",
            what_it_does="Turns off hibernation (powercfg /h off) and disables Fast Startup (HiberBootEnabled=0). Deletes hiberfil.sys (saves RAM-size worth of disk).",
            why_it_helps="Saves disk space equal to your RAM size. Clean boot avoids stale driver states. Prevents wake-from-hibernate issues.",
            limitations="No hibernate option. Boot time may increase by 2-5 seconds (SSD) or 10-20 seconds (HDD).",
            warnings=["Boot may be slightly slower on HDD"],
            risk_level="LOW",
            expected_gain="Save disk space (= RAM size)",
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_modern_standby",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_throttling",
            name="Disable Power Throttling",
            category="power",
            description="Prevent Windows from throttling CPU for power saving",
            what_it_does="Disables PowerThrottling, Connected Standby (CsEnabled=0), and AOAC power management. CPU always runs at full power.",
            why_it_helps="Eliminates unexpected CPU throttling during gaming. Background processes don't trigger power-saving mode.",
            limitations="Higher power consumption. Laptop battery life significantly reduced.",
            warnings=["Significant battery impact on laptops"],
            risk_level="MEDIUM",
            expected_gain="Consistent CPU performance",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling",
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power",
            ],
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_power_throttling",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_epp",
            name="Energy Performance Preference (EPP=0)",
            category="power",
            description="Set CPU to maximum performance mode",
            what_it_does="Sets Energy Performance Preference to 0 (max performance) on AC power. CPU always boosts to maximum frequency without power-saving delays.",
            why_it_helps="Eliminates CPU frequency scaling delays. Instant boost response for gaming workloads.",
            limitations="CPU runs hotter. Fan noise increases. Not suitable for quiet environments.",
            warnings=["CPU runs at max frequency constantly"],
            risk_level="MEDIUM",
            expected_gain="1-3% FPS improvement",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerSettings"
            ],
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_epp_performance",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_cppc",
            name="AMD CPPC Preferred Core",
            category="power",
            description="Let AMD CPU choose its fastest cores automatically",
            what_it_does="Enables CPPC (Collaborative Processor Performance Control) which lets AMD Ryzen CPUs report their best cores to Windows for optimal thread scheduling.",
            why_it_helps="Windows schedules game threads on the fastest cores. Better single-thread performance. 1-3% boost on Ryzen 5000+.",
            limitations="AMD Ryzen only. No effect on Intel CPUs. Requires BIOS CPPC support.",
            warnings=["AMD Ryzen only"],
            risk_level="LOW",
            expected_gain="1-3% on AMD Ryzen",
            compatible_hardware={"cpu_vendor": "AMD"},
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_cppc_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_coalescence",
            name="Timer Coalescence Optimization",
            category="power",
            description="Reduce timer coalescing for lower DPC latency",
            what_it_does="Sets the global timer coalescence resolution to minimum (1). Reduces the delay Windows adds when coalescing timer interrupts.",
            why_it_helps="Lower DPC latency by reducing timer batching. Source: Ghost-Optimizer.",
            limitations="Slightly higher power consumption from more frequent timer interrupts.",
            warnings=[],
            risk_level="LOW",
            expected_gain="1-2ms DPC latency reduction",
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_coalescence_timers",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="pwr_spectre",
            name="Disable Spectre/Meltdown Mitigations",
            category="power",
            description="Remove CPU vulnerability mitigations for raw speed",
            what_it_does="Sets FeatureSettingsOverride=3 and FeatureSettingsOverrideMask=3 to disable all Spectre/Meltdown CPU mitigations.",
            why_it_helps="5-15% CPU performance gain by removing branch prediction restrictions and memory isolation overhead.",
            limitations="System is vulnerable to Spectre/Meltdown side-channel attacks. Only safe on isolated gaming PCs.",
            warnings=[
                "⚠️ SECURITY RISK: Removes CPU vulnerability protections",
                "Only for dedicated gaming PCs, NOT daily drivers",
                "Requires restart",
            ],
            risk_level="HIGH",
            expected_gain="5-15% CPU performance",
            requires_restart=True,
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management"
            ],
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_spectre_disable",
            preset_extreme=True,
        ),
        # ================================================================
        # GPU & GRAPHICS (8 tweaks)
        # ================================================================
        Tweak(
            id="gpu_hags",
            name="Hardware-Accelerated GPU Scheduling",
            category="gpu",
            description="Let GPU manage its own memory scheduling",
            what_it_does="Enables HwSchMode=2. GPU handles its own VRAM scheduling instead of Windows, reducing CPU overhead for graphics operations.",
            why_it_helps="3-5% FPS gain in GPU-bound scenarios. Lower CPU overhead for frame presentation. Reduced input lag.",
            limitations="Requires Windows 10 2004+ and compatible GPU driver. May cause issues with very old games.",
            warnings=["Requires compatible GPU driver"],
            risk_level="LOW",
            expected_gain="3-5% FPS improvement",
            requires_restart=True,
            registry_keys=["HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers"],
            bat_script="core/gpu-optimizer.bat",
            bat_function=":apply_hags",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_nvidia_telemetry",
            name="Disable NVIDIA Telemetry",
            category="gpu",
            description="Stop NVIDIA driver data collection",
            what_it_does="Disables NvTmMon, NvTmRep, and other NVIDIA telemetry services that collect GPU usage data.",
            why_it_helps="Reduces background CPU usage from NVIDIA services. Privacy improvement.",
            limitations="NVIDIA GeForce Experience may have reduced recommendations.",
            warnings=["NVIDIA GPU only"],
            risk_level="LOW",
            expected_gain="1-2% less background CPU",
            compatible_hardware={"gpu_vendor": "NVIDIA"},
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_nvidia_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_msi_mode",
            name="Enable GPU MSI Mode",
            category="gpu",
            description="Use Message Signaled Interrupts for GPU",
            what_it_does="Enables MSI (Message Signaled Interrupts) mode for the GPU instead of line-based interrupts. More efficient interrupt handling.",
            why_it_helps="Lower interrupt latency for GPU operations. Can reduce DPC latency by 1-3ms. Source: CS2-Ultimate-Optimization.",
            limitations="Some older GPUs may not support MSI. Very rarely causes display issues.",
            warnings=["Test stability after enabling"],
            risk_level="MEDIUM",
            expected_gain="1-3ms DPC latency reduction",
            requires_restart=True,
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_msi_mode",
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_directx",
            name="DirectX & Direct3D Optimizations",
            category="gpu",
            description="Optimize DirectX settings for gaming performance",
            what_it_does="Sets TdrDelay=10 (more time before GPU reset), disables debug layer, enables shader cache, optimizes flip queue size.",
            why_it_helps="Prevents false GPU timeout crashes. Shader cache reduces stutter on second launch. Optimized flip queue reduces latency.",
            limitations="TdrDelay increase means frozen screens last longer before recovery.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Less stutter, fewer crashes",
            registry_keys=["HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers"],
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_directx_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_fullscreen",
            name="Disable Fullscreen Optimizations",
            category="gpu",
            description="Use true exclusive fullscreen mode",
            what_it_does="Disables Windows fullscreen optimizations (borderless-fullscreen emulation) globally. Games use true exclusive fullscreen.",
            why_it_helps="True fullscreen bypasses DWM compositor. Lower input lag by 5-15ms. More consistent frame delivery.",
            limitations="Alt-Tab is slower from true fullscreen. Multi-monitor setups may flash when switching.",
            warnings=["Alt-Tab will be slower in fullscreen games"],
            risk_level="LOW",
            expected_gain="5-15ms input lag reduction",
            registry_keys=["HKCU\\System\\GameConfigStore"],
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_fullscreen_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_nvidia_pstate",
            name="NVIDIA GPU P-State Control",
            category="gpu",
            description="Prevent NVIDIA GPU from downclocking",
            what_it_does="Disables NVIDIA PerfLevelSrc power limiting. GPU stays at higher performance states instead of aggressively downclocking.",
            why_it_helps="Eliminates micro-stutters from GPU frequency changes. More consistent frame times.",
            limitations="GPU runs warmer at idle. Higher power draw when not gaming.",
            warnings=["NVIDIA only", "Higher idle power consumption"],
            risk_level="MEDIUM",
            expected_gain="Consistent frametimes",
            compatible_hardware={"gpu_vendor": "NVIDIA"},
            bat_script="core/power-manager-enhanced.bat",
            bat_function=":apply_gpu_pstate",
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_vbs",
            name="Disable VBS / Memory Integrity",
            category="gpu",
            description="Turn off Virtualization-Based Security for GPU performance",
            what_it_does="Disables VBS (Virtualization-Based Security) and HVCI (Hypervisor-Enforced Code Integrity). Removes hypervisor overhead from graphics pipeline.",
            why_it_helps="5-10% FPS gain by removing VBS overhead. Significant in CPU-bound games. Source: Ghost-Optimizer.",
            limitations="Reduces system security. Credential Guard disabled. Memory integrity protection removed.",
            warnings=[
                "⚠️ SECURITY RISK: Disables hardware security features",
                "Not recommended for systems handling sensitive data",
            ],
            risk_level="HIGH",
            expected_gain="5-10% FPS improvement",
            requires_restart=True,
            registry_keys=["HKLM\\SYSTEM\\CurrentControlSet\\Control\\DeviceGuard"],
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_vbs_disable",
            preset_extreme=True,
        ),
        Tweak(
            id="gpu_dwm",
            name="Optimize DWM Compositor",
            category="gpu",
            description="Reduce Desktop Window Manager overhead",
            what_it_does="Disables DWM overlay test mode and optimizes compositor settings. Reduces overhead when games use windowed/borderless mode.",
            why_it_helps="Lower DWM CPU usage. Slightly better frame pacing in borderless windowed mode.",
            limitations="May affect window transparency rendering.",
            warnings=[],
            risk_level="LOW",
            expected_gain="1-2% in windowed mode",
            registry_keys=["HKLM\\SOFTWARE\\Microsoft\\Windows\\Dwm"],
            bat_script="core/gpu-optimizer-enhanced.bat",
            bat_function=":apply_fullscreen_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        # ================================================================
        # NETWORK (6 tweaks)
        # ================================================================
        Tweak(
            id="net_nagle",
            name="Disable Nagle's Algorithm",
            category="network",
            description="Send packets immediately without buffering",
            what_it_does="Sets TcpAckFrequency=1 and TCPNoDelay=1. Disables Nagle's algorithm which normally buffers small packets together before sending.",
            why_it_helps="Critical for online gaming: game actions are sent instantly. Reduces network latency by 5-20ms in games.",
            limitations="Slightly more network overhead from smaller packets. Impacts large file download efficiency.",
            warnings=["May reduce large file transfer speed by 5-10%"],
            risk_level="MEDIUM",
            expected_gain="5-20ms network latency reduction",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters\\Interfaces"
            ],
            bat_script="core/network-optimizer-enhanced.bat",
            bat_function=":apply_nagle_disable",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="net_tcp_global",
            name="TCP Global Stack Optimization",
            category="network",
            description="Optimize TCP/IP stack for low-latency gaming",
            what_it_does="Sets autotuning=normal, ECN=disabled, timestamps=disabled, RSS=enabled. Optimizes the Windows TCP/IP stack for responsive networking.",
            why_it_helps="ECN disable prevents some ISPs from throttling. RSS spreads network load across CPU cores. Timestamps disable saves packet overhead.",
            limitations="ECN disable may slightly increase packet loss on congested networks.",
            warnings=["Advanced network change"],
            risk_level="MEDIUM",
            expected_gain="2-5ms network improvement",
            bat_script="core/network-optimizer-enhanced.bat",
            bat_function=":apply_tcp_global",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="net_dns",
            name="Set Optimized DNS Servers",
            category="network",
            description="Use fast DNS (Cloudflare 1.1.1.1 or Google 8.8.8.8)",
            what_it_does="Changes DNS servers from ISP defaults to Cloudflare (1.1.1.1), Google (8.8.8.8), or Quad9 (9.9.9.9) — faster and more reliable.",
            why_it_helps="Faster DNS resolution = faster initial connection to game servers. Cloudflare averages 11ms vs ISP 20-50ms.",
            limitations="ISP-specific internal services may not resolve. Parental controls via ISP DNS won't work.",
            warnings=["Override your ISP's DNS"],
            risk_level="LOW",
            expected_gain="Faster server connections",
            bat_script="core/network-optimizer-enhanced.bat",
            bat_function=":set_dns_preset",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="net_netbios",
            name="Disable NetBIOS over TCP/IP",
            category="network",
            description="Remove legacy network protocol overhead",
            what_it_does="Disables NetBIOS name resolution over TCP/IP. NetBIOS is a legacy protocol from Windows 3.1 era that's rarely needed today.",
            why_it_helps="Reduces network attack surface. Eliminates NetBIOS broadcast traffic. Minor latency improvement.",
            limitations="Very old network printers or NAS devices using NetBIOS names won't be accessible by name. Use IP instead.",
            warnings=["Legacy network devices may need IP address instead of name"],
            risk_level="LOW",
            expected_gain="Cleaner network stack",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Services\\NetBT\\Parameters"
            ],
            bat_script="core/network-optimizer-enhanced.bat",
            bat_function=":apply_tcp_global",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="net_window_size",
            name="Optimize TCP Window Size",
            category="network",
            description="Set optimal TCP receive window for gaming",
            what_it_does="Sets TcpWindowSize=65535, MaxUserPort=65534, TcpTimedWaitDelay=30. Optimizes TCP connection parameters.",
            why_it_helps="More available ports for game connections. Faster connection teardown frees resources sooner.",
            limitations="On very high bandwidth connections (10Gbps+), the window size cap may limit throughput.",
            warnings=[],
            risk_level="MEDIUM",
            expected_gain="More reliable connections",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip\\Parameters"
            ],
            bat_script="core/network-optimizer-enhanced.bat",
            bat_function=":apply_nagle_disable",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="net_throttling",
            name="Disable Network Throttling",
            category="network",
            description="Remove Windows network bandwidth limits",
            what_it_does="Sets NetworkThrottlingIndex=0xFFFFFFFF. Removes the 10-packet-per-millisecond throttle that Windows applies to multimedia applications.",
            why_it_helps="Removes artificial bandwidth caps during gaming. Full network throughput available.",
            limitations="None significant.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Full network bandwidth",
            registry_keys=[
                "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile"
            ],
            bat_script="core/input-optimizer.bat",
            bat_function=":apply_latency",
            preset_competitive=True,
            preset_extreme=True,
        ),
        # ================================================================
        # SERVICES (5 tweaks)
        # ================================================================
        Tweak(
            id="svc_telemetry",
            name="Disable Telemetry Services",
            category="services",
            description="Stop DiagTrack and dmwappushservice",
            what_it_does="Disables and stops DiagTrack (Connected User Experiences) and dmwappushservice (WAP Push Message Routing). Both send data to Microsoft.",
            why_it_helps="Frees 1-3% CPU used for data collection. Reduces network usage.",
            limitations="Windows troubleshooting feedback loop broken. Microsoft won't receive crash data.",
            warnings=[],
            risk_level="LOW",
            expected_gain="1-3% CPU freed",
            requires_restart=True,
            bat_script="core/service-manager.bat",
            bat_function=":disable_telemetry",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="svc_xbox",
            name="Disable Xbox Services",
            category="services",
            description="Stop Xbox authentication and game save sync",
            what_it_does="Disables XblAuthManager, XblGameSave, XboxNetApiSvc, and XboxGipSvc services. Stops Xbox Live integration.",
            why_it_helps="Frees ~50MB RAM and background CPU from Xbox services. Faster boot time.",
            limitations="Xbox Game Pass features won't work. Xbox social features unavailable. Some games may require re-enabling.",
            warnings=["Xbox Game Pass games may not launch"],
            risk_level="MEDIUM",
            expected_gain="~50MB RAM, faster boot",
            requires_restart=True,
            bat_script="core/service-manager.bat",
            bat_function=":disable_xbox",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="svc_search",
            name="Disable Windows Search Indexer",
            category="services",
            description="Stop background file indexing (WSearch)",
            what_it_does="Disables the Windows Search service that continuously indexes files for Start menu and Explorer search.",
            why_it_helps="Eliminates 1-5% constant CPU and disk I/O from indexing. Major improvement on HDD systems.",
            limitations="Start menu search is much slower. File Explorer search won't find content inside files.",
            warnings=[
                "⚠️ Start menu search will be very slow",
                "Use Everything app as replacement",
            ],
            risk_level="MEDIUM",
            expected_gain="1-5% CPU, less disk I/O",
            requires_restart=True,
            bat_script="core/service-manager.bat",
            bat_function=":disable_optional",
            preset_extreme=True,
        ),
        Tweak(
            id="svc_sysmain",
            name="Disable SysMain (Superfetch)",
            category="services",
            description="Stop predictive app preloading",
            what_it_does="Disables SysMain service which preloads frequently used apps into RAM. Also disables Prefetch.",
            why_it_helps="Frees RAM for games instead of preloaded apps. Reduces random disk I/O. Especially useful on systems with 8GB RAM.",
            limitations="Frequently used apps take longer to open initially. First launch after boot is slower.",
            warnings=["Apps may open slower the first time after boot"],
            risk_level="MEDIUM",
            expected_gain="200-500MB RAM freed",
            requires_restart=True,
            bat_script="core/service-manager.bat",
            bat_function=":disable_optional",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="svc_print",
            name="Disable Print Spooler",
            category="services",
            description="Stop printer service (if no printer needed)",
            what_it_does="Disables the Print Spooler service. Frees resources and closes a common attack vector (PrintNightmare).",
            why_it_helps="Removes security vulnerability. Frees ~20MB RAM. Faster boot.",
            limitations="Cannot print to any printer (local or network). Must re-enable to print.",
            warnings=["Cannot print while disabled"],
            risk_level="LOW",
            expected_gain="Security hardening + 20MB RAM",
            requires_restart=True,
            bat_script="core/service-manager.bat",
            bat_function=":disable_optional",
            preset_extreme=True,
        ),
        # ================================================================
        # MEMORY (4 tweaks)
        # ================================================================
        Tweak(
            id="mem_svchost",
            name="SvcHost Split Threshold",
            category="memory",
            description="Reduce service host process splitting overhead",
            what_it_does="Sets SvcHostSplitThresholdInKB based on your RAM amount. Windows splits services into separate processes; this threshold controls when splitting occurs.",
            why_it_helps="On systems with 16GB+ RAM, reduces the number of svchost.exe processes by grouping services. Saves ~200MB RAM. Source: QuickBoost.",
            limitations="Grouped services share memory space. A crash in one service may affect grouped services.",
            warnings=["Set based on your RAM amount"],
            risk_level="MEDIUM",
            expected_gain="~200MB RAM saved",
            requires_restart=True,
            registry_keys=["HKLM\\SYSTEM\\ControlSet001\\Control"],
            bat_script="core/service-manager.bat",
            bat_function=":apply_svchost",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="mem_paging_exec",
            name="Disable Paging Executive",
            category="memory",
            description="Keep kernel and drivers in physical RAM",
            what_it_does="Sets DisablePagingExecutive=1. Forces Windows kernel and hardware drivers to stay in physical RAM instead of being paged to disk.",
            why_it_helps="Prevents micro-stutters from kernel code being paged to disk. More consistent frame times. Source: QuickBoost.",
            limitations="Uses more physical RAM (~100-200MB). Not recommended for systems with less than 8GB RAM.",
            warnings=["Requires 8GB+ RAM"],
            risk_level="MEDIUM",
            expected_gain="Fewer micro-stutters",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management"
            ],
            bat_script="core/service-manager.bat",
            bat_function=":apply_memory",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="mem_large_cache",
            name="Enable Large System Cache",
            category="memory",
            description="Allocate more RAM for system file caching",
            what_it_does="Sets LargeSystemCache=1. Windows uses more RAM for caching system files and game assets, reducing disk reads.",
            why_it_helps="Reduces game stutter from disk I/O. Faster level loading. Most effective on systems with 16GB+ RAM.",
            limitations="Less free RAM available for applications. Not suitable for systems with 8GB or less RAM.",
            warnings=["Best for 16GB+ RAM systems"],
            risk_level="MEDIUM",
            expected_gain="Faster loading, less stutter",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management"
            ],
            bat_script="core/service-manager.bat",
            bat_function=":apply_memory",
            preset_extreme=True,
        ),
        Tweak(
            id="mem_paging_combining",
            name="Disable Page Combining",
            category="memory",
            description="Prevent memory compression and page sharing",
            what_it_does="Sets DisablePagingCombining=1. Disables Windows memory compression and copy-on-write page sharing.",
            why_it_helps="Eliminates CPU overhead from memory compression/decompression. Reduces DPC latency spikes. Source: QuickBoost.",
            limitations="Higher RAM usage since pages aren't shared or compressed. Requires 16GB+ RAM.",
            warnings=["Requires 16GB+ RAM", "Higher memory usage"],
            risk_level="MEDIUM",
            expected_gain="Lower DPC latency",
            registry_keys=[
                "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management"
            ],
            bat_script="core/service-manager.bat",
            bat_function=":apply_memory",
            preset_extreme=True,
        ),
        # ================================================================
        # BOOT / BCDEDIT (5 tweaks)
        # ================================================================
        Tweak(
            id="bcd_dynamic_tick",
            name="Disable Dynamic Tick",
            category="boot",
            description="Use fixed timer interrupts instead of dynamic",
            what_it_does="Sets disabledynamictick=yes. Windows uses a fixed 15.6ms timer interrupt instead of dynamically adjusting. Combined with useplatformtick for consistent timing.",
            why_it_helps="More consistent timer resolution. Reduces jitter in frame timing. Essential for competitive gaming.",
            limitations="Slightly higher power consumption from constant timer interrupts. Requires restart.",
            warnings=["Requires restart", "BCD change"],
            risk_level="MEDIUM",
            expected_gain="More consistent frametimes",
            requires_restart=True,
            bat_script="core/bcdedit-manager.bat",
            bat_function=":apply_safe_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="bcd_tsc_sync",
            name="Enhanced TSC Sync Policy",
            category="boot",
            description="Improve timestamp counter synchronization",
            what_it_does="Sets tscsyncpolicy=enhanced. Uses enhanced synchronization for the Time Stamp Counter across CPU cores.",
            why_it_helps="Better timer accuracy across cores. Reduces timing inconsistencies. Important for multi-threaded games.",
            limitations="Very minor boot time increase.",
            warnings=["Requires restart"],
            risk_level="LOW",
            expected_gain="Better timer accuracy",
            requires_restart=True,
            bat_script="core/bcdedit-manager.bat",
            bat_function=":apply_safe_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="bcd_x2apic",
            name="Enable x2APIC Mode",
            category="boot",
            description="Use improved interrupt handling on modern CPUs",
            what_it_does="Sets x2apicpolicy=Enable. Uses the extended APIC mode for faster interrupt delivery on modern CPUs. Source: Ghost-Optimizer.",
            why_it_helps="Faster interrupt handling reduces DPC latency. More efficient CPU interrupt routing.",
            limitations="CPU must support x2APIC (most CPUs since 2010+). Falls back silently if unsupported.",
            warnings=["Requires restart"],
            risk_level="LOW",
            expected_gain="~1ms DPC improvement",
            requires_restart=True,
            bat_script="core/bcdedit-manager.bat",
            bat_function=":apply_safe_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="bcd_configaccess",
            name="Default Config Access Policy",
            category="boot",
            description="Faster MMIO access for hardware",
            what_it_does="Sets configaccesspolicy=Default. Uses default (faster) memory-mapped I/O access instead of locked access. Source: Ghost-Optimizer.",
            why_it_helps="Slightly faster hardware communication. Reduces boot-time hardware initialization latency.",
            limitations="On very rare hardware, may cause boot issues. Easily reversible with bcdedit /deletevalue.",
            warnings=["Requires restart"],
            risk_level="LOW",
            expected_gain="Faster hardware access",
            requires_restart=True,
            bat_script="core/bcdedit-manager.bat",
            bat_function=":apply_safe_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="bcd_hypervisor",
            name="Disable Hypervisor",
            category="boot",
            description="Turn off Hyper-V for maximum CPU performance",
            what_it_does="Sets hypervisorlaunchtype=off. Disables the Windows hypervisor that enables WSL2, Docker, and Hyper-V virtual machines.",
            why_it_helps="Removes hypervisor overhead (2-5% CPU). Direct hardware access for games. Lower interrupt latency.",
            limitations="WSL2 won't work. Docker Desktop won't work. Hyper-V VMs won't start. Android emulators may fail.",
            warnings=[
                "⚠️ Breaks WSL2, Docker, and Hyper-V",
                "Only for dedicated gaming PCs",
            ],
            risk_level="HIGH",
            expected_gain="2-5% CPU performance",
            requires_restart=True,
            bat_script="core/bcdedit-manager.bat",
            bat_function=":apply_advanced_tweaks",
            preset_extreme=True,
        ),
        # ================================================================
        # VISUAL EFFECTS (4 tweaks)
        # ================================================================
        Tweak(
            id="vis_animations",
            name="Disable Window Animations",
            category="visual",
            description="Remove minimize, maximize, and fade animations",
            what_it_does="Disables MinAnimate, TaskbarAnimations, and all window transition effects. Windows appear/disappear instantly.",
            why_it_helps="Eliminates GPU time spent on animations. Windows feel more responsive. 1-2% GPU freed on integrated graphics.",
            limitations="UI feels less polished. No smooth transitions.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Snappier UI, 1-2% GPU on iGPU",
            registry_keys=[
                "HKCU\\Control Panel\\Desktop\\WindowMetrics",
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced",
            ],
            bat_script="core/registry-utils.bat",
            bat_function=":apply_visual_tweaks",
            preset_safe=True,
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="vis_transparency",
            name="Disable Transparency Effects",
            category="visual",
            description="Remove blur and transparency from taskbar and windows",
            what_it_does="Disables acrylic/mica transparency effects in Windows 10/11. Taskbar, Start menu, and Action Center become opaque.",
            why_it_helps="Saves GPU resources used for blur calculations. Especially impactful on integrated graphics (3-5% GPU).",
            limitations="Flat, opaque appearance. Less visually appealing UI.",
            warnings=[],
            risk_level="LOW",
            expected_gain="3-5% GPU on integrated graphics",
            registry_keys=[
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize"
            ],
            bat_script="core/registry-utils.bat",
            bat_function=":apply_visual_tweaks",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="vis_drag_full",
            name="Disable Full Window Drag",
            category="visual",
            description="Show outline instead of full window when dragging",
            what_it_does="Sets DragFullWindows=0. When dragging a window, only an outline moves instead of rendering the full window content.",
            why_it_helps="Reduces GPU rendering during window management. Minor performance gain.",
            limitations="Can't see window content while dragging.",
            warnings=[],
            risk_level="LOW",
            expected_gain="Minor GPU reduction",
            registry_keys=["HKCU\\Control Panel\\Desktop"],
            bat_script="core/registry-utils.bat",
            bat_function=":apply_visual_tweaks",
            preset_extreme=True,
        ),
        Tweak(
            id="vis_visual_fx",
            name="Best Performance Visual Settings",
            category="visual",
            description="Set Windows to 'Adjust for best performance'",
            what_it_does="Sets VisualFXSetting=3 (best performance). Disables all visual effects: shadows, thumbnails, smooth scrolling, Aero Peek, etc.",
            why_it_helps="Maximum GPU resources for games. Eliminates all compositor overhead. Significant on low-end systems.",
            limitations="Windows looks like Windows 2000. No font smoothing. No thumbnail previews. Very spartan appearance.",
            warnings=["UI will look very basic"],
            risk_level="LOW",
            expected_gain="5-10% on low-end GPUs",
            registry_keys=[
                "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects"
            ],
            bat_script="core/registry-utils.bat",
            bat_function=":apply_visual_tweaks",
            preset_extreme=True,
        ),
        # ================================================================
        # CLEANUP & DEBLOAT (3 tweaks)
        # ================================================================
        Tweak(
            id="cln_bloatware",
            name="Remove Windows Bloatware",
            category="cleanup",
            description="Uninstall pre-installed apps you don't need",
            what_it_does="Removes 30+ pre-installed apps: Bing apps, social media, entertainment, etc. Protected apps (Calculator, Photos, Store, Notepad, Terminal, Defender) are kept.",
            why_it_helps="Frees 1-3GB disk space. Removes background update processes for unused apps. Cleaner Start menu.",
            limitations="Removed apps are gone (can reinstall from Microsoft Store). Some users may want specific apps.",
            warnings=["Apps can be reinstalled from Microsoft Store if needed"],
            risk_level="MEDIUM",
            expected_gain="1-3GB disk space, cleaner system",
            bat_script="core/debloater.bat",
            bat_function=":apply_debloat",
            preset_extreme=True,
        ),
        Tweak(
            id="cln_onedrive",
            name="Disable OneDrive Auto-Start",
            category="cleanup",
            description="Stop OneDrive from running at startup",
            what_it_does="Removes OneDrive from startup registry. OneDrive won't launch automatically when you log in. You can still open it manually.",
            why_it_helps="Frees 50-200MB RAM and CPU from OneDrive sync. Faster login time.",
            limitations="Files won't sync automatically. Must open OneDrive manually when needed.",
            warnings=["Cloud sync paused until manually opened"],
            risk_level="LOW",
            expected_gain="50-200MB RAM, faster login",
            registry_keys=["HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"],
            bat_script="core/debloater.bat",
            bat_function=":apply_onedrive",
            preset_competitive=True,
            preset_extreme=True,
        ),
        Tweak(
            id="cln_ntfs",
            name="NTFS File System Optimizations",
            category="cleanup",
            description="Disable last access timestamps and 8.3 names",
            what_it_does="Disables NtfsDisableLastAccessUpdate and 8.3 name creation. Removes overhead from tracking file access times and creating legacy short filenames.",
            why_it_helps="Reduces disk write operations by 5-10%. Faster file operations, especially with many small files.",
            limitations="Programs that rely on last access time won't see accurate data. Very old 16-bit programs may not find files.",
            warnings=[],
            risk_level="LOW",
            expected_gain="5-10% faster file operations",
            bat_script="core/storage-optimizer.bat",
            bat_function=":apply_ntfs",
            preset_competitive=True,
            preset_extreme=True,
        ),
    ]


class TweakRegistry:
    """Central registry for all optimization tweaks"""

    def __init__(self):
        self._tweaks = {t.id: t for t in _build_tweaks()}
        logger.info(f"TweakRegistry loaded: {len(self._tweaks)} tweaks")

    def get_all_tweaks(self) -> List[Tweak]:
        """Get all tweaks"""
        return list(self._tweaks.values())

    def get_tweak(self, tweak_id: str) -> Optional[Tweak]:
        """Get tweak by ID"""
        return self._tweaks.get(tweak_id)

    def get_tweaks_by_category(self, category: str) -> List[Tweak]:
        """Get tweaks filtered by category"""
        return [t for t in self._tweaks.values() if t.category == category]

    def get_tweaks_for_preset(self, preset: str) -> List[Tweak]:
        """Get tweaks included in a preset (safe/competitive/extreme)"""
        attr = f"preset_{preset.lower()}"
        return [t for t in self._tweaks.values() if getattr(t, attr, False)]

    def get_compatible_tweaks(self, system_profile: Any) -> List[Tweak]:
        """Filter tweaks by system compatibility"""
        compatible = []
        os_ver = getattr(system_profile, "os", None)
        os_version = (
            "11" if os_ver and "11" in str(getattr(os_ver, "version", "")) else "10"
        )
        gpu_vendor = ""
        if hasattr(system_profile, "gpu"):
            gpu_vendor = getattr(system_profile.gpu, "vendor", "").upper()

        for t in self._tweaks.values():
            # Check OS
            if os_version not in t.compatible_os:
                continue
            # Check hardware
            if t.compatible_hardware:
                if "gpu_vendor" in t.compatible_hardware:
                    if t.compatible_hardware["gpu_vendor"].upper() not in gpu_vendor:
                        continue
                if "cpu_vendor" in t.compatible_hardware:
                    cpu_vendor = ""
                    if hasattr(system_profile, "cpu"):
                        cpu_vendor = getattr(system_profile.cpu, "vendor", "").upper()
                    if t.compatible_hardware["cpu_vendor"].upper() not in cpu_vendor:
                        continue
            compatible.append(t)
        return compatible

    def suggest_preset(self, system_profile: Any) -> Dict[str, Any]:
        """Suggest a preset based on system specs.

        .. deprecated::
            Use ``core.recommendation_service.recommend_preset()`` instead.
            This method is kept for backward compatibility and now delegates
            to the unified recommendation service, augmenting the result with
            tweak/compatibility counts that callers may still need.
        """
        from core.recommendation_service import recommend_preset

        result = recommend_preset(system_profile)
        preset = result.preset

        return {
            "preset": preset,
            "reason": result.reason,
            "source": result.source,
            "total_score": result.total_score,
            "confidence": result.confidence,
            "tweak_count": len(self.get_tweaks_for_preset(preset)),
            "compatible_count": len(self.get_compatible_tweaks(system_profile)),
        }

    def get_category_stats(self) -> Dict[str, int]:
        """Get count of tweaks per category"""
        stats = {}
        for t in self._tweaks.values():
            stats[t.category] = stats.get(t.category, 0) + 1
        return stats

    def get_risk_distribution(self) -> Dict[str, int]:
        """Get count of tweaks per risk level"""
        dist = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for t in self._tweaks.values():
            dist[t.risk_level] = dist.get(t.risk_level, 0) + 1
        return dist

    def build_custom_preset(self, tweak_ids: List[str]) -> Dict[str, Any]:
        """Validate and build a custom preset from selected tweak IDs"""
        tweaks = []
        warnings = []
        requires_restart = False
        max_risk = "LOW"
        risk_order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}

        for tid in tweak_ids:
            t = self._tweaks.get(tid)
            if not t:
                warnings.append(f"Unknown tweak ID: {tid}")
                continue
            tweaks.append(t)
            if t.requires_restart:
                requires_restart = True
            if risk_order.get(t.risk_level, 0) > risk_order.get(max_risk, 0):
                max_risk = t.risk_level
            warnings.extend(t.warnings)

        return {
            "tweaks": tweaks,
            "count": len(tweaks),
            "max_risk": max_risk,
            "requires_restart": requires_restart,
            "warnings": list(set(warnings)),
        }


# Singleton
_registry_instance: Optional[TweakRegistry] = None


def get_tweak_registry() -> TweakRegistry:
    """Get singleton TweakRegistry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = TweakRegistry()
    return _registry_instance

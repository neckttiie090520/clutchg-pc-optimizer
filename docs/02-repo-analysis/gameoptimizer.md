# GameOptimizer Analysis

> **Repository:** [github.com/vdavidyang/GameOptimizer](https://github.com/vdavidyang/GameOptimizer)
> **Primary Focus:** Game process priority optimization, Anti-cheat CPU affinity limiting
> **Platform:** Windows 10/11
> **Language:** Batch (.bat) and PowerShell (.ps1)
> **License:** MIT License

## Overview

GameOptimizer is a specialized Windows optimization tool that focuses exclusively on process scheduling optimizations. Unlike general-purpose optimizers, it targets two specific mechanisms:
1. **Process Priority**: Sets game executables to High priority via registry
2. **CPU Affinity**: Restricts anti-cheat processes to the last CPU core with Idle priority

The author claims this approach reduces game stuttering and can improve FPS by 10-20 frames.

## Primary Goals

1. **Reduce Game Stuttering** - Prioritize game process scheduling
2. **Limit Anti-Cheat Impact** - Restrict Tencent anti-cheat to single core
3. **Persistent Optimization** - Registry-based settings survive reboots
4. **On-Demand Tuning** - Runtime script for active processes

## Tweak Categories Extracted

### 1. Registry-Based Process Priority (Persistent)

| Game/Process | Registry Path | CPU Priority | I/O Priority | Validity |
|--------------|---------------|--------------|--------------|----------|
| League of Legends | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\League of Legends.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Crossfire | `...\crossfire.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| VALORANT (2 processes) | `...\VALORANT-Win64-Shipping.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Delta Force (WeGame) | `...\DeltaForce-Win64-Shipping.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Delta Force (Official) | `...\DeltaForceClient-Win64-Shipping.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Gunshooter (TPS) | `...\TPS.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| FragPunk | `...\FragPunk.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Overwatch | `...\Overwatch.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| CS2 | `...\cs2.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Alloy Arena | `...\UAgame.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |
| Naraka: Bladepoint | `...\NarakaBladepoint.exe\PerfOptions` | 3 (High) | 3 (High) | ✅ Valid |

**Registry Key Details:**
- **CpuPriorityClass**: DWORD value (1=Idle, 2=Normal, 3=High, 4=Realtime)
- **IoPriority**: DWORD value (0=Very Low, 1=Low, 2=Normal, 3=High)
- **Persistence**: These settings apply automatically whenever the executable runs

### 2. Anti-Cheat Process Limiting (Runtime)

| Process | CPU Affinity | Priority Class | Purpose | Validity |
|---------|--------------|----------------|---------|----------|
| SGuard.exe | Last core only | Idle | Tencent anti-cheat (32-bit) | ⚠️ Risky |
| SGuard64.exe | Last core only | Idle | Tencent anti-cheat (64-bit) | ⚠️ Risky |
| SGuardSvc64.exe | Last core only | Idle | Tencent anti-cheat service | ⚠️ Risky |

**Implementation Details:**
- **Script**: `SetProcessPriority.ps1`
- **CPU Affinity Calculation**: `[IntPtr]::new([Int64]1 -shl ($cpuCount - 1))`
  - For 8 cores: Binary `10000000` (decimal 128)
  - For 16 cores: Binary `1000000000000000` (decimal 32768)
  - **Fixed in v2.1**: Handles CPUs with ≥32 logical cores
- **Timing**: Must be run after game launches (when anti-cheat processes are active)

### 3. Shortcut Automation

| Feature | Implementation | Validity |
|---------|----------------|----------|
| Desktop shortcut creation | PowerShell WScript.Shell COM object | ✅ Safe |
| Admin flag enforcement | Modify shortcut byte 0x15 with OR 0x20 | ✅ Valid technique |
| Working directory preservation | Uses script's directory | ✅ Proper |

## Technical Analysis

### What Works Well

1. **Image File Execution Options (IFEO) Optimization**
   - Registry-based priority is the correct way to set persistent process priorities
   - IFEO is the documented Windows mechanism for process-specific settings
   - Applies automatically on process launch - no manual intervention needed

2. **Dual Priority Approach**
   - CPU Priority Class (3 = High) prioritizes CPU time allocation
   - I/O Priority (3 = High) prioritizes disk/network I/O operations
   - Both are meaningful for gaming performance

3. **CPU Affinity for Anti-Cheat**
   - Technically valid approach to isolate background processes
   - Bit shifting logic is mathematically correct
   - The fix for ≥32 core systems shows active maintenance

4. **Safety Features**
   - Requires administrator privileges (necessary for registry changes)
   - Includes deletion script to revert changes
   - Doesn't modify game files or memory

### Problematic Aspects

1. **Anti-Cheat Restriction Risks**
   - **CRITICAL**: Limiting anti-cheat processes may trigger detection systems
   - Tencent's TenProtect actively monitors for process manipulation
   - Binding to single core could cause anti-cheat performance issues
   - **Author's claim**: "Absolutely safe! Long-term streamer testing"
   - **Reality**: Anti-cheat systems can ban for any form of process manipulation

2. **Limited Applicability**
   - Only targets Tencent games with SGuard anti-cheat
   - Not applicable to other games (Easy Anti-Cheat, BattlEye, etc.)
   - Registry tweaks only work if you play the specific supported games

3. **Inconsistent Priority Levels**
   - Anti-cheat set to **CPU Priority 1 (Idle)** but **I/O Priority 0 (Very Low)**
   - Registry script comments say "CPU=1 (Low)" but Windows calls it "Idle"
   - Documentation inconsistency could confuse users

4. **Runtime Script Limitations**
   - `SetProcessPriority.ps1` must be manually run after each game launch
   - No automatic process monitoring
   - If anti-cheat restarts during gaming session, restrictions are lost

5. **Missing Error Handling**
   - PowerShell script has try-catch blocks but only displays errors
   - No verification that changes actually persist
   - Silent failures could mislead users

6. **No Backup Creation**
   - Registry changes are not backed up before modification
   - Deletion script is the only recovery mechanism
   - If deletion script is lost, changes are difficult to reverse manually

## Risk Assessment

| Category | Risk Level | Detailed Analysis |
|----------|------------|-------------------|
| **Game Bans** | **HIGH** | Anti-cheat manipulation violates many ToS agreements |
| **Stability** | **Medium** | Single-core affinity may starve anti-cheat, causing disconnects |
| **Security** | **Low** | No security-breaking tweaks |
| **Reversibility** | **Good** | Dedicated deletion script provided |
| **System Impact** | **Low** | Only affects specific game executables |
| **Compatibility** | **Medium** | Only works for Tencent games with SGuard |

## Anti-Cheat Risk Analysis

### Why This Is Dangerous

1. **Terms of Service Violations**
   - Most anti-cheat EULAs explicitly forbid process manipulation
   - Tencent's TenProtect is particularly aggressive
   - "Optimization" is not a valid defense if detected

2. **Detection Vectors**
   - Process priority changes are visible via Windows API
   - CPU affinity changes are easily detected
   - Anti-cheat systems scan for unusual process configurations

3. **Account Risk**
   - Bans are typically permanent
   - Appeals rarely succeed for ToS violations
   - Account loss includes all purchases and progress

### Author's Defense vs Reality

| Author's Claim | Technical Reality |
|----------------|-------------------|
| "Absolutely safe! Only adjusts system scheduling rules" | True technically, but violates ToS |
| "Doesn't inject or modify game memory" | True, but still detectable |
| "Streamer long-term testing" | Anecdotal evidence ≠ Ban guarantee |
| "Won't be banned" | **FALSE** - Anti-cheat can detect this |

## Windows 10/11 Compatibility

| Feature | Windows 10 | Windows 11 | Notes |
|---------|-----------|-----------|-------|
| IFEO Registry | ✅ Fully supported | ✅ Fully supported | Core Windows feature |
| CPU Affinity | ✅ Supported | ✅ Supported | Limited to 64 logical processors |
| PowerShell commands | ✅ Compatible | ✅ Compatible | Uses standard cmdlets |
| UAC Elevation | ✅ Supported | ✅ Supported | Standard VBScript technique |
| Execution Policy | ⚠️ Needs Bypass | ⚠️ Needs Bypass | Security consideration |

**Windows 7 Compatibility:**
- Author notes: "PowerShell may not support Windows 7"
- IFEO exists in Windows 7 but PowerShell version may be outdated
- Not officially supported

## Code Quality Assessment

### Batch Scripts (一键设置游戏优先级（注册表）_通用版.bat)

**Strengths:**
- Proper UAC elevation implementation
- Clear user confirmation prompts
- Structured code with subroutines (`:SetPriority`)
- Comments explain priority values
- ASCII art boxes for visual appeal

**Weaknesses:**
- Chinese-only output (no i18n)
- Hardcoded game list (not easily extensible)
- No backup before registry changes
- Inconsistent commenting (mix of Chinese and English comments in source)

### PowerShell Script (SetProcessPriority.ps1)

**Strengths:**
- Administrator privilege verification
- Error handling with try-catch blocks
- Process filtering by specific names
- Status output with color coding
- Automatic countdown before exit

**Weaknesses:**
- No logging of changes made
- No verification that changes persist
- Hardcoded process list
- Chinese encoding issues (file has garbled comments)
- No persistence monitoring

### Shortcut Creation Script (一键新建快捷方式.bat)

**Strengths:**
- Proper PowerShell integration
- Desktop path detection via .NET framework
- Admin flag modification (byte 0x15)
- Verification of shortcut creation

**Weaknesses:**
- Assumes script names in Chinese
- No error handling for PowerShell failures
- Hardcoded filenames

## Effectiveness Analysis

### Registry Priority Tweaks

**Expected Impact: Low-Medium**

**Why Limited:**
1. **Windows Scheduler Already Prioritizes Foreground Apps**
   - Modern Windows (8+) automatically boosts foreground process priority
   - Games already receive scheduling preference when visible
   - Registry changes may provide minimal additional benefit

2. **Priority Inversion**
   - High-priority processes waiting on low-priority resources can cause worse performance
   - If game depends on system services, starving them hurts performance

3. **I/O Priority Already High for Games**
   - Games typically get high I/O priority automatically
   - Explicitly setting it may have marginal impact

**Best Case Scenario:**
- 5-10% improvement in frame consistency
- Reduced background process interference during CPU-heavy scenes

**Realistic Impact:**
- 0-5 FPS improvement
- Potentially reduced 1% low frame dips
- Placebo effect likely for many users

### Anti-Cheat CPU Affinity

**Expected Impact: Low**

**Why Limited:**
1. **Anti-Cheat is Already Low-Priority**
   - SGuard typically runs at background priority
   - Most anti-cheat systems are designed to minimize impact
   - Restricting to one core may not provide noticeable benefit

2. **Single-Core Bottleneck**
   - If anti-cheat needs more resources, it will lag
   - Lagging anti-cheat can cause game disconnects
   - Risk outweighs minimal benefit

3. **Modern CPU Efficiency**
   - Modern CPUs have efficient scheduling
   - Background processes already get deprioritized
   - Manual intervention is rarely necessary

**Realistic Impact:**
- Negligible FPS improvement (<2%)
- Higher risk of anti-cheat issues
- Not worth the ban risk

## Comparison to Alternatives

| Method | Risk | Effectiveness | Effort |
|--------|------|---------------|--------|
| **GameOptimizer (Registry)** | Medium (ToS) | Low-Medium | One-time setup |
| **GameOptimizer (Runtime)** | **High (Ban)** | Very Low | Every game session |
| **Windows Game Mode** | None | Low | Built-in |
| **Process Lasso** | Low | Medium | Paid software |
| **Manual priority (Task Manager)** | Low | Very Low | Every game session |
| **Driver optimizations** | None | High | One-time setup |

## Verdict

**Rating: 4/10**

GameOptimizer is a technically competent but misguided tool. While the implementation of registry-based process priorities is sound, the anti-cheat restriction approach introduces unnecessary risk for minimal gain.

### Breakdown

| Criterion | Score | Notes |
|-----------|-------|-------|
| **Technical Quality** | 7/10 | Well-implemented but lacks error handling |
| **Effectiveness** | 4/10 | Registry tweaks: Low impact; Anti-cheat tweaks: Negligible |
| **Safety** | 3/10 | Anti-cheat manipulation is high-risk |
| **Documentation** | 6/10 | Clear instructions, but downplays risks |
| **Reversibility** | 8/10 | Deletion script provided |
| **Value Proposition** | 3/10 | High risk for minimal reward |

### Recommendations

#### For Users

1. ❌ **AVOID anti-cheat restriction script** (`SetProcessPriority.ps1`)
   - Ban risk exceeds any performance benefit
   - Tencent anti-cheat is particularly aggressive
   - Not worth losing your account

2. ⚠️ **Use registry tweaks with caution**
   - May provide minor improvements
   - Reversible if needed
   - Less likely to trigger anti-cheat detection

3. ✅ **Use built-in alternatives instead**
   - Enable **Game Mode** in Windows 10/11 (Settings → Gaming → Game Mode)
   - Set power plan to **High Performance** or **Ultimate Performance**
   - Update GPU drivers
   - Close background applications manually

4. ✅ **If you must use this tool**
   - Never use the anti-cheat script
   - Only use the registry script for games you actually play
   - Keep the deletion script for backup
   - Manually export registry keys before running:
   ```cmd
   reg export "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options" backup.reg
   ```

#### For the Author

1. **Remove Anti-Cheat Restrictions**
   - This feature endangers users' accounts
   - Minimal performance benefit does not justify the risk
   - Irresponsible to distribute without prominent warnings

2. **Add Backup Functionality**
   - Export registry keys before modification
   - Store backup file with timestamp
   - Provide restore functionality

3. **Improve Error Handling**
   - Verify registry writes succeed
   - Log all changes to file
   - Provide rollback on failure

4. **Add Disclaimer**
   - Clearly warn about anti-cheat ToS risks
   - Explain that registry tweaks are safer
   - Recommend against anti-cheat script for competitive games

5. **Internationalization**
   - Translate scripts to English
   - Use UTF-8 encoding for proper character display
   - Widen potential user base

## Conclusion

GameOptimizer demonstrates a solid understanding of Windows process scheduling mechanisms, particularly the IFEO registry technique. However, the inclusion of anti-cheat process manipulation is irresponsible and potentially dangerous for users.

The registry priority tweaks are relatively safe and may provide minor performance improvements for competitive gamers. However, the anti-cheat CPU affinity restrictions should be avoided entirely due to the high risk of account bans.

**Final Recommendation:** Use the registry tweaks only if you're desperate for every last frame of performance, but **absolutely avoid the anti-cheat restriction script**. There are safer ways to optimize your system that don't violate game ToS agreements.

---

**Analysis Date:** January 4, 2026
**Repository Version:** v2.3.3
**Analyzer:** Technical Review of Public Code
**License Compliance:** This analysis is permitted under MIT License for educational purposes.

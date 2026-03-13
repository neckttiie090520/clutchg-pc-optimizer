# ClutchG User Manual

> **Version:** 1.0
> **Date:** 6 February 2026
> **Language:** English
> **For:** Windows 10 22H2+ and Windows 11 23H2+

---

## Table of Contents

1. [About ClutchG](#1-about-clutchg)
2. [Installation](#2-installation)
3. [First Run](#3-first-run)
4. [Key Terminology](#4-key-terminology)
5. [Dashboard Overview](#5-dashboard-overview)
6. [Optimization Profiles](#6-optimization-profiles)
7. [Script Library](#7-script-library)
8. [Backup & Restore Center](#8-backup--restore-center)
9. [Help & Documentation](#9-help--documentation)
10. [Settings](#10-settings)
11. [Troubleshooting](#11-troubleshooting)
12. [FAQ](#12-faq-frequently-asked-questions)
13. [Additional Resources](#13-additional-resources)

---

## 1. About ClutchG

### 1.1 What is ClutchG?

**ClutchG** is a Windows PC optimization tool for gaming and performance, designed to:

- ✅ **Improve gaming FPS**
- ✅ **Reduce latency** (ping, input lag)
- ✅ **Enhance system responsiveness**
- ✅ **Work safely** - All changes are reversible
- ✅ **Use evidence** - Developed from research of 28 repositories

### 1.2 Core Principles

**Safety-First Philosophy:**
- ❌ **Never disable** Windows Defender
- ❌ **Never disable** Windows Update
- ❌ **Never disable** DEP/ASLR/CFG (security features)
- ✅ **Every tweak is reversible**
- ✅ **Automatic backups** before applying
- ✅ **Log every operation** for audit

### 1.3 When to Use ClutchG?

**Use ClutchG if:**
- You game and want higher FPS
- You have high ping or input lag
- Windows feels sluggish
- You want to clean bloatware

**Don't use if:**
- PC is for general office use (not gaming-focused)
- You're not comfortable tweaking PC settings
- You have less than 500 MB free disk space

### 1.4 System Requirements

**Minimum:**
- Windows 10 22H2 (Build 19045) or later
- Windows 11 23H2 (Build 22631) recommended
- 4 GB+ RAM
- 500 MB+ free disk space for backups
- Python 3.11+
- Administrator rights

**Recommended:**
- 8 GB+ RAM
- SSD storage
- 4+ core CPU (Intel/AMD)
- Dedicated GPU (NVIDIA/AMD)

---

## 2. Installation

### 2.1 Install Python Dependencies

**Step 1:** Open Command Prompt or PowerShell

**Step 2:** Navigate to ClutchG folder:
```bash
cd C:\Users\nextzus\Documents\thesis\bat\clutchg
```

**Step 3:** Install dependencies:
```bash
pip install -r requirements.txt
```

**Dependencies Installed:**
- `customtkinter>=5.2.0` - UI framework
- `Pillow>=10.0.0` - Image processing
- `psutil>=5.9.0` - System information
- `pywin32>=306` - Windows API

### 2.2 Install Material Symbols Font (Optional)

ClutchG uses **Material Symbols Outlined** font for icons

**If icons don't display:**
1. Download font: https://fonts.google.com/icons
2. Install font (right-click → Install)
3. Restart ClutchG

**Fallback:**
- Windows will automatically use **Segoe MDL2 Assets**
- Icons will still display correctly

### 2.3 Run Application

**Option 1: Run with Python**
```bash
cd clutchg\src
python app_minimal.py
```

**Option 2: Run with main.py**
```bash
cd clutchg\src
python main.py
```

**⚠️ Important:** Must run **as Administrator**

**How to run as Administrator:**
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Navigate and run application

### 2.4 Verify Installation

**On first open:**
- You should see **Welcome overlay** (introductory window)
- You should see **Dashboard** with system info
- You should see **sidebar** on the left

**If icons appear as squares:**
- Material Symbols font not installed
- ClutchG will fallback to Segoe MDL2 Assets
- If still failing, install font per section 2.2

---

## 3. First Run

### 3.1 Welcome Overlay

When you first open ClutchG, you'll see the **Welcome overlay** - an introductory walkthrough

**5 Steps in Welcome:**

**Step 1: Welcome**
- Introduces ClutchG
- Explains philosophy (safe, evidence-based)

**Step 2: Dashboard Overview**
- Explains Performance Score
- Hardware detection

**Step 3: Choose Your Profile**
- **SAFE** - For beginners
- **COMPETITIVE** - For gamers
- **EXTREME** - For advanced users

**Step 4: Automatic Backups**
- Explains every optimize has backup
- System restore points
- Registry backups

**Step 5: Ready to Optimize!**
- Explains profile application steps
- Suggests going to Profiles tab

**Buttons:**
- **← Back** - Go back
- **Next →** - Next step
- **Skip Tutorial** - Skip tutorial

### 3.2 System Detection

ClutchG automatically detects hardware:

**What's Detected:**
- **CPU** - Vendor (Intel/AMD), cores, threads
- **GPU** - Primary GPU model
- **RAM** - Total, available, usage %
- **OS** - Windows version, build number

**This info is used to:**
- Display in Dashboard
- Calculate Performance Score
- Apply appropriate tweaks for your hardware

### 3.3 Performance Score

**Performance Score** is a 0-100 score indicating your PC's potential

**Calculated from:**
- CPU cores/threads
- RAM capacity
- GPU model (if available)
- SSD or HDD

**Meaning:**
- **90-100** - High-end gaming PC
- **70-89** - Mid-range gaming PC
- **50-69** - Entry-level gaming PC
- **0-49** - Office/Basic PC

**⚠️ Note:** Score is not real FPS, but potential score

---

## 4. Key Terminology

### 4.1 Technical Terms

| Term | Meaning |
|------|---------|
| **Tweak** | Small registry/settings adjustment |
| **Profile** | Set of tweaks grouped for a purpose |
| **Backup** | Copy of registry/settings before changes |
| **Restore** | Revert settings from backup |
| **Registry** | Windows settings database |
| **System Restore Point** | Windows system rollback point |
| **Timeline** | Visual history of tweaks |
| **Flight Recorder** | System logging every tweak in detail |

### 4.2 Risk Levels

**LOW RISK (🟢):**
- 100% safe tweak
- No functionality impact
- Suitable for everyone

**MEDIUM RISK (🟡):**
- May affect some features
- Recommended to test
- Backup required

**HIGH RISK (🔴):**
- Impacts multiple functionalities
- Experts only
- Must understand consequences

---

## 5. Dashboard Overview

### 5.1 What is Dashboard?

Dashboard is the main screen showing your system overview

**Components:**
1. **System Info Card** - Hardware summary
2. **Performance Score** - Efficiency score
3. **Quick Actions** - Shortcut buttons
4. **Recent Activity** - Recent tweaks

### 5.2 System Info Card

**Displays:**
- **CPU** - Vendor, cores, threads
- **GPU** - Model name
- **RAM** - Total GB, used GB
- **OS** - Windows version

**Refresh:**
- Click **Refresh button** to recheck
- Use after hardware upgrades

### 5.3 Performance Score

**Displays:**
- Score 0-100 with color
- 🟢 90-100 (Excellent)
- 🟡 70-89 (Good)
- 🟠 50-69 (Fair)
- 🔴 0-49 (Poor)

**Tip:**
- Score is not real FPS
- But indicates hardware potential

### 5.4 Quick Actions

**Shortcuts:**
- **Create Backup** - Create backup immediately
- **View Timeline** - View tweak history
- **System Info** - View hardware details

---

## 6. Optimization Profiles

### 6.1 What are Profiles?

**Profiles** are pre-configured tweak sets designed for specific purposes

ClutchG has 3 profiles:

### 6.2 SAFE Profile (🛡️ LOW RISK)

**For:**
- Beginners
- General users
- Stability lovers

**What it does:**
- ✅ Disable bloatware
- ✅ Disable unnecessary services
- ✅ Adjust privacy settings
- ✅ Disable GameDVR
- ✅ Adjust power plan

**What it doesn't do:**
- ❌ Doesn't disable Windows Defender
- ❌ Doesn't disable Windows Update
- ❌ Doesn't touch security features

**Expected Improvement:**
- FPS: +2-5%
- Responsiveness: +1-3%

**Good for:**
- Everyone unsure
- Office PCs
- Those wanting stability

### 6.3 COMPETITIVE Profile (⚡ MEDIUM RISK)

**For:**
- Gamers
- Those wanting low latency
- People understanding risks

**What it does:**
- Everything in SAFE +
- ✅ Network optimization
- ✅ Disable telemetry
- ✅ Aggressive power settings
- ✅ Memory optimization
- ✅ Gaming service tweaks

**Expected Improvement:**
- FPS: +5-10%
- Ping: -5-15ms
- Input lag: -5-10ms

**Good for:**
- Competitive gamers
- FPS game players (CS2, Valorant)
- Those wanting an edge in competition

### 6.4 EXTREME Profile (🔥 HIGH RISK)

**For:**
- Benchmarkers
- Enthusiasts
- People understanding consequences

**Warnings before use:**
- ⚠️ May remove some features
- ⚠️ Not recommended for daily drivers
- ⚠️ Always have backup

**What it does:**
- Everything in COMPETITIVE +
- ✅ Disable Windows Defender (if other AV present)
- ✅ Disable automatic Windows Update
- ✅ Aggressive memory cleaning
- ✅ Strip down Windows features

**Expected Improvement:**
- FPS: +10-15%
- System resources: -10-20% usage

**Good for:**
- Benchmark rigs
- Performance testing
- Not for daily drivers

### 6.5 Applying a Profile

**Step 1:** Go to **Profiles tab** in sidebar

**Step 2:** Select desired profile

**Step 3:** Read descriptions and risks

**Step 4:** Click **Apply** button

**Step 5:** **Confirmation Dialog**
- Warnings displayed if any
- Read and understand warnings
- Click **Yes** if agree, **No** if not

**Step 6:** **Execution Dialog**
- Shows progress
- Shows applied tweaks
- Shows results (SUCCESS/FAILED)

**Step 7:** **Finish**
- Toast notification shows result
- Backup created automatically before apply

### 6.6 After Applying Profile

**Check:**
1. Restart PC if prompted
2. Test gaming
3. Verify no issues

**If problems:**
- Go to **Backup & Restore Center**
- Restore from latest backup
- PC returns to previous state

---

## 7. Script Library

### 7.1 What are Scripts?

**Scripts** are batch scripts performing specific tweaks

**Difference from Profiles:**
- Profiles = Multiple tweaks
- Scripts = Single or specific group of tweaks

### 7.2 When to Use Scripts?

**Use scripts if:**
- Want specific tweaks
- Don't want to apply entire profile
- Want detailed control

**Examples:**
- Disable GameDVR only
- Optimize network only
- Clear cache only

### 7.3 Using Script Library

**Step 1:** Go to **Scripts tab** in sidebar

**Step 2:** See all scripts in grid

**Step 3:** **Search** (if don't remember name)
- Type in search box
- List filters by query

**Step 4:** Select desired script

**Step 5:** Read details:
- **Name** - Script name
- **Filename** - Actual filename
- **Risk Level** - LOW/MEDIUM/HIGH

**Step 6:** Click **RUN** button

**Step 7:** **Execution Dialog**
- Shows output
- Shows progress
- Shows result

### 7.4 Risk Indicators

**🟢 LOW (Green):**
- 100% safe
- No system impact

**🟡 MEDIUM (Yellow):**
- May affect some features
- Recommended to read descriptions

**🔴 HIGH (Red):**
- Impacts functionality
- Experts only

---

## 8. Backup & Restore Center

### 8.1 Know Backup & Restore Center

Backup & Restore Center is the central point for managing all backups

**2 Modes:**
1. **Simple Mode** - Easy backup management
2. **Advanced Mode** - Timeline visualization with Flight Recorder

### 8.2 Simple Mode (Default)

**What it is:**
- Shows backups as cards
- Good for general users

**What you can do:**
- ✅ Create backup
- ✅ View backup details
- ✅ Restore from backup
- ✅ Delete backup

**How to use:**

**Create Backup:**
1. Click **Create Backup** button
2. Enter backup name
3. Click **OK**
4. Backup created successfully
5. Toast notification appears

**View Backup Details:**
1. Click backup card
2. Details show:
   - Type (Manual/Auto)
   - Size
   - Date created
   - Registry backup size

**Restore from Backup:**
1. Click **Restore** button on backup card
2. Confirmation dialog appears
3. Click **Yes** to confirm
4. Restore proceeds
5. Toast notification shows result

**Delete Backup:**
1. Click **Delete** button
2. Confirmation dialog appears
3. Click **Yes** to confirm
4. Backup deleted

### 8.3 Advanced Mode (Timeline)

**What it is:**
- Visual timeline of all tweaks
- Uses Flight Recorder for tracking
- Good for advanced users

**What you can do:**
- ✅ View tweak timeline
- ✅ Filter by type (manual, auto, profile_applied, restore)
- ✅ Click to view details
- ✅ Undo individual tweaks

**How to use:**

**Switch to Advanced Mode:**
1. Click mode toggle → **Advanced**
2. Simple mode hides
3. Timeline displays horizontally

**Timeline Visualization:**
- **Horizontal** - Chronological order
- **Colors** - Indicate status
  - 🟢 Green = SUCCESS
  - 🔴 Red = FAILED
- **Size** - Indicates complexity

**Filter Timeline:**
1. Select filter type
   - All
   - Manual
   - Auto (from profile)
   - Profile Applied
   - Restore
2. Timeline filters by type

**Click Timeline Item:**
1. Click item on timeline
2. Details panel shows:
   - Tweak name
   - Category
   - Risk level
   - Status
   - Timestamp
   - Undo command (if available)

**Undo Tweak:**
1. Click timeline item
2. Click **Undo** button
3. Confirmation dialog
4. Tweak reverted successfully

### 8.4 Automatic Backups

**When auto backup happens:**
- ✅ Before applying profile
- ✅ Before running script
- ✅ Manual backup per schedule (if set)

**Backup types:**
1. **System Restore Point** - Windows restore point
2. **Registry Backup** - Export registry as .reg file
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

**Should:**
- ✅ Create backup before major changes
- ✅ Delete some old backups (save space)
- ✅ Name backups meaningfully
- ✅ Test restore regularly

**Shouldn't:**
- ❌ Delete all backups
- ❌ Ignore backup warnings
- ❌ Restore without understanding consequences

---

## 9. Help & Documentation

### 9.1 Help Tab

**What it is:**
- Bilingual knowledge base (TH/EN)
- Frequently asked questions
- Myth-busting section

**Categories:**
1. **Getting Started** - For beginners
2. **Profiles** - Explains each profile
3. **Backups** - Backup management
4. **Troubleshooting** - Problem solving
5. **Myth-Busting** - Truth vs fiction

### 9.2 Using Help

**Search:**
1. Type search term in search box
2. Results filter by query
3. Click to view content

**Browse Categories:**
1. Click category card
2. Content shows in detail panel
3. Click topics to expand

### 9.3 Myth-Busting Section

**Why Myth-Busting?**
Because there's lots of misinformation about optimization

**Myths Debunked:**
1. ❌ "Windows reserves 20% bandwidth" → ✅ False
2. ❌ "Timer resolution boosts FPS" → ✅ Old (worked only on Win7)
3. ❌ "Disable 100 services = faster" → ✅ Dangerous

**In Help Tab:**
- 📕 Red = Myth (false)
- 📗 Green = Fact (true)

---

## 10. Settings

### 10.1 Settings Tab

**What it is:**
- Manage application settings
- Language, theme, accent colors

### 10.2 Language

**Options:**
- 🇬🇧 **English** - English language
- 🇹🇭 **Thai** - Thai language

**Changing:**
1. Select language in Settings
2. All views change immediately
3. Restart not required

**What changes:**
- UI labels
- Help content
- Button text
- Error messages

### 10.3 Theme

**Options:**
- 🌙 **Dark** - Dark theme (default)
- ☀️ **Light** - Light theme

**Changing:**
1. Select theme in Settings
2. All views change immediately

**What changes:**
- Background colors
- Text colors
- Card colors
- Border colors

### 10.4 Accent Colors

**Options:**
- 🔵 **Blue** - Blue (default)
- 🟣 **Purple** - Purple
- 🔷 **Cyan** - Cyan
- 🟢 **Green** - Green
- 🩷 **Pink** - Pink

**Changing:**
1. Select color in Settings
2. Applies across entire app immediately

**What changes:**
- Active navigation highlighting
- Button primary colors
- Progress bars
- Status indicators

---

## 11. Troubleshooting

### 11.1 Common Problems

**Problem 1: Application Won't Open**

**Symptoms:**
- Double-click and nothing happens
- Error message: "Access Denied"

**Solution:**
1. Close application
2. Right-click Command Prompt
3. Select "Run as administrator"
4. Navigate and run again

---

**Problem 2: Icons Display as Squares**

**Symptoms:**
- Icons don't display
- Show as empty squares

**Solution:**
1. Download Material Symbols font
2. Install font
3. Restart ClutchG
4. If still failing → ClutchG will fallback to Segoe MDL2 Assets

---

**Problem 3: Apply Profile Failed**

**Symptoms:**
- Execution dialog shows FAILED
- Toast error notification

**Possible Causes:**
1. **No admin rights** → Run as admin
2. **Registry access denied** → Check Windows permissions
3. **Disk full** → Delete old files
4. **Antivirus blocking** → Configure antivirus to allow

**Solution:**
1. Check error message in execution dialog
2. Fix per cause
3. Try applying again

---

**Problem 4: Restore Failed**

**Symptoms:**
- Restore failed
- Error message: "Cannot import registry"

**Solution:**
1. Check backup file still exists
2. Check disk space
3. Try manual restore:
   ```bash
   reg import "path\to\backup.reg"
   ```
4. Use System Restore if registry restore fails

---

**Problem 5: Performance Score Not Updating**

**Symptoms:**
- Upgraded hardware but score unchanged

**Solution:**
1. Click **Refresh** button
2. System detector will rescan
3. Score should update

---

**Problem 6: Timeline Not Showing**

**Symptoms:**
- Advanced mode empty
- Timeline has no items

**Solution:**
1. Check if you've applied tweaks before
2. If never → Normal (no history yet)
3. Apply profile or run script → Timeline starts recording

---

**Problem 7: Memory Leak**

**Symptoms:**
- Application slows over time
- Memory usage keeps increasing

**Solution:**
1. Restart ClutchG
2. Report issue with log files
3. Temporarily → Don't switch views more than 50 times per session

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

**Usage:**
- Attach log files when reporting bugs
- Check logs if you have issues

---

### 11.3 Reporting Bugs

**Template:**
```markdown
### Bug Report

**Environment:**
- Windows Version: [e.g., Windows 11 23H2]
- Python Version: [e.g., 3.11.5]
- ClutchG Version: [e.g., 1.0.0]

**Summary:**
[One sentence summary]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]

**Expected Behavior:**
[What you expect]

**Actual Behavior:**
[What actually happened]

**Attachments:**
- Screenshots
- Log files
```

---

## 12. FAQ (Frequently Asked Questions)

### 12.1 General Questions

**Q1: Is ClutchG safe?**
**A:** Yes, designed with safety as priority:
- All changes reversible
- Automatic backups
- Doesn't disable Windows Defender
- Doesn't disable security features

---

**Q2: Is ClutchG free?**
**A:** Yes, 100% free and open-source

---

**Q3: Can I use ClutchG on Windows 10?**
**A:** Yes, but must be Windows 10 22H2 (Build 19045) or later
- Windows 11 23H2+ recommended

---

**Q4: How much disk space do I need?**
**A:** At least 500 MB for backups
- Recommended 2 GB+ if keeping multiple backups

---

### 12.2 Usage Questions

**Q5: Which Profile should I choose?**
**A:**
- **Beginners** → SAFE
- **Gamers** → COMPETITIVE
- **Benchmarkers** → EXTREME

---

**Q6: Do I need to restart after applying Profile?**
**A:** Some tweaks require restart:
- Power plan changes
- Service changes
- Registry changes

Execution dialog will notify if restart is needed

---

**Q7: Can I apply multiple profiles?**
**A:** Not recommended
- Choose one profile and stick with it
- If want to change → restore first, then apply new profile

---

**Q8: What's the difference between Scripts and Profiles?**
**A:**
- **Profiles** = Multiple tweaks
- **Scripts** = Single or specific group of tweaks

Use scripts if you want detailed control

---

**Q9: Where are backups stored?**
**A:**
```
clutchg/data/backups/
```
- Registry backups (.reg files)
- Snapshots (.json)
- Timeline data (.json)

---

**Q10: Should I delete old backups?**
**A:** Yes, recommended
- Keep 5-10 most recent backups
- Delete older ones to save space
- But never delete all of them

---

### 12.3 Performance Questions

**Q11: How much FPS gain will I get?**
**A:** Depends on profile:
- **SAFE** → +2-5%
- **COMPETITIVE** → +5-10%
- **EXTREME** → +10-15%

Not guaranteed, depends on hardware/game

---

**Q12: How much ping reduction?**
**A:**
- **COMPETITIVE** → -5-15ms (average)
- **EXTREME** → -10-20ms (average)

Depends on network/ISP

---

**Q13: Will ClutchG make boot slower?**
**A:** No
- Enable/disable services not affecting boot time
- May actually boot slightly faster (disabling bloatware)

---

### 12.4 Safety Questions

**Q14: What if I have problems after applying profile?**
**A:**
1. Go to Backup & Restore Center
2. Restore from latest backup
3. PC returns to previous state

---

**Q15: What if restore fails?**
**A:**
1. Use Windows System Restore
2. Manual import registry backup
3. Reinstall ClutchG and restore again

---

**Q16: Does ClutchG send data anywhere?**
**A:** No
- 100% offline
- No telemetry
- No internet connection required

---

## 13. Additional Resources

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
- Architecture based on research of 28 Windows optimization repositories
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

## 📞 Contact

If you find bugs or have questions:

1. **Check:** Read troubleshooting section first
2. **Search:** Use Help tab
3. **Report:** Create issue with log files

---

**This document is part of ClutchG Project**
**Version:** 1.0 | **Last Updated:** 6 February 2026
**Language:** English

---

## 🎓 Quick Reference

**Hotkeys (if available):**
- `Ctrl+B` - Create backup
- `Ctrl+T` - View timeline
- `Ctrl+S` - Open settings

**Bash Commands:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run app (as admin)
cd clutchg\src
python app_minimal.py
```

**Batch Commands:**
```batch
# Manual registry restore
reg import "clutchg\data\backups\backup.reg"

# Create system restore point
powershell -Command "Checkpoint-Computer -Description 'Before ClutchG' -RestorePointType 'MODIFY_SETTINGS'"
```

---

**End of Document**

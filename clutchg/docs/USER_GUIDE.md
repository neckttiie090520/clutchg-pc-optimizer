# ClutchG User Guide

## 📋 Overview

**ClutchG** is a modern Windows PC optimizer with a user-friendly interface. It provides easy access to performance optimization scripts through three preset profiles.

---

## 🚀 Getting Started

### Requirements
- Windows 10/11 (64-bit)
- Administrator privileges
- 100MB disk space

### Installation
1. Download `ClutchG.exe`
2. Right-click → **Run as Administrator**
3. The app will request admin privileges if needed

---

## 🎯 Optimization Profiles

### 🛡️ SAFE Mode
**Best for:** Beginners, laptops, work PCs

- Power plan optimization
- Telemetry disabling
- No restart required
- **Risk:** Low | **FPS Gain:** +2-5%

### ⚔️ COMPETITIVE Mode
**Best for:** Gamers, desktop PCs

Includes all SAFE optimizations plus:
- Service optimization
- Network tuning
- BCDEdit safe tweaks
- **Risk:** Medium | **FPS Gain:** +5-10%

### 🔥 EXTREME Mode
**Best for:** Enthusiasts, high-end PCs

Includes all optimizations:
- Aggressive service disabling
- Maximum performance settings
- Full BCDEdit optimization
- **Risk:** High | **FPS Gain:** +10-15%

> ⚠️ **Warning:** EXTREME mode may cause instability on some systems. Always create a backup first!

---

## 💾 Backup & Restore

### Creating a Backup
1. Go to **Backup** view
2. Click **Create Backup**
3. Enter a name (e.g., "Pre-Competitive")
4. Select options:
   - ✅ Create Windows Restore Point
   - ✅ Backup Registry Keys
5. Click **Create Backup**

### Restoring from Backup
1. Go to **Backup** view
2. Find your backup in the list
3. Click **Restore**
4. Confirm the action
5. Restart your computer

---

## 📜 Scripts Browser

View and run individual optimization scripts:

1. Go to **Scripts** view
2. Use filters:
   - **Category:** power, services, network, etc.
   - **Search:** type to filter by name
3. Click **Run** on any script
4. Monitor execution in real-time

---

## ⚙️ Settings

### Language
- **Language:** English / Thai (ไทย)

### Safety Options
- **Auto-backup:** Create backup before applying profiles
- **Confirm actions:** Show confirmation dialogs
- **Max backups:** Number of backups to keep

### Paths
- **Batch Scripts:** Location of .bat files
- **Backup Directory:** Where backups are stored

---

## ❓ Troubleshooting

### "Not running as administrator"
**Solution:** Right-click ClutchG.exe → Run as Administrator

### System detection shows "Unknown"
**Solution:** Ensure psutil and wmi packages are installed

### Profile application fails
**Solution:** 
1. Check if batch scripts exist in the scripts directory
2. Review the console output for errors
3. Restore from backup if needed

### High risk warning
**Solution:** Use SAFE mode for your first optimization

---

## 🔄 How to Rollback

If something goes wrong:

1. **Use Windows System Restore:**
   - Press Win+R → type `rstrui.exe` → Enter
   - Select a restore point created by ClutchG
   - Follow the wizard

2. **Use ClutchG Backup:**
   - Open ClutchG
   - Go to Backup view
   - Click Restore on your backup
   - Restart computer

---

## 📊 System Tiers

ClutchG automatically detects your system tier:

| Tier | Score | Description |
|------|-------|-------------|
| Entry | 0-29 | Basic PC, use SAFE only |
| Mid | 30-49 | Standard PC, SAFE or COMPETITIVE |
| High | 50-69 | Gaming PC, COMPETITIVE recommended |
| Enthusiast | 70+ | High-end PC, any profile |

---

## 📝 Tips

1. **Start with SAFE mode** - Test your system first
2. **Always create backups** - Enable auto-backup in settings
3. **Restart after COMPETITIVE/EXTREME** - Changes require restart
4. **Check scripts before running** - Review in Scripts view
5. **Keep backups** - Don't delete all backups at once

---

## 🆘 Support

For issues or feedback, check the project repository.

---

**ClutchG v1.0.0**  
*Windows PC Optimizer*

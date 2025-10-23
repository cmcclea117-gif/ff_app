# 🏈 Fantasy Football Dashboard V3.3 - Quick Start

## ⚡ 5-Minute Setup

### 1️⃣ Download Everything
Get these files from Claude:
- ✅ `generate_dashboard.py` - The generator script
- ✅ `generate.sh` - Mac/Linux helper (optional)
- ✅ `generate.bat` - Windows helper (optional)
- ✅ `README.md` - Full documentation (optional)

### 2️⃣ Create Folder Structure
```
your_folder/
├── generate_dashboard.py
├── generate.sh (Mac/Linux)
├── generate.bat (Windows)
└── historical_data/
    └── (your 9 CSV files go here)
```

**Quick command:**
```bash
mkdir historical_data
```

### 3️⃣ Add Your CSV Files
Copy these 9 files into `historical_data/`:

**PPR Files:**
- `2022_FantasyPros_Fantasy_Football_Points_PPR.csv`
- `2023_FantasyPros_Fantasy_Football_Points_PPR.csv`
- `2024_FantasyPros_Fantasy_Football_Points_PPR.csv`

**Half-PPR Files:**
- `2022_FantasyPros_Fantasy_Football_Points_HALF.csv`
- `2023_FantasyPros_Fantasy_Football_Points_HALF.csv`
- `2024_FantasyPros_Fantasy_Football_Points_HALF.csv`

**Standard Files:**
- `2022_FantasyPros_Fantasy_Football_Points.csv`
- `2023_FantasyPros_Fantasy_Football_Points.csv`
- `2024_FantasyPros_Fantasy_Football_Points.csv`

### 4️⃣ Run the Generator

**Option A - Simple (Mac/Linux):**
```bash
chmod +x generate.sh
./generate.sh
```

**Option B - Simple (Windows):**
```
Double-click generate.bat
```

**Option C - Manual:**
```bash
python3 generate_dashboard.py
```

### 5️⃣ Open Your Dashboard
Double-click `fantasy_dashboard_v33.html` and you're done! 🎉

---

## 📋 Weekly Usage

Every week, you'll need:

1. **Updated 2025 results CSV** (download from FantasyPros after games)
2. **Next week's projections CSV** (download Wednesday/Thursday)

Then just:
1. Open your dashboard HTML file
2. Upload the 2 new CSVs
3. Dashboard auto-updates!

---

## 🔄 Next Season Update (2026)

**Step 1:** Edit `generate_dashboard.py` line 27:
```python
HISTORICAL_FILES = {
    'PPR': {
        2023: '2023_FantasyPros_Fantasy_Football_Points_PPR.csv',  # New: Remove 2022
        2024: '2024_FantasyPros_Fantasy_Football_Points_PPR.csv',
        2025: '2025_FantasyPros_Fantasy_Football_Points_PPR.csv',  # New: Add 2025
    },
    # ... update HALF_PPR and STANDARD the same way
}
```

**Step 2:** Add your 2025 CSV files to `historical_data/` folder

**Step 3:** Run generator again:
```bash
python3 generate_dashboard.py
```

**Done!** New HTML now has 2023-2025 data embedded. 🚀

---

## ❓ Common Issues

### "Python not found"
**Solution:** Install Python from [python.org](https://www.python.org/)
- Check "Add Python to PATH" during install (Windows)
- Need Python 3.7 or newer

### "No CSV files found"
**Solution:** Make sure files are in `historical_data/` folder with EXACT names
```bash
ls historical_data/  # Mac/Linux
dir historical_data\  # Windows
```

### "File won't open in browser"
**Solution:** 
- Make sure `.html` extension is visible
- Right-click → Open With → Chrome/Firefox/Safari
- Some email/messaging apps may block HTML files - use file explorer instead

---

## 🎯 What You Get

✅ **Self-contained** - Single 1.5MB HTML file  
✅ **Portable** - Works offline, no server needed  
✅ **Multi-format** - PPR, Half-PPR, Standard  
✅ **Smart projections** - Learns from FantasyPros accuracy  
✅ **Easy updates** - Just re-run Python script next season  
✅ **Hostable** - GitHub Pages, Netlify, Vercel  

---

## 💡 Pro Tips

### Backup Your Files
```bash
# Create a backup folder
mkdir backups
cp historical_data/*.csv backups/
```

### Use Git for Version Control
```bash
git init
git add .
git commit -m "Initial fantasy dashboard"
```

### Share with Your League
1. Generate the HTML
2. Upload to GitHub Pages or Netlify
3. Share the URL with your league
4. Everyone uses the same projections!

---

## 🚀 Cloud Hosting (30 seconds)

### GitHub Pages (FREE forever)
```bash
# In your folder
git init
git add fantasy_dashboard_v33.html
git commit -m "Add dashboard"
gh repo create fantasy-dashboard --public --source=. --push
# Enable Pages in repo settings
# URL: https://yourusername.github.io/fantasy-dashboard/fantasy_dashboard_v33.html
```

### Netlify Drop (No account needed)
1. Go to: https://app.netlify.com/drop
2. Drag `fantasy_dashboard_v33.html` onto the page
3. Get instant URL: `https://random-name.netlify.app/`

---

## 📞 Help

**If something's not working:**
1. Check you have Python 3.7+ installed
2. Verify all 9 CSV files are in `historical_data/`
3. Check filenames match exactly (case-sensitive)
4. Read any error messages from the Python script

**Still stuck?** The full README.md has detailed troubleshooting.

---

## 🎉 You're Ready!

```
✅ Python installed
✅ Folder structure created  
✅ CSV files added
✅ Generator script run
✅ HTML file generated
✅ Dashboard opened in browser

🏆 Now go win your league!
```

---

**Need the full documentation?** See `README.md`

**Want to customize?** The Python script is fully commented and easy to modify!

**Have fun! 🏈📊🚀**
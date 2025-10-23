# Git Setup & Initial Commit Instructions

## 🎯 Goal
Connect your local `ff_app` project folder to GitHub repo: https://github.com/cmcclea117-gif/ff_app

---

## 📋 Prerequisites

1. **Git installed** - Check with: `git --version`
   - If not installed: https://git-scm.com/downloads

2. **GitHub account authenticated**
   - Either SSH keys set up OR
   - Personal access token ready

---

## 🚀 Step-by-Step Commands

### Step 1: Navigate to Your Project Folder
```bash
cd c:\Users\chrismccleary\Documents\ff_app
```

---

### Step 2: Initialize Git Repository (if not already done)
```bash
git init
```

**Note**: If the folder already has a `.git` directory, skip this step.

---

### Step 3: Add the Remote Repository
```bash
git remote add origin https://github.com/cmcclea117-gif/ff_app.git
```

**Verify it worked:**
```bash
git remote -v
```

**Should show:**
```
origin  https://github.com/cmcclea117-gif/ff_app.git (fetch)
origin  https://github.com/cmcclea117-gif/ff_app.git (push)
```

---

### Step 4: Create .gitignore File
Create a file called `.gitignore` in your project root with this content:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
desktop.ini

# Project specific
*.html.backup
*_old.*
*_backup.*
temp/
tmp/

# Keep the generated HTML
# (Comment out if you DON'T want to commit it)
# fantasy_dashboard_v34_complete.html
```

**Create the file:**
```bash
# Windows (PowerShell)
New-Item -Path .gitignore -ItemType File

# Or use notepad
notepad .gitignore
```

Then paste the content above and save.

---

### Step 5: Add All Files to Staging
```bash
git add .
```

**Check what will be committed:**
```bash
git status
```

**Should show:**
```
On branch main
Changes to be committed:
  new file:   generate_dashboard_fixed.py
  new file:   historical_data/...
  new file:   HANDOFF.md
  new file:   QUICK_START.md
  ... etc
```

---

### Step 6: Create Initial Commit
```bash
git commit -m "Initial commit: Fantasy Football Dashboard v3.4

- Complete ECR-based projection system
- Position-specific reliability tracking
- Sleeper API integration
- Historical analysis (2022-2024)
- Week-by-week accuracy calculations
- Fixed display bugs and projection algorithm
- Comprehensive documentation included"
```

---

### Step 7: Set Default Branch Name
```bash
git branch -M main
```

**Note**: GitHub uses `main` as default (not `master`).

---

### Step 8: Push to GitHub
```bash
git push -u origin main
```

**If this is your first push, you might need authentication:**

#### Option A: Personal Access Token (Recommended)
If prompted for username/password:
- **Username**: Your GitHub username
- **Password**: Use a Personal Access Token (NOT your GitHub password)

**Create a token**: 
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Generate and copy the token
5. Use it as your password

#### Option B: SSH (Alternative)
If you prefer SSH:
```bash
# Change remote to SSH
git remote set-url origin git@github.com:cmcclea117-gif/ff_app.git

# Then push
git push -u origin main
```

---

## ✅ Verification

After pushing, visit your repo:
https://github.com/cmcclea117-gif/ff_app

You should see:
- ✅ All your files
- ✅ The commit message
- ✅ README.md (create one if you want - see below)

---

## 📝 Optional: Create a README

Create `README.md` in your project root:

```markdown
# Fantasy Football Dashboard v3.4

Advanced fantasy football analytics dashboard with expert consensus rankings (ECR) integration, position-specific reliability tracking, and intelligent projections.

## Features

- **ECR-Based Projections**: Converts FantasyPros expert consensus rankings to point projections
- **Reliability Tracking**: Measures how accurate ECR has been for each player and position
- **Position-Specific Analysis**: Different reliability metrics for QB/RB/WR/TE
- **Sleeper Integration**: Connect to your Sleeper league and roster
- **Historical Analysis**: 3 years of historical data (2022-2024)
- **Intelligent Algorithm**: Blends ECR with player averages based on reliability
- **7 Functional Tabs**: Projections, Reliability, Rankings, Waiver Targets, Lineup Optimizer, Matchups, Historical

## Quick Start

```bash
# Generate the dashboard
python generate_dashboard_fixed.py

# Open the generated HTML
fantasy_dashboard_v34_complete.html
```

## Documentation

- **[HANDOFF.md](HANDOFF.md)** - Complete project context and handoff instructions
- **[QUICK_START.md](QUICK_START.md)** - Quick reference guide
- **[FIXES_SUMMARY.md](FIXES_SUMMARY.md)** - Detailed explanation of all fixes
- **[CODE_CHANGES.md](CODE_CHANGES.md)** - Before/after code comparisons

## Requirements

- Python 3.x
- CSV files from FantasyPros:
  - Weekly ECR rankings
  - Season results
  - Historical data (2022-2024)

## Data Sources

Place your CSV files in `historical_data/` folder:
- `FantasyPros_2025_Week_X_OP_Rankings.csv` - Weekly ECR
- `FantasyPros_Fantasy_Football_Points_PPR.csv` - 2025 results
- Historical files for 2022-2024 (PPR, Half-PPR, Standard)

## Key Metrics

- **FP Acc**: Percentage of weeks projected rank within 3 ranks of actual (stricter = better)
- **MAE**: Mean absolute error in ranks (lower = better)
- **Correlation**: How well ranks predict scores (-1 to 1, higher = better)
- **Avg Diff**: Average rank difference (negative = finishes better than projected)

## Latest Improvements

- Fixed display bug showing correlation instead of accuracy
- Changed accuracy threshold from 5 ranks to 3 ranks (stricter)
- Disabled over-aggressive bias adjustment
- Improved handling of negative correlation
- Increased minimum games from 3 to 5 for player-specific patterns

## Author

Built with ❤️ for fantasy football domination 🏈
```

**Add and commit the README:**
```bash
git add README.md
git commit -m "Add comprehensive README"
git push
```

---

## 🔄 Future Commits

After the initial setup, making changes is easy:

```bash
# After editing files
git add .
git commit -m "Description of what you changed"
git push
```

**Or for specific files:**
```bash
git add generate_dashboard_fixed.py
git commit -m "Fix: Improved projection algorithm for negative correlation"
git push
```

---

## 🆘 Troubleshooting

### Issue: "fatal: remote origin already exists"
```bash
# Remove existing remote
git remote remove origin

# Add it again
git remote add origin https://github.com/cmcclea117-gif/ff_app.git
```

### Issue: "Updates were rejected"
```bash
# Pull first, then push
git pull origin main --rebase
git push -u origin main
```

### Issue: "Authentication failed"
- Make sure you're using a Personal Access Token, not your password
- Generate one at: https://github.com/settings/tokens

### Issue: "Can't find git command"
- Install Git: https://git-scm.com/downloads
- Restart your terminal after installing

---

## 📊 Git Best Practices

### Good Commit Messages:
✅ "Fix: Corrected projection algorithm for Ladd McConkey"  
✅ "Add: New reliability tracking for positions"  
✅ "Update: HANDOFF.md with latest session changes"  

❌ "updated stuff"  
❌ "fixes"  
❌ "asdfasdf"

### Commit Often:
- After each feature/fix
- Before making major changes
- At the end of each work session

### Use Branches (Optional):
```bash
# Create a feature branch
git checkout -b feature/new-tier-system

# Work on your feature...
git add .
git commit -m "Add new tier calculation system"

# Push branch
git push -u origin feature/new-tier-system

# Merge to main later via GitHub PR
```

---

## 🎯 Quick Reference Card

```bash
# Status
git status

# Add files
git add .
git add filename.py

# Commit
git commit -m "Your message"

# Push
git push

# Pull latest
git pull

# View history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename.py
```

---

## ✅ Checklist

Before pushing:
- [ ] Reviewed changes with `git status`
- [ ] No sensitive data (passwords, API keys)
- [ ] .gitignore is set up
- [ ] Commit message is descriptive
- [ ] Code is tested and working

---

You're all set! Happy coding and may your fantasy team dominate! 🏈🎯

# 🔧 ECR Dashboard Troubleshooting Guide

## 📊 Current Issues You're Seeing

Based on your screenshots:

### 1. ❌ "With FP Data" = 0
**Cause:** JavaScript is checking for `.proj` field, but Python stores `.ecr` field

### 2. ❌ "High Accuracy" = 0  
**Cause:** Same issue - no ECR matches found, so no accuracy calculated

### 3. ❌ Reliability Tab Empty
**Cause:** FP_ACCURACY object is empty (no matches found)

### 4. ❌ Projections = Season Averages  
**Cause:** ECR conversion isn't working, falling back to `avgScore`

### 5. ⚠️ Available Players Filter Issue
**Cause:** Player name normalization differences between your data and Sleeper

---

## 🎯 The Root Cause

**Your Python generator stores:**
```python
projections.append({
    'p': player,
    'pos': pos,
    'ecr': ecr,      # ✅ This is correct
    'std': std_dev   # ✅ This is correct
})
```

**But your JavaScript checks for:**
```javascript
if (proj && proj.proj > 0) {  // ❌ Looking for .proj
    // This will NEVER match!
}
```

**Should be:**
```javascript
if (proj && proj.ecr > 0) {  // ✅ Looking for .ecr
    // This will match!
}
```

---

## 🚀 THE FIX - Use the Patcher

### Step 1: Run the ECR Patcher
```bash
python3 patch_ecr_fix.py fantasy_dashboard_v34_complete.html
```

This creates: `fantasy_dashboard_v34_complete_ecr_fixed.html`

### Step 2: Open the Fixed Dashboard
```bash
# On Mac/Linux:
open fantasy_dashboard_v34_complete_ecr_fixed.html

# Or just double-click the file
```

### Step 3: Check the Console (F12)
You should now see:
```
Sample ECR entry: {p: "Bijan Robinson", pos: "RB", ecr: 2, std: 0.8}
Checking 556 players against 8 weeks of ECR data
FP Accuracy calculated for X players  // X should be > 0 now!
Generated 556 projections, Y with ECR data  // Y should be > 0 now!
```

---

## ✅ Expected Results After Fix

### Metrics Cards:
```
Total Players: 556
With FP Data: 200+  ✅ (was 0)
High Accuracy: 50+  ✅ (was 0)
My Roster: 14
Available: 342
```

### Projections Tab:
```
Player              Pos  Rank  Week 8 Proj  Floor-Ceiling    Tier
────────────────────────────────────────────────────────────────
Patrick Mahomes II  QB    1      22.7       21.8 - 23.5    [Elite]
Josh Allen          QB    2      22.5       21.8 - 23.2    [Elite]
Bijan Robinson      RB    1      22.2       21.8 - 22.6    [Elite]
```

**NOT:**
```
Puka Nacua          WR    1      23.1       16.2 - 30.1    [Elite]  ❌
```

### Reliability Tab:
Should show players with correlation, MAE, etc.

---

## 🐛 If It Still Doesn't Work

### Debug Step 1: Check Console Messages

Open F12 Console and look for:

**Good Messages:**
```
✅ "Sample ECR entry: {p: '...', pos: '...', ecr: 2, std: 0.8}"
✅ "FP Accuracy calculated for 100+ players"
```

**Bad Messages:**
```
❌ "Sample ECR entry: {p: '...', pos: '...', proj: 326, best: 326, worst: 326}"
❌ "FP Accuracy calculated for 0 players"
```

If you still see `.proj` in the sample entry, the patch didn't apply correctly.

---

### Debug Step 2: Manual Check

1. Open `fantasy_dashboard_v34_complete_ecr_fixed.html` in a text editor
2. Search for: `if (proj && proj.proj > 0)`
3. If found → Patch failed, replace manually with `if (proj && proj.ecr > 0)`
4. Search for: `if (ecrData && ecrData.proj > 0)`
5. If found → Replace with `if (ecrData && ecrData.ecr > 0)`

---

### Debug Step 3: Player Name Matching

If "With FP Data" is still low (like 10-20 instead of 200+):

**The Issue:** Player names don't match between your CSVs.

**Check:**
```javascript
// In console, run:
WEEKLY_PROJECTIONS[8][0].p  // ECR player name
SEASON_2025.data[0].p       // 2025 results player name
```

**Common Mismatches:**
- ECR: "Patrick Mahomes II" vs Results: "Patrick Mahomes"
- ECR: "D.J. Moore" vs Results: "DJ Moore"
- ECR: "AJ Brown" vs Results: "A.J. Brown"

**Solution:** Improve name normalization:
```javascript
function normalizePlayerName(name) {
  return name.toLowerCase()
    .replace(/\s+(jr|sr|ii|iii|iv|v)\.?$/i, '')
    .replace(/\./g, '')  // Remove periods
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}
```

---

## 🎯 Why Projections Were Matching Season Averages

When ECR data isn't found, the code does this:
```javascript
let proj = avgScore;  // Default to season average

if (ecrData && ecrData.ecr > 0) {
  // Convert ECR to projection
  proj = baselines[pos][ecrData.ecr - 1];
} else {
  // No ECR found, proj stays as avgScore
}
```

Since `.ecr` wasn't being found (because code checked `.proj`), every player fell back to `avgScore`. That's why:
- Puka Nacua: proj = 23.1 = his season average
- Patrick Mahomes: proj = his season average
- Etc.

After the fix, ECR #1 QB (Patrick Mahomes) should get ~22-23 points from the QB1 historical baseline, not his exact season average.

---

## 🔄 Available Players Filter Issue

For the Sleeper roster filter, the issue is similar - name matching.

**Current Implementation:**
```javascript
function isRostered(playerName) {
  if (!SLEEPER_DATA) return false;
  
  const norm = normalizePlayerName(playerName);
  const players = SLEEPER_DATA.players;
  
  for (const [pid, player] of Object.entries(players)) {
    if (player.full_name && normalizePlayerName(player.full_name) === norm) {
      return ALL_ROSTERED.has(pid);
    }
  }
  
  return false;
}
```

**The Problem:** 
If Sleeper has "A.J. Brown" but your CSV has "AJ Brown", the normalization might not match.

**Enhanced Solution:**
```javascript
function normalizePlayerName(name) {
  return name.toLowerCase()
    .replace(/\s+(jr|sr|ii|iii|iv|v)\.?$/i, '')
    .replace(/\./g, '')        // Remove ALL periods
    .replace(/-/g, '')         // Remove hyphens
    .replace(/'/g, '')         // Remove apostrophes
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, '')       // Remove ALL spaces for tight matching
    .trim();
}
```

This makes:
- "A.J. Brown" → "ajbrown"
- "AJ Brown" → "ajbrown"
- "D.J. Moore" → "djmoore"
- "DJ Moore" → "djmoore"

---

## 📋 Quick Reference: What Each Fix Does

| Fix | What It Does | Impact |
|-----|--------------|--------|
| `.proj` → `.ecr` | Checks correct field in ECR data | Enables ECR matching |
| Add console.log | Shows what's happening | Helps debugging |
| Fix avgScore calc | Gets score from 2025 data | Fixes Reliability tab |
| Empty state check | Shows message if no data | Better UX |
| Enhanced normalization | Better name matching | More ECR matches |

---

## ✅ Success Checklist

After running the patcher and opening the fixed dashboard:

- [ ] "With FP Data" > 100
- [ ] "High Accuracy" > 20
- [ ] Reliability tab has data
- [ ] Projections differ from season averages
- [ ] Patrick Mahomes shows ~22-23 points (not his exact season avg)
- [ ] Console shows "Sample ECR entry" with `.ecr` field
- [ ] Console shows "FP Accuracy calculated for X players" (X > 0)

---

## 🆘 If Still Stuck

1. **Run the patcher:**
   ```bash
   python3 patch_ecr_fix.py fantasy_dashboard_v34_complete.html
   ```

2. **Open the fixed file**

3. **Check console (F12)**

4. **Take a screenshot of:**
   - The dashboard (all metrics cards)
   - The console output
   - Projections tab (first 10 rows)

5. **Send me:**
   - The screenshots
   - The console output (copy/paste text)
   - First 3 lines of your Week 8 ECR CSV

And I'll help diagnose exactly what's happening!

---

## 💡 Understanding the System

Once fixed, here's how it works:

1. **Python loads ECR:** "Patrick Mahomes ranked #2 overall (QB1)"
2. **JavaScript gets ECR:** `{p: "Patrick Mahomes II", pos: "QB", ecr: 2, std: 1.7}`
3. **Look up QB1 baseline:** Historical QB1 = 22.5 PPG
4. **Apply adjustments:** If correlation > 70%, blend with season avg
5. **Calculate range:** Use std dev for floor/ceiling
6. **Result:** Projection = ~22-23 points ✅

Not: Projection = 22.7 (exact season average) ❌

---

Good luck! The patcher should fix everything! 🚀

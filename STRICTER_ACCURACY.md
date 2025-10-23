# Accuracy Threshold Update - Within 3 Ranks

## 🎯 Changes Made

Changed accuracy calculation from **"within 5 ranks"** to **"within 3 ranks"** for stricter, more meaningful evaluation.

---

## 📊 Impact

### Ray-Ray McCloud III Example:
- Rank differences: [26, 5, 20]
- **Old (within 5)**: 33% accurate (1 out of 3 weeks)
- **New (within 3)**: 0% accurate (0 out of 3 weeks)

### Example Good Player:
- Rank differences: [2, 4, 1]
- **Old (within 5)**: 100% accurate
- **New (within 3)**: 67% accurate

---

## ✅ What Changed in Code

### 1. Changed threshold (Line ~999):
```javascript
// BEFORE:
const within5 = rankDiffs.filter(d => d <= 5).length / rankDiffs.length;

// AFTER:
const within3 = rankDiffs.filter(d => d <= 3).length / rankDiffs.length;
```

### 2. Updated variable names throughout:
- `within5` → `within3`
- `avgWithin5` → `avgWithin3`

### 3. Updated column header (Line 748):
```javascript
// BEFORE:
<th>Within 3pts %</th>

// AFTER:
<th>Within 3 Ranks %</th>
```

---

## 🎓 Why This Is Better

### More Meaningful Evaluation:
- **Within 5 ranks**: Too lenient
  - QB5 vs QB10 = pass ✅
  - That's a huge difference in fantasy!
  
- **Within 3 ranks**: More realistic
  - QB5 vs QB8 = pass ✅
  - QB5 vs QB10 = fail ❌

### Better Reflects Fantasy Impact:
- Being off by 4-5 ranks can mean the difference between:
  - Starting a player vs benching them
  - Hitting value vs missing value
  - Winning vs losing your week

### More Honest Accuracy Scores:
- Most players will now show **0-50% accuracy** (realistic!)
- Instead of **30-80% accuracy** (inflated)
- Helps identify truly predictable players

---

## 📈 Expected Results

### Projections Tab - FP Acc Column:
You'll see **much lower** accuracy percentages:
- Elite predictable players: 50-70%
- Average: 20-40%
- Volatile players: 0-20%

### Reliability Tab:
- **FP Accuracy** (correlation): Still high (70-100%)
- **Within 3 Ranks %**: Now lower (0-60%)

This makes sense! Experts can identify **talent** (correlation), but struggle with **exact weekly performance** (accuracy).

---

## 🎯 Interpretation Guide

### For FP Acc % (Within 3 Ranks):

**70-100%**: 🟢 **Extremely Reliable**
- ECR is very accurate for this player
- High confidence in projections
- Safe to trust the ranking

**50-70%**: 🟡 **Moderately Reliable**
- ECR is decent but not perfect
- Good guideline, use other factors too
- Safe for start/sit decisions

**30-50%**: 🟠 **Somewhat Reliable**
- ECR has significant variance
- Use as one of many factors
- Consider matchups heavily

**0-30%**: 🔴 **Unreliable**
- ECR struggles with this player
- High volatility or unpredictable usage
- Trust your gut over rankings

---

## 🔄 All Changes Summary

1. ✅ **Fixed display bug**: Shows accuracy instead of correlation
2. ✅ **Added accuracy to projections**: Now available in Projections tab
3. ✅ **Stricter threshold**: Within 3 ranks (was 5)
4. ✅ **Fixed header**: "Within 3 Ranks %" (was "Within 3pts %")

---

## 🚀 Run It!

```bash
python generate_dashboard_fixed.py
```

Then check:
- **Projections tab**: FP Acc should show lower numbers (0-60% range)
- **Reliability tab**: Within 3 Ranks % should match
- Ray-Ray McCloud: Should show **0%** (not 100%!)

---

## 💡 Pro Tip

Sort the Projections table by **FP Acc** (click the header) to see:
- **Top**: Most predictable players (trust their projections!)
- **Bottom**: Most volatile players (use caution!)

This helps you make better start/sit decisions! 🏈

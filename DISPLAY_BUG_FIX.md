# Display Bug Fix - FP Acc Column

## 🐛 The Bug

**Problem**: The "FP Acc" column in the Projections tab was showing **correlation** instead of **accuracy**.

### What's the Difference?

- **Correlation** (0.999 = 99.9%): Measures if high ranks = high scores (linear relationship)
- **Accuracy** (0.33 = 33%): Measures % of weeks within 5 ranks of projected rank

### Example: Ray-Ray McCloud III
- **Correlation**: 0.999 (99.9%) - His ranks and scores move together perfectly
- **Actual Performance**:
  - Week 1: Projected WR78 → Actual WR52 (26 ranks better!)
  - Week 3: Projected WR86 → Actual WR81 (5 ranks better)
  - Week 4: Projected WR94 → Actual WR114 (20 ranks worse)
- **Accuracy**: 33% (only 1 out of 3 weeks within 5 ranks)

## Why High Correlation ≠ High Accuracy

Ray-Ray has perfect correlation because when his rank goes up, his score goes up proportionally. But the **absolute ranks** are way off!

Think of it like:
- **Correlation**: "The shape of the line is right"
- **Accuracy**: "The line is in the right place"

## ✅ The Fix

### Changed in `generate_dashboard_fixed.py`:

**Line 1227** - Projections Table:
```javascript
// BEFORE (WRONG):
<td>${{(p.correlation * 100).toFixed(0)}}%</td>

// AFTER (CORRECT):
<td>${{p.accuracy ? (p.accuracy * 100).toFixed(0) + '%' : '-'}}</td>
```

**Line 1126-1139** - Projections Object:
```javascript
// ADDED accuracy field:
projections.push({
  // ... other fields
  correlation: FP_ACCURACY[name]?.correlation || 0,
  mae: FP_ACCURACY[name]?.mae || 0,
  avgDiff: FP_ACCURACY[name]?.avgDiff || 0,
  accuracy: FP_ACCURACY[name]?.accuracy || 0  // ← ADDED THIS
});
```

## 📊 What You'll See Now

### Projections Tab - "FP Acc" Column:
- **Before**: 100%, 99%, 97%, 95%... (correlation)
- **After**: 33%, 67%, 100%, 0%... (actual accuracy)

Much more realistic numbers!

### Reliability Tab:
Already correct - shows BOTH:
- **FP Accuracy** column = correlation (how well ranks predict scores)
- **Within 3pts %** column = accuracy (% within 5 ranks)

Wait, that's confusing too! Let me check...

Actually looking at the Reliability table headers:
- Column 4: "FP Accuracy" = correlation ✅
- Column 5: "MAE" = Mean Absolute Error ✅
- Column 6: "Within 3pts %" = Should be "Within 5 Ranks %" ❌

## 🤔 Additional Issue Found

The column header says "Within 3pts %" but the code calculates "within 5 ranks". This is misleading!

### Should We Also Fix the Header?

**Option 1**: Change header to match code
```javascript
// Line ~746
<th>Within 5 Ranks %</th>  // More accurate
```

**Option 2**: Change threshold to match header
```javascript
// Line 999
const within3 = rankDiffs.filter(d => d <= 3).length / rankDiffs.length;
```

I recommend **Option 2** - changing to "within 3 ranks" would give more realistic/useful accuracy numbers:
- Within 5 ranks: Too lenient (Ray-Ray = 33%)
- Within 3 ranks: More meaningful (Ray-Ray = 33% still, but most would be lower)

## 📈 Expected Results After Fix

Run the updated generator and you should see:

### Projections Tab:
- Ray-Ray McCloud III: **33%** accuracy (was 100%)
- Ashton Dulin: **0%** accuracy (was 99%)
- More realistic spread of accuracy scores

### Reliability Tab:
- FP Accuracy (correlation) column: Still high numbers (70-100%)
- Within 3pts % (accuracy) column: Lower numbers (0-60%)
- This makes sense - experts can identify talent (correlation) but struggle with exact weekly ranks (accuracy)

## 🎯 Summary

**Fixed**: Projections table now shows true accuracy (% within 5 ranks), not correlation

**Still Shows Both**:
- Projections tab: Shows accuracy only
- Reliability tab: Shows BOTH correlation and accuracy for detailed analysis

**Remaining Question**: Should we change "within 5 ranks" to "within 3 ranks" for stricter evaluation?

---

## 🔄 Next Steps

1. **Run the fixed generator**:
```bash
python generate_dashboard_fixed.py
```

2. **Check the Projections tab**: 
   - FP Acc column should now show lower, more realistic numbers
   - Ray-Ray should be ~33%, not 100%

3. **Decide on threshold**:
   - If accuracy numbers seem too high, we can tighten to "within 3 ranks"
   - Current: within 5 ranks
   - Stricter: within 3 ranks

Let me know what you think of the accuracy percentages after this fix!

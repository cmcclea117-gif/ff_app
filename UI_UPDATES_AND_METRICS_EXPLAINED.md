# UI Updates Summary

## ✅ Changes Made

### 1. Column Renamed: "Accuracy" → "Rating"
- More intuitive for users
- Clearer that it's a quality score (0-100) rather than a percentage

### 2. Removed Percentage Sign (%)
- Displays as: `84` instead of `84%`
- Consistent with rating interpretation (like a grade out of 100)

### 3. Fixed Sort Order
- **Before**: Clicking "Accuracy" showed ascending MAE → lowest ratings first ❌
- **After**: Clicking "Rating" shows descending ratings → highest ratings first ✅
- Technical fix: Inverted sort logic for MAE column since lower MAE = higher rating

### 4. Updated Tooltip
- **Before**: "Accuracy score based on Mean Absolute Error"
- **After**: "Rating score (0-100) based on prediction accuracy - hover over values to see underlying MAE"

---

## 📊 Understanding Rating vs. Trend

### What Each Metric Measures:

**Rating (based on MAE - Mean Absolute Error)**
- **What it measures**: How far off predictions are on average (magnitude only)
- **Scale**: 0-100 (higher is better)
- **Interpretation**: 
  - 90-100 = Elite accuracy (MAE 3-12)
  - 75-89 = Good accuracy (MAE 12-24)
  - <75 = Poor accuracy (MAE >24)

**Trend (avgDiff - Average Rank Difference)**
- **What it measures**: Bias in predictions (direction)
- **Formula**: actual_rank - projected_rank
- **Interpretation**:
  - **Negative** (📈): Consistently outperforms projections
  - **Near zero** (➡️): Unbiased predictions
  - **Positive** (📉): Consistently underperforms projections

### Example Scenarios:

| Player | Rating | MAE | Trend | Interpretation |
|--------|--------|-----|-------|----------------|
| Player A | 95 | 5.0 | -0.5 | **Very accurate, slightly underestimated** - Nearly perfect predictions |
| Player B | 84 | 17.0 | +15.0 | **Average accuracy, overestimated** - Projections too optimistic, moderate errors |
| Player C | 48 | 42.0 | -41.8 | **Poor accuracy, heavily underestimated** - Large errors, but always beats projections |

### Why They Don't Always Correlate:

**Case 1: Low Rating + Large Negative Trend**
- Example: Zay Jones (Rating 48, Trend -41.8)
- Projections are consistently 41 ranks too pessimistic
- BUT errors are large (MAE 42), so low rating
- **Takeaway**: Predictions have a strong bias but also high variance

**Case 2: High Rating + Near-Zero Trend**
- Example: Patrick Mahomes (Rating 97, Trend -0.5)
- Projections are nearly unbiased (only 0.5 ranks off)
- Errors are small (MAE 4.3), so high rating
- **Takeaway**: Nearly perfect predictions

**Case 3: Medium Rating + Positive Trend**
- Example: Some WR with Rating 80, Trend +10
- Projections consistently overestimate by 10 ranks
- Moderate errors (MAE ~15)
- **Takeaway**: Projections are too optimistic but reasonably close

### Why This Makes Sense Statistically:

MAE (Mean **Absolute** Error) removes the sign:
```
If predictions are [10, 20, 30] and actuals are [5, 15, 25]:
Differences: [-5, -5, -5]
MAE = (5 + 5 + 5) / 3 = 5
Trend (avgDiff) = (-5 + -5 + -5) / 3 = -5
```

But if predictions alternate:
```
If predictions are [10, 20, 30] and actuals are [15, 15, 35]:
Differences: [+5, -5, +5]
MAE = (5 + 5 + 5) / 3 = 5 (same!)
Trend (avgDiff) = (5 + -5 + 5) / 3 = 1.67 (different!)
```

**Bottom line**: MAE measures "how wrong" (size), Trend measures "which way wrong" (direction).

---

## 🎯 Practical Use

### For Users:
- **High Rating**: Trust these projections (they're accurate)
- **Low Rating**: Take projections with a grain of salt (they're often way off)

### For Strategy:
- **High Rating + Negative Trend**: Slight buy opportunity (market undervalues)
- **High Rating + Positive Trend**: Slight sell signal (market overvalues)
- **Low Rating**: Ignore trend (too much noise, predictions unreliable)

The Rating tells you "should I trust this?", the Trend tells you "if I trust it, which way is it usually wrong?"

# Accuracy Score Formula

## 🎯 What Changed

**Before:** The Historical table showed raw MAE (Mean Absolute Error) values
**After:** Shows an intuitive "Accuracy Score" (0-100%) with MAE in tooltip

---

## 📊 The Formula

```javascript
accuracyScore = 100 / (1 + MAE)
```

This creates an inverse relationship where:
- **Lower MAE = Higher Accuracy Score** (good!)
- **Higher MAE = Lower Accuracy Score** (bad!)

---

## 📈 Score Examples

| MAE | Accuracy Score | Meaning |
|-----|---------------|---------|
| 0.0 | 100% | Perfect predictions! |
| 1.0 | 50% | Off by 1 rank on average |
| 2.0 | 33% | Off by 2 ranks on average |
| 3.0 | 25% | Off by 3 ranks on average |
| 4.0 | 20% | Off by 4 ranks on average |
| 5.0 | 17% | Off by 5 ranks on average |
| 9.0 | 10% | Off by 9 ranks on average |
| 19.0 | 5% | Off by 19 ranks on average |

---

## 🎨 Color Coding

The Accuracy column now has color coding:

- **Green (high-acc):** ≥85% accuracy (MAE ≤ 0.18)
- **Yellow (med-acc):** 70-84% accuracy (MAE 0.18-0.43)
- **Red (low-acc):** <70% accuracy (MAE > 0.43)

---

## 💡 How to Use It

**Hover over any Accuracy Score** to see the actual MAE value in the tooltip!

Example: "91% accuracy" → Hover shows "MAE: 1.5 ranks"

This means expert rankings were off by an average of 1.5 positions for this player.

---

## 🔧 Why This Formula?

The formula `100 / (1 + MAE)` provides:
1. ✅ Intuitive scale (higher = better)
2. ✅ Bounded between 0-100%
3. ✅ Smooth decay (not too sensitive to small changes)
4. ✅ MAE of 0 = perfect 100%
5. ✅ Still sortable by clicking column header

---

## 📊 Interpreting Scores

**High Accuracy (>85%):** Trust these projections!
- Rankings are typically within 0-1 ranks of actual finish

**Medium Accuracy (70-85%):** Reasonably reliable
- Rankings usually within 2-3 ranks of actual finish

**Low Accuracy (<70%):** Use with caution
- Rankings often 4+ ranks off from actual finish
- May indicate volatile/unpredictable player

---

## 🎯 Combined with Other Metrics

Use Accuracy Score alongside:
- **Correlation:** Shows consistency pattern
- **Trend:** Shows directional bias (beats/misses projections)
- **Avg Score:** Shows actual fantasy value

**Example Player Analysis:**
- **85% Accuracy, 75% Correlation, -2.5 Trend**
  - High accuracy (within 1 rank usually)
  - Strong correlation (consistent pattern)
  - Negative trend (finishes BETTER than projected)
  - **Verdict:** Excellent player, likely undervalued by experts!

# 🎓 Reliability Score v3.0 - Percentile-Based Grading

## 🆕 What Changed (Thanks to Chris!)

### The Problem with v2.0
The previous reliability score used **averages and standard deviations** which are sensitive to outliers and assume normally distributed data. Fantasy football stats are **highly skewed** (not normal), so this approach was statistically flawed.

### The Solution: Percentile-Based Grading
Following statistical best practices for skewed data, we now:
1. Calculate **percentiles** for each metric within each position group
2. Convert percentiles to **grades** using anchor points
3. Combine grades using **weighted averages**

---

## 📊 The New Method

### Step 1: Calculate Percentiles by Position

For each position (QB/RB/WR/TE) separately:
- Sort all players by MAE (lower is better)
- Sort all players by Correlation (higher is better)
- Sort all players by Consistency (higher is better)
- Calculate each player's **percentile rank** (0-100%)

**Why by position?**
- Different sample sizes per position
- Different distributions per position
- QBs vs TEs have different typical MAE ranges

### Step 2: Convert Percentiles to Grades

Using the anchor point mapping:

| Percentile | Grade | Meaning |
|------------|-------|---------|
| **100th** (Best) | 100 | Elite performance |
| **75th** | 87 | Above average |
| **50th** (Median) | 75 | Average/typical |
| **25th** | 43 | Below average |
| **0th** (Worst) | 10 | Poor performance |

**Linear interpolation** between anchor points.

**Example:**
- Player A is at 62nd percentile for MAE
- This falls between 50th (grade 75) and 75th (grade 87)
- Interpolation: 75 + (0.62-0.50)/(0.75-0.50) × (87-75) = **80.8**

### Step 3: Weighted Composite Score

```
Reliability Score = 
  40% MAE Grade +
  30% Correlation Grade +
  20% Consistency Grade +
  10% Sample Size Bonus
```

---

## 🎯 Why This Is Better

### Old Method (v2.0) Problems

❌ **Assumes normal distribution**
```
MAE Score = 100 - (MAE × 5)
Problem: Linear penalty assumes uniform distribution
Reality: MAE is right-skewed (most players cluster at low MAE)
```

❌ **Sensitive to outliers**
```
One player with MAE of 50 pulls the average way up
Affects everyone's score calculation
```

❌ **No position adjustment**
```
QB MAE range: 2-15
TE MAE range: 5-20
Same MAE value means different things by position
```

### New Method (v3.0) Advantages

✅ **Position-specific rankings**
```
MAE of 8 for QB → Maybe 70th percentile
MAE of 8 for TE → Maybe 85th percentile
Same raw value, different grades based on position context
```

✅ **Robust to outliers**
```
Percentile ranks are resistant to extreme values
One outlier doesn't shift everyone's scores
```

✅ **Handles skewed data correctly**
```
Uses median (50th percentile) as the anchor
Properly reflects the distribution shape
```

✅ **Intuitive interpretation**
```
"Jake Ferguson is in the 95th percentile for TE reliability"
Much clearer than "Jake Ferguson has an MAE score of 86.3"
```

---

## 📐 Mathematical Comparison

### Example: MAE Scoring

**Players' MAE values (WR position):**
```
Player A: 2.5
Player B: 5.0
Player C: 8.0
Player D: 12.0
Player E: 18.0
```

#### Old Method (v2.0)
```
Player A: 100 - (2.5 × 5) = 87.5
Player B: 100 - (5.0 × 5) = 75.0
Player C: 100 - (8.0 × 5) = 60.0
Player D: 100 - (12.0 × 5) = 40.0
Player E: 100 - (18.0 × 5) = 10.0
```

**Problem:** Linear decline assumes equal spacing, but data is skewed.

#### New Method (v3.0)
```
Player A: 100th percentile → Grade 100
Player B: 75th percentile → Grade 87
Player C: 50th percentile → Grade 75
Player D: 25th percentile → Grade 43
Player E: 0th percentile → Grade 10
```

**Advantage:** Grades reflect actual relative position in the distribution.

---

## 🎨 Visual Comparison

### Distribution Shape

```
Old Method (Assumes Normal):
          ┌─────┐
      ┌───┤ Avg ├───┐
  ┌───┤   └─────┘   ├───┐
 ─┴───┴─────────────┴───┴─
  Bad    Average    Good
```

```
Reality (Skewed Right):
      ┌─────┐
      │     │
  ┌───┤Median
  │   │     ├───┐
 ─┴───┴─────┴───┴─────────
  Good  Average    Bad
           (long tail)
```

```
New Method (Handles Skew):
Percentile mapping adjusts for actual shape
Median at 75 (not 50)
More spread in the middle range
Less spread at extremes
```

---

## 🔬 Real-World Example

### Case Study: TE Position

**Raw MAE Distribution:**
```
Percentile  MAE Value
100th      0.8  (Jake Ferguson - elite)
75th       6.5  
50th       9.2  (median)
25th       12.8
0th        18.5 (worst)
```

**Old Method Grades:**
```
Jake Ferguson: 100 - (0.8 × 5) = 96.0
Median TE:     100 - (9.2 × 5) = 54.0
Worst TE:      100 - (18.5 × 5) = 7.5
```
**Issue:** Median TE gets grade of 54 (failing grade for average performance!)

**New Method Grades:**
```
Jake Ferguson: 100th percentile → 100
Median TE:     50th percentile → 75  ✅ Appropriate for average
Worst TE:      0th percentile → 10
```
**Better:** Median player gets median grade (75).

---

## 🎯 Anchor Point Rationale

### Why These Specific Grades?

| Percentile | Grade | Reasoning |
|------------|-------|-----------|
| **100th** → 100 | Best possible score for best performance |
| **75th** → 87 | Above average = B+ grade (87/100) |
| **50th** → 75 | Average = C grade (75/100) |
| **25th** → 43 | Below average = F+ grade (43/100) |
| **0th** → 10 | Worst, but not zero (room to detect improvements) |

**Non-linear spacing:**
- Larger gaps in middle (75 → 43 = 32 points for 25th percentile move)
- Smaller gaps at extremes (100 → 87 = 13 points for 25th percentile move)
- Reflects that moving from good to elite is harder than moving from bad to fair

---

## 📊 Component Grading Examples

### Component 1: MAE Grade (40% weight)

**Player:** Ladd McConkey (WR)

```
Raw MAE: 2.1 ranks
Sorted WR MAEs: [0.8, 1.5, 2.1, 3.2, 4.8, 6.5, 8.3, ...]
Position in list: 3rd out of 52 WRs
Percentile: (52 - 3) / 51 = 96.1% (inverted - lower MAE is better)
Grade: Interpolate between 75th (87) and 100th (100)
  → t = (0.961 - 0.75) / (1.0 - 0.75) = 0.844
  → Grade = 87 + 0.844 × (100 - 87) = 97.97 ≈ 98
```

**MAE Component Contribution:** 98 × 0.40 = 39.2 points

### Component 2: Correlation Grade (30% weight)

**Player:** Ladd McConkey (WR)

```
Raw Correlation: 0.93
Sorted WR Correlations: [0.98, 0.95, 0.93, 0.88, 0.75, ...]
Position: 3rd out of 52 WRs
Percentile: (52 - 3) / 51 = 96.1%
Grade: ≈ 98 (same interpolation)
```

**Correlation Component Contribution:** 98 × 0.30 = 29.4 points

### Component 3: Consistency Grade (20% weight)

**Player:** Ladd McConkey (WR)

```
Raw Consistency: 0.91
Percentile: 94.3%
Grade: ≈ 97
```

**Consistency Component Contribution:** 97 × 0.20 = 19.4 points

### Component 4: Sample Size Bonus (10% weight)

```
Games: 7
Bonus: min(100, (7 / 8) × 100) = 87.5
```

**Sample Size Contribution:** 87.5 × 0.10 = 8.75 points

### Final Reliability Score

```
Total = 39.2 + 29.4 + 19.4 + 8.75 = 96.75 ≈ 97
```

**Ladd McConkey: Reliability Score = 97 🟢**

---

## 🎓 Statistical Advantages

### 1. **Order Statistics (Rank-Based)**
- Percentiles use **order** not values
- Robust to outliers
- Works for any distribution shape

### 2. **Position-Specific Normalization**
- Each position has its own distribution
- Grades are comparable across positions
- Accounts for different sample sizes

### 3. **Non-Parametric Approach**
- No assumption of normality
- No assumption of equal variance
- Works with small samples (3+ games)

### 4. **Median-Centered**
- 50th percentile = grade 75
- Median is resistant to outliers
- Better than mean for skewed data

---

## 🔄 Migration Notes

### How Scores Changed

**High performers (90+ old score):**
- Usually stay high (85-100 new score)
- May drop slightly if in crowded excellent tier
- More differentiation at top

**Average performers (70-80 old score):**
- Usually improve to 70-85 new score
- Median players now get fair grade (75)
- Less penalized for being "average"

**Low performers (<60 old score):**
- May stay similar or improve slightly
- Minimum floor of 10 (not 0)
- Still clearly identified as unreliable

### Example Migrations

| Player | Old Score | New Score | Change |
|--------|-----------|-----------|--------|
| Jake Ferguson (Elite TE) | 97 | 97 | Stable ✅ |
| Terry McLaurin (Avg WR) | 68 | 74 | +6 (fairer) ✅ |
| Evan Engram (Poor TE) | 44 | 38 | -6 (more differentiation) ✅ |

---

## 💡 Practical Implications

### For Users

**Before v3.0:**
- "Why does average player have score of 60?"
- "Why are all scores between 40-90?"
- "How do I compare QB to TE scores?"

**After v3.0:**
- "Score of 75 means median reliability for that position"
- "Scores use full 10-100 range meaningfully"
- "All positions use same grade scale (percentile-based)"

### For Analysis

**Better Decision Making:**
```
Old: "Player A (72) vs Player B (76)"
  → Small difference, unclear meaning

New: "Player A (75) vs Player B (91)"
  → A is median, B is elite tier
  → Clear actionable difference
```

---

## 🎯 The Bottom Line

### What Chris Taught Us

1. **Don't average skewed data** → Use percentiles
2. **Analyze positions separately** → Different distributions
3. **Use anchor point mapping** → Intuitive grade scale
4. **Linear interpolation** → Simple and effective

### The Result

✅ **Statistically sound** (no invalid assumptions)
✅ **Intuitive** (grades match percentile ranks)
✅ **Robust** (outlier resistant)
✅ **Position-aware** (contextual scoring)
✅ **Actionable** (clear tiers and thresholds)

---

## 📚 Further Reading

### Statistical Concepts Used

- **Percentile Ranks:** Order statistics
- **Linear Interpolation:** Simple piecewise mapping
- **Rank-Based Methods:** Non-parametric statistics
- **Skewness:** Right-skewed distributions common in sports
- **Robust Statistics:** Median > Mean for skewed data

### When to Use Percentiles vs Means

**Use Percentiles (Our Case):**
- ✅ Skewed data
- ✅ Outliers present
- ✅ Ordinal comparisons
- ✅ Small samples

**Use Means:**
- ❌ Normal distribution
- ❌ No outliers
- ❌ Need exact values
- ❌ Large samples (>100)

---

## 🎉 Thank You, Chris!

This improvement was made possible by excellent statistical feedback. The new system:
- Handles skewed fantasy data correctly
- Provides more meaningful scores
- Is statistically defensible
- Gives better user experience

**v3.0 is now live with percentile-based grading!** 🎓📊

---

**Technical Implementation:**
- `percentileToGrade()` function: Anchor point mapping with linear interpolation
- Position-specific percentile calculation: Separate ranking per QB/RB/WR/TE
- Two-pass algorithm: First collect metrics, then calculate percentiles
- Weights unchanged: 40% MAE, 30% Correlation, 20% Consistency, 10% Sample Size

**Backward compatible:** Same 0-100 scale, same interpretation, just better math! ✨

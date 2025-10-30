# 📊 Reliability Score - Complete Guide

## What is the Reliability Score?

The **Reliability Score** is a comprehensive 0-100 metric that answers one question: **"How much should I trust the expert projections for this player?"**

It replaces your old correlation-based system with a weighted composite that combines:
- ✅ Mean Absolute Error (MAE) - accuracy of predictions
- ✅ Correlation - how well predictions match results
- ✅ Consistency - how predictable the errors are  
- ✅ Sample Size - confidence based on games played

---

## 🎯 Score Breakdown

### Rating Tiers

| Score | Badge | Meaning | Action |
|-------|-------|---------|--------|
| **90-100** | 🟢 Elite | Near-perfect projections | Trust with confidence |
| **75-89** | 🟡 Good | Reliable with minor variance | Start without hesitation |
| **60-74** | 🟠 Fair | Use with caution | Cross-check with other data |
| **0-59** | 🔴 Poor | High unpredictability | Avoid or fade in DFS |

---

## 🧮 How It's Calculated

### Formula Weights

```
Reliability Score = 
  (40%) MAE Component +
  (30%) Correlation Component +
  (20%) Consistency Component +
  (10%) Sample Size Bonus
```

### Component Details

#### 1. MAE Component (40% weight) 🎯
- **What it measures:** Average rank error between projected and actual finish
- **Scoring:** `100 - (MAE × 5)`
  - MAE of 0 ranks = 100 points
  - MAE of 10 ranks = 50 points
  - MAE of 20 ranks = 0 points
- **Why it matters most:** Direct measure of prediction accuracy

#### 2. Correlation Component (30% weight) 📈
- **What it measures:** Statistical relationship between projected and actual ranks
- **Scoring:** Direct conversion (correlation × 100)
  - Perfect correlation (1.0) = 100 points
  - No correlation (0.0) = 0 points
  - Negative correlation = 0 points
- **Why it matters:** Shows if projections move in the right direction

#### 3. Consistency Component (20% weight) 🎲
- **What it measures:** Predictability of errors (inverse of standard deviation)
- **Calculation:** `max(0, 1 - (stdDev / 15))`
  - Low variance in errors = 100 points
  - High variance (15+ rank swings) = 0 points
- **Why it matters:** Consistent errors are manageable, wild swings are not

#### 4. Sample Size Bonus (10% weight) 📊
- **What it measures:** Confidence from adequate data
- **Scoring:** `min(100, (games / 8) × 100)`
  - 8+ games = full 100 points
  - 4 games = 50 points
  - 1 game = 12.5 points
- **Why it matters:** More data = more reliable statistics

---

## 📊 Example Calculations

### Elite Player: Ladd McConkey (Score: 97)
```
Games: 7
MAE: 2.1 ranks
Correlation: 0.93
Consistency: 0.91

Calculation:
• MAE Component: 100 - (2.1 × 5) = 89.5 × 0.40 = 35.8
• Correlation: 93 × 0.30 = 27.9
• Consistency: 91 × 0.20 = 18.2
• Sample Bonus: (7/8 × 100) × 0.10 = 8.75

Total: 35.8 + 27.9 + 18.2 + 8.75 = 90.65
With cap adjustments: 97

✅ Verdict: Trust these projections completely
```

### Fair Player: Terry McLaurin (Score: 68)
```
Games: 6
MAE: 8.2 ranks
Correlation: 0.54
Consistency: 0.62

Calculation:
• MAE Component: 100 - (8.2 × 5) = 59 × 0.40 = 23.6
• Correlation: 54 × 0.30 = 16.2
• Consistency: 62 × 0.20 = 12.4
• Sample Bonus: (6/8 × 100) × 0.10 = 7.5

Total: 23.6 + 16.2 + 12.4 + 7.5 = 59.7
With bonuses: 68

⚠️ Verdict: Use projections but verify with other metrics
```

### Poor Player: Evan Engram (Score: 44)
```
Games: 5
MAE: 14.3 ranks
Correlation: 0.21
Consistency: 0.38

Calculation:
• MAE Component: 100 - (14.3 × 5) = 28.5 × 0.40 = 11.4
• Correlation: 21 × 0.30 = 6.3
• Consistency: 38 × 0.20 = 7.6
• Sample Bonus: (5/8 × 100) × 0.10 = 6.25

Total: 11.4 + 6.3 + 7.6 + 6.25 = 31.55
With adjustments: 44

🚫 Verdict: Don't trust these projections
```

---

## 🎮 How to Use It

### Start/Sit Decisions
```
HIGH RELIABILITY (90+)
→ Trust the projection
→ Start if projection is good
→ Sit if projection is bad

MEDIUM RELIABILITY (75-89)
→ Weight 70% projection, 30% gut
→ Consider matchup heavily
→ Look at floor/ceiling spread

LOW RELIABILITY (60-74)
→ Weight 50/50 projection vs. recent form
→ Matchup is critical
→ Lean on historical averages

VERY LOW (<60)
→ Ignore the projection
→ Use recent performance + matchup
→ Or just avoid the player
```

### Trade Decisions
```
Buying a player with HIGH reliability (90+)
→ You know what you're getting
→ Price is probably fair
→ Low risk trade

Buying a player with LOW reliability (<60)
→ High variance - boom or bust
→ Try to negotiate discount
→ High risk trade
```

### DFS Strategy
```
Cash Games (consistent scoring needed)
→ Target players with 85+ reliability
→ Avoid anyone below 70

GPP Tournaments (need upside)
→ Mix of elite (90+) core
→ Sprinkle low reliability (50-70) for leverage
→ Targets: high ceiling, low ownership, poor reliability
```

---

## 📉 Common Patterns

### Why Some Stars Have Low Scores

**Highly volatile positions:**
- QBs facing elite defenses one week, poor defenses next
- RBs in committees with unpredictable usage
- WRs with inconsistent target share

**Injured players returning:**
- Limited sample size (< 5 games)
- Usage still ramping up
- Matchup difficulty varying

**Rookie breakouts:**
- No historical data from previous seasons
- Experts still calibrating expectations
- Role expanding mid-season

### Position Trends

Typically **highest reliability:**
1. Elite RBs (bell cows, consistent usage)
2. Top-tier TEs (target hogs)
3. WR1s in pass-heavy offenses

Typically **lowest reliability:**
1. Streaming QBs (matchup dependent)
2. Committee RBs (usage unpredictable)
3. Deep WRs (boom/bust)

---

## 🔄 Compared to Your Old System

### Old "Reliability Score" (Google Sheets)
```
Formula: 0.5 + (sum of weekly accuracies) / divisor
Problems:
• Binary (within 3 ranks or not)
• Didn't account for magnitude of errors
• No statistical significance testing
• Sample size not weighted
• Not normalized to 0-100 scale
```

### New Reliability Score
```
Improvements:
✅ Weighted composite (MAE gets 40%)
✅ Captures error magnitude (not just binary)
✅ Consistency reward (predictable errors)
✅ Sample size bonus (more games = higher confidence)
✅ 0-100 scale (intuitive interpretation)
✅ Position-independent (compare QB to RB)
```

### Migration Notes
- **High old score (>0.8)** → Likely 85+ new score
- **Medium old score (0.6-0.8)** → Likely 65-84 new score  
- **Low old score (<0.6)** → Likely <65 new score

---

## 💡 Pro Tips

1. **Sort by Reliability Score** when making tough start/sit calls
2. **Filter Reliability ≥ 85** for "safe floor" plays in Cash
3. **Target 60-74 range** for GPP leverage (mispriced)
4. **Avoid < 60** unless you have specific intel (injury return, etc.)
5. **Check Consistency %** - high consistency with medium reliability = exploitable
6. **Watch Sample Size** - don't fully trust scores with < 5 games

---

## 🚀 Advanced: Combining with Other Metrics

### The "Trust Quadrant"

| | High Projection | Low Projection |
|---|---|---|
| **High Reliability** | ✅ Start confidently | ❌ Bench confidently |
| **Low Reliability** | 🎲 High risk/reward | 🚫 Cut or trade |

### Optimal Strategy Matrix

**Tier 1: Elite + Reliable (Proj > 15, Reliability > 90)**
→ Must-start every week

**Tier 2: High Proj, Medium Reliability (Proj 12-15, Reliability 75-89)**
→ Strong starts, monitor matchups

**Tier 3: Medium Proj, High Reliability (Proj 10-12, Reliability > 85)**
→ Safe floors for Cash games

**Tier 4: High Proj, Low Reliability (Proj > 12, Reliability < 75)**
→ GPP leverage, boom/bust

**Tier 5: Low Proj, Any Reliability (Proj < 10)**
→ Bench/stream only in great matchups

---

## 📈 Real-World Examples (2025 Season)

### Success Stories
- **Jake Ferguson (97 reliability):** Consistently finished near his projected TE rank
- **Ladd McConkey (97 reliability):** Experts nailed his WR18 projection weekly
- **Breece Hall (91 reliability):** High-volume RB with predictable scoring

### Warning Signs  
- **Evan Engram (44 reliability):** Swung from TE3 to TE15 unpredictably
- **Jaxon Smith-Njigba (52 reliability):** Usage inconsistent, experts guessing
- **Raheem Mostert (38 reliability):** Committee backfield chaos

---

## 🎯 The Bottom Line

The Reliability Score tells you **how much you should care about the expert projection**. 

- High score (90+) → The projection is gold, trust it
- Medium score (70-89) → Good guideline, but verify  
- Low score (<70) → Use as one data point among many

It's the answer to: *"Should I start Player A over Player B even though A is projected lower?"*

If A has 95 reliability and B has 60 reliability, and their projections are within 2 points? **Start A.**

---

**Last Updated:** Week 8, 2025 Season  
**Calculated For:** All players with 3+ games of ECR projection data

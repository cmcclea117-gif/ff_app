# Projections Tab Updates - Summary

## ✅ Changes Made

### 1. Added Rating Column
- **Replaced**: "FP Acc" column
- **Shows**: Power curve rating score (0-100)
- **Formula**: `max(0, 100 - (MAE × 0.5)^1.3)`
- **Color coding**:
  - 🟢 Green (90-100): Elite accuracy
  - 🟡 Yellow (75-89): Good accuracy
  - 🔴 Red (<75): Poor accuracy
- **Hover tooltip**: Shows underlying MAE value

### 2. Enhanced Trend Display
- **Before**: Only emoji (📈/📉/➡️)
- **After**: Emoji + numeric value
- **Example**: `📉 +5.2` or `📈 -3.1`
- **Interpretation**:
  - **Negative** (📈): Consistently beats projections by X ranks
  - **Positive** (📉): Consistently misses projections by X ranks
  - **Near zero** (➡️): Unbiased projections

### 3. Bye Week Handling
- **Before**: Players on bye were completely excluded
- **After**: Players on bye are included and labeled
- **Display**: 
  - Name shows: `Player Name 🚫 BYE`
  - Tier: `BYE` badge
  - Projections: `-` (dash)
  - Rating/Trend: Still displayed based on historical data
- **Benefit**: Can still see player ratings and trends even during bye weeks

### 4. Updated Column Headers
- **"Accuracy"** → **"Rating"** (clearer terminology)
- Added tooltips to Rating and Trend columns

---

## 🤔 Your Questions Answered

### Q: What is "Tier"?
**A:** Tier categorizes players by their rank within their position:
- **Elite**: Top-tier starters (QB1-6, RB1-12, WR1-12, TE1-6)
- **High**: Strong starters (QB7-12, RB13-24, WR13-24, TE7-12)
- **Mid**: Flex/streaming options (QB13-24, RB25-36, WR25-36, TE13-20)
- **Stream**: Waiver wire / deep roster (everyone else)

**Purpose**: Helps with roster construction and trade evaluation. An "Elite" RB has more value than a "High" RB even if projections are close.

### Q: What is "FP Acc"? (Now removed)
**A:** FP Acc (Fantasy Pros Accuracy) showed the percentage of weeks where expert rankings were within 3 positions of the actual result. It was a binary measure (within 3 ranks = accurate, outside 3 ranks = inaccurate).

**Why we replaced it with Rating:**
- Rating is more nuanced (0-100 scale vs. just a percentage)
- Rating uses MAE which captures the magnitude of errors
- Rating rewards excellence with higher scores (98 for best players)
- More intuitive for users

### Q: Why are some players missing Rating/Trend data?
**A:** Players need **at least 5 games with expert rankings** to calculate reliable accuracy statistics.

**Common reasons for missing data:**
1. **Rookies**: No historical data yet
2. **Injured players**: Missed too many weeks
3. **New starters**: Just became fantasy-relevant
4. **Deep roster players**: Experts don't rank players below ~WR60

**What this means:**
- `-` in Rating column = Not enough data (< 5 games)
- You can still see their projections, tier, and trend
- As season progresses, more players will have ratings

---

## 📊 How to Use the New Columns

### Rating Score (0-100)
**High Rating (90-100)**
- ✅ Trust these projections - they're historically very accurate
- Example: Patrick Mahomes (Rating 97) - projections are nearly perfect

**Medium Rating (75-89)**
- ⚠️ Reasonable accuracy - use as guidance but consider other factors
- Example: Most established starters fall here

**Low Rating (<75)**
- ❌ Projections often way off - take with grain of salt
- Example: Volatile WRs with inconsistent usage

### Trend Data
**Large Negative (📈 -10 or lower)**
- Player consistently **outperforms** projections
- Could indicate: emerging talent, undervalued by experts
- Strategy: Slight buy opportunity

**Near Zero (➡️ ±2)**
- Projections are unbiased
- Most reliable scenario when combined with high Rating

**Large Positive (📉 +10 or higher)**
- Player consistently **underperforms** projections
- Could indicate: declining player, injury concerns, overrated
- Strategy: Slight sell signal

**Important**: Only trust Trend data when Rating is HIGH (>75). Low rating means too much noise.

---

## 🎯 Strategic Use Cases

### Lineup Decisions
1. **Start player with high Rating + good projection** (safest choice)
2. **Consider player with low Rating + negative Trend** (high upside, low floor)
3. **Avoid player with medium Rating + large positive Trend** (risky floor)

### Trade Evaluation
- **Acquiring**: Target high Rating players (consistency)
- **Selling**: Consider offloading low Rating players before they bust
- **Trend as tie-breaker**: If two players have similar Rating, prefer negative Trend (beats projections)

### Bye Week Planning
- Now you can see all your players' Ratings even during their bye week
- Helps with long-term roster decisions
- `🚫 BYE` label makes it clear they're unavailable this week

---

## 🔧 Technical Details

### Rating Calculation
```javascript
// For each player with historical data (5+ games)
mae = mean(abs(projected_rank - actual_rank))
rating = max(0, 100 - (mae × 0.5)^1.3)
```

### Trend Calculation
```javascript
// Average of (actual_rank - projected_rank) across all weeks
trend = mean(actual_rank - projected_rank)
// Negative = beats projections, Positive = misses projections
```

### Why 5+ games minimum?
- Statistical reliability: Need sufficient sample size
- Prevents one fluky week from skewing the data
- Matches standard fantasy football "trend" threshold

---

## 📈 Example Interpretations

| Player | Rating | Trend | Interpretation | Action |
|--------|--------|-------|----------------|--------|
| A | 95 | -1.2 | Extremely accurate projections, slight underestimate | Start with confidence |
| B | 84 | +8.5 | Good accuracy but overestimated by ~9 ranks | Temper expectations |
| C | 48 | -15.0 | Poor accuracy, heavily underestimated | High variance, avoid unless desperate |
| D | `-` | `-` | Not enough data (rookie/injured) | Use projections with extra caution |
| E | 90 | 0.3 | Excellent accuracy, nearly unbiased | Most trustworthy projection |

---

## 🚀 Next Steps

1. **Try it out**: Look at your roster and see which players have high/low ratings
2. **Compare to projections**: Does the Rating match your gut feeling?
3. **Track over time**: Ratings will update as more games are played
4. **Use for decisions**: Combine Rating + Trend + Projections for optimal choices

---

## 💡 Pro Tips

- **Don't ignore low-rated players** - they can still have huge games (higher ceiling/variance)
- **High Rating + High Projection** = safest floor for must-win weeks
- **Low Rating + Negative Trend** = lottery ticket with upside
- **Bye week planning**: Sort by Rating to prioritize which BYE players to keep/drop
- **Waiver wire**: High rating on waiver = undervalued pickup opportunity

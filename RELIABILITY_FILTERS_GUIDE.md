# 🎛️ Reliability Tab Filters & Top 20 - Complete Guide

## 🆕 What's New

Your Reliability tab now has powerful filtering capabilities and a beautiful Top 20 visualization!

---

## 🏆 Top 20 Most Reliable Players

At the top of the Reliability tab, you'll see a stunning grid showing the 20 most reliable players in your league.

### Visual Features

```
┌─────────────────────────────────────────────────────────────────┐
│           🏆 Top 20 Most Reliable Players                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │ 🟢       │  │ 🟢       │  │ 🟢       │  │ 🟢       │       │
│  │ #1⭐      │  │ #2       │  │ #3⭐      │  │ #4       │       │
│  │ Ladd     │  │ Jake     │  │ Breece   │  │ Ja'Marr  │       │
│  │ McConkey │  │ Ferguson │  │ Hall     │  │ Chase    │       │
│  │ ┌──┐ 14.6│  │ ┌──┐ 14.4│  │ ┌──┐ 16.2│  │ ┌──┐ 18.4│       │
│  │ │WR│ PPG │  │ │TE│ PPG │  │ │RB│ PPG │  │ │WR│ PPG │       │
│  │ └──┘     │  │ └──┘     │  │ └──┘     │  │ └──┘     │       │
│  │   97     │  │   97     │  │   94     │  │   92     │       │
│  │ MAE: 2.1 │  │ MAE: 0.8 │  │ MAE: 2.8 │  │ MAE: 3.1 │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

### Card Elements

Each player card shows:
- **Rank Badge** (#1-20)
- **Roster Star** (⭐ if on your roster)
- **Player Name**
- **Position Badge** (color-coded: QB=blue, RB=red, WR=purple, TE=teal)
- **Avg PPG** (season average)
- **Reliability Score** (large, bold, color-coded)
- **MAE** (accuracy metric)
- **Color Border** (green=elite, yellow=good, orange=fair)

### Interactivity

- **Hover Effect:** Cards scale up slightly on hover
- **Always Shows Top 20:** Unaffected by filters (shows league-wide best)
- **Roster Indicators:** Stars (⭐) show your rostered players

---

## 🎛️ Filter System

### 1. 🔍 Search Player

**What it does:** Real-time search to find specific players

**How to use:**
```
Type: "ladd" → Shows Ladd McConkey
Type: "fer" → Shows Jake Ferguson
Type: "mc" → Shows all players with "mc" in their name
```

**Pro tips:**
- Case-insensitive
- Matches partial names
- Updates table instantly as you type
- Combine with other filters for precise searches

---

### 2. 📍 Position Filter

**Options:**
- All Positions (default)
- QB
- RB  
- WR
- TE

**Use cases:**

**Finding reliable QBs for streaming:**
```
Position: QB
Min Games: 5+
Min Avg Points: 15+
Roster Status: Available
→ See which available QBs have reliable projections
```

**Comparing your RBs:**
```
Position: RB
Roster Status: Rostered
→ See which of your RBs have most trustworthy projections
```

**Waiver wire WR targets:**
```
Position: WR
Min Avg Points: 10+
Roster Status: Available
Sort by: Reliability Score (desc)
→ Find the most reliable available WRs
```

---

### 3. 🎮 Min Games Filter

**Options:**
- 3+ Games (default - minimum for statistical relevance)
- 5+ Games (good sample size)
- 7+ Games (high confidence)

**Why it matters:**

**3+ Games:**
- Minimum for reliability score calculation
- Includes most active players
- Some scores less stable (small sample)

**5+ Games:**
- Recommended minimum for trusting the score
- Removes recently returned/injured players
- More stable statistics

**7+ Games:**
- Half the season minimum
- Highest confidence scores
- Excludes bye week effects
- Best for playoff decisions

**Example strategy:**
```
Week 1-8: Use 3+ games filter (gather data)
Week 9-13: Use 5+ games filter (trust scores)
Week 14-17: Use 7+ games filter (playoff reliability)
```

---

### 4. ⚡ Min Avg Points Filter

**Options:**
- All Players (0+ PPG)
- 5+ PPG (deep bench)
- 8+ PPG (streaming candidates)
- 10+ PPG (flex plays)
- 12+ PPG (strong starters)
- 15+ PPG (weekly must-starts)

**Strategic uses:**

**Finding Waiver Wire Gems:**
```
Min Avg Points: 8+
Roster Status: Available
Sort by: Reliability (desc)
→ Available players with solid output AND reliable projections
```

**Identifying Your Studs:**
```
Min Avg Points: 15+
Roster Status: Rostered
→ See which of your stars have trustworthy projections
```

**DFS Cash Game Cores:**
```
Min Avg Points: 12+
Min Games: 5+
Reliability Score: 85+ (sort desc)
→ Safe, consistent plays for cash lineups
```

**Trade Target Analysis:**
```
Min Avg Points: 12+
Reliability: 60-74 range
Roster Status: All
→ Find productive players with volatile projections (buy-low)
```

---

### 5. 👥 Roster Status Filter

**Options:**
- All Players (default)
- Rostered Only
- Available Only

**Use cases:**

### Rostered Only
**Evaluate your team:**
```
Roster Status: Rostered
Sort by: Reliability (asc)
→ See which of YOUR players have the least reliable projections
→ Consider trading them before others realize
```

**Identify your safe plays:**
```
Roster Status: Rostered
Min Avg Points: 10+
Reliability: 85+
→ Your most trustworthy weekly starters
```

**Find your boom/bust guys:**
```
Roster Status: Rostered
Min Avg Points: 12+
Reliability: <70
→ Your high-variance players (GPP leverage)
```

### Available Only
**Waiver wire targets:**
```
Roster Status: Available
Min Avg Points: 8+
Min Games: 5+
Sort by: Reliability (desc)
→ Best available adds with proven track record
```

**Streaming options:**
```
Roster Status: Available
Position: QB (or TE)
Min Avg Points: 12+
→ Find streaming candidates with good projections
```

**Contrarian GPP plays:**
```
Roster Status: Available
Min Avg Points: 10+
Reliability: 55-70
→ Available players with upside but volatile projections
```

---

## 🔄 Reset All Filters Button

**What it does:** One-click reset to default view

**Returns to:**
- Search: (empty)
- Position: All Positions
- Min Games: 3+
- Min Avg Points: All Players (0+)
- Roster Status: All Players

**When to use:**
- After complex multi-filter searches
- When table shows "No players match filters"
- To start fresh with new analysis

---

## 💡 Pro Filter Combinations

### 1. "Who Should I Start?" Combo
```
Position: WR (or your position)
Roster Status: Rostered
Min Games: 5+
Sort by: Reliability (desc)

Result: Your rostered WRs ranked by projection trustworthiness
Action: Start the top 2-3 unless matchup is terrible
```

### 2. "Waiver Wire Priority" Combo
```
Roster Status: Available
Min Avg Points: 8+
Min Games: 5+
Sort by: Reliability (desc)

Result: Best available players with proven reliability
Action: Target #1-3 on your waiver claims
```

### 3. "Trade Target Finder" Combo
```
Position: RB (your need)
Min Avg Points: 12+
Reliability: 65-80 (sort by avgScore desc)
Roster Status: All

Result: Productive RBs with medium reliability
Action: These are buy-low candidates (high output, low trust)
```

### 4. "Playoff Safe Plays" Combo
```
Min Games: 7+
Min Avg Points: 12+
Reliability: 85+
Roster Status: Rostered

Result: Your most trustworthy high-volume players
Action: Build playoff lineups around these players
```

### 5. "GPP Leverage Finder" Combo
```
Min Avg Points: 10+
Reliability: 50-70
Min Games: 5+
Roster Status: Available or All

Result: Productive players experts struggle to project
Action: Low ownership GPP plays with boom potential
```

### 6. "Position Comparison" Combo
```
Position: TE (or QB)
Min Games: 5+
Sort by: Reliability (desc)

Result: See which TEs have most reliable projections
Action: Use for streaming decisions or identifying positional advantages
```

### 7. "Deep Sleeper Hunter" Combo
```
Roster Status: Available
Min Avg Points: 5+
Min Games: 3+ (include emerging players)
Reliability: 75+ (but low ownership)
Sort by: avgDiff (negative bias)

Result: Low-rostered players who beat projections
Action: Stash before others notice
```

### 8. "Sell High Identifier" Combo
```
Roster Status: Rostered
Min Avg Points: 12+
Reliability: <65
Sort by: avgDiff (most positive)

Result: Your players who consistently underperform projections
Action: Sell before others catch on
```

---

## 🎯 Real-World Examples

### Example 1: Week 8 Start/Sit (WR3)

**Question:** Jordan Addison or Terry McLaurin?

**Filters:**
```
Position: WR
Roster Status: Rostered
Search: "addison" → note his reliability
Search: "mclaurin" → compare
```

**Results:**
```
Jordan Addison:  🟡 86 reliability, 13.2 PPG
Terry McLaurin:  🟠 68 reliability, 12.1 PPG
```

**Decision:** Start Addison (higher reliability + higher PPG)

---

### Example 2: Waiver Wire Priority (Week 9)

**Question:** Who should I prioritize on waivers?

**Filters:**
```
Roster Status: Available
Min Avg Points: 8+
Min Games: 5+
Sort by: Reliability (desc)
```

**Results:**
```
1. Player A: 🟡 82 reliability, 10.8 PPG, RB
2. Player B: 🟡 79 reliability, 11.2 PPG, WR
3. Player C: 🟠 71 reliability, 12.4 PPG, WR
```

**Decision:** Claim A if you need RB, B if you need WR
- Player C has higher PPG but lower reliability (more risk)

---

### Example 3: Playoff Prep (Week 12)

**Question:** Which of my players are "safe" for playoffs?

**Filters:**
```
Roster Status: Rostered
Min Games: 7+
Min Avg Points: 10+
Reliability: 80+
```

**Results:**
```
Safe players to build around:
- Breece Hall (🟢 94, 16.2 PPG)
- Ladd McConkey (🟢 97, 14.6 PPG)
- Travis Etienne (🟡 83, 14.8 PPG)

Risky players to consider replacing:
- Terry McLaurin (🟠 68, 12.1 PPG)
- Evan Engram (🔴 44, 9.8 PPG)
```

**Decision:** Look to trade or bench risky players in playoffs

---

### Example 4: Streaming QB (Week 10)

**Question:** Need a bye week fill-in at QB

**Filters:**
```
Position: QB
Roster Status: Available
Min Games: 5+
Min Avg Points: 15+
Sort by: Reliability (desc)
```

**Results:**
```
1. Sam Darnold: 🟡 78 reliability, 17.2 PPG
2. Geno Smith: 🟠 69 reliability, 16.8 PPG
3. Derek Carr: 🟠 65 reliability, 15.9 PPG
```

**Decision:** Stream Darnold (best reliability + PPG combo)

---

### Example 5: Trade Analysis

**Question:** Should I trade for high-upside WR?

**Filters:**
```
Position: WR
Min Avg Points: 12+
Reliability: <70 (volatile)
Roster Status: All
Sort by: avgScore (desc)
```

**Results:**
```
Players with high output but low reliability:
- Player X: 15.8 PPG, 58 reliability
- Player Y: 14.2 PPG, 62 reliability
- Player Z: 13.9 PPG, 67 reliability
```

**Decision:** 
- If you're leading league → avoid (too risky)
- If you need upside → target X or Y (boom potential)

---

## 🎨 Visual Elements

### Top 20 Cards

**Elite (90+):**
- Green border (#2ecc71)
- Green background glow
- 🟢 Badge

**Good (75-89):**
- Yellow border (#f1c40f)  
- Yellow background glow
- 🟡 Badge

**Fair (60-74):**
- Orange border (#e67e22)
- Orange background glow
- 🟠 Badge

### Position Badges

- **QB:** Blue (#3498db)
- **RB:** Red (#e74c3c)
- **WR:** Purple (#9b59b6)
- **TE:** Teal (#16a085)

### Roster Stars

- **⭐:** Player is on your roster (both in Top 20 and table)

---

## 📊 Filter State Persistence

**Note:** Filters reset when you:
- Navigate to another tab and back
- Refresh the page
- Close the dashboard

**Best practice:** Bookmark common filter combinations in a note or document for quick access!

---

## 🚀 Advanced Strategies

### Strategy 1: "Consistency Mining"
```
Goal: Find consistent performers for Cash games
Filters:
  - Min Games: 7+
  - Min Avg Points: 12+
  - Reliability: 85+
  - Consistency: 85%+ (check table)
Sort by: Consistency (desc)
```

### Strategy 2: "Upside Hunting"
```
Goal: GPP leverage with boom potential
Filters:
  - Min Avg Points: 10+
  - Reliability: 55-70
  - Min Games: 5+
  - Roster Status: Available
Sort by: avgScore (desc)
Look for: High ceiling despite low reliability
```

### Strategy 3: "Buy-Low Targets"
```
Goal: Trade for undervalued players
Filters:
  - Min Avg Points: 12+
  - Bias: Negative (sort by avgDiff asc)
  - Reliability: 75+
  - Roster Status: All
Interpretation: These beat projections consistently
```

### Strategy 4: "Sell-High Targets"
```
Goal: Trade away overvalued players
Filters:
  - Roster Status: Rostered
  - Min Avg Points: 10+
  - Bias: Most positive (sort by avgDiff desc)
  - Reliability: 65+
Interpretation: These consistently underperform expectations
```

---

## 🎯 The Bottom Line

The new filtering system gives you:

1. **Precise Control** → Find exactly the players you need
2. **Multi-Dimensional Analysis** → Combine 5+ filters simultaneously
3. **Visual Top 20** → See the most reliable players at-a-glance
4. **Waiver Wire Power** → Roster status filter for adds/drops
5. **Real-Time Search** → Find any player instantly

It's your **complete reliability analysis workstation** - from league-wide overview (Top 20) to laser-focused player lookup! 🎯

---

**Pro Tip:** Start each week by checking the Top 20 to see if any of your starters have dropped in reliability, then use the filters to find better alternatives!

# CSS FOR SORTING + FIX FOR HISTORICAL TAB

## 1. ADD THIS CSS (in the `<style>` section)

```css
/* ==================== SORTABLE TABLE STYLES ==================== */

th {{
  cursor: pointer;
  user-select: none;
  position: relative;
  transition: background 0.2s ease;
}}

th:hover {{
  background: rgba(255,255,255,0.1) !important;
}}

th.sorted-asc,
th.sorted-desc {{
  background: rgba(102, 126, 234, 0.3) !important;
  font-weight: 700;
}}

.sort-arrow {{
  color: #4CAF50;
  font-size: 11px;
  margin-left: 4px;
  font-weight: bold;
}}

/* Make sure table headers are visible */
thead th {{
  position: sticky;
  top: 0;
  background: #1a2332;
  z-index: 10;
  padding: 12px 8px;
}}
```

## 2. FIX FOR HISTORICAL TAB

The issue in your screenshot is that the Historical tab is showing **positional baseline data** instead of **individual player data**.

The table shows "QB Historical Averages (Top 24)" with ranks 1-24, which are the ECR rank baselines, NOT individual players.

### Find the Historical Tab Rendering Code

Look for where the Historical tab content is generated. It's probably around line 890-920. You should see something like:

**WRONG CODE (what you have now):**
```javascript
<!-- Historical Tab -->
<div id="historical" class="tab-content">
  <h3>QB Historical Averages (Top 24)</h3>
  <table>
    <thead>
      <tr>
        <th>Rank</th>
        <th>2022</th>
        <th>2023</th>
        <th>2024</th>
        <th>3-Yr Avg</th>
      </tr>
    </thead>
    <tbody id="historicalBody"></tbody>
  </table>
</div>
```

This is showing the positional BASELINES table, not individual players!

### CORRECT HTML FOR HISTORICAL TAB

```html
<!-- Historical Tab -->
<div id="historical" class="tab-content">
  <h3>📊 Player Historical Reliability</h3>
  <p style="color: #a0aec0; margin-bottom: 15px;">
    Shows players with 5+ games of historical ECR data. Higher correlation = more reliable projections.
  </p>
  
  <div class="table-container">
    <table id="historicalTable">
      <thead>
        <tr>
          <th data-column="player" onclick="sortTable('historical', 'player', 'string')" style="cursor: pointer;">Player</th>
          <th data-column="pos" onclick="sortTable('historical', 'pos', 'string')" style="cursor: pointer;">Pos</th>
          <th data-column="games" onclick="sortTable('historical', 'games', 'number')" style="cursor: pointer;">Games</th>
          <th data-column="correlation" onclick="sortTable('historical', 'correlation', 'number')" style="cursor: pointer;">Correlation</th>
          <th data-column="mae" onclick="sortTable('historical', 'mae', 'number')" style="cursor: pointer;">MAE</th>
          <th data-column="avgScore" onclick="sortTable('historical', 'avgScore', 'number')" style="cursor: pointer;">Avg Score</th>
        </tr>
      </thead>
      <tbody></tbody>
    </table>
  </div>
</div>
```

### CORRECT JAVASCRIPT FOR HISTORICAL TAB

Add this `renderHistoricalTable()` function:

```javascript
function renderHistoricalTable() {{
  // Get all players with historical data (5+ games)
  let data = Object.entries(FP_ACCURACY)
    .filter(([name, acc]) => acc.games >= 5)
    .map(([name, acc]) => ({{
      player: name,
      pos: PROJECTIONS.find(p => p.p === name)?.pos || '?',
      games: acc.games,
      correlation: acc.correlation,
      mae: acc.mae,
      avgScore: acc.avgScore
    }}));
  
  // Apply sorting
  data = applySorting(data, 'historical');
  
  const tbody = document.getElementById('historicalTable').querySelector('tbody');
  if (!tbody) {{
    console.warn('Historical table tbody not found');
    return;
  }}
  
  tbody.innerHTML = data.map(p => {{
    // Color code by correlation strength
    let corrClass = 'low-acc';
    if (p.correlation >= 0.7) corrClass = 'high-acc';
    else if (p.correlation >= 0.5) corrClass = 'med-acc';
    
    return `
      <tr class="pos-${{p.pos}}">
        <td><strong>${{p.player}}</strong></td>
        <td>${{p.pos}}</td>
        <td>${{p.games}}</td>
        <td class="${{corrClass}}">
          ${{(p.correlation * 100).toFixed(0)}}%
        </td>
        <td>${{p.mae.toFixed(1)}}</td>
        <td>${{p.avgScore.toFixed(1)}}</td>
      </tr>
    `;
  }}).join('');
  
  console.log('✅ Historical table rendered with', data.length, 'players');
}}
```

### Make sure it's called on page load:

In your initialization code (around line 1820-1830), add:

```javascript
// Initialize all tables
calculateFPAccuracy();
PROJECTIONS = calculateProjections();
updateMetrics();
renderProjectionsTable();
renderReliabilityTable();
renderRankingsTable('QB');
renderWaiverTable();
renderHistoricalTable();  // ← ADD THIS LINE
```

## 3. REMOVE OLD BASELINE TABLE (if it exists)

If you have code that renders the "QB Historical Averages" table with positional baselines, you can either:
- Delete it entirely
- Move it to a separate "Positional Baselines" tab
- Keep it but rename the tab to avoid confusion

The baselines are useful for debugging but shouldn't be in the "Historical" tab since users expect to see PLAYER data there.

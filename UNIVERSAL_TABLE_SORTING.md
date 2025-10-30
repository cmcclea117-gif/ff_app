# Universal Table Sorting for Fantasy Trust

Add this JavaScript code to your dashboard to enable sorting on ALL tables.

## 📋 Step 1: Add Universal Sorting Function

Add this AFTER your utility functions (after `normalizePlayerName`, etc.):

```javascript
// ==================== UNIVERSAL TABLE SORTING ====================

let sortState = {{
  projections: {{ column: 'proj', direction: 'desc' }},
  reliability: {{ column: 'correlation', direction: 'desc' }},
  rankings: {{ column: 'rank', direction: 'asc' }},
  waiver: {{ column: 'proj', direction: 'desc' }},
  matchups: {{ column: 'proj', direction: 'desc' }},
  historical: {{ column: 'player', direction: 'asc' }}
}};

function sortTable(tableId, column, type = 'number') {{
  const state = sortState[tableId];
  
  // Toggle direction if same column
  if (state.column === column) {{
    state.direction = state.direction === 'asc' ? 'desc' : 'asc';
  }} else {{
    state.column = column;
    state.direction = type === 'number' ? 'desc' : 'asc';
  }}
  
  // Update visual indicators
  updateSortIndicators(tableId, column, state.direction);
  
  // Trigger re-render for each table type
  switch(tableId) {{
    case 'projections':
      renderProjectionsTable();
      break;
    case 'reliability':
      renderReliabilityTable();
      break;
    case 'rankings':
      renderRankingsTable(currentRankingsPosition || 'QB');
      break;
    case 'waiver':
      renderWaiverTable();
      break;
    case 'matchups':
      renderMatchupsTable();
      break;
    case 'historical':
      renderHistoricalTable();
      break;
  }}
}}

function updateSortIndicators(tableId, column, direction) {{
  const table = document.getElementById(`${{tableId}}Table`);
  if (!table) return;
  
  // Remove all existing indicators
  table.querySelectorAll('th').forEach(th => {{
    th.classList.remove('sorted-asc', 'sorted-desc');
    const arrow = th.querySelector('.sort-arrow');
    if (arrow) arrow.remove();
  }});
  
  // Add indicator to sorted column
  const headers = Array.from(table.querySelectorAll('th'));
  const targetHeader = headers.find(th => th.dataset.column === column);
  
  if (targetHeader) {{
    targetHeader.classList.add(`sorted-${{direction}}`);
    const arrow = document.createElement('span');
    arrow.className = 'sort-arrow';
    arrow.textContent = direction === 'asc' ? ' ▲' : ' ▼';
    targetHeader.appendChild(arrow);
  }}
}}

function applySorting(data, tableId) {{
  const state = sortState[tableId];
  if (!state) return data;
  
  return [...data].sort((a, b) => {{
    let aVal = a[state.column];
    let bVal = b[state.column];
    
    // Handle null/undefined
    if (aVal == null) return 1;
    if (bVal == null) return -1;
    
    // Handle strings vs numbers
    if (typeof aVal === 'string') {{
      aVal = aVal.toLowerCase();
      bVal = bVal.toLowerCase();
    }}
    
    // Compare
    let result = 0;
    if (aVal < bVal) result = -1;
    if (aVal > bVal) result = 1;
    
    // Apply direction
    return state.direction === 'asc' ? result : -result;
  }});
}}

// ==================== END UNIVERSAL SORTING ====================
```

## 📋 Step 2: Update HTML Table Headers

Add `data-column` attributes and `onclick` handlers to ALL table headers:

### Projections Table Headers:
```html
<thead>
  <tr>
    <th data-column="p" onclick="sortTable('projections', 'p', 'string')">Player</th>
    <th data-column="pos" onclick="sortTable('projections', 'pos', 'string')">Pos</th>
    <th data-column="rank" onclick="sortTable('projections', 'rank', 'number')">Rank</th>
    <th data-column="proj" onclick="sortTable('projections', 'proj', 'number')">Week {nw} Proj</th>
    <th data-column="floor" onclick="sortTable('projections', 'floor', 'number')">Floor-Ceiling</th>
    <th data-column="tier" onclick="sortTable('projections', 'tier', 'string')">Tier</th>
    <th data-column="correlation" onclick="sortTable('projections', 'correlation', 'number')">FP Acc</th>
    <th data-column="avgDiff" onclick="sortTable('projections', 'avgDiff', 'number')">Trend</th>
  </tr>
</thead>
```

### Reliability Table Headers (already has sorting, just update):
```html
<thead>
  <tr>
    <th data-column="player" onclick="sortTable('reliability', 'player', 'string')">Player</th>
    <th data-column="pos" onclick="sortTable('reliability', 'pos', 'string')">Pos</th>
    <th data-column="games" onclick="sortTable('reliability', 'games', 'number')">Games</th>
    <th data-column="correlation" onclick="sortTable('reliability', 'correlation', 'number')">FP Accuracy</th>
    <th data-column="mae" onclick="sortTable('reliability', 'mae', 'number')">MAE</th>
    <th data-column="accuracy" onclick="sortTable('reliability', 'accuracy', 'number')">Within 3 Ranks %</th>
    <th data-column="avgScore" onclick="sortTable('reliability', 'avgScore', 'number')">Avg Score</th>
    <th data-column="avgDiff" onclick="sortTable('reliability', 'avgDiff', 'number')">Avg Diff</th>
  </tr>
</thead>
```

### Rankings Table Headers:
```html
<thead>
  <tr>
    <th data-column="rank" onclick="sortTable('rankings', 'rank', 'number')">Rank</th>
    <th data-column="p" onclick="sortTable('rankings', 'p', 'string')">Player</th>
    <th data-column="avgScore" onclick="sortTable('rankings', 'avgScore', 'number')">Avg Score</th>
    <th data-column="games" onclick="sortTable('rankings', 'games', 'number')">Games</th>
    <th data-column="correlation" onclick="sortTable('rankings', 'correlation', 'number')">FP Acc</th>
    <th data-column="proj" onclick="sortTable('rankings', 'proj', 'number')">Week {nw} Proj</th>
  </tr>
</thead>
```

### Waiver Table Headers:
```html
<thead>
  <tr>
    <th data-column="priority" onclick="sortTable('waiver', 'proj', 'number')">Priority</th>
    <th data-column="p" onclick="sortTable('waiver', 'p', 'string')">Player</th>
    <th data-column="pos" onclick="sortTable('waiver', 'pos', 'string')">Pos</th>
    <th data-column="proj" onclick="sortTable('waiver', 'proj', 'number')">Week {nw} Proj</th>
    <th data-column="tier" onclick="sortTable('waiver', 'tier', 'string')">Tier</th>
    <th data-column="avgDiff" onclick="sortTable('waiver', 'avgDiff', 'number')">Trend</th>
    <th data-column="correlation" onclick="sortTable('waiver', 'correlation', 'number')">FP Acc</th>
  </tr>
</thead>
```

### Historical Table Headers:
```html
<thead>
  <tr>
    <th data-column="player" onclick="sortTable('historical', 'player', 'string')">Player</th>
    <th data-column="pos" onclick="sortTable('historical', 'pos', 'string')">Pos</th>
    <th data-column="games" onclick="sortTable('historical', 'games', 'number')">Games</th>
    <th data-column="correlation" onclick="sortTable('historical', 'correlation', 'number')">Correlation</th>
    <th data-column="mae" onclick="sortTable('historical', 'mae', 'number')">MAE</th>
    <th data-column="avgScore" onclick="sortTable('historical', 'avgScore', 'number')">Avg Score</th>
  </tr>
</thead>
```

## 📋 Step 3: Update Each Render Function

Add sorting before rendering. Example for `renderProjectionsTable`:

```javascript
function renderProjectionsTable() {{
  // Get filtered data
  let filtered = PROJECTIONS.filter(p => {{
    // ... your existing filters
  }});
  
  // Apply sorting
  filtered = applySorting(filtered, 'projections');
  
  // Render rows
  const tbody = document.getElementById('projectionsTable').querySelector('tbody');
  tbody.innerHTML = filtered.map(p => {{
    // ... your existing rendering
  }}).join('');
}}
```

## 📋 Step 4: Add CSS for Sort Indicators

```css
th {{
  cursor: pointer;
  user-select: none;
  position: relative;
}}

th:hover {{
  background: rgba(255,255,255,0.1);
}}

th.sorted-asc,
th.sorted-desc {{
  background: rgba(255,255,255,0.15);
  font-weight: 700;
}}

.sort-arrow {{
  color: #4CAF50;
  font-size: 12px;
  margin-left: 4px;
}}
```

## 🎯 Result:

After these changes, EVERY table will:
- ✅ Have clickable headers
- ✅ Show arrow indicators (▲/▼)
- ✅ Toggle between ascending/descending
- ✅ Highlight the sorted column
- ✅ Remember sort state per table

Try it out! Click any column header to sort. 🚀

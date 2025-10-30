# UPDATED RENDER FUNCTIONS WITH SORTING

## 1. renderProjectionsTable() - Add sorting after filtering

Find your `renderProjectionsTable()` function and add sorting before rendering:

```javascript
function renderProjectionsTable() {{
  const posFilter = document.getElementById('positionFilter').value;
  const rosterFilter = document.getElementById('rosterFilter').value;
  const searchTerm = document.getElementById('searchBox').value.toLowerCase();
  
  let filtered = PROJECTIONS.filter(p => {{
    if (posFilter !== 'ALL' && p.pos !== posFilter) return false;
    if (rosterFilter === 'MY_ROSTER' && !isOnRoster(p.p)) return false;
    if (rosterFilter === 'AVAILABLE' && isRostered(p.p)) return false;
    if (searchTerm && !p.p.toLowerCase().includes(searchTerm)) return false;
    return true;
  }});
  
  // ✅ APPLY SORTING
  filtered = applySorting(filtered, 'projections');
  
  const tbody = document.getElementById('projectionsTable').querySelector('tbody');
  tbody.innerHTML = filtered.map(p => {{
    const rowClass = isOnRoster(p.p) ? 'my-roster' : isRostered(p.p) ? 'rostered' : '';
    const fpAccDisplay = p.hasECR && p.correlation !== 0 ? `${{(p.correlation * 100).toFixed(0)}}%` : '-';
    
    return `
      <tr class="${{rowClass}} pos-${{p.pos}}">
        <td><strong>${{p.p}}</strong></td>
        <td>${{p.pos}}</td>
        <td>${{p.rank}}</td>
        <td><strong>${{p.proj.toFixed(1)}}</strong></td>
        <td>${{p.floor.toFixed(1)}} - ${{p.ceiling.toFixed(1)}}</td>
        <td><span class="tier-badge tier-${{p.tier.toLowerCase()}}">${{p.tier}}</span></td>
        <td>${{fpAccDisplay}}</td>
        <td>${{getTrendIcon(p.avgDiff)}}</td>
      </tr>
    `;
  }}).join('');
}}
```

## 2. renderReliabilityTable() - Add sorting

```javascript
function renderReliabilityTable() {{
  let data = Object.entries(FP_ACCURACY).map(([name, acc]) => ({{
    player: name,
    pos: PROJECTIONS.find(p => p.p === name)?.pos || '?',
    games: acc.games,
    correlation: acc.correlation,
    mae: acc.mae,
    accuracy: acc.accuracy,
    avgScore: acc.avgScore,
    avgDiff: acc.avgDiff
  }}));
  
  // ✅ APPLY SORTING
  data = applySorting(data, 'reliability');
  
  const tbody = document.getElementById('reliabilityTable').querySelector('tbody');
  tbody.innerHTML = data.map(p => `
    <tr class="pos-${{p.pos}}">
      <td><strong>${{p.player}}</strong></td>
      <td>${{p.pos}}</td>
      <td>${{p.games}}</td>
      <td class="${{p.correlation >= 0.7 ? 'high-acc' : p.correlation >= 0.5 ? 'med-acc' : 'low-acc'}}">
        ${{(p.correlation * 100).toFixed(0)}}%
      </td>
      <td>${{p.mae.toFixed(1)}}</td>
      <td>${{(p.accuracy * 100).toFixed(0)}}%</td>
      <td>${{p.avgScore.toFixed(1)}}</td>
      <td class="${{p.avgDiff > 0 ? 'positive' : 'negative'}}">
        ${{p.avgDiff > 0 ? '+' : ''}}${{p.avgDiff.toFixed(1)}}
      </td>
    </tr>
  `).join('');
}}
```

## 3. renderRankingsTable() - Add sorting

```javascript
function renderRankingsTable(position) {{
  currentRankingsPosition = position; // Track for sorting
  
  document.querySelectorAll('.pos-btn').forEach(btn => btn.classList.remove('active'));
  const buttons = document.querySelectorAll('.pos-btn');
  buttons.forEach(btn => {{
    if (btn.textContent.includes(position)) {{
      btn.classList.add('active');
    }}
  }});
  
  const limits = {{ QB: 30, RB: 41, WR: 54, TE: 26 }};
  const limit = limits[position] || 30;
  
  let filtered = PROJECTIONS
    .filter(p => p.pos === position)
    .slice(0, limit);
  
  // ✅ APPLY SORTING
  filtered = applySorting(filtered, 'rankings');
  
  const tbody = document.getElementById('rankingsTable').querySelector('tbody');
  tbody.innerHTML = filtered.map(p => `
    <tr class="pos-${{p.pos}}">
      <td><strong>${{p.rank}}</strong></td>
      <td>${{p.p}}</td>
      <td>${{p.avgScore.toFixed(1)}}</td>
      <td>${{p.games}}</td>
      <td>${{p.correlation ? (p.correlation * 100).toFixed(0) + '%' : '-'}}</td>
      <td><strong>${{p.proj.toFixed(1)}}</strong></td>
    </tr>
  `).join('');
}}
```

## 4. renderWaiverTable() - Add sorting

```javascript
function renderWaiverTable() {{
  const minProj = parseFloat(document.getElementById('minProj').value) || 0;
  
  let available = PROJECTIONS
    .filter(p => !isRostered(p.p) && p.proj >= minProj)
    .slice(0, 50);
  
  // ✅ APPLY SORTING
  available = applySorting(available, 'waiver');
  
  const tbody = document.getElementById('waiverTable').querySelector('tbody');
  tbody.innerHTML = available.map((p, idx) => `
    <tr class="pos-${{p.pos}}">
      <td><strong>${{idx + 1}}</strong></td>
      <td>${{p.p}}</td>
      <td>${{p.pos}}</td>
      <td><strong>${{p.proj.toFixed(1)}}</strong></td>
      <td><span class="tier-badge tier-${{p.tier.toLowerCase()}}">${{p.tier}}</span></td>
      <td>${{getTrendIcon(p.avgDiff)}}</td>
      <td>${{p.correlation ? (p.correlation * 100).toFixed(0) + '%' : '-'}}</td>
    </tr>
  `).join('');
}}
```

## 5. renderHistoricalTable() - Add sorting

```javascript
function renderHistoricalTable() {{
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
  
  // ✅ APPLY SORTING
  data = applySorting(data, 'historical');
  
  const tbody = document.getElementById('historicalTable').querySelector('tbody');
  tbody.innerHTML = data.map(p => `
    <tr class="pos-${{p.pos}}">
      <td><strong>${{p.player}}</strong></td>
      <td>${{p.pos}}</td>
      <td>${{p.games}}</td>
      <td class="${{p.correlation >= 0.7 ? 'high-acc' : p.correlation >= 0.5 ? 'med-acc' : 'low-acc'}}">
        ${{(p.correlation * 100).toFixed(0)}}%
      </td>
      <td>${{p.mae.toFixed(1)}}</td>
      <td>${{p.avgScore.toFixed(1)}}</td>
    </tr>
  `).join('');
}}
```

## 6. renderMatchupsTable() - Add sorting (if exists)

```javascript
function renderMatchupsTable() {{
  // Your existing matchups logic here
  let matchups = []; // however you build this
  
  // ✅ APPLY SORTING
  matchups = applySorting(matchups, 'matchups');
  
  // Render as normal
}}
```

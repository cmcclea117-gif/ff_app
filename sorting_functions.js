// ==================== COMPLETE TABLE SORTING SYSTEM ====================
// Add this section after your utility functions (around line 1230)

let sortState = {{
  projections: {{ column: 'proj', direction: 'desc' }},
  reliability: {{ column: 'correlation', direction: 'desc' }},
  rankings: {{ column: 'rank', direction: 'asc' }},
  waiver: {{ column: 'proj', direction: 'desc' }},
  matchups: {{ column: 'proj', direction: 'desc' }},
  historical: {{ column: 'player', direction: 'asc' }}
}};

let currentRankingsPosition = 'QB'; // Track current position for rankings tab

function sortTable(tableId, column, type = 'number') {{
  const state = sortState[tableId];
  
  // Toggle direction if same column
  if (state.column === column) {{
    state.direction = state.direction === 'asc' ? 'desc' : 'asc';
  }} else {{
    state.column = column;
    state.direction = type === 'number' ? 'desc' : 'asc';
  }}
  
  console.log(`Sorting ${{tableId}} by ${{column}} (${{state.direction}})`);
  
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
      renderRankingsTable(currentRankingsPosition);
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
  if (!state || !data || data.length === 0) return data;
  
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

// ==================== END TABLE SORTING ====================

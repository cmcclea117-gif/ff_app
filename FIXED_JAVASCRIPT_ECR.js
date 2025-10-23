// ==================== COMPLETE FIXED JAVASCRIPT FOR ECR DASHBOARD ====================
// Replace everything from "// ==================== GLOBAL STATE ====================" 
// to "// ==================== INITIALIZATION ====================" with this code

// ==================== GLOBAL STATE ====================
let CURRENT_SCORING = 'PPR';
let FP_ACCURACY = {};
let PROJECTIONS = [];
let ALL_ROSTERED = new Set();
let USER_ROSTER = [];
let SLEEPER_DATA = null;

// ==================== UTILITY FUNCTIONS ====================
function normalizePlayerName(name) {
  return name.toLowerCase()
    .replace(/\s+(jr|sr|ii|iii|iv|v)\.?$/i, '')
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function pearsonCorrelation(x, y) {
  if (x.length !== y.length || x.length === 0) return 0;
  
  const n = x.length;
  const sumX = x.reduce((a, b) => a + b, 0);
  const sumY = y.reduce((a, b) => a + b, 0);
  const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0);
  const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0);
  const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0);
  
  const numerator = n * sumXY - sumX * sumY;
  const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY));
  
  return denominator === 0 ? 0 : numerator / denominator;
}

// ==================== NEW: Calculate Positional Baselines ====================
function calculatePositionalBaselines() {
  const baselines = {};
  
  ['QB', 'RB', 'WR', 'TE'].forEach(pos => {
    const historicalPlayers = HISTORICAL_DATA[CURRENT_SCORING]['2024'] || [];
    const posPlayers = historicalPlayers
      .filter(p => p.pos === pos)
      .map(p => {
        const weeks = Object.values(p.w);
        const avg = weeks.length > 0 ? weeks.reduce((a,b) => a+b, 0) / weeks.length : 0;
        return avg;
      })
      .filter(avg => avg > 0)
      .sort((a,b) => b - a);
    
    baselines[pos] = posPlayers.slice(0, 100);
  });
  
  console.log('Positional baselines:', { 
    QB: baselines.QB?.length, 
    RB: baselines.RB?.length, 
    WR: baselines.WR?.length, 
    TE: baselines.TE?.length 
  });
  
  return baselines;
}

// ==================== FIXED: Calculate FP Accuracy ====================
function calculateFPAccuracy() {
  FP_ACCURACY = {};
  
  if (!SEASON_2025 || !SEASON_2025.data) {
    console.log('No 2025 season data');
    return;
  }
  
  const seasonData = SEASON_2025.data;
  const weekNums = Object.keys(WEEKLY_PROJECTIONS).map(Number).sort((a,b) => a-b);
  
  console.log(`Checking ${seasonData.length} players against ${weekNums.length} weeks of ECR data`);
  
  let matchCount = 0;
  
  seasonData.forEach(player => {
    const name = player.p;
    const weeks = player.w;
    const pos = player.pos;
    
    if (!weeks || Object.keys(weeks).length < 3) return;
    
    const projectedRanks = [];
    const actualScores = [];
    const weekDetails = {};
    
    weekNums.forEach(weekNum => {
      if (weeks[weekNum] !== undefined) {
        const projData = WEEKLY_PROJECTIONS[weekNum];
        if (projData) {
          const normName = normalizePlayerName(name);
          const ecrEntry = projData.find(p => normalizePlayerName(p.p) === normName);
          
          // FIXED: Check for .ecr, not .proj
          if (ecrEntry && ecrEntry.ecr > 0) {
            projectedRanks.push(ecrEntry.ecr);
            actualScores.push(weeks[weekNum]);
            weekDetails[weekNum] = {
              ecrRank: ecrEntry.ecr,
              actual: weeks[weekNum]
            };
          }
        }
      }
    });
    
    if (projectedRanks.length >= 3) {
      matchCount++;
      
      // Convert actual scores to performance ranks
      const actualRanks = actualScores.map((score, idx) => {
        const sorted = [...actualScores].sort((a,b) => b - a);
        return sorted.indexOf(score) + 1;
      });
      
      const correlation = pearsonCorrelation(projectedRanks, actualRanks);
      const diffs = projectedRanks.map((r, i) => Math.abs(r - actualRanks[i]));
      const mae = diffs.reduce((a, b) => a + b, 0) / diffs.length;
      const within3 = diffs.filter(d => d <= 3).length / diffs.length;
      const avgDiff = projectedRanks.reduce((sum, r, i) => sum + (actualRanks[i] - r), 0) / projectedRanks.length;
      
      FP_ACCURACY[name] = {
        position: pos,
        games: projectedRanks.length,
        weeks: weekDetails,
        correlation: correlation,
        mae: mae,
        accuracy: within3,
        avgDiff: avgDiff
      };
    }
  });
  
  console.log(`FP Accuracy calculated for ${matchCount} players`);
}

// ==================== FIXED: Calculate Projections ====================
function calculateProjections() {
  if (!SEASON_2025 || !SEASON_2025.data) return [];
  
  const projections = [];
  const nextWeekECR = WEEKLY_PROJECTIONS[NEXT_WEEK] || [];
  const baselines = calculatePositionalBaselines();
  
  console.log(`Calculating projections with ${nextWeekECR.length} ECR entries for Week ${NEXT_WEEK}`);
  
  // Check first ECR entry structure
  if (nextWeekECR.length > 0) {
    console.log('Sample ECR entry:', nextWeekECR[0]);
  }
  
  SEASON_2025.data.forEach(player => {
    const name = player.p;
    const pos = player.pos;
    const weeks = player.w;
    
    if (!weeks || Object.keys(weeks).length === 0) return;
    
    const scores = Object.values(weeks);
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const games = scores.length;
    
    const normName = normalizePlayerName(name);
    const ecrData = nextWeekECR.find(p => normalizePlayerName(p.p) === normName);
    
    let proj = avgScore;
    let floor = avgScore * 0.7;
    let ceiling = avgScore * 1.3;
    let hasECR = false;
    let positionRank = 999;
    
    // FIXED: Check for .ecr field
    if (ecrData && ecrData.ecr > 0) {
      hasECR = true;
      positionRank = ecrData.ecr;
      
      // Convert ECR to points using baseline
      const posBaseline = baselines[pos] || [];
      const ecrIndex = Math.floor(ecrData.ecr) - 1;
      
      if (ecrIndex < posBaseline.length) {
        proj = posBaseline[ecrIndex];
      } else {
        const lastKnown = posBaseline[posBaseline.length - 1] || avgScore;
        const dropPerRank = 0.3;
        proj = lastKnown - (ecrIndex - posBaseline.length) * dropPerRank;
        proj = Math.max(proj, 3);
      }
      
      // Calculate floor/ceiling from std deviation
      const stdDev = ecrData.std || 5;
      floor = Math.max(proj - stdDev * 0.5, proj * 0.5);
      ceiling = proj + stdDev * 0.5;
      
      // Apply correlation adjustment
      const accuracy = FP_ACCURACY[name];
      if (accuracy && accuracy.games >= 3) {
        if (accuracy.correlation > 0.6) {
          const blendFactor = accuracy.correlation;
          proj = blendFactor * proj + (1 - blendFactor) * avgScore;
        }
        
        if (Math.abs(accuracy.avgDiff) > 2) {
          const adjustment = -accuracy.avgDiff * 0.5;
          proj += adjustment;
        }
      }
    }
    
    projections.push({
      p: name,
      pos: pos,
      proj: proj,
      floor: floor,
      ceiling: ceiling,
      avgScore: avgScore,
      games: games,
      hasECR: hasECR,
      ecrRank: positionRank,
      correlation: FP_ACCURACY[name]?.correlation || 0,
      mae: FP_ACCURACY[name]?.mae || 0,
      avgDiff: FP_ACCURACY[name]?.avgDiff || 0
    });
  });
  
  projections.sort((a, b) => b.proj - a.proj);
  
  const posCounts = { QB: 0, RB: 0, WR: 0, TE: 0 };
  projections.forEach(p => {
    posCounts[p.pos]++;
    p.rank = posCounts[p.pos];
    
    const rank = p.rank;
    if (p.pos === 'QB') {
      if (rank <= 6) p.tier = 'Elite';
      else if (rank <= 12) p.tier = 'High';
      else if (rank <= 24) p.tier = 'Mid';
      else p.tier = 'Stream';
    } else if (p.pos === 'RB') {
      if (rank <= 12) p.tier = 'Elite';
      else if (rank <= 24) p.tier = 'High';
      else if (rank <= 36) p.tier = 'Mid';
      else p.tier = 'Stream';
    } else if (p.pos === 'WR') {
      if (rank <= 12) p.tier = 'Elite';
      else if (rank <= 24) p.tier = 'High';
      else if (rank <= 36) p.tier = 'Mid';
      else p.tier = 'Stream';
    } else if (p.pos === 'TE') {
      if (rank <= 6) p.tier = 'Elite';
      else if (rank <= 12) p.tier = 'High';
      else if (rank <= 20) p.tier = 'Mid';
      else p.tier = 'Stream';
    }
  });
  
  console.log(`Generated ${projections.length} projections, ${projections.filter(p => p.hasECR).length} with ECR data`);
  
  return projections;
}

// ==================== RENDERING FUNCTIONS ====================
function updateMetrics() {
  const cards = [
    { label: 'Total Players', value: PROJECTIONS.length },
    { label: 'With FP Data', value: PROJECTIONS.filter(p => p.hasECR).length },
    { label: 'High Accuracy', value: Object.values(FP_ACCURACY).filter(a => a.correlation > 0.7).length },
    { label: 'My Roster', value: USER_ROSTER.length },
    { label: 'Available', value: PROJECTIONS.filter(p => !isRostered(p.p)).length }
  ];
  
  const html = cards.map(card => `
    <div class="stat-card">
      <h3>${card.label}</h3>
      <div class="value">${card.value}</div>
    </div>
  `).join('');
  
  document.getElementById('statsCards').innerHTML = html;
}

function renderProjectionsTable() {
  const posFilter = document.getElementById('posFilter').value;
  const rosterFilter = document.getElementById('rosterFilter').value;
  const searchTerm = document.getElementById('searchBox').value.toLowerCase();
  
  let filtered = PROJECTIONS.filter(p => {
    if (posFilter !== 'ALL' && p.pos !== posFilter) return false;
    if (rosterFilter === 'MY_ROSTER' && !isOnRoster(p.p)) return false;
    if (rosterFilter === 'AVAILABLE' && isRostered(p.p)) return false;
    if (searchTerm && !p.p.toLowerCase().includes(searchTerm)) return false;
    return true;
  });
  
  const tbody = document.getElementById('projectionsTable').querySelector('tbody');
  tbody.innerHTML = filtered.map(p => {
    const trend = p.avgDiff < -1 ? '📈' : p.avgDiff > 1 ? '📉' : '➡️';
    const trendClass = p.avgDiff < -1 ? 'trend-up' : p.avgDiff > 1 ? 'trend-down' : 'trend-stable';
    const roster = isOnRoster(p.p) ? '🏠' : '';
    const rowClass = isOnRoster(p.p) ? 'my-roster' : isRostered(p.p) ? 'rostered' : '';
    
    return `
      <tr class="pos-${p.pos} ${rowClass}">
        <td>${roster} ${p.p}</td>
        <td>${p.pos}</td>
        <td>${p.rank}</td>
        <td><strong>${p.proj.toFixed(1)}</strong></td>
        <td>${p.floor.toFixed(1)} - ${p.ceiling.toFixed(1)}</td>
        <td><span class="badge ${p.tier.toLowerCase()}">${p.tier}</span></td>
        <td>${p.hasECR ? (p.correlation * 100).toFixed(0) + '%' : '-'}</td>
        <td class="${trendClass}">${trend}</td>
      </tr>
    `;
  }).join('');
}

function renderReliabilityTable() {
  const data = Object.entries(FP_ACCURACY)
    .filter(([name, stats]) => stats.games >= 3)
    .map(([name, stats]) => ({ name, ...stats }))
    .sort((a, b) => b.correlation - a.correlation);
  
  const tbody = document.getElementById('reliabilityTable').querySelector('tbody');
  
  if (data.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;padding:40px;color:#95a5a6;">No reliability data available. ECR player names may not match 2025 results.</td></tr>';
    return;
  }
  
  tbody.innerHTML = data.map(p => {
    const playerData = SEASON_2025.data.find(pd => pd.p === p.name);
    let avgScore = 0;
    if (playerData && playerData.w) {
      const scores = Object.values(playerData.w);
      avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
    }
    
    const diffClass = p.avgDiff < 0 ? 'trend-up' : p.avgDiff > 0 ? 'trend-down' : 'trend-stable';
    const diffSymbol = p.avgDiff < -1 ? '✅' : p.avgDiff > 1 ? '❌' : '⚠️';
    
    return `
      <tr class="pos-${p.position}">
        <td>${p.name}</td>
        <td>${p.position}</td>
        <td>${p.games}</td>
        <td><strong>${(p.correlation * 100).toFixed(0)}%</strong></td>
        <td>${p.mae.toFixed(1)}</td>
        <td>${(p.accuracy * 100).toFixed(0)}%</td>
        <td>${avgScore.toFixed(1)}</td>
        <td class="${diffClass}">${p.avgDiff > 0 ? '+' : ''}${p.avgDiff.toFixed(1)} ${diffSymbol}</td>
      </tr>
    `;
  }).join('');
}

function renderRankingsTable(position) {
  document.querySelectorAll('.pos-btn').forEach(btn => btn.classList.remove('active'));
  const buttons = document.querySelectorAll('.pos-btn');
  buttons.forEach(btn => {
    if (btn.textContent.includes(position)) {
      btn.classList.add('active');
    }
  });
  
  const limits = { QB: 30, RB: 41, WR: 54, TE: 26 };
  const limit = limits[position] || 30;
  
  const filtered = PROJECTIONS
    .filter(p => p.pos === position)
    .slice(0, limit);
  
  const tbody = document.getElementById('rankingsTable').querySelector('tbody');
  tbody.innerHTML = filtered.map(p => `
    <tr class="pos-${p.pos}">
      <td><strong>${p.rank}</strong></td>
      <td>${p.p}</td>
      <td>${p.avgScore.toFixed(1)}</td>
      <td>${p.games}</td>
      <td>${p.hasECR ? (p.correlation * 100).toFixed(0) + '%' : '-'}</td>
      <td><strong>${p.proj.toFixed(1)}</strong></td>
    </tr>
  `).join('');
}

function renderWaiverTable() {
  const minProj = parseFloat(document.getElementById('minProj').value) || 0;
  
  const available = PROJECTIONS
    .filter(p => !isRostered(p.p) && p.proj >= minProj)
    .sort((a, b) => b.proj - a.proj)
    .slice(0, 30);
  
  const tbody = document.getElementById('waiverTable').querySelector('tbody');
  tbody.innerHTML = available.map((p, idx) => {
    const priority = idx < 5 ? '🔥' : idx < 15 ? '⭐' : '👀';
    const priorityClass = idx < 5 ? 'priority-hot' : idx < 15 ? 'priority-star' : 'priority-watch';
    const trend = p.avgDiff < -1 ? '📈' : p.avgDiff > 1 ? '📉' : '➡️';
    const trendClass = p.avgDiff < -1 ? 'trend-up' : p.avgDiff > 1 ? 'trend-down' : 'trend-stable';
    
    return `
      <tr class="pos-${p.pos}">
        <td class="${priorityClass}">${priority}</td>
        <td><strong>${p.p}</strong></td>
        <td>${p.pos}</td>
        <td><strong>${p.proj.toFixed(1)}</strong></td>
        <td><span class="badge ${p.tier.toLowerCase()}">${p.tier}</span></td>
        <td class="${trendClass}">${trend}</td>
        <td>${p.hasECR ? (p.correlation * 100).toFixed(0) + '%' : '-'}</td>
      </tr>
    `;
  }).join('');
}

function renderHistoricalTable() {
  const positions = ['QB', 'RB', 'WR', 'TE'];
  const container = document.getElementById('historicalTables');
  
  if (!container) {
    console.error('Historical tables container not found');
    return;
  }
  
  const html = positions.map(pos => {
    const posData = {};
    
    ['2022', '2023', '2024'].forEach(year => {
      const yearData = HISTORICAL_DATA[CURRENT_SCORING][year] || [];
      const posPlayers = yearData.filter(p => p.pos === pos);
      
      posPlayers.forEach((player, idx) => {
        const rank = idx + 1;
        if (rank > 24) return;
        
        const weeks = Object.values(player.w).filter(w => w > 0);
        if (weeks.length === 0) return;
        
        const avg = weeks.reduce((a, b) => a + b, 0) / weeks.length;
        
        if (!posData[rank]) posData[rank] = {};
        posData[rank][year] = avg;
      });
    });
    
    const rows = Object.entries(posData)
      .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
      .map(([rank, years]) => {
        const vals = Object.values(years);
        const avg3yr = vals.length > 0 ? vals.reduce((a,b) => a+b, 0) / vals.length : 0;
        
        return `
          <tr class="pos-${pos}">
            <td><strong>${rank}</strong></td>
            <td>${years['2022']?.toFixed(1) || '-'}</td>
            <td>${years['2023']?.toFixed(1) || '-'}</td>
            <td>${years['2024']?.toFixed(1) || '-'}</td>
            <td><strong>${avg3yr.toFixed(1)}</strong></td>
          </tr>
        `;
      }).join('');
    
    return `
      <div class="historical-section">
        <h3>${pos} Historical Averages (Top 24)</h3>
        <div class="table-container">
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
            <tbody>${rows}</tbody>
          </table>
        </div>
      </div>
    `;
  }).join('');
  
  container.innerHTML = html;
}

// ==================== SLEEPER INTEGRATION (rest of code unchanged) ====================
// ... (keep all the Sleeper functions as they were)

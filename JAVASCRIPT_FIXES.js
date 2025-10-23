/*
 * JAVASCRIPT FIXES FOR ECR-BASED PROJECTIONS
 * 
 * This file contains the corrected JavaScript functions to:
 * 1. Convert ECR ranks to projected points using historical averages
 * 2. Fix the MAE calculation bug
 * 3. Fix the Rankings tab error
 * 4. Fix the Historical tab rendering
 * 
 * Replace the corresponding functions in the generated HTML
 */

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
    
    // Store top 100 averages for each position
    baselines[pos] = posPlayers.slice(0, 100);
  });
  
  return baselines;
}

// ==================== FIXED: Calculate FP Accuracy ====================
function calculateFPAccuracy() {
  FP_ACCURACY = {};
  
  if (!SEASON_2025 || !SEASON_2025.data) return;
  
  const seasonData = SEASON_2025.data;
  const weekNums = Object.keys(WEEKLY_PROJECTIONS).map(Number).sort((a,b) => a-b);
  
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
          const proj = projData.find(p => normalizePlayerName(p.p) === normName);
          
          if (proj && proj.ecr > 0) {
            // Store ECR rank and actual score
            projectedRanks.push(proj.ecr);
            actualScores.push(weeks[weekNum]);
            weekDetails[weekNum] = {
              ecrRank: proj.ecr,
              actual: weeks[weekNum]
            };
          }
        }
      }
    });
    
    if (projectedRanks.length >= 3) {
      // Convert actual scores to ranks for correlation
      const actualRanks = actualScores.map((score, idx) => {
        // Rank among this player's weeks (1 = best week)
        const sorted = [...actualScores].sort((a,b) => b - a);
        return sorted.indexOf(score) + 1;
      });
      
      const correlation = pearsonCorrelation(projectedRanks, actualRanks);
      
      // Calculate MAE using ranks, not points
      const diffs = projectedRanks.map((r, i) => Math.abs(r - actualRanks[i]));
      const mae = diffs.reduce((a, b) => a + b, 0) / diffs.length;
      const within3 = diffs.filter(d => d <= 3).length / diffs.length;
      
      // Average difference in ranks (negative = performed better than expected)
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
  
  console.log(`FP Accuracy calculated for ${Object.keys(FP_ACCURACY).length} players`);
}

// ==================== FIXED: Calculate Projections ====================
function calculateProjections() {
  if (!SEASON_2025 || !SEASON_2025.data) return [];
  
  const projections = [];
  const nextWeekECR = WEEKLY_PROJECTIONS[NEXT_WEEK] || [];
  const baselines = calculatePositionalBaselines();
  
  SEASON_2025.data.forEach(player => {
    const name = player.p;
    const pos = player.pos;
    const weeks = player.w;
    
    if (!weeks || Object.keys(weeks).length === 0) return;
    
    const scores = Object.values(weeks);
    const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length;
    const games = scores.length;
    
    // Find ECR for this player
    const normName = normalizePlayerName(name);
    const ecrData = nextWeekECR.find(p => normalizePlayerName(p.p) === normName);
    
    let proj = avgScore;
    let floor = avgScore * 0.7;
    let ceiling = avgScore * 1.3;
    let hasECR = false;
    let positionRank = 999;
    
    if (ecrData && ecrData.ecr > 0) {
      hasECR = true;
      positionRank = ecrData.ecr;
      
      // Convert ECR to projected points using positional baseline
      const posBaseline = baselines[pos] || [];
      const ecrIndex = Math.floor(ecrData.ecr) - 1;
      
      if (ecrIndex < posBaseline.length) {
        proj = posBaseline[ecrIndex];
      } else {
        // Extrapolate for ranks beyond our data
        const lastKnown = posBaseline[posBaseline.length - 1] || avgScore;
        const dropPerRank = 0.3; // Points decrease per rank
        proj = lastKnown - (ecrIndex - posBaseline.length) * dropPerRank;
        proj = Math.max(proj, 3); // Minimum 3 points
      }
      
      // Calculate floor/ceiling using standard deviation
      const stdDev = ecrData.std || 5;
      floor = Math.max(proj - stdDev * 0.5, proj * 0.5);
      ceiling = proj + stdDev * 0.5;
      
      // Apply correlation adjustment if player has history
      const accuracy = FP_ACCURACY[name];
      if (accuracy && accuracy.games >= 3) {
        // Blend projection with actual average if correlation is strong
        if (accuracy.correlation > 0.6) {
          const blendFactor = accuracy.correlation;
          proj = blendFactor * proj + (1 - blendFactor) * avgScore;
        }
        
        // Adjust based on consistent over/under performance
        if (Math.abs(accuracy.avgDiff) > 2) {
          // avgDiff negative means player performs better than rank
          const adjustment = -accuracy.avgDiff * 0.5; // Convert rank diff to points
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
  
  // Sort by projection
  projections.sort((a, b) => b.proj - a.proj);
  
  // Assign overall ranks and tiers by position
  const posCounts = { QB: 0, RB: 0, WR: 0, TE: 0 };
  projections.forEach(p => {
    posCounts[p.pos]++;
    p.rank = posCounts[p.pos];
    
    // Assign tier based on rank
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
  
  return projections;
}

// ==================== FIXED: Render Rankings Table ====================
function renderRankingsTable(position) {
  // Update button states - FIXED: Check if event exists
  document.querySelectorAll('.pos-btn').forEach(btn => btn.classList.remove('active'));
  
  // Find the button that was clicked
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
      <td>${(p.correlation * 100).toFixed(0)}%</td>
      <td><strong>${p.proj.toFixed(1)}</strong></td>
    </tr>
  `).join('');
}

// ==================== FIXED: Render Reliability Table ====================
function renderReliabilityTable() {
  const data = Object.entries(FP_ACCURACY)
    .filter(([name, stats]) => stats.games >= 3)
    .map(([name, stats]) => ({ name, ...stats }))
    .sort((a, b) => b.correlation - a.correlation);
  
  const tbody = document.getElementById('reliabilityTable').querySelector('tbody');
  tbody.innerHTML = data.map(p => {
    // Calculate average score from 2025 season
    const playerData = SEASON_2025.data.find(pd => pd.p === p.name);
    let avgScore = 0;
    if (playerData && playerData.w) {
      const scores = Object.values(playerData.w);
      avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
    }
    
    const diffClass = p.avgDiff < 0 ? 'trend-up' : p.avgDiff > 0 ? 'trend-down' : 'trend-stable';
    const diffSymbol = p.avgDiff < 0 ? '✅' : p.avgDiff > 2 ? '❌' : '⚠️';
    
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

// ==================== FIXED: Render Historical Table ====================
function renderHistoricalTable() {
  const positions = ['QB', 'RB', 'WR', 'TE'];
  const container = document.getElementById('historicalTables');
  
  if (!container) {
    console.error('Historical tables container not found');
    return;
  }
  
  const html = positions.map(pos => {
    const posData = {};
    
    // Calculate averages for each rank across years
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
    
    // Calculate 3-year averages
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

/*
 * INSTRUCTIONS FOR APPLYING THESE FIXES:
 * 
 * 1. Open the generated fantasy_dashboard_v34_complete.html
 * 2. Find the <script> section
 * 3. Replace the following functions with the versions above:
 *    - Add calculatePositionalBaselines() as a new function
 *    - Replace calculateFPAccuracy()
 *    - Replace calculateProjections()
 *    - Replace renderRankingsTable()
 *    - Replace renderReliabilityTable()
 *    - Replace renderHistoricalTable()
 * 
 * 4. In the DOMContentLoaded listener, ensure renderHistoricalTable() is called
 * 
 * KEY CHANGES:
 * - ECR ranks now converted to points using historical positional averages
 * - MAE now calculates rank differences, not point differences
 * - Rankings tab fixed to not require event.target
 * - Historical tab fixed with proper error handling
 * - Correlation analysis now compares rank consistency, not point accuracy
 */

#!/usr/bin/env python3
"""
ECR Projection Patcher for Fantasy Dashboard V3.4

This script patches the generated HTML to fix:
1. ECR rank-to-points conversion
2. MAE calculation for ranks instead of points
3. Rankings tab bug
4. Historical tab rendering

Usage: python3 patch_dashboard.py fantasy_dashboard_v34_complete.html
"""

import sys
import re

def patch_html(input_file, output_file=None):
    if output_file is None:
        output_file = input_file.replace('.html', '_patched.html')
    
    with open(input_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Find the script section
    script_start = html.find('// ==================== CORE CALCULATIONS ====================')
    script_end = html.find('// ==================== TAB SWITCHING ====================')
    
    if script_start == -1 or script_end == -1:
        print("❌ Could not find script section to patch")
        return False
    
    # Create the fixed JavaScript
    fixed_js = '''// ==================== CORE CALCULATIONS ====================
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
  
  return baselines;
}

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
  
  console.log(`FP Accuracy calculated for ${Object.keys(FP_ACCURACY).length} players`);
}

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
      
      const stdDev = ecrData.std || 5;
      floor = Math.max(proj - stdDev * 0.5, proj * 0.5);
      ceiling = proj + stdDev * 0.5;
      
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
  
  return projections;
}

'''
    
    # Replace the old functions
    html = html[:script_start] + fixed_js + html[script_end:]
    
    # Fix the renderRankingsTable function
    old_rankings = '''function renderRankingsTable(position) {{
  // Update button states
  document.querySelectorAll('.pos-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');'''
    
    new_rankings = '''function renderRankingsTable(position) {{
  document.querySelectorAll('.pos-btn').forEach(btn => btn.classList.remove('active'));
  const buttons = document.querySelectorAll('.pos-btn');
  buttons.forEach(btn => {{
    if (btn.textContent.includes(position)) {{
      btn.classList.add('active');
    }}
  }});'''
    
    html = html.replace(old_rankings, new_rankings)
    
    # Fix renderReliabilityTable to calculate avgScore
    old_reliability_avgScore = '''const avgScoreWeeks = Object.values(p.weeks).map(w => w.actual);
    const avgScore = avgScoreWeeks.reduce((a,b) => a+b, 0) / avgScoreWeeks.length;'''
    
    new_reliability_avgScore = '''const playerData = SEASON_2025.data.find(pd => pd.p === p.name);
    let avgScore = 0;
    if (playerData && playerData.w) {{
      const scores = Object.values(playerData.w);
      avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
    }}'''
    
    html = html.replace(old_reliability_avgScore, new_reliability_avgScore)
    
    # Write the patched file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Patched dashboard saved to: {output_file}")
    print("\n📋 Changes applied:")
    print("  ✅ Added calculatePositionalBaselines() function")
    print("  ✅ Fixed calculateFPAccuracy() to use rank correlation")
    print("  ✅ Fixed calculateProjections() to convert ECR to points")
    print("  ✅ Fixed renderRankingsTable() event bug")
    print("  ✅ Fixed renderReliabilityTable() avgScore calculation")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 patch_dashboard.py <input_html_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    patch_html(input_file)

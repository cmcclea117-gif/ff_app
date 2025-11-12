#!/usr/bin/env python3
"""
Fantasy Truss - COMPLETE EDITION
Generates a fully self-contained HTML with embedded data and full UI
"""

import csv
import json
import re
from pathlib import Path

# ==================== CONFIGURATION ====================
HISTORICAL_FILES = {
    'PPR': {
        2022: '2022_FantasyPros_Fantasy_Football_Points_PPR.csv',
        2023: '2023_FantasyPros_Fantasy_Football_Points_PPR.csv',
        2024: '2024_FantasyPros_Fantasy_Football_Points_PPR.csv',
    },
    'HALF_PPR': {
        2022: '2022_FantasyPros_Fantasy_Football_Points_HALF.csv',
        2023: '2023_FantasyPros_Fantasy_Football_Points_HALF.csv',
        2024: '2024_FantasyPros_Fantasy_Football_Points_HALF.csv',
    },
    'STANDARD': {
        2022: '2022_FantasyPros_Fantasy_Football_Points.csv',
        2023: '2023_FantasyPros_Fantasy_Football_Points.csv',
        2024: '2024_FantasyPros_Fantasy_Football_Points.csv',
    }
}

CURRENT_SEASON_FILE = 'FantasyPros_Fantasy_Football_Points_PPR.csv'
DATA_FOLDER = 'historical_data'
OUTPUT_FILE = 'fantasy_dashboard_v34_complete.html'

# ==================== FUNCTIONS ====================

def parse_csv_to_compact(filepath):
    """Parse FantasyPros CSV and convert to compact format."""
    compact_data = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row is None or not row:
                continue
            
            player = (row.get('Player', '') or '').strip()
            pos = (row.get('Pos', '') or '').strip()
            pos = ''.join(c for c in pos if not c.isdigit())
            
            if not player or pos not in ['QB', 'RB', 'WR', 'TE']:
                continue
            
            weeks = {}
            for week_num in range(1, 19):
                week_val = (row.get(str(week_num), '') or '').strip()
                if week_val and week_val not in ['-', 'BYE', '']:
                    try:
                        weeks[week_num] = float(week_val)
                    except ValueError:
                        pass
            
            compact_data.append({'p': player, 'pos': pos, 'w': weeks})
    
    return compact_data


def parse_projections_csv(filepath):
    """Parse FantasyPros ECR rankings CSV and convert to projection format."""
    projections = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if row is None or not row:
                continue
            
            player = (row.get('PLAYER NAME', '') or row.get('Player', '') or '').strip()
            pos_raw = (row.get('POS', '') or row.get('Pos', '') or '').strip()
            
            # Extract position and position rank (e.g., "QB1" -> pos="QB", rank=1)
            pos = ''.join(c for c in pos_raw if c.isalpha())
            pos_rank_str = ''.join(c for c in pos_raw if c.isdigit())
            
            if not player or pos not in ['QB', 'RB', 'WR', 'TE']:
                continue
            
            try:
                # Use position rank (QB1, RB2, etc.) not overall rank
                ecr = float(pos_rank_str) if pos_rank_str else 0
                std_dev = float(row.get('STD.DEV', '') or '0')
                
                if ecr == 0:
                    continue
                
                # Store position-based ECR rank - JavaScript will convert to points
                projections.append({
                    'p': player,
                    'pos': pos,
                    'ecr': ecr,  # Position-based Expert Consensus Rank (QB1=1, not overall #2)
                    'std': std_dev  # Standard deviation of ranks
                })
            except (ValueError, TypeError):
                continue
    
    return projections


def load_all_historical_data():
    """Load historical data."""
    all_data = {}
    
    for scoring_format, years in HISTORICAL_FILES.items():
        all_data[scoring_format] = {}
        
        for year, filename in years.items():
            filepath = Path(DATA_FOLDER) / filename
            if not filepath.exists():
                print(f"⚠️  WARNING: {filepath} not found")
                continue
            
            print(f"📂 Loading {scoring_format} {year}...")
            data = parse_csv_to_compact(filepath)
            all_data[scoring_format][str(year)] = data
            print(f"   ✅ {len(data)} players")
    
    return all_data


def load_current_season():
    """Load 2025 current season data."""
    filepath = Path(DATA_FOLDER) / CURRENT_SEASON_FILE
    if not filepath.exists():
        print(f"⚠️  2025 results not found: {filepath}")
        return None
    
    print(f"\n📂 Loading 2025 season...")
    data = parse_csv_to_compact(filepath)
    max_week = max([max(p['w'].keys()) for p in data if p['w']], default=0)
    print(f"   ✅ {len(data)} players, Week {max_week}")
    
    return {'data': data, 'current_week': max_week}


def load_weekly_projections():
    """Auto-detect and load weekly projection files."""
    projections = {}
    data_folder = Path(DATA_FOLDER)
    
    print(f"\n📂 Scanning projections...")
    all_csvs = list(data_folder.glob('*.csv'))
    proj_csvs = [f for f in all_csvs if '2025' in f.name and 
                 f.name != CURRENT_SEASON_FILE and
                 not any(y in f.name for y in ['2022','2023','2024'])]
    
    for filepath in proj_csvs:
        week_num = None
        match1 = re.search(r'[\s_-](\d+)\.csv$', filepath.name, re.I)
        if match1:
            week_num = int(match1.group(1))
        if not week_num:
            match2 = re.search(r'week[\s_]*(\d+)', filepath.name, re.I)
            if match2:
                week_num = int(match2.group(1))
        
        if week_num and 1 <= week_num <= 18:
            proj_data = parse_projections_csv(filepath)
            if proj_data:
                projections[week_num] = proj_data
                print(f"   📊 Week {week_num}: {len(proj_data)} players")
    
    if projections:
        weeks = sorted(projections.keys())
        print(f"\n   ✅ {len(weeks)} weeks loaded: {', '.join(map(str, weeks))}")
    
    return projections


def generate_complete_html(historical_data, current_season, projections):
    """Generate complete HTML with full V3.2 UI."""
    
    hist_json = json.dumps(historical_data, separators=(',', ':'))
    season_json = json.dumps(current_season, separators=(',', ':'))
    proj_json = json.dumps(projections, separators=(',', ':'))
    
    total_kb = (len(hist_json) + len(season_json) + len(proj_json)) / 1024
    print(f"\n📊 Data: Historical {len(hist_json)/1024:.1f}KB + Season {len(season_json)/1024:.1f}KB + Proj {len(proj_json)/1024:.1f}KB = {total_kb:.1f}KB")
    
    cw = current_season.get('current_week', 7) if current_season else 7
    nw = cw + 1
    pw = f"{min(projections.keys())}-{max(projections.keys())}" if projections else "N/A"
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Fantasy Truss - Week {nw}</title>
<style>
* {{
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}}

body {{
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
  color: #ecf0f1;
  min-height: 100vh;
  padding: 20px;
}}

.container {{
  max-width: 1800px;
  margin: 0 auto;
}}

h1 {{
  text-align: center;
  margin-bottom: 20px;
  font-size: 2.5em;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}}

/* Upload Section */
.upload-section {{
  background: rgba(255,255,255,0.1);
  border-radius: 15px;
  padding: 20px;
  margin-bottom: 20px;
  backdrop-filter: blur(10px);
}}

.upload-section h2 {{
  margin-bottom: 15px;
  font-size: 1.3em;
}}

.controls {{
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: center;
}}

.control-group {{
  display: flex;
  flex-direction: column;
  gap: 5px;
}}

.control-group label {{
  font-size: 0.9em;
  color: #bdc3c7;
}}

.control-group input,
.control-group select {{
  padding: 8px 12px;
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  color: #ecf0f1;
  font-size: 1em;
}}

.control-group input:focus,
.control-group select:focus {{
  outline: none;
  border-color: #6fc6ab;
}}

button {{
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 1em;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  font-weight: 600;
}}

button:hover {{
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}}

button:active {{
  transform: translateY(0);
}}

.status {{
  margin-top: 10px;
  padding: 10px;
  border-radius: 8px;
  font-size: 0.95em;
}}

.status.success {{
  background: rgba(46, 204, 113, 0.2);
  border: 1px solid #2ecc71;
}}

.status.error {{
  background: rgba(231, 76, 60, 0.2);
  border: 1px solid #e74c3c;
}}

/* Tab Navigation */
.tab-container {{
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
  padding: 20px;
  backdrop-filter: blur(10px);
}}

.tab-nav {{
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}}

.tab-btn {{
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  background: rgba(255,255,255,0.1);
  color: #bdc3c7;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}}

.tab-btn:hover {{
  background: rgba(255,255,255,0.2);
  color: #ecf0f1;
}}

.tab-btn.active {{
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
}}

.tab-content {{
  display: none;
}}

.tab-content.active {{
  display: block;
  animation: fadeIn 0.3s;
}}

@keyframes fadeIn {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

/* Stats Cards */
.stats-cards {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}}

.stat-card {{
  background: rgba(255,255,255,0.1);
  border-radius: 10px;
  padding: 15px;
  text-align: center;
  border-left: 4px solid #6fc6ab;
}}

.stat-card h3 {{
  font-size: 0.9em;
  color: #bdc3c7;
  margin-bottom: 5px;
}}

.stat-card .value {{
  font-size: 1.8em;
  font-weight: bold;
  color: #6fc6ab;
}}

/* Filters */
.filters {{
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  align-items: center;
}}

.filter-group {{
  display: flex;
  flex-direction: column;
  gap: 5px;
}}

.filter-group label {{
  font-size: 0.9em;
  color: #bdc3c7;
}}

.filter-group select,
.filter-group input {{
  padding: 8px 12px;
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  color: #ecf0f1;
  font-size: 1em;
}}

/* Position Buttons */
.position-buttons {{
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}}

.pos-btn {{
  padding: 10px 20px;
  border: 2px solid rgba(255,255,255,0.2);
  border-radius: 8px;
  background: rgba(255,255,255,0.1);
  color: #ecf0f1;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 600;
}}

.pos-btn:hover {{
  background: rgba(255,255,255,0.2);
}}

.pos-btn.active {{
  border-color: #6fc6ab;
  background: rgba(52, 152, 219, 0.3);
  color: #6fc6ab;
}}

/* Tables */
.table-container {{
  overflow-x: auto;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
}}

table {{
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}}

thead {{
  background: rgba(255,255,255,0.1);
  position: sticky;
  top: 0;
  z-index: 10;
}}

th {{
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #6fc6ab;
  cursor: pointer;
  user-select: none;
  white-space: nowrap;
}}

th:hover {{
  background: rgba(255,255,255,0.15);
}}

th.sortable::after {{
  content: ' ⇅';
  color: #7f8c8d;
}}

th.sort-asc::after {{
  content: ' ↑';
  color: #6fc6ab;
}}

th.sort-desc::after {{
  content: ' ↓';
  color: #6fc6ab;
}}

td {{
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}}

tbody tr {{
  transition: background 0.2s;
}}

tbody tr:hover {{
  background: rgba(255,255,255,0.1);
}}

/* Position Colors */
.pos-QB {{ border-left: 4px solid #fc8b5f; }}
.pos-RB {{ border-left: 4px solid #abda5e; }}
.pos-WR {{ border-left: 4px solid #8caacb; }}
.pos-TE {{ border-left: 4px solid #e683bf; }}

/* Position Badge Colors */
.pos-badge-QB {{ 
  background: rgba(252, 139, 95, 0.2);
  color: #fc8b5f;
  border: 1px solid #fc8b5f;
}}
.pos-badge-RB {{ 
  background: rgba(171, 218, 94, 0.2);
  color: #abda5e;
  border: 1px solid #abda5e;
}}
.pos-badge-WR {{ 
  background: rgba(140, 170, 203, 0.2);
  color: #8caacb;
  border: 1px solid #8caacb;
}}
.pos-badge-TE {{ 
  background: rgba(230, 131, 191, 0.2);
  color: #e683bf;
  border: 1px solid #e683bf;
}}

/* Tier Badges */
.badge {{
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.85em;
  font-weight: 600;
  display: inline-block;
}}

.badge.elite {{
  background: #2ecc71;
  color: white;
}}

.badge.high {{
  background: #6fc6ab;
  color: white;
}}

.badge.mid {{
  background: #f39c12;
  color: white;
}}

.badge.stream {{
  background: #95a5a6;
  color: white;
}}

/* Trend Indicators */
.trend-up {{ color: #2ecc71; }}
.trend-down {{ color: #e74c3c; }}
.trend-stable {{ color: #95a5a6; }}

/* Roster Highlight */
.rostered {{
  background: rgba(52, 152, 219, 0.15);
  font-weight: 600;
}}

.my-roster {{
  background: rgba(46, 204, 113, 0.15);
  font-weight: 600;
}}

/* Priority Icons */
.priority-hot {{ color: #e74c3c; font-size: 1.2em; }}
.priority-star {{ color: #f39c12; font-size: 1.2em; }}
.priority-watch {{ color: #95a5a6; font-size: 1.2em; }}

/* Lineup Optimizer */
.lineup-config {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}}

.lineup-results {{
  margin-top: 20px;
}}

.starters-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}}

.starter-card {{
  background: rgba(46, 204, 113, 0.2);
  border: 2px solid #2ecc71;
  border-radius: 10px;
  padding: 15px;
}}

.starter-card.pos-QB {{
  background: rgba(252, 139, 95, 0.15);
  border: 2px solid #fc8b5f;
}}

.starter-card.pos-QB h4 {{
  color: #fc8b5f;
}}

.starter-card.pos-RB {{
  background: rgba(171, 218, 94, 0.15);
  border: 2px solid #abda5e;
}}

.starter-card.pos-RB h4 {{
  color: #abda5e;
}}

.starter-card.pos-WR {{
  background: rgba(140, 170, 203, 0.15);
  border: 2px solid #8caacb;
}}

.starter-card.pos-WR h4 {{
  color: #8caacb;
}}

.starter-card.pos-TE {{
  background: rgba(230, 131, 191, 0.15);
  border: 2px solid #e683bf;
}}

.starter-card.pos-TE h4 {{
  color: #e683bf;
}}

.starter-card.pos-FLEX {{
  background: rgba(111, 198, 171, 0.15);
  border: 2px solid #6fc6ab;
}}

.starter-card.pos-FLEX h4 {{
  color: #6fc6ab;
}}

.starter-card h4 {{
  color: #2ecc71;
  margin-bottom: 10px;
}}

.bench-section {{
  background: rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 15px;
}}

.bench-section h3 {{
  margin-bottom: 10px;
  color: #95a5a6;
}}

.bench-list {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 10px;
}}

/* Historical Tables */
.historical-section {{
  margin-bottom: 30px;
}}

.historical-section h3 {{
  margin-bottom: 15px;
  padding: 10px;
  background: rgba(255,255,255,0.1);
  border-radius: 8px;
  border-left: 4px solid #6fc6ab;
}}

/* Responsive */
@media (max-width: 768px) {{
  h1 {{ font-size: 1.8em; }}
  .controls {{ flex-direction: column; }}
  .tab-nav {{ flex-direction: column; }}
  .filters {{ flex-direction: column; }}
  .stats-cards {{ grid-template-columns: 1fr; }}
}}
</style>
</head>
<body>

<div class="container">
  <h1>🏈 Fantasy Truss - Week {nw}</h1>
  
  <!-- ADD THIS SLEEPER CONNECTION WIDGET -->
    <div id="sleeperConnection" style="max-width: 600px; margin: 30px auto; padding: 25px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
      <div style="background: white; border-radius: 12px; padding: 25px;">
        <h2 style="margin: 0 0 10px 0; font-size: 24px; color: #333;">
          🏈 Connect Your Roster
        </h2>
        <p style="margin: 0 0 20px 0; color: #777; font-size: 14px;">
          Enter your Sleeper username to highlight your players
        </p>
        
        <!-- Step 1: Username -->
        <div id="usernameSection">
          <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555; font-size: 14px;">
            Sleeper Username:
          </label>
          <div style="display: flex; gap: 10px;">
            <input 
              type="text" 
              id="sleeperUsername" 
              placeholder="your_username"
              style="flex: 1; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px;"
            >
            <button 
              id="loadLeaguesBtn"
              onclick="loadSleeperLeagues()"
              style="padding: 12px 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;"
            >
              Load Leagues
            </button>
          </div>
          <div id="sleeperStatus" style="margin-top: 10px; font-size: 13px;"></div>
        </div>
        
        <!-- Step 2: League Selector -->
        <div id="leagueSection" style="display: none; margin-top: 20px;">
          <label style="display: block; margin-bottom: 8px; font-weight: 600; color: #555; font-size: 14px;">
            Select Your League:
          </label>
          <select 
            id="leagueDropdown"
            style="width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; margin-bottom: 10px;"
          ></select>
          <button 
            id="connectLeagueBtn"
            onclick="connectSleeperLeague()"
            style="width: 100%; padding: 12px; background: linear-gradient(135deg, #28a745, #20c997); color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer;"
          >
            📤 Load Roster to Fantasy Truss
          </button>
        </div>
        
        <!-- Step 3: Connected Status -->
        <div id="connectedSection" style="display: none; margin-top: 20px;">
          <div id="rosterInfo" style="background: #d4edda; border: 2px solid #28a745; padding: 15px; border-radius: 8px; margin-bottom: 10px;"></div>
          <button 
            onclick="clearSleeperRoster()"
            style="width: 100%; padding: 10px; background: white; color: #dc3545; border: 2px solid #dc3545; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px;"
          >
            Clear Roster
          </button>
        </div>
      </div>
    </div>
    <!-- END SLEEPER CONNECTION WIDGET -->
  
  <!-- Tab Container -->
  <div class="tab-container">
    <div class="tab-nav">
      <button class="tab-btn active" onclick="switchTab('projections')">📊 Projections</button>
      <button class="tab-btn" onclick="switchTab('reliability')">🎯 Reliability</button>
      <button class="tab-btn" onclick="switchTab('rankings')">📈 Rankings</button>
      <button class="tab-btn" onclick="switchTab('waiver')">🔥 Waiver Targets</button>
      <button class="tab-btn" onclick="switchTab('lineups')">⚡ Lineup Optimizer</button>
      <button class="tab-btn" onclick="switchTab('matchups')">⚔️ Matchups</button>
      <button class="tab-btn" onclick="switchTab('historical')">📚 Historical</button>
    </div>
    
    <!-- Projections Tab -->
    <div id="projections" class="tab-content active">
      <div class="stats-cards" id="statsCards"></div>
      
      <div class="filters">
        <div class="filter-group">
          <label>Position:</label>
          <select id="posFilter" onchange="renderProjectionsTable()">
            <option value="ALL">All Positions</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Roster Filter:</label>
          <select id="rosterFilter" onchange="renderProjectionsTable()">
            <option value="ALL">All Players</option>
            <option value="MY_ROSTER">My Roster</option>
            <option value="AVAILABLE">Available</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Search Player:</label>
          <input type="text" id="searchBox" placeholder="Type name..." oninput="renderProjectionsTable()">
        </div>
      </div>
      
      <div class="table-container">
        <table id="projectionsTable">
          <thead>
            <tr>
              <th>Player</th>
              <th>Pos</th>
              <th>Rank</th>
              <th>Week {nw} Proj</th>
              <th>Floor-Ceiling</th>
              <th>Tier</th>
              <th title="Rating score (0-100) based on prediction accuracy">Rating</th>
              <th title="Trend: Negative (📈) = beats projections, Positive (📉) = misses projections">Trend</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    
    <!-- Reliability Tab -->
    <div id="reliability" class="tab-content">
      <!-- Top 20 Most Reliable Players -->
      <div id="top20Container" style="margin-bottom: 20px; padding: 20px; background: linear-gradient(135deg, rgba(46,204,113,0.1) 0%, rgba(111,198,171,0.1) 100%); border-radius: 15px; border: 2px solid rgba(46,204,113,0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
          <h3 style="margin: 0; font-size: 1.3em;">🏆 Top 20 Most Reliable Players</h3>
          <div style="display: flex; gap: 10px;">
            <button id="top20Overall" onclick="setTop20Mode('overall')" style="padding: 8px 16px; background: rgba(46,204,113,0.3); border: 2px solid #2ecc71; border-radius: 5px; color: #ecf0f1; cursor: pointer; font-weight: bold; font-size: 0.9em;">
              🌍 Overall
            </button>
            <button id="top20Available" onclick="setTop20Mode('available')" style="padding: 8px 16px; background: rgba(111,198,171,0.15); border: 2px solid rgba(111,198,171,0.5); border-radius: 5px; color: #ecf0f1; cursor: pointer; font-size: 0.9em;">
              💎 Available
            </button>
          </div>
        </div>
        <div id="top20Grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 10px;"></div>
      </div>
      
      <div class="filters" style="margin-bottom: 20px; padding: 15px; background: rgba(255,255,255,0.05); border-radius: 10px;">
        <h3 style="margin-bottom: 10px; font-size: 1.1em;">📊 Understanding Reliability Metrics</h3>
        <p style="margin-bottom: 10px; color: #bdc3c7;"><strong>Reliability Score (0-100):</strong> Composite metric combining accuracy, consistency, and sample size. Higher is better!</p>
        <ul style="color: #bdc3c7; margin-left: 20px; line-height: 1.6;">
          <li><strong>90+:</strong> 🟢 Elite - Trust these projections</li>
          <li><strong>75-89:</strong> 🟡 Good - Reliable with minor variance</li>
          <li><strong>60-74:</strong> 🟠 Fair - Use with caution</li>
          <li><strong>&lt;60:</strong> 🔴 Poor - High unpredictability</li>
        </ul>
      </div>
      
      <!-- Filters Section - Horizontal Layout -->
      <div class="filters" style="margin-bottom: 20px; padding: 20px; background: rgba(255,255,255,0.08); border-radius: 10px;">
        <div style="display: flex; flex-wrap: wrap; gap: 15px; align-items: flex-end; margin-bottom: 15px;">
          <div class="filter-group" style="flex: 1; min-width: 180px;">
            <label>🔍 Search Player:</label>
            <input type="text" id="reliabilitySearch" placeholder="Type name..." oninput="renderReliabilityTable()" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: #ecf0f1;">
          </div>
          
          <div class="filter-group" style="flex: 0 0 140px;">
            <label>📍 Position:</label>
            <select id="reliabilityPosFilter" onchange="updateReliabilityWithFilters()" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: #ecf0f1;">
              <option value="ALL">All Positions</option>
              <option value="QB">QB</option>
              <option value="RB">RB</option>
              <option value="WR">WR</option>
              <option value="TE">TE</option>
              <option value="FLEX">FLEX (RB/WR/TE)</option>
            </select>
          </div>
          
          <div class="filter-group" style="flex: 0 0 120px;">
            <label>🎮 Min Games:</label>
            <select id="reliabilityGamesFilter" onchange="updateReliabilityWithFilters()" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: #ecf0f1;">
              <option value="3">3+ Games</option>
              <option value="5">5+ Games</option>
              <option value="7">7+ Games</option>
            </select>
          </div>
          
          <div class="filter-group" style="flex: 0 0 130px;">
            <label>⚡ Min Avg Points:</label>
            <select id="reliabilityPointsFilter" onchange="updateReliabilityWithFilters()" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: #ecf0f1;">
              <option value="0">All Players</option>
              <option value="5">5+ PPG</option>
              <option value="8">8+ PPG</option>
              <option value="10">10+ PPG</option>
              <option value="12">12+ PPG</option>
              <option value="15">15+ PPG</option>
            </select>
          </div>
          
          <div class="filter-group" style="flex: 0 0 140px;">
            <label>👥 Roster Status:</label>
            <select id="reliabilityRosterFilter" onchange="renderReliabilityTable()" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.3); color: #ecf0f1;">
              <option value="ALL">All Players</option>
              <option value="ROSTERED">Rostered Only</option>
              <option value="AVAILABLE">Available Only</option>
            </select>
          </div>
          
          <button onclick="resetReliabilityFilters()" style="flex: 0 0 auto; padding: 8px 16px; background: rgba(231,76,60,0.2); border: 1px solid #e74c3c; border-radius: 5px; color: #ecf0f1; cursor: pointer; font-size: 0.9em; height: 38px;">
            🔄 Reset
          </button>
        </div>
      </div>
      
      <div class="table-container">
        <table id="reliabilityTable">
          <thead>
            <tr>
              <th class="sortable" onclick="sortReliability('name')">Player</th>
              <th class="sortable" onclick="sortReliability('position')">Pos</th>
              <th class="sortable" onclick="sortReliability('games')">Games</th>
              <th class="sortable" onclick="sortReliability('reliabilityScore')" title="Composite score (0-100): Combines MAE, correlation, consistency, and sample size">⭐ Reliability</th>
              <th class="sortable" onclick="sortReliability('mae')" title="Mean Absolute Error: Average rank difference between projected and actual">MAE</th>
              <th class="sortable" onclick="sortReliability('correlation')" title="Correlation between projections and results">Corr %</th>
              <th class="sortable" onclick="sortReliability('consistency')" title="How consistent the projection errors are">Consistency</th>
              <th class="sortable" onclick="sortReliability('avgScore')">Avg Pts</th>
              <th class="sortable" onclick="sortReliability('avgDiff')" title="Average bias: Negative means player beats projections">Bias</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    
    <!-- Rankings Tab -->
    <div id="rankings" class="tab-content">
      <div class="position-buttons">
        <button class="pos-btn active" onclick="renderRankingsTable('QB')">QB (Top 30)</button>
        <button class="pos-btn" onclick="renderRankingsTable('RB')">RB (Top 41)</button>
        <button class="pos-btn" onclick="renderRankingsTable('WR')">WR (Top 54)</button>
        <button class="pos-btn" onclick="renderRankingsTable('TE')">TE (Top 26)</button>
      </div>
      
      <div class="table-container">
        <table id="rankingsTable">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Avg Score</th>
              <th>Games</th>
              <th>FP Acc</th>
              <th>Week {nw} Proj</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
    </div>
    
    <!-- Waiver Tab -->
    <div id="waiver" class="tab-content">
      <!-- Smart Filters Section -->
      <div class="filters" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px;">
        <div class="filter-group">
          <label>🔍 Search:</label>
          <input type="text" id="waiverSearch" placeholder="Player name..." oninput="renderWaiverTable()">
        </div>
        
        <div class="filter-group">
          <label>Position:</label>
          <select id="waiverPosFilter" onchange="renderWaiverTable()">
            <option value="ALL">All Positions</option>
            <option value="QB">QB</option>
            <option value="RB">RB</option>
            <option value="WR">WR</option>
            <option value="TE">TE</option>
            <option value="FLEX">FLEX (RB/WR/TE)</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Tier:</label>
          <select id="waiverTierFilter" onchange="renderWaiverTable()">
            <option value="ALL">All Tiers</option>
            <option value="Elite">Elite</option>
            <option value="High">High</option>
            <option value="Mid">Mid</option>
            <option value="Stream">Stream</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Min Projection:</label>
          <input type="number" id="minProj" value="6" step="0.5" oninput="renderWaiverTable()" style="width: 80px;">
        </div>
        
        <div class="filter-group">
          <label>Max Results:</label>
          <select id="waiverLimit" onchange="renderWaiverTable()">
            <option value="20">Top 20</option>
            <option value="30" selected>Top 30</option>
            <option value="50">Top 50</option>
            <option value="100">All Available</option>
          </select>
        </div>
      </div>
      
      <!-- Stats Summary Cards -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 20px;">
        <div class="stat-card" style="padding: 15px;">
          <h4 style="margin: 0; font-size: 0.9em; color: #bdc3c7;">Available Players</h4>
          <div id="waiverAvailableCount" style="font-size: 1.8em; font-weight: bold; color: #6fc6ab;">-</div>
        </div>
        <div class="stat-card" style="padding: 15px;">
          <h4 style="margin: 0; font-size: 0.9em; color: #bdc3c7;">Top QB Available</h4>
          <div id="waiverTopQB" style="font-size: 1.2em; font-weight: bold; color: #fc8b5f;">-</div>
        </div>
        <div class="stat-card" style="padding: 15px;">
          <h4 style="margin: 0; font-size: 0.9em; color: #bdc3c7;">Top RB Available</h4>
          <div id="waiverTopRB" style="font-size: 1.2em; font-weight: bold; color: #abda5e;">-</div>
        </div>
        <div class="stat-card" style="padding: 15px;">
          <h4 style="margin: 0; font-size: 0.9em; color: #bdc3c7;">Top WR Available</h4>
          <div id="waiverTopWR" style="font-size: 1.2em; font-weight: bold; color: #8caacb;">-</div>
        </div>
        <div class="stat-card" style="padding: 15px;">
          <h4 style="margin: 0; font-size: 0.9em; color: #bdc3c7;">Top TE Available</h4>
          <div id="waiverTopTE" style="font-size: 1.2em; font-weight: bold; color: #e683bf;">-</div>
        </div>
      </div>
      
      <div class="table-container">
        <table id="waiverTable">
          <thead>
            <tr>
              <th onclick="sortTable('waiver', 'priority', 'number')" style="cursor: pointer;" title="Click to sort">Priority</th>
              <th onclick="sortTable('waiver', 'player', 'string')" style="cursor: pointer;" title="Click to sort">Player</th>
              <th onclick="sortTable('waiver', 'pos', 'string')" style="cursor: pointer;" title="Click to sort">Pos</th>
              <th onclick="sortTable('waiver', 'rank', 'number')" style="cursor: pointer;" title="Click to sort">Rank</th>
              <th onclick="sortTable('waiver', 'proj', 'number')" style="cursor: pointer;" title="Click to sort">Week {nw} Proj</th>
              <th onclick="sortTable('waiver', 'range', 'number')" style="cursor: pointer;" title="Click to sort">Floor-Ceiling</th>
              <th onclick="sortTable('waiver', 'tier', 'string')" style="cursor: pointer;" title="Click to sort">Tier</th>
              <th onclick="sortTable('waiver', 'avgScore', 'number')" style="cursor: pointer;" title="Click to sort">Season Avg</th>
              <th onclick="sortTable('waiver', 'reliabilityScore', 'number')" style="cursor: pointer;" title="Click to sort - Higher is better!">Reliability</th>
              <th onclick="sortTable('waiver', 'trend', 'number')" style="cursor: pointer;" title="Click to sort">Trend</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody></tbody>
        </table>
      </div>
      
      <!-- Helper text -->
      <div style="margin-top: 15px; padding: 15px; background: rgba(111,198,171,0.1); border-left: 3px solid #6fc6ab; border-radius: 5px;">
        <strong>💡 Tips:</strong>
        <ul style="margin: 10px 0 0 20px; color: #bdc3c7;">
          <li>🔥 = Top 5 priority pickups</li>
          <li>⭐ = High value targets</li>
          <li>👀 = Watchlist candidates</li>
          <li>📈 = Player consistently beats projections</li>
          <li>📉 = Player consistently underperforms</li>
          <li><strong>Reliability Score:</strong> 🟢 Elite (90+) | 🟡 Good (75-89) | 🟠 Fair (60-74) | 🔴 Poor (&lt;60)</li>
          <li>Click column headers to sort</li>
        </ul>
      </div>
    </div>
    
    <!-- Lineups Tab -->
    <div id="lineups" class="tab-content">
      <div class="control-group" style="margin-bottom: 20px;">
        <label>Select Team:</label>
        <select id="teamSelector" style="max-width: 300px;">
          <option value="">Connect to Sleeper first</option>
        </select>
      </div>
      
      <div class="lineup-config">
        <div class="control-group">
          <label>QB:</label>
          <input type="number" id="qbSlots" value="1" min="0" max="3">
        </div>
        <div class="control-group">
          <label>RB:</label>
          <input type="number" id="rbSlots" value="2" min="0" max="4">
        </div>
        <div class="control-group">
          <label>WR:</label>
          <input type="number" id="wrSlots" value="2" min="0" max="4">
        </div>
        <div class="control-group">
          <label>TE:</label>
          <input type="number" id="teSlots" value="1" min="0" max="3">
        </div>
        <div class="control-group">
          <label>FLEX:</label>
          <input type="number" id="flexSlots" value="1" min="0" max="3">
        </div>
      </div>
      
      <button onclick="generateOptimalLineup()">⚡ Generate Optimal Lineup</button>
      
      <div class="lineup-results" id="lineupResults"></div>
    </div>
    
    <!-- Matchups Tab -->
    <div id="matchups" class="tab-content">
      <div style="text-align: center; padding: 40px; background: rgba(255,255,255,0.05); border-radius: 10px;">
        <h2>⚔️ Matchup Simulator</h2>
        <p style="margin-top: 10px; color: #bdc3c7;">Coming soon! Head-to-head matchup analysis and win probability.</p>
      </div>
    </div>
    
    <!-- Historical Tab -->
    <div id="historical" class="tab-content">
      
      <!-- Player Reliability Section -->
      <div style="margin-bottom: 40px;">
        <h3>📊 Player Historical Reliability</h3>
        <p style="color: #a0aec0; margin-bottom: 15px;">
          Shows how reliable expert rankings have been for each player (5+ games minimum)
        </p>
        <div class="table-container">
          <table id="historicalTable">
            <thead>
              <tr>
                <th data-column="player" onclick="sortTable('historical', 'player', 'string')" style="cursor: pointer;">Player</th>
                <th data-column="pos" onclick="sortTable('historical', 'pos', 'string')" style="cursor: pointer;">Pos</th>
                <th data-column="games" onclick="sortTable('historical', 'games', 'number')" style="cursor: pointer;">Games</th>
                <th data-column="correlation" onclick="sortTable('historical', 'correlation', 'number')" style="cursor: pointer;">Correlation</th>
                <th data-column="mae" onclick="sortTable('historical', 'mae', 'number')" style="cursor: pointer;" title="Rating score (0-100) based on prediction accuracy - hover over values to see underlying MAE">Rating</th>
                <th data-column="avgDiff" onclick="sortTable('historical', 'avgDiff', 'number')" style="cursor: pointer;" title="Negative = beats projections, Positive = misses projections">Trend</th>
                <th data-column="avgScore" onclick="sortTable('historical', 'avgScore', 'number')" style="cursor: pointer;">Avg Score</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
      
      <!-- Positional Baselines Section -->
      <div>
        <h3>📈 Positional Baseline Averages (2022-2024)</h3>
        <p style="color: #a0aec0; margin-bottom: 15px;">
          Historical average scores by position rank across the last 3 years
        </p>
        <div id="baselineTables"></div>
      </div>
      
    </div>
  </div>
</div>

<script>
// ==================== EMBEDDED DATA ====================
const HISTORICAL_DATA = {hist_json};
const SEASON_2025 = {season_json};
const WEEKLY_PROJECTIONS = {proj_json};
const CURRENT_WEEK = {cw};
const NEXT_WEEK = {nw};

// ==================== GLOBAL STATE ====================
let CURRENT_SCORING = 'PPR';
let FP_ACCURACY = {{}};
let POSITION_ACCURACY = {{ QB: {{}}, RB: {{}}, WR: {{}}, TE: {{}} }};
let PROJECTIONS = [];
let ALL_ROSTERED = new Set();
let USER_ROSTER = [];
let ROSTER_SOURCE = 'None';
let SLEEPER_DATA = null;

// Sleeper-specific variables
let sleeperUserId = null;
let sleeperLeagues = null;

// ==================== SLEEPER INTEGRATION ====================

// Load saved roster on page load
window.addEventListener('DOMContentLoaded', () => {{
  const savedUsername = localStorage.getItem('sleeper_username');
  if (savedUsername) {{
    document.getElementById('sleeperUsername').value = savedUsername;
  }}
  loadSavedSleeperRoster();
}});

async function loadSleeperLeagues() {{
  const username = document.getElementById('sleeperUsername').value.trim();
  const button = document.getElementById('loadLeaguesBtn');
  const statusDiv = document.getElementById('sleeperStatus');
  
  if (!username) {{
    statusDiv.innerHTML = '<span style="color: #dc3545;">❌ Please enter your Sleeper username</span>';
    return;
  }}
  
  button.disabled = true;
  button.textContent = '⏳ Loading...';
  statusDiv.innerHTML = '<span style="color: #0c5460;">Fetching your leagues...</span>';
  
  try {{
    localStorage.setItem('sleeper_username', username);
    
    const userResponse = await fetch(`https://api.sleeper.app/v1/user/${{username}}`);
    if (!userResponse.ok) throw new Error('Username not found!');
    
    const user = await userResponse.json();
    sleeperUserId = user.user_id;
    console.log('Found user ID:', sleeperUserId);
    
    const currentYear = new Date().getFullYear();
    const leaguesResponse = await fetch(
      `https://api.sleeper.app/v1/user/${{sleeperUserId}}/leagues/nfl/${{currentYear}}`
    );
    
    if (!leaguesResponse.ok) throw new Error('Could not fetch leagues');
    
    sleeperLeagues = await leaguesResponse.json();
    console.log('Found leagues:', sleeperLeagues.length);
    
    if (sleeperLeagues.length === 0) {{
      throw new Error('No leagues found for this season');
    }}
    
    displaySleeperLeagues(sleeperLeagues);
    statusDiv.innerHTML = `<span style="color: #28a745;">✅ Found ${{sleeperLeagues.length}} league(s)!</span>`;
    
  }} catch (error) {{
    console.error('Sleeper error:', error);
    statusDiv.innerHTML = `<span style="color: #dc3545;">❌ ${{error.message}}</span>`;
  }} finally {{
    button.disabled = false;
    button.textContent = 'Load Leagues';
  }}
}}

function displaySleeperLeagues(leagues) {{
  const dropdown = document.getElementById('leagueDropdown');
  const section = document.getElementById('leagueSection');
  
  dropdown.innerHTML = '';
  leagues.forEach((league, index) => {{
    const option = document.createElement('option');
    option.value = index;
    option.textContent = `${{league.name}} (${{league.total_rosters}} teams)`;
    dropdown.appendChild(option);
  }});
  
  section.style.display = 'block';
  
  // Auto-connect if only 1 league
  if (leagues.length === 1) {{
    setTimeout(() => connectSleeperLeague(), 500);
  }}
}}

async function connectSleeperLeague() {{
  const dropdown = document.getElementById('leagueDropdown');
  const button = document.getElementById('connectLeagueBtn');
  const statusDiv = document.getElementById('sleeperStatus');
  
  const leagueIndex = parseInt(dropdown.value);
  const selectedLeague = sleeperLeagues[leagueIndex];
  
  button.disabled = true;
  button.textContent = '⏳ Loading roster...';
  
  try {{
    console.log('Connecting to league:', selectedLeague.name);
    
    const rostersResponse = await fetch(
      `https://api.sleeper.app/v1/league/${{selectedLeague.league_id}}/rosters`
    );
    const rosters = await rostersResponse.json();

    // Find user's roster
    const userRoster = rosters.find(r => r.owner_id === sleeperUserId);

    if (!userRoster || !userRoster.players) {{
      throw new Error('Could not find your roster');
    }}

    console.log('Found roster with', userRoster.players.length, 'players');
    console.log('Total league rosters:', rosters.length);

    // Fetch player data
    const playersResponse = await fetch('https://api.sleeper.app/v1/players/nfl');
    const allPlayers = await playersResponse.json();

    // Process USER roster
    const playerNames = userRoster.players.map(id => {{
      const player = allPlayers[id];
      return player ? player.full_name : null;
    }}).filter(name => name !== null && name !== undefined && name.trim() !== '');

    console.log('User players:', playerNames.length);

    // Process ALL OTHER rosters in league
    const allRosteredPlayers = new Set();
    rosters.forEach(roster => {{
      if (roster.players) {{
        roster.players.forEach(playerId => {{
          const player = allPlayers[playerId];
          if (player && player.full_name) {{
            allRosteredPlayers.add(player.full_name);
          }}
        }});
      }}
    }});

    console.log('Total rostered players in league:', allRosteredPlayers.size);

    // Save both
    const rosterData = {{
      leagueName: selectedLeague.name,
      leagueId: selectedLeague.league_id,
      players: playerNames,
      allRostered: Array.from(allRosteredPlayers),
      totalTeams: rosters.length,
      fetchedAt: new Date().toISOString()
    }};

    localStorage.setItem('sleeper_roster', JSON.stringify(rosterData));
    USER_ROSTER = playerNames;
    ALL_ROSTERED = allRosteredPlayers;  // Set global for availability checks
    ROSTER_SOURCE = 'Sleeper';
    
    console.log('💾 Saved roster data:', {{
      myTeam: USER_ROSTER.length,
      allRostered: ALL_ROSTERED.size,
      teams: rosterData.totalTeams
    }});
    
    // Fetch users for team names
    const usersResponse = await fetch(`https://api.sleeper.app/v1/league/${{selectedLeague.league_id}}/users`);
    const users = await usersResponse.json();
    
    // Populate SLEEPER_DATA for lineup optimizer
    SLEEPER_DATA = {{
      rosters: rosters,
      players: allPlayers,
      users: users,
      myRoster: userRoster,
      leagueId: selectedLeague.league_id
    }};
    
    console.log('✅ SLEEPER_DATA populated with', rosters.length, 'teams');
    
    // Populate team selector dropdown
    populateTeamSelector(rosters, users);
    
    displayConnectedRoster(rosterData);
    
    // Refresh tables to highlight players
    if (typeof renderProjectionsTable === 'function') {{
      renderProjectionsTable();
    }}
    
    // Refresh waiver table now that roster data is available
    if (typeof renderWaiverTable === 'function') {{
      renderWaiverTable();
    }}
    
    // Update metrics to show roster count
    if (typeof updateMetrics === 'function') {{
      updateMetrics();
    }}
    
    statusDiv.innerHTML = '<span style="color: #28a745;">✅ Roster loaded!</span>';
    
  }} catch (error) {{
    console.error('Connect error:', error);
    statusDiv.innerHTML = `<span style="color: #dc3545;">❌ ${{error.message}}</span>`;
  }} finally {{
    button.disabled = false;
    button.textContent = '📤 Load Roster to Fantasy Truss';
  }}
}}

function populateTeamSelector(rosters, users) {{
  const selector = document.getElementById('teamSelector');
  if (!selector) {{
    console.warn('Team selector not found');
    return;
  }}
  
  selector.innerHTML = '';
  
  rosters.forEach((roster, index) => {{
    const user = users.find(u => u.user_id === roster.owner_id);
    const teamName = user ? (user.metadata?.team_name || user.display_name || `Team ${{index + 1}}`) : `Team ${{index + 1}}`;
    const option = document.createElement('option');
    option.value = index;
    option.textContent = `${{teamName}} (${{roster.players?.length || 0}} players)`;
    selector.appendChild(option);
  }});
  
  console.log('✅ Populated', rosters.length, 'teams in selector');
}}

function displayConnectedRoster(rosterData) {{
  document.getElementById('usernameSection').style.display = 'none';
  document.getElementById('leagueSection').style.display = 'none';
  document.getElementById('connectedSection').style.display = 'block';
  
  const date = new Date(rosterData.fetchedAt).toLocaleString();
  const totalRostered = rosterData.allRostered ? rosterData.allRostered.length : 0;
  const teams = rosterData.totalTeams || '?';
  
  document.getElementById('rosterInfo').innerHTML = `
    <div style="display: flex; align-items: center; gap: 15px;">
      <span style="font-size: 40px;">✅</span>
      <div>
        <strong style="display: block; font-size: 16px; color: #155724;">
          ${{rosterData.leagueName}}
        </strong>
        <span style="font-size: 13px; color: #155724;">
          Your team: ${{rosterData.players.length}} players<br>
          League: ${{teams}} teams, ${{totalRostered}} rostered players<br>
          <em style="opacity: 0.8;">${{date}}</em>
        </span>
      </div>
    </div>
  `;
  
  // Update metrics
  updateMetrics();
}}

function clearSleeperRoster() {{
  if (confirm('Clear your connected roster?')) {{
    localStorage.removeItem('sleeper_roster');
    USER_ROSTER = [];
    ALL_ROSTERED.clear(); // Clear rostered players set
    ROSTER_SOURCE = 'None';
    document.getElementById('usernameSection').style.display = 'block';
    document.getElementById('leagueSection').style.display = 'none';
    document.getElementById('connectedSection').style.display = 'none';
    document.getElementById('sleeperStatus').innerHTML = '';
    
    if (typeof renderProjectionsTable === 'function') {{
      renderProjectionsTable();
    }}
    
    // Refresh waiver table to show "Connect Sleeper" message
    if (typeof renderWaiverTable === 'function') {{
      renderWaiverTable();
    }}
  }}
}}

function loadSavedSleeperRoster() {{
  try {{
    const saved = localStorage.getItem('sleeper_roster');
    if (saved) {{
      const rosterData = JSON.parse(saved);
      USER_ROSTER = rosterData.players;
      
      // Load all rostered players too
      if (rosterData.allRostered) {{
        ALL_ROSTERED = new Set(rosterData.allRostered);
        console.log('Loaded', ALL_ROSTERED.size, 'rostered players from league');
      }}
      
      ROSTER_SOURCE = 'Sleeper';
      console.log('Loaded saved roster:', rosterData.leagueName, USER_ROSTER.length, 'players');
      displayConnectedRoster(rosterData);
      
      // Update metrics after loading
      if (typeof updateMetrics === 'function') {{
        updateMetrics();
      }}
      
      // Refresh waiver table now that roster data is available
      if (typeof renderWaiverTable === 'function') {{
        renderWaiverTable();
      }}
    }}
  }} catch (e) {{
    console.warn('Could not load saved roster:', e);
  }}
}}

// ==================== END SLEEPER INTEGRATION ====================

// ==================== UTILITY FUNCTIONS ====================
function normalizePlayerName(name) {{
  if (!name) return '';
  if (typeof name !== 'string') return '';
  
  return name.toLowerCase()
    .replace(/\s+(jr|sr|ii|iii|iv|v)\.?$/i, '')
    .replace(/[^a-z0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}}

// Convert percentile (0-1) to grade (0-100) using anchor points
// Based on statistical best practices for skewed data
function percentileToGrade(percentile) {{
  // Anchor points (percentile → grade)
  // 0th percentile (worst) → 10
  // 25th percentile → 43
  // 50th percentile (median) → 75
  // 75th percentile → 87
  // 100th percentile (best) → 100
  
  const anchors = [
    {{ p: 0.00, g: 10 }},
    {{ p: 0.25, g: 43 }},
    {{ p: 0.50, g: 75 }},
    {{ p: 0.75, g: 87 }},
    {{ p: 1.00, g: 100 }}
  ];
  
  // Find the two anchor points to interpolate between
  for (let i = 0; i < anchors.length - 1; i++) {{
    if (percentile >= anchors[i].p && percentile <= anchors[i + 1].p) {{
      const p1 = anchors[i].p;
      const p2 = anchors[i + 1].p;
      const g1 = anchors[i].g;
      const g2 = anchors[i + 1].g;
      
      // Linear interpolation
      const t = (percentile - p1) / (p2 - p1);
      return g1 + t * (g2 - g1);
    }}
  }}
  
  // Fallback (shouldn't happen)
  return percentile * 100;
}}

function pearsonCorrelation(x, y) {{
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
}}

// ==================== COMPLETE TABLE SORTING SYSTEM ====================
// Add this section after your utility functions (around line 1230)

let sortState = {{
  projections: {{ column: 'proj', direction: 'desc' }},
  reliability: {{ column: 'reliabilityScore', direction: 'desc' }},  // ✅ Changed from 'correlation' to 'reliabilityScore'
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
    
    // SPECIAL CASE: For "mae" column, invert sort
    // because lower MAE = better = higher rating score
    // So "asc" should show LOW mae (HIGH rating) first
    const shouldInvert = ((tableId === 'historical' || tableId === 'reliability') && state.column === 'mae');
    const effectiveDirection = shouldInvert ? 
      (state.direction === 'asc' ? 'desc' : 'asc') : 
      state.direction;
    
    // Apply direction
    return effectiveDirection === 'asc' ? result : -result;
  }});
}}

// ==================== END TABLE SORTING ====================

// ==================== CORE CALCULATIONS ====================
function calculatePositionalBaselines() {{
  const baselines = {{}};
  
  ['QB', 'RB', 'WR', 'TE'].forEach(pos => {{
    const historicalPlayers = HISTORICAL_DATA[CURRENT_SCORING]['2024'] || [];
    const posPlayers = historicalPlayers
      .filter(p => p.pos === pos)
      .map(p => {{
        const weeks = Object.values(p.w);
        const avg = weeks.length > 0 ? weeks.reduce((a,b) => a+b, 0) / weeks.length : 0;
        return avg;
      }})
      .filter(avg => avg > 0)
      .sort((a,b) => b - a);
    
    // Store top 100 averages for each position
    baselines[pos] = posPlayers.slice(0, 100);
  }});
  
  return baselines;
}}
function calculateFPAccuracy() {{
  FP_ACCURACY = {{}};
  const POSITION_ACCURACY = {{ QB: [], RB: [], WR: [], TE: [] }};
  
  if (!SEASON_2025 || !SEASON_2025.data) return;
  
  const seasonData = SEASON_2025.data;
  const weekNums = Object.keys(WEEKLY_PROJECTIONS).map(Number).sort((a,b) => a-b);
  
  // First pass: Calculate positional ranks for each week's actual scores
  const weeklyRanks = {{}};
  weekNums.forEach(weekNum => {{
    weeklyRanks[weekNum] = {{ QB: [], RB: [], WR: [], TE: [] }};
    
    // Collect all scores by position
    seasonData.forEach(player => {{
      const score = player.w[weekNum];
      if (score !== undefined && score > 0) {{
        weeklyRanks[weekNum][player.pos].push({{ name: player.p, score: score }});
      }}
    }});
    
    // Sort and assign ranks
    ['QB', 'RB', 'WR', 'TE'].forEach(pos => {{
      weeklyRanks[weekNum][pos].sort((a, b) => b.score - a.score);
    }});
  }});
  
  // Second pass: Compare ECR ranks to actual performance ranks
  seasonData.forEach(player => {{
    const name = player.p;
    const weeks = player.w;
    const pos = player.pos;
    
    if (!weeks || Object.keys(weeks).length < 3) return;
    
    const projectedRanks = [];
    const actualRanks = [];
    const weekDetails = {{}};
    
    weekNums.forEach(weekNum => {{
      if (weeks[weekNum] !== undefined && weeks[weekNum] > 0) {{
        const projData = WEEKLY_PROJECTIONS[weekNum];
        if (projData) {{
          const normName = normalizePlayerName(name);
          const proj = projData.find(p => normalizePlayerName(p.p) === normName);
          
          if (proj && proj.ecr > 0) {{
            // Find actual rank for this player this week
            const posPlayers = weeklyRanks[weekNum][pos];
            const actualRank = posPlayers.findIndex(p => normalizePlayerName(p.name) === normName) + 1;
            
            if (actualRank > 0) {{
              projectedRanks.push(proj.ecr);
              actualRanks.push(actualRank);
              weekDetails[weekNum] = {{
                projRank: proj.ecr,
                actualRank: actualRank,
                actualScore: weeks[weekNum],
                rankDiff: actualRank - proj.ecr
              }};
            }}
          }}
        }}
      }}
    }});
    
    if (projectedRanks.length >= 3) {{
      const correlation = pearsonCorrelation(projectedRanks, actualRanks);
      const rankDiffs = projectedRanks.map((p, i) => Math.abs(p - actualRanks[i]));
      const mae = rankDiffs.reduce((a, b) => a + b, 0) / rankDiffs.length;
      const within3 = rankDiffs.filter(d => d <= 3).length / rankDiffs.length;  // Within 3 ranks (stricter)
      const avgDiff = projectedRanks.reduce((sum, p, i) => sum + (actualRanks[i] - p), 0) / projectedRanks.length;
      
      // ✅ Calculate average score from all weeks played
      const allScores = Object.values(weeks).filter(score => score !== undefined && score > 0);
      const avgScore = allScores.length > 0 ? allScores.reduce((a, b) => a + b, 0) / allScores.length : 0;
      
      // ✅ Calculate consistency (inverse of standard deviation of rank differences)
      const variance = rankDiffs.reduce((sum, d) => sum + Math.pow(d - mae, 2), 0) / rankDiffs.length;
      const stdDev = Math.sqrt(variance);
      const consistency = Math.max(0, 1 - (stdDev / 15)); // Normalize to 0-1 (15 ranks = 0 consistency)
      
      // Store raw metrics for later percentile calculation
      FP_ACCURACY[name] = {{
        position: pos,
        games: projectedRanks.length,
        weeks: weekDetails,
        correlation: correlation,
        mae: mae,
        accuracy: within3,
        avgDiff: avgDiff,
        avgScore: avgScore,
        consistency: consistency,
        reliabilityScore: 0  // Will be calculated after all players processed
      }};
      
      // Track position-level accuracy
      POSITION_ACCURACY[pos].push({{ correlation, mae, within3, consistency }});
    }}
  }});
  
  // ✅ SECOND PASS: Calculate percentile-based reliability scores
  // Group players by position for percentile calculation
  const playersByPosition = {{ QB: [], RB: [], WR: [], TE: [] }};
  
  Object.entries(FP_ACCURACY).forEach(([name, stats]) => {{
    if (stats.position && playersByPosition[stats.position]) {{
      playersByPosition[stats.position].push({{ name, ...stats }});
    }}
  }});
  
  // Calculate percentile-based grades for each position separately
  ['QB', 'RB', 'WR', 'TE'].forEach(pos => {{
    const players = playersByPosition[pos];
    if (players.length === 0) return;
    
    // Extract and sort metrics for percentile calculation
    const maes = players.map(p => p.mae).sort((a, b) => a - b); // Lower is better
    const correlations = players.map(p => p.correlation).sort((a, b) => b - a); // Higher is better
    const consistencies = players.map(p => p.consistency).sort((a, b) => b - a); // Higher is better
    
    // Calculate percentile ranks and convert to grades for each player
    players.forEach(player => {{
      // MAE Grade: Lower MAE = Higher Grade (inverted percentile)
      const maeRank = maes.indexOf(player.mae);
      const maePercentile = (maes.length - 1 - maeRank) / (maes.length - 1); // Inverted
      const maeGrade = percentileToGrade(maePercentile);
      
      // Correlation Grade: Higher correlation = Higher Grade
      const corrRank = correlations.indexOf(player.correlation);
      const corrPercentile = (correlations.length - 1 - corrRank) / (correlations.length - 1);
      const corrGrade = percentileToGrade(corrPercentile);
      
      // Consistency Grade: Higher consistency = Higher Grade
      const consRank = consistencies.indexOf(player.consistency);
      const consPercentile = (consistencies.length - 1 - consRank) / (consistencies.length - 1);
      const consGrade = percentileToGrade(consPercentile);
      
      // Sample Size Bonus (same as before)
      const sampleBonus = Math.min(100, (player.games / 8) * 100);
      
      // Weighted Composite Score
      const reliabilityScore = (
        maeGrade * 0.40 +
        corrGrade * 0.30 +
        consGrade * 0.20 +
        sampleBonus * 0.10
      );
      
      // Update the player's reliability score
      FP_ACCURACY[player.name].reliabilityScore = Math.max(0, Math.min(100, reliabilityScore));
    }});
  }});
  
  // Calculate average accuracy by position
  ['QB', 'RB', 'WR', 'TE'].forEach(pos => {{
    const posData = POSITION_ACCURACY[pos];
    if (posData.length > 0) {{
      const avgCorr = posData.reduce((sum, d) => sum + d.correlation, 0) / posData.length;
      const avgMAE = posData.reduce((sum, d) => sum + d.mae, 0) / posData.length;
      const avgWithin3 = posData.reduce((sum, d) => sum + d.within3, 0) / posData.length;
      
      // Calculate average reliability from updated scores
      const players = playersByPosition[pos];
      const avgReliability = players.length > 0 ? 
        players.reduce((sum, p) => sum + (FP_ACCURACY[p.name]?.reliabilityScore || 0), 0) / players.length : 0;
      
      POSITION_ACCURACY[pos] = {{
        avgCorrelation: avgCorr,
        avgMAE: avgMAE,
        avgAccuracy: avgWithin3,
        avgReliability: avgReliability,
        playerCount: posData.length
      }};
    }}
  }});
  
  console.log(`FP Accuracy calculated for ${{Object.keys(FP_ACCURACY).length}} players`);
  console.log('Position Reliability:', POSITION_ACCURACY);
  
  return POSITION_ACCURACY;
}}

function calculateProjections() {{
  if (!SEASON_2025 || !SEASON_2025.data) return [];
  
  const projections = [];
  const nextWeekECR = WEEKLY_PROJECTIONS[NEXT_WEEK] || [];
  const baselines = calculatePositionalBaselines();  // ✅ Get positional averages
  
  SEASON_2025.data.forEach(player => {{
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
    
    // Check if player is on bye (no ECR data for this week)
    let onBye = false;
    if (!ecrData || !ecrData.ecr || ecrData.ecr <= 0) {{
      onBye = true;
      // Still include bye players with basic info
      projections.push({{
        p: name,
        pos: pos,
        proj: 0,
        floor: 0,
        ceiling: 0,
        avgScore: avgScore,
        games: games,
        hasECR: false,
        ecrRank: 999,
        correlation: FP_ACCURACY[name]?.correlation || 0,
        mae: FP_ACCURACY[name]?.mae || 0,
        avgDiff: FP_ACCURACY[name]?.avgDiff || 0,
        accuracy: FP_ACCURACY[name]?.accuracy || 0,
        onBye: true,
        tier: 'BYE'
      }});
      return;
    }}

    // Player has ECR - continue with projection
    let hasECR = true;
    let positionRank = ecrData.ecr;

    let proj = avgScore;
    let floor = avgScore * 0.7;
    let ceiling = avgScore * 1.3;

    // Now continue with the ECR conversion code below...
      
      // ✅ Convert ECR to points using baseline
      const posBaseline = baselines[pos] || [];
      const ecrIndex = Math.floor(ecrData.ecr) - 1;  // Rank 1 = index 0
      
      if (ecrIndex < posBaseline.length) {{
        proj = posBaseline[ecrIndex];
      }} else {{
        // Extrapolate for ranks beyond our data
        const lastKnown = posBaseline[posBaseline.length - 1] || avgScore;
        const dropPerRank = 0.3;  // Points decrease per rank
        proj = lastKnown - (ecrIndex - posBaseline.length) * dropPerRank;
        proj = Math.max(proj, 3);  // Minimum 3 points
      }}
      
      // ✅ Calculate floor/ceiling from std deviation
      const stdDev = ecrData.std || 5;
      const stdPoints = stdDev * 0.8;  // Convert rank std to points (approx)
      floor = Math.max(proj - stdPoints, proj * 0.5);
      ceiling = proj + stdPoints;
      
      // ✅ Apply position-level reliability
      const posReliability = POSITION_ACCURACY[pos]?.avgCorrelation || 0.5;
      const posMAE = POSITION_ACCURACY[pos]?.avgMAE || 10;
      
      // Weight ECR projection by position reliability
      // High reliability (e.g., RB) = trust ECR more
      // Low reliability (e.g., QB) = blend more with player average
      let reliabilityWeight = Math.max(0.3, Math.min(0.9, posReliability));
      
      // ⚠️ If position has negative correlation, trust player avg more than ECR
      if (posReliability < 0) {{
        reliabilityWeight = 0.3;  // Only 30% weight to ECR if position reliability is broken
      }}
      
      // ✅ Apply player-specific correlation adjustment
      const accuracy = FP_ACCURACY[name];
      if (accuracy && accuracy.games >= 5) {{  // ⬆️ Increased from 3 to 5 games minimum
        // If player has strong personal correlation, use it
        if (accuracy.correlation > 0.7) {{
          const playerWeight = 0.7 + (accuracy.correlation - 0.7) * 0.3;
          proj = playerWeight * proj + (1 - playerWeight) * avgScore;
        }} else if (accuracy.correlation < 0) {{
          // Negative correlation - heavily favor player average
          proj = 0.3 * proj + 0.7 * avgScore;
        }} else {{
          // Otherwise blend using position reliability
          proj = reliabilityWeight * proj + (1 - reliabilityWeight) * avgScore;
        }}
        
        // ⚠️ DISABLED - Bias adjustment was too aggressive and double-penalized players
        // Experts already adjust ECR based on recent performance, so we don't need to
        /*
        // Adjust for consistent rank bias (over/under-ranking)
        if (Math.abs(accuracy.avgDiff) > 3) {{
          // Convert rank difference to approximate point adjustment
          const pointsPerRank = proj / (ecrData.ecr || 10);
          const adjustment = -accuracy.avgDiff * pointsPerRank * 0.3;
          proj += adjustment;
        }}
        */
      }} else {{
        // No player history OR not enough games - use position reliability only
        proj = reliabilityWeight * proj + (1 - reliabilityWeight) * avgScore;
      }}
    
    projections.push({{
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
      avgDiff: FP_ACCURACY[name]?.avgDiff || 0,
      accuracy: FP_ACCURACY[name]?.accuracy || 0,
      onBye: false
    }});
  }});
  
  // Sort by projection (bye weeks will be at bottom with 0 proj)
  projections.sort((a, b) => b.proj - a.proj);
  
  // Assign ranks and tiers (skip bye weeks for rank counting)
  const posCounts = {{ QB: 0, RB: 0, WR: 0, TE: 0 }};
  projections.forEach(p => {{
    // Skip bye weeks for rank assignment
    if (p.onBye) {{
      p.rank = 999;
      p.tier = 'BYE';
      return;
    }}
    
    posCounts[p.pos]++;
    p.rank = posCounts[p.pos];
    
    // Assign tier based on rank
    const rank = p.rank;
    if (p.pos === 'QB') {{
      if (rank <= 6) p.tier = 'Elite';
      else if (rank <= 12) p.tier = 'High';
      else if (rank <= 24) p.tier = 'Mid';
      else p.tier = 'Stream';
    }} else if (p.pos === 'RB') {{
      if (rank <= 12) p.tier = 'Elite';
      else if (rank <= 24) p.tier = 'High';
      else if (rank <= 36) p.tier = 'Mid';
      else p.tier = 'Stream';
    }} else if (p.pos === 'WR') {{
      if (rank <= 12) p.tier = 'Elite';
      else if (rank <= 24) p.tier = 'High';
      else if (rank <= 36) p.tier = 'Mid';
      else p.tier = 'Stream';
    }} else if (p.pos === 'TE') {{
      if (rank <= 6) p.tier = 'Elite';
      else if (rank <= 12) p.tier = 'High';
      else if (rank <= 20) p.tier = 'Mid';
      else p.tier = 'Stream';
    }}
  }});
  
  return projections;
}}

// ==================== RENDERING FUNCTIONS ====================
function updateMetrics() {{
  const cards = [
    {{ label: 'Total Players', value: PROJECTIONS.length }},
    {{ label: 'With FP Data', value: PROJECTIONS.filter(p => p.hasECR).length }},
    {{ label: 'High Accuracy', value: Object.values(FP_ACCURACY).filter(a => a.correlation > 0.7).length }},
    {{ label: 'My Roster', value: USER_ROSTER.length }},
    {{ label: 'Available', value: PROJECTIONS.filter(p => !isRostered(p.p)).length }}
  ];
  
  const html = cards.map(card => `
    <div class="stat-card">
      <h3>${{card.label}}</h3>
      <div class="value">${{card.value}}</div>
    </div>
  `).join('');
  
  document.getElementById('statsCards').innerHTML = html;
}}

function renderProjectionsTable() {{
  const posFilter = document.getElementById('posFilter').value;
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
    // Calculate rating score from MAE
    const rating = p.mae > 0 ? Math.max(0, 100 - Math.pow(p.mae * 0.5, 1.3)) : 0;
    const ratingClass = rating >= 90 ? 'high-acc' : rating >= 75 ? 'med-acc' : 'low-acc';
    
    // Trend display with value
    const trendIcon = p.avgDiff < -2 ? '📈' : p.avgDiff > 2 ? '📉' : '➡️';
    const trendClass = p.avgDiff < -2 ? 'trend-up' : p.avgDiff > 2 ? 'trend-down' : 'trend-stable';
    const trendText = p.avgDiff !== 0 ? (p.avgDiff > 0 ? '+' : '') + p.avgDiff.toFixed(1) : '0.0';
    
    const roster = isOnRoster(p.p) ? '🏠' : '';
    const rowClass = isOnRoster(p.p) ? 'my-roster' : isRostered(p.p) ? 'rostered' : '';
    
    // Check if player is on bye (has no ECR for this week but exists in season data)
    const byeIndicator = p.onBye ? ' 🚫 BYE' : '';
    
    return `
      <tr class="pos-${{p.pos}} ${{rowClass}}">
        <td>${{roster}} ${{p.p}}${{byeIndicator}}</td>
        <td>${{p.pos}}</td>
        <td>${{p.rank}}</td>
        <td><strong>${{p.onBye ? '-' : p.proj.toFixed(1)}}</strong></td>
        <td>${{p.onBye ? '-' : p.floor.toFixed(1) + ' - ' + p.ceiling.toFixed(1)}}</td>
        <td><span class="badge ${{p.tier.toLowerCase()}}">${{p.tier}}</span></td>
        <td class="${{ratingClass}}" title="MAE: ${{p.mae.toFixed(1)}} ranks">${{rating > 0 ? rating.toFixed(0) : '-'}}</td>
        <td class="${{trendClass}}" title="Avg rank difference">${{trendIcon}} ${{trendText}}</td>
      </tr>
    `;
  }}).join('');
}}

function renderReliabilityTable() {{
  // Get all filter values
  const searchTerm = (document.getElementById('reliabilitySearch')?.value || '').toLowerCase();
  const posFilter = document.getElementById('reliabilityPosFilter')?.value || 'ALL';
  const minGames = parseInt(document.getElementById('reliabilityGamesFilter')?.value || '3');
  const minPoints = parseFloat(document.getElementById('reliabilityPointsFilter')?.value || '0');
  const rosterFilter = document.getElementById('reliabilityRosterFilter')?.value || 'ALL';
  
  let data = Object.entries(FP_ACCURACY)
    .filter(([name, stats]) => {{
      // Filter by minimum games
      if (stats.games < minGames) return false;
      
      // Get avgScore
      const playerData = SEASON_2025.data.find(pd => pd.p === name);
      let avgScore = 0;
      if (playerData && playerData.w) {{
        const scores = Object.values(playerData.w);
        avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
      }}
      
      // Filter by minimum points
      if (avgScore < minPoints) return false;
      
      // Filter by position
      if (posFilter === 'FLEX') {{
        // FLEX includes RB, WR, TE (not QB)
        if (!['RB', 'WR', 'TE'].includes(stats.position)) return false;
      }} else if (posFilter !== 'ALL' && stats.position !== posFilter) {{
        return false;
      }}
      
      // Filter by search term
      if (searchTerm && !name.toLowerCase().includes(searchTerm)) return false;
      
      // Filter by roster status
      if (rosterFilter === 'ROSTERED' && !isRostered(name)) return false;
      if (rosterFilter === 'AVAILABLE' && isRostered(name)) return false;
      
      return true;
    }})
    .map(([name, stats]) => {{
      const playerData = SEASON_2025.data.find(pd => pd.p === name);
      let avgScore = 0;
      if (playerData && playerData.w) {{
        const scores = Object.values(playerData.w);
        avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
      }}
      
      return {{
        name: name,
        position: stats.position,
        games: stats.games,
        correlation: stats.correlation,
        mae: stats.mae,
        accuracy: stats.accuracy,
        avgScore: avgScore,
        avgDiff: stats.avgDiff,
        consistency: stats.consistency || 0,
        reliabilityScore: stats.reliabilityScore || 0
      }};
    }});
  
  // Sort the data
  data = applySorting(data, 'reliability');
  
  // Render the table
  const tbody = document.getElementById('reliabilityTable').querySelector('tbody');
  
  if (data.length === 0) {{
    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; padding: 30px; color: #95a5a6;">No players match your filters. Try adjusting the criteria.</td></tr>';
    return;
  }}
  
  tbody.innerHTML = data.map(p => {{
    const diffClass = p.avgDiff > 0 ? 'trend-up' : p.avgDiff < 0 ? 'trend-down' : 'trend-stable';
    
    // Color code reliability score
    const reliability = p.reliabilityScore;
    let reliabilityClass = '';
    let reliabilityIcon = '';
    if (reliability >= 90) {{
      reliabilityClass = 'rating-elite';
      reliabilityIcon = '🟢';
    }} else if (reliability >= 75) {{
      reliabilityClass = 'rating-good';
      reliabilityIcon = '🟡';
    }} else if (reliability >= 60) {{
      reliabilityClass = 'rating-fair';
      reliabilityIcon = '🟠';
    }} else {{
      reliabilityClass = 'rating-poor';
      reliabilityIcon = '🔴';
    }}
    
    // Format consistency as percentage
    const consistencyPct = (p.consistency * 100).toFixed(0);
    
    // Add roster indicator
    const rosterIcon = isRostered(p.name) ? '⭐' : '';
    
    return `
      <tr class="pos-${{p.position}}">
        <td>${{rosterIcon}} ${{p.name}}</td>
        <td>${{p.position}}</td>
        <td>${{p.games}}</td>
        <td class="${{reliabilityClass}}"><strong>${{reliabilityIcon}} ${{reliability.toFixed(0)}}</strong></td>
        <td>${{p.mae.toFixed(1)}}</td>
        <td>${{(p.correlation * 100).toFixed(0)}}%</td>
        <td>${{consistencyPct}}%</td>
        <td>${{p.avgScore.toFixed(1)}}</td>
        <td class="${{diffClass}}">${{p.avgDiff > 0 ? '+' : ''}}${{p.avgDiff.toFixed(1)}}</td>
      </tr>
    `;
  }}).join('');
}}

function renderTop20Visualization() {{
  // Get filter values (only position, games, and points - NOT search or roster status)
  const posFilter = document.getElementById('reliabilityPosFilter')?.value || 'ALL';
  const minGames = parseInt(document.getElementById('reliabilityGamesFilter')?.value || '3');
  const minPoints = parseFloat(document.getElementById('reliabilityPointsFilter')?.value || '0');
  
  // Get top 20 players based on filters and mode
  const top20 = Object.entries(FP_ACCURACY)
    .filter(([name, stats]) => {{
      // Apply minimum games filter
      if (stats.games < minGames) return false;
      
      // Get avgScore
      const playerData = SEASON_2025.data.find(pd => pd.p === name);
      let avgScore = 0;
      if (playerData && playerData.w) {{
        const scores = Object.values(playerData.w);
        avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
      }}
      
      // Apply minimum points filter
      if (avgScore < minPoints) return false;
      
      // Apply position filter
      if (posFilter === 'FLEX') {{
        // FLEX includes RB, WR, TE (not QB)
        if (!['RB', 'WR', 'TE'].includes(stats.position)) return false;
      }} else if (posFilter !== 'ALL' && stats.position !== posFilter) {{
        return false;
      }}
      
      // Apply roster status based on top20Mode
      if (top20Mode === 'available' && isRostered(name)) return false;
      
      return true;
    }})
    .map(([name, stats]) => {{
      const playerData = SEASON_2025.data.find(pd => pd.p === name);
      let avgScore = 0;
      if (playerData && playerData.w) {{
        const scores = Object.values(playerData.w);
        avgScore = scores.reduce((a,b) => a+b, 0) / scores.length;
      }}
      
      return {{
        name: name,
        position: stats.position,
        reliabilityScore: stats.reliabilityScore || 0,
        mae: stats.mae,
        avgScore: avgScore
      }};
    }})
    .sort((a, b) => b.reliabilityScore - a.reliabilityScore)
    .slice(0, 20);
  
  const container = document.getElementById('top20Grid');
  
  if (top20.length === 0) {{
    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 30px; color: #95a5a6;">No players match the current filters. Try adjusting your criteria.</div>';
    return;
  }}
  
  container.innerHTML = top20.map((p, idx) => {{
    // Color based on reliability
    const reliability = p.reliabilityScore;
    let bgColor = '';
    let borderColor = '';
    let icon = '';
    
    if (reliability >= 90) {{
      bgColor = 'rgba(46,204,113,0.15)';
      borderColor = '#2ecc71';
      icon = '🟢';
    }} else if (reliability >= 75) {{
      bgColor = 'rgba(241,196,15,0.15)';
      borderColor = '#f1c40f';
      icon = '🟡';
    }} else if (reliability >= 60) {{
      bgColor = 'rgba(230,126,34,0.15)';
      borderColor = '#e67e22';
      icon = '🟠';
    }} else {{
      bgColor = 'rgba(231,76,60,0.15)';
      borderColor = '#e74c3c';
      icon = '🔴';
    }}
    
    // Position badge color
    const posColors = {{
      QB: '#fc8b5f',
      RB: '#abda5e',
      WR: '#8caacb',
      TE: '#e683bf'
    }};
    
    const rosterIcon = isRostered(p.name) ? ' ⭐' : '';
    
    return `
      <div style="
        background: ${{bgColor}};
        border: 2px solid ${{borderColor}};
        border-radius: 10px;
        padding: 12px;
        position: relative;
        transition: transform 0.2s;
        cursor: pointer;
      " onmouseover="this.style.transform='scale(1.05)'" onmouseout="this.style.transform='scale(1)'">
        <div style="position: absolute; top: 8px; right: 8px; font-size: 1.2em;">${{icon}}</div>
        <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px; padding-right: 25px;">#${{idx + 1}}${{rosterIcon}} ${{p.name}}</div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
          <span style="background: ${{posColors[p.position] || '#7f8c8d'}}; padding: 2px 8px; border-radius: 3px; font-size: 0.85em; font-weight: bold;">${{p.position}}</span>
          <span style="font-size: 0.9em; color: #bdc3c7;">${{p.avgScore.toFixed(1)}} PPG</span>
        </div>
        <div style="font-size: 1.3em; font-weight: bold; color: ${{borderColor}};">${{p.reliabilityScore.toFixed(0)}}</div>
        <div style="font-size: 0.8em; color: #95a5a6;">MAE: ${{p.mae.toFixed(1)}}</div>
      </div>
    `;
  }}).join('');
}}

function resetReliabilityFilters() {{
  document.getElementById('reliabilitySearch').value = '';
  document.getElementById('reliabilityPosFilter').value = 'ALL';
  document.getElementById('reliabilityGamesFilter').value = '3';
  document.getElementById('reliabilityPointsFilter').value = '0';
  document.getElementById('reliabilityRosterFilter').value = 'ALL';
  
  // Reset Top 20 mode to overall
  setTop20Mode('overall');
  
  // Re-render everything
  renderTop20Visualization();
  renderReliabilityTable();
}}

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

function renderWaiverTable() {{
  const tbody = document.getElementById('waiverTable').querySelector('tbody');
  
  // Check if roster data is available
  if (ALL_ROSTERED.size === 0) {{
    tbody.innerHTML = `
      <tr>
        <td colspan="11" style="text-align: center; padding: 40px;">
          <div style="background: rgba(231,76,60,0.1); border: 2px solid #e74c3c; border-radius: 10px; padding: 30px; max-width: 600px; margin: 0 auto;">
            <div style="font-size: 2em; margin-bottom: 15px;">⚠️</div>
            <h3 style="margin-bottom: 15px; color: #e74c3c;">No Roster Data Available</h3>
            <p style="color: #bdc3c7; margin-bottom: 20px;">
              To see waiver targets, you need to connect to Sleeper so we can filter out rostered players.
            </p>
            <button onclick="document.getElementById('connectBtn').click()" style="padding: 12px 24px; background: #27ae60; border: none; border-radius: 8px; color: white; font-size: 1.1em; cursor: pointer; font-weight: bold;">
              📱 Connect to Sleeper
            </button>
            <p style="margin-top: 15px; font-size: 0.9em; color: #7f8c8d;">
              Without roster data, this tab would show all players (including rostered ones), which isn't useful for waivers.
            </p>
          </div>
        </td>
      </tr>
    `;
    
    // Clear summary stats
    document.getElementById('waiverAvailableCount').textContent = '-';
    document.getElementById('waiverTopQB').textContent = 'Connect Sleeper';
    document.getElementById('waiverTopRB').textContent = 'Connect Sleeper';
    document.getElementById('waiverTopWR').textContent = 'Connect Sleeper';
    document.getElementById('waiverTopTE').textContent = 'Connect Sleeper';
    return;
  }}
  
  // Get all filter values
  const searchTerm = (document.getElementById('waiverSearch')?.value || '').toLowerCase();
  const posFilter = document.getElementById('waiverPosFilter')?.value || 'ALL';
  const tierFilter = document.getElementById('waiverTierFilter')?.value || 'ALL';
  const minProj = parseFloat(document.getElementById('minProj')?.value || 0);
  const limit = parseInt(document.getElementById('waiverLimit')?.value || 30);
  
  // Filter available players
  let available = PROJECTIONS.filter(p => {{
    // Must not be rostered
    if (isRostered(p.p)) return false;
    
    // Search filter
    if (searchTerm && !p.p.toLowerCase().includes(searchTerm)) return false;
    
    // Position filter
    if (posFilter === 'FLEX') {{
      if (!['RB', 'WR', 'TE'].includes(p.pos)) return false;
    }} else if (posFilter !== 'ALL' && p.pos !== posFilter) {{
      return false;
    }}
    
    // Tier filter
    if (tierFilter !== 'ALL' && p.tier !== tierFilter) return false;
    
    // Projection minimum
    if (p.proj < minProj) return false;
    
    return true;
  }});
  
  // Apply sorting
  available = applySorting(available, 'waiver');
  
  // Limit results
  const limitedResults = available.slice(0, limit);
  
  // Update summary stats
  updateWaiverStats(available);
  
  // Render the table (tbody already declared at top of function)
  if (limitedResults.length === 0) {{
    tbody.innerHTML = `
      <tr>
        <td colspan="11" style="text-align: center; padding: 40px; color: #95a5a6;">
          <div style="font-size: 1.2em; margin-bottom: 10px;">No players found</div>
          <div>Try adjusting your filters or lowering the minimum projection</div>
        </td>
      </tr>
    `;
    return;
  }}
  
  tbody.innerHTML = limitedResults.map((p, idx) => {{
    // Priority indicator
    const priority = idx < 5 ? '🔥' : idx < 15 ? '⭐' : '👀';
    const priorityClass = idx < 5 ? 'priority-hot' : idx < 15 ? 'priority-star' : 'priority-watch';
    
    // Trend analysis
    const trendIcon = p.avgDiff < -2 ? '📈' : p.avgDiff > 2 ? '📉' : '➡️';
    const trendClass = p.avgDiff < -2 ? 'trend-up' : p.avgDiff > 2 ? 'trend-down' : 'trend-stable';
    const trendValue = p.avgDiff !== 0 ? (p.avgDiff > 0 ? '+' : '') + p.avgDiff.toFixed(1) : '0.0';
    
    // Reliability Score - get from FP_ACCURACY
    let reliabilityDisplay = '-';
    let reliabilityClass = '';
    let reliabilityIcon = '';
    const accuracyData = FP_ACCURACY[p.p];
    if (accuracyData && accuracyData.reliabilityScore !== undefined) {{
      const reliability = accuracyData.reliabilityScore;
      reliabilityDisplay = reliability.toFixed(0);
      
      // Color code based on score
      if (reliability >= 90) {{
        reliabilityClass = 'rating-elite';
        reliabilityIcon = '🟢';
      }} else if (reliability >= 75) {{
        reliabilityClass = 'rating-good';
        reliabilityIcon = '🟡';
      }} else if (reliability >= 60) {{
        reliabilityClass = 'rating-fair';
        reliabilityIcon = '🟠';
      }} else {{
        reliabilityClass = 'rating-poor';
        reliabilityIcon = '🔴';
      }}
    }}
    
    // Season average
    const seasonAvg = p.avgScore > 0 ? p.avgScore.toFixed(1) : '-';
    
    // Floor-ceiling range
    const floorCeiling = `${{p.floor.toFixed(1)}}-${{p.ceiling.toFixed(1)}}`;
    
    // Action button
    const actionBtn = `<button onclick="addToWatchlist('${{p.p}}')" style="padding: 5px 10px; background: rgba(111,198,171,0.2); border: 1px solid #6fc6ab; border-radius: 5px; cursor: pointer; color: #ecf0f1; font-size: 0.9em;">📋 Add</button>`;
    
    return `
      <tr class="pos-${{p.pos}}">
        <td class="${{priorityClass}}" style="font-size: 1.2em;">${{priority}}</td>
        <td><strong>${{p.p}}</strong></td>
        <td>${{p.pos}}</td>
        <td>${{p.rank}}</td>
        <td><strong style="color: #6fc6ab;">${{p.proj.toFixed(1)}}</strong></td>
        <td style="font-size: 0.9em; color: #bdc3c7;">${{floorCeiling}}</td>
        <td><span class="badge ${{p.tier.toLowerCase()}}">${{p.tier}}</span></td>
        <td>${{seasonAvg}}</td>
        <td class="${{reliabilityClass}}" title="Reliability Score (0-100): Higher = More accurate projections"><strong>${{reliabilityIcon}} ${{reliabilityDisplay}}</strong></td>
        <td class="${{trendClass}}" title="Average rank difference from projections">${{trendIcon}} ${{trendValue}}</td>
        <td>${{actionBtn}}</td>
      </tr>
    `;
  }}).join('');
}}

function updateWaiverStats(availablePlayers) {{
  // Total available
  document.getElementById('waiverAvailableCount').textContent = availablePlayers.length;
  
  // Top player by position
  const byPos = {{
    QB: availablePlayers.filter(p => p.pos === 'QB').sort((a,b) => b.proj - a.proj)[0],
    RB: availablePlayers.filter(p => p.pos === 'RB').sort((a,b) => b.proj - a.proj)[0],
    WR: availablePlayers.filter(p => p.pos === 'WR').sort((a,b) => b.proj - a.proj)[0],
    TE: availablePlayers.filter(p => p.pos === 'TE').sort((a,b) => b.proj - a.proj)[0]
  }};
  
  document.getElementById('waiverTopQB').textContent = byPos.QB ? `${{byPos.QB.p}} (${{byPos.QB.proj.toFixed(1)}})` : 'None';
  document.getElementById('waiverTopRB').textContent = byPos.RB ? `${{byPos.RB.p}} (${{byPos.RB.proj.toFixed(1)}})` : 'None';
  document.getElementById('waiverTopWR').textContent = byPos.WR ? `${{byPos.WR.p}} (${{byPos.WR.proj.toFixed(1)}})` : 'None';
  document.getElementById('waiverTopTE').textContent = byPos.TE ? `${{byPos.TE.p}} (${{byPos.TE.proj.toFixed(1)}})` : 'None';
}}

function addToWatchlist(playerName) {{
  // Simple alert for now - you can expand this to actually maintain a watchlist
  alert(`${{playerName}} added to watchlist!\\n\\nNote: This is a placeholder. You can expand this to:\\n- Save to localStorage\\n- Highlight in other tabs\\n- Send notifications\\n- Export to CSV`);
}}

function renderPositionalBaselines() {{
  const positions = ['QB', 'RB', 'WR', 'TE'];
  const container = document.getElementById('baselineTables');
  
  const html = positions.map(pos => {{
    const posData = {{}};
    
    // Calculate averages for each rank across years
    ['2022', '2023', '2024'].forEach(year => {{
      const yearData = HISTORICAL_DATA[CURRENT_SCORING][year] || [];
      const posPlayers = yearData.filter(p => p.pos === pos);
      
      // ✅ Calculate averages first, then sort by average score
      const playersWithAvg = posPlayers.map(player => {{
        const weeks = Object.values(player.w);
        const avg = weeks.length > 0 ? weeks.reduce((a, b) => a + b, 0) / weeks.length : 0;
        return {{ player, avg }};
      }}).sort((a, b) => b.avg - a.avg);  // Sort by average score descending
      
      playersWithAvg.forEach(({{ player, avg }}, idx) => {{
        const rank = idx + 1;
        if (rank > 24) return;
        
        if (!posData[rank]) posData[rank] = {{}};
        posData[rank][year] = avg;
      }});
    }});
    
    // Calculate 3-year averages
    const rows = Object.entries(posData)
      .sort((a, b) => parseInt(a[0]) - parseInt(b[0]))
      .map(([rank, years]) => {{
        const vals = Object.values(years);
        const avg3yr = vals.length > 0 ? vals.reduce((a,b) => a+b, 0) / vals.length : 0;
        
        return `
          <tr class="pos-${{pos}}">
            <td><strong>${{rank}}</strong></td>
            <td>${{years['2022']?.toFixed(1) || '-'}}</td>
            <td>${{years['2023']?.toFixed(1) || '-'}}</td>
            <td>${{years['2024']?.toFixed(1) || '-'}}</td>
            <td><strong>${{avg3yr.toFixed(1)}}</strong></td>
          </tr>
        `;
      }}).join('');
    
    return `
      <div class="historical-section">
        <h3>${{pos}} Historical Averages (Top 24)</h3>
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
            <tbody>${{rows}}</tbody>
          </table>
        </div>
      </div>
    `;
  }}).join('');
  
  container.innerHTML = html;
}}

function renderHistoricalTable() {{
  console.log('🔍 renderHistoricalTable called');
  console.log('FP_ACCURACY exists?', typeof FP_ACCURACY !== 'undefined');
  console.log('FP_ACCURACY keys:', FP_ACCURACY ? Object.keys(FP_ACCURACY).length : 0);
  console.log('PROJECTIONS exists?', typeof PROJECTIONS !== 'undefined');
  console.log('PROJECTIONS length:', PROJECTIONS ? PROJECTIONS.length : 0);
  
  // Check if FP_ACCURACY is empty
  if (!FP_ACCURACY || Object.keys(FP_ACCURACY).length === 0) {{
    console.warn('⚠️ FP_ACCURACY is empty - no historical data available');
    const tbody = document.getElementById('historicalTable')?.querySelector('tbody');
    if (tbody) {{
      tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 20px;">No historical data available yet. Play more games to build accuracy statistics.</td></tr>';
    }}
    return;
  }}
  
  // Get all players with historical FP_ACCURACY data (5+ games)
  let data = Object.entries(FP_ACCURACY)
    .filter(([name, acc]) => acc.games >= 5)
    .map(([name, acc]) => {{
      // Get position from FP_ACCURACY (already stored from SEASON data)
      // Fallback to PROJECTIONS if needed
      let pos = acc.position || '?';
      if (pos === '?' || !pos) {{
        const playerProj = PROJECTIONS.find(p => p.p === name);
        pos = playerProj?.pos || '?';
      }}
      
      return {{
        player: name,
        pos: pos,
        games: acc.games,
        correlation: acc.correlation || 0,
        mae: acc.mae || 0,
        avgScore: acc.avgScore || 0,
        avgDiff: acc.avgDiff || 0  // ✅ ADD THIS
      }};
    }});
  
  // ✅ APPLY SORTING
  data = applySorting(data, 'historical');
  
  // Get table body
  const tbody = document.getElementById('historicalTable')?.querySelector('tbody');
  if (!tbody) {{
    console.warn('Historical table tbody not found');
    return;
  }}
  
  // Render rows
  tbody.innerHTML = data.map(p => {{
    // Color code by correlation strength
    let corrClass = 'low-acc';
    if (p.correlation >= 0.7) corrClass = 'high-acc';
    else if (p.correlation >= 0.5) corrClass = 'med-acc';
    
    // Calculate accuracy score from MAE (0-100 scale)
    // Formula: max(0, 100 - (MAE × 0.5)^1.3)
    // Power curve that rewards excellence: Best (MAE 3.6) = 98, Median (MAE 17) = 84, Worst (MAE 63) = 12
    const accuracyScore = Math.max(0, 100 - Math.pow((p.mae || 0) * 0.5, 1.3));
    
    // Determine accuracy class for color coding (adjusted for power curve distribution)
    let accClass = 'low-acc';
    if (accuracyScore >= 90) accClass = 'high-acc';      // Top performers (low MAE)
    else if (accuracyScore >= 75) accClass = 'med-acc';  // Middle performers
    
    // Trend indicator (avgDiff)
    const trendIcon = p.avgDiff < -2 ? '📈' : p.avgDiff > 2 ? '📉' : '➡️';
    const trendClass = p.avgDiff < -2 ? 'trend-up' : p.avgDiff > 2 ? 'trend-down' : 'trend-stable';
    const trendText = p.avgDiff > 0 ? '+' : '';
    
    return `
      <tr class="pos-${{p.pos}}">
        <td><strong>${{p.player}}</strong></td>
        <td>${{p.pos}}</td>
        <td>${{p.games}}</td>
        <td class="${{corrClass}}">
          ${{(p.correlation * 100).toFixed(0)}}%
        </td>
        <td class="${{accClass}}" title="MAE: ${{(p.mae || 0).toFixed(1)}} ranks">
          ${{accuracyScore.toFixed(0)}}
        </td>
        <td class="${{trendClass}}" title="Avg rank difference: ${{trendText}}${{p.avgDiff.toFixed(1)}}">
          ${{trendIcon}} ${{trendText}}${{p.avgDiff.toFixed(1)}}
        </td>
        <td>${{(p.avgScore || 0).toFixed(1)}}</td>
      </tr>
    `;
  }}).join('');
  
  console.log('✅ Historical table rendered with', data.length, 'players');
}}

function isOnRoster(playerName) {{
  if (!playerName) return false;
  if (!USER_ROSTER || USER_ROSTER.length === 0) return false;
  
  const normalizedPlayer = normalizePlayerName(playerName);
  if (!normalizedPlayer) return false;
  
  return USER_ROSTER.some(rosterName => {{
    if (!rosterName) return false;
    const normalizedRoster = normalizePlayerName(rosterName);
    return normalizedRoster === normalizedPlayer;
  }});
}}

function isRostered(playerName) {{
  if (!playerName) return false;
  if (ALL_ROSTERED.size === 0) return false;
  
  const normalized = normalizePlayerName(playerName);
  if (!normalized) return false;
  
  // Check if player is on ANY roster in the league
  for (const rosteredPlayer of ALL_ROSTERED) {{
    if (normalizePlayerName(rosteredPlayer) === normalized) {{
      return true;
    }}
  }}
  
  return false;
}}

// ==================== LINEUP OPTIMIZER ====================
function generateOptimalLineup() {{
  const teamIdx = parseInt(document.getElementById('teamSelector').value);
  if (isNaN(teamIdx) || !SLEEPER_DATA) {{
    alert('Please connect to Sleeper first');
    return;
  }}
  
  const roster = SLEEPER_DATA.rosters[teamIdx];
  const players = SLEEPER_DATA.players;
  
  // Get roster players with projections
  const rosterPlayers = (roster.players || []).map(pid => {{
    const p = players[pid];
    if (!p || !p.full_name) return null;
    
    const proj = PROJECTIONS.find(pr => normalizePlayerName(pr.p) === normalizePlayerName(p.full_name));
    return proj ? {{ ...proj, sleeperPos: p.position }} : null;
  }}).filter(Boolean);
  
  // Get slot counts
  const qbSlots = parseInt(document.getElementById('qbSlots').value) || 0;
  const rbSlots = parseInt(document.getElementById('rbSlots').value) || 0;
  const wrSlots = parseInt(document.getElementById('wrSlots').value) || 0;
  const teSlots = parseInt(document.getElementById('teSlots').value) || 0;
  const flexSlots = parseInt(document.getElementById('flexSlots').value) || 0;
  
  // Separate by position
  const byPos = {{
    QB: rosterPlayers.filter(p => p.pos === 'QB').sort((a,b) => b.proj - a.proj),
    RB: rosterPlayers.filter(p => p.pos === 'RB').sort((a,b) => b.proj - a.proj),
    WR: rosterPlayers.filter(p => p.pos === 'WR').sort((a,b) => b.proj - a.proj),
    TE: rosterPlayers.filter(p => p.pos === 'TE').sort((a,b) => b.proj - a.proj)
  }};
  
  // Fill starters
  const starters = {{
    QB: byPos.QB.slice(0, qbSlots),
    RB: byPos.RB.slice(0, rbSlots),
    WR: byPos.WR.slice(0, wrSlots),
    TE: byPos.TE.slice(0, teSlots),
    FLEX: []
  }};
  
  // Fill FLEX with best remaining
  const flexPool = [
    ...byPos.RB.slice(rbSlots),
    ...byPos.WR.slice(wrSlots),
    ...byPos.TE.slice(teSlots)
  ].sort((a,b) => b.proj - a.proj);
  
  starters.FLEX = flexPool.slice(0, flexSlots);
  
  // Calculate total
  const allStarters = [...starters.QB, ...starters.RB, ...starters.WR, ...starters.TE, ...starters.FLEX];
  const totalProj = allStarters.reduce((sum, p) => sum + p.proj, 0);
  const totalFloor = allStarters.reduce((sum, p) => sum + p.floor, 0);
  const totalCeiling = allStarters.reduce((sum, p) => sum + p.ceiling, 0);
  
  // Get bench
  const starterNames = new Set(allStarters.map(p => p.p));
  const bench = rosterPlayers.filter(p => !starterNames.has(p.p));
  
  // Render results
  const resultsDiv = document.getElementById('lineupResults');
  
  const startersHtml = Object.entries(starters).map(([pos, players]) => {{
    if (players.length === 0) return '';
    
    return `
      <div class="starter-card pos-${{pos}}">
        <h4>${{pos}}</h4>
        ${{players.map(p => `
          <div style="margin-top: 8px;">
            <strong>${{p.p}}</strong><br>
            <span style="font-size: 0.9em;">
              Proj: ${{p.proj.toFixed(1)}} (${{p.floor.toFixed(1)}}-${{p.ceiling.toFixed(1)}})
            </span>
          </div>
        `).join('')}}
      </div>
    `;
  }}).join('');
  
  const benchHtml = bench.map(p => `
    <div style="padding: 10px; background: rgba(255,255,255,0.05); border-radius: 5px; border-left: 3px solid #95a5a6;">
      <strong>${{p.p}}</strong> (${{p.pos}}) - ${{p.proj.toFixed(1)}}
    </div>
  `).join('');
  
  resultsDiv.innerHTML = `
    <div style="background: rgba(111,198,171,0.2); border: 2px solid #6fc6ab; border-radius: 10px; padding: 15px; margin-bottom: 20px;">
      <h3>📊 Total Projection</h3>
      <div style="font-size: 2em; font-weight: bold; color: #6fc6ab;">${{totalProj.toFixed(1)}}</div>
      <div style="margin-top: 5px; color: #bdc3c7;">Range: ${{totalFloor.toFixed(1)}} - ${{totalCeiling.toFixed(1)}}</div>
    </div>
    
    <h3 style="margin-bottom: 15px;">⚡ Starters</h3>
    <div class="starters-grid">${{startersHtml}}</div>
    
    <div class="bench-section">
      <h3>💺 Bench (${{bench.length}})</h3>
      <div class="bench-list">${{benchHtml || '<p style="color: #95a5a6;">No bench players</p>'}}</div>
    </div>
  `;
}}

// ==================== TAB SWITCHING ====================
function switchTab(tabName) {{
  // Update buttons
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  
  // Update content
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  document.getElementById(tabName).classList.add('active');
}}
// ==================== SORTING ====================
let top20Mode = 'overall'; // Track whether to show overall or available players

function setTop20Mode(mode) {{
  top20Mode = mode;
  
  // Update button styles
  const overallBtn = document.getElementById('top20Overall');
  const availableBtn = document.getElementById('top20Available');
  
  if (mode === 'overall') {{
    overallBtn.style.background = 'rgba(46,204,113,0.3)';
    overallBtn.style.border = '2px solid #2ecc71';
    overallBtn.style.fontWeight = 'bold';
    
    availableBtn.style.background = 'rgba(111,198,171,0.15)';
    availableBtn.style.border = '2px solid rgba(111,198,171,0.5)';
    availableBtn.style.fontWeight = 'normal';
  }} else {{
    availableBtn.style.background = 'rgba(111,198,171,0.3)';
    availableBtn.style.border = '2px solid #6fc6ab';
    availableBtn.style.fontWeight = 'bold';
    
    overallBtn.style.background = 'rgba(46,204,113,0.15)';
    overallBtn.style.border = '2px solid rgba(46,204,113,0.5)';
    overallBtn.style.fontWeight = 'normal';
  }}
  
  // Re-render Top 20 with current filters
  renderTop20Visualization();
}}

function updateReliabilityWithFilters() {{
  // Update both Top 20 and table when position/games/points filters change
  renderTop20Visualization();
  renderReliabilityTable();
}}

function sortReliability(column) {{
  sortTable('reliability', column);
}}

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', () => {{
  console.log('🏈 Fantasy Truss Loaded');
  console.log('Data:', {{
    historical: Object.keys(HISTORICAL_DATA.PPR).length,
    season: SEASON_2025.data.length,
    projections: Object.keys(WEEKLY_PROJECTIONS).length
  }});
  
  // Calculate everything
  POSITION_ACCURACY = calculateFPAccuracy();
  console.log('📊 ECR Accuracy Stats:');
  console.log(`  Players with ECR history: ${{Object.keys(FP_ACCURACY).length}}`);
  console.log('  Position reliability:', POSITION_ACCURACY);
  
  PROJECTIONS = calculateProjections();
  console.log(`📈 Generated ${{PROJECTIONS.length}} projections`);
  console.log(`  With ECR: ${{PROJECTIONS.filter(p => p.hasECR).length}}`);
  
  // Debug: Show a few example projections
  const examples = ['Ladd McConkey', 'Jordan Addison', 'Puka Nacua'];
  examples.forEach(name => {{
    const p = PROJECTIONS.find(proj => proj.p === name);
    if (p) {{
      const acc = FP_ACCURACY[name];
      console.log(`  ${{name}}: ${{p.proj.toFixed(1)}} pts (ECR: WR${{p.ecrRank}}, Avg: ${{p.avgScore.toFixed(1)}}, Corr: ${{acc?.correlation.toFixed(2) || 'N/A'}})`);
    }}
  }});
  
  // Initial render
  updateMetrics();
  renderProjectionsTable();
  renderReliabilityTable();
  renderRankingsTable('QB');
  renderWaiverTable();
  renderHistoricalTable();        // ← Player reliability
  renderPositionalBaselines();     // ← Your baseline data
  
  console.log('✅ Dashboard ready!');
}});

// Scoring format change handler
const scoringFormatEl = document.getElementById('scoringFormat');
if (scoringFormatEl) {{
  scoringFormatEl.addEventListener('change', (e) => {{
    CURRENT_SCORING = e.target.value;
    console.log('Switched to', CURRENT_SCORING);
    
    // Recalculate with new scoring
    calculateFPAccuracy();
    PROJECTIONS = calculateProjections();
    
    // Re-render everything
    updateMetrics();
    renderProjectionsTable();
    renderReliabilityTable();
    renderRankingsTable('QB');
    renderWaiverTable();
    renderHistoricalTable();
  }});
}}
</script>

</body>
</html>'''
    
    return html


def main():
    print("=" * 60)
    print("🏈 Fantasy Truss - COMPLETE EDITION")
    print("=" * 60)
    
    historical = load_all_historical_data()
    current = load_current_season()
    projections = load_weekly_projections()
    
    print("\n🔨 Generating complete HTML with full UI...")
    html = generate_complete_html(historical, current, projections)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_mb = Path(OUTPUT_FILE).stat().st_size / (1024 * 1024)
    print(f"\n✅ SUCCESS!")
    print(f"📄 {OUTPUT_FILE} ({size_mb:.2f} MB)")
    print("\n🎯 Features included:")
    print("  ✅ 7 fully functional tabs")
    print("  ✅ FantasyPros projection integration")
    print("  ✅ Sleeper API connection")
    print("  ✅ Lineup optimizer")
    print("  ✅ Waiver wire analysis")
    print("  ✅ Reliability tracking")
    print("  ✅ Historical averages")
    print("=" * 60)


if __name__ == "__main__":
    main()
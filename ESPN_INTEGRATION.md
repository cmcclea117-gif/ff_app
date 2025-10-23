# ESPN API Integration Guide

## 🎯 Goal
Add ESPN Fantasy Football API support to the dashboard alongside existing Sleeper integration.

---

## 📚 Resources

### Official & Community Resources:
1. **Reddit Discussion**: https://www.reddit.com/r/fantasyfootball/comments/im6mui/espn_api_question/
2. **Public ESPN API Repo**: https://github.com/pseudo-r/Public-ESPN-API
3. **ESPN Fantasy API Docs** (unofficial): Various community documentation

### Key API Endpoints:
```
Base URL: https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{leagueId}

Common Views:
- mRoster: Roster information
- mTeam: Team details
- mMatchup: Weekly matchups
- mSettings: League settings
- kona_player_info: Player information
```

---

## 🔑 ESPN API Basics

### Finding Your League ID:
1. Go to your ESPN fantasy league
2. Look at the URL: `https://fantasy.espn.com/football/league?leagueId=123456789`
3. Your league ID is: `123456789`

### Public vs Private Leagues:
- **Public leagues**: No authentication needed ✅
- **Private leagues**: Requires cookies (swid + espn_s2) 🔐

### Getting Cookies for Private Leagues:
1. Open ESPN Fantasy in Chrome/Firefox
2. Press F12 (Developer Tools)
3. Go to "Application" tab (Chrome) or "Storage" tab (Firefox)
4. Find Cookies → `https://fantasy.espn.com`
5. Copy these two values:
   - `swid`: Looks like `{ABC123-DEF456-...}`
   - `espn_s2`: Long string (200+ characters)

---

## 🏗️ Implementation Architecture

### Current State (Sleeper Only):
```javascript
// Sleeper API client
async function connectToSleeper() {
  const username = document.getElementById('sleeperUsername').value;
  // Fetch user → leagues → rosters
  USER_ROSTER = [...players];
}
```

### Desired State (Sleeper + ESPN):
```javascript
// Unified API client
async function connectToLeague(platform) {
  if (platform === 'sleeper') {
    return await connectToSleeper();
  } else if (platform === 'espn') {
    return await connectToESPN();
  }
}
```

---

## 📋 Step-by-Step Implementation

### Phase 1: UI Changes

**Add ESPN connection option** (modify HTML):
```html
<div id="leagueConnection">
  <label>Platform:</label>
  <select id="platformSelector">
    <option value="sleeper">Sleeper</option>
    <option value="espn">ESPN</option>
  </select>
  
  <!-- Sleeper fields -->
  <div id="sleeperFields">
    <input type="text" id="sleeperUsername" placeholder="Sleeper Username">
    <input type="text" id="leagueId" placeholder="League ID">
  </div>
  
  <!-- ESPN fields -->
  <div id="espnFields" style="display:none;">
    <input type="text" id="espnLeagueId" placeholder="ESPN League ID">
    <input type="text" id="espnSwid" placeholder="SWID (for private leagues)">
    <input type="text" id="espnS2" placeholder="espn_s2 (for private leagues)">
  </div>
  
  <button onclick="connectToLeague()">Connect</button>
</div>

<script>
// Toggle fields based on platform
document.getElementById('platformSelector').addEventListener('change', (e) => {
  if (e.target.value === 'sleeper') {
    document.getElementById('sleeperFields').style.display = 'block';
    document.getElementById('espnFields').style.display = 'none';
  } else {
    document.getElementById('sleeperFields').style.display = 'none';
    document.getElementById('espnFields').style.display = 'block';
  }
});
</script>
```

---

### Phase 2: ESPN API Client

**Add to JavaScript section**:

```javascript
// ESPN API Configuration
const ESPN_BASE_URL = 'https://fantasy.espn.com/apis/v3/games/ffl/seasons';
const CURRENT_YEAR = 2025;

async function connectToESPN() {
  const leagueId = document.getElementById('espnLeagueId').value.trim();
  const swid = document.getElementById('espnSwid').value.trim();
  const espn_s2 = document.getElementById('espnS2').value.trim();
  
  if (!leagueId) {
    alert('Please enter your ESPN League ID');
    return;
  }
  
  try {
    // Fetch league data
    const leagueData = await fetchESPNLeague(leagueId, swid, espn_s2);
    
    // Find user's team
    const userTeam = await selectESPNTeam(leagueData.teams);
    
    // Extract roster
    USER_ROSTER = parseESPNRoster(userTeam, leagueData.players);
    
    // Update UI
    document.getElementById('connectionStatus').innerHTML = 
      `✅ Connected! Found ${USER_ROSTER.length} players on your roster`;
    
    // Re-render tables
    renderProjectionsTable();
    
  } catch (error) {
    console.error('ESPN connection error:', error);
    alert('Failed to connect to ESPN. Check your League ID and cookies.');
  }
}

async function fetchESPNLeague(leagueId, swid, espn_s2) {
  const url = `${ESPN_BASE_URL}/${CURRENT_YEAR}/segments/0/leagues/${leagueId}?view=mRoster&view=mTeam&view=kona_player_info`;
  
  const headers = {};
  
  // Add cookies if provided (for private leagues)
  if (swid && espn_s2) {
    headers['Cookie'] = `swid=${swid}; espn_s2=${espn_s2}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers: headers,
    credentials: swid ? 'include' : 'omit'
  });
  
  if (!response.ok) {
    throw new Error(`ESPN API error: ${response.status}`);
  }
  
  return await response.json();
}

async function selectESPNTeam(teams) {
  // If only one team, return it
  if (teams.length === 1) {
    return teams[0];
  }
  
  // If multiple teams, let user choose
  const teamNames = teams.map((t, i) => `${i + 1}. ${t.name || t.location + ' ' + t.nickname}`);
  const choice = prompt(`You have multiple teams. Select one:\n${teamNames.join('\n')}`);
  const index = parseInt(choice) - 1;
  
  if (index >= 0 && index < teams.length) {
    return teams[index];
  }
  
  throw new Error('Invalid team selection');
}

function parseESPNRoster(team, playersData) {
  const roster = [];
  
  // ESPN roster is in team.roster.entries
  const entries = team.roster?.entries || [];
  
  entries.forEach(entry => {
    const playerId = entry.playerId;
    const playerInfo = entry.playerPoolEntry?.player || {};
    
    // Extract player name
    const fullName = playerInfo.fullName || '';
    
    // Only include active roster spots (not bench/IR if filtering)
    const lineupSlot = entry.lineupSlotId;
    
    roster.push({
      name: fullName,
      espnId: playerId,
      position: getESPNPosition(playerInfo.defaultPositionId),
      lineupSlot: lineupSlot
    });
  });
  
  console.log(`Parsed ESPN roster: ${roster.length} players`);
  return roster;
}

function getESPNPosition(positionId) {
  // ESPN position IDs
  const positions = {
    1: 'QB',
    2: 'RB',
    3: 'WR',
    4: 'TE',
    5: 'K',
    16: 'D/ST'
  };
  
  return positions[positionId] || 'FLEX';
}
```

---

### Phase 3: Unified Roster Handling

**Modify existing functions**:

```javascript
function isRostered(playerName) {
  if (!USER_ROSTER || USER_ROSTER.length === 0) return false;
  
  // Normalize names for comparison
  const normalized = normalizePlayerName(playerName);
  
  return USER_ROSTER.some(p => {
    // Handle both Sleeper format (string) and ESPN format (object)
    const rosterName = typeof p === 'string' ? p : p.name;
    return normalizePlayerName(rosterName) === normalized;
  });
}

async function connectToLeague() {
  const platform = document.getElementById('platformSelector').value;
  
  if (platform === 'sleeper') {
    await connectToSleeper();
  } else if (platform === 'espn') {
    await connectToESPN();
  }
}
```

---

## 🔬 Testing Steps

### 1. Test with Public League (No Auth):
```javascript
// In browser console
const testLeagueId = '123456789'; // Use a public league ID
const url = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/2025/segments/0/leagues/${testLeagueId}?view=mRoster`;
fetch(url).then(r => r.json()).then(console.log);
```

### 2. Test with Your League:
1. Enter your ESPN League ID
2. If private, add your cookies
3. Click "Connect"
4. Verify roster appears

### 3. Check Console:
```javascript
// Should see:
console.log(USER_ROSTER);
// [
//   {name: "Patrick Mahomes", espnId: 123, position: "QB"},
//   {name: "Christian McCaffrey", espnId: 456, position: "RB"},
//   ...
// ]
```

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Errors
**Error**: "Access-Control-Allow-Origin blocked"

**Solution**: ESPN API should allow CORS, but if blocked:
```javascript
// Use a CORS proxy (last resort)
const proxyUrl = 'https://cors-anywhere.herokuapp.com/';
const url = proxyUrl + espnUrl;
```

### Issue 2: 401 Unauthorized (Private League)
**Error**: HTTP 401

**Solution**: 
- Make sure swid and espn_s2 cookies are correct
- Cookies expire - may need to refresh them periodically
- Try accessing the league in ESPN first, then copying cookies

### Issue 3: Player Names Don't Match
**Error**: ESPN player "Patrick Mahomes" doesn't match FantasyPros "Patrick Mahomes II"

**Solution**: Enhance `normalizePlayerName()`:
```javascript
function normalizePlayerName(name) {
  if (!name) return '';
  return name
    .toLowerCase()
    .trim()
    .replace(/\./g, '')
    .replace(/'/g, '')
    .replace(/\s+/g, ' ')
    .replace(/\s+(jr|sr|ii|iii|iv)$/i, '') // Remove suffixes
    .replace(/\s+/g, '');
}
```

### Issue 4: Can't Find Roster Data
**Error**: `entries` is undefined

**Solution**: Check API response structure:
```javascript
console.log('Full response:', leagueData);
console.log('Teams:', leagueData.teams);
console.log('Team 0:', leagueData.teams[0]);
console.log('Roster:', leagueData.teams[0].roster);
```

---

## 📊 ESPN API Response Structure

### League Data:
```json
{
  "id": 123456789,
  "settings": {...},
  "teams": [
    {
      "id": 1,
      "name": "Team Name",
      "location": "Team",
      "nickname": "Name",
      "roster": {
        "entries": [
          {
            "playerId": 3139477,
            "lineupSlotId": 0,
            "playerPoolEntry": {
              "player": {
                "fullName": "Patrick Mahomes",
                "defaultPositionId": 1,
                "stats": {...}
              }
            }
          }
        ]
      }
    }
  ]
}
```

### Lineup Slot IDs:
```javascript
const LINEUP_SLOTS = {
  0: 'QB',
  2: 'RB',
  4: 'WR',
  6: 'TE',
  16: 'D/ST',
  17: 'K',
  20: 'BENCH',
  21: 'IR',
  23: 'FLEX'
};
```

---

## 🎯 Implementation Checklist

### Phase 1: Basic Connection
- [ ] Add platform selector UI
- [ ] Add ESPN input fields
- [ ] Implement `fetchESPNLeague()`
- [ ] Test with public league
- [ ] Display success/error messages

### Phase 2: Roster Parsing
- [ ] Implement `parseESPNRoster()`
- [ ] Handle team selection (if multiple)
- [ ] Map ESPN player names to dashboard format
- [ ] Test with real roster

### Phase 3: Integration
- [ ] Update `isRostered()` to handle both formats
- [ ] Update roster display
- [ ] Test projection filtering
- [ ] Verify "My Roster" vs "Available" works

### Phase 4: Polish
- [ ] Save ESPN credentials to localStorage
- [ ] Auto-reconnect on page load
- [ ] Better error messages
- [ ] Loading indicators
- [ ] Cookie help documentation

---

## 💡 Future Enhancements

### After Basic Integration Works:
1. **Multi-league support**: Connect to multiple ESPN leagues
2. **Lineup suggestions**: Use ESPN lineup slots to suggest starters
3. **Trade analyzer**: Compare players from your roster vs others
4. **Weekly matchup**: Show opponent's roster
5. **Schedule analysis**: Use ESPN schedule data

### Advanced Features:
- **Auto-refresh**: Check for roster changes
- **Notifications**: Alert when projected player is available
- **Historical league data**: Import past seasons from ESPN
- **Draft integration**: Pre-draft rankings for ESPN leagues

---

## 📝 Code Location in Generator

Add the ESPN integration code to `generate_dashboard_fixed.py` in the JavaScript section, around line ~850 (after Sleeper code):

```python
# In generate_dashboard_fixed.py, JavaScript section:

// ==================== SLEEPER API ====================
function connectToSleeper() { ... }

// ==================== ESPN API ====================
async function connectToESPN() {
  // Add ESPN code here
}

// ==================== UNIFIED ROSTER ====================
async function connectToLeague() {
  // Platform-agnostic connection
}
```

---

## 🚀 Next Steps

1. **Gather user info**:
   - ESPN League ID
   - Is it public or private?
   - If private, get swid and espn_s2 cookies

2. **Test API access**:
   - Try fetching league data in console
   - Verify roster structure

3. **Implement basic version**:
   - Add UI elements
   - Implement ESPN client
   - Test with user's actual league

4. **Iterate**:
   - Fix name matching issues
   - Handle edge cases
   - Polish UI

---

This should get ESPN integration up and running! Let me know your ESPN League ID and whether it's public/private, and we can test the API access! 🏈

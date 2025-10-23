// Popup logic for ESPN Roster Connector extension

let currentRoster = null;

// Load saved config on popup open
document.addEventListener('DOMContentLoaded', async () => {
  // Load saved settings
  const settings = await chrome.storage.sync.get([
    'leagueId', 'seasonYear', 'swid', 'espnS2'
  ]);
  
  if (settings.leagueId) document.getElementById('leagueId').value = settings.leagueId;
  if (settings.seasonYear) document.getElementById('seasonYear').value = settings.seasonYear;
  if (settings.swid) document.getElementById('swid').value = settings.swid;
  if (settings.espnS2) document.getElementById('espnS2').value = settings.espnS2;
  
  // Load cached roster if exists
  const cached = await chrome.storage.local.get(['cachedRoster']);
  if (cached.cachedRoster) {
    currentRoster = cached.cachedRoster;
    displayRoster(currentRoster);
  }
  
  // Add event listeners
  document.getElementById('fetchRoster').addEventListener('click', fetchRoster);
  document.getElementById('clearData').addEventListener('click', clearData);
  document.getElementById('injectRoster')?.addEventListener('click', injectRoster);
});

async function fetchRoster() {
  const leagueId = document.getElementById('leagueId').value.trim();
  const seasonYear = document.getElementById('seasonYear').value;
  const swid = document.getElementById('swid').value.trim();
  const espnS2 = document.getElementById('espnS2').value.trim();
  
  const statusDiv = document.getElementById('status');
  const button = document.getElementById('fetchRoster');
  
  if (!leagueId) {
    showStatus('error', 'Please enter your ESPN League ID');
    return;
  }
  
  // Save settings
  await chrome.storage.sync.set({ leagueId, seasonYear, swid, espnS2 });
  
  // Show loading
  button.disabled = true;
  button.textContent = '⏳ Fetching...';
  showStatus('info', 'Connecting to ESPN...');
  
  try {
    // Build URL
    const url = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/${seasonYear}/segments/0/leagues/${leagueId}?view=mRoster&view=mTeam`;
    
    // Build headers with cookies if provided
    const headers = {};
    if (swid && espnS2) {
      headers['Cookie'] = `swid=${swid}; espn_s2=${espnS2}`;
    }
    
    // Fetch from ESPN (no CORS in extension!)
    const response = await fetch(url, {
      method: 'GET',
      headers: headers,
      credentials: swid ? 'include' : 'omit'
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Private league - please add your SWID and espn_s2 cookies');
      } else if (response.status === 404) {
        throw new Error(`League ${leagueId} not found for ${seasonYear}`);
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    }
    
    const data = await response.json();
    
    // Parse roster
    const roster = parseRoster(data);
    
    if (!roster) {
      throw new Error('Failed to parse roster data');
    }
    
    // Save to cache
    currentRoster = roster;
    await chrome.storage.local.set({ cachedRoster: roster });
    
    // Display
    displayRoster(roster);
    showStatus('success', `✅ Found ${roster.roster.length} players!`);
    
  } catch (error) {
    console.error('Fetch error:', error);
    showStatus('error', `❌ ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = 'Fetch My Roster';
  }
}

function parseRoster(data) {
  const teams = data.teams || [];
  
  if (teams.length === 0) {
    throw new Error('No teams found in league');
  }
  
  // For now, use the first team
  // TODO: Let user select if multiple teams
  const team = teams[0];
  const teamName = `${team.location || ''} ${team.nickname || ''}`.trim();
  
  const entries = team.roster?.entries || [];
  
  const positionMap = {
    1: 'QB',
    2: 'RB',
    3: 'WR',
    4: 'TE',
    5: 'K',
    16: 'D/ST'
  };
  
  const roster = entries.map(entry => {
    const player = entry.playerPoolEntry?.player || {};
    return {
      name: player.fullName || 'Unknown',
      position: positionMap[player.defaultPositionId] || 'FLEX',
      espnId: entry.playerId,
      lineupSlot: entry.lineupSlotId
    };
  });
  
  return {
    teamName: teamName,
    roster: roster,
    leagueId: data.id,
    season: data.seasonId,
    fetchedAt: new Date().toISOString()
  };
}

function displayRoster(roster) {
  const section = document.getElementById('rosterSection');
  const info = document.getElementById('rosterInfo');
  
  // Show section
  section.style.display = 'block';
  
  // Display info
  const playersByPos = {};
  roster.roster.forEach(p => {
    if (!playersByPos[p.position]) playersByPos[p.position] = [];
    playersByPos[p.position].push(p.name);
  });
  
  let html = `<strong>${roster.teamName}</strong><br>`;
  html += `${roster.roster.length} players • ${roster.season}<br><br>`;
  
  Object.keys(playersByPos).sort().forEach(pos => {
    html += `<strong>${pos}:</strong> ${playersByPos[pos].length}<br>`;
  });
  
  info.innerHTML = html;
}

async function injectRoster() {
  if (!currentRoster) {
    showStatus('error', 'No roster loaded. Fetch your roster first.');
    return;
  }
  
  const button = document.getElementById('injectRoster');
  button.disabled = true;
  button.textContent = '📤 Sending...';
  
  try {
    // Get active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) {
      throw new Error('No active tab found');
    }
    
    // Send roster to content script
    await chrome.tabs.sendMessage(tab.id, {
      type: 'INJECT_ESPN_ROSTER',
      roster: currentRoster
    });
    
    showStatus('success', '✅ Roster sent to dashboard!');
    
    // Close popup after 1 second
    setTimeout(() => window.close(), 1000);
    
  } catch (error) {
    console.error('Inject error:', error);
    showStatus('error', `❌ ${error.message}\nMake sure you're on the dashboard page.`);
  } finally {
    button.disabled = false;
    button.textContent = '📤 Send to Dashboard';
  }
}

async function clearData() {
  if (confirm('Clear all saved data including league info and cached roster?')) {
    await chrome.storage.sync.clear();
    await chrome.storage.local.clear();
    
    // Clear form
    document.getElementById('leagueId').value = '';
    document.getElementById('swid').value = '';
    document.getElementById('espnS2').value = '';
    
    // Hide roster
    document.getElementById('rosterSection').style.display = 'none';
    currentRoster = null;
    
    showStatus('info', 'All data cleared');
  }
}

function showStatus(type, message) {
  const statusDiv = document.getElementById('status');
  statusDiv.className = `status ${type}`;
  statusDiv.textContent = message;
  statusDiv.style.display = 'block';
}

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
  document.getElementById('autoDetectCookies').addEventListener('click', autoDetectCookies);
  document.getElementById('autoDetectLeagueId').addEventListener('click', autoDetectLeagueId);
});

async function autoDetectLeagueId() {
  const button = document.getElementById('autoDetectLeagueId');
  const leagueIdInput = document.getElementById('leagueId');
  
  button.disabled = true;
  button.textContent = '...';
  
  try {
    // Get current active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab || !tab.url) {
      throw new Error('No active tab found');
    }
    
    // Check if it's an ESPN Fantasy URL
    if (!tab.url.includes('fantasy.espn.com')) {
      throw new Error('Current tab is not ESPN Fantasy. Open your league page first.');
    }
    
    // Extract league ID from URL
    // URL format: https://fantasy.espn.com/football/league?leagueId=123456
    const match = tab.url.match(/leagueId=(\d+)/);
    
    if (!match) {
      throw new Error('Could not find League ID in URL. Make sure you\'re on your league page.');
    }
    
    const leagueId = match[1];
    leagueIdInput.value = leagueId;
    
    // Save to storage
    await chrome.storage.sync.set({ leagueId });
    
    showStatus('success', `✅ Found League ID: ${leagueId}`);
    
  } catch (error) {
    console.error('Auto-detect league ID error:', error);
    showStatus('error', `❌ ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = '🔍 From Tab';
  }
}

async function autoDetectCookies() {
  const button = document.getElementById('autoDetectCookies');
  const swidInput = document.getElementById('swid');
  const espnS2Input = document.getElementById('espnS2');
  
  button.disabled = true;
  button.textContent = '🔍 Detecting...';
  
  try {
    console.log('Auto-detecting ESPN cookies...');
    
    // Get all ESPN cookies
    const cookies = await chrome.cookies.getAll({
      domain: '.espn.com'
    });
    
    console.log('Found cookies:', cookies.map(c => c.name));
    
    // Find SWID and espn_s2
    const swidCookie = cookies.find(c => c.name === 'swid');
    const espnS2Cookie = cookies.find(c => c.name === 'espn_s2');
    
    if (!swidCookie || !espnS2Cookie) {
      // Check if user has ESPN open
      const espnTabs = await chrome.tabs.query({ url: 'https://*.espn.com/*' });
      
      if (espnTabs.length === 0) {
        throw new Error('No ESPN cookies found. Please open ESPN Fantasy in another tab and log in first.');
      } else {
        throw new Error('Cookies not found. Make sure you\'re logged into ESPN Fantasy.');
      }
    }
    
    // Fill in the form
    swidInput.value = swidCookie.value;
    espnS2Input.value = espnS2Cookie.value;
    
    // Save to storage
    await chrome.storage.sync.set({
      swid: swidCookie.value,
      espnS2: espnS2Cookie.value
    });
    
    showStatus('success', '✅ Cookies auto-detected! You can now fetch your roster.');
    
    console.log('Auto-detect successful!');
    
  } catch (error) {
    console.error('Auto-detect error:', error);
    showStatus('error', `❌ ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = '🔍 Auto-Detect ESPN Cookies';
  }
}

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
  showStatus('info', 'Connecting to ESPN via background script...');
  
  try {
    // Delegate to background script which has better cookie handling
    console.log('Popup: Sending fetch request to background script...');
    
    const response = await chrome.runtime.sendMessage({
      type: 'FETCH_ESPN_ROSTER',
      config: { leagueId, seasonYear, swid, espnS2 }
    });
    
    console.log('Popup: Got response from background:', response);
    
    if (!response.success) {
      throw new Error(response.error);
    }
    
    const data = response.roster;
    
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
    console.error('Popup: Fetch error:', error);
    showStatus('error', `❌ ${error.message || error}`);
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

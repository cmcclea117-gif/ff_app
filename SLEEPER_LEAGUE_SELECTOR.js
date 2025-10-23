// Sleeper Integration Improvement
// Fetch user's leagues and let them select

async function fetchSleeperLeagues() {
  const username = document.getElementById('sleeperUsername').value.trim();
  const button = document.getElementById('fetchSleeperLeagues');
  const selectContainer = document.getElementById('sleeperLeagueSelect');
  
  if (!username) {
    showStatus('error', 'Please enter your Sleeper username');
    return;
  }
  
  button.disabled = true;
  button.textContent = '⏳ Loading...';
  showStatus('info', 'Fetching your Sleeper leagues...');
  
  try {
    // Step 1: Get user ID from username
    console.log('Fetching Sleeper user:', username);
    const userResponse = await fetch(`https://api.sleeper.app/v1/user/${username}`);
    
    if (!userResponse.ok) {
      throw new Error('Sleeper username not found');
    }
    
    const user = await userResponse.json();
    console.log('Found user:', user.user_id);
    
    // Step 2: Get user's leagues for current season
    const currentYear = new Date().getFullYear();
    const season = currentYear; // Or 2024 if mid-season
    
    console.log('Fetching leagues for season:', season);
    const leaguesResponse = await fetch(
      `https://api.sleeper.app/v1/user/${user.user_id}/leagues/nfl/${season}`
    );
    
    if (!leaguesResponse.ok) {
      throw new Error('Could not fetch leagues');
    }
    
    const leagues = await leaguesResponse.json();
    console.log('Found leagues:', leagues.length);
    
    if (leagues.length === 0) {
      throw new Error('No leagues found for this user');
    }
    
    // Step 3: Display league selector
    displaySleeperLeagues(leagues, user.user_id);
    showStatus('success', `✅ Found ${leagues.length} league(s)!`);
    
  } catch (error) {
    console.error('Sleeper fetch error:', error);
    showStatus('error', `❌ ${error.message}`);
  } finally {
    button.disabled = false;
    button.textContent = 'Load My Leagues';
  }
}

function displaySleeperLeagues(leagues, userId) {
  const container = document.getElementById('sleeperLeagueSelect');
  
  // Create select dropdown
  let html = '<label>Select Your League:</label>';
  html += '<select id="sleeperLeagueDropdown" style="width: 100%; padding: 8px; margin-bottom: 10px;">';
  
  leagues.forEach(league => {
    html += `<option value="${league.league_id}">${league.name} (${league.total_rosters} teams)</option>`;
  });
  
  html += '</select>';
  html += '<button id="connectSleeperLeague" style="width: 100%; background: #28a745;">Connect to Selected League</button>';
  
  container.innerHTML = html;
  container.style.display = 'block';
  
  // Save user ID for later
  window.sleeperUserId = userId;
  
  // Add event listener to connect button
  document.getElementById('connectSleeperLeague').addEventListener('click', connectSleeperLeague);
}

async function connectSleeperLeague() {
  const dropdown = document.getElementById('sleeperLeagueDropdown');
  const selectedLeagueId = dropdown.value;
  const selectedLeagueName = dropdown.options[dropdown.selectedIndex].text;
  
  console.log('Connecting to league:', selectedLeagueId, selectedLeagueName);
  
  try {
    // Fetch roster for this league
    const rostersResponse = await fetch(
      `https://api.sleeper.app/v1/league/${selectedLeagueId}/rosters`
    );
    
    if (!rostersResponse.ok) {
      throw new Error('Could not fetch rosters');
    }
    
    const rosters = await rostersResponse.json();
    
    // Find user's roster
    const userRoster = rosters.find(r => r.owner_id === window.sleeperUserId);
    
    if (!userRoster) {
      throw new Error('Could not find your roster in this league');
    }
    
    console.log('Found roster with', userRoster.players?.length || 0, 'players');
    
    // Fetch player data
    const playersResponse = await fetch('https://api.sleeper.app/v1/players/nfl');
    const allPlayers = await playersResponse.json();
    
    // Map player IDs to names
    const playerNames = userRoster.players.map(playerId => {
      const player = allPlayers[playerId];
      return player ? player.full_name : 'Unknown';
    });
    
    console.log('Player names:', playerNames);
    
    // Save to storage
    const rosterData = {
      leagueName: selectedLeagueName,
      leagueId: selectedLeagueId,
      players: playerNames,
      fetchedAt: new Date().toISOString()
    };
    
    await chrome.storage.local.set({ sleeperRoster: rosterData });
    
    showStatus('success', `✅ Connected to ${selectedLeagueName}! ${playerNames.length} players loaded.`);
    
    // Show inject button
    document.getElementById('injectRosterSection').style.display = 'block';
    
    // Store current roster globally
    window.currentRoster = {
      teamName: selectedLeagueName,
      roster: playerNames.map(name => ({ name, source: 'sleeper' })),
      source: 'Sleeper'
    };
    
  } catch (error) {
    console.error('Connect error:', error);
    showStatus('error', `❌ ${error.message}`);
  }
}

// HTML to add to popup:
/*
<div class="section">
  <h3>Sleeper Integration</h3>
  
  <label>Sleeper Username:</label>
  <input type="text" id="sleeperUsername" placeholder="your_username">
  
  <button id="fetchSleeperLeagues">Load My Leagues</button>
  
  <div id="sleeperLeagueSelect" style="display: none; margin-top: 15px;">
    <!-- League selector will appear here -->
  </div>
</div>
*/

// Background service worker for ESPN Roster Connector

console.log('ESPN Roster Connector: Background service worker loaded');

// Listen for extension icon clicks
chrome.action.onClicked.addListener((tab) => {
  // Open popup (this is handled automatically by manifest)
});

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'FETCH_ESPN_ROSTER') {
    // Handle roster fetch if needed
    fetchESPNRoster(message.config)
      .then(roster => sendResponse({ success: true, roster }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    
    return true; // Keep channel open for async response
  }
});

async function fetchESPNRoster(config) {
  const { leagueId, seasonYear, swid, espnS2 } = config;
  
  const url = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/${seasonYear}/segments/0/leagues/${leagueId}?view=mRoster&view=mTeam`;
  
  const headers = {};
  if (swid && espnS2) {
    headers['Cookie'] = `swid=${swid}; espn_s2=${espnS2}`;
  }
  
  const response = await fetch(url, {
    method: 'GET',
    headers: headers
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  return await response.json();
}

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('ESPN Roster Connector installed!');
    
    // Open welcome page
    chrome.tabs.create({
      url: 'https://github.com/cmcclea117-gif/ff_app'
    });
  }
});

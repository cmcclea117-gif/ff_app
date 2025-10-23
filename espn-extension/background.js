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
  
  console.log('Background: Fetching ESPN roster for league', leagueId);
  
  const url = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/${seasonYear}/segments/0/leagues/${leagueId}?view=mRoster&view=mTeam`;
  
  // Set cookies if provided
  if (swid && espnS2) {
    console.log('Background: Setting cookies via Chrome API...');
    
    try {
      // Remove old cookies first
      await chrome.cookies.remove({ url: 'https://fantasy.espn.com', name: 'swid' });
      await chrome.cookies.remove({ url: 'https://fantasy.espn.com', name: 'espn_s2' });
      
      // Set SWID
      await chrome.cookies.set({
        url: 'https://fantasy.espn.com',
        name: 'swid',
        value: swid,
        domain: '.espn.com',
        path: '/',
        secure: true,
        sameSite: 'lax'
      });
      
      // Set espn_s2
      await chrome.cookies.set({
        url: 'https://fantasy.espn.com',
        name: 'espn_s2',
        value: espnS2,
        domain: '.espn.com',
        path: '/',
        secure: true,
        httpOnly: true,
        sameSite: 'lax'
      });
      
      console.log('Background: Cookies set successfully');
      
      // Give cookies time to propagate
      await new Promise(resolve => setTimeout(resolve, 300));
      
    } catch (cookieError) {
      console.error('Background: Cookie error:', cookieError);
      throw new Error(`Failed to set cookies: ${cookieError.message}`);
    }
  }
  
  console.log('Background: Fetching from URL...');
  
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'include', // Include cookies
    headers: {
      'Accept': 'application/json'
    }
  });
  
  console.log('Background: Response status:', response.status);
  
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('401 Unauthorized - Cookies may be invalid or expired');
    } else if (response.status === 404) {
      throw new Error(`League ${leagueId} not found for ${seasonYear} season`);
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }
  
  const data = await response.json();
  console.log('Background: Successfully fetched roster data');
  
  return data;
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

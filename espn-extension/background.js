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
  
  // New approach: Use the content script running ON the ESPN page
  // This way it has access to the actual ESPN session!
  
  try {
    // First, find an ESPN tab
    console.log('Background: Looking for ESPN Fantasy tab...');
    const espnTabs = await chrome.tabs.query({ url: 'https://fantasy.espn.com/*' });
    
    if (espnTabs.length === 0) {
      // No ESPN tab open - try to open one and instruct user
      throw new Error('Please open ESPN Fantasy Football in another tab first, then try again.');
    }
    
    console.log('Background: Found ESPN tab, sending fetch request to page context...');
    
    // Send message to content script running on ESPN page
    const response = await chrome.tabs.sendMessage(espnTabs[0].id, {
      type: 'FETCH_FROM_ESPN_PAGE',
      config: { leagueId, seasonYear }
    });
    
    if (!response.success) {
      throw new Error(response.error);
    }
    
    console.log('Background: Successfully fetched roster from ESPN page!');
    return response.data;
    
  } catch (error) {
    console.error('Background: ESPN page fetch failed:', error);
    
    // Fallback: Try the old cookie method if page method fails
    console.log('Background: Trying fallback cookie method...');
    return await fetchViaBackgroundCookies(config);
  }
}

// Fallback method using background script cookies (old way)
async function fetchViaBackgroundCookies(config) {
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
  
  // Try WITHOUT credentials first (for public leagues)
  let response = await fetch(url, {
    method: 'GET',
    credentials: 'omit', // Don't send cookies first
    headers: {
      'Accept': 'application/json'
    }
  });
  
  console.log('Background: Initial response status:', response.status);
  
  // If we get 401 and have cookies, try again WITH credentials
  if (response.status === 401 && swid && espnS2) {
    console.log('Background: Got 401, retrying with credentials...');
    
    response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    console.log('Background: Response with credentials:', response.status);
  }
  
  // Check for redirects (ESPN redirects to login if auth fails)
  if (response.redirected) {
    console.error('Background: ESPN redirected to:', response.url);
    throw new Error('ESPN redirected to login. Possible fixes: 1) Try year 2024, 2) Get fresh cookies, 3) Check league privacy');
  }
  
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

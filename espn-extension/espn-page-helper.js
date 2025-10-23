// ESPN page content script - runs directly on fantasy.espn.com pages
// This has access to the actual ESPN session!

console.log('ESPN Page Helper: Loaded on ESPN page');

// Listen for requests from the extension
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'FETCH_FROM_ESPN_PAGE') {
    console.log('ESPN Page Helper: Fetching roster from within ESPN page context');
    
    fetchRosterFromPage(message.config)
      .then(data => {
        console.log('ESPN Page Helper: Fetch successful!');
        sendResponse({ success: true, data });
      })
      .catch(error => {
        console.error('ESPN Page Helper: Fetch failed:', error);
        sendResponse({ success: false, error: error.message });
      });
    
    return true; // Keep channel open for async
  }
});

async function fetchRosterFromPage(config) {
  const { leagueId, seasonYear } = config;
  
  const url = `https://fantasy.espn.com/apis/v3/games/ffl/seasons/${seasonYear}/segments/0/leagues/${leagueId}?view=mRoster&view=mTeam`;
  
  console.log('ESPN Page Helper: Fetching from', url);
  
  // Fetch from within the ESPN page context - cookies are automatically included!
  const response = await fetch(url, {
    method: 'GET',
    credentials: 'same-origin', // Use same-origin to include cookies from this domain
    headers: {
      'Accept': 'application/json'
    }
  });
  
  console.log('ESPN Page Helper: Response status:', response.status);
  
  if (!response.ok) {
    if (response.status === 401) {
      throw new Error('Not logged in or league is private');
    } else if (response.status === 404) {
      throw new Error(`League ${leagueId} not found for ${seasonYear}`);
    } else {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
  }
  
  const data = await response.json();
  console.log('ESPN Page Helper: Got data successfully');
  
  return data;
}

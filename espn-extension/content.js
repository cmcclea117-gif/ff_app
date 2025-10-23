// Content script - runs on dashboard pages
// Receives roster data from extension and injects into page

console.log('ESPN Roster Connector: Content script loaded');

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'INJECT_ESPN_ROSTER') {
    console.log('Received ESPN roster from extension:', message.roster);
    
    try {
      injectRoster(message.roster);
      sendResponse({ success: true });
    } catch (error) {
      console.error('Failed to inject roster:', error);
      sendResponse({ success: false, error: error.message });
    }
    
    return true; // Keep message channel open for async response
  }
});

function injectRoster(rosterData) {
  // Create a custom event with roster data
  const event = new CustomEvent('espnRosterLoaded', {
    detail: rosterData
  });
  
  // Dispatch to page
  window.dispatchEvent(event);
  
  // Also try to inject directly if dashboard has global variables
  if (typeof window.USER_ROSTER !== 'undefined') {
    window.USER_ROSTER = rosterData.roster.map(p => p.name);
    window.ROSTER_SOURCE = 'ESPN';
    window.ESPN_ROSTER_DATA = rosterData;
    
    console.log('Injected roster into window.USER_ROSTER:', window.USER_ROSTER);
    
    // Trigger refresh if function exists
    if (typeof window.renderProjectionsTable === 'function') {
      window.renderProjectionsTable();
      console.log('Refreshed projections table');
    }
    
    // Show notification
    showNotification(rosterData);
  } else {
    console.warn('Dashboard not detected. Roster data dispatched via event.');
  }
}

function showNotification(rosterData) {
  // Create notification element
  const notification = document.createElement('div');
  notification.id = 'espn-roster-notification';
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    z-index: 10000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    font-size: 14px;
    max-width: 300px;
    animation: slideIn 0.3s ease-out;
  `;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 10px;">
      <span style="font-size: 24px;">🏈</span>
      <div>
        <strong>ESPN Roster Loaded!</strong><br>
        <span style="font-size: 12px; opacity: 0.9;">
          ${rosterData.teamName} • ${rosterData.roster.length} players
        </span>
      </div>
    </div>
  `;
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(400px);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Check if page is a dashboard and notify extension
function detectDashboard() {
  // Look for dashboard indicators
  const isDashboard = 
    document.querySelector('[data-dashboard]') ||
    document.querySelector('#projectionsTable') ||
    typeof window.PROJECTIONS !== 'undefined';
  
  if (isDashboard) {
    console.log('ESPN Roster Connector: Dashboard detected!');
  }
}

// Run detection on load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', detectDashboard);
} else {
  detectDashboard();
}

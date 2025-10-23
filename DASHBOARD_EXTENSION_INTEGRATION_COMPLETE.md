# Adding Extension Support to Your Dashboard

## 📍 Where to Add Code in generate_dashboard_fixed.py

### Step 1: Find the JavaScript Section

Look for the section that starts with:
```python
<script>
// ==================== CONFIGURATION ====================
```

This is around **line 800-1500** depending on your version.

### Step 2: Add Extension Listener AFTER Sleeper Code

Find this section:
```javascript
// ==================== SLEEPER API INTEGRATION ====================
```

Right AFTER the Sleeper integration section (but BEFORE the table rendering functions), add:

```javascript
// ==================== EXTENSION INTEGRATION ====================

// Global variable to track roster source
let ROSTER_SOURCE = 'None';
let EXTENSION_ROSTER_DATA = null;

// Listen for roster data from browser extension
window.addEventListener('espnRosterLoaded', (event) => {
  const rosterData = event.detail;
  console.log('🏈 ESPN roster received from extension:', rosterData);
  
  try {
    // Extract player names
    USER_ROSTER = rosterData.roster.map(p => p.name);
    ROSTER_SOURCE = 'ESPN Extension';
    EXTENSION_ROSTER_DATA = rosterData;
    
    console.log(`✅ Loaded ${USER_ROSTER.length} players from ${rosterData.teamName}`);
    
    // Save to localStorage
    try {
      localStorage.setItem('extension_roster', JSON.stringify(rosterData));
      localStorage.setItem('roster_source', 'ESPN');
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
    }
    
    // Update any connection status UI
    updateConnectionStatus(rosterData);
    
    // Refresh tables to highlight rostered players
    if (typeof renderProjectionsTable === 'function') {
      renderProjectionsTable();
    }
    
    // Show success notification
    showRosterLoadedNotification(rosterData);
    
  } catch (error) {
    console.error('Failed to process extension roster:', error);
    alert('Failed to load roster: ' + error.message);
  }
});

// Listen for Sleeper roster from extension
window.addEventListener('sleeperRosterLoaded', (event) => {
  const rosterData = event.detail;
  console.log('🏈 Sleeper roster received from extension:', rosterData);
  
  try {
    USER_ROSTER = rosterData.players;
    ROSTER_SOURCE = 'Sleeper Extension';
    EXTENSION_ROSTER_DATA = rosterData;
    
    console.log(`✅ Loaded ${USER_ROSTER.length} players from ${rosterData.leagueName}`);
    
    // Save to localStorage
    try {
      localStorage.setItem('extension_roster', JSON.stringify(rosterData));
      localStorage.setItem('roster_source', 'Sleeper');
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
    }
    
    updateConnectionStatus(rosterData);
    
    if (typeof renderProjectionsTable === 'function') {
      renderProjectionsTable();
    }
    
    showRosterLoadedNotification(rosterData);
    
  } catch (error) {
    console.error('Failed to process Sleeper roster:', error);
    alert('Failed to load roster: ' + error.message);
  }
});

function updateConnectionStatus(rosterData) {
  // Find or create connection status element
  let statusEl = document.getElementById('connectionStatus');
  
  if (!statusEl) {
    // Create it if it doesn't exist
    statusEl = document.createElement('div');
    statusEl.id = 'connectionStatus';
    statusEl.style.cssText = 'margin: 20px 0; padding: 15px; border-radius: 8px;';
    
    // Insert at top of page
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(statusEl, container.firstChild);
  }
  
  const source = rosterData.source || ROSTER_SOURCE;
  const teamName = rosterData.teamName || rosterData.leagueName || 'Your Team';
  const playerCount = rosterData.roster?.length || rosterData.players?.length || USER_ROSTER.length;
  
  statusEl.innerHTML = `
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
      <div style="display: flex; align-items: center; gap: 15px;">
        <span style="font-size: 40px;">🏈</span>
        <div style="flex: 1;">
          <strong style="font-size: 18px; display: block; margin-bottom: 5px;">
            Roster Connected!
          </strong>
          <span style="font-size: 14px; opacity: 0.95;">
            ${teamName} • ${playerCount} players • ${source}
          </span>
        </div>
        <button onclick="clearRoster()" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); padding: 8px 15px; border-radius: 5px; cursor: pointer; font-size: 12px;">
          Clear
        </button>
      </div>
    </div>
  `;
}

function showRosterLoadedNotification(rosterData) {
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #28a745, #20c997);
    color: white;
    padding: 20px 25px;
    border-radius: 10px;
    box-shadow: 0 6px 20px rgba(40, 167, 69, 0.4);
    z-index: 10000;
    font-size: 15px;
    max-width: 350px;
    animation: slideIn 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  `;
  
  const teamName = rosterData.teamName || rosterData.leagueName || 'Your Team';
  const playerCount = rosterData.roster?.length || rosterData.players?.length || 0;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 15px;">
      <span style="font-size: 36px;">✅</span>
      <div>
        <strong style="display: block; margin-bottom: 5px; font-size: 16px;">
          Roster Loaded!
        </strong>
        <span style="font-size: 13px; opacity: 0.95;">
          ${teamName}<br>
          ${playerCount} players
        </span>
      </div>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

function clearRoster() {
  if (confirm('Clear your connected roster?')) {
    USER_ROSTER = [];
    ROSTER_SOURCE = 'None';
    EXTENSION_ROSTER_DATA = null;
    
    localStorage.removeItem('extension_roster');
    localStorage.removeItem('roster_source');
    
    const statusEl = document.getElementById('connectionStatus');
    if (statusEl) {
      statusEl.remove();
    }
    
    if (typeof renderProjectionsTable === 'function') {
      renderProjectionsTable();
    }
  }
}

// Load saved roster on page load
function loadSavedExtensionRoster() {
  try {
    const saved = localStorage.getItem('extension_roster');
    if (saved) {
      const rosterData = JSON.parse(saved);
      
      if (rosterData.roster) {
        USER_ROSTER = rosterData.roster.map(p => p.name);
      } else if (rosterData.players) {
        USER_ROSTER = rosterData.players;
      }
      
      ROSTER_SOURCE = localStorage.getItem('roster_source') || 'Extension';
      EXTENSION_ROSTER_DATA = rosterData;
      
      console.log(`✅ Loaded saved roster: ${USER_ROSTER.length} players`);
      
      updateConnectionStatus(rosterData);
    }
  } catch (e) {
    console.warn('Could not load saved roster:', e);
  }
}

// Add animations
const extensionStyles = document.createElement('style');
extensionStyles.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(400px) scale(0.8);
      opacity: 0;
    }
    to {
      transform: translateX(0) scale(1);
      opacity: 1;
    }
  }
  @keyframes slideOut {
    from {
      transform: translateX(0) scale(1);
      opacity: 1;
    }
    to {
      transform: translateX(400px) scale(0.8);
      opacity: 0;
    }
  }
`;
document.head.appendChild(extensionStyles);

// Call on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadSavedExtensionRoster);
} else {
  loadSavedExtensionRoster();
}

console.log('✅ Extension integration loaded - ready to receive roster data!');

// ==================== END EXTENSION INTEGRATION ====================
```

### Step 3: Update the Content Script

In your extension's `content.js`, make sure it dispatches the right events:

```javascript
// For ESPN rosters
window.dispatchEvent(new CustomEvent('espnRosterLoaded', {
  detail: {
    teamName: "Team Name",
    roster: [{name: "Player Name", position: "QB"}, ...],
    source: "ESPN"
  }
}));

// For Sleeper rosters
window.dispatchEvent(new CustomEvent('sleeperRosterLoaded', {
  detail: {
    leagueName: "League Name",
    players: ["Player 1", "Player 2", ...],
    source: "Sleeper"
  }
}));
```

---

## 🎯 Result

When a user loads their roster via the extension:

1. ✅ Dashboard receives event
2. ✅ Player names extracted
3. ✅ Tables refresh with highlights
4. ✅ Big notification appears
5. ✅ Status banner shows at top
6. ✅ Saved to localStorage for next visit

---

## 🎨 What It Looks Like

**Connection Status Banner:**
```
┌────────────────────────────────────────────────┐
│ 🏈  Roster Connected!                    [Clear]│
│     Your Team Name • 15 players • ESPN         │
└────────────────────────────────────────────────┘
```

**Notification (appears briefly):**
```
  ┌──────────────────────┐
  │ ✅ Roster Loaded!    │
  │    Your Team Name    │
  │    15 players        │
  └──────────────────────┘
```

---

## 📝 Next Steps

1. Add this code to `generate_dashboard_fixed.py`
2. Regenerate your dashboard
3. Test with extension
4. See roster highlights! ✨

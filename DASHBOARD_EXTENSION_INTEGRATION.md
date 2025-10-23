# Integrating ESPN Extension with Your Dashboard

## 🎯 What You Need to Add

Your dashboard needs to **listen for roster data** from the extension.

---

## 📝 Code to Add to Your Dashboard

Add this JavaScript to your `generate_dashboard_fixed.py` in the main JavaScript section:

```javascript
// ==================== ESPN EXTENSION SUPPORT ====================

// Listen for ESPN roster from browser extension
window.addEventListener('espnRosterLoaded', (event) => {
  const rosterData = event.detail;
  console.log('🏈 ESPN roster received from extension:', rosterData);
  
  try {
    // Extract player names for roster checking
    USER_ROSTER = rosterData.roster.map(p => p.name);
    ROSTER_SOURCE = 'ESPN Extension';
    window.ESPN_ROSTER_DATA = rosterData;
    
    console.log(`✅ Loaded ${USER_ROSTER.length} players from ${rosterData.teamName}`);
    
    // Save to localStorage for next visit
    try {
      localStorage.setItem('espn_roster', JSON.stringify(rosterData));
      localStorage.setItem('roster_source', 'ESPN');
    } catch (e) {
      console.warn('Could not save to localStorage:', e);
    }
    
    // Update connection status UI
    updateConnectionStatus(rosterData);
    
    // Refresh tables to highlight rostered players
    if (typeof renderProjectionsTable === 'function') {
      renderProjectionsTable();
    }
    
    // Show success notification
    showRosterNotification(rosterData);
    
  } catch (error) {
    console.error('Failed to process ESPN roster:', error);
    alert('Failed to load ESPN roster: ' + error.message);
  }
});

function updateConnectionStatus(rosterData) {
  // Update any connection status UI elements
  const statusEl = document.getElementById('connectionStatus');
  if (statusEl) {
    statusEl.innerHTML = `
      <div style="background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <strong style="color: #155724;">🏈 ESPN Roster Connected</strong><br>
        <span style="font-size: 0.9em; color: #155724;">
          Team: ${rosterData.teamName}<br>
          Players: ${rosterData.roster.length}<br>
          Season: ${rosterData.season}<br>
          <em>Last updated: ${new Date(rosterData.fetchedAt).toLocaleString()}</em>
        </span>
      </div>
    `;
  }
}

function showRosterNotification(rosterData) {
  // Create temporary notification
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #28a745;
    color: white;
    padding: 20px 25px;
    border-radius: 10px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
    z-index: 10000;
    font-size: 15px;
    max-width: 350px;
    animation: slideIn 0.3s ease-out;
  `;
  
  notification.innerHTML = `
    <div style="display: flex; align-items: center; gap: 15px;">
      <span style="font-size: 32px;">🏈</span>
      <div>
        <strong style="display: block; margin-bottom: 5px;">ESPN Roster Loaded!</strong>
        <span style="font-size: 13px; opacity: 0.9;">
          ${rosterData.teamName}<br>
          ${rosterData.roster.length} players
        </span>
      </div>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Remove after 4 seconds
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-in';
    setTimeout(() => notification.remove(), 300);
  }, 4000);
}

// Load saved ESPN roster on page load
function loadSavedESPNRoster() {
  try {
    const saved = localStorage.getItem('espn_roster');
    if (saved) {
      const rosterData = JSON.parse(saved);
      USER_ROSTER = rosterData.roster.map(p => p.name);
      ROSTER_SOURCE = 'ESPN';
      window.ESPN_ROSTER_DATA = rosterData;
      
      console.log(`✅ Loaded saved ESPN roster: ${rosterData.teamName} (${USER_ROSTER.length} players)`);
      
      updateConnectionStatus(rosterData);
    }
  } catch (e) {
    console.warn('Could not load saved ESPN roster:', e);
  }
}

// Call on page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadSavedESPNRoster);
} else {
  loadSavedESPNRoster();
}

// Add slide animation styles
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

// ==================== END ESPN EXTENSION SUPPORT ====================
```

---

## 📍 Where to Add This Code

In `generate_dashboard_fixed.py`, find the JavaScript section (around line ~800-1500) and add this code after the Sleeper integration but before the final closing `</script>` tag.

---

## 🎨 Optional: Add Extension Instructions to UI

Add this HTML section to your dashboard to guide users:

```python
# In generate_dashboard_fixed.py, in the HTML section:

  <div class="connection-section" style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px;">
    <h3>🏈 Connect Your Roster</h3>
    
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 15px;">
      <!-- Sleeper -->
      <div>
        <h4>Sleeper</h4>
        <input type="text" id="sleeperUsername" placeholder="Username" style="width: 100%; padding: 8px; margin: 5px 0;">
        <input type="text" id="leagueId" placeholder="League ID" style="width: 100%; padding: 8px; margin: 5px 0;">
        <button onclick="connectToSleeper()" style="width: 100%; padding: 10px; background: #0066cc; color: white; border: none; border-radius: 5px; cursor: pointer;">
          Connect Sleeper
        </button>
      </div>
      
      <!-- ESPN -->
      <div>
        <h4>ESPN</h4>
        <p style="font-size: 0.9em; margin: 10px 0;">
          Install the <strong>ESPN Roster Connector</strong> Chrome extension, then click the extension icon to connect your roster.
        </p>
        <a href="https://github.com/cmcclea117-gif/ff_app/tree/main/espn-extension" 
           target="_blank"
           style="display: inline-block; width: 100%; padding: 10px; background: #28a745; color: white; text-decoration: none; text-align: center; border-radius: 5px;">
          Get Extension →
        </a>
      </div>
    </div>
    
    <div id="connectionStatus" style="margin-top: 15px;"></div>
  </div>
```

---

## ✅ Testing

1. **Update your dashboard** with the code above
2. **Regenerate the HTML**: `python generate_dashboard_fixed.py`
3. **Push to GitHub**: `git add . && git commit -m "Add ESPN extension support" && git push`
4. **Install the extension** (see extension README)
5. **Test the flow**:
   - Open your dashboard on GitHub Pages
   - Click extension icon
   - Click "Send to Dashboard"
   - Verify roster highlights work!

---

## 🐛 Debugging

### Check if extension is loaded:
```javascript
// In browser console (F12) on your dashboard
console.log('Extension active?', typeof window.ESPN_ROSTER_DATA !== 'undefined');
```

### Manually trigger event (testing):
```javascript
// Test the event listener
window.dispatchEvent(new CustomEvent('espnRosterLoaded', {
  detail: {
    teamName: 'Test Team',
    roster: [
      { name: 'Patrick Mahomes', position: 'QB' },
      { name: 'Christian McCaffrey', position: 'RB' }
    ],
    leagueId: 123456,
    season: 2024,
    fetchedAt: new Date().toISOString()
  }
}));
```

### Check roster loaded:
```javascript
// Should show array of player names
console.log('Loaded roster:', USER_ROSTER);
console.log('Source:', ROSTER_SOURCE);
```

---

## 🎯 Expected Behavior

1. User installs extension
2. User configures ESPN League ID + cookies
3. User clicks "Fetch My Roster"
4. User opens your dashboard
5. User clicks "Send to Dashboard" in extension
6. Dashboard receives roster via event
7. Roster is highlighted in tables ✅
8. Success notification appears
9. Roster saved to localStorage for next visit

---

Perfect! Your dashboard now works with the ESPN extension! 🎉

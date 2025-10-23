# ESPN Fantasy Roster Connector - Chrome Extension

A Chrome extension that connects your ESPN Fantasy Football roster to web-based fantasy dashboards by bypassing CORS restrictions.

---

## 🎯 What It Does

- ✅ Fetches your ESPN Fantasy roster (no CORS issues!)
- ✅ Injects roster data into compatible dashboards
- ✅ Works with private leagues (using cookies)
- ✅ Caches roster for quick access
- ✅ Clean, simple UI

---

## 📦 Installation

### For Development/Testing:

1. **Download the extension folder** (`espn-extension`)

2. **Add placeholder icons** (or use the ones provided):
   - Create 3 PNG files in the `icons/` folder:
   - `icon16.png` (16x16)
   - `icon48.png` (48x48)
   - `icon128.png` (128x128)
   
   **Quick icon creation**:
   - Use any image editor
   - Create a simple football icon 🏈
   - Or use https://www.favicon-generator.org/

3. **Load in Chrome**:
   - Open Chrome
   - Go to `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `espn-extension` folder

4. **Pin the extension**:
   - Click the puzzle piece icon in Chrome toolbar
   - Find "ESPN Roster Connector"
   - Click the pin icon

---

## 🚀 How to Use

### Step 1: Configure Extension

1. Click the extension icon
2. Enter your **ESPN League ID**
3. Select **Season Year** (2024 or 2025)
4. For **private leagues**, expand "Private League?" and add cookies:
   - Go to ESPN Fantasy in another tab
   - Press F12 → Application → Cookies
   - Copy `swid` and `espn_s2` values
   - Paste into extension

### Step 2: Fetch Roster

1. Click **"Fetch My Roster"**
2. Extension will fetch from ESPN (bypassing CORS!)
3. You'll see your team name and player count

### Step 3: Inject into Dashboard

1. Open your fantasy dashboard (e.g., GitHub Pages)
2. Click the extension icon
3. Click **"Send to Dashboard"**
4. Your roster will be highlighted! 🎉

---

## 🔧 Dashboard Integration

Your dashboard needs to listen for the roster data. Add this code:

```javascript
// Listen for ESPN roster from extension
window.addEventListener('espnRosterLoaded', (event) => {
  const rosterData = event.detail;
  console.log('ESPN roster received:', rosterData);
  
  // Extract player names
  USER_ROSTER = rosterData.roster.map(p => p.name);
  ROSTER_SOURCE = 'ESPN';
  
  // Refresh your tables
  if (typeof renderProjectionsTable === 'function') {
    renderProjectionsTable();
  }
  
  // Show success message
  alert(`✅ ESPN roster loaded! ${rosterData.roster.length} players from ${rosterData.teamName}`);
});
```

---

## 📁 File Structure

```
espn-extension/
├── manifest.json       # Extension configuration
├── popup.html          # Extension popup UI
├── popup.js            # Popup logic
├── content.js          # Injected into dashboard pages
├── background.js       # Background service worker
├── icons/              # Extension icons
│   ├── icon16.png
│   ├── icon48.png
│   └── icon128.png
└── README.md           # This file
```

---

## 🔐 Privacy & Security

- ✅ **Your data never leaves your machine**
- ✅ **Cookies stored locally in Chrome**
- ✅ **No external servers**
- ✅ **Open source - audit the code**

Your ESPN cookies give access to your account, so:
- 🔒 Only use on your personal computer
- 🔒 Don't share your configured extension
- 🔒 Clear data when done (use "Clear Saved Data" button)

---

## 🐛 Troubleshooting

### "401 Unauthorized" Error
**Problem**: Private league without cookies  
**Solution**: Add your `swid` and `espn_s2` cookies in the extension popup

### "404 Not Found" Error
**Problem**: Wrong league ID or year  
**Solution**: Double-check league ID, try 2024 instead of 2025

### "No active tab found"
**Problem**: Dashboard not open  
**Solution**: Open your dashboard first, then click "Send to Dashboard"

### Extension Not Injecting
**Problem**: Dashboard not compatible  
**Solution**: Make sure dashboard has the event listener code (see above)

### Roster Not Highlighted
**Problem**: Name matching issues  
**Solution**: Check console (F12) for errors, may need name normalization

---

## 🚀 Publishing to Chrome Web Store

Want to publish this extension?

1. **Create icons** (professional quality)
2. **Test thoroughly** with multiple leagues
3. **Write store description**
4. **Submit to Chrome Web Store**:
   - Go to: https://chrome.google.com/webstore/devconsole
   - Pay $5 one-time developer fee
   - Upload extension ZIP
   - Fill out listing details
   - Submit for review (~3-7 days)

---

## 📝 Future Enhancements

Potential features to add:
- [ ] Support for multiple teams in same league
- [ ] Auto-refresh roster on dashboard load
- [ ] Support for Firefox
- [ ] Weekly lineup suggestions
- [ ] Trade analyzer
- [ ] Player news integration

---

## 🤝 Contributing

Found a bug? Have an idea?  
Open an issue or submit a PR!

---

## 📄 License

MIT License - Feel free to use and modify!

---

## 🙏 Credits

Created for the Fantasy Football Dashboard project:  
https://github.com/cmcclea117-gif/ff_app

---

**Enjoy your ESPN-connected dashboard! 🏈🎉**

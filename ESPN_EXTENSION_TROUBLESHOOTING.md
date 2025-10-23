# ESPN Extension Troubleshooting Guide

## 🔍 Your Current Error: "Failed to fetch"

This usually means the extension can't reach ESPN's API. Let's debug it!

---

## ✅ Step 1: Reload the Extension

After making changes, you MUST reload:

1. Go to `chrome://extensions/`
2. Find "ESPN Fantasy Roster Connector"
3. Click the **🔄 Reload** button
4. Try fetching again

---

## 🔍 Step 2: Check Console Logs

The extension has detailed logging. Let's see what's happening:

### Check Extension Popup Console:

1. Click the extension icon (to open popup)
2. **Right-click anywhere in the popup**
3. Select **"Inspect"**
4. A DevTools window opens showing the popup's console
5. Click "Fetch My Roster" again
6. Look for errors in the console

**What to look for:**
- `Setting ESPN cookies...` (if you entered cookies)
- `Cookies set successfully`
- Any error messages
- Network tab shows the request to ESPN

---

## 🔍 Step 3: Check Background Service Worker

1. Go to `chrome://extensions/`
2. Find your extension
3. Click **"service worker"** link (in blue)
4. DevTools opens for background script
5. Try fetching again
6. Check for errors

---

## 🐛 Common Issues & Fixes

### Issue 1: "Failed to fetch" with no other info

**Possible causes:**
- Extension doesn't have permission to access ESPN
- Network issue
- Cookies not set correctly

**Fix:**
1. Check `manifest.json` has `"cookies"` permission
2. Check `host_permissions` includes `"https://fantasy.espn.com/*"`
3. Reload extension
4. Try again

---

### Issue 2: "401 Unauthorized"

**Cause:** Private league, cookies not working

**Fix:**
1. Make sure you copied the FULL cookie values
2. `swid` should include the curly braces: `{ABC123-...}`
3. `espn_s2` is a very long string (200+ characters)
4. Get fresh cookies (log out and back into ESPN)

**How to verify cookies:**
1. In popup inspector, go to **Application** tab
2. Look at Cookies → `https://fantasy.espn.com`
3. Verify `swid` and `espn_s2` are there after clicking "Fetch"

---

### Issue 3: "404 Not Found"

**Cause:** Wrong League ID or year doesn't exist yet

**Fix:**
1. Double-check your League ID
2. Try 2024 instead of 2025
3. Make sure you're using the RIGHT League ID (from URL)

**How to find League ID:**
```
https://fantasy.espn.com/football/league?leagueId=40251425
                                                  ^^^^^^^^
                                                  This number
```

---

### Issue 4: Extension loads but nothing happens

**Cause:** Code error in one of the files

**Fix:**
1. Check all 5 files are in the folder:
   - manifest.json
   - popup.html
   - popup.js
   - content.js
   - background.js
2. No typos or syntax errors
3. Check console for JavaScript errors

---

## 🧪 Manual Testing

### Test 1: Can extension reach ESPN at all?

Add this temporary code to `popup.js` inside the `fetchRoster` function, right after `try {`:

```javascript
console.log('Testing basic fetch...');
const testResponse = await fetch('https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leagues/40251425');
console.log('Test response:', testResponse.status, testResponse.statusText);
```

This tests if the extension can reach ESPN at all (with a public league).

---

### Test 2: Check if cookies are being set

Add this after the cookie-setting code:

```javascript
// Verify cookies were set
const cookies = await chrome.cookies.getAll({
  url: 'https://fantasy.espn.com'
});
console.log('Current ESPN cookies:', cookies);
```

This shows what cookies are actually set.

---

## 📋 Debugging Checklist

Go through this checklist:

- [ ] Extension shows up in `chrome://extensions/`
- [ ] Extension is enabled (toggle is ON)
- [ ] Developer mode is enabled
- [ ] Clicked "Reload" after any file changes
- [ ] All 5 files exist in the folder
- [ ] Icons folder exists (even if empty)
- [ ] Manifest has `"cookies"` permission
- [ ] Can open popup by clicking icon
- [ ] League ID is correct (numbers only)
- [ ] Year is set (2024 or 2025)
- [ ] For private league: Copied FULL cookie values
- [ ] Checked popup console (right-click → Inspect)
- [ ] No JavaScript errors in console

---

## 🔧 Enhanced Error Logging

Replace the `catch` block in `popup.js` with this for better errors:

```javascript
} catch (error) {
  console.error('Fetch error:', error);
  console.error('Error stack:', error.stack);
  console.error('Error name:', error.name);
  console.error('Error message:', error.message);
  
  let errorMessage = error.message;
  
  // Check if it's a network error
  if (error.name === 'TypeError' && error.message.includes('fetch')) {
    errorMessage = 'Network error - check console for details. Extension may need cookies permission.';
  }
  
  showStatus('error', `❌ ${errorMessage}`);
}
```

This gives much more detailed error info.

---

## 🆘 If Nothing Works

### Last Resort: Simplest Possible Test

Create a test file `test.html`:

```html
<!DOCTYPE html>
<html>
<body>
  <button id="test">Test ESPN API</button>
  <div id="result"></div>
  
  <script>
    document.getElementById('test').onclick = async () => {
      try {
        const response = await fetch(
          'https://fantasy.espn.com/apis/v3/games/ffl/seasons/2024/segments/0/leagues/40251425'
        );
        document.getElementById('result').textContent = 
          `Status: ${response.status} - ${response.statusText}`;
      } catch (error) {
        document.getElementById('result').textContent = 
          `Error: ${error.message}`;
      }
    };
  </script>
</body>
</html>
```

Add this to your extension folder and set it as `default_popup` temporarily to isolate the issue.

---

## 📞 Getting More Help

If still stuck, gather this info:

1. **Chrome version**: chrome://version
2. **Extension manifest**: Copy/paste your `manifest.json`
3. **Console errors**: Screenshot of any red errors
4. **Network tab**: Screenshot showing failed request
5. **What you've tried**: List all troubleshooting steps

Then share this info and I can help diagnose further!

---

## 🎯 Most Likely Fix for Your Error

Based on your screenshot, the most likely issue is **cookie permission**. 

**Try this:**

1. Update `manifest.json` to include `"cookies"` permission (see updated version)
2. Update `popup.js` to use Chrome Cookie API (see updated version)
3. **Reload the extension** in `chrome://extensions/`
4. Try fetching again

The updated files are in the latest ZIP!

---

## ✅ Verification Steps

After fix:

1. Open popup
2. Right-click → Inspect
3. Go to Console tab
4. Enter League ID + cookies
5. Click "Fetch My Roster"
6. You should see:
   ```
   Setting ESPN cookies...
   Cookies set successfully
   [fetch happens]
   ✅ Found X players!
   ```

Let me know what you see in the console! 🔍

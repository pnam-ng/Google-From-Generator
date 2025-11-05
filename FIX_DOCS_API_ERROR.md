# 🔧 Fix: Google Docs API Not Enabled

## Error Message

If you see this error:
```
Google Docs API has not been used in project ... or it is disabled.
Enable it by visiting https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=...
```

## Quick Fix (1 Click)

**Direct Link to Enable:** Click the link provided in the error message, or use this:
```
https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your project ID (found in the error message).

## Step-by-Step Solution

### Step 1: Go to Google Cloud Console

1. Visit: https://console.cloud.google.com/
2. Sign in with your Google account
3. Select your project (project ID: `689227515779` in your case)

### Step 2: Enable Google Docs API

**Option A: Direct Link (Fastest)**
- Click this link: https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=689227515779
- Click the **"Enable"** button
- Wait for confirmation

**Option B: Manual Steps**
1. In Google Cloud Console, click **"APIs & Services"** in the left menu
2. Click **"Library"**
3. Search for **"Google Docs API"**
4. Click on **"Google Docs API"**
5. Click the **"Enable"** button (blue button)
6. Wait a few seconds for activation

### Step 3: Wait 2-5 Minutes

After enabling, Google needs 2-5 minutes to sync. Wait before trying again.

### Step 4: Try Again

Go back to your app and try creating a form from a Google Docs link again.

## Why Google Docs API is Needed

The Google Docs API is required when you use the **"Google Docs Link"** feature to:
- Read content from Google Docs documents
- Extract text for form generation
- Convert document content into form questions

## All Required APIs

For full functionality, enable these APIs:

1. ✅ **Google Forms API** - Core functionality (required)
2. ✅ **Google Drive API** - Creates forms in Drive (required)
3. ✅ **Google Docs API** - Reads Google Docs content (required for Docs link feature)

## Quick Check

To verify all APIs are enabled:

1. Go to Google Cloud Console
2. Click **"APIs & Services"** > **"Enabled APIs"**
3. You should see:
   - ✅ Google Drive API
   - ✅ Google Forms API
   - ✅ Google Docs API

## Troubleshooting

### Still getting the error after enabling?

1. **Wait longer** - Sometimes takes up to 10 minutes
2. **Check project** - Make sure you're using the correct project
3. **Clear cache** - Delete `token.pickle` and re-authenticate:
   ```bash
   # Delete token file
   rm token.pickle  # Linux/Mac
   del token.pickle  # Windows
   ```
4. **Re-authenticate** - Run your app again and sign in fresh

### Don't need Google Docs feature?

If you're not using the Google Docs link feature, you can skip enabling this API. The error will only occur when trying to use that specific feature.

## Direct Enable Links

For your project (689227515779):
- **Google Docs API:** https://console.developers.google.com/apis/api/docs.googleapis.com/overview?project=689227515779

---

**That's it!** Once enabled, the Google Docs link feature will work. 🎉


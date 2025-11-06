# 🔧 Fix Redirect URI Mismatch - Step by Step

## Your Current Setup

Based on your `credentials.json`:
- **Client ID**: `689227515779-72e576trca43ircif4jh17brv3c26n8b.apps.googleusercontent.com`
- **Project ID**: `bustling-psyche-313714`
- **OAuth Client Name**: "Form Gen"

## Step-by-Step Fix

### Step 1: Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Make sure you're in project: **bustling-psyche-313714**

### Step 2: Find Your OAuth Client

1. Go to **APIs & Services** → **Credentials**
2. Look for the OAuth 2.0 Client ID with this Client ID:
   ```
   689227515779-72e576trca43ircif4jh17brv3c26n8b
   ```
3. The name should be **"Form Gen"** (or check if it matches)
4. Click on it to edit

### Step 3: Add Authorized Redirect URIs

In the OAuth client settings, find **"Authorized redirect URIs"** section.

**For Local Development, add:**
```
http://localhost:5000/auth/callback
```

**For Render (Production), add:**
```
https://google-from-generator.onrender.com/auth/callback
```

**Important:** Add BOTH if you want to test locally and on Render.

### Step 4: Save

1. Click **SAVE** at the bottom
2. Wait 1-2 minutes for changes to propagate

### Step 5: Verify Application Type

Make sure the OAuth client type is **"Web application"** (not "Desktop app"):
- If it says "Desktop app", you need to create a new "Web application" OAuth client
- Or update your code to handle desktop app credentials (but web app is recommended)

### Step 6: Test

1. **For Local:**
   - Make sure your app is running on `http://localhost:5000`
   - Click "Sign In"
   - Check the browser console/logs for: `🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback`

2. **For Render:**
   - Visit your Render app
   - Click "Sign In"
   - Check Render logs for: `🔗 [LOGIN] Redirect URI: https://google-from-generator.onrender.com/auth/callback`

## Common Issues

### Issue 1: "FormGeneration" vs "Form Gen"

- The error message shows "FormGeneration" because that's the **OAuth consent screen app name**
- Your OAuth client is named "Form Gen" - that's fine!
- What matters is the **Client ID** matches: `689227515779-72e576trca43ircif4jh17brv3c26n8b`

### Issue 2: Redirect URI Still Not Working

If you still get the error after adding redirect URIs:

1. **Double-check the exact URI:**
   - No trailing slash: `/auth/callback` ✅ (not `/auth/callback/` ❌)
   - Correct protocol: `http://` for local, `https://` for Render
   - Correct port: `:5000` for local
   - Exact domain: `google-from-generator.onrender.com` (check your actual Render URL)

2. **Check the logs:**
   - The app will print the exact redirect URI it's using
   - Make sure it matches exactly what you added in Google Cloud Console

3. **Wait a few minutes:**
   - Google sometimes takes 1-2 minutes to update redirect URI settings

### Issue 3: Wrong OAuth Client

If you have multiple OAuth clients:

1. Check which Client ID is in your `credentials.json`
2. Make sure you're editing the correct OAuth client in Google Cloud Console
3. The Client ID must match exactly

## Quick Verification

After adding redirect URIs, verify:

1. **In Google Cloud Console:**
   - OAuth client → Authorized redirect URIs
   - Should show both:
     - `http://localhost:5000/auth/callback`
     - `https://google-from-generator.onrender.com/auth/callback`

2. **In your app logs:**
   - When clicking "Sign In", you should see:
     ```
     🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback
        Is production: False
        Request scheme: http
        Request host: localhost:5000
     ```

3. **The redirect URI in logs must match exactly** what's in Google Cloud Console!

## Still Having Issues?

1. Share the redirect URI from your logs
2. Share a screenshot of your Google Cloud Console OAuth client settings
3. Check if you're using the correct OAuth client (Client ID matches)


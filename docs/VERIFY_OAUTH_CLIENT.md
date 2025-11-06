# ✅ Verify OAuth Client Configuration

## Issue

The error message shows "FormGeneration" but your OAuth client is named "Form Gen". This means you might be using the wrong OAuth client credentials.

## How to Verify

### Step 1: Check Your credentials.json Client ID

Your `credentials.json` file contains:
```json
{
  "web": {
    "client_id": "689227515779-72e576trca43ircif4jh17brv3c26n8b.apps.googleusercontent.com",
    ...
  }
}
```

### Step 2: Verify in Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: **bustling-psyche-313714**
3. Navigate to **APIs & Services** → **Credentials**
4. Find the OAuth 2.0 Client ID that matches your `client_id`:
   - Look for: `689227515779-72e576trca43ircif4jh17brv3c26n8b`
5. Check the **Name** of that OAuth client:
   - If it says "Form Gen" ✅ - You're using the correct one
   - If it says "FormGeneration" or something else ❌ - You're using the wrong one

### Step 3: Check Authorized Redirect URIs

For the OAuth client with Client ID `689227515779-72e576trca43ircif4jh17brv3c26n8b`, make sure these redirect URIs are added:

**For Local Development:**
```
http://localhost:5000/auth/callback
```

**For Render (Production):**
```
https://google-from-generator.onrender.com/auth/callback
```

### Step 4: If Using Wrong OAuth Client

If the OAuth client name doesn't match "Form Gen":

**Option A: Use the Correct OAuth Client**
1. In Google Cloud Console → **Credentials**
2. Find the OAuth client named **"Form Gen"**
3. Copy its **Client ID** and **Client Secret**
4. Update your `credentials.json` or environment variables with the correct values

**Option B: Update the OAuth Client Name**
1. In Google Cloud Console → **Credentials**
2. Click on the OAuth client with ID `689227515779-72e576trca43ircif4jh17brv3c26n8b`
3. You can't change the name directly, but you can verify it's the right one
4. Make sure the redirect URIs are correct

### Step 5: Check OAuth Consent Screen

The application name "FormGeneration" might be coming from the OAuth consent screen:

1. Go to **APIs & Services** → **OAuth consent screen**
2. Check the **App name** field
3. If it says "FormGeneration" but you want "Form Gen":
   - You can update it (but this affects all OAuth clients in the project)
   - Or just make sure you're using the correct OAuth client

## Important Notes

- The **OAuth client name** and **OAuth consent screen app name** are different things
- The error message shows the **OAuth consent screen app name**
- What matters for the redirect_uri_mismatch error is:
  1. Using the correct OAuth client (correct Client ID)
  2. Having the correct redirect URIs added to that OAuth client

## Quick Check

Run this to see what redirect URI your app is using:

```bash
# Check the logs when you click "Sign In"
# You should see:
# 🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback
#    (or https://google-from-generator.onrender.com/auth/callback for production)
```

Make sure this **exact** redirect URI is added to your OAuth client in Google Cloud Console.


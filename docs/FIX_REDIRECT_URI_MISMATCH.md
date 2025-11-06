# 🔧 Fix OAuth Redirect URI Mismatch Error

## Error Message

```
Error 400: redirect_uri_mismatch
Bạn không đăng nhập được vì FormGeneration đã gửi một yêu cầu không hợp lệ.
```

## Problem

The redirect URI used in the OAuth flow doesn't match what's configured in your Google Cloud Console OAuth client.

## Solution

You need to add the redirect URI to your Google Cloud Console OAuth client configuration.

### Step 1: Find Your Redirect URI

The redirect URI depends on where you're running the app:

**For Local Development:**
```
http://localhost:5000/auth/callback
```

**For Render.com:**
```
https://your-app-name.onrender.com/auth/callback
```
(Replace `your-app-name` with your actual Render app name)

### Step 2: Add Redirect URI to Google Cloud Console

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to **APIs & Services** → **Credentials**
4. Click on your **OAuth 2.0 Client ID** (Web application type)
5. Under **Authorized redirect URIs**, click **+ ADD URI**
6. Add the redirect URI:
   - For local: `http://localhost:5000/auth/callback`
   - For Render: `https://your-app-name.onrender.com/auth/callback`
7. Click **SAVE**

### Step 3: Verify OAuth Client Type

Make sure your OAuth client is configured as **Web application** (not Desktop app):

1. In Google Cloud Console → **Credentials**
2. Check your OAuth 2.0 Client ID type
3. If it's "Desktop app", you need to create a new "Web application" client:
   - Click **+ CREATE CREDENTIALS** → **OAuth client ID**
   - Application type: **Web application**
   - Add authorized redirect URIs
   - Save and use the new Client ID and Secret

### Step 4: Update Environment Variables (if using env vars)

If you're creating `credentials.json` from environment variables, make sure you're using the **Web application** Client ID and Secret, not the Desktop app ones.

### Step 5: Test

1. Restart your application
2. Try logging in again
3. Check the logs - you should see:
   ```
   🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback
   ```

## Common Redirect URIs

Add these to your Google Cloud Console:

**Local Development:**
- `http://localhost:5000/auth/callback`
- `http://localhost/auth/callback` (if using port 80)

**Production (Render):**
- `https://your-app-name.onrender.com/auth/callback`

**Production (Railway):**
- `https://your-app-name.railway.app/auth/callback`

## Important Notes

1. **Exact Match Required**: The redirect URI must match **exactly** (including protocol, domain, port, and path)
2. **No Trailing Slash**: Don't add a trailing slash (`/`) unless your app uses it
3. **Case Sensitive**: The path is case-sensitive
4. **Wait Time**: After adding a redirect URI, wait a few minutes for Google to update

## Debugging

Check your application logs to see what redirect URI is being used:

```
🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback
   Is production: False
   Request scheme: http
   Request host: localhost:5000
```

Make sure this exact URI is added to your Google Cloud Console.

## Still Having Issues?

1. Double-check the redirect URI in your logs matches what's in Google Cloud Console
2. Make sure you're using the correct OAuth client (Web application, not Desktop)
3. Wait a few minutes after adding the redirect URI
4. Clear your browser cache and cookies
5. Try in an incognito/private window


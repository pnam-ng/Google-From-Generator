# 🔍 Troubleshooting Redirect URI Mismatch

## You've Added the Redirect URIs - But Still Getting Error?

If you've already added the redirect URIs to Google Cloud Console but still getting the error, check these:

### 1. Wait Time

After adding redirect URIs, **wait 2-5 minutes** for Google to propagate the changes. Sometimes it takes a few minutes.

### 2. Check Exact Match

The redirect URI must match **EXACTLY**. Check for:

- ✅ **No trailing slash**: `/auth/callback` (not `/auth/callback/`)
- ✅ **Correct protocol**: `http://` for local, `https://` for production
- ✅ **Correct port**: `:5000` for local (if using port 5000)
- ✅ **Exact domain**: `google-from-generator.onrender.com` (check your actual Render URL)
- ✅ **Case sensitive**: The path is case-sensitive

### 3. Check OAuth Client Type

Make sure your OAuth client is **"Web application"** type:

1. Go to Google Cloud Console → **Credentials**
2. Click on your OAuth client
3. Check the **Application type**
4. If it says **"Desktop app"**, you need to:
   - Create a new **"Web application"** OAuth client
   - Use the new Client ID and Secret
   - Update your `credentials.json` or environment variables

### 4. Check Which OAuth Client You're Using

Make sure you're using the correct OAuth client:

1. Your `credentials.json` has Client ID: `689227515779-72e576trca43ircif4jh17brv3c26n8b`
2. In Google Cloud Console, find the OAuth client with this exact Client ID
3. Make sure you added redirect URIs to **this specific OAuth client**, not a different one

### 5. Check the Logs

When you click "Sign In", check your application logs. You should see:

```
🔗 [LOGIN] Redirect URI: http://localhost:5000/auth/callback
   Is production: False
   Request scheme: http
   Request host: localhost:5000
   Full request URL: http://localhost:5000/auth/login
   Expected redirect URIs in Google Cloud Console:
     - http://localhost:5000/auth/callback
     - https://google-from-generator.onrender.com/auth/callback
   Make sure the redirect URI above matches EXACTLY one of these!
```

**The redirect URI shown in logs must match EXACTLY** what you added in Google Cloud Console.

### 6. Common Mistakes

❌ **Wrong:** `http://localhost:5000/auth/callback/` (trailing slash)
✅ **Correct:** `http://localhost:5000/auth/callback`

❌ **Wrong:** `https://localhost:5000/auth/callback` (HTTPS for local)
✅ **Correct:** `http://localhost:5000/auth/callback`

❌ **Wrong:** `http://google-from-generator.onrender.com/auth/callback` (HTTP for production)
✅ **Correct:** `https://google-from-generator.onrender.com/auth/callback`

❌ **Wrong:** `http://localhost/auth/callback` (missing port)
✅ **Correct:** `http://localhost:5000/auth/callback` (if using port 5000)

### 7. Verify in Google Cloud Console

Double-check in Google Cloud Console:

1. Go to **APIs & Services** → **Credentials**
2. Click on OAuth client: `689227515779-72e576trca43ircif4jh17brv3c26n8b`
3. Under **"Authorized redirect URIs"**, you should see:
   - `http://localhost:5000/auth/callback`
   - `https://google-from-generator.onrender.com/auth/callback`
4. Make sure there are **no extra spaces** or **trailing slashes**

### 8. Try Clearing Browser Cache

Sometimes browser cache can cause issues:

1. Clear browser cache and cookies
2. Try in an incognito/private window
3. Try a different browser

### 9. Check OAuth Consent Screen

The error message shows "FormGeneration" - this is from the OAuth consent screen:

1. Go to **APIs & Services** → **OAuth consent screen**
2. Check the **App name**
3. This doesn't affect the redirect URI, but make sure the consent screen is properly configured

### 10. Still Not Working?

If you've checked all the above and it's still not working:

1. **Share the redirect URI from your logs** - the exact one shown when you click "Sign In"
2. **Share a screenshot** of your Google Cloud Console OAuth client settings
3. **Check if you're using the correct project** - make sure you're in project `bustling-psyche-313714`

## Quick Test

1. Click "Sign In" in your app
2. Check the logs for the redirect URI
3. Copy the exact redirect URI from logs
4. Go to Google Cloud Console → Your OAuth client
5. Check if that exact URI (character by character) is in the "Authorized redirect URIs" list
6. If not, add it exactly as shown in logs
7. Wait 2-5 minutes
8. Try again


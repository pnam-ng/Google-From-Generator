# 🔧 Fix: Gemini API Key Error on Render.com

## Problem
The error "Failed to initialize AI creator" only happens on Render, not locally. This means the `GEMINI_API_KEY` environment variable is not set in Render.

## Quick Fix (3 Steps)

### Step 1: Go to Render Dashboard
1. Visit: https://dashboard.render.com/
2. Sign in to your account
3. Click on your **"google-form-generator"** service (or whatever you named it)

### Step 2: Add Environment Variable
1. In your service dashboard, click on the **"Environment"** tab (in the left sidebar)
2. Scroll down to **"Environment Variables"** section
3. Click **"Add Environment Variable"** button
4. Fill in:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** `YOUR_GEMINI_API_KEY_HERE` (get from https://aistudio.google.com/app/apikey)
5. Click **"Save Changes"**

### Step 3: Redeploy
1. After saving, Render will automatically start a new deployment
2. Wait for deployment to complete (~2-3 minutes)
3. Check the logs to verify it's working

## Detailed Steps with Screenshots Guide

### Step-by-Step:

1. **Navigate to Your Service**
   ```
   Render Dashboard → Your Service → Environment Tab
   ```

2. **Add the Variable**
   - Click "Add Environment Variable"
   - Key: `GEMINI_API_KEY`
   - Value: `YOUR_GEMINI_API_KEY_HERE` (get from https://aistudio.google.com/app/apikey)
   - Click "Save Changes"

3. **Verify It's Added**
   - You should see `GEMINI_API_KEY` in the environment variables list
   - Status should show deployment is in progress

4. **Check Deployment Logs**
   - Go to "Logs" tab
   - Look for any errors
   - Should see "Building..." then "Deploying..."

## Alternative: Use render.yaml (If You Prefer)

If you want to set it in code (less secure, but easier), you can update `render.yaml`:

```yaml
services:
  - type: web
    name: google-form-generator
    env: python
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: python -m gunicorn --config gunicorn_config.py app:app
    plan: free
    healthCheckPath: /api/health
     envVars:
      - key: GEMINI_API_KEY
        sync: false
        # ⚠️ IMPORTANT: Set this value in Render Dashboard → Environment tab
        # Do NOT hardcode API keys here. Use Render Dashboard instead.
      - key: SECRET_KEY
        generateValue: true
      - key: FLASK_ENV
        value: production
      - key: DEBUG
        value: "False"
      - key: PORT
        value: "5000"
```

**⚠️ Warning:** Hardcoding API keys in files is NOT recommended for security. Use environment variables in Render dashboard instead.

## Verify It's Working

After deployment:

1. **Check Health Endpoint:**
   ```
   https://your-app-name.onrender.com/api/health
   ```
   Should return: `{"status":"ok","ai_initialized":true}`

2. **Test Form Creation:**
   - Try creating a form from text
   - Should work without the "Failed to initialize AI creator" error

## Troubleshooting

### Still Getting Error?

1. **Check Environment Variables:**
   - Go to Environment tab
   - Verify `GEMINI_API_KEY` is listed
   - Check there are no extra spaces in the value

2. **Check Deployment Logs:**
   - Go to "Logs" tab
   - Look for error messages
   - Check if the build completed successfully

3. **Verify API Key Format:**
   - Should start with `AIza`
   - Should be about 39 characters
   - No quotes or spaces

4. **Force Redeploy:**
   - Go to "Events" tab
   - Click "Manual Deploy" → "Deploy latest commit"
   - This forces a fresh deployment with new environment variables

### Common Issues

**Issue:** Variable not showing up
- **Fix:** Make sure you clicked "Save Changes" after adding

**Issue:** Deployment fails
- **Fix:** Check logs for build errors
- **Fix:** Verify `requirements.txt` includes all dependencies

**Issue:** Still getting error after setting
- **Fix:** Wait 2-3 minutes for deployment to complete
- **Fix:** Clear browser cache and try again
- **Fix:** Check if you're using the correct service/environment

## Security Best Practices

✅ **DO:**
- Set environment variables in Render dashboard (secure)
- Use different API keys for development and production
- Keep API keys private (never commit to git)

❌ **DON'T:**
- Hardcode API keys in code files
- Commit `.env` files to git
- Share API keys publicly

## Quick Checklist

- [ ] Logged into Render dashboard
- [ ] Navigated to service → Environment tab
- [ ] Added `GEMINI_API_KEY` environment variable
- [ ] Set value to your Gemini API key
- [ ] Saved changes
- [ ] Waited for deployment to complete
- [ ] Tested form creation

---

**That's it!** Once you set the environment variable in Render, the error should be resolved. 🎉



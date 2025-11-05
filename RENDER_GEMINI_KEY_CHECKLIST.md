# ✅ Render GEMINI_API_KEY Setup Checklist

## Current Error

```
Failed to initialize AI creator. Please check your GEMINI_API_KEY is valid.
```

This means the API key is either:
- ❌ Not set in Render
- ❌ Set but invalid/expired
- ❌ Set but with wrong format

## Step-by-Step Fix

### Step 1: Get Your Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Get Your API Key:**
   - If you see existing keys, check if any are active
   - Click **"Create API Key"** to make a new one
   - Copy the key immediately (starts with `AIza...`)

### Step 2: Set in Render Dashboard

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Sign in
   - Click on your service: `google-from-generator`

2. **Navigate to Environment:**
   - Click **"Environment"** tab in left sidebar
   - Scroll to **"Environment Variables"** section

3. **Add/Update GEMINI_API_KEY:**
   - Look for `GEMINI_API_KEY` in the list
   - If it exists, click to **edit** it
   - If it doesn't exist, click **"Add Environment Variable"**
   - Set:
     - **Key:** `GEMINI_API_KEY`
     - **Value:** `YOUR_API_KEY_HERE` (paste your key from Step 1)
   - **IMPORTANT:** 
     - No quotes around the value
     - No spaces before/after
     - Copy the entire key (39 characters)

4. **Save Changes:**
   - Click **"Save Changes"**
   - Render will automatically redeploy

### Step 3: Verify Key Format

Your API key should:
- ✅ Start with `AIza`
- ✅ Be about 39 characters long
- ✅ Have no spaces
- ✅ Look like: `AIzaSy...` (starts with AIza, ~39 characters)

### Step 4: Wait for Redeploy

- Render will automatically redeploy after saving
- Wait 2-3 minutes for deployment to complete
- Check the "Logs" tab to see progress

### Step 5: Check Logs

After deployment, check logs for:

**✅ Success:**
```
✅ Using Gemini model: gemini-1.5-flash
```

**❌ Still Error:**
```
❌ Error initializing AI Creator: ...
```

## Common Issues

### Issue 1: Key Not Visible in Environment

**Fix:**
- Make sure you clicked "Save Changes"
- Refresh the page
- Check if variable is in the list

### Issue 2: Key Has Spaces

**Fix:**
- Remove any spaces before/after the key
- Make sure no quotes around the value

### Issue 3: Wrong Key

**Fix:**
- Make sure you're using Gemini API key, not Google Cloud API key
- Get key from: https://aistudio.google.com/app/apikey
- Not from Google Cloud Console

### Issue 4: Key Expired/Revoked

**Fix:**
- Create a new API key
- Update it in Render
- Redeploy

## Quick Test

After setting the key, test your app:
1. Go to your app URL: `https://google-from-generator.onrender.com`
2. Try creating a form from Google Docs
3. Should work now!

## Complete Environment Variables Checklist

Make sure you have ALL these set in Render:

- ✅ `GEMINI_API_KEY` = Your Gemini API key
- ✅ `SECRET_KEY` = Your Flask secret key
- ✅ `FLASK_ENV` = `production`
- ✅ `DEBUG` = `False`
- ✅ `PORT` = `5000`
- ✅ `GOOGLE_CLIENT_ID` = (if using env vars for credentials)
- ✅ `GOOGLE_CLIENT_SECRET` = (if using env vars for credentials)
- ✅ `GOOGLE_PROJECT_ID` = (if using env vars for credentials)

## Still Not Working?

1. **Check Render Logs:**
   - Go to "Logs" tab
   - Look for error messages
   - Copy the exact error

2. **Verify Key Locally:**
   ```python
   import google.generativeai as genai
   genai.configure(api_key="YOUR_KEY")
   model = genai.GenerativeModel('gemini-1.5-flash')
   response = model.generate_content("Hello")
   print(response.text)
   ```

3. **Get Fresh Key:**
   - Delete old key
   - Create new one
   - Update in Render

---

**Quick Action:** 
1. Go to https://aistudio.google.com/app/apikey
2. Get your API key
3. Add it to Render Dashboard → Environment → `GEMINI_API_KEY`
4. Save and wait for redeploy

That's it! 🎉



# 🔧 Fix: "No API_KEY or ADC found" Error

## Error Message

```
No API_KEY or ADC found. Please either:
- Set the `GOOGLE_API_KEY` environment variable.
- Manually pass the key with `genai.configure(api_key=my_api_key)`.
- Or set up Application Default Credentials
```

## Solution

The code now supports **both** `GEMINI_API_KEY` and `GOOGLE_API_KEY` environment variable names. 

### Set in Render Dashboard

Go to Render Dashboard → Environment tab and set **ONE** of these:

**Option 1 (Recommended):**
- Key: `GEMINI_API_KEY`
- Value: `YOUR_GEMINI_API_KEY_HERE` (get from https://aistudio.google.com/app/apikey)

**Option 2 (Also works):**
- Key: `GOOGLE_API_KEY`
- Value: `YOUR_GEMINI_API_KEY_HERE` (get from https://aistudio.google.com/app/apikey)

## What I Fixed

1. ✅ Code now checks for both `GEMINI_API_KEY` and `GOOGLE_API_KEY`
2. ✅ Better error messages with helpful links
3. ✅ Automatic fallback to environment variables if key not passed directly

## Quick Fix

1. **Go to Render Dashboard:**
   - https://dashboard.render.com/
   - Your service → Environment tab

2. **Add Environment Variable:**
   - Key: `GEMINI_API_KEY` (or `GOOGLE_API_KEY`)
   - Value: Your Gemini API key from https://aistudio.google.com/app/apikey
   - Save

3. **Wait for redeploy** (2-3 minutes)

That's it! The code will now find your API key automatically. 🎉



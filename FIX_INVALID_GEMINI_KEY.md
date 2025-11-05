# 🔧 Fix: Invalid GEMINI_API_KEY Error

## Error Message

```
Failed to initialize AI creator. Please check your GEMINI_API_KEY is valid.
```

## What This Means

The API key is **set** but **invalid** or **has issues**. This could be:
- ❌ Invalid API key format
- ❌ Revoked/disabled API key
- ❌ API key doesn't have Gemini API access
- ❌ API key expired
- ❌ Network/API issues

## Quick Fix

### Step 1: Get a New Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Create or Get API Key:**
   - If you have existing keys, check if any are active
   - Click **"Create API Key"** to make a new one
   - Or regenerate an existing key

3. **Copy the Key:**
   - Should start with `AIza...`
   - About 39 characters long
   - Copy it immediately (you can't see it again!)

### Step 2: Verify Key Format

Your API key should:
- ✅ Start with `AIza`
- ✅ Be about 39 characters
- ✅ Have no spaces or special characters (except dashes)
- ✅ Look like: `AIzaSy...` (starts with AIza, ~39 characters)

### Step 3: Update Your Key

#### **If on Render:**

1. Go to Render Dashboard → Your Service → Environment
2. Find `GEMINI_API_KEY`
3. Click to edit
4. Paste your new API key
5. Save and redeploy

#### **If Running Locally:**

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="YOUR_NEW_KEY_HERE"
python app.py
```

**Windows CMD:**
```cmd
set GEMINI_API_KEY=YOUR_NEW_KEY_HERE
python app.py
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="YOUR_NEW_KEY_HERE"
python app.py
```

#### **Or Update .env file:**
```env
GEMINI_API_KEY=YOUR_NEW_KEY_HERE
```

### Step 4: Test the Key

You can test if your key works:

```python
import google.generativeai as genai

genai.configure(api_key="YOUR_KEY_HERE")
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Hello")
print(response.text)
```

If this works, your key is valid!

## Common Issues

### Issue 1: Key Doesn't Work

**Solution:**
- Make sure you're using the key from https://aistudio.google.com/app/apikey
- Not from Google Cloud Console (different service)
- Create a new key if unsure

### Issue 2: "API key not found"

**Solution:**
- Check for typos in the key
- Make sure there are no extra spaces
- Copy-paste the entire key

### Issue 3: "Permission denied" or "403"

**Solution:**
- Your key might be restricted
- Check API key restrictions in Google Cloud Console
- Make sure Gemini API is enabled for your project

### Issue 4: Works Locally but Not on Render

**Solution:**
- Make sure you set the environment variable in Render Dashboard
- Check Render logs for the actual error
- Verify the key is set correctly (no quotes, no spaces)

## Verify Your Setup

### Check Key Format:
```bash
# The key should be about 39 characters
echo $GEMINI_API_KEY | wc -c  # Should show ~40 (including newline)
```

### Check Key Starts Correctly:
```bash
# Should start with AIza
echo $GEMINI_API_KEY | head -c 4  # Should show "AIza"
```

## Still Not Working?

1. **Get a fresh API key:**
   - Delete old key
   - Create new one
   - Update everywhere

2. **Check API Status:**
   - Visit: https://status.cloud.google.com/
   - Check if Gemini API is having issues

3. **Try Different Model:**
   - The code tries multiple models automatically
   - If one fails, it tries others

4. **Check Network:**
   - Make sure you can access Google APIs
   - Check firewall/proxy settings

## Quick Test Script

Create `test_gemini_key.py`:

```python
import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY', 'YOUR_KEY_HERE')
print(f"Testing API key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello")
    print("✅ API key is valid!")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"❌ API key is invalid: {e}")
```

Run it:
```bash
python test_gemini_key.py
```

---

**Quick Answer:** Get a new API key from https://aistudio.google.com/app/apikey and update it in your environment variables!



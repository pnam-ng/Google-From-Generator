# 🔧 Fix: "Failed to initialize AI creator"

## Error Message

```
❌ Error: Failed to initialize AI creator. Please check your credentials.
```

## Cause

The `GEMINI_API_KEY` environment variable is either:
- Not set
- Empty
- Invalid

## Quick Fix

### Step 1: Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy the API key (starts with `AIza...`)

**Replace with your actual API key from Google AI Studio**

### Step 2: Set Environment Variable

#### **Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
python app.py
```

#### **Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
python app.py
```

#### **macOS/Linux:**
```bash
export GEMINI_API_KEY="AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY"
python app.py
```

### Step 3: Create `.env` File (Recommended)

Create a file named `.env` in your project root:

```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
SECRET_KEY=your_secret_key_here
```

Then install `python-dotenv` if not already installed:
```bash
pip install python-dotenv
```

The app will automatically load variables from `.env` file.

### Step 4: For Production/Deployment

#### **Render.com:**
1. Go to your service dashboard
2. Click **"Environment"** tab
3. Add environment variable:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY`
4. Save and redeploy

#### **Railway:**
1. Go to your project dashboard
2. Click **"Variables"** tab
3. Add variable:
   - Key: `GEMINI_API_KEY`
   - Value: `AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY`
4. Save

#### **Docker:**
Add to `docker-compose.yml`:
```yaml
environment:
  - GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

Or use `.env` file (recommended).

## Verify It's Set

### Check in Python:
```python
import os
print(os.getenv('GEMINI_API_KEY'))
```

Should print your API key (not empty).

### Check in Terminal:
```bash
# Windows
echo %GEMINI_API_KEY%

# macOS/Linux
echo $GEMINI_API_KEY
```

## Permanent Solution (Windows)

### Option 1: System Environment Variables
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click **"Advanced"** tab
3. Click **"Environment Variables"**
4. Under **"User variables"**, click **"New"**
5. Variable name: `GEMINI_API_KEY`
6. Variable value: `AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY`
7. Click **"OK"** on all dialogs
8. Restart your terminal/IDE

### Option 2: Create `.env` File (Best Practice)

Create `.env` in project root:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

Make sure `.env` is in `.gitignore` (don't commit it to git!)

## Troubleshooting

### Still getting error?

1. **Check if variable is actually set:**
   ```python
   import os
   key = os.getenv('GEMINI_API_KEY')
   print(f"Key length: {len(key) if key else 0}")
   ```

2. **Restart your server:**
   - Environment variables are loaded when the server starts
   - Set the variable BEFORE running `python app.py`

3. **Check for typos:**
   - Variable name must be exactly: `GEMINI_API_KEY`
   - Not: `GEMINI_API`, `GEMINIKEY`, etc.

4. **Verify API key format:**
   - Should start with `AIza`
   - Should be about 39 characters long
   - No spaces or quotes in the value

## Quick Test

Run this to verify:
```bash
# Set key
export GEMINI_API_KEY="AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY"  # Linux/Mac
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE      # Windows CMD

# Verify
python -c "import os; print('✅ Key set' if os.getenv('GEMINI_API_KEY') else '❌ Key not set')"
```

---

**That's it!** Once the API key is set, restart your app and it should work. 🎉



# 🔧 Fix "gunicorn: command not found" on Render

## Quick Fix

In your Render dashboard, update these settings:

### 1. Build Command:
```
pip install --upgrade pip && pip install -r requirements.txt
```

### 2. Start Command (CHANGE THIS):
```
python -m gunicorn --config gunicorn_config.py app:app
```

**Important:** Use `python -m gunicorn` instead of just `gunicorn`

### 3. Verify requirements.txt has:
```
gunicorn>=21.2.0
```

## Steps to Fix:

1. **Go to Render Dashboard** → Your Service → Settings
2. **Update Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```
3. **Update Start Command:**
   ```
   python -m gunicorn --config gunicorn_config.py app:app
   ```
4. **Click "Save Changes"**
5. **Go to "Events" tab** → Click "Manual Deploy" → "Deploy latest commit"

## Why This Works:

- `python -m gunicorn` uses Python's module system to find gunicorn
- This ensures gunicorn is found even if it's not in PATH
- The `--upgrade pip` ensures latest pip version

## Alternative (If Still Not Working):

If `python -m gunicorn` doesn't work, try:
```bash
/opt/render/project/src/.venv/bin/gunicorn --config gunicorn_config.py app:app
```

Or use full Python path:
```bash
python3 -m gunicorn --config gunicorn_config.py app:app
```

## Verify Installation:

After deployment, check logs to see if gunicorn is installed:
- Look for "Successfully installed gunicorn" in build logs
- If not installed, check build logs for errors


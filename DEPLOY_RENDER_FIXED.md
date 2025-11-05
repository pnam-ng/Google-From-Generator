# 🔧 Fixed Render Deployment Guide

## Problem: "gunicorn: command not found"

This happens when gunicorn isn't installed or not in PATH. Here's the fix:

## Solution 1: Use Python Module Syntax (Recommended)

In Render dashboard, change your **Start Command** to:
```bash
python -m gunicorn --config gunicorn_config.py app:app
```

This uses Python's module system to find gunicorn.

## Solution 2: Use Full Path

If that doesn't work, use:
```bash
/opt/render/project/src/.venv/bin/gunicorn --config gunicorn_config.py app:app
```

## Solution 3: Install in Build Command

Update your **Build Command** to:
```bash
pip install --upgrade pip && pip install -r requirements.txt
```

## Updated Render Configuration

### In Render Dashboard:

1. **Build Command:**
   ```
   pip install --upgrade pip && pip install -r requirements.txt
   ```

2. **Start Command:**
   ```
   python -m gunicorn --config gunicorn_config.py app:app
   ```

3. **Environment Variables:**
   ```
   GEMINI_API_KEY = your_api_key
   SECRET_KEY = your_secret_key
   FLASK_ENV = production
   DEBUG = False
   PORT = 5000
   ```

## Verify Requirements.txt

Make sure `gunicorn` is in `requirements.txt`:
```
gunicorn>=21.2.0
```

## Alternative: Use Flask's Built-in Server (NOT Recommended for Production)

If gunicorn still doesn't work, you can temporarily use Flask's server:
```bash
python app.py
```

But this is **NOT recommended** for production. Fix gunicorn instead.

## Quick Fix Steps:

1. Go to Render Dashboard → Your Service → Settings
2. Update **Build Command:** `pip install --upgrade pip && pip install -r requirements.txt`
3. Update **Start Command:** `python -m gunicorn --config gunicorn_config.py app:app`
4. Click "Save Changes"
5. Manual Deploy → "Deploy latest commit"

This should fix the issue!


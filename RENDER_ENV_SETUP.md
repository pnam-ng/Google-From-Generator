# 🔧 Setting Environment Variables in Render

## Important: Render Doesn't Use .env Files!

Render uses environment variables set in the dashboard, not `.env` files. However, you can use `.env.example` as a reference.

## Step-by-Step: Set Environment Variables in Render

### Step 1: Go to Render Dashboard

1. Visit: https://dashboard.render.com/
2. Sign in
3. Click on your service: `google-from-generator`

### Step 2: Navigate to Environment Tab

1. Click **"Environment"** tab in the left sidebar
2. Scroll to **"Environment Variables"** section

### Step 3: Add Variables One by One

Use the values from `.env.example` and add them in Render:

#### Required Variables:

1. **GEMINI_API_KEY**
   - Key: `GEMINI_API_KEY`
   - Value: Your Gemini API key (from https://aistudio.google.com/app/apikey)
   - **How to get:**
     1. Go to https://aistudio.google.com/app/apikey
     2. Sign in with your Google account
     3. Click "Create API Key"
     4. Copy the generated key
     5. Paste it as the value in Render
   - Format: Starts with `AIzaSy...` (long alphanumeric string)

2. **SECRET_KEY**
   - Key: `SECRET_KEY`
   - Value: Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Example: `a1b2c3d4e5f6...` (64 characters)

3. **FLASK_ENV**
   - Key: `FLASK_ENV`
   - Value: `production`

4. **DEBUG**
   - Key: `DEBUG`
   - Value: `False`

5. **PORT** (Optional)
   - Key: `PORT`
   - Value: `5000`

#### Optional Variables (if using env vars for credentials):

6. **GOOGLE_CLIENT_ID** (if not using credentials.json file)
   - Key: `GOOGLE_CLIENT_ID`
   - Value: From your credentials.json file

7. **GOOGLE_CLIENT_SECRET** (if not using credentials.json file)
   - Key: `GOOGLE_CLIENT_SECRET`
   - Value: From your credentials.json file

8. **GOOGLE_PROJECT_ID** (if not using credentials.json file)
   - Key: `GOOGLE_PROJECT_ID`
   - Value: From your credentials.json file

9. **CREDENTIALS_FILE_PATH** (if credentials.json is in custom location)
   - Key: `CREDENTIALS_FILE_PATH`
   - Value: `/etc/secrets/credentials.json` (or your custom path)

### Step 4: Save and Deploy

1. Click **"Save Changes"** after adding each variable
2. Render will automatically redeploy
3. Wait 2-3 minutes for deployment

## Quick Checklist

Copy from `.env.example` and add to Render:

- [ ] `GEMINI_API_KEY` = Your Gemini API key
- [ ] `SECRET_KEY` = Generated secret key
- [ ] `FLASK_ENV` = `production`
- [ ] `DEBUG` = `False`
- [ ] `PORT` = `5000` (optional)
- [ ] `GOOGLE_CLIENT_ID` = (if not using credentials.json file)
- [ ] `GOOGLE_CLIENT_SECRET` = (if not using credentials.json file)
- [ ] `GOOGLE_PROJECT_ID` = (if not using credentials.json file)
- [ ] `CREDENTIALS_FILE_PATH` = (if using custom path like `/etc/secrets/credentials.json`)

## For Local Development

If you want to use `.env` file locally:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and fill in your actual values

3. Install python-dotenv (already in requirements.txt):
   ```bash
   pip install python-dotenv
   ```

4. The app will automatically load from `.env`

## Important Notes

- ✅ **Render:** Set variables in dashboard (Environment tab)
- ✅ **Local:** Use `.env` file (convenient for development)
- ❌ **Don't commit `.env`** to git (already in .gitignore)
- ✅ **Do commit `.env.example`** (template only)

---

**Quick Answer:** Use `.env.example` as a reference, then copy those variable names and values to Render Dashboard → Environment tab!



# Detailed Setup Guide

## Step-by-Step Setup Instructions

### Step 1: Install Python

Make sure you have Python 3.7 or higher installed:

**Windows:**
- Download from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"

**macOS:**
- Python 3 is usually pre-installed
- Check version: `python3 --version`
- If not installed, use Homebrew: `brew install python3`

**Linux:**
- `sudo apt-get update && sudo apt-get install python3 python3-pip`

### Step 2: Install Dependencies

Open a terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

Or on macOS/Linux:

```bash
pip3 install -r requirements.txt
```

### Step 3: Google Cloud Console Setup

#### 3.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on the project dropdown at the top
3. Click "New Project"
4. Enter a project name (e.g., "Google Forms Generator")
5. Click "Create"

#### 3.2 Enable Required APIs

**You need to enable TWO APIs:**

**A. Enable Google Forms API:**
1. In your project, go to "APIs & Services" > "Library"
2. Search for "Google Forms API"
3. Click on "Google Forms API"
4. Click the "Enable" button

**B. Enable Google Drive API (REQUIRED):**
1. Still in "APIs & Services" > "Library"
2. Search for "Google Drive API"
3. Click on "Google Drive API"
4. Click the "Enable" button

**C. Enable Google Docs API (REQUIRED for Docs link feature):**
1. Still in "APIs & Services" > "Library"
2. Search for "Google Docs API"
3. Click on "Google Docs API"
4. Click the "Enable" button

**⚠️ IMPORTANT:** 
- Google Forms API requires Google Drive API to create forms. Both must be enabled!
- Google Docs API is required if you want to use the "Google Docs Link" feature to generate forms from Google Docs documents.

#### 3.3 Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Choose "External" (unless you have a Google Workspace account)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Google Forms Generator"
   - User support email: Your email
   - Developer contact information: Your email
5. Click "Save and Continue"
6. Skip "Scopes" (click "Save and Continue")
7. **IMPORTANT: Add Test Users** (This is critical!)
   - You will see a section called "Test users"
   - Click "ADD USERS"
   - Enter your Google email address (the one you'll use to sign in)
   - Click "ADD"
   - You can add multiple test users if needed
8. Click "Save and Continue"
9. Review and go back to dashboard

**⚠️ CRITICAL NOTE:** If you skip step 7, you will get a "403: access_denied" error when trying to authenticate. Your email MUST be in the test users list!

#### 3.4 Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Choose application type: **Desktop app**
4. Name it: "Google Forms Generator Client"
5. Click "Create"
6. Click "Download JSON"
7. Save the file as `credentials.json` in your project root directory

### Step 4: Verify Setup

Run the configuration helper:

```bash
python config_helper.py
```

Or on macOS/Linux:

```bash
python3 config_helper.py
```

This will verify that your credentials file is set up correctly.

### Step 5: First Run

Run the example script:

```bash
python example.py
```

Or:

```bash
python3 example.py
```

On first run:
1. A browser window will open
2. Sign in with your Google account
3. Grant the necessary permissions
4. A `token.pickle` file will be created (this stores your authentication)

## Troubleshooting

### Issue: "credentials.json not found"

**Solution:**
- Make sure you downloaded the JSON file from Google Cloud Console
- Rename it to exactly `credentials.json`
- Place it in the same directory as `google_form_generator.py`

### Issue: "403: access_denied" or "Access blocked: This app's request is invalid"

**Error Message (Vietnamese):**
```
FormGeneration chưa hoàn tất quy trình xác minh của Google. 
Ứng dụng này đang trong giai đoạn kiểm thử...
```

**Solution (Cách khắc phục):**
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Select your project
3. Navigate to "APIs & Services" > "OAuth consent screen"
4. Scroll down to the "Test users" section
5. Click "ADD USERS"
6. Enter your Google email address (the exact email you use to sign in)
7. Click "ADD"
8. Click "SAVE" at the bottom
9. Run your script again

**Important:** 
- The email you add must be the EXACT email you use to sign in to Google
- You can add multiple test users if needed
- For production use, you'll need to publish your app (requires verification)
- This is a common issue when the app is in "Testing" mode

### Issue: "API not enabled" or "Google Drive API has not been used"

**Error Message:**
```
Google Drive API has not been used in project ... or it is disabled.
Enable it by visiting https://console.developers.google.com/...
```

**Solution:**
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. **Enable Google Drive API:**
   - Search for "Google Drive API"
   - Click on it
   - Click "Enable"
5. **Enable Google Forms API** (if not already enabled):
   - Search for "Google Forms API"
   - Click on it
   - Click "Enable"
6. Wait 2-5 minutes for APIs to activate
7. Run your script again

**Important:** Both APIs must be enabled. Google Forms API requires Google Drive API to create forms.

### Issue: Authentication popup doesn't open

**Solution:**
- Make sure you're running the script from a terminal
- Check firewall settings
- Try running: `python -m google_form_generator` directly

### Issue: "Module not found"

**Solution:**
- Make sure you installed dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.7+)

## Cross-Platform Notes

### Windows
- Use `python` command (or `py` if multiple Python versions)
- Path separators are handled automatically
- No special permissions needed

### macOS
- Use `python3` command
- May need to grant terminal permissions in System Preferences > Security & Privacy
- If you get SSL errors, update certificates: `/Applications/Python\ 3.x/Install\ Certificates.command`

### Linux
- Use `python3` command
- May need to install: `sudo apt-get install python3-venv python3-pip`
- For better isolation, use virtual environments

## Virtual Environment (Recommended)

For better dependency management, use a virtual environment:

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then run your scripts as usual.


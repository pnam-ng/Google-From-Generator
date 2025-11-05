"""
Diagnostic script to check Google Forms Generator setup
Helps identify configuration issues before running the main script
"""

import os
import json
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def check_credentials_file():
    """Check if credentials.json exists and is valid."""
    print_header("Checking Credentials File")
    
    creds_file = 'credentials.json'
    
    if not os.path.exists(creds_file):
        print(f"❌ {creds_file} not found!")
        print("\n📝 Solution:")
        print("   1. Go to Google Cloud Console")
        print("   2. Create OAuth 2.0 credentials (Desktop app)")
        print("   3. Download the JSON file")
        print(f"   4. Save it as '{creds_file}' in this directory")
        return False
    
    print(f"✅ {creds_file} found")
    
    try:
        with open(creds_file, 'r') as f:
            data = json.load(f)
        
        # Check structure
        oauth_data = data.get('installed') or data.get('web')
        
        if not oauth_data:
            print("❌ Invalid credentials file structure")
            print("   Expected 'installed' or 'web' key")
            return False
        
        print("✅ Credentials file is valid JSON")
        
        # Extract client info
        client_id = oauth_data.get('client_id', 'Not found')
        project_id = data.get('project_id', 'Not found')
        
        print(f"\n📋 Credentials Info:")
        print(f"   Project ID: {project_id}")
        print(f"   Client ID: {client_id[:50]}..." if len(str(client_id)) > 50 else f"   Client ID: {client_id}")
        
        # Check if it's desktop app type
        if 'installed' in data:
            print("✅ Application type: Desktop app (correct)")
        elif 'web' in data:
            print("⚠️  Application type: Web app (should be Desktop app)")
            print("   Consider creating Desktop app credentials instead")
        
        return True
        
    except json.JSONDecodeError:
        print("❌ Invalid JSON format")
        return False
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False


def check_token_file():
    """Check if token.pickle exists."""
    print_header("Checking Token File")
    
    token_file = 'token.pickle'
    
    if os.path.exists(token_file):
        print(f"✅ {token_file} exists (authentication completed before)")
        print("   If you're having issues, try deleting this file and re-authenticating")
        return True
    else:
        print(f"ℹ️  {token_file} not found (will be created on first authentication)")
        return True


def check_dependencies():
    """Check if required Python packages are installed."""
    print_header("Checking Python Dependencies")
    
    required_packages = [
        'google.auth',
        'google_auth_oauthlib',
        'googleapiclient',
    ]
    
    all_installed = True
    
    for package in required_packages:
        try:
            # Try importing the package
            if package == 'google.auth':
                import google.auth
            elif package == 'google_auth_oauthlib':
                import google_auth_oauthlib
            elif package == 'googleapiclient':
                import googleapiclient
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} not installed")
            all_installed = False
    
    if not all_installed:
        print("\n📝 Solution:")
        print("   Run: pip install -r requirements.txt")
        print("   Or: pip3 install -r requirements.txt")
    
    return all_installed


def check_oauth_consent_screen():
    """Provide instructions for OAuth consent screen setup."""
    print_header("OAuth Consent Screen Checklist")
    
    print("⚠️  IMPORTANT: Verify these settings in Google Cloud Console:\n")
    
    checklist = [
        "1. OAuth consent screen is configured",
        "2. App is in 'Testing' mode (for development)",
        "3. Your email is added to 'Test users' list",
        "4. Google Forms API is enabled",
        "5. Google Drive API is enabled (required for Forms API)"
    ]
    
    for item in checklist:
        print(f"   ☐ {item}")
    
    print("\n📝 To add yourself as a test user:")
    print("   1. Go to: https://console.cloud.google.com/")
    print("   2. Select your project")
    print("   3. Navigate to: APIs & Services > OAuth consent screen")
    print("   4. Scroll to 'Test users' section")
    print("   5. Click 'ADD USERS'")
    print("   6. Enter your Google email")
    print("   7. Click 'SAVE'")
    
    print("\n📖 For detailed instructions, see: FIX_403_ERROR.md")


def check_python_version():
    """Check Python version."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 7:
        print("✅ Python version is compatible (3.7+)")
        return True
    else:
        print("❌ Python 3.7 or higher is required")
        print("   Please upgrade Python")
        return False


def main():
    """Run all diagnostic checks."""
    print("\n" + "=" * 70)
    print("  Google Forms Generator - Setup Diagnostic")
    print("=" * 70)
    print("\nThis script will check your setup and identify any issues.\n")
    
    results = {
        'credentials': check_credentials_file(),
        'dependencies': check_dependencies(),
        'python_version': check_python_version(),
        'token': check_token_file(),
    }
    
    check_oauth_consent_screen()
    
    # Summary
    print_header("Diagnostic Summary")
    
    all_ok = all([
        results['credentials'],
        results['dependencies'],
        results['python_version']
    ])
    
    if all_ok:
        print("✅ Basic setup looks good!")
        print("\n📝 Next steps:")
        print("   1. Make sure your email is in the Test users list")
        print("   2. Run: python quick_start.py")
        print("   3. If you get 403 error, see: FIX_403_ERROR.md")
    else:
        print("❌ Some issues found. Please fix them before proceeding.")
        print("\n📖 See setup_guide.md for detailed instructions")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during diagnostic: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


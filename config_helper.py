"""
Configuration helper for Google Forms Generator
Provides utilities for managing credentials and configuration
"""

import os
import json
from pathlib import Path


class ConfigHelper:
    """Helper class for managing configuration and credentials."""
    
    @staticmethod
    def check_credentials_file(file_path: str = 'credentials.json') -> bool:
        """
        Check if credentials file exists and is valid.
        
        Args:
            file_path: Path to credentials file
        
        Returns:
            True if file exists and is valid, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Check if it has the required OAuth structure
                if 'installed' in data or 'web' in data:
                    return True
                return False
        except (json.JSONDecodeError, KeyError):
            return False
    
    @staticmethod
    def get_credentials_info(file_path: str = 'credentials.json') -> dict:
        """
        Get information about credentials file.
        
        Args:
            file_path: Path to credentials file
        
        Returns:
            Dictionary with credentials information
        """
        if not os.path.exists(file_path):
            return {
                'exists': False,
                'valid': False,
                'message': f'Credentials file not found at {file_path}'
            }
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
            info = {
                'exists': True,
                'valid': True,
                'client_id': None,
                'project_id': None,
                'auth_uri': None,
                'token_uri': None
            }
            
            # Handle both 'installed' and 'web' OAuth types
            oauth_data = data.get('installed') or data.get('web') or {}
            
            if oauth_data:
                info['client_id'] = oauth_data.get('client_id', 'Not found')
                info['project_id'] = data.get('project_id', 'Not found')
                info['auth_uri'] = oauth_data.get('auth_uri', 'Not found')
                info['token_uri'] = oauth_data.get('token_uri', 'Not found')
            
            return info
            
        except Exception as e:
            return {
                'exists': True,
                'valid': False,
                'message': f'Error reading credentials file: {str(e)}'
            }
    
    @staticmethod
    def print_setup_instructions():
        """Print setup instructions for the user."""
        print("\n" + "=" * 70)
        print("Google Forms Generator - Setup Instructions")
        print("=" * 70)
        print("\n1. Go to Google Cloud Console:")
        print("   https://console.cloud.google.com/")
        print("\n2. Create a new project or select an existing one")
        print("\n3. Enable Google Forms API:")
        print("   - Navigate to 'APIs & Services' > 'Library'")
        print("   - Search for 'Google Forms API'")
        print("   - Click 'Enable'")
        print("\n4. Create OAuth 2.0 Credentials:")
        print("   - Go to 'APIs & Services' > 'Credentials'")
        print("   - Click 'Create Credentials' > 'OAuth client ID'")
        print("   - Configure OAuth consent screen (if not done)")
        print("   - Choose application type: 'Desktop app'")
        print("   - Download the JSON file")
        print("   - Rename it to 'credentials.json'")
        print("   - Place it in the project root directory")
        print("\n5. Run your script - authentication will happen automatically")
        print("\n" + "=" * 70 + "\n")
    
    @staticmethod
    def validate_setup() -> bool:
        """
        Validate that the setup is complete.
        
        Returns:
            True if setup is valid, False otherwise
        """
        if not ConfigHelper.check_credentials_file():
            print("\n❌ Setup incomplete: credentials.json not found or invalid")
            ConfigHelper.print_setup_instructions()
            return False
        
        print("\n✅ Credentials file found and valid")
        return True


if __name__ == '__main__':
    # Check setup
    print("Checking Google Forms Generator setup...")
    
    if ConfigHelper.validate_setup():
        info = ConfigHelper.get_credentials_info()
        print("\nCredentials Information:")
        print(f"  Project ID: {info.get('project_id', 'N/A')}")
        print(f"  Client ID: {info.get('client_id', 'N/A')[:50]}..." if info.get('client_id') else "  Client ID: N/A")
        print("\n✅ Setup is complete! You can now use the Google Forms Generator.")
    else:
        print("\n⚠️  Please complete the setup before using the generator.")


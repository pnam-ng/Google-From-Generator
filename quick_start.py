"""
Quick Start Script - Create a simple form to test the setup
"""

from google_form_generator import GoogleFormGenerator
from config_helper import ConfigHelper


def quick_start():
    """Quick start example - creates a simple test form."""
    print("\n" + "=" * 70)
    print("Google Forms Generator - Quick Start")
    print("=" * 70)
    
    # Check setup first
    if not ConfigHelper.validate_setup():
        return
    
    print("\nCreating a simple test form...")
    
    try:
        # Initialize generator
        generator = GoogleFormGenerator()
        
        # Create a simple form
        form = generator.create_form(
            title="Quick Test Form",
            description="This is a test form created by Google Forms Generator"
        )
        
        # Add a few basic questions
        form.add_question(
            question_text="What is your name?",
            question_type="text",
            required=True
        )
        
        form.add_question(
            question_text="Rate your experience (1-5)",
            question_type="scale",
            scale_min=1,
            scale_max=5,
            scale_min_label="Poor",
            scale_max_label="Excellent"
        )
        
        form.add_question(
            question_text="What is your favorite programming language?",
            question_type="choice",
            options=["Python", "JavaScript", "Java", "C++", "Other"]
        )
        
        # Get URLs
        view_url = form.get_url()
        edit_url = form.get_edit_url()
        
        print("\n" + "=" * 70)
        print("✅ Form created successfully!")
        print("=" * 70)
        print(f"\n📝 View your form:")
        print(f"   {view_url}")
        print(f"\n✏️  Edit your form:")
        print(f"   {edit_url}")
        print("\n" + "=" * 70 + "\n")
        
        return view_url
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("\nPlease follow the setup instructions in README.md or setup_guide.md")
        
    except PermissionError as e:
        # This is the 403 access_denied error
        print(str(e))
        print("\n📖 For detailed fix instructions, see: FIX_403_ERROR.md")
        print("   Or run: python diagnose_setup.py")
        
    except Exception as e:
        error_str = str(e).lower()
        if 'access_denied' in error_str or '403' in error_str:
            print("\n" + "="*70)
            print("❌ 403: access_denied Error Detected")
            print("="*70)
            print("\nYour app is in testing mode. You need to add your email")
            print("to the Test users list in Google Cloud Console.")
            print("\n📖 See FIX_403_ERROR.md for step-by-step instructions")
            print("\nQuick fix:")
            print("1. Go to: https://console.cloud.google.com/")
            print("2. APIs & Services > OAuth consent screen")
            print("3. Scroll to 'Test users' > Click 'ADD USERS'")
            print("4. Add your Google email > Click 'SAVE'")
            print("5. Run this script again")
            print("="*70)
        else:
            print(f"\n❌ An error occurred: {e}")
            import traceback
            traceback.print_exc()
            print("\nPlease check:")
            print("1. Google Forms API is enabled in Google Cloud Console")
            print("2. OAuth consent screen is configured")
            print("3. credentials.json is valid")
            print("4. Run: python diagnose_setup.py")


if __name__ == '__main__':
    quick_start()


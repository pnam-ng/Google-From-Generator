"""
Quick test script for AI form creation
"""

from ai_form_creator import AIFormCreator

# Gemini API Key
# Get your API key from: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "YOUR_API_KEY_HERE"

def test_text_input():
    """Test form creation from text."""
    print("Testing text input...")
    
    creator = AIFormCreator(GEMINI_API_KEY)
    
    text = """
    Create a simple customer feedback form with:
    - Customer name (required)
    - Email address (required)
    - Rating (1-5 scale)
    - Feedback comments
    """
    
    try:
        form_url = creator.create_form_from_text(text)
        print(f"\n✅ Test successful! Form URL: {form_url}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def test_file_input():
    """Test form creation from file."""
    print("Testing file input...")
    
    creator = AIFormCreator(GEMINI_API_KEY)
    
    try:
        form_url = creator.create_form_from_file("example_input.txt")
        print(f"\n✅ Test successful! Form URL: {form_url}")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'file':
        test_file_input()
    else:
        test_text_input()



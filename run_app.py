"""
Launcher script for the web application
Cross-platform launcher for Windows and macOS
"""

import os
import sys
import webbrowser
from threading import Timer

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import flask
        return True
    except ImportError:
        print("\n" + "="*70)
        print("❌ Missing dependency: Flask")
        print("="*70)
        print("Please install Flask:")
        print("  pip install flask")
        print("\nOr install all dependencies:")
        print("  pip install -r requirements.txt")
        print("="*70 + "\n")
        return False

def main():
    """Main launcher function."""
    print("\n" + "="*70)
    print("  🌐 AI-Powered Google Form Creator")
    print("  Web Application Launcher")
    print("="*70)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import app after checking dependencies
    from app import app
    
    print("\n📝 Starting web server...")
    print("💡 The application will open in your browser automatically")
    print("💡 Server URL: http://127.0.0.1:5000")
    print("💡 Press Ctrl+C to stop the server\n")
    print("="*70 + "\n")
    
    # Open browser after a short delay
    def open_browser():
        try:
            webbrowser.open('http://127.0.0.1:5000')
        except:
            print("⚠️  Could not open browser automatically.")
            print("   Please open http://127.0.0.1:5000 in your browser manually.")
    
    Timer(1.5, open_browser).start()
    
    # Run Flask app
    try:
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


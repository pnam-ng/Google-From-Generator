"""
Helper script to install optional dependencies for file reading
"""

import subprocess
import sys

def install_package(package):
    """Install a Python package using pip."""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {package}")
        return False

def main():
    """Install optional dependencies."""
    print("\n" + "="*70)
    print("  Installing Optional Dependencies for File Reading")
    print("="*70)
    
    dependencies = {
        'python-docx': 'Word documents (.docx, .doc)',
        'PyPDF2': 'PDF files (.pdf)',
        'pandas': 'Excel/CSV files (.xlsx, .xls, .csv)',
        'openpyxl': 'Excel files (.xlsx)'
    }
    
    print("\nOptional dependencies:")
    for i, (package, description) in enumerate(dependencies.items(), 1):
        print(f"  {i}. {package:15} - {description}")
    
    print("\nChoose what to install:")
    print("  1. Install all dependencies")
    print("  2. Install only Word document support (python-docx)")
    print("  3. Install only PDF support (PyPDF2)")
    print("  4. Install only Excel/CSV support (pandas, openpyxl)")
    print("  5. Exit")
    
    choice = input("\nEnter your choice (1-5): ").strip()
    
    if choice == '1':
        print("\nInstalling all dependencies...")
        for package in dependencies.keys():
            install_package(package)
    
    elif choice == '2':
        install_package('python-docx')
    
    elif choice == '3':
        install_package('PyPDF2')
    
    elif choice == '4':
        install_package('pandas')
        install_package('openpyxl')
    
    elif choice == '5':
        print("\n👋 Exiting...")
        return
    
    else:
        print("❌ Invalid choice.")
        return
    
    print("\n" + "="*70)
    print("✅ Installation complete!")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Installation cancelled.")
    except Exception as e:
        print(f"\n❌ Error: {e}")


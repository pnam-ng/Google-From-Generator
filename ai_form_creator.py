"""
AI-Powered Google Form Creator
Uses Gemini AI to generate forms from user input (text or file upload)
"""

import os
import sys
from typing import Optional
from google_form_generator import GoogleFormGenerator
from gemini_form_generator import GeminiFormGenerator


class AIFormCreator:
    """Main class for AI-powered form creation."""
    
    def __init__(self, gemini_api_key: str):
        """
        Initialize AI Form Creator.
        
        Args:
            gemini_api_key: Google Gemini API key
        """
        self.gemini = GeminiFormGenerator(gemini_api_key)
        self.form_generator = GoogleFormGenerator()
    
    def create_form_from_text(self, text: str) -> str:
        """
        Create a Google Form from text input using AI.
        
        Args:
            text: User's text describing the form requirements
        
        Returns:
            URL of the created form
        """
        print("\n" + "="*70)
        print("🤖 Generating form structure using Gemini AI...")
        print("="*70)
        
        # Generate form structure from text
        try:
            form_structure = self.gemini.generate_from_text(text)
            print("✅ Form structure generated successfully!")
        except Exception as e:
            print(f"❌ Error generating form structure: {e}")
            raise
        
        # Return structure for preview
        return form_structure
    
    def generate_form_structure_from_google_doc(self, doc_url: str) -> dict:
        """
        Generate form structure from Google Docs link.
        
        Args:
            doc_url: Google Docs URL
        
        Returns:
            Dictionary containing form structure
        """
        print("\n" + "="*70)
        print(f"📄 Reading Google Docs: {doc_url}")
        print("🤖 Generating form structure using Gemini AI...")
        print("="*70)
        
        # Read content from Google Docs
        try:
            content = self.form_generator.read_google_doc(doc_url)
            print(f"✅ Successfully read Google Docs content ({len(content)} characters)")
        except Exception as e:
            print(f"❌ Error reading Google Docs: {e}")
            raise
        
        # Generate form structure from content
        try:
            form_structure = self.gemini.generate_from_text(content)
            print("✅ Form structure generated successfully!")
        except Exception as e:
            print(f"❌ Error generating form structure: {e}")
            raise
        
        # Return structure for preview
        return form_structure
    
    def generate_form_structure_from_file(self, file_path: str) -> dict:
        """
        Create a Google Form from uploaded file using AI.
        
        Args:
            file_path: Path to the uploaded file
        
        Returns:
            URL of the created form
        """
        print("\n" + "="*70)
        print(f"📄 Reading file: {file_path}")
        print("🤖 Generating form structure using Gemini AI...")
        print("="*70)
        
        # Generate form structure from file
        try:
            form_structure = self.gemini.generate_from_file(file_path)
            print("✅ Form structure generated successfully!")
        except ImportError as e:
            print(f"\n❌ Error: Missing dependency")
            print(f"{e}")
            print("\n💡 Quick fix:")
            file_ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
            if file_ext in ['docx', 'doc']:
                print("  pip install python-docx")
            elif file_ext == 'pdf':
                print("  pip install PyPDF2")
            elif file_ext in ['xlsx', 'xls', 'csv']:
                print("  pip install pandas openpyxl")
            else:
                print("  pip install python-docx PyPDF2 pandas openpyxl")
            print("\nOr run: python install_dependencies.py")
            raise
        except Exception as e:
            print(f"❌ Error generating form structure: {e}")
            raise
        
        # Return structure for preview
        return form_structure
    
    def _create_form_from_structure(self, form_structure: dict) -> str:
        """
        Create a Google Form from the generated structure.
        
        Args:
            form_structure: Dictionary containing form structure
        
        Returns:
            URL of the created form
        """
        print("\n" + "="*70)
        print("📝 Creating Google Form...")
        print("="*70)
        
        # Extract form info
        title = form_structure.get('title', 'AI Generated Form')
        description = form_structure.get('description', '')
        questions = form_structure.get('questions', [])
        
        print(f"📋 Form Title: {title}")
        print(f"📝 Description: {description[:100]}..." if len(description) > 100 else f"📝 Description: {description}")
        print(f"❓ Number of questions: {len(questions)}")
        
        # Return form structure instead of creating immediately
        # This allows users to review and modify required settings
        return {
            'title': title,
            'description': description,
            'questions': questions
        }

    def create_form_from_structure(self, form_structure: dict) -> str:
        """
        Create a Google Form from a form structure (after preview/edit).
        
        Args:
            form_structure: Dictionary containing form structure with questions
        
        Returns:
            URL of the created form
        """
        print("\n" + "="*70)
        print("📝 Creating Google Form...")
        print("="*70)
        
        # Extract form info
        title = form_structure.get('title', 'AI Generated Form')
        description = form_structure.get('description', '')
        questions = form_structure.get('questions', [])
        
        print(f"📋 Form Title: {title}")
        print(f"📝 Description: {description[:100]}..." if len(description) > 100 else f"📝 Description: {description}")
        print(f"❓ Number of questions: {len(questions)}")
        
        # Create form
        form = self.form_generator.create_form(title, description)
        
        # Add questions
        print("\n➕ Adding questions...")
        for i, question in enumerate(questions, 1):
            try:
                question_text = question.get('text', '')
                question_type = question.get('type', 'text')
                required = question.get('required', False)
                
                print(f"  [{i}/{len(questions)}] {question_text[:50]}... ({question_type})")
                
                # Add question based on type
                if question_type in ['choice', 'checkbox', 'dropdown']:
                    options = question.get('options', [])
                    form.add_question(
                        question_text=question_text,
                        question_type=question_type,
                        required=required,
                        options=options
                    )
                elif question_type == 'scale':
                    form.add_question(
                        question_text=question_text,
                        question_type=question_type,
                        required=required,
                        scale_min=question.get('scale_min', 1),
                        scale_max=question.get('scale_max', 5),
                        scale_min_label=question.get('scale_min_label'),
                        scale_max_label=question.get('scale_max_label')
                    )
                else:
                    form.add_question(
                        question_text=question_text,
                        question_type=question_type,
                        required=required
                    )
                    
            except Exception as e:
                print(f"  ⚠️  Warning: Could not add question {i}: {e}")
                continue
        
        # Get form URL
        form_url = form.get_url()
        edit_url = form.get_edit_url()
        
        print("\n" + "="*70)
        print("✅ Form created successfully!")
        print("="*70)
        print(f"\n📝 View form: {form_url}")
        print(f"✏️  Edit form: {edit_url}")
        print("="*70 + "\n")
        
        return form_url


def main():
    """Main function for CLI interface."""
    print("\n" + "="*70)
    print("  🤖 AI-Powered Google Form Creator")
    print("  Using Google Gemini 2.5 Flash")
    print("="*70)
    
    # Gemini API Key
    GEMINI_API_KEY = "AIzaSyCzlgkxBgZ2gbF-WxHwE-v9Emw1JeHEYaY"
    
    # Initialize AI Form Creator
    creator = AIFormCreator(GEMINI_API_KEY)
    
    # Get user input method
    print("\nHow would you like to create your form?")
    print("1. Enter text description")
    print("2. Upload a file")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        # Text input
        print("\n" + "-"*70)
        print("Enter your form requirements or description:")
        print("(Press Enter twice or type 'END' on a new line to finish)")
        print("-"*70)
        
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
            if len(lines) >= 2 and lines[-1] == '' and lines[-2] == '':
                break
        
        text = '\n'.join(lines).strip()
        
        if not text:
            print("❌ No text provided. Exiting.")
            return
        
        try:
            form_url = creator.create_form_from_text(text)
            print(f"\n🎉 Your form is ready at: {form_url}")
        except Exception as e:
            print(f"\n❌ Error creating form: {e}")
            import traceback
            traceback.print_exc()
    
    elif choice == '2':
        # File upload
        file_path = input("\nEnter the path to your file: ").strip().strip('"').strip("'")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return
        
        try:
            form_url = creator.create_form_from_file(file_path)
            print(f"\n🎉 Your form is ready at: {form_url}")
        except Exception as e:
            print(f"\n❌ Error creating form: {e}")
            import traceback
            traceback.print_exc()
    
    elif choice == '3':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid choice. Please run again and select 1, 2, or 3.")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


"""
Gemini AI Integration for Google Forms Generation
Uses Google Gemini 2.5 Flash to generate form structure from user input
"""

import json
import re
from typing import Dict, List, Optional, Any
import google.generativeai as genai


class GeminiFormGenerator:
    """Generate Google Form structure using Gemini AI."""
    
    def __init__(self, api_key: str):
        """
        Initialize Gemini AI client.
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)
        # Try different model names - use the best available
        model_names = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        self.model = None
        for model_name in model_names:
            try:
                self.model = genai.GenerativeModel(model_name)
                break
            except Exception as e:
                continue
        
        if self.model is None:
            raise ValueError("Could not initialize any Gemini model. Please check your API key.")
        
        # System prompt for form generation
        self.system_prompt = """You are an expert at creating Google Forms. 
When given content (text, documents, requirements), analyze it and generate a comprehensive form structure.

Your response must be in JSON format with the following structure:
{
    "title": "Form Title",
    "description": "Form description",
    "questions": [
        {
            "text": "Question text",
            "type": "text|paragraph|choice|checkbox|dropdown|scale|date|time",
            "required": true/false,
            "options": ["option1", "option2"] (for choice/checkbox/dropdown),
            "scale_min": 1 (for scale type),
            "scale_max": 5 (for scale type),
            "scale_min_label": "Poor" (optional, for scale),
            "scale_max_label": "Excellent" (optional, for scale)
        }
    ]
}

Question types:
- "text": Short answer
- "paragraph": Long answer
- "choice": Multiple choice (single answer)
- "checkbox": Multiple choice (multiple answers)
- "dropdown": Dropdown menu
- "scale": Linear scale (1-5, 1-10, etc.)
- "date": Date picker
- "time": Time picker

Generate relevant questions based on the content provided. Make questions clear and actionable.

IMPORTANT: Set "required": true for essential questions (like name, email, contact info) and "required": false for optional questions (like comments, suggestions, additional info)."""

    def generate_from_text(self, text: str) -> Dict[str, Any]:
        """
        Generate form structure from text input.
        
        Args:
            text: User's text input describing the form or requirements
        
        Returns:
            Dictionary containing form structure (title, description, questions)
        """
        prompt = f"""{self.system_prompt}

User Requirements:
{text}

Generate a Google Form structure based on the above requirements. Return ONLY valid JSON, no additional text or explanation."""
        
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean the response - remove markdown code blocks if present
            response_text = self._clean_json_response(response_text)
            
            # Parse JSON
            form_structure = json.loads(response_text)
            return form_structure
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing Gemini response: {e}")
            print(f"Response preview: {response_text[:500]}")
            print("\nTrying to extract JSON from response...")
            
            # Try to fix common JSON issues
            try:
                # Remove markdown if present
                cleaned = self._clean_json_response(response_text)
                form_structure = json.loads(cleaned)
                return form_structure
            except:
                raise ValueError(
                    f"Failed to parse form structure from AI response.\n"
                    f"Error: {e}\n"
                    f"Response: {response_text[:1000]}"
                )
        except Exception as e:
            print(f"Error generating form: {e}")
            raise
    
    def generate_from_file(self, file_path: str, file_type: str = None) -> Dict[str, Any]:
        """
        Generate form structure from uploaded file.
        
        Args:
            file_path: Path to the uploaded file
            file_type: File type (txt, pdf, docx, etc.) - auto-detected if None
        
        Returns:
            Dictionary containing form structure
        """
        # Read file content
        content = self._read_file(file_path, file_type)
        
        # Generate form from content
        return self.generate_from_text(content)
    
    def _read_file(self, file_path: str, file_type: str = None) -> str:
        """
        Read file content based on file type.
        
        Args:
            file_path: Path to file
            file_type: File type extension
        
        Returns:
            File content as string
        """
        if not file_type:
            file_type = file_path.split('.')[-1].lower()
        
        try:
            if file_type == 'txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_type == 'pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        text = ""
                        for page in reader.pages:
                            text += page.extract_text() + "\n"
                        return text
                except ImportError:
                    print("\n" + "="*70)
                    print("❌ Missing dependency: PyPDF2")
                    print("="*70)
                    print("To read PDF files, please install:")
                    print("  pip install PyPDF2")
                    print("\nOr install all optional dependencies:")
                    print("  pip install python-docx PyPDF2 pandas openpyxl")
                    print("="*70 + "\n")
                    raise ImportError(
                        "PyPDF2 required for PDF files.\n"
                        "Install with: pip install PyPDF2"
                    )
            
            elif file_type in ['docx', 'doc']:
                try:
                    from docx import Document
                    doc = Document(file_path)
                    text = "\n".join([para.text for para in doc.paragraphs])
                    return text
                except ImportError:
                    print("\n" + "="*70)
                    print("❌ Missing dependency: python-docx")
                    print("="*70)
                    print("To read Word documents (.docx, .doc), please install:")
                    print("  pip install python-docx")
                    print("\nOr install all optional dependencies:")
                    print("  pip install python-docx PyPDF2 pandas openpyxl")
                    print("="*70 + "\n")
                    raise ImportError(
                        "python-docx required for Word files.\n"
                        "Install with: pip install python-docx"
                    )
            
            elif file_type in ['csv', 'xlsx', 'xls']:
                try:
                    import pandas as pd
                    df = pd.read_excel(file_path) if file_type in ['xlsx', 'xls'] else pd.read_csv(file_path)
                    return df.to_string()
                except ImportError:
                    print("\n" + "="*70)
                    print("❌ Missing dependency: pandas and/or openpyxl")
                    print("="*70)
                    print("To read Excel/CSV files, please install:")
                    print("  pip install pandas openpyxl")
                    print("\nOr install all optional dependencies:")
                    print("  pip install python-docx PyPDF2 pandas openpyxl")
                    print("="*70 + "\n")
                    raise ImportError(
                        "pandas and openpyxl required for Excel/CSV files.\n"
                        "Install with: pip install pandas openpyxl"
                    )
            
            else:
                # Try to read as text
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except Exception as e:
            raise Exception(f"Error reading file: {e}")
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean JSON response from Gemini (remove markdown, code blocks, etc.).
        
        Args:
            response: Raw response from Gemini
        
        Returns:
            Cleaned JSON string
        """
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Find JSON object in response
        # Try to extract JSON between { and }
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        # Remove leading/trailing whitespace
        response = response.strip()
        
        return response
    
    def generate_from_file_content(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Generate form structure from uploaded file content (for web/file uploads).
        
        Args:
            file_content: File content as bytes
            filename: Original filename
        
        Returns:
            Dictionary containing form structure
        """
        import tempfile
        import os
        
        # Determine file type
        file_type = filename.split('.')[-1].lower() if '.' in filename else 'txt'
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # Generate form
            form_structure = self.generate_from_file(tmp_path, file_type)
            return form_structure
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


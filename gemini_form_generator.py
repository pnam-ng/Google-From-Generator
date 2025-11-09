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
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini AI client.
        
        Args:
            api_key: Google Gemini API key (optional, will check environment variables if not provided)
        """
        # Check for API key in multiple environment variables
        if not api_key:
            import os
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        
        # Strip whitespace to avoid issues
        if api_key:
            api_key = api_key.strip()
        
        if not api_key:
            raise ValueError(
                "No API key found. Please set GEMINI_API_KEY or GOOGLE_API_KEY environment variable. "
                "Get your key from: https://aistudio.google.com/app/apikey"
            )
        
        self.api_key = api_key
        genai.configure(api_key=api_key)
        
        # PRIMARY MODEL: gemini-2.5-flash is the main and preferred model
        # Fallback models are only used if the primary model is unavailable
        primary_model = 'gemini-2.5-flash'
        fallback_models = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        
        self.model = None
        last_error = None
        
        # Try primary model first
        try:
            self.model = genai.GenerativeModel(primary_model)
            print(f"✅ Using PRIMARY Gemini model: {primary_model}")
        except Exception as e:
            last_error = str(e)
            print(f"⚠️  Primary model {primary_model} unavailable: {last_error}")
            print(f"🔄 Trying fallback models...")
            
            # Try fallback models only if primary fails
            for model_name in fallback_models:
                try:
                    self.model = genai.GenerativeModel(model_name)
                    print(f"✅ Using FALLBACK Gemini model: {model_name}")
                    break
                except Exception as e:
                    last_error = str(e)
                    print(f"⚠️  Could not use {model_name}: {last_error}")
                    continue
        
        if self.model is None:
            error_msg = f"Could not initialize Gemini model. "
            error_msg += f"Primary model ({primary_model}) and all fallback models failed. "
            if last_error:
                error_msg += f"Last error: {last_error}. "
            error_msg += "Please check your API key is valid and has access to Gemini API."
            raise ValueError(error_msg)
        
        # System prompt for form generation
        self.system_prompt = """You are an expert at creating Google Forms for English reading and listening exams. 
When given content (text, documents, exam papers), analyze it and generate a comprehensive exam form structure that matches standard IELTS/TOEFL format.

Your response must be in JSON format with the following structure:
{
    "title": "Form Title",
    "description": "Form description",
    "sections": [
        {
            "title": "Section title (e.g., 'READING PASSAGE 1')",
            "description": "Section description (e.g., reading passage text, instructions)",
            "question_groups": [
                {
                    "title": "Question group title (e.g., 'Questions 1–5')",
                    "description": "Optional group description/instructions",
                    "questions": [
                        {
                            "text": "Question text",
                            "type": "choice" or "text",
                            "required": true,
                            "options": ["option A", "option B", "option C", "option D"] (for choice type) or [] (for text type)
                        }
                    ]
                }
            ]
        }
    ]
}

IMPORTANT STRUCTURE NOTES:
- ALWAYS use "sections" array (even if document has no clear sections, create one section)
- Each section can have a title (e.g., "READING PASSAGE 1") and description (the actual reading passage text)
- Use "question_groups" to group related questions (e.g., "Questions 1–5", "Questions 6-9")
- Questions within groups should be in the "questions" array
- If document has no clear sections, create one section titled "Section 1" with all questions in one group
- For backward compatibility, you can also include a flat "questions" array at the root level, but "sections" is preferred

Question types:
- "choice": Multiple choice question with options (A, B, C, D)
- "text": Fill-in-the-blank or short answer question where user types the answer (has blanks like ……………………… or ______)

PRIMARY USE CASE:
This application is designed to help create Google Forms for English exams from documents.
- Questions can be either multiple choice (type "choice") or fill-in-the-blank (type "text")
- All questions should be marked as "required": true
- Multiple choice questions should have options (typically 3-4 options: A, B, C, D or A, B, C)
- Fill-in-the-blank questions should use type "text" and have NO options

CRITICAL REQUIREMENTS:
1. You MUST extract ALL questions from the document. If the document says it has 40 questions, you MUST create exactly 40 questions.
2. Count the questions as you extract them to ensure completeness.
3. Do NOT skip any questions, even if they appear in different sections or formats.
4. Verify the total number of questions matches what the document indicates.

QUESTION TYPE DETECTION:
You must identify TWO types of questions:

TYPE 1: MULTIPLE CHOICE QUESTIONS (type: "choice")
- These questions have multiple options labeled A, B, C, D (or a, b, c, d, or 1, 2, 3, 4)
- Example: "11 Before Queen Elizabeth I visited the castle in 1576, A repairs were carried out... B a new building was constructed... C a fire damaged..."
- For these: Use type "choice" and include all options in the "options" array

TYPE 2: FILL-IN-THE-BLANK QUESTIONS (type: "text")
- These questions have blanks represented by dots (………………………), underscores (______), or spaces
- They do NOT have multiple choice options (A, B, C, D)
- Example: "was born in Scotland in 1831 – father was a 9 …………………………"
- Example: "people bought Henderson's photos because photography took up considerable time and the 10 ……………………… was heavy"
- For these: Use type "text" and set "options" to an empty array [] or omit it
- The question text should include the blank (keep the dots/underscores as part of the question text)

QUESTION DETECTION RULES:
When analyzing the input content to identify exam questions, follow these rules STRICTLY:
1. Identify questions by the fact that the beginning of the question will have an ordinal number:
   - Multiple choice: "1. Question ...", "2. Question ...", "11 Question ..." (number followed by period or space)
   - Fill-in-the-blank: "9 ………………………", "10 ………………………" (number followed by dots/blank)
   - Paragraph matching: "1. A natural phenomenon..." (questions asking which paragraph contains information)
2. If the question after the number is 1 line, the question will be the whole line.
3. A question number can appear in these formats:
   - With period: "1.", "2.", "11."
   - With space: "11 ", "12 " (followed by question text)
   - With dots/blank: "9 ………………………", "10 ………………………" (fill-in-the-blank format)
   - Bold formatting: "**1.**" or "**1.**" (common in formatted documents)
4. Questions may be numbered sequentially (1, 2, 3...) or in ranges (1-10, 11-15, 16-20, etc.). Extract ALL of them.
5. For multiple choice questions: After each question, identify the multiple choice options (typically labeled as A, B, C, D or a, b, c, d, or 1, 2, 3, 4)
6. For fill-in-the-blank questions: The question text contains blanks (……………………… or ______) and has NO options. The number may appear before or within the question text with the blank.
7. For paragraph matching questions: Questions asking "Which paragraph contains..." should be type "text" (short answer) where students type the paragraph letter (A, B, C, D, E, F)
8. Extract the question text and all its corresponding options (if any) as a single question entry
9. Some questions may span multiple lines - capture the complete question text including any preceding context
10. For fill-in-the-blank questions like "was born in Scotland in 1831 – father was a 9 …………………………", include the full sentence with the number and blank in the question text
11. Questions that ask to match statements to paragraphs or people should be type "text" (short answer) where students type the answer

QUESTION FORMAT HANDLING:
- Question text should include the full question statement (may span multiple lines)
- For multiple choice: Options should be extracted from the document (typically 3-4 options per question)
- For multiple choice: Remove the option labels (A, B, C, D) from the option text when creating the options array
- For fill-in-the-blank: Keep the blank markers (……………………… or ______) in the question text
- For fill-in-the-blank: Do NOT include any options array, or set it to empty []
- Each multiple choice question must have at least 2 options, typically 3-4 options for English exams

SECTION AND READING PASSAGE HANDLING:
- Documents may be divided into sections with reading passages (e.g., "READING PASSAGE 1", "READING PASSAGE 2", "READING PASSAGE 3")
- Each reading passage should be a separate section with:
  - Section title: The passage identifier (e.g., "READING PASSAGE 1")
  - Section description: The full reading passage text (paragraphs A, B, C, D, E, F, etc.)
- Questions related to each passage should be grouped within that section's question_groups
- Question groups should be titled with question ranges (e.g., "Questions 1–5", "Questions 6-9", "Questions 10-13")
- Extract questions from ALL sections and passages
- Do not stop after one section - continue through all sections until all questions are extracted
- If questions reference paragraphs (e.g., "Which paragraph contains..."), include the full question text with paragraph references

QUESTION GROUPING:
- Group questions logically by their question number ranges
- Use descriptive group titles like "Questions 1–5", "Questions 6-9", etc.
- If instructions specify a grouping (e.g., "Questions 1–5" with specific instructions), create a separate question group
- Each question group can have an optional description for instructions (e.g., "Reading Passage 1 has 5 paragraphs, A – E. Which paragraph contains...")

VALIDATION:
Before finalizing your response:
1. Count the total number of questions extracted across all sections
2. Verify it matches the expected count (e.g., if document mentions 40 questions, ensure you have 40)
3. For multiple choice questions: Ensure each has at least 2 options
4. For fill-in-the-blank questions: Ensure they have type "text" and no options (or empty options array)
5. For paragraph matching questions: Ensure they have type "text" (students type paragraph letters)
6. Check that question numbers are sequential and complete
7. Verify question types are correctly assigned (choice for questions with options, text for questions with blanks or paragraph matching)
8. Ensure reading passages are included as section descriptions
9. Verify question groups are properly organized by question ranges

FORM STRUCTURE BEST PRACTICES:
- Create sections for each major reading passage or listening section
- Include full reading passage text in section descriptions
- Group questions logically by their number ranges
- Use clear section titles (e.g., "READING PASSAGE 1", "READING PASSAGE 2")
- Maintain question numbering sequence across all sections

Generate the exam form structure based on the content provided. Extract ALL questions, organize them into proper sections with reading passages, and group them logically. Do not miss any questions."""

    def generate_from_text(self, text: str) -> Dict[str, Any]:
        """
        Generate form structure from text input.
        
        Args:
            text: User's text input describing the form or requirements
        
        Returns:
            Dictionary containing form structure (title, description, questions)
        """
        prompt = f"""{self.system_prompt}

EXAM DOCUMENT CONTENT:
{text}

CRITICAL INSTRUCTIONS:
1. Analyze the entire document carefully
2. Extract ALL questions from all sections
3. If the document mentions a specific number of questions (e.g., 40 questions), ensure you extract exactly that many
4. Count your questions before responding to verify completeness
5. Identify question types correctly:
   - Questions with options (A, B, C, D) → type "choice" with options array
   - Questions with blanks (……………………… or ______) and NO options → type "text" with empty options array []
6. For fill-in-the-blank questions (type "text"), keep the blank markers in the question text
7. For multiple choice questions (type "choice"), extract all options and remove labels (A, B, C, D)

Generate a Google Form structure based on the exam document above. Return ONLY valid JSON, no additional text or explanation. Ensure ALL questions are included with correct types."""
        
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
            print("\nTrying to fix JSON issues...")
            
            # Try to fix common JSON issues
            try:
                # Remove markdown if present
                cleaned = self._clean_json_response(response_text)
                
                # Always try to fix control characters if JSON parsing fails
                # (control characters are a common issue with Gemini responses)
                print("Attempting to fix control characters in JSON strings...")
                cleaned = self._fix_json_control_characters(cleaned)
                
                form_structure = json.loads(cleaned)
                print("✅ Successfully fixed and parsed JSON!")
                return form_structure
            except json.JSONDecodeError as e2:
                print(f"Still failing after control character fix: {e2}")
                # Try one more time with more aggressive cleaning
                try:
                    # Remove any remaining problematic characters
                    # This is a last resort - might not always work
                    cleaned = cleaned.replace('\x00', '')  # Remove null bytes
                    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', cleaned)  # Remove other control chars outside strings
                    
                    form_structure = json.loads(cleaned)
                    print("✅ Successfully parsed after aggressive cleaning!")
                    return form_structure
                except Exception as e3:
                    raise ValueError(
                        f"Failed to parse form structure from AI response.\n"
                        f"Original error: {e}\n"
                        f"Control character fix error: {e2}\n"
                        f"Aggressive fix error: {e3}\n"
                        f"Response preview: {response_text[:1000]}"
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
    
    def _fix_json_control_characters(self, json_str: str) -> str:
        """
        Fix control characters in JSON string values by properly escaping them.
        
        This function walks through the JSON string and escapes control characters
        only within string values (between quotes), preserving the JSON structure.
        
        Args:
            json_str: JSON string that may contain unescaped control characters
        
        Returns:
            JSON string with control characters properly escaped
        """
        result = []
        i = 0
        in_string = False
        escape_next = False
        
        while i < len(json_str):
            char = json_str[i]
            
            if escape_next:
                # Next character is escaped, so copy it as-is
                result.append(char)
                escape_next = False
                i += 1
                continue
            
            if char == '\\':
                # Escape character - next char should be preserved
                result.append(char)
                escape_next = True
                i += 1
                continue
            
            if char == '"':
                # Check if this quote is escaped (odd number of backslashes before it)
                backslash_count = 0
                j = i - 1
                while j >= 0 and json_str[j] == '\\':
                    backslash_count += 1
                    j -= 1
                
                if backslash_count % 2 == 0:
                    # Not escaped, so it's a real quote - toggle string state
                    in_string = not in_string
                
                result.append(char)
                i += 1
                continue
            
            if in_string:
                # We're inside a string, escape control characters
                if ord(char) < 32:  # Control character (0x00-0x1F)
                    if char == '\n':
                        result.append('\\n')
                    elif char == '\r':
                        result.append('\\r')
                    elif char == '\t':
                        result.append('\\t')
                    elif char == '\b':
                        result.append('\\b')
                    elif char == '\f':
                        result.append('\\f')
                    else:
                        # Other control characters
                        result.append(f'\\u{ord(char):04x}')
                else:
                    result.append(char)
            else:
                # Outside string, copy as-is
                result.append(char)
            
            i += 1
        
        return ''.join(result)
    
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


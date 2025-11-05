"""
Google Forms Generator - Automated Google Forms creation using Google Forms API
Cross-platform compatible (Windows, macOS, Linux)
"""

import os
import pickle
from typing import List, Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleFormGenerator:
    """Main class for creating and managing Google Forms using Google Forms API."""
    
    # Scopes required for Google Forms API
    SCOPES = [
        'https://www.googleapis.com/auth/forms.body',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive',  # Needed to set permissions
        'https://www.googleapis.com/auth/documents.readonly'  # For reading Google Docs
    ]
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize the Google Form Generator.
        
        Args:
            credentials_file: Path to OAuth 2.0 credentials JSON file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.drive_service = None
        self.docs_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google APIs using OAuth 2.0."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # Check if scopes are sufficient (new scope added for permissions)
        if creds and creds.valid:
            token_scopes = creds.scopes if hasattr(creds, 'scopes') else []
            required_scope = 'https://www.googleapis.com/auth/drive'
            if required_scope not in token_scopes:
                # Token doesn't have the new scope, need to re-authenticate
                print("\n⚠️  New permissions required. Please re-authenticate.")
                print("   Deleting old token and requesting new authentication...\n")
                if os.path.exists(self.token_file):
                    os.remove(self.token_file)
                creds = None
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    # If refresh fails, re-authenticate
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"Credentials file '{self.credentials_file}' not found. "
                        "Please download it from Google Cloud Console and place it in the project root."
                    )
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    error_msg = str(e).lower()
                    if 'access_denied' in error_msg or '403' in error_msg:
                        raise PermissionError(
                            "\n" + "="*70 + "\n"
                            "❌ LỖI XÁC THỰC (Authentication Error)\n"
                            "="*70 + "\n"
                            "Ứng dụng của bạn đang ở chế độ kiểm thử.\n"
                            "Bạn cần thêm email của mình vào danh sách người dùng thử nghiệm.\n\n"
                            "CÁCH KHẮC PHỤC (How to Fix):\n"
                            "1. Truy cập Google Cloud Console:\n"
                            "   https://console.cloud.google.com/\n"
                            "2. Chọn dự án của bạn\n"
                            "3. Vào 'APIs & Services' > 'OAuth consent screen'\n"
                            "4. Cuộn xuống phần 'Test users'\n"
                            "5. Click 'ADD USERS'\n"
                            "6. Thêm email Google của bạn (email bạn đăng nhập)\n"
                            "7. Click 'SAVE'\n"
                            "8. Chạy lại script này\n\n"
                            "="*70 + "\n"
                            "❌ AUTHENTICATION ERROR\n"
                            "="*70 + "\n"
                            "Your app is in testing mode.\n"
                            "You need to add your email to the test users list.\n\n"
                            "HOW TO FIX:\n"
                            "1. Go to Google Cloud Console:\n"
                            "   https://console.cloud.google.com/\n"
                            "2. Select your project\n"
                            "3. Go to 'APIs & Services' > 'OAuth consent screen'\n"
                            "4. Scroll to 'Test users' section\n"
                            "5. Click 'ADD USERS'\n"
                            "6. Add your Google email (the one you use to sign in)\n"
                            "7. Click 'SAVE'\n"
                            "8. Run this script again\n"
                            "="*70 + "\n"
                        ) from e
                    else:
                        raise
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        # Build services
        self.service = build('forms', 'v1', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.docs_service = build('docs', 'v1', credentials=creds)
    
    def create_form(self, title: str, description: str = None) -> 'Form':
        """
        Create a new Google Form.
        
        Args:
            title: Form title
            description: Form description (optional)
        
        Returns:
            Form object for adding questions
        """
        # Create form in Google Drive
        form_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.form'
        }
        
        try:
            form = self.drive_service.files().create(
                body=form_metadata
            ).execute()
            
            form_id = form.get('id')
            
            if not form_id:
                raise ValueError("Failed to create form: No form ID returned")
            
            # Set permissions to make form accessible
            # Allow anyone with the link to view the form
            self._set_form_permissions(form_id)
            
            # Update form with description if provided
            # (Title is already set via Drive API, but we update it via Forms API for consistency)
            if description:
                self.update_form_info(form_id, title, description)
            
            return Form(self.service, form_id, title, description)
            
        except HttpError as error:
            error_content = str(error.content).lower() if error.content else ""
            
            # Check if Drive API is not enabled
            if 'drive' in error_content and ('not been used' in error_content or 'disabled' in error_content or 'not enabled' in error_content):
                raise PermissionError(
                    "\n" + "="*70 + "\n"
                    "❌ GOOGLE DRIVE API CHƯA ĐƯỢC BẬT (Google Drive API Not Enabled)\n"
                    "="*70 + "\n"
                    "Google Forms API cần Google Drive API để tạo form.\n"
                    "Bạn cần bật Google Drive API trong Google Cloud Console.\n\n"
                    "CÁCH KHẮC PHỤC (How to Fix):\n"
                    "1. Truy cập Google Cloud Console:\n"
                    "   https://console.cloud.google.com/\n"
                    "2. Chọn dự án của bạn\n"
                    "3. Vào 'APIs & Services' > 'Library'\n"
                    "4. Tìm 'Google Drive API'\n"
                    "5. Click 'Enable' để bật API\n"
                    "6. Đợi vài phút để API được kích hoạt\n"
                    "7. Chạy lại script này\n\n"
                    "="*70 + "\n"
                    "❌ GOOGLE DRIVE API NOT ENABLED\n"
                    "="*70 + "\n"
                    "Google Forms API requires Google Drive API to create forms.\n"
                    "You need to enable Google Drive API in Google Cloud Console.\n\n"
                    "HOW TO FIX:\n"
                    "1. Go to Google Cloud Console:\n"
                    "   https://console.cloud.google.com/\n"
                    "2. Select your project\n"
                    "3. Go to 'APIs & Services' > 'Library'\n"
                    "4. Search for 'Google Drive API'\n"
                    "5. Click 'Enable' to enable the API\n"
                    "6. Wait a few minutes for the API to activate\n"
                    "7. Run this script again\n"
                    "="*70 + "\n"
                ) from error
            else:
                print(f"An error occurred while creating form: {error}")
                raise
        except Exception as e:
            print(f"Unexpected error while creating form: {e}")
            raise
    
    def _set_form_permissions(self, form_id: str):
        """
        Set permissions for the form to make it accessible.
        Allows anyone with the link to view the form.
        
        Args:
            form_id: Google Form ID
        """
        try:
            # Set permission to allow anyone with the link to view
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.drive_service.permissions().create(
                fileId=form_id,
                body=permission
            ).execute()
            
        except HttpError as error:
            # If permission already exists or other error, log but don't fail
            # (form might already be accessible)
            error_str = str(error).lower()
            if 'permission denied' not in error_str and 'already exists' not in error_str:
                print(f"Warning: Could not set form permissions: {error}")
                print("You may need to manually set permissions in Google Drive")
    
    def update_form_info(self, form_id: str, title: str, description: str = None):
        """Update form title and description."""
        update_request = {
            'requests': [
                {
                    'updateFormInfo': {
                        'info': {
                            'title': title
                        },
                        'updateMask': 'title'
                    }
                }
            ]
        }
        
        if description:
            update_request['requests'][0]['updateFormInfo']['info']['description'] = description
            update_request['requests'][0]['updateFormInfo']['updateMask'] = 'title,description'
        
        try:
            self.service.forms().batchUpdate(formId=form_id, body=update_request).execute()
        except HttpError as error:
            print(f"An error occurred while updating form info: {error}")
            raise
    
    def get_form(self, form_id: str) -> Dict[str, Any]:
        """
        Retrieve an existing form.
        
        Args:
            form_id: Google Form ID
        
        Returns:
            Form data as dictionary
        """
        try:
            form = self.service.forms().get(formId=form_id).execute()
            return form
        except HttpError as error:
            print(f"An error occurred while retrieving form: {error}")
            raise
    
    def get_form_url(self, form_id: str) -> str:
        """
        Get the URL of a form.
        
        Args:
            form_id: Google Form ID
        
        Returns:
            Form URL
        """
        return f"https://docs.google.com/forms/d/{form_id}/viewform"
    
    def extract_doc_id_from_url(self, url: str) -> str:
        """
        Extract document ID from Google Docs URL.
        
        Args:
            url: Google Docs URL (various formats supported)
        
        Returns:
            Document ID
        """
        import re
        
        # Patterns for different Google Docs URL formats
        patterns = [
            r'/document/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'docs\.google\.com/document/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If no pattern matches, assume it's already a document ID
        if re.match(r'^[a-zA-Z0-9-_]+$', url):
            return url
        
        raise ValueError(f"Could not extract document ID from URL: {url}")
    
    def read_google_doc(self, doc_url: str) -> str:
        """
        Read content from a Google Docs document.
        
        Args:
            doc_url: Google Docs URL or document ID
        
        Returns:
            Document content as plain text
        """
        try:
            # Extract document ID if URL is provided
            if '/' in doc_url or 'docs.google.com' in doc_url:
                doc_id = self.extract_doc_id_from_url(doc_url)
            else:
                doc_id = doc_url
            
            # Get document content
            doc = self.docs_service.documents().get(documentId=doc_id).execute()
            
            # Extract text from document
            content = []
            if 'body' in doc and 'content' in doc['body']:
                for element in doc['body']['content']:
                    if 'paragraph' in element:
                        para = element['paragraph']
                        if 'elements' in para:
                            for elem in para['elements']:
                                if 'textRun' in elem:
                                    content.append(elem['textRun'].get('content', ''))
            
            text_content = ''.join(content).strip()
            
            if not text_content:
                raise ValueError("Document appears to be empty or could not be read")
            
            return text_content
            
        except HttpError as error:
            error_content = str(error.content).lower() if error.content else ""
            if 'permission denied' in error_content or 'not found' in error_content:
                raise PermissionError(
                    f"Could not access Google Docs document. "
                    f"Please ensure:\n"
                    f"1. The document exists and you have access to it\n"
                    f"2. The document is shared with your Google account\n"
                    f"3. Google Docs API is enabled in your Google Cloud project"
                ) from error
            else:
                raise Exception(f"Error reading Google Docs: {error}") from error
        except Exception as e:
            raise Exception(f"Error reading Google Docs: {str(e)}") from e
    
    def save_form(self, form: 'Form') -> str:
        """
        Finalize and save a form, returning its URL.
        
        Args:
            form: Form object to save
        
        Returns:
            Form URL
        """
        return form.get_url()


class Form:
    """Represents a Google Form with methods to add questions."""
    
    def __init__(self, service, form_id: str, title: str, description: str = None):
        """
        Initialize a Form object.
        
        Args:
            service: Google Forms API service object
            form_id: Google Form ID
            title: Form title
            description: Form description
        """
        self.service = service
        self.form_id = form_id
        self.title = title
        self.description = description
        self.questions = []
    
    def add_question(
        self,
        question_text: str,
        question_type: str = 'text',
        required: bool = False,
        options: List[str] = None,
        scale_min: int = 1,
        scale_max: int = 5,
        scale_min_label: str = None,
        scale_max_label: str = None
    ) -> Dict[str, Any]:
        """
        Add a question to the form.
        
        Args:
            question_text: The question text
            question_type: Type of question (text, paragraph, choice, checkbox, dropdown, scale, date, time, file)
            required: Whether the question is required
            options: List of options for choice/checkbox/dropdown questions
            scale_min: Minimum value for scale questions
            scale_max: Maximum value for scale questions
            scale_min_label: Label for minimum scale value
            scale_max_label: Label for maximum scale value
        
        Returns:
            Created question data
        """
        # Map question types to Google Forms API question types
        type_mapping = {
            'text': 'SHORT_ANSWER',
            'paragraph': 'PARAGRAPH_TEXT',
            'choice': 'RADIO',
            'checkbox': 'CHECKBOX',
            'dropdown': 'DROP_DOWN',
            'scale': 'SCALE',
            'date': 'DATE',
            'time': 'TIME',
            'file': 'FILE_UPLOAD'
        }
        
        if question_type not in type_mapping:
            raise ValueError(
                f"Invalid question type: {question_type}. "
                f"Valid types: {', '.join(type_mapping.keys())}"
            )
        
        google_type = type_mapping[question_type]
        
        # Build question request
        question_request = {
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'choiceQuestion': None,
                            'textQuestion': None,
                            'scaleQuestion': None,
                            'dateQuestion': None,
                            'timeQuestion': None,
                            'fileUploadQuestion': None
                        }
                    }
                },
                'location': {
                    'index': len(self.questions)
                }
            }
        }
        
        # Configure question based on type
        if question_type in ['text', 'paragraph']:
            question_request['createItem']['item']['questionItem']['question']['textQuestion'] = {}
        
        elif question_type in ['choice', 'checkbox', 'dropdown']:
            if not options:
                raise ValueError(f"Options are required for {question_type} questions")
            
            choice_question = {
                'type': 'RADIO' if question_type == 'choice' else ('CHECKBOX' if question_type == 'checkbox' else 'DROP_DOWN'),
                'options': [{'value': option} for option in options]
            }
            
            question_request['createItem']['item']['questionItem']['question']['choiceQuestion'] = choice_question
        
        elif question_type == 'scale':
            scale_question = {
                'low': scale_min,
                'high': scale_max
            }
            if scale_min_label:
                scale_question['lowLabel'] = scale_min_label
            if scale_max_label:
                scale_question['highLabel'] = scale_max_label
            
            question_request['createItem']['item']['questionItem']['question']['scaleQuestion'] = scale_question
        
        elif question_type == 'date':
            question_request['createItem']['item']['questionItem']['question']['dateQuestion'] = {
                'includeTime': False,
                'includeYear': True
            }
        
        elif question_type == 'time':
            question_request['createItem']['item']['questionItem']['question']['timeQuestion'] = {}
        
        elif question_type == 'file':
            question_request['createItem']['item']['questionItem']['question']['fileUploadQuestion'] = {
                'maxFileSize': '10MB',
                'maxFiles': 1
            }
        
        # Submit the question
        try:
            batch_update_request = {'requests': [question_request]}
            response = self.service.forms().batchUpdate(
                formId=self.form_id,
                body=batch_update_request
            ).execute()
            
            # Store question info
            question_data = {
                'text': question_text,
                'type': question_type,
                'required': required
            }
            self.questions.append(question_data)
            
            return response
            
        except HttpError as error:
            print(f"An error occurred while adding question: {error}")
            raise
    
    def get_url(self) -> str:
        """Get the URL of this form."""
        return f"https://docs.google.com/forms/d/{self.form_id}/viewform"
    
    def get_edit_url(self) -> str:
        """Get the edit URL of this form."""
        return f"https://docs.google.com/forms/d/{self.form_id}/edit"


# Example usage
if __name__ == '__main__':
    # Initialize the generator
    generator = GoogleFormGenerator()
    
    # Create a new form
    form = generator.create_form(
        title="Sample Survey Form",
        description="This is a sample survey created using Google Forms API"
    )
    
    # Add questions
    form.add_question(
        question_text="What is your name?",
        question_type="text",
        required=True
    )
    
    form.add_question(
        question_text="How would you rate our service?",
        question_type="scale",
        scale_min=1,
        scale_max=5,
        scale_min_label="Poor",
        scale_max_label="Excellent"
    )
    
    form.add_question(
        question_text="Select your favorite color",
        question_type="choice",
        options=["Red", "Blue", "Green", "Yellow"]
    )
    
    # Get the form URL
    form_url = form.get_url()
    print(f"Form created successfully!")
    print(f"View form: {form_url}")
    print(f"Edit form: {form.get_edit_url()}")


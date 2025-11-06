"""
Flask Web Application for AI-Powered Google Form Creator
Cross-platform web UI for non-technical users
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory, session, redirect, url_for
from werkzeug.utils import secure_filename
import traceback
import io
from contextlib import redirect_stdout
from datetime import datetime
from ai_form_creator import AIFormCreator

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, skip loading .env file
    pass

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', os.urandom(32).hex())

# Allow insecure transport (HTTP) in development only
# IMPORTANT: This should NEVER be set in production!
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
if FLASK_ENV == 'development' or DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    print("⚠️  Development mode: OAuth insecure transport enabled (HTTP allowed)")
    print("   ⚠️  WARNING: This should NEVER be enabled in production!")

# Security headers
@app.after_request
def set_security_headers(response):
    """Set security headers for production."""
    if os.getenv('FLASK_ENV') == 'production':
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        # Only set strict transport if using HTTPS
        # response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc', 'csv', 'xlsx', 'xls'}

# Gemini API Key - Load from environment variable (support both names)
# Strip whitespace to avoid issues with copy-paste
GEMINI_API_KEY = (os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY', '')).strip()

# Log API key status at startup (for debugging)
if GEMINI_API_KEY:
    api_key_preview = GEMINI_API_KEY[:10] + "..." if len(GEMINI_API_KEY) > 10 else "***"
    print(f"🔑 GEMINI_API_KEY loaded: {api_key_preview} (length: {len(GEMINI_API_KEY)})")
    # Validate API key format (should start with "AIza")
    if not GEMINI_API_KEY.startswith('AIza'):
        print("⚠️  Warning: API key doesn't start with 'AIza' - may be invalid")
else:
    print("⚠️  GEMINI_API_KEY not found in environment variables")

# Initialize AI Form Creator
ai_creator = None

class LogCapture:
    """Capture logs during form creation."""
    def __init__(self):
        self.logs = []
        self.buffer = io.StringIO()
    
    def write(self, message):
        """Capture print statements."""
        if message.strip():
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.logs.append({
                'timestamp': timestamp,
                'message': message.strip(),
                'type': self._determine_type(message)
            })
            self.buffer.write(message)
    
    def flush(self):
        """Flush buffer."""
        self.buffer.flush()
    
    def _determine_type(self, message):
        """Determine log type from message."""
        msg_lower = message.lower()
        if 'error' in msg_lower or '❌' in message or 'failed' in msg_lower:
            return 'error'
        elif 'success' in msg_lower or '✅' in message or 'created' in msg_lower:
            return 'success'
        elif 'warning' in msg_lower or '⚠️' in message:
            return 'warning'
        else:
            return 'info'
    
    def get_logs(self):
        """Get all captured logs."""
        return self.logs

def init_ai_creator():
    """Initialize AI Form Creator."""
    global ai_creator
    if ai_creator is None:
        # Check if API key is provided
        if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
            print("❌ Error: GEMINI_API_KEY or GOOGLE_API_KEY environment variable is not set or is empty")
            print("   Please set GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable before running the app")
            print("   Get your key from: https://aistudio.google.com/app/apikey")
            return False
        
        # Log API key status (first few characters only for security)
        api_key_preview = GEMINI_API_KEY[:10] + "..." if len(GEMINI_API_KEY) > 10 else "***"
        print(f"🔑 Attempting to initialize AI Creator with API key: {api_key_preview}")
        
        try:
            # Pass the API key directly
            ai_creator = AIFormCreator(GEMINI_API_KEY)
            print("✅ AI Creator initialized successfully")
            return True
        except ValueError as e:
            error_msg = str(e)
            print(f"❌ Error initializing AI Creator (ValueError): {error_msg}")
            if "API key" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"   Your GEMINI_API_KEY may be invalid or expired.")
                print(f"   Get a new key at: https://aistudio.google.com/app/apikey")
            return False
        except (RuntimeError, Exception) as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            # Log the full error for debugging
            print(f"❌ Error initializing AI Creator ({type(e).__name__}): {error_msg}")
            import traceback
            traceback.print_exc()
            
            # Check if it's an OAuth/browser authentication error
            # On headless servers, OAuth errors are expected and OK - authentication happens via web UI
            if 'browser' in error_lower or 'runnable' in error_lower or 'oauth' in error_lower or 'authentication' in error_lower or 'headless' in error_lower:
                print("⚠️  OAuth authentication not available at startup (this is normal on headless servers)")
                print("   Authentication will happen when you use the 'Login with Google' button in the web UI")
                print("   The AI Creator is initialized and ready to generate form structures")
                # Don't fail initialization - OAuth can happen later
                # Try to initialize again - _authenticate_lazy should handle this gracefully now
                try:
                    ai_creator = AIFormCreator(GEMINI_API_KEY)
                    print("✅ AI Creator initialized (OAuth will be handled via web UI)")
                    return True
                except Exception as retry_error:
                    print(f"⚠️  Retry failed: {retry_error}")
                    # Still return True - Gemini API works, OAuth can happen later via web UI
                    return True
            
            # Check if it's a credentials file error
            if 'credentials' in error_lower or 'not found' in error_lower:
                print(f"❌ OAuth Credentials Error: {error_msg}")
                print(f"   Error type: {type(e).__name__}")
                print(f"\n   Missing OAuth credentials file.")
                print(f"   How to fix:")
                print(f"   1. Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_PROJECT_ID")
                print(f"      in Render Dashboard → Environment tab")
                print(f"   2. Or upload credentials.json file to Render")
                print(f"\n   See: FIX_RENDER_CREDENTIALS.md for detailed instructions")
                return False
            
            # Generic error (likely Gemini API)
            print(f"❌ Error initializing AI Creator: {error_msg}")
            print(f"   Error type: {type(e).__name__}")
            print(f"   Please check:")
            print(f"   1. GEMINI_API_KEY is set correctly")
            print(f"   2. API key is valid (get new one at https://aistudio.google.com/app/apikey)")
            print(f"   3. API key has access to Gemini API")
            print(f"   4. Internet connection is working")
            return False
    return True

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page."""
    # Check if user is authenticated
    user_creds = session.get('user_credentials')
    user_email = user_creds.get('user_email', None) if user_creds else None
    
    # If user_email is None or 'Unknown', try to refresh it
    if user_creds and (not user_email or user_email == 'Unknown'):
        try:
            from google.oauth2.credentials import Credentials
            from googleapiclient.discovery import build
            
            # Recreate credentials from session
            creds = Credentials(
                token=user_creds.get('token'),
                refresh_token=user_creds.get('refresh_token'),
                token_uri=user_creds.get('token_uri'),
                client_id=user_creds.get('client_id'),
                client_secret=user_creds.get('client_secret'),
                scopes=user_creds.get('scopes', [])
            )
            
            # Get user info
            user_info_service = build('oauth2', 'v2', credentials=creds)
            user_info = user_info_service.userinfo().get().execute()
            user_email = user_info.get('email', None)
            
            # Update session with email
            if user_email:
                user_creds['user_email'] = user_email
                session['user_credentials'] = user_creds
                print(f"✅ Refreshed user email: {user_email}")
        except Exception as e:
            print(f"⚠️  Could not refresh user email: {e}")
    
    return render_template('index.html', user_logged_in=user_creds is not None, user_email=user_email or 'Unknown')

@app.route('/help')
def help_page():
    """Help and guide page."""
    # Check if user is authenticated
    user_creds = session.get('user_credentials')
    user_email = user_creds.get('user_email', None) if user_creds else None
    return render_template('help.html', user_logged_in=user_creds is not None, user_email=user_email or 'Unknown')

@app.route('/api/create-from-text', methods=['POST'])
def create_from_text():
    """Create form from text input."""
    log_capture = LogCapture()
    
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'error': 'Text input is required',
                'logs': []
            }), 400
        
        if not init_ai_creator():
            error_msg = 'Failed to initialize AI creator. '
            if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
                error_msg += 'GEMINI_API_KEY environment variable is not set. Please set it and restart the server.'
            else:
                error_msg += 'Please check your GEMINI_API_KEY is valid.'
            return jsonify({
                'success': False,
                'error': error_msg,
                'logs': []
            }), 500
        
        # Capture logs during form structure generation
        with redirect_stdout(log_capture):
            log_capture.write("📝 Starting form generation process...\n")
            log_capture.write("🤖 Analyzing text input with Gemini AI...\n")
            
            # Generate form structure
            form_structure = ai_creator.generate_form_structure_from_text(text)
            
            log_capture.write("✅ Form structure generated successfully!\n")
            log_capture.write(f"📋 Found {len(form_structure.get('questions', []))} questions\n")
        
        return jsonify({
            'success': True,
            'form_structure': form_structure,
            'message': 'Form structure generated successfully!',
            'logs': log_capture.get_logs()
        })
        
    except ImportError as e:
        log_capture.write(f"❌ Error: {str(e)}\n")
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestion': 'Please install required dependencies. See terminal for details.',
            'logs': log_capture.get_logs()
        }), 400
    except Exception as e:
        error_msg = str(e)
        log_capture.write(f"❌ Error: {error_msg}\n")
        print(f"Error creating form: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'logs': log_capture.get_logs()
        }), 500

@app.route('/api/create-from-file', methods=['POST'])
def create_from_file():
    """Create form from uploaded file."""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': f'File type not supported. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        if not init_ai_creator():
            error_msg = 'Failed to initialize AI creator. '
            if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
                error_msg += 'GEMINI_API_KEY environment variable is not set. Please set it and restart the server.'
            else:
                error_msg += 'Please check your GEMINI_API_KEY is valid.'
            return jsonify({
                'success': False,
                'error': error_msg
            }), 500
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        log_capture = LogCapture()
        
        try:
            # Capture logs during form structure generation
            with redirect_stdout(log_capture):
                log_capture.write(f"📄 Reading file: {filename}\n")
                log_capture.write("🤖 Generating form structure using Gemini AI...\n")
                
                # Generate form structure
                form_structure = ai_creator.generate_form_structure_from_file(filepath)
                
                log_capture.write("✅ Form structure generated successfully!\n")
                log_capture.write(f"📋 Found {len(form_structure.get('questions', []))} questions\n")
            
            return jsonify({
                'success': True,
                'form_structure': form_structure,
                'message': 'Form structure generated successfully!',
                'logs': log_capture.get_logs()
            })
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
        
    except ImportError as e:
        if 'log_capture' in locals():
            log_capture.write(f"❌ Error: {str(e)}\n")
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestion': 'Please install required dependencies. See terminal for details.',
            'logs': log_capture.get_logs() if 'log_capture' in locals() else []
        }), 400
    except Exception as e:
        error_msg = str(e)
        if 'log_capture' in locals():
            log_capture.write(f"❌ Error: {error_msg}\n")
        print(f"Error creating form: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'logs': log_capture.get_logs() if 'log_capture' in locals() else []
        }), 500

@app.route('/api/create-form-with-questions', methods=['POST'])
def create_form_with_questions():
    """Create form with modified questions (after preview)."""
    log_capture = LogCapture()
    
    try:
        data = request.get_json()
        form_structure = data.get('form_structure')
        
        if not form_structure:
            return jsonify({
                'success': False,
                'error': 'Form structure is required',
                'logs': []
            }), 400
        
        if not init_ai_creator():
            error_msg = 'Failed to initialize AI creator. '
            if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
                error_msg += 'GEMINI_API_KEY environment variable is not set. Please set it and restart the server.'
            else:
                error_msg += 'Please check your GEMINI_API_KEY is valid.'
            return jsonify({
                'success': False,
                'error': error_msg,
                'logs': []
            }), 500
        
        # Create form with modified structure
        with redirect_stdout(log_capture):
            log_capture.write("📝 Creating Google Form with your settings...\n")
            
            # Extract form info
            title = form_structure.get('title', 'AI Generated Form')
            description = form_structure.get('description', '')
            questions = form_structure.get('questions', [])
            
            log_capture.write(f"📋 Form Title: {title}\n")
            log_capture.write(f"❓ Number of questions: {len(questions)}\n")
            
            # Get user credentials (for per-user authentication)
            user_creds = get_user_credentials()
            
            # Create form generator with user credentials (if available) or use default
            if user_creds:
                log_capture.write("👤 Using your Google account credentials\n")
                form_generator = GoogleFormGenerator(user_credentials=user_creds)
            else:
                log_capture.write("🔧 Using server account credentials\n")
                form_generator = ai_creator.form_generator
            
            # Create form
            form = form_generator.create_form(title, description)
            
            # Add questions with updated required settings
            log_capture.write("\n➕ Adding questions...\n")
            for i, question in enumerate(questions, 1):
                try:
                    question_text = question.get('text', '')
                    question_type = question.get('type', 'text')
                    required = question.get('required', False)
                    
                    required_status = "Required" if required else "Optional"
                    log_capture.write(f"  [{i}/{len(questions)}] {question_text[:40]}... ({question_type}, {required_status})\n")
                    
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
                    log_capture.write(f"  ⚠️  Warning: Could not add question {i}: {e}\n")
                    continue
            
            form_url = form.get_url()
            log_capture.write("\n✅ Form created successfully!\n")
            log_capture.write(f"🔗 Form URL: {form_url}\n")
        
        return jsonify({
            'success': True,
            'form_url': form_url,
            'message': 'Form created successfully!',
            'logs': log_capture.get_logs()
        })
        
    except Exception as e:
        error_msg = str(e)
        if 'log_capture' in locals():
            log_capture.write(f"❌ Error: {error_msg}\n")
        print(f"Error creating form: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'logs': log_capture.get_logs() if 'log_capture' in locals() else []
        }), 500

@app.route('/api/create-from-docs', methods=['POST'])
def create_from_docs():
    """Create form from Google Docs link."""
    log_capture = LogCapture()
    
    try:
        data = request.get_json()
        doc_url = data.get('url', '').strip()
        
        if not doc_url:
            return jsonify({
                'success': False,
                'error': 'Google Docs URL is required',
                'logs': []
            }), 400
        
        # Initialize AI creator with detailed logging
        log_capture.write("🔧 Initializing AI creator...\n")
        if not init_ai_creator():
            error_msg = 'Failed to initialize AI creator. '
            if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
                error_msg += 'GEMINI_API_KEY environment variable is not set. Please set it in Render Dashboard → Environment tab and restart the server.'
            else:
                error_msg += f'Please check your GEMINI_API_KEY is valid. Current key starts with: {GEMINI_API_KEY[:10]}...'
            log_capture.write(f"❌ {error_msg}\n")
            return jsonify({
                'success': False,
                'error': error_msg,
                'logs': log_capture.get_logs()
            }), 500
        
        log_capture.write("✅ AI creator initialized successfully\n")
        
        # Capture logs during form structure generation
        with redirect_stdout(log_capture):
            log_capture.write("📄 Reading Google Docs document...\n")
            log_capture.write(f"🔗 URL: {doc_url}\n")
            log_capture.write("🤖 Generating form structure using Gemini AI...\n")
            
            # Generate form structure from Google Docs
            form_structure = ai_creator.generate_form_structure_from_google_doc(doc_url)
            
            log_capture.write("✅ Form structure generated successfully!\n")
            log_capture.write(f"📋 Found {len(form_structure.get('questions', []))} questions\n")
        
        return jsonify({
            'success': True,
            'form_structure': form_structure,
            'message': 'Form structure generated successfully!',
            'logs': log_capture.get_logs()
        })
        
    except ImportError as e:
        log_capture.write(f"❌ Error: {str(e)}\n")
        return jsonify({
            'success': False,
            'error': str(e),
            'suggestion': 'Please install required dependencies. See terminal for details.',
            'logs': log_capture.get_logs()
        }), 400
    except Exception as e:
        error_msg = str(e)
        log_capture.write(f"❌ Error: {error_msg}\n")
        print(f"Error creating form from Google Docs: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'logs': log_capture.get_logs()
        }), 500

@app.route('/api/create-from-script', methods=['POST'])
def create_from_script():
    """Create form from uploaded script (Google Apps Script or JSON)."""
    log_capture = LogCapture()
    
    try:
        data = request.get_json()
        script_code = data.get('script_code', '')
        script_data = data.get('script', None)
        
        if not script_code and not script_data:
            return jsonify({
                'success': False,
                'error': 'Script code or data is required',
                'logs': []
            }), 400
        
        if not init_ai_creator():
            error_msg = 'Failed to initialize form creator. '
            if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == '':
                error_msg += 'GEMINI_API_KEY environment variable is not set. Please set it and restart the server.'
            else:
                error_msg += 'Please check your GEMINI_API_KEY is valid.'
            return jsonify({
                'success': False,
                'error': error_msg,
                'logs': []
            }), 500
        
        # Parse script if script_code is provided
        if script_code:
            try:
                from script_parser import parse_script
                script_data = parse_script(script_code)
                log_capture.write("✅ Script parsed successfully\n")
            except Exception as e:
                return jsonify({
                    'success': False,
                    'error': f'Error parsing script: {str(e)}',
                    'logs': log_capture.get_logs()
                }), 400
        
        # Validate script structure
        if not isinstance(script_data, dict):
            return jsonify({
                'success': False,
                'error': 'Script must be a valid JSON object or Google Apps Script',
                'logs': []
            }), 400
        
        # Capture logs during form creation
        with redirect_stdout(log_capture):
            log_capture.write("📜 Creating form from script...\n")
            
            title = script_data.get('title', 'Form from Script')
            description = script_data.get('description', '')
            questions = script_data.get('questions', [])
            
            if not questions:
                return jsonify({
                    'success': False,
                    'error': 'Script must contain at least one question',
                    'logs': log_capture.get_logs()
                }), 400
            
            log_capture.write(f"📋 Form Title: {title}\n")
            log_capture.write(f"📝 Description: {description[:100]}..." if len(description) > 100 else f"📝 Description: {description}\n")
            log_capture.write(f"❓ Number of questions: {len(questions)}\n")
            
            # Get user credentials (for per-user authentication)
            user_creds = get_user_credentials()
            
            # Create form generator with user credentials (if available) or use default
            if user_creds:
                log_capture.write("👤 Using your Google account credentials\n")
                form_generator = GoogleFormGenerator(user_credentials=user_creds)
            else:
                log_capture.write("🔧 Using server account credentials\n")
                form_generator = ai_creator.form_generator
            
            # Create form
            form = form_generator.create_form(title, description)
            log_capture.write("\n➕ Adding questions...\n")
            
            for i, question in enumerate(questions, 1):
                try:
                    question_text = question.get('text', '')
                    question_type = question.get('type', 'text')
                    # Use default setting from request or default to True
                    default_required = data.get('default_required', True)
                    required = question.get('required', default_required)
                    
                    required_status = "Required" if required else "Optional"
                    log_capture.write(f"  [{i}/{len(questions)}] {question_text[:40]}... ({question_type}, {required_status})\n")
                    
                    # Add question based on type
                    if question_type == 'choice' or question_type == 'multiple_choice':
                        options = question.get('options', [])
                        if options:
                            form.add_multiple_choice_question(question_text, options, required=required)
                        else:
                            log_capture.write(f"  ⚠️  Warning: Question {i} has type 'choice' but no options, creating as text question\n")
                            form.add_question(question_text, required=required)
                    elif question_type == 'dropdown':
                        options = question.get('options', [])
                        if options:
                            form.add_dropdown_question(question_text, options, required=required)
                        else:
                            log_capture.write(f"  ⚠️  Warning: Question {i} has type 'dropdown' but no options, creating as text question\n")
                            form.add_question(question_text, required=required)
                    elif question_type == 'checkbox':
                        options = question.get('options', [])
                        if options:
                            form.add_checkbox_question(question_text, options, required=required)
                        else:
                            form.add_question(question_text, required=required)
                    elif question_type == 'scale' or question_type == 'linear_scale':
                        min_value = question.get('min', 1)
                        max_value = question.get('max', 5)
                        min_label = question.get('min_label', '')
                        max_label = question.get('max_label', '')
                        form.add_linear_scale_question(question_text, min_value, max_value, min_label, max_label, required=required)
                    else:
                        # Default to text question
                        form.add_question(question_text, required=required)
                        
                except Exception as e:
                    log_capture.write(f"  ⚠️  Warning: Could not add question {i}: {e}\n")
                    continue
            
            form_url = form.get_url()
            log_capture.write("\n✅ Form created successfully!\n")
            log_capture.write(f"🔗 Form URL: {form_url}\n")
        
        return jsonify({
            'success': True,
            'form_url': form_url,
            'message': 'Form created successfully from script!',
            'logs': log_capture.get_logs()
        })
        
    except Exception as e:
        error_msg = str(e)
        log_capture.write(f"❌ Error: {error_msg}\n")
        print(f"Error creating form from script: {error_msg}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': error_msg,
            'logs': log_capture.get_logs()
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'ai_initialized': ai_creator is not None
    })

@app.route('/api/check-credentials', methods=['GET'])
def check_credentials():
    """Check credentials configuration status."""
    try:
        # Check for credentials file
        credentials_file = os.getenv('CREDENTIALS_FILE_PATH')
        found_file = False
        file_path = None
        
        # Primary location: /etc/secrets/credentials.json
        primary_location = '/etc/secrets/credentials.json'
        
        # Get absolute path for project root
        project_root = os.path.dirname(os.path.abspath(__file__))
        project_root_creds = os.path.join(project_root, 'credentials.json')
        
        print(f"🔍 [CHECK-CREDENTIALS] Checking credentials...")
        print(f"   Project root: {project_root}")
        print(f"   Project root credentials: {project_root_creds}")
        print(f"   Project root credentials exists: {os.path.exists(project_root_creds)}")
        
        if credentials_file and os.path.exists(credentials_file):
            found_file = True
            file_path = os.path.abspath(credentials_file)
            print(f"✅ Found credentials via CREDENTIALS_FILE_PATH: {file_path}")
        else:
            # Check primary location first
            if os.path.exists(primary_location):
                found_file = True
                file_path = primary_location
                print(f"✅ Found credentials at primary location: {file_path}")
            else:
                # Check fallback locations (use absolute paths)
                fallback_locations = [
                    project_root_creds,  # Project root (absolute path)
                    'credentials.json',  # Relative path (current working directory)
                    '/opt/render/project/src/credentials.json',  # Render project path
                    os.path.expanduser('~/credentials.json'),  # Home directory
                ]
                for location in fallback_locations:
                    abs_location = os.path.abspath(location) if not os.path.isabs(location) else location
                    if os.path.exists(location) or os.path.exists(abs_location):
                        found_file = True
                        file_path = abs_location if os.path.exists(abs_location) else location
                        print(f"✅ Found credentials at fallback location: {file_path}")
                        break
        
        # Check environment variables
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        project_id = os.getenv('GOOGLE_PROJECT_ID')
        
        env_vars_set = bool(client_id and client_secret and project_id)
        
        return jsonify({
            'credentials_file_found': found_file,
            'credentials_file_path': file_path,
            'environment_variables_set': env_vars_set,
            'client_id_set': bool(client_id),
            'client_secret_set': bool(client_secret),
            'project_id_set': bool(project_id),
            'can_create_credentials': env_vars_set and not found_file,
            'status': 'ok' if (found_file or env_vars_set) else 'missing',
            'message': (
                'Credentials configured' if (found_file or env_vars_set) else
                'No credentials found. Please set environment variables or upload credentials.json'
            )
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check if user is authenticated."""
    user_creds = session.get('user_credentials')
    return jsonify({
        'authenticated': user_creds is not None,
        'user_email': user_creds.get('user_email', None) if user_creds else None
    })

@app.route('/auth/login', methods=['GET'])
def login():
    """Initiate OAuth flow for user."""
    try:
        from google_auth_oauthlib.flow import Flow
        from google_form_generator import GoogleFormGenerator
        
        print(f"🔍 [LOGIN] Starting OAuth login flow...")
        print(f"   Current working directory: {os.getcwd()}")
        
        # First, try to find or create credentials file
        # Check environment variable first
        credentials_file = os.getenv('CREDENTIALS_FILE_PATH')
        print(f"   CREDENTIALS_FILE_PATH env var: {credentials_file}")
        
        # Primary location: /etc/secrets/credentials.json (works on both local and Render)
        primary_location = '/etc/secrets/credentials.json'
        print(f"   Primary location: {primary_location}")
        print(f"   Primary location exists: {os.path.exists(primary_location)}")
        
        # Ensure /etc/secrets/ directory exists (create if needed)
        secrets_dir = '/etc/secrets'
        if not os.path.exists(secrets_dir):
            try:
                os.makedirs(secrets_dir, mode=0o755, exist_ok=True)
                print(f"✅ Created directory: {secrets_dir}")
            except (OSError, PermissionError) as e:
                # If we can't create /etc/secrets (e.g., no admin on Windows), fall back
                print(f"⚠️  Could not create {secrets_dir}: {e}")
                print(f"   Will use alternative location")
        
        # If not set via env var, check primary location first
        if not credentials_file or not os.path.exists(credentials_file):
            print(f"   Checking primary location: {primary_location}")
            if os.path.exists(primary_location):
                credentials_file = primary_location
                print(f"✅ [LOGIN] Found credentials at primary location: {credentials_file}")
            else:
                print(f"   Primary location not found, checking fallback locations...")
                # Get absolute path for project root
                project_root = os.path.dirname(os.path.abspath(__file__))
                project_root_creds = os.path.join(project_root, 'credentials.json')
                print(f"   Project root: {project_root}")
                print(f"   Project root credentials: {project_root_creds}")
                print(f"   Project root credentials exists: {os.path.exists(project_root_creds)}")
                
                # Fallback locations (check absolute paths first)
                fallback_locations = [
                    project_root_creds,  # Project root (absolute path) - CHECK THIS FIRST
                    'credentials.json',  # Relative path (current working directory)
                    '/opt/render/project/src/credentials.json',  # Render project path
                    os.path.expanduser('~/credentials.json'),  # Home directory
                ]
                for location in fallback_locations:
                    abs_location = os.path.abspath(location) if not os.path.isabs(location) else location
                    if os.path.exists(location) or os.path.exists(abs_location):
                        credentials_file = abs_location if os.path.exists(abs_location) else location
                        print(f"✅ [LOGIN] Found credentials at fallback location: {credentials_file}")
                        break
                
                # If still not found, use primary location (will create from env vars)
                if not credentials_file or not os.path.exists(credentials_file):
                    credentials_file = primary_location
        
        # If still not found, try to create from environment variables
        print(f"   Final credentials_file value: {credentials_file}")
        print(f"   credentials_file exists: {os.path.exists(credentials_file) if credentials_file else 'N/A'}")
        
        if not credentials_file or not os.path.exists(credentials_file):
            print(f"⚠️  [LOGIN] Credentials file not found, attempting to create from environment variables...")
            client_id = os.getenv('GOOGLE_CLIENT_ID', '').strip()
            client_secret = os.getenv('GOOGLE_CLIENT_SECRET', '').strip()
            project_id = os.getenv('GOOGLE_PROJECT_ID', '').strip()
            
            # Debug logging
            print(f"🔍 Checking environment variables for OAuth credentials...")
            print(f"   GOOGLE_CLIENT_ID: {'Set (length: ' + str(len(client_id)) + ')' if client_id else 'Not set'}")
            print(f"   GOOGLE_CLIENT_SECRET: {'Set (length: ' + str(len(client_secret)) + ')' if client_secret else 'Not set'}")
            print(f"   GOOGLE_PROJECT_ID: {'Set (value: ' + project_id + ')' if project_id else 'Not set'}")
            print(f"   Target credentials file: {credentials_file}")
            
            if client_id and client_secret and project_id:
                try:
                    # Use primary location: /etc/secrets/credentials.json
                    if not credentials_file or credentials_file == 'credentials.json':
                        credentials_file = primary_location
                    
                    print(f"📝 Attempting to create credentials file at: {credentials_file}")
                    
                    # Ensure /etc/secrets/ directory exists
                    creds_dir = os.path.dirname(credentials_file)
                    print(f"📁 Credentials directory: {creds_dir}")
                    
                    if not os.path.exists(creds_dir):
                        try:
                            os.makedirs(creds_dir, mode=0o755, exist_ok=True)
                            print(f"✅ Created directory: {creds_dir}")
                        except (OSError, PermissionError) as e:
                            print(f"⚠️  Could not create {creds_dir}: {e}")
                            # Fallback to project root if /etc/secrets can't be created
                            print(f"⚠️  Falling back to project root")
                            credentials_file = 'credentials.json'
                            creds_dir = '.'
                    
                    # Verify directory exists now
                    if not os.path.exists(creds_dir):
                        raise Exception(f"Directory does not exist and could not be created: {creds_dir}")
                    
                    # Create credentials.json from environment variables
                    import json
                    # Use "web" type for web applications (not "installed" for desktop apps)
                    credentials_data = {
                        "web": {
                            "client_id": client_id,
                            "client_secret": client_secret,
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": [
                                "http://localhost:5000/auth/callback",
                                "http://localhost/auth/callback",
                                "https://localhost:5000/auth/callback"
                            ]
                        },
                        "project_id": project_id
                    }
                    
                    print(f"💾 Writing credentials file to: {credentials_file}")
                    print(f"   Directory exists: {os.path.exists(creds_dir)}")
                    print(f"   Directory writable: {os.access(creds_dir, os.W_OK) if os.path.exists(creds_dir) else 'N/A'}")
                    
                    # Ensure directory exists (double check)
                    os.makedirs(creds_dir, mode=0o755, exist_ok=True)
                    
                    with open(credentials_file, 'w') as f:
                        json.dump(credentials_data, f, indent=2)
                    
                    # Verify file was created
                    if os.path.exists(credentials_file):
                        file_size = os.path.getsize(credentials_file)
                        print(f"✅ Created credentials.json from environment variables at: {credentials_file} (size: {file_size} bytes)")
                        # File created successfully, continue with OAuth flow
                    else:
                        raise Exception(f"File was written but not found at: {credentials_file}")
                except Exception as e:
                    print(f"⚠️  Could not create credentials.json from environment: {e}")
                    import traceback
                    traceback.print_exc()
                    return jsonify({
                        'success': False,
                        'error': f'Could not create credentials file: {str(e)}. Please ensure GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_PROJECT_ID are set correctly. Error details: {str(e)}'
                    }), 500
            else:
                missing_vars = []
                if not client_id:
                    missing_vars.append('GOOGLE_CLIENT_ID')
                if not client_secret:
                    missing_vars.append('GOOGLE_CLIENT_SECRET')
                if not project_id:
                    missing_vars.append('GOOGLE_PROJECT_ID')
                
                error_msg = (
                    'Credentials file not found. Please configure OAuth credentials.\n\n'
                    'Option 1: Upload credentials.json file to your server\n'
                    'Option 2: Set the following environment variables in Render Dashboard:\n'
                    f'  - {", ".join(missing_vars)}\n\n'
                    'To get these values:\n'
                    '1. Go to Google Cloud Console → APIs & Services → Credentials\n'
                    '2. Click on your OAuth 2.0 Client ID\n'
                    '3. Copy the Client ID → Set as GOOGLE_CLIENT_ID\n'
                    '4. Copy the Client Secret → Set as GOOGLE_CLIENT_SECRET\n'
                    '5. Copy the Project ID → Set as GOOGLE_PROJECT_ID'
                )
                return jsonify({
                    'success': False,
                    'error': error_msg
                }), 500
        
        # Final verification (after potential creation from env vars)
        # Re-check if file exists (it might have been created from env vars)
        if not os.path.exists(credentials_file):
            # Try to find it again in case it was created elsewhere
            if os.path.exists(primary_location):
                credentials_file = primary_location
                print(f"✅ Found credentials file at primary location: {credentials_file}")
            elif os.path.exists('credentials.json'):
                credentials_file = 'credentials.json'
                print(f"✅ Found credentials file at fallback location: {credentials_file}")
            else:
                # Additional debug info
                print(f"❌ Credentials file not found at: {credentials_file}")
                print(f"   Current working directory: {os.getcwd()}")
                print(f"   Checking if /etc/secrets/ exists: {os.path.exists('/etc/secrets')}")
                if os.path.exists('/etc/secrets'):
                    print(f"   Files in /etc/secrets/: {os.listdir('/etc/secrets') if os.path.exists('/etc/secrets') else 'N/A'}")
                print(f"   Files in current directory: {os.listdir('.') if os.path.exists('.') else 'N/A'}")
                
                return jsonify({
                    'success': False,
                    'error': f'Credentials file not found at: {credentials_file}. Please configure OAuth credentials. Check Render logs for detailed debug information.'
                }), 500
        
        # Verify file is readable and valid JSON
        try:
            with open(credentials_file, 'r') as f:
                import json
                creds_data = json.load(f)
                if 'installed' not in creds_data and 'web' not in creds_data:
                    raise ValueError("Invalid credentials file format")
            
            # Check OAuth client type
            oauth_type = 'web' if 'web' in creds_data else 'installed'
            client_id = creds_data.get(oauth_type, {}).get('client_id', 'Not found')
            print(f"✅ Verified credentials file is valid at: {credentials_file}")
            print(f"   OAuth client type: {oauth_type}")
            print(f"   Client ID: {client_id[:50]}..." if len(str(client_id)) > 50 else f"   Client ID: {client_id}")
            
            # Warn if using 'installed' type (should be 'web' for web apps)
            if oauth_type == 'installed':
                print(f"⚠️  WARNING: Using 'installed' type. For web applications, 'web' type is recommended.")
                print(f"   Consider creating a new 'Web application' OAuth client in Google Cloud Console.")
        except Exception as e:
            print(f"⚠️  Credentials file exists but is invalid: {e}")
            return jsonify({
                'success': False,
                'error': f'Credentials file is invalid: {str(e)}. Please check the file format.'
            }), 500
        
        # Get redirect URI - use _external=True to get full URL
        redirect_uri = url_for('callback', _external=True)
        
        # Detect if we're on Render or production (check for RENDER environment or HTTPS)
        is_production = (
            os.getenv('RENDER') == 'true' or
            os.getenv('FLASK_ENV') == 'production' or
            request.scheme == 'https' or
            'onrender.com' in request.host or
            'railway.app' in request.host
        )
        
        # In production, force HTTPS
        if is_production and redirect_uri.startswith('http://'):
            redirect_uri = redirect_uri.replace('http://', 'https://')
        
        print(f"🔗 [LOGIN] Redirect URI: {redirect_uri}")
        print(f"   Is production: {is_production}")
        print(f"   Request scheme: {request.scheme}")
        print(f"   Request host: {request.host}")
        print(f"   Full request URL: {request.url}")
        print(f"   Expected redirect URIs in Google Cloud Console:")
        print(f"     - http://localhost:5000/auth/callback")
        print(f"     - https://google-from-generator.onrender.com/auth/callback")
        print(f"   Make sure the redirect URI above matches EXACTLY one of these!")
        
        # Create OAuth flow
        try:
            flow = Flow.from_client_secrets_file(
                credentials_file,
                scopes=GoogleFormGenerator.SCOPES,
                redirect_uri=redirect_uri
            )
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent to get refresh token
            )
            print(f"✅ OAuth flow created successfully")
            print(f"   Authorization URL generated")
        except Exception as flow_error:
            print(f"❌ Error creating OAuth flow: {flow_error}")
            print(f"   This might indicate a redirect_uri_mismatch")
            print(f"   Redirect URI used: {redirect_uri}")
            raise
        
        session['oauth_state'] = state
        session['oauth_flow_credentials_file'] = credentials_file
        
        return redirect(authorization_url)
    except Exception as e:
        print(f"Error initiating OAuth: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Failed to initiate OAuth: {str(e)}'
        }), 500

@app.route('/auth/callback', methods=['GET'])
def callback():
    """Handle OAuth callback."""
    try:
        from google_auth_oauthlib.flow import Flow
        from google_form_generator import GoogleFormGenerator
        from google.oauth2.credentials import Credentials
        
        # Check state
        state = session.get('oauth_state')
        if not state or state != request.args.get('state'):
            return jsonify({
                'success': False,
                'error': 'Invalid OAuth state. Please try again.'
            }), 400
        
        credentials_file = session.get('oauth_flow_credentials_file', 'credentials.json')
        
        # Get redirect URI - use _external=True to get full URL
        redirect_uri = url_for('callback', _external=True)
        
        # Detect if we're on Render or production
        is_production = (
            os.getenv('RENDER') == 'true' or
            os.getenv('FLASK_ENV') == 'production' or
            request.scheme == 'https' or
            'onrender.com' in request.host or
            'railway.app' in request.host
        )
        
        # In production, force HTTPS
        if is_production and redirect_uri.startswith('http://'):
            redirect_uri = redirect_uri.replace('http://', 'https://')
        
        print(f"🔗 [CALLBACK] Redirect URI: {redirect_uri}")
        print(f"   Callback URL received: {request.url}")
        print(f"   Make sure redirect URI matches what was used in /auth/login")
        
        # Create flow and fetch token
        try:
            flow = Flow.from_client_secrets_file(
                credentials_file,
                scopes=GoogleFormGenerator.SCOPES,
                redirect_uri=redirect_uri
            )
            
            print(f"✅ OAuth flow created for callback")
            flow.fetch_token(authorization_response=request.url)
            print(f"✅ Token fetched successfully")
        except Exception as token_error:
            print(f"❌ Error fetching token: {token_error}")
            print(f"   Redirect URI used: {redirect_uri}")
            print(f"   Callback URL: {request.url}")
            if 'redirect_uri_mismatch' in str(token_error).lower():
                print(f"   ⚠️  REDIRECT URI MISMATCH DETECTED!")
                print(f"   Please verify the redirect URI in Google Cloud Console matches exactly:")
                print(f"   {redirect_uri}")
            raise
        credentials = flow.credentials
        
        # Get user info
        user_email = None
        try:
            from googleapiclient.discovery import build
            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()
            user_email = user_info.get('email', None)
            
            # Try alternative methods to get email
            if not user_email:
                user_email = user_info.get('emailAddress', None)
            
            # Log user info for debugging
            print(f"📧 User info retrieved: {user_info}")
            print(f"📧 User email: {user_email}")
            
            # Fallback if still no email
            if not user_email:
                print(f"⚠️  Could not retrieve user email from user_info")
                user_email = None
            else:
                print(f"✅ Retrieved user email: {user_email}")
        except Exception as e:
            print(f"⚠️  Error getting user info: {e}")
            import traceback
            traceback.print_exc()
            user_email = None
        
        # If we still don't have email, try to get from token
        if not user_email:
            try:
                # Try to extract from ID token if available
                if hasattr(credentials, 'id_token') and credentials.id_token:
                    import base64
                    import json
                    # ID token is a JWT, decode it (without verification for now)
                    parts = credentials.id_token.split('.')
                    if len(parts) >= 2:
                        # Decode the payload (second part)
                        payload = parts[1]
                        # Add padding if needed
                        payload += '=' * (4 - len(payload) % 4)
                        decoded = base64.urlsafe_b64decode(payload)
                        token_data = json.loads(decoded)
                        user_email = token_data.get('email', None)
                        if user_email:
                            print(f"✅ Retrieved user email from ID token: {user_email}")
            except Exception as token_error:
                print(f"⚠️  Could not get email from ID token: {token_error}")
        
        # Final fallback
        if not user_email:
            user_email = 'Unknown'
            print(f"⚠️  Using fallback email: Unknown")
        
        # Store in session
        session['user_credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': list(credentials.scopes) if credentials.scopes else [],
            'user_email': user_email
        }
        
        # Clear OAuth state
        session.pop('oauth_state', None)
        session.pop('oauth_flow_credentials_file', None)
        
        return redirect(url_for('index'))
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'OAuth callback failed: {str(e)}'
        }), 500

@app.route('/auth/logout', methods=['POST', 'GET'])
def logout():
    """Logout user."""
    session.pop('user_credentials', None)
    session.pop('oauth_state', None)
    session.pop('oauth_flow_credentials_file', None)
    
    if request.method == 'POST':
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    return redirect(url_for('index'))

def get_user_credentials():
    """Get user credentials from session or return None."""
    user_creds_data = session.get('user_credentials')
    
    if not user_creds_data:
        return None
    
    try:
        from google.oauth2.credentials import Credentials
        
        # Reconstruct credentials object
        user_creds = Credentials(
            token=user_creds_data['token'],
            refresh_token=user_creds_data.get('refresh_token'),
            token_uri=user_creds_data['token_uri'],
            client_id=user_creds_data['client_id'],
            client_secret=user_creds_data['client_secret'],
            scopes=user_creds_data['scopes']
        )
        
        # Refresh if expired
        if user_creds.expired and user_creds.refresh_token:
            try:
                user_creds.refresh(Request())
                # Update session with new token
                session['user_credentials']['token'] = user_creds.token
            except Exception as e:
                print(f"Warning: Could not refresh token: {e}")
        
        return user_creds
    except Exception as e:
        print(f"Error reconstructing credentials: {e}")
        return None

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors with JSON."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors with JSON."""
    import traceback
    error_details = traceback.format_exc()
    print(f"Internal Server Error: {error_details}")
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred. Please check the server logs.',
        'details': str(error) if os.getenv('DEBUG', 'False').lower() == 'true' else None
    }), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions with JSON."""
    import traceback
    error_details = traceback.format_exc()
    print(f"Unhandled Exception: {error_details}")
    return jsonify({
        'success': False,
        'error': 'An unexpected error occurred',
        'message': str(e),
        'details': error_details if os.getenv('DEBUG', 'False').lower() == 'true' else None
    }), 500

if __name__ == '__main__':
    import webbrowser
    from threading import Timer
    
    def open_browser():
        """Open browser after a short delay."""
        webbrowser.open('http://127.0.0.1:5000')
    
    print("\n" + "="*70)
    print("  🌐 Starting AI Form Creator Web Application")
    print("="*70)
    print("\n📝 Server will start at: http://127.0.0.1:5000")
    print("💡 The browser will open automatically...")
    print("💡 Press Ctrl+C to stop the server\n")
    
    # Open browser after 1.5 seconds
    Timer(1.5, open_browser).start()
    
    # Run Flask app
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)


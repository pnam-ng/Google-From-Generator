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
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY', '')

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
        
        try:
            # Pass None to let AIFormCreator check environment variables itself
            ai_creator = AIFormCreator(GEMINI_API_KEY if GEMINI_API_KEY else None)
            return True
        except ValueError as e:
            error_msg = str(e)
            print(f"❌ Error initializing AI Creator: {error_msg}")
            if "API key" in error_msg.lower() or "invalid" in error_msg.lower():
                print(f"   Your GEMINI_API_KEY may be invalid or expired.")
                print(f"   Get a new key at: https://aistudio.google.com/app/apikey")
            return False
        except Exception as e:
            error_msg = str(e)
            error_lower = error_msg.lower()
            
            # Check if it's an OAuth/browser authentication error
            if 'browser' in error_lower or 'runnable' in error_lower or 'oauth' in error_lower:
                print(f"❌ OAuth Authentication Error: {error_msg}")
                print(f"   Error type: {type(e).__name__}")
                print(f"\n   This is an OAuth authentication issue, not a Gemini API issue.")
                print(f"   The app needs to authenticate with Google on first startup.")
                print(f"\n   How to fix:")
                print(f"   1. Check Render logs for the authorization URL")
                print(f"   2. Visit the URL in your browser to authorize")
                print(f"   3. The app will automatically use console-based authentication")
                print(f"   4. Or upload an existing token.pickle file to Render")
                print(f"\n   See: FIX_HEADLESS_AUTH.md for detailed instructions")
                return False
            
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
    return render_template('index.html', user_logged_in=user_creds is not None, user_email=user_email)

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
        
        # Find credentials file
        credentials_file = os.getenv('CREDENTIALS_FILE_PATH')
        if not credentials_file or not os.path.exists(credentials_file):
            # Try to find it automatically
            possible_locations = [
                'credentials.json',
                '/etc/secrets/credentials.json',
                '/opt/render/project/src/credentials.json',
            ]
            for loc in possible_locations:
                if os.path.exists(loc):
                    credentials_file = loc
                    break
        
        if not credentials_file or not os.path.exists(credentials_file):
            return jsonify({
                'success': False,
                'error': 'Credentials file not found. Please configure OAuth credentials.'
            }), 500
        
        # Get redirect URI - use _external=True to get full URL
        # For production, ensure HTTPS is used
        redirect_uri = url_for('callback', _external=True)
        
        # In production, force HTTPS
        FLASK_ENV = os.getenv('FLASK_ENV', 'development')
        if FLASK_ENV == 'production':
            redirect_uri = redirect_uri.replace('http://', 'https://')
        
        # Create OAuth flow
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
        # For production, ensure HTTPS is used
        redirect_uri = url_for('callback', _external=True)
        
        # In production, force HTTPS
        FLASK_ENV = os.getenv('FLASK_ENV', 'development')
        if FLASK_ENV == 'production':
            redirect_uri = redirect_uri.replace('http://', 'https://')
        
        # Create flow and fetch token
        flow = Flow.from_client_secrets_file(
            credentials_file,
            scopes=GoogleFormGenerator.SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(authorization_response=request.url)
        credentials = flow.credentials
        
        # Get user info
        try:
            from googleapiclient.discovery import build
            user_info_service = build('oauth2', 'v2', credentials=credentials)
            user_info = user_info_service.userinfo().get().execute()
            user_email = user_info.get('email', 'Unknown')
        except:
            user_email = 'Unknown'
        
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


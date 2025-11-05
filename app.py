"""
Flask Web Application for AI-Powered Google Form Creator
Cross-platform web UI for non-technical users
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_from_directory
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

# Gemini API Key - Load from environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

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
        try:
            ai_creator = AIFormCreator(GEMINI_API_KEY)
            return True
        except Exception as e:
            print(f"Error initializing AI Creator: {e}")
            return False
    return True

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')

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
            return jsonify({
                'success': False,
                'error': 'Failed to initialize AI creator. Please check your credentials.',
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
            return jsonify({
                'success': False,
                'error': 'Failed to initialize AI creator. Please check your credentials.'
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
            return jsonify({
                'success': False,
                'error': 'Failed to initialize AI creator. Please check your credentials.',
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
            
            # Create form
            form = ai_creator.form_generator.create_form(title, description)
            
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
        
        if not init_ai_creator():
            return jsonify({
                'success': False,
                'error': 'Failed to initialize AI creator. Please check your credentials.',
                'logs': []
            }), 500
        
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
            return jsonify({
                'success': False,
                'error': 'Failed to initialize form creator. Please check your credentials.',
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
            
            # Create form
            form = ai_creator.form_generator.create_form(title, description)
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


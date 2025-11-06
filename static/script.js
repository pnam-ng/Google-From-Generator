// Global variable to store default required setting
window.defaultRequiredSetting = true; // true = all required, false = all optional

// Setup default required/optional buttons
function setupDefaultSettingButtons() {
    // Text tab buttons
    const setRequiredText = document.getElementById('set-default-required-btn');
    const setOptionalText = document.getElementById('set-default-optional-btn');
    
    if (setRequiredText) {
        setRequiredText.addEventListener('click', () => {
            window.defaultRequiredSetting = true;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Required');
        });
    }
    
    if (setOptionalText) {
        setOptionalText.addEventListener('click', () => {
            window.defaultRequiredSetting = false;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Optional');
        });
    }
    
    // File tab buttons
    const setRequiredFile = document.getElementById('set-default-required-btn-file');
    const setOptionalFile = document.getElementById('set-default-optional-btn-file');
    
    if (setRequiredFile) {
        setRequiredFile.addEventListener('click', () => {
            window.defaultRequiredSetting = true;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Required');
        });
    }
    
    if (setOptionalFile) {
        setOptionalFile.addEventListener('click', () => {
            window.defaultRequiredSetting = false;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Optional');
        });
    }
    
    // Docs tab buttons
    const setRequiredDocs = document.getElementById('set-default-required-btn-docs');
    const setOptionalDocs = document.getElementById('set-default-optional-btn-docs');
    
    if (setRequiredDocs) {
        setRequiredDocs.addEventListener('click', () => {
            window.defaultRequiredSetting = true;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Required');
        });
    }
    
    if (setOptionalDocs) {
        setOptionalDocs.addEventListener('click', () => {
            window.defaultRequiredSetting = false;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Optional');
        });
    }
    
    // Script tab buttons
    const setRequiredScript = document.getElementById('set-default-required-btn-script');
    const setOptionalScript = document.getElementById('set-default-optional-btn-script');
    
    if (setRequiredScript) {
        setRequiredScript.addEventListener('click', () => {
            window.defaultRequiredSetting = true;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Required');
        });
    }
    
    if (setOptionalScript) {
        setOptionalScript.addEventListener('click', () => {
            window.defaultRequiredSetting = false;
            updateDefaultButtonStates();
            console.log('✅ Default setting: All Optional');
        });
    }
    
    // Initial button state
    updateDefaultButtonStates();
}

function updateDefaultButtonStates() {
    const isRequired = window.defaultRequiredSetting;
    
    // Update all required buttons
    document.querySelectorAll('#set-default-required-btn, #set-default-required-btn-file, #set-default-required-btn-docs, #set-default-required-btn-script').forEach(btn => {
        if (btn) {
            if (isRequired) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    });
    
    // Update all optional buttons
    document.querySelectorAll('#set-default-optional-btn, #set-default-optional-btn-file, #set-default-optional-btn-docs, #set-default-optional-btn-script').forEach(btn => {
        if (btn) {
            if (!isRequired) {
                btn.classList.add('active');
            } else {
                btn.classList.remove('active');
            }
        }
    });
}

// Tab switching
document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Update active tab content
        document.querySelectorAll('.tab-panel').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        // Hide results
        hideResults();
    });
});

// Setup default buttons when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupDefaultSettingButtons);
} else {
    setupDefaultSettingButtons();
}

// File upload handling
const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const fileInfo = document.getElementById('file-info');
const fileNameSpan = fileInfo.querySelector('.file-name');
const removeFileBtn = document.getElementById('remove-file-btn');
const createFromFileBtn = document.getElementById('create-from-file-btn');

uploadArea.addEventListener('click', () => {
    fileInput.click();
});

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    fileNameSpan.textContent = file.name;
    fileInfo.style.display = 'flex';
    createFromFileBtn.disabled = false;
}

removeFileBtn.addEventListener('click', () => {
    fileInput.value = '';
    fileInfo.style.display = 'none';
    createFromFileBtn.disabled = true;
});

// Create form from text
document.getElementById('create-from-text-btn').addEventListener('click', async () => {
    const text = document.getElementById('text-input').value.trim();
    
    if (!text) {
        showError('Please enter some text describing your form requirements.');
        return;
    }
    
    await createForm('text', { text });
});

// Create form from file
document.getElementById('create-from-file-btn').addEventListener('click', async () => {
    if (!fileInput.files.length) {
        showError('Please select a file to upload.');
        return;
    }
    
    await createForm('file', null, fileInput.files[0]);
});

// Create form from Google Docs link
const createFromDocsBtn = document.getElementById('create-from-docs-btn');
if (createFromDocsBtn) {
    createFromDocsBtn.addEventListener('click', async () => {
        const docsUrl = document.getElementById('docs-url-input').value.trim();
        
        if (!docsUrl) {
            showError('Please enter a Google Docs URL.');
            return;
        }
        
        if (!docsUrl.includes('docs.google.com') && !docsUrl.match(/^[a-zA-Z0-9-_]+$/)) {
            showError('Please enter a valid Google Docs URL.');
            return;
        }
        
        await createForm('docs', { url: docsUrl });
    });
} else {
    console.warn('create-from-docs-btn not found');
}

// Script upload handling
const scriptUploadArea = document.getElementById('script-upload-area');
const scriptFileInput = document.getElementById('script-file-input');
const scriptTextInput = document.getElementById('script-text-input');
const createFromScriptBtn = document.getElementById('create-from-script-btn');

if (scriptUploadArea && scriptFileInput) {
    scriptUploadArea.addEventListener('click', () => {
        scriptFileInput.click();
    });
    
    scriptUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        scriptUploadArea.classList.add('dragover');
    });
    
    scriptUploadArea.addEventListener('dragleave', () => {
        scriptUploadArea.classList.remove('dragover');
    });
    
    scriptUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        scriptUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            const fileName = file.name.toLowerCase();
            if (fileName.endsWith('.json') || fileName.endsWith('.gs') || fileName.endsWith('.js') || file.type === 'application/json' || file.type === 'text/javascript' || file.type === 'application/javascript') {
                handleScriptFileSelect(file);
            } else {
                showError('Please upload a .gs, .js, or .json file.');
            }
        }
    });
}

if (scriptFileInput) {
    scriptFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleScriptFileSelect(e.target.files[0]);
        }
    });
}

async function handleScriptFileSelect(file) {
    try {
        const text = await file.text();
        scriptTextInput.value = text;
        console.log('✅ Script file loaded');
    } catch (error) {
        showError(`Error reading file: ${error.message}`);
    }
}

// Create form from script
if (createFromScriptBtn) {
    createFromScriptBtn.addEventListener('click', async () => {
        const scriptText = scriptTextInput.value.trim();
        
        if (!scriptText) {
            showError('Please upload a JSON file or paste the script.');
            return;
        }
        
        try {
            // Try to parse as JSON first
            let scriptData = null;
            try {
                scriptData = JSON.parse(scriptText);
            } catch (jsonError) {
                // Not JSON, treat as Google Apps Script
                scriptData = null;
            }
            
            // Send to backend for parsing
            await createForm('script', { 
                script_code: scriptText,  // Send raw script code
                script: scriptData,  // Send parsed JSON if available
                default_required: window.defaultRequiredSetting !== false
            });
        } catch (error) {
            showError(`Error processing script: ${error.message}`);
        }
    });
}

async function createForm(method, data = null, file = null) {
    hideResults();
    
    const btn = method === 'text' 
        ? document.getElementById('create-from-text-btn')
        : method === 'file'
        ? document.getElementById('create-from-file-btn')
        : method === 'docs'
        ? document.getElementById('create-from-docs-btn')
        : document.getElementById('create-from-script-btn');
    
    const btnText = btn.querySelector('.btn-label');
    const btnLoader = btn.querySelector('.btn-loader');
    
    // Show log console
    const logConsole = method === 'text' 
        ? document.getElementById('log-console-text')
        : method === 'file'
        ? document.getElementById('log-console-file')
        : method === 'docs'
        ? document.getElementById('log-console-docs')
        : document.getElementById('log-console-script');
    const logContent = method === 'text'
        ? document.getElementById('log-content-text')
        : method === 'file'
        ? document.getElementById('log-content-file')
        : method === 'docs'
        ? document.getElementById('log-content-docs')
        : document.getElementById('log-content-script');
    
    logConsole.style.display = 'block';
    logContent.innerHTML = '';
    
    btn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
    
    // Add initial log
    addLogEntry(logContent, 'info', '⏳ Starting form generation...');
    
    try {
        let response;
        
        if (method === 'text') {
            response = await fetch('/api/create-from-text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        } else if (method === 'file') {
            const formData = new FormData();
            formData.append('file', file);
            
            response = await fetch('/api/create-from-file', {
                method: 'POST',
                body: formData
            });
        } else if (method === 'docs') {
            response = await fetch('/api/create-from-docs', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        } else if (method === 'script') {
            response = await fetch('/api/create-from-script', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });
        }
        
        // Check if response is OK (status 200-299)
        if (!response.ok) {
            // Try to parse error response as JSON
            let errorData;
            try {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    errorData = await response.json();
                } else {
                    // If not JSON, read as text (might be HTML error page)
                    const errorText = await response.text();
                    console.error('Non-JSON error response:', errorText.substring(0, 200));
                    errorData = {
                        success: false,
                        error: `Server error (${response.status}): ${response.statusText}`,
                        message: 'The server returned an error. Please check the server logs.'
                    };
                }
            } catch (parseError) {
                // If parsing fails, create error object
                errorData = {
                    success: false,
                    error: `Server error (${response.status}): ${response.statusText}`,
                    message: 'Unable to parse server response. Please check your connection.'
                };
            }
            
            addLogEntry(logContent, 'error', `❌ Error: ${errorData.error || errorData.message || 'Unknown error'}`);
            showError(errorData.error || errorData.message || 'Failed to create form. Please try again.');
            return;
        }
        
        // Parse JSON response
        let result;
        try {
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Non-JSON response received:', text.substring(0, 200));
                addLogEntry(logContent, 'error', '❌ Server returned non-JSON response');
                showError('Server returned an unexpected response format. Please try again.');
                return;
            }
            result = await response.json();
        } catch (jsonError) {
            console.error('JSON parse error:', jsonError);
            addLogEntry(logContent, 'error', `❌ Error parsing response: ${jsonError.message}`);
            showError('Error parsing server response. Please try again.');
            return;
        }
        
        // Display logs
        if (result.logs && result.logs.length > 0) {
            result.logs.forEach(log => {
                addLogEntry(logContent, log.type, log.message, log.timestamp);
            });
        }
        
        if (result.success) {
            // For script method, show success directly (no preview needed)
            if (method === 'script') {
                if (result.form_url) {
                    showSuccess(result.form_url, result.form_url.replace('/viewform', '/edit'));
                } else {
                    showError('Form URL not received. Please try again.');
                }
            } else if (result.form_structure) {
                // Store form structure for preview
                window.formStructure = result.form_structure;
                console.log('Form structure received:', result.form_structure);
                showQuestionPreview(result.form_structure);
            } else {
                // Fallback: if no preview, show success directly
                console.warn('No form_structure in response, showing success directly');
                if (result.form_url) {
                    showSuccess(result.form_url, result.form_url.replace('/viewform', '/edit'));
                } else {
                    showError('Form structure not received. Please try again.');
                }
            }
        } else {
            showError(result.error || 'Failed to create form. Please try again.');
        }
    } catch (error) {
        addLogEntry(logContent, 'error', `❌ Error: ${error.message}`);
        showError(`Error: ${error.message}. Please check your connection and try again.`);
    } finally {
        btn.disabled = false;
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
    }
}

function addLogEntry(container, type, message, timestamp = null) {
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    
    const time = timestamp || new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    
    const icon = type === 'error' ? '❌' : 
                 type === 'success' ? '✅' : 
                 type === 'warning' ? '⚠️' : 'ℹ️';
    
    entry.innerHTML = `
        <span class="timestamp">[${time}]</span>
        <span class="icon">${icon}</span>
        <span class="message">${escapeHtml(message)}</span>
    `;
    
    container.appendChild(entry);
    
    // Auto scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showSuccess(formUrl, editUrl) {
    document.getElementById('form-url').href = formUrl;
    document.getElementById('form-edit-url').href = editUrl;
    document.getElementById('result-section').style.display = 'block';
    document.getElementById('error-section').style.display = 'none';
    
    // Scroll to result
    document.getElementById('result-section').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showError(message) {
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-section').style.display = 'block';
    document.getElementById('result-section').style.display = 'none';
    
    // Scroll to error
    document.getElementById('error-section').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showQuestionPreview(formStructure) {
    // Hide other sections first
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
    
    console.log('=== showQuestionPreview called ===');
    console.log('Form structure:', formStructure);
    
    const previewSection = document.getElementById('question-preview-section');
    const questionsList = document.getElementById('questions-list');
    
    if (!previewSection) {
        console.error('❌ Preview section not found in DOM!');
        alert('Preview section not found. Please refresh the page.');
        return;
    }
    
    if (!questionsList) {
        console.error('❌ Questions list not found in DOM!');
        alert('Questions list not found. Please refresh the page.');
        return;
    }
    
    console.log('✅ Preview section and questions list found');
    
    // Clear previous content
    questionsList.innerHTML = '';
    
    // Get questions
    const questions = formStructure && formStructure.questions ? formStructure.questions : [];
    
    console.log(`📋 Found ${questions.length} questions to display`);
    console.log('Questions:', questions);
    
    if (questions.length === 0) {
        questionsList.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 40px; background: var(--bg-color); border-radius: 12px;"><p>⚠️ No questions found in the form structure.</p><p style="font-size: 0.9rem; margin-top: 8px;">Please check the console for details.</p></div>';
        previewSection.style.display = 'block';
        previewSection.style.visibility = 'visible';
        return;
    }
    
    questions.forEach((question, index) => {
        console.log(`Creating question ${index + 1}:`, question);
        
        const questionItem = document.createElement('div');
        questionItem.className = 'question-item';
        questionItem.dataset.index = index;
        
        // Handle required field - use global default setting if not specified
        const required = question.hasOwnProperty('required') ? Boolean(question.required) : (window.defaultRequiredSetting !== false);
        
        const questionText = escapeHtml(question.text || 'Untitled question');
        const questionType = escapeHtml(question.type || 'text');
        
        questionItem.innerHTML = `
            <div style="display: flex !important; align-items: center !important; gap: 16px; width: 100%; min-height: 60px;">
                <div style="flex: 1; display: flex; align-items: flex-start; gap: 12px; min-width: 0;">
                    <div class="question-number">${index + 1}</div>
                    <div style="flex: 1; min-width: 0;">
                        <div class="question-text">${questionText}</div>
                        <div class="question-meta">
                            <span class="question-type">${questionType}</span>
                            <span class="${required ? 'required-badge' : 'optional-badge'}" id="badge-${index}">
                                ${required ? 'Required' : 'Optional'}
                            </span>
                        </div>
                    </div>
                </div>
                <div id="toggle-wrapper-${index}" style="display: flex !important; visibility: visible !important; opacity: 1 !important; align-items: center; gap: 8px; padding: 10px 14px; background: #f1f5f9 !important; border-radius: 8px; border: 2px solid #cbd5e1 !important; white-space: nowrap; flex-shrink: 0; z-index: 10; min-width: 150px; position: relative;">
                    <span style="font-size: 0.9rem; font-weight: 600; color: #475569; display: inline-block !important;">Required:</span>
                    <label class="toggle-switch" style="display: inline-block !important; visibility: visible !important; opacity: 1 !important; position: relative; width: 56px !important; height: 30px !important; cursor: pointer; margin: 0 !important;">
                        <input type="checkbox" class="required-toggle" data-index="${index}" ${required ? 'checked' : ''} style="opacity: 0; width: 0; height: 0; position: absolute; z-index: 1;">
                        <span class="toggle-slider" style="position: absolute !important; cursor: pointer !important; top: 0 !important; left: 0 !important; right: 0 !important; bottom: 0 !important; background-color: ${required ? '#10b981' : '#cbd5e1'} !important; transition: 0.3s; border-radius: 30px !important; display: block !important; visibility: visible !important; opacity: 1 !important; width: 56px !important; height: 30px !important;">
                            <span style="position: absolute !important; height: 24px !important; width: 24px !important; left: ${required ? '26px' : '3px'} !important; bottom: 3px !important; background-color: white !important; transition: 0.3s; border-radius: 50% !important; box-shadow: 0 2px 6px rgba(0,0,0,0.3) !important; display: block !important; visibility: visible !important;"></span>
                        </span>
                    </label>
                </div>
            </div>
        `;
        
        questionsList.appendChild(questionItem);
        console.log(`✅ Question ${index + 1} added to DOM`);
        
        // Verify toggle exists and is visible after adding
        const toggleWrapper = questionItem.querySelector(`#toggle-wrapper-${index}`);
        const toggle = questionItem.querySelector('.required-toggle');
        const toggleSwitch = questionItem.querySelector('.toggle-switch');
        const toggleSlider = questionItem.querySelector('.toggle-slider');
        
        if (!toggleWrapper) {
            console.error(`❌ Toggle wrapper not found for question ${index + 1}`);
        } else {
            const computedStyle = window.getComputedStyle(toggleWrapper);
            console.log(`✅ Toggle wrapper found for question ${index + 1}:`, {
                display: computedStyle.display,
                visibility: computedStyle.visibility,
                opacity: computedStyle.opacity,
                width: computedStyle.width,
                height: computedStyle.height
            });
            // Force visible
            toggleWrapper.style.display = 'flex';
            toggleWrapper.style.visibility = 'visible';
            toggleWrapper.style.opacity = '1';
        }
        
        if (!toggle) {
            console.error(`❌ Toggle checkbox not found for question ${index + 1}`);
        } else {
            console.log(`✅ Toggle checkbox found for question ${index + 1}, checked: ${toggle.checked}`);
        }
        
        if (!toggleSwitch) {
            console.error(`❌ Toggle switch element not found for question ${index + 1}`);
        } else {
            toggleSwitch.style.display = 'inline-block';
            toggleSwitch.style.visibility = 'visible';
        }
        
        if (!toggleSlider) {
            console.error(`❌ Toggle slider not found for question ${index + 1}`);
        } else {
            toggleSlider.style.display = 'block';
            toggleSlider.style.visibility = 'visible';
        }
    });
    
    // Add event listeners to toggles after they're added to DOM
    setTimeout(() => {
        const toggles = document.querySelectorAll('.required-toggle');
        console.log(`Found ${toggles.length} toggles to setup listeners`);
        
        toggles.forEach((toggle, toggleIndex) => {
            toggle.addEventListener('change', (e) => {
                const index = parseInt(e.target.dataset.index);
                const badge = document.getElementById(`badge-${index}`);
                const isRequired = e.target.checked;
                
                // Update toggle slider visual
                const slider = toggle.nextElementSibling;
                if (slider) {
                    slider.style.backgroundColor = isRequired ? '#10b981' : '#cbd5e1';
                    slider.style.display = 'block';
                    slider.style.visibility = 'visible';
                    const sliderCircle = slider.querySelector('span');
                    if (sliderCircle) {
                        sliderCircle.style.left = isRequired ? '26px' : '3px';
                        sliderCircle.style.display = 'block';
                    }
                }
                
                // Also update the wrapper to ensure visibility
                const wrapper = document.getElementById(`toggle-wrapper-${index}`);
                if (wrapper) {
                    wrapper.style.display = 'flex';
                    wrapper.style.visibility = 'visible';
                    wrapper.style.opacity = '1';
                }
                
                if (badge) {
                    if (isRequired) {
                        badge.className = 'required-badge';
                        badge.textContent = 'Required';
                    } else {
                        badge.className = 'optional-badge';
                        badge.textContent = 'Optional';
                    }
                }
                
                // Update form structure
                if (window.formStructure && window.formStructure.questions && window.formStructure.questions[index]) {
                    window.formStructure.questions[index].required = isRequired;
                    console.log(`✅ Question ${index + 1} set to ${isRequired ? 'required' : 'optional'}`);
                }
            });
        });
        
        console.log(`✅ All ${toggles.length} toggle listeners setup complete`);
    }, 100);
    
    // Show preview section - use multiple methods to ensure it's visible
    previewSection.style.display = 'block';
    previewSection.style.visibility = 'visible';
    previewSection.style.opacity = '1';
    previewSection.style.height = 'auto';
    previewSection.style.overflow = 'visible';
    
    // Remove any inline display:none
    previewSection.removeAttribute('style');
    previewSection.style.display = 'block';
    
    // Force a reflow to ensure display
    void previewSection.offsetHeight;
    
    console.log(`✅ Preview displayed with ${questions.length} questions`);
    console.log('Preview section:', previewSection);
    console.log('Preview section display style:', window.getComputedStyle(previewSection).display);
    console.log('Preview section visible:', previewSection.offsetHeight > 0);
    
    // Scroll to preview
    setTimeout(() => {
        previewSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);
    
    // Add a visual indicator
    if (questions.length > 0) {
        console.log(`🎯 SUCCESS: Preview should be visible with ${questions.length} questions and toggles!`);
    }
    
    // Setup bulk action buttons now that preview section is visible
    // Use setTimeout to ensure DOM is fully updated
    setTimeout(() => {
        setupBulkActionButtons();
        setupCreateFormButton();
        setupBackToEditButton();
    }, 50);
}

// Setup bulk action buttons - wait for DOM to be ready
function setupBulkActionButtons() {
    // Query from preview section to ensure they exist
    const previewSection = document.getElementById('question-preview-section');
    if (!previewSection) {
        console.warn('Preview section not found, cannot setup bulk action buttons');
        return;
    }
    
    const selectAllRequiredBtn = previewSection.querySelector('#select-all-required-btn') || document.getElementById('select-all-required-btn');
    const selectAllOptionalBtn = previewSection.querySelector('#select-all-optional-btn') || document.getElementById('select-all-optional-btn');
    const testToggleBtn = previewSection.querySelector('#test-toggle-visibility-btn') || document.getElementById('test-toggle-visibility-btn');
    
    if (selectAllRequiredBtn && !selectAllRequiredBtn.dataset.listenerAdded) {
        selectAllRequiredBtn.dataset.listenerAdded = 'true';
        selectAllRequiredBtn.addEventListener('click', () => {
            console.log('Setting all questions to Required');
            document.querySelectorAll('.required-toggle').forEach(toggle => {
                if (!toggle.checked) {
                    toggle.checked = true;
                    // Trigger change event to update visuals
                    const changeEvent = new Event('change', { bubbles: true });
                    toggle.dispatchEvent(changeEvent);
                }
            });
            console.log('✅ All questions set to Required');
        });
        console.log('✅ select-all-required-btn setup complete');
    } else if (!selectAllRequiredBtn) {
        console.warn('⚠️ select-all-required-btn not found');
    }
    
    if (selectAllOptionalBtn && !selectAllOptionalBtn.dataset.listenerAdded) {
        selectAllOptionalBtn.dataset.listenerAdded = 'true';
        selectAllOptionalBtn.addEventListener('click', () => {
            console.log('Setting all questions to Optional');
            document.querySelectorAll('.required-toggle').forEach(toggle => {
                if (toggle.checked) {
                    toggle.checked = false;
                    // Trigger change event to update visuals
                    const changeEvent = new Event('change', { bubbles: true });
                    toggle.dispatchEvent(changeEvent);
                }
            });
            console.log('✅ All questions set to Optional');
        });
        console.log('✅ select-all-optional-btn setup complete');
    } else if (!selectAllOptionalBtn) {
        console.warn('⚠️ select-all-optional-btn not found');
    }
    
    if (testToggleBtn && !testToggleBtn.dataset.listenerAdded) {
        testToggleBtn.dataset.listenerAdded = 'true';
        testToggleBtn.addEventListener('click', () => {
    console.log('=== TOGGLE VISIBILITY DEBUG ===');
    const toggles = document.querySelectorAll('.required-toggle');
    const toggleSwitches = document.querySelectorAll('.toggle-switch');
    const toggleContainers = document.querySelectorAll('.toggle-container');
    
    console.log(`Found ${toggles.length} toggles`);
    console.log(`Found ${toggleSwitches.length} toggle switches`);
    console.log(`Found ${toggleContainers.length} toggle containers`);
    
    toggleContainers.forEach((container, index) => {
        const computedStyle = window.getComputedStyle(container);
        console.log(`Container ${index + 1}:`, {
            display: computedStyle.display,
            visibility: computedStyle.visibility,
            opacity: computedStyle.opacity,
            width: computedStyle.width,
            height: computedStyle.height,
            position: computedStyle.position
        });
        
        // Force show
        container.style.display = 'flex';
        container.style.visibility = 'visible';
        container.style.opacity = '1';
    });
    
    toggleSwitches.forEach((toggleSwitch, index) => {
        const computedStyle = window.getComputedStyle(toggleSwitch);
        console.log(`Toggle Switch ${index + 1}:`, {
            display: computedStyle.display,
            visibility: computedStyle.visibility,
            opacity: computedStyle.opacity,
            width: computedStyle.width,
            height: computedStyle.height
        });
        
        // Force show
        toggleSwitch.style.display = 'inline-block';
        toggleSwitch.style.visibility = 'visible';
        toggleSwitch.style.opacity = '1';
    });
    
    alert(`Debug complete! Check console.\nFound ${toggles.length} toggles, ${toggleSwitches.length} switches, ${toggleContainers.length} containers.`);
        });
        console.log('✅ test-toggle-visibility-btn setup complete');
    } else if (!testToggleBtn) {
        console.warn('test-toggle-visibility-btn not found');
    }
}

// Initial setup attempt (buttons may not exist until preview is shown)
// They will be set up again when preview is displayed

// Create form button (after preview) - setup with null check
function setupCreateFormButton() {
    const createFormBtn = document.getElementById('create-form-btn');
    if (createFormBtn && !createFormBtn.dataset.listenerAdded) {
        createFormBtn.dataset.listenerAdded = 'true';
        createFormBtn.addEventListener('click', async () => {
            if (!window.formStructure) {
                showError('Form structure not found. Please try again.');
                return;
            }
            
            const btn = document.getElementById('create-form-btn');
            const btnText = btn.querySelector('.btn-label');
            const btnLoader = btn.querySelector('.btn-loader');
            const logConsole = document.getElementById('log-console-text');
            const logContent = document.getElementById('log-content-text');
            
            // Show log console if not already visible
            if (logConsole) {
                logConsole.style.display = 'block';
                if (logContent) {
                    logContent.innerHTML = '';
                    addLogEntry(logContent, 'info', '⏳ Creating form with your settings...');
                }
            }
            
            btn.disabled = true;
            btnText.style.display = 'none';
            btnLoader.style.display = 'inline';
            
            try {
                const response = await fetch('/api/create-form-with-questions', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        form_structure: window.formStructure
                    })
                });
                
                // Check if response is OK
                if (!response.ok) {
                    let errorData;
                    try {
                        const contentType = response.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            errorData = await response.json();
                        } else {
                            const errorText = await response.text();
                            console.error('Non-JSON error response:', errorText.substring(0, 200));
                            errorData = {
                                success: false,
                                error: `Server error (${response.status}): ${response.statusText}`
                            };
                        }
                    } catch (parseError) {
                        errorData = {
                            success: false,
                            error: `Server error (${response.status}): ${response.statusText}`
                        };
                    }
                    if (logContent) {
                        addLogEntry(logContent, 'error', `❌ Error: ${errorData.error || errorData.message || 'Unknown error'}`);
                    }
                    showError(errorData.error || errorData.message || 'Failed to create form. Please try again.');
                    return;
                }
                
                // Parse JSON response
                let result;
                try {
                    const contentType = response.headers.get('content-type');
                    if (!contentType || !contentType.includes('application/json')) {
                        const text = await response.text();
                        console.error('Non-JSON response received:', text.substring(0, 200));
                        if (logContent) {
                            addLogEntry(logContent, 'error', '❌ Server returned non-JSON response');
                        }
                        showError('Server returned an unexpected response format. Please try again.');
                        return;
                    }
                    result = await response.json();
                } catch (jsonError) {
                    console.error('JSON parse error:', jsonError);
                    if (logContent) {
                        addLogEntry(logContent, 'error', `❌ Error parsing response: ${jsonError.message}`);
                    }
                    showError('Error parsing server response. Please try again.');
                    return;
                }
                
                // Display logs
                if (result.logs && result.logs.length > 0 && logContent) {
                    result.logs.forEach(log => {
                        addLogEntry(logContent, log.type, log.message, log.timestamp);
                    });
                }
                
                if (result.success) {
                    document.getElementById('question-preview-section').style.display = 'none';
                    showSuccess(result.form_url, result.form_url.replace('/viewform', '/edit'));
                } else {
                    showError(result.error || 'Failed to create form. Please try again.');
                }
            } catch (error) {
                if (logContent) {
                    addLogEntry(logContent, 'error', `❌ Error: ${error.message}`);
                }
                showError(`Error: ${error.message}. Please check your connection and try again.`);
            } finally {
                btn.disabled = false;
                btnText.style.display = 'inline';
                btnLoader.style.display = 'none';
            }
        });
    }
}

// Back to edit button - setup with null check
function setupBackToEditButton() {
    const backBtn = document.getElementById('back-to-edit-btn');
    if (backBtn && !backBtn.dataset.listenerAdded) {
        backBtn.dataset.listenerAdded = 'true';
        backBtn.addEventListener('click', () => {
            document.getElementById('question-preview-section').style.display = 'none';
            window.formStructure = null;
        });
    }
}

// Setup buttons when preview is shown
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            setupBulkActionButtons();
            setupCreateFormButton();
            setupBackToEditButton();
        }, 100);
    });
} else {
    setTimeout(() => {
        setupBulkActionButtons();
        setupCreateFormButton();
        setupBackToEditButton();
    }, 100);
}

function hideResults() {
    const resultSection = document.getElementById('result-section');
    const errorSection = document.getElementById('error-section');
    const previewSection = document.getElementById('question-preview-section');
    
    if (resultSection) resultSection.style.display = 'none';
    if (errorSection) errorSection.style.display = 'none';
    // Don't hide preview here - let showQuestionPreview handle it
}

// Create another button
document.getElementById('create-another-btn').addEventListener('click', () => {
    hideResults();
    document.getElementById('text-input').value = '';
    fileInput.value = '';
    fileInfo.style.display = 'none';
    createFromFileBtn.disabled = true;
    
    // Hide log consoles
    document.getElementById('log-console-text').style.display = 'none';
    document.getElementById('log-console-file').style.display = 'none';
    document.getElementById('log-console-docs').style.display = 'none';
    document.getElementById('log-console-script').style.display = 'none';
    document.getElementById('log-content-text').innerHTML = '';
    document.getElementById('log-content-file').innerHTML = '';
    document.getElementById('log-content-docs').innerHTML = '';
    document.getElementById('log-content-script').innerHTML = '';
    
    // Clear inputs
    document.getElementById('docs-url-input').value = '';
    document.getElementById('script-text-input').value = '';
    if (document.getElementById('script-file-input')) {
        document.getElementById('script-file-input').value = '';
    }
    
    document.getElementById('text-tab').classList.add('active');
    document.getElementById('file-tab').classList.remove('active');
    document.querySelectorAll('.tab')[0].classList.add('active');
    document.querySelectorAll('.tab')[1].classList.remove('active');
});

// Try again button
document.getElementById('try-again-btn').addEventListener('click', () => {
    hideResults();
});

// Authentication functions
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        if (data.authenticated) {
            // Update UI if user is logged in
            updateAuthUI(data.user_email);
        }
    } catch (error) {
        console.error('Error checking auth status:', error);
    }
}

function updateAuthUI(userEmail) {
    const authSection = document.getElementById('auth-section');
    if (!authSection) return;
    
    // Update user email display
    const userEmailElement = authSection.querySelector('.user-email');
    if (userEmailElement && userEmail) {
        userEmailElement.textContent = userEmail;
    }
    
    // Show auth info if user is logged in
    if (userEmail) {
        const authInfo = authSection.querySelector('.auth-info');
        if (!authInfo) {
            // Create auth info div if it doesn't exist
            const newAuthInfo = document.createElement('div');
            newAuthInfo.className = 'auth-info';
            newAuthInfo.innerHTML = `
                <span class="user-email">${userEmail}</span>
                <button class="btn-auth btn-logout" onclick="logout()">Logout</button>
            `;
            authSection.innerHTML = '';
            authSection.appendChild(newAuthInfo);
        }
    }
}

async function logout() {
    try {
        const response = await fetch('/auth/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            // Reload page to update UI
            window.location.reload();
        } else {
            // If POST fails, try GET redirect
            window.location.href = '/auth/logout';
        }
    } catch (error) {
        console.error('Error logging out:', error);
        // Fallback to GET redirect
        window.location.href = '/auth/logout';
    }
}

// Check auth status and credentials on page load
document.addEventListener('DOMContentLoaded', async () => {
    checkAuthStatus();
    
    // Also check credentials configuration
    try {
        const response = await fetch('/api/check-credentials');
        const data = await response.json();
        
        if (data.status === 'missing') {
            console.warn('⚠️ Credentials not configured:', data.message);
            // Optionally show a notification to the user
            const authSection = document.getElementById('auth-section');
            if (authSection && !authSection.querySelector('.credentials-warning')) {
                const warning = document.createElement('div');
                warning.className = 'credentials-warning';
                warning.style.cssText = 'padding: 0.75rem; background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; margin-top: 0.5rem; font-size: 0.875rem; color: #92400e;';
                warning.innerHTML = '⚠️ OAuth credentials not configured. Please set environment variables in Render Dashboard.';
                authSection.appendChild(warning);
            }
        }
    } catch (error) {
        console.error('Error checking credentials:', error);
    }
});


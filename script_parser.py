"""
Google Apps Script Parser
Parses Google Apps Script code to extract form structure.
"""

import re
from typing import Dict, List, Any, Optional


class ScriptParser:
    """Parser for Google Apps Script form creation code."""
    
    def __init__(self):
        self.form_title = None
        self.form_description = None
        self.questions = []
        self.current_section = None
        
    def parse_script(self, script_code: str) -> Dict[str, Any]:
        """
        Parse Google Apps Script code and extract form structure.
        
        Args:
            script_code: Google Apps Script code as string
        
        Returns:
            Dictionary containing form structure
        """
        # Remove comments
        script_code = self._remove_comments(script_code)
        
        # Extract form title
        self.form_title = self._extract_form_title(script_code)
        
        # Extract form description
        self.form_description = self._extract_form_description(script_code)
        
        # Extract questions
        self.questions = self._extract_questions(script_code)
        
        return {
            'title': self.form_title or 'Form from Script',
            'description': self.form_description or '',
            'questions': self.questions
        }
    
    def _remove_comments(self, code: str) -> str:
        """Remove JavaScript comments from code."""
        # Remove single-line comments
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code
    
    def _extract_form_title(self, code: str) -> Optional[str]:
        """Extract form title from FormApp.create() call."""
        # Match: FormApp.create('Title') or FormApp.create("Title")
        # Escape quotes properly in regex
        match = re.search(r'FormApp\.create\(["\'](.*?)["\']\)', code)
        if match:
            return match.group(1)
        return None
    
    def _extract_form_description(self, code: str) -> Optional[str]:
        """Extract form description from setDescription() call."""
        # Match: form.setDescription('Description') - handle both single and double quotes
        # Also handle multi-line strings
        match = re.search(r'\.setDescription\(["\'](.*?)["\']\)', code, re.DOTALL)
        if match:
            desc = match.group(1)
            # Clean up escaped characters
            desc = desc.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            return desc.strip()
        return None
    
    def _extract_questions(self, code: str) -> List[Dict[str, Any]]:
        """Extract all questions from the script."""
        questions = []
        
        # Find all question blocks
        # Each question starts with form.add*Item() and may have chained methods
        question_blocks = self._extract_question_blocks(code)
        
        for block in question_blocks:
            question = self._parse_question_block(block)
            if question and question.get('text'):  # Only add if question has text
                questions.append(question)
        
        return questions
    
    def _extract_question_blocks(self, code: str) -> List[str]:
        """Extract individual question blocks from code."""
        blocks = []
        
        # Pattern to match: form.add*Item() followed by method chains
        # Handle both single-line and multi-line method chains
        # Match: form.add*Item()...setTitle()...setRequired()... (up to next statement)
        pattern = r'form\.(add\w+Item\(\)(?:\s*\.[^;]*)*)'
        
        matches = re.finditer(pattern, code, re.DOTALL)
        for match in matches:
            block = match.group(0)
            # Extend to include all chained methods until semicolon or new form.add
            # Find the end of the statement
            start_pos = match.end()
            # Look for semicolon or next form.add
            end_match = re.search(r'[;]|form\.add', code[start_pos:])
            if end_match:
                end_pos = start_pos + end_match.start()
                block = code[match.start():end_pos]
            blocks.append(block)
        
        return blocks
    
    def _parse_question_block(self, block: str) -> Optional[Dict[str, Any]]:
        """Parse a single question block."""
        question = {
            'text': '',
            'type': 'text',
            'required': False,
            'options': [],
            'help_text': ''
        }
        
        # Determine question type
        if 'addTextItem()' in block:
            question['type'] = 'text'
        elif 'addMultipleChoiceItem()' in block:
            question['type'] = 'choice'
        elif 'addListItem()' in block:
            question['type'] = 'dropdown'
        elif 'addCheckboxItem()' in block:
            question['type'] = 'checkbox'
        elif 'addScaleItem()' in block or 'addLinearScaleItem()' in block:
            question['type'] = 'linear_scale'
        elif 'addPageBreakItem()' in block or 'addSectionHeaderItem()' in block:
            # Skip page breaks and section headers - they're not questions
            return None
        else:
            return None
        
        # Extract title - handle escaped quotes and newlines
        title_match = re.search(r'\.setTitle\(["\'](.*?)["\']\)', block, re.DOTALL)
        if title_match:
            title_text = title_match.group(1)
            # Unescape common escape sequences
            title_text = title_text.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            question['text'] = title_text.strip()
        
        # Extract required status - default to False if not specified
        required_match = re.search(r'\.setRequired\((true|false)\)', block)
        if required_match:
            question['required'] = required_match.group(1).lower() == 'true'
        else:
            # If not explicitly set, default to False (optional)
            question['required'] = False
        
        # Extract help text
        help_match = re.search(r'\.setHelpText\(["\'](.*?)["\']\)', block, re.DOTALL)
        if help_match:
            help_text = help_match.group(1)
            # Unescape
            help_text = help_text.replace('\\n', '\n').replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
            question['help_text'] = help_text.strip()
        
        # Extract options (for choice/dropdown/checkbox)
        if question['type'] in ['choice', 'dropdown', 'checkbox']:
            options = self._extract_options(block)
            question['options'] = options
        
        # Extract scale parameters
        if question['type'] == 'linear_scale':
            scale_params = self._extract_scale_params(block)
            question.update(scale_params)
        
        return question
    
    def _extract_options(self, block: str) -> List[str]:
        """Extract options from setChoiceValues() call."""
        options = []
        
        # Match: .setChoiceValues(['Option 1', 'Option 2', ...])
        # Handle both single and multi-line arrays
        match = re.search(r'\.setChoiceValues\(\s*\[(.*?)\]\s*\)', block, re.DOTALL)
        if match:
            options_str = match.group(1)
            # Extract individual string values - handle escaped quotes
            # Match strings that may contain escaped quotes - use proper escaping
            option_pattern = r'["\'](?:(?:\\.)|[^"\'])*?["\']'
            option_matches = re.findall(option_pattern, options_str)
            for opt in option_matches:
                # Remove quotes and unescape
                opt = opt.strip("'\"")
                opt = opt.replace("\\'", "'").replace('\\"', '"').replace('\\n', '\n')
                options.append(opt)
        
        return options
    
    def _extract_scale_params(self, block: str) -> Dict[str, Any]:
        """Extract linear scale parameters."""
        params = {
            'min': 1,
            'max': 5,
            'min_label': '',
            'max_label': ''
        }
        
        # Extract min value
        min_match = re.search(r'\.setBounds\((\d+),\s*(\d+)\)', block)
        if min_match:
            params['min'] = int(min_match.group(1))
            params['max'] = int(min_match.group(2))
        
        # Extract labels (if any)
        min_label_match = re.search(r'\.setLabels\(["\'](.*?)["\']\s*,\s*["\'](.*?)["\']\)', block)
        if min_label_match:
            params['min_label'] = min_label_match.group(1)
            params['max_label'] = min_label_match.group(2)
        
        return params


def parse_script(script_code: str) -> Dict[str, Any]:
    """
    Parse script code (Google Apps Script or JSON) and return form structure.
    
    Args:
        script_code: Script code as string (JavaScript or JSON)
    
    Returns:
        Dictionary containing form structure
    """
    # Try to parse as JSON first
    try:
        import json
        data = json.loads(script_code)
        if isinstance(data, dict) and 'questions' in data:
            return data
    except:
        pass
    
    # If not JSON, try to parse as Google Apps Script
    parser = ScriptParser()
    return parser.parse_script(script_code)


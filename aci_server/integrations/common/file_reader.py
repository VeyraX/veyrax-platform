import PyPDF2
import io
import json
from typing import Tuple

def read_file_content(file_content: io.BytesIO, mime_type: str) -> Tuple[str, bool]:
    """
    Read content from various file types and return as text.
    Returns tuple of (content, success)
    """
    try:
        file_content.seek(0)
        
        if mime_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(file_content)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            return text_content.strip(), True

        elif mime_type == 'text/plain':
            return file_content.read().decode('utf-8').strip(), True

        elif mime_type == 'application/json':
            content = json.loads(file_content.read().decode('utf-8'))
            return json.dumps(content, indent=2), True

        elif mime_type == 'text/markdown' or mime_type == 'text/x-markdown':
            return file_content.read().decode('utf-8').strip(), True

        elif mime_type.startswith('text/'): 
            return file_content.read().decode('utf-8').strip(), True

        elif 'google-apps.document' in mime_type: 
            pdf_reader = PyPDF2.PdfReader(file_content)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            return text_content.strip(), True

        elif any(x in mime_type for x in ['spreadsheet', 'excel', 'csv']):
            return "[Spreadsheet files are not supported for text reading]", False

        else:
            return f"[File type {mime_type} is not supported for text extraction]", False

    except Exception as e:
        return f"Error reading file: {str(e)}", False
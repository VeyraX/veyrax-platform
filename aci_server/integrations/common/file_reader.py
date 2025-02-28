import PyPDF2
import io
import json
from typing import Tuple, Union

def read_file_content(file_content: Union[bytes, io.BytesIO], mime_type: str) -> Tuple[str, bool]:
    """
    Read content from various file types and return as text.
    
    Args:
        file_content: File content as bytes or BytesIO object
        mime_type: MIME type of the file
        
    Returns:
        Tuple of (content, success)
    """
    try:
        # Convert bytes to BytesIO if needed
        if isinstance(file_content, bytes):
            file_content = io.BytesIO(file_content)
        
        # Reset file pointer to beginning
        file_content.seek(0)
        
        if mime_type == 'application/pdf':
            pdf_reader = PyPDF2.PdfReader(file_content)
            text_content = ""
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            return text_content.strip(), True

        elif mime_type == 'text/plain':
            return file_content.read().decode('utf-8', errors='replace').strip(), True

        elif mime_type == 'application/json':
            content = json.loads(file_content.read().decode('utf-8', errors='replace'))
            return json.dumps(content, indent=2), True

        elif mime_type in ('text/markdown', 'text/x-markdown'):
            return file_content.read().decode('utf-8', errors='replace').strip(), True

        elif mime_type.startswith('text/'): 
            return file_content.read().decode('utf-8', errors='replace').strip(), True

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

    except UnicodeDecodeError:
        return "[File contains binary data that cannot be decoded as text]", False
    except json.JSONDecodeError:
        # If JSON parsing fails, try to return as plain text
        file_content.seek(0)
        try:
            return file_content.read().decode('utf-8', errors='replace').strip(), True
        except:
            return "[Error parsing file content]", False
    except Exception as e:
        return f"Error reading file: {str(e)}", False
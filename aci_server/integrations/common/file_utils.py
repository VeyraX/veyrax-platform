from typing import Optional, Dict

def get_mime_type_from_extension(filename: str) -> Optional[str]:
    """
    Determine MIME type based on file extension.
    
    Args:
        filename: The name of the file including extension
        
    Returns:
        The MIME type as a string, or None if the extension is not recognized
    """
    if not filename or '.' not in filename:
        return None
        
    extension = filename.split('.')[-1].lower()
    
    # Common file extensions to MIME types mapping
    extension_to_mime = {
        # Documents
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ppt': 'application/vnd.ms-powerpoint',
        'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        'txt': 'text/plain',
        'rtf': 'application/rtf',
        'odt': 'application/vnd.oasis.opendocument.text',
        
        # Images
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'bmp': 'image/bmp',
        'svg': 'image/svg+xml',
        'webp': 'image/webp',
        
        # Audio
        'mp3': 'audio/mpeg',
        'wav': 'audio/wav',
        'ogg': 'audio/ogg',
        'flac': 'audio/flac',
        
        # Video
        'mp4': 'video/mp4',
        'avi': 'video/x-msvideo',
        'mov': 'video/quicktime',
        'wmv': 'video/x-ms-wmv',
        'webm': 'video/webm',
        
        # Archives
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
        'tar': 'application/x-tar',
        'gz': 'application/gzip',
        '7z': 'application/x-7z-compressed',
        
        # Code
        'html': 'text/html',
        'css': 'text/css',
        'js': 'application/javascript',
        'json': 'application/json',
        'xml': 'application/xml',
        'py': 'text/x-python',
        'java': 'text/x-java',
        'c': 'text/x-c',
        'cpp': 'text/x-c++',
        'cs': 'text/x-csharp',
        'php': 'application/x-php',
        'rb': 'text/x-ruby',
        'go': 'text/x-go',
        'ts': 'application/typescript',
        
        # Markdown
        'md': 'text/markdown',
        'markdown': 'text/markdown',
        
        # Other
        'csv': 'text/csv',
        'log': 'text/plain',
        'ini': 'text/plain',
        'yaml': 'application/x-yaml',
        'yml': 'application/x-yaml',
    }
    
    return extension_to_mime.get(extension, 'application/octet-stream') 
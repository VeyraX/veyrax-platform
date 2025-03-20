import os
import secrets
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def encrypt(text: str) -> str:
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY must be set in environment variables")
    
    key = bytes.fromhex(encryption_key)
    
    iv = secrets.token_bytes(16)
    
    block_size = 16
    padding_length = block_size - (len(text) % block_size)
    padding = bytes([padding_length]) * padding_length
    padded_text = text.encode('utf-8') + padding
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    encrypted = encryptor.update(padded_text) + encryptor.finalize()
    
    return iv.hex() + ':' + encrypted.hex()

def decrypt(encrypted_text: str) -> str:
    encryption_key = os.getenv('ENCRYPTION_KEY')
    
    if not encryption_key:
        raise ValueError("ENCRYPTION_KEY must be set in environment variables")
    
    key = bytes.fromhex(encryption_key)
    
    parts = encrypted_text.split(':')
    if len(parts) != 2:
        raise ValueError("Invalid encrypted text format")
    
    iv = bytes.fromhex(parts[0])
    encrypted_bytes = bytes.fromhex(parts[1])
    
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    
    decrypted = decryptor.update(encrypted_bytes) + decryptor.finalize()
    
    padding_length = decrypted[-1]
    decrypted = decrypted[:-padding_length]
    
    return decrypted.decode('utf-8')

def is_encrypted(text: str) -> bool:
    if not text:
        return False
        
    try:
        parts = text.split(':', 1)
        if len(parts) != 2:
            return False
            
        iv = parts[0]
        if len(iv) != 32 or not all(c in '0123456789abcdef' for c in iv.lower()):
            return False
            
        encrypted = parts[1]
        if not all(c in '0123456789abcdef' for c in encrypted.lower()):
            return False
            
        return True
    except:
        return False

def safe_decrypt(text: str) -> str:
    if not text:
        return text
    if is_encrypted(text):
        try:
            return decrypt(text)
        except:
            return text
    return text

def safe_encrypt(text: str) -> str:
    if not text:
        return text
    if not is_encrypted(text):
        try:
            return encrypt(text)
        except:
            return text
    return text
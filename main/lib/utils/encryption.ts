import crypto from 'crypto';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;

if (!ENCRYPTION_KEY) {
  throw new Error('ENCRYPTION_KEY must be set in environment variables');
}

const key = Buffer.from(ENCRYPTION_KEY, 'hex');

export function encrypt(text: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return iv.toString('hex') + ':' + encrypted;
}

export function decrypt(encryptedText: string): string {
  const parts = encryptedText.split(':');
  if (parts.length !== 2) {
    throw new Error('Invalid encrypted text format');
  }
  const iv = Buffer.from(parts[0], 'hex');
  const encryptedData = parts[1];
  const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
  let decrypted = decipher.update(encryptedData, 'hex', 'utf8');
  decrypted += decipher.final('utf8');
  return decrypted;
}

export function decrypt_with_code(encryptedText: string, code: string): string {
  if (!encryptedText || !code) {
    return '';
  }
  
  try {
    const combinedKey = crypto.createHash('sha256')
      .update(ENCRYPTION_KEY + code)
      .digest('hex');
    
    const keyPart = combinedKey.substring(0, 32);
    const ivPart = combinedKey.substring(32, 64);
    
    const keyBuffer = Buffer.from(keyPart, 'hex');
    const ivBuffer = Buffer.from(ivPart, 'hex');
    
    const decipher = crypto.createDecipheriv('aes-128-cbc', keyBuffer, ivBuffer);
    decipher.setAutoPadding(false);
    
    const encryptedBuffer = Buffer.from(encryptedText, 'hex');
    
    let decrypted = decipher.update(encryptedBuffer);
    decrypted = Buffer.concat([decrypted, decipher.final()]);
    
    const paddingLength = decrypted[decrypted.length - 1];
    
    if (paddingLength <= 0 || paddingLength > 16) {
      console.error('Invalid padding length:', paddingLength);
      return '';
    }
    
    let validPadding = true;
    for (let i = decrypted.length - paddingLength; i < decrypted.length; i++) {
      if (decrypted[i] !== paddingLength) {
        validPadding = false;
        break;
      }
    }
    
    if (!validPadding) {
      return '';
    }
    
    const unpaddedData = decrypted.slice(0, decrypted.length - paddingLength);
    
    return unpaddedData.toString('utf8');
  } catch (error) {
    return '';
  }
}
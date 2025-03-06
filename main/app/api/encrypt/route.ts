import { NextRequest, NextResponse } from 'next/server';
import { encrypt } from '@/lib/utils/encryption';

export async function POST(req: NextRequest) {
  try {
    const { apiKey } = await req.json();
    
    if (!apiKey) {
      return NextResponse.json({ error: 'API key is required' }, { status: 400 });
    }
    
    const encryptedKey = encrypt(apiKey);
    
    return NextResponse.json({ encryptedKey });
  } catch (error) {
    console.error('Error encrypting API key:', error);
    return NextResponse.json({ error: 'Failed to encrypt API key' }, { status: 500 });
  }
}
import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { apiKey } = await request.json();
    
    if (!apiKey) {
      return NextResponse.json(
        { valid: false, error: 'API key is required' },
        { status: 400 }
      );
    }

    const response = await fetch('https://api.openai.com/v1/models', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
    });

    if (response.ok) {
      return NextResponse.json({ valid: true });
    } else {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        { 
          valid: false, 
          error: error.error?.message || `Invalid OpenAI API key (Status: ${response.status})` 
        },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Server error validating OpenAI API key:', error);
    return NextResponse.json(
      { valid: false, error: 'Server error during validation' },
      { status: 500 }
    );
  }
} 
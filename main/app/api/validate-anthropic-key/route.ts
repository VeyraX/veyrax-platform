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

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: 'claude-haiku-5-5',
        max_tokens: 10,
        messages: [
          { role: 'user', content: 'Hello, this is a test message.' }
        ]
      })
    });

    if (response.ok) {
      return NextResponse.json({ valid: true });
    } else {
      const error = await response.json().catch(() => ({}));
      return NextResponse.json(
        { 
          valid: false, 
          error: error.error?.message || `Invalid Anthropic API key (Status: ${response.status})` 
        },
        { status: 400 }
      );
    }
  } catch (error) {
    console.error('Server error validating Anthropic API key:', error);
    return NextResponse.json(
      { valid: false, error: 'Server error during validation' },
      { status: 500 }
    );
  }
} 
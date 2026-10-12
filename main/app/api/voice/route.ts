import { NextRequest, NextResponse } from 'next/server';
import { OPENROUTER_BASE_URL, TRANSCRIPTION_MODEL, openrouterHeaders } from '@/lib/ai/openrouter';

export const runtime = 'nodejs';

const AUDIO_FORMATS: Record<string, string> = { mp4: 'm4a', mpeg: 'mp3', ogg: 'ogg', wav: 'wav' };

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const audioFile = formData.get('audio') as Blob;

    if (!audioFile) {
      return NextResponse.json(
        { error: 'No audio file provided' },
        { status: 400 }
      );
    }

    const subtype = audioFile.type.split('/')[1]?.split(';')[0] || '';
    const response = await fetch(`${OPENROUTER_BASE_URL}/audio/transcriptions`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${process.env.OPENROUTER_API_KEY || ''}`,
        'Content-Type': 'application/json',
        ...openrouterHeaders,
      },
      body: JSON.stringify({
        model: TRANSCRIPTION_MODEL,
        input_audio: {
          data: Buffer.from(await audioFile.arrayBuffer()).toString('base64'),
          format: AUDIO_FORMATS[subtype] || 'webm',
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`OpenRouter transcription failed: ${response.status} ${await response.text()}`);
    }

    const transcription = await response.json();
    return NextResponse.json({ text: transcription.text });

  } catch (error) {
    console.error('Error processing audio:', error);
    return NextResponse.json(
      { error: 'Failed to process audio' },
      { status: 500 }
    );
  }
}

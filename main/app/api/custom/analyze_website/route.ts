import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(req: NextRequest) {
  try {
    const { url, apiKey, screenshotApiKey, delayInSeconds = 15 } = await req.json();

    if (!url || !apiKey) {
      return NextResponse.json({ error: 'URL and OpenRouter API key are required' }, { status: 400 });
    }

    if (!screenshotApiKey) {
      return NextResponse.json({ error: 'Screenshot API key is required' }, { status: 400 });
    }

    const screenshotResponse = await fetch(`https://api.screenshotone.com/take?access_key=${screenshotApiKey}&url=${encodeURIComponent(url)}&format=jpg&block_cookie_banners=true&block_trackers=true&timeout=60&image_quality=80&delay=${delayInSeconds}`, {
      method: 'GET',
    });

    if (!screenshotResponse.ok) {
      return NextResponse.json({ 
        error: 'Failed to capture screenshot', 
        details: `ScreenshotOne API returned ${screenshotResponse.status}` 
      }, { status: 500 });
    }

    const imageBuffer = await screenshotResponse.arrayBuffer();
    const base64Image = Buffer.from(imageBuffer).toString('base64');
    const dataUrl = `data:image/jpeg;base64,${base64Image}`;
    
    const client = new OpenAI({
      baseURL: 'https://openrouter.ai/api/v1',
      apiKey: apiKey,
    });
    
    const designEvaluationPrompt = `
As an expert UI/UX designer, evaluate this website's visual design and score it from 1-5 where:
1 = Urgently needs redesign (looks like it was made in 2008 or earlier)
5 = No redesign needed (looks modern and professional)

Focus primarily on:
- Overall visual appearance 
- How modern the design looks (what year it appears to be from)
- Visual appeal and aesthetics
- Whether it looks professional and up-to-date
- If it meets current design standards

Ignore technical aspects like responsiveness, information architecture, or detailed typography analysis.

Format your response as a valid JSON object with only these two fields:
1. "score" - Integer 1-5
2. "reasoning" - Brief explanation focusing on how modern the site looks and whether it needs a visual refresh
`;

    const completion = await client.chat.completions.create({
      model: 'openai/o4-mini',
      messages: [
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: designEvaluationPrompt
            },
            {
              type: 'image_url',
              image_url: {
                url: dataUrl
              }
            }
          ]
        }
      ],
      response_format: {
        type: 'json_object'
      }
    });
    
    const analysis = JSON.parse(completion.choices[0].message.content || '{}');
    
    return NextResponse.json({
      result: analysis,
      previewUrl: url
    });
    
  } catch (error: unknown) {
    console.error('Error analyzing webpage:', error);
    return NextResponse.json(
      { 
        error: 'Failed to analyze webpage', 
        details: error instanceof Error ? error.message : String(error)
      },
      { status: 500 }
    );
  }
}

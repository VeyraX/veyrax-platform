import { openai } from '@ai-sdk/openai';
import { generateObject } from 'ai';
import { z } from 'zod';
import { createClient } from '@/lib/utils/supabase/server';

const chatTitleSystemPrompt = `You are a helpful assistant that creates short, concise chat titles based on the user's first message.
Rules:
- Keep titles between 3-5 words
- Make it descriptive but concise
- Remove any unnecessary words
- Focus on the main topic or question
- Don't use special characters`;

export async function POST(req: Request) {
  const supabase = createClient();
  const body = await req.json();
  const { chatId, firstMessage } = body;

  if (!chatId || !firstMessage) {
    return new Response(JSON.stringify({ error: 'Missing required parameters' }), {
      status: 400,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  const { object } = await generateObject({
    model: openai('gpt-4o'),
    system: chatTitleSystemPrompt,
    schema: z.object({
      title: z.string(),
    }),
    prompt: `Generate a concise title for a chat that starts with this message: "${firstMessage}"`,
  });
  
  try {
    const { data, error } = await supabase
      .from('chats_chats')
      .update({ name: object.title })
      .eq('id', chatId)
      .select('*')
      .single();

    if (error) throw error;
    
    return new Response(JSON.stringify({ title: object.title }), {
      status: 200,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } catch (error) {
    console.error('Error updating chat title:', error);
    return new Response(JSON.stringify({ error: 'Failed to update chat title' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
}
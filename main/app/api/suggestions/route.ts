import { openai } from '@ai-sdk/openai';
import { generateObject, generateText } from 'ai';
import { tools } from '@/lib/ai/tools';
import { suggestions_system_prompt } from '@/app/prompts/suggestions_system_prompt';
import { z } from 'zod';

export async function POST(req: Request) {
  const body = await req.json();
  const messages = body.messages;

  const lastUserMessage = messages[messages.length - 1];
  const lastAssistantMessage = messages.find(
    (m: any) => m.role === 'assistant'
  );

  const { object } = await generateObject({
    model: openai('gpt-4o'),
    system: suggestions_system_prompt,
    schema: z.object({
      suggestions: z.array(z.string()),
    }),
    prompt: `
    User: ${lastUserMessage?.content || ''}
    Assistant: ${lastAssistantMessage?.content || ''}
    `,
  });
  
  return new Response(JSON.stringify(object), {
    status: 200,
    headers: {
      'Content-Type': 'application/json',
    },
  });
}
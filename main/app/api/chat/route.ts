import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { getUserTools } from '@/lib/utils/get-user-tools';
import { main_system_prompt } from '../../prompts/main_system_prompt';
import { createClient } from '@/lib/utils/supabase/server';

export const maxDuration = 30;

export async function POST(req: Request) {
  const supabase = createClient();
  
  const { data: { user }, error: userError } = await supabase.auth.getUser();
  
  if (userError || !user) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = await req.json();
  const { messages } = body;

  try {
    const userTools = await getUserTools(user.id);

    const result = streamText({
      model: openai('gpt-4o'),
      messages,
      system: main_system_prompt,
      tools: userTools,
      experimental_toolCallStreaming: true,
      maxSteps: 20,
    });

    return result.toDataStreamResponse({
      getErrorMessage: (error: unknown) => {
        if (error instanceof Error && error.message.includes('maximum context length')) {
          const truncatedMessages = messages.slice(0, -1);
          return "Token limit exceeded. Please try rephrasing your last question more concisely.";
        }
        
        return error instanceof Error ? error.message : 'An unknown error occurred';
      }
    });
  } catch (error) {
    console.error('Error in chat route:', error);
    return new Response('An error occurred while processing your request', { status: 500 });
  }
}
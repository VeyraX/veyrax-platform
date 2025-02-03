import { openai } from '@ai-sdk/openai';
import { streamText } from 'ai';
import { tools } from '@/lib/ai/tools';
import { main_system_prompt } from '../../prompts/main_system_prompt';
export const maxDuration = 30;

export async function POST(req: Request) {
  const body = await req.json();
  const { messages } = body;

  try {

    const result = streamText({
      model: openai('gpt-4o'),
      messages,
      system: main_system_prompt,
      tools,
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
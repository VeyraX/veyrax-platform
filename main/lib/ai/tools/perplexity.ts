import { tool } from 'ai';
import { z } from 'zod';
import { type PerplexityResponse } from '@/app/modules/agent/components/tools/perplexity/types.perplexity';

export const askPerplexityTool = tool({
  description: 'Ask a question using Perplexity AI',
  parameters: z.object({
    content: z.string().describe('The question or prompt to send to Perplexity'),
  }),
  execute: async function({ content }: { content: string }): Promise<{ 
    success: boolean,
    response?: PerplexityResponse,
    error?: string 
  }> {
    try {
      const response = await fetch('http://localhost:8000/perplexity/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [
            {
              role: "user",
              content: content
            }
          ],
        }),
      });

      if (!response.ok) throw new Error('Failed to get answer from Perplexity');
      
      const data = await response.json();
      return {
        success: true,
        response: {
          id: data.id || '1',
          model: 'perplexity',
          object: 'chat.completion',
          created: Date.now(),
          citations: data.citations || [],
          choices: [{
            index: 0,
            finish_reason: 'stop',
            message: {
              role: 'assistant',
              content: data.choices[0].message.content
            },
            delta: {
              role: 'assistant',
              content: data.choices[0].message.content
            }
          }],
          usage: data.usage || {
            prompt_tokens: 0,
            completion_tokens: 0,
            total_tokens: 0
          }
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get answer from Perplexity'
      };
    }
  }
});

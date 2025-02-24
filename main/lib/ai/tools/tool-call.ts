import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const tool_call = tool({
  description: 'Универсальный вызов инструмента с произвольными параметрами',
  parameters: z.object({
    method: z.string().describe('Название метода для вызова'),
    params: z.record(z.any()).describe('Объект с произвольными параметрами')
  }),
  execute: async function({ method, params }) {
    try {
      const headers = await getAuthHeaders();
      const queryParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/tool-call/${method}?${queryParams.toString()}`,
        {
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) throw new Error(`Failed to execute tool call: ${method}`);
      
      const data = await response.json();
      return {
        success: true,
        result: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute tool call'
      };
    }
  }
});

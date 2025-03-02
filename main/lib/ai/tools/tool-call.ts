import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const tool_call = tool({
  description: 'Unified tool call for all tools, based on annotation you must choose the correct tool and method',
  parameters: z.object({
    tool: z.string().describe('Name of the tool/integration to use, example: "google_calendar"'),
    method: z.string().describe('Name of the method to call, example: "get_event"'),
    params: z.record(z.any())
      .describe('Object with arbitrary parameters, example: { "event_id": 123 }, follow the annotation of the tool to choose the correct parameters. Parameters are NOT optional. You MUST include all required parameters.')
      .default({})
  }),
  execute: async function({ tool, method, params = {} }) {
    try {
      const headers = await getAuthHeaders();
      const queryParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, String(value));
        }
      });

      const url = `${process.env.NEXT_PUBLIC_API_URL}/tool-call/${tool}/${method}`;
      console.log('Making request to:', url);
      console.log('With params:', JSON.stringify(params, null, 2));
      console.log('With headers:', JSON.stringify(headers, null, 2));

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(params),
        credentials: 'include'
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Error response:', errorText);
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      return {
        success: true,
        result: {
          data: data.data,
          component: data.component || null
        }
      };
    } catch (error) {
      console.error('Tool call execution error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute tool call'
      };
    }
  }
});

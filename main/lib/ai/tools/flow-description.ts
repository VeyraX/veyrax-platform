import { tool } from 'ai';
import { z } from 'zod';

export const flow_improve_description = tool({
  description: 'Improves the flow description by analyzing the current description and making it more detailed and structured',
  parameters: z.object({
    description: z.string().describe('The current flow description to improve'),
    name: z.string().optional().describe('The name of the flow (optional)'),
  }),
  execute: async function({ description, name }) {
    try {
      const baseUrl = process.env.VERCEL_URL 
        ? `https://${process.env.VERCEL_URL}` 
        : process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
      
      const response = await fetch(`${baseUrl}/api/flow/improve-description`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          description,
          name: name || ''
        }),
      });
      
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
      
      const result = await response.json();
      console.log('result', result.description);
      return {
        name: result.name || name || 'Untitled Flow',
        description: result.description || description
      };
    } catch (error) {
      console.error('Error in flow_improve_description tool:', error);
      return {
        name: name || 'Untitled Flow',
        description: description || 'No description provided'
      };
    }
  }
});
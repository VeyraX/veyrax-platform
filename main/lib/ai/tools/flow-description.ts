import { tool } from 'ai';
import { z } from 'zod';

export const flow_improve_description = tool({
  description: 'Returns the flow description and name without modifications',
  parameters: z.object({
    description: z.string().describe('The flow description'),
    name: z.string().describe('The name of the flow (optional)'),
  }),
  execute: async function({ description, name }) {
    return {
      name: name || 'Untitled Flow',
      description: description || 'No description provided'
    };
  }
});
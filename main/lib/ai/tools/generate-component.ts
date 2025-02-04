import { tool } from 'ai';
import { z } from 'zod';

export const generateComponentTool = tool({
  description: 'Generate a new component with a progress indicator showing the generation steps',
  parameters: z.object({
    title: z.string(),
    steps: z.array(z.object({
      description: z.string(),
      progress: z.number()
    })).optional()
  }),
  execute: async function({ title, steps }): Promise<{ 
    success: boolean, 
    title: string,
    progressStates: Array<{ description: string, progress: number }>,
    error?: string 
  }> {
    try {
      const defaultSteps = [
        { description: "Analyzing requirements", progress: 0 },
        { description: "Setting up component structure", progress: 25 },
        { description: "Implementing core functionality", progress: 50 },
        { description: "Adding styling and animations", progress: 75 },
        { description: "Finalizing and testing", progress: 100 }
      ];

      const progressStates = steps || defaultSteps;
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      return {
        success: true,
        title,
        progressStates
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to generate component',
        progressStates: [],
        title: ''
      };
    }
  }
});
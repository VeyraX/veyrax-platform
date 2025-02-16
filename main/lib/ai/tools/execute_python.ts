import { tool } from 'ai';
import { z } from 'zod';
import { Sandbox } from '@e2b/code-interpreter';
import { sandboxManager } from '@/lib/utils/sanbox-manager';

export const executePython = tool({
  description: 'Execute Python code in a Jupyter notebook cell and return result',
  parameters: z.object({
    code: z.string().describe('The Python code to execute in a single cell'),
    sandboxId: z.string().optional().describe('Optional sandbox ID to reuse existing sandbox'),
  }),
  execute: async function({ code, sandboxId }) {
    try {
      let sandbox: Sandbox;
      
      if (sandboxId) {
        sandbox = await Sandbox.connect(sandboxId);
      } else {
        sandbox = await sandboxManager.getSandbox();
        sandboxManager.setCurrentSandbox(sandbox.sandboxId);
      }
        
      const { results, error } = await sandbox.runCode(code);
      
      if (error) {
        return {
          success: false,
          error: error.toString()
        };
      }

      return {
        success: true,
        data: results,
        sandboxId: sandbox.sandboxId
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      };
    }
  },
});
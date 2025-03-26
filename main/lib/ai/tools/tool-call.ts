import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const tool_call = tool({
  description: 'Unified tool call for all tools, based on annotation you must choose the correct tool and method',
  parameters: z.object({
    tool: z.string().describe('Name of the tool/integration to use, example: "google_calendar"'),
    method: z.string().describe('Name of the method to call, example: "get_event"'),
    params: z.object({}).catchall(z.any())
      .describe('Object with arbitrary parameters. Parameters are NOT optional. You MUST include all required parameters.')
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

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
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
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute tool call'
      };
    }
  }
});

export const tool_call_test_flow = tool({
  description: 'Unified tool call for all tools, based on annotation you must choose the correct tool and method',
  parameters: z.object({
    tool: z.string().describe('Name of the tool/integration to use, example: "google_calendar"'),
    method: z.string().describe('Name of the method to call, example: "get_event"'),
    params: z.object({}).catchall(z.any())
      .describe('Object with arbitrary parameters. Parameters are NOT optional. You MUST include all required parameters.')
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
      console.log('url', url);
      console.log('params', params);
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
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
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute tool call'
      };
    }
  }
});

export const get_flow = tool({
  description: 'Get user flow actions and examples that can be used to automate tasks',
  parameters: z.object({
    flowId: z.string().describe('ID of the flow to get')
  }),
  execute: async function({ flowId }) {
    try {
      const headers = await getAuthHeaders();
      
      const url = `${process.env.NEXT_PUBLIC_API_URL}/get-flow/${flowId}`;

      const response = await fetch(url, {
        method: 'GET',
        headers,
        credentials: 'include'
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      return {
        success: true,
        flows: data.flows,
        examples: data.examples
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch flows'
      };
    }
  }
});

export const tool_call_builder = tool({
  description: 'Unified tool call for all tools, based on annotation you must choose the correct tool and method',
  parameters: z.object({
    tool: z.string().describe('Name of the tool/integration to use, example: "google_calendar"'),
    method: z.string().describe('Name of the method to call, example: "get_event"'),
    params: z.object({}).catchall(z.any())
      .describe('Object with arbitrary parameters. Parameters are NOT optional. You MUST include all required parameters.')
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

      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(params)
      });
      
      if (!response.ok) {
        const errorText = await response.text();
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
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to execute tool call'
      };
    }
  }
});

export const get_tools = tool({
  description: 'Get user tools and examples that can be used to automate tasks',
  parameters: z.object({}),
  execute: async function() {
    try {
      const headers = await getAuthHeaders();
      
      const url = `${process.env.NEXT_PUBLIC_API_URL}/get-tools`;

      const response = await fetch(url, {
        method: 'GET',
        headers,
        credentials: 'include'
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API request failed with status ${response.status}: ${errorText}`);
      }
      
      const data = await response.json();
      
      return {
        success: true,
        tools: data.tools, 
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch tools'
      };
    }
  }
});
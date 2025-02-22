import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const confluence_listSpaces = tool({
  description: 'List all available Confluence spaces',
  parameters: z.object({}),
  execute: async function() {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/confluence/spaces`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to list spaces');
      
      const data = await response.json();
      return {
        success: true,
        spaces: data.results
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list spaces'
      };
    }
  }
});

export const confluence_listPages = tool({
  description: 'List pages in Confluence with optional filters',
  parameters: z.object({
    spaceId: z.string().optional().describe('Filter pages by space ID, string value strictly'),
    title: z.string().optional().describe('Filter pages by title, string'),
    limit: z.number().optional().describe('Maximum number of results to return (default: 50, max: 100), number'),
  }),
  execute: async function({ spaceId, title, limit }) {
    try {
      const headers = await getAuthHeaders();
      const params = new URLSearchParams();
      if (spaceId) params.append('space_id', spaceId);
      if (title) params.append('title', title);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/confluence/pages?${params.toString()}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to list pages');
      
      const data = await response.json();
      return {
        success: true,
        pages: data.results
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list pages'
      };
    }
  }
});

export const confluence_getPage = tool({
  description: 'Get a specific Confluence page by ID',
  parameters: z.object({
    pageId: z.string().describe('ID of the page to get'),
  }),
  execute: async function({ pageId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/confluence/pages/${pageId}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to get page');
      
      const data = await response.json();
      return {
        success: true,
        page: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get page'
      };
    }
  }
});

export const confluence_searchContent = tool({
  description: 'Search content in Confluence using various filters',
  parameters: z.object({
    cql: z.string().optional().describe('Confluence Query Language (CQL) search string'),
    spaceKey: z.string().optional().describe('Filter by space key'),
    title: z.string().optional().describe('Filter by content title'),
    type: z.string().optional().describe('Content type (default: page)'),
    limit: z.number().optional().describe('Maximum number of results to return'),
  }),
  execute: async function({ cql, spaceKey, title, type, limit }) {
    try {
      const headers = await getAuthHeaders();
      const params = new URLSearchParams();
      if (cql) params.append('cql', cql);
      if (spaceKey) params.append('space_key', spaceKey);
      if (title) params.append('title', title);
      if (type) params.append('type', type);
      if (limit) params.append('limit', limit.toString());

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/confluence/content?${params.toString()}`, {
        headers,
        credentials: 'include'
      });
      if (!response.ok) throw new Error('Failed to search content');
      
      const data = await response.json();
      return {
        success: true,
        results: data.results
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to search content'
      };
    }
  }
});

export const confluence_vectorSearch = tool({
  description: 'Search through indexed Confluence documents using semantic search',
  parameters: z.object({
    queryText: z.string().describe('The search query text'),
    spaceKey: z.string().optional().describe('Filter by space key'),
    title: z.string().optional().describe('Filter by page title'),
    type: z.string().optional().describe('Filter by content type'),
  }),
  execute: async function({ queryText, ...filters }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/vector-tools/search`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          query_text: queryText,
          search_params: {
            collection: 'confluence',
            query: filters
          }
        })
      });

      if (!response.ok) throw new Error('Failed to search documents');
      
      const data = await response.json();
      return {
        success: true,
        results: data.results
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to search documents'
      };
    }
  }
});
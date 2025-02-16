import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const notion_listDatabases = tool({
  description: 'List available Notion databases',
  parameters: z.object({
    startCursor: z.string().optional().describe('Cursor for pagination')
  }),
  execute: async function({ startCursor }) {
    try {
      const params = new URLSearchParams();
      if (startCursor) params.append('start_cursor', startCursor);

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/notion/databases?${params.toString()}`,
        {
          headers,
          credentials: 'include'
        }
      );
      if (!response.ok) throw new Error('Failed to fetch databases');
      
      const data = await response.json();
      return {
        success: true,
        databases: data.items,
        nextCursor: data.next_cursor
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch databases'
      };
    }
  }
});

export const notion_listPages = tool({
  description: 'List pages from a specific Notion database with optional filters',
  parameters: z.object({
    databaseId: z.string().describe('ID of the database to query'),
    startCursor: z.string().optional().describe('Cursor for pagination'),
    searchQuery: z.string().optional().describe('Search query for filtering pages'),
    filterBy: z.record(z.any()).optional().describe('Filter criteria'),
    sortBy: z.record(z.any()).optional().describe('Sort criteria')
  }),
  execute: async function({ databaseId, startCursor, searchQuery, filterBy, sortBy }) {
    try {
      const filters = {
        database_id: databaseId,
        search_query: searchQuery,
        filter_by: filterBy,
        sort_by: sortBy
      };

      const headers = await getAuthHeaders();
      const response = await fetch(`http://localhost:8000/notion/databases/${databaseId}/pages`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          start_cursor: startCursor,
          filters
        })
      });

      if (!response.ok) throw new Error('Failed to fetch pages');
      
      const data = await response.json();
      return {
        success: true,
        pages: data.items,
        nextCursor: data.next_cursor
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch pages'
      };
    }
  }
});

export const notion_createPage = tool({
  description: 'Create a new page in a Notion database',
  parameters: z.object({
    parentId: z.string().describe('ID of the database'),
    title: z.string().describe('Title of the page'),
    properties: z.record(z.any()).describe('Page properties in Notion format'),
    content: z.record(z.any()).optional().describe('Page content blocks')
  }),
  execute: async function({ parentId, title, properties, content }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch('http://localhost:8000/notion/pages', {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          parent_id: parentId,
          title,
          properties,
          content
        })
      });

      if (!response.ok) throw new Error('Failed to create page');
      
      const data = await response.json();
      return {
        success: true,
        page: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create page'
      };
    }
  }
});

export const notion_searchPages = tool({
  description: 'Search for pages across all Notion databases',
  parameters: z.object({
    query: z.string().describe('Search query string'),
    startCursor: z.string().optional().describe('Cursor for pagination')
  }),
  execute: async function({ query, startCursor }) {
    try {
      const params = new URLSearchParams();
      params.append('query', query);
      if (startCursor) params.append('start_cursor', startCursor);

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/notion/search?${params.toString()}`,
        {
          headers,
          credentials: 'include'
        }
      );
      if (!response.ok) throw new Error('Failed to search pages');
      
      const data = await response.json();
      return {
        success: true,
        pages: data.items,
        nextCursor: data.next_cursor
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to search pages'
      };
    }
  }
});

export const notion_readPage = tool({
  description: 'Get details of a specific Notion page by ID',
  parameters: z.object({
    pageId: z.string().describe('ID of the page to fetch')
  }),
  execute: async function({ pageId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/notion/pages/${pageId}`,
        {
          headers,
          credentials: 'include'
        }
      );
      
      if (!response.ok) throw new Error('Failed to fetch page');
      
      const data = await response.json();
      return {
        success: true,
        page: data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch page'
      };
    }
  }
});

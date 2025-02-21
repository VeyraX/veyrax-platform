import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';
import { formatProperties, formatDatabaseFilter, formatSort } from '@/lib/utils/notion-formatter';

export const notion_listDatabases = tool({
  description: 'List available Notion databases',
  parameters: z.object({
    startCursor: z.string().optional().describe('Cursor for pagination'),
    maxResults: z.number().optional().describe('Maximum number of results to return (default: 100)')
  }),
  execute: async function({ startCursor, maxResults }) {
    try {
      const params = new URLSearchParams();
      if (startCursor) params.append('start_cursor', startCursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/notion/databases?${params.toString()}`,
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
    sortBy: z.record(z.any()).optional().describe('Sort criteria'),
    maxResults: z.number().optional().describe('Maximum number of results to return (default: 100)')
  }),
  execute: async function({ databaseId, startCursor, searchQuery, filterBy, sortBy, maxResults }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notion/databases/${databaseId}/pages`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({
          start_cursor: startCursor,
          filters: {
            database_id: databaseId,
            search_query: searchQuery,
            filter_by: filterBy,
            sort_by: sortBy,
            max_results: maxResults
          }
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
  description: 'Create a new page in a Notion database with simple properties',
  parameters: z.object({
    databaseId: z.string().describe('ID of the database'),
    title: z.string().describe('Page title'),
    text: z.string().optional().describe('Text content'),
    date: z.string().optional().describe('Date in YYYY-MM-DD format'),
    status: z.string().optional().describe('Status value'),
    number: z.number().optional().describe('Number value'),
    checkbox: z.boolean().optional().describe('Checkbox value'),
    properties: z.record(z.any()).optional().describe('Additional properties in Notion format'),
    content: z.array(z.record(z.any())).optional().describe('Page content blocks')
  }),
  execute: async function({ 
    databaseId, 
    title, 
    text, 
    date, 
    status, 
    number, 
    checkbox, 
    properties = {}, 
    content = [] 
  }) {
    try {
      const formattedProperties = formatProperties(
        title,
        text,
        date,
        status,
        number,
        checkbox,
        properties
      );

      const requestBody = {
        parent: { database_id: databaseId },
        properties: formattedProperties,
        ...(content.length > 0 && { children: content })
      };

      console.log('Notion Create Page Request:', {
        databaseId,
        requestBody
      });

      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notion/pages`, {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create page');
      }
      
      return {
        success: true,
        result: data
      };
    } catch (error) {
      console.error('Notion Create Page Error:', error);
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
    startCursor: z.string().optional().describe('Cursor for pagination'),
    maxResults: z.number().optional().describe('Maximum number of results to return (default: 100)'),
    sortDirection: z.enum(['ascending', 'descending']).optional()
      .describe('Sort direction for results based on last edited time')
  }),
  execute: async function({ query, startCursor, maxResults, sortDirection }) {
    try {
      const params = new URLSearchParams();
      params.append('query', query);
      if (startCursor) params.append('start_cursor', startCursor);
      if (maxResults) params.append('page_size', maxResults.toString());
      if (sortDirection) params.append('sort_direction', sortDirection);

      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/notion/search?${params.toString()}`,
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
        `${process.env.NEXT_PUBLIC_API_URL}/notion/pages/${pageId}`,
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

export const notion_vectorSearch = tool({
  description: 'Search through indexed Notion pages using semantic search',
  parameters: z.object({
    queryText: z.string().describe('The search query text'),
    docId: z.string().optional().describe('Filter by specific document ID'),
    title: z.string().optional().describe('Filter by page title'),
    databaseId: z.string().optional().describe('Filter by database ID'),
    url: z.string().optional().describe('Filter by page URL'),
    lastEditedTime: z.string().optional().describe('Filter by last edited time')
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
            collection: 'notion',
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

export const notion_getDatabaseProperties = tool({
  description: 'Get properties and schema of a specific Notion database',
  parameters: z.object({
    databaseId: z.string().describe('ID of the database to fetch properties for')
  }),
  execute: async function({ databaseId }) {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/notion/databases/${databaseId}`,
        {
          headers,
          credentials: 'include'
        }
      );
      
      if (!response.ok) throw new Error('Failed to fetch database properties');
      
      const data = await response.json();
      return {
        success: true,
        database: {
          id: data.id,
          title: data.title,
          properties: data.properties
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch database properties'
      };
    }
  }
});

export const notion_updatePage = tool({
  description: 'Update an existing page in Notion',
  parameters: z.object({
    pageId: z.string().describe('ID of the page to update'),
    title: z.string().optional().describe('New title of the page'),
    text: z.string().optional().describe('New text content'),
    date: z.string().optional().describe('Date in YYYY-MM-DD format'),
    status: z.string().optional().describe('Status value'),
    number: z.number().optional().describe('Number value'),
    checkbox: z.boolean().optional().describe('Checkbox value'),
    properties: z.record(z.any()).optional().describe('Raw properties in Notion format')
  }),
  execute: async function({ pageId, title, text, date, status, number, checkbox, properties = {} }) {
    try {
      const formattedProperties = formatProperties(
        title,
        text,
        date,
        status,
        number,
        checkbox,
        properties
      );

      const requestBody = {
        properties: formattedProperties
      };

      console.log('Notion Update Page Request:', {
        pageId,
        requestBody
      });

      const headers = await getAuthHeaders();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/notion/pages/${pageId}`, {
        method: 'PATCH',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(requestBody)
      });

      const data = await response.json();
      console.log('Notion Update Page Response:', data);

      if (!response.ok) {
        const error = data.detail || 'Failed to update page';
        console.error('Notion API Error:', error);
        throw new Error(error);
      }
      
      return {
        success: true,
        result: data
      };
    } catch (error) {
      console.error('Notion Update Page Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update page'
      };
    }
  }
});

export const notion_queryDatabase = tool({
  description: 'Query a Notion database with simple filters and sorts',
  parameters: z.object({
    databaseId: z.string().describe('ID of the database to query'),
    title: z.string().optional().describe('Filter by title containing text'),
    date: z.string().optional().describe('Filter by exact date (YYYY-MM-DD)'),
    dateAfter: z.string().optional().describe('Filter by date after (YYYY-MM-DD)'),
    dateBefore: z.string().optional().describe('Filter by date before (YYYY-MM-DD)'),
    status: z.string().optional().describe('Filter by status/select value'),
    checkbox: z.boolean().optional().describe('Filter by checkbox value'),
    number: z.number().optional().describe('Filter by exact number value'),
    numberGreater: z.number().optional().describe('Filter by number greater than'),
    numberLess: z.number().optional().describe('Filter by number less than'),
    sortBy: z.string().optional().describe('Property to sort by'),
    sortDirection: z.enum(['ascending', 'descending']).optional().describe('Sort direction'),
    startCursor: z.string().optional().describe('Cursor for pagination'),
    pageSize: z.number().optional().describe('Number of results per page (max: 100)'),
    filter: z.record(z.any()).optional().describe('Raw filter in Notion format'),
    sorts: z.array(z.record(z.any())).optional().describe('Raw sorts in Notion format')
  }),
  execute: async function({ 
    databaseId, 
    title, 
    date, 
    dateAfter,
    dateBefore,
    status,
    checkbox,
    number,
    numberGreater,
    numberLess,
    sortBy,
    sortDirection,
    startCursor,
    pageSize,
    filter,
    sorts 
  }) {
    try {
      const compiledFilter = formatDatabaseFilter({
        title,
        date,
        dateAfter,
        dateBefore,
        status,
        checkbox,
        number,
        numberGreater,
        numberLess,
        filter
      });

      const compiledSorts = formatSort(sortBy, sortDirection, sorts);

      const requestBody: any = {
        filter: compiledFilter,
        ...(compiledSorts && { sorts: compiledSorts }),
        ...(startCursor && { start_cursor: startCursor }),
        ...(pageSize && { page_size: pageSize })
      };
      
      console.log('Notion Query Database Request:', {
        databaseId,
        requestBody
      });

      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/notion/databases/${databaseId}/query`,
        {
          method: 'POST',
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          credentials: 'include',
          body: JSON.stringify(requestBody)
        }
      );

      if (!response.ok) throw new Error('Failed to query database');
      
      const data = await response.json();
      return {
        success: true,
        pages: data.items,
        nextCursor: data.next_cursor
      };
    } catch (error) {
      console.error('Notion Query Database Error:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to query database'
      };
    }
  }
});
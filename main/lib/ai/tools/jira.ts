import { tool } from 'ai';
import { z } from 'zod';
import { getAuthHeaders } from '@/lib/actions/actions';

export const jira_listIssues = tool({
  description: 'List Jira issues with optional filters',
  parameters: z.object({
    project_id: z.string().optional().describe('Project ID'),
    status_id: z.string().optional().describe('Status ID'),
    assignee: z.string().optional().describe('Assignee username'),
    priority_id: z.string().optional().describe('Priority ID'),
    max_results: z.number().optional().describe('Maximum number of results (default: 50)')
  }),
  execute: async function(filters: {
    project_id?: string;
    status_id?: string;
    assignee?: string;
    priority_id?: string;
    max_results?: number;
  }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issues?${new URLSearchParams(filters as any)}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list issues'
      };
    }
  }
});

export const jira_getIssue = tool({
  description: 'Get a specific Jira issue by ID',
  parameters: z.object({
    issue_id: z.string().describe('Issue ID')
  }),
  execute: async function({ issue_id }: { issue_id: string }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issues/${issue_id}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get issue'
      };
    }
  }
});

export const jira_createIssue = tool({
  description: 'Create a new Jira issue',
  parameters: z.object({
    project_id: z.string().describe('Project ID'),
    summary: z.string().describe('Issue summary'),
    issue_type_id: z.string().describe('Issue type ID'),
    description: z.string().optional().describe('Issue description'),
    assignee_id: z.string().optional().describe('Assignee ID'),
    priority_id: z.string().optional().describe('Priority ID'),
    status_id: z.string().optional().describe('Status ID'),
    labels: z.array(z.string()).optional().describe('Issue labels')
  }),
  execute: async function(issueData: {
    project_id: string;
    summary: string;
    issue_type_id: string;
    description?: string;
    assignee_id?: string;
    priority_id?: string;
    status_id?: string;
    labels?: string[];
  }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issues`,
        {
          method: 'POST',
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(issueData),
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create issue'
      };
    }
  }
});

export const jira_listProjects = tool({
  description: 'List all Jira projects',
  parameters: z.object({}),
  execute: async function(): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/projects`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list projects'
      };
    }
  }
});

export const jira_updateIssue = tool({
  description: 'Update an existing Jira issue',
  parameters: z.object({
    issue_id: z.string().describe('Issue ID'),
    summary: z.string().optional().describe('Issue summary'),
    description: z.string().optional().describe('Issue description'),
    assignee_id: z.string().optional().describe('Assignee ID'),
    priority_id: z.string().optional().describe('Priority ID'),
    status_id: z.string().optional().describe('Status ID'),
    labels: z.array(z.string()).optional().describe('Issue labels')
  }),
  execute: async function({ issue_id, ...updateData }: {
    issue_id: string;
    summary?: string;
    description?: string;
    assignee_id?: string;
    priority_id?: string;
    status_id?: string;
    labels?: string[];
  }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issues/${issue_id}`,
        {
          method: 'PATCH',
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(updateData),
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update issue'
      };
    }
  }
});

export const jira_deleteIssue = tool({
  description: 'Delete a Jira issue',
  parameters: z.object({
    issue_id: z.string().describe('Issue ID')
  }),
  execute: async function({ issue_id }: { issue_id: string }): Promise<{
    success: boolean;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issues/${issue_id}`,
        {
          method: 'DELETE',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to delete issue'
      };
    }
  }
});

export const jira_getProject = tool({
  description: 'Get a specific Jira project',
  parameters: z.object({
    project_id: z.string().describe('Project ID')
  }),
  execute: async function({ project_id }: { project_id: string }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/projects/${project_id}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get project'
      };
    }
  }
});

export const jira_listStatuses = tool({
  description: 'List all Jira statuses',
  parameters: z.object({}),
  execute: async function(): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/statuses`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list statuses'
      };
    }
  }
});

export const jira_listPriorities = tool({
  description: 'List all Jira priorities',
  parameters: z.object({}),
  execute: async function(): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/priorities`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list priorities'
      };
    }
  }
});

export const jira_listIssueTypes = tool({
  description: 'List all Jira issue types',
  parameters: z.object({}),
  execute: async function(): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/issue-types`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list issue types'
      };
    }
  }
});

export const jira_listFields = tool({
  description: 'List all Jira fields',
  parameters: z.object({}),
  execute: async function(): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/jira/fields`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list fields'
      };
    }
  }
});

export const jira_listUsers = tool({
  description: 'List Jira users with optional search query',
  parameters: z.object({
    query: z.string().optional().describe('Search query to filter users')
  }),
  execute: async function({ query }: { query?: string }): Promise<{
    success: boolean;
    data?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      const url = new URL(`${process.env.NEXT_PUBLIC_API_URL}/jira/users`);
      if (query) {
        url.searchParams.append('query', query);
      }

      const response = await fetch(url.toString(), {
        method: 'GET',
        headers,
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error(await response.text());
      }

      const data = await response.json();
      return { success: true, data };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to list users'
      };
    }
  }
});
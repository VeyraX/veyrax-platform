import { tool } from 'ai';
import { z } from 'zod';
import { 
  IssueList, 
  ProjectList, 
  IssueCreateProps, 
  IssueFilterProps,
  TeamList,
  WorkflowStateList
} from '@/app/modules/agent/components/tools/linear/types.linear';
import { getAuthHeaders } from '@/lib/actions/actions';

export const linear_listIssues = tool({
  description: 'List all Linear issues with optional pagination',
  parameters: z.object({
    cursor: z.string().optional().describe('Pagination cursor'),
    maxResults: z.number().optional().describe('Maximum number of results to return (1-100)')
  }),
  execute: async function({ cursor, maxResults }: { cursor?: string, maxResults?: number }): Promise<{
    success: boolean;
    data?: IssueList;
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      if (cursor) params.append('cursor', cursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/linear/issues?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );
      console.log(response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch issues');
      }
      
      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch issues'
      };
    }
  }
});

export const linear_searchIssues = tool({
  description: 'Search Linear issues using a text query',
  parameters: z.object({
    query: z.string().describe('Search query string'),
    cursor: z.string().optional().describe('Pagination cursor'),
    maxResults: z.number().optional().describe('Maximum number of results to return (1-100)')
  }),
  execute: async function({ query, cursor, maxResults }: { 
    query: string; 
    cursor?: string;
    maxResults?: number;
  }): Promise<{
    success: boolean;
    data?: IssueList;
    error?: string;
  }> {
    try {
      const params = new URLSearchParams({
        query: query
      });
      if (cursor) params.append('cursor', cursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/linear/issues/search?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to search issues');
      }
      
      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to search issues'
      };
    }
  }
});

export const linear_createIssue = tool({
  description: 'Create a new Linear issue',
  parameters: z.object({
    title: z.string().describe('Title of the issue'),
    teamId: z.string().describe('ID of the team'),
    description: z.string().optional().describe('Description of the issue'),
    assigneeId: z.string().optional().describe('ID of the assignee'),
    stateId: z.string().optional().describe('ID of the state'),
    priority: z.number().int().min(0).max(4).optional().describe('Priority of the issue (0-4)'),
    projectId: z.string().optional().describe('ID of the project'),
    labels: z.array(z.string()).optional().describe('Array of label names')
  }),
  execute: async function(issueData: IssueCreateProps): Promise<{
    success: boolean;
    issue?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      
      const requestBody = {
        title: issueData.title,
        team_id: issueData.teamId,
        description: issueData.description,
        assignee_id: issueData.assigneeId,
        state_id: issueData.stateId,
        priority: issueData.priority,
        project_id: issueData.projectId,
        labels: issueData.labels
      };
      
      const response = await fetch('http://localhost:8000/linear/issues', {
        method: 'POST',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody),
        credentials: 'include'
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || 'Failed to create issue');
      }
      
      return {
        success: true,
        issue: responseData
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to create issue'
      };
    }
  }
});

export const linear_listProjects = tool({
  description: 'List all Linear projects with optional pagination',
  parameters: z.object({
    cursor: z.string().optional().describe('Pagination cursor'),
    maxResults: z.number().optional().describe('Maximum number of results to return (1-100)')
  }),
  execute: async function({ cursor, maxResults }: { 
    cursor?: string;
    maxResults?: number;
  }): Promise<{
    success: boolean;
    data?: ProjectList;
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      if (cursor) params.append('cursor', cursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/linear/projects?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch projects');
      }
      
      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch projects'
      };
    }
  }
});

export const linear_listTeams = tool({
  description: 'List all Linear teams with optional pagination',
  parameters: z.object({
    cursor: z.string().optional().describe('Pagination cursor'),
    maxResults: z.number().optional().describe('Maximum number of results to return (1-100)')
  }),
  execute: async function({ cursor, maxResults }: { 
    cursor?: string;
    maxResults?: number;
  }): Promise<{
    success: boolean;
    data?: TeamList;
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      if (cursor) params.append('cursor', cursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/linear/teams?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch teams');
      }
      
      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch teams'
      };
    }
  }
});

export const linear_updateIssue = tool({
  description: 'Update an existing Linear issue',
  parameters: z.object({
    issueId: z.string().describe('ID of the issue to update'),
    title: z.string().optional().describe('New title of the issue'),
    description: z.string().optional().describe('New description of the issue'),
    assignee_id: z.string().optional().describe('New assignee ID'),
    state_id: z.string().optional().describe('New state ID'),
    priority: z.number().int().min(0).max(4).optional().describe('New priority (0-4)'),
    project_id: z.string().optional().describe('New project ID'),
    labels: z.array(z.string()).optional().describe('New array of label names')
  }),
  execute: async function({ issueId, ...updateData }: { 
    issueId: string;
    title?: string;
    description?: string;
    assignee_id?: string;
    state_id?: string;
    priority?: number;
    project_id?: string;
    labels?: string[];
  }): Promise<{
    success: boolean;
    issue?: any;
    error?: string;
  }> {
    try {
      const headers = await getAuthHeaders();
      
      const response = await fetch(`http://localhost:8000/linear/issues/${issueId}`, {
        method: 'PATCH',
        headers: {
          ...headers,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(updateData),
        credentials: 'include'
      });

      const responseData = await response.json();

      if (!response.ok) {
        throw new Error(responseData.detail || 'Failed to update issue');
      }
      
      return {
        success: true,
        issue: responseData
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to update issue'
      };
    }
  }
});

export const linear_listWorkflowStates = tool({
  description: 'List all Linear workflow states (statuses) with optional pagination',
  parameters: z.object({
    cursor: z.string().optional().describe('Pagination cursor'),
    maxResults: z.number().optional().describe('Maximum number of results to return (1-100)')
  }),
  execute: async function({ cursor, maxResults }: { 
    cursor?: string;
    maxResults?: number;
  }): Promise<{
    success: boolean;
    data?: WorkflowStateList;
    error?: string;
  }> {
    try {
      const params = new URLSearchParams();
      if (cursor) params.append('cursor', cursor);
      if (maxResults) params.append('max_results', maxResults.toString());

      const headers = await getAuthHeaders();
      const response = await fetch(
        `http://localhost:8000/linear/workflow-states?${params.toString()}`,
        {
          method: 'GET',
          headers,
          credentials: 'include'
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch workflow states');
      }
      
      const data = await response.json();
      return {
        success: true,
        data
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch workflow states'
      };
    }
  }
});
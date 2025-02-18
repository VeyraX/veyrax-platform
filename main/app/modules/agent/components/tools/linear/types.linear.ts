export interface User {
    id: string;
    name: string;
    email?: string;
  }
  
  export interface Issue {
    id: string;
    title: string;
    description?: string;
    state: string;
    priority?: number;
    assignee?: User;
    creator: User;
    createdAt: string;
    updatedAt: string;
    labels?: string[];
    projectId?: string;
    teamId: string;
    identifier: string;
    teamKey: string;
  }
  
  export interface Project {
    id: string;
    name: string;
    description?: string;
    state: string;
    createdAt: string;
    updatedAt: string;
    lead?: User;
  }
  
  export interface IssueList {
    issues: Issue[];
    cursor?: string;
    hasNextPage?: boolean;
    totalCount?: number;
  }
  
  export interface ProjectList {
    projects: Project[];
    cursor?: string;
    hasNextPage?: boolean;
    totalCount?: number;
  }
  
  export interface IssueCreateProps {
    title: string;
    teamId: string;
    description?: string;
    assigneeId?: string;
    stateId?: string;
    priority?: number;
    projectId?: string;
    labels?: string[];
  }
  
  export interface IssueFilterProps {
    assigneeId?: string;
    creatorId?: string;
    projectId?: string;
    stateId?: string;
    priority?: number;
    createdAfter?: string;
    createdBefore?: string;
  }
  
  export interface Team {
    id: string;
    name: string;
    description?: string;
    key: string;
    createdAt: string;
    updatedAt: string;
  }
  
  export interface TeamList {
    teams: Team[];
    cursor?: string;
    hasNextPage?: boolean;
    totalCount?: number;
  }
  
  export interface IssueUpdateProps {
    title?: string;
    description?: string;
    assigneeId?: string;
    stateId?: string;
    priority?: number;
    projectId?: string;
    labels?: string[];
  }

  export interface PaginationParams {
    cursor?: string;
    maxResults?: number;
  }

  export interface WorkflowState {
    id: string;
    name: string;
    color: string;
    type: string;
    position: number;
    team_id: string;
    team_key: string;
    team_name: string;
  }

  export interface WorkflowStateList {
    states: WorkflowState[];
    cursor?: string;
  }
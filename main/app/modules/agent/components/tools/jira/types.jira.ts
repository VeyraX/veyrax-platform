export interface User {
    id: string;
    name: string;
    email?: string;
  }
  
  export interface Issue {
    id: string;
    key: string;
    summary: string;
    description?: string;
    status: {
      name: string;
      statusCategory: {
        name: string;
      };
    };
    priority?: {
      id: string;
      name: string;
      iconUrl?: string;
    };
    assignee?: {
      name?: string;
      displayName?: string;
      emailAddress?: string;
      accountId: string;
    };
    reporter: {
      displayName: string;
      emailAddress: string;
      accountId: string;
    };
    created: string;
    updated: string;
    labels?: string[];
    projectId: string;
    projectKey: string;
    issueType: {
      id: string;
      name: string;
      iconUrl?: string;
    };
    url: string;
  }
  
  export interface Project {
    id: string;
    key: string;
    name: string;
    description?: string;
    lead?: User;
    url?: string;
  }
  
  export interface Status {
    id: string;
    name: string;
    statusCategory: {
      id: string;
      key: string;
      name: string;
      colorName: string;
    };
  }
  
  export interface Priority {
    id: string;
    name: string;
    description?: string;
    iconUrl?: string;
  }
  
  export interface IssueType {
    id: string;
    name: string;
    description?: string;
    iconUrl?: string;
    subtask: boolean;
  }
  
  export interface Field {
    id: string;
    name: string;
    custom: boolean;
    schema?: {
      type: string;
      customId?: number;
    };
  }
  
  export interface IssueList {
    issues: Issue[];
    total: number;
    startAt: number;
    maxResults: number;
  }
  
  export interface ProjectList {
    projects: Project[];
  }
  
  export interface StatusList {
    statuses: Status[];
  }
  
  export interface PriorityList {
    priorities: Priority[];
  }
  
  export interface IssueTypeList {
    issueTypes: IssueType[];
  }
  
  export interface FieldList {
    fields: Field[];
  }

export interface JiraUser {
  accountId: string;
  email?: string;
  displayName: string;
  active: boolean;
}

export interface JiraUserList {
  users: JiraUser[];
}
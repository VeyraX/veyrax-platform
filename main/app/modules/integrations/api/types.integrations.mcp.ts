export interface Tool {
  id: string;
  name: string;
  description: string;
}

export interface EnvVariable {
  key: string;
  value: string;
}

export interface McpDetails {
  id: string;
  image_name: string;
  repo_url: string;
  name: string;
  description: string | null;
  input_schema: any[];
  env: Record<string, string>;
  metadata?: Record<string, any>;
  created_at: string;
  author_user_id: string | null;
  last_commit_hash?: string | null;
  is_approved?: boolean;
}

export interface SchemaProperty {
  type?: string;
  description?: string;
  title?: string;
  default?: any;
  anyOf?: any[];
  $ref?: string;
}

export interface ParameterObject {
  name: string;
  type: string;
  required: boolean;
  description: string;
  isRef: boolean;
  refName: string | null;
  default?: string;
  nestedParams?: ParameterObject[];
}

export interface McpDeployment {
  id: string;
  deployment_id?: string;
  repo_id: string;
  status: 'pending' | 'building' | 'success' | 'failed';
  build_logs: string | null;
  error: string | null;
  created_at: string;
  commit_hash: string | null;
}

export interface GitHubRepoInfo {
  stars: number;
  forks: number;
  created_at: string;
  updated_at: string;
  owner: string;
  name: string; 
  avatar_url?: string;
  description?: string;
  license?: {
    name: string;
    spdx_id: string;
  };
}

export interface McpViewPageProps {
  mcpId?: string;
  repoName?: string;
  githubUrl?: string;
  imageName?: string;
}

export interface UserMcpEnvironment {
  id?: string;
  user_id: string;
  repo_id: string;
  env: Record<string, string>;
  status?: 'connected' | 'connecting' | 'failed' | 'disconnected';
  error?: string | null;
  process_id?: string;
}

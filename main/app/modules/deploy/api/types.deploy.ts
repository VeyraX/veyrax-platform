export interface Tool {
  id: string;
  name: string;
  description: string;
}

export interface DeployMetrics {
  monthlyToolCalls: string;
  license: string;
  local: string;
  published: string;
}

export interface McpInfo {
  id: string;
  repoName: string;
  githubUrl: string;
  status: 'Active' | 'Inactive';
}

export interface RepositoryMetaRequest {
  repo_url: string;
}

export interface RepositoryMetaResponse {
  env_variables: Record<string, string>;
  name?: string;
  description?: string;
} 
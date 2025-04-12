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

export interface EnvVariablesRequest {
  repo_url: string;
}

export interface EnvVariable {
  name: string;
  default_value?: string;
  required: boolean;
}

export interface EnvVariablesResponse {
  env_variables: Record<string, string>;
} 
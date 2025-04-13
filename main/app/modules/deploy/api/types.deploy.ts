export interface RepositoryMetaRequest {
  repo_url: string;
}

export interface RepositoryMetaResponse {
  env_variables: Record<string, string>;
  name?: string;
  description?: string;
  repository_id?: string;
  last_commit_hash?: string;
}

export interface DeployMCPRequest {
  repo_url: string;
  image_name: string;
  repository_id: string;
  commit_hash?: string;
}

export interface DeployMCPResponse {
  status: string;
  dockerfile?: string;
  dockerfile_base64?: string;
  github_workflow_url?: string;
  message?: string;
}

export interface ExternalMcpRepository {
  id: string;
  name: string;
  metadata: {
    url?: string;
    external_url?: string;
    github_stars?: number;
    package_name?: string;
    source_code_url?: string;
    package_registry?: string;
    short_description?: string;
    package_download_count?: number;
    ai_generated_description?: string;
  };
} 
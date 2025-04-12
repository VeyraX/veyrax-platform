export interface RepositoryMetaRequest {
  repo_url: string;
}

export interface RepositoryMetaResponse {
  env_variables: Record<string, string>;
  name?: string;
  description?: string;
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
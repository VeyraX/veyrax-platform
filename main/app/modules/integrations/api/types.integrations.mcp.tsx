export interface Tool {
  id: string;
  name: string;
  description: string;
}

export interface McpDetails {
  id: string;
  image_name: string;
  repo_url: string;
  name: string;
  description: string | null;
  input_schema: any[];
  env: Record<string, string>;
  created_at: string;
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

export interface McpViewPageProps {
  mcpId?: string;
  repoName?: string;
  githubUrl?: string;
  imageName?: string;
}

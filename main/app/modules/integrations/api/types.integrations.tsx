export interface Provider {
  id: string;
  name: string;
  description: string;
  logo_url?: string;
  provider_tag: string;
  auth_method: 'oauth' | 'api_key' | 'api_key_with_base' | 'db_access' | 'none' | 'custom';
  scopes?: {
    scope: string;
    scope_name: string;
  }[];
  auth_schema?: CustomAuthField[];
  input_schema?: string | object;
  output_schema?: string | object;
  created_at?: string | number;
  is_enabled?: boolean;
  ui_component?: string | object;
  categories?: string;
}

export interface DbConfig {
  host?: string;
  port?: string;
  dbname?: string;
  user: string;
  password: string;
  schema: string;
  warehouse?: string;
  account?: string;
  role?: string;
  database?: string;
}

export interface UserDbAccess {
  id: string;
  user_id: string;
  provider_id: string;
  credentials: string;
}

export interface IntegrationCardProps extends Provider {
  connected: boolean;
  isPopular?: boolean;
  hasIndex: false;
  indexStatus: null;
  lastSyncDate?: null;
  processedEntities?: null;
  onConnectionChange?: () => void;
  isPublic?: boolean;
  onShowSettings?: (provider: Provider) => void;
}

export interface UserProvider {
  id: string;
  user_id: string;
  provider_id: string;
}

export interface UserProviderApiKey {
  id: string;
  created_at: string;
  api_key: string;
  user_id: string;
  provider_id: string;
}
  
export interface ManageDialogProps {
  provider: Provider & {
    connected: boolean;
    hasIndex: false;
    indexStatus: null;
    lastSyncDate?: null;
    processedEntities?: null;
  };
  open: boolean;
  onClose: () => void;
  onUpdate: () => void;
}

export interface ProviderEndpoint {
  name: string;
  functionId: string;
  description: string;
  paramCount: number;
}

export interface ProviderDetails {
  provider: Provider;
  totalEndpoints: number;
  totalParameters: number;
  totalComponents: number;
  endpointsList: ProviderEndpoint[];
  exampleSchema?: any;
}

export interface IntegrationDetailSummaryProps {
  providerDetails: ProviderDetails;
}

export interface ComponentData {
  name: string;
  jsx?: string;
  component?: {
    jsx: string;
  };
  exampleProps?: {
    data: any;
  };
  description?: string;
  related_endpoints?: string[];
  version?: string;
}

export interface SchemaProperty {
  type?: string;
  title?: string;
  description?: string;
  default?: any;
  $ref?: string;
  anyOf?: Array<{type?: string | null}>;
  properties?: Record<string, SchemaProperty>;
  items?: {
    type?: string;
    properties?: Record<string, SchemaProperty>;
  };
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

export interface ApiKeyWithBaseConfig {
  api_key: string;
  base_url: string;
}

export interface CustomAuthField {
  key: string;
  label: string;
  type: string;
  required: boolean;
  placeholder?: string;
  sensitive?: boolean;
  options?: { label: string, value: string }[];
}
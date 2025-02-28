export interface Provider {
  id: string;
  name: string;
  description: string;
  logo_url?: string;
  provider_tag: string;
  auth_method: 'oauth' | 'api_key';
  scopes?: {
    scope: string;
    scope_name: string;
  }[];
  has_index_capability?: boolean;
  input_schema?: string | object;
  output_schema?: string | object;
  created_at?: string | number;
  is_enabled?: boolean;
  ui_component?: string | object;
}

export interface IntegrationCardProps extends Provider {
  connected: boolean;
  hasIndex: boolean;
  indexStatus: 'synced' | 'syncing' | 'failed' | 'pending' | null;
  lastSyncDate?: string;
  processedEntities?: number;
  onConnectionChange?: () => void;
  onShowSettings?: (provider: Provider) => void;
}

export interface UserProvider {
  id: string;
  user_id: string;
  provider_id: string;
}
  
export interface ManageDialogProps {
  provider: Provider & {
    connected: boolean;
    hasIndex: boolean;
    indexStatus: 'synced' | 'syncing' | 'failed' | 'pending' | null;
    lastSyncDate?: string;
    processedEntities?: number;
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
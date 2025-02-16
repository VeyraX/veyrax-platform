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
}

export interface UserOAuthToken {
  user_id: string;
  provider_id: string;
  access_token: string;
  refresh_token: string;
}

export interface IntegrationCardProps extends Provider {
  connected: boolean;
  hasIndex: boolean;
  onConnectionChange?: () => void;
  onShowSettings?: (provider: Provider) => void;
}

export interface UserProvider {
  id: string;
  user_id: string;
  provider_id: string;
}
  
export interface Provider {
  id: string;
  name: string;
  description: string;
  logo_url?: string;
  provider_tag: string;
  auth_method: 'oauth' | 'api_key';
}

export interface UserOAuthToken {
  user_id: string;
  provider_id: string;
  access_token: string;
  refresh_token: string;
}


export interface IntegrationCardProps {
  id: string;
  name: string;
  description: string;
  logo_url?: string;
  provider_tag: string;
  connected: boolean;
  auth_method: string;
  onConnectionChange?: () => void;
}
  
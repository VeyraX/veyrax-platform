export interface Provider {
  id: string;
  name: string;
  description: string;
  logo?: string;
  provider_tag: string;
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
  logo?: string;
  provider_tag: string;
  connected: boolean;
  onConnectionChange?: () => void;
}
  
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
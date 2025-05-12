import { McpDetails, McpDeployment, GitHubRepoInfo, UserMcpEnvironment } from './types.integrations.mcp';
import { createClient } from '@/lib/utils/supabase/client';
import { getCacheItem, setCacheItem, deleteCacheItem, CacheStore, clearUserStoreCache } from '@/lib/utils/index-db';

const supabase = createClient();

const CACHE_KEYS = {
  MCP_REPOSITORIES: 'mcp_repositories',
};

export const getAllMcpRepositories = async (): Promise<McpDetails[]> => {
  try {
    const response = await fetch('/api/integrations/mcp/repositories')
    
    if (!response.ok) {
      console.error(`Error fetching MCP repositories: ${response.status}`)
      return []
    }
    
    const data = await response.json()
    
    if (!Array.isArray(data)) {
      console.error('Invalid response format from MCP repositories API')
      return []
    }
    
    return data as McpDetails[]
  } catch (error) {
    console.error('Error in getAllMcpRepositories:', error)
    return []
  }
};

export const getMcpDetailsByImageName = async (imageName: string): Promise<McpDetails | null> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, metadata, created_at, author_user_id, last_commit_hash')
      .eq('image_name', imageName);
    
    if (error) {
      return null;
    }
    
    if (!data || data.length === 0) {
      return null;
    }
    
    return data[0] as McpDetails;
  } catch (error) {
    return null;
  }
};

export const getMcpDeployments = async (repoId: string): Promise<McpDeployment[]> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repository_deployments')
      .select('id, repo_id, status, build_logs, error, created_at, commit_hash, deployment_id')
      .eq('repo_id', repoId)
      .order('created_at', { ascending: false });

    if (error || !data) {
      return [];
    }

    return data as McpDeployment[];
  } catch (error) {
    return [];
  }
};

export const getMcpDeploymentById = async (deploymentId: string): Promise<McpDeployment | null> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repository_deployments')
      .select('id, repo_id, status, build_logs, error, created_at, commit_hash, deployment_id')
      .eq('id', deploymentId)
      .single();

    if (error || !data) {
      return null;
    }

    return data as McpDeployment;
  } catch (error) {
    return null;
  }
};

export const getGitHubRepoInfo = async (repoUrl: string): Promise<GitHubRepoInfo | null> => {
  try {
    if (!repoUrl || !repoUrl.includes('github.com')) {
      return null;
    }
    
    const response = await fetch('/api/integrations/mcp/github-repo-info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repoUrl })
    });
    
    if (!response.ok) {
      return null;
    }
    
    const data = await response.json();
    return data as GitHubRepoInfo;
  } catch (error) {
    return null;
  }
};

export const getUserMcpEnvironment = async (repositoryId: string): Promise<UserMcpEnvironment | null> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user || !user.id) {
      return null;
    }
    
    const { data, error } = await supabase
      .from('users_mcp')
      .select('*')
      .eq('user_id', user.id)
      .eq('repo_id', repositoryId)
      .single();
    
    if (error) {
      return null;
    }
    
    return data as UserMcpEnvironment;
  } catch (error) {
    return null;
  }
};

export const disconnectUserMcp = async (repositoryId: string): Promise<boolean> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user || !user.id) {
      return false;
    }
    
    const { error } = await supabase
      .from('users_mcp')
      .delete()
      .eq('user_id', user.id)
      .eq('repo_id', repositoryId);
    
    if (error) {
      return false;
    }
    
    await clearUserStoreCache(CacheStore.INTEGRATIONS, user.id);
    
    return true;
  } catch (error) {
    return false;
  }
};

export const enableMcpIntegration = async (
  imageName: string, 
  environmentVariables?: Record<string, string>,
  encrypted_api_key?: string, 
  code?: string,
  repository_id?: string,
  metadata?: Record<string, any>
): Promise<boolean> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    const response = await fetch('/api/integrations/mcp', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        image_name: imageName,
        env: environmentVariables,
        user_id: user?.id,
        encrypted_api_key,
        status: 'connecting',
        code,
        repository_id,
        metadata
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to enable MCP integration');
    }
    
    const data = await response.json();
    if (!data.success) {
      throw new Error(data.error || 'Failed to enable MCP integration');
    }
    
    let repositoryId = repository_id || data.repository_id;
    
    if (!repositoryId) {
      const mcpDetails = await getMcpDetailsByImageName(imageName);
      repositoryId = mcpDetails?.id;
    }
    
    if (repositoryId) {
      try {
        let token;
        
        if (encrypted_api_key) {
          token = encrypted_api_key;
        } else {
          const { data: { session } } = await supabase.auth.getSession();
          token = session?.access_token;
          
          if (!token) {
            throw new Error('No auth token available');
          }
        }
        
        const connectResponse = await fetch('/api/integrations/mcp/connect', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            repository_id: repositoryId,
            code,
            encrypted_api_key,
            auth_token: token,
            metadata
          })
        });
        
        if (!connectResponse.ok) {
          let errorMessage = `Failed to connect MCP container: ${connectResponse.statusText}`;
          try {
            const errorData = await connectResponse.json();
            console.error('Error connecting user MCP container:', errorData);
            if (errorData.error) {
              errorMessage = errorData.error;
            }
          } catch (e) {
          }
          throw new Error(errorMessage);
        }
      } catch (containerError) {
        console.warn("MCP integration enabled, but container connection failed:", containerError);
      }
    }
    
    if (user?.id) {
      await clearUserStoreCache(CacheStore.INTEGRATIONS, user.id);
    }
    
    return true;
  } catch (error) {
    console.error('Error enabling MCP integration:', error);
    return false;
  }
};

export const getSingleMcpRepositoryData = async (repositoryId: string) => {
  try {
    const response = await fetch('/api/integrations/mcp/single-repository', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ repositoryId })
    })
    
    if (!response.ok) {
      console.error(`Error fetching single MCP repository: ${response.status}`)
      return null
    }
    
    const result = await response.json()
    
    const userEnvironment = await getUserMcpEnvironment(repositoryId)
    result.userEnvironment = userEnvironment
    result.isConnected = !!userEnvironment
    
    return result
  } catch (error) {
    console.error('Error fetching single MCP repository data:', error)
    return null
  }
};

export const getUserApiKey = async (): Promise<string | null> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      return null;
    }
    
    const { data, error } = await supabase
      .from('users_api_keys')
      .select('api_key')
      .eq('user_id', user.id)
      .single();
    
    if (error || !data) {
      console.error('Error fetching user API key:', error);
      return null;
    }
    
    return data.api_key;
  } catch (error) {
    console.error('Error fetching user API key:', error);
    return null;
  }
};

export const getAllMcpRepositoriesFormatted = async (isPublic = false): Promise<Array<{
  mcpDetails: McpDetails;
  repoInfo: GitHubRepoInfo | null;
  userEnvironment: UserMcpEnvironment | null;
  isConnected: boolean;
}>> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    const userId = user?.id;
    
    if (!isPublic && userId) {
      const cachedData = await getCacheItem<Array<{
        mcpDetails: McpDetails;
        repoInfo: GitHubRepoInfo | null;
        userEnvironment: UserMcpEnvironment | null;
        isConnected: boolean;
      }>>(
        CacheStore.INTEGRATIONS,
        CACHE_KEYS.MCP_REPOSITORIES, 
        userId
      );
      
      if (cachedData) {
        return cachedData;
      }
    }
    
    const response = await fetch('/api/integrations/mcp/repositories')
    
    if (!response.ok) {
      return []
    }
    
    const mcpData = await response.json()
    
    if (!Array.isArray(mcpData)) {
      return []
    }
    
    let userConnections: Record<string, UserMcpEnvironment> = {};
    
    if (!isPublic) {
      try {
        if (userId) {
          const { data } = await supabase
            .from('users_mcp')
            .select('*')
            .eq('user_id', userId);
            
          if (data && data.length > 0) {
            userConnections = data.reduce((acc, connection) => {
              acc[connection.repo_id] = connection;
              return acc;
            }, {} as Record<string, UserMcpEnvironment>);
          }
        }
      } catch (error) {
        console.error('Error fetching user MCP connections:', error);
      }
    }
    
    const formattedRepositories = mcpData.map((repo: McpDetails) => {
      const stars = repo.metadata?.stars ? Number(repo.metadata.stars) : 0;
      
      const repoInfo: GitHubRepoInfo | null = stars ? {
        stars,
        forks: 0,
        created_at: repo.created_at,
        updated_at: repo.created_at,
        owner: '',
        name: repo.name
      } : null;
      
      return {
        mcpDetails: repo,
        repoInfo,
        userEnvironment: userConnections[repo.id] || null,
        isConnected: !!userConnections[repo.id]
      };
    });
    
    const result = formattedRepositories.sort((a, b) => (b.repoInfo?.stars || 0) - (a.repoInfo?.stars || 0));
    
    if (!isPublic && userId) {
      await setCacheItem(
        CacheStore.INTEGRATIONS,
        CACHE_KEYS.MCP_REPOSITORIES, 
        userId, 
        result
      );
    }
    
    return result;
  } catch (error) {
    return [];
  }
};

import { McpDetails, McpDeployment, GitHubRepoInfo, UserMcpEnvironment } from './types.integrations.mcp';
import { createClient } from '@/lib/utils/supabase/client';

const supabase = createClient();

const githubRepoCache = new Map<string, { data: GitHubRepoInfo | null, timestamp: number }>();
const CACHE_TTL = 24 * 3600 * 1000;

const pendingRequests = new Map<string, Promise<GitHubRepoInfo | null>>();

export const getAllMcpRepositories = async (): Promise<McpDetails[]> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, metadata, created_at, author_user_id, last_commit_hash')
      .eq('is_approved', true)
      .order('created_at', { ascending: false });
    
    if (error || !data) {
      console.error('Error fetching all MCP repositories:', error);
      return [];
    }
    
    return data as McpDetails[];
  } catch (error) {
    console.error('Error fetching all MCP repositories:', error);
    return [];
  }
};

export const getMcpDetailsByImageName = async (imageName: string): Promise<McpDetails | null> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, metadata, created_at, author_user_id, last_commit_hash')
      .eq('image_name', imageName);
    
    if (error) {
      console.error('Error fetching MCP details:', error);
      return null;
    }
    
    if (!data || data.length === 0) {
      console.error('MCP details not found for image name:', imageName);
      return null;
    }
    
    return data[0] as McpDetails;
  } catch (error) {
    console.error('Error fetching MCP details:', error);
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
      console.error('Error fetching MCP deployments:', error);
      return [];
    }

    return data as McpDeployment[];
  } catch (error) {
    console.error('Error fetching MCP deployments:', error);
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
      console.error('Error fetching MCP deployment:', error);
      return null;
    }

    return data as McpDeployment;
  } catch (error) {
    console.error('Error fetching MCP deployment:', error);
    return null;
  }
};

export const getGitHubRepoInfo = async (repoUrl: string): Promise<GitHubRepoInfo | null> => {
  try {
    if (!repoUrl || !repoUrl.includes('github.com')) {
      return null;
    }
    
    const url = new URL(repoUrl);
    const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
    
    if (pathSegments.length < 2) {
      return null;
    }
    
    const owner = pathSegments[0];
    const repo = pathSegments[1];
    
    const normalizedUrl = `https://github.com/${owner}/${repo}`;
    
    if (githubRepoCache.has(normalizedUrl)) {
      const cached = githubRepoCache.get(normalizedUrl)!;
      const now = Date.now();
      
      if (now - cached.timestamp < CACHE_TTL) {
        return cached.data;
      }
    }
    
    if (pendingRequests.has(normalizedUrl)) {
      return pendingRequests.get(normalizedUrl)!;
    }
    
    const requestPromise = (async () => {
      try {
        const response = await fetch('/api/github/repo', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ repoUrl: normalizedUrl })
        });
        
        if (!response.ok) {
          return null;
        }
        
        const data = await response.json();
        
        githubRepoCache.set(normalizedUrl, { 
          data: data as GitHubRepoInfo, 
          timestamp: Date.now() 
        });
        
        return data as GitHubRepoInfo;
      } catch (error) {
        return null;
      } finally {
        pendingRequests.delete(normalizedUrl);
      }
    })();
    
    pendingRequests.set(normalizedUrl, requestPromise);
    
    return requestPromise;
  } catch (error) {
    console.error("Error parsing GitHub URL:", error);
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
    
    if (error || !data) {
      return null;
    }
    
    return data as UserMcpEnvironment;
  } catch (error) {
    console.error('Error fetching user MCP environment:', error);
    return null;
  }
};

export const disconnectUserMcp = async (repositoryId: string): Promise<boolean> => {
  try {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user || !user.id) {
      throw new Error('User not authenticated');
    }
    
    const { error } = await supabase
      .from('users_mcp')
      .delete()
      .eq('user_id', user.id)
      .eq('repo_id', repositoryId);
    
    if (error) {
      console.error('Error disconnecting user MCP:', error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error disconnecting user MCP:', error);
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
    
    return true;
  } catch (error) {
    console.error('Error enabling MCP integration:', error);
    return false;
  }
};

export const getSingleMcpRepositoryData = async (repositoryId: string) => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, metadata, created_at, author_user_id, last_commit_hash')
      .eq('id', repositoryId)
      .single();
    
    if (error || !data) {
      console.error('Error fetching single MCP repository:', error);
      return null;
    }
    
    const mcpDetails = data as McpDetails;
    
    const repoInfo = (!mcpDetails.metadata?.stars && mcpDetails.repo_url) ? 
      await getGitHubRepoInfo(mcpDetails.repo_url) : null;
    
    const userEnvironment = await getUserMcpEnvironment(repositoryId);
    
    return {
      mcpDetails,
      repoInfo,
      userEnvironment,
      isConnected: !!userEnvironment
    };
  } catch (error) {
    console.error('Error fetching single MCP repository data:', error);
    return null;
  }
};

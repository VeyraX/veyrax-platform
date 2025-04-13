import { McpDetails, McpDeployment, GitHubRepoInfo, UserMcpEnvironment } from './types.integrations.mcp';
import { createClient } from '@/lib/utils/supabase/client';

const supabase = createClient();

export const getAllMcpRepositories = async (): Promise<McpDetails[]> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, created_at, author_user_id, last_commit_hash')
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
      .select('id, image_name, repo_url, name, description, input_schema, env, created_at, author_user_id, last_commit_hash')
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
    
    const normalizedUrl = repoUrl.endsWith('/') ? repoUrl.slice(0, -1) : repoUrl;
    const parts = normalizedUrl.split('/');
    const repo = parts[parts.length - 1];
    const owner = parts[parts.length - 2];
    
    if (!owner || !repo) {
      console.error('Could not extract owner or repo from URL:', repoUrl);
      return null;
    }

    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
      headers: {
        ...(process.env.GITHUB_TOKEN ? { 'Authorization': `token ${process.env.GITHUB_TOKEN}` } : {}),
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!response.ok) {
      console.error('Error fetching GitHub repo info:', response.statusText);
      return null;
    }
    
    const data = await response.json();

    console.log('GitHub repo info:', data);
    return {
      stars: data.stargazers_count,
      forks: data.forks_count,
      created_at: data.created_at,
      updated_at: data.updated_at,
      owner: owner,
      name: repo,
      avatar_url: data.owner?.avatar_url,
      description: data.description,
      license: data.license ? {
        name: data.license.name,
        spdx_id: data.license.spdx_id
      } : undefined
    };
  } catch (error) {
    console.error('Error fetching GitHub repo info:', error);
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

export const connectUserMcpContainer = async (
  repositoryId: string,
  encrypted_api_key?: string,
  code?: string
): Promise<boolean> => {
  try {
    let token;
    
    if (encrypted_api_key) {
      token = encrypted_api_key;
    } else {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user || !user.id) {
        throw new Error('User not authenticated');
      }
      
      const { data: { session } } = await supabase.auth.getSession();
      token = session?.access_token;
      
      if (!token) {
        throw new Error('No auth token available');
      }
    }
    
    const response = await fetch(`${process.env.NEXT_PUBLIC_VEYRAX_DEPLOY_BASE_URL}/repo/connect`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        repository_id: repositoryId,
        code,
        encrypted_api_key
      })
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      console.error('Error connecting user MCP container:', errorData);
      throw new Error(`Failed to connect MCP container: ${response.statusText}`);
    }
    
    return true;
  } catch (error) {
    console.error('Error connecting user MCP container:', error);
    return false;
  }
};

export const enableMcpIntegration = async (
  imageName: string, 
  environmentVariables?: Record<string, string>,
  encrypted_api_key?: string, 
  code?: string
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
        code
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
    
    return true;
  } catch (error) {
    console.error('Error enabling MCP integration:', error);
    return false;
  }
};

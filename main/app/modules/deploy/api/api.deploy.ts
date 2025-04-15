import { RepositoryMetaResponse, ExternalMcpRepository, DeployMCPResponse } from "./types.deploy";
import { createClient } from '@/lib/utils/supabase/client';

const supabase = createClient();

export const getLatestCommitHash = async (repoUrl: string): Promise<string | null> => {
  try {
    const url = new URL(repoUrl.trim());
    const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
    
    if (pathSegments.length < 2) {
      return null;
    }
    
    const owner = pathSegments[0];
    const repo = pathSegments[1].replace('.git', '');

    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/commits/HEAD`);
    
    if (!response.ok) {
      return null;
    }
    
    const data = await response.json();
    return data.sha;
  } catch (error) {
    console.error('Error fetching latest commit:', error);
    return null;
  }
};

const getRepositoryMetaFromDb = async (repoUrl: string, latestCommitHash?: string | null): Promise<RepositoryMetaResponse | null> => {
  try {
    const url = new URL(repoUrl.trim());
    const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
    
    if (pathSegments.length < 2) {
      return null;
    }
    
    const owner = pathSegments[0];
    const repo = pathSegments[1].replace('.git', '');
    
    const normalizedUrl = `https://github.com/${owner}/${repo}`;
    
    const { data: existingRepo, error } = await supabase
      .from('mcp_repositories')
      .select('env, last_commit_hash, name, description, is_approved, image_name')
      .eq('repo_url', normalizedUrl)
      .single();
    
    if (error || !existingRepo || !existingRepo.env) {
      return null;
    }
    
    if (latestCommitHash && existingRepo.last_commit_hash !== latestCommitHash) {
      return null;
    }
    
    return {
      env_variables: existingRepo.env,
      name: existingRepo.name,
      description: existingRepo.description,
      is_approved: existingRepo.is_approved,
      image_name: existingRepo.image_name
    };
  } catch (error) {
    console.error('Error fetching from database:', error);
    return null;
  }
};

const getRepositoryMetaFromApi = async (repoUrl: string): Promise<RepositoryMetaResponse> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/mcp_deployment/generate-repository-meta`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_url: repoUrl,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch repository metadata: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching from API:', error);
    throw error;
  }
};

export const fetchRepositoryMeta = async (
  repoUrl: string
): Promise<RepositoryMetaResponse & { repository_id?: string, last_commit_hash?: string }> => {
  try {
    const latestCommitHash = await getLatestCommitHash(repoUrl);
    const dbResult = await getRepositoryMetaFromDb(repoUrl, latestCommitHash);
    
    if (dbResult) {
      const { data: repoData } = await supabase
        .from('mcp_repositories')
        .select('id, last_commit_hash, is_approved, image_name')
        .eq('repo_url', repoUrl)
        .single();
      
      return {
        ...dbResult,
        repository_id: repoData?.id,
        last_commit_hash: repoData?.last_commit_hash
      };
    }
    
    const apiResult = await getRepositoryMetaFromApi(repoUrl);
    
    try {
      const { data: { user } } = await supabase.auth.getUser();
      const currentUserId = user?.id || null;
      
      const { data: insertData, error } = await supabase
        .from('mcp_repositories')
        .upsert({
          repo_url: repoUrl,
          env: apiResult.env_variables,
          last_commit_hash: latestCommitHash,
          name: apiResult.name,
          description: apiResult.description,
          author_user_id: currentUserId
        }, {
          onConflict: 'repo_url'
        })
        .select('id, last_commit_hash')
        .single();
      
      if (error) {
        console.error('Error saving to database:', error);
        return apiResult;
      }
      
      return {
        ...apiResult,
        repository_id: insertData?.id,
        last_commit_hash: insertData?.last_commit_hash
      };
    } catch (saveError) {
      console.error('Error saving to database:', saveError);
      return apiResult;
    }
  } catch (error) {
    console.error('Error fetching repository metadata:', error);
    throw error;
  }
};

export const checkMcpExists = async (repoUrl: string): Promise<boolean | { exists: boolean, is_approved: boolean, image_name: string, env: Record<string, string> }> => {
  try {
    const url = new URL(repoUrl.trim());
    const pathSegments = url.pathname.split('/').filter(segment => segment.length > 0);
    
    if (pathSegments.length < 2) {
      return false;
    }
    
    const owner = pathSegments[0];
    const repo = pathSegments[1].replace('.git', '');
    
    const normalizedUrl = `https://github.com/${owner}/${repo}`;
    
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, is_approved, image_name, env')
      .eq('repo_url', normalizedUrl)
      .single();
    
    if (error || !data) {
      return false;
    }
    
    return {
      exists: true,
      is_approved: !!data.is_approved,
      image_name: data.image_name || '',
      env: data.env || {}
    };
  } catch (error) {
    console.error('Error checking MCP existence:', error);
    return false;
  }
};

export const fetchExternalMcpRepositories = async (
  page: number = 1,
  pageSize: number = 6
): Promise<{ data: ExternalMcpRepository[], count: number }> => {
  try {
    const { count, error: countError } = await supabase
      .from('external_mcp_repositories')
      .select('*', { count: 'exact', head: true });
    
    if (countError) {
      console.error('Error counting external MCP repositories:', countError);
      return { data: [], count: 0 };
    }
    
    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;
    
    const { data, error } = await supabase
      .from('external_mcp_repositories')
      .select('*')
      .order('metadata->github_stars', { ascending: false })
      .range(from, to);
    
    if (error) {
      console.error('Error fetching external MCP repositories:', error);
      return { data: [], count: 0 };
    }
    
    return { 
      data: data || [], 
      count: count || 0 
    };
  } catch (error) {
    console.error('Error fetching external MCP repositories:', error);
    return { data: [], count: 0 };
  }
};

export const deployMcpRepository = async (
  repoUrl: string,
  imageName: string,
  repositoryId: string,
  commitHash?: string
): Promise<DeployMCPResponse> => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    const authToken = session?.access_token;
    
    if (!authToken) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/mcp_deployment/push-mcp-to-dockerhub`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        repo_url: repoUrl,
        image_name: imageName,
        repository_id: repositoryId,
        commit_hash: commitHash
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(`Failed to deploy MCP: ${errorData.detail || response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error deploying MCP:', error);
    throw error;
  }
};

export const updateMcpImageName = async (repositoryId: string, imageName: string): Promise<boolean> => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    const authToken = session?.access_token;
    
    if (!authToken) {
      throw new Error('Authentication required');
    }

    const { error } = await supabase
      .from('mcp_repositories')
      .update({ image_name: imageName })
      .eq('id', repositoryId);
    
    if (error) {
      console.error('Error updating MCP image name:', error);
      return false;
    }
    
    return true;
  } catch (error) {
    console.error('Error updating MCP image name:', error);
    return false;
  }
};


export const CreateUserMCPConnection = async (
  imageName: string, 
  environmentVariables?: Record<string, string>,
  encrypted_api_key?: string, 
  code?: string,
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
    console.error('Error creating user MCP connection:', error);
    return false;
  }
};
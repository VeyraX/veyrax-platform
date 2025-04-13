import { McpDetails, McpDeployment, GitHubRepoInfo } from './types.integrations.mcp';
import { createClient } from '@/lib/utils/supabase/client';

const supabase = createClient();

export const getMcpDetailsByImageName = async (imageName: string): Promise<McpDetails | null> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, created_at, author_user_id')
      .eq('image_name', imageName)
      .single();
    
    if (error || !data) {
      console.error('Error fetching MCP details:', error);
      return null;
    }
    
    return data as McpDetails;
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

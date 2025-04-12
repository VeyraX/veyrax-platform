import { RepositoryMetaResponse } from "./types.deploy";
import { createClient } from '@/lib/utils/supabase/client';

const supabase = createClient();

export const getLatestCommitHash = async (repoUrl: string): Promise<string | null> => {
  try {
    const url = repoUrl.trim();
    const parts = url.split('/');
    const owner = parts[parts.length - 2];
    const repo = parts[parts.length - 1].replace('.git', '');

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
    const { data: existingRepo, error } = await supabase
      .from('mcp_repositories')
      .select('env, last_commit_hash, name, description')
      .eq('repo_url', repoUrl)
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
      description: existingRepo.description
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
): Promise<RepositoryMetaResponse> => {
  try {
    const latestCommitHash = await getLatestCommitHash(repoUrl);
    const dbResult = await getRepositoryMetaFromDb(repoUrl, latestCommitHash);
    if (dbResult) {
      return dbResult;
    }
    
    const apiResult = await getRepositoryMetaFromApi(repoUrl);
    
    try {
      await supabase
        .from('mcp_repositories')
        .upsert({
          repo_url: repoUrl,
          env: apiResult.env_variables,
          last_commit_hash: latestCommitHash,
          name: apiResult.name,
          description: apiResult.description
        }, {
          onConflict: 'repo_url'
        });
    } catch (saveError) {
    }
    
    return apiResult;
  } catch (error) {
    console.error('Error fetching repository metadata:', error);
    throw error;
  }
};

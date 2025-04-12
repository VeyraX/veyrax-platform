import { EnvVariablesResponse } from "./types.deploy";
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

const getEnvVariablesFromDb = async (repoUrl: string, latestCommitHash?: string | null): Promise<EnvVariablesResponse | null> => {
  try {
    const { data: existingRepo, error } = await supabase
      .from('mcp_repositories')
      .select('env, last_commit_hash')
      .eq('repo_url', repoUrl)
      .single();
    
    if (error || !existingRepo || !existingRepo.env) {
      return null;
    }
    
    if (latestCommitHash && existingRepo.last_commit_hash !== latestCommitHash) {
      return null;
    }
    
    return {
      env_variables: existingRepo.env
    };
  } catch (error) {
    console.error('Error fetching from database:', error);
    return null;
  }
};

const getEnvVariablesFromApi = async (repoUrl: string): Promise<EnvVariablesResponse> => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/mcp_deployment/generate-env-variables`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        repo_url: repoUrl,
      }),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch environment variables: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching from API:', error);
    throw error;
  }
};

export const fetchEnvironmentVariables = async (
  repoUrl: string
): Promise<EnvVariablesResponse> => {
  try {
    const latestCommitHash = await getLatestCommitHash(repoUrl);
    const dbResult = await getEnvVariablesFromDb(repoUrl, latestCommitHash);
    if (dbResult) {
      return dbResult;
    }
    
    const apiResult = await getEnvVariablesFromApi(repoUrl);
    
    try {
      await supabase
        .from('mcp_repositories')
        .upsert({
          repo_url: repoUrl,
          env: apiResult.env_variables,
          last_commit_hash: latestCommitHash
        }, {
          onConflict: 'repo_url'
        });
    } catch (saveError) {
    }
    
    return apiResult;
  } catch (error) {
    console.error('Error fetching environment variables:', error);
    throw error;
  }
};

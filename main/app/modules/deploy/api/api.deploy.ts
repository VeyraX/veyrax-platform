import { RepositoryMetaResponse, ExternalMcpRepository } from "./types.deploy";
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

export const checkMcpExists = async (repoUrl: string): Promise<boolean> => {
  try {
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id')
      .eq('repo_url', repoUrl)
      .single();
    
    return !!data;
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
    // Получаем общее количество репозиториев для расчета пагинации
    const { count, error: countError } = await supabase
      .from('external_mcp_repositories')
      .select('*', { count: 'exact', head: true });
    
    if (countError) {
      console.error('Error counting external MCP repositories:', countError);
      return { data: [], count: 0 };
    }
    
    // Рассчитываем смещение на основе номера страницы и размера страницы
    const from = (page - 1) * pageSize;
    const to = from + pageSize - 1;
    
    // Получаем данные для текущей страницы
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

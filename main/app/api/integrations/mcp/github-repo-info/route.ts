import { NextRequest, NextResponse } from 'next/server'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_PREFIX = 'github_repo_info_'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const { repoUrl } = body
    
    if (!repoUrl) {
      return NextResponse.json({ error: 'Repository URL is required' }, { status: 400 })
    }
    
    const normalizedUrl = repoUrl.toLowerCase().trim()
    const cacheKey = `${CACHE_PREFIX}${normalizedUrl}`
    
    const cachedData = await getCache(cacheKey)
    
    if (cachedData) {
      return NextResponse.json(cachedData)
    }
    
    const normalizedGithubUrl = normalizedUrl.endsWith('/') ? normalizedUrl.slice(0, -1) : normalizedUrl;
    const parts = normalizedGithubUrl.split('/');
    const repo = parts[parts.length - 1];
    const owner = parts[parts.length - 2];
    
    if (!owner || !repo) {
      return NextResponse.json({ error: 'Could not extract owner or repo from URL' }, { status: 400 });
    }

    const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
    
    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`, {
      headers: {
        ...(GITHUB_TOKEN ? { 'Authorization': `token ${GITHUB_TOKEN}` } : {}),
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!response.ok) {
      return NextResponse.json(
        { error: `Error fetching GitHub repo info: ${response.statusText}` }, 
        { status: response.status }
      );
    }
    
    const githubData = await response.json();

    const data = {
      stars: githubData.stargazers_count,
      forks: githubData.forks_count,
      created_at: githubData.created_at,
      updated_at: githubData.updated_at,
      owner: owner,
      name: repo,
      avatar_url: githubData.owner?.avatar_url,
      description: githubData.description,
      license: githubData.license ? {
        name: githubData.license.name,
        spdx_id: githubData.license.spdx_id
      } : undefined
    };
    
    await setCache(cacheKey, data)
    
    return NextResponse.json(data)
  } catch (err) {
    console.error('Unexpected error in POST /api/integrations/mcp/github-repo-info:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
} 
import { NextRequest, NextResponse } from 'next/server';

// Create a simple in-memory cache
const CACHE = new Map<string, { data: any, timestamp: number }>();
const CACHE_TTL = 24 * 3600 * 1000; // 24 hours in milliseconds

export async function POST(request: NextRequest) {
  try {
    const { repoUrl } = await request.json();
    
    if (!repoUrl || !repoUrl.includes('github.com')) {
      return NextResponse.json({ error: 'Invalid GitHub repository URL' }, { status: 400 });
    }
    
    // Check if we have a cached response
    if (CACHE.has(repoUrl)) {
      const cached = CACHE.get(repoUrl)!;
      const now = Date.now();
      
      // If cache is still valid, return cached data
      if (now - cached.timestamp < CACHE_TTL) {
        const response = NextResponse.json(cached.data);
        response.headers.set('X-Cache', 'HIT');
        return response;
      }
    }
    
    const normalizedUrl = repoUrl.endsWith('/') ? repoUrl.slice(0, -1) : repoUrl;
    const parts = normalizedUrl.split('/');
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
      console.log('GitHub API Error Response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      });
      const errorBody = await response.json();
      console.log('GitHub API Error Body:', errorBody);
      
      return NextResponse.json(
        { error: `Error fetching GitHub repo info: ${response.statusText}` }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();

    const repoData = {
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
    
    // Cache the data
    CACHE.set(repoUrl, { data: repoData, timestamp: Date.now() });

    const nextResponse = NextResponse.json(repoData);
    nextResponse.headers.set('X-Cache', 'MISS');
    return nextResponse;
    
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch repository information' }, 
      { status: 500 }
    );
  }
} 
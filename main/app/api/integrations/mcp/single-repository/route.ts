import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_PREFIX = 'mcp_repository_'

export async function POST(request: NextRequest) {
  try {
    const { repositoryId } = await request.json()
    
    if (!repositoryId) {
      return NextResponse.json({ error: 'Repository ID is required' }, { status: 400 })
    }
    
    const cacheKey = `${CACHE_PREFIX}${repositoryId}`
    
    const cachedData = await getCache(cacheKey)
    
    if (cachedData) {
      return NextResponse.json(cachedData)
    }
    
    const supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_KEY!
    )
    
    const { data, error } = await supabase
      .from('mcp_repositories')
      .select('id, image_name, repo_url, name, description, input_schema, env, metadata, created_at, author_user_id, last_commit_hash')
      .eq('id', repositoryId)
      .single()
    
    if (error || !data) {
      console.error('Error fetching single MCP repository:', error)
      return NextResponse.json({ error: 'Failed to fetch MCP repository' }, { status: 500 })
    }
    
    const result = {
      mcpDetails: data,
      repoInfo: null, 
      userEnvironment: null,
      isConnected: false
    }
    
    if (data.repo_url && (!data.metadata?.stars)) {
      try {
        const frontendUrl = process.env.FRONTEND_URL || process.env.NEXT_PUBLIC_FRONTEND_URL || 'http://localhost:3000'
        
        const repoResponse = await fetch(`${frontendUrl}/api/github/repo`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ repoUrl: data.repo_url })
        })
        
        if (repoResponse.ok) {
          result.repoInfo = await repoResponse.json()
        }
      } catch (error) {
        console.error('Error fetching GitHub repo info:', error)
      }
    }
    
    await setCache(cacheKey, result)
    
    return NextResponse.json(result)
  } catch (err) {
    console.error('Unexpected error in POST /api/integrations/mcp/single-repository:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
} 
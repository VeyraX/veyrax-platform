import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_KEY = 'all_mcp_repositories'

export async function GET() {
  try {
    const cachedData = await getCache(CACHE_KEY)
    
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
      .eq('is_approved', true)
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Error fetching MCP repositories:', error)
      return NextResponse.json({ error: 'Failed to fetch MCP repositories', details: error.message }, { status: 500 })
    }
    
    const result = data || []

    await setCache(CACHE_KEY, result)

    return NextResponse.json(result)
  } catch (err) {
    console.error('Unexpected error in GET /api/integrations/mcp/repositories:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
} 
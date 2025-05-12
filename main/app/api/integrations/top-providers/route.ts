import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_KEY = 'top_connected_providers'

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

    const { data, error } = await supabase.rpc('get_top_connected_providers')

    if (error) {
      console.error('Error fetching top connected providers:', error)
      return NextResponse.json({ error: 'Failed to fetch top connected providers', details: error.message }, { status: 500 })
    }

    const result = data || []

    await setCache(CACHE_KEY, result)

    return NextResponse.json(result)
  } catch (err) {
    console.error('Unexpected error in GET /api/integrations/top-providers:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
} 
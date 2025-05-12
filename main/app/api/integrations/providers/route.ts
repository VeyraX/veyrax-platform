import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_KEY = 'all_providers'

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

    const { data: providers, error } = await supabase
      .from('providers')
      .select(`
        *,
        provider_scopes (
          id,
          scope_id,
          scope_name
        )
      `)

    if (error) {
      console.error('Error fetching providers:', error)
      return NextResponse.json({ error: 'Failed to fetch providers', details: error.message }, { status: 500 })
    }

    await setCache(CACHE_KEY, providers)

    return NextResponse.json(providers)
  } catch (err) {
    console.error('Unexpected error in GET /api/integrations/providers:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
}

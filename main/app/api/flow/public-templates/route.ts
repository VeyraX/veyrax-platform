import { NextResponse } from 'next/server'
import { createClient } from '@supabase/supabase-js'
import { getCache, setCache } from '@/lib/utils/redis-cache'

const CACHE_KEY = 'flows_public_templates'

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
      .from('user_flows')
      .select('*')
      .eq('is_template', true)
      .eq('is_shared', true);

    if (error) {
      console.error('Error fetching public templates:', error)
      return NextResponse.json({ error: 'Failed to fetch public templates', details: error.message }, { status: 500 })
    }

    await setCache(CACHE_KEY, data)

    return NextResponse.json(data)
  } catch (err) {
    console.error('Unexpected error in GET /api/flow/public-templates:', err)
    const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred'
    return NextResponse.json({ error: 'Internal Server Error', details: errorMessage }, { status: 500 })
  }
} 
import { createBrowserClient } from '@supabase/ssr'
import { UserProfile } from '@/app/modules/settings/api/types.settings'

export async function getUserProfile(): Promise<UserProfile | null> {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser()
    if (error || !user) {
      return null
    }

    return {
      id: user.id,
      email: user.email ?? null,
      full_name: user.user_metadata?.full_name ?? null,
      avatar_url: user.user_metadata?.picture ?? user.user_metadata?.avatar_url ?? null,
    }
  } catch (error) {
    console.error('Error in getUserProfile:', error)
    return null
  }
}
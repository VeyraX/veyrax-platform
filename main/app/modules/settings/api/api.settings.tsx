import { createBrowserClient } from '@supabase/ssr'
import { UserProfile, UserApiKey } from '@/app/modules/settings/api/types.settings'

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

export async function getUserApiKey(): Promise<UserApiKey | null> {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) {
      return null
    }

    const { data, error } = await supabase
      .from('users_api_keys')
      .select('*')
      .eq('user_id', user.id)
      .single()

    if (error) {
      console.error('Error fetching API key:', error)
      return null
    }

    return data
  } catch (error) {
    console.error('Error in getUserApiKey:', error)
    return null
  }
}

export async function generateApiKey(): Promise<UserApiKey | null> {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) {
      return null
    }

    // Generate a random API key with a prefix
    const randomBytes = new Uint8Array(20)
    window.crypto.getRandomValues(randomBytes)
    const apiKey = 'vrx-' + Array.from(randomBytes)
      .map(b => b.toString(16).padStart(2, '0'))
      .join('')

    // First check if user already has an API key
    const { data: existingKey } = await supabase
      .from('users_api_keys')
      .select('id')
      .eq('user_id', user.id)
      .single()

    let result
    
    if (existingKey) {
      // Update existing key
      const { data, error } = await supabase
        .from('users_api_keys')
        .update({ api_key: apiKey })
        .eq('id', existingKey.id)
        .select()
        .single()
        
      if (error) throw error
      result = data
    } else {
      // Insert new key
      const { data, error } = await supabase
        .from('users_api_keys')
        .insert({ 
          api_key: apiKey,
          user_id: user.id
        })
        .select()
        .single()
        
      if (error) throw error
      result = data
    }

    return result
  } catch (error) {
    console.error('Error generating API key:', error)
    return null
  }
}

export async function revokeApiKey(): Promise<boolean> {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data: { user }, error: userError } = await supabase.auth.getUser()
    if (userError || !user) {
      return false
    }

    const { error } = await supabase
      .from('users_api_keys')
      .delete()
      .eq('user_id', user.id)

    if (error) {
      console.error('Error revoking API key:', error)
      return false
    }

    return true
  } catch (error) {
    console.error('Error in revokeApiKey:', error)
    return false
  }
}
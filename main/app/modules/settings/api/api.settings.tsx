import { createBrowserClient } from '@supabase/ssr'
import { UserProfile, UserApiKey, UserSubscription } from '@/app/modules/settings/api/types.settings'

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

export async function deleteUserAccount(): Promise<boolean> {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data: { user }, error } = await supabase.auth.getUser()
    
    if (error || !user) {
      console.error('No authenticated user found:', error)
      return false
    }
    
    const response = await fetch('/api/user/delete-account', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ user_id: user.id }),
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('Delete account response error:', errorData)
      throw new Error(errorData.message || `Failed to delete account: ${response.status}`)
    }

    await supabase.auth.signOut()
    return true
  } catch (error) {
    console.error('Error in deleteUserAccount:', error)
    return false
  }
}

export async function getUserSubscription() {
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
      .from('users_subscription_status_view')
      .select('*')
      .eq('user_id', user.id)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        return null
      }
      console.error('Error fetching subscription data:', error)
      return null
    }

    return data
  } catch (error) {
    console.error('Error in getUserSubscription:', error)
    return null
  }
}

export async function getUserUsage() {
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
      .from('user_monthly_usage_view')
      .select('*')
      .eq('user_id', user.id)
      .single()

    console.log(data)

    if (error) {
      if (error.code === 'PGRST116') {
        return { user_id: user.id, api_call_count: 0, active_flow_count: 0, chat_count: 0 }
      }
      console.error('Error fetching usage data:', error)
      return null
    }

    return data
  } catch (error) {
    console.error('Error in getUserUsage:', error)
    return null
  }
}

export async function getProductInfoByTag(tag: string) {
  const supabase = createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
  
  try {
    const { data, error } = await supabase
      .from('products_info')
      .select('*')
      .eq('product_tag', tag)
      .single()

    if (error) {
      console.error('Error fetching product info:', error)
      return null
    }

    // Parse the JSONB attrs field
    if (data && typeof data.attrs === 'string') {
      data.attrs = JSON.parse(data.attrs)
    }

    return data
  } catch (error) {
    console.error('Error in getProductInfo:', error)
    return null
  }
}

export async function getUserProductInfo() {
  try {
    // First try to get subscription from Stripe
    const subscription = await getUserSubscription()
    
    if (subscription) {
      // Extract product_tag from subscription data
      // This is based on your data structure - you might need to adjust
      const productName = subscription.product_name.toLowerCase()
      let productTag = 'free'
      
      if (productName.includes('pro')) {
        productTag = 'pro'
      } else if (productName.includes('team')) {
        productTag = 'teams'
      } else if (productName.includes('starter')) {
        productTag = 'starter'
      }
      
      return await getProductInfoByTag(productTag)
    } else {
      // No subscription, user is on free plan
      return await getProductInfoByTag('free')
    }
  } catch (error) {
    console.error('Error getting user product info:', error)
    // Fallback to free plan on error
    return await getProductInfoByTag('free')
  }
}

export async function isUserOnFreePlan() {
  try {
    const subscription = await getUserSubscription()
    return !subscription
  } catch (error) {
    console.error('Error checking if user is on free plan:', error)
    return true
  }
}
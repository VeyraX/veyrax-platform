import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      auth: {
        persistSession: true,          // ❗  cookie/localStorage
        autoRefreshToken: true,
        detectSessionInUrl: true       // ❗  reads #access_token and clean up URL
      }
    }
  )
}
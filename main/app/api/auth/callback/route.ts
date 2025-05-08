import { NextRequest, NextResponse } from 'next/server'
import { createClient } from '@/lib/utils/supabase/server'

export const runtime = 'edge'

export async function GET(request: NextRequest) {
  const requestUrl = new URL(request.url)
  const code = requestUrl.searchParams.get('code')
  const access_token = requestUrl.searchParams.get('access_token')
  const refresh_token = requestUrl.searchParams.get('refresh_token')
  
  // Get the next destination from query params, with default
  const next = requestUrl.searchParams.get('next') || '/integrations'
  
  // Create initial response object
  let response = NextResponse.redirect(`${requestUrl.origin}${next}`)

  try {
    // Create Supabase client using the project's utility function
    const supabase = createClient()

    if (code) {
      // Handle code-based authentication
      const { error } = await supabase.auth.exchangeCodeForSession(code)
      if (error) {
        console.error('Code exchange error:', error)
        return NextResponse.redirect(`${requestUrl.origin}/login?error=${encodeURIComponent(error.message)}`)
      }
      return response
    }

    if (access_token && refresh_token) {
      // Handle token-based authentication
      const { error } = await supabase.auth.setSession({
        access_token,
        refresh_token,
      })
      if (error) {
        console.error('Set session error:', error)
        return NextResponse.redirect(`${requestUrl.origin}/login?error=${encodeURIComponent(error.message)}`)
      }
      return response
    }

    // If we haven't returned yet, check if this is the API route and redirect to client
    // (which can handle URL hash fragments that servers can't access)
    if (requestUrl.pathname === '/api/auth/callback' && !code && !access_token) {
      // Special case: hash-based auth - redirect to client-side handler
      const clientRoute = new URL('/auth/callback', requestUrl.origin)
      requestUrl.searchParams.forEach((value, key) => {
        clientRoute.searchParams.set(key, value)
      })
      return NextResponse.redirect(clientRoute)
    }

    // If we get here, authentication failed
    return NextResponse.redirect(`${requestUrl.origin}/login?error=missing_authentication_parameters`)
  } catch (error: any) {
    console.error('Auth callback error:', error)
    return NextResponse.redirect(`${requestUrl.origin}/login?error=${encodeURIComponent(error.message || 'unknown_error')}`)
  }
}
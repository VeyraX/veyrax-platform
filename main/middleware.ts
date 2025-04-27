import { NextResponse, type NextRequest } from 'next/server'
import { updateSession } from './lib/utils/supabase/middleware'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const { response, session } = await updateSession(request)

  if (pathname.includes('/oauth/') || 
      pathname.includes('/user/') && pathname.includes('/auth') || 
      request.nextUrl.search.includes('oauth_return=') || 
      request.nextUrl.search.includes('success=')) {
    console.log('Skipping middleware for OAuth path:', pathname);
    return response;
  }

  if (pathname === '/pricing/success') {
    const url = new URL(request.url)
    const sessionId = url.searchParams.get('session_id')
    
    if (!sessionId) {
      return NextResponse.redirect(new URL('/pricing', request.url))
    }
  }

  if (pathname === '/') {
    return NextResponse.redirect(new URL('/web', request.url))
  }

  if (pathname === '/agent') {
    return NextResponse.redirect(new URL('/agent/new', request.url))
  }

  if (pathname === '/marketplace' && session) {
    return NextResponse.redirect(new URL('/integrations', request.url))
  }

  const marketplaceMcpMatch = pathname.match(/^\/marketplace\/mcp\/([^\/]+)$/);
  if (marketplaceMcpMatch) {
    if (session) {
      const mcpName = marketplaceMcpMatch[1];
      return NextResponse.redirect(new URL(`/integrations/mcp/${mcpName}`, request.url));
    }
  }

  if (pathname === '/integrations/gmail') {
    return NextResponse.redirect(new URL('integrations/mail', request.url))
  }

  // if (pathname === '/integrations' && !session) {
  //   return NextResponse.redirect(new URL('/marketplace', request.url))
  // }

  const integrationsMcpMatch = pathname.match(/^\/integrations\/mcp\/([^\/]+)$/);
  if (integrationsMcpMatch) {
    if (!session) {
      const mcpName = integrationsMcpMatch[1];
      return NextResponse.redirect(new URL(`/marketplace/mcp/${mcpName}`, request.url));
    }
  }

  const providerTagMatch = pathname.match(/^\/integrations\/([^\/]+)$/);
  
  if (providerTagMatch && !session && !pathname.includes('/auth-complete')) {
    const providerTag = providerTagMatch[1];
    return NextResponse.redirect(new URL(`/marketplace/${providerTag}`, request.url));
  }

  const isAuthCompletePath = /\/integrations\/[\w-]+\/auth-complete/.test(pathname);

  if (
    pathname.startsWith('/agent/') || 
    pathname.startsWith('/components/') || 
    (pathname.startsWith('/integrations') && !isAuthCompletePath) ||
    (pathname.startsWith('/integrations/') && !isAuthCompletePath) ||
    pathname.startsWith('/flows') ||
    (pathname.startsWith('/flow/') && !pathname.includes('/shared')) ||
    pathname.startsWith('/deployment')
  ) {
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  if ((pathname === '/login' || pathname === '/register') && session) {
    return NextResponse.redirect(new URL('/agent/new', request.url))
  }

  return response
}

export const config = {
  matcher: [
    '/',
    '/login',
    '/register',
    '/agent/:path*',
    '/components/:path*',
    '/web',
    '/marketplace',
    '/marketplace/:path*',
    '/marketplace/mcp/:path*',
    '/integrations',
    '/integrations/:path*',
    '/integrations/mcp/:path*',
    '/flows',
    '/flow/:path*',
    '/pricing/success',
    '/deployment',
    '/deployment/:path*',
  ]
}
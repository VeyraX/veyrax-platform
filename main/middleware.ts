import { NextResponse, type NextRequest } from 'next/server'
import { updateSession } from './lib/utils/supabase/middleware'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const { response, session } = await updateSession(request)

  if (pathname === '/') {
    return NextResponse.redirect(new URL('/web', request.url))
  }

  if (pathname === '/agent') {
    return NextResponse.redirect(new URL('/agent/new', request.url))
  }

  if (pathname === '/marketplace' && session) {
    return NextResponse.redirect(new URL('/integrations', request.url))
  }

  // Исключить маршруты auth-complete из проверки авторизации
  const isAuthCompletePath = /\/integrations\/[\w-]+\/auth-complete/.test(pathname);

  if (
    pathname.startsWith('/agent/') || 
    pathname.startsWith('/components/') || 
    (pathname.startsWith('/integrations') && !isAuthCompletePath) ||
    (pathname.startsWith('/integrations/') && !isAuthCompletePath) ||
    pathname.startsWith('/flows') ||
    (pathname.startsWith('/flow/') && !pathname.includes('/shared'))
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
    '/integrations',
    '/integrations/:path*',
    '/flows',
    '/flow/:path*',
  ]
}
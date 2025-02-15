import { NextResponse, type NextRequest } from 'next/server'
import { updateSession } from './lib/utils/supabase/middleware'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const { response, session } = await updateSession(request)

  if (pathname === '/') {
    return NextResponse.redirect(new URL('/web', request.url))
  }

  if (pathname.startsWith('/agent') || pathname.startsWith('/components/') || pathname.startsWith('/integrations')) {
    if (!session) {
      return NextResponse.redirect(new URL('/login', request.url))
    }
  }

  if (pathname === '/login' && session) {
    return NextResponse.redirect(new URL('/agent', request.url))
  }

  return response
}

export const config = {
  matcher: [
    '/',
    '/login',
    '/agent/:path*',
    '/components/:path*',
    '/web',
    '/integrations'
  ]
}
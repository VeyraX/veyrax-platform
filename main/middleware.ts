import { NextResponse, NextRequest } from "next/server";
import { GetAuthToken } from "./lib/actions/actions";

export async function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl;
  const authToken = await GetAuthToken();
  const cookieToken = req.cookies.get('authToken')?.value;
  const envToken = process.env.NEXT_PUBLIC_AUTH_TOKEN_DATA;

  const isValidToken = cookieToken === envToken;

  if (pathname === '/login') {
    if (authToken && isValidToken) {
      return NextResponse.redirect(new URL('/agent', req.url));
    }
    return NextResponse.next();
  }

  if (pathname === '/') {
    if (authToken && isValidToken) {
      return NextResponse.redirect(new URL('/agent', req.url));
    } else {
      return NextResponse.redirect(new URL('/login', req.url));
    }
  }

  if (pathname.startsWith('/agent')) {
    if (!authToken || !isValidToken) {
      return NextResponse.redirect(new URL('/login', req.url));
    }
    return NextResponse.next();
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/login', '/agent/:path*']
}
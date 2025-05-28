import { NextResponse } from '@vercel/edge';

export function middleware(request) {
  const url = new URL(request.url);

  if (url.pathname === '/') {
    return NextResponse.rewrite(new URL('/public/index.html', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/' // This middleware will run only when the root path is accessed.
  ],
};
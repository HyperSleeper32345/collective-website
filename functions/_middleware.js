// Keeps repository files that are not part of the website off the web.
//
// Cloudflare Pages serves every file in the repository root, including the
// build brief and the git ignore list. _routes.json sends only /api/* and
// those internal paths to Functions, so this runs on nothing else; the
// internal paths answer with the site's own 404 page and a 404 status.

const INTERNAL = /^\/(CLAUDE\.md|README\.md|\.gitignore|_routes\.json|\.wrangler(\/.*)?)$/i;

export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (!INTERNAL.test(url.pathname)) return context.next();
  const page = await context.env.ASSETS.fetch(new URL('/404.html', url.origin));
  const headers = new Headers(page.headers);
  headers.set('X-Robots-Tag', 'noindex');
  headers.set('Cache-Control', 'no-store');
  return new Response(page.status === 200 ? page.body : 'Not found', { status: 404, headers: headers });
}

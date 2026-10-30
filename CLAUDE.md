# CLAUDE.md: Collective website (v5)

The site at wearecollective.com.au. Cloudflare Pages project `collective-website`, git-connected, production branch `main`, output directory the repository root, no build command on Pages.

## Sources of truth

- **Design and copy:** David's v5 source, `~/Documents/Codex/2026-10-30/please-provide-me-with-the-raw/outputs/collective-website-v5-exact-source` (commit da6f835). The site is word for word and pixel for pixel to it. Read only.
- **Programme brief:** collective-os `knowledge/briefs/missions/C-SITE-V5.md` (URLs, redirects, lead path, measurement, gate).
- **Brand:** brand `collective`, v5 signed off by David on 31 Oct 2026. Until C-SITE-V5-BRAND lands tokens 2.0, the brand gate is pixel parity with the v5 source at 390 and 1440, not tokens 1.7.

## How the site is built

- Page content: `site-src/content/` (page JSON, article JSON, fragments, `home.html`, `contact.html`).
- Generator: `python3 site-src/build.py` (standard library only). It writes the page HTML, `site-config.js`, `sitemap.xml`, `robots.txt` and `_redirects` into the repository root. Edit content, then rebuild; never hand-edit generated HTML.
- Styles, scripts and assets are edited in place at the root: `styles.css`, `brackets.css`, `site.css`, `site.js`, `brackets.js`, `measurement.js`, `enquiry.js`, `lead-client.mjs`, `assets/`.
- Check: `node site-src/check-enquiry-contract.mjs` (lead receipt rules, measurement allowlist, `/api/lead` field mapping).

## Rules that hold

- URLs are slashless (`/about`, never `/about/`): pages are emitted as `about.html`, and canonicals, sitemap and internal links are slashless.
- The only 301s are the six retired routes in `_redirects` (`/system`, `/services`, `/pitcher`, `/catcher`, `/closer`, `/collective-os`, each with its `/` and `.html` forms).
- No privacy page until David says so.
- Server side: `functions/api/lead.js` posts to Supabase `public.ingest_collective_lead`; `functions/_middleware.js` and `_routes.json` keep `site-src/`, `scripts/` and repository files off the web. Environment values live on the Pages project, never in the repository.
- Test leads have first name TEST. On this project's preview host (`*.collective-website-1lc.pages.dev`) the form sends only TEST leads; any other name prepares the email draft.
- No em or en dashes anywhere; title separators are a vertical bar. Australian English.

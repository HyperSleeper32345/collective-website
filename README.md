# collective-website

The Collective website, wearecollective.com.au, served by Cloudflare Pages from this repository's root.

- Build: `python3 site-src/build.py` regenerates the pages from `site-src/content/`.
- Check: `node site-src/check-enquiry-contract.mjs`.
- Enquiries: `functions/api/lead.js` (Pages Function) records leads in HyperPipe through Supabase.

See `CLAUDE.md` for the rules the site keeps.

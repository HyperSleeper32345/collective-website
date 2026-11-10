#!/usr/bin/env python3
"""Build the Collective website (v5) into the repository root for Cloudflare Pages.

Ported from the v5 source generator (Codex export, commit da6f835,
scripts/build-site.py) for the live host, per the C-SITE-V5 brief:

- Pages are written as slashless files (about.html, insights/pipeline-velocity.html),
  so Cloudflare Pages serves /about and canonicals, sitemap and internal links stay
  slashless, as on the live site.
- Always the production build: canonical origin https://wearecollective.com.au,
  index,follow, enquiries through the existing /api/lead Pages Function.
- Title separators are a vertical bar, never a dash.
- No privacy page, no legacy alias stubs, no identity study: the six retired routes
  are HTTP 301s in _redirects.
- JSON-LD: Organization on home, Article and BreadcrumbList on every article (and a
  DefinedTermSet on the series glossary), BreadcrumbList on the other pages.
- The Commercial Performance series (C-SITE-ARTICLES-1) is converted from its markdown
  by site-src/markdown_article.py; its articles sort after the four field notes and
  have their own rows on /insights.
- The contact page keeps the Antares chat and booking widget beneath the form.
- Every article names David Collins as author (C-SITE-ARTICLES-2): a linked byline, a
  visible publish date, an author box with his LinkedIn, one Person @id in every
  Article's data, the author page /about/david-collins, previous and next links between
  the seven series parts, lastmod in the sitemap and /llms.txt.

Static styles, scripts and assets live at the repository root, where they are
served. This script writes only the generated files listed in GENERATED.

Run from anywhere: python3 site-src/build.py
"""
from pathlib import Path
from html import escape
import argparse
import json
import re

ROOT = Path(__file__).resolve().parent.parent
CONTENT = Path(__file__).resolve().parent / 'content'
SITE = 'https://wearecollective.com.au'
EMAIL = 'david@wearecollective.com.au'
# Preview deployments of this Pages project may send TEST leads (see enquiry.js).
LEAD_TEST_HOST = 'collective-website-1lc.pages.dev'
# Measurement (C-SITE-V5-2): one GTM container carries GA4 G-GTJXEGTF0G and the Meta pixel.
# On the preview host the page loads the container's "Pages preview" environment, so a
# version can be proven there before it is published to Live at cutover.
GTM_CONTAINER = 'GTM-NT8V9Z6W'
GTM_PREVIEW_ENVIRONMENT = {'auth':'al8LAMD2C2BQln6BaJOdEA','preview':'env-3'}
NAV = [('approach', 'Approach'), ('capabilities', 'Capabilities'), ('work', 'Work'), ('insights', 'Thinking'), ('about', 'About')]
ARROW = '<span aria-hidden="true">↗</span>'
# C-SITE-ARROW-1: iOS and some Android fonts draw the arrow characters as emoji tiles, so
# every arrow character in a page's text is emitted as one line arrow instead. The drawing
# is the closing action's arrow (M10 90 90 10M22 10H90V78) on a 24 grid, at the same
# stroke weight for its size; each direction is that one drawing rotated (styles.css .arrow).
ARROW_PATH = 'M2.5 21.5 21.5 2.5M5.35 2.5H21.5V18.65'
ARROW_DIRECTIONS = {'↗':'ne','→':'e','↘':'se','↓':'s','↙':'sw','←':'w','↖':'nw','↑':'n'}
ARROW_CHARACTER = re.compile('['+''.join(ARROW_DIRECTIONS)+']')
TAG_OR_TEXT = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<title>.*?</title>|<[^>]*>)', re.S)

def arrow(direction='ne'):
    return f'<svg class="arrow arrow--{direction}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" aria-hidden="true" focusable="false"><path d="{ARROW_PATH}"/></svg>'

def line_arrows(html):
    # Text between tags only: attributes, titles, scripts and styles are left as they are.
    return ''.join(part if i % 2 else ARROW_CHARACTER.sub(lambda m: arrow(ARROW_DIRECTIONS[m.group()]), part)
                   for i, part in enumerate(TAG_OR_TEXT.split(html)))
SITEMAP = []
GENERATED = []
PAGE_INDEX = {}

# The six retired routes (plan section 3). Each form is one hop to its destination.
RETIRED = {
    'system': '/approach',
    'services': '/capabilities',
    'pitcher': '/capabilities#demand',
    'catcher': '/capabilities#conversion',
    'closer': '/capabilities#demand',
    'collective-os': '/capabilities#operations',
}

def brand(reverse=False):
    tone = ' data-brand-tone="reverse"' if reverse else ''
    suffix = '-reverse' if reverse else ''
    # Width and height carry the artwork's ratio at its rendered size (H5); CSS sets the size.
    return f'<span class="identity-lockup identity-lockup--framed" data-brand-lockup{tone} aria-hidden="true"><img class="identity-artwork" src="/assets/identity/collective-primary{suffix}.svg" alt="" width="208" height="32"></span>'

def nav_links(active):
    return ''.join(f'<a href="/{slug}/"'+(' aria-current="page"' if active == slug else '')+f'>{label}</a>' for slug,label in NAV)

def header(active):
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<div class="reading-progress" aria-hidden="true"><span></span></div>
<header class="site-header"><div class="page-width header-inner">
<a class="brand" href="/" aria-label="Collective home">{brand()}</a>
<p class="header-descriptor">Independent<br>growth partner</p>
<nav class="desktop-navigation" aria-label="Main navigation">{nav_links(active)}</nav>
<a class="header-apply" href="/contact/">Let’s talk {ARROW}</a>
<button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="Open navigation"><span>Menu</span><span class="menu-lines" aria-hidden="true"></span></button>
</div></header>
<dialog class="site-menu" id="site-menu" aria-label="Site navigation" tabindex="-1"><div class="menu-top"><a class="brand" href="/" aria-label="Collective home">{brand()}</a><button type="button" data-close-menu aria-label="Close navigation">Close <span aria-hidden="true">×</span></button></div><nav aria-label="Mobile navigation"><a href="/">Home</a>{nav_links(active)}<a href="/contact/">Let’s talk {ARROW}</a></nav><div class="menu-bottom"><a href="/partnership/">Ecommerce founding partnership {ARROW}</a><a href="/developer-partnership/">Developer founding partnership {ARROW}</a><span class="mono">Founder-led. Australia.</span></div></dialog>'''

def closing(label='Let’s start with your business.'):
    return f'''<section class="site-closing"><div class="page-width"><div class="section-label"><span class="mono">A conversation with Collective</span><span class="mono">Start with the real question</span></div><a href="/contact/" class="closing-action"><span>WHAT’S<br>NEXT?</span><svg viewBox="0 0 100 100" aria-hidden="true"><path d="M10 90 90 10M22 10H90V78"/></svg></a><div class="closing-bottom"><p>{label}</p><a class="mono" href="mailto:{EMAIL}">Email David {ARROW}</a></div></div></section>'''

def footer():
    # No privacy page at launch (David, 31 Oct 2026): the v5 "Privacy & enquiries" link is removed.
    return f'''<footer class="full-footer page-width"><div class="full-footer-top"><div class="footer-identity"><a class="brand" href="/" aria-label="Collective home">{brand()}</a><p>Grow what you keep.<br>Founder-led by David Collins.</p></div><nav aria-label="Explore Collective"><span class="mono">Explore</span>{nav_links('')}</nav><nav aria-label="Working together"><span class="mono">Working together</span><a href="/contact/">Start a conversation {ARROW}</a><a href="/partnership/">Ecommerce founding partnership {ARROW}</a><a href="/developer-partnership/">Developer founding partnership {ARROW}</a><a href="mailto:{EMAIL}">Email David {ARROW}</a></nav></div><div class="full-footer-bottom"><span class="mono">© Collective 2026</span><span class="mono">Independent thinking. Connected work.</span><a href="#top">Back to top ↑</a></div></footer>'''

def page_hero(p):
    intro=f'<p>{escape(p["intro"])}</p>'
    if p.get('hero_action'):
        action=p['hero_action']
        intro=f'<div class="page-hero-intro">{intro}<a class="text-action" href="{escape(action["href"],quote=True)}"><span>{escape(action["label"])}</span>{ARROW}</a></div>'
    return f'''<section class="page-hero page-width"><div class="hero-meta"><p class="mono">{escape(p.get('eyebrow',p['nav']))}</p><a class="mono" href="/">Collective / Home ↗</a></div><h1>{p['heading']}</h1><div class="page-hero-bottom"><p class="mono">{escape(p.get('hero_note','Commercial perspective. Connected execution.'))}</p>{intro}</div></section>'''

def page_url(slug):
    return SITE + ('/' + slug if slug else '/')

def plain(text):
    return re.sub(r'\s+', ' ', re.sub('<[^>]+>', ' ', text)).strip()

def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '</script>'

PUBLISHER = {'@type': 'Organization', '@id': SITE + '/#organization', 'name': 'Collective', 'url': SITE + '/',
             'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/identity/collective-primary.png'}}

# The author (C-SITE-ARTICLES-2). Every line about David is in the credential sources
# (collective-os evidence/2026-11-10/c-site-articles-2/credential-sources.md).
AUTHOR_SLUG = 'about/david-collins'
LINKEDIN = 'https://www.linkedin.com/in/davidtmcollins/'
AUTHOR_ROLE = 'Founder & director, Collective'
AUTHOR_BIO = ('David Collins is the founder and director of Collective, an independent growth business. '
              'He leads the client relationship and commercial direction, and stays hands-on across the work. '
              'He has worked in marketing since 2018, in agencies and inside a property development business.')
PERSON = {'@type': 'Person', '@id': SITE + '/' + AUTHOR_SLUG + '#person', 'name': 'David Collins',
          'url': SITE + '/' + AUTHOR_SLUG, 'jobTitle': 'Founder and director', 'sameAs': [LINKEDIN]}
# The LinkedIn mark: one line icon at the arrow's weight (assets/icons/linkedin.svg), inlined so it takes the ink colour.
LINKEDIN_ICON = re.search(r'<path d="([^"]+)"', (ROOT / 'assets/icons/linkedin.svg').read_text()).group(1)

def linkedin_icon():
    return f'<svg class="linkedin-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="square" aria-hidden="true" focusable="false"><path d="{LINKEDIN_ICON}"/></svg>'

# Publish dates: the day each article page first reached main, and the last day its words
# changed there (link wrapping, byline and chrome are not a change of words). Read from git.
DATES = {
    'diagnose-marketing-performance': ('2026-09-27', '20088da', '2026-10-31', '40bd0f5'),
    'pipeline-velocity': ('2026-09-27', '20088da', '2026-10-31', '40bd0f5'),
    'revenue-and-profit': ('2026-10-31', '40bd0f5', '2026-10-31', '40bd0f5'),
    'independent-growth-business': ('2026-10-31', '40bd0f5', '2026-10-31', '40bd0f5'),
    **{slug: ('2026-11-10', '192045c', '2026-11-10', '192045c') for slug in [
        'understanding-ecommerce-commercial-performance', 'revenue-contribution-and-operating-profit',
        'reading-monthly-and-year-on-year-performance', 'mer-roas-and-profitable-growth',
        'customer-acquisition-cost-value-and-payback', 'cash-inventory-and-the-pace-of-growth',
        'ecommerce-performance-glossary']},
}
MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
LASTMOD = {}

def long_date(iso):
    y, m, d = iso.split('-')
    return f'{int(d)} {MONTHS[int(m) - 1]} {y}'

def breadcrumbs(trail):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i, 'name': name, 'item': page_url(slug)}
        for i, (name, slug) in enumerate([('Home', '')] + trail, 1)]}

def structured_data(p):
    slug = p['slug'].strip('/')
    if slug == '404':
        return ''
    if not slug:
        return ld({'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Collective', 'url': SITE + '/',
                   'logo': SITE + '/assets/identity/collective-primary.png', 'email': EMAIL,
                   'founder': {'@type': 'Person', 'name': 'David Collins'}})
    if p.get('article'):
        a = p['article']
        blocks = [{'@context': 'https://schema.org', '@type': 'Article', 'headline': a['title'], 'description': a['description'],
                   'url': page_url(slug), 'mainEntityOfPage': page_url(slug),
                   'image': SITE + '/assets/identity/collective-social-share.png',
                   'datePublished': DATES[a['slug']][0], 'dateModified': DATES[a['slug']][2],
                   'author': PERSON, 'publisher': PUBLISHER,
                   'isPartOf': {'@type': 'CollectionPage', 'name': 'Thinking', 'url': page_url('insights')}},
                  breadcrumbs([('Thinking', 'insights'), (a['title'], slug)])]
        if a.get('defined_terms'):
            term_set = {'@type': 'DefinedTermSet', '@id': page_url(slug) + '#terms', 'name': a['title'], 'url': page_url(slug)}
            blocks.append({'@context': 'https://schema.org', **term_set, 'hasDefinedTerm': [
                {'@type': 'DefinedTerm', 'name': t['name'], 'description': t['description'], 'url': page_url(slug) + '#' + t['id'],
                 'inDefinedTermSet': {'@id': term_set['@id']}} for t in a['defined_terms']]})
        return ''.join(ld(b) for b in blocks)
    if slug == AUTHOR_SLUG:
        return ld({'@context': 'https://schema.org', '@type': 'ProfilePage', 'url': page_url(slug), 'name': plain(p['title']),
                   'mainEntity': {**PERSON, 'description': AUTHOR_BIO, 'worksFor': PUBLISHER}}) + ld(breadcrumbs([('About', 'about'), ('David Collins', slug)]))
    trail = []
    if slug.startswith('work/'):
        trail.append(('Work', 'work'))
    trail.append((p.get('crumb') or plain(p['title']).split(' | ')[0], slug))
    return ld(breadcrumbs(trail))

def page_shell(p, body, with_hero=True, with_closing=True):
    slug = p['slug'].strip('/')
    url = page_url(slug)
    title = p['title'] if 'Collective' in p['title'] else p['title']+' | Collective'
    description = escape(p['description'], quote=True)
    robots = 'noindex,nofollow' if slug == '404' else 'index,follow'
    if slug != '404':
        SITEMAP.append(url)
        PAGE_INDEX[slug] = (plain(p['title']).split(' | ')[0] if slug else 'Home', p['description'])
    head = f'''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#f7f7f2"><meta name="robots" content="{robots}"><title>{escape(title)}</title><meta name="description" content="{description}"><link rel="canonical" href="{url}"><meta property="og:title" content="{escape(title,quote=True)}"><meta property="og:description" content="{description}"><meta property="og:type" content="{'article' if p.get('article') else 'website'}"><meta property="og:url" content="{url}"><meta property="og:image" content="{SITE}/assets/identity/collective-social-share.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Collective | red brackets around the Collective wordmark"><meta name="twitter:card" content="summary_large_image"><link rel="icon" type="image/svg+xml" href="/assets/identity/collective-favicon.svg"><link rel="icon" type="image/png" sizes="32x32" href="/assets/identity/favicon-32.png"><link rel="apple-touch-icon" sizes="180x180" href="/assets/identity/apple-touch-icon.png"><link rel="preload" href="/assets/fonts-v2/archivo-latin-variable.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="/styles.css"><link rel="stylesheet" href="/brackets.css"><link rel="stylesheet" href="/site.css"><script src="/site-config.js" defer></script><script src="/measurement.js" defer></script><script src="/site.js" defer></script><script src="/enquiry.js" defer></script><script src="/brackets.js" defer></script>{structured_data(p)}</head><body class="full-site {escape(p.get('body_class',''),quote=True)}" id="top">'''
    main = (page_hero(p) if with_hero else '') + body
    return head+header(p.get('nav',''))+f'<main id="main">{main}</main>'+(closing() if with_closing else '')+footer()+'</body></html>\n'

# v5 links use trailing slashes (/about/, /capabilities/#demand). The live URLs are
# slashless, so every internal page link drops the slash before any query or fragment.
INTERNAL_LINK = re.compile(r'href="(/[^"#?]*[^/"#?])/((?:[?#][^"]*)?)"')

def slashless(html):
    return INTERNAL_LINK.sub(lambda m: f'href="{m.group(1)}{m.group(2)}"', html)

def write(relative, text):
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    GENERATED.append(relative)

def write_page(slug, html):
    slug = slug.strip('/')
    write((slug or 'index') + '.html', line_arrows(slashless(html)))

def article_heading(a):
    # An article may name the closing phrase of its title as its one red phrase (title_red).
    title, red = a['title'], a.get('title_red')
    if not red:
        return escape(title)
    if not title.endswith(' ' + red):
        raise ValueError(f"{a['slug']}: title_red {red!r} is not the close of the title")
    return f'{escape(title[:-len(red)])}<span class="red-text">{escape(red)}</span>'

def article_rows(articles, limit=None):
    html=[]
    for i,a in enumerate(articles[:limit] if limit else articles,1):
        html.append(f'''<a class="article-row" href="/insights/{a['slug']}/"><span class="mono">{i:02d} / {escape(a.get('category','Field note'))}</span><div><h3>{escape(a['title'])}</h3><p>{escape(a['description'])}</p></div><span class="row-arrow" aria-hidden="true">↗</span></a>''')
    return '<div class="article-rows">'+''.join(html)+'</div>'

def related(a, series):
    # A series article's two rows are the pillar and the glossary; theirs are each other and part one.
    pillar, glossary = series[0], series[-1]
    rows = [x for x in [pillar, glossary, series[1]] if x['slug'] != a['slug']]
    return rows[:2]

def byline(a):
    name = a.get('byline', 'Collective')
    return f'By <a href="/{AUTHOR_SLUG}">{escape(name)}</a>' if name == 'David Collins' else f'By {escape(name)}'

def series_navigation(a, series):
    # Previous and next between the seven parts, in series order (C-SITE-ARTICLES-2).
    i = next(n for n, x in enumerate(series) if x['slug'] == a['slug'])
    links = []
    if i > 0:
        x = series[i - 1]
        links.append(f'<a class="text-action article-series-previous" href="/insights/{x["slug"]}"><span><span class="mono">Previous in the series</span>{escape(x["title"])}</span>{arrow("w")}</a>')
    if i < len(series) - 1:
        x = series[i + 1]
        links.append(f'<a class="text-action article-series-next" href="/insights/{x["slug"]}"><span><span class="mono">Next in the series</span>{escape(x["title"])}</span>{arrow("e")}</a>')
    return f'<nav class="article-series" aria-label="{escape(a["series"]["name"])}">' + ''.join(links) + '</nav>'

def author_box():
    return f'''<aside class="article-author" aria-label="About the author"><div class="section-label"><span class="mono">About the author</span><a class="article-author-linkedin" href="{LINKEDIN}" target="_blank" rel="me noopener" aria-label="David Collins on LinkedIn">{linkedin_icon()}</a></div><p class="article-author-name"><a href="/{AUTHOR_SLUG}">David Collins</a></p><p class="mono">{escape(AUTHOR_ROLE)}</p><p class="article-author-bio">{escape(AUTHOR_BIO)}</p></aside>'''

# The author page. Each line is in the credential sources, with its source and the date read.
AUTHOR_EXPERIENCE = [
    'Founder and director of Collective, which has been operating for more than four years.',
    'Founder and director of Stratosphere, a marketing practice for property development, property investment, construction and trades, and buyers agents.',
    'In-house sales and marketing leadership at <a href="/work/little-fish">Little Fish Property Developments</a>: customer relationship management (CRM) and reporting, acquisition, automation and demand generation.',
    'Digital Account Director at Impressive Digital, 2020 to 2021, and Senior Digital Account Manager at King Kong, 2018 to 2020.',
    'Studied business at the University of the Sunshine Coast, majoring in marketing and management.',
    'Built HyperCtrl, the operating system Collective uses as execution infrastructure behind the work.',
]
AUTHOR_RECOGNITION = [
    'Listed by PPC Experts in its Top 100 Most Influential PPC Experts, 2023 and 2024. David placed in the top 50 globally and first in Australia. PPC is pay-per-click advertising.',
    'Australian Financial Review Top 100 Fast Starters, 2022, for Little Fish Property Developments. The listing belongs to that business; David led the sales and marketing strategy behind the growth it was listed for.',
    'Australian Enterprise Awards, Best Residential Property Development Firm, Melbourne, 2021 and 2022, for Little Fish Property Developments. The award belongs to that business, where David led sales and marketing.',
]

AUTHOR_SOURCES = ('Sources: <a href="/about">the Collective about page</a> and <a href="https://www.stratospheregroup.com.au/about/david-collins/">'
                  'David’s author page on the Stratosphere website</a>, read 10 November 2026.')

def author_page(articles):
    page = {'slug': AUTHOR_SLUG, 'title': 'David Collins, founder and director', 'description': 'David Collins is the founder and director of Collective and the author of its articles. His experience, recognition and every article he has written for Collective.',
            'nav': 'about', 'eyebrow': '05 / About the author', 'heading': 'DAVID<br><span class="red-text">COLLINS.</span>', 'hero_note': AUTHOR_ROLE, 'intro': AUTHOR_BIO,
            'hero_action': {'href': LINKEDIN, 'label': 'David Collins on LinkedIn'}}
    lines = lambda items: ''.join(f'<p>{x}</p>' for x in items)
    body = f'''<section class="page-section page-width"><div class="section-label"><span class="mono">01 / Experience</span><span class="mono">Agency, in-house and founder roles</span></div><div class="section-split"><h2 class="display-heading">THE WORK<br>BEHIND THE<br><span class="red-text">WRITING.</span></h2><div class="prose author-lines">{lines(AUTHOR_EXPERIENCE)}<p class="author-sources">{AUTHOR_SOURCES}</p></div></div></section><section class="page-section page-width"><div class="section-label"><span class="mono">02 / Recognition</span><span class="mono">Each listing names who it belongs to</span></div><div class="section-split"><h2 class="display-heading">THE<br><span class="red-text">RECOGNITION.</span></h2><div class="prose author-lines">{lines(AUTHOR_RECOGNITION)}<p class="author-sources">Source: <a href="https://www.stratospheregroup.com.au/about/david-collins/">David’s author page on the Stratosphere website</a>, read 10 November 2026.</p><a class="text-action" href="{LINKEDIN}" target="_blank" rel="me noopener"><span>David Collins on LinkedIn</span>{linkedin_icon()}</a></div></div></section><section class="page-section page-width"><div class="section-label"><span class="mono">03 / Articles</span><span class="mono">Every article on Collective</span></div>{article_rows(articles)}</section>'''
    return page, body

def llms_txt(articles):
    # What Collective is, in the site's own words (the about page and the home description), then one line per page.
    lines = ['# Collective', '',
             '> Collective is an independent growth business led by David Collins. Collective connects strategy, acquisition, conversion and operations around the commercial priorities of your business.', '',
             'Every article is written by David Collins, founder and director of Collective: ' + page_url(AUTHOR_SLUG), '', '## Articles', '']
    lines += [f'- [{a["title"]}]({page_url("insights/" + a["slug"])}): {a["description"]}' for a in articles]
    lines += ['', '## Pages', '']
    # Three pages' own descriptions read as lists of terms; their lines here are taken from their introductions or say what the page holds.
    lines_for = {'partnership': 'A partnership for two ecommerce businesses, with David directly involved in the decisions and the work.',
                 'developer-partnership': 'A partnership for property developers building a business and brand across projects.',
                 'about': 'Who leads Collective, how the work comes together, and the businesses beside it.'}
    for slug in ['', 'approach', 'capabilities', 'work', 'insights', 'about', AUTHOR_SLUG, 'partnership', 'developer-partnership', 'contact']:
        name, description = PAGE_INDEX[slug]
        description = lines_for.get(slug, description)
        lines.append(f'- [{name}]({page_url(slug)}): {description}')
    return '\n'.join(lines) + '\n'

# Beneath v5's form on /contact: the Antares chat and booking widget kept from the
# live site (ANTARES-3), styled with v5's tokens (site.css, .contact-booking).
BOOKING = '''<section class="contact-booking page-width" aria-labelledby="contact-booking-title"><div class="section-label"><span class="mono">Prefer to talk it through?</span><span class="mono">Book a time in chat</span></div><div class="contact-booking-body"><div class="contact-booking-intro"><h2 id="contact-booking-title">Ask a question,<br>or book a time.</h2><p>Use the chat to ask a question or choose a time to speak with David.</p></div><div class="contact-booking-chat" data-antares-chat></div></div><script src="https://yceyuxsltbtxhlxymury.supabase.co/functions/v1/scheduler-agent/widget.js" data-tenant="collective" data-heading="Discuss a project" data-label="Book a time in chat" defer></script></section>'''

def main():
    parser=argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--no-lead-test-host', action='store_true', help='Build without the preview TEST-lead host (enquiries send only from the production origin).')
    args=parser.parse_args()
    config={'environment':'production','productionOrigin':SITE,'enquiryMode':'api','leadEndpoint':'/api/lead','leadTestHost':None if args.no_lead_test_host else LEAD_TEST_HOST,'measurementEnabled':True,'analyticsConsent':'granted','gtmContainerId':GTM_CONTAINER,'gtmTestEnvironment':None if args.no_lead_test_host else GTM_PREVIEW_ENVIRONMENT}
    write('site-config.js', '/* Generated launch settings (site-src/build.py). measurement.js loads GTM from these. */\nwindow.CollectiveSite = Object.freeze('+json.dumps(config,separators=(',',':'))+');\n')
    pages=[json.loads(p.read_text()) for p in sorted((CONTENT/'pages').glob('*.json'))]
    articles=[json.loads(p.read_text()) for p in sorted((CONTENT/'articles').glob('*.json'))]
    priority=['independent-growth-business','diagnose-marketing-performance','pipeline-velocity','revenue-and-profit']
    articles.sort(key=lambda x:priority.index(x['slug']) if x['slug'] in priority else 99+x.get('series',{}).get('position',0))
    notes=[a for a in articles if 'series' not in a]
    series=[a for a in articles if 'series' in a]
    for p in pages:
        body=p['body']
        if p['slug']=='approach':
            body+=(CONTENT/'fragments/scenarios.html').read_text().replace('id="approach"','id="situations"').replace('02 / A view into the thinking','A closer look / Ecommerce examples')
        write_page(p['slug'],page_shell(p,body))
    home={'slug':'','title':'Collective | Grow what you keep.','description':'An independent growth partner. Collective connects strategy, acquisition, conversion and operations around the commercial priorities of your business. Led by David Collins.','nav':'','body_class':'home-page'}
    body=(CONTENT/'home.html').read_text().replace('<!-- ARTICLE_ROWS -->',article_rows(articles,3))
    write_page('',page_shell(home,body,False))
    insights={'slug':'insights','title':'Thinking','description':'Field notes on commercial growth, diagnosis and measurement. A seven-part series on ecommerce commercial performance. Practical thinking from Collective.','nav':'insights','eyebrow':'04 / Thinking','heading':'THE QUESTIONS<br>BEHIND <span class="red-text">THE WORK.</span>','intro':'A closer look at the decisions that shape growth. What to measure, where to look, and why the next move depends on the business.'}
    intro='<section class="page-section page-width" id="field-notes"><div class="section-label" id="frameworks"><span class="mono">Field notes / Read in full</span><span class="mono">A point of view, put to work</span></div>'+article_rows(notes)+'</section>'
    if series:
        intro+='<section class="page-section page-width" id="commercial-performance"><div class="section-label"><span class="mono">Commercial performance series / Read in order</span><span class="mono">Ecommerce, from revenue to cash</span></div>'+article_rows(series)+'</section>'
    write_page('insights',page_shell(insights,intro))
    for a in articles:
        reading=max(1,round(len(re.sub('<[^>]+>',' ',a['body']).split())/220))
        p={'slug':'insights/'+a['slug'],'title':a.get('seo_title',a['title']),'description':a['description'],'nav':'insights','body_class':'article-page','article':a}
        contents=''.join(f'<a href="#section-{i}">{escape(re.sub("<[^>]+>","",h))}</a>' for i,h in enumerate(re.findall(r'<h2[^>]*>(.*?)</h2>',a['body'],re.S),1))
        count=[0]
        def heading(m):
            count[0]+=1
            return f'<h2 id="section-{count[0]}">{m.group(1)}</h2>'
        article_body=re.sub(r'<h2[^>]*>(.*?)</h2>',heading,a['body'],flags=re.S)
        body=f'''<header class="article-hero page-width"><a href="/insights/" class="mono">← All thinking</a><div class="article-meta mono"><span>{escape(a.get('category','Field note'))}</span><span><time datetime="{DATES[a['slug']][0]}">{long_date(DATES[a['slug']][0])}</time> / {reading} minute read</span></div><h1>{article_heading(a)}</h1><div class="article-standfirst"><span class="mono">{byline(a)}</span><p>{a.get('intro_html') or escape(a['intro'])}</p></div></header><section class="article-layout page-width"><aside class="article-contents"><span class="mono">In this note</span><nav aria-label="Article contents">{contents}</nav></aside><article class="article-body">{article_body}{series_navigation(a, series) if 'series' in a else ''}{author_box()}<div class="article-end"><span class="mono">Continue the conversation</span><a class="text-action" href="/contact/"><span>What does this mean for your business?</span>{ARROW}</a></div></article></section><section class="page-section page-width related-reading"><div class="section-label"><span class="mono">Keep thinking</span><a class="mono" href="/insights/">All field notes ↗</a></div>{article_rows(related(a,series) if 'series' in a else [x for x in articles if x['slug']!=a['slug']],2)}</section>'''
        write_page(p['slug'],page_shell(p,body,False))
        LASTMOD[page_url(p['slug'])] = DATES[a['slug']][2]
    write_page(AUTHOR_SLUG, page_shell(*author_page(articles)))
    contact={'slug':'contact','title':'Let’s talk','description':'Start a conversation with David Collins about your business, the opportunity and what you would like to change.','nav':'contact','eyebrow':'A conversation with Collective','heading':'LET’S LOOK AT<br><span class="red-text">THE BUSINESS.</span>','intro':'Tell us where you are, where you want to get to and what is getting in the way. You do not need to arrive with the answer.','crumb':'Contact'}
    write_page('contact',page_shell(contact,(CONTENT/'contact.html').read_text()+BOOKING,True,False))
    partnership={'slug':'partnership','title':'Ecommerce founding partnership','description':'Two founding ecommerce partnerships with direct founder involvement. AUD $10,000 per month + GST for agreed scope; implementation, advertising and agreed third-party costs additional.','nav':'','eyebrow':'The ecommerce founding partnership','heading':'A CLOSER<br><span class="red-text">PARTNERSHIP.</span>','intro':'A close working partnership for two established ecommerce businesses. One commercial plan, connected delivery and David directly involved in the decisions and the work.','hero_note':'Two places. Staggered onboarding.'}
    offer=(CONTENT/'fragments/partnership.html').read_text()
    offer=offer.replace('<button class="solid-action" data-apply>Apply for a founding partnership <span aria-hidden="true">↗</span></button>','<a class="solid-action" href="/contact/?enquiry=partnership">Enquire about a founding partnership <span aria-hidden="true">↗</span></a>')
    offer=offer.replace('04 / The founding partnership','01 / The engagement').replace('01 / Application','01 / Enquiry')
    offer+=(CONTENT/'fragments/questions.html').read_text()
    write_page('partnership',page_shell(partnership,offer))
    notfound={'slug':'404','title':'Page not found','description':'Find your way back to Collective.','nav':'','eyebrow':'404 / Page not found','heading':'A DIFFERENT<br><span class="red-text">DIRECTION.</span>','intro':'That page is not here. Start from the homepage or explore what Collective can help with.'}
    write_page('404',page_shell(notfound,'<section class="page-section page-width"><a class="solid-action" href="/">Back to Collective <span aria-hidden="true">↗</span></a></section>',True,False))
    write('robots.txt', 'User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: '+SITE+'/sitemap.xml\n')
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc>'+(f'<lastmod>{LASTMOD[u]}</lastmod>' if u in LASTMOD else '')+'</url>' for u in sorted(SITEMAP))+'</urlset>\n')
    write('llms.txt', llms_txt(articles))
    rules=''.join(f'/{old}{suffix} {target} 301\n' for old,target in RETIRED.items() for suffix in ['', '/', '.html'])
    write('_redirects', '# The six retired routes (C-SITE-V5 plan section 3), each form one hop. Generated by site-src/build.py.\n'+rules)
    print(f'Built {len(SITEMAP)} indexable pages ({len(articles)} articles) and a 404 page; {len(RETIRED)*3} redirect rules; {len(GENERATED)} files.')

if __name__=='__main__':
    main()

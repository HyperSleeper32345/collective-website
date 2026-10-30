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
- JSON-LD: Organization on home, Article and BreadcrumbList on the four articles,
  BreadcrumbList on the other pages.
- The contact page keeps the Antares chat and booking widget beneath the form.

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
SITEMAP = []
GENERATED = []

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
<dialog class="site-menu" id="site-menu" aria-label="Site navigation"><div class="menu-top"><a class="brand" href="/" aria-label="Collective home">{brand()}</a><button type="button" data-close-menu aria-label="Close navigation">Close <span aria-hidden="true">×</span></button></div><nav aria-label="Mobile navigation"><a href="/">Home</a>{nav_links(active)}<a href="/contact/">Let’s talk {ARROW}</a></nav><div class="menu-bottom"><a href="/partnership/">Ecommerce founding partnership {ARROW}</a><a href="/developer-partnership/">Developer founding partnership {ARROW}</a><span class="mono">Founder-led. Australia.</span></div></dialog>'''

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

PUBLISHER = {'@type': 'Organization', 'name': 'Collective', 'url': SITE + '/',
             'logo': {'@type': 'ImageObject', 'url': SITE + '/assets/identity/collective-primary.png'}}

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
                   'author': {'@type': 'Person', 'name': 'David Collins'}, 'publisher': PUBLISHER,
                   'isPartOf': {'@type': 'CollectionPage', 'name': 'Thinking', 'url': page_url('insights')}},
                  breadcrumbs([('Thinking', 'insights'), (a['title'], slug)])]
        return ''.join(ld(b) for b in blocks)
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
    write((slug or 'index') + '.html', slashless(html))

def article_rows(articles, limit=None):
    html=[]
    for i,a in enumerate(articles[:limit] if limit else articles,1):
        html.append(f'''<a class="article-row" href="/insights/{a['slug']}/"><span class="mono">0{i} / {escape(a.get('category','Field note'))}</span><div><h3>{escape(a['title'])}</h3><p>{escape(a['description'])}</p></div><span class="row-arrow" aria-hidden="true">↗</span></a>''')
    return '<div class="article-rows">'+''.join(html)+'</div>'

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
    articles.sort(key=lambda x:priority.index(x['slug']) if x['slug'] in priority else 99)
    for p in pages:
        body=p['body']
        if p['slug']=='approach':
            body+=(CONTENT/'fragments/scenarios.html').read_text().replace('id="approach"','id="situations"').replace('02 / A view into the thinking','A closer look / Ecommerce examples')
        write_page(p['slug'],page_shell(p,body))
    home={'slug':'','title':'Collective | Grow what you keep.','description':'An independent growth partner. Collective connects strategy, acquisition, conversion and operations around the commercial priorities of your business. Led by David Collins.','nav':'','body_class':'home-page'}
    body=(CONTENT/'home.html').read_text().replace('<!-- ARTICLE_ROWS -->',article_rows(articles,3))
    write_page('',page_shell(home,body,False))
    insights={'slug':'insights','title':'Thinking','description':'Field notes on commercial growth, diagnosis and measurement. Practical thinking from Collective.','nav':'insights','eyebrow':'04 / Thinking','heading':'THE QUESTIONS<br>BEHIND <span class="red-text">THE WORK.</span>','intro':'A closer look at the decisions that shape growth. What to measure, where to look, and why the next move depends on the business.'}
    intro='<section class="page-section page-width" id="field-notes"><div class="section-label" id="frameworks"><span class="mono">Field notes / Read in full</span><span class="mono">A point of view, put to work</span></div>'+article_rows(articles)+'</section>'
    write_page('insights',page_shell(insights,intro))
    for a in articles:
        reading=max(1,round(len(re.sub('<[^>]+>',' ',a['body']).split())/220))
        p={'slug':'insights/'+a['slug'],'title':a['title'],'description':a['description'],'nav':'insights','body_class':'article-page','article':a}
        contents=''.join(f'<a href="#section-{i}">{escape(re.sub("<[^>]+>","",h))}</a>' for i,h in enumerate(re.findall(r'<h2[^>]*>(.*?)</h2>',a['body'],re.S),1))
        count=[0]
        def heading(m):
            count[0]+=1
            return f'<h2 id="section-{count[0]}">{m.group(1)}</h2>'
        article_body=re.sub(r'<h2[^>]*>(.*?)</h2>',heading,a['body'],flags=re.S)
        body=f'''<header class="article-hero page-width"><a href="/insights/" class="mono">← All thinking</a><div class="article-meta mono"><span>{escape(a.get('category','Field note'))}</span><span>{reading} minute read</span></div><h1>{escape(a['title'])}</h1><div class="article-standfirst"><span class="mono">By {escape(a.get('byline','Collective'))}</span><p>{escape(a['intro'])}</p></div></header><section class="article-layout page-width"><aside class="article-contents"><span class="mono">In this note</span><nav aria-label="Article contents">{contents}</nav></aside><article class="article-body">{article_body}<div class="article-end"><span class="mono">Continue the conversation</span><a class="text-action" href="/contact/"><span>What does this mean for your business?</span>{ARROW}</a></div></article></section><section class="page-section page-width related-reading"><div class="section-label"><span class="mono">Keep thinking</span><a class="mono" href="/insights/">All field notes ↗</a></div>{article_rows([x for x in articles if x['slug']!=a['slug']],2)}</section>'''
        write_page(p['slug'],page_shell(p,body,False))
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
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join('<url><loc>'+u+'</loc></url>' for u in sorted(SITEMAP))+'</urlset>\n')
    rules=''.join(f'/{old}{suffix} {target} 301\n' for old,target in RETIRED.items() for suffix in ['', '/', '.html'])
    write('_redirects', '# The six retired routes (C-SITE-V5 plan section 3), each form one hop. Generated by site-src/build.py.\n'+rules)
    print(f'Built {len(SITEMAP)} indexable pages ({len(articles)} articles) and a 404 page; {len(RETIRED)*3} redirect rules; {len(GENERATED)} files.')

if __name__=='__main__':
    main()

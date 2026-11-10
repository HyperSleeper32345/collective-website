#!/usr/bin/env python3
"""Convert the Commercial Performance series (C-SITE-ARTICLES-1) into article content.

The seven markdown files are David's approved copy and are published word for word:
this script converts their markdown to HTML and never changes a word. The first
paragraph becomes the standfirst (moved, not repeated), so the reading order stays
the source's. Links wrap words already in the text and add none.

Supported markdown, which is all the series uses: one `# ` title, `## ` and `### `
headings, paragraphs, `- ` and `1. ` lists, pipe tables with column alignment,
`**bold**` and a two-space hard line break.

  python3 site-src/markdown_article.py <articles folder>          write the seven JSON files
  python3 site-src/markdown_article.py <articles folder> --check  word diff of content against source

Standard library only. The build (site-src/build.py) then renders the pages.
"""
from pathlib import Path
from html import escape, unescape
import argparse
import json
import re
import sys

CONTENT = Path(__file__).resolve().parent / 'content' / 'articles'
SERIES_NAME = 'Commercial performance series'
GLOSSARY = 'ecommerce-performance-glossary'

# File, slug, title tag, meta description, category. The title tag and description are
# metadata, not article text; the H1 is always the file's own `# ` title.
SERIES = [
    ('00-understanding-ecommerce-commercial-performance.md', 'understanding-ecommerce-commercial-performance',
     'Understanding ecommerce commercial performance',
     'How revenue, contribution, profit, customer economics and cash connect in ecommerce. The order in which to read an executive dashboard.',
     'Commercial performance'),
    ('01-revenue-contribution-and-operating-profit.md', 'revenue-contribution-and-operating-profit',
     'Revenue, contribution and operating profit in ecommerce',
     'How net revenue becomes gross profit, contribution and operating profit. Why profit dollars and margins are read together, with an example month.',
     'Commercial performance'),
    ('02-reading-monthly-and-year-on-year-performance.md', 'reading-monthly-and-year-on-year-performance',
     'Reading monthly and year-on-year ecommerce performance',
     'How to choose a comparison period for ecommerce results. Dollars, percentages and percentage points, and combined ratios from the totals.',
     'Commercial performance'),
    ('03-mer-roas-and-profitable-growth.md', 'mer-roas-and-profitable-growth',
     'MER, ROAS and profitable growth in ecommerce',
     'How MER and ROAS differ, and how efficiency relates to contribution and profit. How to test assumptions about spending more on media.',
     'Commercial performance'),
    ('04-customer-acquisition-cost-customer-value-and-payback.md', 'customer-acquisition-cost-value-and-payback',
     'Customer acquisition cost, customer value and payback',
     'Business media CAC, allowable CAC, contribution lifetime value and payback. How cohorts show when acquisition cost is recovered.',
     'Commercial performance'),
    ('05-cash-inventory-and-the-pace-of-growth.md', 'cash-inventory-and-the-pace-of-growth',
     'Cash, inventory and the pace of ecommerce growth',
     'Why profit and cash follow different timing. How to read a cash forecast by date, stock cover and the reserve that limits growth.',
     'Commercial performance'),
    ('06-ecommerce-performance-glossary.md', GLOSSARY,
     'Ecommerce glossary: profit, MER, CAC and cash',
     'Definitions and calculations for the measures in the Commercial Performance series. Revenue, contribution, profit, MER, ROAS, CAC, LTV, payback and cash.',
     'Reference'),
]
PILLAR = SERIES[0][1]

# Phrases already in the text that name another part of the series, or a live service page:
# (source file, phrase, destination). The first whole-phrase occurrence in the file's body
# paragraphs and lists is wrapped; the words stay as they are (C-SITE-ARTICLES-2).
SERIES_PHRASES = [
    ('02-reading-monthly-and-year-on-year-performance.md', 'the previous article', 'revenue-contribution-and-operating-profit'),
    ('04-customer-acquisition-cost-customer-value-and-payback.md', 'this series', PILLAR),
    ('00-understanding-ecommerce-commercial-performance.md', 'An executive dashboard', '/capabilities#operations'),
    ('02-reading-monthly-and-year-on-year-performance.md', 'MER', 'mer-roas-and-profitable-growth'),
    ('03-mer-roas-and-profitable-growth.md', 'this series', PILLAR),
    ('03-mer-roas-and-profitable-growth.md', 'acquisition cost, customer value and payback', 'customer-acquisition-cost-value-and-payback'),
    ('04-customer-acquisition-cost-customer-value-and-payback.md', 'profit, inventory and available cash', 'cash-inventory-and-the-pace-of-growth'),
    ('05-cash-inventory-and-the-pace-of-growth.md', 'earlier articles', PILLAR),
    ('05-cash-inventory-and-the-pace-of-growth.md', 'previous article', 'customer-acquisition-cost-value-and-payback'),
    ('06-ecommerce-performance-glossary.md', 'this series', PILLAR),
]

def href(target):
    return target if target.startswith('/') else f'/insights/{target}'

def outside_links(html, change):
    """Apply change to the text between tags that is not already inside a link."""
    out, depth = [], 0
    for part in re.split(r'(<[^>]+>)', html):
        if part.startswith('<'):
            depth += 1 if re.match(r'<a\b', part) else -1 if part.startswith('</a') else 0
            out.append(part)
        else:
            out.append(change(part) if depth == 0 else part)
    return ''.join(out)

def link_phrase(html, phrase, target):
    """Wrap the first whole-phrase occurrence outside a link; return the html and whether it was found."""
    pattern = re.compile(r'(?<![\w-])' + re.escape(phrase) + r'(?![\w-])')
    done = [False]
    def change(text):
        if done[0]:
            return text
        new = pattern.sub(lambda m: f'<a href="{href(target)}">{m.group(0)}</a>', text, count=1)
        done[0] = new != text
        return new
    return outside_links(html, change), done[0]

def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def inline(text):
    html = escape(text, quote=False)
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    if '*' in html:
        raise ValueError(f'unsupported inline markdown: {text}')
    return html

def table(lines):
    rows = [[c.strip() for c in line.strip().strip('|').split('|')] for line in lines]
    head, rule, body = rows[0], rows[1], rows[2:]
    numeric = [c.endswith(':') and not c.startswith(':') for c in rule]
    # On a phone (13px type, site.css) a table that cannot fit as a grid reflows: every
    # row, the heading row included, on the same small grid, the first cell across the
    # top and the figures beneath it in one line. The width is estimated from the longest word in
    # each column: over 400px it reflows under 620px wide, over 280px under 380px wide.
    def longest(i):
        return max([len(w) for r in body for w in r[i].replace('**', '').split()] + [min(len(w), 8) for w in head[i].replace('**', '').split()])
    estimate = sum(longest(i) * 7.8 + 12 for i in range(len(head)))
    values = len(head) - 1
    reflow = '' if estimate <= 280 else ' article-table--reflow' if estimate > 400 else ' article-table--reflow-narrow'
    if reflow and values > 3:
        reflow += f' article-table--reflow-{values}'
    def cls(i):
        return ' class="num"' if numeric[i] else ''
    out = [f'<table class="article-table article-table--series{reflow}"><thead><tr>' + ''.join(f'<th scope="col"{cls(i)}>{inline(c)}</th>' for i, c in enumerate(head)) + '</tr></thead><tbody>']
    for r in body:
        cells = [f'<th scope="row">{inline(r[0])}</th>'] + [f'<td{cls(i)}>{inline(c)}</td>' for i, c in enumerate(r[1:], 1)]
        out.append('<tr>' + ''.join(cells) + '</tr>')
    out.append('</tbody></table>')
    return '\n'.join(out)

def blocks(markdown):
    """Yield (kind, html) for each block, in source order."""
    lines = markdown.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            text = line[level:].strip()
            yield f'h{level}', text
            i += 1
            continue
        group = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith('#'):
            group.append(lines[i])
            i += 1
        if group[0].startswith('|'):
            yield 'table', table(group)
        elif re.match(r'- ', group[0]):
            yield 'ul', '<ul>' + ''.join(f'<li>{inline(l[2:])}</li>' for l in group) + '</ul>'
        elif re.match(r'\d+\. ', group[0]):
            yield 'ol', '<ol>' + ''.join('<li>' + inline(re.sub(r'^\d+\. ', '', l)) + '</li>' for l in group) + '</ol>'
        else:
            parts = [inline(l[:-2] if l.endswith('  ') else l) + ('<br>' if l.endswith('  ') else '') for l in group]
            yield 'p', '<p>' + '\n'.join(parts) + '</p>'

def glossary_terms(markdown):
    return [line[4:].strip() for line in markdown.split('\n') if line.startswith('### ')]

def link_terms(html, terms, linked):
    """Wrap the first occurrence of each glossary term on the page in a link to its entry."""
    if not terms:
        return html
    pattern = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(t) for t in sorted(terms, key=len, reverse=True)) + r')(?![\w-])', re.I)
    def text(segment):
        def wrap(m):
            key = m.group(1).lower()
            if key in linked:
                return m.group(1)
            linked.add(key)
            return f'<a href="/insights/{GLOSSARY}#{slugify(key)}">{m.group(1)}</a>'
        return pattern.sub(wrap, segment)
    return outside_links(html, text)

# The closing phrase of each title carries the brand's one red phrase (David, 10 Nov 2026;
# C-SITE-ARTICLES-1B). The words stay the title's own: build.py only wraps them in the H1.
# Each phrase is short enough to stay on the title's last line at 320 to 1440 wide.
TITLE_RED = {
    'understanding-ecommerce-commercial-performance': 'performance',
    'revenue-contribution-and-operating-profit': 'operating profit',
    'reading-monthly-and-year-on-year-performance': 'performance',
    'mer-roas-and-profitable-growth': 'profitable growth',
    'customer-acquisition-cost-value-and-payback': 'payback',
    'cash-inventory-and-the-pace-of-growth': 'growth',
    GLOSSARY: 'glossary',
}

def convert(source, glossary_md):
    name = source.name
    entry = next(s for s in SERIES if s[0] == name)
    _, slug, seo_title, description, category = entry
    markdown = source.read_text()
    items = list(blocks(markdown))
    if [k for k, _ in items].count('h1') != 1 or items[0][0] != 'h1':
        raise ValueError(f'{name}: expected one # title first')
    title = items[0][1]
    if items[1][0] != 'p':
        raise ValueError(f'{name}: expected a first paragraph after the title')
    intro_html = items[1][1][3:-4]
    # Glossary terms of two or more words link to their entry; single words are too general.
    terms = [] if slug == GLOSSARY else [t for t in glossary_terms(glossary_md) if ' ' in t or '-' in t]
    linked = set()
    phrases = [(p, s) for f, p, s in SERIES_PHRASES if f == name]
    expected = len(phrases)
    body = []
    for kind, html in items[2:]:
        if kind in ('h2', 'h3'):
            text = inline(html)
            attr = f' id="{slugify(html)}" class="glossary-term"' if slug == GLOSSARY and kind == 'h3' else ''
            body.append(f'<{kind}{attr}>{text}</{kind}>')
            continue
        if kind in ('p', 'ul', 'ol'):
            for phrase, target in list(phrases):
                html, found = link_phrase(html, phrase, target)
                if found:
                    phrases.remove((phrase, target))
            html = link_terms(html, terms, linked)
        if kind == 'table' and slug == PILLAR:
            # The pillar's series table names each article in bold: the name links to it.
            for s in SERIES[1:6]:
                t = next(b for k, b in blocks((source.parent / s[0]).read_text()) if k == 'h1')
                html = html.replace(f'<strong>{escape(t, quote=False)}</strong>', f'<strong><a href="/insights/{s[1]}">{escape(t, quote=False)}</a></strong>')
        body.append(html)
    if phrases:
        raise ValueError(f'{name}: {len(phrases)} of {expected} series phrases not found: {phrases}')
    position = SERIES.index(entry) + 1
    if not title.endswith(' ' + TITLE_RED[slug]):
        raise ValueError(f'{name}: the red phrase {TITLE_RED[slug]!r} is not the close of the title')
    article = {'slug': slug, 'title': title, 'title_red': TITLE_RED[slug], 'seo_title': seo_title, 'description': description,
               'category': category, 'byline': 'David Collins',
               'intro': re.sub(r'<[^>]+>', '', unescape(intro_html)), 'intro_html': intro_html,
               'series': {'name': SERIES_NAME, 'position': position, 'source': name},
               'body': '\n'.join(body)}
    if slug == GLOSSARY:
        article['defined_terms'] = defined_terms(items)
    return article

def defined_terms(items):
    """Each term heading and the first paragraph of its entry, for the DefinedTermSet."""
    terms = []
    for (kind, text), nxt in zip(items, items[1:]):
        if kind == 'h3' and nxt[0] == 'p':
            terms.append({'name': text, 'id': slugify(text), 'description': re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', '', nxt[1]))).strip()})
    return terms

def plain(html):
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', html))).strip()

def source_words(markdown):
    """The source's words with markdown syntax removed: markers, table rules and pipes."""
    out = []
    for line in markdown.split('\n'):
        if re.fullmatch(r'\|?[\s:|-]+\|?', line) and '-' in line:
            continue
        if line.startswith('#'):
            line = re.sub(r'^#+ ', '', line)
        else:
            line = re.sub(r'^(- |\d+\. )', '', line)
        line = line.replace('**', '').replace('|', ' ')
        out.extend(line.split())
    return out

def content_words(article):
    html = f'<h1>{escape(article["title"])}</h1><p>{article["intro_html"]}</p>' + article['body']
    html = re.sub(r'<(?:/?(?:p|li|ul|ol|h\d|table|thead|tbody|tr|th|td)|br)\b[^>]*>', ' ', html)
    return unescape(re.sub(r'<[^>]+>', '', html)).split()

def word_diff(a, b):
    import difflib
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if tag != 'equal')

def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('source', type=Path, help='the series articles folder')
    parser.add_argument('--check', action='store_true', help='compare the content files with the source; write nothing')
    args = parser.parse_args()
    glossary_md = (args.source / SERIES[-1][0]).read_text()
    failures = 0
    for name, slug, *_ in SERIES:
        source = args.source / name
        article = convert(source, glossary_md)
        path = CONTENT / f'{slug}.json'
        if args.check:
            stored = json.loads(path.read_text())
            diff = word_diff(source_words(source.read_text()), content_words(stored))
            failures += diff > 0 or stored != article
            print(f'{slug}: {len(source_words(source.read_text()))} source words, {diff} word differences' + ('' if stored == article else ', content file out of date'))
        else:
            path.write_text(json.dumps(article, ensure_ascii=False, indent=2) + '\n')
            print(f'wrote {path.relative_to(CONTENT.parent.parent.parent)}')
    sys.exit(1 if failures else 0)

if __name__ == '__main__':
    main()

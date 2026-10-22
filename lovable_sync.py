#!/usr/bin/env python3
"""Sync the static Charleston comp into the git-connected Lovable repo.

Source of truth: this folder (index.html + the pages build_pages.py writes).
Target: ../../../Lovable/charleston-charm-builder (bytezeroinc-cloud/charleston-charm-builder,
which Lovable pulls from `main` without agent credits).

What it writes:
  src/styles/charleston.css, src/styles/pages.css   verbatim copies
  public/img/{w,brand,cred}                          every image the comp uses
  src/content/<page>.html                            body markup, sprite through footer, with
                                                     /img paths and route links
  src/routes/<page>.tsx                              one route per page from the static head
Then run, in the repo:  bun install && bun run build && bunx tsc --noEmit  (regenerates routeTree.gen.ts)
"""
import re, json, pathlib, shutil, html as htmlmod

COMP = pathlib.Path(__file__).resolve().parent
REPO = COMP.parents[2] / 'Lovable' / 'charleston-charm-builder'
assert (REPO / 'package.json').exists(), f'Lovable clone not found at {REPO}'

PAGES = {  # static file -> route path
    'index.html': '/',
    'about.html': '/about',
    'faq.html': '/faq',
    'contact.html': '/contact',
    'mount-pleasant.html': '/mount-pleasant',
    'isle-of-palms.html': '/isle-of-palms',
    'sullivans-island.html': '/sullivans-island',
    'daniel-island.html': '/daniel-island',
    'custom-homes.html': '/custom-homes',
    'renovations-additions.html': '/renovations-additions',
    'design-preconstruction.html': '/design-preconstruction',
    'lowcountry.html': '/lowcountry',
    'process.html': '/process',
}
LINKS = {f: (p if p != '/' else '/') for f, p in PAGES.items()}

# ── 1. stylesheets ───────────────────────────────────────────────────────────
for name in ('charleston.css', 'pages.css'):
    css = (COMP / 'css' / name).read_text()
    assert 'url(img/' not in css, f'{name} has a relative image url; rewrite it to /img/'
    (REPO / 'src' / 'styles' / name).write_text(css)
print('css written')

# ── 2. images ────────────────────────────────────────────────────────────────
copied = 0
for sub in ('w', 'brand', 'cred'):
    src = COMP / 'img' / sub; dst = REPO / 'public' / 'img' / sub
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file() and not f.name.startswith('.'):
            t = dst / f.name
            if not t.exists() or t.stat().st_size != f.stat().st_size:
                shutil.copy2(f, t); copied += 1
print('images copied', copied)

# ── 3. content + routes ──────────────────────────────────────────────────────
def body_of(page):
    s = page
    i = s.index('<svg width="0" height="0"')
    j = s.index('</footer>') + len('</footer>')
    b = s[i:j]
    b = b.replace('="img/', '="/img/').replace("url(img/", "url(/img/")
    b = b.replace(' onsubmit="return false"', '')
    # page links
    for f, p in LINKS.items():
        if f == 'index.html':
            b = b.replace('href="index.html#', 'href="/#').replace('href="index.html"', 'href="/"')
        else:
            b = b.replace(f'href="{f}"', f'href="{p}"')
    return b

def head_of(page):
    h = page[page.index('<head>'):page.index('</head>')]
    get = lambda rx: (re.search(rx, h, re.S) or [None, None])[1]
    title = htmlmod.unescape(get(r'<title>(.*?)</title>'))
    desc = htmlmod.unescape(get(r'name="description" content="([^"]*)"'))
    og_title = htmlmod.unescape(get(r'property="og:title" content="([^"]*)"') or title)
    og_image = get(r'property="og:image" content="([^"]*)"')
    preloads = re.findall(r'<link rel="preload" as="image" href="([^"]+)"(?: media="([^"]*)")?>', h)
    return dict(title=title, description=desc, og_title=og_title, og_image='/' + og_image if og_image and not og_image.startswith('/') else og_image, preloads=[(u if u.startswith('/') else '/' + u, m or None) for u, m in preloads])

def jsonld_of(page):
    """Static ld+json blocks after the body (the org / page schema); FAQPage is derived from markup at runtime."""
    tail = page[page.index('</footer>'):]
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', tail, re.S)
    out = []
    for b in blocks:
        try:
            out.append(json.loads(b))
        except json.JSONDecodeError:
            pass
    return out

ROUTE_TPL = '''import {{ createFileRoute }} from "@tanstack/react-router";

import markup from "../content/{content}?raw";
import {{ charlestonPage }} from "../lib/charleston-page";

export const Route = createFileRoute("{path}")(
  charlestonPage({{
    path: "{path}",
    markup,
    title: {title},
    description: {description},
    ogTitle: {og_title},
    ogImage: {og_image},
    preloads: {preloads},
    inner: {inner},
    jsonLd: {jsonld},
  }}),
);
'''

routes_dir = REPO / 'src' / 'routes'
for file, path in PAGES.items():
    page = (COMP / file).read_text()
    slug = 'charleston-home' if file == 'index.html' else file[:-5]
    (REPO / 'src' / 'content' / f'{slug}.html').write_text(body_of(page))
    h = head_of(page)
    route_file = 'index.tsx' if file == 'index.html' else f'{file[:-5]}.tsx'
    tsx = ROUTE_TPL.format(
        content=f'{slug}.html', path=path,
        title=json.dumps(h['title']), description=json.dumps(h['description']),
        og_title=json.dumps(h['og_title']), og_image=json.dumps(h['og_image']),
        preloads=json.dumps([{"href": u, **({"media": m} if m else {})} for u, m in h['preloads']]),
        inner='false' if file == 'index.html' else 'true',
        jsonld=json.dumps(jsonld_of(page), ensure_ascii=False),
    )
    (routes_dir / route_file).write_text(tsx)
    print('route', route_file, '<-', file)
print('done: now `bun install && bun run build && bunx tsc --noEmit` in', REPO)

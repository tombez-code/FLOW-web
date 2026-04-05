#!/usr/bin/env python3
"""
Downloads all English pages from skolaflow.cz/en/* and saves them
to the en/ directory as a fully working offline clone.

Run from Terminal:
  cd "$(dirname "$0")"
  python3 download_english.py
"""
import os, re, urllib.request, urllib.parse, time, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EN_DIR = os.path.join(SCRIPT_DIR, 'en')
EN_PRO_ZAJEMCE = os.path.join(EN_DIR, 'pro-zajemce')
os.makedirs(EN_DIR, exist_ok=True)
os.makedirs(EN_PRO_ZAJEMCE, exist_ok=True)

BASE_URL = 'https://www.skolaflow.cz'
CDN_BASE = 'https://cdn.prod.website-files.com/67b351f4c755934221b66277/'

# Map: (url_path, save_path_relative_to_en_dir, depth_from_en_dir)
# depth=1 means file is directly in en/, depth=2 means in en/subdir/
PAGES = [
    ('/en',                                          'index.html',                                          1),
    ('/en/about-us',                                 'about-us.html',                                       1),
    ('/en/nase-skola',                               'nase-skola.html',                                     1),
    ('/en/vzdelavaci-program',                       'vzdelavaci-program.html',                             1),
    ('/en/pro-rodice',                               'pro-rodice.html',                                     1),
    ('/en/faq',                                      'faq.html',                                            1),
    ('/en/nas-tym',                                  'nas-tym.html',                                        1),
    ('/en/nas-model-vyuky-a-uceni',                  'nas-model-vyuky-a-uceni.html',                        1),
    ('/en/kariera',                                  'kariera.html',                                        1),
    ('/en/after-work-seminare-flow',                 'after-work-seminare-flow.html',                       1),
    ('/en/novy-kampus',                              'novy-kampus.html',                                    1),
    ('/en/pro-zajemce',                              'pro-zajemce.html',                                    1),
    ('/en/blog',                                     'blog.html',                                           1),
    ('/en/kontakt',                                  'kontakt.html',                                        1),
    ('/en/gdpr',                                     'gdpr.html',                                           1),
    ('/en/pro-zajemce/prijimaci-rizeni-do-1-rocniku-2026-27', 'pro-zajemce/prijimaci-rizeni-do-1-rocniku-2026-27.html', 2),
    ('/en/pro-zajemce/prestupy',                     'pro-zajemce/prestupy.html',                           2),
    ('/en/pro-zajemce/navstivte-skolu-flow',         'pro-zajemce/navstivte-skolu-flow.html',               2),
    ('/en/pro-zajemce/poplatky-2025-26',             'pro-zajemce/poplatky-2025-26.html',                   2),
]

def fetch_url(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.skolaflow.cz/en'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace')

def process_html(html, depth):
    """Process downloaded HTML: fix CDN refs, fix links, inject custom assets."""

    # ── 1. CDN image/font URLs → local paths ────────────────────────────────
    img_prefix  = '../' * depth + 'images/'
    font_prefix = '../' * depth + 'fonts/'

    def repl_cdn(m):
        path_part = urllib.parse.unquote(m.group(1).split('?')[0])
        filename  = path_part.split('/')[-1]
        ext       = os.path.splitext(filename)[1].lower()
        if ext in {'.woff', '.woff2', '.ttf', '.otf'}:
            return font_prefix + filename
        return img_prefix + filename

    html = re.sub(
        r'https://cdn\.prod\.website-files\.com/67b351f4c755934221b66277/([^\s"\'<>)]+)',
        repl_cdn, html
    )
    # uploads-ssl.webflow.com fallback
    html = re.sub(
        r'https://uploads-ssl\.webflow\.com/67b351f4c755934221b66277/([^\s"\'<>)]+)',
        repl_cdn, html
    )

    # ── 2. Internal EN links → relative local links ──────────────────────────
    up = '../' * depth  # e.g. '../' for depth=1, '../../' for depth=2

    # /en/pro-zajemce/xxx  → ../pro-zajemce/xxx.html  (from depth-1 file)
    #                       → ../../pro-zajemce/xxx.html (from depth-2 file)
    def fix_en_link(m):
        attr, path = m.group(1), m.group(2)
        # Strip /en prefix
        local = re.sub(r'^/en/?', '', path)
        if not local:
            # /en itself → index.html at en root
            return f'{attr}="index.html"'
        # Map to relative path from current depth
        # files in en/ (depth=1): href="about-us.html" or "pro-zajemce/xxx.html"
        # files in en/pro-zajemce/ (depth=2): href="../about-us.html" etc.
        if depth == 1:
            return f'{attr}="{local}.html"' if not local.endswith('.html') else f'{attr}="{local}"'
        else:
            # We're inside en/pro-zajemce/ — go up one level
            return f'{attr}="../{local}.html"' if not local.endswith('.html') else f'{attr}="../{local}"'

    # Fix /en/... hrefs
    html = re.sub(r'(href)="(/en[^"]*)"', fix_en_link, html)

    # CS links: /  /about-us  /nase-skola etc. → go up to CS root
    cs_root = '../' * depth  # from en/ depth=1 → '../'; from en/sub/ depth=2 → '../../'

    def fix_cs_link(m):
        attr, path = m.group(1), m.group(2)
        if path == '/':
            return f'{attr}="{cs_root}index.html"'
        if path.startswith('/') and not path.startswith('/en'):
            local = path.lstrip('/')
            return f'{attr}="{cs_root}{local}.html"' if not local.endswith('.html') else f'{attr}="{cs_root}{local}"'
        return m.group(0)

    html = re.sub(r'(href)="(/?[a-z][^"]*)"', fix_cs_link, html)

    # ── 3. Fix Calendly / remove Luma ────────────────────────────────────────
    html = re.sub(r'https://lu\.ma/skolaflow[^\s"\']+',
                  'https://calendly.com/skolaflowcz/kafe-s-ridou', html)
    html = html.replace('<script src="https://embed.lu.ma/checkout-button.js"></script>', '')

    # ── 4. Replace Webflow tracking scripts ──────────────────────────────────
    html = re.sub(r'<script[^>]*webflow[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<script[^>]*gtm[^>]*>.*?</script>', '', html, flags=re.S)
    html = re.sub(r'<!--\[if lte IE.*?<!\[endif\]-->', '', html, flags=re.S)

    # ── 5. Ensure our custom CSS and JS are loaded ───────────────────────────
    css_path = '../' * depth + 'css/custom.css'
    js_path  = '../' * depth + 'js/main.js'

    if 'custom.css' not in html:
        html = html.replace('</head>', f'<link rel="stylesheet" href="{css_path}">\n</head>')
    if 'main.js' not in html:
        html = html.replace('</body>', f'<script src="{js_path}"></script>\n</body>')

    # ── 6. Fix EN language switcher - hide EN link (it's current page) ───────
    # Add w--current to EN link, hide CS link display handled via CSS
    html = re.sub(
        r'(<a [^>]*class="[^"]*nav-link[^"]*is-lang[^"]*"[^>]*>EN</a>)',
        lambda m: m.group(0).replace('class="', 'class="w--current '),
        html
    )

    return html

# ── Download and process all pages ──────────────────────────────────────────
ok = fail = 0
for url_path, save_rel, depth in PAGES:
    url  = BASE_URL + url_path
    dest = os.path.join(EN_DIR, save_rel)
    print(f"\nFetching {url_path} ...", flush=True)
    try:
        html = fetch_url(url)
        html = process_html(html, depth)
        with open(dest, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓  Saved → en/{save_rel}  ({len(html):,} bytes)")
        ok += 1
        time.sleep(0.5)
    except Exception as e:
        print(f"  ✗  FAILED: {e}")
        fail += 1

print(f"\n{'='*50}")
print(f"Done: {ok} pages saved, {fail} failed")
print("English site is at: en/index.html")

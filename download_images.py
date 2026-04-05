#!/usr/bin/env python3
"""
Run this script from Terminal to download all images locally:
  cd "$(dirname "$0")"
  python3 download_images.py

Images will be saved to ./images/ and ./fonts/
The script will also update HTML and CSS files to use local paths.
"""
import glob, re, os, urllib.request, urllib.parse, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, 'images')
FONT_DIR = os.path.join(SCRIPT_DIR, 'fonts')
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(FONT_DIR, exist_ok=True)

CDN_BASE = 'https://cdn.prod.website-files.com/67b351f4c755934221b66277/'
FONT_EXTS = {'.woff', '.woff2', '.ttf', '.otf'}

# Collect all CDN URLs from HTML + CSS
all_urls = set()
for fpath in glob.glob(os.path.join(SCRIPT_DIR, '**/*.html'), recursive=True):
    with open(fpath, encoding='utf-8') as f:
        all_urls.update(re.findall(r'https://cdn\.prod\.website-files\.com/[^\s"\'<>]+', f.read()))
css_path = os.path.join(SCRIPT_DIR, 'css/webflow.css')
with open(css_path) as f:
    all_urls.update(re.findall(r'https://cdn\.prod\.website-files\.com/[^\s"\'<>)]+', f.read()))

IMAGE_EXTS = {'.webp','.jpg','.jpeg','.png','.gif','.svg','.mp4','.webm','.avif','.woff','.woff2','.ttf','.otf'}
assets = [u for u in sorted(all_urls) if os.path.splitext(u.split('?')[0])[1].lower() in IMAGE_EXTS]
print(f'Found {len(assets)} assets to download...')

ok = fail = skip = 0
url_to_local = {}

for url in assets:
    path = url.split('?')[0]
    filename = urllib.parse.unquote(path.split('/')[-1])
    ext = os.path.splitext(filename)[1].lower()
    subfolder = 'fonts' if ext in FONT_EXTS else 'images'
    dest = os.path.join(SCRIPT_DIR, subfolder, filename)

    if ext in FONT_EXTS:
        url_to_local[url] = f'../fonts/{filename}'
    else:
        url_to_local[url] = f'images/{filename}'

    if os.path.exists(dest) and os.path.getsize(dest) > 100:
        skip += 1
        continue
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://www.skolaflow.cz/'
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f'  OK  {filename[:70]} ({len(data)//1024}KB)')
        ok += 1
        time.sleep(0.03)
    except Exception as e:
        print(f'  ERR {filename[:70]}: {e}')
        fail += 1

print(f'\nDownload done: OK={ok}, skipped={skip}, failed={fail}')

if ok > 0 or skip > 0:
    print('\nUpdating HTML and CSS to use local paths...')
    # Update HTML files
    for fpath in glob.glob(os.path.join(SCRIPT_DIR, '**/*.html'), recursive=True):
        with open(fpath, encoding='utf-8') as f:
            content = f.read()
        changed = False
        # Determine relative prefix (subdirs need ../)
        rel = fpath.replace(SCRIPT_DIR, '').lstrip('/')
        depth = len(rel.split('/')) - 1
        prefix = '../' * depth
        for url, local in url_to_local.items():
            if url in content:
                content = content.replace(url, prefix + local)
                changed = True
        if changed:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(content)
    # Update CSS
    with open(css_path, encoding='utf-8') as f:
        css = f.read()
    for url, local in url_to_local.items():
        if url in css:
            css = css.replace(url, '../' + local)
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css)
    print('HTML and CSS updated to use local paths.')

print('\nAll done!')

#!/usr/bin/env python3
"""
SkolaFlow Asset Downloader
Run this script to download all images/fonts/assets from Webflow CDN
so the website works completely offline/standalone.

Usage:
  python3 download_assets.py

It will scan all HTML files for CDN references and download them to images/
"""
import os, re, sys, time, urllib.request, urllib.error

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(OUTPUT_DIR, 'images')
CSS_DIR = os.path.join(OUTPUT_DIR, 'css')

CDN_BASE = 'https://cdn.prod.website-files.com/67b351f4c755934221b66277/'
CSS_URL = CDN_BASE + 'css/skola-flow-2-0.webflow.shared.5fd23d3c8.min.css'

os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(CSS_DIR, exist_ok=True)

def download(url, dest):
    if os.path.exists(dest):
        print(f'  [skip] {os.path.basename(dest)}')
        return True
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
        print(f'  [ok]   {os.path.basename(dest)} ({len(data)//1024}KB)')
        return True
    except Exception as e:
        print(f'  [err]  {os.path.basename(dest)}: {e}')
        return False

# 1. Download Webflow CSS
print('Downloading Webflow CSS...')
download(CSS_URL, os.path.join(CSS_DIR, 'webflow.css'))

# 2. Find all CDN image/asset URLs from HTML files
print('\nScanning HTML files for CDN assets...')
cdn_urls = set()

html_files = []
for root, dirs, files in os.walk(OUTPUT_DIR):
    for f in files:
        if f.endswith('.html'):
            html_files.append(os.path.join(root, f))

for fpath in html_files:
    with open(fpath, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    # Find all CDN URLs
    matches = re.findall(
        r'https://cdn\.prod\.website-files\.com/[a-f0-9]{24}/([^\s"\'<>]+)',
        content
    )
    for m in matches:
        if not m.startswith('css/') and not m.startswith('js/'):
            cdn_urls.add(m)

print(f'Found {len(cdn_urls)} unique assets')

# 3. Download each asset
print('\nDownloading assets...')
ok = 0
err = 0
for fname in sorted(cdn_urls):
    url = CDN_BASE + fname
    # Save to images/ with the full filename
    safe_name = fname.replace('/', '_')
    dest = os.path.join(IMAGES_DIR, safe_name)
    time.sleep(0.05)  # Be polite
    if download(url, dest):
        ok += 1
    else:
        err += 1

print(f'\nDone: {ok} downloaded, {err} errors')
print('\nNow update HTML files to use local image paths...')

# 4. Update HTML files to reference local images
print('Updating HTML files to use local paths...')
updated = 0
for fpath in html_files:
    with open(fpath, encoding='utf-8', errors='ignore') as f:
        content = f.read()

    original = content
    # Determine relative path prefix
    relpath = os.path.relpath(OUTPUT_DIR, os.path.dirname(fpath))
    if relpath == '.':
        prefix = ''
    else:
        prefix = relpath + '/'

    # Replace CDN URLs with local paths
    def replace_cdn(m):
        fname = m.group(1)
        if fname.startswith('css/'):
            return f'{prefix}css/' + fname[4:]
        safe_name = fname.replace('/', '_')
        return f'{prefix}images/' + safe_name

    content = re.sub(
        r'https://cdn\.prod\.website-files\.com/[a-f0-9]{24}/([^\s"\'<>]+)',
        replace_cdn,
        content
    )

    if content != original:
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        updated += 1
        print(f'  Updated: {os.path.basename(fpath)}')

print(f'\nUpdated {updated} HTML files to use local assets.')
print('\nYour website is now fully standalone!')

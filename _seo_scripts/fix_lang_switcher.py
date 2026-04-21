#!/usr/bin/env python3
"""
Fix language switcher hrefs.

On CZ pages, the `CS` link was hardcoded to kariera.html (leftover from a
Webflow template). It should point to the current page. Leaves the `EN` link
alone unless it's clearly wrong (points to /en/blog.html instead of the EN
version of the current blog-post detail).

On EN pages the links are already correct and we don't touch them.
"""

import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent


def fix_page(path: Path):
    rel = path.relative_to(SITE_ROOT)
    parts = rel.parts
    is_en = parts and parts[0] == "en"
    if is_en:
        # EN pages — skip, already correct
        return "SKIP (en) " + str(rel)

    content = path.read_text(encoding="utf-8")
    original = content

    # Self URL is simply the filename — the lang link points to the same
    # directory as the current page.
    self_href = parts[-1]

    # Fix CS link pointing to kariera
    # Patterns to look for:
    #   <a href="kariera.html" ... class="nav-link is-lang w--current">CS</a>
    #   <a href="../kariera.html" ... class="nav-link is-lang w--current">CS</a>
    patterns = [
        (r'(<a\s+href=")(?:\.\./)*kariera\.html("[^>]*class="nav-link is-lang[^"]*w--current[^"]*"[^>]*>CS</a>)', r'\1' + self_href + r'\2'),
    ]
    for pat, repl in patterns:
        content = re.sub(pat, repl, content)

    # Fix EN link on blog-post detail pages: currently `../en/blog.html` →
    # should point to `../en/blog-post/<slug>.html`
    if len(parts) >= 2 and parts[0] == "blog-post":
        slug = parts[1]
        wrong_en = r'(<a\s+href=")(?:\.\./)*en/blog\.html("[^>]*class="nav-link is-lang[^"]*"[^>]*>EN</a>)'
        correct = rf'\1../en/blog-post/{slug}\2'
        content = re.sub(wrong_en, correct, content)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return "FIXED " + str(rel)
    return "unchanged " + str(rel)


def main():
    for html in SITE_ROOT.rglob("*.html"):
        rel = html.relative_to(SITE_ROOT)
        if str(rel).startswith(("_backups/", "_seo_scripts/")):
            continue
        res = fix_page(html)
        if res.startswith(("FIXED", "SKIP")):
            print(res)


if __name__ == "__main__":
    main()

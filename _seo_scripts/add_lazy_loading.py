#!/usr/bin/env python3
"""
Add loading="lazy" to <img> tags that don't already have a loading attribute.

Skips images in the page header area (first .nav block) because those are
typically logos shown above the fold — native browsers already load them
immediately, but we set them explicitly to `eager` to be safe and avoid any
jank on slow connections.

Idempotent: skips imgs that already declare `loading=`.
"""

import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

# Filenames of images that should load eagerly (logos, hero images typically
# above the fold). Everything else gets lazy.
EAGER_FILENAMES = {
    "6803765eddf9ecceb76bb904_flow-logo.svg",
    "67c55ee11c9d998cbc1cec25_flow-white.svg",
}


def process(path: Path) -> str:
    rel = str(path.relative_to(SITE_ROOT))
    if rel.startswith(("_backups/", "_seo_scripts/")):
        return ""
    content = path.read_text(encoding="utf-8")
    changed = [0]

    def replace(match):
        tag = match.group(0)
        # Already has loading attribute → leave as is
        if re.search(r'\bloading\s*=', tag):
            return tag
        # Extract src filename
        src_m = re.search(r'src="([^"]+)"', tag)
        fname = src_m.group(1).split("/")[-1] if src_m else ""
        loading = "eager" if fname in EAGER_FILENAMES else "lazy"
        changed[0] += 1
        # Insert `loading="..."` before the closing `>` (handle self-closing `/>`)
        if tag.endswith("/>"):
            return tag[:-2].rstrip() + f' loading="{loading}"/>'
        return tag[:-1].rstrip() + f' loading="{loading}">'

    new_content = re.sub(r"<img\b[^>]*>", replace, content)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return f"{rel}: added loading= on {changed[0]} imgs"
    return ""


def main():
    for html in SITE_ROOT.rglob("*.html"):
        res = process(html)
        if res:
            print(res)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Add H1 tags to pages that are missing them.

Strategy:
  1. If the page has a hero `<h2 class="heading is-extra-large-title">`, promote
     the FIRST such occurrence to h1 (close tag follows). Webflow styles are
     keyed on the .heading class, not the tag name, so visual styling is preserved.
  2. For pages without a hero extra-large-title, insert a visually-hidden H1
     right after `<body ...>` open tag with the provided title text.
  3. Idempotent: if a page already has an <h1, skip it.
"""

import os
import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

# Pages missing H1, with the fallback H1 text if no hero-title exists.
PAGES = [
    # CZ
    ("nase-skola.html",                             "Naše škola"),
    ("vzdelavaci-program.html",                     "Vzdělávací program"),
    ("kontakt.html",                                "Kontakt"),
    ("faq.html",                                    "Často kladené otázky"),
    ("blog.html",                                   "Blog školy FLOW"),
    ("pro-zajemce/poplatky-2025-26.html",           "Poplatky pro školní rok 2025/26"),
    # CZ blog-post details
    ("blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame.html",
        "Jak stavíme pedagogický tým ve FLOW a koho to vlastně hledáme"),
    ("blog-post/marv-shamma-smysl-zivota-je-pomahat.html",
        "Marv Shamma: Smysl života je pomáhat"),
    ("blog-post/marv-shamma-tedx-prague-ed.html",
        "Marv Shamma – TEDx Prague ED"),
    ("blog-post/na-vlne-podnikani-s-marvem-shammou.html",
        "Na vlně podnikání s Marvem Shammou"),
    ("blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani.html",
        "Proč jsem založil školu FLOW a jak vnímám vzdělávání"),
    ("blog-post/proc-ve-flow-sazime-na-projektovou-vyuku.html",
        "Proč ve FLOW sázíme na projektovou výuku"),
    ("blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime.html",
        "S mindsetem minulosti děti na budoucnost nikdy nepřipravíme"),
    ("blog-post/talk-z-lomu-s-marvem-shammou.html",
        "Talk (z)lomu s Marvem Shammou"),
    # EN
    ("en/nase-skola.html",                          "Our School"),
    ("en/blog.html",                                "Flow School Blog"),
    ("en/pro-zajemce/poplatky-2025-26.html",        "Fees for the 2025/26 school year"),
    ("en/blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame.html",
        "How we build the Flow teaching team — and who we're looking for"),
    ("en/blog-post/marv-shamma-smysl-zivota-je-pomahat.html",
        "Marv Shamma: The meaning of life is to help"),
    ("en/blog-post/marv-shamma-tedx-prague-ed.html",
        "Marv Shamma – TEDx Prague ED"),
    ("en/blog-post/na-vlne-podnikani-s-marvem-shammou.html",
        "On the wave of entrepreneurship with Marv Shamma"),
    ("en/blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani.html",
        "Why I founded Flow School and how I see education"),
    ("en/blog-post/proc-ve-flow-sazime-na-projektovou-vyuku.html",
        "Why we bet on project-based learning at Flow"),
    ("en/blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime.html",
        "You can't prepare children for the future with a mindset from the past"),
    ("en/blog-post/talk-z-lomu-s-marvem-shammou.html",
        "A breaking-point talk with Marv Shamma"),
]

VISUALLY_HIDDEN_STYLE = (
    "position:absolute;width:1px;height:1px;padding:0;margin:-1px;"
    "overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0;"
)


def process_page(rel: str, fallback_title: str) -> str:
    path = SITE_ROOT / rel
    if not path.exists():
        return f"MISSING {rel}"
    content = path.read_text(encoding="utf-8")

    # Skip if already has an <h1 in body
    if re.search(r"<h1[\s>]", content):
        return f"SKIP (has h1) {rel}"

    # Try promoting the first extra-large-title H2 → H1
    pattern_open = re.compile(
        r'<h2(\s+class="[^"]*\bis-extra-large-title\b[^"]*")', re.IGNORECASE
    )
    m = pattern_open.search(content)
    if m:
        # Find matching </h2> for this opening tag.
        open_end = m.end()
        tag_start = m.start()
        close_match = re.search(r"</h2\s*>", content[open_end:], re.IGNORECASE)
        if close_match:
            close_abs = open_end + close_match.start()
            close_end = open_end + close_match.end()
            before = content[:tag_start]
            opening = content[tag_start:open_end].replace("<h2", "<h1", 1)
            inner = content[open_end:close_abs]
            after = content[close_end:]
            new_content = before + opening + ">" if not opening.endswith(">") else before + opening
            # Actually, the opening tag captured does not include the closing '>' of the tag.
            # Re-extract properly:
            full_open_match = re.match(r"<h2[^>]*>", content[tag_start:], re.IGNORECASE)
            if full_open_match:
                full_open_tag = full_open_match.group(0)
                new_open_tag = "<h1" + full_open_tag[3:]  # replace leading <h2 with <h1
                tag_close = tag_start + full_open_match.end()
                inner = content[tag_close:close_abs]
                new_content = (
                    content[:tag_start]
                    + new_open_tag
                    + inner
                    + "</h1>"
                    + content[close_end:]
                )
                path.write_text(new_content, encoding="utf-8")
                return f"PROMOTED h2→h1 {rel}"

    # Fallback: insert visually-hidden H1 right after <body ...>
    body_match = re.search(r"<body[^>]*>", content, re.IGNORECASE)
    if not body_match:
        return f"NO BODY {rel}"
    insert_at = body_match.end()
    hidden_h1 = (
        f'<h1 style="{VISUALLY_HIDDEN_STYLE}">{fallback_title}</h1>'
    )
    new_content = content[:insert_at] + hidden_h1 + content[insert_at:]
    path.write_text(new_content, encoding="utf-8")
    return f"HIDDEN h1 inserted {rel}"


def main():
    for rel, title in PAGES:
        print(process_page(rel, title))


if __name__ == "__main__":
    main()

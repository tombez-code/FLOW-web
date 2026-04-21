#!/usr/bin/env python3
"""
Add hreflang alternate tags to CZ/EN page pairs.

Strategy:
  - For each CZ file path P, look for corresponding en/P (EN) file.
  - If both exist and the page is the homepage, use "/" and "/en/" URLs.
  - Otherwise use the path without .html extension (matches how Webflow serves these).
  - Inject three <link rel="alternate"> tags before </head>.
  - Idempotent: skip files that already contain rel="alternate" hreflang.
"""

import os
import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.skolaflow.cz"

# CZ files that have an EN equivalent (same filename under en/)
PAGE_MAP = [
    # (cz_rel_path, cz_url_path, en_url_path)
    ("index.html", "/", "/en/"),
    ("nase-skola.html", "/nase-skola", "/en/nase-skola"),
    ("about-us.html", "/about-us", "/en/about-us"),
    ("vzdelavaci-program.html", "/vzdelavaci-program", "/en/vzdelavaci-program"),
    ("nas-model-vyuky-a-uceni.html", "/nas-model-vyuky-a-uceni", "/en/nas-model-vyuky-a-uceni"),
    ("kurikulum.html", "/kurikulum", "/en/kurikulum"),
    ("anglictina-ve-flow.html", "/anglictina-ve-flow", "/en/anglictina-ve-flow"),
    ("informatika-a-digitalni-gramotnost.html", "/informatika-a-digitalni-gramotnost", "/en/informatika-a-digitalni-gramotnost"),
    ("telesna-vychova.html", "/telesna-vychova", "/en/telesna-vychova"),
    ("wellbeing.html", "/wellbeing", "/en/wellbeing"),
    ("nas-tym.html", "/nas-tym", "/en/nas-tym"),
    ("novy-kampus.html", "/novy-kampus", "/en/novy-kampus"),
    ("kariera.html", "/kariera", "/en/kariera"),
    ("pro-rodice.html", "/pro-rodice", "/en/pro-rodice"),
    ("kontakt.html", "/kontakt", "/en/kontakt"),
    ("faq.html", "/faq", "/en/faq"),
    ("blog.html", "/blog", "/en/blog"),
    ("after-work-seminare-flow.html", "/after-work-seminare-flow", "/en/after-work-seminare-flow"),
    ("gdpr.html", "/gdpr", "/en/gdpr"),
    ("pro-zajemce.html", "/pro-zajemce", "/en/pro-zajemce"),
    ("pro-zajemce/navstivte-skolu-flow.html", "/pro-zajemce/navstivte-skolu-flow", "/en/pro-zajemce/navstivte-skolu-flow"),
    ("pro-zajemce/poplatky-2025-26.html", "/pro-zajemce/poplatky-2025-26", "/en/pro-zajemce/poplatky-2025-26"),
    ("pro-zajemce/prijimaci-rizeni.html", "/pro-zajemce/prijimaci-rizeni", "/en/pro-zajemce/prijimaci-rizeni"),
    ("pro-zajemce/prestupy.html", "/pro-zajemce/prestupy", "/en/pro-zajemce/prestupy"),
    # Blog posts
    ("blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame.html",
     "/blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame",
     "/en/blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame"),
    ("blog-post/marv-shamma-smysl-zivota-je-pomahat.html",
     "/blog-post/marv-shamma-smysl-zivota-je-pomahat",
     "/en/blog-post/marv-shamma-smysl-zivota-je-pomahat"),
    ("blog-post/marv-shamma-tedx-prague-ed.html",
     "/blog-post/marv-shamma-tedx-prague-ed",
     "/en/blog-post/marv-shamma-tedx-prague-ed"),
    ("blog-post/na-vlne-podnikani-s-marvem-shammou.html",
     "/blog-post/na-vlne-podnikani-s-marvem-shammou",
     "/en/blog-post/na-vlne-podnikani-s-marvem-shammou"),
    ("blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani.html",
     "/blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani",
     "/en/blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani"),
    ("blog-post/proc-ve-flow-sazime-na-projektovou-vyuku.html",
     "/blog-post/proc-ve-flow-sazime-na-projektovou-vyuku",
     "/en/blog-post/proc-ve-flow-sazime-na-projektovou-vyuku"),
    ("blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime.html",
     "/blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime",
     "/en/blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime"),
    ("blog-post/talk-z-lomu-s-marvem-shammou.html",
     "/blog-post/talk-z-lomu-s-marvem-shammou",
     "/en/blog-post/talk-z-lomu-s-marvem-shammou"),
]


def build_block(cz_url: str, en_url: str, canonical_url: str = None, is_en: bool = False) -> str:
    """Build the hreflang block (with leading newline)."""
    tags = [
        f'<link rel="alternate" hreflang="cs" href="{BASE}{cz_url}" />',
        f'<link rel="alternate" hreflang="en" href="{BASE}{en_url}" />',
        f'<link rel="alternate" hreflang="x-default" href="{BASE}/" />',
    ]
    if canonical_url:
        tags.insert(0, f'<link rel="canonical" href="{BASE}{canonical_url}" />')
    return "\n".join(tags)


def inject_head(path: Path, block: str) -> bool:
    """Inject block before </head>. Skip if hreflang already present."""
    if not path.exists():
        print(f"  skip (missing): {path.relative_to(SITE_ROOT)}")
        return False
    content = path.read_text(encoding="utf-8")
    if 'rel="alternate" hreflang=' in content or "rel='alternate' hreflang=" in content:
        print(f"  skip (already has hreflang): {path.relative_to(SITE_ROOT)}")
        return False
    # Insert right before </head>
    new, n = re.subn(
        r"</head>",
        block + "\n</head>",
        content,
        count=1,
        flags=re.IGNORECASE,
    )
    if n == 0:
        print(f"  WARN: no </head> found in {path.relative_to(SITE_ROOT)}")
        return False
    path.write_text(new, encoding="utf-8")
    return True


def process():
    total_cz = 0
    total_en = 0
    for cz_rel, cz_url, en_url in PAGE_MAP:
        cz_path = SITE_ROOT / cz_rel
        en_path = SITE_ROOT / "en" / cz_rel

        # CZ: canonical to CZ URL
        cz_block = build_block(cz_url, en_url, canonical_url=cz_url)
        if inject_head(cz_path, cz_block):
            total_cz += 1

        # EN: canonical to EN URL
        en_block = build_block(cz_url, en_url, canonical_url=en_url, is_en=True)
        if inject_head(en_path, en_block):
            total_en += 1

    print(f"\nDone. CZ modified: {total_cz}, EN modified: {total_en}")


if __name__ == "__main__":
    process()

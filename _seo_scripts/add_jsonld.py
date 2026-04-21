#!/usr/bin/env python3
"""
Inject JSON-LD structured data into the right pages.

Adds:
  - Organization + EducationalOrganization on every CZ/EN page (base schema block)
  - FAQPage on /faq (with the current FAQ questions)
  - Article schema on every blog-post/* detail page
"""

import json
import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.skolaflow.cz"

ORG_BASE_CZ = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": ["Organization", "EducationalOrganization"],
            "@id": f"{BASE}/#organization",
            "name": "Základní škola FLOW",
            "alternateName": "Flow Elementary School",
            "url": f"{BASE}/",
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE}/images/favicon.png"
            },
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Jankovcova 53",
                "addressLocality": "Praha 7",
                "postalCode": "170 00",
                "addressCountry": "CZ"
            },
            "sameAs": [
                "https://www.linkedin.com/company/skolaflow/",
                "https://www.instagram.com/skolaflowcz",
                "https://www.facebook.com/skolaflowcz"
            ]
        }
    ]
}

ORG_BASE_EN = {
    "@context": "https://schema.org",
    "@graph": [
        {
            "@type": ["Organization", "EducationalOrganization"],
            "@id": f"{BASE}/#organization",
            "name": "Flow Elementary School",
            "alternateName": "Základní škola FLOW",
            "url": f"{BASE}/en/",
            "logo": {
                "@type": "ImageObject",
                "url": f"{BASE}/images/favicon.png"
            },
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Jankovcova 53",
                "addressLocality": "Prague 7",
                "postalCode": "170 00",
                "addressCountry": "CZ"
            },
            "sameAs": [
                "https://www.linkedin.com/company/skolaflow/",
                "https://www.instagram.com/skolaflowcz",
                "https://www.facebook.com/skolaflowcz"
            ]
        }
    ]
}


def wrap_jsonld(data: dict) -> str:
    return (
        '<script type="application/ld+json">'
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + "</script>"
    )


def inject_before_head_close(path: Path, block: str, marker: str) -> str:
    """Inject block before </head>. marker is a unique substring to check
    idempotency (if marker already in content, skip)."""
    if not path.exists():
        return f"MISSING {path.relative_to(SITE_ROOT)}"
    content = path.read_text(encoding="utf-8")
    if marker in content:
        return f"SKIP (already has {marker[:30]}) {path.relative_to(SITE_ROOT)}"
    new, n = re.subn(r"</head>", block + "\n</head>", content, count=1, flags=re.IGNORECASE)
    if n == 0:
        return f"NO </head> in {path.relative_to(SITE_ROOT)}"
    path.write_text(new, encoding="utf-8")
    return f"OK {path.relative_to(SITE_ROOT)}"


# --- Organization schema on all pages ---
CZ_FILES = [
    "index.html", "nase-skola.html", "vzdelavaci-program.html",
    "nas-model-vyuky-a-uceni.html", "kurikulum.html", "anglictina-ve-flow.html",
    "informatika-a-digitalni-gramotnost.html", "telesna-vychova.html", "wellbeing.html",
    "nas-tym.html", "novy-kampus.html", "kariera.html", "pro-rodice.html",
    "kontakt.html", "faq.html", "blog.html", "after-work-seminare-flow.html",
    "gdpr.html", "pro-zajemce.html",
    "pro-zajemce/navstivte-skolu-flow.html", "pro-zajemce/poplatky-2025-26.html",
    "pro-zajemce/prijimaci-rizeni.html", "pro-zajemce/prijimaci-rizeni-do-1-rocniku-2026-27.html",
    "pro-zajemce/prestupy.html",
    "about-us.html",
]
CZ_BLOG_POSTS = [
    "blog-post/jak-stavime-pedagogicky-tym-ve-flow-a-koho-to-vlastne-hledame.html",
    "blog-post/marv-shamma-smysl-zivota-je-pomahat.html",
    "blog-post/marv-shamma-tedx-prague-ed.html",
    "blog-post/na-vlne-podnikani-s-marvem-shammou.html",
    "blog-post/proc-jsem-zalozil-skolu-flow-a-jak-vnimam-vzdelavani.html",
    "blog-post/proc-ve-flow-sazime-na-projektovou-vyuku.html",
    "blog-post/s-mindsetem-minulosti-deti-na-budoucnost-nikdy-nepripravime.html",
    "blog-post/talk-z-lomu-s-marvem-shammou.html",
]


def en_of(rel: str) -> str:
    return "en/" + rel


# --- FAQ data ---
def extract_faq_items(content: str, max_items: int = 30) -> list:
    """Attempt to extract FAQ Q/A pairs from HTML.
    Looks for `.accordion-question` and `.accordion-text` (or similar) blocks."""
    # Flow's faq uses `<div class="accordion-heading-text">...</div>` for question
    # and `<div class="accordion-paragraph">...</div>` for answer (common Webflow pattern).
    q_pattern = re.compile(
        r'<div class="accordion-heading-text"[^>]*>(.*?)</div>',
        re.IGNORECASE | re.DOTALL,
    )
    a_pattern = re.compile(
        r'<div class="accordion-paragraph[^"]*"[^>]*>(.*?)</div>',
        re.IGNORECASE | re.DOTALL,
    )
    questions = [re.sub(r"<[^>]+>", "", m).strip() for m in q_pattern.findall(content)]
    answers = [re.sub(r"<[^>]+>", "", m).strip() for m in a_pattern.findall(content)]
    items = []
    for i, q in enumerate(questions[:max_items]):
        a = answers[i] if i < len(answers) else ""
        if q and a:
            items.append({"q": q, "a": a})
    return items


def faqpage_schema(items: list) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": it["q"],
                "acceptedAnswer": {"@type": "Answer", "text": it["a"]},
            }
            for it in items
        ],
    }


# --- Article schema ---
def article_schema(url: str, title: str, lang: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "headline": title,
        "inLanguage": lang,
        "publisher": {"@id": f"{BASE}/#organization"},
        "author": {
            "@type": "Organization",
            "name": "Flow Elementary School" if lang == "en" else "Základní škola FLOW"
        },
        "image": f"{BASE}/images/67f6bd29bd8f96e006163b1f_flow-cover.webp",
    }


def run():
    org_cz_block = wrap_jsonld(ORG_BASE_CZ)
    org_en_block = wrap_jsonld(ORG_BASE_EN)
    org_marker = '"@id":"' + BASE + '/#organization"'

    # Organization on CZ pages
    for rel in CZ_FILES + CZ_BLOG_POSTS:
        print(inject_before_head_close(SITE_ROOT / rel, org_cz_block, org_marker))
    # Organization on EN pages
    for rel in CZ_FILES + CZ_BLOG_POSTS:
        en_path = SITE_ROOT / en_of(rel)
        if en_path.exists():
            print(inject_before_head_close(en_path, org_en_block, org_marker))

    # FAQ schema on CZ faq + EN faq
    faq_cz = SITE_ROOT / "faq.html"
    faq_en = SITE_ROOT / "en/faq.html"

    for path in [faq_cz, faq_en]:
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        items = extract_faq_items(content)
        print(f"  {path.relative_to(SITE_ROOT)} — extracted {len(items)} FAQ items")
        if items:
            block = wrap_jsonld(faqpage_schema(items))
            marker = '"@type":"FAQPage"'
            print(inject_before_head_close(path, block, marker))

    # Article schema on blog-post detail pages
    for rel in CZ_BLOG_POSTS:
        for lang_rel, lang in [(rel, "cs"), (en_of(rel), "en")]:
            path = SITE_ROOT / lang_rel
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            title_match = re.search(r"<title>([^<]+)</title>", content)
            title = title_match.group(1) if title_match else rel
            slug = rel.replace("blog-post/", "").replace(".html", "")
            url = f"{BASE}/blog-post/{slug}" if lang == "cs" else f"{BASE}/en/blog-post/{slug}"
            block = wrap_jsonld(article_schema(url, title, lang))
            marker = f'"@id":"{url}"'
            print(inject_before_head_close(path, block, marker))


if __name__ == "__main__":
    run()

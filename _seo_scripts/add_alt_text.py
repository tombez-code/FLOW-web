#!/usr/bin/env python3
"""
Populate alt attributes on /novy-kampus (CZ + EN).

Strategy: map each unique image `src` filename to a descriptive alt text
(Czech for CZ page, English for EN page). Replace empty `alt=""` with the
mapped string. Idempotent: skips non-empty alt attributes.
"""

import re
from pathlib import Path

SITE_ROOT = Path(__file__).resolve().parent.parent

# fname → (cs_alt, en_alt)
ALT_MAP = {
    # Content photos / renderings of the new campus
    "Novy kampus.jpeg": (
        "Vizualizace nového kampusu FLOW na pražské Jankovcově ulici",
        "Rendering of the new Flow Elementary School campus on Jankovcova Street, Prague 7",
    ),
    "69bc127ed739bdf38334cd9e_0.6.png": (
        "Vizualizace nového kampusu FLOW – venkovní zahrada a hřiště",
        "Rendering of the new Flow campus – outdoor garden and playground",
    ),
    "69bc101576bfccee451887f8_0.2.jpeg": (
        "Vizualizace nového kampusu FLOW – pohled na budovu z ulice",
        "Rendering of the new Flow campus – street view of the building",
    ),
    "69bc1012f0db9c78be6b7e54_0.3.jpeg": (
        "Vizualizace nového kampusu FLOW – vnitřní prostory učebny",
        "Rendering of the new Flow campus – interior classroom space",
    ),
    "69bc1012037b3de47a62565d_0.4.jpeg": (
        "Vizualizace nového kampusu FLOW – společenský prostor a jídelna",
        "Rendering of the new Flow campus – common space and dining area",
    ),
    "69bc101284854bda3bfcf9dc_1.1.jpg": (
        "Vizualizace nového kampusu FLOW – vstupní hala a recepce",
        "Rendering of the new Flow campus – entrance hall and reception",
    ),
    "69bc101244890a80617a72d9_0.5.jpeg": (
        "Vizualizace nového kampusu FLOW – knihovna a klidová zóna",
        "Rendering of the new Flow campus – library and quiet zone",
    ),
    "69bc1221f261ad2074da9873_3.png": (
        "Půdorys nového kampusu FLOW",
        "Floor plan of the new Flow campus",
    ),

    # Logos
    "6803765eddf9ecceb76bb904_flow-logo.svg": (
        "Logo Základní školy FLOW",
        "Flow Elementary School logo",
    ),
    "67c55ee11c9d998cbc1cec25_flow-white.svg": (
        "Logo Základní školy FLOW",
        "Flow Elementary School logo",
    ),
    "67b351f4c755934221b6669f_facebook-logo-white.svg": (
        "Facebook",
        "Facebook",
    ),
    "67b351f4c755934221b666a1_linkedin-logo-white.svg": (
        "LinkedIn",
        "LinkedIn",
    ),
    "67b351f4c755934221b666a4_instagram-logo-white.svg": (
        "Instagram",
        "Instagram",
    ),
    "680935e767127338a262bfd9_EU_2BM_D9_86MT_20_D8_8CB.svg": (
        "Logo – spolufinancováno Evropskou unií a MŠMT",
        "Co-funded by the European Union and the Czech Ministry of Education logo",
    ),
    "68093a79aace0042c9a41742_CC_partner_kulaty_20copy.svg": (
        "Logo – partner Creative Commons",
        "Creative Commons partner logo",
    ),

    # Decorative / UI icons (short functional description)
    "67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24_20_1_.svg": (
        "Rozbalit",
        "Expand",
    ),
    "67b351f4c755934221b66584_add-fill0-wght600-grad0-opsz24.svg": (
        "Rozbalit",
        "Expand",
    ),
    "67b351f4c755934221b66646_65df7897ecfb010bff6e38ab-event-fill0-wght600-grad0-opsz24.svg": (
        "Termín",
        "Event date",
    ),
    "67b351f4c755934221b66627_arrow-forward-fill0-wght400-grad0-opsz24-purple.svg": (
        "Šipka vpřed",
        "Forward arrow",
    ),
    "67b351f4c755934221b66626_arrow-forward-fill0-wght400-grad0-opsz24-white.svg": (
        "Šipka vpřed",
        "Forward arrow",
    ),
    "67b351f4c755934221b665b4_close-fill0-wght600-grad0-opsz24.svg": (
        "Zavřít menu",
        "Close menu",
    ),
    "67b351f4c755934221b66523_mesh-gradient-1.webp": (
        "",  # pure decorative background — empty alt is correct WCAG
        "",
    ),
    "67b351f4c755934221b66583_design-element-11.svg": (
        "",  # decorative design element
        "",
    ),
}


def process(rel: str, lang_idx: int) -> None:
    path = SITE_ROOT / rel
    if not path.exists():
        print(f"MISSING {rel}")
        return
    content = path.read_text(encoding="utf-8")

    # Find every <img ...> tag with src and (possibly empty) alt
    img_re = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
    changed = 0
    def replace(match):
        nonlocal changed
        tag = match.group(0)
        src_m = re.search(r'src="([^"]+)"', tag)
        if not src_m:
            return tag
        src = src_m.group(1).split("/")[-1]
        if src not in ALT_MAP:
            return tag  # unknown — leave as-is
        desired = ALT_MAP[src][lang_idx]
        # Replace existing alt= with desired, or append if missing
        if re.search(r'\balt\s*=\s*"[^"]*"', tag):
            # Only replace if current alt is empty
            def alt_sub(m):
                current = m.group(0)
                cur_val = re.search(r'alt\s*=\s*"([^"]*)"', current).group(1)
                if cur_val.strip() == "":
                    changed_flag[0] = True
                    return f'alt="{desired}"'
                return current
            changed_flag = [False]
            new_tag = re.sub(r'alt\s*=\s*"[^"]*"', alt_sub, tag)
            if changed_flag[0]:
                changed += 1
            return new_tag
        else:
            # no alt attribute at all — insert before closing bracket
            changed += 1
            return tag[:-1] + f' alt="{desired}"' + tag[-1]

    new_content = img_re.sub(replace, content)
    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
    print(f"{rel}: updated {changed} alt attributes")


if __name__ == "__main__":
    process("novy-kampus.html", 0)  # Czech
    process("en/novy-kampus.html", 1)  # English

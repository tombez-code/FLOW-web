# SEO / Mobile — TODO (server-config & follow-ups)

Vytvořeno: 2026-04-21. Dokumentuje položky, které **nelze opravit ve static HTML**
(server-side config) + nalezené drobné chyby obsahu / nápady na další iteraci.

---

## 1. Server-side — musí hostitel

### 1.1 404 stránka se statusem 404
Stránka `/404.html` existuje (CZ) a `/en/404.html` existuje (EN), ale aby
prohlížeč/Google dostal skutečný HTTP 404, musí to nakonfigurovat hosting:

- **Netlify** (`netlify.toml` nebo `_redirects`):
  ```
  /*  /404.html  404
  ```
- **Apache** (`.htaccess`):
  ```
  ErrorDocument 404 /404.html
  ```
- **Nginx**:
  ```
  error_page 404 /404.html;
  ```
- **Cloudflare Pages** (`_routes.json` / `_worker.js`): default fallback na
  `/404.html` je built-in, stačí soubor nahrát do rootu.

Ověřit: `curl -I https://www.skolaflow.cz/neexistujici-url` → musí vrátit
`HTTP/1.1 404` a ne `200`.

### 1.2 Redirecty (301) pro staré URL
Aktuálně se několik EN slugů přesměrovává na homepage (ztráta SEO signálu).
Správně:

| Stará URL | Nová URL | Status |
|---|---|---|
| `/en/admissions` | `/en/pro-zajemce.html` | 301 |
| `/en/contact` | `/en/kontakt.html` | 301 |
| `/en/our-team` | `/en/nas-tym.html` | 301 |
| `/en/for-parents` | `/en/pro-zajemce.html` | 301 |
| `/en/careers` | `/en/kariera.html` | 301 |
| `/en/fees-2025-26` | `/en/pro-zajemce/poplatky-2025-26.html` | 301 |
| `/en/new-campus` | `/en/novy-kampus.html` | 301 |
| `/en` (bez slashe) | `/en/index.html` | 301 |
| `/preview-booking` | `/` | 301 (nebo `noindex`) |
| `/nas-model-vyuky-a-uceni-old` | `/vzdelavaci-program.html` | 301 |
| `/skolaflow_homepage` | `/` | 301 |

Příklad `_redirects` (Netlify):
```
/en/admissions       /en/pro-zajemce.html            301
/en/contact          /en/kontakt.html                301
/en/our-team         /en/nas-tym.html                301
/en/for-parents      /en/pro-zajemce.html            301
/en/careers          /en/kariera.html                301
/en/fees-2025-26     /en/pro-zajemce/poplatky-2025-26.html  301
/en/new-campus       /en/novy-kampus.html            301
/preview-booking     /                               301
/nas-model-vyuky-a-uceni-old  /vzdelavaci-program.html  301
/skolaflow_homepage  /                               301
```

### 1.3 HTTPS & www canonical
Ujistit se, že `http://` → `https://` a `skolaflow.cz` → `www.skolaflow.cz`
(nebo naopak, dle preference) jsou 301 redirecty. Sitemap, canonical tagy
i JSON-LD URL jsou všechny nastavené na `https://www.skolaflow.cz/`.

### 1.4 Cache-Control pro statická aktiva
```
Cache-Control: public, max-age=31536000, immutable   # pro /images, /css, /js
Cache-Control: public, max-age=600                    # pro HTML
```

### 1.5 Compression
Zapnout gzip / brotli na `text/html`, `text/css`, `application/javascript`,
`image/svg+xml`.

---

## 2. Git branch situace
- Při pokusu o `git init` v tomto pracovním adresáři macOS ACL (`Operation
  not permitted`) zablokoval zápis do `.git/`. Branche jsem proto nemohl
  vytvořit — **úpravy jsou zapsané přímo do souborů** a originály jsou
  v `_backups/pre-seo-fixes/` (snapshot před změnami).
- Až budeš commit dělat lokálně (mimo sandbox), navrhuji:
  - branch `seo-fixes-2026-04-21`
  - dva commity (SEO vs. mobile), viz **Commit split** dole

---

## 3. Known content issues (k dořešení ručně)

### 3.1 `blog-post/marv-shamma-smysl-zivota-je-pomahat.html`
Hlavní heading + úvodní odstavec jsou **v angličtině**, přestože `<html lang="cs">`
a stránka je CZ varianta. Pravděpodobně se po exportu z Webflow zapomnělo
přeložit obsah. H1 se promotnul správně, ale text vyžaduje překladatelský zásah.

### 3.2 EN stránky se slugy v češtině
`/en/nase-skola`, `/en/kontakt`, `/en/nas-tym`, `/en/pro-zajemce` a další EN
stránky mají **české slugy v URL**. Pro EN SEO je to slabší signál — ideální
by bylo `/en/our-school`, `/en/contact`, `/en/our-team`. Vyžaduje ale:
- přejmenování souborů
- update všech interních linků (cca 70 HTML souborů)
- 301 redirecty ze starých slugů
- update sitemap.xml, hreflang tagů, canonical

Doporučuji v samostatné iteraci — je to větší refactor.

### 3.3 Sitemap
`sitemap.xml` aktuálně neuvádí odkazy na přesměrovávané EN slugy
(`/en/admissions` apod.). Pokud se v bodě **1.2** nastaví 301 redirecty
na existující EN stránky, ty cílové stránky v sitemap jsou (`/en/pro-zajemce.html`
atd.) — takže je to v pořádku.

### 3.4 Alt texty mimo `/novy-kampus`
Alt texty jsem v této iteraci dodělával primárně pro `/novy-kampus` (CZ + EN),
což bylo dle auditu prioritní. Ostatní stránky by chtěly projít podobně —
zejména `/nas-tym` (portréty bez popisu jmen) a blog-post thumbnails.

---

## 4. Mobile — co nebylo nasazeno (větší refactor)

Provedl jsem **low-risk mobile quick wins** (viewport audit, injekce lang
switcher do burger menu, min-height 44px pro tap-targets, max-width:100%
na img v `<main>`, lazy-loading na `<img>` bez `loading=`).

Zbývá a doporučujeme v samostatné iteraci:

- **Nav dropdown na mobilu** — `.nav-dropdown-link` panely jsou na mobilu
  zatím skryté přes CSS; měly by se buď složit do burger menu jako
  seznam podstránek, nebo fungovat jako "tap → rozbalit sekci".
- **Hero nadpisy** — `is-extra-large-title` je na mobilu pořád dost velká
  (~48-56px), chtělo by to clampnout (`clamp(2rem, 8vw, 3.5rem)`).
- **Touch-target audit** — CSS quick-fix pokrývá `.menu-main-links a`,
  ale drobná ikonová tlačítka (close, burger) jsou už správně 44×44;
  ideálně ručně obejít všechna `.w-nav` CTA.
- **Responsive images** — `srcset` je nastavený pouze na CMS obrázky z
  Webflow exportu; vlastní asset fotky (logos, ikony) by mohly dostat
  `srcset` pro 1x/2x/3x displaye.
- **Font loading** — `@font-face` nemá `font-display: swap` → FOIT na
  pomalém spojení. Chce se přidat do webflow.css nebo použít Google
  Fonts s `display=swap`.

---

## 5. Commit split (doporučení)

Až se budou změny commitovat, navrhuji dva commity:

### Commit 1 — SEO must-fix
```
seo: sitemap, 404, hreflang, H1, EN meta, JSON-LD, alt, lang-switcher

- Add sitemap.xml + robots.txt with real CZ/EN URLs and hreflang alternates
- Add 404.html (CZ) and en/404.html with Flow branding (server 404-status
  wiring deferred to TODO.md §1.1)
- Add canonical + hreflang (cs/en/x-default) to every CZ/EN page pair
  via _seo_scripts/add_hreflang.py
- Promote or inject missing H1 on nase-skola, vzdelavaci-program, kontakt,
  faq, blog, pro-zajemce/poplatky-2025-26 and all blog-post detail pages
  via _seo_scripts/add_h1.py
- Fix en/index.html title / description / og:title / twitter:title (were
  in Czech); fix "personalrůst" → "personal growth" on en/about-us.html
- Inject Organization + EducationalOrganization JSON-LD into every page;
  FAQPage schema on faq.html + en/faq.html (17 Q/As); Article schema on
  all blog-post detail pages
- Populate alt attributes on novy-kampus.html (104 imgs) and
  en/novy-kampus.html (55 imgs) from ALT_MAP in add_alt_text.py
- Fix broken CS language-switcher link that pointed to kariera.html on
  most pages (_seo_scripts/fix_lang_switcher.py + outputs/fix_cs_link_all.py)
```

### Commit 2 — Mobile quick wins
```
mobile: viewport, burger lang switcher, tap targets, lazy images

- Confirm viewport meta tag on all 70 HTML pages (no change needed)
- Add initMobileLangSwitcher() to js/main.js — clones .nav-link.is-lang
  (CS/EN) into .menu-main-links on page load, fixes missing language
  switcher in burger menu on mobile
- css/custom.css: .menu-lang-links styling; @media (max-width: 991px)
  block for 44px min-height tap targets and max-width:100% on content
  images
- Add loading="lazy" to 150+ <img> tags across the site that lacked a
  loading attribute; logo SVGs tagged loading="eager" explicitly
  (_seo_scripts/add_lazy_loading.py)
```

---

## 6. Helper scripts (reference)

Vše ve `_seo_scripts/` — idempotentní, dají se pouštět opakovaně:

- `add_hreflang.py` — canonical + hreflang tagy
- `add_h1.py` — doplňuje / promotuje H1
- `add_jsonld.py` — Organization / FAQPage / Article schema
- `add_alt_text.py` — alt texty z ALT_MAP
- `fix_lang_switcher.py` — oprava CS/EN lang linků
- `add_lazy_loading.py` — doplňuje `loading="lazy"` / `"eager"`

Vzájemně na sobě nezávisí, ale v pořádku dobré spouštět v pořadí:
hreflang → h1 → jsonld → alt → lang-switcher → lazy-loading.

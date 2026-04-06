#!/usr/bin/env python3
"""
Creates English versions of all Czech HTML pages for the Flow School website.
Translates Czech text to English and adjusts paths for the en/ subdirectory structure.
"""

import os
import re
from pathlib import Path

# Configuration
SOURCE_DIR = '/sessions/loving-clever-fermi/mnt/Flow website'
TARGET_DIR = os.path.join(SOURCE_DIR, 'en')

# Ensure en/ and en/pro-zajemce/ directories exist
os.makedirs(TARGET_DIR, exist_ok=True)
os.makedirs(os.path.join(TARGET_DIR, 'pro-zajemce'), exist_ok=True)

# Page metadata: (czech_source, english_target, depth_from_en)
PAGES = [
    ('index.html',          'en/index.html',          1),
    ('about-us.html',       'en/about-us.html',       1),
    ('nase-skola.html',     'en/nase-skola.html',     1),
    ('vzdelavaci-program.html', 'en/vzdelavaci-program.html', 1),
    ('pro-rodice.html',     'en/pro-rodice.html',     1),
    ('faq.html',            'en/faq.html',            1),
    ('nas-tym.html',        'en/nas-tym.html',        1),
    ('nas-model-vyuky-a-uceni.html', 'en/nas-model-vyuky-a-uceni.html', 1),
    ('kariera.html',        'en/kariera.html',        1),
    ('after-work-seminare-flow.html', 'en/after-work-seminare-flow.html', 1),
    ('novy-kampus.html',    'en/novy-kampus.html',    1),
    ('pro-zajemce.html',    'en/pro-zajemce.html',    1),
    ('blog.html',           'en/blog.html',           1),
    ('kontakt.html',        'en/kontakt.html',        1),
    ('gdpr.html',           'en/gdpr.html',           1),
    ('pro-zajemce/prijimaci-rizeni-do-1-rocniku-2026-27.html', 'en/pro-zajemce/prijimaci-rizeni-do-1-rocniku-2026-27.html', 2),
    ('pro-zajemce/prestupy.html', 'en/pro-zajemce/prestupy.html', 2),
    ('pro-zajemce/navstivte-skolu-flow.html', 'en/pro-zajemce/navstivte-skolu-flow.html', 2),
    ('pro-zajemce/poplatky-2025-26.html', 'en/pro-zajemce/poplatky-2025-26.html', 2),
]

# Page title translations
PAGE_TITLES = {
    'index.html': 'Flow Elementary School',
    'about-us.html': 'A Day at Flow | Flow School',
    'nase-skola.html': 'Our School | Flow School',
    'vzdelavaci-program.html': 'Educational Programme | Flow School',
    'pro-rodice.html': 'For Parents | Flow School',
    'faq.html': 'FAQ | Flow School',
    'nas-tym.html': 'Meet Our Team | Flow School',
    'nas-model-vyuky-a-uceni.html': 'Our Teaching & Learning Model | Flow School',
    'kariera.html': 'Career | Flow School',
    'after-work-seminare-flow.html': 'After-work Seminars | Flow School',
    'novy-kampus.html': 'New Campus | Flow School',
    'pro-zajemce.html': 'For Applicants | Flow School',
    'blog.html': 'Blog | Flow School',
    'kontakt.html': 'Contact Us | Flow School',
    'gdpr.html': 'GDPR | Flow School',
    'prijimaci-rizeni-do-1-rocniku-2026-27.html': 'Grade 1 Admissions | Flow School',
    'prestupy.html': 'School Transfers | Flow School',
    'navstivte-skolu-flow.html': 'Visit Flow School | Flow School',
    'poplatky-2025-26.html': 'Fees 2025/26 | Flow School',
}

# Comprehensive translation dictionary
TRANSLATIONS = {
    # Navigation
    'O škole Flow': 'About Flow School',
    'Den ve Flow': 'A Day at Flow',
    'Prostředí a koncepce': 'Environment & Concept',
    'Vzdělávací program': 'Educational Programme',
    'Sekce pro rodiče': 'For Parents',
    'Tým Flow': 'Flow Team',
    'Pro zájemce': 'For Applicants',
    'Příjimací řízení do 1. třídy': 'Grade 1 Admissions',
    'Přestupy': 'School Transfers',
    'Navštivte školu Flow': 'Visit Flow School',
    'Poplatky 2025/26': 'Fees 2025/26',
    'Studium ve FLOW': 'Learning at FLOW',
    'Náš model výuky a učení': 'Our Teaching & Learning Model',
    'Kariéra': 'Career',
    'After-work semináře': 'After-work Seminars',
    'Kontakt': 'Contact',
    'Nový kampus': 'New Campus',

    # Footer & Contact
    'Menu': 'Menu',
    'Škola Flow': 'Flow School',
    'GDPR': 'GDPR',
    'Blog': 'Blog',
    'Kontaktní informace': 'Contact Information',
    'Roh Přívozní 1064/2a a Jankovcovy 53': 'Corner of Přívozní 1064/2a and Jankovcovy 53',
    'Praha 7 - Holešovice': 'Prague 7 - Holešovice',
    'Datová schránka:': 'Data box:',
    'Dejte nám vědět': 'Get in Touch',
    'Pro obecné informace': 'General enquiries',
    'Kontakt na pověřence GDPR:': 'GDPR Officer contact:',
    'Infolinka': 'Info line',
    'Po-St, Pá: 9–12': 'Mon–Wed, Fri: 9am–12pm',
    'Ke stažení': 'Downloads',
    'Ke satežení': 'Downloads',
    'Školní vzdělávací program': 'School Educational Programme',
    'Školní řád': 'School Rules',
    'Výroční zpráva': 'Annual Report',
    'Kontaktujte nás': 'Contact Us',
    'Rádi vás uslyšíme': 'We\'d love to hear from you',

    # Blue announcement box (homepage)
    'Pro školní rok 2026/27 nabízíme volná místa na prvním a druhém stupni, dále na nově vzniklé MŠ LittleFLOW': 'For the 2026/27 school year, we have open spots in grades 1–6 as well as our new kindergarten, LittleFLOW',
    'Domluvte si osobní schůzku': 'Book a personal meeting',
    'Osobní setkání': 'Personal meeting',

    # Homepage content
    'Vracíme dětem radost do školních lavic': 'We bring joy back to the classroom',
    'Vracíme dětem radost': 'We bring joy back',
    'Jsme akreditovaná základní škola a naší misí je pomoct dětem rozvíjet myšlení budoucích inovátorů.': 'We are an accredited primary school and our mission is to help children develop the mindset of future innovators.',
    'Chci vědět víc': 'Tell me more',
    'projektů ročně': 'projects per year',
    'žáků ve třídě': 'students per class',
    'učitelé pro třídu': 'teachers per class',
    'třída ZŠ': 'primary school grade',
    'Naše základní pilíře': 'Our Core Pillars',
    'pilíře': 'pillars',
    'Vstoupit do světa FLOW je začátkem jedinečné vzdělávací cesty. Naše přijímací řízení je navrženo tak': 'Entering the world of FLOW is the beginning of a unique educational journey.',
    'Projektová výuka': 'Project-Based Learning',
    'Naše výuka se opírá o projektové učení, kde žáci řeší reálné problémy a výzvy. Tím rozvíjejí schopno': 'Our teaching is rooted in project-based learning, where students tackle real-world problems and challenges, developing critical thinking and collaboration skills.',
    'Vzdělávací program FLOW': 'FLOW Educational Programme',
    'Rozšířená výuka AJ': 'Extended English Teaching',
    'Programování a digitální gramotnost': 'Programming & Digital Literacy',
    'Psychologické bezpečí': 'Psychological Safety',
    'Vstoupit do světa FLOW je začátkem jedinečné vzdělávací cesty.': 'Entering the world of FLOW is the beginning of a unique educational journey.',
    'Naše kurikulum je navrženo tak, aby reflektovalo požadavky současného, neustále se měnícího světa.': 'Our curriculum is designed to reflect the demands of today\'s ever-changing world.',
    'kurikulum': 'curriculum',
    'reflektovalo požadavky současného': 'designed for the demands',
    'světa': 'of today\'s world',
    'Rodiče mluví za nás': 'Parents speak for us',
    'Rodiče': 'Parents',
    'Jste připraveni začít svou cestu s námi?': 'Ready to start your journey with us?',
    'Jste připraveni začít': 'Ready to start',
    'Důležité informace pro zájemce': 'Important information for applicants',

    # Team page
    'Poznejte náš tým': 'Meet Our Team',
    'Školu FLOW vede tým odborníků a v každé třídě vždy potkáte hlavního pedagoga, asistenta a rodilého mluvčího angličtiny, doplněné o psychologa a logopeda': 'FLOW School is led by a team of experts. In every classroom you will find a lead teacher, a teaching assistant, and a native English speaker, supported by a psychologist and speech therapist',
    'Volné pozice': 'Open Positions',
    'Náš tým': 'Our Team',
    'Odpolední programy a družinu řídí vychovatelský tým': 'After-school programmes and care are run by our education team',
    'Ředitel školy': 'School Principal',
    'Zakladatel školy': 'School Founder',
    'Spoluzakladatelka, metodik & tvůrce obsahu': 'Co-founder, Curriculum Lead & Content Creator',
    'učitel ICT': 'ICT Teacher',
    'Třídní učitelka': 'Class Teacher',
    'Třídní učitel': 'Class Teacher',
    'Učitel TV': 'PE Teacher',
    'Asistentka a vychovatelka': 'Teaching Assistant & Carer',
    'Asisteka pro první stupeň': 'Primary School Assistant',
    'logopedka': 'Speech Therapist',
    'Speciální pedagožka': 'Special Education Specialist',

    # FAQ page
    'Často kladené otázky': 'Frequently Asked Questions',
    'Odpovědi na nejčastejší dotazy rodičů': 'Answers to the most common questions from parents',
    'Dostávají děti domácí úkoly?': 'Do children get homework?',
    'Jak se mohou rodiče zapojit do vzdělávacího procesu?': 'How can parents get involved in the educational process?',
    'Pořádáte společné akce pro celé rodiny?': 'Do you organise events for whole families?',
    'Čím se Flow liší od ostatních škol?': 'How is Flow different from other schools?',
    'Kdo jsou pedagogové ve Flow?': 'Who are the teachers at Flow?',
    'Jaké mimoškolní aktivity jsou ve Flow k dispozici?': 'What after-school activities are available at Flow?',
    'Jak škola podporuje pozitivní a inkluzivní vzdělávací prostředí?': 'How does the school support a positive and inclusive learning environment?',
    'Jak jsou do učebních osnov začleněny technologie?': 'How is technology integrated into the curriculum?',
    'Mají děti možnost využívat služeb psychologa/speciálního pedagoga?': 'Do children have access to a psychologist or special education teacher?',
    'Moje dítě nemluví anglicky. Je to problém?': 'My child doesn\'t speak English. Is that a problem?',
    'Organizujete školy v přírodě?': 'Do you organise outdoor education trips?',
    'Jak škola komunikuje s rodiči o pokroku jejich dítěte?': 'How does the school communicate with parents about their child\'s progress?',
    'Jak vypadá výuka angličtiny?': 'What does English teaching look like?',
    'Kolik učitelů je ve třídě během výuky?': 'How many teachers are in the classroom during lessons?',
    'Jaký je počet dětí ve třídě?': 'How many children are in each class?',
    'Jak vypadá běžný školní den?': 'What does a typical school day look like?',
    'Stále máte otázky?': 'Still have questions?',
    'Napište nám': 'Write to us',

    # Career page
    'Kariéra ve FLOW': 'Career at FLOW',
    'Přidejte se k nám': 'Join Our Team',

    # New Campus page
    'FLOW má nový domov.': 'FLOW has a new home.',
    'Místo, kde vzdělání dýchá': 'A place where education breathes',
    'Od září 2026 se stěhujeme do moderního kampusu na Balabence.': 'From September 2026, we\'re moving to a modern campus in Balabanka.',
    'Více prostoru, čerstvý vzduch a špičkové zázemí pro vaše děti': 'More space, fresh air and top-class facilities for your children',
    'Prohlédnout vizualizace': 'View visualisations',
    'Lokalita: Strategicky a bezpečně': 'Location: Strategic and safe',
    'Kampus: Prostor stvořený pro soustředění': 'Campus: A space built for focus',
    'Milestones': 'Milestones',

    # For Applicants page
    'Vše, co potřebujete vědět': 'Everything you need to know',

    # Blog page
    'Novinky z naší školy FLOW': 'News from our FLOW school',
    'Naše poslední články': 'Our latest articles',
}

def get_page_title(filename):
    """Get English page title for the given Czech filename."""
    # Extract just the filename
    base_name = os.path.basename(filename)
    return PAGE_TITLES.get(base_name, 'Flow School')

def translate_text(content):
    """Apply all translations to the content."""
    for czech, english in TRANSLATIONS.items():
        # Simple string replacement - handle both exact matches and partial matches
        content = content.replace(czech, english)
    return content

def adjust_paths(content, depth):
    """Adjust relative paths for files in en/ subdirectory."""
    if depth == 1:
        # Files in en/ - prepend ../
        # Fix root-relative paths: images/, css/, js/, fonts/
        # Use negative lookbehind to avoid matching already prefixed paths
        content = re.sub(r'(href|src|content)="(?!\.\./)(?!http)(images|css|js|fonts)/', r'\1="../\2/', content)
    elif depth == 2:
        # Files in en/pro-zajemce/ - prepend ../../
        # First convert single ../ to ../../
        content = re.sub(r'(href|src|content)="(?<!\.)\.\./(images|css|js|fonts)/', r'\1="../../\2/', content)
        # Then handle root-relative paths
        content = re.sub(r'(href|src|content)="(?!\.\./)(?!http)(images|css|js|fonts)/', r'\1="../../\2/', content)

    return content

def update_language_switcher(content, depth, target_page):
    """Update language switcher for English pages."""
    # For English pages, the EN link should have w--current, CS should not
    # Also update link hrefs appropriately

    # Extract the base filename without extension for CS link
    base_name = os.path.basename(target_page).replace('.html', '')

    if depth == 1:
        cs_href = f'../{base_name}.html'
    else:  # depth == 2
        cs_href = f'../../{base_name}.html'

    # Pattern for the language switcher div
    # Look for the language switcher structure and update it
    # The CS link should point to the Czech version, EN link should be current

    # Replace CS link to point to Czech version
    content = re.sub(
        r'<a[^>]*?href="(\.\./)?' + re.escape(base_name) + r'\.html"[^>]*?w--current[^>]*?>',
        f'<a href="{cs_href}">',
        content
    )

    return content

def process_page(czech_source, english_target, depth):
    """Process a single page: read Czech, translate, and write English."""
    czech_path = os.path.join(SOURCE_DIR, czech_source)
    english_path = os.path.join(SOURCE_DIR, english_target)

    # Check if Czech source exists
    if not os.path.exists(czech_path):
        print(f'⚠ Skipping {czech_source}: source file not found')
        return False

    try:
        # Read Czech file
        with open(czech_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Change language attribute
        content = re.sub(r'<html lang="cs">', '<html lang="en">', content)

        # Update page title
        czech_filename = os.path.basename(czech_source)
        english_title = get_page_title(czech_filename)
        content = re.sub(
            r'<title>[^<]*</title>',
            f'<title>{english_title}</title>',
            content
        )

        # Apply translations
        content = translate_text(content)

        # Adjust paths for en/ subdirectory structure
        content = adjust_paths(content, depth)

        # Update language switcher
        # In the HTML, find the language switcher and toggle w--current classes
        # CS link gets removed w--current and points to Czech version
        # EN link gets w--current and points to current page

        # For root-level en/ pages
        if depth == 1:
            base_name = czech_filename.replace('.html', '')
            # Remove w--current from lang="cs" link
            content = re.sub(
                r'(<a[^>]*?hreflang="cs"[^>]*?class="[^"]*?)w--current([^"]*?"[^>]*?href=")[^"]*(")',
                r'\1\2../' + base_name + r'.html\3',
                content
            )
            # Add w--current to lang="en" link
            content = re.sub(
                r'(<a[^>]*?hreflang="en"[^>]*?class=")(?!.*w--current)([^"]*?")',
                r'\1w--current \2',
                content
            )
        else:  # depth == 2
            base_name = czech_filename.replace('.html', '')
            # Remove w--current from lang="cs" link
            content = re.sub(
                r'(<a[^>]*?hreflang="cs"[^>]*?class="[^"]*?)w--current([^"]*?"[^>]*?href=")[^"]*(")',
                r'\1\2../../' + base_name + r'.html\3',
                content
            )
            # Add w--current to lang="en" link
            content = re.sub(
                r'(<a[^>]*?hreflang="en"[^>]*?class=")(?!.*w--current)([^"]*?")',
                r'\1w--current \2',
                content
            )

        # Ensure target directory exists
        target_dir = os.path.dirname(english_path)
        os.makedirs(target_dir, exist_ok=True)

        # Write English file
        with open(english_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f'✓ Created {english_target}')
        return True

    except Exception as e:
        print(f'✗ Error processing {czech_source}: {e}')
        return False

def main():
    """Process all pages."""
    print('Starting English page generation...\n')

    success_count = 0
    for czech_source, english_target, depth in PAGES:
        if process_page(czech_source, english_target, depth):
            success_count += 1

    print(f'\n✓ Successfully created {success_count}/{len(PAGES)} English pages')

if __name__ == '__main__':
    main()

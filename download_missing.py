#!/usr/bin/env python3
"""
Download missing images with correct CDN bucket and URL encoding.
Run from Terminal:
  cd "$(dirname "$0")"
  python3 download_missing.py
"""
import os, subprocess, time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR    = os.path.join(SCRIPT_DIR, 'images')

CDN_STATIC = 'https://cdn.prod.website-files.com/67b351f4c755934221b66277/'
CDN_CMS    = 'https://cdn.prod.website-files.com/67b351f4c755934221b662d0/'

# (cdn_url_filename, local_filename)
# cdn_url_filename = exact filename as it appears in the CDN URL (percent-encoded)
# local_filename   = how it should be saved locally (matching what HTML references)

STATIC_IMAGES = [
    # SVG icons — in 66277 (static) bucket
    # Filename pattern: special chars encoded as %20, %28, %29 in URL
    ('67b351f4c755934221b66561_icon-element-2%20(1).svg',
     '67b351f4c755934221b66561_icon-element-2_20_1_.svg'),
    ('67b351f4c755934221b6657f_design-element-1%20(1).svg',
     '67b351f4c755934221b6657f_design-element-1_20_1_.svg'),
    ('67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24%20(1).svg',
     '67b351f4c755934221b66585_add-fill0-wght600-grad0-opsz24_20_1_.svg'),
    ('67b351f4c755934221b66647_location-on-fill0-wght600-grad0-opsz24%20(1).svg',
     '67b351f4c755934221b66647_location-on-fill0-wght600-grad0-opsz24_20_1_.svg'),
    ('67b351f4c755934221b66649_local-library-fill0-wght600-grad0-opsz24%20(1).svg',
     '67b351f4c755934221b66649_local-library-fill0-wght600-grad0-opsz24_20_1_.svg'),
    ('67b351f4c755934221b6669e_facebook-logo-black.svg',
     '67b351f4c755934221b6669e_facebook-logo-black.svg'),
    ('67b351f4c755934221b666a2_linkedin-logo-black.svg',
     '67b351f4c755934221b666a2_linkedin-logo-black.svg'),
    ('67b351f4c755934221b666a3_instagram-logo-dark.svg',
     '67b351f4c755934221b666a3_instagram-logo-dark.svg'),
    # Open Day announcement image — in 66277 bucket (confirmed via network intercept)
    ('6900e0b366ea2612977f2440_Copy%20of%20%20Flow_OpenDay_Post1Announce-min.png',
     '6900e0b366ea2612977f2440_Copy_20of_20_20Flow_OpenDay_Post1Announce-min.png'),
    # Jan 2026 WhatsApp event image
    ('696e29589da08f0f2728144e_WhatsApp%20Image%202026-01-19%20at%2013.47.52.jpeg',
     '696e29589da08f0f2728144e_WhatsApp_20Image_202026-01-19_20at_2013.47.52.jpeg'),
]

CMS_IMAGES = [
    # All CMS images — in 662d0 bucket (confirmed via network intercept)
    # Team photos
    ('68af7535879a555050038f0b_stella_foto.jpg',
     '68af7535879a555050038f0b_stella_foto.jpg'),
    ('68af75a538dad4cbf9c8600a_karlie_foto.jpg',
     '68af75a538dad4cbf9c8600a_karlie_foto.jpg'),
    ('68af76a655587d6bbf72e4e0_jelena_foto.jpg',
     '68af76a655587d6bbf72e4e0_jelena_foto.jpg'),
    ('68af76fcc41ae63ebe523e79_kathleen_foto.jpg',
     '68af76fcc41ae63ebe523e79_kathleen_foto.jpg'),
    ('68af77e51686d9a038d27e47_filip_brunclik_foto.jpg',
     '68af77e51686d9a038d27e47_filip_brunclik_foto.jpg'),
    ('68af79080e7a8da80cd42089_bara_foto.jpg',
     '68af79080e7a8da80cd42089_bara_foto.jpg'),
    ('68af7a7ba7b40a91b364915c_zofie_zemanova.jpg',
     '68af7a7ba7b40a91b364915c_zofie_zemanova.jpg'),
    ('68af7bf7b4ae80ca81893782_Sabrina%20Rhea%20Mazu%CC%81rova%CC%81.jpg',
     '68af7bf7b4ae80ca81893782_Sabrina_20Rhea_20Mazu_CC_81rova_CC_81.jpg'),
    ('68af7c4c48aa07e51c307c39_andrea_foto2.jpg',
     '68af7c4c48aa07e51c307c39_andrea_foto2.jpg'),
    ('68af7d6435b523f087deeeb1_tomas_foto.jpg',
     '68af7d6435b523f087deeeb1_tomas_foto.jpg'),
    ('67fa0475909cf7ec7a5b53a4_65450e36bb837c027473f6ef_FilipKabrt.jpeg',
     '67fa0475909cf7ec7a5b53a4_65450e36bb837c027473f6ef_FilipKabrt.jpeg'),
    ('67fa04761746ed1633a4365b_65450e2767da5fb9bee127be_Jitka.jpeg',
     '67fa04761746ed1633a4365b_65450e2767da5fb9bee127be_Jitka.jpeg'),
    ('67fa0478832cdc06e495b6b5_65450e48ec70f7d838edf89a_MichaelaKralova.jpeg',
     '67fa0478832cdc06e495b6b5_65450e48ec70f7d838edf89a_MichaelaKralova.jpeg'),
    ('67fa0478ff3797629639b018_677e4374d11099bb60f941d4_WhatsApp%2520Image%25202025-01-06%2520at%252014.01.53%2520(2).jpeg',
     '67fa0478ff3797629639b018_677e4374d11099bb60f941d4_WhatsApp_2520Image_25202025-01-06_2520at_252014.01.53_2520_2_.jpeg'),
    # Blog / about-us images
    ('67fa05ad909cf7ec7a5bd386_64131a4573926c53e4c8212c_marv%2520shamma%2520petr%2520mara%2520FLOW.png',
     '67fa05ad909cf7ec7a5bd386_64131a4573926c53e4c8212c_marv_2520shamma_2520petr_2520mara_2520FLOW.png'),
    ('67fa05ae85195bec98df752c_6413163efec18fbaf55f0913_marv%2520shamma%2520louis%2520theo%2520FLOW.png',
     '67fa05ae85195bec98df752c_6413163efec18fbaf55f0913_marv_2520shamma_2520louis_2520theo_2520FLOW.png'),
    ('67fa05ae0ed6b068638595e2_641315d2358366a47666a6bb_marv%2520shamma%2520TEDx%2520FLOW.png',
     '67fa05ae0ed6b068638595e2_641315d2358366a47666a6bb_marv_2520shamma_2520TEDx_2520FLOW.png'),
    ('67fa05ae59969dafd32603ab_64131bc6a541e877293bbb08_marv%2520shamma%2520eduzin.png',
     '67fa05ae59969dafd32603ab_64131bc6a541e877293bbb08_marv_2520shamma_2520eduzin.png'),
    ('67fa05af4ab03eb3caaeacca_6413191c73926ca33fc80f56_marv%2520shamma%2520talk%2520zlomu.png',
     '67fa05af4ab03eb3caaeacca_6413191c73926ca33fc80f56_marv_2520shamma_2520talk_2520zlomu.png'),
    ('67fa05ae93bc5ebc07b9e7e7_641317711bd52332d6f5038d_marv%2520shamma%2520na%2520vlne%2520podnikani%2520FLOW.png',
     '67fa05ae93bc5ebc07b9e7e7_641317711bd52332d6f5038d_marv_2520shamma_2520na_2520vlne_2520podnikani_2520FLOW.png'),
    ('67fa05ae61e24d76e7339090_62bc62bda6c21724b173b9bf_Flow_zalozeni_Flow_pilire.jpeg',
     '67fa05ae61e24d76e7339090_62bc62bda6c21724b173b9bf_Flow_zalozeni_Flow_pilire.jpeg'),
    ('67fa05ad1009eed5417a453c_629a06f52615627d37c29fd6_1_zMG2xRokwU0TADG7tNC7Lw.jpeg',
     '67fa05ad1009eed5417a453c_629a06f52615627d37c29fd6_1_zMG2xRokwU0TADG7tNC7Lw.jpeg'),
    ('67fa05ad1009eed5417a450b_629a06bc26638588a3f21bda_0_KOTOokIMM2pmbM9Y.jpeg',
     '67fa05ad1009eed5417a450b_629a06bc26638588a3f21bda_0_KOTOokIMM2pmbM9Y.jpeg'),
    ('67fa05ad1009eed5417a450f_629a06bc64c671f7ddc0d9c1_0_xarQLghBIcgoXo5n.jpeg',
     '67fa05ad1009eed5417a450f_629a06bc64c671f7ddc0d9c1_0_xarQLghBIcgoXo5n.jpeg'),
    ('67fa05ad85195bec98df7518_629f3156638026433e34a100_skolaflow_marvshammakids2.jpeg',
     '67fa05ad85195bec98df7518_629f3156638026433e34a100_skolaflow_marvshammakids2.jpeg'),
    ('67fa05ad85195bec98df751c_62aaf28906b229972a5ddbc1_skolaflow_4pilire.jpeg',
     '67fa05ad85195bec98df751c_62aaf28906b229972a5ddbc1_skolaflow_4pilire.jpeg'),
    ('67fa05ae61e24d76e733903e_62bc62886d06e59fd8fc8b99_Flow_tematicke_pilire.jpeg',
     '67fa05ae61e24d76e733903e_62bc62886d06e59fd8fc8b99_Flow_tematicke_pilire.jpeg'),
    ('67fa05ae61e24d76e7339046_62bc6246fe7b1f7566ab5c9d_Flow_dovednosti.jpeg',
     '67fa05ae61e24d76e7339046_62bc6246fe7b1f7566ab5c9d_Flow_dovednosti.jpeg'),
    # Team photo — confirmed 662d0
    ('68b58f006379b6fa63e1e1f4_9ABFEEF0-1572-44BD-8785-65B8FA7E8423_1_105_c.jpeg',
     '68b58f006379b6fa63e1e1f4_9ABFEEF0-1572-44BD-8785-65B8FA7E8423_1_105_c.jpeg'),
    # Timeline SVG (CMS asset — double ID prefix pattern)
    ('67c582cad2d3c9b602f5e136_66d96930ad1e7d10bbc6aa59_skola%20flow%20timeline.svg',
     '67c582cad2d3c9b602f5e136_66d96930ad1e7d10bbc6aa59_skola_20flow_20timeline.svg'),
    # Partner logos (CMS)
    ('680935e767127338a262bfd9_EU%2BM%D9%86MT%20%D8%8CB.svg',
     '680935e767127338a262bfd9_EU_2BM_D9_86MT_20_D8_8CB.svg'),
    ('68093a79aace0042c9a41742_CC_partner_kulaty%20copy.svg',
     '68093a79aace0042c9a41742_CC_partner_kulaty_20copy.svg'),
]

ok = fail = skip = 0

def curl_get(url, dest, label):
    global ok, fail, skip
    if os.path.exists(dest) and os.path.getsize(dest) > 100:
        print(f'  SKIP  {label[:60]}')
        skip += 1
        return
    result = subprocess.run([
        'curl', '-L', '-s', '-f',
        '-A', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        '-H', 'Referer: https://www.skolaflow.cz/',
        '-H', 'Accept: image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        '--max-time', '30',
        '-o', dest, url
    ], capture_output=True)
    if result.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 100:
        print(f'  OK    {label[:60]} ({os.path.getsize(dest):,} bytes)')
        ok += 1
    else:
        if os.path.exists(dest): os.remove(dest)
        print(f'  FAIL  {label[:60]} (exit {result.returncode})')
        fail += 1

total = len(STATIC_IMAGES) + len(CMS_IMAGES)
print(f'Downloading {total} missing images...\n')

print('=== Static bucket (66277) ===')
for cdn_name, local_name in STATIC_IMAGES:
    curl_get(CDN_STATIC + cdn_name, os.path.join(IMG_DIR, local_name), local_name)
    time.sleep(0.15)

print('\n=== CMS bucket (662d0) ===')
for cdn_name, local_name in CMS_IMAGES:
    curl_get(CDN_CMS + cdn_name, os.path.join(IMG_DIR, local_name), local_name)
    time.sleep(0.15)

print(f'\nDone: {ok} downloaded, {skip} skipped, {fail} failed')

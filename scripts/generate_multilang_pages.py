#!/usr/bin/env python3
"""Generate English and French wine pages for SEO.

This produces:
- /en/index.html
- /fr/index.html
- /wine/en/{pref}/index.html
- /wine/fr/{pref}/index.html
- /wine/en/{pref}/{id}.html
- /wine/fr/{pref}/{id}.html

The pages are intentionally lightweight but fully indexable and internally linked.
"""

import glob
import json
import os
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "wine.terroirhub.com"

PREF_NAMES_JA = {
    'hokkaido':'北海道','aomori':'青森県','iwate':'岩手県','miyagi':'宮城県','akita':'秋田県',
    'yamagata':'山形県','fukushima':'福島県','ibaraki':'茨城県','tochigi':'栃木県','gunma':'群馬県',
    'saitama':'埼玉県','chiba':'千葉県','tokyo':'東京都','kanagawa':'神奈川県','niigata':'新潟県',
    'toyama':'富山県','ishikawa':'石川県','fukui':'福井県','yamanashi':'山梨県','nagano':'長野県',
    'gifu':'岐阜県','shizuoka':'静岡県','aichi':'愛知県','mie':'三重県','shiga':'滋賀県',
    'kyoto':'京都府','osaka':'大阪府','hyogo':'兵庫県','nara':'奈良県','wakayama':'和歌山県',
    'tottori':'鳥取県','shimane':'島根県','okayama':'岡山県','hiroshima':'広島県','yamaguchi':'山口県',
    'tokushima':'徳島県','kagawa':'香川県','ehime':'愛媛県','kochi':'高知県','fukuoka':'福岡県',
    'saga':'佐賀県','nagasaki':'長崎県','kumamoto':'熊本県','oita':'大分県','miyazaki':'宮崎県',
    'kagoshima':'鹿児島県','okinawa':'沖縄県'
}

PREF_NAMES_EN = {
    k: v.replace("県", "").replace("府", "").replace("都", "").replace("道", "")
    for k, v in PREF_NAMES_JA.items()
}
PREF_NAMES_FR = PREF_NAMES_EN.copy()

ROOT_COPY = {
    "en": {
        "lang": "en",
        "title": "Japanese Wine Search — Terroir HUB WINE",
        "desc": "Explore Japan's wineries in English. Search by region, grape variety, and winery name across 432 wineries.",
        "headline": "Japanese Wine, made easy to explore.",
        "sub": "A multilingual directory of Japanese wine regions and wineries. Search, compare, and save wineries from one account.",
        "cta_search": "Search wineries",
        "cta_guide": "Read guides",
        "cta_plans": "See plans",
        "pill1": "Free login",
        "pill2": "My page included",
        "pill3": "Sakura is monthly",
        "section": "Featured regions",
        "section_sub": "Start with the regions that matter most to international search.",
        "regions": ["hokkaido", "yamanashi", "nagano", "tochigi", "hiroshima", "okayama"],
    },
    "fr": {
        "lang": "fr",
        "title": "Recherche de vins japonais — Terroir HUB WINE",
        "desc": "Découvrez les domaines viticoles japonais en français. Recherche par région, cépage et nom sur 432 domaines.",
        "headline": "Le vin japonais, facile à explorer.",
        "sub": "Un annuaire multilingue des régions et domaines viticoles japonais. Recherchez, comparez et enregistrez vos favoris avec un seul compte.",
        "cta_search": "Rechercher",
        "cta_guide": "Guides",
        "cta_plans": "Tarifs",
        "pill1": "Connexion gratuite",
        "pill2": "Espace personnel",
        "pill3": "Sakura en abonnement",
        "section": "Régions à découvrir",
        "section_sub": "Commencez par les régions les plus recherchées par les visiteurs internationaux.",
        "regions": ["hokkaido", "yamanashi", "nagano", "tochigi", "hiroshima", "okayama"],
    }
}

UI = {
    "en": {
        "home": "Home",
        "search": "Search",
        "guide": "Guides",
        "plans": "Plans",
        "mypage": "My Page",
        "back": "Back to Japan",
        "overview": "Overview",
        "features": "Features",
        "wines": "Representative wines",
        "visit": "Visit information",
        "faq": "FAQ",
        "pref_list": "{pref} wineries",
        "founded": "Founded",
        "located": "Located in",
        "phone": "Phone",
        "website": "Website",
        "visit_note": "Visit / tasting details",
        "faq_q1": "Can I visit {name}?",
        "faq_a1": "Visit and tasting availability is shown on the official information we have collected.",
        "faq_q2": "What are the signature wines?",
        "faq_a2": "Representative wines are listed on the page so you can compare them quickly.",
        "faq_q3": "Is there a Sakura assistant?",
        "faq_a3": "Yes. Sakura can answer questions in multiple languages after login.",
        "intro": "Official profile of {name}, a winery in {pref}, Japan.",
        "intro2": "This page is built for international search, comparison, and visit planning.",
        "brand_hint": "Representative brand",
        "region_h1": "{pref} wineries",
        "region_sub": "A curated list of wineries in {pref}.",
    },
    "fr": {
        "home": "Accueil",
        "search": "Recherche",
        "guide": "Guides",
        "plans": "Tarifs",
        "mypage": "Mon espace",
        "back": "Retour au Japon",
        "overview": "Aperçu",
        "features": "Caractéristiques",
        "wines": "Vins représentatifs",
        "visit": "Visite",
        "faq": "FAQ",
        "pref_list": "Domaines de {pref}",
        "founded": "Créé en",
        "located": "Situé à",
        "phone": "Téléphone",
        "website": "Site web",
        "visit_note": "Visite / dégustation",
        "faq_q1": "Peut-on visiter {name} ?",
        "faq_a1": "Les informations de visite et de dégustation sont indiquées selon les sources officielles disponibles.",
        "faq_q2": "Quels sont les vins phares ?",
        "faq_a2": "Les vins représentatifs sont listés pour faciliter la comparaison.",
        "faq_q3": "Y a-t-il un assistant Sakura ?",
        "faq_a3": "Oui. Sakura répond dans plusieurs langues après connexion.",
        "intro": "Fiche officielle de {name}, domaine viticole situé à {pref}, Japon.",
        "intro2": "Cette page est conçue pour la recherche internationale, la comparaison et la préparation de visite.",
        "brand_hint": "Marque phare",
        "region_h1": "Domaines de {pref}",
        "region_sub": "Une sélection des domaines viticoles de {pref}.",
    },
}


def esc(s):
    if s is None:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def slug_pref(pref):
    return pref


def pref_name(pref, lang):
    if lang == "en":
        return PREF_NAMES_EN.get(pref, pref)
    if lang == "fr":
        return PREF_NAMES_FR.get(pref, pref)
    return PREF_NAMES_JA.get(pref, pref)


def load_css():
    with open(os.path.join(BASE, "template_wine.html"), "r", encoding="utf-8") as f:
        tmpl = f.read()
    return tmpl[tmpl.find("<style>") + 7 : tmpl.find("</style>")]


CSS = load_css()


def page_head(title, desc, canonical, lang, hreflangs):
    links = "\n".join(
        f'<link rel="alternate" hreflang="{k}" href="{v}">' for k, v in hreflangs.items()
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{canonical}">
{links}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;700&family=Noto+Sans+JP:wght@300;400;500&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>"""


def page_footer():
    return """<footer class="site-footer">
  <div class="footer-brand">
    <p class="footer-tagline">Terroir HUB WINE</p>
    <div class="footer-logo">Terroir HUB <span class="accent">WINE</span></div>
  </div>
</footer>
</body></html>"""


def root_page(lang):
    t = ROOT_COPY[lang]
    ui = UI[lang]
    hreflangs = {
        "ja": "https://wine.terroirhub.com/",
        "en": "https://wine.terroirhub.com/en/",
        "fr": "https://wine.terroirhub.com/fr/",
        "x-default": "https://wine.terroirhub.com/en/",
    }
    cards = []
    for pref in t["regions"]:
        pn = pref_name(pref, lang)
        cards.append(
            f'<a class="promo-card" href="/wine/{lang}/{pref}/index.html"><div class="pc-body"><div class="pc-label">{esc(pn)}</div><div class="pc-name">{esc(ui["pref_list"].format(pref=pn))}</div><div class="pc-desc">{esc(ui["region_sub"].format(pref=pn))}</div></div></a>'
        )
    cards_html = "\n".join(cards)
    return page_head(t["title"], t["desc"], f"https://wine.terroirhub.com/{lang}/", lang, hreflangs) + f"""
<nav class="nav">
  <div class="nav-top">
    <a href="/" class="nav-logo">Terroir HUB <span style="color:#722F37">WINE</span></a>
    <a href="/" class="nav-back">{esc(ui["home"])}</a>
    <a href="/wine/search/" class="nav-page">{esc(ui["search"])}</a>
    <a href="/wine/guide/" class="nav-page">{esc(ui["guide"])}</a>
    <a href="/wine/plans/" class="nav-page">{esc(ui["plans"])}</a>
    <a href="/wine/mypage/" class="nav-page">{esc(ui["mypage"])}</a>
  </div>
</nav>
<section class="hero" style="grid-template-columns:1.15fr .85fr;">
  <div class="hero-left">
    <div class="hero-catch">TERROIR HUB WINE</div>
    <h1 class="hero-brand">{esc(t["headline"])}</h1>
    <p class="hero-sub">{esc(t["sub"])}</p>
    <div class="hero-role-row">
      <span class="hero-role-pill"><strong>{esc(t["pill1"])}</strong></span>
      <span class="hero-role-pill"><strong>{esc(t["pill2"])}</strong></span>
      <span class="hero-role-pill"><strong>{esc(t["pill3"])}</strong></span>
    </div>
    <div class="hero-search" style="margin-top:24px;">
      <a class="hero-ai-btn" href="/wine/search/">{esc(t["cta_search"])}</a>
      <a class="hero-ai-btn" href="/wine/guide/">{esc(t["cta_guide"])}</a>
      <a class="hero-ai-btn" href="/wine/plans/">{esc(t["cta_plans"])}</a>
    </div>
  </div>
  <div class="hero-right">
    <img class="hero-right-img" src="/img/hero-top.png" alt="Terroir HUB WINE">
  </div>
</section>
<section class="section features-sec">
  <div class="inner">
    <div class="sec-label">{esc(t["section"])}</div>
    <h2 class="sec-title">{esc(t["section"])}</h2>
    <p class="sec-desc">{esc(t["section_sub"])}</p>
  </div>
  <div class="feature-grid" style="margin-top:28px;">
    {cards_html}
  </div>
</section>
{page_footer()}
"""


def wine_page(b, pref, lang):
    t = UI[lang]
    pref_n = pref_name(pref, lang)
    bid = b.get("id", "")
    name = b.get("name", "")
    brand = b.get("brand", "")
    founded = str(b.get("founded", "") or "")
    desc = b.get("desc", "")
    address = b.get("address", "")
    tel = b.get("tel", "")
    url = b.get("url", "")
    area = b.get("area", "")
    visit = b.get("visit", "")
    station = b.get("nearest_station", "")
    features = b.get("features", []) or []
    brands = b.get("brands", []) or []

    canonical = f"https://wine.terroirhub.com/wine/{lang}/{pref}/{bid}.html"
    hreflangs = {
        "ja": f"https://wine.terroirhub.com/wine/{pref}/{bid}.html",
        "en": f"https://wine.terroirhub.com/wine/en/{pref}/{bid}.html",
        "fr": f"https://wine.terroirhub.com/wine/fr/{pref}/{bid}.html",
        "x-default": f"https://wine.terroirhub.com/wine/en/{pref}/{bid}.html",
    }
    intro = t["intro"].format(name=name, pref=pref_n)
    intro2 = t["intro2"]
    meta = f"{name} — {pref_n} {('winery' if lang == 'en' else 'domaine') if lang == 'fr' else 'winery'}"
    if founded:
        meta = f"{name} — {founded} {t['founded']} {pref_n}"

    brand_cards = []
    for br in brands[:3]:
        if isinstance(br, str):
            br = {"name": br, "specs": "", "type": ""}
        br_name = esc(br.get("name", ""))
        br_specs = esc(br.get("specs", ""))
        br_type = esc(br.get("type", ""))
        card = f'<div class="feature-card"><div class="fc-icon">🍷</div><div class="fc-name">{br_name}</div>'
        if br_type:
            card += f'<div class="fc-desc">{esc(t["brand_hint"])}: {br_type}</div>'
        if br_specs:
            card += f'<div class="fc-desc">{br_specs}</div>'
        card += "</div>"
        brand_cards.append(card)
    brand_cards_html = "\n".join(brand_cards)

    feature_cards = []
    for i, feat in enumerate(features[:3], start=1):
        feature_cards.append(
            f'<div class="feature-card"><div class="fc-icon">{i}</div><div class="fc-name">{esc(t["features"])} {i}</div><div class="fc-desc">{esc(feat)}</div></div>'
        )
    feature_cards_html = "\n".join(feature_cards)

    faq_html = f"""
    <div class="faq-item"><div class="faq-q">{esc(t["faq_q1"].format(name=name))}</div><div class="faq-a">{esc(t["faq_a1"])}</div></div>
    <div class="faq-item"><div class="faq-q">{esc(t["faq_q2"])}</div><div class="faq-a">{esc(t["faq_a2"])}</div></div>
    <div class="faq-item"><div class="faq-q">{esc(t["faq_q3"])}</div><div class="faq-a">{esc(t["faq_a3"])}</div></div>
    """
    visit_bits = []
    if address:
        visit_bits.append(f"<p><strong>{esc(t['located'])}</strong> {esc(address)}</p>")
    if station:
        visit_bits.append(f"<p><strong>Access</strong> {esc(station)}</p>")
    if tel:
        visit_bits.append(f"<p><strong>{esc(t['phone'])}</strong> {esc(tel)}</p>")
    if url:
        visit_bits.append(f'<p><strong>{esc(t["website"])}</strong> <a href="{esc(url)}" target="_blank" rel="noopener">{esc(url)}</a></p>')
    if visit:
        visit_bits.append(f"<p><strong>{esc(t['visit_note'])}</strong> {esc(visit)}</p>")
    visit_html = "\n".join(visit_bits) if visit_bits else "<p>—</p>"

    lang_back = "Back" if lang == "en" else "Retour"
    return page_head(f"{name} — {pref_n} | Terroir HUB WINE", intro, canonical, lang, hreflangs) + f"""
<nav class="nav">
  <div class="nav-top">
    <a href="/{lang}/" class="nav-logo">Terroir HUB <span style="color:#722F37">WINE</span></a>
    <a href="/{lang}/" class="nav-back">{esc(t["back"])}</a>
    <a href="/wine/{pref}/index.html" class="nav-page">JP</a>
    <a href="/wine/en/{pref}/index.html" class="nav-page">EN</a>
    <a href="/wine/fr/{pref}/index.html" class="nav-page">FR</a>
  </div>
</nav>
<section class="hero">
  <div class="hero-left">
    <div class="hero-catch">TERROIR HUB WINE</div>
    <h1 class="hero-brand">{esc(name)}</h1>
    <p class="hero-sub">{esc(intro)} {esc(intro2)}</p>
    <div class="hero-role-row">
      <span class="hero-role-pill"><strong>{esc(pref_n)}</strong></span>
      {f'<span class="hero-role-pill"><strong>{esc(founded)}</strong> {esc(t["founded"])}</span>' if founded else ''}
      {f'<span class="hero-role-pill"><strong>{esc(brand)}</strong></span>' if brand else ''}
    </div>
    <div class="hero-search" style="margin-top:24px;">
      <a class="hero-ai-btn" href="/wine/search/">{esc(t["search"])}</a>
      <a class="hero-ai-btn" href="/wine/guide/">{esc(t["guide"])}</a>
      <a class="hero-ai-btn" href="/wine/plans/">{esc(t["plans"])}</a>
    </div>
  </div>
  <div class="hero-right">
    <img class="hero-right-img" src="/img/winery-mountain-filled.jpg" alt="{esc(name)}">
  </div>
</section>

<section class="section features-sec">
  <div class="inner">
    <div class="sec-label">{esc(t["overview"])}</div>
    <h2 class="sec-title">{esc(name)}</h2>
    <p class="sec-desc">{esc(desc or intro)}</p>
    <div class="feature-grid" style="margin-top:28px;grid-template-columns:repeat(2,1fr);">
      <div class="feature-card"><div class="fc-icon">📍</div><div class="fc-name">{esc(t["visit"])}</div><div class="fc-desc">{visit_html}</div></div>
      <div class="feature-card"><div class="fc-icon">🗺️</div><div class="fc-name">{esc(pref_n)}</div><div class="fc-desc">{esc(area or pref_n)}</div></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="inner">
    <div class="sec-label">{esc(t["features"])}</div>
    <h2 class="sec-title">{esc(name)} {esc(t["features"])}</h2>
    <div class="feature-grid" style="margin-top:28px;">
      {feature_cards_html}
    </div>
  </div>
</section>

<section class="section features-sec">
  <div class="inner">
    <div class="sec-label">{esc(t["wines"])}</div>
    <h2 class="sec-title">{esc(name)} {esc(t["wines"])}</h2>
    <div class="feature-grid" style="margin-top:28px;">
      {brand_cards_html or '<div class="feature-card"><div class="fc-icon">🍇</div><div class="fc-name">—</div><div class="fc-desc">No public brand data</div></div>'}
    </div>
  </div>
</section>

<section class="section">
  <div class="inner">
    <div class="sec-label">{esc(t["faq"])}</div>
    <h2 class="sec-title">{esc(t["faq"])}</h2>
    <div class="feature-card" style="padding:20px;">
      {faq_html}
    </div>
  </div>
</section>

<section class="section features-sec">
  <div class="inner">
    <a class="hero-ai-btn" href="/wine/{pref}/index.html">{esc(pref_n)} index</a>
  </div>
</section>
{page_footer()}
"""


def pref_page(items, pref, lang):
    t = UI[lang]
    pref_n = pref_name(pref, lang)
    canonical = f"https://wine.terroirhub.com/wine/{lang}/{pref}/index.html"
    hreflangs = {
        "ja": f"https://wine.terroirhub.com/wine/{pref}/",
        "en": f"https://wine.terroirhub.com/wine/en/{pref}/index.html",
        "fr": f"https://wine.terroirhub.com/wine/fr/{pref}/index.html",
        "x-default": f"https://wine.terroirhub.com/wine/en/{pref}/index.html",
    }
    cards = []
    for b in items:
        name = esc(b.get("name", ""))
        bid = b.get("id", "")
        desc = esc((b.get("desc", "") or "")[:120])
        cards.append(
            f'<a class="feature-card" href="/wine/{lang}/{pref}/{bid}.html"><div class="fc-icon">🍷</div><div class="fc-name">{name}</div><div class="fc-desc">{desc}</div></a>'
        )
    cards_html = "\n".join(cards)
    return page_head(f"{pref_n} wineries | Terroir HUB WINE", t["region_sub"].format(pref=pref_n), canonical, lang, hreflangs) + f"""
<nav class="nav">
  <div class="nav-top">
    <a href="/{lang}/" class="nav-logo">Terroir HUB <span style="color:#722F37">WINE</span></a>
    <a href="/{lang}/" class="nav-back">{esc(t["back"])}</a>
    <a href="/wine/search/" class="nav-page">{esc(t["search"])}</a>
    <a href="/wine/guide/" class="nav-page">{esc(t["guide"])}</a>
    <a href="/wine/plans/" class="nav-page">{esc(t["plans"])}</a>
  </div>
</nav>
<section class="hero" style="min-height:auto;">
  <div class="hero-left">
    <div class="hero-catch">TERROIR HUB WINE</div>
    <h1 class="hero-brand">{esc(t["region_h1"].format(pref=pref_n))}</h1>
    <p class="hero-sub">{esc(t["region_sub"].format(pref=pref_n))}</p>
  </div>
  <div class="hero-right"><img class="hero-right-img" src="/img/map-japan-filled.jpg" alt="{esc(pref_n)}"></div>
</section>
<section class="section">
  <div class="inner">
    <div class="feature-grid">
      {cards_html}
    </div>
  </div>
</section>
{page_footer()}
"""


def main():
    json_files = sorted(glob.glob(os.path.join(BASE, "data", "data_*_wineries.json")))
    for lang in ("en", "fr"):
        Path(os.path.join(BASE, lang)).mkdir(parents=True, exist_ok=True)
        with open(os.path.join(BASE, lang, "index.html"), "w", encoding="utf-8") as f:
            f.write(root_page(lang))

    totals = {"en": 0, "fr": 0}
    for jf in json_files:
        pref = os.path.basename(jf).replace("data_", "").replace("_wineries.json", "")
        with open(jf, "r", encoding="utf-8") as f:
            items = json.load(f)

        for lang in ("en", "fr"):
            out_dir = os.path.join(BASE, "wine", lang, pref)
            os.makedirs(out_dir, exist_ok=True)

            pref_html = pref_page(items, pref, lang)
            with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write("\n".join(line.rstrip() for line in pref_html.splitlines()) + "\n")

            for b in items:
                if not b.get("id"):
                    continue
                html = wine_page(b, pref, lang)
                out = os.path.join(out_dir, f"{b['id']}.html")
                with open(out, "w", encoding="utf-8") as f:
                    f.write("\n".join(line.rstrip() for line in html.splitlines()) + "\n")
                totals[lang] += 1
        print(f"{pref}: generated en/fr pages")

    print(f"Done: en={totals['en']} fr={totals['fr']}")


if __name__ == "__main__":
    main()

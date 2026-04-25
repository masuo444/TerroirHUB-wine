#!/usr/bin/env python3
"""Generate localized English/French guide pages from Japanese sources."""

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def apply(text: str, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text


COMMON = [
    ('<html lang="ja">', '<html lang="{lang}">'),
    ('<a href="/" class="nav-logo">Terroir HUB <span>WINE</span></a>', '{logo}'),
    ('<a href="/wine/guide/">ガイド</a>', '{nav_guide}'),
    ('<a href="/wine/guide/beginner.html">初心者</a>', '{nav_beginner}'),
    ('<a href="/wine/guide/visit.html">見学</a>', '{nav_visit}'),
    ('<a href="/wine/guide/compare.html">比較</a>', '{nav_compare}'),
    ('<a href="/wine/guide/koshu.html">甲州</a>', '{nav_koshu}'),
    ('<a href="/wine/guide/yamanashi-vs-nagano.html">山梨 vs 長野</a>', '{nav_yamanashi_nagano}'),
    ('<a href="/wine/guide/koshu-vs-pinot.html">甲州 vs ピノ</a>', '{nav_koshu_pinot}'),
    ('<a href="/wine/guide/beginner-white.html">初心者の白</a>', '{nav_beginner_white}'),
    ('<a href="/wine/guide/hokkaido-pinot-noir.html">北海道ピノ</a>', '{nav_hokkaido_pinot}'),
    ('<a href="/wine/guide/nagano-merlot.html">長野メルロー</a>', '{nav_nagano_merlot}'),
]


def localized_link_prefix(text: str, lang: str) -> str:
    prefix = f'/{lang}/wine/guide/'
    text = text.replace('href="/wine/guide/', f'href="{prefix}')
    for slug in ("regions.html", "varieties.html", "production.html", "drinking.html", "pairing.html", "history.html", "glossary.html"):
        text = text.replace(f'href="{prefix}{slug}"', f'href="/wine/guide/{slug}"')
    text = text.replace('href="/wine/yamanashi/"', f'href="/{lang}/wine/yamanashi/"')
    text = text.replace('href="/wine/hokkaido/"', f'href="/{lang}/wine/hokkaido/"')
    text = text.replace('href="/wine/nagano/"', f'href="/{lang}/wine/nagano/"')
    text = text.replace('href="/wine/yamagata/"', f'href="/{lang}/wine/yamagata/"')
    text = text.replace('href="/wine/osaka/"', f'href="/{lang}/wine/osaka/"')
    text = text.replace('href="/wine/guide/"', f'href="/{lang}/wine/guide/"')
    text = text.replace('href="/wine/"', f'href="/{lang}/wine/"')
    return text


def build_page(src_name: str, lang: str, replacements, extras=None):
    src = read(BASE / "wine" / "guide" / src_name)
    text = src
    text = text.replace('<meta name="viewport" content="width=device-width, initial-scale=1.0">', '<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    text = localized_link_prefix(text, lang)
    source_url = f"https://wine.terroirhub.com/wine/guide/{src_name}"
    localized_url = f"https://wine.terroirhub.com/{lang}/wine/guide/{src_name}"
    text = text.replace(source_url, localized_url)
    if src_name != "index.html" and '<link rel="canonical" href="' in text:
        hreflang_block = (
            f'<link rel="alternate" hreflang="ja" href="{source_url}">\n'
            f'<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/{src_name}">\n'
            f'<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/wine/guide/{src_name}">\n'
            f'<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/en/wine/guide/{src_name}">'
        )
        text = text.replace(f'<link rel="canonical" href="{localized_url}">', f'<link rel="canonical" href="{localized_url}">\n{hreflang_block}')
    if extras:
        for old, new in extras:
            text = text.replace(old, new)
    for old, new in COMMON:
        text = text.replace(old, new.format(**replacements))
    return text


def main():
    pages = {
        "index.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "beginner.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html" class="active">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html" class="active">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "visit.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html" class="active">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html" class="active">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "compare.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html" class="active">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html" class="active">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "koshu.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html" class="active">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html" class="active">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "yamanashi-vs-nagano.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html" class="active">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html" class="active">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "koshu-vs-pinot.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html" class="active">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html" class="active">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "beginner-white.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html" class="active">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html" class="active">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "hokkaido-pinot-noir.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html" class="active">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html" class="active">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html">Merlot de Nagano</a>',
            },
        },
        "nagano-merlot.html": {
            "en": {
                "lang": "en",
                "logo": '<a href="/en/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/en/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/en/wine/guide/beginner.html">Beginner</a>',
                "nav_visit": '<a href="/en/wine/guide/visit.html">Visit</a>',
                "nav_compare": '<a href="/en/wine/guide/compare.html">Compare</a>',
                "nav_koshu": '<a href="/en/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/en/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/en/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/en/wine/guide/beginner-white.html">Beginner White</a>',
                "nav_hokkaido_pinot": '<a href="/en/wine/guide/hokkaido-pinot-noir.html">Hokkaido Pinot</a>',
                "nav_nagano_merlot": '<a href="/en/wine/guide/nagano-merlot.html" class="active">Nagano Merlot</a>',
            },
            "fr": {
                "lang": "fr",
                "logo": '<a href="/fr/" class="nav-logo">Terroir HUB <span>WINE</span></a>',
                "nav_guide": '<a href="/fr/wine/guide/">Guide</a>',
                "nav_beginner": '<a href="/fr/wine/guide/beginner.html">Débutant</a>',
                "nav_visit": '<a href="/fr/wine/guide/visit.html">Visite</a>',
                "nav_compare": '<a href="/fr/wine/guide/compare.html">Comparatif</a>',
                "nav_koshu": '<a href="/fr/wine/guide/koshu.html">Koshu</a>',
                "nav_yamanashi_nagano": '<a href="/fr/wine/guide/yamanashi-vs-nagano.html">Yamanashi vs Nagano</a>',
                "nav_koshu_pinot": '<a href="/fr/wine/guide/koshu-vs-pinot.html">Koshu vs Pinot</a>',
                "nav_beginner_white": '<a href="/fr/wine/guide/beginner-white.html">Blanc débutant</a>',
                "nav_hokkaido_pinot": '<a href="/fr/wine/guide/hokkaido-pinot-noir.html">Pinot d’Hokkaido</a>',
                "nav_nagano_merlot": '<a href="/fr/wine/guide/nagano-merlot.html" class="active">Merlot de Nagano</a>',
            },
        },
    }

    replacements = {
        ("index.html", "en"): [
            ('<title>日本ワインガイド — 品種・産地・歴史・ペアリングの総合教科書 | Terroir HUB WINE</title>', '<title>Japanese Wine Guide — varieties, regions, history, pairing | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの品種・産地・歴史・醸造工程・飲み方・ペアリングまで網羅する総合ガイド。甲州・マスカット・ベーリーAからGI産地まで徹底解説。">', '<meta name="description" content="A multilingual guide to Japanese wine: varieties, regions, history, brewing, drinking, and pairing.">'),
            ('<meta property="og:title" content="日本ワインガイド — 品種・産地・歴史・ペアリングの総合教科書 | Terroir HUB WINE">', '<meta property="og:title" content="Japanese Wine Guide | Terroir HUB WINE">'),
            ('<meta property="og:description" content="日本ワインの品種・産地・歴史・醸造工程・飲み方・ペアリングまで網羅する総合ガイド。">', '<meta property="og:description" content="A multilingual guide to Japanese wine.">'),
            ('<meta property="og:url" content="https://wine.terroirhub.com/wine/guide/index.html">', '<meta property="og:url" content="https://wine.terroirhub.com/en/wine/guide/index.html">'),
            ('<link rel="canonical" href="https://wine.terroirhub.com/wine/guide/index.html">', '<link rel="canonical" href="https://wine.terroirhub.com/en/wine/guide/index.html">'),
            ('<link rel="alternate" hreflang="ja" href="https://wine.terroirhub.com/wine/guide/index.html">', '<link rel="alternate" hreflang="ja" href="https://wine.terroirhub.com/wine/guide/index.html">'),
            ('<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/guide/index.html">', '<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/index.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><strong>日本ワインガイド</strong>', '<a href="/en/">← Terroir HUB WINE</a><span>›</span><strong>Japanese Wine Guide</strong>'),
            ('<h1>日本ワインガイド</h1>', '<h1>Japanese Wine Guide</h1>'),
            ('国産ぶどうから生まれる日本ワイン。品種・産地・醸造・歴史・ペアリングまで、基礎から深くまで解説する総合教科書です。', 'Japanese wine, from native grapes to modern styles. A practical guide to varieties, regions, brewing, history, and pairing.'),
            ('<h2>日本ワインとは</h2>', '<h2>What is Japanese wine?</h2>'),
            ('日本ワインとは、国産のぶどうのみを原料として日本国内で醸造されたワインです。2018年の酒税法改正により、この定義が法律上明確化されました。それ以前は「国産ワイン」という表示が外国産濃縮果汁を使ったものにも適用されていましたが、現在は国産ぶどう100%のものだけが「日本ワイン」を名乗れます。', 'Japanese wine is made in Japan from 100% domestically grown grapes. The legal definition was clarified in 2018.'),
            ('<h2>GI（地理的表示）産地</h2>', '<h2>GI (Geographical Indication) regions</h2>'),
            ('<h2 style="font-family:\'Shippori Mincho\',serif;font-size:22px;color:#2A1A1C;margin-bottom:24px;padding-bottom:8px;border-bottom:2px solid #722F37;">ガイド一覧</h2>', '<h2 style="font-family:\'Shippori Mincho\',serif;font-size:22px;color:#2A1A1C;margin-bottom:24px;padding-bottom:8px;border-bottom:2px solid #722F37;">Guide list</h2>'),
            ('<div class="card-num">GUIDE 00</div>', '<div class="card-num">GUIDE 00</div>'),
            ('<h3>初心者ガイド</h3>', '<h3>Beginner guide</h3>'),
            ('<p>日本ワインをどこから飲むか、最初の選び方をまとめた入口ページ。</p>', '<p>The best starting point for deciding where to begin with Japanese wine.</p>'),
        ],
        ("beginner.html", "en"): [
            ('<title>日本ワイン初心者ガイド | どこから飲むかが分かる入門ページ | Terroir HUB WINE</title>', '<title>Japanese wine beginner guide | Where to start | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをどこから飲むか迷う人向けの初心者ガイド。甲州・マスカット・ベーリーA・北海道ピノ・ノワール・長野メルローまで、最初の選び方を分かりやすく整理。">', '<meta name="description" content="A beginner guide to Japanese wine: how to start with Koshu, Muscat Bailey A, Hokkaido Pinot Noir, and Nagano Merlot.">'),
            ('<meta property="og:title" content="日本ワイン初心者ガイド | Terroir HUB WINE">', '<meta property="og:title" content="Japanese wine beginner guide | Terroir HUB WINE">'),
            ('<meta property="og:description" content="日本ワインをどこから飲むか迷う人向けの入門ページ。">', '<meta property="og:description" content="A beginner entry point for Japanese wine.">'),
            ('<h1>日本ワイン初心者ガイド</h1>', '<h1>Japanese wine beginner guide</h1>'),
            ('<p>どこから飲むか迷う人向けに、最初の一本、最初の産地、最初の見学先を整理しました。</p>', '<p>Where to start: the first bottle, the first region, and the first winery visit.</p>'),
            ('<h2>最初の結論</h2>', '<h2>Start here</h2>'),
            ('<p>最初の1本は甲州、赤からならマスカット・ベーリーAか長野のメルロー。産地は山梨・北海道・長野の3つから入ると理解しやすいです。</p>', '<p>Start with Koshu for white, or Muscat Bailey A / Nagano Merlot for red. Begin with Yamanashi, Hokkaido, and Nagano to understand the landscape quickly.</p>'),
            ('<h2>選び方の順番</h2>', '<h2>How to choose</h2>'),
            ('<strong>1. 産地を決める</strong>山梨・北海道・長野を先に見ると、気候と品種の違いが分かりやすいです。', '<strong>1. Choose a region</strong> Start with Yamanashi, Hokkaido, and Nagano to see the climate difference.'),
            ('<strong>2. 品種を決める</strong>甲州、ピノ・ノワール、メルローの3つを比較すると日本ワインの輪郭が見えます。', '<strong>2. Choose a grape</strong> Compare Koshu, Pinot Noir, and Merlot to see the core styles.'),
            ('<strong>3. 体験を決める</strong>見学できるワイナリーや直売所から入ると、味だけでなく現地の文脈も掴めます。', '<strong>3. Choose the experience</strong> Winery visits and direct sales help you understand the local context as well as the wine.'),
            ('<h2>最初に見るページ</h2>', '<h2>Pages to open first</h2>'),
            ('<a href="/wine/yamanashi/">山梨のワイナリー<span>甲州の本場</span></a>', '<a href="/en/wine/yamanashi/">Yamanashi wineries<span>Home of Koshu</span></a>'),
            ('<a href="/wine/hokkaido/">北海道のワイナリー<span>ピノとケルナー</span></a>', '<a href="/en/wine/hokkaido/">Hokkaido wineries<span>Pinot and Kerner</span></a>'),
            ('<a href="/wine/nagano/">長野のワイナリー<span>メルローの比較軸</span></a>', '<a href="/en/wine/nagano/">Nagano wineries<span>Merlot comparison axis</span></a>'),
            ('<a href="/wine/guide/regions.html">GI産地ガイド<span>5産地の比較</span></a>', '<a href="/wine/guide/regions.html">GI regions<span>Compare the five GI regions</span></a>'),
        ],
        ("visit.html", "en"): [
            ('<title>見学できる日本ワイナリーガイド | Terroir HUB WINE</title>', '<title>Japanese wineries you can visit | Terroir HUB WINE</title>'),
            ('<meta name="description" content="見学・試飲・直売がしやすい日本ワイナリーを探すための実用ガイド。山梨・北海道・長野・山形・大阪の導線をまとめています。">', '<meta name="description" content="A practical guide to Japanese wineries with visits, tastings, and direct sales.">'),
            ('<h1>見学できる日本ワイナリーガイド</h1>', '<h1>Japanese wineries you can visit</h1>'),
            ('<p>見学・試飲・直売の情報を起点に、現地で体験しやすい日本ワイナリーを探すためのページです。</p>', '<p>Start from visit, tasting, and direct-sales information to find wineries that are easy to experience on site.</p>'),
            ('<h2>探し方</h2>', '<h2>How to search</h2>'),
            ('<h2>見学前の確認</h2>', '<h2>Before you visit</h2>'),
            ('<h2>関連ページ</h2>', '<h2>Related pages</h2>'),
            ('<a class="card" href="/wine/yamanashi/">山梨から探す<span>勝沼・笛吹・甲府</span></a>', '<a class="card" href="/en/wine/yamanashi/">Search Yamanashi<span>Katsunuma, Fuefuki, Kofu</span></a>'),
            ('<a class="card" href="/wine/hokkaido/">北海道から探す<span>余市・仁木・空知</span></a>', '<a class="card" href="/en/wine/hokkaido/">Search Hokkaido<span>Yoichi, Niki, Sorachi</span></a>'),
            ('<a class="card" href="/wine/nagano/">長野から探す<span>塩尻・東御・安曇野</span></a>', '<a class="card" href="/en/wine/nagano/">Search Nagano<span>Shiojiri, Tōmi, Azumino</span></a>'),
            ('<a class="card" href="/wine/yamagata/">山形から探す<span>上山・高畠・南陽</span></a>', '<a class="card" href="/en/wine/yamagata/">Search Yamagata<span>Kaminoyama, Takahata, Nanyō</span></a>'),
            ('<a class="card" href="/wine/osaka/">大阪から探す<span>河内エリア</span></a>', '<a class="card" href="/en/wine/osaka/">Search Osaka<span>Kawachi area</span></a>'),
        ],
        ("compare.html", "en"): [
            ('<title>日本ワイン比較ハブ | 初心者・見学・甲州・北海道ピノ・長野メルロー | Terroir HUB WINE</title>', '<title>Japanese wine compare hub | beginner, visit, Koshu, Pinot, Merlot | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをどこから入るかを最短で決める比較ハブ。初心者、見学、甲州、北海道ピノ・ノワール、長野メルローを一目で比較できます。">', '<meta name="description" content="A compare hub for deciding where to start with Japanese wine.">'),
            ('<h1>日本ワイン比較ハブ</h1>', '<h1>Japanese wine compare hub</h1>'),
            ('<p>どこから入るかを先に決めると、日本ワインは一気に選びやすくなります。初心者、見学、甲州、北海道ピノ、長野メルローの5本柱で比較してください。</p>', '<p>Choosing the right entry point makes Japanese wine much easier to navigate. Compare beginner, visit, Koshu, Hokkaido Pinot, and Nagano Merlot.</p>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<th>入口</th>', '<th>Entry</th>'),
            ('<th>向いている人</th>', '<th>Best for</th>'),
            ('<th>主役</th>', '<th>Main focus</th>'),
            ('<th>次に読む</th>', '<th>Next</th>'),
            ('<h2>主要ページへの導線</h2>', '<h2>Key page links</h2>'),
            ('<a class="card" href="/wine/yamanashi/">山梨のワイナリー<span>甲州の本場</span></a>', '<a class="card" href="/en/wine/yamanashi/">Yamanashi wineries<span>Home of Koshu</span></a>'),
            ('<a class="card" href="/wine/hokkaido/">北海道のワイナリー<span>ピノ・ノワールとケルナー</span></a>', '<a class="card" href="/en/wine/hokkaido/">Hokkaido wineries<span>Pinot Noir and Kerner</span></a>'),
            ('<a class="card" href="/wine/nagano/">長野のワイナリー<span>メルローと欧州系品種</span></a>', '<a class="card" href="/en/wine/nagano/">Nagano wineries<span>Merlot and European varieties</span></a>'),
            ('<a class="card" href="/wine/guide/regions.html">GI産地ガイド<span>5産地の比較</span></a>', '<a class="card" href="/wine/guide/regions.html">GI regions<span>Compare the five GI regions</span></a>'),
        ],
        ("koshu.html", "en"): [
            ('<title>甲州ワイン完全ガイド | Terroir HUB WINE</title>', '<title>Koshu wine guide | Terroir HUB WINE</title>'),
            ('<meta name="description" content="甲州ワインの特徴、和食との相性、山梨の代表ワイナリーをまとめた完全ガイド。日本ワインの中心品種を深く知りたい人向け。">', '<meta name="description" content="A complete guide to Koshu wine, its style, food pairing, and key wineries in Yamanashi.">'),
            ('<h1>甲州ワイン完全ガイド</h1>', '<h1>Koshu wine guide</h1>'),
            ('<p>日本ワインの代表品種である甲州の味わい、料理との相性、探し方をまとめました。</p>', '<p>Everything you need to know about Koshu: style, food pairing, and where to find it.</p>'),
            ('<h2>甲州の特徴</h2>', '<h2>Koshu characteristics</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Where to start</h2>'),
            ('<h2>相性の良い料理</h2>', '<h2>Best food pairings</h2>'),
            ('<a class="card" href="/wine/guide/beginner.html">初心者向け<span>最初の1本として選ぶ</span></a>', '<a class="card" href="/en/wine/guide/beginner.html">Beginner<span>Choose your first bottle</span></a>'),
            ('<a class="card" href="/wine/guide/visit.html">見学ガイド<span>現地で味を確かめる</span></a>', '<a class="card" href="/en/wine/guide/visit.html">Visit guide<span>Taste it on site</span></a>'),
            ('<a class="card" href="/wine/yamanashi/">山梨のワイナリー<span>甲州の本場</span></a>', '<a class="card" href="/en/wine/yamanashi/">Yamanashi wineries<span>Home of Koshu</span></a>'),
        ],
        ("yamanashi-vs-nagano.html", "en"): [
            ('<title>山梨 vs 長野の日本ワイン比較 | 産地で選ぶならどっち？ | Terroir HUB WINE</title>', '<title>Yamanashi vs Nagano | which region should you choose? | Terroir HUB WINE</title>'),
            ('<meta name="description" content="山梨と長野の日本ワインを比較するページ。甲州の山梨、メルローと欧州系品種の長野を、気候・品種・味わい・向き不向きで整理。">', '<meta name="description" content="Compare Yamanashi and Nagano, two of the most important regions for Japanese wine.">'),
            ('<h1>山梨 vs 長野</h1>', '<h1>Yamanashi vs Nagano</h1>'),
            ('<p>産地で選ぶなら、この2つを並べるのが最短です。山梨は甲州の本場、長野は欧州系品種の完成度が見やすい産地です。</p>', '<p>If you choose by region, these two are the fastest comparison. Yamanashi is the home of Koshu, while Nagano shows European varieties at a high level.</p>'),
            ('<th>項目</th>', '<th>Item</th>'),
            ('<th>山梨</th>', '<th>Yamanashi</th>'),
            ('<th>長野</th>', '<th>Nagano</th>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        ("koshu-vs-pinot.html", "en"): [
            ('<title>甲州 vs ピノ・ノワールの比較 | 白と赤で迷う人のために | Terroir HUB WINE</title>', '<title>Koshu vs Pinot Noir | choose between white and red | Terroir HUB WINE</title>'),
            ('<meta name="description" content="甲州とピノ・ノワールを比較するページ。味わい、食事との相性、飲むシーンを並べて、白と赤で迷う人の選び方を整理。">', '<meta name="description" content="Compare Koshu and Pinot Noir side by side to decide between white and red.">'),
            ('<h1>甲州 vs ピノ・ノワール</h1>', '<h1>Koshu vs Pinot Noir</h1>'),
            ('<p>白と赤で迷ったら、この2本を並べるのが分かりやすいです。甲州は和食向きの白、ピノ・ノワールは軽やかな赤の代表です。</p>', '<p>If you are choosing between white and red, compare these two. Koshu is the white wine for Japanese food, while Pinot Noir is the classic light red.</p>'),
            ('<th>項目</th>', '<th>Item</th>'),
            ('<th>甲州</th>', '<th>Koshu</th>'),
            ('<th>ピノ・ノワール</th>', '<th>Pinot Noir</th>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        ("beginner-white.html", "en"): [
            ('<title>初心者向け白ワイン比較 | 甲州・シャルドネ・ケルナー | Terroir HUB WINE</title>', '<title>Beginner white wine comparison | Koshu, Chardonnay, Kerner | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワイン初心者が白から入るための比較ページ。甲州、シャルドネ、ケルナーを並べて、最初の1本を選びやすく整理。">', '<meta name="description" content="A white-wine comparison for beginners starting with Japanese wine.">'),
            ('<h1>初心者向け白ワイン比較</h1>', '<h1>Beginner white wine comparison</h1>'),
            ('<p>最初の1本を白から選ぶなら、甲州、シャルドネ、ケルナーの3本を見れば十分です。味わいの違いが分かりやすく、次の選択も簡単になります。</p>', '<p>If you want to start with white wine, Koshu, Chardonnay, and Kerner are enough to begin with.</p>'),
            ('<th>品種</th>', '<th>Variety</th>'),
            ('<th>向いている人</th>', '<th>Best for</th>'),
            ('<th>印象</th>', '<th>Impression</th>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        ("hokkaido-pinot-noir.html", "en"): [
            ('<title>北海道ピノ・ノワールガイド | Terroir HUB WINE</title>', '<title>Hokkaido Pinot Noir guide | Terroir HUB WINE</title>'),
            ('<meta name="description" content="北海道のピノ・ノワールを深掘りするガイド。余市・仁木・空知の代表的な探し方と、冷涼産地ならではの味わいを整理。">', '<meta name="description" content="A guide to Pinot Noir from Hokkaido, focused on Yoichi, Niki, and Sorachi.">'),
            ('<h1>北海道ピノ・ノワールガイド</h1>', '<h1>Hokkaido Pinot Noir guide</h1>'),
            ('<p>冷涼産地の代表である北海道のピノ・ノワールを、余市・仁木・空知を軸に整理しました。</p>', '<p>Hokkaido Pinot Noir, organized around Yoichi, Niki, and Sorachi.</p>'),
            ('<h2>北海道ピノの特徴</h2>', '<h2>Characteristics</h2>'),
            ('<h2>探し方</h2>', '<h2>How to search</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Pairing</h2>'),
        ],
        ("nagano-merlot.html", "en"): [
            ('<title>長野メルロー特化ガイド | Terroir HUB WINE</title>', '<title>Nagano Merlot guide | Terroir HUB WINE</title>'),
            ('<meta name="description" content="長野のメルローを深掘りするガイド。塩尻・東御・安曇野の探し方、味わいの傾向、合わせやすい料理をまとめています。">', '<meta name="description" content="A guide to Nagano Merlot, with Shiojiri, Tōmi, and Azumino as entry points.">'),
            ('<h1>長野メルロー特化ガイド</h1>', '<h1>Nagano Merlot guide</h1>'),
            ('<p>塩尻・東御・安曇野を軸に、長野のメルローを探すための比較ページです。</p>', '<p>A comparison page for finding Nagano Merlot through Shiojiri, Tōmi, and Azumino.</p>'),
            ('<h2>長野メルローの特徴</h2>', '<h2>Characteristics</h2>'),
            ('<h2>探し方</h2>', '<h2>How to search</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Pairing</h2>'),
        ],
    }

    french = {
        "index.html": [
            ('<title>日本ワインガイド — 品種・産地・歴史・ペアリングの総合教科書 | Terroir HUB WINE</title>', '<title>Guide du vin japonais — cépages, régions, histoire, accords | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの品種・産地・歴史・醸造工程・飲み方・ペアリングまで網羅する総合ガイド。甲州・マスカット・ベーリーAからGI産地まで徹底解説。">', '<meta name="description" content="Guide complet du vin japonais: cépages, régions, histoire, vinification et accords.">'),
            ('<meta property="og:title" content="日本ワインガイド — 品種・産地・歴史・ペアリングの総合教科書 | Terroir HUB WINE">', '<meta property="og:title" content="Guide du vin japonais | Terroir HUB WINE">'),
            ('<meta property="og:description" content="日本ワインの品種・産地・歴史・醸造工程・飲み方・ペアリングまで網羅する総合ガイド。">', '<meta property="og:description" content="Guide complet du vin japonais.">'),
            ('<meta property="og:url" content="https://wine.terroirhub.com/wine/guide/index.html">', '<meta property="og:url" content="https://wine.terroirhub.com/fr/wine/guide/index.html">'),
            ('<link rel="canonical" href="https://wine.terroirhub.com/wine/guide/index.html">', '<link rel="canonical" href="https://wine.terroirhub.com/fr/wine/guide/index.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><strong>日本ワインガイド</strong>', '<a href="/fr/">← Terroir HUB WINE</a><span>›</span><strong>Guide du vin japonais</strong>'),
            ('<h1>日本ワインガイド</h1>', '<h1>Guide du vin japonais</h1>'),
            ('国産ぶどうから生まれる日本ワイン。品種・産地・醸造・歴史・ペアリングまで、基礎から深くまで解説する総合教科書です。', 'Le vin japonais, des cépages aux accords.'),
            ('<h2>日本ワインとは</h2>', '<h2>Qu’est-ce que le vin japonais ?</h2>'),
            ('<h2>GI（地理的表示）産地</h2>', '<h2>Régions GI</h2>'),
            ('<h2 style="font-family:\'Shippori Mincho\',serif;font-size:22px;color:#2A1A1C;margin-bottom:24px;padding-bottom:8px;border-bottom:2px solid #722F37;">ガイド一覧</h2>', '<h2 style="font-family:\'Shippori Mincho\',serif;font-size:22px;color:#2A1A1C;margin-bottom:24px;padding-bottom:8px;border-bottom:2px solid #722F37;">Liste des guides</h2>'),
            ('<h3>初心者ガイド</h3>', '<h3>Guide débutant</h3>'),
            ('<p>日本ワインをどこから飲むか、最初の選び方をまとめた入口ページ。</p>', '<p>Le point de départ pour savoir par où commencer.</p>'),
        ],
        "beginner.html": [
            ('<title>日本ワイン初心者ガイド | どこから飲むかが分かる入門ページ | Terroir HUB WINE</title>', '<title>Guide débutant du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをどこから飲むか迷う人向けの初心者ガイド。甲州・マスカット・ベーリーA・北海道ピノ・ノワール・長野メルローまで、最初の選び方を分かりやすく整理。">', '<meta name="description" content="Guide débutant pour savoir par où commencer avec le vin japonais.">'),
            ('<h1>日本ワイン初心者ガイド</h1>', '<h1>Guide débutant du vin japonais</h1>'),
            ('<p>どこから飲むか迷う人向けに、最初の一本、最初の産地、最初の見学先を整理しました。</p>', '<p>Commencez ici: premier vin, première région, première visite.</p>'),
            ('<h2>最初の結論</h2>', '<h2>Conclusion</h2>'),
            ('<h2>選び方の順番</h2>', '<h2>Comment choisir</h2>'),
            ('<h2>最初に見るページ</h2>', '<h2>Pages à ouvrir d’abord</h2>'),
        ],
        "visit.html": [
            ('<title>見学できる日本ワイナリーガイド | Terroir HUB WINE</title>', '<title>Domaines japonais à visiter | Terroir HUB WINE</title>'),
            ('<meta name="description" content="見学・試飲・直売がしやすい日本ワイナリーを探すための実用ガイド。山梨・北海道・長野・山形・大阪の導線をまとめています。">', '<meta name="description" content="Guide pratique pour trouver des domaines japonais à visiter et déguster.">'),
            ('<h1>見学できる日本ワイナリーガイド</h1>', '<h1>Domaines japonais à visiter</h1>'),
            ('<p>見学・試飲・直売の情報を起点に、現地で体験しやすい日本ワイナリーを探すためのページです。</p>', '<p>Partez des informations de visite, dégustation et vente directe pour trouver un domaine facilement accessible.</p>'),
            ('<h2>探し方</h2>', '<h2>Comment chercher</h2>'),
            ('<h2>見学前の確認</h2>', '<h2>Avant la visite</h2>'),
            ('<h2>関連ページ</h2>', '<h2>Pages liées</h2>'),
        ],
        "compare.html": [
            ('<title>日本ワイン比較ハブ | 初心者・見学・甲州・北海道ピノ・長野メルロー | Terroir HUB WINE</title>', '<title>Hub comparatif du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをどこから入るかを最短で決める比較ハブ。初心者、見学、甲州、北海道ピノ・ノワール、長野メルローを一目で比較できます。">', '<meta name="description" content="Hub comparatif pour choisir rapidement par où commencer avec le vin japonais.">'),
            ('<h1>日本ワイン比較ハブ</h1>', '<h1>Hub comparatif du vin japonais</h1>'),
            ('<p>どこから入るかを先に決めると、日本ワインは一気に選びやすくなります。初心者、見学、甲州、北海道ピノ、長野メルローの5本柱で比較してください。</p>', '<p>Choisir l’entrée la plus simple rend le vin japonais beaucoup plus facile à explorer.</p>'),
            ('<h2>比較表</h2>', '<h2>Tableau comparatif</h2>'),
            ('<h2>主要ページへの導線</h2>', '<h2>Pages principales</h2>'),
        ],
        "koshu.html": [
            ('<title>甲州ワイン完全ガイド | Terroir HUB WINE</title>', '<title>Guide du Koshu | Terroir HUB WINE</title>'),
            ('<meta name="description" content="甲州ワインの特徴、和食との相性、山梨の代表ワイナリーをまとめた完全ガイド。日本ワインの中心品種を深く知りたい人向け。">', '<meta name="description" content="Guide du Koshu: style, accords et domaines de Yamanashi.">'),
            ('<h1>甲州ワイン完全ガイド</h1>', '<h1>Guide du Koshu</h1>'),
            ('<p>日本ワインの代表品種である甲州の味わい、料理との相性、探し方をまとめました。</p>', '<p>Tout sur le Koshu: goût, accords et comment le trouver.</p>'),
            ('<h2>甲州の特徴</h2>', '<h2>Caractéristiques</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Par où commencer</h2>'),
            ('<h2>相性の良い料理</h2>', '<h2>Accords recommandés</h2>'),
        ],
        "yamanashi-vs-nagano.html": [
            ('<title>山梨 vs 長野の日本ワイン比較 | 産地で選ぶならどっち？ | Terroir HUB WINE</title>', '<title>Yamanashi vs Nagano | Terroir HUB WINE</title>'),
            ('<meta name="description" content="山梨と長野の日本ワインを比較するページ。甲州の山梨、メルローと欧州系品種の長野を、気候・品種・味わい・向き不向きで整理。">', '<meta name="description" content="Compare Yamanashi and Nagano, two major regions for Japanese wine.">'),
            ('<h1>山梨 vs 長野</h1>', '<h1>Yamanashi vs Nagano</h1>'),
            ('<p>産地で選ぶなら、この2つを並べるのが最短です。山梨は甲州の本場、長野は欧州系品種の完成度が見やすい産地です。</p>', '<p>These two regions are the fastest comparison when you choose by place.</p>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        "koshu-vs-pinot.html": [
            ('<title>甲州 vs ピノ・ノワールの比較 | 白と赤で迷う人のために | Terroir HUB WINE</title>', '<title>Koshu vs Pinot Noir | Terroir HUB WINE</title>'),
            ('<meta name="description" content="甲州とピノ・ノワールを比較するページ。味わい、食事との相性、飲むシーンを並べて、白と赤で迷う人の選び方を整理。">', '<meta name="description" content="Compare Koshu and Pinot Noir side by side.">'),
            ('<h1>甲州 vs ピノ・ノワール</h1>', '<h1>Koshu vs Pinot Noir</h1>'),
            ('<p>白と赤で迷ったら、この2本を並べるのが分かりやすいです。甲州は和食向きの白、ピノ・ノワールは軽やかな赤の代表です。</p>', '<p>If you are choosing between white and red, these two wines are the clearest comparison.</p>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        "beginner-white.html": [
            ('<title>初心者向け白ワイン比較 | 甲州・シャルドネ・ケルナー | Terroir HUB WINE</title>', '<title>Beginner white wine comparison | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワイン初心者が白から入るための比較ページ。甲州、シャルドネ、ケルナーを並べて、最初の1本を選びやすく整理。">', '<meta name="description" content="A white-wine comparison for beginners.">'),
            ('<h1>初心者向け白ワイン比較</h1>', '<h1>Beginner white wine comparison</h1>'),
            ('<p>最初の1本を白から選ぶなら、甲州、シャルドネ、ケルナーの3本を見れば十分です。味わいの違いが分かりやすく、次の選択も簡単になります。</p>', '<p>Koshu, Chardonnay, and Kerner are enough to start with white wine.</p>'),
            ('<h2>比較表</h2>', '<h2>Comparison table</h2>'),
            ('<h2>次に読む</h2>', '<h2>Next pages</h2>'),
        ],
        "hokkaido-pinot-noir.html": [
            ('<title>北海道ピノ・ノワールガイド | Terroir HUB WINE</title>', '<title>Hokkaido Pinot Noir guide | Terroir HUB WINE</title>'),
            ('<meta name="description" content="北海道のピノ・ノワールを深掘りするガイド。余市・仁木・空知の代表的な探し方と、冷涼産地ならではの味わいを整理。">', '<meta name="description" content="A guide to Hokkaido Pinot Noir.">'),
            ('<h1>北海道ピノ・ノワールガイド</h1>', '<h1>Hokkaido Pinot Noir guide</h1>'),
            ('<p>冷涼産地の代表である北海道のピノ・ノワールを、余市・仁木・空知を軸に整理しました。</p>', '<p>Pinot Noir from Hokkaido, centered on Yoichi, Niki, and Sorachi.</p>'),
            ('<h2>北海道ピノの特徴</h2>', '<h2>Characteristics</h2>'),
            ('<h2>探し方</h2>', '<h2>How to search</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Pairing</h2>'),
        ],
        "nagano-merlot.html": [
            ('<title>長野メルロー特化ガイド | Terroir HUB WINE</title>', '<title>Nagano Merlot guide | Terroir HUB WINE</title>'),
            ('<meta name="description" content="長野のメルローを深掘りするガイド。塩尻・東御・安曇野の探し方、味わいの傾向、合わせやすい料理をまとめています。">', '<meta name="description" content="A guide to Nagano Merlot.">'),
            ('<h1>長野メルロー特化ガイド</h1>', '<h1>Nagano Merlot guide</h1>'),
            ('<p>塩尻・東御・安曇野を軸に、長野のメルローを探すための比較ページです。</p>', '<p>Find Nagano Merlot through Shiojiri, Tōmi, and Azumino.</p>'),
            ('<h2>長野メルローの特徴</h2>', '<h2>Characteristics</h2>'),
            ('<h2>探し方</h2>', '<h2>How to search</h2>'),
            ('<h2>合わせる料理</h2>', '<h2>Pairing</h2>'),
        ],
    }

    for src_name, lang_map in pages.items():
        for lang in ("en", "fr"):
            data = dict(lang_map[lang])
            text = build_page(src_name, lang, data)
            for old, new in replacements[(src_name, lang)] if (src_name, lang) in replacements else []:
                text = text.replace(old, new)
            for old, new in french.get(src_name, []) if lang == "fr" else []:
                text = text.replace(old, new)
            # Keep canonical and alternate links coherent.
            if lang == "en":
                text = text.replace('hreflang="en" href="https://wine.terroirhub.com/en/guide/index.html"',
                                    'hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/index.html"')
            if lang == "fr":
                text = text.replace('hreflang="en" href="https://wine.terroirhub.com/en/guide/index.html"',
                                    'hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/index.html"')
            out = BASE / lang / "wine" / "guide" / src_name
            write(out, text)

    print("Localized guide pages generated")


if __name__ == "__main__":
    main()

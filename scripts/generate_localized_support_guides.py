#!/usr/bin/env python3
"""Generate localized English/French versions of the remaining guide pages."""

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
SLUGS = ["regions.html", "varieties.html", "production.html", "drinking.html", "pairing.html", "history.html", "glossary.html"]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def replace_all(text: str, replacements):
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def localized_common(src_slug: str, lang: str):
    base = f"https://wine.terroirhub.com/{lang}/wine/guide/{src_slug}"
    ja = f"https://wine.terroirhub.com/wine/guide/{src_slug}"
    return [
        ('<html lang="ja">', f'<html lang="{lang}">'),
        (f'<link rel="canonical" href="{ja}">', f'<link rel="canonical" href="{base}">'),
        (f'<meta property="og:url" content="{ja}">', f'<meta property="og:url" content="{base}">'),
        (f'<link rel="alternate" hreflang="ja" href="{ja}">', f'<link rel="alternate" hreflang="ja" href="{ja}">'),
        (f'<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/{src_slug}">', f'<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/{src_slug}">'),
        (f'<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/wine/guide/{src_slug}">', f'<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/wine/guide/{src_slug}">'),
    ]


PAGES = {
    "regions.html": {
        "en": [
            ('<title>日本ワインのGI産地ガイド — 5地域の特徴 | Terroir HUB WINE</title>', '<title>Japanese wine GI regions — five key regions | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインのGI（地理的表示）認定5産地を解説。GI山梨・GI北海道・GI山形・GI大阪・GI長野の気候・土壌・代表ワイナリー・主要品種。">', '<meta name="description" content="A guide to the five Japanese wine GI regions: Yamanashi, Hokkaido, Yamagata, Osaka, and Nagano.">'),
            ('<meta property="og:title" content="日本ワインのGI産地ガイド — 5地域の特徴 | Terroir HUB WINE">', '<meta property="og:title" content="Japanese wine GI regions | Terroir HUB WINE">'),
            ('<meta property="og:description" content="GI山梨・GI北海道・GI山形・GI大阪・GI長野の特徴と代表ワイナリーを解説。">', '<meta property="og:description" content="The five Japanese wine GI regions and their characteristics.">'),
            ('<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/guide/regions.html">', '<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/regions.html">'),
            ('<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/wine/guide/regions.html">', '<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/en/wine/guide/regions.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><a href="/wine/guide/">ガイド</a><span>›</span><strong>GI産地ガイド</strong>', '<a href="/en/">← Terroir HUB WINE</a><span>›</span><a href="/en/wine/guide/">Guide</a><span>›</span><strong>GI regions</strong>'),
            ('<h1>日本ワインのGI産地ガイド</h1>', '<h1>Japanese wine GI regions</h1>'),
            ('<p>日本初のGI山梨からGI長野まで、国税庁が認定した5つのワインGI（地理的表示）産地を解説します。各産地の気候・土壌・代表品種・代表ワイナリーを紹介します。</p>', '<p>The five GI regions recognized for Japanese wine: Yamanashi, Hokkaido, Yamagata, Osaka, and Nagano.</p>'),
            ('<h2 class="section-h2">主要GI比較</h2>', '<h2 class="section-h2">GI comparison</h2>'),
            ('<h2 class="section-h2">GI（地理的表示）産地一覧</h2>', '<h2 class="section-h2">GI region list</h2>'),
            ('<a href="/wine/guide/varieties.html">品種から探す<span>甲州・MBA・ピノ・ノワール</span></a>', '<a href="/en/wine/guide/varieties.html">Search by grape<span>Koshu, MBA, Pinot Noir</span></a>'),
        ],
        "fr": [
            ('<title>日本ワインのGI産地ガイド — 5地域の特徴 | Terroir HUB WINE</title>', '<title>Régions GI du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインのGI（地理的表示）認定5産地を解説。GI山梨・GI北海道・GI山形・GI大阪・GI長野の気候・土壌・代表ワイナリー・主要品種。">', '<meta name="description" content="Les cinq régions GI du vin japonais: Yamanashi, Hokkaido, Yamagata, Osaka et Nagano.">'),
            ('<meta property="og:title" content="日本ワインのGI産地ガイド — 5地域の特徴 | Terroir HUB WINE">', '<meta property="og:title" content="Régions GI du vin japonais | Terroir HUB WINE">'),
            ('<meta property="og:description" content="GI山梨・GI北海道・GI山形・GI大阪・GI長野の特徴と代表ワイナリーを解説。">', '<meta property="og:description" content="Les cinq régions GI du vin japonais et leurs caractéristiques.">'),
            ('<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/guide/regions.html">', '<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/wine/guide/regions.html">'),
            ('<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/wine/guide/regions.html">', '<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/en/wine/guide/regions.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><a href="/wine/guide/">ガイド</a><span>›</span><strong>GI産地ガイド</strong>', '<a href="/fr/">← Terroir HUB WINE</a><span>›</span><a href="/fr/wine/guide/">Guide</a><span>›</span><strong>Régions GI</strong>'),
            ('<h1>日本ワインのGI産地ガイド</h1>', '<h1>Régions GI du vin japonais</h1>'),
            ('<p>日本初のGI山梨からGI長野まで、国税庁が認定した5つのワインGI（地理的表示）産地を解説します。各産地の気候・土壌・代表品種・代表ワイナリーを紹介します。</p>', '<p>Présentation des cinq régions GI reconnues pour le vin japonais.</p>'),
            ('<h2 class="section-h2">主要GI比較</h2>', '<h2 class="section-h2">Comparatif des régions GI</h2>'),
            ('<h2 class="section-h2">GI（地理的表示）産地一覧</h2>', '<h2 class="section-h2">Liste des régions GI</h2>'),
            ('<a href="/wine/guide/varieties.html">品種から探す<span>甲州・MBA・ピノ・ノワール</span></a>', '<a href="/fr/wine/guide/varieties.html">Chercher par cépage<span>Koshu, MBA, Pinot Noir</span></a>'),
        ],
    },
    "varieties.html": {
        "en": [
            ('<title>日本ワインのぶどう品種ガイド — 甲州・マスカット・ベーリーA・シャルドネ | Terroir HUB WINE</title>', '<title>Japanese wine grape varieties | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインで使われる主要ぶどう品種を解説。甲州・マスカット・ベーリーA・シャルドネ・メルロー・ピノ・ノワール・ケルナーなど白品種・赤品種の特徴・産地・代表銘柄。">', '<meta name="description" content="A guide to the main grape varieties used in Japanese wine.">'),
            ('<meta property="og:title" content="日本ワインのぶどう品種ガイド | Terroir HUB WINE">', '<meta property="og:title" content="Japanese wine grape varieties | Terroir HUB WINE">'),
            ('<meta property="og:description" content="甲州・MBA・シャルドネ・ピノ・ノワールなど日本ワインの主要品種を徹底解説。">', '<meta property="og:description" content="The main grape varieties used in Japanese wine.">'),
            ('<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/guide/varieties.html">', '<link rel="alternate" hreflang="en" href="https://wine.terroirhub.com/en/wine/guide/varieties.html">'),
            ('<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/wine/guide/varieties.html">', '<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/en/wine/guide/varieties.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><a href="/wine/guide/">ガイド</a><span>›</span><strong>品種ガイド</strong>', '<a href="/en/">← Terroir HUB WINE</a><span>›</span><a href="/en/wine/guide/">Guide</a><span>›</span><strong>Grape varieties</strong>'),
            ('<h1>日本ワインのぶどう品種ガイド</h1>', '<h1>Japanese wine grape varieties</h1>'),
            ('<p>甲州・マスカット・ベーリーAという日本固有の品種から、シャルドネ・メルロー・ピノ・ノワールなど欧州系品種まで。日本で栽培される主要品種の特徴・産地・代表銘柄を解説します。</p>', '<p>The main grape varieties used in Japanese wine, from Koshu and Muscat Bailey A to Chardonnay, Merlot, and Pinot Noir.</p>'),
            ('<h2 class="section-h2">品種早見表</h2>', '<h2 class="section-h2">Variety quick table</h2>'),
            ('<h2 class="section-h3" id="koshu">甲州</h2>', '<h2 class="section-h3" id="koshu">Koshu</h2>'),
            ('<h2 class="section-h3" id="mba">マスカット・ベーリーA</h2>', '<h2 class="section-h3" id="mba">Muscat Bailey A</h2>'),
            ('<h2 class="section-h3" id="chardonnay">シャルドネ</h2>', '<h2 class="section-h3" id="chardonnay">Chardonnay</h2>'),
            ('<h2 class="section-h3" id="kerner">ケルナー</h2>', '<h2 class="section-h3" id="kerner">Kerner</h2>'),
            ('<h2 class="section-h3" id="merlot">メルロー</h2>', '<h2 class="section-h3" id="merlot">Merlot</h2>'),
        ],
        "fr": [
            ('<title>日本ワインのぶどう品種ガイド — 甲州・マスカット・ベーリーA・シャルドネ | Terroir HUB WINE</title>', '<title>Cépages du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインで使われる主要ぶどう品種を解説。甲州・マスカット・ベーリーA・シャルドネ・メルロー・ピノ・ノワール・ケルナーなど白品種・赤品種の特徴・産地・代表銘柄。">', '<meta name="description" content="Guide des principaux cépages du vin japonais.">'),
            ('<meta property="og:title" content="日本ワインのぶどう品種ガイド | Terroir HUB WINE">', '<meta property="og:title" content="Cépages du vin japonais | Terroir HUB WINE">'),
            ('<meta property="og:description" content="甲州・MBA・シャルドネ・ピノ・ノワールなど日本ワインの主要品種を徹底解説。">', '<meta property="og:description" content="Les principaux cépages du vin japonais.">'),
            ('<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/guide/varieties.html">', '<link rel="alternate" hreflang="fr" href="https://wine.terroirhub.com/fr/wine/guide/varieties.html">'),
            ('<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/wine/guide/varieties.html">', '<link rel="alternate" hreflang="x-default" href="https://wine.terroirhub.com/en/wine/guide/varieties.html">'),
            ('<a href="/">← Terroir HUB WINE</a><span>›</span><a href="/wine/guide/">ガイド</a><span>›</span><strong>品種ガイド</strong>', '<a href="/fr/">← Terroir HUB WINE</a><span>›</span><a href="/fr/wine/guide/">Guide</a><span>›</span><strong>Cépages</strong>'),
            ('<h1>日本ワインのぶどう品種ガイド</h1>', '<h1>Cépages du vin japonais</h1>'),
            ('<p>甲州・マスカット・ベーリーAという日本固有の品種から、シャルドネ・メルロー・ピノ・ノワールなど欧州系品種まで。日本で栽培される主要品種の特徴・産地・代表銘柄を解説します。</p>', '<p>Les principaux cépages du vin japonais, des variétés natives aux cépages européens.</p>'),
            ('<h2 class="section-h2">品種早見表</h2>', '<h2 class="section-h2">Tableau rapide</h2>'),
        ],
    },
    "production.html": {
        "en": [
            ('<title>日本ワインの醸造工程 — 収穫から瓶詰めまで | Terroir HUB WINE</title>', '<title>Japanese wine production — harvest to bottle | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの醸造工程を収穫から瓶詰めまで詳しく解説。白ワイン・赤ワインの製法の違い、樽熟成・瓶熟成、自然派（ナチュラルワイン）についても紹介。">', '<meta name="description" content="A guide to Japanese wine production, from harvest to bottling.">'),
            ('<h1>日本ワインの醸造工程</h1>', '<h1>Japanese wine production</h1>'),
            ('<p>収穫・発酵・熟成・瓶詰めまでのワイン造りの流れを、白ワインと赤ワインの違いとあわせて整理します。</p>', '<p>From harvest to fermentation, aging, and bottling.</p>'),
            ('<h2 class="section-h2">醸造の基本ステップ</h2>', '<h2 class="section-h2">Basic production steps</h2>'),
            ('<h2 class="section-h2">白と赤の製法の違い</h2>', '<h2 class="section-h2">White vs red production</h2>'),
            ('<h2 class="section-h2">樽熟成の役割</h2>', '<h2 class="section-h2">The role of barrel aging</h2>'),
        ],
        "fr": [
            ('<title>日本ワインの醸造工程 — 収穫から瓶詰めまで | Terroir HUB WINE</title>', '<title>Vin japonais: de la vendange à la mise en bouteille | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの醸造工程を収穫から瓶詰めまで詳しく解説。白ワイン・赤ワインの製法の違い、樽熟成・瓶熟成、自然派（ナチュラルワイン）についても紹介。">', '<meta name="description" content="Guide de production du vin japonais, de la vendange à la mise en bouteille.">'),
            ('<h1>日本ワインの醸造工程</h1>', '<h1>Vin japonais: production</h1>'),
            ('<p>収穫・発酵・熟成・瓶詰めまでのワイン造りの流れを、白ワインと赤ワインの違いとあわせて整理します。</p>', '<p>De la vendange à la fermentation, l’élevage et la mise en bouteille.</p>'),
            ('<h2 class="section-h2">醸造の基本ステップ</h2>', '<h2 class="section-h2">Étapes de base</h2>'),
            ('<h2 class="section-h2">白と赤の製法の違い</h2>', '<h2 class="section-h2">Blanc vs rouge</h2>'),
            ('<h2 class="section-h2">樽熟成の役割</h2>', '<h2 class="section-h2">Rôle de l’élevage en fût</h2>'),
        ],
    },
    "drinking.html": {
        "en": [
            ('<title>日本ワインの飲み方 — 温度・グラス・保存方法 | Terroir HUB WINE</title>', '<title>How to drink Japanese wine — temperature, glass, storage | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをより美味しく楽しむための飲み方ガイド。白ワインの適飲温度8〜12℃、赤ワイン16〜18℃、スパークリング6〜8℃。グラス選びと開封後の保存方法も解説。">', '<meta name="description" content="A guide to serving Japanese wine: temperature, glassware, and storage.">'),
            ('<h1>日本ワインの飲み方</h1>', '<h1>How to drink Japanese wine</h1>'),
            ('<p>温度、グラス、保存の基本を押さえると、日本ワインの香りと味わいが素直に見えてきます。</p>', '<p>Temperature, glassware, and storage basics for Japanese wine.</p>'),
            ('<h2 class="section-h2">温度の目安</h2>', '<h2 class="section-h2">Serving temperatures</h2>'),
            ('<h2 class="section-h2">グラスの選び方</h2>', '<h2 class="section-h2">Choosing the right glass</h2>'),
            ('<h2 class="section-h2">開封後の保存</h2>', '<h2 class="section-h2">Storing after opening</h2>'),
        ],
        "fr": [
            ('<title>日本ワインの飲み方 — 温度・グラス・保存方法 | Terroir HUB WINE</title>', '<title>Servir le vin japonais — température, verre, conservation | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインをより美味しく楽しむための飲み方ガイド。白ワインの適飲温度8〜12℃、赤ワイン16〜18℃、スパークリング6〜8℃。グラス選びと開封後の保存方法も解説。">', '<meta name="description" content="Guide de service du vin japonais: température, verre et conservation.">'),
            ('<h1>日本ワインの飲み方</h1>', '<h1>Servir le vin japonais</h1>'),
            ('<p>温度、グラス、保存の基本を押さえると、日本ワインの香りと味わいが素直に見えてきます。</p>', '<p>Température, verre et conservation pour mieux apprécier le vin japonais.</p>'),
            ('<h2 class="section-h2">温度の目安</h2>', '<h2 class="section-h2">Températures de service</h2>'),
            ('<h2 class="section-h2">グラスの選び方</h2>', '<h2 class="section-h2">Choisir le verre</h2>'),
            ('<h2 class="section-h2">開封後の保存</h2>', '<h2 class="section-h2">Conservation après ouverture</h2>'),
        ],
    },
    "pairing.html": {
        "en": [
            ('<title>日本ワインと料理のペアリング — 和食×日本ワインの組み合わせ | Terroir HUB WINE</title>', '<title>Japanese wine food pairing | Terroir HUB WINE</title>'),
            ('<meta name="description" content="和食と日本ワインのペアリングガイド。甲州×刺身・天ぷら、MBA×焼き鳥・すき焼き、ピノ・ノワール×鴨・鮭、シャルドネ×蟹・ホタテ。和の食卓に合う日本ワインを解説。">', '<meta name="description" content="Food pairing guide for Japanese wine, especially with Japanese cuisine.">'),
            ('<h1>日本ワインと料理のペアリング</h1>', '<h1>Japanese wine food pairing</h1>'),
            ('<p>和食との相性を軸に、日本ワインの定番ペアリングをまとめました。</p>', '<p>Classic pairings for Japanese wine and Japanese cuisine.</p>'),
            ('<h2 class="section-h2">白ワインのペアリング</h2>', '<h2 class="section-h2">White wine pairings</h2>'),
            ('<h2 class="section-h2">赤ワインのペアリング</h2>', '<h2 class="section-h2">Red wine pairings</h2>'),
            ('<h2 class="section-h2">迷ったときの選び方</h2>', '<h2 class="section-h2">How to choose when in doubt</h2>'),
        ],
        "fr": [
            ('<title>日本ワインと料理のペアリング — 和食×日本ワインの組み合わせ | Terroir HUB WINE</title>', '<title>Accords mets-vins japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="和食と日本ワインのペアリングガイド。甲州×刺身・天ぷら、MBA×焼き鳥・すき焼き、ピノ・ノワール×鴨・鮭、シャルドネ×蟹・ホタテ。和の食卓に合う日本ワインを解説。">', '<meta name="description" content="Guide des accords mets-vins avec le vin japonais.">'),
            ('<h1>日本ワインと料理のペアリング</h1>', '<h1>Accords mets-vins japonais</h1>'),
            ('<p>和食との相性を軸に、日本ワインの定番ペアリングをまとめました。</p>', '<p>Accords classiques entre vin japonais et cuisine japonaise.</p>'),
            ('<h2 class="section-h2">白ワインのペアリング</h2>', '<h2 class="section-h2">Accords avec les blancs</h2>'),
            ('<h2 class="section-h2">赤ワインのペアリング</h2>', '<h2 class="section-h2">Accords avec les rouges</h2>'),
            ('<h2 class="section-h2">迷ったときの選び方</h2>', '<h2 class="section-h2">Comment choisir</h2>'),
        ],
    },
    "history.html": {
        "en": [
            ('<title>日本ワインの歴史 — 明治から現代まで | Terroir HUB WINE</title>', '<title>History of Japanese wine | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの歴史を年表で解説。1875年の国産ワイン発祥から、川上善兵衛のMBA育成、2013年GI山梨認定、2018年酒税法改正による「日本ワイン」定義明確化まで。">', '<meta name="description" content="A timeline of the history of Japanese wine.">'),
            ('<h1>日本ワインの歴史</h1>', '<h1>History of Japanese wine</h1>'),
            ('<p>1875年の国産ワイン発祥から、川上善兵衛によるMBA育成、GI制度の確立まで。150年に及ぶ日本ワインの歩みを年表で辿ります。</p>', '<p>From the birth of domestic wine in 1875 to today, traced as a timeline.</p>'),
            ('<h2 class="section-h2">日本ワイン年表</h2>', '<h2 class="section-h2">Timeline</h2>'),
        ],
        "fr": [
            ('<title>日本ワインの歴史 — 明治から現代まで | Terroir HUB WINE</title>', '<title>Histoire du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインの歴史を年表で解説。1875年の国産ワイン発祥から、川上善兵衛のMBA育成、2013年GI山梨認定、2018年酒税法改正による「日本ワイン」定義明確化まで。">', '<meta name="description" content="Chronologie de l’histoire du vin japonais.">'),
            ('<h1>日本ワインの歴史</h1>', '<h1>Histoire du vin japonais</h1>'),
            ('<p>1875年の国産ワイン発祥から、川上善兵衛によるMBA育成、GI制度の確立まで。150年に及ぶ日本ワインの歩みを年表で辿ります。</p>', '<p>De 1875 à aujourd’hui, l’histoire du vin japonais en timeline.</p>'),
            ('<h2 class="section-h2">日本ワイン年表</h2>', '<h2 class="section-h2">Chronologie</h2>'),
        ],
    },
    "glossary.html": {
        "en": [
            ('<title>日本ワイン用語集 — 20の基本用語 | Terroir HUB WINE</title>', '<title>Japanese wine glossary | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインを読むときに知っておきたい基本用語を解説。GI・テロワール・マセラシオン・樽熟成・スキンコンタクトなど20の重要ワード。">', '<meta name="description" content="A glossary of essential Japanese wine terms.">'),
            ('<h1>日本ワイン用語集</h1>', '<h1>Japanese wine glossary</h1>'),
            ('<p>日本ワインを読むときに知っておきたい基本用語をまとめました。</p>', '<p>Essential terms for reading about Japanese wine.</p>'),
        ],
        "fr": [
            ('<title>日本ワイン用語集 — 20の基本用語 | Terroir HUB WINE</title>', '<title>Glossaire du vin japonais | Terroir HUB WINE</title>'),
            ('<meta name="description" content="日本ワインを読むときに知っておきたい基本用語を解説。GI・テロワール・マセラシオン・樽熟成・スキンコンタクトなど20の重要ワード。">', '<meta name="description" content="Glossaire des termes essentiels du vin japonais.">'),
            ('<h1>日本ワイン用語集</h1>', '<h1>Glossaire du vin japonais</h1>'),
            ('<p>日本ワインを読むときに知っておきたい基本用語をまとめました。</p>', '<p>Termes essentiels pour lire sur le vin japonais.</p>'),
        ],
    },
}


def main():
    for slug in SLUGS:
        src = read(BASE / "wine" / "guide" / slug)
        for lang in ("en", "fr"):
            text = src
            text = replace_all(text, localized_common(slug, lang))
            text = replace_all(text, PAGES[slug][lang])
            text = text.replace("https://wine.terroirhub.com/en/guide/", "https://wine.terroirhub.com/en/wine/guide/")
            text = text.replace("https://wine.terroirhub.com/fr/guide/", "https://wine.terroirhub.com/fr/wine/guide/")
            text = text.replace('href="/wine/guide/', f'href="/{lang}/wine/guide/')
            text = text.replace('href="/wine/"', f'href="/{lang}/wine/"')
            text = text.replace('href="/wine/yamanashi/"', f'href="/{lang}/wine/yamanashi/"')
            text = text.replace('href="/wine/hokkaido/"', f'href="/{lang}/wine/hokkaido/"')
            text = text.replace('href="/wine/nagano/"', f'href="/{lang}/wine/nagano/"')
            text = text.replace('href="/wine/yamagata/"', f'href="/{lang}/wine/yamagata/"')
            text = text.replace('href="/wine/osaka/"', f'href="/{lang}/wine/osaka/"')
            out = BASE / lang / "wine" / "guide" / slug
            write(out, text)
    print("Localized support guide pages generated")


if __name__ == "__main__":
    main()

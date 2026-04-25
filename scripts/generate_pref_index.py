#!/usr/bin/env python3
"""
県別 index.html 生成スクリプト
各県のワイナリー一覧ページを SEO/AIO 最適化して生成。
ItemList JSON-LD + BreadcrumbList + FAQPage を含む。
"""

import json, glob, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

with open(os.path.join(BASE, 'template_wine.html'), 'r') as f:
    tmpl = f.read()
CSS = tmpl[tmpl.find('<style>') + 7:tmpl.find('</style>')]

DOMAIN = 'wine.terroirhub.com'

PREF_NAMES = {
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

GI_MAP = {
    'yamanashi': 'GI山梨', 'hokkaido': 'GI北海道',
    'nagano': 'GI長野', 'yamagata': 'GI山形', 'osaka': 'GI大阪'
}

PREF_VISUALS = {
    'yamanashi': {
        'src': 'https://commons.wikimedia.org/wiki/Special:FilePath/Katsunuma%20vineyard%2002.jpg',
        'alt': '勝沼のぶどう畑',
        'caption': '勝沼のぶどう畑 / Wikimedia Commons / CC BY 2.0',
    },
    'hokkaido': {
        'src': 'https://commons.wikimedia.org/wiki/Special:FilePath/130823Nikka%20Wisky%20Yoichi%20Distillery%20Hokkaido%20Japan18s3.jpg',
        'alt': '北海道・余市の蒸溜所',
        'caption': '北海道・余市の蒸溜所 / Wikimedia Commons',
    },
    'nagano': {
        'src': 'https://commons.wikimedia.org/wiki/Special:FilePath/Azumino%20Winery.jpg',
        'alt': '安曇野ワイナリー',
        'caption': '安曇野ワイナリー / Wikimedia Commons',
    },
}

WINE_STYLE_LABELS = {
    'dry_white':'辛口白', 'red':'赤', 'rose':'ロゼ', 'sweet':'甘口', 'sparkling':'泡'
}

def esc(s):
    if not s: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def brand_name(brand):
    if isinstance(brand, dict):
        return str(brand.get('name', '')).strip()
    return str(brand).strip() if brand else ''

def can_visit(winery):
    text = str(winery.get('visit', ''))
    if not text:
        return False
    negative = ('見学不可', '一般見学なし', '見学なし', '受け付けていない', '受付なし', '公開情報では')
    if any(word in text for word in negative):
        return False
    positive = ('見学', 'ツアー', '試飲', 'テイスティング', 'ショップ', '直売', 'カフェ', 'レストラン', 'ワインバー', '販売')
    return any(word in text for word in positive)

def generate_pref_page(pref_slug, wineries):
    pref_name = PREF_NAMES.get(pref_slug, pref_slug)
    gi = GI_MAP.get(pref_slug, '')
    count = len(wineries)
    page_url = f"https://{DOMAIN}/wine/{pref_slug}/"

    # A/Bランク判定
    def rank(b):
        return bool(b.get('url') and b.get('founded') and
                    len(b.get('brands',[])) >= 1 and len(b.get('features',[])) >= 2)

    a_wineries = [b for b in wineries if rank(b)]
    b_wineries = [b for b in wineries if not rank(b)]

    # 代表ワイナリー（メタ説明用）
    rep_names = '、'.join(b['name'] for b in a_wineries[:3]) if a_wineries else (wineries[0]['name'] if wineries else '')

    # メタ説明
    gi_txt = f'{gi}認定産地。' if gi else ''
    meta_desc = f"{pref_name}のワイナリー{count}件を掲載。{gi_txt}{rep_names}など{pref_name}の日本ワイン生産者情報。Terroir HUB WINE。"
    meta_desc = meta_desc[:160]

    top_grapes = {}
    for b in wineries:
        for g in b.get('grapes',[]):
            top_grapes[g] = top_grapes.get(g,0) + 1
    top_grape_names = sorted(top_grapes, key=lambda x:-top_grapes[x])[:5]
    visit_wineries = [b for b in wineries if can_visit(b)]
    brand_wineries = [b for b in wineries if any(brand_name(br) for br in b.get('brands', []) or [])]
    area_counts = {}
    for b in wineries:
        area = b.get('area') or pref_name
        area_counts[area] = area_counts.get(area, 0) + 1
    top_areas = sorted(area_counts, key=lambda x:-area_counts[x])[:5]

    # ItemList JSON-LD
    item_list = {
        "@type": "ItemList",
        "name": f"{pref_name}のワイナリー一覧",
        "description": meta_desc,
        "numberOfItems": count,
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": b.get('name',''),
                "url": f"https://{DOMAIN}/wine/{pref_slug}/{b['id']}.html"
            }
            for i, b in enumerate(wineries) if b.get('id')
        ]
    }

    breadcrumb = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type":"ListItem","position":1,"name":"Terroir HUB WINE","item":f"https://{DOMAIN}/"},
            {"@type":"ListItem","position":2,"name":pref_name,"item":page_url}
        ]
    }

    collection_page = {
        "@type": "CollectionPage",
        "@id": f"{page_url}#webpage",
        "url": page_url,
        "name": f"{pref_name}のワイナリー一覧",
        "description": meta_desc,
        "inLanguage": "ja",
        "isPartOf": {
            "@type": "WebSite",
            "@id": f"https://{DOMAIN}/#website",
            "name": "Terroir HUB WINE",
            "url": f"https://{DOMAIN}/"
        },
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": count,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": b.get('name',''),
                    "url": f"https://{DOMAIN}/wine/{pref_slug}/{b['id']}.html"
                }
                for i, b in enumerate(wineries) if b.get('id')
            ]
        },
        "about": [{"@type": "Thing", "name": g} for g in top_grape_names] + ([{"@type": "Thing", "name": gi}] if gi else [])
    }

    # FAQ JSON-LD
    faqs_data = [
        (f"{pref_name}にはワイナリーが何件ありますか？",
         f"{pref_name}には{count}件のワイナリーがあります（Terroir HUB WINE調べ）。"),
    ]
    if gi:
        faqs_data.append((
            f"{gi}とは何ですか？",
            f"{gi}は国税庁が認定した地理的表示（GI）で、{pref_name}産ぶどう100%使用のワインに付与されます。"
        ))
    if top_grapes:
        main_grapes = '、'.join(sorted(top_grapes, key=lambda x:-top_grapes[x])[:3])
        faqs_data.append((
            f"{pref_name}の主なブドウ品種は何ですか？",
            f"{pref_name}では主に{main_grapes}などが栽培されています。"
        ))
    visit_count = len(visit_wineries)
    if visit_count:
        faqs_data.append((
            f"{pref_name}のワイナリーは見学できますか？",
            f"{pref_name}では{visit_count}件のワイナリーが見学・テイスティングを受け入れています。要予約のところが多いため、各ワイナリーの公式サイトでご確認ください。"
        ))

    faq_schema = {
        "@type": "FAQPage",
        "mainEntity": [
            {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}
            for q, a in faqs_data
        ]
    }

    jsonld = json.dumps(
        {"@context":"https://schema.org","@graph":[collection_page, item_list, breadcrumb, faq_schema]},
        ensure_ascii=False, indent=2
    )

    # ── ワイナリーカード生成 ──
    def winery_card(b):
        style_label = WINE_STYLE_LABELS.get(b.get('wine_style',''), '')
        gi_b = b.get('gi','')
        grapes = b.get('grapes',[])
        brands_list = b.get('brands',[])
        brand_names = '、'.join(
            br.get('name','') if isinstance(br,dict) else str(br)
            for br in brands_list[:2] if br
        )
        founded = str(b.get('founded',''))
        area = b.get('area','')

        gi_html = f'<span class="gi-badge" style="font-size:9px;padding:2px 8px;">{esc(gi_b)}</span>' if gi_b else ''
        style_html = f'<span class="wine-badge {b.get("wine_style","red").replace("_","-")}" style="font-size:9px;padding:2px 8px;">{esc(style_label)}</span>' if style_label else ''
        grape_html = ''.join(f'<span class="grape-pill" style="font-size:9px;padding:3px 9px;">{esc(g)}</span>' for g in grapes[:3])
        brand_html = f'<p style="font-size:11px;color:var(--text-muted);margin:4px 0 0;">銘柄: {esc(brand_names)}</p>' if brand_names else ''
        founded_html = f'<span style="font-size:10px;color:var(--text-muted);">Est. {esc(founded)}</span>' if founded else ''

        return f'''
    <a href="/wine/{pref_slug}/{esc(b["id"])}.html" class="pref-card" style="text-decoration:none;display:block;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:18px 16px;transition:all 0.22s;position:relative;overflow:hidden;" onmouseover="this.style.boxShadow='0 4px 20px rgba(114,47,55,0.12)';this.style.borderColor='var(--gb)'" onmouseout="this.style.boxShadow='none';this.style.borderColor='var(--border)'">
      <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:8px;margin-bottom:8px;">
        <h3 style="font-family:'Zen Old Mincho',serif;font-size:15px;color:var(--text);line-height:1.3;flex:1;">{esc(b.get("name",""))}</h3>
        {founded_html}
      </div>
      <p style="font-size:11px;color:var(--text-muted);margin-bottom:8px;letter-spacing:0.05em;">{esc(area)}</p>
      <div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;">{gi_html}{style_html}</div>
      {f'<div class="grape-pills" style="margin-top:0;gap:4px;">{grape_html}</div>' if grape_html else ''}
      {brand_html}
      <div style="position:absolute;bottom:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--accent),transparent);opacity:0;transition:opacity 0.3s;" class="card-bar"></div>
    </a>'''

    # A/Bランク別セクション
    a_cards = ''.join(winery_card(b) for b in a_wineries)
    b_cards = ''.join(winery_card(b) for b in b_wineries)

    b_section = ''
    if b_wineries:
        b_section = f'''
<section class="section" style="background:var(--surface-warm);padding:48px 24px;">
  <div class="sec-inner">
    <label class="sec-label">MORE WINERIES</label>
    <h2 class="sec-title">その他のワイナリー</h2>
    <div class="sec-divider"></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">
      {b_cards}
    </div>
  </div>
</section>'''

    intent_cards = [
        (
            '見学で選ぶ',
            f'{visit_count}件',
            f'{pref_name}で見学・試飲・ショップ利用の導線があるワイナリー。',
            '#visit-guide'
        ),
        (
            '品種で選ぶ',
            '、'.join(top_grape_names[:3]) if top_grape_names else '主要品種',
            f'{pref_name}で多く使われる品種からワイナリーを探す。',
            '#grape-guide'
        ),
        (
            '代表銘柄で選ぶ',
            f'{len(brand_wineries)}件',
            '銘柄名が確認できるワイナリーから選ぶ。',
            '#brand-guide'
        ),
        (
            'エリアで選ぶ',
            '、'.join(top_areas[:3]),
            '市町村・産地エリアごとに比較する。',
            '#area-guide'
        ),
    ]
    if gi:
        intent_cards.insert(2, (
            'GIで選ぶ',
            gi,
            f'{gi}の地理的表示に関連するワイナリーを確認する。',
            '#gi-guide'
        ))

    intent_cards_html = ''.join(f'''
      <a href="{href}" style="display:block;text-decoration:none;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:18px 16px;min-height:132px;">
        <div style="font-size:11px;color:var(--accent);letter-spacing:0.14em;margin-bottom:10px;">{esc(title)}</div>
        <div style="font-family:'Zen Old Mincho',serif;font-size:20px;color:var(--text);line-height:1.35;margin-bottom:8px;">{esc(metric)}</div>
        <p style="font-size:12px;line-height:1.7;color:var(--text-muted);">{esc(body)}</p>
      </a>''' for title, metric, body, href in intent_cards)

    visit_links = ''.join(
        f'<li><a href="/wine/{pref_slug}/{esc(b["id"])}.html">{esc(b.get("name",""))}</a><span>{esc(b.get("area",""))}</span></li>'
        for b in visit_wineries[:8]
    ) or '<li><span>公開情報で確認できる見学・試飲情報は限定的です。訪問前に公式情報をご確認ください。</span></li>'

    grape_links = ''.join(
        f'<li><span>{esc(g)}</span><span>{top_grapes[g]}件</span></li>'
        for g in top_grape_names
    )

    brand_links = ''.join(
        f'<li><a href="/wine/{pref_slug}/{esc(b["id"])}.html">{esc(b.get("name",""))}</a><span>{esc(brand_name((b.get("brands") or [""])[0]))}</span></li>'
        for b in brand_wineries[:8]
    )

    area_links = ''.join(
        f'<li><span>{esc(area)}</span><span>{area_counts[area]}件</span></li>'
        for area in top_areas
    )

    gi_panel = ''
    if gi:
        gi_count = sum(1 for b in wineries if b.get('gi') == gi)
        gi_panel = f'''
      <div class="intent-panel" id="gi-guide">
        <h3>{esc(gi)}で選ぶ</h3>
          <p>{esc(pref_name)}はワインGI認定産地です。データ上は{gi_count}件が{esc(gi)}として掲載されています。</p>
      </div>'''

    hero_visual = ''
    if pref_slug in PREF_VISUALS:
        visual = PREF_VISUALS[pref_slug]
        hero_visual = f'''
<figure class="hero-visual" style="max-width:1100px;margin:24px auto 0;border:1px solid var(--border);border-radius:14px;overflow:hidden;background:var(--surface);">
  <img src="{visual["src"]}" alt="{esc(visual["alt"])}" style="display:block;width:100%;aspect-ratio:16/8;object-fit:cover;">
  <figcaption style="padding:12px 16px;font-size:12px;color:var(--text-muted);background:var(--surface-warm);border-top:1px solid var(--border);">{esc(visual["caption"])}</figcaption>
</figure>'''

    intent_section = f'''
<section class="section" style="background:var(--surface-warm);padding:44px 24px;">
  <div class="sec-inner">
    <label class="sec-label">FIND BY PURPOSE</label>
    <h2 class="sec-title">{esc(pref_name)}ワインの探し方</h2>
    <div class="sec-divider"></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin-bottom:28px;">
      {intent_cards_html}
    </div>
    <div class="intent-grid">
      <div class="intent-panel" id="visit-guide">
        <h3>見学・試飲で選ぶ</h3>
        <ul>{visit_links}</ul>
      </div>
      <div class="intent-panel" id="grape-guide">
        <h3>品種で選ぶ</h3>
        <ul>{grape_links}</ul>
      </div>
      {gi_panel}
      <div class="intent-panel" id="brand-guide">
        <h3>代表銘柄で選ぶ</h3>
        <ul>{brand_links}</ul>
      </div>
      <div class="intent-panel" id="area-guide">
        <h3>エリアで選ぶ</h3>
        <ul>{area_links}</ul>
      </div>
    </div>
  </div>
</section>'''

    # FAQ HTML
    faq_items_html = ''
    for i, (q, a) in enumerate(faqs_data):
        faq_items_html += f'''
    <div class="faq-item" id="faq-{i}">
      <div class="faq-q" onclick="var el=document.getElementById('faq-{i}');el.classList.toggle('open')">
        <span class="faq-q-q">Q</span>
        <span class="faq-q-text">{esc(q)}</span>
        <span class="faq-q-icon">▼</span>
      </div>
      <div class="faq-a">{esc(a)}</div>
    </div>'''

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(pref_name)}のワイナリー一覧（{count}件）| Terroir HUB WINE</title>
<meta name="description" content="{esc(meta_desc)}">
<meta property="og:title" content="{esc(pref_name)}のワイナリー一覧（{count}件）| Terroir HUB WINE">
<meta property="og:description" content="{esc(meta_desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="https://{DOMAIN}/img/hero.jpg">
<link rel="canonical" href="{page_url}">
<script type="application/ld+json">
{jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Noto+Serif+JP:wght@200;300;400&family=Zen+Old+Mincho:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
{CSS}
.intent-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;}}
.intent-panel{{background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:18px 16px;}}
.intent-panel h3{{font-family:'Zen Old Mincho',serif;font-size:17px;color:var(--text);margin-bottom:10px;}}
.intent-panel p{{font-size:13px;line-height:1.8;color:var(--text-muted);}}
.intent-panel ul{{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:8px;}}
.intent-panel li{{display:flex;justify-content:space-between;gap:12px;border-bottom:1px solid rgba(114,47,55,0.08);padding-bottom:8px;font-size:12px;color:var(--text-muted);}}
.intent-panel li:last-child{{border-bottom:0;padding-bottom:0;}}
.intent-panel a{{color:var(--text);text-decoration:none;}}
.intent-panel a:hover{{color:var(--accent);}}
</style>
</head>
<body>

<nav class="nav">
  <a class="nav-brand" href="/">
    <span class="nav-logo">Terroir HUB</span>
    <span class="nav-logo-sub">WINE</span>
  </a>
  <div class="nav-r">
    <a class="lb" href="/">TOP</a>
    <a class="lb" href="/wine/guide/">ガイド</a>
  </div>
</nav>

<nav class="breadcrumb" aria-label="パンくずリスト">
  <a href="/">Terroir HUB WINE</a>
  <span class="breadcrumb-sep">›</span>
  <span class="breadcrumb-current">{esc(pref_name)}</span>
</nav>

<section class="hero" style="min-height:50vh;">
  <div class="hero-bg"></div>
  <div class="hero-content">
    <div class="hero-badge"><span class="badge-dot"></span>TERROIR HUB WINE</div>
    {f'<div class="gi-badge" style="margin-bottom:16px;">{esc(gi)}</div>' if gi else ''}
    <h1 class="hero-title" style="font-size:clamp(32px,7vw,54px);">{esc(pref_name)}</h1>
    <p class="hero-subtitle">ワイナリー一覧</p>
    <p class="hero-en">{count} Wineries</p>
    <div class="hero-actions">
      <button class="btn-p" onclick="document.getElementById('winery-list').scrollIntoView({{behavior:'smooth'}})">一覧を見る</button>
    </div>
  </div>
</section>
{hero_visual}

{intent_section}

<section class="section" style="background:var(--bg);" id="winery-list">
  <div class="sec-inner">
    <label class="sec-label">WINERIES</label>
    <h2 class="sec-title">{esc(pref_name)}のワイナリー <span style="font-size:0.6em;color:var(--text-muted);">{count}件</span></h2>
    <div class="sec-divider"></div>
    {f'<p style="font-size:13px;color:var(--text-muted);margin-bottom:24px;letter-spacing:0.08em;">{esc(gi)}認定産地</p>' if gi else ''}
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">
      {a_cards}
    </div>
  </div>
</section>

{b_section}

<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <label class="sec-label">FAQ</label>
    <h2 class="sec-title">{esc(pref_name)}のワインについて</h2>
    <div class="sec-divider"></div>
    <div class="faq-list">{faq_items_html}
    </div>
  </div>
</section>

<footer class="site-footer">
  <div class="footer-brand">
    <p class="footer-tagline">日本ワインの世界を、もっと深く。</p>
    <div class="footer-logo">Terroir HUB <span class="accent">WINE</span></div>
  </div>
  <nav class="footer-nav">
    <a href="/">トップ</a>
    <a href="/wine/guide/">ワインガイド</a>
    <a href="/wine/region/hokkaido.html">産地別</a>
    <a href="https://sake.terroirhub.com/">日本酒版</a>
  </nav>
  <p class="footer-copy">© 2025 Terroir HUB WINE — {DOMAIN}</p>
</footer>

<script src="/wine/track.js" defer></script>
</body>
</html>'''


# ── メイン ──
json_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*_wineries.json')))
total = 0

for jf in json_files:
    pref = os.path.basename(jf).replace('data_','').replace('_wineries.json','')
    with open(jf, 'r', encoding='utf-8') as f:
        wineries = json.load(f)
    if not wineries:
        continue

    out_dir = os.path.join(BASE, 'wine', pref)
    os.makedirs(out_dir, exist_ok=True)

    html = '\n'.join(line.rstrip() for line in generate_pref_page(pref, wineries).splitlines()) + '\n'
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    total += 1
    print(f'  {pref}: {len(wineries)}件')

print(f'\n県別index.html: {total}県 生成完了')

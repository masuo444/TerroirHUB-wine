#!/usr/bin/env python3
"""
全ワイナリーHTMLページを一括再生成。
SEO/AIO強化版: Winery JSON-LD, FAQPage, GeoCoordinates, パンくずリスト, 品種タグ, FAQ HTML
"""

import json
import glob
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# テンプレートからCSS取得
with open(os.path.join(BASE, 'template_wine.html'), 'r') as f:
    tmpl = f.read()
CSS = tmpl[tmpl.find('<style>') + 7:tmpl.find('</style>')]

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

WINERY_TYPE_LABELS = {
    'estate': 'エステートワイナリー',
    'large': '大規模ワイナリー',
    'medium': '中規模ワイナリー',
    'small': '小規模ワイナリー',
    'natural': 'ナチュラルワイナリー',
}

WINE_STYLE_LABELS = {
    'dry_white': '辛口白ワイン',
    'red': '赤ワイン',
    'rose': 'ロゼワイン',
    'sweet': '甘口ワイン',
    'sparkling': 'スパークリングワイン',
}

DOMAIN = 'wine.terroirhub.com'


def esc(s):
    if not s: return ''
    return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def jsesc(s):
    if not s: return ''
    return str(s).replace('\\','\\\\').replace("'","\\'").replace('\n','\\n')

def build_faqs(name, brand, founded, founded_era, visit, address, station, brands, pref_name, grapes):
    faqs = []
    if visit:
        faqs.append((
            f"{name}の見学・テイスティングはできますか？",
            visit
        ))
    if brands:
        brand_names = [br.get('name','') for br in brands[:3] if isinstance(br, dict) and br.get('name')]
        if brand_names:
            a = f"代表銘柄は{'、'.join(brand_names)}などがあります。"
            if isinstance(brands[0], dict) and brands[0].get('specs'):
                a += brands[0]['specs']
            faqs.append((f"{name}の代表的なワインを教えてください", a))
    if address:
        a = f"住所は{address}です。"
        if station:
            a += f"最寄りは{station}です。"
        faqs.append((f"{name}の所在地・アクセスを教えてください", a))
    if founded:
        if founded_era:
            a = f"{founded_era}（{founded}年）に創業しました。{pref_name}を代表するワイナリーのひとつです。"
        else:
            a = f"{founded}年に創業しました。{pref_name}を代表するワイナリーのひとつです。"
        faqs.append((f"{name}はいつ創業しましたか？", a))
    if grapes:
        faqs.append((
            f"{name}ではどのようなブドウ品種を使っていますか？",
            f"主に{'、'.join(grapes)}を使用しています。"
        ))
    return faqs


def generate_page(b, pref_slug):
    pref_name = PREF_NAMES.get(pref_slug, pref_slug)
    name      = b.get('name','')
    brand     = b.get('brand','')
    founded   = str(b.get('founded','')) if b.get('founded') else ''
    founded_era = b.get('founded_era','')
    desc      = b.get('desc','')
    address   = b.get('address','')
    tel       = b.get('tel','')
    url       = b.get('url','')
    area      = b.get('area','')
    visit     = b.get('visit','')
    station   = b.get('nearest_station','')
    source    = b.get('source','')
    features  = b.get('features', [])
    brands    = b.get('brands', [])
    winery_type = b.get('winery_type','')
    wine_style  = b.get('wine_style','')
    gi        = b.get('gi','')
    grapes    = b.get('grapes', [])
    lat       = b.get('lat')
    lng       = b.get('lng')

    winery_label = WINERY_TYPE_LABELS.get(winery_type, '日本ワイナリー')

    years = ''
    if founded and founded.isdigit():
        years = str(2026 - int(founded))

    page_url = f"https://{DOMAIN}/wine/{pref_slug}/{b['id']}.html"

    # ── Meta description (SEO: ~120-160 chars) ──
    desc_short = desc[:80] if desc else ''
    if founded_era and area:
        meta_desc = f"{founded_era}創業。{pref_name}{area}の{winery_label}「{name}」。{desc_short}"
    elif founded and area:
        meta_desc = f"{founded}年創業。{pref_name}{area}の{winery_label}「{name}」。{desc_short}"
    else:
        meta_desc = f"{pref_name}の{winery_label}「{name}」。{desc_short}"
    meta_desc = meta_desc[:160]

    # ── FAQ data ──
    faqs = build_faqs(name, brand, founded, founded_era, visit, address, station, brands, pref_name, grapes)

    # ── JSON-LD ──
    local_biz = {
        "@type": ["LocalBusiness", "Winery"],
        "@id": page_url,
        "name": name,
        "description": desc[:200] if desc else name,
        "url": url if url else page_url,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address,
            "addressLocality": area or pref_name,
            "addressRegion": pref_name,
            "addressCountry": "JP"
        }
    }
    if founded:
        local_biz["foundingDate"] = founded
    if tel:
        local_biz["telephone"] = tel
    if lat and lng:
        local_biz["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": lat,
            "longitude": lng
        }
    if grapes:
        local_biz["knowsAbout"] = grapes

    breadcrumb_schema = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Terroir HUB WINE", "item": f"https://{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": pref_name, "item": f"https://{DOMAIN}/wine/{pref_slug}/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": page_url}
        ]
    }

    graph = [local_biz, breadcrumb_schema]

    if faqs:
        faq_schema = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": q,
                    "acceptedAnswer": {"@type": "Answer", "text": a}
                }
                for q, a in faqs
            ]
        }
        graph.append(faq_schema)

    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)

    # ── GI badge ──
    gi_badge_html = f'<div class="gi-badge">{esc(gi)}</div>' if gi else ''

    # ── Brands HTML ──
    brands_html = ''
    for br in brands[:3]:
        if isinstance(br, str):
            br = {'name': br, 'specs': ''}
        if not isinstance(br, dict):
            continue
        br_name   = str(br.get('name',''))
        br_specs  = str(br.get('specs',''))
        br_type   = br.get('type','')
        br_grapes = br.get('grapes','')
        specs_short = br_specs.split('、')[0] if br_specs else ''

        wine_badge_html = ''
        style_class = 'red'
        if br_type:
            if '白' in br_type: style_class = 'white'
            elif 'ロゼ' in br_type: style_class = 'rose'
            elif 'スパークリング' in br_type or '泡' in br_type: style_class = 'sparkling'
            elif '甘口' in br_type: style_class = 'sweet'
            wine_badge_html = f'<div class="wine-badge {style_class}">{esc(br_type)}</div>'

        brands_html += f'''
    <div class="brand-card">
      <div class="brand-img-wrap">
        <div class="brand-img-placeholder">PHOTO</div>
      </div>
      {wine_badge_html}
      {f'<div class="grape-tag">{esc(br_grapes)}</div>' if br_grapes else ''}
      <h3 class="brand-name">{esc(br_name)}</h3>
      <p class="brand-type">{esc(br_type or specs_short)}</p>
      {f'<p class="brand-desc">{esc(br_specs)}</p>' if br_specs else ''}
    </div>'''

    # ── Features HTML ──
    nums = ['①','②','③']
    features_html = ''
    for i, feat in enumerate(features[:3]):
        feat_text = feat if isinstance(feat, str) else str(feat)
        features_html += f'''
      <div class="fact">
        <div class="fact-num" style="font-family:\'Zen Old Mincho\',serif;font-size:42px;opacity:0.7;">{nums[i]}</div>
        <div>
          <div class="fact-lbl">特徴 {i+1}</div>
          <div class="fact-body">{esc(feat_text)}</div>
        </div>
      </div>'''

    # ── Founded fact ──
    facts_html = ''
    if years:
        facts_html = f'''
          <div class="fact">
            <div class="fact-num">{years}</div>
            <div>
              <div class="fact-lbl">年の歴史</div>
              <div class="fact-body">{esc(founded_era)}（{esc(founded)}年）創業。</div>
            </div>
          </div>'''

    # ── Story section ──
    story_section = ''
    if desc:
        story_section = f'''
<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <div class="story-grid">
      <div class="story-visual">
        <div class="story-visual-inner">
          <div class="bottle">
            <div class="bottle-neck"></div>
            <div class="bottle-lbl">
              <div class="bottle-lbl-txt">{esc(brand or name)}</div>
            </div>
          </div>
        </div>
      </div>
      <div>
        <label class="sec-label">STORY</label>
        <h2 class="sec-title">{esc(name)}の物語</h2>
        <div class="sec-divider"></div>
        <p class="sec-body">{esc(desc)}</p>
        {f'<div class="facts" style="margin-top:32px;">{facts_html}</div>' if facts_html else ''}
      </div>
    </div>
  </div>
</section>'''

    # ── Features section ──
    features_section = ''
    if features:
        features_section = f'''
<section class="section" style="background:var(--surface-warm);">
  <div class="sec-inner">
    <label class="sec-label">FEATURES</label>
    <h2 class="sec-title">{esc(name)}の特徴</h2>
    <div class="sec-divider"></div>
    <div class="facts">{features_html}
    </div>
  </div>
</section>'''

    # ── Grapes section ──
    grapes_section = ''
    if grapes:
        pills_html = ''
        for i, g in enumerate(grapes):
            cls = 'grape-pill main' if i == 0 else 'grape-pill'
            pills_html += f'<span class="{cls}">{esc(g)}</span>'
        grapes_section = f'''
<section class="section" style="background:var(--bg);padding:48px 24px;">
  <div class="sec-inner">
    <label class="sec-label">GRAPE VARIETIES</label>
    <h2 class="sec-title">使用品種</h2>
    <div class="sec-divider"></div>
    <p class="sec-body" style="font-size:14px;margin-bottom:4px;">{esc(name)}が使用する主なブドウ品種</p>
    <div class="grape-pills">{pills_html}</div>
  </div>
</section>'''

    # ── GI section ──
    gi_section = ''
    if gi:
        gi_section = f'''
<section class="section" style="background:var(--surface-warm);padding:36px 24px;">
  <div class="sec-inner" style="text-align:center;">
    <label class="sec-label">GEOGRAPHICAL INDICATION</label>
    <h2 class="sec-title" style="font-size:22px;">地理的表示（GI）認定産地</h2>
    <div class="sec-divider" style="margin:12px auto 16px;"></div>
    <div class="gi-badge" style="font-size:14px;padding:8px 24px;">{esc(gi)}</div>
    <p style="font-size:13px;color:var(--text-muted);margin-top:10px;letter-spacing:0.1em;">国税庁認定 地理的表示保護ワイン産地</p>
  </div>
</section>'''

    # ── Brands section ──
    brands_section = ''
    if brands:
        brands_section = f'''
<section class="section brands-section">
  <div class="sec-inner">
    <label class="sec-label">WINE</label>
    <h2 class="sec-title">代表銘柄</h2>
    <div class="sec-divider"></div>
    <div class="brands-grid">{brands_html}
    </div>
  </div>
</section>'''

    # ── Visit info items ──
    visit_items = ''
    if address:
        visit_items += f'<div style="display:flex;gap:14px;align-items:flex-start;"><span style="font-size:20px;">📍</span><div><div style="font-size:14px;font-weight:500;margin-bottom:3px;">所在地</div><div style="font-size:15px;color:var(--text-body);">{esc(address)}</div></div></div>'
    if tel:
        visit_items += f'<div style="display:flex;gap:14px;align-items:flex-start;"><span style="font-size:20px;">📞</span><div><div style="font-size:14px;font-weight:500;margin-bottom:3px;">電話</div><div style="font-size:15px;color:var(--text-body);">{esc(tel)}</div></div></div>'
    if url:
        visit_items += f'<div style="display:flex;gap:14px;align-items:flex-start;"><span style="font-size:20px;">🌐</span><div><div style="font-size:14px;font-weight:500;margin-bottom:3px;">ウェブサイト</div><div style="font-size:15px;"><a href="{esc(url)}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">{esc(url)}</a></div></div></div>'
    if visit:
        visit_items += f'<div style="display:flex;gap:14px;align-items:flex-start;"><span style="font-size:20px;">🏠</span><div><div style="font-size:14px;font-weight:500;margin-bottom:3px;">見学・試飲</div><div style="font-size:15px;color:var(--text-body);">{esc(visit)}</div></div></div>'

    # ── FAQ HTML ──
    faq_section = ''
    if faqs:
        faq_items_html = ''
        for i, (q, a) in enumerate(faqs):
            faq_items_html += f'''
    <div class="faq-item" id="faq-{i}">
      <div class="faq-q" onclick="toggleFaq({i})">
        <span class="faq-q-q">Q</span>
        <span class="faq-q-text">{esc(q)}</span>
        <span class="faq-q-icon" id="faq-icon-{i}">▼</span>
      </div>
      <div class="faq-a" id="faq-a-{i}">{esc(a)}</div>
    </div>'''
        faq_section = f'''
<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <label class="sec-label">FAQ</label>
    <h2 class="sec-title">よくある質問</h2>
    <div class="sec-divider"></div>
    <div class="faq-list">{faq_items_html}
    </div>
  </div>
</section>'''

    # ── Sakura chat suggestions ──
    sug1 = f'{jsesc(brand or name)}ってどんなワイン？' if brand else f'{jsesc(name)}について教えて'
    sug2 = 'ワイナリー見学はできる？'
    sug3 = 'おすすめのペアリングは？'
    sug4 = f'{jsesc(name)}の歴史を教えて'
    js_name  = jsesc(name)
    js_brand = jsesc(brand or name)

    og_desc = esc(meta_desc[:120])

    public_site_btn = ''
    if url:
        public_site_btn = f'<a class="btn-s" href="{esc(url)}" target="_blank" rel="noopener noreferrer">公式サイト</a>'

    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>{esc(name)} — {esc(pref_name)}のワイナリー | Terroir HUB WINE</title>
<meta name="description" content="{esc(meta_desc)}">
<meta property="og:title" content="{esc(name)} — {esc(pref_name)}のワイナリー | Terroir HUB WINE">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="https://{DOMAIN}/img/hero.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(name)} | Terroir HUB WINE">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image" content="https://{DOMAIN}/img/hero.jpg">
<link rel="canonical" href="{page_url}">
<link rel="alternate" hreflang="ja" href="{page_url}">
<link rel="alternate" hreflang="en" href="https://{DOMAIN}/wine/en/{pref_slug}/{b['id']}.html">
<link rel="alternate" hreflang="fr" href="https://{DOMAIN}/wine/fr/{pref_slug}/{b['id']}.html">
<link rel="alternate" hreflang="x-default" href="https://{DOMAIN}/wine/en/{pref_slug}/{b['id']}.html">
<script type="application/ld+json">
{jsonld}
</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300&family=Noto+Serif+JP:wght@200;300;400&family=Zen+Old+Mincho:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>

<nav class="nav">
  <a class="nav-brand" href="/">
    <span class="nav-logo">Terroir HUB</span>
    <span class="nav-logo-sub">WINE</span>
  </a>
  <div class="nav-r">
    <a class="lb active" href="/wine/{pref_slug}/{b['id']}.html">日本語</a>
    <a class="lb" href="/wine/en/{pref_slug}/{b['id']}.html">EN</a>
    <a class="lb" href="/wine/fr/{pref_slug}/{b['id']}.html">FR</a>
  </div>
</nav>

<nav class="breadcrumb" aria-label="パンくずリスト">
  <a href="/">Terroir HUB WINE</a>
  <span class="breadcrumb-sep">›</span>
  <a href="/wine/{pref_slug}/">{esc(pref_name)}</a>
  <span class="breadcrumb-sep">›</span>
  <span class="breadcrumb-current">{esc(name)}</span>
</nav>

<section class="hero">
  <div class="hero-bg">
    <div class="petal" style="left:10%;animation-delay:0s;"></div>
    <div class="petal" style="left:25%;animation-delay:1.5s;animation-duration:9s;"></div>
    <div class="petal" style="left:50%;animation-delay:3s;animation-duration:8s;width:8px;height:8px;"></div>
    <div class="petal" style="left:75%;animation-delay:4.5s;animation-duration:10s;"></div>
  </div>
  <div class="hero-content">
    <div class="hero-badge"><span class="badge-dot"></span>TERROIR HUB WINE</div>
    {f'<p class="hero-est">EST. {esc(founded)}</p>' if founded else ''}
    <h1 class="hero-title">{esc(name)}</h1>
    {f'<p class="hero-subtitle">{esc(brand)}</p>' if brand else ''}
    {f'<p class="hero-en">Since {esc(founded)} — {esc(area)}, {esc(pref_name)}</p>' if founded and area else ''}
    {gi_badge_html}
    <div class="hero-actions">
      <button class="btn-p" onclick="openPanel()">サクラに聞く</button>
      {public_site_btn}
    </div>
  </div>
  <div class="scroll-hint">
    <div class="scroll-line"></div>
    <span>SCROLL</span>
  </div>
</section>

{story_section}

{features_section}

{grapes_section}

{gi_section}

{brands_section}

<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <label class="sec-label">INFORMATION</label>
    <h2 class="sec-title">基本情報</h2>
    <div class="sec-divider"></div>
    <div class="story-grid" style="gap:32px;">
      <div style="display:flex;flex-direction:column;gap:22px;">
        {visit_items}
      </div>
      <div style="background:var(--surface-warm);border:1px solid var(--border);border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:240px;gap:8px;">
        <span style="font-size:28px;">📍</span>
        <div style="font-family:\'Zen Old Mincho\',serif;font-size:16px;color:var(--text);">{esc(name)}</div>
        <div style="font-size:13px;color:var(--text-muted);">{esc(pref_name)}{(' ' + esc(area)) if area else ''}</div>
      </div>
    </div>
    {f'<p style="font-size:13px;color:var(--text-muted);margin-top:16px;">{esc(station)}</p>' if station else ''}
    {f'<p style="font-size:11px;color:var(--text-muted);margin-top:12px;">出典：<a href="{esc(source)}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">{esc(source)}</a></p>' if source else ''}
  </div>
</section>

{faq_section}

<section class="section" style="background:var(--surface-warm);padding:32px 24px;">
  <div class="sec-inner">
    <a href="/wine/{pref_slug}/" class="back-link">← {esc(pref_name)}のワイナリー一覧へ</a>
  </div>
</section>

<!-- TRACKING -->
<script src="/wine/track.js" defer></script>
<div id="reviews-section" data-producer-id="{b['id']}" data-category="wine"></div>
<script src="/wine/reviews.js" defer></script>

<footer class="site-footer">
  <div class="footer-brand">
    <p class="footer-tagline">日本ワインの世界を、もっと深く。</p>
    <div class="footer-logo">Terroir HUB <span class="accent">WINE</span></div>
  </div>
  <nav class="footer-nav">
    <a href="/">トップ</a>
    <a href="/wine/{pref_slug}/">{esc(pref_name)}</a>
    <a href="/wine/guide/">ワインガイド</a>
    <a href="/wine/region/hokkaido.html">産地別</a>
    <a href="https://sake.terroirhub.com/">日本酒版</a>
  </nav>
  <p class="footer-copy">© 2025 Terroir HUB WINE — {DOMAIN}</p>
</footer>

<!-- FAB -->
<button class="fab" onclick="openPanel()" id="fab">
  <span class="fab-pulse"></span>
  <span>🌸</span>
  <span id="fab-txt">サクラに聞く</span>
</button>

<!-- SAKURA PANEL -->
<div class="overlay" id="overlay" onclick="if(event.target===this)closePanel()">
  <div class="panel">
    <div class="p-handle"></div>
    <div class="p-hdr">
      <div class="p-hdr-l">
        <div class="p-av">桜</div>
        <div>
          <div class="p-title">サクラ — AIコンシェルジュ</div>
          <div class="p-status"><div class="p-dot"></div><span>オンライン</span></div>
        </div>
      </div>
      <div style="display:flex;align-items:center;gap:7px;">
        <button class="p-close" onclick="closePanel()">✕</button>
      </div>
    </div>
    <div class="chat" id="chat"></div>
    <div class="sugs" id="sugs"></div>
    <div class="inp-row">
      <textarea id="chat-inp" rows="1" placeholder="{esc(name)}について何でもどうぞ…" onkeydown="if(event.key==='Enter'&&!event.shiftKey){{event.preventDefault();sendMsg();}}"></textarea>
      <button id="chat-send" onclick="sendMsg()">↑</button>
    </div>
  </div>
</div>

<script>
function toggleFaq(i){{
  var item=document.getElementById('faq-'+i);
  item.classList.toggle('open');
}}
function openPanel(){{document.getElementById('overlay').classList.add('open');document.getElementById('fab').style.display='none';if(!ci)initChat();}}
function closePanel(){{document.getElementById('overlay').classList.remove('open');document.getElementById('fab').style.display='flex';}}
var ci=false;
var BN='{js_name}',BB='{js_brand}';
var SUGS=['{jsesc(sug1)}','{jsesc(sug2)}','{jsesc(sug3)}','{jsesc(sug4)}'];
function initChat(){{ci=true;document.getElementById('chat').innerHTML='';addMsg('butler','ようこそ、'+BN+'へ。\\n\\nこのワイナリーについて何でもお気軽にお尋ねください。');renderSugs();}}
function addMsg(r,t){{var c=document.getElementById('chat'),d=document.createElement('div');d.className='msg '+r;d.innerHTML='<div class="av">'+(r==='butler'?'桜':'あ')+'</div><div class="bubble">'+t.replace(/\\n/g,'<br>')+'</div>';c.appendChild(d);c.scrollTop=c.scrollHeight;}}
function renderSugs(){{document.getElementById('sugs').innerHTML=SUGS.map(function(s){{return '<button class="sug" onclick="askSug(this.textContent)">'+s+'</button>';}}).join('');}}
var chatHistory=[];
function askSug(q){{document.getElementById('sugs').innerHTML='';sendQuestion(q);}}
function sendMsg(){{var i=document.getElementById('chat-inp'),q=i.value.trim();if(!q)return;i.value='';sendQuestion(q);}}
async function sendQuestion(q){{
  document.getElementById('sugs').innerHTML='';
  addMsg('user',q);showT();
  chatHistory.push({{role:'user',content:q}});
  try{{
    var ctx=BN+' — {jsesc(pref_name)}のワイナリー';
    var res=await fetch('https://sake.terroirhub.com/api/sakura',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{question:q,history:chatHistory.slice(-10),context:ctx,userId:window._thubUserId||null}})}});
    var data=await res.json();
    removeT();
    var ans=data.answer||'申し訳ありません、少し時間をおいてからもう一度お試しください。';
    addMsg('butler',ans);
    chatHistory.push({{role:'assistant',content:ans}});
  }}catch(e){{
    removeT();addMsg('butler','通信エラーが発生しました。もう一度お試しください。');
  }}
  renderSugs();
}}
function showT(){{var c=document.getElementById('chat'),d=document.createElement('div');d.className='msg butler';d.id='tp';d.innerHTML='<div class="av">桜</div><div class="bubble"><div class="typing"><div class="td"></div><div class="td"></div><div class="td"></div></div></div>';c.appendChild(d);c.scrollTop=c.scrollHeight;}}
function removeT(){{var e=document.getElementById('tp');if(e)e.remove();}}
</script>
</body>
</html>'''


# Main
json_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*_wineries.json')))
total = 0
errors = 0

for jf in json_files:
    pref = os.path.basename(jf).replace('data_', '').replace('_wineries.json', '')
    with open(jf, 'r', encoding='utf-8') as f:
        wineries = json.load(f)

    out_dir = os.path.join(BASE, 'wine', pref)
    os.makedirs(out_dir, exist_ok=True)

    for b in wineries:
        if not b.get('id'):
            continue
        try:
            html = generate_page(b, pref)
            with open(os.path.join(out_dir, f"{b['id']}.html"), 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
        except Exception as e:
            print(f"  ERROR: {pref}/{b.get('id','?')} — {e}")
            errors += 1

    print(f"  {pref}: {len(wineries)} pages")

print(f"\nDone: {total} pages generated, {errors} errors")

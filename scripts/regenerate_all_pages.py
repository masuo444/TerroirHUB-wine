#!/usr/bin/env python3
"""
全ワイナリーHTMLページを一括再生成。
SEO/AIO強化版: Winery JSON-LD, FAQPage, GeoCoordinates, パンくずリスト, 品種タグ, FAQ HTML
"""

import json
import glob
import os
import sys
import datetime

_TODAY = datetime.date.today().isoformat()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wine_filter import is_wine_item   # ワイン以外の楽天商品を表示しないための共通フィルタ

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# テンプレートからCSS取得
with open(os.path.join(BASE, 'template_wine.html'), 'r') as f:
    tmpl = f.read()
CSS = tmpl[tmpl.find('<style>') + 7:tmpl.find('</style>')]

# ── 楽天商品データ（fetch_rakuten_items.py が生成）
RAKUTEN_DB = {}
_rk_path = os.path.join(BASE, 'wine', 'rakuten_items.json')
if os.path.exists(_rk_path):
    try:
        RAKUTEN_DB = json.load(open(_rk_path, encoding='utf-8'))
    except Exception:
        RAKUTEN_DB = {}

import urllib.parse as _up
# ふるさと納税の返礼品がある県スラッグ（generate_furusato_page.py が出力）
FURUSATO_PREFS = set()
_fp = os.path.join(BASE, 'wine', 'furusato', '_prefs.json')
if os.path.exists(_fp):
    try:
        FURUSATO_PREFS = set(json.load(open(_fp, encoding='utf-8')))
    except Exception:
        FURUSATO_PREFS = set()

AMAZON_TAG = 'terroirhub-22'
def amazon_url(kw):
    return 'https://www.amazon.co.jp/s?k=' + _up.quote(kw or '') + '&i=food-beverage&tag=' + AMAZON_TAG

# ── 購入導線・STORY刷新のための追加CSS
EXTRA_CSS = '''
/* STORY 刷新（写真なし・タイポ中心） */
.story-redesign{background:var(--surface-warm);padding:76px 24px;}
.story-redesign .sec-inner{max-width:780px;margin:0 auto;text-align:center;}
.sr-title{font-family:'Zen Old Mincho',serif;font-size:48px;font-weight:700;color:var(--text);letter-spacing:.05em;line-height:1.45;margin:20px 0 0;}
.sr-rule{width:44px;height:2px;background:var(--accent);margin:30px auto 0;opacity:.8;}
.sr-lead{font-family:'Noto Serif JP',serif;font-weight:400;font-size:17px;line-height:1.95;color:var(--text-body);max-width:680px;margin:30px auto 0;}
.sr-meta{display:flex;justify-content:center;margin-top:56px;border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
.sm-item{flex:1;padding:30px 18px;border-left:1px solid var(--border);display:flex;flex-direction:column;align-items:center;gap:8px;}
.sm-item:first-child{border-left:none;}
.sm-num{font-family:'Cormorant Garamond',serif;font-size:52px;font-weight:300;color:var(--accent);line-height:.9;}
.sm-val{font-family:'Zen Old Mincho',serif;font-size:21px;color:var(--text);line-height:1.2;}
.sm-lbl{font-family:'DM Sans',sans-serif;font-size:10px;letter-spacing:.22em;color:var(--text-muted);}
.sm-sub{font-family:'Noto Serif JP',serif;font-size:12px;color:var(--text-muted);}
/* 代表銘柄カード（楽天画像・価格なし・楽天/Amazonボタン） */
.brands-grid .brand-card{display:flex;flex-direction:column;}
.brand-img-wrap{width:100%;aspect-ratio:1/1;background:#fff;border:1px solid var(--border);border-radius:4px;overflow:hidden;margin-bottom:16px;display:flex;align-items:center;justify-content:center;}
.brand-img{width:100%;height:100%;object-fit:contain;padding:14px;box-sizing:border-box;transition:transform .3s;}
.brand-card:hover .brand-img{transform:scale(1.04);}
.brand-img-placeholder{color:var(--text-muted);font-family:'DM Sans';font-size:13px;letter-spacing:.1em;}
.brand-noimg{background:linear-gradient(135deg,var(--surface-warm) 0%,#fff 100%);padding:24px;}
.brand-noimg-name{font-family:'Zen Old Mincho',serif;font-size:22px;color:var(--text);line-height:1.7;text-align:center;letter-spacing:.05em;}
.buy-btns{display:flex;gap:8px;margin-top:14px;}
.bb{flex:1;text-align:center;font-family:'DM Sans',sans-serif;font-size:12px;font-weight:500;padding:9px 0;border-radius:3px;text-decoration:none;letter-spacing:.03em;transition:all .2s;}
.bb-r{background:#BF0000;color:#fff;}.bb-r:hover{background:#a00000;}
.bb-a{background:#FF9900;color:#1a1a1a;}.bb-a:hover{background:#e88a00;}
/* このワイナリーのワイン（楽天商品グリッド） */
.buy-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}
.buy-card{background:var(--surface);border:1px solid var(--border);border-radius:8px;overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .22s,transform .22s;}
.buy-card:hover{box-shadow:0 8px 24px rgba(42,32,24,.10);transform:translateY(-2px);}
.buy-card-img{width:100%;aspect-ratio:1/1;object-fit:contain;background:#fff;padding:12px;box-sizing:border-box;}
.buy-card-body{padding:12px 14px 14px;display:flex;flex-direction:column;flex:1;}
.buy-card-name{font-size:13px;line-height:1.5;color:var(--text-body);display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:39px;margin-bottom:4px;}
.buy-note{font-size:11px;color:var(--text-muted);line-height:1.7;margin-top:20px;text-align:center;}
@media(max-width:900px){.buy-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:560px){.sr-title{font-size:32px;}.sr-lead{font-size:16px;}.sr-meta{flex-direction:column;}.sm-item{border-left:none;border-top:1px solid var(--border);padding:24px;}.sm-item:first-child{border-top:none;}.buy-grid{grid-template-columns:1fr 1fr;gap:12px;}}
/* 関連ワイナリー（同県） */
.related-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
.related-card{display:flex;flex-direction:column;gap:5px;background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px 18px;text-decoration:none;transition:box-shadow .2s,transform .2s;}
.related-card:hover{box-shadow:0 6px 18px rgba(42,32,24,.08);transform:translateY(-2px);}
.related-name{font-family:'Zen Old Mincho',serif;font-size:15px;color:var(--text);}
.related-meta{font-size:11.5px;color:var(--text-muted);}
@media(max-width:700px){.related-grid{grid-template-columns:1fr 1fr;}}
'''

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


def brand_name(brand):
    if isinstance(brand, dict):
        return str(brand.get('name', '')).strip()
    return str(brand).strip() if brand else ''


def brand_type(brand):
    if isinstance(brand, dict):
        return str(brand.get('type', '')).strip()
    return ''


def brand_specs(brand):
    if isinstance(brand, dict):
        return str(brand.get('specs', '')).strip()
    return ''


def brand_grapes(brand):
    if isinstance(brand, dict):
        return str(brand.get('grapes', '')).strip()
    return ''


def generate_page(b, pref_slug, siblings=None):
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

    # 楽天データ
    rk = RAKUTEN_DB.get(b.get('id'), {}) if b.get('id') else {}
    rk_brands = {x.get('name'): x for x in rk.get('brands', []) if isinstance(x, dict)}
    # ワイン判定を通った楽天商品のURL集合（銘柄画像の検証に使う）
    _valid_rk_urls = {it.get('url') for it in rk.get('items', [])
                      if isinstance(it, dict) and it.get('url') and is_wine_item(it.get('name', ''))}

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
    # 購入・ふるさと納税の意図に答えるFAQ（AIO/被引用強化）
    if any(is_wine_item(it.get('name', '')) for it in rk.get('items', []) if isinstance(it, dict)):
        faqs.append((f"{name}のワインはどこで購入できますか？",
                     f"{name}のワインは楽天市場やAmazonで取り扱いがあります。本ページの「このワイナリーのワイン」から各商品ページをご確認いただけます（在庫・価格は変動します）。"))
    if pref_slug in FURUSATO_PREFS:
        faqs.append((f"{name}のワインはふるさと納税で受け取れますか？",
                     f"{pref_name}のワイナリーの一部はふるさと納税の返礼品として日本ワインを提供しています。{pref_name}のふるさと納税特集ページで対象の返礼品をご確認ください。"))

    # ── JSON-LD ──
    winery_id = f"{page_url}#winery"
    local_biz = {
        "@type": ["LocalBusiness", "Winery"],
        "@id": winery_id,
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
    if source:
        local_biz["subjectOf"] = {
            "@type": "CreativeWork",
            "url": source
        }
    if gi:
        local_biz["additionalProperty"] = [
            {
                "@type": "PropertyValue",
                "name": "地理的表示",
                "value": gi
            }
        ]

    product_schemas = []
    offer_items = []
    for idx, br in enumerate(brands[:6], start=1):
        br_name = brand_name(br)
        if not br_name:
            continue
        product_id = f"{page_url}#wine-{idx}"
        product = {
            "@type": "Product",
            "@id": product_id,
            "name": br_name,
            "category": brand_type(br) or "日本ワイン",
            "brand": {
                "@type": "Brand",
                "name": brand or name
            },
            "manufacturer": {
                "@id": winery_id
            }
        }
        specs = brand_specs(br)
        if specs:
            product["description"] = specs[:300]
        br_grapes = brand_grapes(br)
        if br_grapes:
            product["material"] = br_grapes
        product_schemas.append(product)
        offer_items.append({
            "@type": "Offer",
            "itemOffered": {
                "@id": product_id
            }
        })

    if offer_items:
        local_biz["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": f"{name}の代表銘柄",
            "itemListElement": offer_items
        }

    webpage_schema = {
        "@type": "WebPage",
        "@id": f"{page_url}#webpage",
        "url": page_url,
        "name": f"{name} - {pref_name}のワイナリー",
        "description": meta_desc,
        "dateModified": _TODAY,
        "inLanguage": "ja",
        "isPartOf": {
            "@type": "WebSite",
            "@id": f"https://{DOMAIN}/#website",
            "name": "Terroir HUB WINE",
            "url": f"https://{DOMAIN}/"
        },
        "mainEntity": {
            "@id": winery_id
        }
    }

    breadcrumb_schema = {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Terroir HUB WINE", "item": f"https://{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": pref_name, "item": f"https://{DOMAIN}/wine/{pref_slug}/"},
            {"@type": "ListItem", "position": 3, "name": name, "item": page_url}
        ]
    }

    graph = [webpage_schema, local_biz, breadcrumb_schema] + product_schemas

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
    _used_brand_imgs = set()   # 同じ画像を複数銘柄で使い回さない（嘘の画像防止）
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
            if 'ロゼ' in br_type: style_class = 'rose'
            elif 'スパークリング' in br_type or '泡' in br_type: style_class = 'sparkling'
            elif '赤' in br_type and '白' in br_type: style_class = 'red'   # 赤・白セットは赤系で統一（白誤判定を防止）
            elif '白' in br_type: style_class = 'white'
            elif '甘口' in br_type: style_class = 'sweet'
            wine_badge_html = f'<div class="wine-badge {style_class}">{esc(br_type)}</div>'

        # 楽天画像カード（価格なし・楽天/Amazon両ボタン）。画像なしは明朝で銘柄名表示
        # 銘柄画像は「ワイン判定を通った検証済み商品」と一致するURLのみ採用（誤マッチ画像を出さない）
        rb = rk_brands.get(br_name) or {}
        rimg, rurl = rb.get('image', ''), rb.get('url', '')
        # 検証: match(マッチ商品名)があればワイン判定で、無い旧データはitems一致で担保
        if rimg:
            _m = rb.get('match')
            _ok = is_wine_item(_m) if _m else (rurl in _valid_rk_urls)
            if not _ok or rimg in _used_brand_imgs:   # 無効 or 画像重複 → 名前カードにフォールバック
                rimg, rurl = '', ''
        if rimg:
            _used_brand_imgs.add(rimg)
        if rimg:
            imgwrap = f'<div class="brand-img-wrap"><img class="brand-img" src="{esc(rimg)}" alt="{esc(br_name)}" loading="lazy"></div>'
        else:
            imgwrap = f'<div class="brand-img-wrap brand-noimg"><span class="brand-noimg-name">{esc(br_name)}</span></div>'
        btns = '<div class="buy-btns">'
        if rurl:
            btns += f'<a class="bb bb-r" href="{esc(rurl)}" target="_blank" rel="nofollow sponsored noopener">楽天で見る</a>'
        btns += f'<a class="bb bb-a" href="{esc(amazon_url(br_name))}" target="_blank" rel="nofollow sponsored noopener">Amazon</a></div>'

        brands_html += f'''
    <div class="brand-card">
      {imgwrap}
      {wine_badge_html}
      {f'<div class="grape-tag">{esc(br_grapes)}</div>' if br_grapes else ''}
      <h3 class="brand-name">{esc(br_name)}</h3>
      <p class="brand-type">{esc(br_type or specs_short)}</p>
      {f'<p class="brand-desc">{esc(br_specs)}</p>' if br_specs else ''}
      {btns}
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

    # ── Story section（写真なし・タイポ中心の刷新版） ──
    story_section = ''
    if desc or founded or area:
        sm = ''
        if years:
            sm += f'<div class="sm-item"><span class="sm-num">{years}</span><span class="sm-lbl">YEARS</span><span class="sm-sub">年の歴史</span></div>'
        if founded_era or founded:
            sub = f'{esc(founded)}年創業' if founded else '創業'
            sm += f'<div class="sm-item"><span class="sm-val">{esc(founded_era or founded)}</span><span class="sm-lbl">FOUNDED</span><span class="sm-sub">{sub}</span></div>'
        if area:
            sm += f'<div class="sm-item"><span class="sm-val">{esc(area)}</span><span class="sm-lbl">TERROIR</span><span class="sm-sub">産地</span></div>'
        story_section = f'''
<section class="section story-redesign">
  <div class="sec-inner">
    <label class="sec-label">STORY</label>
    <h2 class="sr-title">{esc(name)}の物語</h2>
    <div class="sr-rule"></div>
    {f'<p class="sr-lead">{esc(desc)}</p>' if desc else ''}
    {f'<div class="sr-meta">{sm}</div>' if sm else ''}
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

    # ── Shop section（このワイナリーのワイン・楽天商品グリッド） ──
    shop_section = ''
    rk_items = [it for it in rk.get('items', []) if isinstance(it, dict) and it.get('image') and is_wine_item(it.get('name', ''))]
    if rk_items:
        cards = ''
        for it in rk_items[:6]:
            iname, iimg, iurl = it.get('name', ''), it.get('image', ''), it.get('url', '')
            cards += f'''
      <div class="buy-card">
        <a href="{esc(iurl)}" target="_blank" rel="nofollow sponsored noopener"><img class="buy-card-img" src="{esc(iimg)}" alt="{esc(iname)}" loading="lazy"></a>
        <div class="buy-card-body">
          <div class="buy-card-name">{esc(iname)}</div>
          <div class="buy-btns">
            <a class="bb bb-r" href="{esc(iurl)}" target="_blank" rel="nofollow sponsored noopener">楽天</a>
            <a class="bb bb-a" href="{esc(amazon_url(iname))}" target="_blank" rel="nofollow sponsored noopener">Amazon</a>
          </div>
        </div>
      </div>'''
        shop_section = f'''
<section class="section buy-section" style="background:var(--surface-warm);">
  <div class="sec-inner">
    <label class="sec-label">BUY</label>
    <h2 class="sec-title">このワイナリーのワイン</h2>
    <div class="sec-divider"></div>
    <div class="buy-grid">{cards}
    </div>
    <p class="buy-note">※ 商品・価格は楽天市場の検索結果です（時点により変動）。Terroir HUB はワインの販売を行っていません。<br>価格・在庫・送料は各ストアでご確認ください。20歳未満の飲酒は法律で禁止されています。</p>
  </div>
</section>'''

    # ── 同じ県の他のワイナリー（ページ毎に内容が変わる独自セクション＋内部リンク） ──
    related_html = ''
    if siblings:
        others = [s for s in siblings if isinstance(s, dict) and s.get('id') and s.get('id') != b.get('id') and s.get('name')]
        # 同じ主要品種を優先して並べ、最大6件
        mg = b.get('main_grape')
        others.sort(key=lambda s: (0 if mg and s.get('main_grape') == mg else 1, s.get('name', '')))
        cards = ''
        for s in others[:6]:
            s_area = esc(s.get('area', '') or pref_name)
            s_grapes = '・'.join((s.get('grapes') or [])[:3])
            cards += f'''
      <a class="related-card" href="/wine/{pref_slug}/{esc(s['id'])}.html">
        <span class="related-name">{esc(s['name'])}</span>
        <span class="related-meta">{s_area}{f' ｜ {esc(s_grapes)}' if s_grapes else ''}</span>
      </a>'''
        if cards:
            related_html = f'''
<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <label class="sec-label">MORE WINERIES</label>
    <h2 class="sec-title">{esc(pref_name)}の他のワイナリー</h2>
    <div class="sec-divider"></div>
    <p style="font-size:13px;color:var(--text-muted);margin-bottom:20px;">{esc(pref_name)}には他にも個性豊かなワイナリーがあります。あわせてご覧ください。</p>
    <div class="related-grid">{cards}
    </div>
    <div style="margin-top:22px;"><a href="/wine/{pref_slug}/" style="font-size:13px;color:var(--accent);text-decoration:none;font-weight:500;">{esc(pref_name)}のワイナリー一覧をすべて見る →</a></div>
  </div>
</section>'''

    # ── ふるさと納税CTA（その県の特集ページへ内部リンク。返礼品がある県のみ） ──
    furusato_cta = ''
    if pref_slug in FURUSATO_PREFS:
        furusato_cta = f'''
<section class="section" style="background:var(--bg);">
  <div class="sec-inner" style="text-align:center;">
    <label class="sec-label">FURUSATO TAX</label>
    <h2 class="sec-title">ふるさと納税で{esc(name)}を応援</h2>
    <div class="sec-divider" style="margin-left:auto;margin-right:auto;"></div>
    <p style="font-size:14px;color:var(--text-body);max-width:560px;margin:0 auto 20px;line-height:1.9;">{esc(pref_name)}のワインは、ふるさと納税の返礼品としても受け取れます。実質自己負担2,000円で、寄付しながら産地と蔵を直接応援できます。</p>
    <a href="/wine/furusato/{pref_slug}.html" style="display:inline-block;background:#722F37;color:#fff;text-decoration:none;font-size:14px;font-weight:600;padding:13px 30px;border-radius:26px;">{esc(pref_name)}のワインふるさと納税を見る →</a>
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

    # ── 地図（lat/lngがあればOpenStreetMap埋め込み・キー不要） ──
    if lat and lng:
        try:
            _la, _ln = float(lat), float(lng)
            _bbox = f"{_ln-0.012}%2C{_la-0.008}%2C{_ln+0.012}%2C{_la+0.008}"
            map_box = (f'<div style="border:1px solid var(--border);border-radius:8px;overflow:hidden;">'
                       f'<iframe title="{esc(name)}の地図" width="100%" height="280" frameborder="0" scrolling="no" loading="lazy" '
                       f'style="display:block;border:0;" src="https://www.openstreetmap.org/export/embed.html?bbox={_bbox}&amp;layer=mapnik&amp;marker={_la}%2C{_ln}"></iframe>'
                       f'<div style="padding:8px 12px;background:var(--surface-warm);font-size:12px;text-align:right;">'
                       f'<a href="https://www.google.com/maps/search/?api=1&amp;query={_la}%2C{_ln}" target="_blank" rel="noopener" style="color:var(--accent);text-decoration:none;">Googleマップで開く →</a></div></div>')
        except (ValueError, TypeError):
            map_box = ''
    else:
        map_box = ''
    if not map_box:
        map_box = (f'<div style="background:var(--surface-warm);border:1px solid var(--border);border-radius:8px;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:240px;gap:8px;">'
                   f'<span style="font-size:28px;">📍</span>'
                   f'<div style="font-family:\'Zen Old Mincho\',serif;font-size:16px;color:var(--text);">{esc(name)}</div>'
                   f'<div style="font-size:13px;color:var(--text-muted);">{esc(pref_name)}{(" " + esc(area)) if area else ""}</div></div>')

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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(name)} — {esc(pref_name)}のワイナリー | Terroir HUB WINE</title>
<meta name="description" content="{esc(meta_desc)}">
<meta property="og:title" content="{esc(name)} — {esc(pref_name)}のワイナリー | Terroir HUB WINE">
<meta property="og:description" content="{og_desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{page_url}">
<meta property="og:image" content="https://{DOMAIN}/img/hero-top.png">
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
<link rel="preconnect" href="https://sake.terroirhub.com">
<script>window.THUB_CONFIG={{genre:'wine',brandColor:'#722F37',brandColor2:'#A86B74',basePath:'/wine',siteName:'Terroir HUB WINE',apiBase:'https://sake.terroirhub.com'}};</script>
<script src="https://sake.terroirhub.com/shared/cookie-storage.js" defer></script>
<script src="https://sake.terroirhub.com/shared/auth.js" defer></script>
<style>
{CSS}
{EXTRA_CSS}
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

{shop_section}
{furusato_cta}
{related_html}

<section class="section" style="background:var(--bg);">
  <div class="sec-inner">
    <label class="sec-label">INFORMATION</label>
    <h2 class="sec-title">基本情報</h2>
    <div class="sec-divider"></div>
    <div class="story-grid" style="gap:32px;">
      <div style="display:flex;flex-direction:column;gap:22px;">
        {visit_items}
      </div>
      <div>{map_box}</div>
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
        <div class="p-av"><img src="/img/sakura-fullbody.png" alt="サクラ" style="width:100%;height:100%;object-fit:cover;border-radius:50%;"></div>
        <div>
          <div class="p-title">サクラ <span id="p-plan-tag" style="font-size:10px;background:rgba(255,255,255,0.25);border-radius:6px;padding:1px 7px;font-weight:400;">Free</span></div>
          <div class="p-status"><div class="p-dot"></div><span>AIソムリエ · オンライン</span></div>
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
    var headers={{'Content-Type':'application/json'}};
    try{{
      if(window.thubAuth&&window.thubAuth.supabase){{
        var sess=await window.thubAuth.supabase.auth.getSession();
        var tok=sess&&sess.data&&sess.data.session&&sess.data.session.access_token;
        if(tok)headers['Authorization']='Bearer '+tok;
      }}
    }}catch(e){{}}
    var res=await fetch('https://sake.terroirhub.com/api/sakura',{{method:'POST',headers:headers,body:JSON.stringify({{question:q,history:chatHistory.slice(-10),context:ctx}})}});
    if(res.status===401){{
      removeT();
      addMsg('butler','サクラAIをご利用いただくにはログインが必要です。\n\n無料アカウントで今すぐ始められます 🌸');
      setTimeout(function(){{if(typeof showAuth==='function')showAuth('login');}},800);
      renderSugs();return;
    }}
    if(res.status===402){{
      removeT();
      addMsg('butler','本日のご利用上限に達しました。明日またお気軽にどうぞ 🌸\n\nプレミアムプランでは無制限でご利用いただけます。');
      renderSugs();return;
    }}
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
import sys as _sys
_test = _sys.argv[_sys.argv.index('--test') + 1] if '--test' in _sys.argv else None
_pref = _sys.argv[_sys.argv.index('--pref') + 1] if '--pref' in _sys.argv else None

json_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*_wineries.json')))
total = 0
errors = 0

for jf in json_files:
    pref = os.path.basename(jf).replace('data_', '').replace('_wineries.json', '')
    if _pref and pref != _pref:
        continue
    with open(jf, 'r', encoding='utf-8') as f:
        wineries = json.load(f)

    out_dir = os.path.join(BASE, 'wine', pref)
    os.makedirs(out_dir, exist_ok=True)

    for b in wineries:
        if not b.get('id'):
            continue
        if _test and b.get('id') != _test:
            continue
        try:
            html = '\n'.join(line.rstrip() for line in generate_page(b, pref, siblings=wineries).splitlines()) + '\n'
            with open(os.path.join(out_dir, f"{b['id']}.html"), 'w', encoding='utf-8') as f:
                f.write(html)
            total += 1
        except Exception as e:
            print(f"  ERROR: {pref}/{b.get('id','?')} — {e}")
            errors += 1

    if not _test:
        print(f"  {pref}: {len(wineries)} pages")

print(f"\nDone: {total} pages generated, {errors} errors")

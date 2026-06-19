#!/usr/bin/env python3
"""
ふるさと納税ページ生成（SEO重視の3層構造）。
  1) ハブ: wine/furusato/index.html （全国・ライブ検索/県フィルタ）
  2) 県別: wine/furusato/{pref}.html （「山梨 ワイン ふるさと納税」等を県ごとに獲る）
既存 rakuten_items.json から【ふるさと納税】返礼品を抽出。各ページに JSON-LD(CollectionPage/
ItemList/FAQPage/BreadcrumbList)・meta/OG。県別ページ一覧は wine/furusato/_prefs.json に出力し、
蔵ページ(regenerate_all_pages.py)からの内部リンクに使う。
"""
import json, glob, os, sys, html, re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wine_filter import is_wine_item

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "wine.terroirhub.com"
OUTDIR = os.path.join(BASE, "wine", "furusato")

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
    'kagoshima':'鹿児島県','okinawa':'沖縄県',
}
PREF_ORDER = list(PREF_NAMES.keys())

# 主要産地の固有リード文（薄いコンテンツ回避・SEO）。未定義の県はデータから自動生成。
PREF_LEAD = {
    'yamanashi': "日本ワイン発祥の地・山梨県。甲州・マスカット・ベーリーAを筆頭に、勝沼を中心とした日本最大級のワイン産地です。GI山梨認定。ふるさと納税では甲州ワインや赤ワインの返礼品が充実しています。",
    'nagano': "標高の高い高原産地・長野県。塩尻のメルロー、東御・小諸のシャルドネなど欧州系品種が高品質に育ちます。GI長野認定。ふるさと納税で長野のワイナリーを応援できます。",
    'hokkaido': "冷涼な気候が生むピノ・ノワールやケルナーで世界的評価を高める北海道。余市・空知が主産地でGI北海道認定。ふるさと納税では自然派・小規模ワイナリーの返礼品も見つかります。",
    'yamagata': "上山・南陽・高畠を中心に多彩なワイナリーが集まる山形県。GI山形認定。デラウェアから本格欧州品種まで、ふるさと納税返礼品の幅が広い産地です。",
    'iwate': "ヤマ・ソービニオンなど寒冷地品種に強い岩手県。エーデルワインやくずまきワインが有名で、ふるさと納税の返礼品も人気です。",
    'osaka': "かつて日本一のぶどう産地だった大阪府。柏原・羽曳野を中心に歴史ある醸造所が点在し、GI大阪認定。ふるさと納税で大阪ワインを楽しめます。",
    'niigata': "砂丘地の岩の原葡萄園（川上善兵衛の地）で知られる新潟県。雪国の気候を活かしたワイン造りが進み、ふるさと納税返礼品も増えています。",
    'tochigi': "ココ・ファーム・ワイナリーをはじめ個性的な造り手が集まる栃木県。ふるさと納税で足利・那須のワインを応援できます。",
    'okayama': "マスカット・オブ・アレキサンドリアなどぶどう王国・岡山県。温暖な気候のワイナリーが揃い、ふるさと納税返礼品も多彩です。",
}


def esc(s):
    return html.escape(str(s or ""), quote=True)


def load_wineries():
    m = {}
    for jf in glob.glob(os.path.join(BASE, "data", "data_*_wineries.json")):
        pref = os.path.basename(jf).replace("data_", "").replace("_wineries.json", "")
        for b in json.load(open(jf, encoding="utf-8")):
            if b.get("id"):
                m[b["id"]] = {"name": b.get("name", ""), "pref": pref, "id": b["id"]}
    return m


def collect():
    rk = json.load(open(os.path.join(BASE, "wine", "rakuten_items.json"), encoding="utf-8"))
    wineries = load_wineries()
    by_pref, seen = {}, set()
    for wid, g in rk.items():
        w = wineries.get(wid)
        if not w:
            continue
        for it in g.get("items", []):
            nm = it.get("name", "")
            if not it.get("image") or "ふるさと納税" not in nm or not is_wine_item(nm):
                continue
            key = it.get("url") or nm
            if key in seen:
                continue
            seen.add(key)
            by_pref.setdefault(w["pref"], []).append({**it, "winery": w["name"], "winery_id": wid})
    return by_pref


def clean_name(nm):
    s = re.sub(r'^[【\[]?\s*ふるさと納税\s*[】\]]?\s*', '', nm)
    s = re.sub(r'\s*(御祝|御礼|母の日|父の日|敬老の日|御中元|御歳暮|御年賀|内祝|出産内祝|誕生日祝|結婚祝|退職祝|卒業祝|還暦祝|古希祝|傘寿祝|喜寿祝|米寿祝|開店祝|感謝|贈り物|プレゼント|ギフト|人気|寿|壽|御供|仏事).*$', '', s)
    return s.strip() or nm


def card_html(it):
    nm = clean_name(it["name"])
    kw = esc((nm + " " + it["winery"]).lower())
    return f'''
        <article class="fcard" data-kw="{kw}">
          <a class="fcard-imgwrap" href="{esc(it['url'])}" target="_blank" rel="nofollow sponsored noopener">
            <img class="fcard-img" src="{esc(it['image'])}" alt="{esc(nm)}" loading="lazy">
            <span class="fcard-badge">ふるさと納税</span>
          </a>
          <div class="fcard-body">
            <div class="fcard-winery">{esc(it['winery'])}</div>
            <h3 class="fcard-name" title="{esc(it['name'])}">{esc(nm)}</h3>
            <a class="fcard-btn" href="{esc(it['url'])}" target="_blank" rel="nofollow sponsored noopener">楽天ふるさと納税で見る</a>
          </div>
        </article>'''


FAQ_COMMON = [
    ("ふるさと納税でワインを選ぶメリットは？",
     "実質自己負担2,000円で、寄付額に応じた返礼品として日本ワインを受け取れます。さらに地域の小規模ワイナリーを直接応援できるのが魅力です。控除上限額は年収・家族構成で変わるため、各ふるさと納税サイトのシミュレーターで確認してから寄付しましょう。"),
    ("掲載のワインはどこで寄付できますか？",
     "各返礼品の「楽天ふるさと納税で見る」ボタンから、楽天ふるさと納税の該当ページに移動して寄付できます。楽天ポイントを貯めている方は楽天経由が便利です。"),
    ("控除を受けるには何が必要ですか？",
     "確定申告、またはワンストップ特例制度の申請が必要です。ワンストップ特例は、確定申告が不要な給与所得者で寄付先が年間5自治体以内の場合に利用でき、寄付ごとに申請書を提出します。"),
    ("返礼品の内容や寄付額は変わりますか？",
     "返礼品・寄付額・在庫・取扱自治体は時期により変動します。本ページは楽天ふるさと納税の情報をもとにしており、最新の内容は各返礼品ページでご確認ください。"),
]

CSS = """
*{margin:0;padding:0;box-sizing:border-box;}
html{scroll-behavior:smooth;overflow-x:hidden;}
body{background:#fdfaf8;color:#222;font-family:'Noto Sans JP',sans-serif;font-size:16px;line-height:1.8;-webkit-font-smoothing:antialiased;}
a{color:inherit;}
.nav{position:fixed;top:0;left:0;right:0;z-index:100;background:rgba(255,255,255,0.95);backdrop-filter:blur(20px);border-bottom:1px solid rgba(0,0,0,0.06);}
.nav-top{display:flex;align-items:center;height:54px;padding:0 28px;max-width:1280px;margin:0 auto;}
.nav-logo{font-family:'Shippori Mincho',serif;font-size:18px;font-weight:700;color:#1a1a1a;text-decoration:none;letter-spacing:0.04em;}
.nav-back{font-size:13px;color:#722F37;text-decoration:none;margin-left:auto;padding:6px 16px;border:1px solid rgba(114,47,55,0.3);border-radius:20px;transition:all 0.2s;}
.nav-back:hover{background:#722F37;color:#fff;}
.crumb{max-width:1180px;margin:0 auto;padding:10px 24px 0;font-size:12px;color:#9a8a8d;}
.crumb a{color:#9a8a8d;text-decoration:none;}.crumb a:hover{color:#722F37;}
.hero{margin-top:54px;position:relative;background:linear-gradient(135deg,#3d0c12 0%,#722F37 55%,#9c4750 100%);color:#fff;padding:60px 28px 52px;overflow:hidden;}
.hero::after{content:"";position:absolute;inset:0;background:radial-gradient(circle at 80% 20%,rgba(255,255,255,0.12),transparent 45%);}
.hero-inner{max-width:960px;margin:0 auto;position:relative;z-index:1;}
.hero-tag{display:inline-block;font-size:12px;letter-spacing:0.16em;background:rgba(255,255,255,0.15);border:1px solid rgba(255,255,255,0.32);border-radius:20px;padding:5px 16px;margin-bottom:16px;}
.hero h1{font-family:'Shippori Mincho',serif;font-size:clamp(26px,5vw,44px);font-weight:700;letter-spacing:0.03em;line-height:1.4;margin-bottom:16px;}
.hero p{font-size:clamp(15px,2vw,17px);line-height:2;opacity:0.94;max-width:700px;}
.stats{display:flex;gap:14px;margin-top:28px;flex-wrap:wrap;}
.stat{background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.22);border-radius:12px;padding:13px 22px;min-width:108px;}
.stat-n{font-family:'Shippori Mincho',serif;font-size:28px;font-weight:700;line-height:1;}
.stat-l{font-size:12px;opacity:0.85;margin-top:6px;letter-spacing:0.06em;}
.steps{max-width:960px;margin:0 auto;padding:40px 28px 4px;}
.steps-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;}
.step{background:#fff;border:1px solid #f0e2e2;border-radius:14px;padding:22px 20px;}
.step-n{font-family:'Shippori Mincho',serif;font-size:13px;color:#fff;background:#722F37;width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-bottom:11px;}
.step h3{font-size:15px;color:#2a0a0e;margin-bottom:6px;}
.step p{font-size:13.5px;color:#666;line-height:1.75;}
.simbar{max-width:1180px;margin:18px auto 0;padding:0 24px;}
.simcard{background:linear-gradient(135deg,#fff,#fbf3f3);border:1px solid #f0dede;border-radius:14px;padding:20px 24px;display:flex;align-items:center;gap:18px;flex-wrap:wrap;}
.simcard p{font-size:14px;color:#5a4a4d;flex:1;min-width:240px;}
.simcard a{background:#722F37;color:#fff;text-decoration:none;font-size:13.5px;font-weight:600;padding:11px 22px;border-radius:24px;white-space:nowrap;}
.simcard a:hover{background:#561f26;}
.toolbar{position:sticky;top:54px;z-index:90;background:rgba(253,250,248,0.96);backdrop-filter:blur(12px);border-bottom:1px solid #efe2e2;padding:14px 0;margin-top:30px;}
.toolbar-inner{max-width:1180px;margin:0 auto;padding:0 24px;}
.search-box{width:100%;max-width:440px;padding:11px 18px;border:1px solid #e2cfcf;border-radius:24px;font-size:14px;font-family:inherit;outline:none;background:#fff;}
.search-box:focus{border-color:#722F37;}
.pills{display:flex;gap:8px;overflow-x:auto;margin-top:12px;padding-bottom:4px;-webkit-overflow-scrolling:touch;}
.pill{flex:0 0 auto;font-family:inherit;font-size:13px;color:#722F37;background:#fff;border:1px solid #e2cfcf;border-radius:20px;padding:7px 14px;cursor:pointer;transition:all .18s;white-space:nowrap;text-decoration:none;}
.pill:hover{background:#fbeeee;}
.pill.active{background:#722F37;color:#fff;border-color:#722F37;}
.pill-n{font-size:11px;opacity:0.7;margin-left:5px;}
.content{max-width:1180px;margin:0 auto;padding:30px 24px 60px;}
.lead{max-width:960px;margin:0 auto;padding:26px 24px 0;font-size:15px;color:#4a4044;line-height:2;}
.pref-block{margin-bottom:44px;scroll-margin-top:150px;}
.pref-title{font-family:'Shippori Mincho',serif;font-size:21px;font-weight:600;color:#2a0a0e;margin-bottom:16px;padding-bottom:9px;border-bottom:2px solid #722F37;display:flex;align-items:baseline;gap:10px;flex-wrap:wrap;}
.pref-count{font-size:13px;font-weight:400;color:#a8808a;}
.pref-more{margin-left:auto;font-size:13px;color:#722F37;text-decoration:none;font-family:'Noto Sans JP',sans-serif;font-weight:500;}
.pref-more:hover{text-decoration:underline;}
.fgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(218px,1fr));gap:18px;}
.fcard{background:#fff;border:1px solid #f0e2e2;border-radius:12px;overflow:hidden;display:flex;flex-direction:column;transition:box-shadow .22s,transform .22s;}
.fcard:hover{box-shadow:0 10px 28px rgba(80,20,30,.12);transform:translateY(-3px);}
.fcard-imgwrap{position:relative;display:block;aspect-ratio:1/1;background:#fff;}
.fcard-img{width:100%;height:100%;object-fit:contain;padding:14px;box-sizing:border-box;}
.fcard-badge{position:absolute;top:10px;left:10px;background:#722F37;color:#fff;font-size:10.5px;letter-spacing:.05em;padding:4px 9px;border-radius:4px;}
.fcard-body{padding:13px 15px 16px;display:flex;flex-direction:column;flex:1;}
.fcard-winery{font-size:11.5px;color:#9a7e84;margin-bottom:5px;}
.fcard-name{font-size:13.5px;line-height:1.55;color:#33272a;font-weight:500;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:13px;flex:1;}
.fcard-btn{display:block;text-align:center;background:#BF0000;color:#fff;font-size:12.5px;font-weight:600;padding:10px 0;border-radius:5px;text-decoration:none;transition:background .2s;margin-top:auto;}
.fcard-btn:hover{background:#a00000;}
.noresult{text-align:center;color:#999;padding:60px 0;font-size:15px;display:none;}
.otherpref{max-width:1180px;margin:0 auto;padding:8px 24px 0;}
.otherpref h2{font-family:'Shippori Mincho',serif;font-size:18px;color:#2a0a0e;margin-bottom:14px;}
.otherpref-list{display:flex;flex-wrap:wrap;gap:8px;}
.otherpref-list a{font-size:13px;color:#722F37;background:#fff;border:1px solid #e2cfcf;border-radius:20px;padding:7px 14px;text-decoration:none;}
.otherpref-list a:hover{background:#722F37;color:#fff;}
.faqsec{max-width:960px;margin:8px auto 0;padding:10px 24px 0;}
.faqsec h2{font-family:'Shippori Mincho',serif;font-size:22px;color:#2a0a0e;margin-bottom:18px;}
.faq{background:#fff;border:1px solid #f0e2e2;border-radius:14px;padding:28px;}
.faq-item{margin-bottom:20px;padding-bottom:20px;border-bottom:1px solid #f3e6e6;}
.faq-item:last-child{margin-bottom:0;padding-bottom:0;border-bottom:none;}
.faq-item dt{font-weight:600;color:#2a0a0e;margin-bottom:8px;font-size:15px;}
.faq-item dd{font-size:14px;color:#5a5a5a;line-height:1.85;margin:0;}
.note{max-width:960px;margin:22px auto 0;padding:0 24px;font-size:11.5px;color:#a99;line-height:1.8;}
.footer{background:#1a0508;padding:46px 24px 30px;color:rgba(255,255,255,0.5);font-size:13px;text-align:center;margin-top:52px;}
.footer-logo{font-family:'Shippori Mincho',serif;font-size:24px;color:#fff;font-weight:600;margin-bottom:16px;}
.footer-logo .accent{color:#722F37;}
.footer-nav{display:flex;justify-content:center;flex-wrap:wrap;margin-bottom:22px;padding-top:20px;border-top:1px solid rgba(255,255,255,0.1);}
.footer-nav a{color:rgba(255,255,255,0.6);text-decoration:none;font-size:13px;padding:0 16px;border-right:1px solid rgba(255,255,255,0.2);line-height:1;}
.footer-nav a:last-child{border-right:none;}
.footer-copy{font-size:11px;color:rgba(255,255,255,0.3);}
@media(max-width:700px){.steps-grid{grid-template-columns:1fr;}.fgrid{grid-template-columns:repeat(2,1fr);gap:12px;}}
"""

HEAD = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="https://wine.terroirhub.com/img/hero.jpg">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Shippori+Mincho:wght@400;500;600;700&family=Noto+Sans+JP:wght@300;400;500;700&display=swap" rel="stylesheet">
<script type="application/ld+json">
{jsonld}
</script>
"""

HEAD_TAIL = "<style>\n" + CSS + """</style>
</head>
<body>
<nav class="nav">
  <div class="nav-top">
    <a href="/" class="nav-logo">Terroir HUB <span style="color:#722F37">WINE</span></a>
    <a href="/wine/furusato/" class="nav-back">&#8592; ふるさと納税トップ</a>
  </div>
</nav>
"""

FOOTER = """
<footer class="footer">
  <div class="footer-logo">Terroir HUB <span class="accent">WINE</span></div>
  <nav class="footer-nav">
    <a href="/">ホーム</a>
    <a href="/wine/search/">ワイナリー検索</a>
    <a href="/wine/furusato/">ふるさと納税</a>
    <a href="/wine/guide/">ワインガイド</a>
    <a href="/privacy.html">プライバシー</a>
    <a href="/terms.html">利用規約</a>
  </nav>
  <p class="footer-copy">&copy; 2026 合同会社FOMUS — Terroir HUB WINE</p>
</footer>
</body>
</html>
"""

NOTE = ('<p class="note">※ 返礼品・寄付額・在庫・取扱自治体は時期により変動します。本ページは楽天ふるさと納税の情報をもとに構成しており、'
        '最新の内容・正確な控除上限は各返礼品ページおよび各自治体・ふるさと納税サイトでご確認ください。控除には確定申告またはワンストップ特例申請が必要です。'
        '20歳未満の飲酒・お酒の購入は法律で禁止されています。Terroir HUB はワインの販売を行っていません。</p>')


def jsonld_for(name, desc, url, crumb, items, faqs):
    item_list = [{"@type": "ListItem", "position": i + 1, "name": clean_name(it["name"]),
                  "image": it["image"], "url": it["url"]} for i, it in enumerate(items[:30])]
    g = [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": c[0], "item": c[1]} for i, c in enumerate(crumb)]},
        {"@type": "CollectionPage", "name": name, "description": desc, "url": url,
         "isPartOf": {"@type": "WebSite", "name": "Terroir HUB WINE", "url": f"https://{DOMAIN}/"}},
        {"@type": "ItemList", "name": name, "numberOfItems": len(items), "itemListElement": item_list},
        {"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": g}, ensure_ascii=False, indent=1)


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def build_hub(by_pref):
    ordered = [(p, by_pref[p]) for p in PREF_ORDER if p in by_pref]
    total = sum(len(v) for v in by_pref.values())
    n_pref = len(by_pref)
    n_winery = len({c["winery_id"] for v in by_pref.values() for c in v})

    pills = f'<button class="pill active" data-pref="all">すべて<span class="pill-n">{total}</span></button>'
    pills += "".join(
        f'<button class="pill" data-pref="{p}">{esc(PREF_NAMES[p])}<span class="pill-n">{len(v)}</span></button>'
        for p, v in ordered)

    sections = ""
    for p, items in ordered:
        cards = "".join(card_html(it) for it in items[:12])
        more = (f'<a class="pref-more" href="/wine/furusato/{p}.html">{esc(PREF_NAMES[p])}の返礼品をすべて見る ({len(items)}件) →</a>'
                if len(items) > 12 else
                f'<a class="pref-more" href="/wine/furusato/{p}.html">{esc(PREF_NAMES[p])}の特集ページ →</a>')
        sections += f'''
      <section class="pref-block" data-pref="{p}" id="pref-{p}">
        <h2 class="pref-title">{esc(PREF_NAMES[p])}のワインふるさと納税 <span class="pref-count">{len(items)}件</span>{more}</h2>
        <div class="fgrid">{cards}
        </div>
      </section>'''

    faqs = [("日本ワインのふるさと納税でおすすめは？",
             f"Terroir HUB WINEでは全国{n_pref}都道府県・{n_winery}ワイナリーの日本ワインふるさと納税返礼品{total}件を産地別に掲載。山梨・長野・北海道・山形など主要産地から、甲州・メルロー・シャルドネなど多彩な日本ワインを寄付で応援しながら受け取れます。")] + FAQ_COMMON
    desc = (f"日本ワインのふるさと納税返礼品を産地別に{total}件掲載。全国{n_winery}ワイナリーの甲州・メルロー・シャルドネを、"
            "寄付で蔵を応援しながら受け取れます。楽天ふるさと納税対応。")
    title = "日本ワインのふるさと納税 返礼品 | 全国の蔵を応援 — Terroir HUB WINE"
    url = f"https://{DOMAIN}/wine/furusato/"
    crumb = [("Terroir HUB WINE", f"https://{DOMAIN}/"), ("ふるさと納税", url)]
    all_items = [it for _, v in ordered for it in v]
    jsonld = jsonld_for("日本ワインのふるさと納税 返礼品", desc, url, crumb, all_items, faqs)

    head = HEAD.format(title=esc(title), desc=esc(desc), ogtitle=esc("日本ワインのふるさと納税 返礼品｜全国の蔵を応援"),
                       canonical=url, jsonld=jsonld) + HEAD_TAIL
    faq_html = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(a)}</dd></div>' for q, a in faqs)
    body = f'''
<header class="hero">
  <div class="hero-inner">
    <div class="hero-tag">FURUSATO TAX — ふるさと納税で日本ワインを</div>
    <h1>寄付して、日本のワイナリーを応援しよう。</h1>
    <p>ふるさと納税の返礼品として日本ワインを受け取りながら、産地と蔵を直接応援。Terroir HUBが全国のワイナリーの返礼品を産地別に集めました。実質自己負担2,000円で、あなたの好きな日本ワインを。</p>
    <div class="stats">
      <div class="stat"><div class="stat-n">{total}</div><div class="stat-l">返礼品</div></div>
      <div class="stat"><div class="stat-n">{n_winery}</div><div class="stat-l">ワイナリー</div></div>
      <div class="stat"><div class="stat-n">{n_pref}</div><div class="stat-l">都道府県</div></div>
    </div>
  </div>
</header>
<section class="steps"><div class="steps-grid">
  <div class="step"><div class="step-n">1</div><h3>控除上限を確認</h3><p>年収・家族構成で寄付できる上限額が決まります。各サイトのシミュレーターで確認しましょう。</p></div>
  <div class="step"><div class="step-n">2</div><h3>好きなワインを選ぶ</h3><p>産地・ワイナリーから選んで「楽天ふるさと納税で見る」へ。寄付すると返礼品として届きます。</p></div>
  <div class="step"><div class="step-n">3</div><h3>控除を申請</h3><p>ワンストップ特例（5自治体以内）または確定申告で、実質自己負担2,000円に。</p></div>
</div></section>
<div class="simbar"><div class="simcard">
  <p>💡 まずは控除上限額をチェック。年収と家族構成を入れるだけで、いくらまで寄付できるか分かります。</p>
  <a href="https://event.rakuten.co.jp/furusato/simulation/" target="_blank" rel="noopener">控除シミュレーターを開く ›</a>
</div></div>
<div class="toolbar"><div class="toolbar-inner">
  <input type="search" class="search-box" id="fsearch" placeholder="🔍 ワイナリー名・銘柄で絞り込む（例: 甲州、メルロー、北海道）">
  <div class="pills" id="fpills">{pills}</div>
</div></div>
<main class="content" id="fcontent">
  {sections}
  <div class="noresult" id="noresult">該当する返礼品が見つかりませんでした。</div>
</main>
<section class="faqsec"><h2>ふるさと納税ワインのよくある質問</h2><dl class="faq">{faq_html}</dl></section>
{NOTE}
{HUB_JS}
'''
    write(os.path.join(OUTDIR, "index.html"), head + body + FOOTER)
    return ordered


HUB_JS = """
<script>
(function(){
  var search=document.getElementById('fsearch'),pills=document.getElementById('fpills');
  var blocks=[].slice.call(document.querySelectorAll('.pref-block')),noresult=document.getElementById('noresult');
  var curPref='all';
  function apply(){
    var q=(search.value||'').trim().toLowerCase(),any=false;
    blocks.forEach(function(b){
      var prefOk=(curPref==='all'||b.getAttribute('data-pref')===curPref),shown=0;
      [].forEach.call(b.querySelectorAll('.fcard'),function(c){
        var ok=prefOk&&(!q||c.getAttribute('data-kw').indexOf(q)>-1);
        c.style.display=ok?'':'none';if(ok)shown++;
      });
      b.style.display=shown>0?'':'none';if(shown>0)any=true;
    });
    noresult.style.display=any?'none':'block';
  }
  search.addEventListener('input',apply);
  pills.addEventListener('click',function(e){
    var btn=e.target.closest('.pill');if(!btn)return;
    curPref=btn.getAttribute('data-pref');
    [].forEach.call(pills.querySelectorAll('.pill'),function(p){p.classList.toggle('active',p===btn);});
    apply();
    if(curPref!=='all'){var t=document.getElementById('pref-'+curPref);if(t)t.scrollIntoView({behavior:'smooth',block:'start'});}
    else window.scrollTo({top:0,behavior:'smooth'});
  });
})();
</script>
"""


def build_pref(pref, items, all_prefs):
    pn = PREF_NAMES[pref]
    n = len(items)
    n_winery = len({it["winery_id"] for it in items})
    wineries = sorted({it["winery"] for it in items})
    lead = PREF_LEAD.get(pref) or (
        f"{pn}のワイナリーによる日本ワインのふるさと納税返礼品をまとめました。"
        f"{n_winery}のワイナリーから{n}件の返礼品を掲載しています。寄付で{pn}のワイン産地を応援できます。")
    cards = "".join(card_html(it) for it in items)

    title = f"{pn}のワイン ふるさと納税 返礼品{n}件 | Terroir HUB WINE"
    desc = (f"{pn}の日本ワインふるさと納税返礼品を{n}件掲載（{n_winery}ワイナリー）。"
            f"{('、'.join(wineries[:4]))}など{pn}のワインを、寄付で応援しながら受け取れます。楽天ふるさと納税対応。")
    url = f"https://{DOMAIN}/wine/furusato/{pref}.html"
    crumb = [("Terroir HUB WINE", f"https://{DOMAIN}/"),
             ("ふるさと納税", f"https://{DOMAIN}/wine/furusato/"),
             (pn, url)]
    faqs = [
        (f"{pn}のワインでふるさと納税のおすすめは？",
         f"{pn}では{n_winery}のワイナリーから{n}件の日本ワイン返礼品が選べます。{('、'.join(wineries[:5]))}などのワインが寄付で受け取れます。"),
        (f"{pn}のワインふるさと納税はどこで寄付できますか？",
         "各返礼品の「楽天ふるさと納税で見る」ボタンから楽天ふるさと納税の該当ページに移動して寄付できます。"),
    ] + FAQ_COMMON[:3]
    jsonld = jsonld_for(f"{pn}のワイン ふるさと納税返礼品", desc, url, crumb, items, faqs)
    head = HEAD.format(title=esc(title), desc=esc(desc), ogtitle=esc(f"{pn}のワイン ふるさと納税 返礼品{n}件"),
                       canonical=url, jsonld=jsonld) + HEAD_TAIL

    others = [p for p in all_prefs if p != pref]
    other_links = "".join(f'<a href="/wine/furusato/{p}.html">{esc(PREF_NAMES[p])}</a>' for p in others)
    faq_html = "".join(f'<div class="faq-item"><dt>{esc(q)}</dt><dd>{esc(a)}</dd></div>' for q, a in faqs)
    body = f'''
<div class="crumb"><a href="/">ホーム</a> › <a href="/wine/furusato/">ふるさと納税</a> › {esc(pn)}</div>
<header class="hero">
  <div class="hero-inner">
    <div class="hero-tag">FURUSATO TAX — {esc(pn)}</div>
    <h1>{esc(pn)}のワインを、ふるさと納税で。</h1>
    <p>{esc(lead)}</p>
    <div class="stats">
      <div class="stat"><div class="stat-n">{n}</div><div class="stat-l">返礼品</div></div>
      <div class="stat"><div class="stat-n">{n_winery}</div><div class="stat-l">ワイナリー</div></div>
    </div>
  </div>
</header>
<div class="simbar"><div class="simcard">
  <p>💡 控除上限額を先にチェック。年収と家族構成を入れるだけで、いくらまで寄付できるか分かります。</p>
  <a href="https://event.rakuten.co.jp/furusato/simulation/" target="_blank" rel="noopener">控除シミュレーターを開く ›</a>
</div></div>
<main class="content">
  <section class="pref-block">
    <h2 class="pref-title">{esc(pn)}のワインふるさと納税 返礼品 <span class="pref-count">{n}件</span></h2>
    <div class="fgrid">{cards}
    </div>
  </section>
  <div class="otherpref">
    <h2>他の産地のワインふるさと納税</h2>
    <div class="otherpref-list">{other_links}</div>
  </div>
</main>
<section class="faqsec"><h2>{esc(pn)}のワインふるさと納税 よくある質問</h2><dl class="faq">{faq_html}</dl></section>
{NOTE}
'''
    write(os.path.join(OUTDIR, f"{pref}.html"), head + body + FOOTER)


def main():
    by_pref = collect()
    ordered = build_hub(by_pref)
    all_prefs = [p for p, _ in ordered]
    for p, items in ordered:
        build_pref(p, items, all_prefs)
    # 蔵ページからの内部リンク用に、返礼品ありの県スラッグを出力
    write(os.path.join(OUTDIR, "_prefs.json"), json.dumps(all_prefs, ensure_ascii=False))
    total = sum(len(v) for v in by_pref.values())
    print(f"生成: ハブ + 県別{len(all_prefs)}ページ / 返礼品{total}件")
    print("県別:", " ".join(all_prefs))


if __name__ == "__main__":
    main()

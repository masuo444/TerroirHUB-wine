#!/usr/bin/env python3
"""
AIサクラ ナレッジベース構築（強化版）
全ワイナリーデータ + GI情報 + 品種知識 + FAQ を統合。
wine/sakura_kb.json と wine/search_index.json を生成。
"""

import json, glob, os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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

# ── ワイナリーデータ収集 ──
all_wineries = []
search_index = []
by_pref = {}

for jf in sorted(glob.glob(os.path.join(BASE, 'data', 'data_*_wineries.json'))):
    pref = os.path.basename(jf).replace('data_','').replace('_wineries.json','')
    pref_name = PREF_NAMES.get(pref, pref)
    try:
        with open(jf, 'r', encoding='utf-8') as f:
            wineries = json.load(f)
    except Exception as e:
        print(f"  WARN {pref}: {e}")
        continue

    pref_entries = []
    for w in wineries:
        if not w.get('id'): continue
        brands_names = [br.get('name','') for br in w.get('brands',[]) if isinstance(br,dict) and br.get('name')]
        entry = {
            'id':         w.get('id',''),
            'name':       w.get('name',''),
            'brand':      w.get('brand',''),
            'pref':       pref,
            'pref_name':  pref_name,
            'area':       w.get('area',''),
            'founded':    w.get('founded',''),
            'founded_era':w.get('founded_era',''),
            'gi':         w.get('gi',''),
            'grapes':     w.get('grapes',[])[:6],
            'wine_style': w.get('wine_style',''),
            'main_grape': w.get('main_grape',''),
            'winery_type':w.get('winery_type',''),
            'url':        w.get('url',''),
            'tel':        w.get('tel',''),
            'address':    w.get('address',''),
            'visit':      w.get('visit',''),
            'desc':       w.get('desc','')[:300],
            'brands':     brands_names[:3],
            'features':   w.get('features',[])[:3],
            'page':       f"/wine/{pref}/{w.get('id','')}.html",
        }
        all_wineries.append(entry)
        pref_entries.append(entry)

        # 検索インデックス（軽量）
        search_index.append({
            'id':       w.get('id',''),
            'name':     w.get('name',''),
            'brand':    w.get('brand',''),
            'pref':     pref,
            'pref_name':pref_name,
            'area':     w.get('area',''),
            'gi':       w.get('gi',''),
            'main_grape':w.get('main_grape',''),
            'grapes':   w.get('grapes',[])[:3],
            'brands':   brands_names[:2],
            'page':     f"/wine/{pref}/{w.get('id','')}.html",
        })

    a_count = sum(1 for w in pref_entries if w.get('url') and w.get('founded') and w.get('brands') and w.get('features'))
    by_pref[pref] = {
        'name':      pref_name,
        'count':     len(pref_entries),
        'a_rank':    a_count,
        'wineries':  pref_entries,
    }

# ── ナレッジベース ──
kb = {
    'version':  '2.0',
    'domain':   'wine',
    'updated':  date.today().isoformat(),
    'total_wineries': len(all_wineries),
    'site_url': 'https://wine.terroirhub.com',

    # GI認定産地
    'gi_regions': {
        'GI山梨': {
            'year': 2013, 'pref': '山梨県',
            'main_grapes': ['甲州','マスカット・ベーリーA','メルロー'],
            'winery_count': by_pref.get('yamanashi',{}).get('count',0),
            'desc': '2013年、日本初のGI認定。山梨県産ぶどう100%使用のワイン。甲州・マスカット・ベーリーAが主要品種。勝沼・甲州市・笛吹市が主産地。'
        },
        'GI北海道': {
            'year': 2018, 'pref': '北海道',
            'main_grapes': ['ピノ・ノワール','ツヴァイゲルト','ケルナー','シャルドネ'],
            'winery_count': by_pref.get('hokkaido',{}).get('count',0),
            'desc': '2018年認定。冷涼な気候で欧州系品種が育つ。余市・仁木エリアが中心産地。ピノ・ノワールが高く評価される。'
        },
        'GI長野': {
            'year': 2020, 'pref': '長野県',
            'main_grapes': ['メルロー','シャルドネ','カベルネ・フラン','ソーヴィニョン・ブラン'],
            'winery_count': by_pref.get('nagano',{}).get('count',0),
            'desc': '2020年認定。標高の高い冷涼な産地。塩尻・東御・上田エリアが主産地。シャトー・メルシャンなど国際的に評価が高い。'
        },
        'GI山形': {
            'year': 2023, 'pref': '山形県',
            'main_grapes': ['メルロー','シャルドネ','デラウェア'],
            'winery_count': by_pref.get('yamagata',{}).get('count',0),
            'desc': '2023年認定。フルーツ王国山形の恵みを活かしたワイン。上山・高畠・天童エリアが産地。'
        },
        'GI大阪': {
            'year': 2024, 'pref': '大阪府',
            'main_grapes': ['デラウェア','マスカット・ベーリーA'],
            'winery_count': by_pref.get('osaka',{}).get('count',0),
            'desc': '2024年認定、最新のGI産地。河内エリア（柏原・羽曳野・富田林）が主産地。日本最古のワイン産地のひとつ。'
        },
    },

    # 主要ブドウ品種
    'grape_varieties': {
        '甲州': {
            'en': 'Koshu', 'code': 'koshu', 'style': '白',
            'region': '山梨', 'color': 'white',
            'desc': '日本固有の白ワイン用品種。淡いゴールドの色合いと繊細な香り、すっきりとした味わい。和食との相性が抜群。GI山梨の代表品種。'
        },
        'マスカット・ベーリーA': {
            'en': 'Muscat Bailey A', 'code': 'mba', 'style': '赤',
            'region': '山梨・新潟', 'color': 'red',
            'desc': '川上善兵衛が育種した日本固有の赤ワイン用品種。フルーティで飲みやすく渋みが少ない。「日本のボジョレー」とも呼ばれる。'
        },
        'メルロー': {
            'en': 'Merlot', 'code': 'merlot', 'style': '赤',
            'region': '長野・山梨', 'color': 'red',
            'desc': 'フランスボルドー系品種。長野・山梨で国際コンクール受賞レベルの高品質なものが生産される。'
        },
        'シャルドネ': {
            'en': 'Chardonnay', 'code': 'chardonnay', 'style': '白',
            'region': '北海道・長野', 'color': 'white',
            'desc': '世界的に有名な白ワイン用品種。北海道の冷涼な気候で育ったものは酸が豊かで複雑。'
        },
        'ピノ・ノワール': {
            'en': 'Pinot Noir', 'code': 'pinot_noir', 'style': '赤',
            'region': '北海道', 'color': 'red',
            'desc': '冷涼な気候を好む繊細な赤ワイン用品種。北海道余市・仁木エリアが主産地。エレガントなスタイルが特徴。'
        },
        'カベルネ・フラン': {
            'en': 'Cabernet Franc', 'code': 'cabernet_franc', 'style': '赤',
            'region': '長野・山梨', 'color': 'red',
            'desc': 'ボルドー系品種。ハーブ香が特徴的。長野・山梨で栽培され、単一品種でも造られる。'
        },
        'ツヴァイゲルト': {
            'en': 'Zweigelt', 'code': 'zweigelt', 'style': '赤',
            'region': '北海道', 'color': 'red',
            'desc': 'オーストリア原産の赤ワイン用品種。北海道で広く栽培される。チェリー系の果実味が特徴。'
        },
        'ケルナー': {
            'en': 'Kerner', 'code': 'kerner', 'style': '白',
            'region': '北海道', 'color': 'white',
            'desc': 'ドイツ原産の白ワイン用品種。北海道で良質なものが生産。アロマティックで花の香りが特徴。'
        },
        'ソーヴィニョン・ブラン': {
            'en': 'Sauvignon Blanc', 'code': 'sauvignon_blanc', 'style': '白',
            'region': '長野', 'color': 'white',
            'desc': 'ハーブや柑橘の香りが特徴的な白ワイン用品種。長野で高品質なものが生産される。'
        },
        'カベルネ・ソーヴィニョン': {
            'en': 'Cabernet Sauvignon', 'code': 'cabernet_sauvignon', 'style': '赤',
            'region': '山梨・長野', 'color': 'red',
            'desc': '世界で最も有名な赤ワイン用品種。重厚で長期熟成向き。山梨・長野で栽培。'
        },
    },

    # ペアリング知識
    'pairing': {
        '甲州（白）':               ['寿司', '刺身', '天ぷら', '和食全般', '魚介類', '豆腐料理'],
        'マスカット・ベーリーA（赤）':['焼き鳥', 'すき焼き', '煮物', '和牛', 'ハンバーグ', '鶏料理'],
        'ピノ・ノワール（赤）':       ['サーモン', '鴨肉', 'きのこ料理', 'ブルゴーニュ料理'],
        'メルロー（赤）':            ['牛肉ステーキ', 'ジビエ', 'ラム肉', 'チーズ全般'],
        'シャルドネ（白）':          ['クリーム系パスタ', '魚のムニエル', '白身魚', 'チキン'],
        'スパークリング':            ['前菜全般', '寿司', '揚げ物', '刺身'],
    },

    # 飲み方知識
    'serving': {
        '白ワイン': {'temp': '8〜12℃', 'glass': 'ワイングラス（中型）'},
        '赤ワイン': {'temp': '16〜18℃', 'glass': 'ワイングラス（大型）', 'note': 'デカンタージュすると香りが開く'},
        'ロゼワイン': {'temp': '10〜12℃', 'glass': 'ワイングラス（中型）'},
        'スパークリング': {'temp': '6〜8℃', 'glass': 'フルートグラス'},
        '甲州（特別）': {'temp': '10〜12℃', 'note': '少し高めの温度で複雑な香りが開く'},
    },

    # FAQ
    'faq': [
        {
            'q': '日本ワインとは何ですか？',
            'a': '国産ぶどうを100%使用し、日本国内で醸造されたワインです。2015年の国税庁の定義により、ラベルに「日本ワイン」と表示できるようになりました。輸入果汁を使ったものは「国内製造ワイン」として区別されます。'
        },
        {
            'q': 'GI（地理的表示）とは何ですか？',
            'a': 'GIとは国税庁が認定する地理的表示制度で、特定地域産のぶどうだけで造られたワインに与えられます。現在GI山梨（2013年）・GI北海道（2018年）・GI長野（2020年）・GI山形（2023年）・GI大阪（2024年）の5産地が認定されています。'
        },
        {
            'q': '甲州ワインとはどんなワインですか？',
            'a': '甲州は山梨県が主産地の日本固有の白ワイン用品種です。淡いゴールドの色合いと繊細な香り、すっきりとした辛口の味わいが特徴。和食との相性が抜群で、寿司・天ぷら・魚料理によく合います。'
        },
        {
            'q': 'マスカット・ベーリーAとはどんなワインですか？',
            'a': 'マスカット・ベーリーA（MBA）は川上善兵衛が育種した日本固有の赤ワイン用品種です。フルーティで飲みやすく、渋みが少ないのが特徴。山梨・新潟が主産地で「日本のボジョレー」とも呼ばれます。'
        },
        {
            'q': '日本ワインの産地はどこが有名ですか？',
            'a': '山梨県（国内最大の産地・91ワイナリー）・北海道（冷涼でピノ・ノワールが有名・79ワイナリー）・長野県（標高が高くメルローが秀逸・70ワイナリー）・山形県・岩手県が主要産地です。全国に432以上のワイナリーがあります。'
        },
        {
            'q': 'ワイナリー見学はできますか？',
            'a': 'Terroir HUB WINEに掲載しているワイナリーの多くが見学・テイスティングを受け入れています。各ワイナリーページの「見学」欄をご確認ください。要予約のところが多いため、公式サイトや電話での事前予約をお勧めします。'
        },
        {
            'q': '甲州ワインと料理のペアリングは？',
            'a': '甲州は和食との相性が抜群です。お寿司・刺身・天ぷら・魚介料理・豆腐料理など、繊細な和の味わいを引き立てます。柑橘のような爽やかな酸が料理のうまみと調和します。'
        },
        {
            'q': '北海道のワインはなぜ美味しいですか？',
            'a': '北海道は冷涼な気候がワイン用ぶどうの栽培に適しており、特に余市・仁木エリアはピノ・ノワールやシャルドネが世界的な評価を受けています。昼夜の寒暖差が大きく、酸が豊かで複雑な風味のワインが生まれます。'
        },
        {
            'q': '長野のメルローはなぜ評価が高いですか？',
            'a': '長野県は標高600〜900mの高地で冷涼な気候を持ち、メルローの栽培に最適です。シャトー・メルシャンの椀子メルローや桔梗ヶ原メルローは国際コンクールでも受賞するなど、世界水準のワインが生産されています。'
        },
        {
            'q': '日本ワインはどこで買えますか？',
            'a': '各ワイナリーの直販サイト・ワイナリー附設のショップ・全国のワイン専門店・百貨店・オンラインショッピング（Amazon・楽天市場・ワインショップ各社）で購入できます。希少な小規模ワイナリーのワインはワイナリー直販が確実です。'
        },
        {
            'q': 'ワインの飲み頃の温度は？',
            'a': '白ワイン・ロゼワインは8〜12℃（冷蔵庫から出して少し置く）、赤ワインは16〜18℃（室温より少し低め）、スパークリングワインは6〜8℃（よく冷やす）が目安です。甲州などの繊細な白ワインは少し高めの10〜12℃で飲むと香りが開きます。'
        },
    ],

    # 産地別サマリー
    'prefectures': {
        pref: {
            'name':  info['name'],
            'count': info['count'],
            'a_rank':info['a_rank'],
        }
        for pref, info in by_pref.items()
    },

    # 全ワイナリーデータ
    'wineries': all_wineries,
}

# ── 出力 ──
kb_dir = os.path.join(BASE, 'wine')
os.makedirs(kb_dir, exist_ok=True)

kb_path = os.path.join(kb_dir, 'sakura_kb.json')
with open(kb_path, 'w', encoding='utf-8') as f:
    json.dump(kb, f, ensure_ascii=False, separators=(',',':'))

idx_path = os.path.join(kb_dir, 'search_index.json')
with open(idx_path, 'w', encoding='utf-8') as f:
    json.dump(search_index, f, ensure_ascii=False, separators=(',',':'))

kb_size  = os.path.getsize(kb_path)  // 1024
idx_size = os.path.getsize(idx_path) // 1024

print(f'sakura_kb.json   : {len(all_wineries)}件 / {kb_size}KB')
print(f'search_index.json: {len(search_index)}件 / {idx_size}KB')
print(f'GI産地: {len(kb["gi_regions"])}件 / 品種: {len(kb["grape_varieties"])}種 / FAQ: {len(kb["faq"])}問')

# Terroir HUB WINE — エージェント作業マニュアル

## プロジェクト概要
全国560+ワイナリーの日本ワインデータベース。47都道府県カバー（主要産地：山梨80+蔵・北海道80+蔵・長野70+蔵・山形40+蔵・岩手30+蔵）。
デプロイ先: wine.terroirhub.com
GitHub: （未設定）
姉妹サイト: https://sake.terroirhub.com/（日本酒版）、https://shochu.terroirhub.com/（焼酎版）

## ファイル構成

```
/Users/masuo/Desktop/テロワールハブ　総合/terroirHUB wine/
├── index.html                          # トップページ
├── RULES.md                            # 情報正確性ルール（必読）
├── CLAUDE.md                           # このファイル
├── template_wine.html                  # CSSテンプレート（ワイナリーページ用）
├── data/
│   └── data_{県slug}_wineries.json     # 各県のワイナリーデータ
├── wine/
│   ├── sakura_kb.json                  # AIサクラ ナレッジベース
│   ├── track.js                        # 行動データ取得スクリプト
│   ├── region/                         # 8地域ページ
│   │   ├── hokkaido.html
│   │   ├── tohoku.html
│   │   ├── kanto.html
│   │   ├── chubu.html
│   │   ├── kinki.html
│   │   ├── chugoku.html
│   │   ├── shikoku.html
│   │   └── kyushu.html
│   ├── guide/                          # 教科書ページ
│   │   ├── index.html                  # 日本ワインの基礎
│   │   ├── varieties.html              # 品種（甲州・マスカットベリーA・メルロー等）
│   │   ├── production.html             # 醸造・栽培の製法
│   │   ├── drinking.html               # 飲み方（温度・グラス・デカンタ等）
│   │   ├── pairing.html                # 料理ペアリング
│   │   ├── history.html                # 歴史（明治維新以降の日本ワイン文化）
│   │   ├── regions.html                # 産地別特徴（GI地域等）
│   │   └── glossary.html               # 用語集
│   ├── en/                             # 英語版
│   ├── fr/                             # フランス語版
│   └── {県slug}/                       # 各県ディレクトリ
│       ├── index.html                  # 県一覧ページ
│       └── {winery_id}.html            # 個別ワイナリーページ
├── admin/
│   └── index.html                      # 管理ダッシュボード
├── api/
│   ├── sakura.js                       # Claude AI プロキシ（AIサクラ）
│   ├── create-checkout.js              # Stripe決済
│   └── webhook.js                      # Stripeウェブフック
├── scripts/
│   ├── regenerate_all_pages.py         # 全ワイナリーページ一括生成
│   ├── generate_multilang_pages.py     # 多言語版生成
│   └── build_sakura_kb.py              # AIナレッジベース構築
├── vercel.json
├── robots.txt
├── sitemap.xml
└── package.json
```

## データ形式（JSON）

各`data/{県slug}_wineries.json`は配列。1ワイナリーあたり:

```json
{
  "id": "chateau-mercian-mariko",
  "name": "シャトー・メルシャン 椀子ワイナリー",
  "company": "メルシャン（株）",
  "brand": "椀子",
  "winery_type": "estate",
  "founded": "2019",
  "founded_era": "令和元年",
  "address": "長野県上田市富士山1704",
  "tel": "0268-38-5345",
  "url": "https://www.chateaumercian.com/winery/mariko/",
  "area": "上田市（椀子）",
  "desc": "令和元年（2019年）開業。上田盆地の南東部、標高600〜700mに広がる椀子ヴィンヤードを核に、長野産ぶどうのみで造るエステートワイナリー。",
  "visit": "ワイナリー見学・テイスティング可（要予約）",
  "winery_type": "estate",
  "wine_style": "red",
  "main_grape": "merlot",
  "gi": "GI長野",
  "grapes": ["メルロー", "カベルネ・フラン", "シャルドネ"],
  "brands": [
    {
      "name": "椀子 メルロー",
      "type": "赤ワイン",
      "specs": "メルロー主体、アルコール13度",
      "grapes": "メルロー、カベルネ・フラン"
    },
    {
      "name": "椀子 シャルドネ",
      "type": "白ワイン",
      "specs": "シャルドネ100%、アルコール13度",
      "grapes": "シャルドネ"
    }
  ],
  "features": [
    "標高600〜700mの椀子ヴィンヤード。長野県産ぶどう100%エステートワイン",
    "2023年日本ワインコンクール金賞・最高金賞受賞",
    "ワイナリー見学・テイスティングルーム完備"
  ],
  "nearest_station": "しなの鉄道 大屋駅（車約10分）",
  "source": "https://www.chateaumercian.com/winery/mariko/",
  "lat": 36.3667,
  "lng": 138.2167,
  "name_en": "Chateau Mercian Mariko Winery"
}
```

### 焼酎版との差分フィールド（ワイン固有フィールド）
| フィールド | 説明 | 例 |
|-----------|------|-----|
| `winery_type` | ワイナリー規模・スタイル | "estate" / "large" / "medium" / "small" / "natural" |
| `wine_style` | 主要ワインスタイル | "dry_white" / "red" / "rose" / "sweet" / "sparkling" |
| `main_grape` | 主要品種コード | "koshu" / "mba" / "merlot" / "chardonnay" / "pinot_noir" |
| `gi` | GI（地理的表示）認定 | "GI山梨" / "GI北海道" / "GI長野" / "GI山形" |
| `grapes` | 使用品種の配列 | ["甲州", "メルロー", "シャルドネ"] |
| `brands[].grapes` | 銘柄ごとの使用品種 | "甲州100%" |

## 品質ランク定義

| ランク | 条件 | 状態 |
|--------|------|------|
| A | founded + brands(1〜3銘柄) + features(2+) + url + winery_type | 完全版 |
| B | founded + brands or features あるがURL無し or winery_type未設定 | 要改善 |
| C | foundedのみ | 最低限 |
| D | 何もなし | 対象外 |

**目標: 主要産地（山梨・北海道・長野・山形）は全蔵Aランク**

## AIコンシェルジュ「サクラ」（日本酒版・焼酎版と共通）

全Terroir HUBサイト共通のAIコンシェルジュ「サクラ」。
- 知識ベース: `wine/sakura_kb.json`
- API: `/api/sakura.js`
- キャラクター: 日本ワインの奥深さを語る、落ち着いた案内人

## 日本ワインの主要品種

| コード | 日本語 | 英語 | 主要産地 |
|--------|--------|------|----------|
| koshu | 甲州 | Koshu | 山梨 |
| mba | マスカット・ベーリーA | Muscat Bailey A | 山梨・新潟 |
| merlot | メルロー | Merlot | 長野・山梨 |
| chardonnay | シャルドネ | Chardonnay | 北海道・長野 |
| pinot_noir | ピノ・ノワール | Pinot Noir | 北海道 |
| cabernet_franc | カベルネ・フラン | Cabernet Franc | 長野・山梨 |
| cabernet_sauvignon | カベルネ・ソーヴィニョン | Cabernet Sauvignon | 山梨 |
| zweigelt | ツヴァイゲルト | Zweigelt | 北海道 |
| kerner | ケルナー | Kerner | 北海道 |
| sauvignon_blanc | ソーヴィニョン・ブラン | Sauvignon Blanc | 長野 |

## データソース（ワイナリーリスト取得元）

### 全国データソース
| ソース | URL | 備考 |
|---|---|---|
| 日本ワイナリーアワード | https://japanwineryaward.jp/ | ワイナリー評価・一覧 |
| 日本ワイン | https://www.japanwine.jp/ | 日本ワイン振興会 |
| 国税庁 酒蔵マップ | https://www.nta.go.jp/taxes/sake/sakagura/index.htm | 公式データ（果実酒製造業者） |

### 都道府県ワイン組合・産地別サイト
| 産地 | URL | 備考 |
|---|---|---|
| 山梨ワイン | https://www.wine.or.jp/ | 山梨県ワイン酒造組合 |
| 北海道ワイン | https://www.hokkaido-wine.jp/ | 北海道ワイン連絡協議会 |
| 長野ワイン | https://www.wine.or.jp/nagano/ | 長野県ワイン協会 |
| 山形ワイン | https://yamagata-wine.jp/ | 山形ワイン協議会 |
| 岩手ワイン | https://iwate-wine.jp/ | 岩手県ワイン協会 |

### GI（地理的表示）保護地域
| GI名 | 地域 | 認定年 |
|---|---|---|
| GI山梨 | 山梨県 | 2013年 |
| GI北海道 | 北海道 | 2018年 |
| GI長野 | 長野県 | 2020年 |
| GI山形 | 山形県 | 2023年 |
| GI大阪 | 大阪府 | 2024年 |

## 絶対にやってはいけないこと

1. **情報を捏造しない** — 公式サイトにない情報は入れない
2. **推測で埋めない** — 分からない項目は空欄のまま
3. **AIが文章を生成しない** — 説明文は公式サイトの文言を使う
4. **他のワイナリーのデータを混同しない** — IDとワイナリー名を必ず照合
5. **輸入ワインと日本ワインを混同しない** — 国産ぶどう100%使用のもののみ「日本ワイン」として扱う
6. **brandsにspecs=""で入れて「完了」と言わない** — 実データがないならBランクと正直に報告

## 県slugマッピング

```
hokkaido aomori iwate miyagi akita yamagata fukushima
ibaraki tochigi gunma saitama chiba tokyo kanagawa
niigata toyama ishikawa fukui yamanashi nagano gifu shizuoka aichi
mie shiga kyoto osaka hyogo nara wakayama
tottori shimane okayama hiroshima yamaguchi
tokushima kagawa ehime kochi
fukuoka saga nagasaki kumamoto oita miyazaki kagoshima okinawa
```

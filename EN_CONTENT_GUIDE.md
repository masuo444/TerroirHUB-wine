# English Content Guide — Terroir HUB WINE
（wine英語ページ本物化の品質基準。2026-07-18制定。sake版 EN_CONTENT_GUIDE.md の姉妹版）

## 目的
英語圏のワイン愛好家・訪日旅行者が「飲みたく/行きたくなる」編集品質の英語ワイナリーページを作る。直訳・殻ページ禁止。

## 絶対ルール（RULES.md準拠）
1. **新しい事実を作らない**。日本語データ（desc / features / brands / grapes / gi / winery_type / founded / visit）にある事実だけを英語化
2. 受賞歴・数値・逸話の追加禁止。元データに無い「award-winning」「acclaimed」等の形容禁止
3. ワイン用語の一般説明はglossとして許可（例: Koshu — Japan's indigenous white grape）
4. 読みが不確かなワイナリー名・銘柄はローマ字化しない（name_en・公式サイト表記・確実な一般知識のみ。不明なら日本語のまま）

## 出力形式（data/en_content.json、県:IDキー — sakeと同一スキーマ）
```json
"yamanashi:grace-wine": {
  "tagline_en": "1文フック（12-20語）",
  "desc_en": "40〜120語。元descが薄ければ短く正直に",
  "features_en": ["短句", "短句", "短句"],
  "brands_en": {
    "日本語銘柄名（brands[].nameと完全一致）": {"name_en": "...", "specs_en": "..."}
  },
  "by": "sonnet",
  "audited": false
}
```

## ワイン特有の書き方
- **品種対訳**: 甲州=Koshu / マスカット・ベーリーA=Muscat Bailey A / メルロー=Merlot / シャルドネ=Chardonnay / ピノ・ノワール=Pinot Noir / カベルネ・ソーヴィニヨン=Cabernet Sauvignon / カベルネ・フラン=Cabernet Franc / ツヴァイゲルト=Zweigelt / ケルナー=Kerner / ソーヴィニョン・ブラン=Sauvignon Blanc / 山幸=Yamasachi / ナイアガラ=Niagara / デラウェア=Delaware
- **日本固有品種は初出時にgloss**: Koshu (Japan's indigenous white grape) / Muscat Bailey A (a Japanese-bred red)
- **specs_en形式**: "{英語タイプ} — {品種}, {アルコール度}" 例: "Red — Merlot-led blend, 13% ABV"。typeフィールドの対訳はジェネレータ側でも行うためspecs_enでは品種・度数中心に
- **GI**: "GI Yamanashi" のように表記し、初出時に (Geographical Indication) を添える
- **winery_type**: estate=estate winery（自社畑100%と説明があれば "all estate-grown fruit"）
- 標高・畑名・仕立て（垣根=vertical shoot positioning / 棚=overhead pergola）はdescにある場合のみ

## 文体
sake版と同じ: ナショジオ×ワイン誌。宣伝臭禁止。tagline は創業年の言い換え不可。和暦削除・西暦のみ。

## 監査チェックリスト
- [ ] JA側に無い事実の混入なし（1文ずつ照合）
- [ ] brands_enキーがbrands[].nameと完全一致
- [ ] 品種名の対訳が正確、日本固有品種にgloss
- [ ] 不確かなローマ字なし

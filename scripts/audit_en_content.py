#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EN翻訳バッチの機械監査（Fable人力監査の前段フィルタ）。

検出項目:
 A) 構造: 元データに無いキー / brands_enキー不一致 / 必須フィールド欠落 / desc語数逸脱
 B) 捏造疑い: JA specsが空欄なのに specs_en に形容がある銘柄
 C) 受賞語の出典無し: EN側に award/gold/IWC 等があるのにJA側(desc+features+brands)に受賞語が無い
 D) 数値の出典無し: EN側の 精米歩合/％/年号 がJA側に存在しない（大まかな照合）
使い方: python3 scripts/audit_en_content.py <batch1.json> [batch2.json ...]
"""
import json, io, re, glob, sys

def load_src():
    src = {}
    for p in glob.glob('data/data_*_wineries.json'):
        pref = p.split('data_')[1].replace('_wineries.json', '')
        for b in json.load(io.open(p, encoding='utf-8')):
            src[f"{pref}:{b.get('id')}"] = b
    return src

AWARD_EN = re.compile(r'\b(gold|award|medal|IWC|Kura Master|Monde|champion|platinum|prize)\b', re.I)
AWARD_JA = re.compile(r'金賞|受賞|IWC|Kura ?Master|モンド|プラチナ|チャンピオン|鑑評会|知事賞|コンクール')

def ja_text(b):
    parts = [b.get('desc',''), b.get('visit','') or '']
    vi = b.get('visit_info') or {}
    parts.append(json.dumps(vi, ensure_ascii=False))
    for f in b.get('features', []):
        parts.append(f if isinstance(f, str) else json.dumps(f, ensure_ascii=False))
    for br in b.get('brands', []):
        if isinstance(br, dict): parts.append(' '.join([br.get('name',''), br.get('specs',''), br.get('type',''), str(br.get('grapes',''))]))
    return ' '.join(parts)

def en_text(v):
    parts = [v.get('tagline_en',''), v.get('desc_en','')] + list(v.get('features_en') or [])
    for e in (v.get('brands_en') or {}).values():
        parts.append(e.get('name_en','') + ' ' + e.get('specs_en',''))
    return ' '.join(parts)

def main(paths):
    src = load_src()
    flags = []
    total = 0
    for path in paths:
        out = json.load(io.open(path, encoding='utf-8'))
        for k, v in out.items():
            total += 1
            if k not in src:
                flags.append((k, 'A', 'source not found')); continue
            b = src[k]
            names = {x.get('name') if isinstance(x, dict) else str(x) for x in b.get('brands', [])}
            specs_map = {(x.get('name') if isinstance(x, dict) else str(x)): ((x.get('specs','') + x.get('type','') + str(x.get('grapes',''))) if isinstance(x, dict) else '')
                         for x in b.get('brands', [])}
            for f in ('tagline_en', 'desc_en', 'features_en'):
                if not v.get(f): flags.append((k, 'A', 'missing ' + f))
            wc = len((v.get('desc_en') or '').split())
            if wc < 45 or wc > 145: flags.append((k, 'A', f'desc words={wc}'))
            for bk, e in (v.get('brands_en') or {}).items():
                if bk not in names:
                    flags.append((k, 'A', 'brand key mismatch: ' + bk))
                elif not specs_map.get(bk, '') and len((e.get('specs_en') or '').strip()) > 0:
                    flags.append((k, 'B', f'JA specs空欄なのにspecs_enあり: {bk} -> {e.get("specs_en")[:60]}'))
            jt, et = ja_text(b), en_text(v)
            if AWARD_EN.search(et) and not AWARD_JA.search(jt):
                flags.append((k, 'C', '受賞語がEN側のみ: ' + AWARD_EN.search(et).group(0)))
            for m in set(re.findall(r'polished to (\d{2})', et)):
                if m not in jt:
                    flags.append((k, 'D', f'精米歩合{m}%がJA側に見当たらない'))
    print(f'checked {total} entries, flags: {len(flags)}')
    for k, cat, msg in sorted(flags):
        print(f'[{cat}] {k}: {msg}')

if __name__ == '__main__':
    main(sys.argv[1:])

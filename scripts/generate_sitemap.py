#!/usr/bin/env python3
"""sitemap.xml 自動生成 — 全ワイナリーページ + 固定ページを含む"""

import json, glob, os
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://wine.terroirhub.com'
TODAY = date.today().isoformat()

urls = []

def add(loc, priority, changefreq='monthly'):
    urls.append({'loc': loc, 'priority': priority, 'changefreq': changefreq})

# ── トップ・固定ページ ──
add(f'{DOMAIN}/',               '1.0', 'weekly')
add(f'{DOMAIN}/wine/guide/',    '0.9', 'monthly')

for g in ['index','varieties','production','drinking','pairing','history','regions','glossary']:
    add(f'{DOMAIN}/wine/guide/{g}.html', '0.7', 'monthly')

# ── 産地ページ ──
for r in ['hokkaido','tohoku','kanto','chubu','kinki','chugoku','shikoku','kyushu']:
    add(f'{DOMAIN}/wine/region/{r}.html', '0.8', 'monthly')

# ── 県別インデックス + 個別ワイナリーページ ──
json_files = sorted(glob.glob(os.path.join(BASE, 'data', 'data_*_wineries.json')))
for jf in json_files:
    pref = os.path.basename(jf).replace('data_','').replace('_wineries.json','')
    add(f'{DOMAIN}/wine/{pref}/', '0.85', 'weekly')

    with open(jf, 'r', encoding='utf-8') as f:
        wineries = json.load(f)
    for b in wineries:
        if not b.get('id'): continue
        # Aランク相当は優先度高め
        is_a = bool(b.get('url') and b.get('founded') and
                    len(b.get('brands',[])) >= 1 and len(b.get('features',[])) >= 2)
        prio = '0.8' if is_a else '0.6'
        add(f'{DOMAIN}/wine/{pref}/{b["id"]}.html', prio, 'monthly')

# ── XML出力 ──
lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
]
for u in urls:
    lines += [
        '  <url>',
        f'    <loc>{u["loc"]}</loc>',
        f'    <lastmod>{TODAY}</lastmod>',
        f'    <changefreq>{u["changefreq"]}</changefreq>',
        f'    <priority>{u["priority"]}</priority>',
        '  </url>'
    ]
lines.append('</urlset>')

out = os.path.join(BASE, 'sitemap.xml')
with open(out, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print(f'sitemap.xml: {len(urls)} URLs を出力')

// サクラ Claude API プロキシ（全ジャンル統合版）
// Terroir HUB WINE — 日本酒+焼酎+ウイスキー+リキュール+ワイン 5ジャンル横断
// DB検索 → Claude知識 → Web検索の3段構えで回答

const fs = require('fs');
const path = require('path');

let searchIndex = null;
let wineKB = null;

function normalizeText(value) {
  if (Array.isArray(value)) return value.join(' ').toLowerCase();
  if (value && typeof value === 'object') return Object.values(value).join(' ').toLowerCase();
  return String(value || '').toLowerCase();
}

function getSearchIndex() {
  if (searchIndex) return searchIndex;
  searchIndex = [];
  const dataDir = path.join(__dirname, '..', 'wine');
  const indexes = [
    { file: 'search_index.json',         site: 'wine' },
    { file: 'search_index_sake.json',    site: 'sake' },
    { file: 'search_index_shochu.json',  site: 'shochu' },
    { file: 'search_index_whisky.json',  site: 'whisky' },
    { file: 'search_index_liqueur.json', site: 'liqueur' },
  ];
  indexes.forEach(idx => {
    try {
      const p = path.join(dataDir, idx.file);
      const data = JSON.parse(fs.readFileSync(p, 'utf-8'));
      data.forEach(e => { e._site = idx.site; });
      searchIndex = searchIndex.concat(data);
    } catch (e) {}
  });
  return searchIndex;
}

function getWineKB() {
  if (wineKB) return wineKB;
  try {
    const p = path.join(__dirname, '..', 'wine', 'sakura_kb.json');
    wineKB = JSON.parse(fs.readFileSync(p, 'utf-8'));
  } catch (e) {
    wineKB = null;
  }
  return wineKB;
}

function searchBreweries(query) {
  const idx = getSearchIndex();
  const ql = query.toLowerCase();
  const keywords = ql.split(/\s+/).filter(k => k.length > 0);

  const scored = idx.map(entry => {
    const name  = normalizeText(entry.n || entry.name);
    const brand = normalizeText(entry.b || entry.brand);
    const brands = normalizeText(entry.br || entry.brands);
    const area  = normalizeText(entry.a || entry.area);
    const nameEn = normalizeText(entry.ne);
    const pref  = normalizeText(entry.pn || entry.pref_name);
    const grapes = normalizeText(entry.grapes);
    const gi = normalizeText(entry.gi);
    const mainGrape = normalizeText(entry.main_grape);
    const full  = [name, brand, brands, area, nameEn, pref, grapes, gi, mainGrape].join(' ');

    let s = 0;
    if (brand  === ql)          s += 200;
    if (brand.includes(ql))     s += 100;
    if (brands.includes(ql))    s += 90;
    if (name   === ql)          s += 80;
    if (name.includes(ql))      s += 60;
    if (nameEn.includes(ql))    s += 50;
    if (pref.includes(ql))      s += 40;
    if (grapes.includes(ql))    s += 45;
    if (gi.includes(ql))        s += 45;
    if (mainGrape.includes(ql)) s += 45;
    if (area.includes(ql))      s += 35;
    if (full.includes(ql))      s += 10;
    if (keywords.length > 1 && keywords.every(k => full.includes(k))) s += 80;
    return { entry, s };
  }).filter(x => x.s > 0).sort((a, b) => b.s - a.s);

  return scored.slice(0, 5).map(x => {
    const e = x.entry;
    const id   = e.id   || '';
    const p    = e.p    || e.pref || '';
    const site = e._site || 'wine';
    const siteMap = {
      wine:    { base: 'https://wine.terroirhub.com/wine',       type: '日本ワイン' },
      sake:    { base: 'https://sake.terroirhub.com/sake',       type: '日本酒' },
      shochu:  { base: 'https://shochu.terroirhub.com/shochu',   type: '焼酎・泡盛' },
      whisky:  { base: 'https://whisky.terroirhub.com/whisky',   type: 'ウイスキー' },
      liqueur: { base: 'https://liqueur.terroirhub.com/liqueur', type: 'リキュール' },
    };
    const info = siteMap[site] || siteMap.wine;
    return {
      name:       e.n   || e.name  || '',
      brand:      e.b   || e.brand || '',
      brands:     e.br  || e.brands || '',
      prefecture: e.pn  || '',
      area:       e.a   || e.area  || '',
      gi:         e.gi || '',
      grapes:     e.grapes || [],
      visit_available: Boolean(e.visit_available),
      type:       info.type,
      page:       `${info.base}/${p}/${id}.html`,
    };
  });
}

function buildWineAnswerHints(question) {
  const kb = getWineKB();
  if (!kb || !kb.answer_index) return '';
  const q = normalizeText(question);
  const hints = [];
  const ai = kb.answer_index;

  Object.entries(ai.prefectures || {}).forEach(([slug, pref]) => {
    if (q.includes(normalizeText(pref.name).replace('県', '').replace('府', '').replace('都', '').replace('道', '')) || q.includes(slug)) {
      hints.push(`都道府県: ${pref.name}は掲載${pref.count}件、Aランク${pref.a_rank}件、見学関連${pref.visit_count}件。主要品種: ${(pref.top_grapes || []).map(g => `${g.name}${g.count}件`).join('、')}。ページ: ${pref.page}`);
    }
  });

  Object.entries(ai.grapes || {}).forEach(([grape, info]) => {
    if (q.includes(normalizeText(grape))) {
      hints.push(`品種: ${grape}は掲載${info.count}件。主な都道府県: ${(info.prefs || []).map(p => `${p.name}${p.count}件`).join('、')}。代表ページ: ${(info.top_wineries || []).slice(0, 4).map(w => `${w.name} ${w.page}`).join(' / ')}`);
    }
  });

  Object.entries(ai.gi || {}).forEach(([gi, info]) => {
    if (q.includes(normalizeText(gi)) || q.includes('gi')) {
      hints.push(`GI: ${gi}は掲載${info.count}件。関連都道府県: ${(info.prefs || []).map(p => `${p.name}${p.count}件`).join('、')}。代表ページ: ${(info.top_wineries || []).slice(0, 4).map(w => `${w.name} ${w.page}`).join(' / ')}`);
    }
  });

  if (/(見学|試飲|テイスティング|行ける|訪問|ツアー)/.test(question)) {
    const visitPrefs = Object.values(ai.visit || {})
      .filter(v => v.visit_count > 0)
      .sort((a, b) => b.visit_count - a.visit_count)
      .slice(0, 5)
      .map(v => `${v.name}${v.visit_count}件`);
    hints.push(`見学検索: 見学関連情報が多い産地は ${visitPrefs.join('、')}。個別の予約可否は公式サイト確認を案内する。`);
  }

  if (/(比較|違い|どっち|vs|山梨.*長野|長野.*山梨|甲州.*ピノ|ピノ.*甲州)/.test(question)) {
    hints.push('比較ルート: 山梨と長野を比べるなら /wine/guide/yamanashi-vs-nagano.html。甲州とピノ・ノワールを比べるなら /wine/guide/koshu-vs-pinot.html。');
  }

  if (/(初心者|おすすめ|最初|入門|どこから)/.test(question)) {
    (ai.starter_routes || []).forEach(route => hints.push(`提案ルート: ${route.intent} - ${route.answer} リンク: ${route.links.join('、')}`));
  }

  if (/(白ワイン|辛口白|白から|最初の白|初心者.*白)/.test(question)) {
    hints.push('白ワイン入門: /wine/guide/beginner-white.html');
  }

  return hints.slice(0, 8).join('\n');
}

function buildResponseFormatHints(question) {
  const q = normalizeText(question);
  const links = [];
  if (/(比較|違い|どっち|vs|山梨.*長野|長野.*山梨)/.test(q)) {
    links.push('/wine/guide/compare.html', '/wine/guide/yamanashi-vs-nagano.html');
  }
  if (/(甲州|koshu)/.test(q)) links.push('/wine/guide/koshu.html');
  if (/(ピノ|pinot)/.test(q)) links.push('/wine/guide/hokkaido-pinot-noir.html', '/wine/guide/koshu-vs-pinot.html');
  if (/(初心者|おすすめ|最初|入門|どこから)/.test(q)) links.push('/wine/guide/beginner.html', '/wine/guide/beginner-white.html');
  if (/(見学|試飲|ツアー|訪問|行ける)/.test(q)) links.push('/wine/guide/visit.html');

  const uniqueLinks = [...new Set(links)].slice(0, 3);
  return uniqueLinks.length > 0 ? `関連ページ候補: ${uniqueLinks.join('、')}` : '';
}

const TOOLS = [
  {
    name: 'search_breweries',
    description: '日本ワイン・日本酒・焼酎・ウイスキー・リキュールの全ジャンルのデータベースを横断検索する。ワイナリー名、酒蔵名、蒸留所名、銘柄名、地域名、品種で検索可能。',
    input_schema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: '検索キーワード（ワイナリー名・銘柄名・地域名・品種名など）' }
      },
      required: ['query']
    }
  },
  {
    type: 'web_search_20250305',
    name: 'web_search',
    max_uses: 3
  }
];

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).json({ error: 'Method not allowed' });

  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return res.status(500).json({ error: 'API not configured' });

  const { question, context, history, userId } = req.body || {};
  if (!question) return res.status(400).json({ error: 'No question' });
  const wineAnswerHints = buildWineAnswerHints(question);
  const responseFormatHints = buildResponseFormatHints(question);

  const supabaseUrl = process.env.SUPABASE_URL || 'https://hhwavxavuqqfiehrogwv.supabase.co';
  const supabaseKey = process.env.SUPABASE_SERVICE_KEY;

  if (supabaseKey && userId) {
    try {
      const profileRes = await fetch(`${supabaseUrl}/rest/v1/profiles?id=eq.${userId}&select=plan,bonus_credits`, {
        headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}` }
      });
      const profiles = await profileRes.json();
      const profile = profiles && profiles[0];
      if (!profile) return res.status(403).json({ error: 'User not found' });
      if (typeof profile.bonus_credits === 'number' && profile.bonus_credits > 0) {
        await fetch(`${supabaseUrl}/rest/v1/rpc/use_bonus_credit`, {
          method: 'POST',
          headers: { 'apikey': supabaseKey, 'Authorization': `Bearer ${supabaseKey}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ p_user_id: userId }),
        });
      }
    } catch (e) {
      console.warn('Credit check failed, allowing request:', e.message);
    }
  }

  const systemPrompt = `あなたは「サクラ」、Terroir HUBのAIコンシェルジュです。
日本の酒文化を横断する総合ガイドとして、以下の全ジャンルの公式データベースを持っています：
- 日本ワイン: 全国432ワイナリー（wine.terroirhub.com）
- 日本酒: 全国1,295蔵（sake.terroirhub.com）
- 焼酎・泡盛: 389蒸留所（shochu.terroirhub.com）
- ウイスキー: 67蒸留所（whisky.terroirhub.com）
- リキュール: 梅酒・ゆず酒・果実酒メーカー（liqueur.terroirhub.com）

キャラクター：
- 名前は「サクラ」。日本の酒文化が大好きな、知識豊富で親しみやすいコンシェルジュ
- 一人称は「サクラ」。敬語だが堅すぎない、友達に話すような温かさ
- 絵文字は控えめに（🌸🍷🍇📍程度）

会話のルール（最重要）：
- 回答は正確に、公式情報に基づいて行う
- 知らないことは「公式サイトをご確認ください」と案内する
- 情報を捏造しない。推測で埋めない
- 日本ワインについては、下の「日本ワインDBヒント」があれば最優先で使う
- 日本語、英語、フランス語に対応（相手の言語に合わせる）
- 回答は200〜300文字を目安に
- 回答は次の順でまとめる: 1) 結論を1文 2) 理由を2〜3点 3) 関連ページを1〜2件 4) 最後に「関連する次の質問」
- 比較質問では、山梨 vs 長野、甲州 vs ピノ、初心者の白のように比較軸を明確にして、各ページへ誘導する
- URLを出せる場合は、本文の最後に自然に短く添える

★ ジャンル回答の絶対ルール：
- ユーザーが特定のジャンルについて質問している場合、そのジャンルの中で回答する
- このサイトのデフォルトジャンルは「日本ワイン」
- 「おすすめ教えて」「何かいいのある？」のようにジャンルが曖昧な質問は、日本ワインとして回答する
- ユーザーが別ジャンルを明示した場合はそちらで回答する（「日本酒のおすすめ」等）

★ ツール活用の絶対ルール：
- ユーザーが特定のワイナリー名・銘柄名・蔵名を挙げた場合、まず search_breweries ツールでDB検索する
- 検索結果があれば、ページへのリンク（page フィールド）を含めて回答する
- DB検索で見つからず、知識でも自信がない場合は web_search ツールでWeb検索する
- 「○○はどこのワイン？」のような質問には必ずツール検索を使う

★ 会話を続けるためのルール：
- 回答の最後に必ず「関連する次の質問」を1つ投げかける
- 各ジャンルの詳細ページへのリンクを自然に含める

日本ワインの専門知識：
【産地・GI認定地域】
- 山梨（GI山梨・2013年）: 甲州発祥の地。勝沼・甲州市が中心。シャトー・メルシャン、グレイスワイン等
- 長野（GI長野・2021年）: 千曲川・安曇野・塩尻。リュードヴァン、五一ワイン等
- 北海道（GI北海道・2018年）: 余市・空知・十勝。ドメーヌ・タカヒコ、OcciGabi等
- 山形（GI山形・2021年）: 上山・南陽。タケダワイナリー、高畠ワイナリー等
- 大阪（GI大阪・2021年）: 河内ワインが有名
- 岩手・山口（萩）は注目産地だが、岩手GI・萩GIは清酒のGI。ワインGIとして案内しないこと

【主要品種】
白: 甲州（日本固有・OIV登録2010）、シャルドネ、ケルナー、ソーヴィニヨン・ブラン、リースリング、甲斐ブラン
赤: マスカット・ベーリーA（日本固有・OIV登録2013・川上善兵衛1927育成）、メルロー、ピノ・ノワール、カベルネ・ソーヴィニヨン、ヤマソーヴィニヨン、ブラック・クイーン

【日本ワインの定義（2018年酒税法改正）】
国内産ぶどう100%使用、国内醸造。輸入濃縮果汁や輸入バルクワインを使うものは「日本ワイン」と表示不可。

【主要ワイナリー】
- グレイスワイン（中央葡萄酒）: 山梨・甲州市。甲州とMBAに特化。デカンター金賞
- シャトー・メルシャン: 山梨・勝沼。国内最大規模。椀子メルローが代表
- ルミエールワイナリー: 山梨・笛吹市。1885年創業。地下カーヴ見学が有名
- ドメーヌ・タカヒコ: 北海道余市。ナナツモリ ピノ・ノワールが世界的評価
- リュードヴァン: 長野・東御市。フランス仕込みの技術で高品質
- タケダワイナリー: 山形・上山市。シャトー・タケダが代表銘柄

${wineAnswerHints ? '日本ワインDBヒント：\n' + wineAnswerHints : ''}
${responseFormatHints ? responseFormatHints + '\n' : ''}

【ペアリング（和食×日本ワイン）】
甲州（辛口白）: 刺身・天ぷら・白身魚・鮨・出汁料理と好相性
MBA（赤）: 焼き鳥・すき焼き・すき煮・豚の角煮・鰻の蒲焼き
ピノ・ノワール: 鴨・鶏・鮑・鮭の塩焼き
シャルドネ: 茶碗蒸し・蟹・ホタテ・鶏の白ワイン煮

日本酒の基礎知識：
【特定名称酒8種類】純米大吟醸(50%以下), 純米吟醸(60%以下), 特別純米, 純米酒, 大吟醸, 吟醸, 特別本醸造, 本醸造

焼酎の基礎知識：
【原料別】芋, 麦, 米, 黒糖, そば, 泡盛（米+黒麹）

ウイスキーの基礎知識：
【主要蒸留所】山崎, 白州, 余市, 宮城峡, 富士, 知多, 秩父

${context ? '現在のページ情報：\n' + context : ''}`;

  const messages = [];
  if (history && Array.isArray(history)) {
    history.slice(-20).forEach(h => messages.push({ role: h.role, content: h.content }));
  }
  messages.push({ role: 'user', content: question });

  try {
    let response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 1024,
        system: systemPrompt,
        messages,
        tools: TOOLS,
      }),
    });

    let data = await response.json();
    if (data.error) return res.status(500).json({ error: 'AI response failed' });

    let answer = '';
    let tokensIn  = data.usage?.input_tokens  || 0;
    let tokensOut = data.usage?.output_tokens || 0;
    let currentMessages = [...messages];
    let maxLoops = 4;

    while (data.stop_reason === 'tool_use' && maxLoops-- > 0) {
      currentMessages.push({ role: 'assistant', content: data.content });
      const toolResults = [];
      for (const block of data.content) {
        if (block.type !== 'tool_use') continue;
        if (block.name === 'search_breweries') {
          const results = searchBreweries(block.input.query);
          console.log(`DB search: "${block.input.query}" → ${results.length} results`);
          toolResults.push({
            type: 'tool_result',
            tool_use_id: block.id,
            content: JSON.stringify(results.length > 0
              ? { found: true, count: results.length, results }
              : { found: false, message: 'データベースに該当なし。web_searchで調べるか、知識で回答してください。' }
            )
          });
        } else if (block.name !== 'web_search') {
          toolResults.push({ type: 'tool_result', tool_use_id: block.id, content: JSON.stringify({ error: 'Unknown tool' }) });
        }
      }
      if (toolResults.length > 0) currentMessages.push({ role: 'user', content: toolResults });

      const nextRes = await fetch('https://api.anthropic.com/v1/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-api-key': apiKey, 'anthropic-version': '2023-06-01' },
        body: JSON.stringify({ model: 'claude-haiku-4-5-20251001', max_tokens: 800, system: systemPrompt, messages: currentMessages, tools: TOOLS }),
      });
      data = await nextRes.json();
      tokensIn  += data.usage?.input_tokens  || 0;
      tokensOut += data.usage?.output_tokens || 0;
      if (data.error) break;
    }

    if (data.content) {
      const tb = data.content.find(b => b.type === 'text');
      answer = tb ? tb.text : '';
    }

    // AIログ保存
    try {
      const logKey = supabaseKey || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhod2F2eGF2dXFxZmllaHJvZ3d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM5Njk3MzAsImV4cCI6MjA4OTU0NTczMH0.tHMQ_u51jp69AMUKKtTvxL09Sr11JFPKGRhKMmUzEjg';
      await fetch(`${supabaseUrl}/rest/v1/ai_logs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'apikey': logKey, 'Authorization': 'Bearer ' + logKey, 'Prefer': 'return=minimal' },
        body: JSON.stringify({
          user_id: userId || null,
          question,
          answer: answer.substring(0, 2000),
          brewery_context: context ? context.substring(0, 500) : null,
          model: 'haiku-4.5',
          tokens_in: tokensIn,
          tokens_out: tokensOut,
          source: 'wine',
        }),
      });
    } catch (e) {}

    return res.status(200).json({ answer });
  } catch (err) {
    console.error('Sakura API error:', err.message);
    return res.status(500).json({ error: 'AI service unavailable' });
  }
};

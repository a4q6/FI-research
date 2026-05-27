"""Render the merged catalog model to a single self-contained interactive HTML
page and a regenerated ``docs/data_catalog.md``.

The HTML embeds the whole model as JSON and renders client-side with vanilla JS
(no CDN), so it works offline and on a phone. Navigation is hash-based: the list
screen and per-dataset detail screen are two views toggled by ``location.hash``,
and relation chips are just links to ``#<dataset key>``.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

USAGE_LABEL = {"core": "◎核", "aux": "○補助", "edge": "△周辺", "none": "—"}


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>FI-research データカタログ</title>
<style>
  :root{
    --ink:#16202e; --muted:#5b6675; --line:#e2e7ef; --bg:#f4f6fa; --card:#fff;
    --accent:#1e40af; --core:#15803d; --aux:#b45309; --edge:#64748b;
    --todo:#b91c1c;
  }
  *{box-sizing:border-box}
  html{-webkit-text-size-adjust:100%}
  body{margin:0;font-family:-apple-system,"Hiragino Kaku Gothic ProN","Yu Gothic",Meiryo,sans-serif;
    color:var(--ink);background:var(--bg);line-height:1.65;font-size:15px}
  a{color:#1d4ed8;text-decoration:none}
  a:hover{text-decoration:underline}
  .topbar{position:sticky;top:0;z-index:20;background:#0f2540;color:#fff;
    padding:calc(10px + env(safe-area-inset-top)) 16px 10px;display:flex;align-items:center;gap:12px}
  .topbar h1{font-size:16px;margin:0;font-weight:700;flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .topbar .back{background:rgba(255,255,255,.15);border:0;color:#fff;border-radius:8px;
    padding:6px 12px;font-size:14px;cursor:pointer;display:none}
  .topbar .back.show{display:inline-block}
  .wrap{max-width:1000px;margin:0 auto;padding:14px 16px 60px}

  /* summary */
  .totals{display:flex;flex-wrap:wrap;gap:8px;margin:4px 0 14px}
  .totals .t{background:var(--card);border:1px solid var(--line);border-radius:10px;
    padding:8px 12px;flex:1;min-width:120px}
  .totals .t .k{font-size:11px;color:var(--muted)}
  .totals .t .v{font-size:18px;font-weight:700}
  .note{color:var(--muted);font-size:13px;margin:0 0 14px}

  /* search + filters */
  .search{width:100%;padding:11px 14px;border:1px solid var(--line);border-radius:10px;
    font-size:15px;background:#fff;margin-bottom:10px}
  .chips{display:flex;flex-wrap:wrap;gap:7px;margin-bottom:16px}
  .chip{border:1px solid var(--line);background:#fff;border-radius:18px;padding:5px 13px;
    font-size:12.5px;cursor:pointer;white-space:nowrap;color:var(--ink)}
  .chip.active{background:var(--accent);color:#fff;border-color:var(--accent)}
  .chip .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:5px;vertical-align:baseline}

  /* dataset list */
  .catgroup{margin-bottom:20px}
  .catgroup h2{font-size:14px;margin:0 0 8px;padding-left:10px;border-left:4px solid var(--c,#888);
    display:flex;align-items:center;gap:8px}
  .catgroup h2 small{color:var(--muted);font-weight:400}
  .dscard{display:block;background:var(--card);border:1px solid var(--line);border-radius:11px;
    padding:12px 14px;margin-bottom:8px;cursor:pointer;color:inherit}
  .dscard:hover{border-color:var(--accent);text-decoration:none}
  .dscard .row1{display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}
  .dscard .title{font-weight:700;font-size:15px}
  .dscard .key{font-size:11px;color:var(--muted);font-family:ui-monospace,monospace}
  .dscard .meta{font-size:12.5px;color:var(--muted);margin-top:3px}
  .pills{display:inline-flex;gap:5px;margin-left:auto}
  .pill{font-size:11px;font-weight:700;border-radius:5px;padding:1px 7px}
  .pill.A1{background:#e0f2fe;color:#0369a1}.pill.A2{background:#ffe4e9;color:#be123c}
  .docbar{height:4px;border-radius:3px;background:#eef2f7;margin-top:8px;overflow:hidden}
  .docbar > i{display:block;height:100%;background:var(--core)}
  .todobadge{background:#fee2e2;color:var(--todo);font-size:11px;font-weight:700;border-radius:5px;padding:1px 7px}

  /* detail */
  #detail{display:none}
  .dhead{margin:2px 0 10px}
  .dhead .cat{display:inline-block;font-size:12px;font-weight:700;color:#fff;border-radius:6px;padding:2px 10px}
  .dhead h2{font-size:21px;margin:8px 0 2px}
  .dhead .key{font-family:ui-monospace,monospace;font-size:12px;color:var(--muted)}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
  .grid .f{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:9px 11px}
  .grid .f .k{font-size:11px;color:var(--muted)}
  .grid .f .v{font-size:14px;font-weight:600;word-break:break-word}
  .grid .f .v code{font-size:12px}
  .callout{border:1px solid var(--line);border-left:4px solid var(--aux);background:#fffaf2;
    border-radius:9px;padding:11px 14px;margin:12px 0;font-size:13.5px}
  .callout b{color:var(--aux)}
  .sec-title{font-size:14px;font-weight:700;margin:20px 0 8px;display:flex;align-items:center;gap:8px}
  table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line);
    border-radius:10px;overflow:hidden;font-size:13px;margin-bottom:8px}
  th,td{padding:7px 10px;text-align:left;border-bottom:1px solid var(--line);vertical-align:top}
  th{background:#eef2f8;font-size:12px;color:#334}
  tr:last-child td{border-bottom:none}
  td code,.mono{font-family:ui-monospace,monospace;font-size:12px}
  .undoc{color:#b0b7c3}
  .relchip{display:inline-block;background:#f0e9ff;color:#6d28d9;border:1px solid #e3d6ff;
    border-radius:16px;padding:4px 12px;font-size:12.5px;margin:0 6px 6px 0;cursor:pointer}
  .relchip .kind{font-size:10px;opacity:.7}
  .erbox{background:var(--card);border:1px solid var(--line);border-radius:11px;padding:10px;overflow-x:auto;margin-bottom:18px}
  .erbox svg{display:block;min-width:560px;width:100%;height:auto}
  .collapse-btn{background:#eef2f7;border:1px solid var(--line);border-radius:7px;padding:4px 10px;
    font-size:12px;cursor:pointer;margin-bottom:8px}
  .hidden{display:none}
  .footer{color:var(--muted);font-size:12px;margin-top:30px;border-top:1px solid var(--line);padding-top:12px}
  @media (max-width:560px){
    .totals .t{min-width:46%}
    .dscard .pills{margin-left:0;width:100%;margin-top:6px}
  }
</style>
</head>
<body>
<div class="topbar">
  <button class="back" id="backBtn">← 一覧</button>
  <h1 id="topTitle">FI-research データカタログ</h1>
</div>
<div class="wrap">
  <div id="list">
    <div class="totals" id="totals"></div>
    <p class="note" id="metaNote"></p>
    <div id="erWrap"></div>
    <input class="search" id="search" placeholder="🔍 データセット・提供者・カラム名で検索…" autocomplete="off">
    <div class="chips" id="chips"></div>
    <div id="catalog"></div>
    <div id="pendingWrap"></div>
    <div id="todoWrap"></div>
  </div>
  <div id="detail"></div>
  <div class="footer" id="footer"></div>
</div>

<script id="data" type="application/json">__DATA_JSON__</script>
<script>
const MODEL = JSON.parse(document.getElementById('data').textContent);
const USAGE = {core:'◎ 核', aux:'○ 補助', edge:'△ 周辺', none:'—'};
const catColor = {}; const catLabel = {};
MODEL.categories.forEach(c => {catColor[c.key]=c.color; catLabel[c.key]=c.label;});
const byKey = {}; MODEL.datasets.forEach(d => byKey[d.key]=d);
let activeCat = 'all'; let query = '';

function esc(s){return (s==null?'':String(s)).replace(/[&<>]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[m]));}
function cov(d){return d.start ? (d.start+' → '+(d.end||'')) : '—';}

// ---- summary + filters ----
function renderTotals(){
  const t = MODEL.totals;
  document.getElementById('totals').innerHTML =
    [['データセット',t.datasets],['parquet',t.files],['総行数',t.rows.toLocaleString()],['総サイズ',t.size]]
    .map(([k,v])=>`<div class="t"><div class="k">${k}</div><div class="v">${v}</div></div>`).join('');
  document.getElementById('metaNote').textContent =
    (MODEL.meta.note||'') + '　（ビルド: '+MODEL.built+'）';
  const todos = MODEL.todos||[];
  document.getElementById('todoWrap').innerHTML = todos.length ?
    `<div class="callout"><b>未整備 / ドリフト ${todos.length} 件</b><ul style="margin:6px 0 0;padding-left:18px">`+
    todos.map(t=>`<li>${esc(t)}</li>`).join('')+`</ul></div>` : '';
}
function renderChips(){
  const cats = ['all', ...MODEL.categories.map(c=>c.key)];
  document.getElementById('chips').innerHTML = cats.map(c=>{
    const lab = c==='all'?'すべて':catLabel[c];
    const dot = c==='all'?'':`<span class="dot" style="background:${catColor[c]}"></span>`;
    return `<span class="chip ${c===activeCat?'active':''}" data-cat="${c}">${dot}${lab}</span>`;
  }).join('');
  document.querySelectorAll('#chips .chip').forEach(el=>el.onclick=()=>{activeCat=el.dataset.cat;renderChips();renderList();});
}
function matches(d){
  if(activeCat!=='all' && d.category!==activeCat) return false;
  if(!query) return true;
  const hay = (d.title+' '+d.key+' '+(d.provider||'')+' '+catLabel[d.category]+' '+
    d.columns.map(c=>c.name).join(' ')).toLowerCase();
  return hay.includes(query);
}
function usagePills(d){
  let s='';
  if(d.usage.A1 && d.usage.A1!=='none') s+=`<span class="pill A1">A1 ${USAGE[d.usage.A1]||d.usage.A1}</span>`;
  if(d.usage.A2 && d.usage.A2!=='none') s+=`<span class="pill A2">A2 ${USAGE[d.usage.A2]||d.usage.A2}</span>`;
  return s?`<span class="pills">${s}</span>`:'';
}

// ---- list screen ----
function renderList(){
  const groups = {};
  MODEL.datasets.filter(matches).forEach(d=>{(groups[d.category]=groups[d.category]||[]).push(d);});
  let html='';
  MODEL.categories.forEach(c=>{
    const ds = groups[c.key]; if(!ds) return;
    html += `<div class="catgroup"><h2 style="--c:${c.color}">${c.label} <small>${ds.length}</small></h2>`;
    ds.forEach(d=>{
      const doc = Math.round(d.documented_ratio*100);
      const miss = d.missing?`<span class="todobadge">ファイル無し</span>`:'';
      html += `<a class="dscard" href="#${d.key}">
        <div class="row1"><span class="title">${esc(d.title)}</span> <span class="key">${d.key}</span>${miss}${usagePills(d)}</div>
        <div class="meta">${esc(d.provider||'')}・${esc(d.frequency||'')}・${cov(d)}・${d.rows.toLocaleString()} 行・${d.n_columns} 列・${d.size}</div>
        <div class="docbar" title="カラム定義 ${doc}%"><i style="width:${doc}%"></i></div>
      </a>`;
    });
    html+='</div>';
  });
  document.getElementById('catalog').innerHTML = html || '<p class="note">該当なし</p>';
}

// ---- identifier relation ER mini-map ----
function renderER(){
  document.getElementById('erWrap').innerHTML = `<div class="sec-title">識別子リレーション（エンティティ結合）</div>
  <div class="erbox"><svg viewBox="0 0 720 150">
    <defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#475569"/></marker></defs>
    <g font-size="12" font-family="inherit">
      ${erNode(20,55,'edgar','EDGAR','cik / adsh')}
      ${erNode(210,55,'sec_tickers','SEC tickers','cik · ticker')}
      ${erNode(410,55,'openfigi_mapping','OpenFIGI','ticker → figi')}
      <g stroke="#475569" stroke-width="1.6" marker-end="url(#ar)">
        <path d="M190,80 L210,80" fill="none"/>
        <path d="M380,80 L410,80" fill="none"/>
      </g>
      <text x="200" y="74" font-size="10" fill="#475569" text-anchor="middle">cik</text>
      <text x="395" y="74" font-size="10" fill="#475569" text-anchor="middle">ticker</text>
      <rect x="600" y="60" width="100" height="40" rx="9" fill="#fff" stroke="#dc2626" stroke-dasharray="5 4"/>
      <text x="650" y="78" text-anchor="middle" fill="#b91c1c" font-weight="700">ISIN</text>
      <text x="650" y="93" text-anchor="middle" font-size="10" fill="#b91c1c">⚠ 欠落(仕様)</text>
      <path d="M510,80 L600,80" stroke="#dc2626" stroke-width="1.4" stroke-dasharray="5 4" fill="none"/>
      <text x="555" y="74" font-size="10" fill="#b91c1c" text-anchor="middle">未接続</text>
      <text x="650" y="120" text-anchor="middle" font-size="10" fill="#64748b">→ 社債ID(CUSIP/ISIN)は WRDS/TRACE 必須</text>
    </g>
  </svg></div>`;
  document.querySelectorAll('#erWrap [data-go]').forEach(el=>el.style.cursor='pointer');
}
function erNode(x,y,key,label,sub){
  return `<g data-go="${key}" onclick="location.hash='${key}'" style="cursor:pointer">
    <rect x="${x}" y="${y-15}" width="170" height="48" rx="9" fill="#fff" stroke="#9333ea"/>
    <text x="${x+85}" y="${y+3}" text-anchor="middle" font-weight="700">${label}</text>
    <text x="${x+85}" y="${y+19}" text-anchor="middle" font-size="10" fill="#64748b">${sub}</text></g>`;
}

// ---- detail screen ----
function renderDetail(key){
  const d = byKey[key]; if(!d){location.hash='';return;}
  const c = d.category, color = catColor[c]||'#888';
  let h = `<div class="dhead"><span class="cat" style="background:${color}">${catLabel[c]||c}</span>
    <h2>${esc(d.title)}</h2><div class="key">${d.key}</div></div>`;

  // meta grid
  const f=(k,v)=>v?`<div class="f"><div class="k">${k}</div><div class="v">${v}</div></div>`:'';
  const imp = d.loader?`<code>${esc(d.loader)}</code>`:'';
  const url = d.upstream_url?`<a href="${esc(d.upstream_url)}" target="_blank" rel="noopener">upstream ↗</a>`:'';
  h += `<div class="grid">
    ${f('提供者',esc(d.provider))}${f('頻度',esc(d.frequency))}${f('期間',cov(d))}
    ${f('行数',d.rows.toLocaleString())}${f('ファイル数',d.n_files)}${f('サイズ',d.size)}
    ${f('カラム数',d.n_columns)}${f('結合キー',d.date_col?('<code>'+d.date_col+'</code>'):'—')}
    ${f('loader',imp)}${f('取得元',url)}</div>`;

  if(d.usage.A1||d.usage.A2) h+=`<div style="margin:0 0 10px">${usagePills(d)||''}</div>`;
  if(d.citation) h+=`<div class="callout" style="border-left-color:#64748b;background:#f7f9fc"><b style="color:#475569">引用</b> ${esc(d.citation)}</div>`;
  if(d.license || (d.caveats&&d.caveats.length)){
    h+=`<div class="callout"><b>ライセンス / 注意</b>`;
    if(d.license) h+=`<div>${esc(d.license)}</div>`;
    if(d.caveats&&d.caveats.length) h+=`<ul style="margin:6px 0 0;padding-left:18px">`+d.caveats.map(x=>`<li>${esc(x)}</li>`).join('')+`</ul>`;
    h+=`</div>`;
  }

  // relations
  if(d.relations&&d.relations.length){
    h+=`<div class="sec-title">リレーション</div>`;
    h+=d.relations.map(r=>{
      const tgt=byKey[r.to]; const tl=tgt?tgt.title:r.to;
      const on = r.from?`${r.from} ↔ ${r.on||r.from}`:(d.date_col||'date');
      return `<span class="relchip" onclick="location.hash='${r.to}'">${esc(tl)} <span class="kind">[${on}]</span></span>`;
    }).join('');
  }

  // members
  if(d.members && d.members.length>1){
    h+=`<div class="sec-title">メンバー <small style="color:var(--muted);font-weight:400">（${d.members.length} ファイル）</small></div>`;
    if(d.members_note) h+=`<p class="note">${esc(d.members_note)}</p>`;
    h+=`<table><tr><th>名前</th><th>行数</th><th>期間</th><th>サイズ</th></tr>`+
      d.members.map(m=>`<tr><td class="mono">${esc(m.name)}</td><td>${m.rows.toLocaleString()}</td><td>${m.start?esc(m.start)+'→'+esc(m.end||''):'—'}</td><td>${m.size}</td></tr>`).join('')+`</table>`;
  } else if(d.members_note){
    h+=`<p class="note">${esc(d.members_note)}</p>`;
  }

  // schema
  h+=`<div class="sec-title">スキーマ <small style="color:var(--muted);font-weight:400">（${d.n_columns} 列・定義 ${Math.round(d.documented_ratio*100)}%）</small></div>`;
  const many = d.columns.length>25;
  const rowsHtml = d.columns.map((col,i)=>{
    const cls = many&&i>=25?'colrow hidden':'colrow';
    const defn = col.definition?esc(col.definition):'<span class="undoc">— 未定義</span>';
    return `<tr class="${cls}"><td class="mono">${esc(col.name)}</td><td class="mono" style="color:#64748b">${esc(col.dtype)}</td><td>${defn}</td></tr>`;
  }).join('');
  if(many) h+=`<button class="collapse-btn" id="moreBtn">残り ${d.columns.length-25} 列を表示</button>`;
  h+=`<table><tr><th>カラム</th><th>型</th><th>定義</th></tr>${rowsHtml}</table>`;

  document.getElementById('detail').innerHTML = h;
  const mb=document.getElementById('moreBtn');
  if(mb) mb.onclick=()=>{document.querySelectorAll('.colrow.hidden').forEach(r=>r.classList.remove('hidden'));mb.remove();};
}

// ---- routing ----
function route(){
  const key = decodeURIComponent(location.hash.replace(/^#/,''));
  const isDetail = key && byKey[key];
  document.getElementById('list').style.display = isDetail?'none':'block';
  document.getElementById('detail').style.display = isDetail?'block':'none';
  document.getElementById('backBtn').classList.toggle('show', !!isDetail);
  document.getElementById('topTitle').textContent = isDetail?byKey[key].title:'FI-research データカタログ';
  if(isDetail){renderDetail(key);window.scrollTo(0,0);}
  else if(key){location.hash='';}
}
document.getElementById('backBtn').onclick=()=>{location.hash='';};
document.getElementById('search').oninput=e=>{query=e.target.value.trim().toLowerCase();renderList();};
window.addEventListener('hashchange',route);

function renderPending(){
  const p = MODEL.pending||[];
  if(!p.length){document.getElementById('pendingWrap').innerHTML='';return;}
  const rows = p.map(x=>`<tr><td>${esc(x.priority||'')}</td><td><b>${esc(x.data)}</b></td>
    <td>${esc(x.provider||'')}</td><td>${esc(x.status||'')}</td>
    <td><span class="pill ${x.theme}">${esc(x.theme||'')}</span></td><td>${esc(x.note||'')}</td></tr>`).join('');
  document.getElementById('pendingWrap').innerHTML =
    `<div class="sec-title">未取得データ（取得可 / 取得困難）<small style="color:var(--muted);font-weight:400">${p.length} 件</small></div>
     <table><tr><th>優先</th><th>データ</th><th>提供者</th><th>状態</th><th>テーマ</th><th>メモ</th></tr>${rows}</table>`;
}

renderTotals();renderChips();renderER();renderList();renderPending();
document.getElementById('footer').innerHTML = '生成: <code>python -m fi_research.catalog build</code> ｜ 知識層: <code>docs/catalog/catalog_meta.yaml</code> ｜ 自動層: data/processed の parquet footer';
route();
</script>
</body>
</html>
"""


def render_html(model: dict) -> str:
    model = dict(model)
    model["built"] = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    data_json = json.dumps(model, ensure_ascii=False)
    # guard against closing the script tag from within the JSON
    data_json = data_json.replace("</", "<\\/")
    return _HTML_TEMPLATE.replace("__DATA_JSON__", data_json)


# ---------------------------------------------------------------------------
# Markdown (regenerated mirror of the catalog)
# ---------------------------------------------------------------------------


def render_markdown(model: dict) -> str:
    t = model["totals"]
    built = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    cat_label = {c["key"]: c["label"] for c in model["categories"]}
    lines: list[str] = []
    A = lines.append

    A("# データカタログ（FI-research）")
    A("")
    A("> ⚙️ **このファイルは自動生成**です。手で編集せず、`docs/catalog/catalog_meta.yaml` を更新して")
    A("> `python -m fi_research.catalog build` を実行してください。インタラクティブ版は")
    A("> [`docs/catalog/data_catalog.html`](catalog/data_catalog.html)。")
    A("")
    A(f"最終ビルド: **{built}**　｜　{model['meta'].get('note','').strip()}")
    A("")
    A(f"**合計**: データセット {t['datasets']}／parquet {t['files']}／総行数 {t['rows']:,}／サイズ {t['size']}")
    A("")
    A("## マスタ表")
    A("")
    A("| カテゴリ | データセット | 提供者 | 頻度 | 期間 | 行数 | サイズ | A1 | A2 |")
    A("|---|---|---|---|---|---:|---:|:--:|:--:|")
    for c in model["categories"]:
        for d in model["datasets"]:
            if d["category"] != c["key"]:
                continue
            cov = f"{d['start']}→{d['end']}" if d.get("start") else "—"
            u1 = USAGE_LABEL.get(d["usage"].get("A1"), "")
            u2 = USAGE_LABEL.get(d["usage"].get("A2"), "")
            A(
                f"| {cat_label.get(c['key'], c['key'])} | {d['title']} (`{d['key']}`) | {d.get('provider') or ''} | "
                f"{d.get('frequency') or ''} | {cov} | {d['rows']:,} | {d['size']} | {u1} | {u2} |"
            )
    A("")

    # per-dataset detail sections
    A("## データセット詳細")
    A("")
    for d in model["datasets"]:
        A(f"### {d['title']} — `{d['key']}`")
        A("")
        bits = [
            f"- **カテゴリ**: {cat_label.get(d['category'], d['category'])}",
            f"- **提供者 / 頻度**: {d.get('provider') or '—'} ／ {d.get('frequency') or '—'}",
            f"- **期間 / 行数 / 列数**: {(d.get('start') or '—')} → {(d.get('end') or '')} ／ {d['rows']:,} ／ {d['n_columns']}",
            f"- **loader**: `{d.get('loader') or '—'}`",
        ]
        if d.get("upstream_url"):
            bits.append(f"- **取得元**: {d['upstream_url']}")
        if d.get("citation"):
            bits.append(f"- **引用**: {d['citation']}")
        if d.get("license"):
            bits.append(f"- **ライセンス**: {d['license']}")
        for cav in d.get("caveats", []):
            bits.append(f"- ⚠️ {cav}")
        if d.get("members_note"):
            bits.append(f"- メンバー: {d['members_note']}")
        for r in d.get("relations", []):
            on = f"{r['from']} ↔ {r.get('on', r['from'])}" if r.get("from") else "date"
            bits.append(f"- 🔗 `{r['to']}` ({on})")
        lines.extend(bits)
        A("")
        documented = [c for c in d["columns"] if c["definition"]]
        if documented:
            A("| カラム | 型 | 定義 |")
            A("|---|---|---|")
            for col in d["columns"]:
                if col["definition"]:
                    A(f"| `{col['name']}` | {col['dtype']} | {col['definition']} |")
            A("")

    if model.get("pending"):
        A("## 未取得データ（取得可 / 取得困難）")
        A("")
        A("| 優先 | データ | 提供者 | 状態 | テーマ | メモ |")
        A("|---|---|---|---|:--:|---|")
        for p in model["pending"]:
            A(
                f"| {p.get('priority','')} | {p.get('data','')} | {p.get('provider','')} | "
                f"{p.get('status','')} | {p.get('theme','')} | {p.get('note','')} |"
            )
        A("")

    if model.get("todos"):
        A("## 未整備 / ドリフト")
        A("")
        for todo in model["todos"]:
            A(f"- {todo}")
        A("")

    A("## 関連ドキュメント")
    A("")
    A("- [`data_sources.md`](data_sources.md) — 各 loader の取得・スキーマ詳細")
    A("- [`catalog/catalog_meta.yaml`](catalog/catalog_meta.yaml) — 知識層（編集する真実源）")
    A("- [`catalog/data_catalog.html`](catalog/data_catalog.html) — インタラクティブ版")
    A("")
    return "\n".join(lines)

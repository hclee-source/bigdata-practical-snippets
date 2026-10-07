"""index.html 생성.  실행: python build.py

카드 내용은 cards.py, 「언제 쓰나」 문구는 when.py 에서 고친다. index.html 을 직접 고치지 말 것.
"""
import re, html, sys, hashlib
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
from cards import SECTIONS
from when import WHEN

KW = r'\b(?:import|from|as|def|for|in|return|if|else|lambda|None|True|False|not|and|or|with)\b'
TOK = re.compile(r"(?P<c>#[^\n]*)|(?P<s>'[^'\n]*'|\"[^\"\n]*\")|(?P<k>%s)|(?P<n>\b\d+(?:\.\d+)?\b)|(?P<f>\b[A-Za-z_]\w*(?=\())" % KW)
def hl(code):
    out=[]; i=0
    for m in TOK.finditer(code):
        out.append(html.escape(code[i:m.start()], quote=False))
        out.append(f'<span class="{m.lastgroup}">{html.escape(m.group(), quote=False)}</span>')
        i=m.end()
    out.append(html.escape(code[i:], quote=False))
    return ''.join(out)

GROUPS = [('t1', '작업형 1', '데이터 처리'), ('t2', '작업형 2', '모델 · 제출'), ('t3', '작업형 3', '통계 검정'), ('env', '시험장', '도움말 · 출력')]
def gid(sid): return next(g for g, *_ in GROUPS if sid.startswith(g))
def short(t): return t.split('·', 1)[1].strip() if t.startswith('작업형') else t

missing = [c[0] for s in SECTIONS for c in s['cards'] if c[0] not in WHEN]
assert not missing, missing
TOTAL = sum(len(s['cards']) for s in SECTIONS)
HOT = sum(c[2] for s in SECTIONS for c in s['cards'])

# ── 목차 ──
toc = []
for g, gname, gsub in GROUPS:
    secs = [(i, s) for i, s in enumerate(SECTIONS) if gid(s['id']) == g]
    n = sum(len(s['cards']) for _, s in secs)
    toc.append(f'<div class="toc-group" data-g="{g}"><div class="toc-head"><span>{gname}</span><em>{gsub}</em></div><ol>')
    for i, s in secs:
        toc.append(f'<li><a href="#{s["id"]}" data-sec="{s["id"]}"><span class="toc-no">{i+1:02d}</span><span class="toc-t">{html.escape(short(s["title"]))}</span><span class="toc-c" data-count="{s["id"]}">{len(s["cards"])}</span></a></li>')
    toc.append('</ol></div>')

# ── 본문 ──
body = []
for i, s in enumerate(SECTIONS):
    g = gid(s['id']); gname = next(x[1] for x in GROUPS if x[0] == g)
    rows = []
    for j, (title, tag, hot, kw, code) in enumerate(s['cards']):
        # id 는 제목에서 만든다 — 카드를 끼워 넣어도 다른 카드의 외움 기록이 밀리지 않게
        aid = f'{s["id"]}-{hashlib.md5(title.encode()).hexdigest()[:6]}'
        old = f'{s["id"]}-{j+1}'   # 예전 순번 id — 외움 기록 옮기기용
        flag = f'<span class="flag">{html.escape(tag)}</span>' if hot else f'<span class="lib">{html.escape(tag)}</span>'
        rows.append(f'''<article class="snip{' is-hot' if hot else ''}" id="{aid}" data-old="{old}" data-g="{g}" data-hot="{int(hot)}" data-k="{html.escape(kw)}">
  <span class="snip-no" aria-hidden="true">{i+1:02d}.{j+1}</span>
  <div class="meta">
    {flag}
    <h3 data-t="{html.escape(title)}">{html.escape(title)}</h3>
    <p class="when">{html.escape(WHEN[title])}</p>
    <div class="acts">
      <button type="button" class="act copy" aria-label="{html.escape(title)} 코드 복사"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="5" y="5" width="8.5" height="8.5" rx="1.6"/><path d="M3.2 10.8V3.6c0-.9.7-1.6 1.6-1.6h6"/></svg><span>복사</span></button>
      <button type="button" class="act done" aria-pressed="false" aria-label="{html.escape(title)} 외웠어요"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.4l2.9 2.8 6.1-6.4"/></svg><span>외웠어요</span></button>
    </div>
  </div>
  <div class="code">
    <pre><code>{hl(code)}</code></pre>
    <button type="button" class="reveal">눌러서 코드 보기</button>
  </div>
</article>''')
    body.append(f'''<section id="{s['id']}" data-g="{g}">
  <header class="sec-head">
    <span class="sec-no">{i+1:02d}</span>
    <h2><small>{gname}</small>{html.escape(short(s['title']))}</h2>
    <p class="sec-desc">{html.escape(s['desc'])}</p>
  </header>
  <div class="rows">
{chr(10).join(rows)}
  </div>
</section>''')

CSS = r'''
:root{
  --bg:#ffffff; --bg-2:#f5f6f6; --ink:#141817; --ink-2:#464d4a; --muted:#6b726f; --faint:#a3a9a6;
  --rule:#e4e7e6; --accent:#2b2f9c; --accent-wash:#eceefa; --on-accent:#ffffff; --mark:#fff27a;
  --k:#2b2f9c; --s:#1d6b34; --c:#6b726f; --done:#1e7a37;
  --brand:#2b2f9c; --brand-fg:#f5e400; --brand-2:#ffffff; --brand-rule:rgba(255,255,255,.22); --hl:#f5e400; --hl-ink:#141817;
  --top-bg:rgba(255,255,255,.9); --veil:rgba(255,255,255,.35); --veil-on:rgba(255,255,255,.6);
  --toast-bg:#141817; --toast-fg:#ffffff; --shadow:rgba(20,24,23,.18); --scrim:rgba(20,24,23,.28);
  --side:272px;
  --sans:"IBM Plex Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Consolas,"IBM Plex Sans KR",monospace;
  color-scheme:light dark;
}
@media (prefers-color-scheme:dark){:root{
  --bg:#0f1211; --bg-2:#171b1a; --ink:#e7ebe9; --ink-2:#b2bab6; --muted:#8a928e; --faint:#4f5653;
  --rule:#252b29; --accent:#a7acff; --accent-wash:#1d1f3d; --on-accent:#0f1211; --mark:#4d4710;
  --k:#a7acff; --s:#86d39a; --c:#8a928e; --done:#7fd69a;
  --brand:#23267f; --brand-fg:#f5e400; --brand-2:#ffffff; --brand-rule:rgba(255,255,255,.18); --hl:#f5e400; --hl-ink:#141817;
  --top-bg:rgba(15,18,17,.88); --veil:rgba(15,18,17,.3); --veil-on:rgba(15,18,17,.55);
  --toast-bg:#e7ebe9; --toast-fg:#0f1211; --shadow:rgba(0,0,0,.5); --scrim:rgba(0,0,0,.45);
}}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-padding-top:128px}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.65;word-break:keep-all;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
button{font:inherit;color:inherit;cursor:pointer}
a{color:inherit}
:focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:2px}
::selection{background:var(--accent-wash)}

/* ── 사이드 목차 ── */
.side{position:fixed;inset:0 auto 0 0;width:var(--side);background:var(--bg);border-right:1px solid var(--rule);display:flex;flex-direction:column;z-index:30}
.brand{padding:26px 28px 20px;background:var(--brand);color:var(--brand-2)}
.brand>i{display:block;font-style:normal;font-size:11.5px;font-weight:600;letter-spacing:.04em;color:var(--brand-fg);margin-bottom:6px}
.brand>b{display:block;font-size:17px;font-weight:600;letter-spacing:-.02em;color:var(--brand-fg)}
.brand>small{display:block;color:var(--brand-2);opacity:.8;font-size:12.5px;margin-top:2px}
.progress{margin-top:22px}
.progress-row{display:flex;justify-content:space-between;align-items:baseline;font-size:12.5px;color:var(--brand-2);opacity:.9}
.progress-row strong{font-weight:500;color:var(--brand-2);font-variant-numeric:tabular-nums}
.progress-row strong b{font-size:15px;font-weight:600;color:var(--brand-fg)}
.progress-row strong span{font-weight:400}
.bar{height:3px;background:var(--brand-rule);margin-top:8px}
.bar i{display:block;height:100%;width:0;background:var(--brand-fg);transition:width .3s cubic-bezier(.2,.7,.2,1)}
.toc{flex:1;overflow-y:auto;padding:4px 0 20px}
.toc-group{margin-top:18px}
.toc-head{display:flex;align-items:baseline;justify-content:space-between;padding:0 28px 6px;font-size:12px;font-weight:600;color:var(--ink)}
.toc-head em{font-style:normal;font-weight:400;color:var(--muted)}
.toc ol{list-style:none;margin:0;padding:0}
.toc a{position:relative;display:flex;align-items:baseline;gap:12px;padding:6px 28px;text-decoration:none;color:var(--ink-2);font-size:13.5px;transition:color .15s}
.toc a:hover{color:var(--ink)}
.toc a.on{color:var(--ink);font-weight:600}
.toc a.on::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:2px;background:var(--accent)}
.toc-no{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;width:16px;font-weight:400}
.toc-t{flex:1;min-width:0}
.toc-c{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;font-weight:400}
.toc a.dim{color:var(--faint)}
.toc a.dim .toc-no,.toc a.dim .toc-c{color:var(--faint)}
.side-foot{padding:14px 28px 20px;border-top:1px solid var(--rule);font-size:12px;color:var(--muted);line-height:1.9}
.side-foot button{border:0;background:none;padding:4px 0;color:var(--muted);font-size:12px;text-decoration:underline;text-underline-offset:3px}
.side-foot button:hover{color:var(--ink)}
kbd{font:500 11px/1 var(--mono);border:1px solid var(--rule);border-radius:3px;padding:2px 5px;color:var(--ink-2);background:var(--bg)}

/* ── 상단 도구 ── */
.main{margin-left:var(--side);min-height:100vh}
.top{position:sticky;top:0;z-index:20;background:var(--top-bg);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid var(--rule)}
.top-in{max-width:1000px;margin:0 auto;padding:16px 48px 0}
.search{position:relative;display:flex;align-items:center}
.sbox>svg{position:absolute;left:0;width:17px;height:17px;fill:none;stroke:var(--muted);stroke-width:1.6}
#q{width:100%;height:40px;padding:0 120px 0 28px;border:0;border-radius:0;background:transparent;font:inherit;font-size:16px;color:var(--ink);outline:none}
#q::placeholder{color:var(--muted)}
#q::-webkit-search-cancel-button{-webkit-appearance:none;display:none}
.sbox:focus-within>svg{stroke:var(--ink)}
.sbox:focus-within{box-shadow:inset 0 -2px 0 var(--accent)}
.search .hint{position:absolute;right:0;display:flex;align-items:center;gap:10px;font-size:12.5px;color:var(--muted)}
#clear{display:none;border:0;background:none;padding:2px 0;font-size:12.5px;color:var(--ink-2);text-decoration:underline;text-underline-offset:3px}
body.filtering .hero{display:none}
body.filtering section.first-shown{padding-top:28px}
.filters{display:flex;align-items:center;gap:22px;margin-top:10px}
.seg{display:flex;gap:22px;align-self:stretch}
.seg button{position:relative;border:0;background:none;padding:10px 0 12px;font-size:13.5px;font-weight:500;color:var(--muted);white-space:nowrap;transition:color .15s}
.seg button:hover{color:var(--ink)}
.seg button[aria-pressed="true"]{color:var(--ink);font-weight:600}
.seg button[aria-pressed="true"]::after{content:"";position:absolute;left:0;right:0;bottom:-1px;height:2px;background:var(--accent)}
.sep{width:1px;height:14px;background:var(--rule)}
.tog{display:inline-flex;align-items:center;gap:8px;border:0;background:none;padding:10px 0 12px;font-size:13px;color:var(--ink-2);white-space:nowrap;transition:color .15s}
.tog:hover{color:var(--ink)}
.tog i{position:relative;width:13px;height:13px;border:1.5px solid var(--muted);border-radius:2px;flex:none;transition:background-color .15s,border-color .15s}
.tog[aria-pressed="true"]{color:var(--ink)}
.tog[aria-pressed="true"] i{background:var(--accent);border-color:var(--accent)}
.tog[aria-pressed="true"] i::after{content:"";position:absolute;left:3px;top:0;width:3.5px;height:7px;border:solid var(--on-accent);border-width:0 1.5px 1.5px 0;transform:rotate(45deg)}
.tog.link svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round}
.count{margin-left:auto;padding:10px 0 12px;font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.count b{color:var(--ink);font-weight:600}
#menu{display:none}

/* ── 본문 ── */
.content{max-width:1000px;margin:0 auto;padding:0 48px 96px}
.hero{padding:56px 0 0;max-width:640px}
.hero .kicker{display:inline-block;margin:0 0 14px;font-size:12.5px;font-weight:600;color:var(--accent);letter-spacing:.02em}
.hero h1{margin:0;font-size:32px;line-height:1.3;letter-spacing:-.025em;font-weight:600;text-wrap:balance}
.hero p{margin:14px 0 0;color:var(--ink-2);font-size:15.5px;text-wrap:pretty}
.legend{display:flex;gap:28px;flex-wrap:wrap;margin-top:22px;font-size:13px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:8px}
.legend .tick{width:22px;height:12px;background:var(--hl)}
section{padding-top:64px}
.sec-head{display:grid;grid-template-columns:56px 1fr;column-gap:0;padding-top:14px;border-top:1px solid var(--ink)}
.sec-no{font-size:13px;font-weight:500;color:var(--muted);font-variant-numeric:tabular-nums;padding-top:6px}
.sec-head h2{margin:0;font-size:22px;letter-spacing:-.02em;line-height:1.35;font-weight:600}
.sec-head h2 small{display:block;font-size:12.5px;font-weight:500;letter-spacing:0;color:var(--muted);margin-bottom:4px}
.sec-desc{grid-column:2;margin:6px 0 0;color:var(--ink-2);font-size:14px;max-width:620px;text-wrap:pretty}
.rows{margin-top:18px}

.snip{display:grid;grid-template-columns:56px 216px minmax(0,1fr);gap:0;padding:26px 0;border-top:1px solid var(--rule);position:relative}
.snip-no{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums;padding-top:3px}
.snip.is-hot .snip-no{color:var(--accent);font-weight:600}
.meta{min-width:0;padding-right:28px}
.flag{display:inline-block;font-size:11.5px;font-weight:600;color:var(--hl-ink);background:var(--hl);padding:0 5px;border-radius:1px;letter-spacing:.01em;margin-bottom:6px}
.lib{display:block;font:400 12px/1.6 var(--mono);color:var(--muted);margin-bottom:4px}
.snip h3{margin:0;font-size:15.5px;line-height:1.45;letter-spacing:-.01em;font-weight:600;text-wrap:balance}
.snip h3 mark{background:var(--mark);color:inherit;padding:0 1px}
.when{margin:6px 0 0;font-size:13.5px;line-height:1.6;color:var(--ink-2);text-wrap:pretty}
.acts{display:flex;gap:16px;margin-top:14px}
.act{display:inline-flex;align-items:center;gap:6px;height:24px;padding:0;border:0;background:none;font-size:12.5px;color:var(--muted);transition:color .15s}
.act:hover{color:var(--ink)}
.act:active{transform:translateY(1px)}
.act svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.act.copied{color:var(--accent)}
.done[aria-pressed="true"]{color:var(--done);font-weight:600}
.snip.is-done h3{color:var(--ink-2)}
.code{position:relative;min-width:0}
.code pre{margin:0;background:var(--bg-2);border-radius:4px;padding:16px 20px;overflow-x:auto;font:400 13px/1.7 var(--mono);color:var(--ink);tab-size:4;font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0}
.code pre .k{color:var(--k);font-weight:500}
.code pre .s{color:var(--s)}
.code pre .c{color:var(--c)}
.code pre .n,.code pre .f{color:inherit}
.reveal{display:none}
body.memo .snip:not(.shown) pre{filter:blur(5px);user-select:none;opacity:.5}
body.memo .snip:not(.shown) .reveal{display:flex;position:absolute;inset:0;align-items:center;justify-content:center;border:1px solid var(--rule);background:var(--veil);border-radius:4px;font-size:13px;font-weight:500;color:var(--ink);transition:background-color .15s}
body.memo .snip:not(.shown) .reveal:hover{background:var(--veil-on)}

.empty{display:none;padding:88px 0;color:var(--ink-2)}
.empty b{display:block;font-size:18px;font-weight:600;color:var(--ink);margin-bottom:6px}
.empty button{margin-top:18px;border:0;background:none;padding:0;color:var(--ink);font-weight:600;font-size:14px;text-decoration:underline;text-underline-offset:4px}
.foot{margin-top:72px;padding-top:18px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--muted)}
.toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,8px);background:var(--toast-bg);color:var(--toast-fg);font-size:13px;padding:9px 16px;border-radius:4px;opacity:0;pointer-events:none;transition:opacity .2s,transform .2s;z-index:60}
.toast.on{opacity:1;transform:translate(-50%,0)}
.scrim{display:none}

#hitN{display:none;font-variant-numeric:tabular-nums}
@media (max-width:1180px){
  .count{display:none}
  #hitN{display:inline}
  .snip{grid-template-columns:56px minmax(0,1fr);row-gap:14px}
  .meta{grid-column:2;padding-right:0;display:grid;grid-template-columns:1fr auto;column-gap:20px;align-items:end}
  .meta>*{grid-column:1}
  .acts{grid-column:2;grid-row:1 / span 3;margin:0}
  .code{grid-column:2}
}
@media (max-width:900px){
  :root{--side:0px}
  html{scroll-padding-top:120px}
  .side{width:300px;transform:translateX(-100%);transition:transform .25s cubic-bezier(.2,.7,.2,1)}
  body.nav-open .side{transform:none;box-shadow:0 0 48px var(--shadow)}
  body.nav-open .scrim{display:block;position:fixed;inset:0;background:var(--scrim);z-index:25}
  .top-in{padding:10px 20px 0}
  .content{padding:0 20px 64px}
  #menu{display:inline-flex;align-items:center;gap:6px;height:40px;padding:0 14px 0 0;margin-right:12px;border:0;border-right:1px solid var(--rule);background:none;font-size:14px;font-weight:500;flex:none}
  #menu svg{width:16px;height:16px;stroke:currentColor;stroke-width:1.6;fill:none}
  .search .hint kbd,.keys{display:none}
  #q{padding-right:90px}
  .sbox>svg{left:0}
  .filters{overflow-x:auto;gap:18px;scrollbar-width:none;margin-right:-20px;padding-right:20px}
  .filters::-webkit-scrollbar{display:none}
  .seg{gap:18px}
  .hero{padding-top:36px}
  .hero h1{font-size:25px}
  section{padding-top:52px}
  .sec-head,.snip{grid-template-columns:40px minmax(0,1fr)}
  .meta{display:block}
  .acts{margin-top:12px}
  .code pre{font-size:12.5px;padding:14px 16px}
  .code.scrolls::after{content:"";position:absolute;top:0;right:0;bottom:0;width:28px;border-radius:0 4px 4px 0;background:linear-gradient(90deg,transparent,var(--bg-2));pointer-events:none}
  .code.scrolls.at-end::after{display:none}
}
@media print{
  :root{
  --bg:#ffffff; --bg-2:#f5f6f6; --ink:#141817; --ink-2:#464d4a; --muted:#6b726f; --faint:#a3a9a6;
  --rule:#e4e7e6; --accent:#2b2f9c; --accent-wash:#eceefa; --on-accent:#ffffff; --mark:#fff27a;
  --k:#2b2f9c; --s:#1d6b34; --c:#6b726f; --done:#1e7a37;
  --brand:#2b2f9c; --brand-fg:#f5e400; --brand-2:#ffffff; --brand-rule:rgba(255,255,255,.22); --hl:#f5e400; --hl-ink:#141817;
  --top-bg:rgba(255,255,255,.9); --veil:rgba(255,255,255,.35); --veil-on:rgba(255,255,255,.6);
  --toast-bg:#141817; --toast-fg:#ffffff; --shadow:rgba(20,24,23,.18); --scrim:rgba(20,24,23,.28);
  }
  .side,.top,.acts,.reveal,.legend,.toast{display:none!important}
  .main{margin:0}.content{max-width:none;padding:0}
  body{background:#fff;font-size:12px}
  .code pre{background:#fff;border:1px solid var(--rule);white-space:pre-wrap;font-size:11px}
  .snip{grid-template-columns:32px 170px minmax(0,1fr);row-gap:0;break-inside:avoid;padding:12px 0}
  .meta{grid-column:2;grid-row:1;display:block;padding-right:16px}
  .code{grid-column:3;grid-row:1}
  body.memo .snip pre{filter:none!important;opacity:1!important}
  section{padding-top:20px}.sec-head{break-after:avoid}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
'''

JS = r'''
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  // 저장소 이름은 이 사이트 전용(bdps.) — 같은 github.io 주소의 다른 페이지와 겹치지 않게
  const store = { get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
                  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
                  del(k) { try { localStorage.removeItem(k); } catch {} } };
  const snips = $$('.snip'), sections = $$('section'), q = $('#q'), clear = $('#clear'), side = $('.side'), menu = $('#menu');
  const TOTAL = snips.length;
  const IDS = new Set(snips.map(s => s.id));
  const GROUPS = ['t1', 't2', 't3', 'env'];
  const st = { g: 'all', hot: false, todo: false, memo: store.get('bdps.memo', false) === true, q: '' };
  // 주소로 공유되는 상태: ?type=t1|t2|t3|env · hot=1 · q=검색어 (외움·암기 모드는 개인 설정이라 주소에 넣지 않는다)
  const P = new URLSearchParams(location.search);
  if (GROUPS.includes(P.get('type'))) st.g = P.get('type');
  if (P.get('hot') === '1') st.hot = true;
  if (P.get('q')) st.q = P.get('q');
  function syncURL() {
    const u = new URLSearchParams();
    if (st.g !== 'all') u.set('type', st.g);
    if (st.hot) u.set('hot', '1');
    if (st.q.trim()) u.set('q', st.q.trim());
    const qs = u.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }
  // 외움 기록 — 배열이 아니거나 지금 없는 카드 id 는 버린다. 예전 키(bd.done, 순번 id)는 한 번 옮겨 온다
  function loadDone() {
    let raw = store.get('bdps.done', null);
    if (raw === null) {
      const old = store.get('bd.done', null), map = new Map(snips.map(s => [s.dataset.old, s.id]));
      raw = Array.isArray(old) ? old.map(x => map.get(x)) : [];
      store.del('bd.done'); store.del('bd.memo');
    }
    return new Set((Array.isArray(raw) ? raw : []).filter(x => typeof x === 'string' && IDS.has(x)));
  }
  const done = loadDone();
  const saveDone = () => store.set('bdps.done', [...done]);
  saveDone();
  // 검색 대상은 카드 내용만 — 버튼 글자(복사·외웠어요)와 카드 번호는 빼고
  snips.forEach(s => s._hay = [s.dataset.k, $('h3', s).dataset.t, $('.flag, .lib', s)?.textContent, $('.when', s).textContent, $('pre', s).textContent].join(' ').toLowerCase());

  const toast = $('.toast'); let tt;
  const say = m => { toast.textContent = m; toast.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('on'), 1400); };

  function paintDone() {
    snips.forEach(s => { const on = done.has(s.id); s.classList.toggle('is-done', on); $('.done', s).setAttribute('aria-pressed', on); $('.done span', s).textContent = on ? '외움' : '외웠어요'; });
    $('#doneN').textContent = done.size; $('.bar i').style.width = (done.size / TOTAL * 100) + '%';
  }
  function markTitle(s, t) {
    const h = $('h3', s), raw = h.dataset.t;
    const i = t ? raw.toLowerCase().indexOf(t) : -1;
    if (i < 0) { h.textContent = raw; return; }
    h.textContent = '';
    const m = document.createElement('mark'); m.textContent = raw.slice(i, i + t.length);
    h.append(raw.slice(0, i), m, raw.slice(i + t.length));
  }
  // 좁은 화면: 코드는 들여쓰기가 문법이라 줄을 꺾지 않고 옆으로 넘긴다 — 넘길 게 있으면 오른쪽 끝을 흐리게
  const edge = p => p.parentElement.classList.toggle('at-end', p.scrollLeft + p.clientWidth >= p.scrollWidth - 2);
  const markScroll = () => $$('.code pre').forEach(p => { if (!p.offsetParent) return; p.parentElement.classList.toggle('scrolls', p.scrollWidth > p.clientWidth + 1); edge(p); });

  function apply() {
    const t = st.q.trim().toLowerCase(); let n = 0;
    snips.forEach(s => {
      const show = (st.g === 'all' || s.dataset.g === st.g) && (!st.hot || s.dataset.hot === '1') && (!st.todo || !done.has(s.id)) && (!t || s._hay.includes(t));
      s.hidden = !show; if (show) n++; markTitle(s, show ? t : '');
    });
    let first = true;
    sections.forEach(sec => {
      const c = $$('.snip', sec).filter(s => !s.hidden).length;
      sec.hidden = c === 0;
      sec.classList.toggle('first-shown', c > 0 && first); if (c > 0) first = false;
      const tc = $(`[data-count="${sec.id}"]`), a = tc.closest('a');
      tc.textContent = c; a.classList.toggle('dim', c === 0);
      if (c === 0) a.setAttribute('aria-disabled', 'true'); else a.removeAttribute('aria-disabled');
    });
    const filtering = !!t || st.g !== 'all' || st.hot || st.todo;
    $('#shownN').textContent = n;
    document.body.classList.toggle('filtering', filtering);
    $('#hitN').textContent = filtering ? n + '개' : '';
    $('.empty').style.display = n ? 'none' : 'block';
    $('#emptyQ').textContent = t ? `「${st.q.trim()}」에 맞는 스니펫이 없다` : '조건에 맞는 스니펫이 없다';
    clear.style.display = st.q ? 'inline-block' : 'none';
    $('.search kbd').style.display = st.q ? 'none' : '';
    syncURL();
    requestAnimationFrame(markScroll);
  }
  const paintTabs = () => $$('.seg button').forEach(x => x.setAttribute('aria-pressed', x.dataset.g === st.g));

  q.addEventListener('input', () => { st.q = q.value; apply(); });
  clear.addEventListener('click', () => { q.value = st.q = ''; apply(); q.focus(); });
  document.addEventListener('keydown', e => {
    const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName) || document.activeElement?.isContentEditable;
    if (e.key === '/' && !typing) { e.preventDefault(); q.focus(); q.select(); }
    else if (e.key === 'Escape') { if (document.body.classList.contains('nav-open')) closeNav(true); else if (st.q) { q.value = st.q = ''; apply(); } else q.blur(); }
  });
  $$('.seg button').forEach(b => b.addEventListener('click', () => { st.g = b.dataset.g; paintTabs(); apply(); window.scrollTo({ top: 0 }); }));
  const toggles = { hot: $('#tHot'), todo: $('#tTodo'), memo: $('#tMemo') };
  Object.entries(toggles).forEach(([k, b]) => {
    b.setAttribute('aria-pressed', st[k]);
    b.addEventListener('click', () => {
      st[k] = !st[k]; b.setAttribute('aria-pressed', st[k]);
      if (k === 'memo') { document.body.classList.toggle('memo', st.memo); snips.forEach(s => s.classList.remove('shown')); store.set('bdps.memo', st.memo); }
      else apply();
    });
  });
  document.body.classList.toggle('memo', st.memo);
  $('.empty button').addEventListener('click', () => {
    q.value = st.q = ''; st.g = 'all'; st.hot = st.todo = false;
    paintTabs(); toggles.hot.setAttribute('aria-pressed', false); toggles.todo.setAttribute('aria-pressed', false); apply();
  });

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch { const ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.append(ta); ta.select();
            let ok = false; try { ok = document.execCommand('copy'); } catch {} ta.remove(); return ok; }
  }
  snips.forEach(s => {
    const cp = $('.copy', s); let ct;
    cp.addEventListener('click', async () => {
      const ok = await copyText($('pre', s).textContent);
      if (!ok) { say('복사하지 못했다 — 코드를 직접 선택해 주세요'); return; }
      cp.classList.add('copied'); $('span', cp).textContent = '복사됨'; say('코드를 복사했다');
      clearTimeout(ct); ct = setTimeout(() => { cp.classList.remove('copied'); $('span', cp).textContent = '복사'; }, 1400);
    });
    $('.done', s).addEventListener('click', () => {
      done.has(s.id) ? done.delete(s.id) : done.add(s.id); saveDone(); paintDone(); if (st.todo) apply();
    });
    $('.reveal', s).addEventListener('click', () => s.classList.add('shown'));
    $('pre', s).addEventListener('scroll', e => edge(e.currentTarget), { passive: true });
  });

  const links = $$('.toc a');
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.dataset.sec === e.target.id));
  }), { rootMargin: '-25% 0px -65% 0px' });
  sections.forEach(s => io.observe(s));
  links.forEach(a => a.addEventListener('click', e => { if (a.getAttribute('aria-disabled') === 'true') e.preventDefault(); }));

  // 휴대폰 목차 서랍 — 닫혀 있으면 키보드 포커스가 들어가지 못하게(inert), 열고 닫을 때 포커스를 옮긴다
  const narrow = matchMedia('(max-width: 900px)');
  const syncInert = () => { side.inert = narrow.matches && !document.body.classList.contains('nav-open'); };
  function closeNav(refocus) { document.body.classList.remove('nav-open'); menu.setAttribute('aria-expanded', false); syncInert(); if (refocus) menu.focus(); }
  menu.addEventListener('click', () => {
    const o = document.body.classList.toggle('nav-open'); menu.setAttribute('aria-expanded', o); syncInert();
    if (o) (side.querySelector('.toc a:not([aria-disabled])') || side).focus();
  });
  $('.scrim').addEventListener('click', () => closeNav(true));
  links.forEach(a => a.addEventListener('click', () => closeNav(false)));
  narrow.addEventListener ? narrow.addEventListener('change', syncInert) : narrow.addListener(syncInert);
  $('#resetDone').addEventListener('click', () => { if (!done.size) return; done.clear(); saveDone(); paintDone(); apply(); say('외움 표시를 모두 지웠다'); });

  q.value = st.q;
  paintTabs();
  $('#share').addEventListener('click', async () => say(await copyText(location.href) ? '지금 화면 그대로의 주소를 복사했다' : '주소를 복사하지 못했다'));
  addEventListener('resize', markScroll); document.fonts && document.fonts.ready.then(markScroll);
  syncInert(); paintDone(); apply();
})();
'''

page = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>빅데이터분석기사 실기 파이썬 스니펫</title>
<meta name="description" content="빅데이터분석기사 실기 작업형 1·2·3 파이썬 스니펫 {TOTAL}개. 감점 포인트 {HOT}개, 복사·검색·암기 모드.">

<!-- 공유 카드(카카오톡·슬랙·트위터).
     og:image·twitter:image는 반드시 절대 주소여야 합니다 — 카카오톡은 상대 경로를 읽지 못합니다.
     저장소 이름이나 도메인을 바꾸면 아래 세 URL도 같이 바꿔 주세요. -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="골든래빗">
<meta property="og:title" content="빅데이터분석기사 실기 파이썬 스니펫">
<meta property="og:description" content="작업형 1·2·3에 쓰는 코드 {TOTAL}개. 감점 포인트 {HOT}개와 암기 모드까지.">
<meta property="og:url" content="https://hclee-source.github.io/bigdata-practical-snippets/">
<meta property="og:image" content="https://hclee-source.github.io/bigdata-practical-snippets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="ko_KR">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="빅데이터분석기사 실기 파이썬 스니펫">
<meta name="twitter:description" content="작업형 1·2·3에 쓰는 코드 {TOTAL}개. 감점 포인트 {HOT}개와 암기 모드까지.">
<meta name="twitter:image" content="https://hclee-source.github.io/bigdata-practical-snippets/og.png">

<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon.png" sizes="96x96" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="theme-color" content="#2b2f9c" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#23267f" media="(prefers-color-scheme: dark)">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+KR:wght@400;500;600&display=swap">
<style>{CSS}</style>
</head>
<body>
<aside class="side" aria-label="목차">
  <div class="brand">
    <i>2027 빠르게 따는</i><b>빅데이터분석기사 실기</b><small>파이썬 스니펫 {TOTAL}</small>
    <div class="progress">
      <div class="progress-row"><span>외운 스니펫</span><strong><b id="doneN">0</b> <span>/ {TOTAL}</span></strong></div>
      <div class="bar"><i></i></div>
    </div>
  </div>
  <nav class="toc">{''.join(toc)}</nav>
  <div class="side-foot"><span class="keys"><kbd>/</kbd> 검색 &nbsp;·&nbsp; <kbd>Esc</kbd> 지우기<br></span><button id="resetDone" type="button">외움 표시 모두 지우기</button></div>
</aside>
<div class="scrim"></div>

<div class="main">
  <div class="top">
    <div class="top-in">
      <div class="search">
        <button id="menu" type="button" aria-expanded="false" aria-label="목차 열기"><svg viewBox="0 0 16 16"><path d="M2.5 4h11M2.5 8h11M2.5 12h11"/></svg>목차</button>
        <div class="sbox" style="position:relative;flex:1;display:flex;align-items:center">
          <svg viewBox="0 0 16 16"><circle cx="7" cy="7" r="4.6"/><path d="M10.4 10.4l3.2 3.2"/></svg>
          <input id="q" type="search" placeholder="검색 (예: 오즈비)" autocomplete="off" spellcheck="false" aria-label="스니펫 검색">
          <span class="hint"><span id="hitN"></span><kbd>/</kbd><button id="clear" type="button">지우기</button></span>
        </div>
      </div>
      <div class="filters" role="toolbar" aria-label="보기 설정">
        <div class="seg" role="group" aria-label="작업형">
          <button type="button" data-g="all" aria-pressed="true">전체</button>
          <button type="button" data-g="t1" aria-pressed="false">작업형 1</button>
          <button type="button" data-g="t2" aria-pressed="false">작업형 2</button>
          <button type="button" data-g="t3" aria-pressed="false">작업형 3</button>
          <button type="button" data-g="env" aria-pressed="false">시험장</button>
        </div>
        <span class="sep" aria-hidden="true"></span>
        <button type="button" class="tog" id="tHot" aria-pressed="false"><i></i>감점 포인트만</button>
        <button type="button" class="tog" id="tTodo" aria-pressed="false"><i></i>안 외운 것만</button>
        <button type="button" class="tog" id="tMemo" aria-pressed="false"><i></i>암기 모드</button>
        <button type="button" class="tog link" id="share"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M6.6 9.4l2.8-2.8M7.3 4.6l1-1a2.6 2.6 0 0 1 3.7 3.7l-1 1M8.7 11.4l-1 1A2.6 2.6 0 0 1 4 8.7l1-1"/></svg>링크 복사</button>
        <span class="count"><b id="shownN">{TOTAL}</b> / {TOTAL}개</span>
      </div>
    </div>
  </div>

  <main class="content">
    <div class="hero">
      <p class="kicker">빅데이터분석기사 실기 · Python</p>
      <h1>작업형 1·2·3에서 쓰는 파이썬 코드 {TOTAL}개</h1>
      <p>『2027 빠르게 따는 빅데이터분석기사 실기』의 풀이 코드 관례를 따랐고, 모든 코드는 실제로 실행해 확인했다. 시험장 버전(scikit-learn 1.2 이상)에서도 그대로 돈다.</p>
      <div class="legend">
        <span><span class="tick"></span>감점 포인트 {HOT}개 — 「함정·필수·빈출」 형광펜</span>
        <span>암기 모드 — 코드를 가리고 떠올린 뒤 눌러서 확인</span>
      </div>
    </div>
{chr(10).join(body)}
    <div class="empty"><b id="emptyQ">조건에 맞는 스니펫이 없다</b>다른 말로 찾거나 필터를 풀어 보세요.<br><button type="button">필터 모두 풀기</button></div>
    <p class="foot">빅데이터분석기사 실기 파이썬 스니펫 · pandas · scikit-learn · SciPy · statsmodels — 인쇄(Ctrl+P)하면 버튼 없이 코드만 나온다.</p>
  </main>
</div>
<div class="toast" role="status" aria-live="polite"></div>
<script>{JS}</script>
</body>
</html>
'''
if __name__ == '__main__':
    import os
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    open('index.html', 'w', encoding='utf-8', newline='\n').write(page)
    print('cards', TOTAL, 'hot', HOT, 'bytes', len(page.encode()))

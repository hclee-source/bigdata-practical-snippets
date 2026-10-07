"""index.html 생성.  실행: python build.py

카드 내용은 cards.py, 「언제 쓰나」 문구는 when.py 에서 고친다. index.html 을 직접 고치지 말 것.
"""
import re, html, sys
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
        aid = f'{s["id"]}-{j+1}'
        flag = f'<span class="flag">{html.escape(tag)}</span>' if hot else f'<span class="lib">{html.escape(tag)}</span>'
        rows.append(f'''<article class="snip{' is-hot' if hot else ''}" id="{aid}" data-g="{g}" data-hot="{int(hot)}" data-k="{html.escape(kw)}">
  <div class="meta">
    <div class="meta-top">{flag}</div>
    <h3 data-t="{html.escape(title)}">{html.escape(title)}</h3>
    <p class="when">{html.escape(WHEN[title])}</p>
    <div class="acts">
      <button type="button" class="act copy" aria-label="{html.escape(title)} 코드 복사"><svg viewBox="0 0 16 16" aria-hidden="true"><rect x="5" y="5" width="8.5" height="8.5" rx="1.6"/><path d="M3.2 10.8V3.6c0-.9.7-1.6 1.6-1.6h6"/></svg><span>복사</span></button>
      <button type="button" class="act done" aria-pressed="false" aria-label="{html.escape(title)} 외움 표시"><svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3.5 8.4l2.9 2.8 6.1-6.4"/></svg><span>외웠어요</span></button>
    </div>
  </div>
  <div class="code">
    <pre><code>{hl(code)}</code></pre>
    <button type="button" class="reveal">눌러서 코드 보기</button>
  </div>
</article>''')
    body.append(f'''<section id="{s['id']}" data-g="{g}">
  <header class="sec-head">
    <p class="eyebrow">{gname} <span>·</span> {i+1:02d}</p>
    <h2>{html.escape(short(s['title']))}</h2>
    <p class="sec-desc">{html.escape(s['desc'])}</p>
  </header>
  <div class="rows">
{chr(10).join(rows)}
  </div>
</section>''')

CSS = r'''
:root{
  --green:#146c50; --green-ink:#0f5640; --mint:#e7f2ed; --on-green:#ffffff;
  --paper:#fbf8f1; --sheet:#ffffff; --ink:#1b211e; --ink-2:#4a524d; --muted:#687069;
  --rule:#e6e1d4; --rule-2:#efebe1; --rule-3:#cfc8b8;
  --code:#f5f2ea; --amber:#b7791f; --amber-ink:#8a5a12; --amber-wash:#fdf3df; --mark:#fbe7a6;
  --k:#146c50; --s:#8f5310; --c:#666d67; --n:#a83d29; --f:#1d5b86;
  --top-bg:rgba(251,248,241,.92); --tog:#d6d1c4; --ring:rgba(20,108,80,.14); --veil:rgba(251,248,241,.35); --veil-on:rgba(231,242,237,.6);
  --toast-bg:#1b211e; --toast-fg:#ffffff; --shadow:rgba(27,33,30,.12);
  --side:264px;
  --sans:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  --mono:"JetBrains Mono","D2Coding",Consolas,"Pretendard Variable",monospace;
  color-scheme:light dark;
}
@media (prefers-color-scheme:dark){:root{
  --green:#6ecfa8; --green-ink:#8fe0bd; --mint:#183429; --on-green:#0c1714;
  --paper:#101513; --sheet:#161c19; --ink:#e6ece9; --ink-2:#b3c0ba; --muted:#8e9c96;
  --rule:#27302c; --rule-2:#222a26; --rule-3:#3a4540;
  --code:#1a201d; --amber:#e0a84a; --amber-ink:#f1c27a; --amber-wash:#3a2c14; --mark:#5a4a1a;
  --k:#7fd6b1; --s:#e6b77f; --c:#8b9892; --n:#f29a86; --f:#8cc4ef;
  --top-bg:rgba(16,21,19,.9); --tog:#3a4540; --ring:rgba(110,207,168,.2); --veil:rgba(16,21,19,.3); --veil-on:rgba(24,52,41,.6);
  --toast-bg:#e6ece9; --toast-fg:#101513; --shadow:rgba(0,0,0,.4);
}}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{scroll-padding-top:132px}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6;word-break:keep-all;-webkit-font-smoothing:antialiased}
button{font:inherit;color:inherit;cursor:pointer}
a{color:inherit}
:focus-visible{outline:2px solid var(--green);outline-offset:2px;border-radius:6px}

/* ── 사이드 목차 ── */
.side{position:fixed;inset:0 auto 0 0;width:var(--side);background:var(--sheet);border-right:1px solid var(--rule);display:flex;flex-direction:column;z-index:30}
.brand{padding:22px 22px 18px;border-bottom:1px solid var(--rule-2)}
.brand-row{display:flex;align-items:center;gap:10px}
.mark{width:30px;height:30px;border-radius:8px;background:var(--green);display:grid;place-items:center;flex:none}
.mark i{width:9px;height:9px;border-radius:50%;background:var(--on-green)}
.brand-row b{display:block;font-size:15px;letter-spacing:-.01em}
.brand small{display:block;color:var(--muted);font-size:12px;margin-top:1px}
.progress{margin-top:16px}
.progress-row{display:flex;justify-content:space-between;align-items:baseline;font-size:12px;color:var(--ink-2)}
.progress-row strong{font-size:18px;color:var(--ink);font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.progress-row strong span{font-size:12px;color:var(--muted);font-weight:500}
.bar{height:5px;background:var(--rule-2);border-radius:99px;margin-top:7px;overflow:hidden}
.bar i{display:block;height:100%;width:0;background:var(--green);border-radius:99px;transition:width .3s ease}
.toc{flex:1;overflow-y:auto;padding:10px 12px 18px}
.toc-group{margin-top:14px}
.toc-head{display:flex;align-items:baseline;justify-content:space-between;padding:0 10px 6px;font-size:12px;font-weight:700;color:var(--ink)}
.toc-head em{font-style:normal;font-weight:500;color:var(--muted);font-size:11.5px}
.toc ol{list-style:none;margin:0;padding:0}
.toc a{display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:8px;text-decoration:none;color:var(--ink-2);font-size:13.5px;transition:background .12s,color .12s}
.toc a:hover{background:var(--paper);color:var(--ink)}
.toc a.on{background:var(--mint);color:var(--green-ink);font-weight:600}
.toc-no{font:600 11px/1 var(--mono);color:var(--muted);width:18px}
.toc a.on .toc-no{color:var(--green)}
.toc-t{flex:1;min-width:0}
.toc-c{font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}
.toc a.dim{opacity:.38}
.side-foot{padding:14px 22px 18px;border-top:1px solid var(--rule-2);font-size:12px;color:var(--muted);line-height:1.8}
kbd{font:600 11px/1 var(--mono);background:var(--paper);border:1px solid var(--rule);border-bottom-width:2px;border-radius:5px;padding:2px 5px;color:var(--ink-2)}

/* ── 상단 도구 ── */
.main{margin-left:var(--side);min-height:100vh}
.top{position:sticky;top:0;z-index:20;background:var(--top-bg);backdrop-filter:saturate(1.4) blur(10px);-webkit-backdrop-filter:saturate(1.4) blur(10px);border-bottom:1px solid var(--rule)}
.top-in{max-width:1040px;margin:0 auto;padding:14px 40px 12px}
.search{position:relative;display:flex;align-items:center}
.sbox>svg{position:absolute;left:14px;width:16px;height:16px;fill:none;stroke:var(--muted);stroke-width:1.8}
#q{width:100%;height:44px;padding:0 92px 0 40px;border:1px solid var(--rule);border-radius:11px;background:var(--sheet);font:inherit;font-size:15px;color:var(--ink);outline:none;transition:border-color .15s,box-shadow .15s}
#q::placeholder{color:var(--muted)}
#q::-webkit-search-cancel-button{-webkit-appearance:none;display:none}
body.filtering .hero{display:none}
body.filtering section:first-of-type{padding-top:24px}
#q:focus{border-color:var(--green);box-shadow:0 0 0 3px var(--ring)}
.search .hint{position:absolute;right:12px;display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted)}
#clear{display:none;border:0;background:var(--rule-2);border-radius:6px;padding:3px 8px;font-size:12px;color:var(--ink-2)}
.filters{display:flex;align-items:center;gap:14px;margin-top:11px;flex-wrap:wrap}
.seg{display:inline-flex;background:var(--rule-2);border-radius:9px;padding:3px}
.seg button{border:0;background:none;padding:5px 12px;border-radius:7px;font-size:13px;font-weight:600;color:var(--ink-2);white-space:nowrap}
.seg button[aria-pressed="true"]{background:var(--sheet);color:var(--green-ink);box-shadow:0 1px 2px var(--shadow)}
.tog{display:inline-flex;align-items:center;gap:7px;border:0;background:none;padding:4px 2px;font-size:13px;color:var(--ink-2);white-space:nowrap}
.tog i{width:30px;height:18px;border-radius:99px;background:var(--tog);position:relative;transition:background .15s;flex:none}
.tog i::after{content:"";position:absolute;top:2px;left:2px;width:14px;height:14px;border-radius:50%;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.2);transition:transform .15s}
.tog[aria-pressed="true"]{color:var(--ink)}
.tog.link svg{width:15px;height:15px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round}
.tog.link:hover{color:var(--green-ink)}
.tog[aria-pressed="true"] i{background:var(--green)}
.tog[aria-pressed="true"] i::after{transform:translateX(12px)}
.count{margin-left:auto;font-size:12.5px;color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.count b{color:var(--ink);font-weight:600}
#menu{display:none}

/* ── 본문 ── */
.content{max-width:1040px;margin:0 auto;padding:8px 40px 80px}
.hero{padding:40px 0 8px}
.hero h1{margin:0;font-size:30px;line-height:1.3;letter-spacing:-.03em;font-weight:700}
.hero h1 em{font-style:normal;color:var(--green)}
.hero p{margin:10px 0 0;color:var(--ink-2);max-width:600px}
.legend{display:flex;gap:18px;flex-wrap:wrap;margin-top:16px;font-size:12.5px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
section{padding-top:44px}
.sec-head{padding-bottom:14px;border-bottom:2px solid var(--ink)}
.eyebrow{margin:0;font:600 12px/1 var(--sans);color:var(--green);letter-spacing:.02em}
.eyebrow span{color:var(--muted);margin:0 2px}
.sec-head h2{margin:8px 0 0;font-size:22px;letter-spacing:-.02em;line-height:1.35}
.sec-desc{margin:6px 0 0;color:var(--ink-2);font-size:14px}

.snip{display:grid;grid-template-columns:232px minmax(0,1fr);gap:28px;padding:22px 0;border-bottom:1px solid var(--rule);position:relative}
.snip.is-hot::before{content:"";position:absolute;left:-16px;top:22px;bottom:22px;width:3px;border-radius:3px;background:var(--amber)}
.meta{min-width:0}
.meta-top{min-height:20px}
.flag{display:inline-block;font-size:11.5px;font-weight:700;color:var(--amber-ink);background:var(--amber-wash);border-radius:5px;padding:2px 7px}
.lib{font:500 11.5px/1.6 var(--mono);color:var(--muted)}
.snip h3{margin:5px 0 0;font-size:16px;line-height:1.4;letter-spacing:-.015em}
.snip h3 mark{background:var(--mark);color:inherit;border-radius:3px;padding:0 1px}
.when{margin:5px 0 0;font-size:13.5px;line-height:1.55;color:var(--ink-2)}
.acts{display:flex;gap:6px;margin-top:12px}
.act{display:inline-flex;align-items:center;gap:5px;height:30px;padding:0 10px;border:1px solid var(--rule);background:var(--sheet);border-radius:8px;font-size:12.5px;color:var(--ink-2);transition:border-color .12s,background .12s,color .12s}
.act:hover{border-color:var(--rule-3);color:var(--ink)}
.act svg{width:14px;height:14px;fill:none;stroke:currentColor;stroke-width:1.6;stroke-linecap:round;stroke-linejoin:round}
.act.copied{border-color:var(--green);color:var(--green-ink);background:var(--mint)}
.done[aria-pressed="true"]{background:var(--green);border-color:var(--green);color:var(--on-green)}
.snip.is-done h3{color:var(--ink-2)}
.code{position:relative;min-width:0}
.code pre{margin:0;background:var(--code);border-radius:10px;padding:16px 18px;overflow-x:auto;font:400 13px/1.7 var(--mono);color:var(--ink);tab-size:4;font-variant-ligatures:none;font-feature-settings:'liga' 0,'calt' 0}
.code pre .k{color:var(--k);font-weight:600}
.code pre .s{color:var(--s)}
.code pre .c{color:var(--c)}
.code pre .n{color:var(--n)}
.code pre .f{color:var(--f)}
.reveal{display:none}
body.memo .snip:not(.shown) pre{filter:blur(6px);user-select:none;opacity:.55}
body.memo .snip:not(.shown) .reveal{display:flex;position:absolute;inset:0;align-items:center;justify-content:center;border:1.5px dashed var(--rule-3);background:var(--veil);border-radius:10px;font-size:13.5px;font-weight:600;color:var(--green-ink)}
body.memo .snip:not(.shown) .reveal:hover{background:var(--veil-on)}

.empty{display:none;padding:70px 0;text-align:center;color:var(--ink-2)}
.empty b{display:block;font-size:17px;color:var(--ink);margin-bottom:6px}
.empty button{margin-top:16px;border:1px solid var(--green);background:var(--sheet);color:var(--green-ink);border-radius:9px;padding:8px 16px;font-weight:600;font-size:13.5px}
.foot{margin-top:56px;padding-top:18px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--muted)}
.toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,12px);background:var(--toast-bg);color:var(--toast-fg);font-size:13px;padding:9px 16px;border-radius:10px;opacity:0;pointer-events:none;transition:opacity .18s,transform .18s;z-index:60}
.toast.on{opacity:1;transform:translate(-50%,0)}
.scrim{display:none}

#hitN{display:none;font-variant-numeric:tabular-nums}
@media (max-width:1180px){
  .count{display:none}
  #hitN{display:inline}
  .snip{grid-template-columns:1fr;gap:12px}
  .acts{margin-top:10px}
  .meta{display:grid;grid-template-columns:1fr auto;column-gap:16px;align-items:end}
  .meta-top,.meta h3,.when{grid-column:1}
  .acts{grid-column:2;grid-row:1 / span 3;align-self:end}
}
@media (max-width:900px){
  :root{--side:0px}
  html{scroll-padding-top:150px}
  .side{width:300px;transform:translateX(-100%);transition:transform .22s ease;box-shadow:none}
  body.nav-open .side{transform:none;box-shadow:0 0 40px rgba(0,0,0,.18)}
  body.nav-open .scrim{display:block;position:fixed;inset:0;background:rgba(27,33,30,.32);z-index:25}
  .top-in{padding:10px 16px}
  .content{padding:0 16px 60px}
  #menu{display:inline-flex;align-items:center;gap:6px;height:44px;padding:0 12px;margin-right:8px;border:1px solid var(--rule);background:var(--sheet);border-radius:11px;font-size:13.5px;font-weight:600;flex:none}
  #menu svg{width:16px;height:16px;stroke:currentColor;stroke-width:1.8;fill:none}
  .search .hint kbd,.keys{display:none}
  #q{padding-right:110px}
  .filters{flex-wrap:nowrap;overflow-x:auto;gap:12px;scrollbar-width:none;margin-right:-16px;padding-right:16px}
  .filters::-webkit-scrollbar{display:none}
  .count{display:none}
  .hero{padding-top:26px}
  .hero h1{font-size:24px}
  .snip.is-hot::before{left:-10px}
  .meta{display:block}
  .acts{margin-top:10px}
  .code pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:12.5px;padding:14px}
}
@media print{
  :root{
  --green:#146c50; --green-ink:#0f5640; --mint:#e7f2ed; --on-green:#ffffff;
  --paper:#fbf8f1; --sheet:#ffffff; --ink:#1b211e; --ink-2:#4a524d; --muted:#687069;
  --rule:#e6e1d4; --rule-2:#efebe1; --rule-3:#cfc8b8;
  --code:#f5f2ea; --amber:#b7791f; --amber-ink:#8a5a12; --amber-wash:#fdf3df; --mark:#fbe7a6;
  --k:#146c50; --s:#8f5310; --c:#666d67; --n:#a83d29; --f:#1d5b86;
  --top-bg:rgba(251,248,241,.92); --tog:#d6d1c4; --ring:rgba(20,108,80,.14); --veil:rgba(251,248,241,.35); --veil-on:rgba(231,242,237,.6);
  --toast-bg:#1b211e; --toast-fg:#ffffff; --shadow:rgba(27,33,30,.12);
  }
  .side,.top,.acts,.reveal,.legend,.toast{display:none!important}
  .main{margin:0}.content{max-width:none;padding:0}
  body{background:#fff;font-size:12px}
  .code pre{background:#fff}
  .snip{grid-template-columns:180px 1fr;break-inside:avoid;padding:12px 0}
  .snip.is-hot::before{left:-8px}
  body.memo .snip pre{filter:none!important;opacity:1!important}
  .code pre{white-space:pre-wrap;font-size:11px;border:1px solid var(--rule)}
  section{padding-top:20px}.sec-head{break-after:avoid}
}
@media (prefers-reduced-motion:reduce){*{transition:none!important;scroll-behavior:auto!important}}
'''

JS = r'''
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const store = { get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
                  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} } };
  const snips = $$('.snip'), sections = $$('section'), q = $('#q'), clear = $('#clear');
  const TOTAL = snips.length;
  const st = { g: 'all', hot: false, todo: false, memo: store.get('bd.memo', false), q: '' };
  // 주소로 공유되는 상태: ?type=t1|t2|t3 · hot=1 · q=검색어 (외움·암기 모드는 개인 설정이라 주소에 넣지 않는다)
  const P = new URLSearchParams(location.search);
  if (['t1', 't2', 't3', 'env'].includes(P.get('type'))) st.g = P.get('type');
  if (P.get('hot') === '1') st.hot = true;
  if (P.get('q')) { st.q = P.get('q'); }
  function syncURL() {
    const u = new URLSearchParams();
    if (st.g !== 'all') u.set('type', st.g);
    if (st.hot) u.set('hot', '1');
    if (st.q.trim()) u.set('q', st.q.trim());
    const qs = u.toString();
    history.replaceState(null, '', location.pathname + (qs ? '?' + qs : '') + location.hash);
  }
  const done = new Set(store.get('bd.done', []));
  snips.forEach(s => s._hay = (s.dataset.k + ' ' + s.textContent).toLowerCase());

  const toast = $('.toast'); let tt;
  const say = m => { toast.textContent = m; toast.classList.add('on'); clearTimeout(tt); tt = setTimeout(() => toast.classList.remove('on'), 1400); };

  function paintDone() {
    snips.forEach(s => { const on = done.has(s.id); s.classList.toggle('is-done', on); $('.done', s).setAttribute('aria-pressed', on); $('.done span', s).textContent = on ? '외움' : '외웠어요'; });
    $('#doneN').textContent = done.size; $('.bar i').style.width = (done.size / TOTAL * 100) + '%';
  }
  function markTitle(s, t) {
    const h = $('h3', s), raw = h.dataset.t;
    if (!t) { h.textContent = raw; return; }
    const i = raw.toLowerCase().indexOf(t);
    if (i < 0) { h.textContent = raw; return; }
    h.innerHTML = '';
    h.append(raw.slice(0, i)); const m = document.createElement('mark'); m.textContent = raw.slice(i, i + t.length); h.append(m, raw.slice(i + t.length));
  }
  function apply() {
    const t = st.q.trim().toLowerCase(); let n = 0;
    snips.forEach(s => {
      const ok = (st.g === 'all' || s.dataset.g === st.g) && (!st.hot || s.dataset.hot === '1') && (!st.todo || !done.has(s.id)) && (!t || s._hay.includes(t));
      s.hidden = !ok; if (ok) n++; markTitle(s, ok ? t : '');
    });
    sections.forEach(sec => {
      const c = $$('.snip', sec).filter(s => !s.hidden).length;
      sec.hidden = c === 0;
      const tc = $(`[data-count="${sec.id}"]`); tc.textContent = c; tc.closest('a').classList.toggle('dim', c === 0);
    });
    $('#shownN').textContent = n;
    document.body.classList.toggle('filtering', !!t || st.g !== 'all' || st.hot || st.todo);
    $('#hitN').textContent = t ? n + '개' : '';
    $('.empty').style.display = n ? 'none' : 'block';
    $('#emptyQ').textContent = t ? `「${st.q.trim()}」에 맞는 스니펫이 없다` : '조건에 맞는 스니펫이 없다';
    clear.style.display = st.q ? 'inline-block' : 'none';
    $('.search kbd').style.display = st.q ? 'none' : '';
    syncURL();
  }

  q.addEventListener('input', () => { st.q = q.value; apply(); });
  clear.addEventListener('click', () => { q.value = st.q = ''; apply(); q.focus(); });
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); q.select(); }
    else if (e.key === 'Escape') { if (document.body.classList.contains('nav-open')) closeNav(); else if (st.q) { q.value = st.q = ''; apply(); } else q.blur(); }
  });
  $$('.seg button').forEach(b => b.addEventListener('click', () => {
    st.g = b.dataset.g; $$('.seg button').forEach(x => x.setAttribute('aria-pressed', x === b)); apply();
    window.scrollTo({ top: 0 });
  }));
  const toggles = { hot: $('#tHot'), todo: $('#tTodo'), memo: $('#tMemo') };
  Object.entries(toggles).forEach(([k, b]) => {
    b.setAttribute('aria-pressed', st[k]);
    b.addEventListener('click', () => {
      st[k] = !st[k]; b.setAttribute('aria-pressed', st[k]);
      if (k === 'memo') { document.body.classList.toggle('memo', st.memo); snips.forEach(s => s.classList.remove('shown')); store.set('bd.memo', st.memo); }
      else apply();
    });
  });
  document.body.classList.toggle('memo', st.memo);
  $('.empty button').addEventListener('click', () => {
    q.value = st.q = ''; st.g = 'all'; st.hot = st.todo = false;
    $$('.seg button').forEach(x => x.setAttribute('aria-pressed', x.dataset.g === 'all'));
    toggles.hot.setAttribute('aria-pressed', false); toggles.todo.setAttribute('aria-pressed', false); apply();
  });

  async function copyText(text) {
    try { await navigator.clipboard.writeText(text); return true; }
    catch { const ta = document.createElement('textarea'); ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0'; document.body.append(ta); ta.select();
            let ok = false; try { ok = document.execCommand('copy'); } catch {} ta.remove(); return ok; }
  }
  snips.forEach(s => {
    const cp = $('.copy', s);
    cp.addEventListener('click', async () => {
      const ok = await copyText($('pre', s).textContent);
      if (!ok) { say('복사하지 못했다 — 코드를 직접 선택해 주세요'); return; }
      cp.classList.add('copied'); $('span', cp).textContent = '복사됨'; say('코드를 복사했다');
      setTimeout(() => { cp.classList.remove('copied'); $('span', cp).textContent = '복사'; }, 1400);
    });
    $('.done', s).addEventListener('click', () => {
      done.has(s.id) ? done.delete(s.id) : done.add(s.id); store.set('bd.done', [...done]); paintDone(); if (st.todo) apply();
    });
    $('.reveal', s).addEventListener('click', () => s.classList.add('shown'));
  });

  const links = $$('.toc a');
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) links.forEach(a => a.classList.toggle('on', a.dataset.sec === e.target.id));
  }), { rootMargin: '-25% 0px -65% 0px' });
  sections.forEach(s => io.observe(s));

  const closeNav = () => { document.body.classList.remove('nav-open'); $('#menu').setAttribute('aria-expanded', false); };
  $('#menu').addEventListener('click', () => { const o = document.body.classList.toggle('nav-open'); $('#menu').setAttribute('aria-expanded', o); });
  $('.scrim').addEventListener('click', closeNav);
  links.forEach(a => a.addEventListener('click', closeNav));
  $('#resetDone').addEventListener('click', () => { if (!done.size) return; done.clear(); store.set('bd.done', []); paintDone(); apply(); say('외움 표시를 모두 지웠다'); });

  q.value = st.q;
  $$('.seg button').forEach(x => x.setAttribute('aria-pressed', x.dataset.g === st.g));
  $('#share').addEventListener('click', async () => say(await copyText(location.href) ? '지금 화면 그대로의 주소를 복사했다' : '주소를 복사하지 못했다'));
  paintDone(); apply();
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
<meta name="theme-color" content="#fbf8f1" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101513" media="(prefers-color-scheme: dark)">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap">
<style>{CSS}</style>
</head>
<body>
<aside class="side" aria-label="목차">
  <div class="brand">
    <div class="brand-row"><span class="mark"><i></i></span><div><b>빅분기 실기 스니펫</b><small>빠르게 따는 빅데이터분석기사 실기</small></div></div>
    <div class="progress">
      <div class="progress-row"><span>외운 스니펫</span><strong><b id="doneN">0</b> <span>/ {TOTAL}</span></strong></div>
      <div class="bar"><i></i></div>
    </div>
  </div>
  <nav class="toc">{''.join(toc)}</nav>
  <div class="side-foot"><span class="keys"><kbd>/</kbd> 검색 &nbsp;·&nbsp; <kbd>Esc</kbd> 지우기<br></span><button id="resetDone" type="button" style="border:0;background:none;padding:6px 0;color:var(--muted);text-decoration:underline;font-size:12px">외움 표시 모두 지우기</button></div>
</aside>
<div class="scrim"></div>

<div class="main">
  <div class="top">
    <div class="top-in">
      <div class="search">
        <button id="menu" type="button" aria-expanded="false" aria-label="목차 열기"><svg viewBox="0 0 16 16"><path d="M2.5 4h11M2.5 8h11M2.5 12h11"/></svg>목차</button>
        <div class="sbox" style="position:relative;flex:1;display:flex;align-items:center">
          <svg viewBox="0 0 16 16"><circle cx="7" cy="7" r="4.6"/><path d="M10.4 10.4l3.2 3.2"/></svg>
          <input id="q" type="search" placeholder="함수·상황 검색 (예: 오즈비, 결측)" autocomplete="off" spellcheck="false" aria-label="스니펫 검색">
          <span class="hint"><span id="hitN"></span><kbd>/</kbd><button id="clear" type="button">지우기</button></span>
        </div>
      </div>
      <div class="filters" role="toolbar" aria-label="보기 설정">
        <div class="seg" role="group" aria-label="작업형">
          <button type="button" data-g="all" aria-pressed="true">전체</button>
          <button type="button" data-g="t1" aria-pressed="false">작업형 1</button>
          <button type="button" data-g="t2" aria-pressed="false">작업형 2</button>
          <button type="button" data-g="t3" aria-pressed="false">작업형 3</button>
        </div>
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
      <h1>작업형 1 · 2 · 3에 쓰는 코드, <em>{TOTAL}개</em>로 끝낸다</h1>
      <p>교재 「빠르게 따는 빅데이터분석기사 실기」의 풀이 코드 관례를 그대로 따랐다. 모든 스니펫은 실제로 실행해 확인했다.</p>
      <div class="legend">
        <span><span class="flag">함정 · 필수 · 빈출</span> 감점 포인트 {HOT}개 — 왼쪽 노란 선</span>
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
open('index.html', 'w', encoding='utf-8', newline='\n').write(page)
print('cards', TOTAL, 'hot', HOT, 'bytes', len(page.encode()))

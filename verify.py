"""검증.  실행: python verify.py
필요: pandas · numpy · scikit-learn · scipy · statsmodels · Pillow

1. 스니펫 실행 — 75개 코드를 가짜 데이터로 전부 실제 실행한다.
   준비 코드(setup)는 가짜 데이터만 만든다. import 와 함수는 화면 순서대로 앞 카드에서
   정의된 것만 이어받는다 — 화면의 import 줄을 지우면 여기서 실패한다.
2. 주석 검산   — 주석에 쓴 주장(버림 방향, sklearn = statsmodels 계수 등)을 숫자로 확인한다.
3. 페이지 점검 — index.html 이 build.py 결과와 통째로 같은지, 공유 카드·아이콘·404,
   다크모드·인쇄 색, 글자 대비(WCAG AA).

시험장 하한 버전에서도 돌릴 것(README 「시험장 버전으로 검증」). 경고는 실패로 치지 않고
마지막에 모아 보여 준다.
"""
import builtins, contextlib, io, math, os, re, sys, tempfile, types, warnings
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.chdir(HERE)
from cards import SECTIONS
from when import WHEN

fails = []
def ok(cond, msg):
    if not cond: fails.append(msg)
    return cond

import numpy as np, pandas as pd, scipy, sklearn, statsmodels
print(f'환경  pandas {pd.__version__} · scikit-learn {sklearn.__version__} · scipy {scipy.__version__} · statsmodels {statsmodels.__version__}')

# ── 1. 스니펫 실행 ─────────────────────────────────────────────
SETUP_MODULES = {'pd', 'np', 'os'}              # 준비 코드가 가져와도 되는 모듈
LIBS = ('scipy', 'statsmodels', 'sklearn', 'pandas', 'numpy', 'math')
def is_tool(v):
    """다음 섹션으로 이어받을 것 — 모듈 · 함수 · 클래스 · 라이브러리 함수(데이터는 제외)"""
    if isinstance(v, (types.ModuleType, types.FunctionType, type)):
        return True
    return callable(v) and str(getattr(v, '__module__', '')).split('.')[0] in LIBS and not hasattr(v, 'shape')

carry = {}
seen_warn = {}
real_help = builtins.help
builtins.help = lambda *a, **k: None             # 시험장 카드의 help() 출력 생략
n_run = 0
for s in SECTIONS:
    with tempfile.TemporaryDirectory() as tmp:
        os.chdir(tmp)
        ns = {}
        exec(s['setup'], ns)
        leaked = [k for k, v in ns.items() if isinstance(v, types.ModuleType) and k not in SETUP_MODULES]
        ok(not leaked, f'준비 코드가 import 를 대신 넣는다 [{s["id"]}]: {leaked} — 화면 카드에서 import 할 것')
        for k, v in carry.items():
            ns.setdefault(k, v)
        for title, tag, hot, kw, code in s['cards']:
            n_run += 1
            before = {k: id(v) for k, v in ns.items()}
            try:
                with warnings.catch_warnings(record=True) as w, contextlib.redirect_stdout(io.StringIO()):
                    warnings.simplefilter('always')
                    exec(code, ns)
                for x in w:
                    if x.category.__name__ != 'ConvergenceWarning':
                        seen_warn.setdefault(f'{x.category.__name__}: {str(x.message)[:110]}', set()).add(title)
            except BaseException as e:                 # exit()·quit() 도 실패로 잡는다
                fails.append(f'실행 실패 [{s["id"]}] {title}: {type(e).__name__} {e}')
                continue
            for k, v in ns.items():
                if not k.startswith('__') and before.get(k) != id(v) and is_tool(v):
                    carry[k] = v
        os.chdir(HERE)
builtins.help = real_help
print(f'1. 스니펫 실행  {n_run}개')

# ── 2. 주석 검산 ───────────────────────────────────────────────
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
warnings.filterwarnings('ignore')

ok(int(-2.7) == -2 and math.floor(-2.7) == -3 and math.ceil(2.1) == 3, 'int/floor/ceil 방향')
ok(round(2.5) == 2 and round(3.5) == 4, 'round 는 .5 를 짝수 쪽으로 (카드 주석)')
ok(pd.Series([60, 80]).between(60, 80).all(), 'between 양 끝 포함')
ok(pd.Timestamp('2024-01-01').weekday() == 0, 'weekday 월=0')
# 카드와 같은 설정의 sklearn 로지스틱이 statsmodels 와 넷째 자리까지 같은지 — 데이터 20벌, 경고 없이
log_warn = 0
mism = 0
for seed in range(20):
    rng = np.random.default_rng(seed); n = 300
    d = pd.DataFrame({'x': rng.normal(50, 10, n), 'x2': rng.integers(0, 2, n), 'x3': rng.normal(0, 1, n)})
    d['label'] = (d['x'] + 3 * d['x3'] + rng.normal(0, 8, n) > 50).astype(int)
    X = d[['x', 'x2', 'x3']]
    ref = sm.Logit(d['label'], sm.add_constant(X)).fit(disp=False).params.values
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter('always')
        lr = LogisticRegression(penalty=None, solver='newton-cholesky', tol=1e-8, max_iter=1000).fit(X, d['label'])
    log_warn += sum('penalty' not in str(x.message) for x in w)
    mism += any(round(a, 4) != round(b, 4) for a, b in zip(np.r_[lr.intercept_, lr.coef_[0]], ref))
ok(log_warn == 0, f'카드 설정의 sklearn 로지스틱이 경고를 낸다 — {log_warn}건 (시험장 화면에 그대로 뜬다)')
ok(mism == 0, f'sklearn(newton-cholesky, tol=1e-8) ≠ statsmodels Logit 넷째 자리 — 20벌 중 {mism}벌')
l2 = LogisticRegression(solver='newton-cg', max_iter=1000).fit(X, d['label'])
ok(not np.allclose(l2.coef_[0], ref[1:], atol=1e-3), '기본값(l2)도 같은 값이 나온다 — 카드 주석 재검토')
t2 = pd.DataFrame([[10, 20], [20, 10]])
ok(stats.chi2_contingency(t2)[0] < stats.chi2_contingency(t2, correction=False)[0], '2×2 연속성 보정 기본')
x = d['x']; t = (x.mean() - 50) / (x.std() / np.sqrt(n)); r = stats.ttest_1samp(x, 50)
ok(abs(t - r.statistic) < 1e-9 and abs(2 * (1 - stats.t.cdf(abs(t), n - 1)) - r.pvalue) < 1e-9, 't 직접 계산 ≠ ttest_1samp')
a = pd.Series(rng.normal(0, 1, 50)); b = a + 1
ok(stats.ttest_ind(a, b, alternative='less').pvalue < 0.05, "alternative='less' 는 첫 인자 < 둘째 인자")
ok(not np.allclose((x - x.mean()) / x.std(), stats.zscore(x)), 'zscore 가 ddof=1 과 같다 — 카드 주석 재검토')
side = pd.concat([pd.DataFrame({'id': [1, 2]}), pd.DataFrame({'id': [2, 1]})], axis=1)
ok(list(side.iloc[0]) == [1, 2], 'concat axis=1 이 키로 맞춘다 — 카드 주석 재검토')
print('2. 주석 검산   11건')

# ── 3. 페이지 점검 ─────────────────────────────────────────────
os.chdir(HERE)
page = open('index.html', encoding='utf-8').read()
with contextlib.redirect_stdout(io.StringIO()):
    import build
ok(build.page == page, 'index.html 이 build.py 결과와 다르다 — python build.py 를 다시 돌릴 것')
total, hot = build.TOTAL, build.HOT
ok(all(c[0] in WHEN for s in SECTIONS for c in s['cards']), '「언제 쓰나」 누락')
ok(page.count('class="snip is-hot"') == hot, '감점 카드 수')
ok(len(set(re.findall(r'<article class="snip[^"]*" id="([^"]+)"', page))) == total, '스니펫 id 중복')

BASE = 'https://hclee-source.github.io/bigdata-practical-snippets/'
for prop in ('og:url" content="' + BASE, 'og:image" content="' + BASE + 'og.png', 'twitter:image" content="' + BASE + 'og.png'):
    ok(prop in page, f'공유 카드 절대 주소: {prop}')
from PIL import Image
for f, size in (('og.png', (1200, 630)), ('favicon.png', (96, 96)), ('apple-touch-icon.png', (180, 180))):
    ok(os.path.exists(f) and Image.open(f).size == size, f'{f} 크기 {size}')
if os.path.exists('og.png'):
    og = Image.open('og.png').convert('RGB')
    ok(og.getpixel((8, 8)) == (43, 47, 156) and len(og.getcolors(1 << 20) or []) > 50, 'og.png 가 표지색 공유 카드가 아니다 — python make_og.py')
ok('og:image:width" content="1200"' in page and 'og:image:height" content="630"' in page, 'og 크기 메타')
svg = open('favicon.svg', encoding='utf-8').read() if os.path.exists('favicon.svg') else ''
ok('<svg' in svg and '<path' in svg, 'favicon.svg 내용')
nf = open('404.html', encoding='utf-8').read() if os.path.exists('404.html') else ''
hrefs = re.findall(r'href="([^"]+)"', nf)
bad = [h for h in hrefs if not h.startswith(('/bigdata-practical-snippets/', 'https://'))]
ok(nf.count('<a ') >= 5, '404 바로 가기 링크')
ok(not bad, f'404 상대 경로 — 하위 주소에서 깨진다: {bad}')
ok(f'감점 포인트 {hot}개' in nf, '404 감점 개수')
ok('[hidden]{display:none!important}' in page, '필터 숨김이 grid 에 덮이지 않게')

# 대비 — CSS 변수 블록을 정확히 잘라 읽는다. #RRGGBB 가 아니면 계산할 수 없으므로 실패.
def block(pattern, name):
    m = re.search(pattern, page, re.S)
    if not ok(m is not None, f'{name} 색 블록을 찾지 못했다'):
        return {}
    return {k: v.strip() for k, v in re.findall(r'--([\w-]+):\s*([^;}]+)', m.group(1))}
light = block(r'<style>\s*:root\{(.*?)\}', '라이트')
dark = block(r'@media \(prefers-color-scheme:dark\)\{:root\{(.*?)\}', '다크')
prnt = block(r'@media print\{\s*:root\{(.*?)\}', '인쇄')
ok(bool(dark) and all(k in light for k in dark), '다크에 라이트에 없는 변수가 있다')
ok(set(prnt) >= set(dark) and all(prnt[k] == light[k] for k in prnt), '인쇄 색이 라이트와 다르거나 빠진 변수가 있다')

def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def cr(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return (x + 0.05) / (y + 0.05)
HEX = re.compile(r'#[0-9a-fA-F]{6}$')
# 글자로 쓰이는 색 — --faint 는 0건으로 흐려진(비활성) 목차 링크에만 쓰여 대비 기준 예외
PAIRS = [('ink', 'bg'), ('ink-2', 'bg'), ('muted', 'bg'), ('accent', 'bg'),       # 본문·보조·라벨
         ('ink', 'bg-2'), ('ink-2', 'bg-2'), ('muted', 'bg-2'),                      # 코드 바탕 위
         ('k', 'bg-2'), ('s', 'bg-2'), ('c', 'bg-2'),                                # 구문 강조
         ('on-accent', 'accent'), ('toast-fg', 'toast-bg'), ('ink', 'mark'),         # 체크·알림·검색 강조
         ('done', 'bg'), ('hl-ink', 'hl'), ('brand-fg', 'brand'), ('brand-2', 'brand')]  # 외움·형광펜 라벨·책등
for name, P in (('라이트', light), ('다크', {**light, **dark})):
    for f_, b_ in PAIRS:
        fv, bv = P.get(f_, '?'), P.get(b_, '?')
        if not ok(bool(HEX.match(fv)) and bool(HEX.match(bv)), f'대비 계산 불가 {name} --{f_}: {fv} / --{b_}: {bv} (#RRGGBB 만)'):
            continue
        ok(cr(fv, bv) >= 4.5, f'대비 미달 {name} --{f_} / --{b_} = {cr(fv, bv):.2f}')
print(f'3. 페이지 점검  화면 전체 대조 · 대비 {len(PAIRS) * 2}쌍')

if tuple(int(v) for v in sklearn.__version__.split('.')[:2]) >= (1, 3):
    print()
    print(f'※ scikit-learn {sklearn.__version__} 에서 돌렸다 — 시험장 하한(1.2)에서도 돌릴 것 (README 「시험장 버전으로 검증」)')
if seen_warn:
    print('\n경고 (실패 아님)')
    for msg, titles in seen_warn.items():
        print(' -', msg, '←', ', '.join(sorted(titles)))
if fails:
    print('\nFAIL', len(fails))
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('\n전부 통과')

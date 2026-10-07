"""검증.  실행: python verify.py   (pandas · numpy · scikit-learn · scipy · statsmodels 필요)

1. 스니펫 실행 — 75개 코드를 가짜 데이터로 전부 실제 실행한다
2. 주석 검산   — 코드 주석에 쓴 주장(버림 방향, sklearn = statsmodels 계수 등)을 숫자로 확인한다
3. 페이지 점검 — index.html 이 cards.py 와 같은지, 공유 카드·아이콘·404·다크모드·인쇄, 글자 대비(WCAG AA)
"""
import builtins, contextlib, html, io, math, os, re, sys, tempfile, warnings
sys.stdout.reconfigure(encoding='utf-8')
warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cards import SECTIONS
from when import WHEN

fails = []
def ok(cond, msg):
    if not cond: fails.append(msg)
    return cond

# ── 1. 스니펫 실행 ─────────────────────────────────────────────
cwd = os.getcwd()
real_help = builtins.help
builtins.help = lambda *a, **k: None          # 시험장 카드의 help() 출력 생략
n_run = 0
for s in SECTIONS:
    ns = {}
    exec(s['setup'], ns)
    for title, tag, hot, kw, code in s['cards']:
        n_run += 1
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(code, ns)
        except Exception as e:
            fails.append(f'실행 실패 [{s["id"]}] {title}: {type(e).__name__} {e}')
builtins.help = real_help
os.chdir(cwd)
print(f'1. 스니펫 실행  {n_run}개')

# ── 2. 주석 검산 ───────────────────────────────────────────────
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression

ok(int(-2.7) == -2 and math.floor(-2.7) == -3 and math.ceil(2.1) == 3, 'int/floor/ceil 방향')
ok(pd.Series([60, 80]).between(60, 80).all(), 'between 양 끝 포함')
ok(pd.Timestamp('2024-01-01').weekday() == 0, 'weekday 월=0')
rng = np.random.default_rng(0); n = 300
d = pd.DataFrame({'x': rng.normal(50, 10, n), 'x2': rng.integers(0, 2, n)})
d['label'] = (d['x'] + rng.normal(0, 8, n) > 50).astype(int)
lg = sm.Logit(d['label'], sm.add_constant(d[['x', 'x2']])).fit(disp=False)
lr = LogisticRegression(penalty=None, max_iter=5000).fit(d[['x', 'x2']], d['label'])
ok(np.allclose([lr.intercept_[0], *lr.coef_[0]], lg.params.values, atol=1e-3), 'sklearn penalty=None ≠ statsmodels Logit')
l2 = LogisticRegression(max_iter=5000).fit(d[['x', 'x2']], d['label'])
ok(not np.allclose(l2.coef_[0], lg.params.values[1:], atol=1e-3), '기본값(l2)도 같은 값이 나온다 — 카드 주석 재검토')
t2 = pd.DataFrame([[10, 20], [20, 10]])
ok(stats.chi2_contingency(t2)[0] < stats.chi2_contingency(t2, correction=False)[0], '2×2 연속성 보정 기본')
x = d['x']; t = (x.mean() - 50) / (x.std() / np.sqrt(n)); r = stats.ttest_1samp(x, 50)
ok(abs(t - r.statistic) < 1e-9 and abs(2 * (1 - stats.t.cdf(abs(t), n - 1)) - r.pvalue) < 1e-9, 't 직접 계산 ≠ ttest_1samp')
a = pd.Series(rng.normal(0, 1, 50)); b = a + 1
ok(stats.ttest_ind(a, b, alternative='less').pvalue < 0.05, "alternative='less' 는 첫 인자 < 둘째 인자")
print('2. 주석 검산   8건')

# ── 3. 페이지 점검 ─────────────────────────────────────────────
os.chdir(HERE)
page = open('index.html', encoding='utf-8').read()
codes = [c[4] for s in SECTIONS for c in s['cards']]
pres = [html.unescape(re.sub(r'<[^>]+>', '', m)) for m in re.findall(r'<pre><code>(.*?)</code></pre>', page, re.S)]
ok(pres == codes, 'index.html 코드가 cards.py 와 다르다 — python build.py 를 다시 돌릴 것')
total, hot = len(codes), sum(c[2] for s in SECTIONS for c in s['cards'])
ok(f'>{total}개<' in page or f'{total}개' in page, '총 개수 표기')
ok(f'감점 포인트 {hot}개' in page, '감점 포인트 개수 표기')
ok(page.count('class="snip is-hot"') == hot, '노란 카드 수')
ok(all(c[0] in WHEN for s in SECTIONS for c in s['cards']), '「언제 쓰나」 누락')
BASE = 'https://hclee-source.github.io/bigdata-practical-snippets/'
for prop in ('og:url" content="' + BASE, 'og:image" content="' + BASE + 'og.png', 'twitter:image" content="' + BASE + 'og.png'):
    ok(prop in page, f'공유 카드 절대 주소: {prop}')
for f in ('og.png', 'favicon.svg', 'favicon.png', 'apple-touch-icon.png', '404.html'):
    ok(os.path.exists(f), f'파일 없음: {f}')
ok('href="favicon.svg"' in page and 'href="apple-touch-icon.png"' in page, '아이콘 링크')
ok('prefers-color-scheme:dark' in page, '다크모드')
ok(re.search(r'@media print\{\s*:root\{', page) is not None, '인쇄 때 밝은 색 되돌리기')
ok('[hidden]{display:none!important}' in page, '필터 숨김이 grid 에 덮이지 않게')
from PIL import Image
ok(Image.open('og.png').size == (1200, 630), 'og.png 크기')

# 글자 대비 — CSS 변수에서 직접 읽는다
def block(src):
    return dict(re.findall(r'--([\w-]+):(#[0-9a-fA-F]{6})', src))
light = block(page[page.index(':root{'):page.index('@media (prefers-color-scheme:dark)')])
dark = {**light, **block(page[page.index('@media (prefers-color-scheme:dark)'):page.index('}}', page.index('@media (prefers-color-scheme:dark)'))])}
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def cr(a, b):
    x, y = sorted([lum(a), lum(b)], reverse=True); return (x + 0.05) / (y + 0.05)
PAIRS = [('ink', 'paper'), ('ink-2', 'paper'), ('muted', 'paper'), ('muted', 'sheet'), ('ink-2', 'sheet'), ('ink-2', 'rule-2'),
         ('green', 'paper'), ('green-ink', 'mint'), ('amber-ink', 'amber-wash'), ('muted', 'code'),
         ('k', 'code'), ('s', 'code'), ('c', 'code'), ('n', 'code'), ('f', 'code'), ('ink', 'code'),
         ('on-green', 'green'), ('toast-fg', 'toast-bg')]
for name, P in (('라이트', light), ('다크', dark)):
    for f_, b_ in PAIRS:
        r = cr(P[f_], P[b_])
        ok(r >= 4.5, f'대비 미달 {name} --{f_} / --{b_} = {r:.2f}')
print(f'3. 페이지 점검  코드 {len(pres)}개 대조 · 대비 {len(PAIRS) * 2}쌍')

if fails:
    print('\nFAIL', len(fails)); [print(' -', f) for f in fails]; sys.exit(1)
print('\n전부 통과')

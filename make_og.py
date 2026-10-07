"""공유 카드용 og.png(1200x630) 생성.  실행: python make_og.py

서체는 페이지와 같은 IBM Plex Sans KR · IBM Plex Mono (OFL). 처음 실행할 때
google/fonts 저장소에서 .fonts/ 로 받아 둔다(.gitignore 대상, 배포에 필요 없음).
"""
import os, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

os.chdir(os.path.dirname(os.path.abspath(__file__)))   # 어디서 실행해도 레포 폴더에 쓴다
sys.path.insert(0, os.getcwd())
from cards import SECTIONS
TOTAL = sum(len(s['cards']) for s in SECTIONS)
HOT = sum(c[2] for s in SECTIONS for c in s['cards'])

W, H = 1200, 630
# 『2027 빠르게 따는 빅데이터분석기사 실기』 표지 색
NAVY = (43, 47, 156)
YELLOW = (245, 228, 0)
WHITE = (255, 255, 255)
SOFT = (205, 208, 240)
CODE_BG = (30, 33, 112)
COMMENT = (150, 156, 214)

GF = 'https://github.com/google/fonts/raw/main/ofl/'
FONTS = {
    'semibold': ('ibmplexsanskr/IBMPlexSansKR-SemiBold.ttf'),
    'regular': ('ibmplexsanskr/IBMPlexSansKR-Regular.ttf'),
    'medium': ('ibmplexsanskr/IBMPlexSansKR-Medium.ttf'),
    'mono': ('ibmplexmono/IBMPlexMono-Regular.ttf'),
}
os.makedirs('.fonts', exist_ok=True)
for key, rel in FONTS.items():
    dst = os.path.join('.fonts', os.path.basename(rel))
    if not os.path.exists(dst):
        urllib.request.urlretrieve(GF + rel, dst)
    FONTS[key] = dst
SEMI, REG, MED, MONO = FONTS['semibold'], FONTS['regular'], FONTS['medium'], FONTS['mono']


def font(path, size):
    return ImageFont.truetype(path, size)


img = Image.new('RGB', (W, H), NAVY)
d = ImageDraw.Draw(img)

x = 96
d.text((x, 92), '2027 빠르게 따는 · 빅데이터분석기사 실기', font=font(MED, 26), fill=WHITE)
d.text((x, 134), f'파이썬 스니펫 {TOTAL}', font=font(SEMI, 88), fill=YELLOW)
d.rectangle([x, 282, W - 96, 284], fill=YELLOW)
d.text((x, 312), '작업형 1·2·3에서 쓰는 코드를 모두 실행해 확인했습니다.', font=font(REG, 29), fill=WHITE)
d.text((x, 356), f'감점 포인트 {HOT}개 · 복사 · 검색 · 암기 모드', font=font(REG, 29), fill=SOFT)

# 스니펫 한 줄 — 페이지와 같은 문법(번호 · 형광펜 라벨 · 제목 | 코드)
y0 = 440
d.text((x, y0 + 4), '07.3', font=font(SEMI, 20), fill=YELLOW)
lab = font(SEMI, 19)
lw = d.textlength('함정', font=lab)
d.rectangle([x + 70, y0 + 2, x + 70 + lw + 12, y0 + 28], fill=YELLOW)
d.text((x + 76, y0 + 1), '함정', font=lab, fill=(20, 24, 23))
d.text((x + 70, y0 + 36), '양성 확률 꺼내기', font=font(SEMI, 25), fill=WHITE)
cx0 = x + 330
d.rectangle([cx0, y0 - 2, W - 96, y0 + 106], fill=CODE_BG)
m = font(MONO, 20)
def code_line(y, parts):
    cx = cx0 + 22
    for text, color in parts:
        d.text((cx, y), text, font=m, fill=color)
        cx += d.textlength(text, font=m)
    assert cx < W - 96 - 10, '코드가 상자 밖으로 나간다'
# 실제 07.3 카드와 같은 변수 이름
code_line(y0 + 12, [('proba = model.predict_proba(X_va)', WHITE)])
code_line(y0 + 42, [('pos = list(model.classes_).index(1)', WHITE)])
code_line(y0 + 72, [('p1 = proba[:, pos]', WHITE), ('   # ROC-AUC', COMMENT)])

d.text((x, H - 54), '골든래빗 · 도서 부속 자료', font=font(REG, 20), fill=SOFT)

img.save('og.png', optimize=True)
print('og.png: %dx%d' % (W, H))

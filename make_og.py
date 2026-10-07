"""공유 카드용 og.png(1200x630) 생성.  실행: python make_og.py"""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
PAPER = (251, 248, 241)
INK = (27, 33, 30)
INK_SOFT = (74, 82, 77)
FAINT = (104, 112, 105)
ACCENT = (20, 108, 80)
CODE = (245, 242, 234)
RULE = (230, 225, 212)
AMBER = (183, 121, 31)
AMBER_INK = (138, 90, 18)
AMBER_WASH = (253, 243, 223)
# 코드 색 — 사이트의 구문 강조와 같은 값
K, S, C, F, N = (20, 108, 80), (143, 83, 16), (102, 109, 103), (29, 91, 134), (168, 61, 41)

BOLD = 'C:/Windows/Fonts/malgunbd.ttf'
REG = 'C:/Windows/Fonts/malgun.ttf'
MONO = 'C:/Windows/Fonts/consola.ttf'
MONO_B = 'C:/Windows/Fonts/consolab.ttf'


def font(path, size):
    return ImageFont.truetype(path, size)


img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

d.rectangle([0, 0, 18, H], fill=ACCENT)          # 필기 공식집과 같은 왼쪽 기둥

x = 88
d.text((x, 92), '빠 르 게   따 는   ·   실 기', font=font(BOLD, 24), fill=ACCENT)
d.text((x, 138), '빅데이터분석기사', font=font(BOLD, 74), fill=INK)
d.text((x, 226), '실기 스니펫', font=font(BOLD, 74), fill=INK)

d.rectangle([x, 348, W - 88, 351], fill=INK)

d.text((x, 378), '작업형 1 · 2 · 3에 쓰는 파이썬 코드 75개.', font=font(REG, 31), fill=INK_SOFT)
d.text((x, 422), '감점 포인트 12개와 암기 모드까지.', font=font(REG, 31), fill=INK_SOFT)

# 작업형 배지 — 사이트의 작업형 필터와 같은 문법
bx = x
for label, filled in (('작업형 1', True), ('작업형 2', False), ('작업형 3', False)):
    f = font(BOLD, 25)
    bw = int(d.textlength(label, font=f)) + 42
    box = [bx, 486, bx + bw, 534]
    if filled:
        d.rounded_rectangle(box, radius=9, fill=ACCENT)
        d.text((bx + 21, 497), label, font=f, fill=(255, 255, 255))
    else:
        d.rounded_rectangle(box, radius=9, fill=(255, 255, 255), outline=RULE, width=2)
        d.text((bx + 21, 497), label, font=f, fill=INK_SOFT)
    bx += bw + 14

# 오른쪽 위 — 코드 한 조각으로 무슨 자료인지 바로 보이게 (감점 포인트 카드)
cx0, cy0, cx1 = W - 450, 88, W - 88
d.rounded_rectangle([cx0, cy0, cx1, cy0 + 196], radius=14, fill=CODE)
d.rectangle([cx0 - 14, cy0 + 6, cx0 - 9, cy0 + 190], fill=AMBER)    # 사이트의 노란 세로선
fl = font(BOLD, 19)
d.rounded_rectangle([cx0 + 24, cy0 + 22, cx0 + 24 + int(d.textlength('함정', font=fl)) + 20, cy0 + 52], radius=6, fill=AMBER_WASH)
d.text((cx0 + 34, cy0 + 25), '함정', font=fl, fill=AMBER_INK)
d.text((cx0 + 90, cy0 + 24), '양성 확률 꺼내기', font=font(BOLD, 21), fill=INK)

m, mb = font(MONO, 19), font(MONO_B, 19)
def code_line(y, parts):
    cx = cx0 + 24
    for text, color in parts:
        d.text((cx, y), text, font=m, fill=color)
        cx += d.textlength(text, font=m)
    assert cx < cx1 - 12, '코드가 카드 밖으로 나간다'

code_line(cy0 + 84, [('p = m.', INK), ('predict_proba', F), ('(X)', INK)])
code_line(cy0 + 118, [('i = ', INK), ('list', F), ('(m.classes_).', INK), ('index', F), ('(', INK), ('1', N), (')', INK)])
code_line(cy0 + 152, [('p1 = p[:, i]', INK), ('   # ROC-AUC', C)])

d.text((x, H - 52), '골든래빗  ·  『2027 빠르게 따는 빅데이터분석기사 실기』 부속 자료',
       font=font(REG, 22), fill=FAINT)

img.save('og.png', optimize=True)
print('og.png 생성 완료: %dx%d' % (W, H))

"""파비콘 생성.  실행: python make_icons.py

favicon.svg  — 벡터. 최신 브라우저가 우선 사용한다.
favicon.png  — 96px. SVG를 못 읽는 곳(구형 브라우저·북마크) 대비.
apple-touch-icon.png — 180px. iOS 홈 화면 추가용.
모양은 코드 프롬프트 「>_」 — 필기 공식집의 Σ와 짝을 이룬다.
"""
from PIL import Image, ImageDraw

ACCENT = (20, 108, 80)
WHITE = (255, 255, 255)

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="실기 스니펫">
  <rect width="64" height="64" rx="13" fill="#146C50"/>
  <path d="M17 21l13 11-13 11" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="33" y="40" width="15" height="6" rx="3" fill="#fff"/>
</svg>
'''
open('favicon.svg', 'w', encoding='utf-8', newline='\n').write(SVG)


def raster(size, radius_ratio=13 / 64):
    ss = 8
    n = size * ss
    u = n / 64                                # SVG 좌표 1칸
    img = Image.new('RGBA', (n, n), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, n - 1, n - 1], radius=int(n * radius_ratio), fill=ACCENT)
    w = int(6 * u)
    pts = [(17 * u, 21 * u), (30 * u, 32 * u), (17 * u, 43 * u)]
    d.line(pts, fill=WHITE, width=w, joint='curve')
    for x, y in (pts[0], pts[2]):             # 둥근 끝
        d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=WHITE)
    d.rounded_rectangle([33 * u, 40 * u, 48 * u, 46 * u], radius=int(3 * u), fill=WHITE)
    return img.resize((size, size), Image.LANCZOS)


raster(96).save('favicon.png', optimize=True)
apple = Image.new('RGB', (180, 180), ACCENT)  # iOS는 둥근 모서리를 스스로 처리한다
apple.paste(raster(180, radius_ratio=0).convert('RGB'), (0, 0))
apple.save('apple-touch-icon.png', optimize=True)
print('favicon.svg / favicon.png(96) / apple-touch-icon.png(180) 생성 완료')

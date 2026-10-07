# 빅데이터분석기사 실기 파이썬 스니펫

『2027 빠르게 따는 빅데이터분석기사 실기』(골든래빗) 부속 자료.
작업형 1·2·3에 쓰는 파이썬 코드 **75개**를 모았고, 감점이 자주 나는 **12개**에는
노란 선과 「함정·필수·빈출」 표시를 붙였습니다. 코드는 교재 풀이의 관례
(`prepare_features`, `reindex(fill_value=0)`, `classes_`로 양성 확률 위치 찾기,
`Logit(...).fit(disp=False)` 등)를 그대로 따릅니다.

공개 주소: **https://hclee-source.github.io/bigdata-practical-snippets/**

필기 편: [빅데이터분석기사 필기 공식집](https://hclee-source.github.io/bigdata-formulas/)

## 화면에서 할 수 있는 것

| 기능 | 설명 |
|---|---|
| 복사 | 스니펫마다 버튼 하나로 코드 복사 |
| 언제 쓰나 | 스니펫마다 한 줄 — 함수 이름을 몰라도 상황으로 찾는다 |
| 검색 | 제목·설명·코드·검색어 전부. `/` 로 검색창, `Esc` 로 지우기 |
| 작업형 필터 | 전체 / 작업형 1 / 2 / 3 |
| 감점 포인트만 | 노란 표시 12개만 |
| 암기 모드 | 코드를 흐리게 가리고, 떠올린 뒤 눌러서 확인 |
| 외웠어요 | 진도(n / 75) 표시와 「안 외운 것만」 보기. 브라우저에 저장된다 |
| 링크 복사 | 지금 화면 그대로의 주소를 복사 |

다크모드는 기기 설정을 따릅니다. 인쇄(Ctrl+P)하면 버튼 없이 코드만, 항상 밝은 색으로 나옵니다.

## 링크로 공유하기

| 주소 | 열리는 화면 |
|---|---|
| `?type=t1` | 작업형 1만 (`t2`·`t3`·`env`=시험장) |
| `?hot=1` | 감점 포인트 12개만 |
| `?type=t3&hot=1` | 작업형 3 감점 포인트 4개 |
| `?q=오즈비` | '오즈비'로 검색한 결과 |

외움 표시와 암기 모드는 개인 설정이라 주소에 넣지 않습니다.

## 배포

GitHub Pages로 그대로 올라갑니다. Settings → Pages → Branch: `main` / `/ (root)`.
빌드 없이 아래 정적 파일만으로 동작합니다.

| 파일 | 역할 |
|---|---|
| `index.html` | 화면 (`build.py` 가 만든다 — 직접 고치지 말 것) |
| `404.html` | 잘못된 주소로 들어왔을 때 |
| `og.png` | 공유 카드 이미지 1200×630 |
| `favicon.svg` · `favicon.png` · `apple-touch-icon.png` | 탭·북마크·홈 화면 아이콘 |

### 저장소 이름을 바꾼다면

`index.html` 의 `og:url`·`og:image`·`twitter:image`는 절대 주소입니다.
**카카오톡은 상대 경로 `og:image`를 읽지 못해서**입니다. 저장소명이나 도메인을 바꾸면
`build.py` 의 이 세 줄과 `verify.py` 의 `BASE` 를 같이 바꿔 주세요.

## 내용을 고칠 때

1. `cards.py` — 스니펫 코드·제목·태그·검색어 / `when.py` — 「언제 쓰나」 한 줄
2. `python build.py` — `index.html` 을 다시 만든다
3. `python verify.py` — 아래를 한 번에 검사한다 (pandas·numpy·scikit-learn·scipy·statsmodels·Pillow 필요)

| 검사 | 내용 |
|---|---|
| 스니펫 실행 | 75개 코드를 가짜 데이터로 **전부 실제 실행** |
| 주석 검산 | 주석에 쓴 주장을 숫자로 확인 — `int()` 는 0 쪽으로 버림, `LogisticRegression(penalty=None)` 계수 = statsmodels `Logit` 계수, 2×2 카이제곱 기본 연속성 보정, t 직접 계산 = `ttest_1samp`, `alternative` 방향 등 |
| 페이지 점검 | `index.html` 코드 = `cards.py` 코드(한 글자까지), 개수 표기, 공유 카드 절대 주소, 아이콘·404, 다크모드, 인쇄 색 되돌리기 |
| 글자 대비 | 라이트·다크 모두 실제 쓰는 18쌍이 WCAG AA(4.5:1) 이상 |

보조 스크립트는 배포에 필요 없고 Pages도 무시합니다.

| 스크립트 | 하는 일 |
|---|---|
| `make_og.py` | `og.png` 재생성 (Pillow, 맑은 고딕·Consolas) |
| `make_icons.py` | 파비콘 3종 재생성 |

## 색

과목 색은 빅분기 실기 CBT와 같은 초록(`#146c50`)입니다. 색은 전부 CSS 변수라
`build.py` 의 `:root` 한 곳만 보면 됩니다. 다크모드는 `@media (prefers-color-scheme:dark)`
에서, 인쇄는 `@media print` 에서 같은 변수를 덮어씁니다. **색을 새로 넣으면 세 곳 모두에
넣고 `verify.py` 의 대비 목록에도 추가하세요.**

## 알아 둘 점

- 시험장의 scikit-learn 버전은 확인하지 못했습니다. 1.2 미만이면 `penalty=None` 대신
  `penalty='none'` 문자열을 써야 해서 해당 카드 주석에 적어 두었습니다.
- 스니펫은 교재 원본 데이터가 아니라, 같은 컬럼 구조의 가짜 데이터로 실행 검증합니다.

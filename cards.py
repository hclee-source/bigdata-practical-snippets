# 빅데이터분석기사 실기 스니펫 — 카드 정의 (교재 『2027 빠르게 따는 빅데이터분석기사 실기』 본문 코드 관례 기준)
# 섹션: id, 제목, 설명, setup(검증용 가짜 데이터 — 페이지엔 안 나감), cards
# card: (제목, 태그, hot, 검색어, 코드)

SECTIONS = []
def sec(id, title, desc, setup, cards): SECTIONS.append(dict(id=id, title=title, desc=desc, setup=setup, cards=cards))

T1_SETUP = r'''
import pandas as pd, numpy as np
rng = np.random.default_rng(0)
n = 200
df = pd.DataFrame({
  'id': range(n),
  'group': rng.choice(['G1','G2','G3'], n),
  'flag': rng.integers(0, 2, n),
  'region': rng.choice(['north','east','central','south'], n),
  'segment': rng.choice(['A','B','C'], n),
  'age': rng.integers(20, 70, n),
  'score': rng.normal(70, 10, n).round(1),
  'amount': rng.normal(100000, 30000, n).round(0),
  'price': np.r_[rng.normal(50, 10, n-3), [300, 400, -100]],
  'views': np.where(rng.random(n) < .1, np.nan, rng.integers(10, 999, n)),
  'rating': np.where(rng.random(n) < .1, np.nan, rng.uniform(1, 5, n).round(1)),
  'status': rng.choice(['방문','취소','대기'], n),
  'code': rng.choice(['AB-01','CD-02','AB-03'], n),
  'name': rng.choice(['Kim Apple','Lee Pear','park apple'], n),
  'date': pd.date_range('2024-01-01', periods=n, freq='D').astype(str),
  'end_date': pd.date_range('2024-01-05', periods=n, freq='D').astype(str),
  'qty': rng.integers(1, 10, n),
  'unit_price': rng.integers(1000, 5000, n),
})
other = pd.DataFrame({'id': range(0, n, 2), 'extra': 1})
import os, tempfile
os.chdir(tempfile.mkdtemp()); os.makedirs('data')
df.to_csv('data/파일명.csv', index=False)
'''

sec('t1base', '작업형 1 · 판다스 기본', '불러오기 → 확인 → 조건 → 계산 → print. 작업형 1 은 이 다섯 단계 안에서 끝난다.', T1_SETUP, [
('불러오기 · 크기 · 앞부분', 'pandas', False, 'read_csv shape head info describe 불러오기 확인 to_string',
'''import pandas as pd
import numpy as np

df = pd.read_csv('data/파일명.csv')
print(df.shape)                        # (행, 열)
print(df.head(3).to_string(index=False))
df.info()                              # 자료형 · 결측 개수
print(df.describe())                   # 수치형 요약'''),
('컬럼 선택 · loc / iloc', 'pandas', False, 'loc iloc 컬럼 선택 인덱싱 행 열',
'''df['score']                         # Series
df[['group', 'score']]              # DataFrame
df.loc[df['flag'] == 1, 'amount']   # 조건 + 컬럼
df.loc[0, 'score']                  # 라벨 기준
df.iloc[0, 2]                       # 위치 기준 (0번 행, 2번 열)
df.iloc[:10]                        # 앞 10행'''),
('조건 필터링 · 다중 조건', '빈출', True, '조건 필터링 & | isin between 괄호 다중 조건 ~',
'''cond = (df['flag'] == 1) & (df['group'] == 'G2')   # 조건마다 괄호
print(cond.sum())                       # 조건 만족 행 수
print(df.loc[cond, 'amount'].mean())

df[df['region'].isin(['north', 'east'])]
df[df['score'].between(60, 80)]        # 60 이상 80 이하 (양 끝 포함)
df[~(df['segment'] == 'B')]            # 부정은 ~'''),
('정렬 후 N번째 값', 'sort_values', False, '정렬 sort_values ascending 상위 N 번째 iloc nlargest',
'''s = df.sort_values('amount', ascending=False)
print(s.iloc[0]['id'])             # 1등
print(s.iloc[2]['amount'])         # 3등 값

# 여러 기준 정렬
df.sort_values(['score', 'age'], ascending=[False, True])

df.nlargest(10, 'amount')          # 상위 10행 바로'''),
('value_counts — 이름인가 개수인가', '함정', True, 'value_counts 최빈값 index iloc normalize 비율 mode',
'''vc = df['group'].value_counts()
print(vc.index[0])     # 가장 많은 그룹 「이름」
print(vc.iloc[0])      # 그 그룹의 「개수」

df['group'].value_counts(normalize=True)   # 비율
df['group'].mode()[0]                      # 최빈값'''),
('기초 통계 함수', 'pandas', False, 'sum mean median std var max min nunique quantile 분위수 표준편차',
'''df['score'].sum(); df['score'].mean(); df['score'].median()
df['score'].std()        # 표본표준편차 (ddof=1)
df['score'].std(ddof=0)  # 모표준편차 — 문제에 「모」가 있으면
df['score'].var()
df['score'].quantile(0.75)
df['group'].nunique()    # 고유값 개수'''),
])

sec('t1prep', '작업형 1 · 결측치 · 이상치', '「몇 개인가」와 「채운 뒤 계산」이 단골. 채울 값은 반드시 원본에서 먼저 구한다.', T1_SETUP, [
('결측치 확인 · 제거', 'isna', False, '결측치 isna isnull sum dropna subset 제거',
'''print(df.isna().sum())               # 컬럼별 결측 개수
print(df['views'].isna().sum())
print(df.isna().sum().sum())         # 전체 결측 개수

drop_df = df.dropna(subset=['rating', 'views'])
print(len(df) - len(drop_df))        # 제거된 행 수'''),
('결측치 대체 — 값은 먼저 구한다', 'fillna', False, 'fillna median mean mode 결측치 대체 채우기',
'''work = df.copy()
med = work['rating'].median()     # 채우기 「전」 값으로 구한다
work['rating'] = work['rating'].fillna(med)

work['views'] = work['views'].fillna(work['views'].mean())
work['status'] = work['status'].fillna(work['status'].mode()[0])'''),
('그룹별 값으로 결측치 채우기', 'transform', False, 'groupby transform 그룹별 중앙값 결측 대체',
'''work = df.copy()
grp_med = work.groupby('group')['views'].transform('median')
work['views'] = work['views'].fillna(grp_med)
# 그룹 전체가 결측이면 전체 중앙값으로 한 번 더
work['views'] = work['views'].fillna(work['views'].median())'''),
('IQR 이상치', 'quantile', False, 'IQR 이상치 quantile 1.5 사분위 lower upper outlier',
'''q1 = df['price'].quantile(0.25)
q3 = df['price'].quantile(0.75)
iqr = q3 - q1
lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr

out = (df['price'] < lower) | (df['price'] > upper)
print(out.sum())                      # 이상치 개수
print(df.loc[~out, 'price'].mean())   # 이상치 제외 평균'''),
('이상치 바꾸기 · 표준화', 'clip', False, 'clip 상한 하한 대체 표준화 z-score min-max 정규화',
'''capped = df['price'].clip(lower, upper)    # 경계값으로 대체

z = (df['score'] - df['score'].mean()) / df['score'].std()
print((z.abs() > 3).sum())                 # |z| > 3 개수

lo, hi = df['score'].min(), df['score'].max()
mm = (df['score'] - lo) / (hi - lo)              # min-max 0~1'''),
('중복 처리', 'duplicated', False, '중복 duplicated drop_duplicates keep',
'''print(df.duplicated().sum())                    # 완전 중복 행 수
print(df.duplicated(subset=['id']).sum())       # id 기준 중복
dedup = df.drop_duplicates(subset=['id'], keep='first')'''),
])

sec('t1derive', '작업형 1 · 파생변수 · 문자열 · 날짜', '컬럼을 하나 만들고 그걸로 다시 집계하는 2단계 문제가 대부분이다.', T1_SETUP, [
('파생변수 · 구간 나누기', 'pd.cut', False, '파생변수 pd.cut 구간 bins labels right qcut',
'''df['total'] = df['qty'] * df['unit_price']
df['is_high'] = (df['amount'] >= 150000).astype(int)

bins = [0, 30, 40, 50, float('inf')]
df['age_band'] = pd.cut(df['age'], bins=bins,
                        labels=['~29', '30대', '40대', '50+'],
                        right=False)      # [0,30) [30,40) ...
df['q4'] = pd.qcut(df['score'], 4, labels=False)   # 4분위 0~3'''),
('값 바꾸기 · map · apply', 'map', False, 'map replace apply lambda np.where 값 변경 조건',
'''df['flag_txt'] = df['flag'].map({1: 'Y', 0: 'N'})
df['status2'] = df['status'].map({'방문': 1, '취소': -1, '대기': 0})
df['region2'] = df['region'].replace('central', 'center')
df['grade'] = np.where(df['score'] >= 70, 'pass', 'fail')
df['len'] = df['name'].apply(lambda x: len(x))'''),
('문자열 처리', 'str', False, 'str contains split startswith upper lower replace len 문자열',
'''df['code'].str.split('-').str[0]          # 'AB-01' → 'AB'
df['code'].str[:2]                        # 앞 두 글자
df['name'].str.lower().str.contains('apple')
df['code'].str.startswith('AB')
df['name'].str.replace(' ', '')
df['name'].str.len()'''),
('날짜 처리', 'datetime', False, '날짜 to_datetime dt year month day weekday dayofweek 요일 주말',
'''df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['weekday'] = df['date'].dt.weekday     # 월=0 … 일=6
df['is_weekend'] = (df['weekday'] >= 5).astype(int)
df[(df['date'] >= '2024-03-01') & (df['date'] < '2024-04-01')]'''),
('날짜 차이 · 기간', 'timedelta', False, '날짜 차이 days 기간 timedelta 일수 경과',
'''df['date'] = pd.to_datetime(df['date'])
df['end_date'] = pd.to_datetime(df['end_date'])
df['days'] = (df['end_date'] - df['date']).dt.days
df['hours'] = (df['end_date'] - df['date']).dt.total_seconds() / 3600'''),
])

sec('t1agg', '작업형 1 · 집계 · 병합', 'groupby 한 줄로 끝나는 문제와, 결과에서 다시 하나를 고르는 문제로 나뉜다.', T1_SETUP, [
('groupby 기본', 'groupby', False, 'groupby mean sum count size 그룹별 집계',
'''df.groupby('group')['amount'].mean()
df.groupby('group')['amount'].sum().sort_values(ascending=False)
df.groupby('group').size()             # 그룹별 행 수
df.groupby(['region', 'group'])['score'].mean().reset_index()'''),
('agg 이름 붙여 여러 집계', 'agg', False, 'agg named aggregation 여러 집계 count sum mean',
'''summary = df.groupby('region').agg(
    cnt=('id', 'count'),
    amount_sum=('amount', 'sum'),
    score_mean=('score', 'mean'),
).sort_values('amount_sum', ascending=False)
print(summary.round(2))'''),
('집계 결과에서 하나 고르기', 'idxmax', False, 'idxmax idxmin 최대 그룹 이름 abs 절댓값 최대',
'''g = df.groupby('group')['amount'].mean()
print(g.idxmax(), g.max())     # 평균이 가장 큰 그룹과 그 값
print(g.idxmin())

bal = df.groupby('region')['flag'].sum()
key = bal.abs().idxmax()       # 절댓값이 가장 큰 그룹
print(key, bal.loc[key])       # 값은 원래 부호로'''),
('pivot_table · crosstab · unstack', 'pivot', False, 'pivot_table crosstab unstack 교차표 피벗 aggfunc',
'''pt = df.pivot_table(index='region', columns='group',
                    values='amount', aggfunc='mean')
ct = pd.crosstab(df['region'], df['group'])            # 빈도
ct_r = pd.crosstab(df['region'], df['group'], normalize='index')  # 행 비율
wide = df.groupby(['region', 'group'])['amount'].mean().unstack()'''),
('병합 · 이어 붙이기', 'merge', False, 'merge join concat how left inner 병합 결합',
'''m = pd.merge(df, other, on='id', how='left')   # inner/left/right/outer
both = pd.concat([df, df], axis=0, ignore_index=True)  # 위아래
side = pd.concat([df, other], axis=1)                  # 좌우'''),
('상관계수 · 순위 · 누적', 'corr', False, 'corr 상관계수 rank cumsum shift diff 누적 순위',
'''df[['age', 'score', 'amount']].corr()
df['age'].corr(df['score'])                    # 피어슨
df['age'].corr(df['score'], method='spearman')
df['rank'] = df['amount'].rank(ascending=False, method='min')
df['cum'] = df['amount'].cumsum()
df['prev'] = df['amount'].shift(1)'''),
])

sec('t1answer', '작업형 1 · 답안 처리', '값은 맞았는데 형식에서 틀린다. 정수인지, 몇째 자리인지, 버림인지 반올림인지부터 본다.', T1_SETUP, [
('정수 처리 — int 는 버림이다', '함정', True, 'int round 정수 버림 반올림 소수점 답안',
'''x = df['amount'].mean()
print(int(x))          # 소수점 버림 (0 쪽으로 자름)
print(round(x))        # 반올림 → 정수
print(round(x, 2))     # 소수 둘째 자리까지
# 「정수로(소수점 이하 버림)」      → int(x)
# 「소수 셋째 자리에서 반올림」     → round(x, 2)'''),
('음수 · 올림 · 내림', 'math', False, 'floor ceil 음수 내림 올림 trunc np.floor math',
'''import math
print(int(-2.7))         # -2  (0 쪽으로)
print(math.floor(-2.7))  # -3  (아래로)
print(math.ceil(2.1))    # 3
np.floor(df['score'])    # Series 버림
np.ceil(df['score'])'''),
('처음부터 정수인 값', 'sum', False, 'sum 개수 정수 bool 결측 개수 행 수',
'''print((df['amount'] >= 150000).sum())   # 조건 만족 개수
print(df['views'].isna().sum())         # 결측 개수
print(df['flag'].sum())                 # 0/1 합
print(len(df[df['flag'] == 1]))'''),
('최종 답은 값 하나만', '필수', True, 'print answer 출력 최종 답 점검 출력',
'''cond = df['group'] == 'G1'
print('G1 행 수:', cond.sum())     # 점검용은 설명을 붙여 출력

answer = round(df.loc[cond, 'score'].mean(), 2)
print(answer)                      # 답안 칸에는 이 숫자만 입력'''),
])

T2_SETUP = r'''
import pandas as pd, numpy as np, os, tempfile
os.chdir(tempfile.mkdtemp())
os.makedirs('data', exist_ok=True)
rng = np.random.default_rng(0)
def mk(n, with_y=True):
    d = pd.DataFrame({
      'id': range(n),
      'num1': np.where(rng.random(n) < .05, np.nan, rng.normal(0, 1, n)),
      'num2': rng.integers(0, 100, n).astype(float),
      'cat1': rng.choice(['a','b','c', None], n),
      'cat2': rng.choice(['x','y'], n),
    })
    if with_y: d['target'] = (d['num2'] + rng.normal(0, 20, n) > 50).astype(int)
    return d
train = mk(400); test = mk(150, False)
test.loc[0, 'cat1'] = 'z_only_test'
train.to_csv('data/train.csv', index=False); test.to_csv('data/test.csv', index=False)
sample = pd.DataFrame({'id': test['id'], 'pred': 0})
target_col, id_col = 'target', 'id'
'''

PREP_FN = r'''
def prepare_features(ref_X, other_X):
    ref_X, other_X = ref_X.copy(), other_X.copy()
    cat = ref_X.select_dtypes(include='object').columns
    num = ref_X.select_dtypes(exclude='object').columns
    for c in num:
        m = ref_X[c].median(); ref_X[c] = ref_X[c].fillna(m); other_X[c] = other_X[c].fillna(m)
    for c in cat:
        ref_X[c] = ref_X[c].fillna('unknown'); other_X[c] = other_X[c].fillna('unknown')
    ref_X = pd.get_dummies(ref_X)
    other_X = pd.get_dummies(other_X).reindex(columns=ref_X.columns, fill_value=0)
    return ref_X, other_X
'''

sec('t2prep', '작업형 2 · 전처리', 'target·id 분리 → 결측 → 인코딩 → train 기준으로 컬럼 맞추기. 이 순서만 지키면 된다.', T2_SETUP, [
('라이브러리 · 데이터 불러오기', 'sklearn', False, 'import train test sample_submission 불러오기',
'''import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

train = pd.read_csv('data/train.csv')
test = pd.read_csv('data/test.csv')
print(train.shape, test.shape)'''),
('target 찾기 · 분류인가 회귀인가', 'target', False, 'target 분류 회귀 이진 다중 value_counts nunique train에만 있는 컬럼',
'''# train 에만 있는 컬럼 = target 후보
print(set(train.columns) - set(test.columns))
print(train[target_col].value_counts().sort_index())
print(train[target_col].nunique())
# 값 2개   → 이진분류 (ROC-AUC 면 확률 제출)
# 값 여러 개 → 다중분류 (Macro F1 · 클래스 제출)
# 연속값   → 회귀'''),
('X · y 분리 — id 는 뺀다', 'drop', False, 'target 분리 id 제거 X y drop columns',
'''X_raw = train.drop(columns=[target_col, id_col]).copy()
y = train[target_col].copy()
test_raw = test.drop(columns=[id_col]).copy()
print(X_raw.shape, y.shape, test_raw.shape)'''),
('결측 채우기 — 기준은 train', '함정', True, 'fillna median unknown select_dtypes object 결측 train 기준',
'''cat_cols = X_raw.select_dtypes(include='object').columns
num_cols = X_raw.select_dtypes(exclude='object').columns

for col in num_cols:
    med = X_raw[col].median()                    # train 에서 구한 값을
    X_raw[col] = X_raw[col].fillna(med)
    test_raw[col] = test_raw[col].fillna(med)    # test 에도 그대로
for col in cat_cols:
    X_raw[col] = X_raw[col].fillna('unknown')
    test_raw[col] = test_raw[col].fillna('unknown')'''),
('원-핫 인코딩 + 컬럼 맞추기', '필수', True, 'get_dummies reindex fill_value 컬럼 불일치 columns.equals 원핫',
'''X_enc = pd.get_dummies(X_raw)
test_enc = pd.get_dummies(test_raw)
test_enc = test_enc.reindex(columns=X_enc.columns, fill_value=0)

print(X_enc.columns.equals(test_enc.columns))   # True 여야 한다'''),
('라벨 인코딩 (대안)', 'LabelEncoder', False, 'LabelEncoder 라벨 인코딩 범주형 숫자 변환 concat',
'''from sklearn.preprocessing import LabelEncoder

X_le, test_le = X_raw.copy(), test_raw.copy()
for col in cat_cols:
    le = LabelEncoder()
    le.fit(pd.concat([X_le[col], test_le[col]]))   # test 에만 있는 값 대비
    X_le[col] = le.transform(X_le[col])
    test_le[col] = le.transform(test_le[col])'''),
('전처리 함수로 묶기 (교재 패턴)', 'prepare_features', False, 'prepare_features 함수 전처리 재사용 검증 최종',
'''def prepare_features(ref_X, other_X):
    ref_X, other_X = ref_X.copy(), other_X.copy()
    cat = ref_X.select_dtypes(include='object').columns
    num = ref_X.select_dtypes(exclude='object').columns
    for c in num:
        m = ref_X[c].median()
        ref_X[c] = ref_X[c].fillna(m)
        other_X[c] = other_X[c].fillna(m)
    for c in cat:
        ref_X[c] = ref_X[c].fillna('unknown')
        other_X[c] = other_X[c].fillna('unknown')
    ref_X = pd.get_dummies(ref_X)
    other_X = pd.get_dummies(other_X)
    other_X = other_X.reindex(columns=ref_X.columns, fill_value=0)
    return ref_X, other_X

X_raw = train.drop(columns=[target_col, id_col])
test_raw = test.drop(columns=[id_col])'''),
('스케일링 (필요할 때만)', 'StandardScaler', False, 'StandardScaler MinMaxScaler 스케일링 fit_transform transform',
'''from sklearn.preprocessing import StandardScaler

X_enc, test_enc = prepare_features(X_raw, test_raw)
sc = StandardScaler()
X_sc = sc.fit_transform(X_enc)      # train 은 fit_transform
test_sc = sc.transform(test_enc)    # test 는 transform 만
# 트리 모델(RandomForest)은 스케일링 없이도 된다'''),
])

sec('t2model', '작업형 2 · 모델 · 검증', '검증으로 점수를 보고, 전체 train 으로 다시 학습해 test 를 예측한다.', T2_SETUP + PREP_FN + r'''
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, mean_absolute_error, mean_squared_error, r2_score
X_raw = train.drop(columns=[target_col, id_col]); y = train[target_col]; test_raw = test.drop(columns=[id_col])
yr = train['num2'] * 1.5 + rng.normal(0, 5, len(train)) + 10
''', [
('검증 데이터 나누기', 'train_test_split', False, 'train_test_split stratify test_size random_state 검증',
'''X_tr_raw, X_va_raw, y_tr, y_va = train_test_split(
    X_raw, y, test_size=0.2, random_state=0,
    stratify=y)              # 분류면 stratify, 회귀면 빼기
X_tr, X_va = prepare_features(X_tr_raw, X_va_raw)'''),
('분류 모델', 'RandomForest', False, 'RandomForestClassifier 분류 fit predict n_estimators',
'''model = RandomForestClassifier(n_estimators=200, random_state=0)
model.fit(X_tr, y_tr)
pred = model.predict(X_va)
print(accuracy_score(y_va, pred))'''),
('양성 확률 꺼내기', '함정', True, 'predict_proba classes_ 양성 확률 positive_index roc_auc 이진분류',
'''proba = model.predict_proba(X_va)            # (행, 클래스 수)
pos = list(model.classes_).index(1)           # 라벨 1 의 열 위치
p1 = proba[:, pos]
print(roc_auc_score(y_va, p1))                # ROC-AUC 는 확률로'''),
('분류 평가지표', 'metrics', False, 'f1 macro accuracy precision recall roc_auc 평가지표 분류',
'''from sklearn.metrics import precision_score, recall_score

accuracy_score(y_va, pred)
f1_score(y_va, pred)                    # 이진
f1_score(y_va, pred, average='macro')   # 다중분류 Macro F1
precision_score(y_va, pred); recall_score(y_va, pred)
roc_auc_score(y_va, p1)                 # 확률값 넣기'''),
('회귀 모델', 'RandomForest', False, 'RandomForestRegressor 회귀 fit predict',
'''Xr_tr_raw, Xr_va_raw, yr_tr, yr_va = train_test_split(
    X_raw, yr, test_size=0.2, random_state=0)
Xr_tr, Xr_va = prepare_features(Xr_tr_raw, Xr_va_raw)

reg = RandomForestRegressor(n_estimators=200, random_state=0)
reg.fit(Xr_tr, yr_tr)
r_pred = reg.predict(Xr_va)'''),
('회귀 평가지표', 'metrics', False, 'MAE MSE RMSE RMSLE R2 결정계수 회귀 평가지표 sqrt',
'''from sklearn.metrics import mean_squared_log_error

mae = mean_absolute_error(yr_va, r_pred)
mse = mean_squared_error(yr_va, r_pred)
rmse = np.sqrt(mse)                                      # RMSE
rmsle = np.sqrt(mean_squared_log_error(yr_va, r_pred))   # 음수가 있으면 오류
r2 = r2_score(yr_va, r_pred)'''),
('다른 모델로 바꿔 보기', 'sklearn', False, 'LogisticRegression DecisionTree GradientBoosting LinearRegression 모델 교체',
'''from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import GradientBoostingClassifier

LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
DecisionTreeClassifier(max_depth=5, random_state=0).fit(X_tr, y_tr)
GradientBoostingClassifier(random_state=0).fit(X_tr, y_tr)
LinearRegression().fit(Xr_tr, yr_tr)'''),
('최종 학습 — 전체 train 으로', 'fit', False, '최종 학습 전체 train 재학습 test 예측',
'''X_full, test_enc = prepare_features(X_raw, test_raw)
final = RandomForestClassifier(n_estimators=200, random_state=0)
final.fit(X_full, y)

pos = list(final.classes_).index(1)
test_pred = final.predict_proba(test_enc)[:, pos]   # 확률 제출
# test_pred = final.predict(test_enc)              # 클래스 제출'''),
])

sec('t2submit', '작업형 2 · 제출 파일', '파일이 틀리면 모델이 아무리 좋아도 0점이다. 저장하고 다시 읽어서 확인한다.', T2_SETUP + r'''
test_pred = np.random.default_rng(1).random(len(test))
''', [
('result.csv 만들기', '필수', True, 'result.csv to_csv index=False pred 제출 sample_submission',
'''result = pd.DataFrame({'pred': test_pred})
# sample_submission 이 주어지면 복사해서 채운다
# result = sample.copy(); result['pred'] = test_pred
result.to_csv('result.csv', index=False)   # index=False 필수'''),
('저장한 파일 다시 읽어 확인', '검증', False, '제출 확인 read_csv shape columns 결측 행 수 검증',
'''check = pd.read_csv('result.csv')
print(check.shape)                     # (test 행 수, 1)
print(check.columns.tolist())          # ['pred']
print(len(check) == len(test))         # True
print(check.isna().sum().sum())        # 0
print(check.head())'''),
('제출값 형태 점검', 'pred', False, '확률 클래스 회귀 범위 min max value_counts 점검',
'''print(check['pred'].min(), check['pred'].max())  # 확률이면 0~1
print(check['pred'].value_counts().head())        # 클래스면 분포 확인
# target 이 양수뿐인 회귀면 음수 예측이 없는지도 본다
print((check['pred'] < 0).sum())'''),
])

T3_SETUP = r'''
import pandas as pd, numpy as np
rng = np.random.default_rng(0)
n = 120
df = pd.DataFrame({
  'x': rng.normal(50, 10, n),
  'x2': rng.integers(0, 2, n),
  'x3': rng.normal(0, 1, n),
  'group': np.repeat(['A','B','C'], n // 3),
  'cat': rng.choice(['p','q'], n),
  'region': rng.choice(['north','south','east'], n),
  'before': rng.normal(60, 8, n),
})
df['after'] = df['before'] + rng.normal(2, 4, n)
df['y'] = 3 + 0.5 * df['x'] + 2 * df['x2'] + rng.normal(0, 3, n)
df['label'] = (df['x'] + rng.normal(0, 8, n) > 50).astype(int)
df['success'] = rng.integers(0, 2, n)
df['grade'] = rng.choice(['A','B','C','D'], n)
a = df.loc[df['cat'] == 'p', 'x']; b = df.loc[df['cat'] == 'q', 'x']
'''
T3_IMPORTS = "\nfrom scipy import stats\nimport statsmodels.api as sm\nfrom statsmodels.formula.api import ols\n"

sec('t3test', '작업형 3 · t-검정 · 비율 검정', '함수보다 「방향(alternative)」과 「무엇 − 무엇」을 먼저 정한다.', T3_SETUP, [
('라이브러리', 'scipy', False, 'scipy stats statsmodels import ols proportions_ztest',
'''from scipy import stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.proportion import proportions_ztest'''),
('단일표본 t-검정', 'ttest_1samp', False, 'ttest_1samp 단일표본 기준값 평균 t검정',
'''r = stats.ttest_1samp(df['x'], 50, alternative='two-sided')
print(round(r.statistic, 4), round(r.pvalue, 4))'''),
('검정 방향 alternative', '함정', True, 'alternative two-sided greater less 단측 양측 방향 크다 작다',
'''# 대립가설 「평균이 50 보다 크다」 → greater
stats.ttest_1samp(df['x'], 50, alternative='greater')
# 「작다」 → less,  「다르다」 → two-sided (기본값)
# 두 표본이면 「첫 번째 인자 − 두 번째 인자」 기준
stats.ttest_ind(a, b, alternative='less')     # a 평균 < b 평균'''),
('정규성 · 등분산 검정', 'shapiro', False, 'shapiro 정규성 levene 등분산 bartlett 검정',
'''print(stats.shapiro(a).pvalue)          # p ≥ 0.05 → 정규성 만족
print(stats.levene(a, b).pvalue)        # p ≥ 0.05 → 등분산
print(stats.bartlett(a, b).pvalue)'''),
('독립표본 t-검정', 'ttest_ind', False, 'ttest_ind 독립표본 equal_var 등분산 welch 두 집단',
'''lev_p = stats.levene(a, b).pvalue
r = stats.ttest_ind(a, b, equal_var=(lev_p >= 0.05))   # 등분산 아니면 Welch
print(round(r.statistic, 4), round(r.pvalue, 4))
print(round(a.mean() - b.mean(), 4))     # 평균 차이 방향 확인'''),
('대응표본 t-검정', 'ttest_rel', False, 'ttest_rel 대응표본 전후 before after 차이',
'''# 「사후 − 사전」 순서로 넣는다
r = stats.ttest_rel(df['after'], df['before'], alternative='greater')
print(round(r.statistic, 4), round(r.pvalue, 4))
print(round((df['after'] - df['before']).mean(), 4))'''),
('신뢰구간', 'confidence_interval', False, '신뢰구간 confidence_interval t.interval 95%',
'''r = stats.ttest_1samp(df['x'], 50)
ci = r.confidence_interval(confidence_level=0.95)
print(round(ci.low, 4), round(ci.high, 4))

se = stats.sem(df['x'])
stats.t.interval(0.95, len(df) - 1, loc=df['x'].mean(), scale=se)'''),
('검정통계량 직접 계산', 't', False, '검정통계량 직접 계산 표준오차 공식 t값',
'''n = len(df); m = df['x'].mean(); s = df['x'].std()
t = (m - 50) / (s / np.sqrt(n))
p = 2 * (1 - stats.t.cdf(abs(t), df=n - 1))   # 양측
print(round(t, 4), round(p, 4))'''),
('비율 검정 (1표본 · 2표본)', 'proportions_ztest', False, '비율 검정 proportions_ztest 성공 수 nobs value z검정',
'''cnt, nobs = df['success'].sum(), len(df)
z, p = proportions_ztest(count=cnt, nobs=nobs, value=0.5)     # 1표본

s = df.groupby('cat')['success'].agg(['sum', 'count'])
z2, p2 = proportions_ztest(count=s['sum'].values,
                           nobs=s['count'].values)             # 2표본'''),
])

sec('t3anova', '작업형 3 · 분산분석 · 카이제곱', '세 집단 이상의 평균은 ANOVA, 범주끼리의 관계는 카이제곱.', T3_SETUP + T3_IMPORTS, [
('일원분산분석 (scipy)', 'f_oneway', False, 'f_oneway 일원분산분석 ANOVA 세 집단 F',
'''groups = [g['x'].values for _, g in df.groupby('group')]
r = stats.f_oneway(*groups)
print(round(r.statistic, 4), round(r.pvalue, 4))'''),
('분산분석표 (statsmodels)', 'anova_lm', False, 'ols anova_lm 분산분석표 C() 이원 typ formula',
'''model = ols('x ~ C(group)', data=df).fit()
print(sm.stats.anova_lm(model, typ=2))

# 이원분산분석 (교호작용 포함)
m2 = ols('x ~ C(group) * C(cat)', data=df).fit()
print(sm.stats.anova_lm(m2, typ=2))'''),
('사후검정 (Tukey)', 'tukeyhsd', False, 'tukey pairwise_tukeyhsd 사후검정 다중비교',
'''from statsmodels.stats.multicomp import pairwise_tukeyhsd

res = pairwise_tukeyhsd(df['x'], df['group'], alpha=0.05)
print(res)'''),
('카이제곱 적합도', 'chisquare', False, 'chisquare 적합도 기대비율 관측도수 기대도수',
'''obs = df['grade'].value_counts().sort_index()      # A B C D
exp_ratio = np.array([0.1, 0.2, 0.3, 0.4])
r = stats.chisquare(obs, f_exp=exp_ratio * obs.sum())   # 합이 같아야 한다
print(round(r.statistic, 4), round(r.pvalue, 4))'''),
('카이제곱 독립성', 'chi2_contingency', False, 'chi2_contingency 독립성 crosstab 교차표 기대도수 자유도',
'''table = pd.crosstab(df['region'], df['cat'])
chi2, p, dof, expected = stats.chi2_contingency(table)
print(round(chi2, 4), round(p, 4), dof)
print(np.round(expected, 2))
# 2×2 표는 기본이 연속성 보정 — 보정 없이: correction=False'''),
('가설 기각 판단', 'p-value', False, 'p-value 유의수준 기각 채택 귀무가설 0.05',
'''alpha = 0.05
p = r.pvalue
print('기각' if p < alpha else '채택')
# p < α → 귀무가설 기각 (차이·관계가 있다)
# p ≥ α → 귀무가설 채택 (기각하지 못한다)'''),
])

sec('t3reg', '작업형 3 · 상관 · 회귀', 'statsmodels 결과에서 필요한 값 하나만 꺼내는 게 실력이다. summary 전체를 외울 필요는 없다.', T3_SETUP + T3_IMPORTS, [
('상관분석', 'pearsonr', False, 'pearsonr spearmanr 상관분석 상관계수 p-value',
'''r = stats.pearsonr(df['x'], df['y'])
print(round(r.statistic, 4), round(r.pvalue, 4))
s = stats.spearmanr(df['x'], df['y'])
print(round(s.statistic, 4))'''),
('선형회귀 OLS', 'sm.OLS', False, 'OLS add_constant 상수항 회귀분석 선형회귀 statsmodels fit',
'''X = sm.add_constant(df[['x', 'x2']])     # 상수항 꼭 추가
model = sm.OLS(df['y'], X).fit()
print(model.summary())'''),
('회귀 결과에서 값 꺼내기', '빈출', True, 'params pvalues rsquared rsquared_adj fvalue f_pvalue 회귀계수 결정계수',
'''model.params['x']          # 회귀계수
model.pvalues['x']         # 계수 p-value
model.rsquared             # 결정계수 R²
model.rsquared_adj         # 수정된 R²
model.fvalue, model.f_pvalue
model.tvalues['x']
model.params.drop('const').abs().idxmax()   # 계수 절댓값이 가장 큰 변수'''),
('formula 로 회귀 (범주형 포함)', 'ols', False, 'ols formula C() 범주형 회귀 더미',
'''m = ols('y ~ x + x2 + C(region)', data=df).fit()
print(m.params)
print(m.rsquared)'''),
('신뢰구간 · 예측', 'conf_int', False, 'conf_int 신뢰구간 predict get_prediction summary_frame 예측구간',
'''print(model.conf_int(alpha=0.05).loc['x'])     # 계수 95% 신뢰구간

new = pd.DataFrame({'x': [55.0], 'x2': [1]})
new_X = sm.add_constant(new, has_constant='add')[model.params.index]
print(model.predict(new_X).iloc[0])
print(model.get_prediction(new_X).summary_frame(alpha=0.05))'''),
('유의한 변수만 다시 적합', 'pvalues', False, '유의 변수 선택 재적합 pvalues 0.05 변수 선별',
'''X0 = sm.add_constant(df[['x', 'x2', 'x3']])
m0 = sm.OLS(df['y'], X0).fit()
sig = m0.pvalues.drop('const')
cols = sig[sig < 0.05].index.tolist()

m1 = sm.OLS(df['y'], sm.add_constant(df[cols], has_constant='add')).fit()
print(cols, round(m1.rsquared, 4))'''),
('더미 변수 만들기', 'get_dummies', False, 'get_dummies drop_first dtype int 더미 기준범주',
'''X = pd.get_dummies(df[['x', 'region']], columns=['region'],
                   drop_first=True, dtype=int)   # bool 말고 int
X = sm.add_constant(X)
sm.OLS(df['y'], X).fit().params'''),
])

sec('t3logit', '작업형 3 · 로지스틱 회귀', '계수 → exp → 오즈비. 문제에 따로 말이 없으면 「규제 없이」 푼다.', T3_SETUP + T3_IMPORTS, [
('로지스틱 회귀 (statsmodels)', 'sm.Logit', False, 'Logit 로지스틱 회귀 disp add_constant statsmodels',
'''X = sm.add_constant(df[['x', 'x2']])
logit = sm.Logit(df['label'], X).fit(disp=False)  # 반복 로그 숨김
print(logit.params)
print(logit.pvalues)'''),
('오즈비', '빈출', True, '오즈비 odds ratio exp np.exp 계수 n단위',
'''odds = np.exp(logit.params)
print(round(odds['x'], 4))                        # x 1 증가 시 오즈비
print(round(np.exp(logit.params['x'] * 5), 4))    # x 5 증가 시
print(np.exp(logit.conf_int()).loc['x'])          # 오즈비 신뢰구간'''),
('예측 확률 · 오분류율', 'predict', False, 'predict 확률 0.5 오분류율 정확도 분류 prsquared aic',
'''prob = logit.predict(X)                 # label=1 일 확률
pred = (prob >= 0.5).astype(int)
err = (pred != df['label']).mean()       # 오분류율
print(round(err, 4), round(1 - err, 4))
print(round(logit.prsquared, 4))         # 의사 R²
print(round(logit.llf, 4), round(logit.aic, 4))   # 로그우도 · AIC'''),
('sklearn 으로 같은 값 내기', '함정', True, 'LogisticRegression penalty None 규제 sklearn 계수 같은 값',
'''from sklearn.linear_model import LogisticRegression

lr = LogisticRegression(penalty=None, max_iter=1000)   # 규제 없이
# (sklearn 1.2 미만이면 penalty='none' 문자열)
lr.fit(df[['x', 'x2']], df['label'])
print(lr.intercept_, lr.coef_)   # statsmodels Logit 과 같은 값
# 기본값(penalty='l2') 그대로면 계수가 달라진다'''),
])

sec('env', '시험장에서', '인터넷이 안 된다. 함수가 기억나지 않으면 dir 과 help 로 찾는다.', T3_SETUP + T3_IMPORTS + "\nimport sklearn\n", [
('함수 이름 · 인자 찾기', 'help', False, 'help dir 도움말 함수 찾기 인자 시험장',
'''import sklearn.metrics
print([m for m in dir(sklearn.metrics) if 'score' in m])
print([f for f in dir(stats) if f.startswith('ttest')])
help(stats.ttest_ind)          # 인자 · alternative 설명'''),
('출력이 잘릴 때', 'option', False, 'set_option max_columns max_rows 출력 잘림 float_format',
'''pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.4f}'.format)
print(df.head().to_string())'''),
('버전 확인', 'version', False, 'version 버전 sklearn pandas __version__',
'''import pandas, scipy, sklearn
print(pandas.__version__, sklearn.__version__, scipy.__version__)'''),
])

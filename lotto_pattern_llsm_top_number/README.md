## DIRECTORY
```
G:lotto_pattern_llsm_top_number
│  config.py # 상수와 필터링 설정
│  lotto.db # 로또 데이터 베이스
│  lotto_analyzer.py # 로또 분석 기법
│  lotto_generator.py # 예측 번호 생성(게임당 6개 번호)
│  lotto_generator_old.py
│  lotto_pattern_llsm.py
│  main.py # 머신러닝과 학습을 통한 번호 생성(번호 6 ~ 45개 생성)
│  number_test.py # 생성된 예측번호를 필터링 조건에 맞는지 검증
│  README.md
│
├─backups
├─logs # main.py 실행시 로그 파일 생성
│      lotto_prediction_20250222-1.log
│
├─models
├─modules # 머신러닝에 필요한 모듈들
│  │  database_manager.py
│  │  file_manager.py
│  │  gui.py
│  │  log_manager.py
│  │  lotto_analyzer.py
│  │  lotto_analyzer_old.py
│  │  model_state.py
│  └─ __init__.py
│
└─predictions
   └─ lotto_prediction_20250222_104145.txt
```
# 로또 패턴 분석 및 예측 시스템 v3.0

## 목차
1. [개요](#1-개요)
2. [시스템 구성](#2-시스템-구성)
3. [주요 기능](#3-주요-기능)
4. [설정 가이드](#4-설정-가이드)
5. [패턴 분석 방법](#5-패턴-분석-방법)
6. [예측 알고리즘](#6-예측-알고리즘)
7. [결과 분석](#7-결과-분석)
8. [기술 상세](#8-기술-상세)
9. [주의사항](#9-주의사항)
10. [부록](#10-부록)

## 1. 개요

### 1.1 시스템 소개
이 시스템은 과거 로또 당첨 번호의 패턴을 분석하여 미래의 번호를 예측하는 프로그램입니다. 
다양한 통계적 방법과 패턴 인식 알고리즘을 사용하여 번호를 선택합니다.

### 1.2 주요 특징
- 패턴 기반 번호 선택
- 사용자 정의 가중치 시스템
- 상세한 분석 및 시각화
- 데이터베이스 기반 이력 관리
- 결과 저장 및 분석 기능

### 1.3 시스템 요구사항
- Python 3.8 이상
- 필요 라이브러리:
  - tkinter
  - pandas
  - numpy
  - matplotlib
  - sqlite3
  - scikit-learn

## 2. 시스템 구성

### 2.1 핵심 컴포넌트
1. **분석 엔진**
   - LottoAnalyzer: 번호 패턴 분석
   - PredictionAnalyzer: 예측 결과 분석
   - LearningAnalyzer: 학습 과정 분석

2. **데이터 관리**
   - DatabaseManager: 데이터베이스 연동
   - FileManager: 파일 관리
   - LogManager: 로깅 시스템

3. **사용자 인터페이스**
   - LottoPredictionGUI: 메인 GUI
   - VisualizationManager: 시각화 관리
   - ResultVisualizer: 결과 표시

### 2.2 데이터 구조
```python
class ModelState:
    """모델 상태 관리 클래스"""
    numbers_memory: Dict[int, float]  # 번호별 가중치
    number_stats: Dict[int, int]      # 번호별 통계
    pattern_history: Dict[tuple, list] # 패턴 이력
```

## 3. 주요 기능

### 3.1 패턴 분석 시스템
#### 3.1.1 기본 패턴 분석
- **2개 번호 패턴**
 - 두 번호가 함께 출현하는 빈도 분석
 - 가중치: 35%
 - 분석 방법: 연속된 두 번호의 출현 빈도 및 최근성 계산

- **3개 번호 패턴**
 - 세 번호의 동시 출현 패턴 분석
 - 가중치: 25%
 - 특징: 더 복잡한 패턴 인식 가능

- **연속성 패턴**
 - 연속된 번호의 출현 분석
 - 가중치: 15%
 - 예: 1-2, 15-16과 같은 연속 번호

#### 3.1.2 고급 패턴 분석
```python
def analyze_patterns(self, historical_data: pd.DataFrame):
   """
   패턴 분석 수행
   - historical_data: 과거 당첨 번호 데이터
   - 반환: 패턴 분석 결과
   """
   for idx, row in historical_data.iterrows():
       numbers = sorted([row[f'num{i}'] for i in range(1, 7)])
       
       # 기본 통계 업데이트
       self._update_basic_stats(numbers)
       
       # 패턴 분석
       self._analyze_pair_patterns(numbers)
       self._analyze_triple_patterns(numbers)
       self._analyze_sequence_patterns(numbers)
```
### 3.2 가중치 시스템
#### 3.2.1 가중치 구성
```Python
pattern_weights = {
    'pair': 0.35,      # 2개 번호 패턴
    'triple': 0.25,    # 3개 번호 패턴
    'sequence': 0.15,  # 연속성
    'frequency': 0.15, # 출현 빈도
    'recency': 0.10    # 최근성
}
```
#### 3.2.2 가중치 조정
- 사용자 정의 가능
- 자동 정규화 기능
- 유효성 검사 시스템

### 3.3 시각화 시스템
#### 번호별 출현 빈도 그래프
- 막대 그래프 형태
- 평균선 표시
- 표준편차 영역 표시
#### 패턴 히트맵
- 번호 간 연관성 시각화
- 컬러 스케일로 강도 표현
#### 트렌드 분석 그래프
- 시계열 데이터 분석
- 이동평균선 표시

## 4. 설정 가이드

### 4.1 기본 설정
#### 4.1.1 번호 선택 설정
```python
# 설정 예시
settings = {
   "선택 번호 개수": 6,     # 기본값, 1-45 사이 설정 가능
   "학습 회차": 100,       # 전체/10/30/50/100/200 선택 가능
   "학습률": 0.1,         # 0-1 사이 값
   "학습 반복": 100       # 반복 학습 횟수
}
```
#### 4.1.2 권장 설정값
| 설정 항목 |권장값|설명|
|-------|---|---|
| 학습 회차 |100|최근 100회차 데이터 사용|
| 학습률   |0.1|안정적인 학습을 위한 값|
| 학습 반복 |100|충분한 학습을 위한 반복 횟수|

### 4.2 패턴 가중치 설정
#### 4.2.1 세부 가중치 조정
|패턴 유형|기본값|권장 범위|영향|
|-----|---|---|---|
|2개 번호|35%|30-40%|기본 패턴 인식|
|3개 번호|25%|20-30%|복합 패턴 인식|
|연속성|15%|10-20%|연속 번호 출현|
|출현 빈도|15%|10-20%|자주 나오는 번호|
|최근성|10%|5-15%|최근 추세 반영|

### 4.3 분석 설정
#### 4.3.1 패턴 인식 임계값
```Python
thresholds = {
    "패턴 강도 임계값": 0.8,    # 상위 20% 패턴만 선택
    "연속성 임계값": 2,        # 최대 연속 번호 개수
    "최소 출현 빈도": 5        # 최소 출현 횟수
}
```

## 5. 패턴 분석 방법

### 5.1 기본 패턴 분석
#### 5.1.1 출현 빈도 분석
```Python
def analyze_frequency(self, numbers: list) -> dict:
    """번호별 출현 빈도 분석"""
    frequency = {
        'total_count': len(numbers),
        'number_counts': {},
        'statistics': {
            'mean': np.mean(numbers),
            'std': np.std(numbers),
            'range': max(numbers) - min(numbers)
        }
    }
    return frequency
```

#### 5.1.2 연속성 분석
```Python
def analyze_sequence(self, numbers: list) -> list:
    """연속 번호 패턴 분석"""
    sequences = []
    for i in range(len(numbers)-1):
        if numbers[i+1] - numbers[i] == 1:
            sequences.append((numbers[i], numbers[i+1]))
    return sequences
```

### 5.2 고급 패턴 분석
#### 5.2.1 구간별 분석
- 번호를 구간별로 나누어 분석
    - 1-10, 11-20, 21-30, 31-40, 41-45
- 각 구간의 출현 비율 계산
- 구간 조합 패턴 분석

## 6. 예측 알고리즘

### 6.1 기본 예측 프로세스
```python
class LottoAnalyzer:
   def select_numbers_by_count(self, count: int) -> list:
       """
       패턴 기반 번호 선택 프로세스
       
       Args:
           count (int): 선택할 번호 개수
       
       Returns:
           list: 선택된 번호 리스트
       """
       selected = []
       while len(selected) < count:
           scores = self._calculate_number_scores(selected)
           next_num = self._select_next_number(scores)
           selected.append(next_num)
       return sorted(selected)
```
### 6.2 점수 계산 시스템
#### 6.2.1 번호별 점수 계산
- 기본 점수 구성요소
    1. 패턴 점수 (60%)
        - 2개 번호 패턴: 35%
        - 3개 번호 패턴: 25%
    2. 보조 점수 (40%)
        - 연속성: 15%
        - 출현 빈도: 15%
        - 최근성: 10%

#### 6.2.2 점수 계산 공식
```python
def _calculate_score(self, num: int, selected: list) -> float:
    """
    각 번호의 종합 점수 계산
    
    계산 방식:
    1. 패턴 점수 = (2개 패턴 점수 * 0.35 + 3개 패턴 점수 * 0.25)
    2. 연속성 점수 = 연속된 번호 여부 * 0.15
    3. 빈도 점수 = (출현 횟수 / 최대 출현 횟수) * 0.15
    4. 최근성 점수 = (마지막 출현 회차 / 전체 회차) * 0.10
    """
    score = 0
    pair_score = self._calculate_pair_pattern_score(num, selected)
    triple_score = self._calculate_triple_pattern_score(num, selected)
    sequence_score = self._calculate_sequence_score(num, selected)
    frequency_score = self._calculate_frequency_score(num)
    recency_score = self._calculate_recency_score(num)
    
    return (pair_score * 0.35 + 
            triple_score * 0.25 + 
            sequence_score * 0.15 + 
            frequency_score * 0.15 + 
            recency_score * 0.10)
```

### 6.3 번호 선택 전략
#### 6.3.1 선택 알고리즘
1. 초기 선택
   - 전체 번호 대상 점수 계산
   - 가장 높은 점수의 번호 선택
2. 후속 선택
   - 기존 선택 번호와의 패턴 고려
   - 패턴 점수 재계산
   - 상위 20% 후보군에서 랜덤 선택

#### 6.3.2 제한 조건
    - 연속 번호 최대 2개까지 허용.
    - 같은 구간 번호 최대 3개까지 허용.
    - 홀짝 비율 2:4 ~ 4:2 유지.

### 6.4 머신러닝 적용
```Python
class LottoMLPredictor:
    def train(self, X, y):
        """
        RandomForest 기반 학습
        
        특성:
        - 이전 5회차 당첨번호
        - 구간별 출현 빈도
        - 연속성 패턴
        - 당첨금 트렌드
        """
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.model.fit(X, y)
```

## 7. 결과 분석 및 시각화

### 7.1 예측 결과 분석
#### 7.1.1 기본 통계 분석
```python
def analyze_prediction(self, numbers: list) -> dict:
   """
   예측된 번호의 통계적 특성 분석
   
   분석 항목:
   1. 기본 통계 (평균, 표준편차, 범위)
   2. 번호 분포 (구간별 분포)
   3. 패턴 일치도
   4. 과거 데이터와의 유사도
   """
   return {
       'basic_stats': self._calculate_basic_stats(numbers),
       'distribution': self._analyze_distribution(numbers),
       'pattern_match': self._analyze_pattern_match(numbers),
       'similarity': self._calculate_similarity(numbers)
   }
```

#### 7.1.2 분석 지표
|지표|설명|적정 범위|
|-----|---|---|
|번호 합계|선택된 번호들의 합|90-180|
|표준편차|번호들의 분산 정도|10-20|
|구간 분포|각 구간별 번호 개수|최대 3개/구간|
|패턴 일치도|기존 패턴과의 일치율|30% 이상|

### 7.2 시각화 시스템
#### 7.2.1 기본 그래프
```python
def create_basic_visualizations(self):
    """기본 시각화 그래프 생성"""
    # 번호별 출현 빈도
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # 빈도 그래프
    frequencies = [self.number_stats.get(n, 0) for n in range(1, 46)]
    ax1.bar(range(1, 46), frequencies)
    ax1.set_title('번호별 출현 빈도')
    
    # 패턴 히트맵
    pattern_matrix = self._create_pattern_matrix()
    sns.heatmap(pattern_matrix, ax=ax2, cmap='YlOrRd')
    ax2.set_title('번호 간 연관성')
```

#### 7.2.2 고급 시각화
```python
def create_advanced_visualizations(self):
    """고급 분석 시각화"""
    fig = plt.figure(figsize=(15, 10))
    
    # 1. 트렌드 분석
    ax1 = fig.add_subplot(221)
    self._plot_trend_analysis(ax1)
    
    # 2. 패턴 네트워크
    ax2 = fig.add_subplot(222)
    self._plot_pattern_network(ax2)
    
    # 3. 예측 성능
    ax3 = fig.add_subplot(223)
    self._plot_prediction_performance(ax3)
    
    # 4. 구간별 분포
    ax4 = fig.add_subplot(224)
    self._plot_zone_distribution(ax4)
```

### 7.3 결과 저장 시스템
#### 7.3.1 파일 저장 형식
```python
def save_results(self, numbers: list, analysis: dict):
    """예측 결과 저장"""
    # CSV 파일로 저장
    prediction_df = pd.DataFrame([numbers], 
                               columns=[f'번호{i+1}' for i in range(6)])
    prediction_df.to_csv('예측결과.csv', index=False)
    
    # Excel 파일로 상세 정보 저장
    with pd.ExcelWriter('상세분석.xlsx') as writer:
        # 예측 번호
        prediction_df.to_excel(writer, sheet_name='예측번호')
        
        # 분석 결과
        analysis_df = pd.DataFrame(analysis)
        analysis_df.to_excel(writer, sheet_name='상세분석')
```
## 8. 기술 상세

### 8.1 시스템 아키텍처
#### 8.1.1 구성요소 상세
```python
class SystemArchitecture:
   def __init__(self):
       """
       시스템 구성요소:
       1. 데이터 계층 (Data Layer)
       2. 비즈니스 로직 계층 (Business Layer)
       3. 프레젠테이션 계층 (Presentation Layer)
       """
       self.data_layer = {
           'DatabaseManager': '데이터베이스 관리',
           'FileManager': '파일 시스템 관리',
           'LogManager': '로깅 시스템'
       }
       
       self.business_layer = {
           'LottoAnalyzer': '패턴 분석 엔진',
           'PredictionAnalyzer': '예측 분석 엔진',
           'LearningAnalyzer': '학습 분석 엔진'
       }
       
       self.presentation_layer = {
           'LottoPredictionGUI': 'GUI 인터페이스',
           'VisualizationManager': '시각화 관리',
           'ResultVisualizer': '결과 표시'
       }
```

### 8.2 데이터베이스 구조
#### 8.2.1 테이블 구조
```sql
CREATE TABLE lotto_results (
    draw_number INTEGER PRIMARY KEY,
    num1 INTEGER NOT NULL,
    num2 INTEGER NOT NULL,
    num3 INTEGER NOT NULL,
    num4 INTEGER NOT NULL,
    num5 INTEGER NOT NULL,
    num6 INTEGER NOT NULL,
    bonus INTEGER NOT NULL,
    money1 INTEGER,
    money2 INTEGER,
    money3 INTEGER,
    money4 INTEGER,
    money5 INTEGER
);
```

#### 8.2.2 데이터 관리
- 백업 시스템
  - 자동 백업 주기: 1일
  - 백업 데이터 보관: 30일
  - 복원 포인트 생성

### 8.3 성능 최적화
#### 8.3.1 메모리 관리
```python
def optimize_memory(self):
    """메모리 사용량 최적화"""
    # 대용량 데이터 처리를 위한 청크 단위 처리
    chunk_size = 1000
    
    # 메모리 모니터링
    memory_usage = psutil.Process().memory_info().rss / 1024 / 1024
    if memory_usage > 500:  # 500MB 초과
        self.clear_cache()
```

#### 8.3.2 실행 속도 개선
```python
def improve_performance(self):
    """성능 최적화"""
    # 멀티스레딩 적용
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for chunk in self.data_chunks:
            future = executor.submit(self.process_chunk, chunk)
            futures.append(future)
```

### 8.4 오류 처리
#### 8.4.1 예외 처리 시스템
```python
def error_handler(self, func):
    """오류 처리 데코레이터"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError:
            self.log_manager.log_error("데이터베이스 오류")
            self.handle_db_error()
        except ValueError:
            self.log_manager.log_error("값 오류")
            self.handle_value_error()
        except Exception as e:
            self.log_manager.log_error(f"예상치 못한 오류: {str(e)}")
            self.handle_unexpected_error()
    return wrapper
```

## 9. 주의사항
### 9.1 데이터 관련 주의사항
1. 데이터 정합성
   - 회차 번호 중복 확인
   - 번호 범위 검증 (1-45)
   - 중복 번호 검사
2. 백업 관리
   - 정기적인 백업 실행
   - 백업 데이터 검증
   - 복원 테스트 수행

### 9.2 성능 관련 주의사항
1. 메모리 사용
   - 대용량 데이터 처리 시 청크 단위 처리
   - 메모리 누수 모니터링
   - 캐시 데이터 정리
2. 실행 시간
   - 장시간 실행 시 진행상황 표시
   - 타임아웃 설정
   - 비동기 처리 활용

## 10. 부록

### 10.1 개발 가이드라인
#### 10.1.1 코드 스타일
```python
# 권장 코드 스타일
class LottoPredictor:
   """로또 번호 예측 클래스
   
   Attributes:
       pattern_weights (dict): 패턴별 가중치
       number_stats (dict): 번호별 통계
   """
   def __init__(self):
       self.pattern_weights = {
           'pair': 0.35,
           'triple': 0.25,
           'sequence': 0.15,
           'frequency': 0.15,
           'recency': 0.10
       }
```

#### 10.1.2 명명 규칙
|유형|규칙|예시|
|-----|---|---|
|클래스|PascalCase|LottoAnalyzer|
|메서드|snake_case|analyze_patterns|
|변수|snake_case|number_stats|
|상수|UPPERCASE|MAX_NUMBERS|

### 10.2 트러블슈팅 가이드

#### 10.2.1 일반적인 문제 해결
1. 데이터베이스 연결 오류
```python
# 문제 해결 코드
def handle_db_connection_error(self):
    try:
        self.reconnect_database()
    except Exception:
        self.use_backup_database()
```
2. 메모리 부족 문제
```python
# 메모리 최적화 코드
def optimize_memory_usage(self):
    gc.collect()  # 가비지 컬렉션 실행
    self.clear_unused_cache()
```

### 10.3 성능 최적화 팁
#### 10.3.1 데이터 처리 최적화
```python
def optimize_data_processing(self):
    """데이터 처리 최적화 방법"""
    # 1. 벡터화 연산 사용
    numbers = np.array(self.numbers)
    frequencies = np.bincount(numbers)
    
    # 2. 데이터 캐싱
    @lru_cache(maxsize=128)
    def calculate_pattern_score(self, pattern):
        return self._complex_calculation(pattern)
```

### 10.4 확장 기능 가이드
#### 10.4.1 새로운 패턴 추가
```python
def add_new_pattern(self):
    """새로운 패턴 분석 추가 방법"""
    class NewPattern(BasePattern):
        def analyze(self, numbers):
            # 패턴 분석 로직
            pattern_score = self._calculate_score(numbers)
            return pattern_score
```
### 10.5 참고 자료
#### 10.5.1 API 문서
```python
class APIReference:
    """API 참조 문서
    
    주요 메서드:
    - analyze_patterns(): 패턴 분석
    - predict_numbers(): 번호 예측
    - evaluate_results(): 결과 평가
    """
    pass
```

#### 10.5.2 성능 벤치마크
```python
def run_benchmark():
    """성능 측정 결과"""
    benchmarks = {
        '패턴 분석': '0.5초/1000회',
        '번호 예측': '0.3초/회',
        '데이터 로딩': '1.2초/10000회',
        '결과 저장': '0.2초/회'
    }
    return benchmarks
```

### 10.6 업데이트 이력
#### 10.6.1 버전별 변경사항
|버전|날짜|주요 변경사항|
|-----|---|---|
|3.0|2024.02|- 패턴 분석 개선<br>- GUI 업데이트<br>- 성능 최적화|
|2.5|2023.12|- ML 모델 추가<br>- 분석 기능 강화|
|2.0|2023.09|- 기본 기능 구현<br>- DB 연동|

----------------------
# 테스트 예측
## 테스트 실행 및 결과
### 1. 기본 설정값으로 테스트
- 선택 번호 개수: 15
- 학습 회차: 100
- 학습률: 0.1
- 학습 반복: 100
- 기본 가중치 설정 사용

### 2. 예상 출력 결과
#### 2.1 실행 로그 창
```
[2024-02-20 10:30:15] INFO: 데이터 로딩 중...
[2024-02-20 10:30:16] INFO: 100회차 데이터 로드 완료
[2024-02-20 10:30:16] INFO: 패턴 분석 시작
=== 자주 출현하는 2개 번호 조합 ===
조합 12-34: 8회 출현
조합 7-43: 7회 출현
조합 1-45: 6회 출현
...
=== 자주 출현하는 3개 번호 조합 ===
조합 7-12-34: 4회 출현
조합 1-23-45: 3회 출현
...
[2024-02-20 10:30:20] INFO: 번호 선택 중...
[2024-02-20 10:30:21] INFO: 예측 완료
```

#### 2.2 예측 결과 창
```
선택된 번호 (15개):
3, 7, 12, 15, 19, 23, 27, 28, 31, 34, 36, 39, 41, 43, 45
=== 번호별 통계 ===
번호 3:

출현: 12회
최근성: 0.85

번호 7:

출현: 15회
최근성: 0.92
...

=== 패턴 분석 ===
2개 번호 패턴:
7-12: 7회
12-34: 8회
...
3개 번호 패턴:
7-12-34: 4회
...
연속 번호 패턴:
27-28
```

#### 2.3 분석 탭 그래프
- 번호별 출현 빈도 막대 그래프
  - X축: 1-45 번호
  - Y축: 출현 횟수
  - 평균선과 표준편차 영역 표시
- 당첨금 트렌드 그래프
  - X축: 회차
  - Y축: 당첨금액
  - 이동평균선 표시

#### 2.4 저장 파일
1. CSV 파일 (예측번호.csv)
```csv
번호1,번호2,번호3,번호4,번호5,번호6,번호7,번호8,번호9,번호10,번호11,번호12,번호13,번호14,번호15
3,7,12,15,19,23,27,28,31,34,36,39,41,43,45
```
2. Excel 파일 (상세분석.xlsx)
   - 시트1: 예측번호
   - 시트2: 번호별 상세정보 (출현횟수, 최근성 등)
   - 시트3: 패턴 분석 결과
3. 통계 탭
```
전체 통계 요약:
- 분석 회차: 100회
- 평균 출현 횟수: 13.2회
- 최다 출현 번호: 34 (18회)
- 최소 출현 번호: 44 (8회)
```
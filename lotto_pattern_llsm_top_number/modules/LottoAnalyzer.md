# LottoAnalyzer 코드 분석 및 설명
## 1. 개요
LottoAnalyzer 클래스는 로또 번호를 분석하고 예측하기 위한 Python 클래스로, 과거 로또 데이터(lotto.db 또는 lotto.csv)를 기반으로 패턴을 분석하고, 머신러닝 모델(MLPRegressor)을 사용하여 번호를 예측합니다. 이 문서는 클래스의 기능, 분석 방법, 문제 해결 과정을 상세히 설명하며, 코드의 동작 방식을 초보자도 이해할 수 있도록 구성합니다.

## 2. 코드의 주요 기능
### 2.1 클래스 개요
- 클래스 이름: LottoAnalyzer
- 목적: 과거 로또 번호 데이터를 분석하여 패턴을 추출하고, 머신러닝을 활용해 새로운 로또 번호를 예측.
- 사용 데이터: lotto.db 또는 lotto.csv에 저장된 과거 로또 회차 데이터(각 회차의 6개 번호 포함).
- 사용 기술: Python, NumPy, Scikit-learn(MLPRegressor), SQLite 또는 CSV 데이터 처리.

### 2.2 주요 메서드
#### 2.2.1 __init__(self, learning_rate: float, log_manager, pattern_weights: dict = None, use_ml: bool = False)
- 기능: LottoAnalyzer 객체를 초기화합니다.
- 입력:
  - learning_rate: 머신러닝 모델 학습률(기본값 0.001).
  - log_manager: 로그를 관리하는 객체(디버그, 정보, 오류 로그 기록).
  - pattern_weights: 번호 패턴 가중치(기본값으로 pair, triple, sequence, frequency, recency 포함).
  - use_ml: 머신러닝 사용 여부(기본값 False).
- 출력: 초기화된 LottoAnalyzer 객체.
- 설명: 내부 상태(numbers_memory, number_stats, pattern_weights, ml_model 등)를 설정하고, 머신러닝 사용 여부를 지정합니다.

#### 2.2.2 analyze_patterns(self, historical_data)
- 기능: 과거 로또 데이터에서 번호 패턴을 분석합니다.
- 입력: historical_data - 과거 로또 회차 데이터(Pandas DataFrame, num1~num6 열 포함).
- 출력: 없음(내부 상태 number_stats, time_weights, number_patterns, triple_patterns 업데이트).
- 설명:
  - 각 번호의 출현 빈도(number_stats)와 최근성(time_weights) 계산.
  - 2개 번호 쌍(number_patterns)과 3개 번호 조합(triple_patterns)의 출현 빈도 분석.
  - 로그에 분석 결과 디버깅 정보 출력.
  - 
#### 2.2.3 train_ml_model(self, historical_data)
- 기능: 머신러닝 모델(MLPRegressor)을 과거 데이터로 학습시킵니다.
- 입력: historical_data - 과거 로또 회차 데이터.
- 출력: 없음(내부 ml_model과 scaler 업데이트).
- 설명:
  - 180개의 특성(stats, time_weights, pattern_scores, sequence_score)을 생성.
  - 각 번호(1~45)에 대한 타겟(선택된 번호는 1, 나머지는 0)으로 45개 출력 뉴런 학습.
  - StandardScaler로 데이터 정규화, MLPRegressor로 신경망 모델 학습(3층 구조, 최대 2000회 반복).

#### 2.2.4 select_numbers_by_ml(self, count: int) -> list
- 기능: 머신러닝을 사용해 count개의 로또 번호를 예측합니다.
- 입력: count - 예측할 번호 개수(기본 로또는 6개).
- 출력: 정렬된 번호 리스트(예: [1, 5, 12, 23, 34, 45]).
- 설명:
  - 특성 데이터를 생성하고, 학습된 모델로 45개 번호에 대한 점수 예측.
  - 상위 점수 인덱스를 기반으로 후보 번호를 선택하고, 무작위 또는 점수 기반으로 count개 번호 선택.
  - 오류 발생 시 select_numbers_by_count로 대체.
  - 
#### 2.2.5 select_numbers_by_count(self, count: int) -> list
- 기능: 패턴 기반으로 count개의 번호를 선택합니다(머신러닝 사용 안 함).
- 입력: count - 예측할 번호 개수.
- 출력: 정렬된 번호 리스트.
- 설명:
  - number_stats, time_weights, number_patterns, triple_patterns를 활용해 각 번호의 점수 계산.
  - 점수가 높은 번호를 우선적으로 선택, 무작위로 count개 번호 반환.

## 3. 분석 방법
### 3.1 데이터 분석
- 데이터 소스: lotto.db 또는 lotto.csv에서 과거 1159개 회차 데이터 로드.
- 분석 항목:
  - 출현 빈도(number_stats): 각 번호(1~45)의 출현 횟수.
  - 시간 가중치(time_weights): 최근 회차일수록 가중치 높임(0~1 범위).
  - 패턴 분석:
    - 2개 번호 쌍(number_patterns): 빈도 높은 조합 추출.
    - 3개 번호 조합(triple_patterns): 복잡한 패턴 분석.
    - 연속성 점수(sequence_score): 연속된 번호(1칸, 2칸, 3칸, 4칸 차이) 가중치 부여.

### 3.2 머신러닝 분석
- 특성 생성: 180개 특성(stats 45개 + time_weights 45개 + pattern_scores 45개 + sequence_score 45개).
- 모델: MLPRegressor(다층 퍼셉트론, 300-150-50 뉴런 구조, ReLU 활성화 함수 사용).
- 학습 데이터: 각 회차의 6개 번호를 타겟으로, 45개 출력 뉴런으로 번호별 점수 학습.
- 예측: 새로운 데이터로 45개 번호 점수 예측, 상위 점수 번호 선택.
- 
### 3.3 번호 선택
- 머신러닝 기반: 모델 점수를 기준으로 상위 번호 선택, 무작위 또는 점수 비례 확률로 count개 번호 추출.
- 패턴 기반: number_stats, time_weights, patterns 점수로 상위 번호 선택, 무작위로 count개 번호 추출.

## 4.문제 해결 과정
### 4.1 초기 문제
- 증상: "머신러닝 예측 실패: 후보 번호가 부족합니다. 현재 후보 수: 6" 오류 발생.
- 원인:
  - predictions_with_noise 값이 중복되거나 유사해 sorted_indices 길이가 6개로 제한.
  - random.sample(numbers, count)에서 numbers 길이가 count(6) 미만 또는 동일.
  - 모델 출력 범위가 작거나, 특성 데이터 다양성 부족.

### 4.2 문제 해결 단계
- 노이즈 크기 증가:
    -np.random.normal(0, 0.1)에서 0.5, 1.0으로 증가, predictions_with_noise 다양성 강화 시도.
- 특성 다양성 강화:
    - pattern_scores 상위 10개 → 30개 → 50개로 확장, sequence_score에 4칸 차이까지 추가.
- 스케일링 도입:
    - predictions 값 0~100으로 스케일링, 더 넓은 범위로 분포.
- 모델 출력 재설계:
    - 6개 번호 직접 예측 대신, 45개 출력 뉴런으로 각 번호 점수 예측.
- 후보 선택 개선:
    - np.unique 제거, np.argsort로 상위 인덱스 직접 선택, 모든 번호(1~45) 포함 보완.

### 4.3 최종 해결
- MLPRegressor가 45개 번호에 대한 점수를 출력하도록 수정.
- sorted_indices가 45개 고유 인덱스 생성, numbers가 45개 번호 포함.
- random.sample로 충분한 후보에서 번호 선택, 오류 제거.

## 5. 개선 방안
### 5.1 번호 선택 최적화
- 현재: 무작위 선택(random.sample).
- 개선: 모델 점수(predictions)에 비례한 확률로 번호 선택(예: 상위 점수 번호 우선).
- 예시 코드:
```Python
top_scores = [(i + 1, predictions[i]) for i in sorted_indices[:count * 2]]
scores = [score for _, score in top_scores]
total_score = sum(scores)
probabilities = [score / total_score for score in scores]
selected_indices = np.random.choice(len(top_scores), count, replace=False, p=probabilities)
selected_numbers = sorted([top_scores[i][0] for i in selected_indices])
```
### 5.2 모델 성능 개선
- 현재: MLPRegressor 기본 설정.
- 개선:
  - 하이퍼파라미터 튜닝(층 수, 뉴런 수, 학습률, 반복 횟수 조정).
  - RandomForestRegressor 또는 GradientBoostingRegressor 테스트.
  - 교차 검증으로 모델 성능 평가.

## 6. 코드 사용 예시
### 6.1 설치 및 준비
```Python
pip install numpy pandas scikit-learn
```
### 6.2 코드 실행
```python
from modules.lotto_analyzer import LottoAnalyzer
from modules.log_manager import LogManager

# 로그 매니저 생성
log_manager = LogManager(log_dir="logs", log_level="INFO")

# LottoAnalyzer 객체 생성 (머신러닝 사용)
analyzer = LottoAnalyzer(learning_rate=0.001, log_manager=log_manager, use_ml=True)

# 과거 데이터 로드 (Pandas DataFrame)
import pandas as pd
historical_data = pd.read_csv("lotto.csv")  # 또는 lotto.db에서 조회

# 패턴 분석
analyzer.analyze_patterns(historical_data)

# 머신러닝 모델 학습
analyzer.train_ml_model(historical_data)

# 6개 번호 예측
predicted_numbers = analyzer.select_numbers_by_ml(count=6)
print(f"예측된 로또 번호: {predicted_numbers}")
```

## 8. 결론
LottoAnalyzer는 과거 로또 데이터를 분석하고, 머신러닝으로 번호를 예측하는 강력한 도구입니다. 
초기 "후보 번호 부족" 문제를 해결하며, 현재는 안정적으로 동작합니다. 
추가 개선을 통해 번호 선택의 의미와 모델 성능을 높일 수 있으며, 데이터 다양성을 확장해 더 나은 예측 성능을 기대할 수 있습니다.
-------------------
# LottoAnalyzer 및 Modules 폴더 코드 상세 분석 및 설명
## 1. 개요
modules 폴더는 로또 번호 분석 및 예측 시스템(LottoAnalyzer)를 구현하는 Python 모듈들을 포함합니다. 
이 문서는 lotto_analyzer.py, log_manager.py, model_state.py 파일의 기능, 구조, 분석 방법, 문제 해결 과정, 그리고 개선 방안을 상세히 설명합니다. 
초보자도 이해하기 쉽고, 상세한 정보를 제공하여 코드의 동작 방식을 명확히 이해할 수 있도록 구성되었습니다.

## 2. 파일별 기능 및 구조
### 2.1 lotto_analyzer.py
#### 2.1.1 개요
- 파일 목적: 로또 번호를 분석하고, 패턴을 추출하며, 머신러닝(MLPRegressor)을 활용해 번호를 예측하는 핵심 클래스(LottoAnalyzer)를 정의.
- 사용 모듈: copy, random, numpy, sklearn.neural_network.MLPRegressor, sklearn.preprocessing.StandardScaler.

#### 2.1.2 클래스: LottoAnalyzer
##### 2.1.2.1 초기화 (__init__)
- 기능: LottoAnalyzer 객체를 생성하고 초기 상태 설정.
- 입력:
  - learning_rate: 머신러닝 모델 학습률(기본값 0.001).
  - log_manager: 로그 관리 객체(LogManager 인스턴스).
  - pattern_weights: 번호 패턴 가중치 딕셔너리(기본값 { 'pair': 0.35, 'triple': 0.25, 'sequence': 0.15, 'frequency': 0.15, 'recency': 0.10 }).
  - use_ml: 머신러닝 사용 여부(기본값 False).
- 상태 변수:
  - numbers_memory: 번호 기억(초기값 1~45까지 1.0).
  - number_stats: 각 번호 출현 빈도(초기값 0).
  - pattern_weights: 패턴 가중치.
  - use_ml: 머신러닝 사용 여부.
  - ml_model: 머신러닝 모델(MLPRegressor).
  - scaler: 데이터 스케일링(StandardScaler).
  - number_patterns: 2개 번호 쌍 출현 빈도.
  - triple_patterns: 3개 번호 조합 출현 빈도.
  - time_weights: 번호 최근성 가중치.
- 설명: 객체 생성 시 내부 상태를 초기화하고, 머신러닝 사용 여부를 설정합니다.

##### 2.1.2.2 analyze_patterns(self, historical_data)
- 기능: 과거 로또 데이터에서 번호 패턴을 분석.
- 입력: historical_data - Pandas DataFrame(num1~num6 열 포함).
- 출력: 없음(내부 상태 업데이트).
- 구현 로직:
  - 각 회차의 6개 번호를 정렬.
  - number_stats: 각 번호 출현 횟수 증가.
  - time_weights: 최근 회차일수록 가중치 높게(0~1 범위, 총 회차 수 기준 비례).
  - number_patterns: 2개 번호 쌍 출현 빈도 계산.
  - triple_patterns: 3개 번호 조합 출현 빈도 계산.
  - 로그에 디버깅 정보 출력.
- 설명: 통계적 패턴을 추출해 이후 예측에 활용.

##### 2.1.2.3 train_ml_model(self, historical_data)
- 기능: 머신러닝 모델을 과거 데이터로 학습.
- 입력: historical_data - 과거 로또 데이터.
- 출력: 없음(내부 ml_model, scaler 업데이트).
- 구현 로직:
180개 특성 생성(stats 45 + time_weights 45 + pattern_scores 45 + sequence_score 45).
- 타겟: 
  - 각 번호(1~45)에 대해 선택 여부(1 또는 0)로 45개 출력 뉴런 설정.
  - StandardScaler로 데이터 정규화.
  - MLPRegressor(3층, 300-150-50 뉴런, ReLU 활성화, 최대 2000회 반복, 학습률 0.001)로 학습.
  - 로그에 학습 완료 정보 출력.
- 설명: 번호별 점수를 예측할 수 있는 모델 학습.

##### 2.1.2.4 select_numbers_by_ml(self, count: int) -> list
- 기능: 머신러닝으로 count개 번호 예측.
- 입력: count - 예측 번호 개수(기본 로또 6개).
- 출력: 정렬된 번호 리스트.
- 구현 로직:
  - 특성 데이터 생성(위와 동일).
  - ml_model로 45개 번호 점수 예측.
  - 상위 점수 인덱스(np.argsort)로 count * 2개 후보 선택.
  - 점수에 비례한 확률로 count개 번호 무작위 선택.
  - 오류 시 select_numbers_by_count로 대체.
  - 로그에 예측 번호 출력.
- 설명: 모델 점수를 활용해 번호 예측, 안정적으로 동작.

##### 2.1.2.5 select_numbers_by_count(self, count: int) -> list
- 기능: 패턴 기반으로 count개 번호 선택(머신러닝 사용 안 함).
- 입력: count - 예측 번호 개수.
- 출력: 정렬된 번호 리스트.
- 구현 로직:
  - number_stats, time_weights, number_patterns, triple_patterns로 각 번호 점수 계산.
  - 점수가 높은 번호 우선, 무작위로 count개 선택.
  - 로그에 선택 번호 출력.
- 설명: 통계적 패턴 기반 예측.

##### 2.1.2.6 get_state 및 set_state
- 기능: 모델 상태 저장 및 복원.
- 입력/출력: ModelState 객체로 상태 저장/복원.
- 설명: 모델 상태를 유지하거나 복원해 재사용 가능.

###2.2 log_manager.py
####2.2.1 개요
- 파일 목적: 로깅 기능을 제공하는 LogManager 클래스를 정의.
- 사용 모듈: logging, os, datetime.

#### 2.2.2 클래스: LogManager
##### 2.2.2.1 초기화 (__init__)
- 기능: 로깅 객체 초기화.
- 입력:
  - log_dir: 로그 파일 저장 디렉토리(기본값 "logs").
  - log_level: 로그 레벨(예: "DEBUG", "INFO", "ERROR", 기본값 "INFO").
- 출력: LogManager 객체.
- 설명: 로그 파일 경로 설정, 로거 생성, 레벨 설정.

##### 2.2.2.2 log_debug, log_info, log_error
- 기능: 디버그, 정보, 오류 로그 기록.
- 입력: 메시지 문자열.
- 출력: 없음(로그 파일 및 콘솔에 기록).
- 설명:
  - log_debug: 디버깅 정보 기록.
  - log_info: 일반 정보 기록.
  - log_error: 오류 정보 기록.
- 파일명: lotto_prediction_YYYYMMDD-N.log 형식, 날짜 및 순차 번호 포함.
- 
### 2.3 model_state.py
#### 2.3.1 개요
- 파일 목적: LottoAnalyzer의 상태를 저장/복원하기 위한 ModelState 클래스를 정의.
- 사용 모듈: 없음(단순 데이터 클래스).

#### 2.3.2 클래스: ModelState
- 기능: LottoAnalyzer의 상태(numbers_memory, number_stats, ml_model)를 캡슐화.
- 속성:
  - numbers_memory: 번호 기억 딕셔너리.
  - number_stats: 번호 출현 빈도 딕셔너리.
  - ml_model: 머신러닝 모델(선택적).
- 설명: 상태 저장/복원을 위한 데이터 구조 제공, 직렬화/역직렬화 가능.

## 3. 분석 방법
### 3.1 데이터 분석
- 데이터 소스: lotto.db(SQLite) 또는 lotto.csv(CSV 파일), 각 회차의 6개 번호(num1~num6) 포함.
- 분석 항목:
  - 출현 빈도(number_stats): 1~45 번호별 출현 횟수.
  - 시간 가중치(time_weights): 최근 회차일수록 가중치 높게(0~1, 총 회차 수 기준).
  - 패턴 분석:
    - number_patterns: 2개 번호 쌍 출현 빈도(예: (10, 23) 13번 출현).
    - triple_patterns: 3개 번호 조합 출현 빈도.
    - 연속성 점수(sequence_score): 1~4칸 차이 번호 가중치(1.0, 0.7, 0.4, 0.2).

### 3.2 머신러닝 분석
- 특성 생성: 180개 특성(분석 항목 기반).
- 모델: MLPRegressor(다층 퍼셉트론, 300-150-50 뉴런, ReLU, 최대 2000회 반복, 학습률 0.001).
- 학습 데이터: 1159개 회차 데이터, 각 번호에 대한 타겟(45개 출력 뉴런, 1/0).
- 예측: 45개 번호 점수 예측, 상위 점수 번호 선택.

### 3.3 번호 선택
- 머신러닝 기반: 점수 상위 번호 무작위 또는 확률적 선택.
- 패턴 기반: 통계 점수 상위 번호 무작위 선택.

## 4. 문제 해결 과정
### 4.1 초기 문제
- 증상: "머신러닝 예측 실패: 후보 번호가 부족합니다. 현재 후보 수: 6".
- 원인:
  - predictions_with_noise 값 중복/유사성으로 sorted_indices 길이 6 제한.
  - random.sample에서 numbers 길이 부족.
  - 모델 출력 범위 작음, 특성 다양성 부족.

### 4.2 문제 해결 단계
- 노이즈 크기 증가:
  - np.random.normal(0, 0.1) → 0.5 → 1.0로 조정, 다양성 강화 시도.
- 특성 다양성 강화:
  - pattern_scores 상위 10 → 30 → 50개로 확장.
  - sequence_score에 4칸 차이까지 추가(가중치 0.2).
- 스케일링 도입:
  - predictions 0~100 스케일링, 범위 확장.
- 모델 출력 재설계:
  - 6개 번호 직접 예측 → 45개 출력 뉴런으로 번호 점수 예측.
- 후보 선택 개선:
  - np.unique 제거, np.argsort로 상위 30개 인덱스 선택.
  - 모든 번호(1~45) 포함 보완.

### 4.3 최종 해결
- MLPRegressor 45개 출력 뉴런으로 점수 예측.
- sorted_indices 45개 고유 인덱스 생성.
- numbers 45개 번호 포함, random.sample 정상 작동.

## 5. 개선 방안
### 5.1 번호 선택 최적화
- 현재: 무작위 선택(random.sample).
- 개선: 모델 점수 기반 확률적 선택.
- 예시 :
```Python
top_scores = [(i + 1, predictions[i]) for i in sorted_indices[:count * 2]]
scores = [score for _, score in top_scores]
total_score = sum(scores)
probabilities = [score / total_score for score in scores]
selected_indices = np.random.choice(len(top_scores), count, replace=False, p=probabilities)
selected_numbers = sorted([top_scores[i][0] for i in selected_indices])
```
### 5.2 모델 성능 개선
- 현재: MLPRegressor 기본 설정.
- 개선:
  - 하이퍼파라미터 튜닝(층 수, 뉴런 수, 학습률, 반복 횟수).
  - RandomForestRegressor 또는 GradientBoostingRegressor 테스트.
  - 교차 검증으로 성능 평가.
  - 
### 5.3 데이터 다양성 강화
- 현재: 1159개 회차 데이터.
- 개선:
  - 시간적/계절적 패턴, 외부 통계 데이터 추가.
  - 더 긴 기간 데이터 또는 다른 로또 데이터 통합.


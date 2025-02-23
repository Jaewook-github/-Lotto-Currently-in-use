# 로또 번호 분석 및 생성 시스템 상세 설명

이 문서는 Python으로 구현된 로또 번호 분석 및 생성 시스템(`config.py`, `lotto_analyzer.py`, `lotto_generator.py`)의 상세한 작동 방식을 설명합니다. 이 시스템은 과거 로또 당첨 데이터를 분석하고, 설정된 기준에 맞는 번호 조합을 생성하는 기능을 제공합니다.

---

## 1. `config.py`

### 역할
- 로또 번호 분석 및 생성에 필요한 상수와 필터링 기준을 정의하는 설정 파일입니다.
- `LottoConfig` 클래스를 통해 모든 설정을 중앙에서 관리하며, 다른 모듈에서 공통으로 참조됩니다.

### 주요 구성 요소

#### 1.1 `CORNER_NUMBERS`
- 로또 번호판의 네 모서리 위치에 해당하는 번호 집합을 정의합니다.
- **구성:**
  - `'좌측 상단': [1, 2, 8, 9]`
  - `'우측 상단': [6, 7, 13, 14]`
  - `'좌측 하단': [29, 30, 36, 37, 43, 44]`
  - `'우측 하단': [34, 35, 41, 42]`
- **용도:** 번호 조합에서 모서리 번호의 개수를 분석하거나 제한할 때 사용.

#### 1.2 `BALL_COLORS`
- 로또 번호(1~45)를 한국 로또 규칙에 따라 색상으로 분류합니다.
- **구성:**
  - `'노랑(🟡)': range(1, 11)` (1~10)
  - `'파랑(🔵)': range(11, 21)` (11~20)
  - `'빨강(🔴)': range(21, 31)` (21~30)
  - `'검정(⚫)': range(31, 41)` (31~40)
  - `'초록(🟢)': range(41, 46)` (41~45)
- **용도:** 번호 조합의 색상 분포를 분석하거나 색상 개수를 제한.

#### 1.3 수학적 특성 정의
- **`COMPOSITE_NUMBERS`**: 합성수 집합 (예: 1, 4, 8, 10 등)
- **`PERFECT_SQUARES`**: 완전제곱수 집합 (예: 1, 4, 9, 16 등)
- **`PRIME_NUMBERS`**: 소수 집합 (예: 2, 3, 5, 7 등)
- **용도:** 번호 조합의 수학적 특성을 분석하거나 필터링 기준으로 활용.

#### 1.4 `MIRROR_NUMBER_GROUPS`
- "동형수" (숫자 순서를 뒤집어도 의미 있는 쌍, 예: 12와 21)를 그룹으로 정의.
- **구성:**
  - `[{12, 21}, {13, 31}, {14, 41}, {23, 32}, {24, 42}, {34, 43}, {6, 9}]`
- **용도:** 번호 조합 내 동형수 그룹 개수를 계산.

#### 1.5 `MULTIPLES`
- 3, 4, 5의 배수를 리스트로 정의.
- **구성:**
  - `'3의 배수': [3, 6, 9, ..., 45]`
  - `'4의 배수': [4, 8, 12, ..., 44]`
  - `'5의 배수': [5, 10, 15, ..., 45]`
- **용도:** 번호 조합 내 배수의 개수를 제한하거나 분석.

#### 1.6 `FILTER_CRITERIA`
- 번호 조합 생성 시 적용되는 필터링 기준을 정의.
- **주요 항목:**
  - **`sum_range`**: 번호 합계 범위 (`min: 100`, `max: 175`)
  - **`ac_range`**: AC 값 범위 (`min: 7`, `max: 10`)
  - **`odd_even_exclude`**: 제외할 홀짝 비율 (예: `{0, 6}` = 모두 짝수)
  - **`high_low_exclude`**: 제외할 고저 비율 (1~22: 저, 23~45: 고)
  - **`same_last_digit`**: 동일 끝자리 개수 (`min: 2`, `max: 3`)
  - **`last_digit_sum`**: 끝자리 합계 (`min: 15`, `max: 35`)
  - **`consecutive_numbers`**:
    - `none: True` (연속 번호 없음 허용)
    - `pairs: [1, 2]` (1~2개의 연속 쌍 허용)
  - **`number_counts`**:
    - 소수, 합성수, 배수, 쌍수, 모서리 번호의 최소/최대 개수
  - **`number_range`**:
    - `start_number_max: 15` (첫 번호 최대값)
    - `end_number_min: 35` (끝 번호 최소값)
  - **`section_numbers`**: 구간별 번호 개수 (`min: 0`, `max: 3`)
  - **`colors`**: 사용 색상 개수 (`min: 3`, `max: 5`)

### 작동 방식
- `LottoConfig` 클래스는 인스턴스로 생성되어 다른 모듈에서 참조됩니다.
- 번호 분석 및 생성 로직이 일관되게 작동하도록 기준을 제공합니다.

---

## 2. `lotto_analyzer.py`

### 역할
- 과거 로또 당첨 번호 데이터를 SQLite 데이터베이스에서 읽어와 통계와 패턴을 분석합니다.
- 단일 번호 조합 분석과 전체 데이터 분석을 모두 지원합니다.

### 주요 클래스: `LottoAnalyzer`

#### 2.1 `__init__(self, db_path)`
- **입력:** SQLite 데이터베이스 경로 (`db_path`)
- **기능:** `LottoConfig` 인스턴스 생성, 내부 변수 초기화 (`results`, `freq_dfs`, `stats_df`)

#### 2.2 `get_frequent_numbers(self, count)`
- **입력:** 가져올 번호 개수 (`count`)
- **기능:** DB에서 번호별 출현 빈도를 계산하고 상위 `count`개의 번호를 반환.
- **SQL 쿼리:** `num1`~`num6`을 `UNION ALL`로 합친 후 빈도순 정렬.
- **출력:** `[번호1, 번호2, ...]`

#### 2.3 분석 메서드
- **`get_ball_color(number)`**: 번호의 색상 반환.
- **`analyze_color_pattern(numbers)`**: 번호 조합의 색상 분포를 `Counter`로 반환.
- **`count_multiples(numbers, multiple_list)`**: 특정 배수의 개수 계산.
- **`count_composite_numbers(numbers)`**: 합성수 개수 계산.
- **`count_perfect_squares(numbers)`**: 완전제곱수 개수 계산.
- **`count_prime_numbers(numbers)`**: 소수 개수 계산.
- **`calculate_last_digit_sum(numbers)`**: 끝자리 합계 계산 (예: [12, 23] → 2 + 3 = 5).
- **`is_palindrome(number)`**: 회문수 여부 확인 (예: 11 → True).
- **`count_palindrome_numbers(numbers)`**: 회문수 개수 계산.
- **`is_double_number(number)`**: 쌍수 여부 확인 (예: 22 → True).
- **`count_double_numbers(numbers)`**: 쌍수 개수 계산.
- **`get_mirror_number_count(numbers)`**: 동형수 그룹 개수 계산.
- **`find_consecutive_numbers(numbers)`**: 연속 번호 패턴 찾기 (예: [1, 2, 3] → [[1, 2, 3]]).
- **`calculate_ac(numbers)`**: AC 값 계산 (인접 차이값 개수 - 5).

#### 2.4 `analyze_numbers(self, draw_numbers=None)`
- **입력:** 단일 번호 리스트 (`draw_numbers`) 또는 None (전체 데이터 분석).
- **기능:**
  - 단일 번호 분석 시: `_analyze_single_draw` 호출 후 결과 반환.
  - 전체 데이터 분석 시: DB에서 데이터를 읽어 모든 회차를 분석.
- **출력:** 빈도 데이터프레임 (`freq_dfs`)과 통계 데이터프레임 (`stats_df`).

#### 2.5 `_analyze_single_draw(self, draw_numbers)`
- **입력:** 번호 리스트 (6개)
- **기능:** 단일 번호 조합을 분석하여 결과를 반환하거나 `self.results`에 추가.
- **분석 항목:** 모서리 번호, AC 값, 연속 번호, 색상, 합성수 등.

#### 2.6 `_create_frequency_dataframes(self)`
- **기능:** 각 분석 항목의 출현 빈도를 Pandas 데이터프레임으로 생성.
- **출력 형식:** `[값, 출현 횟수, 비율(%)]` (예: 모서리 번호 개수별 빈도).

#### 2.7 `_calculate_total_statistics(self)`
- **기능:** 평균, 최대, 최소 등 전체 통계를 계산하여 데이터프레임으로 저장.
- **항목:** 모서리 번호 평균, AC 값 최대/최소, 끝수합 평균 등.

#### 2.8 `print_analysis_results(self)`
- **기능:** 분석 결과를 테이블 형식으로 콘솔에 출력.
- **출력:** 빈도 테이블 + 전체 통계.

### 작동 방식
- SQLite DB의 `lotto_results` 테이블에서 데이터를 읽어 분석.
- Pandas와 NumPy를 활용해 통계 계산.
- 단일 분석과 전체 분석을 유연하게 지원.

### 사용 예시
```python
analyzer = LottoAnalyzer("../lotto.db")
analyzer.print_analysis_results()  # 전체 데이터 분석 출력
analyzer.analyze_single_numbers([1, 12, 23, 34, 41, 45])  # 단일 조합 분석
```

## 3. lotto_generator.py
### 역할:
과거 데이터에서 자주 나온 번호를 기반으로 새로운 로또 번호 조합을 생성.
LottoConfig의 필터링 기준을 적용하여 유효한 조합만 반환.

### 주요 클래스: LottoGenerator
#### 3.1 __init__(self, db_path)
- 입력: SQLite 데이터베이스 경로 (db_path)
- 기능: LottoAnalyzer 인스턴스 생성 및 초기화.

#### 3.2 set_frequent_numbers(self, count)
- 입력: 사용할 번호 개수 (6 <= count <= 45)
- 기능: DB에서 상위 count개의 번호를 가져와 저장.
- 출력: self.frequent_numbers에 저장.

#### 3.3 generate_single_combination(self)
- 기능: self.frequent_numbers에서 무작위로 6개 번호를 선택.
- 출력: 정렬된 번호 리스트 (예: [1, 5, 12, 23, 34, 45]).

#### 3.4 validate_combination(self, numbers)
- 입력: 번호 리스트 (6개)
- 기능: LottoConfig.FILTER_CRITERIA에 따라 조합의 유효성을 검증.
#### 검증 항목:
- 총합 (100~175)
- AC 값 (7~10)
- 홀짝/고저 비율 (0:6, 6:0 제외)
- 끝자리 개수 (23) 및 합계 (1535)
- 연속 번호 (없음 허용, 1~2쌍 허용)
- 소수, 합성수, 배수, 쌍수, 모서리 번호 개수
- 시작/끝 번호 범위
- 구간별 번호 개수 (0~3)
- 색상 개수 (3~5)
- 출력: True (유효) / False (무효)

#### 3.5 generate_numbers(self, num_games=1)
- 입력: 생성할 조합 수 (num_games)
- 기능: 유효한 조합을 num_games개 생성.
#### 작동:
- generate_single_combination으로 조합 생성.
- validate_combination으로 검증.
- 중복 제거 후 최대 시도 횟수(num_games * 1000) 내에서 결과 반환.
- 출력: 유효한 조합 리스트.
#### 작동 방식
- 자주 나온 번호를 풀(pool)로 사용해 무작위 조합 생성.
- 필터링 기준을 적용해 유효성 검사.
- 유효한 조합만 반환하며, 중복 방지.
#### 사용 예시
```Python
generator = LottoGenerator("../lotto.db")
generator.set_frequent_numbers(10)  # 상위 10개 번호 설정
combinations = generator.generate_numbers(5)  # 5개 조합 생성
for i, combo in enumerate(combinations, 1):
    print(f"[{i}] {combo}")
```
## 전체 시스템 작동 흐름
### 설정 (config.py)
LottoConfig에서 번호 특성과 필터링 기준 정의.
- 분석 (lotto_analyzer.py)
    - 과거 데이터 분석 → 패턴/통계 추출 → 빈도표/통계표 생성.
- 생성 (lotto_generator.py)
  - 자주 나온 번호 기반 조합 생성 → 필터링 → 유효 조합 반환.
- 활용 예시
  - 분석: 과거 당첨 번호 패턴 파악.
  - 생성: 통계 기반 번호 추천.
- 요구 사항
  - SQLite DB (lotto.db)에 lotto_results 테이블 필요.
  - 테이블 구조: draw_number, num1, num2, num3, num4, num5, num6.
  - 
이 시스템은 로또 번호의 통계적 특성을 분석하고, 규칙에 맞는 조합을 생성하는 강력한 도구입니다

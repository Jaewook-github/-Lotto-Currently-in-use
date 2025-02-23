# 로또 번호 테스트 모듈 상세 문서

## 1. 모듈 개요

`LottoTestAnalyzer` 클래스는 로또 번호 조합의 상세 분석과 검증을 수행하는 테스트 모듈입니다.

## 2. 주요 분석 항목

### 2.1 기본 정보 분석
- 번호 조합
- 총합 계산 및 검증
- AC 값 계산 및 검증

```python
analysis['기본 정보'] = {
    '번호': sorted_numbers,
    '합계': f"{sum(numbers)} (기준: {min}-{max})",
    'AC 값': f"{results['ac_value']} (기준: {min}-{max})"
}
```

### 2.2 패턴 분석
- 홀짝 비율 계산
- 고저 번호 비율 분석
- 연속된 번호 패턴 확인
- 모서리 번호 개수 확인

### 2.3 구간 분석
구간별 번호 분포를 5개 구간으로 나누어 분석:
- 1-10 구간
- 11-20 구간
- 21-30 구간
- 31-40 구간
- 41-45 구간

### 2.4 색상 분석
- 사용된 색상 수 계산
- 색상 조합 패턴 분석
- 색상 분포의 균형성 검증

### 2.5 수학적 특성 분석
- 소수 개수 확인
- 합성수 개수 확인
- 완전제곱수 개수 확인
- 동형수 그룹 개수 확인

### 2.6 배수 특성 분석
각 배수 유형별 개수 확인:
- 3의 배수
- 4의 배수
- 5의 배수

### 2.7 끝수 분석
- 끝수합 계산
- 끝수 구성 확인
- 회문수 개수 확인
- 쌍수 개수 확인

## 3. 검증 시스템

### 3.1 주요 검증 항목
```python
violations = []
```

1. 총합 범위 검증
```python
if not (min <= total_sum <= max):
    violations.append(f"총합 {total_sum}이 {min}-{max} 범위를 벗어남")
```

2. AC값 범위 검증
3. 색상 개수 검증
4. 소수 개수 검증
5. 끝수합 검증
6. 모서리 번호 개수 검증
7. 배수 개수 검증

### 3.2 위반 사항 보고 형식
```
[기준 위반 사항]
- 위반 내용 1
- 위반 내용 2
...
```

## 4. 테스트 실행 방법

### 4.1 단일 조합 테스트
```python
test_analyzer = LottoTestAnalyzer()
analysis = test_analyzer.analyze_number_combination([1, 2, 3, 4, 5, 6])
violations = test_analyzer.check_criteria_violations([1, 2, 3, 4, 5, 6])
```

### 4.2 다중 조합 테스트
```python
test_combinations = [
    [2, 4, 8, 31, 33, 42],
    [7, 15, 23, 26, 32, 45],
    # ... 추가 테스트 조합
]

for numbers in test_combinations:
    analysis = test_analyzer.analyze_number_combination(numbers)
    violations = test_analyzer.check_criteria_violations(numbers)
```

## 5. 출력 형식

### 5.1 분석 결과 출력
```
=== 조합 1 분석 ===

[기본 정보]
번호: [2, 4, 8, 31, 33, 42]
합계: 120 (기준: 100-175)
AC 값: 8 (기준: 7-10)

[패턴 분석]
홀짝 비율: 2:4
...
```

### 5.2 위반 사항 출력
```
[기준 위반 사항]
- 총합 180이 100-175 범위를 벗어남
- AC값 11이 7-10 범위를 벗어남
...
```

## 6. 활용 방법

### 6.1 테스트 모듈 초기화
```python
test_analyzer = LottoTestAnalyzer("lotto.db")
```

### 6.2 번호 조합 분석
```python
analysis = test_analyzer.analyze_number_combination(numbers)
for category, details in analysis.items():
    print(f"\n[{category}]")
    for key, value in details.items():
        print(f"{key}: {value}")
```

### 6.3 기준 위반 검사
```python
violations = test_analyzer.check_criteria_violations(numbers)
if violations:
    print("\n[기준 위반 사항]")
    for violation in violations:
        print(f"- {violation}")
```

## 7. 주의 사항

1. 데이터베이스 연결
   - 올바른 데이터베이스 경로 지정 필요
   - 데이터베이스 연결 실패 시 오류 처리

2. 번호 입력 형식
   - 6개의 숫자로 구성
   - 1-45 범위 내의 숫자만 허용
   - 중복 숫자 불가

3. 성능 고려사항
   - 대량의 조합 테스트 시 메모리 사용량 주의
   - 분석 결과 캐싱 활용 권장
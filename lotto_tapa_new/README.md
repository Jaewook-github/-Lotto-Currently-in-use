# 로또 타파 분석기

로또 당첨 확률을 높이기 위한 통계 기반 분석 프로그램입니다.

## 프로그램 개요

이 프로그램은 역대 로또 당첨 번호 통계를 기반으로 12가지 핵심 분석 규칙을 적용하여 로또 번호를 생성합니다. 각 규칙은 실제 당첨 번호의 출현 패턴을 분석하여 도출되었습니다.

## 분석 규칙 상세 설명

### 1. 총합 구간 분석
- **범위**: 100 ~ 175
- **설명**: 선택된 6개 번호의 총합이 이 구간에 들어가야 함
- **근거**: 역대 당첨번호 중 90% 이상이 이 구간에 포함
- **예시**: [8, 15, 21, 25, 35, 40] = 144 (유효)

### 2. AC값 분석
- **기준**: 7 이상
- **설명**: 6개 번호 간의 차이값들의 고유한 개수에서 5를 뺀 값
- **계산 방법**: 
  1. 모든 번호 쌍의 차이를 계산
  2. 중복을 제거한 차이값의 개수에서 5를 뺌
- **근거**: 당첨번호의 80% 이상이 AC값 7 이상
- **예시 계산**:
  ```
  번호: [1, 5, 10, 15, 22, 30]
  차이값: 4, 5, 5, 7, 8, 8, 12, 13, 15, 17, 21, 25, 29
  중복 제거 후: 4, 5, 7, 8, 12, 13, 15, 17, 21, 25, 29
  AC값 = 11개 - 5 = 6
  ```

### 3. 홀짝 비율 분석
- **제외 조건**: 6:0 또는 0:6 비율 제외
- **설명**: 홀수와 짝수의 분포 비율
- **근거**: 극단적 비율(모두 홀수 또는 모두 짝수)의 당첨 확률 2% 미만
- **권장**: 3:3, 4:2, 2:4 비율 추천

### 4. 고저 비율 분석
- **기준**: 23을 기준으로 고저 구분
- **제외 조건**: 6:0 또는 0:6 비율 제외
- **설명**: 
  - 저번호(1~22)와 고번호(23~45)의 비율
  - 극단적 비율 제외
- **근거**: 한쪽으로 치우친 번호의 당첨 확률 3% 미만

### 5. 소수 분석
- **대상 번호**: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43
- **권장 개수**: 0~3개
- **근거**: 4개 이상 포함 시 당첨 확률 1% 미만

### 6. 합성수 분석
- **대상 번호**: 1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44
- **권장 개수**: 0~3개
- **근거**: 4개 이상 포함 시 당첨 확률 10% 미만

### 7. 끝수 분석
- **범위**: 15~35
- **설명**: 각 번호의 일의 자리 숫자 합
- **계산 방법**: 
  - 한 자리 수는 그대로 사용
  - 두 자리 수는 끝자리만 사용
- **근거**: 당첨번호의 90% 이상이 이 구간에 포함

### 8. 배수 분석
- **3의 배수**: 0~3개 권장
- **5의 배수**: 0~2개 권장
- **근거**: 해당 범위의 출현 확률 90% 이상

### 9. 제곱수 분석
- **대상 번호**: 1, 4, 9, 16, 25, 36
- **권장 개수**: 0~1개
- **근거**: 2개 이상 포함된 당첨 확률 3% 미만

### 10. 연속수 분석
- **권장 패턴**: 
  - 연속번호 없음
  - 2연속 1쌍
  - 2연속 2쌍
- **예시**: 
  - 1,2 (2연속 1쌍)
  - 1,2,8,9 (2연속 2쌍)
- **근거**: 위 패턴의 출현 확률 90%

### 11. 쌍수 분석
- **대상 번호**: 11, 22, 33, 44
- **권장 개수**: 0~2개
- **근거**: 3개 이상 포함된 경우 2회 미만

### 12. 모서리 패턴 분석
- **대상 영역**:
  - 좌측 상단: 1, 2, 8, 9
  - 우측 상단: 6, 7, 13, 14
  - 좌측 하단: 29, 30, 36, 37
  - 우측 하단: 34, 35, 41, 42
- **권장 개수**: 1~4개
- **추가 규칙**:
  - 한 모서리당 최대 2개
  - 대각선 방향 차이 2 이하
- **근거**: 출현 빈도 90% 이상

## 프로그램 사용법

### 1. 메인 화면
- 게임 수 설정 (기본값: 5게임)
- 번호 생성 버튼
- 생성된 번호 표시 영역

### 2. 규칙 선택 탭
- 12가지 규칙 개별 선택/해제
- 전체 선택/해제 기능

### 3. 상세 설정 탭
- 각 규칙별 세부 설정 조정
- 설정값 저장/불러오기
- 기본값 복원 기능

### 4. 설정 저장
- 설정은 자동 저장
- 프로그램 재시작 시 복원
- 수동 저장/복원 가능

## 주의사항

1. 규칙이 너무 엄격하면 번호 생성이 어려울 수 있습니다.
2. 모든 규칙을 적용하면 생성 시간이 길어질 수 있습니다.
3. 규칙을 선택적으로 적용하여 사용하시기 바랍니다.

## 통계 기반 조합 추천

- 홀짝 비율: 3:3 또는 4:2
- 고저 비율: 3:3 또는 4:2
- 소수: 2~3개
- 연속수: 2연속 1쌍
- 모서리 숫자: 2개
- AC값: 7~8

이러한 조합이 역대 당첨번호에서 가장 높은 빈도로 나타났습니다.
# LogManager 모듈 상세 분석 및 설명
## 1. 개요
log_manager.py 파일은 로깅 기능을 제공하는 LogManager 클래스를 정의합니다. 이 모듈은 LottoAnalyzer 시스템의 디버깅, 정보, 오류 로그를 파일 및 콘솔에 기록합니다.

## 2. 파일 기능 및 구조
### 2.1 개요
- 파일 목적: 로깅 기능 제공, 시스템 동작 추적.
- 사용 모듈: logging, os, datetime.

### 2.2 클래스: LogManager
#### 2.2.1 초기화 (__init__)
- 기능: 로깅 객체 초기화.
- 입력:
  - log_dir: 로그 파일 저장 디렉토리(기본값 "logs").
  - log_level: 로그 레벨(예: "DEBUG", "INFO", "ERROR", 기본값 "INFO").
- 출력: LogManager 객체.
- 설명: 로그 파일 경로 설정, logging 로거 생성, 레벨 설정(DEBUG < INFO < ERROR).

#### 2.2.2 log_debug, log_info, log_error
- 기능: 디버깅, 정보, 오류 로그 기록.
- 입력: 메시지 문자열.
- 출력: 없음(로그 파일 및 콘솔에 기록).
- 설명:
  - log_debug: 디버깅 정보(세부 데이터, 변수 값).
  - log_info: 일반 정보(정상 동작, 성공 메시지).
  - log_error: 오류 정보(예외, 실패 원인).
- 파일명: lotto_prediction_YYYYMMDD-N.log 형식(예: lotto_prediction_20250221_233457.txt), 날짜 및 순차 번호 포함.

## 3. 분석 방법
### 3.1 로깅 분석
- 로그 데이터: 파일(logs 디렉토리) 및 콘솔 출력.
- 분석 항목:
  - 시간 스탬프: [2025-02-21 23:34:52].
  - 로그 레벨: DEBUG, INFO, ERROR.
  - 메시지: 시스템 동작 상태, 데이터, 오류 내용.

### 3.2 로그 관리
- 파일 관리: 디렉토리 생성, 파일명 중복 방지(순차 번호).
- 레벨 관리: log_level로 필터링, 필요 시 동적 변경.

## 4. 문제 해결 과정
### 4.1 초기 문제
- 증상: 로그 기록 실패, 파일 경로 오류.
- 원인:
  - log_dir 잘못 지정.
  - 디렉토리 권한 부족.
  - logging 설정 오류.

### 4.2 문제 해결 단계
-  경로 검증:
  - os.path.exists(log_dir)로 디렉토리 확인, 생성 로직 추가.
- 권한 처리:
  - os.access로 쓰기 권한 확인, 예외 처리.
- 설정 검증:
  - logging 설정(포맷, 핸들러) 점검, 기본값 재설정.

### 4.3 최종 해결
경로/권한 검증 추가, 로그 설정 안정화, 오류 로그 상세 기록.

## 5. 개선 방안
### 5.1 성능 최적화
- 현재: 기본 파일 I/O.
- 개선:
  - 비동기 로깅으로 성능 향상.
  - 로그 압축/분할(크기 기준).

### 5.2 기능 확장
- 현재: 기본 로그 레벨.
- 개선:
  - 사용자 정의 레벨 추가.
  - 로그 필터링(키워드, 시간 범위).

### 5.3 오류 처리 강화
- 현재: 기본 예외 처리.
- 개선:
  - 상세 오류 로그(stack trace 포함).
  - 로그 복구 메커니즘(잔여 로그 복원).

## 6. 코드 사용 예시
### 6.1 설치 및 준비
pip install logging

### 6.2 코드 실행
```python
from modules.log_manager import LogManager

# LogManager 객체 생성
log_manager = LogManager(log_dir="logs", log_level="INFO")

# 로그 기록
log_manager.log_info("애플리케이션 시작 성공")
log_manager.log_debug("데이터베이스 연결 시도...")
log_manager.log_error("예상치 못한 오류 발생: 데이터베이스 연결 실패")
```

## 7. 주의사항
- 파일 경로: log_dir가 쓰기 권한이 있어야 함.
- 성능: 대량 로그로 파일 I/O 부하 발생 가능.
- 레벨 설정: 적절한 log_level로 불필요한 로그 방지.

## 8. 결론
- log_manager.py는 LottoAnalyzer 시스템의 로깅 제공. 
- 초기 경로/설정 문제 해결하며 안정적 동작. 
- 성능 최적화, 기능 확장, 오류 처리 강화로 개선 가능.
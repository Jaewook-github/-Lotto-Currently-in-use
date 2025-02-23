# DatabaseManager 모듈 상세 분석 및 설명
## 1. 개요
database_manager.py 파일은 로또 데이터베이스(lotto.db)를 관리하는 DatabaseManager 클래스를 정의합니다. 
이 모듈은 SQLite 데이터베이스를 사용하여 과거 로또 데이터를 조회하고 관리하며, LottoAnalyzer 시스템에서 데이터 소스를 제공합니다.

## 2. 파일 기능 및 구조
### 2.1 개요
- 파일 목적: SQLite 데이터베이스(lotto.db)를 연결하고, 과거 로또 데이터를 조회/관리.
- 사용 모듈: sqlite3, os, pandas.

### 2.2 클래스: DatabaseManager
#### 2.2.1 초기화 (__init__)
- 기능: 데이터베이스 연결 객체 초기화.
- 입력:
  - db_path: 데이터베이스 파일 경로(예: "..\lotto.db").
- 출력: DatabaseManager 객체.
- 설명: SQLite 데이터베이스 연결을 준비하고, 커넥션 및 커서 생성을 위한 초기 설정을 수행합니다.

#### 2.2.2 connect(self)
- 기능: 데이터베이스 연결.
- 입력: 없음.
- 출력: SQLite 연결 객체.
  - 설명: sqlite3.connect로 lotto.db에 연결하고, 성공 시 로그(log_manager)에 "데이터베이스 연결 성공" 메시지 기록. 
        연결 실패 시 예외 처리.

#### 2.2.3 fetch_historical_data(self)
- 기능: 과거 로또 데이터 조회.
- 입력: 없음.
- 출력: Pandas DataFrame(각 회차의 num1~num6 및 draw_date 포함).
- 설명: SQL 쿼리(SELECT * FROM lotto_draws ORDER BY draw_date)로 데이터 조회, Pandas로 변환하여 반환. 
      데이터베이스 스키마는 로또 회차별 번호와 날짜 정보를 포함.

#### 2.2.4 close(self)
- 기능: 데이터베이스 연결 종료.
- 입력: 없음.
- 출력: 없음.
- 설명: 데이터베이스 커넥션 및 커서 닫기, 리소스 정리. 로그에 연결 종료 정보 기록.

## 3. 분석 방법
### 3.1 데이터 분석
- 데이터 소스: lotto.db SQLite 데이터베이스, lotto_draws 테이블(회차, num1~num6 포함).
- 분석 항목:
  - 과거 로또 회차 데이터 전체 조회.
  - 데이터 정렬(날짜 기준 오름차순).
  - Pandas DataFrame으로 변환, LottoAnalyzer로 전달.

### 3.2 데이터베이스 관리
- 연결 관리: SQLite 연결 유지/종료, 리소스 누수 방지.
- 쿼리 최적화: 효율적인 SQL 쿼리 사용, 인덱스 활용 가능성 고려.

## 4. 문제 해결 과정
### 4.1 초기 문제
- 증상: 데이터베이스 연결 실패 또는 데이터 조회 오류.
- 원인:
  - 파일 경로 오류(db_path 잘못 지정).
  - SQLite 버전 호환성 문제.
  - 테이블 스키마 불일치.

### 4.2 문제 해결 단계
- 파일 경로 검증:
  - os.path.exists(db_path)로 경로 확인, 잘못된 경로 예외 처리.
- SQLite 버전 확인:
  - sqlite3.version로 호환성 확인, 필요 시 업데이트.
- 스키마 검증:
  - PRAGMA table_info(lotto_draws)로 테이블 구조 확인, num1~num6, draw_date 필드 존재 확인.

### 4.3 최종 해결
경로 및 스키마 검증 로직 추가, 로그에 오류 상세 기록.
연결 실패 시 예외 처리 및 사용자 알림.

## 5. 개선 방안
### 5.1 성능 최적화
- 현재: 기본 SQL 쿼리 사용.
- 개선:
  - 인덱스 추가(CREATE INDEX idx_draw_date ON lotto_draws(draw_date)).
  - 쿼리 캐싱 도입(자주 사용 데이터 메모리 저장).

### 5.2 오류 처리 강화
- 현재: 기본 예외 처리.
- 개선:
  - 상세 오류 로그(stack trace 포함).
  - 데이터베이스 복구 메커니즘(백업/복원).

### 5.3 데이터 확장
- 현재: lotto_draws 테이블만 관리.
- 개선:
  - 추가 테이블(예: 패턴 통계, 예측 결과) 지원.
  - 다른 데이터베이스 엔진(MySQL, PostgreSQL) 호환성 추가.

## 6. 코드 사용 예시
### 6.1 설치 및 준비
pip install sqlite3 pandas

### 6.2 코드 실행
```python
from modules.database_manager import DatabaseManager
from modules.log_manager import LogManager

# 로그 매니저 생성
log_manager = LogManager(log_dir="logs", log_level="INFO")

# DatabaseManager 객체 생성
db_manager = DatabaseManager(db_path="G:\program\python\tensorflow\lotto\2025-02-19_Lotto_In_Use\lotto_pattern_llsm_top_number\lotto.db")

# 데이터베이스 연결
db_manager.connect()

# 과거 데이터 조회
historical_data = db_manager.fetch_historical_data()

# 데이터베이스 연결 종료
db_manager.close()

print(f"조회된 데이터 샘플:\n{historical_data.head()}")
```

## 7. 주의사항
- 데이터베이스 파일: lotto.db가 존재하고 읽기/쓰기 권한이 있어야 함.
- 성능: 대량 데이터로 쿼리 시 응답 시간 길어질 수 있음.
- 스키마 호환성: 테이블 구조 변경 시 코드 수정 필요.

## 8. 결론
database_manager.py는 lotto.db를 효율적으로 관리하며, LottoAnalyzer 시스템에 데이터 제공. 
초기 연결/조회 문제 해결하며 안정적 동작. 성능 최적화, 오류 처리 강화, 데이터 확장으로 개선 가능.
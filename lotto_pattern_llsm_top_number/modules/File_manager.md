# FileManager 모듈 상세 분석 및 설명
## 1. 개요
file_manager.py 파일은 파일 입출력 및 CSV 데이터를 처리하는 FileManager 클래스를 정의합니다. 
이 모듈은 로또 데이터(lotto.csv)를 읽고, 예측 결과를 파일로 저장하는 기능을 제공합니다.

## 2. 파일 기능 및 구조
### 2.1 개요
- 파일 목적: CSV 파일 읽기/쓰기 및 예측 결과 저장.
- 사용 모듈: os, pandas, csv.
- 
### 2.2 클래스: FileManager
#### 2.2.1 초기화 (__init__)
- 기능: 파일 관리 객체 초기화.
- 입력:
  - data_dir: 데이터 파일 저장 디렉토리(예: "data").
- 출력: FileManager 객체.
- 설명: 파일 경로 설정, 디렉토리 생성(존재하지 않을 시).

#### 2.2.2 read_csv(self, file_path)
- 기능: CSV 파일 읽기.
- 입력: file_path - CSV 파일 경로(예: "lotto.csv").
- 출력: Pandas DataFrame.
- 설명: pandas.read_csv로 CSV 로드, 열 이름(num1~num6, draw_date) 자동 추론, 오류 처리 포함.

#### 2.2.3 write_predictions(self, numbers, file_path)
- 기능: 예측 번호 저장.
- 입력:
  - numbers: 예측 번호 리스트(예: [1, 5, 12, 23, 34, 45]).
  - file_path: 저장 파일 경로(예: "predictions\lotto_prediction_20250221_233457.txt").
- 출력: 없음.
- 설명: 텍스트 파일로 번호 정렬 후 저장, 로그에 저장 성공 정보 기록.
- 
## 3. 분석 방법
### 3.1 데이터 분석
- 데이터 소스: lotto.csv 파일, num1~num6, draw_date 열 포함.
- 분석 항목:
  - CSV 데이터 구조 검증(열 이름, 데이터 타입).
  - 데이터 무결성 확인(결측값, 중복 회차).

### 3.2 파일 관리
- 파일 입출력: 경로 검증, 디렉토리 생성, 파일 권한 확인.
- 포맷 처리: CSV 표준 준수, 텍스트 저장 형식 통일.

## 4. 문제 해결 과정
### 4.1 초기 문제
- 증상: CSV 읽기/쓰기 실패, 파일 경로 오류.
- 원인:
  - file_path 잘못 지정.
  - 디렉토리 없음 또는 권한 부족.
  - CSV 포맷 불일치.

### 4.2 문제 해결 단계
- 경로 검증:
  - os.path.exists로 파일/디렉토리 존재 확인, 생성 로직 추가.
- 권한 처리:
  - os.access로 읽기/쓰기 권한 확인, 예외 처리.
- 포맷 검증:
  - Pandas로 CSV 로드 시 열 이름/데이터 타입 검증, 오류 로그 기록.

### 4.3 최종 해결
- 경로/권한 검증 로직 추가, 포맷 불일치 시 사용자 알림.
- 로그에 상세 오류 기록, 안정적 파일 입출력 보장.

## 5. 개선 방안
### 5.1 성능 최적화
- 현재: 기본 파일 I/O.
- 개선:
  - 병렬 처리로 대량 파일 읽기/쓰기 속도 향상.
  - 파일 캐싱 도입(자주 사용 데이터 메모리 저장).

### 5.2 포맷 확장
- 현재: CSV 및 텍스트 지원.
- 개선:
  - JSON, Excel 파일 지원 추가.
  - 데이터 압축/암호화 기능 도입.

### 5.3 오류 처리 강화
- 현재: 기본 예외 처리.
- 개선:
  - 상세 오류 로그(stack trace 포함).
  - 파일 복구 메커니즘(백업/복원).

## 6. 코드 사용 예시
### 6.1 설치 및 준비
pip install pandas

### 6.2 코드 실행
```Python
from modules.file_manager import FileManager
from modules.log_manager import LogManager

# 로그 매니저 생성
log_manager = LogManager(log_dir="logs", log_level="INFO")

# FileManager 객체 생성
file_manager = FileManager(data_dir="data")

# CSV 파일 읽기
historical_data = file_manager.read_csv("lotto.csv")
print(f"CSV 데이터 샘플:\n{historical_data.head()}")

# 예측 번호 저장
predicted_numbers = [1, 5, 12, 23, 34, 45]
file_manager.write_predictions(predicted_numbers, "predictions\lotto_prediction.txt")
```
## 7. 주의사항
- 파일 경로: data_dir와 file_path가 올바르게 지정되어야 함.
- 성능: 대량 데이터로 파일 I/O 시 시간이 걸릴 수 있음.
- 포맷 호환성: CSV 열 이름 및 데이터 타입 일관성 유지 필요.

## 8. 결론
file_manager.py는 CSV 및 예측 결과 파일을 효율적으로 관리하며, LottoAnalyzer 시스템에 데이터 제공. 
초기 파일 경로/포맷 문제 해결하며 안정적 동작. 성능 최적화, 포맷 확장, 오류 처리 강화로 개선 가능.
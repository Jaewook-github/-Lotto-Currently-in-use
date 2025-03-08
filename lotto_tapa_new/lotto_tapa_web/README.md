# 로또 타파 웹 서비스 사용 가이드

## 설치 및 실행 방법

### 1. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 웹 서버 실행
```bash
python app.py
```

### 3. 웹 브라우저로 접속
웹 브라우저를 열고 다음 주소로 접속합니다:
```
http://localhost:5000
```

## 주요 기능 설명

### 메인 탭
- 생성할 게임 수를 설정하고 번호 생성 버튼을 누르면 로또 번호가 생성됩니다.
- 생성된 번호는 색상별로 구분되어 표시됩니다(1-10: 노랑, 11-20: 파랑, 21-30: 빨강, 31-40: 회색, 41-45: 초록).
- 최근 당첨 통계와 번호 분포 분석 차트를 확인할 수 있습니다.

### 규칙 선택 탭
- 12가지 규칙을 개별적으로 활성화/비활성화할 수 있습니다.
- 전체 선택/해제 옵션도 제공합니다.
- 각 규칙에 대한 간략한 설명도 함께 제공됩니다.
- 설정 저장 버튼을 눌러 변경 사항을 저장합니다.

### 상세 설정 탭
- 각 규칙별로 상세 설정 값을 조정할 수 있습니다.
- 범위 설정(최소-최대 값), 개수 설정 등을 조정할 수 있습니다.
- 모서리 패턴의 시각적 표현을 통해 이해를 돕습니다.
- 기본값으로 복원 버튼을 통해 모든 설정을 초기화할 수 있습니다.

### 통계 분석 탭
- 번호별 출현 빈도, 홀짝 비율, 고저 비율 등 다양한 통계 데이터를 시각화하여 제공합니다.
- 최근 10회차 당첨번호를 확인할 수 있습니다.
- AC값 분포 및 당첨번호 총합 추이 등 심층 분석 정보를 제공합니다.

### 도움말 탭
- 각 규칙의 자세한 설명과 권장 설정 정보를 제공합니다.
- 시각화된 차트를 통해 규칙의 이해를 돕습니다.

## 다크 모드 지원
- 화면 우측 상단의 테마 전환 버튼을 통해 다크 모드로 전환할 수 있습니다.
- 다크 모드 설정은 로컬 스토리지에 저장되어 다음 방문 시에도 유지됩니다.

## 규칙 설명 요약

1. **총합 구간(100~175)**: 6개 번호의 합이 이 범위에 있어야 함
2. **AC값(7 이상)**: 번호 간 차이값의 다양성 측정
3. **홀짝 비율**: 홀수와 짝수의 분포 비율 (6:0 또는 0:6 제외)
4. **고저 비율**: 23을 기준으로 고번호와 저번호의 비율 (6:0 또는 0:6 제외)
5. **소수 개수**: 소수 번호(2,3,5,...,43)의 개수 제한
6. **합성수 개수**: 합성수 번호의 개수 제한
7. **끝수 총합**: 각 번호의 일의 자리 숫자 합의 범위 제한
8. **3의 배수, 5의 배수**: 각 배수의 개수 제한
9. **제곱수 개수**: 제곱수(1,4,9,16,25,36)의 개수 제한
10. **연속번호**: 연속된 번호 쌍의 개수 제한
11. **쌍수 개수**: 쌍수(11,22,33,44)의 개수 제한
12. **모서리 패턴**: 로또용지 모서리에 있는 번호들의 분포 제한

## 참고 사항
- 설정은 브라우저 세션에 저장되며, 브라우저를 닫으면 초기화됩니다.
- 회원 가입 없이 누구나 사용할 수 있습니다.
- 반응형 디자인이 적용되어 모바일 기기에서도 편리하게 사용할 수 있습니다.
- 조건이 너무 제한적이면 번호 생성이 실패할 수 있으니, 이 경우 일부 조건을 완화하세요.

-----------------

# Synology NAS DSM 7.2에 로또 타파 웹 서비스 배포 가이드

이 가이드는 Synology NAS DSM 7.2에서 웹스테이션을 사용하여 로또 타파 웹 서비스를 배포하는 방법을 단계별로 설명합니다.

## 필수 조건

1. Synology DSM 7.2가 설치된 NAS
2. Web Station 패키지 설치
3. Python3 패키지 설치 
4. SSH 접속 가능 (제어판 → 터미널 및 SNMP에서 활성화)

## 1. 패키지 설치 및 설정

### Web Station 설치
1. DSM 패키지 센터를 열고 "Web Station"을 검색하여 설치합니다.
2. "PHP" 패키지도 함께 설치합니다.

### Python 설치
1. 패키지 센터에서 "Python3"를 검색하여 설치합니다.

## 2. 프로젝트 파일 준비

1. 로또 타파 프로젝트 파일을 NAS의 웹 폴더에 업로드합니다.
   - 예: `/volume1/web/lotto-tapa`
   - File Station을 사용하거나 SCP/SFTP로 파일을 전송할 수 있습니다.

2. 폴더 구조를 다음과 같이 확인합니다:
   ```
   /volume1/web/lotto-tapa/
   ├── app.py
   ├── lotto_config.py
   ├── lotto_analyzer.py
   ├── db_util.py
   ├── wsgi.py
   ├── uwsgi.ini
   ├── static/
   │   ├── css/
   │   │   └── style.css
   │   └── js/
   │       ├── script.js
   │       └── charts.js
   ├── templates/
   │   ├── index.html
   │   ├── 404.html
   │   └── 500.html
   └── data/
       └── lotto.db
   ```

3. 필요한 파일이 모두 있는지 확인합니다:
   - `app.py`: Flask 애플리케이션
   - `db_util.py`: 데이터베이스 유틸리티
   - `wsgi.py`: WSGI 호환 스크립트
   - `uwsgi.ini`: uWSGI 설정 파일

## 3. 필요한 Python 패키지 설치

SSH로 NAS에 접속하여 다음 명령어로 필요한 패키지를 설치합니다:

```bash
# SSH로 NAS에 접속
ssh admin@your_nas_ip

# 애플리케이션 디렉토리로 이동
cd /volume1/web/lotto-tapa

# 필요한 패키지 설치
pip3 install --user flask flask-session uwsgi
```

## 4. 데이터베이스 디렉토리 생성

```bash
# data 디렉토리 생성
mkdir -p /volume1/web/lotto-tapa/data

# 권한 설정
chmod 755 /volume1/web/lotto-tapa/data
```

## 5. uWSGI 설정

1. `uwsgi.ini` 파일을 확인하고 필요한 경우 경로를 수정합니다:
   - `pythonpath`: 실제 Python 라이브러리 경로로 수정
   - `logto`: 로그 파일 경로 확인
   - `chmod-socket`: 소켓 권한 확인

2. 파일 권한 설정:
   ```bash
   chmod 644 /volume1/web/lotto-tapa/uwsgi.ini
   ```

## 6. 웹스테이션 가상 호스트 설정

1. DSM에서 웹스테이션을 실행합니다.
2. "가상 호스트" 탭을 선택하고 "생성" 버튼을 클릭합니다.
3. 다음과 같이 설정합니다:
   - **이름**: `lotto-tapa`
   - **프로토콜**: HTTP 또는 HTTPS(권장)
   - **포트**: 기본값(80 또는 443) 또는 원하는 포트
   - **문서 루트**: `/volume1/web/lotto-tapa`
   - **백엔드 서버**: Python

## 7. Nginx 설정 파일 수정

1. SSH로 NAS에 접속합니다:
   ```bash
   ssh admin@your_nas_ip
   ```

2. 가상 호스트에 대한 Nginx 설정 파일을 찾습니다:
   ```bash
   find /etc/nginx -name "*lotto-tapa*" -type f
   ```

3. 찾은 설정 파일을 수정합니다:
   ```bash
   sudo vi /etc/nginx/conf.d/server.lotto-tapa.conf
   ```

4. 파일의 내용을 다음과 같이 수정합니다:
   ```nginx
   server {
       listen 80;
       server_name lotto-tapa.local;  # 또는 실제 도메인/IP

       location / {
           include uwsgi_params;
           uwsgi_pass unix:/tmp/lotto-tapa.sock;
       }

       location /static {
           alias /volume1/web/lotto-tapa/static;
       }
   }
   ```

5. Nginx 설정을 다시 로드합니다:
   ```bash
   sudo nginx -s reload
   ```

## 8. 자동 시작 스크립트 설정

1. 자동 시작 스크립트를 생성합니다:
   ```bash
   sudo vi /usr/local/etc/rc.d/lotto-tapa.sh
   ```

2. 스크립트 권한 설정:
   ```bash
   sudo chmod +x /usr/local/etc/rc.d/lotto-tapa.sh
   ```

3. 서비스 시작:
   ```bash
   sudo /usr/local/etc/rc.d/lotto-tapa.sh start
   ```

## 9. 서비스 확인 및 문제 해결

1. 서비스 상태 확인:
   ```bash
   sudo /usr/local/etc/rc.d/lotto-tapa.sh status
   ```

2. 로그 확인:
   ```bash
   tail -f /volume1/web/lotto-tapa/uwsgi.log
   ```

3. 소켓 파일 확인:
   ```bash
   ls -la /tmp/lotto-tapa.sock
   ```

4. 웹 브라우저에서 접속 확인:
   - `http://NAS_IP_주소` 또는 설정한 도메인으로 접속

## 10. 일반적인 문제 해결

### 소켓 권한 문제
```bash
sudo chmod 666 /tmp/lotto-tapa.sock
```

### 디렉토리 권한 문제
```bash
sudo chown -R http:http /volume1/web/lotto-tapa
```

### uWSGI 수동 실행 (디버깅용)
```bash
cd /volume1/web/lotto-tapa
~/.local/bin/uwsgi --ini uwsgi.ini
```

### Nginx 오류 로그 확인
```bash
tail -f /var/log/nginx/error.log
```

### 프로세스 확인
```bash
ps aux | grep uwsgi
```

## 11. 백업 및 복원

### 설정 백업
중요한 설정 파일을 정기적으로 백업하는 것이 좋습니다:
```bash
cp /volume1/web/lotto-tapa/uwsgi.ini /volume1/backup/
cp /etc/nginx/conf.d/server.lotto-tapa.conf /volume1/backup/
cp /usr/local/etc/rc.d/lotto-tapa.sh /volume1/backup/
```

### 데이터베이스 백업
```bash
cp /volume1/web/lotto-tapa/data/lotto.db /volume1/backup/
```

## 12. 정기 업데이트

최신 로또 정보를 업데이트하기 위한 Cron 작업 설정:
1. DSM 제어판에서 '작업 스케줄러'를 열고 새 예약 작업을 생성합니다.
2. "사용자 정의 스크립트"를 선택하고 다음과 같이 설정합니다:
   - **사용자**: root 또는 적절한 권한을 가진 사용자
   - **실행 명령**: `python3 /volume1/web/lotto-tapa/update_lotto_db.py`
   - **실행 빈도**: 매주 일요일 (로또 추첨 후)

이제 로또 타파 웹 서비스가 Synology NAS DSM 7.2에서 성공적으로 실행되고 있습니다!

-------------------------

이제 더 모듈식 구조로 HTML 파일을 나누는 방법을 보여드렸습니다. 이 방식을 사용하면 다음과 같은 이점이 있습니다:

관리 용이성: 각 섹션을 개별 파일로 분리하여 코드 관리가 쉬워집니다.
재사용성: 공통 요소(베이스 레이아웃 등)를 여러 페이지에서 재사용할 수 있습니다.
가독성: 각 파일이 더 짧고 집중된 목적을 가져 가독성이 향상됩니다.

구조 설명

base.html: 공통 레이아웃과 구조를 정의합니다.

{% block content %}{% endblock %} 부분에 개별 페이지 내용이 삽입됩니다.


tabs/*.html: 각 탭의 내용만 포함하는 부분 템플릿입니다.

main.html: 메인 탭 내용
rules.html: 규칙 선택 탭 내용
(이외 settings.html, stats.html, help.html 파일도 필요)


index.html: 모든 탭을 포함하는 메인 페이지입니다.

{% extends "base.html" %}: 기본 레이아웃을 상속합니다.
{% include "tabs/xxx.html" %}: 각 탭 내용을 포함합니다.



구현 방법
```
/templates 폴더 구조 생성:
Copytemplates/
├── base.html
├── index.html
└── tabs/
    ├── main.html
    ├── rules.html
    ├── settings.html
    ├── stats.html
    └── help.html
```

각 파일에 적절한 내용을 배치합니다.
Flask 앱에서 사용:
```
@app.route('/')
def index():
    return render_template('index.html')
```

이 방식을 사용하면 HTML 코드가 모듈식으로 나뉘어 관리가 용이해지고, 각 부분을 독립적으로 수정할 수 있게 됩니다. 
또한 공통 요소의 변경 시 한 곳만 수정하면 되므로 유지보수가 쉬워집니다.

--------------------

주요 개선 사항

개선된 사이드바:

버전 정보 표시 추가
모바일에서 토글 기능 추가
최신 데이터 회차 표시 기능 추가


향상된 UI 요소:

푸터 영역 추가
로딩 스피너 컴포넌트 추가
알림 컨테이너 추가


추가된 기능:

서비스 워커를 통한 오프라인 지원
테마 토글 버튼 개선
탭 간 부드러운 전환 효과


기술 개선:

템플릿 블록 확장 ({% block title %}, {% block subtitle %}, {% block content %}, {% block extra_css %}, {% block extra_js %})
모바일 반응형 개선
데이터 기준 회차 표시



새로 추가된 파일

서비스 워커 (service-worker.js):

오프라인 기능 지원
정적 자원 캐싱
푸시 알림 기능


오프라인 페이지 (offline.html):

인터넷 연결이 끊겼을 때 표시되는 페이지
사용자 친화적인 오류 메시지


추가 CSS (extra-style.css):

새로운 UI 요소에 대한 스타일
애니메이션 효과
반응형 디자인 개선



base.html 사용 방법
변경된 base.html은 기존 탭 구조를 유지하면서 더 모듈화되고 확장 가능한 형태로 제공됩니다. 
사용 방법은 다음과 같습니다:

기본 템플릿 확장:
```
{% extends "base.html" %}

{% block title %}맞춤 제목{% endblock %}

{% block content %}
<!-- 페이지 내용 -->
{% endblock %}
```

추가 스타일 또는 스크립트 포함:
```
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/additional.css') }}">
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/additional.js') }}"></script>
{% endblock %}
```

부제목 변경:
```
{% block subtitle %}맞춤 부제목{% endblock %}
```

이 구조를 사용하면 각 페이지나 탭별로 필요한 요소만 커스터마이즈하면서 전체적인 일관성을 유지할 수 있습니다. 
또한 서비스 워커 지원으로 오프라인에서도 기본적인 기능이 동작하며, 모바일 환경에서도 최적화된 경험을 제공합니다.

----------

# 로또 타파 웹 서비스 개선 가이드

이 문서는 스크린샷에서 보이는 문제점들을 해결하고 로또 타파 웹 서비스를 더 효과적으로 구현하기 위한 가이드입니다.

## 발견된 문제점 및 해결책

### 1. 메인 페이지 빈 화면 문제
- **문제**: 메인 페이지에 "로또 타파 분석기"라는 제목만 나오고 내용이 없음
- **원인**: 템플릿 로드 문제 또는 JavaScript 실행 오류
- **해결책**: 
  - 템플릿 구조 개선 및 기본 콘텐츠 추가
  - 메인 페이지에 샘플 데이터로 초기 표시
  - JavaScript 오류 방지를 위한 방어 코드 추가

### 2. 통계 페이지 로딩 문제
- **문제**: 통계 페이지에서 "로딩 중..." 메시지만 표시되고 차트가 나타나지 않음
- **원인**: 서버 API 호출 실패 또는 차트 렌더링 문제
- **해결책**: 
  - 로딩 상태를 명확하게 표시
  - API 호출 실패 시 샘플 데이터 사용
  - 타임아웃 처리를 통한 무한 로딩 방지

## 구현 단계

### 1. 파일 구조 확인 및 업데이트

```
lotto_tapa_web/
├── app.py                    # 수정된 Flask 애플리케이션
├── lotto_config.py           # 로또 설정 클래스
├── lotto_analyzer.py         # 로또 분석기 클래스
├── db_util.py                # 데이터베이스 유틸리티 클래스
├── static/
│   ├── css/
│   │   └── style.css         # 완전히 새로 작성된 스타일시트
│   ├── js/
│   │   ├── script.js         # 기본 JavaScript 기능
│   │   ├── charts.js         # 차트 생성 스크립트 (수정됨)
│   │   ├── tabs.js           # 탭 전환 스크립트
│   │   └── service-worker.js # 오프라인 지원용 서비스 워커
│   └── images/               # 아이콘 및 이미지
├── templates/
│   ├── base.html             # 기본 레이아웃
│   ├── index.html            # 메인 인덱스 페이지
│   ├── tabs/                 # 모듈식 탭 템플릿
│   │   ├── main.html         # 메인 탭 (수정됨)
│   │   ├── rules.html        # 규칙 선택 탭
│   │   ├── settings.html     # 상세 설정 탭
│   │   ├── stats.html        # 통계 분석 탭 (수정됨)
│   │   └── help.html         # 도움말 탭
│   ├── 404.html              # 404 오류 페이지
│   ├── 500.html              # 500 오류 페이지
│   └── offline.html          # 오프라인 페이지
└── data/
    └── lotto.db              # 로또 데이터베이스
```

### 2. 주요 수정 파일

#### A. 수정된 app.py
- Flask 애플리케이션에 오류 처리 강화
- 로그 출력 추가
- 오프라인 라우트 추가

#### B. 새로운 style.css
- 색상 및 레이아웃 변수 정의
- 모바일 반응형 개선
- 사이드바 스타일 개선
- 차트 및 그래프 스타일 추가

#### C. 수정된 HTML 템플릿
- 메인 탭: 샘플 콘텐츠 추가
- 통계 탭: 로딩 상태 및 오류 처리 개선
- 템플릿 구조 모듈화

#### D. 수정된 charts.js
- 샘플 데이터 로드 함수 추가
- 오류 처리 개선
- 차트 로딩 전략 최적화

### 3. 변경 구현 방법

#### 스타일 및 레이아웃 수정
1. `style.css` 파일을 완전히 교체하여 최신 디자인 적용
2. 사이드바와 콘텐츠 영역 레이아웃 개선
3. 반응형 디자인 강화

#### 메인 페이지 콘텐츠 추가
1. 환영 메시지 및 설명 추가
2. 번호 생성 폼 레이아웃 개선
3. 샘플 결과 섹션 추가
4. 최근 당첨번호 정보 표시

#### 통계 탭 개선
1. 로딩 상태 명확하게 표시
2. 샘플 데이터로 초기 차트 렌더링
3. API 호출 실패 시 대체 데이터 사용
4. 차트 컨테이너 높이 고정으로 레이아웃 안정화

#### 자바스크립트 오류 처리 개선
1. 요소 존재 여부 확인 후 코드 실행
2. try-catch 블록으로 오류 처리
3. 타임아웃 설정으로 무한 로딩 방지
4. 콘솔 로그 추가로 디버깅 용이성 확보

### 4. 설치 및 실행 지침

#### 1. 필요 패키지 설치
```bash
pip install -r requirements.txt
```

#### 2. 데이터베이스 초기화 (필요시)
```bash
python update_lotto_db.py
```

#### 3. 애플리케이션 실행
```bash
python app.py
```

#### 4. 브라우저에서 접속
```
http://localhost:5000
```

### 5. 테스트 및 트러블슈팅

#### 메인 페이지 점검
- 번호 생성 폼 작동 확인
- 샘플 차트 렌더링 확인
- 모바일 화면에서 반응형 레이아웃 확인

#### 통계 탭 점검
- 로딩 상태 및 진행 표시 확인
- 샘플 차트 렌더링 확인
- API 오류 시 대체 데이터 표시 확인

#### 공통 문제 해결
- 콘솔에 JavaScript 오류가 없는지 확인
- 네트워크 탭에서 API 응답 확인
- 터미널에서 서버 로그 확인

## 결론

이 가이드에 따라 수정을 진행하면 스크린샷에서 발견된 문제들을 해결하고, 더 안정적이고 사용자 친화적인 로또 타파 웹 서비스를 구현할 수 있습니다. 
메인 페이지와 통계 탭에 기본 콘텐츠와 샘플 데이터를 추가함으로써 사용자가 어떤 상황에서도 서비스를 이용할 수 있도록 개선했습니다.
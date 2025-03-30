## 디렉토리 구조
```
lotto_stats/
├── app.py                     # 메인 애플리케이션 (Flask 실행)
├── config.py                  # 설정 파일
├── utils/
│   ├── __init__.py
│   ├── db_connector.py        # 데이터베이스 연결 유틸리티
│   ├── cache_manager.py       # 캐시 관리 유틸리티
│   └── data_utils.py          # 데이터 처리 유틸리티
├── models/
│   ├── __init__.py
│   └── lotto_stats.py         # 통계 데이터 모델 클래스
├── services/
│   ├── __init__.py
│   ├── stats_service.py       # 통계 계산 서비스
│   ├── analytics_service.py   # 데이터 분석 서비스
│   └── cache_service.py       # 캐시 서비스
├── controllers/
│   ├── __init__.py
│   ├── main_controller.py     # 메인 페이지 컨트롤러
│   ├── api_controller.py      # API 엔드포인트 컨트롤러
│   └── stats_controller.py    # 통계 페이지 컨트롤러
├── static/
│   ├── css/
│   │   ├── style.css          # 기본 스타일
│   │   ├── theme.css          # 테마 관련 스타일
│   │   ├── charts.css         # 차트 관련 스타일
│   │   └── responsive.css     # 반응형 스타일
│   ├── js/
│   │   ├── main.js            # 메인 스크립트
│   │   ├── theme-toggle.js    # 테마 전환 스크립트
│   │   ├── api-client.js      # API 요청 스크립트
│   │   ├── charts/
│   │   │   ├── frequency-chart.js     # 번호 빈도 차트
│   │   │   ├── odd-even-chart.js      # 홀짝 비율 차트
│   │   │   ├── high-low-chart.js      # 고저 비율 차트
│   │   │   ├── ac-chart.js            # AC값 차트
│   │   │   ├── sum-chart.js           # 총합 차트
│   │   │   └── pattern-charts.js      # 패턴 분석 차트
│   │   └── ui/
│   │       ├── tab-manager.js         # 탭 관리 스크립트
│   │       ├── loader.js              # 로딩 관리 스크립트
│   │       └── notifications.js       # 알림 관리 스크립트
│   └── images/
│       └── favicon.ico
├── templates/
│   ├── base.html              # 기본 템플릿
│   ├── index.html             # 메인 페이지
│   ├── partials/
│   │   ├── header.html        # 헤더 부분
│   │   ├── footer.html        # 푸터 부분
│   │   ├── stats-summary.html # 통계 요약 부분
│   │   └── rule-cards.html    # 규칙 카드 부분
│   ├── tabs/
│   │   ├── all-stats.html     # 전체 회차 탭
│   │   ├── recent-100.html    # 최근 100회차 탭
│   │   └── recent-10.html     # 최근 10회차 탭
│   └── pages/
│       ├── detailed.html      # 상세 통계 페이지
│       ├── patterns.html      # 패턴 분석 페이지
│       ├── analyze.html       # 분석 도구 페이지
│       └── error.html         # 오류 페이지
└── data/
    ├── lotto.db               # SQLite 데이터베이스
    └── cache/
        └── stats_cache.json   # 통계 데이터 캐시
```
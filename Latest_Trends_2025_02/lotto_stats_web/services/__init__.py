# services/__init__.py - 서비스 패키지 초기화 파일

# 서비스 클래스들 임포트
from services.stats_service import StatsService
from services.cache_service import CacheService
from services.analytics_service import AnalyticsService

# 버전 정보
__version__ = '1.0.0'

# 패키지 문서
__doc__ = """
로또 통계 분석 사이트 서비스 패키지

이 패키지는 다음과 같은 서비스 클래스를 제공합니다:
- StatsService: 기본 통계 데이터 제공
- CacheService: 통계 데이터 캐싱 관리
- AnalyticsService: 고급 데이터 분석 기능
"""

# 유틸리티 함수
def get_version():
    """
    서비스 패키지 버전 반환
    """
    return __version__
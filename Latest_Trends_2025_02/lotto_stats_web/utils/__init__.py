# utils/__init__.py - 유틸리티 패키지 초기화 파일

# 유틸리티 클래스들 임포트
from utils.db_connector import DatabaseConnector
from utils.cache_manager import CacheManager
from utils.data_utils import DataUtils

# 버전 정보
__version__ = '1.0.0'

# 패키지 문서
__doc__ = """
로또 통계 분석 사이트 유틸리티 패키지

이 패키지는 다음과 같은 유틸리티 클래스를 제공합니다:
- DatabaseConnector: 데이터베이스 연결 및 쿼리 실행
- CacheManager: 데이터 캐싱 및 관리
- DataUtils: 데이터 처리 및 변환
"""

# 유틸리티 함수
def get_version():
    """
    유틸리티 패키지 버전 반환
    """
    return __version__
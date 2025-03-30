# config.py - 설정 파일
import os
import secrets


class Config:
    # 기본 설정
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    DEBUG = os.environ.get('FLASK_DEBUG', 'True') == 'True'
    HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
    PORT = int(os.environ.get('FLASK_PORT', 5001))

    # 경로 설정
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    CACHE_DIR = os.path.join(DATA_DIR, 'cache')

    # 데이터베이스 설정
    DB_PATH = os.environ.get('DB_PATH') or os.path.join(DATA_DIR, 'lotto.db')

    # 캐시 설정
    CACHE_LIFETIME = 86400  # 캐시 유효 시간 (초) - 기본 24시간
    STATS_CACHE_FILE = os.path.join(CACHE_DIR, 'stats_cache.json')

    # 분석 설정
    HIGH_LOW_CUTOFF = 23  # 고저 비율 계산 기준
    DRAW_COUNT_RECENT = 100  # '최근' 회차로 간주할 횟수
    DRAW_COUNT_LATEST = 10  # '최신' 회차로 간주할 횟수


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    DB_PATH = os.path.join(Config.DATA_DIR, 'test_lotto.db')
    STATS_CACHE_FILE = os.path.join(Config.CACHE_DIR, 'test_stats_cache.json')


# 환경 변수로 설정할 설정 클래스 선택
config_mapping = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# 기본 설정 선택
Config = config_mapping.get(os.environ.get('FLASK_ENV', 'development'), DevelopmentConfig)
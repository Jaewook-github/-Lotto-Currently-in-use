# services/cache_service.py - 캐시 서비스
import json
import os
import time
from datetime import datetime
from config import Config
from services.stats_service import StatsService


class CacheService:
    """통계 데이터 캐싱 서비스"""

    @staticmethod
    def get_cached_stats(force_refresh=False):
        """캐시된 통계 데이터 반환 또는 새로 생성"""
        cache_file = Config.STATS_CACHE_FILE
        os.makedirs(os.path.dirname(cache_file), exist_ok=True)

        # 캐시 파일 유효성 검사
        cache_valid = False
        if os.path.exists(cache_file) and not force_refresh:
            try:
                # 파일 수정 시간 확인
                mtime = os.path.getmtime(cache_file)
                current_time = time.time()
                # 설정된 캐시 유효 시간 이내에 갱신된 캐시만 유효
                if current_time - mtime < Config.CACHE_LIFETIME:
                    cache_valid = True
            except:
                cache_valid = False

        # 캐시가 유효하면 파일에서 로드
        if cache_valid:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)

                # 캐시에 타임스탬프 추가
                stats['cache_timestamp'] = datetime.fromtimestamp(mtime).isoformat()
                stats['cache_age'] = round((time.time() - mtime) / 60, 1)  # 분 단위

                return stats
            except Exception as e:
                print(f"캐시 파일 로드 오류: {str(e)}")
                cache_valid = False

        # 캐시가 유효하지 않거나 강제 갱신이면 새로 계산
        stats = refresh_all_stats_cache(force=True)

        return stats


def refresh_all_stats_cache(force=False):
    """전체 통계 데이터 캐시 갱신"""
    cache_file = Config.STATS_CACHE_FILE
    os.makedirs(os.path.dirname(cache_file), exist_ok=True)

    try:
        # 통계 데이터 새로 계산
        stats = StatsService.get_full_stats()

        # 캐시 저장 시간 추가
        cache_time = datetime.now()
        stats['cache_timestamp'] = cache_time.isoformat()
        stats['cache_age'] = 0.0  # 새로 만든 캐시는 나이가 0

        # 캐시 파일에 저장
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False)

        return stats
    except Exception as e:
        print(f"캐시 갱신 오류: {str(e)}")

        # 오류 발생 시 기존 캐시 반환 시도
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                stats['cache_error'] = str(e)
                return stats
            except:
                pass

        # 기존 캐시도 로드 실패 시 빈 객체 반환
        return {'error': str(e), 'cache_error': True}
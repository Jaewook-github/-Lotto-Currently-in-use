# utils/cache_manager.py - 캐시 관리 유틸리티
import os
import json
import time
from datetime import datetime
import hashlib
from config import Config


class CacheManager:
    """
    캐시 관리를 위한 유틸리티 클래스
    파일 기반 캐싱 솔루션을 제공합니다.
    """

    @staticmethod
    def get_cache_path(cache_name):
        """
        캐시 파일 경로 생성

        Args:
            cache_name (str): 캐시 이름

        Returns:
            str: 캐시 파일 전체 경로
        """
        cache_filename = f"{cache_name}.json"
        cache_path = os.path.join(Config.CACHE_DIR, cache_filename)
        return cache_path

    @staticmethod
    def get_cache(cache_name, max_age=None):
        """
        지정된 이름의 캐시 데이터 조회

        Args:
            cache_name (str): 캐시 이름
            max_age (int, optional): 최대 캐시 유효 기간(초). None이면 Config 값 사용

        Returns:
            dict or None: 캐시 데이터 또는 유효하지 않은 경우 None
        """
        if max_age is None:
            max_age = Config.CACHE_LIFETIME

        cache_path = CacheManager.get_cache_path(cache_name)

        # 캐시 파일이 없는 경우
        if not os.path.exists(cache_path):
            return None

        try:
            # 캐시 파일 수정 시간 확인
            mtime = os.path.getmtime(cache_path)
            current_time = time.time()

            # 캐시 유효기간 확인
            if current_time - mtime > max_age:
                return None  # 캐시 만료

            # 캐시 파일 읽기
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 메타데이터 추가
            cache_data['_cache'] = {
                'timestamp': datetime.fromtimestamp(mtime).isoformat(),
                'age': round((current_time - mtime) / 60, 1),  # 분 단위
                'name': cache_name
            }

            return cache_data

        except (IOError, json.JSONDecodeError) as e:
            # 파일 읽기 또는 JSON 파싱 오류
            print(f"캐시 읽기 오류: {str(e)}")
            return None

    @staticmethod
    def set_cache(cache_name, data):
        """
        데이터를 캐시에 저장

        Args:
            cache_name (str): 캐시 이름
            data (dict): 저장할 데이터

        Returns:
            bool: 성공 여부
        """
        cache_path = CacheManager.get_cache_path(cache_name)

        # 캐시 디렉토리 생성
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        try:
            # 캐시 파일 쓰기
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            return True

        except IOError as e:
            print(f"캐시 쓰기 오류: {str(e)}")
            return False

    @staticmethod
    def invalidate_cache(cache_name):
        """
        지정된 이름의 캐시 무효화 (삭제)

        Args:
            cache_name (str): 캐시 이름

        Returns:
            bool: 성공 여부
        """
        cache_path = CacheManager.get_cache_path(cache_name)

        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                return True
            except OSError as e:
                print(f"캐시 삭제 오류: {str(e)}")
                return False
        return True  # 파일이 없어도 성공으로 간주

    @staticmethod
    def invalidate_all_caches():
        """
        모든 캐시 무효화 (전체 캐시 디렉토리 정리)

        Returns:
            int: 삭제된 캐시 파일 수
        """
        cache_dir = Config.CACHE_DIR
        count = 0

        if os.path.exists(cache_dir):
            for filename in os.listdir(cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(cache_dir, filename)
                    try:
                        os.remove(file_path)
                        count += 1
                    except OSError:
                        pass

        return count

    @staticmethod
    def get_or_create_cache(cache_name, data_generator, max_age=None):
        """
        캐시에서 데이터를 가져오거나 없으면 생성

        Args:
            cache_name (str): 캐시 이름
            data_generator (callable): 캐시 미스 시 데이터 생성 함수
            max_age (int, optional): 최대 캐시 유효 기간(초)

        Returns:
            dict: 캐시 데이터 또는 생성된 데이터
        """
        # 캐시 조회
        cached_data = CacheManager.get_cache(cache_name, max_age)

        if cached_data:
            return cached_data

        # 캐시 미스: 데이터 생성
        generated_data = data_generator()

        # 생성된 데이터 캐싱
        CacheManager.set_cache(cache_name, generated_data)

        # 메타데이터 추가
        generated_data['_cache'] = {
            'timestamp': datetime.now().isoformat(),
            'age': 0,  # 새로 생성된 캐시
            'name': cache_name
        }

        return generated_data

    @staticmethod
    def get_cache_key(*args, **kwargs):
        """
        인자들을 기반으로 고유한 캐시 키 생성

        Args:
            *args: 위치 인자
            **kwargs: 키워드 인자

        Returns:
            str: 생성된 캐시 키
        """
        # 모든 인자를 정렬된 문자열로 변환
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])

        # 전체 문자열 결합
        key_string = "|".join(key_parts)

        # 해시 생성 (첫 16자만 사용)
        hash_obj = hashlib.md5(key_string.encode())
        return hash_obj.hexdigest()[:16]
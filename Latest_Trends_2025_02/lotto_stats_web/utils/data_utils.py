# utils/data_utils.py - 데이터 처리 유틸리티
import json
import csv
from datetime import datetime
from io import StringIO
import math
import statistics
from collections import Counter


class DataUtils:
    """
    데이터 처리 및 변환을 위한 유틸리티 클래스
    """

    @staticmethod
    def normalize_data(data, min_val=0, max_val=1):
        """
        데이터 값을 지정된 범위로 정규화

        Args:
            data (list): 정규화할 숫자 리스트
            min_val (float): 결과 최소값
            max_val (float): 결과 최대값

        Returns:
            list: 정규화된 데이터
        """
        if not data:
            return []

        data_min = min(data)
        data_max = max(data)

        # 모든 값이 동일한 경우
        if data_max == data_min:
            return [min_val for _ in data]

        # 정규화 공식 적용
        normalized = [
            min_val + ((x - data_min) * (max_val - min_val) / (data_max - data_min))
            for x in data
        ]

        return normalized

    @staticmethod
    def calculate_percentiles(data, percentiles=[25, 50, 75]):
        """
        데이터의 백분위수 계산

        Args:
            data (list): 데이터 리스트
            percentiles (list): 계산할 백분위수 리스트

        Returns:
            dict: 백분위수 결과 {백분위수: 값}
        """
        if not data:
            return {p: None for p in percentiles}

        sorted_data = sorted(data)
        result = {}

        for p in percentiles:
            k = (len(sorted_data) - 1) * (p / 100)
            f = math.floor(k)
            c = math.ceil(k)

            if f == c:
                result[p] = sorted_data[int(k)]
            else:
                d0 = sorted_data[int(f)] * (c - k)
                d1 = sorted_data[int(c)] * (k - f)
                result[p] = d0 + d1

        return result

    @staticmethod
    def calculate_statistics(data):
        """
        데이터의 기본 통계값 계산

        Args:
            data (list): 숫자 데이터 리스트

        Returns:
            dict: 통계 결과
        """
        if not data:
            return {
                'count': 0,
                'min': None,
                'max': None,
                'sum': None,
                'mean': None,
                'median': None,
                'stdev': None,
                'variance': None
            }

        count = len(data)
        data_min = min(data)
        data_max = max(data)
        data_sum = sum(data)
        mean = data_sum / count

        try:
            median = statistics.median(data)
            stdev = statistics.stdev(data) if count > 1 else 0
            variance = statistics.variance(data) if count > 1 else 0
        except statistics.StatisticsError:
            median = mean
            stdev = 0
            variance = 0

        return {
            'count': count,
            'min': data_min,
            'max': data_max,
            'sum': data_sum,
            'mean': mean,
            'median': median,
            'stdev': stdev,
            'variance': variance
        }

    @staticmethod
    def frequency_distribution(data, bins=None):
        """
        데이터의 빈도 분포 계산

        Args:
            data (list): 데이터 리스트
            bins (int or list): 구간 수 또는 구간 목록

        Returns:
            dict: 빈도 분포 결과
        """
        if not data:
            return {'bins': [], 'counts': []}

        if bins is None:
            # 기본 카운터 사용 (고유값별 카운트)
            counter = Counter(data)
            return {
                'values': list(counter.keys()),
                'counts': list(counter.values())
            }

        # 숫자 구간을 지정한 경우
        if isinstance(bins, int):
            # 자동 구간 계산
            data_min = min(data)
            data_max = max(data)
            bin_width = (data_max - data_min) / bins

            bin_edges = [data_min + (i * bin_width) for i in range(bins + 1)]
        else:
            # 사용자 지정 구간 사용
            bin_edges = bins

        # 각 구간별 카운트
        counts = [0] * (len(bin_edges) - 1)
        for x in data:
            for i in range(len(bin_edges) - 1):
                if bin_edges[i] <= x < bin_edges[i + 1] or (i == len(bin_edges) - 2 and x == bin_edges[i + 1]):
                    counts[i] += 1
                    break

        # 구간 레이블 생성
        labels = [f"{bin_edges[i]:.1f}-{bin_edges[i + 1]:.1f}" for i in range(len(bin_edges) - 1)]

        return {
            'bins': bin_edges,
            'counts': counts,
            'labels': labels
        }

    @staticmethod
    def json_to_csv(json_data, output_file=None):
        """
        JSON 데이터를 CSV로 변환

        Args:
            json_data (list or str): JSON 데이터 또는 JSON 문자열
            output_file (str, optional): 출력 파일 경로, None이면 문자열 반환

        Returns:
            str or bool: CSV 문자열 또는 파일 저장 성공 여부
        """
        # JSON 문자열인 경우 파싱
        if isinstance(json_data, str):
            try:
                json_data = json.loads(json_data)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string")

        # 리스트가 아닌 경우 오류
        if not isinstance(json_data, list):
            raise ValueError("JSON data must be a list of objects")

        # 빈 데이터인 경우
        if not json_data:
            return "" if output_file is None else False

        # 필드 추출 (첫 번째 객체의 모든 키)
        fields = list(json_data[0].keys())

        # CSV 생성
        output = StringIO() if output_file is None else open(output_file, 'w', newline='', encoding='utf-8')
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(json_data)

        if output_file is None:
            # 문자열로 반환
            result = output.getvalue()
            output.close()
            return result
        else:
            # 파일로 저장
            output.close()
            return True

    @staticmethod
    def format_timestamp(timestamp, format_str="%Y-%m-%d %H:%M:%S"):
        """
        타임스탬프를 읽기 쉬운 형식으로 변환

        Args:
            timestamp (int or float): 유닉스 타임스탬프
            format_str (str): 출력 형식

        Returns:
            str: 포맷된 날짜 문자열
        """
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime(format_str)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def get_trend(data):
        """
        데이터의 추세 계산 (상승, 하락, 유지)

        Args:
            data (list): 시간순으로 정렬된 데이터 리스트

        Returns:
            str: 'up', 'down', 'stable'
        """
        if not data or len(data) < 2:
            return 'stable'

        # 단순 선형 회귀 기울기 계산
        n = len(data)
        sum_x = sum(range(n))
        sum_y = sum(data)
        sum_xx = sum(i * i for i in range(n))
        sum_xy = sum(i * y for i, y in enumerate(data))

        # 기울기 계산
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x * sum_x)

        # 임계값 (민감도 조정)
        threshold = (max(data) - min(data)) * 0.05

        if slope > threshold:
            return 'up'
        elif slope < -threshold:
            return 'down'
        else:
            return 'stable'
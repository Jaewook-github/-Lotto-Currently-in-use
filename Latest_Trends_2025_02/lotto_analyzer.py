# lotto_analyzer.py

import sqlite3
import pandas as pd
import numpy as np
from collections import Counter
from config import LottoConfig


class LottoAnalyzer:
    def __init__(self, db_path):
        """
        로또 분석기 초기화
        Args:
            db_path (str): SQLite DB 파일 경로
        """
        self.db_path = db_path
        self.config = LottoConfig()
        self.results = None
        self.freq_dfs = None
        self.stats_df = None
        self.hot_cold_numbers = None
        self.update_hot_cold_numbers(50)  # 기본적으로 최근 50회차 기준 핫/콜드 번호 업데이트

    def update_hot_cold_numbers(self, draw_count=50):
        """
        핫-콜드 번호 업데이트 함수
        Args:
            draw_count (int): 분석할 회차 수
        """
        hot_cold_info = self.get_hot_cold_numbers(draw_count)
        self.hot_cold_numbers = hot_cold_info
        # 설정에 반영
        self.config.HOT_COLD_SETTINGS['hot_numbers'] = hot_cold_info['hot_numbers']
        self.config.HOT_COLD_SETTINGS['cold_numbers'] = hot_cold_info['cold_numbers']
        self.config.HOT_COLD_SETTINGS['normal_numbers'] = hot_cold_info['normal_numbers']

    def get_hot_cold_numbers(self, draw_count=50):
        """
        최근 n회차에서의 핫번호(자주 출현)와 콜드번호(출현 빈도 낮음) 추출
        Args:
            draw_count (int): 분석할 회차 수
        """
        conn = sqlite3.connect(self.db_path)
        query = f"""
        SELECT draw_number, num1, num2, num3, num4, num5, num6
        FROM lotto_results
        ORDER BY draw_number DESC
        LIMIT {draw_count}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        # 모든 번호를 하나의 리스트로
        all_numbers = []
        for _, row in df.iterrows():
            all_numbers.extend([row['num1'], row['num2'], row['num3'],
                                row['num4'], row['num5'], row['num6']])

        # 번호별 출현 빈도 계산
        number_counts = Counter(all_numbers)

        # 빈도 기준 정렬
        sorted_counts = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)

        # 평균 출현 빈도 계산
        avg_frequency = (draw_count * 6) / 45

        # 핫번호 (평균 이상 출현)
        hot_numbers = [num for num, count in sorted_counts if count > avg_frequency]

        # 콜드번호 (평균 미만 출현)
        cold_numbers = [num for num, count in sorted_counts if count < avg_frequency]

        # 보통 번호 (평균 출현)
        normal_numbers = [num for num, count in sorted_counts if count == avg_frequency]

        return {
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'normal_numbers': normal_numbers,
            'number_frequencies': dict(sorted_counts)
        }

    def get_ball_color(self, number):
        """번호의 색상을 반환하는 함수"""
        for color, number_range in self.config.BALL_COLORS.items():
            if number in number_range:
                return color
        return None

    def analyze_color_pattern(self, numbers):
        """당첨번호의 색상 패턴을 분석하는 함수"""
        colors = [self.get_ball_color(num) for num in numbers]
        # None 값을 제거하고 Counter 생성
        colors = [color for color in colors if color is not None]
        return Counter(colors)

    def count_multiples(self, numbers, multiple_list):
        """특정 배수의 개수를 세는 함수"""
        return len([num for num in numbers if num in multiple_list])

    def count_composite_numbers(self, numbers):
        """합성수의 개수를 세는 함수"""
        return len([num for num in numbers if num in self.config.COMPOSITE_NUMBERS])

    def count_perfect_squares(self, numbers):
        """완전제곱수의 개수를 세는 함수"""
        return len([num for num in numbers if num in self.config.PERFECT_SQUARES])

    def count_prime_numbers(self, numbers):
        """소수의 개수를 세는 함수"""
        return len([num for num in numbers if num in self.config.PRIME_NUMBERS])

    def calculate_last_digit_sum(self, numbers):
        """끝수합을 계산하는 함수"""
        return sum(num % 10 for num in numbers)

    def is_palindrome(self, number):
        """회문수 여부를 확인하는 함수"""
        if number < 10:
            return False
        number_str = str(number)
        return number_str == number_str[::-1]

    def count_palindrome_numbers(self, numbers):
        """회문수의 개수를 세는 함수"""
        return len([num for num in numbers if self.is_palindrome(num)])

    def is_double_number(self, number):
        """쌍수 여부를 확인하는 함수"""
        if number < 10:
            return False
        number_str = str(number)
        return len(number_str) == 2 and number_str[0] == number_str[1]

    def count_double_numbers(self, numbers):
        """쌍수의 개수를 세는 함수"""
        return len([num for num in numbers if self.is_double_number(num)])

    def get_mirror_number_count(self, numbers):
        """동형수 그룹의 개수를 세는 함수"""
        mirror_count = 0
        numbers_set = set(numbers)

        for group in self.config.MIRROR_NUMBER_GROUPS:
            if any(num in numbers_set for num in group):
                mirror_count += 1

        return mirror_count

    def find_consecutive_numbers(self, numbers):
        """연속된 번호 패턴을 찾는 함수"""
        sorted_nums = sorted(numbers)
        consecutive_groups = []
        current_group = [sorted_nums[0]]

        for i in range(1, len(sorted_nums)):
            if sorted_nums[i] == sorted_nums[i - 1] + 1:
                current_group.append(sorted_nums[i])
            else:
                if len(current_group) >= 2:
                    consecutive_groups.append(current_group)
                current_group = [sorted_nums[i]]

        if len(current_group) >= 2:
            consecutive_groups.append(current_group)

        return consecutive_groups

    def calculate_ac(self, numbers):
        """AC(Adjacency Criteria) 값을 계산하는 함수"""
        sorted_numbers = sorted(numbers, reverse=True)
        differences = set()

        for i in range(len(sorted_numbers)):
            for j in range(i + 1, len(sorted_numbers)):
                diff = sorted_numbers[i] - sorted_numbers[j]
                differences.add(diff)

        return len(differences) - 5

    def get_high_low_ratio(self, numbers):
        """고저 비율을 계산하는 함수 (1-23: 저번호, 24-45: 고번호)"""
        high_boundary = self.config.TREND_CRITERIA['high_low_ratio']['high_boundary']
        low_count = len([x for x in numbers if x < high_boundary])
        high_count = 6 - low_count
        return f"{high_count}:{low_count}"

    def get_odd_even_ratio(self, numbers):
        """홀짝 비율을 계산하는 함수"""
        odd_count = len([x for x in numbers if x % 2 == 1])
        even_count = 6 - odd_count
        return f"{odd_count}:{even_count}"

    def calculate_sum(self, numbers):
        """번호 합계를 계산하는 함수"""
        return sum(numbers)

    def calculate_std_deviation(self, numbers):
        """표준편차를 계산하는 함수 (번호 분산도)"""
        return round(np.std(numbers), 2)

    def calculate_average_gap(self, numbers):
        """평균 간격을 계산하는 함수"""
        sorted_nums = sorted(numbers)
        gaps = [sorted_nums[i] - sorted_nums[i - 1] for i in range(1, len(sorted_nums))]
        return round(np.mean(gaps), 2)

    def check_diagonal_pattern(self, numbers):
        """
        대각선 매칭 패턴을 확인하는 함수
        """
        # 주대각선 및 부대각선 정의
        main_diagonals = [set(diag) for diag in self.config.DIAGONAL_PATTERNS['주대각선']]
        anti_diagonals = [set(diag) for diag in self.config.DIAGONAL_PATTERNS['부대각선']]

        # 모든 대각선 패턴 합치기
        all_diagonals = main_diagonals + anti_diagonals
        numbers_set = set(numbers)

        # 대각선 교차점 확인
        matches = 0
        intersections = []

        for diagonal in all_diagonals:
            intersection = numbers_set.intersection(diagonal)
            if len(intersection) >= 2:  # 2개 이상 매칭되는 경우
                matches += 1
                intersections.append(intersection)

        return {
            'has_diagonal_pattern': matches > 0,
            'diagonal_match_count': matches,
            'intersections': intersections
        }

    def check_previous_draws_overlap(self, numbers, prev_count=3):
        """
        이전 회차 당첨번호와의 중복을 확인하는 함수

        Args:
            numbers (list): 확인할 번호 리스트
            prev_count (int): 확인할 이전 회차 수
        """
        conn = sqlite3.connect(self.db_path)
        query = f"""
        SELECT draw_number, num1, num2, num3, num4, num5, num6
        FROM lotto_results
        ORDER BY draw_number DESC
        LIMIT {prev_count}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        overlaps = {}
        numbers_set = set(numbers)

        for i, row in df.iterrows():
            prev_numbers = {row['num1'], row['num2'], row['num3'],
                            row['num4'], row['num5'], row['num6']}
            overlap_count = len(numbers_set.intersection(prev_numbers))
            overlaps[row['draw_number']] = overlap_count

        return overlaps

    def _analyze_single_draw(self, numbers):
        """단일 회차 분석"""
        # 모서리 번호 분석
        all_corner_numbers = []
        for corner_nums in self.config.CORNER_NUMBERS.values():
            all_corner_numbers.extend(corner_nums)
        corner_count = len(set(numbers).intersection(set(all_corner_numbers)))

        # 나머지 분석 수행
        ac_value = self.calculate_ac(numbers)
        consecutive_groups = self.find_consecutive_numbers(numbers)
        color_count = self.analyze_color_pattern(numbers)

        # 색상 조합을 문자열로 변환 (정렬된 상태로)
        color_combination = "-".join(
            f"{color}:{count}" for color, count in
            sorted(color_count.items(), key=lambda x: x[0] if x[0] is not None else "")
        )

        # 추가 트렌드 분석 정보
        high_low_ratio = self.get_high_low_ratio(numbers)
        odd_even_ratio = self.get_odd_even_ratio(numbers)
        sum_value = self.calculate_sum(numbers)
        std_deviation = self.calculate_std_deviation(numbers)
        average_gap = self.calculate_average_gap(numbers)
        diagonal_pattern = self.check_diagonal_pattern(numbers)

        # 단일 회차 분석 결과 반환
        results = {
            'corner_count': corner_count,
            'ac_value': ac_value,
            'consecutive_groups': consecutive_groups,
            'color_count': len(color_count),
            'color_combination': color_combination,
            'composite_count': self.count_composite_numbers(numbers),
            'perfect_square_count': self.count_perfect_squares(numbers),
            'mirror_number_count': self.get_mirror_number_count(numbers),
            'multiples_3_count': self.count_multiples(numbers, self.config.MULTIPLES['3의 배수']),
            'multiples_4_count': self.count_multiples(numbers, self.config.MULTIPLES['4의 배수']),
            'multiples_5_count': self.count_multiples(numbers, self.config.MULTIPLES['5의 배수']),
            'prime_count': self.count_prime_numbers(numbers),
            'last_digit_sum': self.calculate_last_digit_sum(numbers),
            'palindrome_count': self.count_palindrome_numbers(numbers),
            'double_number_count': self.count_double_numbers(numbers),
            'high_low_ratio': high_low_ratio,
            'odd_even_ratio': odd_even_ratio,
            'sum': sum_value,
            'std_deviation': std_deviation,
            'average_gap': average_gap,
            'diagonal_pattern': diagonal_pattern
        }

        return results

    def analyze_single_numbers(self, draw_numbers=None):
        """로또 번호 종합 분석 함수"""
        if draw_numbers:
            # 단일 회차 분석
            return self._analyze_single_draw(draw_numbers)
        else:
            # DB에서 전체 회차 분석
            conn = sqlite3.connect(self.db_path)
            query = """
            SELECT draw_number, num1, num2, num3, num4, num5, num6
            FROM lotto_results
            ORDER BY draw_number
            """
            df = pd.read_sql_query(query, conn)

            self.results = {
                'draw_numbers': [],
                'numbers': [],
                'high_low_ratios': [],
                'odd_even_ratios': [],
                'sums': [],
                'std_deviations': [],
                'average_gaps': [],
                'diagonal_patterns': [],
                'diagonal_match_counts': [],
                'corner_results': [],
                'ac_results': [],
                'consecutive_patterns': [],
                'color_patterns': [],
                'color_combinations': [],
                'composite_counts': [],
                'perfect_square_counts': [],
                'mirror_number_counts': [],
                'multiples_3_counts': [],
                'multiples_4_counts': [],
                'multiples_5_counts': [],
                'prime_counts': [],
                'last_digit_sums': [],
                'palindrome_counts': [],
                'double_number_counts': []
            }

            for _, row in df.iterrows():
                numbers = [row['num1'], row['num2'], row['num3'],
                           row['num4'], row['num5'], row['num6']]

                self.results['draw_numbers'].append(row['draw_number'])
                self.results['numbers'].append(numbers)
                self.results['high_low_ratios'].append(self.get_high_low_ratio(numbers))
                self.results['odd_even_ratios'].append(self.get_odd_even_ratio(numbers))
                self.results['sums'].append(self.calculate_sum(numbers))
                self.results['std_deviations'].append(self.calculate_std_deviation(numbers))
                self.results['average_gaps'].append(self.calculate_average_gap(numbers))

                diagonal_result = self.check_diagonal_pattern(numbers)
                self.results['diagonal_patterns'].append(diagonal_result['has_diagonal_pattern'])
                self.results['diagonal_match_counts'].append(diagonal_result['diagonal_match_count'])

                # 기존 분석 함수 호출
                results = self._analyze_single_draw(numbers)

                self.results['corner_results'].append(results['corner_count'])
                self.results['ac_results'].append(results['ac_value'])

                if results['consecutive_groups']:
                    # 각 연속 그룹의 길이 기록
                    consec_lengths = [len(group) for group in results['consecutive_groups']]
                    self.results['consecutive_patterns'].append(consec_lengths)
                else:
                    self.results['consecutive_patterns'].append([0])  # 연속번호 없음

                self.results['color_patterns'].append(results['color_count'])
                self.results['color_combinations'].append(results['color_combination'])
                self.results['composite_counts'].append(results['composite_count'])
                self.results['perfect_square_counts'].append(results['perfect_square_count'])
                self.results['mirror_number_counts'].append(results['mirror_number_count'])
                self.results['multiples_3_counts'].append(results['multiples_3_count'])
                self.results['multiples_4_counts'].append(results['multiples_4_count'])
                self.results['multiples_5_counts'].append(results['multiples_5_count'])
                self.results['prime_counts'].append(results['prime_count'])
                self.results['last_digit_sums'].append(results['last_digit_sum'])
                self.results['palindrome_counts'].append(results['palindrome_count'])
                self.results['double_number_counts'].append(results['double_number_count'])

            conn.close()

        self._create_frequency_dataframes()
        self._calculate_total_statistics()
        return self.freq_dfs, self.stats_df
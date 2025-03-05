# lotto_generator.py

import random
import sqlite3
import numpy as np
import pandas as pd
from collections import Counter
from config import LottoConfig
from lotto_analyzer import LottoAnalyzer


class LottoGenerator:
    def __init__(self, db_path):
        self.db_path = db_path
        self.config = LottoConfig()
        self.analyzer = LottoAnalyzer(db_path)
        # 핫-콜드 번호 업데이트
        self.analyzer.update_hot_cold_numbers(50)

    def calculate_combination_score(self, numbers):
        """
        번호 조합의 트렌드 점수를 계산하는 함수
        최근 트렌드에 얼마나 부합하는지 점수화
        """
        sorted_numbers = sorted(numbers)
        results = self.analyzer._analyze_single_draw(numbers)
        trend_criteria = self.config.TREND_CRITERIA
        score = 0

        # 1. 홀짝 비율 점수
        odd_count = len([x for x in numbers if x % 2 == 1])
        even_count = 6 - odd_count
        odd_even_ratio = f"{odd_count}:{even_count}"
        score += trend_criteria['odd_even_ratio']['weights'].get(odd_even_ratio, 0.5)

        # 2. 고저 비율 점수
        high_boundary = trend_criteria['high_low_ratio']['high_boundary']
        high_count = len([x for x in numbers if x >= high_boundary])
        low_count = 6 - high_count
        high_low_ratio = f"{high_count}:{low_count}"
        score += trend_criteria['high_low_ratio']['weights'].get(high_low_ratio, 0.5)

        # 3. 총합 점수
        total_sum = sum(numbers)
        if trend_criteria['sum_trend']['optimal_range']['min'] <= total_sum <= \
                trend_criteria['sum_trend']['optimal_range']['max']:
            score += trend_criteria['sum_trend']['weights']['optimal']
        elif trend_criteria['sum_trend']['min'] <= total_sum <= trend_criteria['sum_trend']['max']:
            score += trend_criteria['sum_trend']['weights']['acceptable']
        else:
            score += trend_criteria['sum_trend']['weights']['outside']

        # 4. AC값 점수
        ac_value = results['ac_value']
        if ac_value == 8:
            score += trend_criteria['ac_trend']['weights']['8']
        elif ac_value == 9:
            score += trend_criteria['ac_trend']['weights']['9']
        elif ac_value == 7:
            score += trend_criteria['ac_trend']['weights']['7']
        else:
            score += trend_criteria['ac_trend']['weights']['other']

        # 5. 연속 번호 패턴 점수
        consecutive_groups = results['consecutive_groups']
        if consecutive_groups and len(consecutive_groups) == 1 and len(consecutive_groups[0]) == 2:
            # 2개 연속번호 1쌍
            score += trend_criteria['consecutive_trend']['weights']['one_pair']
        elif not consecutive_groups:
            # 연속번호 없음
            score += trend_criteria['consecutive_trend']['weights']['no_consecutive']
        else:
            # 기타 연속번호 패턴
            score += trend_criteria['consecutive_trend']['weights']['other']

        # 6. 대각선 매칭 패턴 점수
        diagonal_pattern = self.analyzer.check_diagonal_pattern(numbers)
        if diagonal_pattern['diagonal_match_count'] >= trend_criteria['diagonal_trend']['min_intersections']:
            score += trend_criteria['diagonal_trend']['weights']['two_plus']
        elif diagonal_pattern['diagonal_match_count'] == 1:
            score += trend_criteria['diagonal_trend']['weights']['one']
        else:
            score += trend_criteria['diagonal_trend']['weights']['none']

        # 7. 번호 간격 점수
        avg_gap = self.analyzer.calculate_average_gap(numbers)
        if trend_criteria['gap_trend']['optimal_range']['min'] <= avg_gap <= \
                trend_criteria['gap_trend']['optimal_range']['max']:
            score += trend_criteria['gap_trend']['weights']['optimal']
        elif avg_gap in [4, 8]:  # 인접 간격
            score += trend_criteria['gap_trend']['weights']['close']
        else:
            score += trend_criteria['gap_trend']['weights']['far']

        # 8. 모서리 패턴 점수
        corner_count = results['corner_count']
        if corner_count == trend_criteria['corner_trend']['optimal']:
            score += trend_criteria['corner_trend']['weights']['3']
        elif corner_count == 2:
            score += trend_criteria['corner_trend']['weights']['2']
        elif corner_count == 4:
            score += trend_criteria['corner_trend']['weights']['4']
        else:
            score += trend_criteria['corner_trend']['weights']['other']

        # 9. 소수/합성수 분포 점수
        prime_count = results['prime_count']
        composite_count = results['composite_count']

        if (prime_count == trend_criteria['number_type_trend']['prime']['optimal'] and
                composite_count == trend_criteria['number_type_trend']['composite']['optimal']):
            score += trend_criteria['number_type_trend']['weights']['optimal']
        elif (trend_criteria['number_type_trend']['prime']['range']['min'] <= prime_count <=
              trend_criteria['number_type_trend']['prime']['range']['max'] and
              trend_criteria['number_type_trend']['composite']['range']['min'] <= composite_count <=
              trend_criteria['number_type_trend']['composite']['range']['max']):
            score += trend_criteria['number_type_trend']['weights']['acceptable']
        else:
            score += trend_criteria['number_type_trend']['weights']['outside']

        # 10. 이전 당첨번호 활용 점수
        prev_draws_overlap = self.analyzer.check_previous_draws_overlap(numbers,
                                                                        trend_criteria['previous_draw_trend'][
                                                                            'lookback_draws'])
        # 직전 회차와의 중복 확인
        if list(prev_draws_overlap.values())[0] == trend_criteria['previous_draw_trend']['include_count']:
            score += trend_criteria['previous_draw_trend']['weights']['one_number']
        elif list(prev_draws_overlap.values())[0] == 0:
            score += trend_criteria['previous_draw_trend']['weights']['none']
        else:
            score += trend_criteria['previous_draw_trend']['weights']['multiple']

        # 11. 분산도(표준편차) 점수
        std_dev = self.analyzer.calculate_std_deviation(numbers)
        if trend_criteria['std_deviation_trend']['optimal_range']['min'] <= std_dev <= \
                trend_criteria['std_deviation_trend']['optimal_range']['max']:
            score += trend_criteria['std_deviation_trend']['weights']['optimal']
        elif trend_criteria['std_deviation_trend']['optimal_range']['min'] - 2 <= std_dev <= \
                trend_criteria['std_deviation_trend']['optimal_range']['max'] + 2:
            score += trend_criteria['std_deviation_trend']['weights']['close']
        else:
            score += trend_criteria['std_deviation_trend']['weights']['far']

        # 12. 색상 다양성 점수
        color_count = results['color_count']
        if color_count == 4:
            score += trend_criteria['color_trend']['weights']['4']
        elif color_count == 5:
            score += trend_criteria['color_trend']['weights']['5']
        elif color_count == 3:
            score += trend_criteria['color_trend']['weights']['3']
        else:
            score += trend_criteria['color_trend']['weights']['other']

        # 13. 핫-콜드 번호 분포 점수
        hot_numbers = set(self.config.HOT_COLD_SETTINGS['hot_numbers'])
        cold_numbers = set(self.config.HOT_COLD_SETTINGS['cold_numbers'])
        normal_numbers = set(self.config.HOT_COLD_SETTINGS['normal_numbers'])

        hot_count = len(set(numbers).intersection(hot_numbers))
        cold_count = len(set(numbers).intersection(cold_numbers))
        normal_count = len(set(numbers).intersection(normal_numbers))

        hot_cold_settings = self.config.HOT_COLD_SETTINGS

        # 핫-콜드 개수 범위 체크
        if (hot_cold_settings['hot_cold_ratio']['hot']['min'] <= hot_count <=
                hot_cold_settings['hot_cold_ratio']['hot']['max'] and
                hot_cold_settings['hot_cold_ratio']['cold']['min'] <= cold_count <=
                hot_cold_settings['hot_cold_ratio']['cold']['max'] and
                hot_cold_settings['hot_cold_ratio']['normal']['min'] <= normal_count <=
                hot_cold_settings['hot_cold_ratio']['normal']['max']):
            score += (hot_count * hot_cold_settings['weights']['hot'] +
                      cold_count * hot_cold_settings['weights']['cold'] +
                      normal_count * hot_cold_settings['weights']['normal']) / 6

        return score

    def validate_combination(self, numbers):
        """번호 조합이 설정된 기준에 맞는지 검증하는 함수"""
        if not numbers or len(numbers) != 6:
            return False

        sorted_numbers = sorted(numbers)
        results = self.analyzer.analyze_single_numbers(numbers)

        # 1. 총합 구간 검증
        total_sum = sum(numbers)
        if not (self.config.FILTER_CRITERIA['sum_range']['min'] <= total_sum <=
                self.config.FILTER_CRITERIA['sum_range']['max']):
            return False

        # 2. AC값 검증
        if not (self.config.FILTER_CRITERIA['ac_range']['min'] <= results['ac_value'] <=
                self.config.FILTER_CRITERIA['ac_range']['max']):
            return False

        # 3. 홀짝 비율 검증
        odd_count = len([x for x in numbers if x % 2 == 1])
        even_count = 6 - odd_count
        if {odd_count, even_count} in self.config.FILTER_CRITERIA['odd_even_exclude']:
            return False

        # 4. 고저 비율 검증 (1-22: 저번호, 23-45: 고번호)
        low_count = len([x for x in numbers if x <= 22])
        high_count = 6 - low_count
        if {low_count, high_count} in self.config.FILTER_CRITERIA['high_low_exclude']:
            return False

        # 5. 끝수 검증
        last_digits = [n % 10 for n in numbers]
        last_digit_count = Counter(last_digits)
        max_same_last_digit = max(last_digit_count.values())
        if not (self.config.FILTER_CRITERIA['same_last_digit']['min'] <= max_same_last_digit <=
                self.config.FILTER_CRITERIA['same_last_digit']['max']):
            return False

        # 6. 끝수 합 검증
        last_digit_sum = sum(last_digits)
        if not (self.config.FILTER_CRITERIA['last_digit_sum']['min'] <= last_digit_sum <=
                self.config.FILTER_CRITERIA['last_digit_sum']['max']):
            return False

        # 7. 연속번호 검증
        consecutive_groups = results['consecutive_groups']
        if not consecutive_groups and not self.config.FILTER_CRITERIA['consecutive_numbers']['none']:
            return False
        if consecutive_groups:
            pair_count = len(consecutive_groups)
            if pair_count not in self.config.FILTER_CRITERIA['consecutive_numbers']['pairs']:
                return False

        # 8. 숫자 특성 검증
        # 8-1. 소수 개수
        if not (self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['min'] <= results['prime_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['max']):
            return False

        # 8-2. 합성수 개수
        if not (self.config.FILTER_CRITERIA['number_counts']['composite_numbers']['min'] <= results[
            'composite_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['composite_numbers']['max']):
            return False

        # 8-3. 배수 개수
        # 3의 배수
        if not (self.config.FILTER_CRITERIA['number_counts']['multiples_of_3']['min'] <= results['multiples_3_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['multiples_of_3']['max']):
            return False

        # 4의 배수
        if not (self.config.FILTER_CRITERIA['number_counts']['multiples_of_4']['min'] <= results['multiples_4_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['multiples_of_4']['max']):
            return False

        # 5의 배수
        if not (self.config.FILTER_CRITERIA['number_counts']['multiples_of_5']['min'] <= results['multiples_5_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['multiples_of_5']['max']):
            return False

        # 8-4. 쌍수 개수
        if not (self.config.FILTER_CRITERIA['number_counts']['double_numbers']['min'] <= results[
            'double_number_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['double_numbers']['max']):
            return False

        # 8-5. 모서리 번호 개수
        if not (self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['min'] <= results['corner_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['max']):
            return False

        # 9. 시작번호, 끝번호 검증
        if (sorted_numbers[0] > self.config.FILTER_CRITERIA['number_range']['start_number_max'] or
                sorted_numbers[-1] < self.config.FILTER_CRITERIA['number_range']['end_number_min']):
            return False

        # 10. 구간별 번호 개수 검증
        sections = [0] * 5  # 1-10, 11-20, 21-30, 31-40, 41-45
        for num in numbers:
            if 1 <= num <= 10:  # 1-10 구간
                sections[0] += 1
            elif 11 <= num <= 20:  # 11-20 구간
                sections[1] += 1
            elif 21 <= num <= 30:  # 21-30 구간
                sections[2] += 1
            elif 31 <= num <= 40:  # 31-40 구간
                sections[3] += 1
            elif 41 <= num <= 45:  # 41-45 구간
                sections[4] += 1

        for count in sections:
            if not (self.config.FILTER_CRITERIA['section_numbers']['min'] <= count <=
                    self.config.FILTER_CRITERIA['section_numbers']['max']):
                return False

        # 11. 색상 개수 검증
        if not (self.config.FILTER_CRITERIA['colors']['min'] <= results['color_count'] <=
                self.config.FILTER_CRITERIA['colors']['max']):
            return False

        # 12. 대각선 패턴 검증 (새로 추가)
        diagonal_pattern = self.analyzer.check_diagonal_pattern(numbers)
        if not diagonal_pattern['has_diagonal_pattern']:
            # 최근 트렌드에 따라 대각선 패턴이 없는 조합은 제외할 수 있음
            # 단, 현재는 비활성화 (필요시 활성화)
            pass

        # 13. 표준편차 검증 (새로 추가)
        std_dev = self.analyzer.calculate_std_deviation(numbers)
        # 표준편차 범위가 너무 작거나 크면 번호가 너무 뭉쳐있거나 너무 분산되어 있음
        # 현재는 비활성화 (필요시 범위 지정하여 활성화)

        return True

    def generate_numbers(self, num_games=1, use_trend_score=True, min_score_threshold=10):
        """
        설정된 기준에 맞는 로또 번호 조합을 생성하는 함수

        Args:
            num_games (int): 생성할 게임 수
            use_trend_score (bool): 트렌드 점수를 사용할지 여부
            min_score_threshold (float): 최소 트렌드 점수 기준 (use_trend_score=True일 때 사용)
        """
        valid_combinations = []
        scored_combinations = []
        total_attempts = 0
        max_attempts = num_games * 1000  # 최대 시도 횟수 설정

        while len(
                scored_combinations if use_trend_score else valid_combinations) < num_games and total_attempts < max_attempts:
            # 번호 랜덤 생성
            numbers = sorted(random.sample(range(1, 46), 6))

            # 생성된 번호가 기준에 맞는지 검증
            if self.validate_combination(numbers) and numbers not in valid_combinations:
                if use_trend_score:
                    # 트렌드 점수 계산
                    score = self.calculate_combination_score(numbers)
                    if score >= min_score_threshold:
                        scored_combinations.append((numbers, score))
                else:
                    valid_combinations.append(numbers)

            total_attempts += 1

        # 트렌드 점수 사용 시 점수별 정렬
        if use_trend_score:
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
            return scored_combinations[:num_games]
        else:
            return valid_combinations

    def generate_numbers_with_previous(self, num_games=1, use_trend_score=True, lookback=3, include_count=1):
        """
        이전 회차 번호를 포함한 로또 번호 조합을 생성하는 함수

        Args:
            num_games (int): 생성할 게임 수
            use_trend_score (bool): 트렌드 점수를 사용할지 여부
            lookback (int): 확인할 이전 회차 수
            include_count (int): 포함할 이전 회차 번호 개수
        """
        # 이전 회차 번호 가져오기
        conn = sqlite3.connect(self.db_path)
        query = f"""
        SELECT draw_number, num1, num2, num3, num4, num5, num6
        FROM lotto_results
        ORDER BY draw_number DESC
        LIMIT {lookback}
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        prev_numbers = []
        for _, row in df.iterrows():
            prev_numbers.extend([row['num1'], row['num2'], row['num3'],
                                 row['num4'], row['num5'], row['num6']])

        # 중복 제거
        prev_numbers = list(set(prev_numbers))

        valid_combinations = []
        scored_combinations = []
        total_attempts = 0
        max_attempts = num_games * 1000  # 최대 시도 횟수 설정

        while len(
                scored_combinations if use_trend_score else valid_combinations) < num_games and total_attempts < max_attempts:
            # 이전 회차 번호 중 include_count개 선택
            if len(prev_numbers) > include_count:
                included_numbers = random.sample(prev_numbers, include_count)
            else:
                included_numbers = prev_numbers[:include_count]

            # 나머지 번호 랜덤 생성
            remaining_count = 6 - len(included_numbers)
            remaining_pool = [n for n in range(1, 46) if n not in included_numbers]
            remaining_numbers = random.sample(remaining_pool, remaining_count)

            # 최종 번호 조합
            numbers = sorted(included_numbers + remaining_numbers)

            # 생성된 번호가 기준에 맞는지 검증
            if self.validate_combination(numbers) and numbers not in valid_combinations:
                if use_trend_score:
                    # 트렌드 점수 계산
                    score = self.calculate_combination_score(numbers)
                    scored_combinations.append((numbers, score))
                else:
                    valid_combinations.append(numbers)

            total_attempts += 1

        # 트렌드 점수 사용 시 점수별 정렬
        if use_trend_score:
            scored_combinations.sort(key=lambda x: x[1], reverse=True)
            return scored_combinations[:num_games]
        else:
            return valid_combinations

    def generate_numbers_with_pattern(self, num_games=1, pattern='odd_even', pattern_value='4:2'):
        """
        특정 패턴에 맞는 로또 번호 조합을 생성하는 함수

        Args:
            num_games (int): 생성할 게임 수
            pattern (str): 패턴 유형 ('odd_even', 'high_low', 'diagonal', 'corner', 'hot_cold')
            pattern_value (str): 패턴 값
        """
        valid_combinations = []
        total_attempts = 0
        max_attempts = num_games * 1000  # 최대 시도 횟수 설정

        while len(valid_combinations) < num_games and total_attempts < max_attempts:
            # 패턴에 따른 번호 생성
            if pattern == 'odd_even':
                numbers = self._generate_with_odd_even_pattern(pattern_value)
            elif pattern == 'high_low':
                numbers = self._generate_with_high_low_pattern(pattern_value)
            elif pattern == 'diagonal':
                numbers = self._generate_with_diagonal_pattern(int(pattern_value))
            elif pattern == 'corner':
                numbers = self._generate_with_corner_pattern(int(pattern_value))
            elif pattern == 'hot_cold':
                hot_count, cold_count = map(int, pattern_value.split(':'))
                numbers = self._generate_with_hot_cold_pattern(hot_count, cold_count)
            else:
                # 패턴 없이 랜덤 생성
                numbers = sorted(random.sample(range(1, 46), 6))

            # 생성된 번호가 기준에 맞는지 검증
            if self.validate_combination(numbers) and numbers not in valid_combinations:
                valid_combinations.append(numbers)

            total_attempts += 1

        # 트렌드 점수 계산 및 정렬
        scored_combinations = []
        for numbers in valid_combinations:
            score = self.calculate_combination_score(numbers)
            scored_combinations.append((numbers, score))

        scored_combinations.sort(key=lambda x: x[1], reverse=True)
        return scored_combinations[:num_games]

    def _generate_with_odd_even_pattern(self, pattern_value):
        """
        홀짝 패턴에 맞는 번호 생성

        Args:
            pattern_value (str): '홀수:짝수' 형태의 비율 (예: '4:2')
        """
        odd_count, even_count = map(int, pattern_value.split(':'))
        odd_numbers = [n for n in range(1, 46) if n % 2 == 1]
        even_numbers = [n for n in range(1, 46) if n % 2 == 0]

        selected_odd = random.sample(odd_numbers, odd_count)
        selected_even = random.sample(even_numbers, even_count)

        return sorted(selected_odd + selected_even)

    def _generate_with_high_low_pattern(self, pattern_value):
        """
        고저 패턴에 맞는 번호 생성

        Args:
            pattern_value (str): '고:저' 형태의 비율 (예: '4:2')
        """
        high_count, low_count = map(int, pattern_value.split(':'))
        high_boundary = self.config.TREND_CRITERIA['high_low_ratio']['high_boundary']
        high_numbers = [n for n in range(high_boundary, 46)]
        low_numbers = [n for n in range(1, high_boundary)]

        selected_high = random.sample(high_numbers, high_count)
        selected_low = random.sample(low_numbers, low_count)

        return sorted(selected_high + selected_low)

    def _generate_with_diagonal_pattern(self, intersection_count):
        """
        대각선 교차점을 포함한 번호 생성

        Args:
            intersection_count (int): 포함할 대각선 교차점 개수
        """
        # 대각선 패턴 정의
        main_diagonals = [set(diag) for diag in self.config.DIAGONAL_PATTERNS['주대각선']]
        anti_diagonals = [set(diag) for diag in self.config.DIAGONAL_PATTERNS['부대각선']]
        all_diagonals = main_diagonals + anti_diagonals

        # 랜덤으로 대각선 선택
        selected_diagonals = random.sample(all_diagonals, min(intersection_count, len(all_diagonals)))

        # 각 대각선에서 최소 2개 번호 선택
        selected_numbers = set()
        for diagonal in selected_diagonals:
            # 이미 선택된 번호 제외
            available = [n for n in diagonal if n not in selected_numbers]
            # 최소 2개 선택
            count = min(2, len(available))
            if count > 0:
                selected_numbers.update(random.sample(available, count))

        # 나머지 번호 랜덤 생성
        remaining_count = 6 - len(selected_numbers)
        if remaining_count > 0:
            remaining_pool = [n for n in range(1, 46) if n not in selected_numbers]
            selected_numbers.update(random.sample(remaining_pool, remaining_count))

        return sorted(selected_numbers)

    def _generate_with_corner_pattern(self, corner_count):
        """
        모서리 번호를 포함한 번호 생성

        Args:
            corner_count (int): 포함할 모서리 번호 개수
        """
        # 모든 모서리 번호 합치기
        all_corner_numbers = []
        for corner_nums in self.config.CORNER_NUMBERS.values():
            all_corner_numbers.extend(corner_nums)

        # 랜덤으로 모서리 번호 선택
        selected_corners = random.sample(all_corner_numbers, min(corner_count, len(all_corner_numbers)))

        # 나머지 번호 랜덤 생성
        remaining_count = 6 - len(selected_corners)
        remaining_pool = [n for n in range(1, 46) if n not in selected_corners]
        selected_numbers = selected_corners + random.sample(remaining_pool, remaining_count)

        return sorted(selected_numbers)

    def _generate_with_hot_cold_pattern(self, hot_count, cold_count):
        """
        핫-콜드 번호 패턴에 맞는 번호 생성

        Args:
            hot_count (int): 포함할 핫 번호 개수
            cold_count (int): 포함할 콜드 번호 개수
        """
        hot_numbers = self.config.HOT_COLD_SETTINGS['hot_numbers']
        cold_numbers = self.config.HOT_COLD_SETTINGS['cold_numbers']
        normal_numbers = self.config.HOT_COLD_SETTINGS['normal_numbers']

        selected_hot = random.sample(hot_numbers, min(hot_count, len(hot_numbers)))
        selected_cold = random.sample(cold_numbers, min(cold_count, len(cold_numbers)))

        # 나머지 번호는 normal에서 선택
        remaining_count = 6 - len(selected_hot) - len(selected_cold)
        remaining_pool = [n for n in normal_numbers if n not in selected_hot and n not in selected_cold]

        # normal 풀이 부족하면 전체 범위에서 선택
        if len(remaining_pool) < remaining_count:
            remaining_pool = [n for n in range(1, 46) if n not in selected_hot and n not in selected_cold]

        selected_normal = random.sample(remaining_pool, remaining_count)

        return sorted(selected_hot + selected_cold + selected_normal)


def main():
    # 사용 예시
    db_path = "lotto.db"  # SQLite DB 파일 경로
    generator = LottoGenerator(db_path)

    # 게임 수 입력 받기
    while True:
        try:
            num_games = int(input("생성할 게임 수를 입력하세요 (1-20): "))
            if 1 <= num_games <= 20:
                break
            print("1에서 20 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("올바른 숫자를 입력해주세요.")

    # 트렌드 점수 사용 여부 선택
    while True:
        use_trend = input("최근 트렌드를 반영한 번호를 생성하시겠습니까? (Y/N): ").upper()
        if use_trend in ['Y', 'N']:
            use_trend = (use_trend == 'Y')
            break
        print("Y 또는 N으로 입력해주세요.")

    # 생성 방식 선택
    generation_method = 1  # 기본 생성 방식
    if use_trend:
        print("\n생성 방식을 선택해주세요:")
        print("1. 기본 트렌드 기반 생성")
        print("2. 이전 당첨번호 포함 생성")
        print("3. 홀짝 패턴 기반 생성 (4:2 비율)")
        print("4. 고저 패턴 기반 생성 (4:2 비율)")
        print("5. 대각선 패턴 기반 생성 (2개 이상 교차점)")
        print("6. 모서리 패턴 기반 생성 (3개 모서리)")
        print("7. 핫-콜드 패턴 기반 생성 (3:1 비율)")

        while True:
            try:
                generation_method = int(input("\n방식 선택 (1-7): "))
                if 1 <= generation_method <= 7:
                    break
                print("1에서 7 사이의 숫자를 입력해주세요.")
            except ValueError:
                print("올바른 숫자를 입력해주세요.")

    # 선택한 생성 방식에 따라 번호 생성
    combinations = []

    if generation_method == 1:
        combinations = generator.generate_numbers(num_games, use_trend)
    elif generation_method == 2:
        combinations = generator.generate_numbers_with_previous(num_games, use_trend)
    elif generation_method == 3:
        combinations = generator.generate_numbers_with_pattern(num_games, 'odd_even', '4:2')
    elif generation_method == 4:
        combinations = generator.generate_numbers_with_pattern(num_games, 'high_low', '4:2')
    elif generation_method == 5:
        combinations = generator.generate_numbers_with_pattern(num_games, 'diagonal', '2')
    elif generation_method == 6:
        combinations = generator.generate_numbers_with_pattern(num_games, 'corner', '3')
    elif generation_method == 7:
        combinations = generator.generate_numbers_with_pattern(num_games, 'hot_cold', '3:1')

    # 결과 출력
    if combinations:
        print(f"\n{num_games}개의 로또 번호 조합이 생성되었습니다:")
        if use_trend:
            for i, (numbers, score) in enumerate(combinations, 1):
                print(f"[{i}번] {numbers} (트렌드 점수: {score:.2f})")
        else:
            for i, numbers in enumerate(combinations, 1):
                print(f"[{i}번] {numbers}")
    else:
        print("\n설정된 기준을 만족하는 번호 조합을 찾지 못했습니다.")
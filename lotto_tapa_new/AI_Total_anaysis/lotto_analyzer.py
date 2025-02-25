import random
from itertools import combinations


class LottoAnalyzer:
    """
    로또 번호 생성 및 검증을 위한 분석기 클래스
    12가지 규칙을 기반으로 로또 번호의 유효성을 검사하고 생성합니다.
    """

    def __init__(self, config):
        """
        LottoAnalyzer 초기화

        Args:
            config: 분석 규칙 설정값을 포함하는 설정 객체
        """
        self.config = config
        # 소수 집합 (1과 자신으로만 나누어지는 수)
        self.prime_numbers = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}
        # 합성수 집합 (소수와 3의 배수를 제외한 수)
        self.composite_numbers = {1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44}

        # 로또용지의 모서리 패턴 정의 (7x6 행렬 기준)
        self.corner_patterns = {
            'top_left': {1, 2, 8, 9},  # 좌측 상단 모서리
            'top_right': {6, 7, 13, 14},  # 우측 상단 모서리
            'bottom_left': {29, 30, 36, 37},  # 좌측 하단 모서리
            'bottom_right': {34, 35, 41, 42}  # 우측 하단 모서리
        }
        # 전체 모서리 숫자 집합
        self.corner_numbers = set().union(*self.corner_patterns.values())
        # 제곱수 집합 (1, 4, 9, 16, 25, 36)
        self.perfect_squares = {1, 4, 9, 16, 25, 36}
        # 쌍수 집합 (11, 22, 33, 44)
        self.twin_numbers = {11, 22, 33, 44}

    def is_valid_combination(self, numbers):
        """
        주어진 로또 번호 조합이 모든 규칙을 만족하는지 검사

        Args:
            numbers: 검사할 6개의 로또 번호 리스트

        Returns:
            bool: 모든 규칙을 만족하면 True, 아니면 False
        """
        # 1. 총합 범위 검사 (100~175)
        if self.config.rules_enabled['sum_range']:
            if not (self.config.sum_range[0] <= sum(numbers) <= self.config.sum_range[1]):
                return False

        # 2. AC값 검사 (번호 간 차이값의 다양성)
        if self.config.rules_enabled['ac_value']:
            if self.calculate_ac_value(numbers) < self.config.ac_value_min:
                return False

        # 3. 홀짝 비율 검사
        if self.config.rules_enabled['odd_even']:
            odd_count = sum(1 for n in numbers if n % 2)  # 홀수 개수 계산
            if (odd_count, 6 - odd_count) in self.config.odd_even_exclude:  # 제외할 비율 검사
                return False

        # 4. 고저 비율 검사 (23 기준)
        if self.config.rules_enabled['high_low']:
            high_count = sum(1 for n in numbers if n >= 23)  # 고번호(23 이상) 개수
            if (high_count, 6 - high_count) in self.config.high_low_exclude:
                return False

        # 5. 소수 개수 검사
        if self.config.rules_enabled['prime']:
            prime_count = sum(1 for n in numbers if n in self.prime_numbers)
            if not (self.config.prime_range[0] <= prime_count <= self.config.prime_range[1]):
                return False

        # 6. 합성수 개수 검사
        if self.config.rules_enabled['composite']:
            composite_count = sum(1 for n in numbers if n in self.composite_numbers)
            if not (self.config.composite_range[0] <= composite_count <= self.config.composite_range[1]):
                return False

        # 7. 끝수 총합 검사
        if self.config.rules_enabled['last_digit']:
            # 각 번호의 일의 자리 숫자 합 계산
            last_digit_sum = sum(n % 10 if n > 9 else n for n in numbers)
            if not (self.config.last_digit_sum_range[0] <= last_digit_sum <= self.config.last_digit_sum_range[1]):
                return False

        # 8. 3의 배수와 5의 배수 개수 검사
        if self.config.rules_enabled['multiples']:
            mult_3_count = sum(1 for n in numbers if n % 3 == 0)  # 3의 배수 개수
            mult_5_count = sum(1 for n in numbers if n % 5 == 0)  # 5의 배수 개수
            if not (self.config.multiples_of_3_range[0] <= mult_3_count <= self.config.multiples_of_3_range[1]):
                return False
            if not (self.config.multiples_of_5_range[0] <= mult_5_count <= self.config.multiples_of_5_range[1]):
                return False

        # 9. 제곱수 개수 검사
        if self.config.rules_enabled['perfect_square']:
            square_count = sum(1 for n in numbers if n in self.perfect_squares)
            if not (self.config.perfect_square_range[0] <= square_count <= self.config.perfect_square_range[1]):
                return False

        # 10. 연속된 숫자 검사
        if self.config.rules_enabled['consecutive']:
            sorted_numbers = sorted(numbers)
            # 연속된 숫자 쌍의 개수 계산
            consecutive_pairs = sum(1 for i in range(len(sorted_numbers) - 1)
                                    if sorted_numbers[i + 1] - sorted_numbers[i] == 1)
            if consecutive_pairs not in self.config.consecutive_numbers:
                return False

        # 11. 쌍수(11,22,33,44) 개수 검사
        if self.config.rules_enabled['twin']:
            twin_count = sum(1 for n in numbers if n in self.twin_numbers)
            if not (self.config.twin_numbers_range[0] <= twin_count <= self.config.twin_numbers_range[1]):
                return False

        # 12. 모서리 패턴 검사
        if self.config.rules_enabled['corner']:
            # 전체 모서리 숫자 개수 확인
            corner_count = sum(1 for n in numbers if n in self.corner_numbers)
            if not (self.config.corner_numbers_range[0] <= corner_count <= self.config.corner_numbers_range[1]):
                return False

            # 각 모서리 영역별 숫자 분포 계산
            corner_distribution = {
                corner: sum(1 for n in numbers if n in number_set)
                for corner, number_set in self.corner_patterns.items()
            }

            # 한 모서리에 숫자가 몰리지 않도록 검사
            if max(corner_distribution.values()) > self.config.corner_max_per_side:
                return False

            # 대각선 방향 모서리의 균형 검사
            diagonal1 = sum(corner_distribution[c] for c in ['top_left', 'bottom_right'])
            diagonal2 = sum(corner_distribution[c] for c in ['top_right', 'bottom_left'])
            if abs(diagonal1 - diagonal2) > self.config.corner_diagonal_diff:
                return False

        # 모든 규칙을 통과한 경우
        return True

    def calculate_ac_value(self, numbers):
        """
        AC값 계산 (Arithmetic Complexity)
        주어진 번호들 간의 차이값의 다양성을 측정

        Args:
            numbers: 6개의 로또 번호 리스트

        Returns:
            int: 고유한 차이값의 개수 - 5
        """
        differences = set()  # 중복 제거를 위해 set 사용
        for i, j in combinations(sorted(numbers), 2):
            differences.add(j - i)  # 모든 가능한 두 수의 차이 계산
        return len(differences) - 5  # 총 차이값 개수에서 5를 뺀 값 반환

    def generate_numbers(self):
        """
        설정된 규칙에 맞는 로또 번호 조합을 생성

        Returns:
            list: 생성된 로또 번호 조합들의 리스트
                 각 조합은 오름차순으로 정렬된 6개의 숫자
        """
        valid_combinations = []
        max_attempts = 10000  # 무한 루프 방지를 위한 최대 시도 횟수
        attempts = 0

        while len(valid_combinations) < self.config.games_count and attempts < max_attempts:
            # 1~45 사이의 숫자 중 6개를 무작위로 선택
            numbers = sorted(random.sample(range(1, 46), 6))
            # 모든 규칙을 만족하는 경우에만 추가
            if self.is_valid_combination(numbers):
                valid_combinations.append(numbers)
            attempts += 1

        return valid_combinations
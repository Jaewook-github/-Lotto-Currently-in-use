# lotto_generator.py

import random
from collections import Counter
from config import LottoConfig
from lotto_analyzer import LottoAnalyzer


class LottoGenerator:
    def __init__(self, db_path):
        self.config = LottoConfig()
        self.analyzer = LottoAnalyzer(db_path)

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

        return True

    def generate_numbers(self, num_games=1):
        """설정된 기준에 맞는 로또 번호 조합을 생성하는 함수"""
        valid_combinations = []
        total_attempts = 0
        max_attempts = num_games * 1000  # 최대 시도 횟수 설정

        while len(valid_combinations) < num_games and total_attempts < max_attempts:
            # 번호 랜덤 생성
            numbers = sorted(random.sample(range(1, 46), 6))

            # 생성된 번호가 기준에 맞는지 검증
            if self.validate_combination(numbers) and numbers not in valid_combinations:
                valid_combinations.append(numbers)

            total_attempts += 1

        return valid_combinations


def main():
    # 사용 예시
    db_path = "lotto.db"  # SQLite DB 파일 경로
    generator = LottoGenerator(db_path)

    # 게임 수 입력 받기
    while True:
        try:
            num_games = int(input("생성할 게임 수를 입력하세요 (1-5): "))
            if 1 <= num_games <= 5:
                break
            print("1에서 5 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("올바른 숫자를 입력해주세요.")

    # 번호 생성
    combinations = generator.generate_numbers(num_games)

    # 결과 출력
    if combinations:
        print(f"\n{num_games}개의 로또 번호 조합이 생성되었습니다:")
        for i, numbers in enumerate(combinations, 1):
            print(f"[{i}번] {numbers}")
    else:
        print("\n설정된 기준을 만족하는 번호 조합을 찾지 못했습니다.")


if __name__ == "__main__":
    main()
# test_analyzer.py

from lotto_analyzer import LottoAnalyzer
from config import LottoConfig


class LottoTestAnalyzer:
    def __init__(self, db_path="lotto.db"):
        self.analyzer = LottoAnalyzer(db_path)
        self.config = LottoConfig()

    def analyze_number_combination(self, numbers):
        """번호 조합 분석"""
        # 기본 분석 수행
        sorted_numbers = sorted(numbers)
        results = self.analyzer.analyze_single_numbers(sorted_numbers)

        # 추가 분석 수행
        analysis = {}

        # 1. 기본 정보
        analysis['기본 정보'] = {
            '번호': sorted_numbers,
            '합계': f"{sum(numbers)} (기준: {self.config.FILTER_CRITERIA['sum_range']['min']}-{self.config.FILTER_CRITERIA['sum_range']['max']})",
            'AC 값': f"{results['ac_value']} (기준: {self.config.FILTER_CRITERIA['ac_range']['min']}-{self.config.FILTER_CRITERIA['ac_range']['max']})"
        }

        # 2. 패턴 분석
        odd_count = len([x for x in numbers if x % 2 == 1])
        even_count = 6 - odd_count
        low_count = len([x for x in numbers if x <= 22])
        high_count = 6 - low_count

        analysis['패턴 분석'] = {
            '홀짝 비율': f"{odd_count}:{even_count}",
            '고저 비율': f"{low_count}:{high_count}",
            '연속된 번호': f"{results['consecutive_groups'] if results['consecutive_groups'] else '없음'}",
            '모서리 번호 개수': results['corner_count']
        }

        # 3. 구간 분석
        sections = [0] * 5  # 1-10, 11-20, 21-30, 31-40, 41-45
        for num in sorted_numbers:
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

        section_desc = f"""구간별 번호 개수:
        - 1-10:  {sections[0]}개
        - 11-20: {sections[1]}개
        - 21-30: {sections[2]}개
        - 31-40: {sections[3]}개
        - 41-45: {sections[4]}개"""

        analysis['구간 분석'] = {
            '구간별 번호 분포': section_desc,
            '구간별 제한 검증': f"각 구간 {self.config.FILTER_CRITERIA['section_numbers']['min']}-{self.config.FILTER_CRITERIA['section_numbers']['max']}개 제한: {'만족' if all(self.config.FILTER_CRITERIA['section_numbers']['min'] <= x <= self.config.FILTER_CRITERIA['section_numbers']['max'] for x in sections) else '위반'}"
        }

        # 4. 색상 분석
        analysis['색상 분석'] = {
            '사용된 색상 수': f"{results['color_count']} (기준: {self.config.FILTER_CRITERIA['colors']['min']}-{self.config.FILTER_CRITERIA['colors']['max']})",
            '색상 조합': results['color_combination']
        }

        # 5. 수학적 특성
        analysis['수학적 특성'] = {
            '소수 개수': f"{results['prime_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['min']}-{self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['max']})",
            '합성수 개수': f"{results['composite_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['composite_numbers']['min']}-{self.config.FILTER_CRITERIA['number_counts']['composite_numbers']['max']})",
            '완전제곱수 개수': results['perfect_square_count'],
            '동형수 그룹 개수': results['mirror_number_count']
        }

        # 6. 배수 특성
        analysis['배수 특성'] = {
            '3의 배수 개수': f"{results['multiples_3_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['multiples_of_3']['min']}-{self.config.FILTER_CRITERIA['number_counts']['multiples_of_3']['max']})",
            '4의 배수 개수': f"{results['multiples_4_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['multiples_of_4']['min']}-{self.config.FILTER_CRITERIA['number_counts']['multiples_of_4']['max']})",
            '5의 배수 개수': f"{results['multiples_5_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['multiples_of_5']['min']}-{self.config.FILTER_CRITERIA['number_counts']['multiples_of_5']['max']})"
        }

        # 7. 끝수 분석
        last_digits = [num % 10 for num in sorted_numbers]
        analysis['끝수 분석'] = {
            '끝수합': f"{results['last_digit_sum']} (기준: {self.config.FILTER_CRITERIA['last_digit_sum']['min']}-{self.config.FILTER_CRITERIA['last_digit_sum']['max']})",
            '끝수 구성': last_digits,
            '회문수 개수': results['palindrome_count'],
            '쌍수 개수': f"{results['double_number_count']} (기준: {self.config.FILTER_CRITERIA['number_counts']['double_numbers']['min']}-{self.config.FILTER_CRITERIA['number_counts']['double_numbers']['max']})"
        }

        return analysis

    def check_criteria_violations(self, numbers):
        """기준 위반 사항 체크"""
        results = self.analyzer.analyze_single_numbers(numbers)
        violations = []

        # 1. 합계 검증
        total_sum = sum(numbers)
        if not (self.config.FILTER_CRITERIA['sum_range']['min'] <= total_sum <=
                self.config.FILTER_CRITERIA['sum_range']['max']):
            violations.append(f"총합 {total_sum}이 {self.config.FILTER_CRITERIA['sum_range']['min']}-"
                              f"{self.config.FILTER_CRITERIA['sum_range']['max']} 범위를 벗어남")

        # 2. AC값 검증
        if not (self.config.FILTER_CRITERIA['ac_range']['min'] <= results['ac_value'] <=
                self.config.FILTER_CRITERIA['ac_range']['max']):
            violations.append(f"AC값 {results['ac_value']}이 {self.config.FILTER_CRITERIA['ac_range']['min']}-"
                              f"{self.config.FILTER_CRITERIA['ac_range']['max']} 범위를 벗어남")

        # 3. 색상 개수 검증
        if not (self.config.FILTER_CRITERIA['colors']['min'] <= results['color_count'] <=
                self.config.FILTER_CRITERIA['colors']['max']):
            violations.append(f"색상 개수 {results['color_count']}개가 {self.config.FILTER_CRITERIA['colors']['min']}-"
                              f"{self.config.FILTER_CRITERIA['colors']['max']} 범위를 벗어남")

        # 4. 소수 개수 검증
        if not (self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['min'] <= results['prime_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['max']):
            violations.append(f"소수 개수 {results['prime_count']}개가 "
                              f"{self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['min']}-"
                              f"{self.config.FILTER_CRITERIA['number_counts']['prime_numbers']['max']} 범위를 벗어남")

        # 5. 끝수합 검증
        if not (self.config.FILTER_CRITERIA['last_digit_sum']['min'] <= results['last_digit_sum'] <=
                self.config.FILTER_CRITERIA['last_digit_sum']['max']):
            violations.append(f"끝수합 {results['last_digit_sum']}이 "
                              f"{self.config.FILTER_CRITERIA['last_digit_sum']['min']}-"
                              f"{self.config.FILTER_CRITERIA['last_digit_sum']['max']} 범위를 벗어남")

        # 모서리 번호 개수 검증
        if not (self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['min'] <= results['corner_count'] <=
                self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['max']):
            violations.append(f"모서리 번호 개수 {results['corner_count']}개가 "
                              f"{self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['min']}-"
                              f"{self.config.FILTER_CRITERIA['number_counts']['corner_numbers']['max']} "
                              f"범위를 벗어남")
        for multiples_type, count_key in [
            ('multiples_of_3', 'multiples_3_count'),
            ('multiples_of_4', 'multiples_4_count'),
            ('multiples_of_5', 'multiples_5_count')
        ]:
            if not (self.config.FILTER_CRITERIA['number_counts'][multiples_type]['min'] <=
                    results[count_key] <=
                    self.config.FILTER_CRITERIA['number_counts'][multiples_type]['max']):
                violations.append(f"{multiples_type.replace('_', ' ')} 개수 {results[count_key]}개가 "
                                  f"{self.config.FILTER_CRITERIA['number_counts'][multiples_type]['min']}-"
                                  f"{self.config.FILTER_CRITERIA['number_counts'][multiples_type]['max']} "
                                  f"범위를 벗어남")

        return violations


def main():
    """메인 테스트 함수"""
    # 테스트할 번호 조합들
    test_combinations = [
        [4, 7, 8, 13, 33, 42],
        [4, 19, 20, 21, 35, 39],
        [2, 8, 19, 28, 30, 43],
        [6, 12, 24, 31, 35, 43],
        [10, 17, 21, 26, 30, 43],
        [4, 13, 25, 35, 39, 42],
        [3, 4, 29, 35, 44, 45],
        [9, 13, 15, 27, 43, 44],
        [7, 9, 21, 39, 40, 44],
        [7, 8, 12, 13, 23, 39]
    ]

    # 분석기 초기화
    test_analyzer = LottoTestAnalyzer()

    # 각 조합 분석
    for i, numbers in enumerate(test_combinations, 1):
        print(f"\n{'=' * 30} 조합 {i} 분석 {'=' * 30}")

        # 상세 분석
        analysis = test_analyzer.analyze_number_combination(numbers)
        for category, details in analysis.items():
            print(f"\n[{category}]")
            for key, value in details.items():
                print(f"{key}: {value}")

        # 기준 위반 사항
        violations = test_analyzer.check_criteria_violations(numbers)
        if violations:
            print("\n[기준 위반 사항]")
            for violation in violations:
                print(f"- {violation}")


if __name__ == "__main__":
    print("\n로또 번호 분석을 시작합니다...")
    main()
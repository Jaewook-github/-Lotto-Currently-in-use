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

    def analyze_numbers(self, draw_numbers=None):
        """로또 번호 종합 분석 함수"""
        if draw_numbers:
            # 단일 회차 분석
            self.results = self._analyze_single_draw(draw_numbers)
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
                self._analyze_single_draw(numbers)

            conn.close()

        self._create_frequency_dataframes()
        self._calculate_total_statistics()
        return self.freq_dfs, self.stats_df

    def _analyze_single_draw(self, draw_numbers):
        """단일 회차 분석"""
        results = {}

        # 모서리 번호 분석
        all_corner_numbers = []
        for corner_nums in self.config.CORNER_NUMBERS.values():
            all_corner_numbers.extend(corner_nums)
        corner_count = len(set(draw_numbers).intersection(set(all_corner_numbers)))

        # 나머지 분석 수행
        ac_value = self.calculate_ac(draw_numbers)
        consecutive_groups = self.find_consecutive_numbers(draw_numbers)
        color_count = self.analyze_color_pattern(draw_numbers)

        if hasattr(self, 'results') and self.results:
            # 전체 회차 분석 중인 경우
            self.results['corner_results'].append(corner_count)
            self.results['ac_results'].append(ac_value)
            if consecutive_groups:
                for group in consecutive_groups:
                    self.results['consecutive_patterns'].append(len(group))
            self.results['color_patterns'].append(len(color_count))
            # 색상 조합을 문자열로 변환 (정렬된 상태로)
            color_combination = "-".join(
                f"{color}:{count}" for color, count in
                sorted(color_count.items(), key=lambda x: x[0] if x[0] is not None else "")
            )
            self.results['color_combinations'].append(color_combination)
            self.results['composite_counts'].append(self.count_composite_numbers(draw_numbers))
            self.results['perfect_square_counts'].append(self.count_perfect_squares(draw_numbers))
            self.results['mirror_number_counts'].append(self.get_mirror_number_count(draw_numbers))
            self.results['multiples_3_counts'].append(
                self.count_multiples(draw_numbers, self.config.MULTIPLES['3의 배수']))
            self.results['multiples_4_counts'].append(
                self.count_multiples(draw_numbers, self.config.MULTIPLES['4의 배수']))
            self.results['multiples_5_counts'].append(
                self.count_multiples(draw_numbers, self.config.MULTIPLES['5의 배수']))
            self.results['prime_counts'].append(self.count_prime_numbers(draw_numbers))
            self.results['last_digit_sums'].append(self.calculate_last_digit_sum(draw_numbers))
            self.results['palindrome_counts'].append(self.count_palindrome_numbers(draw_numbers))
            self.results['double_number_counts'].append(self.count_double_numbers(draw_numbers))
        else:
            # 단일 회차 분석인 경우
            results = {
                'corner_count': corner_count,
                'ac_value': ac_value,
                'consecutive_groups': consecutive_groups,
                'color_count': len(color_count),
                'color_combination': "-".join(f"{color}:{count}" for color, count in sorted(color_count.items())),
                'composite_count': self.count_composite_numbers(draw_numbers),
                'perfect_square_count': self.count_perfect_squares(draw_numbers),
                'mirror_number_count': self.get_mirror_number_count(draw_numbers),
                'multiples_3_count': self.count_multiples(draw_numbers, self.config.MULTIPLES['3의 배수']),
                'multiples_4_count': self.count_multiples(draw_numbers, self.config.MULTIPLES['4의 배수']),
                'multiples_5_count': self.count_multiples(draw_numbers, self.config.MULTIPLES['5의 배수']),
                'prime_count': self.count_prime_numbers(draw_numbers),
                'last_digit_sum': self.calculate_last_digit_sum(draw_numbers),
                'palindrome_count': self.count_palindrome_numbers(draw_numbers),
                'double_number_count': self.count_double_numbers(draw_numbers)
            }
            return results

    def _create_frequency_dataframes(self):
        """빈도 분석 데이터프레임 생성"""
        self.freq_dfs = {
            'corner_freq': pd.DataFrame(pd.Series(self.results['corner_results']).value_counts().sort_index()),
            'ac_freq': pd.DataFrame(pd.Series(self.results['ac_results']).value_counts().sort_index()),
            'consec_freq': pd.DataFrame(pd.Series(self.results['consecutive_patterns']).value_counts().sort_index()),
            'color_freq': pd.DataFrame(pd.Series(self.results['color_patterns']).value_counts().sort_index()),
            'color_comb_freq': pd.DataFrame(pd.Series(self.results['color_combinations']).value_counts().head(10)),
            'composite_freq': pd.DataFrame(pd.Series(self.results['composite_counts']).value_counts().sort_index()),
            'perfect_square_freq': pd.DataFrame(
                pd.Series(self.results['perfect_square_counts']).value_counts().sort_index()),
            'mirror_number_freq': pd.DataFrame(
                pd.Series(self.results['mirror_number_counts']).value_counts().sort_index()),
            'multiples_3_freq': pd.DataFrame(pd.Series(self.results['multiples_3_counts']).value_counts().sort_index()),
            'multiples_4_freq': pd.DataFrame(pd.Series(self.results['multiples_4_counts']).value_counts().sort_index()),
            'multiples_5_freq': pd.DataFrame(pd.Series(self.results['multiples_5_counts']).value_counts().sort_index()),
            'prime_freq': pd.DataFrame(pd.Series(self.results['prime_counts']).value_counts().sort_index()),
            'last_digit_sum_freq': pd.DataFrame(pd.Series(self.results['last_digit_sums']).value_counts().sort_index()),
            'palindrome_freq': pd.DataFrame(pd.Series(self.results['palindrome_counts']).value_counts().sort_index()),
            'double_number_freq': pd.DataFrame(
                pd.Series(self.results['double_number_counts']).value_counts().sort_index())
        }

        # 데이터프레임 이름 설정
        names = {
            'corner_freq': '모서리 번호 개수',
            'ac_freq': 'AC 값',
            'consec_freq': '연속 번호 개수',
            'color_freq': '사용된 색상 수',
            'color_comb_freq': '색상 조합 패턴',
            'composite_freq': '합성수 개수',
            'perfect_square_freq': '완전제곱수 개수',
            'mirror_number_freq': '동형수 그룹 개수',
            'multiples_3_freq': '3의 배수 개수',
            'multiples_4_freq': '4의 배수 개수',
            'multiples_5_freq': '5의 배수 개수',
            'prime_freq': '소수 개수',
            'last_digit_sum_freq': '끝수합',
            'palindrome_freq': '회문수 개수',
            'double_number_freq': '쌍수 개수'
        }

        # 각 데이터프레임 형식 설정
        for key, df in self.freq_dfs.items():
            df.columns = ['출현 횟수']
            df.index.name = names[key]
            df['비율(%)'] = (df['출현 횟수'] / len(self.results['corner_results']) * 100).round(2)

    def _calculate_total_statistics(self):
        """전체 통계 계산"""
        self.stats_df = pd.DataFrame({
            '분석 항목': [
                '평균 모서리 번호',
                '최대 모서리 번호',
                '최소 모서리 번호',
                '평균 AC 값',
                '최대 AC 값',
                '최소 AC 값',
                '평균 사용 색상 수',
                '평균 합성수 개수',
                '평균 완전제곱수 개수',
                '평균 동형수 그룹 개수',
                '평균 3의 배수 개수',
                '평균 4의 배수 개수',
                '평균 5의 배수 개수',
                '평균 소수 개수',
                '평균 끝수합',
                '최대 끝수합',
                '최소 끝수합',
                '평균 회문수 개수',
                '최대 회문수 개수',
                '평균 쌍수 개수',
                '최대 쌍수 개수',
                '연속 번호 패턴 출현 회차 수',
                '총 분석 회차'
            ],
            '값': [
                round(np.mean(self.results['corner_results']), 2),
                max(self.results['corner_results']),
                min(self.results['corner_results']),
                round(np.mean(self.results['ac_results']), 2),
                max(self.results['ac_results']),
                min(self.results['ac_results']),
                round(np.mean(self.results['color_patterns']), 2),
                round(np.mean(self.results['composite_counts']), 2),
                round(np.mean(self.results['perfect_square_counts']), 2),
                round(np.mean(self.results['mirror_number_counts']), 2),
                round(np.mean(self.results['multiples_3_counts']), 2),
                round(np.mean(self.results['multiples_4_counts']), 2),
                round(np.mean(self.results['multiples_5_counts']), 2),
                round(np.mean(self.results['prime_counts']), 2),
                round(np.mean(self.results['last_digit_sums']), 2),
                max(self.results['last_digit_sums']),
                min(self.results['last_digit_sums']),
                round(np.mean(self.results['palindrome_counts']), 2),
                max(self.results['palindrome_counts']),
                round(np.mean(self.results['double_number_counts']), 2),
                max(self.results['double_number_counts']),
                len([x for x in self.results['consecutive_patterns'] if x >= 2]),
                len(self.results['corner_results'])
            ]
        })

    def get_frequency_analysis(self):
        """빈도 분석 결과 반환"""
        if self.freq_dfs is None:
            self.analyze_numbers()
        return self.freq_dfs

    def get_total_statistics(self):
        """전체 통계 결과 반환"""
        if self.stats_df is None:
            self.analyze_numbers()
        return self.stats_df

    def print_analysis_results(self):
        """분석 결과 출력"""
        if self.freq_dfs is None or self.stats_df is None:
            self.analyze_numbers()

        # 테이블 제목 정의
        table_titles = {
            'corner_freq': '모서리 번호 출현 빈도 분석',
            'ac_freq': 'AC 값 빈도 분석',
            'consec_freq': '연속된 번호 패턴 분석',
            'color_freq': '색상 개수 분포 분석',
            'color_comb_freq': '상위 10개 색상 조합 패턴',
            'composite_freq': '합성수 개수 분포 분석',
            'perfect_square_freq': '완전제곱수 개수 분포 분석',
            'mirror_number_freq': '동형수 그룹 개수 분포 분석',
            'multiples_3_freq': '3의 배수 개수 분포 분석',
            'multiples_4_freq': '4의 배수 개수 분포 분석',
            'multiples_5_freq': '5의 배수 개수 분포 분석',
            'prime_freq': '소수 개수 분포 분석',
            'last_digit_sum_freq': '끝수합 분포 분석',
            'palindrome_freq': '회문수 개수 분포 분석',
            'double_number_freq': '쌍수 개수 분포 분석'
        }

        # 결과 출력
        for key, title in table_titles.items():
            print(f"\n=== {title} ===")
            print(self.freq_dfs[key].to_string())

        print("\n=== 전체 통계 ===")
        print(self.stats_df.to_string(index=False))

    def analyze_single_numbers(self, numbers):
        """단일 번호 조합 분석"""
        results = self._analyze_single_draw(numbers)

        # 분석 결과 출력 형식 정의
        format_dict = {
            'corner_count': '모서리 번호 개수',
            'ac_value': 'AC 값',
            'consecutive_groups': '연속된 번호',
            'color_count': '사용된 색상 수',
            'color_combination': '색상 조합',
            'composite_count': '합성수 개수',
            'perfect_square_count': '완전제곱수 개수',
            'mirror_number_count': '동형수 그룹 개수',
            'multiples_3_count': '3의 배수 개수',
            'multiples_4_count': '4의 배수 개수',
            'multiples_5_count': '5의 배수 개수',
            'prime_count': '소수 개수',
            'last_digit_sum': '끝수합',
            'palindrome_count': '회문수 개수',
            'double_number_count': '쌍수 개수'
        }

        # 결과를 보기 좋게 출력
        print("\n=== 번호 조합 분석 결과 ===")
        for key, name in format_dict.items():
            if key == 'consecutive_groups':
                consec_str = []
                for group in results[key]:
                    consec_str.append('->'.join(map(str, group)))
                print(f"{name}: {', '.join(consec_str) if consec_str else '없음'}")
            else:
                print(f"{name}: {results[key]}")

        return results


def main():
    """메인 실행 함수"""
    analyzer = LottoAnalyzer("lotto.db")
    analyzer.print_analysis_results()


if __name__ == "__main__":
    main()
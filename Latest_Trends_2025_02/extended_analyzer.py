# extended_analyzer.py

import sqlite3
import pandas as pd
import numpy as np
from collections import Counter
from config import LottoConfig
from lotto_analyzer import LottoAnalyzer


class ExtendedLottoAnalyzer(LottoAnalyzer):
    def __init__(self, db_path):
        """
        확장된 로또 분석기 초기화
        Args:
            db_path (str): SQLite DB 파일 경로
        """
        super().__init__(db_path)
        self.recent_results = None
        self.recent_freq_dfs = None
        self.recent_stats_df = None
        self.diagonal_patterns = None

    def get_high_low_ratio(self, numbers):
        """
        고저 비율을 계산하는 함수 (1-23: 저번호, 24-45: 고번호)
        """
        low_count = len([x for x in numbers if x <= 23])
        high_count = 6 - low_count
        return f"{low_count}:{high_count}"

    def get_odd_even_ratio(self, numbers):
        """
        홀짝 비율을 계산하는 함수
        """
        odd_count = len([x for x in numbers if x % 2 == 1])
        even_count = 6 - odd_count
        return f"{odd_count}:{even_count}"

    def calculate_sum(self, numbers):
        """
        번호 합계를 계산하는 함수
        """
        return sum(numbers)

    def calculate_std_deviation(self, numbers):
        """
        표준편차를 계산하는 함수 (번호 분산도)
        """
        return round(np.std(numbers), 2)

    def calculate_average_gap(self, numbers):
        """
        평균 간격을 계산하는 함수
        """
        sorted_nums = sorted(numbers)
        gaps = [sorted_nums[i] - sorted_nums[i - 1] for i in range(1, len(sorted_nums))]
        return round(np.mean(gaps), 2)

    def check_diagonal_pattern(self, numbers):
        """
        대각선 매칭 패턴을 확인하는 함수

        대각선 정의:
        - 주대각선: (1,9,17,25,33,41), (2,10,18,26,34,42), ..., (5,13,21,29,37,45)
        - 부대각선: (5,11,17,23,29,35,41), (4,10,16,22,28,34,40), ..., (1,7,13,19,25,31,37,43)
        """
        # 주대각선 정의
        main_diagonals = []
        for start in range(1, 6):
            diagonal = [start + 8 * i for i in range(6) if start + 8 * i <= 45]
            main_diagonals.append(set(diagonal))

        # 부대각선 정의
        anti_diagonals = []
        for start in range(5, 0, -1):
            diagonal = [start + 6 * i for i in range(7) if start + 6 * i <= 45]
            anti_diagonals.append(set(diagonal))

        # 대각선 교차점 확인
        all_diagonals = main_diagonals + anti_diagonals
        numbers_set = set(numbers)

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

    def check_previous_draws_overlap(self, numbers, prev_count=5):
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

    def analyze_recent_draws(self, draw_count=100):
        """
        최근 n회차에 대한 분석 수행

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

        self.recent_results = {
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

            self.recent_results['draw_numbers'].append(row['draw_number'])
            self.recent_results['numbers'].append(numbers)
            self.recent_results['high_low_ratios'].append(self.get_high_low_ratio(numbers))
            self.recent_results['odd_even_ratios'].append(self.get_odd_even_ratio(numbers))
            self.recent_results['sums'].append(self.calculate_sum(numbers))
            self.recent_results['std_deviations'].append(self.calculate_std_deviation(numbers))
            self.recent_results['average_gaps'].append(self.calculate_average_gap(numbers))

            diagonal_result = self.check_diagonal_pattern(numbers)
            self.recent_results['diagonal_patterns'].append(diagonal_result['has_diagonal_pattern'])
            self.recent_results['diagonal_match_counts'].append(diagonal_result['diagonal_match_count'])

            # 기존 분석기 기능으로 분석
            results = self._analyze_single_draw(numbers)

            self.recent_results['corner_results'].append(results['corner_count'])
            self.recent_results['ac_results'].append(results['ac_value'])

            if results['consecutive_groups']:
                for group in results['consecutive_groups']:
                    self.recent_results['consecutive_patterns'].append(len(group))
            else:
                self.recent_results['consecutive_patterns'].append(0)  # 연속번호 없음

            self.recent_results['color_patterns'].append(results['color_count'])
            self.recent_results['color_combinations'].append(results['color_combination'])
            self.recent_results['composite_counts'].append(results['composite_count'])
            self.recent_results['perfect_square_counts'].append(results['perfect_square_count'])
            self.recent_results['mirror_number_counts'].append(results['mirror_number_count'])
            self.recent_results['multiples_3_counts'].append(results['multiples_3_count'])
            self.recent_results['multiples_4_counts'].append(results['multiples_4_count'])
            self.recent_results['multiples_5_counts'].append(results['multiples_5_count'])
            self.recent_results['prime_counts'].append(results['prime_count'])
            self.recent_results['last_digit_sums'].append(results['last_digit_sum'])
            self.recent_results['palindrome_counts'].append(results['palindrome_count'])
            self.recent_results['double_number_counts'].append(results['double_number_count'])

        self._create_recent_frequency_dataframes()
        self._calculate_recent_statistics()

        return self.recent_freq_dfs, self.recent_stats_df

    def _create_recent_frequency_dataframes(self):
        """최근 회차에 대한 빈도 분석 데이터프레임 생성"""
        self.recent_freq_dfs = {
            'high_low_ratio_freq': pd.DataFrame(
                pd.Series(self.recent_results['high_low_ratios']).value_counts().sort_index()),
            'odd_even_ratio_freq': pd.DataFrame(
                pd.Series(self.recent_results['odd_even_ratios']).value_counts().sort_index()),
            'sum_freq': pd.DataFrame(pd.Series(self.recent_results['sums']).value_counts().sort_index()),
            'std_deviation_freq': pd.DataFrame(
                pd.Series(self.recent_results['std_deviations']).round(0).value_counts().sort_index()),
            'average_gap_freq': pd.DataFrame(
                pd.Series(self.recent_results['average_gaps']).round(0).value_counts().sort_index()),
            'diagonal_pattern_freq': pd.DataFrame(pd.Series(self.recent_results['diagonal_patterns']).value_counts()),
            'diagonal_match_count_freq': pd.DataFrame(
                pd.Series(self.recent_results['diagonal_match_counts']).value_counts().sort_index()),
            'corner_freq': pd.DataFrame(pd.Series(self.recent_results['corner_results']).value_counts().sort_index()),
            'ac_freq': pd.DataFrame(pd.Series(self.recent_results['ac_results']).value_counts().sort_index()),
            'consec_freq': pd.DataFrame(
                pd.Series(self.recent_results['consecutive_patterns']).value_counts().sort_index()),
            'color_freq': pd.DataFrame(pd.Series(self.recent_results['color_patterns']).value_counts().sort_index()),
            'color_comb_freq': pd.DataFrame(
                pd.Series(self.recent_results['color_combinations']).value_counts().head(10)),
            'composite_freq': pd.DataFrame(
                pd.Series(self.recent_results['composite_counts']).value_counts().sort_index()),
            'perfect_square_freq': pd.DataFrame(
                pd.Series(self.recent_results['perfect_square_counts']).value_counts().sort_index()),
            'mirror_number_freq': pd.DataFrame(
                pd.Series(self.recent_results['mirror_number_counts']).value_counts().sort_index()),
            'multiples_3_freq': pd.DataFrame(
                pd.Series(self.recent_results['multiples_3_counts']).value_counts().sort_index()),
            'multiples_4_freq': pd.DataFrame(
                pd.Series(self.recent_results['multiples_4_counts']).value_counts().sort_index()),
            'multiples_5_freq': pd.DataFrame(
                pd.Series(self.recent_results['multiples_5_counts']).value_counts().sort_index()),
            'prime_freq': pd.DataFrame(pd.Series(self.recent_results['prime_counts']).value_counts().sort_index()),
            'last_digit_sum_freq': pd.DataFrame(
                pd.Series(self.recent_results['last_digit_sums']).value_counts().sort_index()),
            'palindrome_freq': pd.DataFrame(
                pd.Series(self.recent_results['palindrome_counts']).value_counts().sort_index()),
            'double_number_freq': pd.DataFrame(
                pd.Series(self.recent_results['double_number_counts']).value_counts().sort_index())
        }

        # 데이터프레임 이름 설정
        names = {
            'high_low_ratio_freq': '고저 비율',
            'odd_even_ratio_freq': '홀짝 비율',
            'sum_freq': '총합',
            'std_deviation_freq': '표준편차',
            'average_gap_freq': '평균 간격',
            'diagonal_pattern_freq': '대각선 패턴 존재 여부',
            'diagonal_match_count_freq': '대각선 교차점 개수',
            'corner_freq': '모서리 번호 개수',
            'ac_freq': 'AC 값',
            'consec_freq': '연속 번호 길이',
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
        total_count = len(self.recent_results['corner_results'])
        for key, df in self.recent_freq_dfs.items():
            df.columns = ['출현 횟수']
            df.index.name = names[key]
            df['비율(%)'] = (df['출현 횟수'] / total_count * 100).round(2)

    def _calculate_recent_statistics(self):
        """최근 회차에 대한 전체 통계 계산"""
        self.recent_stats_df = pd.DataFrame({
            '분석 항목': [
                '평균 총합',
                '최대 총합',
                '최소 총합',
                '평균 표준편차',
                '평균 간격',
                '대각선 패턴 출현 비율',
                '평균 대각선 교차점 개수',
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
                '무연속 번호 패턴 출현 회차 수',
                '총 분석 회차'
            ],
            '값': [
                round(np.mean(self.recent_results['sums']), 2),
                max(self.recent_results['sums']),
                min(self.recent_results['sums']),
                round(np.mean(self.recent_results['std_deviations']), 2),
                round(np.mean(self.recent_results['average_gaps']), 2),
                f"{(sum(self.recent_results['diagonal_patterns']) / len(self.recent_results['diagonal_patterns']) * 100):.2f}%",
                round(np.mean(self.recent_results['diagonal_match_counts']), 2),
                round(np.mean(self.recent_results['corner_results']), 2),
                max(self.recent_results['corner_results']),
                min(self.recent_results['corner_results']),
                round(np.mean(self.recent_results['ac_results']), 2),
                max(self.recent_results['ac_results']),
                min(self.recent_results['ac_results']),
                round(np.mean(self.recent_results['color_patterns']), 2),
                round(np.mean(self.recent_results['composite_counts']), 2),
                round(np.mean(self.recent_results['perfect_square_counts']), 2),
                round(np.mean(self.recent_results['mirror_number_counts']), 2),
                round(np.mean(self.recent_results['multiples_3_counts']), 2),
                round(np.mean(self.recent_results['multiples_4_counts']), 2),
                round(np.mean(self.recent_results['multiples_5_counts']), 2),
                round(np.mean(self.recent_results['prime_counts']), 2),
                round(np.mean(self.recent_results['last_digit_sums']), 2),
                max(self.recent_results['last_digit_sums']),
                min(self.recent_results['last_digit_sums']),
                round(np.mean(self.recent_results['palindrome_counts']), 2),
                max(self.recent_results['palindrome_counts']),
                round(np.mean(self.recent_results['double_number_counts']), 2),
                max(self.recent_results['double_number_counts']),
                len([x for x in self.recent_results['consecutive_patterns'] if x > 0]),
                len([x for x in self.recent_results['consecutive_patterns'] if x == 0]),
                len(self.recent_results['corner_results'])
            ]
        })

    def analyze_single_numbers_extended(self, numbers):
        """
        단일 번호 조합에 대한 확장 분석
        """
        # 기본 분석 결과 가져오기
        basic_results = self._analyze_single_draw(numbers)

        # 추가 분석 수행
        additional_results = {
            'high_low_ratio': self.get_high_low_ratio(numbers),
            'odd_even_ratio': self.get_odd_even_ratio(numbers),
            'sum': self.calculate_sum(numbers),
            'std_deviation': self.calculate_std_deviation(numbers),
            'average_gap': self.calculate_average_gap(numbers),
            'diagonal_pattern': self.check_diagonal_pattern(numbers),
            'previous_draw_overlap': self.check_previous_draws_overlap(numbers, 3)
        }

        # 핫/콜드 번호 분석
        hot_cold_info = self.get_hot_cold_numbers(50)
        hot_nums = set(hot_cold_info['hot_numbers'])
        cold_nums = set(hot_cold_info['cold_numbers'])
        normal_nums = set(hot_cold_info['normal_numbers'])

        numbers_set = set(numbers)
        hot_count = len(numbers_set.intersection(hot_nums))
        cold_count = len(numbers_set.intersection(cold_nums))
        normal_count = len(numbers_set.intersection(normal_nums))

        additional_results['hot_cold_analysis'] = {
            'hot_numbers_count': hot_count,
            'cold_numbers_count': cold_count,
            'normal_numbers_count': normal_count
        }

        # 모든 결과 합치기
        all_results = {**basic_results, **additional_results}

        return all_results

    def print_extended_analysis_results(self, numbers=None):
        """확장된 분석 결과 출력"""
        if numbers:
            # 단일 번호 분석
            results = self.analyze_single_numbers_extended(numbers)

            print("\n=== 확장 번호 조합 분석 결과 ===")
            print(f"번호: {sorted(numbers)}")
            print(f"홀짝 비율: {results['odd_even_ratio']}")
            print(f"고저 비율: {results['high_low_ratio']}")
            print(f"총합: {results['sum']}")
            print(f"표준편차: {results['std_deviation']}")
            print(f"평균 간격: {results['average_gap']}")
            print(f"AC 값: {results['ac_value']}")

            # 대각선 패턴 결과
            diagonal = results['diagonal_pattern']
            if diagonal['has_diagonal_pattern']:
                print(f"대각선 패턴: 있음 (교차점 {diagonal['diagonal_match_count']}개)")
                for i, intersection in enumerate(diagonal['intersections'], 1):
                    print(f"  대각선 {i}: {sorted(intersection)}")
            else:
                print("대각선 패턴: 없음")

            # 이전 회차 중복 결과
            print("\n이전 회차와의 중복:")
            for draw, count in results['previous_draw_overlap'].items():
                print(f"  {draw}회차: {count}개 중복")

            # 핫/콜드 번호 분석
            hot_cold = results['hot_cold_analysis']
            print(f"\n핫번호 포함: {hot_cold['hot_numbers_count']}개")
            print(f"콜드번호 포함: {hot_cold['cold_numbers_count']}개")
            print(f"보통번호 포함: {hot_cold['normal_numbers_count']}개")

            # 기존 분석 결과도 출력
            if results['consecutive_groups']:
                consec_str = []
                for group in results['consecutive_groups']:
                    consec_str.append('->'.join(map(str, group)))
                print(f"연속된 번호: {', '.join(consec_str)}")
            else:
                print("연속된 번호: 없음")

            print(f"모서리 번호 개수: {results['corner_count']}")
            print(f"사용된 색상 수: {results['color_count']}")
            print(f"색상 조합: {results['color_combination']}")
            print(f"합성수 개수: {results['composite_count']}")
            print(f"완전제곱수 개수: {results['perfect_square_count']}")
            print(f"동형수 그룹 개수: {results['mirror_number_count']}")
            print(f"3의 배수 개수: {results['multiples_3_count']}")
            print(f"4의 배수 개수: {results['multiples_4_count']}")
            print(f"5의 배수 개수: {results['multiples_5_count']}")
            print(f"소수 개수: {results['prime_count']}")
            print(f"끝수합: {results['last_digit_sum']}")
            print(f"회문수 개수: {results['palindrome_count']}")
            print(f"쌍수 개수: {results['double_number_count']}")
        else:
            # 최근 회차 분석 결과 없는 경우 분석 수행
            if self.recent_freq_dfs is None:
                self.analyze_recent_draws()

            # 테이블 제목 정의
            table_titles = {
                'high_low_ratio_freq': '고저 비율 빈도 분석',
                'odd_even_ratio_freq': '홀짝 비율 빈도 분석',
                'sum_freq': '총합 분포 분석',
                'std_deviation_freq': '표준편차 분포 분석',
                'average_gap_freq': '평균 간격 분포 분석',
                'diagonal_pattern_freq': '대각선 패턴 존재 여부 분석',
                'diagonal_match_count_freq': '대각선 교차점 개수 분석',
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
                print(self.recent_freq_dfs[key].to_string())

            print("\n=== 최근 회차 전체 통계 ===")
            print(self.recent_stats_df.to_string(index=False))



def run_extended_analyzer():
    analyzer = ExtendedLottoAnalyzer("lotto.db")

    print("===== 전체 회차 분석 =====")
    # 전체 회차 기본 분석
    freq_dfs, stats_df = analyzer.analyze_numbers()
    analyzer.print_analysis_results()

    print("\n\n===== 최근 100회차 분석 =====")
    # 최근 100회차 분석
    recent100_freq_dfs, recent100_stats_df = analyzer.analyze_recent_draws(100)
    analyzer.print_extended_analysis_results()

    print("\n\n===== 최근 50회차 분석 =====")
    # 최근 50회차 분석
    recent50_freq_dfs, recent50_stats_df = analyzer.analyze_recent_draws(50)
    analyzer.print_extended_analysis_results()

    # 전체, 100회차, 50회차 트렌드 비교
    print("\n\n===== 트렌드 변화 분석 =====")
    # 핵심 지표 비교
    print("1. 홀짝 및 고저 비율 변화:")
    print("   - 전체 회차 홀짝 비율 분포:")
    print("     ", analyzer.freq_dfs.get('odd_even_ratio_freq', "미분석").head(3).to_string() if hasattr(analyzer,
                                                                                                      'freq_dfs') and analyzer.freq_dfs is not None else "미분석")
    print("   - 최근 100회차 홀짝 비율 분포:")
    print("     ", analyzer.recent_freq_dfs.get('odd_even_ratio_freq', "미분석").head(3).to_string())
    print("   - 최근 50회차 홀짝 비율 분포:")
    print("     ", analyzer.recent_freq_dfs.get('odd_even_ratio_freq', "미분석").head(3).to_string())

    print("\n2. 총합 범위 변화:")
    print("   - 전체 회차 평균 총합:",
          stats_df[stats_df['분석 항목'] == '평균 총합']['값'].values[0] if '평균 총합' in stats_df['분석 항목'].values else "미분석")
    print("   - 최근 100회차 평균 총합:", recent100_stats_df[recent100_stats_df['분석 항목'] == '평균 총합']['값'].values[0])
    print("   - 최근 50회차 평균 총합:", recent50_stats_df[recent50_stats_df['분석 항목'] == '평균 총합']['값'].values[0])

    print("\n3. AC값 분포 변화:")
    print("   - 전체 회차 AC값 분포:")
    print("     ", analyzer.freq_dfs.get('ac_freq', "미분석").head(3).to_string() if hasattr(analyzer,
                                                                                          'freq_dfs') and analyzer.freq_dfs is not None else "미분석")
    print("   - 최근 100회차 AC값 분포:")
    print("     ", analyzer.recent_freq_dfs.get('ac_freq', "미분석").head(3).to_string())
    print("   - 최근 50회차 AC값 분포:")
    print("     ", analyzer.recent_freq_dfs.get('ac_freq', "미분석").head(3).to_string())

    print("\n4. 연속번호 패턴 변화:")
    print("   - 전체 회차 연속번호 비율:",
          f"{(analyzer.stats_df[analyzer.stats_df['분석 항목'] == '연속 번호 패턴 출현 회차 수']['값'].values[0] / analyzer.stats_df[analyzer.stats_df['분석 항목'] == '총 분석 회차']['값'].values[0]) * 100:.2f}%" if '연속 번호 패턴 출현 회차 수' in
                                                                                                                                                                                              analyzer.stats_df[
                                                                                                                                                                                                  '분석 항목'].values else "미분석")
    print("   - 최근 100회차 연속번호 비율:",
          f"{(recent100_stats_df[recent100_stats_df['분석 항목'] == '연속 번호 패턴 출현 회차 수']['값'].values[0] / recent100_stats_df[recent100_stats_df['분석 항목'] == '총 분석 회차']['값'].values[0]) * 100:.2f}%")
    print("   - 최근 50회차 연속번호 비율:",
          f"{(recent50_stats_df[recent50_stats_df['분석 항목'] == '연속 번호 패턴 출현 회차 수']['값'].values[0] / recent50_stats_df[recent50_stats_df['분석 항목'] == '총 분석 회차']['값'].values[0]) * 100:.2f}%")

    print("\n5. 대각선 매칭 패턴 변화:")
    print("   - 최근 100회차 대각선 매칭 비율:", recent100_stats_df[recent100_stats_df['분석 항목'] == '대각선 패턴 출현 비율']['값'].values[0])
    print("   - 최근 50회차 대각선 매칭 비율:", recent50_stats_df[recent50_stats_df['분석 항목'] == '대각선 패턴 출현 비율']['값'].values[0])

    print("\n6. 번호 간격 변화:")
    print("   - 최근 100회차 평균 간격:", recent100_stats_df[recent100_stats_df['분석 항목'] == '평균 간격']['값'].values[0])
    print("   - 최근 50회차 평균 간격:", recent50_stats_df[recent50_stats_df['분석 항목'] == '평균 간격']['값'].values[0])

    print("\n7. 모서리 번호 패턴 변화:")
    print("   - 전체 회차 모서리 번호 분포:")
    print("     ", analyzer.freq_dfs.get('corner_freq', "미분석").head(3).to_string() if hasattr(analyzer,
                                                                                              'freq_dfs') and analyzer.freq_dfs is not None else "미분석")
    print("   - 최근 100회차 모서리 번호 분포:")
    print("     ", analyzer.recent_freq_dfs.get('corner_freq', "미분석").head(3).to_string())
    print("   - 최근 50회차 모서리 번호 분포:")
    print("     ", analyzer.recent_freq_dfs.get('corner_freq', "미분석").head(3).to_string())

    print("\n8. 소수/합성수 분포 변화:")
    print("   - 전체 회차 소수 개수 분포:")
    print("     ", analyzer.freq_dfs.get('prime_freq', "미분석").head(3).to_string() if hasattr(analyzer,
                                                                                             'freq_dfs') and analyzer.freq_dfs is not None else "미분석")
    print("   - 최근 100회차 소수 개수 분포:")
    print("     ", analyzer.recent_freq_dfs.get('prime_freq', "미분석").head(3).to_string())
    print("   - 최근 50회차 소수 개수 분포:")
    print("     ", analyzer.recent_freq_dfs.get('prime_freq', "미분석").head(3).to_string())

    # 예제 번호 조합 분석
    print("\n\n===== 샘플 번호 조합 분석 =====")
    sample_numbers = [3, 11, 19, 23, 33, 42]  # 예시 번호 조합
    analyzer.print_extended_analysis_results(sample_numbers)

    # 핫/콜드 번호 정보 출력
    print("\n\n===== 핫/콜드 번호 정보 =====")
    hot_cold_info = analyzer.get_hot_cold_numbers(50)
    print(f"핫 번호 ({len(hot_cold_info['hot_numbers'])}개): {sorted(hot_cold_info['hot_numbers'])}")
    print(f"콜드 번호 ({len(hot_cold_info['cold_numbers'])}개): {sorted(hot_cold_info['cold_numbers'])}")
    print(f"중간 출현 번호 ({len(hot_cold_info['normal_numbers'])}개): {sorted(hot_cold_info['normal_numbers'])}")


if __name__ == "__main__":
    run_extended_analyzer()
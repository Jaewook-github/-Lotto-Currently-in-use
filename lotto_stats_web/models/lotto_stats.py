# models/lotto_stats.py - 통계 데이터 모델
from utils.db_connector import DatabaseConnector
from collections import Counter
import statistics
import math
from config import Config


class LottoStatsModel:
    """로또 통계 데이터 모델 클래스"""

    @staticmethod
    def get_latest_draw_number():
        """가장 최근 회차 번호 조회"""
        query = "SELECT MAX(draw_number) FROM lotto_results"
        result = DatabaseConnector.execute_query(query, fetch_all=False)
        return result[0] if result and result[0] else 0

    @staticmethod
    def get_draw_count():
        """전체 회차 수 조회"""
        query = "SELECT COUNT(*) FROM lotto_results"
        result = DatabaseConnector.execute_query(query, fetch_all=False)
        return result[0] if result else 0

    @staticmethod
    def get_draws_by_range(start_draw=None, end_draw=None):
        """특정 범위의 회차 데이터 조회"""
        if start_draw and end_draw:
            query = """
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus, draw_date
                FROM lotto_results 
                WHERE draw_number BETWEEN ? AND ?
                ORDER BY draw_number DESC
            """
            params = (start_draw, end_draw)
        else:
            query = """
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus, draw_date
                FROM lotto_results 
                ORDER BY draw_number DESC
            """
            params = ()

        results = DatabaseConnector.execute_query(query, params)

        draws = []
        for row in results:
            draws.append({
                'draw_number': row[0],
                'numbers': list(row[1:7]),
                'bonus': row[7],
                'draw_date': row[8] if len(row) > 8 else None
            })

        return draws

    @staticmethod
    def get_recent_draws(limit=10):
        """최근 N회 당첨번호 조회"""
        latest_draw = LottoStatsModel.get_latest_draw_number()
        start_draw = max(1, latest_draw - limit + 1)
        return LottoStatsModel.get_draws_by_range(start_draw, latest_draw)

    @staticmethod
    def get_number_frequency(draws=None):
        """각 번호별 출현 빈도수 계산"""
        if draws:
            # 제공된 draws 데이터 사용
            all_numbers = []
            for draw in draws:
                all_numbers.extend(draw['numbers'])
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            results = DatabaseConnector.execute_query(query)
            all_numbers = [num for result in results for num in result]

        # Counter를 사용하여 각 번호의 빈도수 계산
        frequency = Counter(all_numbers)

        # 1부터 45까지의 모든 번호에 대해 빈도수 계산 (없는 번호는 0으로 설정)
        frequency_dict = {num: frequency.get(num, 0) for num in range(1, 46)}

        return frequency_dict

    @staticmethod
    def get_bonus_frequency(draws=None):
        """보너스 번호 출현 빈도수 계산"""
        if draws:
            # 제공된 draws 데이터 사용
            bonus_numbers = [draw['bonus'] for draw in draws if 'bonus' in draw]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT bonus FROM lotto_results"
            results = DatabaseConnector.execute_query(query)
            bonus_numbers = [row[0] for row in results]

        # Counter를 사용하여 각 번호의 빈도수 계산
        frequency = Counter(bonus_numbers)

        # 1부터 45까지의 모든 번호에 대해 빈도수 계산 (없는 번호는 0으로 설정)
        frequency_dict = {num: frequency.get(num, 0) for num in range(1, 46)}

        return frequency_dict

    @staticmethod
    def calculate_ac_value(numbers):
        """AC값 계산 (Arithmetic Complexity)"""
        sorted_numbers = sorted(numbers)
        differences = set()

        for i in range(len(sorted_numbers)):
            for j in range(i + 1, len(sorted_numbers)):
                differences.add(sorted_numbers[j] - sorted_numbers[i])

        return len(differences) - 5  # 총 차이값 개수에서 5를 뺀 값 반환

    @staticmethod
    def get_ac_value_stats(draws=None):
        """AC값 분포 통계 조회"""
        if draws:
            # 제공된 draws 데이터 사용
            ac_values = [LottoStatsModel.calculate_ac_value(draw['numbers']) for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            results = DatabaseConnector.execute_query(query)
            ac_values = [LottoStatsModel.calculate_ac_value(row) for row in results]

        # 각 AC값별 카운트
        ac_counts = Counter(ac_values)

        # AC값 통계
        max_ac = max(ac_values) if ac_values else 15
        stats = {
            'counts': [ac_counts.get(i, 0) for i in range(max_ac + 1)],
            'labels': [str(i) for i in range(max_ac + 1)],
            'avg_ac': round(sum(ac_values) / len(ac_values), 2) if ac_values else 0,
            'most_common_ac': Counter(ac_values).most_common(1)[0][0] if ac_values else 0,
            'distribution': dict(sorted(dict(ac_counts).items()))
        }

        return stats

    @staticmethod
    def get_sum_stats(draws=None):
        """당첨 번호 합계 통계"""
        if draws:
            # 제공된 draws 데이터 사용
            sums = [sum(draw['numbers']) for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            results = DatabaseConnector.execute_query(query)
            sums = [sum(row) for row in results]

        # 합계 범위 (기본 간격: 5)
        interval = 5
        min_sum = (min(sums) // interval) * interval if sums else 0
        max_sum = ((max(sums) // interval) + 1) * interval if sums else 0
        ranges = list(range(min_sum, max_sum + interval, interval))

        # 각 범위별 빈도수
        sum_dist = {r: 0 for r in ranges[:-1]}
        for s in sums:
            for i in range(len(ranges) - 1):
                if ranges[i] <= s < ranges[i + 1]:
                    sum_dist[ranges[i]] += 1
                    break

        # 합계 통계 데이터
        stats = {
            'min_sum': min(sums) if sums else 0,
            'max_sum': max(sums) if sums else 0,
            'avg_sum': round(sum(sums) / len(sums), 2) if sums else 0,
            'median_sum': statistics.median(sums) if sums else 0,
            'most_common_sum': Counter(sums).most_common(1)[0][0] if sums else 0,
            'sum_distribution': {f"{r}-{r + interval - 1}": sum_dist[r] for r in sum_dist},
            'all_sums': sums
        }

        return stats

    @staticmethod
    def get_odd_even_stats(draws=None):
        """홀짝 비율 통계 조회"""
        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [draw['numbers'] for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            draw_numbers = DatabaseConnector.execute_query(query)

        # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
        odd_even_counts = {i: 0 for i in range(7)}

        for row in draw_numbers:
            odd_count = sum(1 for num in row if num % 2 == 1)  # 홀수 개수
            odd_even_counts[odd_count] += 1

        # 각 비율의 퍼센트 계산
        total = sum(odd_even_counts.values())
        odd_even_stats = {
            'counts': list(odd_even_counts.values()),
            'percentages': [round(count / total * 100, 1) if total > 0 else 0 for count in odd_even_counts.values()],
            'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
        }

        return odd_even_stats

    @staticmethod
    def get_high_low_stats(draws=None, cutoff=None):
        """고저 비율 통계 조회"""
        if cutoff is None:
            cutoff = Config.HIGH_LOW_CUTOFF  # 기본값 사용

        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [draw['numbers'] for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            draw_numbers = DatabaseConnector.execute_query(query)

        # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
        high_low_counts = {i: 0 for i in range(7)}

        for row in draw_numbers:
            high_count = sum(1 for num in row if num >= cutoff)  # 고번호(기준값 이상) 개수
            high_low_counts[high_count] += 1

        # 각 비율의 퍼센트 계산
        total = sum(high_low_counts.values())
        high_low_stats = {
            'counts': list(high_low_counts.values()),
            'percentages': [round(count / total * 100, 1) if total > 0 else 0 for count in high_low_counts.values()],
            'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0'],
            'cutoff': cutoff
        }

        return high_low_stats

    @staticmethod
    def get_consecutive_pairs_stats(draws=None):
        """연속된 숫자 쌍 개수 통계 조회"""
        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [draw['numbers'] for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            draw_numbers = DatabaseConnector.execute_query(query)

        # 연속 쌍 개수별 카운트 (0, 1, 2, 3, ...)
        consecutive_counts = {i: 0 for i in range(6)}

        for row in draw_numbers:
            sorted_numbers = sorted(row)
            consecutive_pairs = sum(1 for i in range(len(sorted_numbers) - 1)
                                    if sorted_numbers[i + 1] - sorted_numbers[i] == 1)
            consecutive_counts[consecutive_pairs] += 1

        # 각 경우의 퍼센트 계산
        total = sum(consecutive_counts.values())
        consecutive_stats = {
            'counts': list(consecutive_counts.values()),
            'percentages': [round(count / total * 100, 1) if total > 0 else 0 for count in consecutive_counts.values()],
            'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍', '연속 4쌍', '연속 5쌍']
        }

        return consecutive_stats

    @staticmethod
    def analyze_number_patterns(draws=None):
        """번호 패턴 분석 (소수, 연속수, 끝수 등)"""
        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [draw['numbers'] for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results ORDER BY draw_number DESC"
            draw_numbers = DatabaseConnector.execute_query(query)

        # 소수 정의 (1과 자신으로만 나누어지는 수)
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n ** 0.5) + 1):
                if n % i == 0:
                    return False
            return True

        primes = [n for n in range(1, 46) if is_prime(n)]

        # 각 회차별 분석
        pattern_stats = []

        for numbers in draw_numbers:
            sorted_nums = sorted(numbers)

            # 각종 패턴 분석
            odd_count = sum(1 for num in sorted_nums if num % 2 == 1)
            high_count = sum(1 for num in sorted_nums if num >= Config.HIGH_LOW_CUTOFF)
            prime_count = sum(1 for num in sorted_nums if num in primes)
            mult_3_count = sum(1 for num in sorted_nums if num % 3 == 0)
            mult_5_count = sum(1 for num in sorted_nums if num % 5 == 0)

            pattern_stats.append({
                'numbers': sorted_nums,
                'sum': sum(sorted_nums),
                'odd_count': odd_count,
                'even_count': 6 - odd_count,
                'high_count': high_count,
                'low_count': 6 - high_count,
                'prime_count': prime_count,
                'mult_3_count': mult_3_count,
                'mult_5_count': mult_5_count
            })

        # 각 속성별 통계
        prime_distribution = Counter([stat['prime_count'] for stat in pattern_stats])
        mult_3_distribution = Counter([stat['mult_3_count'] for stat in pattern_stats])
        mult_5_distribution = Counter([stat['mult_5_count'] for stat in pattern_stats])

        # 결과 통합
        pattern_analysis = {
            'prime_numbers': primes,
            'prime_distribution': dict(sorted(dict(prime_distribution).items())),
            'mult_3_distribution': dict(sorted(dict(mult_3_distribution).items())),
            'mult_5_distribution': dict(sorted(dict(mult_5_distribution).items())),
        }

        return pattern_analysis

    @staticmethod
    def analyze_last_digits(draws=None):
        """끝수(일의 자리) 분석"""
        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [draw['numbers'] for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            draw_numbers = DatabaseConnector.execute_query(query)

        # 모든 번호의 끝수(일의 자리) 추출
        last_digits = []
        last_digit_sums = []

        for numbers in draw_numbers:
            # 각 번호의 끝수
            draw_last_digits = [num % 10 for num in numbers]
            last_digits.extend(draw_last_digits)

            # 끝수의 합
            last_digit_sums.append(sum(draw_last_digits))

        # 끝수 분포
        digit_counts = Counter(last_digits)

        # 끝수 합계 분포
        if last_digit_sums:
            sum_min = min(last_digit_sums)
            sum_max = max(last_digit_sums)
            interval = 3  # 구간 간격

            # 구간별 빈도
            sum_ranges = list(range(sum_min - sum_min % interval, sum_max + interval, interval))
            sum_distribution = {r: 0 for r in sum_ranges[:-1]}

            for s in last_digit_sums:
                for i in range(len(sum_ranges) - 1):
                    if sum_ranges[i] <= s < sum_ranges[i + 1]:
                        sum_distribution[sum_ranges[i]] += 1
                        break

            # 결과 통합
            last_digit_analysis = {
                'digit_distribution': {str(d): digit_counts.get(d, 0) for d in range(10)},
                'sum_avg': round(sum(last_digit_sums) / len(last_digit_sums), 2),
                'sum_distribution': {f"{r}-{r + interval - 1}": sum_distribution[r] for r in sum_distribution},
                'sum_min': sum_min,
                'sum_max': sum_max
            }
        else:
            last_digit_analysis = {
                'digit_distribution': {str(d): 0 for d in range(10)},
                'sum_avg': 0,
                'sum_distribution': {},
                'sum_min': 0,
                'sum_max': 0
            }

        return last_digit_analysis

    @staticmethod
    def get_number_combinations_analysis(draws=None):
        """번호 조합 패턴 분석"""
        if draws:
            # 제공된 draws 데이터 사용
            draw_numbers = [tuple(sorted(draw['numbers'])) for draw in draws]
        else:
            # DB에서 모든 데이터 조회
            query = "SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results"
            draw_numbers = [tuple(sorted(row)) for row in DatabaseConnector.execute_query(query)]

        # 구간별 번호 출현 패턴
        zone_patterns = []
        for numbers in draw_numbers:
            # 번호대별 카운트 (1-10, 11-20, 21-30, 31-40, 41-45)
            zone_counts = [0, 0, 0, 0, 0]
            for num in numbers:
                if 1 <= num <= 10:
                    zone_counts[0] += 1
                elif 11 <= num <= 20:
                    zone_counts[1] += 1
                elif 21 <= num <= 30:
                    zone_counts[2] += 1
                elif 31 <= num <= 40:
                    zone_counts[3] += 1
                else:  # 41-45
                    zone_counts[4] += 1

            zone_pattern = "".join(str(c) for c in zone_counts)
            zone_patterns.append(zone_pattern)

        # 패턴 빈도수
        pattern_counts = Counter(zone_patterns)
        top_patterns = pattern_counts.most_common(10)

        # 결과 통합
        combinations_analysis = {
            'top_patterns': [{
                'pattern': p[0],
                'count': p[1],
                'percentage': round(p[1] / len(zone_patterns) * 100, 2) if zone_patterns else 0
            } for p in top_patterns],
            'pattern_labels': ['1-10', '11-20', '21-30', '31-40', '41-45']
        }

        return combinations_analysis

    @staticmethod
    def get_stats_summary(draws=None):
        """통계 데이터 요약본 생성"""
        # 필요한 통계 데이터 계산
        sum_stats = LottoStatsModel.get_sum_stats(draws)
        ac_stats = LottoStatsModel.get_ac_value_stats(draws)
        odd_even_stats = LottoStatsModel.get_odd_even_stats(draws)
        high_low_stats = LottoStatsModel.get_high_low_stats(draws)
        consecutive_stats = LottoStatsModel.get_consecutive_pairs_stats(draws)
        pattern_analysis = LottoStatsModel.analyze_number_patterns(draws)

        # 가장 많이 나온 홀짝 비율 찾기
        odd_even_max_index = odd_even_stats['counts'].index(max(odd_even_stats['counts']))
        odd_count = odd_even_max_index
        even_count = 6 - odd_count
        odd_even_percentage = odd_even_stats['percentages'][odd_even_max_index]

        # 가장 많이 나온 고저 비율 찾기
        high_low_max_index = high_low_stats['counts'].index(max(high_low_stats['counts']))
        high_count = high_low_max_index
        low_count = 6 - high_count
        high_low_percentage = high_low_stats['percentages'][high_low_max_index]

        # 가장 많이 나온 연속번호 쌍 찾기
        consecutive_max_index = consecutive_stats['counts'].index(max(consecutive_stats['counts']))
        consecutive_count = consecutive_max_index
        consecutive_percentage = consecutive_stats['percentages'][consecutive_max_index]

        # 요약 정보 생성
        summary = {
            'avg_sum': sum_stats['avg_sum'],
            'sum_min': sum_stats['min_sum'],
            'sum_max': sum_stats['max_sum'],
            'avg_ac': ac_stats['avg_ac'],
            'most_common_ac': ac_stats['most_common_ac'],
            'odd_even_ratio': f"{odd_count}:{even_count} ({odd_even_percentage}%)",
            'high_low_ratio': f"{high_count}:{low_count} ({high_low_percentage}%)",
            'consecutive_pairs': f"{consecutive_count}쌍 ({consecutive_percentage}%)",
            'most_common_prime': list(pattern_analysis['prime_distribution'].keys())[
                list(pattern_analysis['prime_distribution'].values()).index(
                    max(pattern_analysis['prime_distribution'].values()))
            ] if pattern_analysis['prime_distribution'] else 0
        }

        return summary
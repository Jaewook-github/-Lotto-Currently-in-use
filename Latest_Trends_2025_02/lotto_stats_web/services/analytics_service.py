# services/analytics_service.py - 데이터 분석 서비스
from models.lotto_stats import LottoStatsModel
from utils.data_utils import DataUtils
from config import Config
import numpy as np
from sklearn.cluster import KMeans
from collections import defaultdict, Counter
import time


class AnalyticsService:
    """고급 데이터 분석 서비스"""

    @staticmethod
    def analyze_winning_patterns():
        """당첨 번호의 패턴 분석"""
        # 모든 회차 데이터 가져오기
        draws = LottoStatsModel.get_draws_by_range()

        # 분석 시작 시간
        start_time = time.time()

        # 최근 50회차 분석 (또는 전체 회차가 50회 미만이면 전체)
        recent_draws = draws[:min(50, len(draws))]

        # 각 분석 수행
        pattern_analysis = {
            # 기본 통계 분석
            'basic_stats': AnalyticsService._analyze_basic_stats(draws),

            # 출현 간격 분석
            'number_gaps': AnalyticsService._analyze_number_gaps(draws),

            # 출현 기간 분석
            'time_analysis': AnalyticsService._analyze_appearance_timing(draws),

            # 규칙성 점수 (랜덤성 측정)
            'randomness_score': AnalyticsService._calculate_randomness_score(recent_draws),

            # 군집 분석 (유사한 당첨 패턴 그룹)
            'clusters': AnalyticsService._cluster_winning_numbers(draws),

            # 번호 조합 패턴
            'combination_patterns': AnalyticsService._analyze_combination_patterns(draws),

            # 처리 시간 (초)
            'processing_time': round(time.time() - start_time, 2)
        }

        return pattern_analysis

    @staticmethod
    def _analyze_basic_stats(draws):
        """기본 통계 분석"""
        all_numbers = []
        sums = []
        all_gaps = []
        ac_values = []

        for draw in draws:
            numbers = sorted(draw['numbers'])
            all_numbers.extend(numbers)
            sums.append(sum(numbers))

            # 연속된 번호 사이의 간격
            gaps = [numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]
            all_gaps.extend(gaps)

            # AC값 계산
            ac_values.append(LottoStatsModel.calculate_ac_value(numbers))

        # 기본 통계 계산
        number_stats = DataUtils.calculate_statistics(all_numbers)
        sum_stats = DataUtils.calculate_statistics(sums)
        gap_stats = DataUtils.calculate_statistics(all_gaps)
        ac_stats = DataUtils.calculate_statistics(ac_values)

        return {
            'number_statistics': number_stats,
            'sum_statistics': sum_stats,
            'gap_statistics': gap_stats,
            'ac_statistics': ac_stats
        }

    @staticmethod
    def _analyze_number_gaps(draws):
        """각 번호별 출현 간격 분석"""
        # 각 번호의 출현 회차 기록
        number_appearances = defaultdict(list)

        for i, draw in enumerate(reversed(draws)):  # 오래된 것부터 순서대로
            draw_number = draw['draw_number']
            for num in draw['numbers']:
                number_appearances[num].append(draw_number)

        # 각 번호별 출현 간격
        number_gaps = {}
        for num in range(1, 46):
            appearances = number_appearances.get(num, [])
            if len(appearances) > 1:
                # 연속된 회차 간의 차이 계산
                gaps = [appearances[i] - appearances[i - 1] for i in range(1, len(appearances))]
                gap_stats = DataUtils.calculate_statistics(gaps)

                number_gaps[num] = {
                    'appearances': len(appearances),
                    'last_appearance': appearances[-1] if appearances else None,
                    'avg_gap': gap_stats['mean'],
                    'max_gap': gap_stats['max'],
                    'gaps': gaps
                }
            else:
                number_gaps[num] = {
                    'appearances': len(appearances),
                    'last_appearance': appearances[0] if appearances else None,
                    'avg_gap': None,
                    'max_gap': None,
                    'gaps': []
                }

        return number_gaps

    @staticmethod
    def _analyze_appearance_timing(draws):
        """번호 출현 시기 분석"""
        total_draws = len(draws)
        if total_draws == 0:
            return {}

        # 출현 빈도
        frequency = LottoStatsModel.get_number_frequency(draws)

        # 최근 10, 20, 50회차 출현 빈도
        recent_10 = draws[:min(10, total_draws)]
        recent_20 = draws[:min(20, total_draws)]
        recent_50 = draws[:min(50, total_draws)]

        freq_10 = LottoStatsModel.get_number_frequency(recent_10)
        freq_20 = LottoStatsModel.get_number_frequency(recent_20)
        freq_50 = LottoStatsModel.get_number_frequency(recent_50)

        # 출현 추세 계산
        trend_analysis = {}
        for num in range(1, 46):
            # 전체 대비 최근 출현 비율
            total_freq = frequency.get(num, 0)
            recent_10_freq = freq_10.get(num, 0)
            recent_20_freq = freq_20.get(num, 0)
            recent_50_freq = freq_50.get(num, 0)

            # 출현 확률
            total_prob = total_freq / total_draws if total_draws > 0 else 0
            recent_10_prob = recent_10_freq / min(10, total_draws) if total_draws > 0 else 0
            recent_20_prob = recent_20_freq / min(20, total_draws) if total_draws > 0 else 0
            recent_50_prob = recent_50_freq / min(50, total_draws) if total_draws > 0 else 0

            # 초기 확률 대비 최근 확률 변화 (증감률)
            change_10 = ((recent_10_prob / total_prob) - 1) * 100 if total_prob > 0 else 0
            change_20 = ((recent_20_prob / total_prob) - 1) * 100 if total_prob > 0 else 0
            change_50 = ((recent_50_prob / total_prob) - 1) * 100 if total_prob > 0 else 0

            # 추세 판단 (상승, 하락, 유지)
            if recent_10_prob > recent_50_prob > total_prob:
                trend = "increasing"
            elif recent_10_prob < recent_50_prob < total_prob:
                trend = "decreasing"
            else:
                trend = "stable"

            trend_analysis[num] = {
                'total_freq': total_freq,
                'recent_10_freq': recent_10_freq,
                'recent_20_freq': recent_20_freq,
                'recent_50_freq': recent_50_freq,
                'total_probability': round(total_prob * 100, 2),
                'recent_10_probability': round(recent_10_prob * 100, 2),
                'recent_20_probability': round(recent_20_prob * 100, 2),
                'recent_50_probability': round(recent_50_prob * 100, 2),
                'change_10': round(change_10, 2),
                'change_20': round(change_20, 2),
                'change_50': round(change_50, 2),
                'trend': trend
            }

        return trend_analysis

    @staticmethod
    def _calculate_randomness_score(draws):
        """당첨 번호의 랜덤성 점수 계산"""
        if not draws:
            return {
                'score': 0,
                'details': {}
            }

        # 랜덤성 평가 지표들
        scores = {}

        # 1. 번호 분포 균등성 (1-45 범위에서 균등하게 분포되는지)
        number_freq = LottoStatsModel.get_number_frequency(draws)
        values = list(number_freq.values())
        ideal_freq = sum(values) / len(values)  # 이상적인 균등 분포 빈도

        # 편차 계산 (이상적 분포에서 벗어난 정도)
        distribution_variance = sum((freq - ideal_freq) ** 2 for freq in values) / len(values)
        # 정규화 (0-100)
        max_variance = ideal_freq ** 2  # 최악의 경우 (모든 번호가 한 번도 안 나오고 하나만 나올 경우)
        distribution_score = 100 * (1 - min(distribution_variance / max_variance, 1))

        scores['distribution'] = round(distribution_score, 2)

        # 2. 연속번호 발생 빈도
        consecutive_counts = []
        for draw in draws:
            sorted_nums = sorted(draw['numbers'])
            consecutive = sum(1 for i in range(len(sorted_nums) - 1)
                              if sorted_nums[i + 1] - sorted_nums[i] == 1)
            consecutive_counts.append(consecutive)

        # 이상적인 연속번호 발생 비율 (약 5/39 = 12.8%)
        ideal_consecutive_ratio = 5 / 39
        actual_consecutive_ratio = sum(consecutive_counts) / (len(consecutive_counts) * 5) if consecutive_counts else 0
        consecutive_score = 100 * (
                    1 - min(abs(actual_consecutive_ratio - ideal_consecutive_ratio) / ideal_consecutive_ratio, 1))

        scores['consecutive'] = round(consecutive_score, 2)

        # 3. 홀짝 분포
        odd_counts = []
        for draw in draws:
            odd_count = sum(1 for num in draw['numbers'] if num % 2 == 1)
            odd_counts.append(odd_count)

        # 이상적인 홀수 비율 (50%)
        ideal_odd_ratio = 0.5
        actual_odd_ratio = sum(odd_counts) / (len(odd_counts) * 6) if odd_counts else 0
        odd_even_score = 100 * (1 - min(abs(actual_odd_ratio - ideal_odd_ratio) / ideal_odd_ratio, 1))

        scores['odd_even'] = round(odd_even_score, 2)

        # 4. AC값 분포
        ac_values = [LottoStatsModel.calculate_ac_value(draw['numbers']) for draw in draws]
        ideal_ac = 10  # 이상적인 AC값 중간치
        ac_deviation = sum(abs(ac - ideal_ac) for ac in ac_values) / len(ac_values) if ac_values else 0
        ac_score = 100 * (1 - min(ac_deviation / ideal_ac, 1))

        scores['ac_value'] = round(ac_score, 2)

        # 전체 랜덤성 점수 (가중 평균)
        weights = {
            'distribution': 0.4,
            'consecutive': 0.2,
            'odd_even': 0.2,
            'ac_value': 0.2
        }

        overall_score = sum(scores[key] * weights[key] for key in scores)

        return {
            'score': round(overall_score, 2),
            'details': scores
        }

    @staticmethod
    def _cluster_winning_numbers(draws, n_clusters=5):
        """당첨 번호 군집 분석"""
        if len(draws) < n_clusters:
            return {
                'error': '군집 분석을 위한 충분한 데이터가 없습니다.',
                'min_required': n_clusters,
                'actual': len(draws)
            }

        # 번호를 벡터로 변환 (45차원 원-핫 인코딩)
        X = np.zeros((len(draws), 45))
        for i, draw in enumerate(draws):
            for num in draw['numbers']:
                X[i, num - 1] = 1

        # K-means 군집화
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)

        # 각 군집별 특성 분석
        cluster_analysis = {}
        for cluster_id in range(n_clusters):
            # 해당 군집의 당첨 번호들
            cluster_draws = [draws[i] for i in range(len(draws)) if clusters[i] == cluster_id]

            # 군집 내 번호 빈도
            cluster_freq = LottoStatsModel.get_number_frequency(cluster_draws)

            # 가장 많이 등장하는 번호 top 10
            top_numbers = sorted(cluster_freq.items(), key=lambda x: x[1], reverse=True)[:10]

            # 군집의 특성 분석
            cluster_sums = [sum(draw['numbers']) for draw in cluster_draws]
            odd_counts = [sum(1 for num in draw['numbers'] if num % 2 == 1) for draw in cluster_draws]
            high_counts = [sum(1 for num in draw['numbers'] if num >= 23) for draw in cluster_draws]

            cluster_analysis[cluster_id] = {
                'size': len(cluster_draws),
                'percentage': round(len(cluster_draws) / len(draws) * 100, 2),
                'avg_sum': round(sum(cluster_sums) / len(cluster_sums), 2) if cluster_sums else 0,
                'avg_odd_count': round(sum(odd_counts) / len(odd_counts), 2) if odd_counts else 0,
                'avg_high_count': round(sum(high_counts) / len(high_counts), 2) if high_counts else 0,
                'top_numbers': top_numbers,
                'example_draws': [draw for draw in cluster_draws[:3]]  # 예시 당첨 번호
            }

        return cluster_analysis

    @staticmethod
    def _analyze_combination_patterns(draws):
        """당첨 번호 조합 패턴 분석"""
        # 구간별 번호 분포
        zone_patterns = []
        for draw in draws:
            numbers = draw['numbers']
            zone_counts = [0, 0, 0, 0, 0]  # 1-9, 10-19, 20-29, 30-39, 40-45

            for num in numbers:
                if num <= 9:
                    zone_counts[0] += 1
                elif num <= 19:
                    zone_counts[1] += 1
                elif num <= 29:
                    zone_counts[2] += 1
                elif num <= 39:
                    zone_counts[3] += 1
                else:
                    zone_counts[4] += 1

            pattern = "".join(str(c) for c in zone_counts)
            zone_patterns.append({
                'pattern': pattern,
                'draw_number': draw['draw_number'],
                'numbers': draw['numbers']
            })

        # 패턴 빈도 계산
        pattern_counts = Counter([item['pattern'] for item in zone_patterns])

        # 상위 패턴 및 예시
        top_patterns = []
        for pattern, count in pattern_counts.most_common(10):
            examples = [item for item in zone_patterns if item['pattern'] == pattern][:3]
            top_patterns.append({
                'pattern': pattern,
                'count': count,
                'percentage': round(count / len(draws) * 100, 2) if draws else 0,
                'examples': examples
            })

        return {
            'total_patterns': len(pattern_counts),
            'top_patterns': top_patterns,
            'zone_names': ['1-9', '10-19', '20-29', '30-39', '40-45']
        }

    @staticmethod
    def get_predictive_metrics():
        """예측에 도움이 되는 지표 계산"""
        # 모든 회차 데이터 가져오기
        draws = LottoStatsModel.get_draws_by_range()

        # 분석 시작 시간
        start_time = time.time()

        # 결과 저장 변수
        metrics = {}

        # 출현 간격 기반 예측 지표
        number_gaps = AnalyticsService._analyze_number_gaps(draws)

        # 출현 확률이 낮아 곧 출현할 가능성이 높은 번호들 (오랫동안 나오지 않은 번호)
        due_numbers = sorted(
            [(num, data) for num, data in number_gaps.items() if data['appearances'] > 0],
            key=lambda x: (x[1]['last_appearance'] or 0)
        )

        # 출현 간격이 긴 번호들 (평균 출현 간격보다 오래 나오지 않은 번호)
        overdue_numbers = []
        latest_draw = LottoStatsModel.get_latest_draw_number()

        for num, data in number_gaps.items():
            if data['appearances'] > 0 and data['avg_gap'] is not None:
                last_appearance = data['last_appearance']
                avg_gap = data['avg_gap']
                current_gap = latest_draw - last_appearance

                # 평균 간격보다 더 오래 나오지 않았는지 확인
                if current_gap > avg_gap:
                    overdue_factor = current_gap / avg_gap
                    overdue_numbers.append((num, overdue_factor, current_gap, avg_gap))

        # 오버듀 팩터 기준 정렬
        overdue_numbers.sort(key=lambda x: x[1], reverse=True)

        # 전환점 지표 (최근 추세 반전 조짐)
        trend_analysis = AnalyticsService._analyze_appearance_timing(draws)

        # 최근 급상승 또는 급하락 번호
        changing_numbers = {
            'increasing': [],
            'decreasing': [],
            'stable': []
        }

        for num, data in trend_analysis.items():
            # 최근 10회 대비 전체 변화율이 큰 번호들
            if abs(data['change_10']) > 50:  # 50% 이상 변화
                if data['trend'] == 'increasing':
                    changing_numbers['increasing'].append((num, data['change_10']))
                elif data['trend'] == 'decreasing':
                    changing_numbers['decreasing'].append((num, data['change_10']))
            else:
                changing_numbers['stable'].append((num, data['change_10']))

        # 정렬
        changing_numbers['increasing'].sort(key=lambda x: x[1], reverse=True)
        changing_numbers['decreasing'].sort(key=lambda x: x[1])

        # 결과 종합
        metrics = {
            'due_numbers': due_numbers[:10],  # 상위 10개
            'overdue_numbers': overdue_numbers[:10],  # 상위 10개
            'trending_numbers': {
                'increasing': changing_numbers['increasing'][:10],
                'decreasing': changing_numbers['decreasing'][:10],
                'stable': changing_numbers['stable'][:10]
            },
            'processing_time': round(time.time() - start_time, 2)
        }

        return metrics

    @staticmethod
    def get_number_correlations():
        """번호 간 상관관계 분석"""
        # 모든 회차 데이터 가져오기
        draws = LottoStatsModel.get_draws_by_range()

        # 분석 시작 시간
        start_time = time.time()

        # 번호 쌍 카운트
        pair_counts = defaultdict(int)
        total_draws = len(draws)

        for draw in draws:
            numbers = draw['numbers']
            # 모든 가능한 번호 쌍 카운트
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    pair = (min(numbers[i], numbers[j]), max(numbers[i], numbers[j]))
                    pair_counts[pair] += 1

        # 개별 번호 출현 빈도
        number_freq = LottoStatsModel.get_number_frequency(draws)

        # 상관관계 계산
        correlations = {}
        for pair, count in pair_counts.items():
            num1, num2 = pair
            # 개별 출현 확률
            p1 = number_freq.get(num1, 0) / total_draws if total_draws > 0 else 0
            p2 = number_freq.get(num2, 0) / total_draws if total_draws > 0 else 0

            # 동시 출현 확률
            p_joint = count / total_draws if total_draws > 0 else 0

            # 기대 확률 (독립인 경우)
            p_expected = (p1 * p2 * 15)  # 6C2 = 15가지 쌍 중 하나

            # 상관계수 (실제/기대 - 1)
            if p_expected > 0:
                correlation = (p_joint / p_expected) - 1
            else:
                correlation = 0

            correlations[pair] = {
                'count': count,
                'probability': round(p_joint * 100, 2),
                'expected': round(p_expected * 100, 2),
                'correlation': round(correlation * 100, 2)  # 퍼센트로 표현
            }

        # 번호별 호환성 점수
        compatibility_scores = defaultdict(dict)
        for pair, data in correlations.items():
            num1, num2 = pair
            compatibility_scores[num1][num2] = data['correlation']
            compatibility_scores[num2][num1] = data['correlation']

        # 평균 호환성 점수
        average_scores = {}
        for num in range(1, 46):
            if num in compatibility_scores:
                scores = compatibility_scores[num].values()
                average_scores[num] = sum(scores) / len(scores) if scores else 0
            else:
                average_scores[num] = 0

        # 상위/하위 상관관계 찾기
        sorted_correlations = sorted(correlations.items(), key=lambda x: x[1]['correlation'], reverse=True)
        top_positive = sorted_correlations[:20]  # 상위 20개 양의 상관관계
        top_negative = sorted_correlations[-20:]  # 상위 20개 음의 상관관계

        return {
            'top_positive': [{'pair': pair, **data} for pair, data in top_positive],
            'top_negative': [{'pair': pair, **data} for pair, data in top_negative],
            'compatibility_scores': compatibility_scores,
            'average_compatibility': average_scores,
            'processing_time': round(time.time() - start_time, 2)
        }
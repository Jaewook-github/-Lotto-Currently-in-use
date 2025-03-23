# services/stats_service.py - 통계 서비스
from models.lotto_stats import LottoStatsModel
from config import Config
import time


class StatsService:
    """로또 통계 생성 및 관리 서비스"""

    @staticmethod
    def get_full_stats():
        """전체 통계 데이터 생성"""
        # 시간 측정 시작
        start_time = time.time()

        # 기본 데이터 조회
        latest_draw = LottoStatsModel.get_latest_draw_number()
        total_count = LottoStatsModel.get_draw_count()

        # 전체 회차 데이터
        all_draws = LottoStatsModel.get_draws_by_range()

        # 최근 100회 데이터 (또는 전체가 100회 미만이면 모두)
        recent_100_start = max(1, latest_draw - Config.DRAW_COUNT_RECENT + 1)
        recent_100_draws = LottoStatsModel.get_draws_by_range(recent_100_start, latest_draw)

        # 최근 10회 데이터
        recent_10_start = max(1, latest_draw - Config.DRAW_COUNT_LATEST + 1)
        recent_10_draws = LottoStatsModel.get_draws_by_range(recent_10_start, latest_draw)

        # 통계 데이터 생성
        stats = {
            'latest_draw': latest_draw,
            'total_draw_count': total_count,

            # 전체 회차 통계
            'all': {
                'frequency': LottoStatsModel.get_number_frequency(all_draws),
                'bonus_frequency': LottoStatsModel.get_bonus_frequency(all_draws),
                'sum_stats': LottoStatsModel.get_sum_stats(all_draws),
                'ac_value_stats': LottoStatsModel.get_ac_value_stats(all_draws),
                'odd_even_stats': LottoStatsModel.get_odd_even_stats(all_draws),
                'high_low_stats': LottoStatsModel.get_high_low_stats(all_draws),
                'consecutive_pairs_stats': LottoStatsModel.get_consecutive_pairs_stats(all_draws),
                'pattern_analysis': LottoStatsModel.analyze_number_patterns(all_draws),
                'last_digit_analysis': LottoStatsModel.analyze_last_digits(all_draws),
                'combinations_analysis': LottoStatsModel.get_number_combinations_analysis(all_draws),
                'summary': LottoStatsModel.get_stats_summary(all_draws)
            },

            # 최근 100회 통계
            'recent_100': {
                'frequency': LottoStatsModel.get_number_frequency(recent_100_draws),
                'bonus_frequency': LottoStatsModel.get_bonus_frequency(recent_100_draws),
                'sum_stats': LottoStatsModel.get_sum_stats(recent_100_draws),
                'ac_value_stats': LottoStatsModel.get_ac_value_stats(recent_100_draws),
                'odd_even_stats': LottoStatsModel.get_odd_even_stats(recent_100_draws),
                'high_low_stats': LottoStatsModel.get_high_low_stats(recent_100_draws),
                'consecutive_pairs_stats': LottoStatsModel.get_consecutive_pairs_stats(recent_100_draws),
                'pattern_analysis': LottoStatsModel.analyze_number_patterns(recent_100_draws),
                'last_digit_analysis': LottoStatsModel.analyze_last_digits(recent_100_draws),
                'combinations_analysis': LottoStatsModel.get_number_combinations_analysis(recent_100_draws),
                'summary': LottoStatsModel.get_stats_summary(recent_100_draws)
            },

            # 최근 10회 통계
            'recent_10': {
                'frequency': LottoStatsModel.get_number_frequency(recent_10_draws),
                'bonus_frequency': LottoStatsModel.get_bonus_frequency(recent_10_draws),
                'sum_stats': LottoStatsModel.get_sum_stats(recent_10_draws),
                'ac_value_stats': LottoStatsModel.get_ac_value_stats(recent_10_draws),
                'odd_even_stats': LottoStatsModel.get_odd_even_stats(recent_10_draws),
                'high_low_stats': LottoStatsModel.get_high_low_stats(recent_10_draws),
                'consecutive_pairs_stats': LottoStatsModel.get_consecutive_pairs_stats(recent_10_draws),
                'pattern_analysis': LottoStatsModel.analyze_number_patterns(recent_10_draws),
                'last_digit_analysis': LottoStatsModel.analyze_last_digits(recent_10_draws),
                'combinations_analysis': LottoStatsModel.get_number_combinations_analysis(recent_10_draws),
                'summary': LottoStatsModel.get_stats_summary(recent_10_draws)
            },

            # 최근 10회 당첨번호
            'recent_draws': recent_10_draws,

            # 처리 시간 (초)
            'processing_time': round(time.time() - start_time, 2)
        }

        return stats

    @staticmethod
    def get_recent_stats(limit=10):
        """최근 N회 통계 데이터 생성"""
        # 시간 측정 시작
        start_time = time.time()

        # 최근 N회 데이터 조회
        latest_draw = LottoStatsModel.get_latest_draw_number()
        start_draw = max(1, latest_draw - limit + 1)
        draws = LottoStatsModel.get_draws_by_range(start_draw, latest_draw)

        # 필요한 통계 생성
        stats = {
            'draws': draws,
            'frequency': LottoStatsModel.get_number_frequency(draws),
            'bonus_frequency': LottoStatsModel.get_bonus_frequency(draws),
            'sum_stats': LottoStatsModel.get_sum_stats(draws),
            'ac_value_stats': LottoStatsModel.get_ac_value_stats(draws),
            'odd_even_stats': LottoStatsModel.get_odd_even_stats(draws),
            'high_low_stats': LottoStatsModel.get_high_low_stats(draws),
            'consecutive_pairs_stats': LottoStatsModel.get_consecutive_pairs_stats(draws),
            'summary': LottoStatsModel.get_stats_summary(draws),
            'processing_time': round(time.time() - start_time, 2)
        }

        return stats

    @staticmethod
    def get_basic_info():
        """기본 정보 조회 (최신 회차, 전체 회차 수 등)"""
        latest_draw = LottoStatsModel.get_latest_draw_number()
        total_draws = LottoStatsModel.get_draw_count()
        recent_draws = LottoStatsModel.get_recent_draws(10)

        return {
            'latest_draw': latest_draw,
            'total_draws': total_draws,
            'recent_draws': recent_draws
        }
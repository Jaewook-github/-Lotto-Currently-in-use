# controllers/api_controller.py - API 컨트롤러
import os
import time

from flask import Blueprint, jsonify, request, current_app
from services.cache_service import CacheService
from services.stats_service import StatsService
from models.lotto_stats import LottoStatsModel
from datetime import datetime

# API 블루프린트 생성
api_bp = Blueprint('api', __name__)


@api_bp.route('/stats')
def api_stats():
    """전체 통계 API 엔드포인트"""
    try:
        force_refresh = request.args.get('refresh', 'false').lower() == 'true'
        stats = CacheService.get_cached_stats(force_refresh)
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        current_app.logger.error(f"통계 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/recent')
def api_recent():
    """최근 회차 통계 API 엔드포인트"""
    try:
        limit = int(request.args.get('limit', 10))
        stats = StatsService.get_recent_stats(limit)
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        current_app.logger.error(f"최근 회차 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/draws')
def api_draws():
    """회차 데이터 API 엔드포인트"""
    try:
        start = request.args.get('start')
        end = request.args.get('end')

        if start and end:
            start_draw = int(start)
            end_draw = int(end)
            draws = LottoStatsModel.get_draws_by_range(start_draw, end_draw)
        else:
            limit = int(request.args.get('limit', 10))
            draws = LottoStatsModel.get_recent_draws(limit)

        return jsonify({
            'success': True,
            'draws': draws
        })
    except Exception as e:
        current_app.logger.error(f"회차 데이터 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/frequency')
def api_frequency():
    """번호 빈도 API 엔드포인트"""
    try:
        limit = request.args.get('limit')
        if limit:
            draws = LottoStatsModel.get_recent_draws(int(limit))
            frequency = LottoStatsModel.get_number_frequency(draws)
        else:
            frequency = LottoStatsModel.get_number_frequency()

        return jsonify({
            'success': True,
            'frequency': frequency
        })
    except Exception as e:
        current_app.logger.error(f"빈도 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/analysis/<analysis_type>')
def api_analysis(analysis_type):
    """특정 분석 데이터 API 엔드포인트"""
    try:
        limit = request.args.get('limit')
        draws = None

        if limit:
            draws = LottoStatsModel.get_recent_draws(int(limit))

        if analysis_type == 'ac':
            data = LottoStatsModel.get_ac_value_stats(draws)
        elif analysis_type == 'sum':
            data = LottoStatsModel.get_sum_stats(draws)
        elif analysis_type == 'odd_even':
            data = LottoStatsModel.get_odd_even_stats(draws)
        elif analysis_type == 'high_low':
            cutoff = request.args.get('cutoff')
            data = LottoStatsModel.get_high_low_stats(draws, int(cutoff) if cutoff else None)
        elif analysis_type == 'consecutive':
            data = LottoStatsModel.get_consecutive_pairs_stats(draws)
        elif analysis_type == 'patterns':
            data = LottoStatsModel.analyze_number_patterns(draws)
        elif analysis_type == 'last_digits':
            data = LottoStatsModel.analyze_last_digits(draws)
        elif analysis_type == 'combinations':
            data = LottoStatsModel.get_number_combinations_analysis(draws)
        elif analysis_type == 'summary':
            data = LottoStatsModel.get_stats_summary(draws)
        else:
            return jsonify({
                'success': False,
                'error': f"알 수 없는 분석 유형: {analysis_type}"
            }), 400

        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        current_app.logger.error(f"분석 API 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_bp.route('/health')
def api_health():
    """서비스 상태 확인 API"""
    try:
        latest_draw = LottoStatsModel.get_latest_draw_number()

        # 캐시 상태 확인
        cache_file = current_app.config['STATS_CACHE_FILE']
        if os.path.exists(cache_file):
            mtime = os.path.getmtime(cache_file)
            cache_age = (time.time() - mtime) / 60  # 분 단위
        else:
            cache_age = None

        return jsonify({
            'status': 'ok',
            'service': 'lotto-stats-service',
            'latest_draw': latest_draw,
            'cache_age_minutes': round(cache_age, 1) if cache_age is not None else None,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


# 필요한 임포트 추가

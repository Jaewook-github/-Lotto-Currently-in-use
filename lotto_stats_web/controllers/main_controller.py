# controllers/main_controller.py - 메인 컨트롤러
from flask import Blueprint, render_template, redirect, url_for, current_app
from services.stats_service import StatsService
from services.cache_service import CacheService

# 메인 블루프린트 생성
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """통계 분석 메인 페이지"""
    try:
        # 기본 데이터만 조회
        basic_info = StatsService.get_basic_info()

        return render_template('index.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'],
                               recent_draws=basic_info['recent_draws'])
    except Exception as e:
        current_app.logger.error(f"인덱스 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@main_bp.route('/detailed')
def detailed_stats():
    """상세 통계 페이지"""
    try:
        # 기본 데이터만 조회
        basic_info = StatsService.get_basic_info()

        return render_template('pages/detailed.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'])
    except Exception as e:
        current_app.logger.error(f"상세 통계 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@main_bp.route('/patterns')
def patterns_page():
    """패턴 분석 페이지"""
    try:
        # 기본 데이터만 조회
        basic_info = StatsService.get_basic_info()

        return render_template('pages/patterns.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'])
    except Exception as e:
        current_app.logger.error(f"패턴 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@main_bp.route('/analyze')
def analyze_page():
    """분석 도구 페이지"""
    try:
        # 기본 데이터만 조회
        basic_info = StatsService.get_basic_info()

        return render_template('pages/analyze.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'])
    except Exception as e:
        current_app.logger.error(f"분석 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@main_bp.route('/refresh')
def refresh_stats():
    """통계 데이터 수동 새로고침"""
    try:
        CacheService.get_cached_stats(force_refresh=True)
        return redirect(url_for('main.index'))
    except Exception as e:
        current_app.logger.error(f"통계 새로고침 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500
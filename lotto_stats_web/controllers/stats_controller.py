# controllers/stats_controller.py - 통계 컨트롤러
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from services.stats_service import StatsService

# 통계 블루프린트 생성
stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/draw/<int:draw_number>')
def draw_details(draw_number):
    """특정 회차 상세 정보 페이지"""
    try:
        # 회차 정보 조회
        draw_data = StatsService.get_draw_details(draw_number)

        if not draw_data:
            return render_template('pages/error.html',
                                   error=f"{draw_number}회차 정보를 찾을 수 없습니다",
                                   code=404), 404

        return render_template('pages/draw_detail.html', draw=draw_data)
    except Exception as e:
        current_app.logger.error(f"회차 상세 정보 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@stats_bp.route('/recent/<int:limit>')
def recent_stats(limit):
    """최근 N회 통계 페이지"""
    try:
        # 기본 데이터 조회
        basic_info = StatsService.get_basic_info()

        return render_template('pages/recent_stats.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'],
                               limit=limit)
    except Exception as e:
        current_app.logger.error(f"최근 통계 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@stats_bp.route('/compare')
def compare_stats():
    """회차 비교 분석 페이지"""
    try:
        # URL 파라미터에서 비교할 회차들 가져오기
        draw_numbers = request.args.getlist('draws')

        # 기본 데이터 조회
        basic_info = StatsService.get_basic_info()

        # 선택된 회차가 없으면 빈 페이지 표시
        if not draw_numbers:
            return render_template('pages/compare_stats.html',
                                   latest_draw=basic_info['latest_draw'],
                                   total_draws=basic_info['total_draws'],
                                   selected_draws=[])

        # 선택된 회차 정보 조회
        selected_draws = []
        for draw_num in draw_numbers:
            try:
                draw_number = int(draw_num)
                draw_data = StatsService.get_draw_details(draw_number)
                if draw_data:
                    selected_draws.append(draw_data)
            except ValueError:
                continue

        return render_template('pages/compare_stats.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'],
                               selected_draws=selected_draws)
    except Exception as e:
        current_app.logger.error(f"회차 비교 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500


@stats_bp.route('/custom-range')
def custom_range_stats():
    """사용자 지정 범위 통계 페이지"""
    try:
        # URL 파라미터에서 회차 범위 가져오기
        start_draw = request.args.get('start')
        end_draw = request.args.get('end')

        # 기본 데이터 조회
        basic_info = StatsService.get_basic_info()

        # 범위가 없으면 범위 선택 폼 표시
        if not start_draw or not end_draw:
            return render_template('pages/custom_range.html',
                                   latest_draw=basic_info['latest_draw'],
                                   total_draws=basic_info['total_draws'],
                                   has_data=False)

        try:
            start_draw = int(start_draw)
            end_draw = int(end_draw)
        except ValueError:
            return render_template('pages/error.html',
                                   error="유효하지 않은 회차 범위입니다",
                                   code=400), 400

        # 범위 유효성 검사
        if start_draw < 1 or end_draw > basic_info['latest_draw'] or start_draw > end_draw:
            return render_template('pages/error.html',
                                   error="유효하지 않은 회차 범위입니다",
                                   code=400), 400

        return render_template('pages/custom_range.html',
                               latest_draw=basic_info['latest_draw'],
                               total_draws=basic_info['total_draws'],
                               has_data=True,
                               start_draw=start_draw,
                               end_draw=end_draw)
    except Exception as e:
        current_app.logger.error(f"사용자 지정 범위 페이지 로딩 중 오류: {str(e)}")
        return render_template('pages/error.html', error=str(e)), 500
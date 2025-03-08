from flask import Flask, render_template, request, jsonify, session
import random
import uuid
from datetime import datetime
from lotto_config import LottoConfig
from lotto_analyzer import LottoAnalyzer
from db_util import LottoDatabase

app = Flask(__name__)
app.secret_key = 'lotto_tapa_secret_key'  # 세션 관리를 위한 비밀키
app.config['SESSION_TYPE'] = 'filesystem'

# 데이터베이스 초기화
db = LottoDatabase()
db.init_db()


# 사용자 세션 관리
@app.before_request
def create_session():
    """사용자가 처음 접속할 때 고유 세션 생성"""
    if 'user_id' not in session:
        # 사용자를 위한 고유 ID 생성
        session['user_id'] = str(uuid.uuid4())
        # 사용자를 위한 설정 생성
        session['config'] = vars(LottoConfig())


# 라우트
@app.route('/')
def index():
    """메인 페이지 렌더링"""
    try:
        # 최신 회차 정보 가져오기
        latest_draw = db.get_latest_draw_number()
        # 최근 당첨번호 가져오기
        recent_draws = db.get_recent_draws(1)  # 가장 최근 1회차만 가져오기

        return render_template('index.html', latest_draw=latest_draw,
                               recent_draw=recent_draws[0] if recent_draws else None)
    except Exception as e:
        # 오류 발생 시 기본값 사용
        print(f"오류 발생: {str(e)}")
        return render_template('index.html', latest_draw="정보 없음", recent_draw=None)


@app.route('/generate', methods=['POST'])
def generate_numbers():
    """현재 설정 기반으로 로또 번호 생성"""
    try:
        # 요청에서 게임 수 가져오기
        games_count = int(request.form.get('games_count', 5))

        # 사용자 설정 불러오기
        config = LottoConfig()
        config.__dict__.update(session['config'])
        config.games_count = games_count

        # 폼 데이터로 설정 업데이트
        for rule in config.rules_enabled:
            config.rules_enabled[rule] = request.form.get(f'rule_{rule}') == 'true'

        # 번호 생성
        analyzer = LottoAnalyzer(config)
        numbers = analyzer.generate_numbers()

        # 생성 시간 기록
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return jsonify({
            'success': True,
            'numbers': numbers,
            'timestamp': timestamp
        })
    except Exception as e:
        print(f"번호 생성 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/update-config', methods=['POST'])
def update_config():
    """설정 업데이트"""
    try:
        # 세션에서 현재 설정 가져오기
        config_dict = session['config']

        # 규칙 활성화 상태 업데이트
        for rule in config_dict['rules_enabled']:
            if f'rule_{rule}' in request.form:
                config_dict['rules_enabled'][rule] = request.form.get(f'rule_{rule}') == 'true'

        # 범위 및 값 업데이트
        # 총합 범위
        if 'sum_min' in request.form and 'sum_max' in request.form:
            config_dict['sum_range'] = (int(request.form['sum_min']), int(request.form['sum_max']))

        # AC 값
        if 'ac_value_min' in request.form:
            config_dict['ac_value_min'] = int(request.form['ac_value_min'])

        # 홀짝 제외 비율
        config_dict['odd_even_exclude'] = [(0, 6), (6, 0)]

        # 고저 제외 비율
        config_dict['high_low_exclude'] = [(0, 6), (6, 0)]

        # 소수 범위
        if 'prime_min' in request.form and 'prime_max' in request.form:
            config_dict['prime_range'] = (int(request.form['prime_min']), int(request.form['prime_max']))

        # 합성수 범위
        if 'composite_min' in request.form and 'composite_max' in request.form:
            config_dict['composite_range'] = (int(request.form['composite_min']), int(request.form['composite_max']))

        # 끝수 총합 범위
        if 'last_digit_min' in request.form and 'last_digit_max' in request.form:
            config_dict['last_digit_sum_range'] = (
            int(request.form['last_digit_min']), int(request.form['last_digit_max']))

        # 3의 배수 범위
        if 'mult3_min' in request.form and 'mult3_max' in request.form:
            config_dict['multiples_of_3_range'] = (int(request.form['mult3_min']), int(request.form['mult3_max']))

        # 5의 배수 범위
        if 'mult5_min' in request.form and 'mult5_max' in request.form:
            config_dict['multiples_of_5_range'] = (int(request.form['mult5_min']), int(request.form['mult5_max']))

        # 제곱수 범위
        if 'square_min' in request.form and 'square_max' in request.form:
            config_dict['perfect_square_range'] = (int(request.form['square_min']), int(request.form['square_max']))

        # 연속 번호
        consecutive_values = request.form.getlist('consecutive')
        if consecutive_values:
            config_dict['consecutive_numbers'] = [int(val) for val in consecutive_values]

        # 쌍수 범위
        if 'twin_min' in request.form and 'twin_max' in request.form:
            config_dict['twin_numbers_range'] = (int(request.form['twin_min']), int(request.form['twin_max']))

        # 모서리 패턴 범위
        if 'corner_min' in request.form and 'corner_max' in request.form:
            config_dict['corner_numbers_range'] = (int(request.form['corner_min']), int(request.form['corner_max']))

        # 한 모서리 최대 수
        if 'corner_max_per_side' in request.form:
            config_dict['corner_max_per_side'] = int(request.form['corner_max_per_side'])

        # 대각선 최대 차이
        if 'corner_diagonal_diff' in request.form:
            config_dict['corner_diagonal_diff'] = int(request.form['corner_diagonal_diff'])

        # 업데이트된 설정을 세션에 저장
        session['config'] = config_dict

        return jsonify({
            'success': True,
            'message': '설정이 성공적으로 업데이트되었습니다.'
        })
    except Exception as e:
        print(f"설정 업데이트 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/reset-config', methods=['POST'])
def reset_config():
    """설정을 기본값으로 초기화"""
    try:
        # 기본 설정 생성
        session['config'] = vars(LottoConfig())

        return jsonify({
            'success': True,
            'message': '설정이 기본값으로 초기화되었습니다.'
        })
    except Exception as e:
        print(f"설정 초기화 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/stats', methods=['GET'])
def get_stats():
    """로또 데이터베이스에서 통계 데이터 조회"""
    try:
        # 데이터베이스에서 통계 데이터 가져오기
        stats = db.get_stats_for_dashboard()

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        print(f"통계 데이터 조회 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/offline')
def offline():
    """오프라인 페이지"""
    return render_template('offline.html')


@app.errorhandler(404)
def page_not_found(e):
    """404 오류 페이지"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500 오류 페이지"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, jsonify, session
import random
import uuid
import logging
from datetime import datetime
from lotto_config import LottoConfig
from lotto_analyzer import LottoAnalyzer
from db_util import LottoDatabase

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'lotto_tapa_secret_key'  # 세션 관리를 위한 비밀키
app.config['SESSION_TYPE'] = 'filesystem'

# 데이터베이스 초기화 (오류 처리 추가)
try:
    db = LottoDatabase()
    db.init_db()
    logger.info("데이터베이스 초기화 완료")
except Exception as e:
    logger.error(f"데이터베이스 초기화 실패: {str(e)}")
    db = None


# 샘플 데이터 생성 함수
def generate_sample_stats():
    """API 실패 시 사용할 샘플 통계 데이터 생성"""
    return {
        'frequency': {str(i): random.randint(10, 30) for i in range(1, 46)},
        'recent_draws': [
            {
                'draw_number': 1110 - i,
                'numbers': sorted(random.sample(range(1, 46), 6)),
                'bonus': random.randint(1, 45)
            } for i in range(10)
        ],
        'sum_trend': [
            {
                'draw_number': 1100 + i,
                'sum': random.randint(120, 160)
            } for i in range(15)
        ],
        'odd_even': {
            'counts': [5, 15, 45, 35, 30, 10, 5],
            'percentages': [3.4, 10.3, 31.0, 24.1, 20.7, 6.9, 3.4],
            'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
        },
        'high_low': {
            'counts': [8, 18, 40, 38, 25, 12, 4],
            'percentages': [5.5, 12.4, 27.6, 26.2, 17.2, 8.3, 2.8],
            'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
        },
        'ac_value': {
            'counts': [2, 5, 12, 25, 30, 35, 28, 18, 12, 8, 5, 3, 2, 1, 0, 0],
            'labels': [str(i) for i in range(16)]
        },
        'consecutive_pairs': {
            'counts': [50, 35, 12, 3],
            'percentages': [50.0, 35.0, 12.0, 3.0],
            'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍']
        },
        'latest_draw': 1110
    }


# 사용자 세션 관리
@app.before_request
def create_session():
    """사용자가 처음 접속할 때 고유 세션 생성"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
        session['config'] = vars(LottoConfig())


# 라우트
@app.route('/')
def index():
    """메인 페이지 렌더링"""
    try:
        latest_draw = "정보 없음"
        recent_draw = None

        if db:
            latest_draw = db.get_latest_draw_number()
            recent_draws = db.get_recent_draws(1)
            recent_draw = recent_draws[0] if recent_draws else None
        else:
            # 데이터베이스가 없을 때 샘플 데이터 사용
            logger.warning("데이터베이스 연결 없이 샘플 데이터 사용")
            recent_draw = {
                'draw_number': 1110,
                'numbers': [7, 15, 23, 28, 36, 42],
                'bonus': 17
            }
            latest_draw = 1110

        return render_template('index.html',
                               latest_draw=latest_draw,
                               recent_draw=recent_draw)
    except Exception as e:
        logger.error(f"메인 페이지 렌더링 중 오류: {str(e)}")
        # 오류 발생 시에도 기본 페이지 렌더링
        return render_template('index.html',
                               latest_draw="정보 없음",
                               recent_draw=None)


@app.route('/generate', methods=['POST'])
def generate_numbers():
    """현재 설정 기반으로 로또 번호 생성"""
    try:
        games_count = int(request.form.get('games_count', 5))

        # 입력 유효성 검사
        if games_count < 1 or games_count > 20:
            return jsonify({
                'success': False,
                'error': '게임 수는 1-20 사이의 값이어야 합니다.'
            })

        # 사용자 설정 불러오기
        config = LottoConfig()
        if 'config' in session:
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
    except ValueError as e:
        logger.error(f"입력값 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '입력값이 올바르지 않습니다.'
        })
    except Exception as e:
        logger.error(f"번호 생성 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '번호 생성 중 오류가 발생했습니다. 설정을 확인해주세요.'
        })


@app.route('/update-config', methods=['POST'])
def update_config():
    """설정 업데이트"""
    try:
        # 세션에서 현재 설정 가져오기
        config_dict = session.get('config', vars(LottoConfig()))

        # 규칙 활성화 상태 업데이트
        for rule in config_dict.get('rules_enabled', {}):
            if f'rule_{rule}' in request.form:
                config_dict['rules_enabled'][rule] = request.form.get(f'rule_{rule}') == 'true'

        # 범위 및 값 업데이트 (입력 유효성 검사 추가)
        try:
            # 총합 범위
            if 'sum_min' in request.form and 'sum_max' in request.form:
                sum_min = int(request.form['sum_min'])
                sum_max = int(request.form['sum_max'])
                if 21 <= sum_min <= sum_max <= 279:
                    config_dict['sum_range'] = (sum_min, sum_max)

            # AC 값
            if 'ac_value_min' in request.form:
                ac_min = int(request.form['ac_value_min'])
                if 0 <= ac_min <= 15:
                    config_dict['ac_value_min'] = ac_min

            # 기타 설정들 (각각 유효성 검사)
            if 'prime_min' in request.form and 'prime_max' in request.form:
                prime_min = int(request.form['prime_min'])
                prime_max = int(request.form['prime_max'])
                if 0 <= prime_min <= prime_max <= 6:
                    config_dict['prime_range'] = (prime_min, prime_max)

        except ValueError:
            return jsonify({
                'success': False,
                'error': '설정값이 올바르지 않습니다.'
            })

        # 업데이트된 설정을 세션에 저장
        session['config'] = config_dict

        return jsonify({
            'success': True,
            'message': '설정이 성공적으로 업데이트되었습니다.'
        })
    except Exception as e:
        logger.error(f"설정 업데이트 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '설정 업데이트 중 오류가 발생했습니다.'
        })


@app.route('/reset-config', methods=['POST'])
def reset_config():
    """설정을 기본값으로 초기화"""
    try:
        session['config'] = vars(LottoConfig())
        return jsonify({
            'success': True,
            'message': '설정이 기본값으로 초기화되었습니다.'
        })
    except Exception as e:
        logger.error(f"설정 초기화 중 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '설정 초기화 중 오류가 발생했습니다.'
        })


@app.route('/stats', methods=['GET'])
def get_stats():
    """로또 데이터베이스에서 통계 데이터 조회"""
    try:
        if db:
            # 데이터베이스에서 통계 데이터 가져오기
            stats = db.get_stats_for_dashboard()
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            # 데이터베이스가 없을 때 샘플 데이터 반환
            logger.warning("데이터베이스 연결 없이 샘플 통계 데이터 반환")
            stats = generate_sample_stats()
            return jsonify({
                'success': True,
                'stats': stats,
                'is_sample': True
            })
    except Exception as e:
        logger.error(f"통계 데이터 조회 중 오류: {str(e)}")
        # 오류 발생 시 샘플 데이터 반환
        stats = generate_sample_stats()
        return jsonify({
            'success': True,
            'stats': stats,
            'is_sample': True,
            'error_message': '실제 데이터를 불러올 수 없어 샘플 데이터를 표시합니다.'
        })


@app.route('/health')
def health_check():
    """헬스 체크 엔드포인트"""
    try:
        db_status = "connected" if db else "disconnected"
        return jsonify({
            'status': 'healthy',
            'database': db_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/offline')
def offline():
    """오프라인 페이지"""
    return render_template('offline.html')


# 오류 핸들러
@app.errorhandler(404)
def page_not_found(e):
    """404 오류 페이지"""
    logger.warning(f"404 오류: {request.url}")
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """500 오류 페이지"""
    logger.error(f"500 오류: {str(e)}")
    return render_template('500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """모든 예외 처리"""
    logger.error(f"예상치 못한 오류: {str(e)}")

    # AJAX 요청인 경우 JSON 응답
    if request.is_json or request.headers.get('Content-Type') == 'application/json':
        return jsonify({
            'success': False,
            'error': '서버에서 오류가 발생했습니다.'
        }), 500

    # 일반 요청인 경우 오류 페이지
    return render_template('500.html'), 500


if __name__ == '__main__':
    # 환경 변수에서 설정 읽기
    import os

    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')

    logger.info(f"서버 시작: {host}:{port}, 디버그 모드: {debug_mode}")
    app.run(debug=debug_mode, host=host, port=port)
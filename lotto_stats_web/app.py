# app.py - 메인 애플리케이션
from flask import Flask
import os
from config import Config

# 컨트롤러 임포트
from controllers.main_controller import main_bp
from controllers.api_controller import api_bp
from controllers.stats_controller import stats_bp


# 애플리케이션 팩토리 함수
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 데이터 디렉토리 생성
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(app.config['CACHE_DIR'], exist_ok=True)

    # 데이터베이스 초기화 체크
    from utils.db_connector import DatabaseConnector
    db_exists = os.path.exists(app.config['DB_PATH'])
    if not db_exists:
        app.logger.info(f"데이터베이스가 존재하지 않습니다. 초기화합니다: {app.config['DB_PATH']}")
        DatabaseConnector.init_db()

    # 블루프린트 등록
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/stats')

    # 오류 핸들러
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('pages/error.html',
                               error="페이지를 찾을 수 없습니다",
                               code=404), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('pages/error.html',
                               error="서버 내부 오류가 발생했습니다",
                               code=500), 500

    # CLI 명령 등록
    @app.cli.command('init-db')
    def init_db_command():
        """데이터베이스 초기화 명령"""
        from utils.db_connector import DatabaseConnector
        print('데이터베이스 초기화 중...')
        DatabaseConnector.init_db()
        print('데이터베이스 초기화 완료!')

    @app.cli.command('init-cache')
    def init_cache_command():
        """초기 캐시 생성 명령"""
        from services.cache_service import refresh_all_stats_cache
        print('캐시 초기화 중...')
        refresh_all_stats_cache(force=True)
        print('캐시 초기화 완료!')

    return app


# 런타임 실행을 위한 앱 인스턴스 생성
if __name__ == '__main__':
    from flask import render_template

    app = create_app()
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
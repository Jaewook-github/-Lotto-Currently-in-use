import logging
import os
import sys
from gui import LottoGUI
from db_manager import LottoDBManager

# 로깅 설정
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = 'logs'

# 로그 디렉토리 생성
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 로그 파일 설정
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'lotto_tapa.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('LottoTapa')


def main():
    """
    로또 타파 분석기 메인 실행 함수
    """
    logger.info("로또 타파 분석기 - AI 확장 버전 시작")

    # 데이터베이스 초기화 확인
    try:
        db_manager = LottoDBManager()
        last_draw = db_manager.get_last_draw_number()
        logger.info(f"데이터베이스 초기화 완료. 최신 회차: {last_draw}")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {str(e)}")

    # GUI 실행 (지연된 모델 로딩 사용)
    try:
        app = LottoGUI(delayed_ml_init=True)  # 지연된 ML 초기화 옵션 추가
        app.run()
    except Exception as e:
        logger.error(f"애플리케이션 실행 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()
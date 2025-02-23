# FileManager 클래스
# modules/file_manager.py
from pathlib import Path
from datetime import datetime
import logging
import shutil

class FileManager:
    """파일과 디렉토리를 관리하는 클래스"""
    def __init__(self):
        self.base_dir = Path('.')
        self.logs_dir = self.base_dir / 'logs'
        self.predictions_dir = self.base_dir / 'predictions'
        self.models_dir = self.base_dir / 'models'
        self.backups_dir = self.base_dir / 'backups'
        self.setup_directories()

    def setup_directories(self):
        """필요한 디렉토리를 생성"""
        for directory in [self.logs_dir, self.predictions_dir, self.models_dir, self.backups_dir]:
            try:
                directory.mkdir(exist_ok=True)
            except Exception as e:
                logging.error(f"디렉토리 생성 실패 {directory}: {str(e)}")

    def get_new_log_file(self) -> Path:
        """새로운 로그 파일 경로를 생성"""
        current_date = datetime.now().strftime('%Y%m%d')
        existing_logs = list(self.logs_dir.glob(f'lotto_prediction_{current_date}-*.log'))
        new_number = 1 if not existing_logs else max([int(log.stem.split('-')[-1]) for log in existing_logs]) + 1
        return self.logs_dir / f'lotto_prediction_{current_date}-{new_number}.log'

    def get_prediction_file(self, extension: str) -> Path:
        """예측 결과 파일 경로 반환"""
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.predictions_dir / f'lotto_prediction_{current_datetime}.{extension}'

    def get_model_file(self) -> Path:
        """모델 저장 파일 경로 반환"""
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.models_dir / f'best_model_{current_datetime}.pkl'

    def backup_model(self, model_path: Path) -> Path:
        """모델 파일 백업 생성"""
        backup_path = self.backups_dir / f"{model_path.name}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            if model_path.exists():
                shutil.copy(model_path, backup_path)
                logging.info(f"모델 백업 완료: {backup_path}")
                return backup_path
        except Exception as e:
            logging.error(f"모델 백업 실패: {str(e)}")
        return None
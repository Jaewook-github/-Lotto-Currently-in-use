# ModelState 클래스
# modules/model_state.py
import copy
import pickle
import logging

class ModelState:
    """모델 상태를 저장하고 관리하는 클래스"""
    def __init__(self, numbers_memory=None, number_stats=None, score=0, ml_model=None):
        self.numbers_memory = numbers_memory if numbers_memory is not None else {}
        self.number_stats = number_stats if number_stats is not None else {}
        self.score = score
        self.ml_model = ml_model

    def copy(self):
        """현재 모델 상태의 깊은 복사본을 반환"""
        return ModelState(
            numbers_memory=copy.deepcopy(self.numbers_memory),
            number_stats=copy.deepcopy(self.number_stats),
            score=self.score,
            ml_model=copy.deepcopy(self.ml_model) if self.ml_model else None
        )

    def save_to_file(self, filepath):
        """모델 상태를 파일로 저장 (버전 정보 포함)"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump({
                    'version': '3.1',
                    'numbers_memory': self.numbers_memory,
                    'number_stats': self.number_stats,
                    'score': self.score,
                    'ml_model': self.ml_model
                }, f)
            logging.info(f"모델 저장 완료: {filepath}")
            return True
        except Exception as e:
            logging.error(f"모델 저장 실패: {str(e)}")
            return False

    @classmethod
    def load_from_file(cls, filepath):
        """파일에서 모델 상태를 로드 (버전 체크 포함)"""
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                if data.get('version', '1.0') < '3.0':
                    logging.warning("구형 모델 버전을 로드 중")
                return cls(
                    numbers_memory=data.get('numbers_memory', {}),
                    number_stats=data.get('number_stats', {}),
                    score=data.get('score', 0),
                    ml_model=data.get('ml_model', None)
                )
        except Exception as e:
            logging.error(f"모델 로드 실패: {str(e)}")
            return None
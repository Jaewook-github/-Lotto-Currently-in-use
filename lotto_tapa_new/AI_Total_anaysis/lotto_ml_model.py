import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
import joblib
import os
import logging
from db_manager import LottoDBManager
from feature_engineering import LottoFeatureEngineer

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LottoML')


class LottoMLModel:
    """
    로또 당첨 번호를 예측하기 위한 머신러닝 모델 클래스
    다양한 모델과 앙상블 기법을 사용하여 번호 출현 패턴을 학습하고 예측합니다.
    """

    def __init__(self, db_path='lotto.db'):
        """
        LottoMLModel 초기화

        Args:
            db_path: 로또 데이터베이스 파일 경로
        """
        self.db_manager = LottoDBManager(db_path)
        self.feature_engineer = LottoFeatureEngineer()
        self.model = None
        self.number_models = {}  # 각 번호별 개별 모델 저장
        self.models_dir = 'models'  # 모델 저장 디렉토리

        # 모델 저장 디렉토리 생성
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)

    def prepare_data(self):
        """
        학습 데이터 준비: 데이터베이스에서 로또 당첨 번호를 가져와 학습 데이터로 변환

        Returns:
            tuple: (X, y) 형태의 학습 데이터와 라벨
        """
        logger.info("데이터 준비 시작")

        # DB에서 로또 데이터 가져오기
        lotto_data = self.db_manager.fetch_all_draws()

        if not lotto_data:
            logger.error("로또 데이터를 가져오지 못했습니다.")
            return None, None

        logger.info(f"총 {len(lotto_data)} 회차 데이터를 로드했습니다.")

        # 데이터프레임 생성
        df = pd.DataFrame(lotto_data, columns=['draw_number', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus'])

        # 특성 엔지니어링
        X, y = self.feature_engineer.create_features(df)

        logger.info(f"특성 엔지니어링 완료: {X.shape[1]} 개의 특성 생성")

        return X, y

    def train_models(self):
        """
        다양한 머신러닝 모델을 학습합니다.
        - 번호별 개별 모델 (각 숫자의 출현 여부 예측)
        - 앙상블 모델 (최종 번호 조합 평가)
        """
        logger.info("모델 학습 시작")

        X, y = self.prepare_data()
        if X is None or len(X) < 100:  # 최소한의 데이터가 필요
            logger.error("학습에 충분한 데이터가 없습니다.")
            return False

        # 1. 번호별 개별 모델 학습 (1~45 각 숫자에 대해)
        self._train_individual_number_models(X)

        # 2. 번호 조합 평가 모델 학습
        self._train_combination_evaluation_model(X, y)

        logger.info("모델 학습 완료")
        return True

    def _train_individual_number_models(self, X):
        """
        각 번호(1~45)에 대한 개별 출현 확률 예측 모델 학습

        Args:
            X: 학습 데이터
        """
        logger.info("번호별 개별 모델 학습 시작")

        # 숫자 범위를 1~45로 제한
        for num in range(1, 46):
            try:
                # 특성 이름 생성
                num_cols = [f'num{i}' for i in range(1, 7)]

                # 해당 번호가 당첨 번호에 포함되었는지 라벨 생성 (안전한 방식으로)
                def check_number_presence(row, num, num_cols):
                    try:
                        for col in num_cols:
                            if col in row and not pd.isna(row[col]) and row[col] == num:
                                return 1
                        return 0
                    except:
                        return 0

                y_num = X.apply(lambda row: check_number_presence(row, num, num_cols), axis=1)

                # 특정 번호와 관련된 특성만 선택
                X_reduced = self.feature_engineer.select_features_for_number(X, num)

                # 학습/테스트 세트 분리 (비어있지 않은지 확인)
                if len(X_reduced) > 10:  # 최소 데이터 개수 확인
                    X_train, X_test, y_train, y_test = train_test_split(
                        X_reduced, y_num, test_size=0.2, random_state=42, shuffle=True
                    )

                    # 모델 파이프라인 구성
                    pipeline = Pipeline([
                        ('scaler', StandardScaler()),
                        ('model', GradientBoostingClassifier(random_state=42))
                    ])

                    # 간소화된 하이퍼파라미터
                    pipeline.fit(X_train, y_train)

                    # 최적 모델 저장
                    self.number_models[num] = pipeline

                    # 모델 저장
                    model_path = os.path.join(self.models_dir, f'number_{num}_model.pkl')
                    joblib.dump(pipeline, model_path)

                    logger.info(f"번호 {num} 모델 학습 완료")
                else:
                    logger.warning(f"번호 {num}에 대한 학습 데이터가 부족합니다")

            except Exception as e:
                logger.error(f"번호 {num} 모델 학습 중 오류: {str(e)}")
                # 오류가 있어도 다음 번호로 계속 진행

    def _train_combination_evaluation_model(self, X, y):
        """
        번호 조합을 평가하는 앙상블 모델 학습

        Args:
            X: 학습 데이터
            y: 조합 평가 라벨 (당첨 여부 또는 순위)
        """
        logger.info("번호 조합 평가 모델 학습 시작")

        # 학습 데이터를 특성과 라벨로 분리
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # 앙상블 모델 파이프라인 구성
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('model', RandomForestClassifier(random_state=42, n_jobs=-1))
        ])

        # 하이퍼파라미터 최적화
        param_grid = {
            'model__n_estimators': [100, 200],
            'model__max_depth': [None, 10, 20],
            'model__min_samples_split': [2, 5, 10]
        }

        # GridSearchCV로 최적 파라미터 탐색
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=3, scoring='f1_weighted', n_jobs=-1
        )

        # 모델 학습
        grid_search.fit(X_train, y_train)

        # 최적 모델 저장
        self.model = grid_search.best_estimator_

        # 모델 성능 평가
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"조합 평가 모델 학습 완료 - 정확도: {accuracy:.4f}")
        logger.info(f"분류 보고서:\n{classification_report(y_test, y_pred)}")

        # 모델 저장
        joblib.dump(self.model, os.path.join(self.models_dir, 'combination_model.pkl'))

    def load_models(self):
        """
        저장된 모델 로드

        Returns:
            bool: 모델 로드 성공 여부
        """
        logger.info("저장된 모델 로드 시작")

        try:
            # 모델 디렉토리 존재 여부 확인
            if not os.path.exists(self.models_dir):
                logger.warning(f"모델 디렉토리가 없습니다: {self.models_dir}")
                return False

            # 번호별 개별 모델 로드
            loaded_models_count = 0
            for num in range(1, 46):
                model_path = os.path.join(self.models_dir, f'number_{num}_model.pkl')
                if os.path.exists(model_path):
                    try:
                        self.number_models[num] = joblib.load(model_path)
                        loaded_models_count += 1
                    except Exception as e:
                        logger.error(f"번호 {num} 모델 로드 실패: {str(e)}")

            # 조합 평가 모델 로드
            combo_model_path = os.path.join(self.models_dir, 'combination_model.pkl')
            if os.path.exists(combo_model_path):
                try:
                    self.model = joblib.load(combo_model_path)
                except Exception as e:
                    logger.error(f"조합 모델 로드 실패: {str(e)}")

            # 모델 로드 상태 확인
            if loaded_models_count > 0 or self.model is not None:
                logger.info(f"일부 모델 로드 성공: {loaded_models_count}/45 번호 모델, 조합 모델: {self.model is not None}")
                return True
            else:
                logger.warning("로드된 모델이 없습니다.")
                return False

        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {str(e)}")
            return False

        except Exception as e:
            logger.error(f"모델 로드 중 오류 발생: {str(e)}")
            return False

    def predict_numbers(self, n_combinations=5):
        """
        학습된 모델을 사용하여 로또 번호 조합 예측

        Args:
            n_combinations: 생성할 번호 조합의 개수

        Returns:
            list: 예측된 로또 번호 조합 리스트
        """
        logger.info(f"{n_combinations}개의 번호 조합 예측 시작")

        # 모델이 없으면 로드 시도
        if self.model is None:
            if not self.load_models():
                logger.warning("모델이 없어 훈련 시작")
                self.train_models()
                if self.model is None:
                    logger.error("모델 훈련 실패")
                    return []

        # 최근 회차 데이터로 기반 특성 생성
        recent_features = self.feature_engineer.create_recent_features(self.db_manager)

        # 각 번호(1~45)의 출현 확률 예측
        probabilities = {}
        for num in range(1, 46):
            if num in self.number_models:
                # 해당 번호에 필요한 특성만 선택
                num_features = self.feature_engineer.select_features_for_number(recent_features, num)
                # 확률 예측 (예측 확률의 두 번째 열 = 양성 클래스 확률)
                prob = self.number_models[num].predict_proba(num_features)[0][1]
                probabilities[num] = prob
            else:
                # 모델이 없는 경우 평균 확률 0.5 할당
                probabilities[num] = 0.5

        # 확률에 따라 번호 조합 생성
        combinations = []
        for _ in range(n_combinations * 10):  # 후보 조합을 더 많이 생성한 후 필터링
            # 확률 기반 가중치를 사용하여 번호 샘플링
            numbers = self._weighted_sample(probabilities, 6)
            combinations.append(sorted(numbers))

        # 중복 제거 및 조합 평가
        unique_combinations = [list(x) for x in set(tuple(x) for x in combinations)]

        # 각 조합을 평가하여 점수 매기기
        scored_combinations = []
        for combo in unique_combinations:
            combo_features = self.feature_engineer.create_combination_features(combo, recent_features)
            score = self._evaluate_combination(combo, combo_features)
            scored_combinations.append((combo, score))

        # 점수가 높은 순으로 정렬
        scored_combinations.sort(key=lambda x: x[1], reverse=True)

        # 상위 n_combinations개 반환
        result = [combo for combo, _ in scored_combinations[:n_combinations]]

        logger.info(f"{len(result)}개의 번호 조합 예측 완료")
        return result

    def _weighted_sample(self, probabilities, k):
        """
        확률에 따른 가중치 기반 샘플링

        Args:
            probabilities: 각 번호의 출현 확률 딕셔너리
            k: 선택할 샘플 수

        Returns:
            list: 선택된 k개의 샘플
        """
        numbers = list(probabilities.keys())
        weights = list(probabilities.values())

        # 표준화된 가중치 계산
        weights = np.array(weights) / sum(weights)

        # 중복 없이 k개 샘플링
        selected = np.random.choice(numbers, size=k, replace=False, p=weights)
        return selected.tolist()

    def _evaluate_combination(self, combination, features):
        """
        번호 조합의 품질 평가

        Args:
            combination: 평가할 번호 조합
            features: 해당 조합의 특성

        Returns:
            float: 조합 평가 점수
        """
        # 기본 평가: 앙상블 모델의 확률 예측
        if self.model:
            try:
                # 확률 예측 (양성 클래스 확률)
                probability = self.model.predict_proba(features)[0][1]
                base_score = probability
            except Exception as e:
                logger.error(f"조합 평가 중 오류 발생: {str(e)}")
                base_score = 0.5
        else:
            base_score = 0.5

        # 추가 휴리스틱 평가
        heuristic_score = self.feature_engineer.evaluate_combination_heuristically(combination)

        # 최종 점수 = 모델 점수(70%) + 휴리스틱 점수(30%)
        final_score = 0.7 * base_score + 0.3 * heuristic_score

        return final_score
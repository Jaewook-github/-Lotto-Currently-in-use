# modules/lotto_analyzer.py
import copy
import random
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


class LottoAnalyzer:
    """로또 번호 분석 및 예측 클래스 (머신러닝 포함)"""

    def __init__(self, learning_rate: float, log_manager, pattern_weights: dict = None, use_ml: bool = False):
        self.learning_rate = learning_rate
        self.log_manager = log_manager
        self.numbers_memory = {i: 1.0 for i in range(1, 46)}
        self.number_stats = {i: 0 for i in range(1, 46)}
        self.pattern_weights = pattern_weights or {
            'pair': 0.35, 'triple': 0.25, 'sequence': 0.15,
            'frequency': 0.15, 'recency': 0.10
        }
        self.use_ml = use_ml
        self.ml_model = None
        self.scaler = StandardScaler()
        self.number_patterns = {}
        self.triple_patterns = {}
        self.time_weights = {}

    def get_state(self):
        """현재 모델 상태 반환"""
        from .model_state import ModelState  # 내부 모듈 임포트
        return ModelState(
            numbers_memory=dict(self.numbers_memory),
            number_stats=dict(self.number_stats),
            ml_model=self.ml_model
        )

    def set_state(self, state):
        """모델 상태 설정"""
        self.numbers_memory = copy.deepcopy(state.numbers_memory)
        self.number_stats = copy.deepcopy(state.number_stats)
        self.ml_model = copy.deepcopy(state.ml_model)

    def analyze_patterns(self, historical_data):
        """과거 데이터를 분석해 패턴 추출"""
        total_draws = len(historical_data)
        for idx, row in historical_data.iterrows():
            numbers = sorted([row[f'num{i}'] for i in range(1, 7)])
            relative_time = (idx + 1) / total_draws

            for num in numbers:
                self.number_stats[num] = self.number_stats.get(num, 0) + 1
                self.time_weights[num] = relative_time

            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    pair = (numbers[i], numbers[j])
                    self.number_patterns[pair] = self.number_patterns.get(pair, 0) + 1

            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    for k in range(j + 1, len(numbers)):
                        triple = (numbers[i], numbers[j], numbers[k])
                        self.triple_patterns[triple] = self.triple_patterns.get(triple, 0) + 1

        self.log_manager.log_debug(f"number_stats: {self.number_stats}")
        self.log_manager.log_debug(f"time_weights: {self.time_weights}")
        self.log_manager.log_debug(f"number_patterns 상위 5개: {list(self.number_patterns.items())[:5]}")

    def train_ml_model(self, historical_data):
        if not self.use_ml:
            return
        try:
            if historical_data.empty or len(historical_data) < 10:
                raise ValueError("학습을 위한 데이터가 부족합니다 (최소 10개 회차 필요)")
            X = []
            y = []
            for _, row in historical_data.iterrows():
                numbers = [row[f'num{i}'] for i in range(1, 7)]
                # 기본 통계
                stats = [self.number_stats.get(n, 0) for n in range(1, 46)]
                # 시간 가중치
                time_weights = [self.time_weights.get(n, 0) for n in range(1, 46)]
                # 2개 번호 패턴 점수 (45개로 고정)
                pattern_scores = [0] * 45
                sorted_patterns = sorted(self.number_patterns.items(), key=lambda x: x[1], reverse=True)
                total_patterns = len(sorted_patterns)
                for i, (pattern, score) in enumerate(sorted_patterns[:50]):  # 상위 50개 패턴 사용
                    if len(pattern) == 2:
                        weight = score / (total_patterns - i)  # 점수 가중치 부드럽게 감소
                        pattern_scores[pattern[0] - 1] += weight
                        pattern_scores[pattern[1] - 1] += weight
                # 연속성 점수 (더 복잡한 패턴 반영)
                sequence_score = [0] * 45
                for i in range(1, 46):
                    if i < 45 and self.number_stats.get(i + 1, 0) > 0 and self.number_stats.get(i, 0) > 0:
                        sequence_score[i - 1] += 1.0  # 1칸 차이
                    if i < 44 and self.number_stats.get(i + 2, 0) > 0 and self.number_stats.get(i, 0) > 0:
                        sequence_score[i - 1] += 0.7  # 2칸 차이
                    if i < 43 and self.number_stats.get(i + 3, 0) > 0 and self.number_stats.get(i, 0) > 0:
                        sequence_score[i - 1] += 0.4  # 3칸 차이
                    if i < 42 and self.number_stats.get(i + 4, 0) > 0 and self.number_stats.get(i, 0) > 0:
                        sequence_score[i - 1] += 0.2  # 4칸 차이
                # 최종 특성 (45 + 45 + 45 + 45 = 180)
                features = stats + time_weights + pattern_scores + sequence_score
                X.append(features)
                # 각 번호(1~45)에 대한 타겟 (선택된 번호는 1, 나머지는 0)
                target = [1 if i + 1 in numbers else 0 for i in range(45)]
                y.append(target)

            self.log_manager.log_debug(f"학습 데이터 X 크기: {len(X)}, y 크기: {len(y)}, 특성 수: {len(features)}")
            self.log_manager.log_debug(f"학습 데이터 X 샘플: {X[0][:10]}...")
            X_scaled = self.scaler.fit_transform(X)
            self.ml_model = MLPRegressor(hidden_layer_sizes=(300, 150, 50), max_iter=2000, learning_rate_init=0.001,
                                         activation='relu')
            self.ml_model.fit(X_scaled, y)
            self.log_manager.log_info("머신러닝 모델 학습 완료")
        except Exception as e:
            self.log_manager.log_error(f"머신러닝 학습 실패: {str(e)}")
            raise

    def select_numbers_by_ml(self, count: int) -> list:
        if not self.use_ml or not self.ml_model:
            return self.select_numbers_by_count(count)
        try:
            # 기본 통계, 시간 가중치, 패턴 점수, 연속성 점수 계산 (기존 로직 유지)
            stats = [self.number_stats.get(n, 0) for n in range(1, 46)]
            time_weights = [self.time_weights.get(n, 0) for n in range(1, 46)]
            pattern_scores = [0] * 45
            sorted_patterns = sorted(self.number_patterns.items(), key=lambda x: x[1], reverse=True)
            total_patterns = len(sorted_patterns)
            for i, (pattern, score) in enumerate(sorted_patterns[:50]):
                if len(pattern) == 2:
                    weight = score / (total_patterns - i)
                    pattern_scores[pattern[0] - 1] += weight
                    pattern_scores[pattern[1] - 1] += weight
            sequence_score = [0] * 45
            for i in range(1, 46):
                if i < 45 and self.number_stats.get(i + 1, 0) > 0 and self.number_stats.get(i, 0) > 0:
                    sequence_score[i - 1] += 1.0
                if i < 44 and self.number_stats.get(i + 2, 0) > 0 and self.number_stats.get(i, 0) > 0:
                    sequence_score[i - 1] += 0.7
                if i < 43 and self.number_stats.get(i + 3, 0) > 0 and self.number_stats.get(i, 0) > 0:
                    sequence_score[i - 1] += 0.4
                if i < 42 and self.number_stats.get(i + 4, 0) > 0 and self.number_stats.get(i, 0) > 0:
                    sequence_score[i - 1] += 0.2
            features = stats + time_weights + pattern_scores + sequence_score
            if len(features) != 180:
                raise ValueError(f"입력 데이터 크기가 올바르지 않습니다. 현재 크기: {len(features)}")
            self.log_manager.log_debug(f"특성 데이터: {features[:10]}... (총 길이: {len(features)})")
            X_scaled = self.scaler.transform([features])
            predictions = self.ml_model.predict(X_scaled)[0]  # 45개의 출력 (각 번호에 대한 점수)
            self.log_manager.log_debug(f"예측값: {predictions}")

            # 상위 점수 기반 번호 선택
            sorted_indices = np.argsort(predictions)[::-1]  # 점수 내림차순 정렬
            top_scores = [(i + 1, predictions[i]) for i in sorted_indices[:count * 2]]  # 상위 12개 (count * 2)
            self.log_manager.log_debug(f"top_scores: {top_scores}")

            # 점수에 비례한 확률로 번호 선택
            scores = [score for _, score in top_scores]
            total_score = sum(scores)
            probabilities = [score / total_score for score in scores]
            selected_indices = np.random.choice(len(top_scores), count, replace=False, p=probabilities)
            selected_numbers = sorted([top_scores[i][0] for i in selected_indices])

            self.log_manager.log_info(f"머신러닝으로 선택된 번호: {selected_numbers}")
            return selected_numbers
        except Exception as e:
            self.log_manager.log_error(f"머신러닝 예측 실패: {str(e)}")
            return self.select_numbers_by_count(count)

    def select_numbers_by_count(self, count: int) -> list:
        """기존 패턴 기반 번호 선택"""
        selected = []
        while len(selected) < count:
            scores = {}
            for num in range(1, 46):
                if num not in selected:
                    score = 0
                    pair_score = sum(self.number_patterns.get(tuple(sorted([num, sel])), 0)
                                     for sel in selected)
                    score += pair_score * self.pattern_weights['pair']

                    if len(selected) >= 2:
                        triple_score = 0
                        for i in range(len(selected)):
                            for j in range(i + 1, len(selected)):
                                triple = tuple(sorted([num, selected[i], selected[j]]))
                                triple_score += self.triple_patterns.get(triple, 0)
                        score += triple_score * self.pattern_weights['triple']

                    max_stats = max(self.number_stats.values()) or 1
                    frequency_score = self.number_stats.get(num, 0) / max_stats
                    score += frequency_score * self.pattern_weights['frequency']

                    recency_score = self.time_weights.get(num, 0)
                    score += recency_score * self.pattern_weights['recency']

                    scores[num] = score

            max_score = max(scores.values()) if scores else 0
            candidates = [n for n, s in scores.items() if s >= max_score * 0.8] if max_score > 0 else list(
                scores.keys())
            if candidates:
                selected.append(random.choice(candidates))

        return sorted(selected)
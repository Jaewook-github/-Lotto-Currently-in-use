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
        """머신러닝 모델 학습"""
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
                for i, (pattern, score) in enumerate(sorted_patterns[:30]):  # 상위 30개 패턴 사용
                    if len(pattern) == 2:
                        pattern_scores[pattern[0] - 1] = score
                        pattern_scores[pattern[1] - 1] = score
                # 연속성 점수 (더 복잡한 패턴 반영)
                sequence_score = [0] * 45
                for i in range(len(numbers) - 1):
                    if numbers[i + 1] - numbers[i] == 1:
                        sequence_score[numbers[i] - 1] += 1
                    if numbers[i + 1] - numbers[i] == 2:
                        sequence_score[numbers[i] - 1] += 0.7  # 2칸 차이
                    if numbers[i + 1] - numbers[i] == 3:
                        sequence_score[numbers[i] - 1] += 0.4  # 3칸 차이
                # 최종 특성 (45 + 45 + 45 + 45 = 180)
                features = stats + time_weights + pattern_scores + sequence_score
                X.append(features)
                y.append(numbers)

            self.log_manager.log_debug(f"학습 데이터 X 크기: {len(X)}, y 크기: {len(y)}, 특성 수: {len(features)}")
            self.log_manager.log_debug(f"학습 데이터 X 샘플: {X[0][:10]}...")
            X_scaled = self.scaler.fit_transform(X)
            self.ml_model = MLPRegressor(hidden_layer_sizes=(300, 150, 50), max_iter=2000, learning_rate_init=0.001)
            self.ml_model.fit(X_scaled, y)
            self.log_manager.log_info("머신러닝 모델 학습 완료")
        except Exception as e:
            self.log_manager.log_error(f"머신러닝 학습 실패: {str(e)}")
            raise

    def select_numbers_by_ml(self, count: int) -> list:
        if not self.use_ml or not self.ml_model:
            return self.select_numbers_by_count(count)
        try:
            # 기본 통계
            stats = [self.number_stats.get(n, 0) for n in range(1, 46)]
            # 시간 가중치
            time_weights = [self.time_weights.get(n, 0) for n in range(1, 46)]
            # 2개 번호 패턴 점수 (45개로 고정, 상위 50개 패턴 사용)
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
            if len(features) != 180:
                raise ValueError(f"입력 데이터 크기가 올바르지 않습니다. 현재 크기: {len(features)}")
            self.log_manager.log_debug(f"특성 데이터: {features[:10]}... (총 길이: {len(features)})")
            X_scaled = self.scaler.transform([features])
            predictions = self.ml_model.predict(X_scaled)[0]
            # 스케일링 및 노이즈 추가
            predictions_scaled = (predictions - np.min(predictions)) / (np.max(predictions) - np.min(predictions)) * 100
            noise = np.random.normal(0, 1.0, len(predictions_scaled))  # 노이즈 크기 0.5에서 1.0으로 증가
            predictions_with_noise = predictions_scaled + noise
            self.log_manager.log_debug(f"예측값 전 노이즈 추가: {predictions}")
            self.log_manager.log_debug(f"예측값 (스케일링 후 노이즈 추가): {predictions_with_noise}")
            # 상위 예측값에서 중복 제거 후 후보 선택
            sorted_indices = np.unique(np.argsort(predictions_with_noise)[::-1])  # 중복 제거
            self.log_manager.log_debug(f"sorted_indices 길이: {len(sorted_indices)}")
            if len(sorted_indices) < count:  # 최소 count개 후보 보장
                raise ValueError(f"후보 번호가 부족합니다. 현재 후보 수: {len(sorted_indices)}")
            candidates = sorted_indices[:min(len(sorted_indices), count * 5)]  # 더 많은 후보 선택 (최대 30개)
            self.log_manager.log_debug(f"candidates: {candidates}")
            # 중복 제거된 번호 리스트에서 count개 무작위 선택
            numbers = list(set([i + 1 for i in candidates]))  # 중복 제거
            self.log_manager.log_debug(f"numbers 길이: {len(numbers)}, numbers: {numbers}")
            if len(numbers) < count:
                # 후보가 부족할 경우, 모든 가능 번호에서 랜덤 보완
                remaining_numbers = [n for n in range(1, 46) if n not in numbers]
                numbers.extend(random.sample(remaining_numbers, min(count - len(numbers), len(remaining_numbers))))
                if len(numbers) < count:
                    raise ValueError(f"후보 번호를 확보할 수 없습니다. 현재 후보 수: {len(numbers)}")
            selected = sorted(random.sample(numbers, count))
            self.log_manager.log_info(f"머신러닝으로 선택된 번호: {selected}")
            return selected
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
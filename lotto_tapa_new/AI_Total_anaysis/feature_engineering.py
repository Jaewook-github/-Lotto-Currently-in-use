import numpy as np
import pandas as pd
from itertools import combinations
import logging
from collections import Counter
from scipy.stats import skew, kurtosis

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LottoFeature')


class LottoFeatureEngineer:
    """
    로또 번호에 대한 특성 엔지니어링 클래스
    머신러닝 모델에 사용될 다양한 특성들을 생성합니다.
    """

    def __init__(self):
        """
        LottoFeatureEngineer 초기화
        """
        # 소수 집합 (2, 3, 5, ... 43)
        self.prime_numbers = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}

        # 합성수 집합 (1, 4, 6, ... 45)
        self.composite_numbers = set(range(1, 46)) - self.prime_numbers

        # 로또용지의 모서리 패턴 정의 (7x6 행렬 기준)
        self.corner_patterns = {
            'top_left': {1, 2, 8, 9},  # 좌측 상단 모서리
            'top_right': {6, 7, 13, 14},  # 우측 상단 모서리
            'bottom_left': {29, 30, 36, 37, 43, 44},  # 좌측 하단 모서리 (수정됨)
            'bottom_right': {34, 35, 41, 42}  # 우측 하단 모서리
        }
        # 전체 모서리 숫자 집합
        self.corner_numbers = set().union(*self.corner_patterns.values())

        # 제곱수 집합 (1, 4, 9, 16, 25, 36)
        self.perfect_squares = {1, 4, 9, 16, 25, 36}

        # 쌍수 집합 (11, 22, 33, 44)
        self.twin_numbers = {11, 22, 33, 44}

    def create_features(self, df):
        """
        기본 데이터프레임에서 머신러닝에 사용될 특성 생성

        Args:
            df: 로또 당첨 결과 데이터프레임

        Returns:
            tuple: (X, y) 형태의 특성 행렬과 라벨 벡터
        """
        logger.info("특성 생성 시작")

        if df.empty:
            logger.error("빈 데이터프레임이 입력되었습니다.")
            return None, None

        # 당첨 번호를 숫자 리스트로 변환
        df['numbers'] = df.apply(lambda row: sorted([row[f'num{i}'] for i in range(1, 7)]), axis=1)

        # 시계열 특성 (회차 기준)
        X = pd.DataFrame({'draw_number': df['draw_number']})

        # 이전 회차의 번호 포함 여부 (10회차 이내)
        for lag in range(1, 11):
            if len(df) > lag:
                df[f'prev_{lag}_numbers'] = df['numbers'].shift(lag)
                X[f'prev_{lag}_overlap'] = df.apply(
                    lambda row: len(set(row['numbers']) & set(row[f'prev_{lag}_numbers']))
                    if pd.notna(row[f'prev_{lag}_numbers']).all()
                       and isinstance(row[f'prev_{lag}_numbers'], list)
                    else 0,
                    axis=1
                )

        # 통계적 특성
        # 1. 총합
        X['sum'] = df['numbers'].apply(sum)

        # 2. 평균
        X['mean'] = df['numbers'].apply(np.mean)

        # 3. 표준편차
        X['std'] = df['numbers'].apply(np.std)

        # 4. 중앙값
        X['median'] = df['numbers'].apply(np.median)

        # 5. 범위 (최대값 - 최소값)
        X['range'] = df['numbers'].apply(lambda x: max(x) - min(x))

        # 6. 첨도
        X['kurtosis'] = df['numbers'].apply(lambda x: kurtosis(x))

        # 7. 왜도
        X['skewness'] = df['numbers'].apply(lambda x: skew(x))

        # 번호 패턴 특성
        # 1. 연속된 번호 쌍의 수
        X['consecutive_pairs'] = df['numbers'].apply(
            lambda x: sum(1 for i in range(len(x) - 1) if x[i + 1] - x[i] == 1)
        )

        # 2. 홀수 개수
        X['odd_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n % 2 == 1))

        # 3. 짝수 개수
        X['even_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n % 2 == 0))

        # 4. 고번호(23-45) 개수
        X['high_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n >= 23))

        # 5. 저번호(1-22) 개수
        X['low_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n < 23))

        # 6. 소수 개수
        X['prime_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in self.prime_numbers))

        # 7. 합성수 개수
        X['composite_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in self.composite_numbers))

        # 8. 끝수(일의 자리) 합
        X['last_digit_sum'] = df['numbers'].apply(lambda x: sum(n % 10 for n in x))

        # 9. 3의 배수 개수
        X['multiples_of_3'] = df['numbers'].apply(lambda x: sum(1 for n in x if n % 3 == 0))

        # 10. 5의 배수 개수
        X['multiples_of_5'] = df['numbers'].apply(lambda x: sum(1 for n in x if n % 5 == 0))

        # 11. 제곱수 개수
        X['perfect_square_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in self.perfect_squares))

        # 12. 쌍수(11,22,33,44) 개수
        X['twin_number_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in self.twin_numbers))

        # 13. 모서리 숫자 개수
        X['corner_number_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in self.corner_numbers))

        # 14. 각 모서리별 숫자 개수
        for corner, nums in self.corner_patterns.items():
            X[f'{corner}_count'] = df['numbers'].apply(lambda x: sum(1 for n in x if n in nums))

        # 15. AC값 (번호 간 차이의 다양성)
        X['ac_value'] = df['numbers'].apply(self._calculate_ac_value)

        # 16. 번호 밀집도 (평균 간격 = range / 5)
        X['density'] = X['range'] / 5

        # 17. 균형 점수 (홀짝, 고저 비율의 균형)
        X['balance_score'] = abs(X['odd_count'] - X['even_count']) + abs(X['high_count'] - X['low_count'])

        # 18. 10의 자리 분포 (구간별 번호 개수)
        for decade in range(0, 5):
            start = decade * 10 + 1
            end = start + 9
            X[f'decade_{decade}'] = df['numbers'].apply(
                lambda x: sum(1 for n in x if start <= n <= end)
            )

        # 19. 번호 간 간격의 평균 및 표준편차
        X['gaps_mean'] = df['numbers'].apply(
            lambda x: np.mean([x[i + 1] - x[i] for i in range(len(x) - 1)])
        )
        X['gaps_std'] = df['numbers'].apply(
            lambda x: np.std([x[i + 1] - x[i] for i in range(len(x) - 1)])
        )

        # 20. 가중 번호 - 위치별 가중치 적용
        X['weighted_sum'] = df.apply(
            lambda row: sum((6 - i) * row[f'num{i + 1}'] for i in range(6)),
            axis=1
        )

        # 21. 대칭성 점수 (중앙값으로부터의 거리 합)
        X['symmetry_score'] = df['numbers'].apply(
            lambda x: sum(abs(n - np.median(x)) for n in x)
        )

        # 22. 서로 다른 숫자 쌍 간의 최대공약수(GCD)의 평균
        def get_mean_gcd(numbers):
            import math
            gcds = []
            for i, j in combinations(numbers, 2):
                gcds.append(math.gcd(i, j))
            return np.mean(gcds) if gcds else 0

        X['mean_gcd'] = df['numbers'].apply(get_mean_gcd)

        # 23. 서로 다른 숫자 쌍 간의 최소공배수(LCM)의 평균
        def get_mean_lcm(numbers):
            import math
            lcms = []
            for i, j in combinations(numbers, 2):
                lcms.append((i * j) // math.gcd(i, j))
            return np.mean(lcms) if lcms else 0

        X['mean_lcm'] = df['numbers'].apply(get_mean_lcm)

        # 24. 번호별 빈도수 기반 확률값
        # 전체 번호의 빈도를 계산
        all_numbers = []
        for nums in df['numbers']:
            if isinstance(nums, list) and nums:  # 유효한 리스트인지 확인
                all_numbers.extend(nums)
        freq_dict = Counter(all_numbers)
        total_draws = len(df)

        # 각 번호의 확률을 계산
        prob_dict = {num: count / (total_draws * 6) for num, count in freq_dict.items()}

        # 각 번호 조합의 확률 기대값 계산
        X['prob_expectation'] = df['numbers'].apply(
            lambda x: np.mean([prob_dict.get(n, 0) for n in x])
        )

        # 각 위치별 번호 빈도 기반 확률 계산
        for pos in range(1, 7):
            pos_freq = Counter(df[f'num{pos}'])
            pos_prob = {num: count / total_draws for num, count in pos_freq.items()}

            X[f'pos{pos}_prob'] = df.apply(
                lambda row: pos_prob.get(row[f'num{pos}'], 0),
                axis=1
            )

        # 라벨 생성 (다음 회차 번호 포함 여부)
        # 기본적으로 모든 회차는 성공적인 번호 조합으로 간주
        y = np.ones(len(df))

        logger.info(f"특성 생성 완료: {X.shape[1]} 개의 특성 생성")

        return X, y

    def _calculate_ac_value(self, numbers):
        """
        AC값 계산 (Arithmetic Complexity)
        주어진 번호들 간의 차이값의 다양성을 측정

        Args:
            numbers: 6개의 로또 번호 리스트

        Returns:
            int: 고유한 차이값의 개수 - 5
        """
        differences = set()  # 중복 제거를 위해 set 사용
        for i, j in combinations(sorted(numbers), 2):
            differences.add(j - i)  # 모든 가능한 두 수의 차이 계산
        return len(differences) - 5  # 총 차이값 개수에서 5를 뺀 값 반환

    def select_features_for_number(self, X, number):
        """
        특정 번호 예측에 사용될 특성만 선택

        Args:
            X: 모든 특성이 포함된 데이터프레임
            number: 타겟 번호

        Returns:
            pandas.DataFrame: 선택된 특성들
        """
        # 특정 번호와 밀접한 특성만 선택
        # 1. 기본 통계 특성
        basic_features = ['draw_number', 'sum', 'mean', 'std', 'range', 'median']

        # 2. 번호 속성 관련 특성
        number_property_features = []

        # 소수 여부
        if number in self.prime_numbers:
            number_property_features.append('prime_count')

        # 합성수 여부
        if number in self.composite_numbers:
            number_property_features.append('composite_count')

        # 홀짝 여부
        if number % 2 == 0:
            number_property_features.append('even_count')
        else:
            number_property_features.append('odd_count')

        # 고저 여부
        if number >= 23:
            number_property_features.append('high_count')
        else:
            number_property_features.append('low_count')

        # 배수 여부
        if number % 3 == 0:
            number_property_features.append('multiples_of_3')
        if number % 5 == 0:
            number_property_features.append('multiples_of_5')

        # 제곱수 여부
        if number in self.perfect_squares:
            number_property_features.append('perfect_square_count')

        # 쌍수 여부
        if number in self.twin_numbers:
            number_property_features.append('twin_number_count')

        # 모서리 번호 여부
        if number in self.corner_numbers:
            number_property_features.append('corner_number_count')

            # 어느 모서리에 속하는지
            for corner, nums in self.corner_patterns.items():
                if number in nums:
                    number_property_features.append(f'{corner}_count')

        # 10의 자리 구간
        decade = (number - 1) // 10
        number_property_features.append(f'decade_{decade}')

        # 3. 해당 번호의 이전 출현 패턴
        prev_features = [col for col in X.columns if col.startswith('prev_')]

        # 4. 복합 특성
        complex_features = ['ac_value', 'density', 'balance_score', 'gaps_mean',
                            'gaps_std', 'weighted_sum', 'symmetry_score', 'prob_expectation']

        # 5. 번호 위치별 확률
        pos_features = [f'pos{pos}_prob' for pos in range(1, 7)]

        # 모든 필요한 특성 결합
        selected_features = basic_features + number_property_features + prev_features + complex_features + pos_features

        # 존재하는 특성만 선택
        selected_features = [f for f in selected_features if f in X.columns]

        return X[selected_features]

    def create_recent_features(self, db_manager):
        """
        최근 회차의 데이터를 기반으로 예측에 필요한 특성 생성

        Args:
            db_manager: 데이터베이스 관리자 객체

        Returns:
            pandas.DataFrame: 최근 회차의 특성 데이터프레임
        """
        # 최근 100회차 데이터 가져오기
        recent_draws = db_manager.get_recent_draws(100)
        if not recent_draws:
            logger.error("최근 회차 데이터를 가져오지 못했습니다.")
            return pd.DataFrame()

        # 데이터프레임으로 변환
        df = pd.DataFrame(recent_draws)

        # 특성 생성에 필요한 형식으로 변환
        df['numbers'] = df.apply(lambda row: sorted([row[f'num{i}'] for i in range(1, 7)]), axis=1)

        # 특성 생성
        X, _ = self.create_features(df)

        # 가장 최근 회차의 특성만 반환
        return X.iloc[-1:].copy()

    def create_combination_features(self, combination, base_features=None):
        """
        주어진 번호 조합에 대한 특성 생성

        Args:
            combination: 평가할 번호 조합 (6개 숫자 리스트)
            base_features: 기본 특성 정보 (없으면 새로 계산)

        Returns:
            pandas.DataFrame: 해당 조합의 특성 데이터프레임
        """
        # 번호 조합을 정렬
        numbers = sorted(combination)

        # 기본 특성 DataFrame 생성
        X = pd.DataFrame(index=[0])

        # 기본 특성이 제공된 경우 복사
        if base_features is not None and not base_features.empty:
            for col in base_features.columns:
                if col != 'draw_number' and not col.startswith('prev_') and not col.startswith('pos'):
                    X[col] = base_features[col].values[-1]

        # 기본 통계 특성
        X['sum'] = sum(numbers)
        X['mean'] = np.mean(numbers)
        X['std'] = np.std(numbers)
        X['median'] = np.median(numbers)
        X['range'] = max(numbers) - min(numbers)
        X['kurtosis'] = kurtosis(numbers)
        X['skewness'] = skew(numbers)

        # 번호 패턴 특성
        # 연속된 번호 쌍의 수
        X['consecutive_pairs'] = sum(1 for i in range(len(numbers) - 1) if numbers[i + 1] - numbers[i] == 1)

        # 홀수 개수
        X['odd_count'] = sum(1 for n in numbers if n % 2 == 1)

        # 짝수 개수
        X['even_count'] = sum(1 for n in numbers if n % 2 == 0)

        # 고번호(23-45) 개수
        X['high_count'] = sum(1 for n in numbers if n >= 23)

        # 저번호(1-22) 개수
        X['low_count'] = sum(1 for n in numbers if n < 23)

        # 소수 개수
        X['prime_count'] = sum(1 for n in numbers if n in self.prime_numbers)

        # 합성수 개수
        X['composite_count'] = sum(1 for n in numbers if n in self.composite_numbers)

        # 끝수(일의 자리) 합
        X['last_digit_sum'] = sum(n % 10 for n in numbers)

        # 3의 배수 개수
        X['multiples_of_3'] = sum(1 for n in numbers if n % 3 == 0)

        # 5의 배수 개수
        X['multiples_of_5'] = sum(1 for n in numbers if n % 5 == 0)

        # 제곱수 개수
        X['perfect_square_count'] = sum(1 for n in numbers if n in self.perfect_squares)

        # 쌍수(11,22,33,44) 개수
        X['twin_number_count'] = sum(1 for n in numbers if n in self.twin_numbers)

        # 모서리 숫자 개수
        X['corner_number_count'] = sum(1 for n in numbers if n in self.corner_numbers)

        # 각 모서리별 숫자 개수
        for corner, nums in self.corner_patterns.items():
            X[f'{corner}_count'] = sum(1 for n in numbers if n in nums)

        # AC값 (번호 간 차이의 다양성)
        X['ac_value'] = self._calculate_ac_value(numbers)

        # 번호 밀집도 (평균 간격 = range / 5)
        X['density'] = X['range'] / 5

        # 균형 점수 (홀짝, 고저 비율의 균형)
        X['balance_score'] = abs(X['odd_count'] - X['even_count']) + abs(X['high_count'] - X['low_count'])

        # 10의 자리 분포 (구간별 번호 개수)
        for decade in range(0, 5):
            start = decade * 10 + 1
            end = start + 9
            X[f'decade_{decade}'] = sum(1 for n in numbers if start <= n <= end)

        # 번호 간 간격의 평균 및 표준편차
        gaps = [numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]
        X['gaps_mean'] = np.mean(gaps)
        X['gaps_std'] = np.std(gaps)

        # 가중 번호 - 위치별 가중치 적용
        X['weighted_sum'] = sum((6 - i) * numbers[i] for i in range(6))

        # 대칭성 점수 (중앙값으로부터의 거리 합)
        X['symmetry_score'] = sum(abs(n - np.median(numbers)) for n in numbers)

        # GCD 및 LCM 평균
        import math
        gcds = []
        lcms = []
        for i, j in combinations(numbers, 2):
            gcd = math.gcd(i, j)
            gcds.append(gcd)
            lcms.append((i * j) // gcd)

        X['mean_gcd'] = np.mean(gcds)
        X['mean_lcm'] = np.mean(lcms)

        return X

    def evaluate_combination_heuristically(self, combination):
        """
        번호 조합에 대한 휴리스틱 평가 점수 계산
        로또 타파 규칙 기반으로 0~1 사이의 점수 부여

        Args:
            combination: 평가할 번호 조합 (6개 숫자 리스트)

        Returns:
            float: 0~1 사이의 평가 점수
        """
        numbers = sorted(combination)

        # 각 규칙별 점수 (각각 0~1 사이 값)
        scores = {}

        # 1. 총합 규칙 (100~175)
        total_sum = sum(numbers)
        if 100 <= total_sum <= 175:
            # 이상적인 총합 구간(130~150)에 더 높은 점수 부여
            if 130 <= total_sum <= 150:
                scores['sum'] = 1.0
            else:
                # 거리에 따라 감소
                center = 140
                distance = abs(total_sum - center)
                scores['sum'] = max(0, 1.0 - (distance / 40))
        else:
            scores['sum'] = 0

        # 2. AC값 (7 이상)
        ac_value = self._calculate_ac_value(numbers)
        scores['ac'] = min(1.0, ac_value / 10)

        # 3. 홀짝 비율 (극단적 비율 제외)
        odd_count = sum(1 for n in numbers if n % 2 == 1)
        even_count = 6 - odd_count

        if odd_count == 0 or even_count == 0:
            scores['odd_even'] = 0
        elif odd_count == 3 and even_count == 3:  # 가장 이상적인 비율
            scores['odd_even'] = 1.0
        elif odd_count == 2 or odd_count == 4:  # 차선책
            scores['odd_even'] = 0.8
        else:  # 1:5 또는 5:1
            scores['odd_even'] = 0.5

        # 4. 고저 비율 (23 기준, 극단적 비율 제외)
        high_count = sum(1 for n in numbers if n >= 23)
        low_count = 6 - high_count

        if high_count == 0 or low_count == 0:
            scores['high_low'] = 0
        elif high_count == 3 and low_count == 3:  # 가장 이상적인 비율
            scores['high_low'] = 1.0
        elif high_count == 2 or high_count == 4:  # 차선책
            scores['high_low'] = 0.8
        else:  # 1:5 또는 5:1
            scores['high_low'] = 0.5

        # 5. 소수 개수 (0~3개 권장)
        prime_count = sum(1 for n in numbers if n in self.prime_numbers)
        if 1 <= prime_count <= 3:
            scores['prime'] = 1.0
        elif prime_count == 0:
            scores['prime'] = 0.7
        else:  # 4개 이상
            scores['prime'] = max(0, 1.0 - ((prime_count - 3) * 0.3))

        # 6. 연속수 패턴
        consecutive_pairs = sum(1 for i in range(len(numbers) - 1) if numbers[i + 1] - numbers[i] == 1)

        if consecutive_pairs == 0:
            scores['consecutive'] = 0.8  # 연속 번호 없음
        elif consecutive_pairs == 1:
            scores['consecutive'] = 1.0  # 2연속 1쌍 (가장 이상적)
        elif consecutive_pairs == 2:
            # 2연속 2쌍인지 3연속인지 확인
            has_three_consecutive = False
            for i in range(len(numbers) - 2):
                if numbers[i + 2] - numbers[i] == 2:
                    has_three_consecutive = True
                    break

            if has_three_consecutive:
                scores['consecutive'] = 0.7  # 3연속
            else:
                scores['consecutive'] = 0.9  # 2연속 2쌍
        else:
            scores['consecutive'] = 0.4  # 3연속 이상

        # 7. 끝수 총합 (15~35)
        last_digit_sum = sum(n % 10 for n in numbers)
        if 15 <= last_digit_sum <= 35:
            # 이상적인 구간(20~30)에 더 높은 점수 부여
            if 20 <= last_digit_sum <= 30:
                scores['last_digit'] = 1.0
            else:
                # 거리에 따라 감소
                center = 25
                distance = abs(last_digit_sum - center)
                scores['last_digit'] = max(0, 1.0 - (distance / 10))
        else:
            scores['last_digit'] = 0

        # 8. 모서리 패턴 분석
        corner_count = sum(1 for n in numbers if n in self.corner_numbers)

        if 1 <= corner_count <= 4:
            scores['corner'] = 1.0
        elif corner_count == 0:
            scores['corner'] = 0.5
        else:  # 5개 이상
            scores['corner'] = 0.2

        # 각 모서리별 숫자 분포
        corner_distribution = {
            corner: sum(1 for n in numbers if n in number_set)
            for corner, number_set in self.corner_patterns.items()
        }

        # 한 모서리에 숫자가 몰리는 경우 감점
        max_per_corner = max(corner_distribution.values())
        if max_per_corner > 2:
            scores['corner_balance'] = 0.5
        else:
            scores['corner_balance'] = 1.0

        # 9. 배수 분석
        mult_3_count = sum(1 for n in numbers if n % 3 == 0)
        mult_5_count = sum(1 for n in numbers if n % 5 == 0)

        if 0 <= mult_3_count <= 3:
            scores['mult_3'] = 1.0
        else:
            scores['mult_3'] = 0.5

        if 0 <= mult_5_count <= 2:
            scores['mult_5'] = 1.0
        else:
            scores['mult_5'] = 0.5

        # 10. 제곱수 개수
        square_count = sum(1 for n in numbers if n in self.perfect_squares)
        if 0 <= square_count <= 1:
            scores['square'] = 1.0
        elif square_count == 2:
            scores['square'] = 0.7
        else:
            scores['square'] = 0.3

        # 11. 쌍수 개수
        twin_count = sum(1 for n in numbers if n in self.twin_numbers)
        if 0 <= twin_count <= 2:
            scores['twin'] = 1.0
        else:
            scores['twin'] = 0.3

        # 최종 점수 계산 (가중 평균)
        weights = {
            'sum': 1.0,
            'ac': 0.8,
            'odd_even': 1.0,
            'high_low': 1.0,
            'prime': 0.7,
            'consecutive': 0.9,
            'last_digit': 0.8,
            'corner': 0.7,
            'corner_balance': 0.5,
            'mult_3': 0.6,
            'mult_5': 0.6,
            'square': 0.6,
            'twin': 0.6
        }

        weighted_sum = sum(scores[rule] * weights[rule] for rule in scores)
        total_weight = sum(weights.values())

        final_score = weighted_sum / total_weight
        return final_score
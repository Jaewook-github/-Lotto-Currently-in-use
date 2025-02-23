"""
로또 6/45 종합 분석 시스템 (14개 분석 항목)
- 데이터베이스 연동
- 통계 분석
- 패턴 검출
- 보고서 자동 생성
"""

import sqlite3
from contextlib import closing
import pandas as pd
import numpy as np
from tabulate import tabulate
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
from dataclasses import dataclass
import scipy.stats as stats
from math import sqrt
from lotto_exporter import LottoExporter, AnalysisResult

# 데이터 클래스 정의 ----------------------------------------------------
@dataclass
class AnalysisConfig:
    """분석 설정값을 저장하는 데이터 클래스"""
    CORNER_NUMBERS: Dict[str, Set[int]]
    BALL_COLORS: Dict[str, range]
    COMPOSITE_NUMBERS: Set[int]
    PERFECT_SQUARES: Set[int]
    PRIME_NUMBERS: Set[int]
    MIRROR_GROUPS: List[Set[int]]
    MULTIPLES: Dict[str, Set[int]]
    EMOJI_MAP: Dict[str, str]


@dataclass
class AnalysisResult:
    """분석 결과를 저장하는 데이터 클래스"""
    corner_stats: pd.DataFrame
    ac_stats: pd.DataFrame
    consecutive_stats: pd.DataFrame
    color_stats: pd.DataFrame
    composite_stats: pd.DataFrame
    square_stats: pd.DataFrame
    mirror_stats: pd.DataFrame
    multiple_stats: pd.DataFrame
    prime_stats: pd.DataFrame
    last_digit_stats: pd.DataFrame
    palindrome_stats: pd.DataFrame
    double_stats: pd.DataFrame
    color_comb_stats: pd.DataFrame
    full_report: pd.DataFrame


# 상수 관리 클래스 ------------------------------------------------------
class LottoConstants:
    """로또 분석 상수 관리 클래스"""

    def __init__(self):
        self.config = self._init_constants()

    def _init_constants(self) -> AnalysisConfig:
        """모든 상수 초기화"""
        return AnalysisConfig(
            CORNER_NUMBERS=self._init_corners(),
            BALL_COLORS=self._init_ball_colors(),
            COMPOSITE_NUMBERS=self._init_composites(),
            PERFECT_SQUARES={n ** 2 for n in range(1, 7)},
            PRIME_NUMBERS=self._calculate_primes(45),
            MIRROR_GROUPS=self._init_mirror_groups(),
            MULTIPLES=self._init_multiples(),
            EMOJI_MAP=self._init_emojis()
        )

    def _init_corners(self) -> Dict[str, Set[int]]:
        """모서리 번호 정의 (4개 영역)"""
        return {
            '좌상단': {1, 2, 8, 9},
            '우상단': {6, 7, 13, 14},
            '좌하단': {29, 30, 36, 37, 43, 44},
            '우하단': {34, 35, 41, 42}
        }

    def _init_ball_colors(self) -> Dict[str, range]:
        """공 색상 범위 정의 (5색상)"""
        return {
            '노랑': range(1, 10),
            '파랑': range(11, 20),
            '빨강': range(21, 30),
            '검정': range(31, 40),
            '초록': range(41, 45)
        }

    def _init_composites(self) -> Set[int]:
        """합성수 정의 (1 포함)"""
        return {1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44}

    def _init_mirror_groups(self) -> List[Set[int]]:
        """동형수 그룹 정의 (7개 그룹)"""
        return [{12, 21}, {13, 31}, {14, 41}, {23, 32}, {24, 42}, {34, 43}, {6, 9}]

    def _init_multiples(self) -> Dict[str, Set[int]]:
        """배수 그룹 정의 (3,4,5 배수)"""
        return {
            '3배수': set(range(3, 46, 3)),
            '4배수': set(range(4, 45, 4)),
            '5배수': set(range(5, 46, 5))
        }

    def _init_emojis(self) -> Dict[str, str]:
        """색상 이모지 매핑"""
        return {
            '노랑': '🟡', '파랑': '🔵', '빨강': '🔴',
            '검정': '⚫', '초록': '🟢'
        }

    @staticmethod
    def _calculate_primes(max_num: int) -> Set[int]:
        """에라토스테네스의 체를 이용한 소수 계산"""
        sieve = [True] * (max_num + 1)
        sieve[0:2] = [False, False]
        for i in range(2, int(sqrt(max_num)) + 1):
            if sieve[i]:
                sieve[i * i: max_num + 1: i] = [False] * len(sieve[i * i: max_num + 1: i])
        return {i for i, is_prime in enumerate(sieve) if is_prime}


# 핵심 분석 엔진 --------------------------------------------------------
class LottoAnalyzer:
    """로또 분석 메인 클래스"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.constants = LottoConstants().config
        self.data = self._load_data()
        self.analysis_result = None

    def _load_data(self) -> pd.DataFrame:
        """데이터베이스에서 데이터 로드"""
        with closing(sqlite3.connect(self.db_path)) as conn:
            query = """SELECT draw_number, num1, num2, num3, num4, num5, num6 
                       FROM lotto_results ORDER BY draw_number"""
            return pd.read_sql(query, conn)

    def _preprocess_data(self) -> pd.DataFrame:
        """데이터 전처리 파이프라인"""
        df = self.data.copy()
        df['numbers'] = df[['num1', 'num2', 'num3', 'num4', 'num5', 'num6']].values.tolist()
        df['sorted_numbers'] = df['numbers'].apply(sorted)
        return df

    def _analyze_corners(self, df: pd.DataFrame) -> pd.DataFrame:
        """모서리 번호 분석"""
        all_corners = set().union(*self.constants.CORNER_NUMBERS.values())
        df['corner_count'] = df['numbers'].apply(
            lambda nums: len(set(nums) & all_corners))
        return df

    def _calculate_ac(self, numbers: List[int]) -> int:
        """AC 값 계산 (번호 분산 지표)"""
        sorted_nums = sorted(numbers, reverse=True)
        diffs = {a - b for i, a in enumerate(sorted_nums)
                 for b in sorted_nums[i + 1:]}
        return len(diffs) - 5

    def _find_consecutives(self, numbers: List[int]) -> List[List[int]]:
        """연속 번호 패턴 탐지"""
        sorted_nums = sorted(numbers)
        consecutives = []
        current = [sorted_nums[0]]

        for num in sorted_nums[1:]:
            if num == current[-1] + 1:
                current.append(num)
            else:
                if len(current) >= 2:
                    consecutives.append(current)
                current = [num]
        if len(current) >= 2:
            consecutives.append(current)
        return consecutives

    def _analyze_colors(self, df: pd.DataFrame) -> pd.DataFrame:
        """색상 패턴 분석"""

        def get_color(num: int) -> str:
            for color, rng in self.constants.BALL_COLORS.items():
                if num in rng:
                    return f"{color}{self.constants.EMOJI_MAP[color]}"
            return 'Unknown'

        color_data = df['numbers'].apply(
            lambda nums: Counter(get_color(n) for n in nums))

        df['color_count'] = color_data.apply(len)
        df['color_combination'] = color_data.apply(
            lambda x: '-'.join(f"{k}:{v}" for k, v in sorted(x.items())))
        return df

    def _analyze_number_properties(self, df: pd.DataFrame) -> pd.DataFrame:
        """수학적 속성 분석"""
        # 합성수
        df['composite'] = df['numbers'].apply(
            lambda nums: len(set(nums) & self.constants.COMPOSITE_NUMBERS))

        # 완전제곱수
        df['square'] = df['numbers'].apply(
            lambda nums: len(set(nums) & self.constants.PERFECT_SQUARES))

        # 동형수
        df['mirror'] = df['numbers'].apply(
            lambda nums: sum(any(n in group for n in nums)
                             for group in self.constants.MIRROR_GROUPS))

        # 배수 분석
        for name, multiples in self.constants.MULTIPLES.items():
            df[f'multi_{name}'] = df['numbers'].apply(
                lambda nums: len(set(nums) & multiples))

        # 소수
        df['prime'] = df['numbers'].apply(
            lambda nums: len(set(nums) & self.constants.PRIME_NUMBERS))

        return df

    def _analyze_special_numbers(self, df: pd.DataFrame) -> pd.DataFrame:
        """특수 번호 패턴 분석"""
        # 끝수합
        df['last_digit_sum'] = df['numbers'].apply(
            lambda nums: sum(num % 10 for num in nums))
        # df['last_digit_sum'] = df['numbers'].apply(
        #     lambda nums: sum(num % 10 for num in nums if num >= 10))

        # 회문수
        df['palindrome'] = df['numbers'].apply(
            lambda nums: len([n for n in nums if str(n) == str(n)[::-1] and n >= 10]))

        # 쌍수
        df['double'] = df['numbers'].apply(
            lambda nums: len([n for n in nums if 10 <= n <= 99 and str(n)[0] == str(n)[1]]))

        return df

    def _generate_statistics(self, df: pd.DataFrame) -> AnalysisResult:
        """통계 분석 파이프라인"""

        # 빈도 분석 생성 함수
        def create_freq_table(series: pd.Series, name: str) -> pd.DataFrame:
            freq = series.value_counts().sort_index()
            return pd.DataFrame({
                '횟수': freq,
                '비율(%)': (freq / len(series) * 100).round(2)
            }, index=pd.Index(freq.index, name=name))

        # 상위 10개 색상 조합
        color_comb_top10 = (
            df['color_combination'].value_counts().head(10)
            .reset_index()
            .rename(columns={'index': '조합', 'color_combination': '횟수'})
        )

        return AnalysisResult(
            corner_stats=create_freq_table(df['corner_count'], '모서리번호'),
            ac_stats=create_freq_table(df['ac_value'], 'AC값'),
            consecutive_stats=create_freq_table(
                df['consecutive'].apply(len), '연속패턴'),
            color_stats=create_freq_table(df['color_count'], '색상수'),
            composite_stats=create_freq_table(df['composite'], '합성수'),
            square_stats=create_freq_table(df['square'], '완전제곱수'),
            mirror_stats=create_freq_table(df['mirror'], '동형수'),
            multiple_stats=pd.concat([
                create_freq_table(df['multi_3배수'], '3배수'),
                create_freq_table(df['multi_4배수'], '4배수'),
                create_freq_table(df['multi_5배수'], '5배수')
            ], axis=1),
            prime_stats=create_freq_table(df['prime'], '소수'),
            last_digit_stats=create_freq_table(df['last_digit_sum'], '끝수합'),
            palindrome_stats=create_freq_table(df['palindrome'], '회문수'),
            double_stats=create_freq_table(df['double'], '쌍수'),
            color_comb_stats=color_comb_top10,
            full_report=df
        )

    def run_full_analysis(self) -> AnalysisResult:
        """전체 분석 실행"""
        df = self._preprocess_data()
        df = self._analyze_corners(df)
        df['ac_value'] = df['sorted_numbers'].apply(self._calculate_ac)
        df['consecutive'] = df['sorted_numbers'].apply(self._find_consecutives)
        df = self._analyze_colors(df)
        df = self._analyze_number_properties(df)
        df = self._analyze_special_numbers(df)
        self.analysis_result = self._generate_statistics(df)
        return self.analysis_result

    def generate_report(self):
        """분석 보고서 생성"""
        if not self.analysis_result:
            raise ValueError("먼저 run_full_analysis()를 실행해주세요.")

        result = self.analysis_result
        print("=" * 50)
        print("로또 6/45 종합 분석 리포트".center(50))
        print("=" * 50)

        sections = [
            ('1. 모서리 번호 분석', result.corner_stats),
            ('2. AC 값 분포', result.ac_stats),
            ('3. 연속 번호 패턴', result.consecutive_stats),
            ('4. 색상 패턴 분석', result.color_stats),
            ('5. 색상 조합 Top10', result.color_comb_stats),
            ('6. 합성수 분석', result.composite_stats),
            ('7. 완전제곱수 분석', result.square_stats),
            ('8. 동형수 분석', result.mirror_stats),
            ('9. 배수 분석', result.multiple_stats),
            ('10. 소수 분석', result.prime_stats),
            ('11. 끝수합 분석', result.last_digit_stats),
            ('12. 회문수 분석', result.palindrome_stats),
            ('13. 쌍수 분석', result.double_stats)
        ]

        for title, data in sections:
            print(f"\n{title}")
            print(tabulate(data, headers='keys', tablefmt='pretty', showindex=True))

        print("\n" + "=" * 50)
        print("분석이 완료되었습니다.".center(50))
        print("=" * 50)


# 실행 예제 ------------------------------------------------------------
if __name__ == "__main__":
    # 분석기 생성 및 분석 실행
    analyzer = LottoAnalyzer('../lotto.db')
    analyzer.run_full_analysis()

    analysis_result = analyzer.analysis_result

    # 리포트 생성
    analyzer.generate_report()

    # 엑셀/CSV 내보내기
    exporter = LottoExporter(analyzer.analysis_result)
    exporter.export_to_excel()
    exporter.export_to_csv()
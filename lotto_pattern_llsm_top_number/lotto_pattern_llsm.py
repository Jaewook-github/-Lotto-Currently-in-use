import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np
from datetime import datetime
import os
import threading
import logging
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import traceback
import sys
import matplotlib
import matplotlib.font_manager as fm
import copy
import pickle
import random
import math


class ModelState:
    """모델 상태를 관리하는 기본 클래스"""

    def __init__(self, numbers_memory=None, number_stats=None, score=0):
        self.numbers_memory = numbers_memory if numbers_memory is not None else {}
        self.number_stats = number_stats if number_stats is not None else {}
        self.score = score

    def copy(self):
        """현재 상태의 깊은 복사본을 반환"""
        return ModelState(
            numbers_memory=copy.deepcopy(self.numbers_memory),
            number_stats=copy.deepcopy(self.number_stats),
            score=self.score
        )

    def save_to_file(self, filepath):
        """현재 상태를 파일로 저장"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'numbers_memory': self.numbers_memory,
                'number_stats': self.number_stats,
                'score': self.score
            }, f)

    @classmethod
    def load_from_file(cls, filepath):
        """파일에서 상태를 로드"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            return cls(
                numbers_memory=data.get('numbers_memory', {}),
                number_stats=data.get('number_stats', {}),
                score=data.get('score', 0)
            )


class FileManager:
    """파일 및 디렉토리 관리 클래스"""

    def __init__(self):
        self.base_dir = Path('.')
        self.logs_dir = self.base_dir / 'logs'
        self.predictions_dir = self.base_dir / 'predictions'
        self.models_dir = self.base_dir / 'models'
        self.setup_directories()

    def setup_directories(self):
        """필요한 디렉토리 생성"""
        for directory in [self.logs_dir, self.predictions_dir, self.models_dir]:
            directory.mkdir(exist_ok=True)

    def get_new_log_file(self) -> Path:
        """새로운 로그 파일 경로 생성"""
        current_date = datetime.now().strftime('%Y%m%d')
        existing_logs = list(self.logs_dir.glob(f'lotto_prediction_{current_date}-*.log'))

        if not existing_logs:
            new_number = 1
        else:
            max_number = max([int(log.stem.split('-')[-1]) for log in existing_logs])
            new_number = max_number + 1

        return self.logs_dir / f'lotto_prediction_{current_date}-{new_number}.log'

    def get_prediction_file(self, extension: str) -> Path:
        """예측 결과 파일 경로 반환"""
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.predictions_dir / f'lotto_prediction_{current_datetime}.{extension}'

    def get_model_file(self) -> Path:
        """모델 저장 파일 경로 반환"""
        current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
        return self.models_dir / f'best_model_{current_datetime}.pkl'


class LogManager:
    """로깅 관리 클래스"""

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.setup_logging()

    def setup_logging(self):
        """로깅 설정"""
        log_file = self.file_manager.get_new_log_file()
        logger = logging.getLogger('LottoPrediction')
        logger.setLevel(logging.INFO)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)

        logger.handlers = []
        logger.addHandler(file_handler)
        self.logger = logger

    def log_info(self, message: str):
        """정보 로깅"""
        self.logger.info(message)

    def log_error(self, message: str, exc_info=None):
        """에러 로깅"""
        if exc_info:
            self.logger.error(message, exc_info=exc_info)
        else:
            self.logger.error(message)

    def log_debug(self, message: str):
        """디버그 정보 로깅"""
        if not message.startswith("Selected numbers"):
            self.logger.debug(message)

class DatabaseManager:
    """데이터베이스 관리 클래스"""

    def __init__(self, db_path: str, log_manager: LogManager):
        self.db_path = Path(db_path).absolute()  # 절대 경로로 변환
        self.log_manager = log_manager
        self.connection = None
        self.log_manager.log_info(f"Database path: {self.db_path}")  # 경로 로깅

    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.log_manager.log_info("Database connected successfully")
            return self.connection
        except Error as e:
            self.log_manager.log_error("Database connection error", exc_info=True)
            raise

    def get_historical_data(self, limit: int = None) -> pd.DataFrame:
        """당첨 이력 조회"""
        try:
            base_query = """
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus,
                       money1, money2, money3, money4, money5
                FROM lotto_results
            """

            if limit and str(limit).isdigit() and int(limit) > 0:
                query = f"""
                    {base_query}
                    WHERE draw_number IN (
                        SELECT draw_number
                        FROM lotto_results
                        ORDER BY draw_number DESC
                        LIMIT {limit}
                    )
                    ORDER BY draw_number ASC
                """
            else:
                query = f"{base_query} ORDER BY draw_number ASC"

            with self.connect() as conn:
                data_count = "전체" if not limit else limit
                self.log_manager.log_info(f"Retrieving {data_count} historical data")
                df = pd.read_sql_query(query, conn)
                self.log_manager.log_info(f"Retrieved {len(df)} records")
                return df

        except Exception as e:
            self.log_manager.log_error("Data retrieval error", exc_info=True)
            raise
# class DatabaseManager:
#     def __init__(self, db_path: str, log_manager: LogManager):
#         self.db_path = db_path
#         self.log_manager = log_manager
#         self.connection = None
#
#         # 데이터베이스 연결 테스트
#         try:
#             with sqlite3.connect(self.db_path) as conn:
#                 # 테이블 존재 여부 확인
#                 cursor = conn.cursor()
#                 cursor.execute("""
#                     SELECT name FROM sqlite_master
#                     WHERE type='table' AND name='lotto_results';
#                 """)
#                 if cursor.fetchone() is None:
#                     self.log_manager.log_error("lotto_results 테이블이 존재하지 않습니다.")
#                     raise Exception("lotto_results 테이블이 존재하지 않습니다.")
#
#                 # 테이블 구조 확인
#                 cursor.execute("PRAGMA table_info(lotto_results);")
#                 columns = cursor.fetchall()
#                 self.log_manager.log_info(f"테이블 구조: {columns}")
#
#         except sqlite3.Error as e:
#             self.log_manager.log_error(f"데이터베이스 연결 오류: {str(e)}")
#             raise
#
#     def connect(self):
#         """데이터베이스 연결"""
#         try:
#             self.connection = sqlite3.connect(self.db_path)
#             self.log_manager.log_info(f"Database connected successfully: {self.db_path}")
#             return self.connection
#         except sqlite3.Error as e:
#             self.log_manager.log_error(f"Database connection error: {str(e)}", exc_info=True)
#             raise

class LearningAnalyzer:
    """학습 과정 분석 클래스"""
    def __init__(self, log_manager):
        self.log_manager = log_manager
        self.learning_results = {}
        self.prize_counts = {}
        self.best_model = None
        self.best_score = 0

    def evaluate_model(self, analyzer, actual_numbers, iterations=100):
        """모델 성능 평가"""
        total_score = 0
        match_counts = {i: 0 for i in range(7)}  # 0~6개 일치 횟수

        for _ in range(iterations):
            predicted = analyzer.select_numbers_by_count(6)  # 6개 번호 선택
            matches = len(set(predicted) & set(actual_numbers))
            total_score += self._calculate_match_score(matches)
            match_counts[matches] += 1

        average_score = total_score / iterations
        return average_score, match_counts

    def _calculate_match_score(self, matches):
        """일치 개수에 따른 점수 계산"""
        score_table = {
            6: 1000,  # 1등
            5: 50,   # 2등/3등
            4: 20,   # 4등
            3: 5,    # 5등
            2: 1,    # 미당첨이지만 약간의 가치
            1: 0,    # 거의 무가치
            0: 0     # 완전 무가치
        }
        return score_table.get(matches, 0)

    def analyze_match(self, draw_number, actual_numbers, predicted_numbers):
        """회차별 당첨 번호 분석"""
        matches = set(predicted_numbers) & set(actual_numbers)
        match_count = len(matches)
        prize_rank = self._get_prize_rank(match_count)

        if draw_number not in self.prize_counts:
            self.prize_counts[draw_number] = {
                1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 0: 0  # 각 등수별 카운트
            }

        if prize_rank > 0:
            self.prize_counts[draw_number][prize_rank] += 1
        else:
            self.prize_counts[draw_number][0] += 1

        return {
            'draw_number': draw_number,
            'actual_numbers': actual_numbers,
            'predicted_numbers': predicted_numbers,
            'matches': matches,
            'match_count': match_count,
            'prize_rank': prize_rank
        }

    def _get_prize_rank(self, match_count):
        """당첨 등수 판정"""
        prize_ranks = {
            6: 1,  # 1등
            5: 2,  # 2등
            4: 3,  # 3등
            3: 4,  # 4등
            2: 5   # 5등
        }
        return prize_ranks.get(match_count, 0)

    def get_draw_summary(self, draw_number):
        """회차별 학습 결과 요약"""
        if draw_number in self.prize_counts:
            counts = self.prize_counts[draw_number]
            total_tries = sum(counts.values())

            return {
                'draw_number': draw_number,
                'total_tries': total_tries,
                'prize_counts': counts,
                'success_rate': {
                    rank: (count / total_tries * 100) if total_tries > 0 else 0
                    for rank, count in counts.items()
                }
            }
        return None


class LottoAnalyzer:
    """로또 번호 분석 및 예측 클래스"""

    def __init__(self, learning_rate: float, log_manager: LogManager, pattern_weights: dict = None):
        self.learning_rate = learning_rate
        self.log_manager = log_manager
        self.numbers_memory = {i: 1.0 for i in range(1, 46)}
        self.number_stats = {i: 0 for i in range(1, 46)}
        self.number_patterns = {}  # 2개 번호 연관성
        self.triple_patterns = {}  # 3개 번호 연관성
        self.sequence_patterns = []  # 연속 번호 패턴
        self.time_weights = {}  # 시간 가중치
        self.pattern_history = {}  # 패턴 출현 시점 기록

        # 기본 가중치 설정
        self.pattern_weights = pattern_weights or {
            'pair': 0.35,  # 2개 번호 패턴
            'triple': 0.25,  # 3개 번호 패턴
            'sequence': 0.15,  # 연속성
            'frequency': 0.15,  # 출현 빈도
            'recency': 0.10  # 최근성
        }

    def get_state(self) -> ModelState:
        """현재 모델 상태 반환"""
        return ModelState(
            numbers_memory=dict(self.numbers_memory),
            number_stats=dict(self.number_stats)
        )

    def set_state(self, state: ModelState):
        """모델 상태 설정"""
        self.numbers_memory = copy.deepcopy(state.numbers_memory)
        self.number_stats = copy.deepcopy(state.number_stats)

    def analyze_patterns(self, historical_data: pd.DataFrame):
        """패턴 분석"""
        total_draws = len(historical_data)

        for idx, row in historical_data.iterrows():
            draw_number = row['draw_number']
            relative_time = (idx + 1) / total_draws  # 시간 가중치 (0~1)
            numbers = sorted([row[f'num{i}'] for i in range(1, 7)])

            # 기본 출현 통계 및 시간 가중치
            for num in numbers:
                self.number_stats[num] = self.number_stats.get(num, 0) + 1
                self.time_weights[num] = relative_time

            # 2개 번호 패턴
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    pair = (numbers[i], numbers[j])
                    self.number_patterns[pair] = self.number_patterns.get(pair, 0) + 1

                    if pair not in self.pattern_history:
                        self.pattern_history[pair] = []
                    self.pattern_history[pair].append(draw_number)

            # 3개 번호 패턴
            for i in range(len(numbers)):
                for j in range(i + 1, len(numbers)):
                    for k in range(j + 1, len(numbers)):
                        triple = (numbers[i], numbers[j], numbers[k])
                        self.triple_patterns[triple] = self.triple_patterns.get(triple, 0) + 1

                        if triple not in self.pattern_history:
                            self.pattern_history[triple] = []
                        self.pattern_history[triple].append(draw_number)

            # 연속 번호 패턴
            for i in range(len(numbers) - 1):
                if numbers[i + 1] - numbers[i] == 1:
                    self.sequence_patterns.append((numbers[i], numbers[i + 1]))

        self._log_pattern_analysis()

    def _log_pattern_analysis(self):
        """패턴 분석 결과 로깅"""
        # 가장 빈번한 2개 번호 조합
        sorted_pairs = sorted(self.number_patterns.items(), key=lambda x: x[1], reverse=True)
        self.log_manager.log_info("\n=== 자주 출현하는 2개 번호 조합 ===")
        for (n1, n2), count in sorted_pairs[:10]:
            self.log_manager.log_info(f"조합 {n1}-{n2}: {count}회 출현")

        # 가장 빈번한 3개 번호 조합
        sorted_triples = sorted(self.triple_patterns.items(), key=lambda x: x[1], reverse=True)
        self.log_manager.log_info("\n=== 자주 출현하는 3개 번호 조합 ===")
        for (n1, n2, n3), count in sorted_triples[:10]:
            self.log_manager.log_info(f"조합 {n1}-{n2}-{n3}: {count}회 출현")

    def _calculate_pattern_recency(self, pattern):
        """패턴의 최근성 점수 계산"""
        if pattern not in self.pattern_history:
            return 0

        history = self.pattern_history[pattern]
        if not history:
            return 0

        latest_occurrence = max(history)
        all_history = [h for hist in self.pattern_history.values() for h in hist]
        max_draw = max(all_history) if all_history else 1  # 0으로 나누는 것 방지

        return latest_occurrence / max_draw if max_draw > 0 else 0

    def _calculate_sequence_score(self, numbers):
        """연속 번호 패턴 점수 계산"""
        if len(numbers) <= 1:
            return 0

        score = 0
        for i in range(len(numbers) - 1):
            if numbers[i + 1] - numbers[i] == 1:
                score += 1
        # 0으로 나누는 것을 방지
        return score / (len(numbers) - 1) if len(numbers) > 1 else 0

    def select_numbers_by_count(self, count: int) -> list:
        """패턴 기반 번호 선택"""
        selected = []

        while len(selected) < count:
            scores = {}
            for num in range(1, 46):
                if num not in selected:
                    score = 0

                    # 2개 번호 패턴 점수
                    pair_score = 0
                    for sel in selected:
                        pair = tuple(sorted([num, sel]))
                        pair_count = self.number_patterns.get(pair, 0)
                        pair_recency = self._calculate_pattern_recency(pair)
                        pair_score += pair_count * (1 + pair_recency)
                    score += pair_score * self.pattern_weights['pair']

                    # 3개 번호 패턴 점수
                    if len(selected) >= 2:
                        triple_score = 0
                        for i in range(len(selected)):
                            for j in range(i + 1, len(selected)):
                                triple = tuple(sorted([num, selected[i], selected[j]]))
                                triple_count = self.triple_patterns.get(triple, 0)
                                triple_recency = self._calculate_pattern_recency(triple)
                                triple_score += triple_count * (1 + triple_recency)
                        score += triple_score * self.pattern_weights['triple']

                    # 연속성 점수
                    temp_numbers = sorted(selected + [num])
                    sequence_score = self._calculate_sequence_score(temp_numbers)
                    score += sequence_score * self.pattern_weights['sequence']

                    # 출현 빈도 점수 계산 부분 수정
                    max_stats = max(self.number_stats.values())
                    frequency_score = (self.number_stats.get(num, 0) / max_stats) if max_stats > 0 else 0
                    score += frequency_score * self.pattern_weights['frequency']

                    scores[num] = score

                    # 최근성 점수
                    recency_score = self.time_weights.get(num, 0)
                    score += recency_score * self.pattern_weights['recency']

                    scores[num] = score

            # 다음 번호 선택
            max_score = max(scores.values()) if scores else 0
            if max_score > 0:
                threshold = max_score * 0.8
                candidates = [n for n, s in scores.items() if s >= threshold]
            else:
                candidates = list(scores.keys())

            if candidates:
                next_num = random.choice(candidates)
                selected.append(next_num)

        return sorted(selected)

class LottoPredictionGUI:
    """로또 예측 시스템 GUI 클래스"""

    def __init__(self, root):
        self.root = root
        self.root.title("로또 번호 예측 시스템 v3.0")
        self.root.geometry("1200x800")

        # 파일 및 로그 매니저 초기화
        self.file_manager = FileManager()
        self.log_manager = LogManager(self.file_manager)

        # 현재 스크립트의 디렉토리를 기준으로 데이터베이스 경로 설정
        current_dir = Path(__file__).parent
        db_path = current_dir / 'lotto.db'

        # 데이터베이스 매니저 초기화
        self.db_manager = DatabaseManager(str(db_path), self.log_manager)

        # 폰트 설정
        self.setup_fonts()

        # GUI 초기화
        self._setup_gui()
        self._setup_visualization()

        self.is_running = False
        self.best_model_state = None
        self.log_manager.log_info("Application started successfully")
    # def __init__(self, root):
    #     self.root = root
    #     self.root.title("로또 번호 예측 시스템 v3.0")
    #     self.root.geometry("1200x800")
    #
    #     # 파일 및 로그 매니저 초기화
    #     self.file_manager = FileManager()
    #     self.log_manager = LogManager(self.file_manager)
    #
    #     try:
    #         # 현재 실행 파일의 경로 확인
    #         current_path = os.path.dirname(os.path.abspath(__file__))
    #         db_path = os.path.join(current_path, 'lotto.db')
    #
    #         self.log_manager.log_info(f"데이터베이스 경로: {db_path}")
    #
    #         if not os.path.exists(db_path):
    #             self.log_manager.log_error(f"데이터베이스 파일이 존재하지 않습니다: {db_path}")
    #             raise FileNotFoundError(f"데이터베이스 파일을 찾을 수 없습니다: {db_path}")
    #
    #         # 데이터베이스 매니저 초기화
    #         self.db_manager = DatabaseManager(db_path, self.log_manager)
    #
    #         # GUI 초기화
    #         self.setup_fonts()
    #         self._setup_gui()
    #         self._setup_visualization()
    #
    #         self.is_running = False
    #         self.best_model_state = None
    #         self.log_manager.log_info("Application started successfully")
    #
    #     except Exception as e:
    #         self.log_manager.log_error(f"초기화 중 오류 발생: {str(e)}")
    #         messagebox.showerror("초기화 오류", str(e))
    #         raise

    def setup_fonts(self):
        """폰트 설정"""
        try:
            if sys.platform == 'win32':
                font_path = 'C:/Windows/Fonts/malgun.ttf'
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
            else:
                plt.rcParams['font.family'] = 'NanumGothic'

            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.size'] = 10

            # GUI 폰트 설정
            if sys.platform == 'win32':
                default_font = ('맑은 고딕', 9)
            else:
                default_font = ('NanumGothic', 9)

            style = ttk.Style()
            style.configure('TLabel', font=default_font)
            style.configure('TButton', font=default_font)

            self.font_config = {
                'default': default_font,
                'header': (default_font[0], 11),
                'title': (default_font[0], 10)
            }

        except Exception as e:
            self.log_manager.log_error(f"Font setup error: {str(e)}", exc_info=True)
            plt.rcParams['font.family'] = 'sans-serif'

    def _setup_gui(self):
        """GUI 구성요소 초기화"""
        # 노트북(탭) 생성
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

        # 탭 프레임 생성
        self.main_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.main_tab, text="예측")
        self.notebook.add(self.analysis_tab, text="분석")
        self.notebook.add(self.stats_tab, text="통계")

        self._create_main_tab()
        self._create_analysis_tab()
        self._create_stats_tab()

    def _create_main_tab(self):
        """메인 예측 탭 구성"""
        # 기본 설정 프레임
        settings_frame = ttk.LabelFrame(self.main_tab, text="기본 설정", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)

        # 선택 번호 개수 설정
        ttk.Label(settings_frame, text="선택 번호 개수:").grid(row=0, column=0, padx=5)
        self.numbers_var = tk.StringVar(value="6")
        ttk.Entry(settings_frame, textvariable=self.numbers_var, width=10).grid(row=0, column=1)

        # 학습 회차 설정
        ttk.Label(settings_frame, text="학습 회차:").grid(row=0, column=2, padx=5)
        self.learning_draws_var = tk.StringVar(value="100")
        self.learning_draws_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.learning_draws_var,
            values=["전체", "10", "30", "50", "100", "200"]
        )
        self.learning_draws_combo.grid(row=0, column=3, padx=5)

        # 학습률 설정
        ttk.Label(settings_frame, text="학습률:").grid(row=0, column=4, padx=5)
        self.learning_rate_var = tk.StringVar(value="0.1")
        ttk.Entry(settings_frame, textvariable=self.learning_rate_var, width=10).grid(row=0, column=5)

        # 반복 학습 횟수 설정
        ttk.Label(settings_frame, text="학습 반복:").grid(row=0, column=6, padx=5)
        self.iterations_var = tk.StringVar(value="100")
        ttk.Entry(settings_frame, textvariable=self.iterations_var, width=10).grid(row=0, column=7)

        # 가중치 설정 프레임
        weights_frame = ttk.LabelFrame(self.main_tab, text="패턴 가중치 설정", padding=10)
        weights_frame.pack(fill='x', padx=5, pady=5)

        # 가중치 설정
        self.weights = {
            'pair': tk.StringVar(value="35"),      # 2개 번호 패턴
            'triple': tk.StringVar(value="25"),    # 3개 번호 패턴
            'sequence': tk.StringVar(value="15"),  # 연속성
            'frequency': tk.StringVar(value="15"), # 출현 빈도
            'recency': tk.StringVar(value="10")    # 최근성
        }

        # 가중치 입력 필드
        ttk.Label(weights_frame, text="2개 번호 패턴 (%):").grid(row=0, column=0, padx=5, pady=2)
        ttk.Entry(weights_frame, textvariable=self.weights['pair'], width=8).grid(row=0, column=1)

        ttk.Label(weights_frame, text="3개 번호 패턴 (%):").grid(row=0, column=2, padx=5, pady=2)
        ttk.Entry(weights_frame, textvariable=self.weights['triple'], width=8).grid(row=0, column=3)

        ttk.Label(weights_frame, text="연속성 (%):").grid(row=0, column=4, padx=5, pady=2)
        ttk.Entry(weights_frame, textvariable=self.weights['sequence'], width=8).grid(row=0, column=5)

        ttk.Label(weights_frame, text="출현 빈도 (%):").grid(row=1, column=0, padx=5, pady=2)
        ttk.Entry(weights_frame, textvariable=self.weights['frequency'], width=8).grid(row=1, column=1)

        ttk.Label(weights_frame, text="최근성 (%):").grid(row=1, column=2, padx=5, pady=2)
        ttk.Entry(weights_frame, textvariable=self.weights['recency'], width=8).grid(row=1, column=3)

        # 가중치 초기화 버튼
        ttk.Button(weights_frame, text="가중치 초기화",
                  command=self._reset_weights).grid(row=1, column=5, padx=5)

        # 실행 버튼
        self.run_button = ttk.Button(settings_frame, text="예측 시작", command=self.run_prediction)
        self.run_button.grid(row=0, column=8, padx=10)

        # 로그 창
        log_frame = ttk.LabelFrame(self.main_tab, text="실행 로그", padding=10)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill='both', expand=True)

        # 결과 창
        results_frame = ttk.LabelFrame(self.main_tab, text="예측 결과", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.results_text = scrolledtext.ScrolledText(results_frame, height=10)
        self.results_text.pack(fill='both', expand=True)

        # 상태바
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(self.main_tab, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill='x', padx=5, pady=5)

        # 프로그레스바
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_tab,
            length=300,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill='x', padx=5)

    def _create_analysis_tab(self):
        """분석 탭 구성"""
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.analysis_tab)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def _create_stats_tab(self):
        """통계 탭 구성"""
        self.stats_text = scrolledtext.ScrolledText(self.stats_tab, height=30)
        self.stats_text.pack(fill='both', expand=True)

    def _reset_weights(self):
        """가중치 초기화"""
        default_weights = {
            'pair': "35",
            'triple': "25",
            'sequence': "15",
            'frequency': "15",
            'recency': "10"
        }
        for key, value in default_weights.items():
            self.weights[key].set(value)

    def _validate_weights(self):
        """가중치 유효성 검사"""
        try:
            weight_sum = sum(float(self.weights[key].get()) for key in self.weights)
            if not math.isclose(weight_sum, 100, rel_tol=1e-9):
                raise ValueError("가중치의 합이 100%가 되어야 합니다.")

            for key, var in self.weights.items():
                value = float(var.get())
                if value < 0 or value > 100:
                    raise ValueError(f"{key} 가중치는 0~100 사이여야 합니다.")

            return True
        except ValueError as e:
            messagebox.showerror("가중치 오류", str(e))
            return False

    def _setup_visualization(self):
        """시각화 초기 설정"""
        try:
            plt.style.use('default')

            # 그래프 설정
            self.fig.suptitle('로또 번호 분석')
            self.ax1.set_title('번호별 출현 빈도')
            self.ax2.set_title('당첨금 트렌드')

            # 그리드 설정
            self.ax1.grid(True, linestyle='--', alpha=0.7)
            self.ax2.grid(True, linestyle='--', alpha=0.7)

            # 축 레이블 설정
            self.ax1.set_xlabel('번호')
            self.ax1.set_ylabel('출현 횟수')
            self.ax2.set_xlabel('회차')
            self.ax2.set_ylabel('당첨금')

            # 여백 조정
            self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        except Exception as e:
            self.log_manager.log_error(f"Visualization setup error: {str(e)}", exc_info=True)
            raise

    def _setup_fonts(self):
        """폰트 설정"""
        try:
            if sys.platform == 'win32':
                font_path = 'C:/Windows/Fonts/malgun.ttf'
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
            else:
                plt.rcParams['font.family'] = 'NanumGothic'

            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.size'] = 10

            # GUI 폰트 설정
            if sys.platform == 'win32':
                default_font = ('맑은 고딕', 9)
            else:
                default_font = ('NanumGothic', 9)

            style = ttk.Style()
            style.configure('TLabel', font=default_font)
            style.configure('TButton', font=default_font)

            self.font_config = {
                'default': default_font,
                'header': (default_font[0], 11),
                'title': (default_font[0], 10)
            }

        except Exception as e:
            self.log_manager.log_error(f"Font setup error: {str(e)}", exc_info=True)
            plt.rcParams['font.family'] = 'sans-serif'

    def _prediction_thread(self):
        """예측 실행 스레드"""
        try:
            self.status_var.set("데이터 로딩 중...")
            self.log_manager.log_info("Starting prediction process")

            # 학습 회차 설정 적용
            draw_limit = None if self.learning_draws_var.get() == "전체" else int(self.learning_draws_var.get())
            historical_data = self.db_manager.get_historical_data(draw_limit)

            # 가중치 설정 가져오기
            pattern_weights = {
                key: float(value.get()) / 100
                for key, value in self.weights.items()
            }

            # 분석기 초기화
            self.analyzer = LottoAnalyzer(
                learning_rate=float(self.learning_rate_var.get()),
                log_manager=self.log_manager,
                pattern_weights=pattern_weights
            )

            learning_analyzer = LearningAnalyzer(self.log_manager)
            iterations = int(self.iterations_var.get())

            # 패턴 분석
            self.analyzer.analyze_patterns(historical_data)

            # 번호 선택
            self.status_var.set("번호 선택 중...")
            num_count = int(self.numbers_var.get())

            if num_count < 1 or num_count > 45:
                raise ValueError("선택 번호 개수는 1~45 사이여야 합니다")

            selected_numbers = self.analyzer.select_numbers_by_count(num_count)

            # 결과 분석 및 표시
            self._show_prediction_results(selected_numbers, historical_data)

            # 결과 저장
            self._save_prediction_results(selected_numbers)
            self._update_analysis_graphs(historical_data)
            self._update_stats_tab(historical_data)

            self.status_var.set("완료")
            self.log_manager.log_info("Prediction process completed successfully")
            messagebox.showinfo("완료", "예측이 완료되었습니다!")

        except Exception as e:
            self.log_manager.log_error("Prediction process error", exc_info=True)
            self.status_var.set("오류 발생")
            messagebox.showerror("오류", f"예측 중 오류가 발생했습니다: {str(e)}")
        finally:
            self.is_running = False
            self.run_button.config(text="예측 시작")
            self.progress_var.set(0)

    def run_prediction(self):
        """예측 실행"""
        try:
            if self.is_running:
                self.is_running = False
                self.run_button.config(text="예측 시작")
                return

            if not self._validate_weights():
                return

            self.is_running = True
            self.run_button.config(text="중지")
            thread = threading.Thread(target=self._prediction_thread)
            thread.daemon = True
            thread.start()

        except Exception as e:
            self.log_manager.log_error("Prediction initialization error", exc_info=True)
            messagebox.showerror("오류", f"예측 실행 중 오류가 발생했습니다: {str(e)}")

def main():
    try:
        root = tk.Tk()
        app = LottoPredictionGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
# LottoPredictionGUI 클래스
# modules/gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import matplotlib.font_manager as fm
import sys
import threading
import math
from pathlib import Path
from .file_manager import FileManager
from .log_manager import LogManager
from .database_manager import DatabaseManager
from .lotto_analyzer import LottoAnalyzer


class LottoPredictionGUI:
    """로또 예측 시스템 GUI 클래스"""

    def __init__(self, root):
        self.root = root
        self.root.title("로또 번호 예측 시스템 v3.1")
        self.root.geometry("1200x800")

        self.file_manager = FileManager()
        self.log_manager = LogManager(self.file_manager)
        self.use_ml_var = tk.BooleanVar(value=False)

        try:
            db_path = Path(__file__).parent.parent / 'lotto.db'  # 상위 디렉토리 참조
            self.db_manager = DatabaseManager(str(db_path), self.log_manager)

            self.setup_fonts()
            self._setup_gui()
            self._setup_visualization()

            self.is_running = False
            self.best_model_state = None

            self.log_manager.log_info("애플리케이션 시작 성공")
        except Exception as e:
            self.log_manager.log_error(f"초기화 실패: {str(e)}")
            raise

    def setup_fonts(self):
        """운영체제별 폰트 설정"""
        try:
            if sys.platform == 'win32':
                font_path = 'C:/Windows/Fonts/malgun.ttf'
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.family'] = font_prop.get_name()
                default_font = ('맑은 고딕', 9)
            else:
                plt.rcParams['font.family'] = 'NanumGothic'
                default_font = ('NanumGothic', 9)

            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.size'] = 10

            style = ttk.Style()
            style.configure('TLabel', font=default_font)
            style.configure('TButton', font=default_font)

            self.font_config = {
                'default': default_font,
                'header': (default_font[0], 11),
                'title': (default_font[0], 10)
            }
        except Exception as e:
            self.log_manager.log_error(f"폰트 설정 오류: {str(e)}")
            plt.rcParams['font.family'] = 'sans-serif'

    def _setup_gui(self):
        """GUI 구성 요소 초기화"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)

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
        settings_frame = ttk.LabelFrame(self.main_tab, text="기본 설정", padding=10)
        settings_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(settings_frame, text="선택 번호 개수:").grid(row=0, column=0, padx=5)
        self.numbers_var = tk.StringVar(value="6")
        ttk.Entry(settings_frame, textvariable=self.numbers_var, width=10).grid(row=0, column=1)

        ttk.Label(settings_frame, text="학습 회차:").grid(row=0, column=2, padx=5)
        self.learning_draws_var = tk.StringVar(value="100")
        ttk.Combobox(settings_frame, textvariable=self.learning_draws_var,
                     values=["전체", "10", "30", "50", "100", "200"]).grid(row=0, column=3)

        ttk.Label(settings_frame, text="학습률:").grid(row=0, column=4, padx=5)
        self.learning_rate_var = tk.StringVar(value="0.1")
        ttk.Entry(settings_frame, textvariable=self.learning_rate_var, width=10).grid(row=0, column=5)

        ttk.Label(settings_frame, text="학습 반복:").grid(row=0, column=6, padx=5)
        self.iterations_var = tk.StringVar(value="100")
        ttk.Entry(settings_frame, textvariable=self.iterations_var, width=10).grid(row=0, column=7)

        ttk.Checkbutton(settings_frame, text="머신러닝 사용",
                        variable=self.use_ml_var).grid(row=0, column=9, padx=5)

        ttk.Button(settings_frame, text="모델 불러오기",
                   command=self._load_model).grid(row=1, column=8, padx=5)
        ttk.Button(settings_frame, text="모델 저장",
                   command=self._save_model).grid(row=1, column=9, padx=5)

        weights_frame = ttk.LabelFrame(self.main_tab, text="패턴 가중치 설정", padding=10)
        weights_frame.pack(fill='x', padx=5, pady=5)

        self.weights = {
            'pair': tk.StringVar(value="35"),
            'triple': tk.StringVar(value="25"),
            'sequence': tk.StringVar(value="15"),
            'frequency': tk.StringVar(value="15"),
            'recency': tk.StringVar(value="10")
        }

        ttk.Label(weights_frame, text="2개 번호 패턴 (%):").grid(row=0, column=0, padx=5)
        ttk.Entry(weights_frame, textvariable=self.weights['pair'], width=8).grid(row=0, column=1)
        ttk.Label(weights_frame, text="3개 번호 패턴 (%):").grid(row=0, column=2, padx=5)
        ttk.Entry(weights_frame, textvariable=self.weights['triple'], width=8).grid(row=0, column=3)
        ttk.Label(weights_frame, text="연속성 (%):").grid(row=0, column=4, padx=5)
        ttk.Entry(weights_frame, textvariable=self.weights['sequence'], width=8).grid(row=0, column=5)
        ttk.Label(weights_frame, text="출현 빈도 (%):").grid(row=1, column=0, padx=5)
        ttk.Entry(weights_frame, textvariable=self.weights['frequency'], width=8).grid(row=1, column=1)
        ttk.Label(weights_frame, text="최근성 (%):").grid(row=1, column=2, padx=5)
        ttk.Entry(weights_frame, textvariable=self.weights['recency'], width=8).grid(row=1, column=3)

        ttk.Button(weights_frame, text="가중치 초기화",
                   command=self._reset_weights).grid(row=1, column=5, padx=5)

        self.run_button = ttk.Button(settings_frame, text="예측 시작", command=self.run_prediction)
        self.run_button.grid(row=0, column=8, padx=10)

        log_frame = ttk.LabelFrame(self.main_tab, text="실행 로그", padding=10)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15)
        self.log_text.pack(fill='both', expand=True)

        results_frame = ttk.LabelFrame(self.main_tab, text="예측 결과", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.results_text = scrolledtext.ScrolledText(results_frame, height=10)
        self.results_text.pack(fill='both', expand=True)

        self.status_var = tk.StringVar(value="준비")
        ttk.Label(self.main_tab, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill='x', padx=5, pady=5)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_tab, length=300, mode='determinate',
                                            variable=self.progress_var)
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
        """가중치 초기값으로 리셋"""
        default_weights = {'pair': "35", 'triple': "25", 'sequence': "15",
                           'frequency': "15", 'recency': "10"}
        for key, value in default_weights.items():
            self.weights[key].set(value)

    def _validate_weights(self):
        """가중치 유효성 검사"""
        try:
            weight_sum = sum(float(self.weights[key].get()) for key in self.weights)
            if not math.isclose(weight_sum, 100, rel_tol=1e-9):
                raise ValueError("가중치의 합은 100%여야 합니다")
            for key, var in self.weights.items():
                value = float(var.get())
                if value < 0 or value > 100:
                    raise ValueError(f"{key} 가중치는 0~100 사이여야 합니다")
            return True
        except ValueError as e:
            messagebox.showerror("가중치 오류", str(e))
            return False

    def _validate_inputs(self):
        """모든 입력값의 유효성 검사"""
        try:
            num_count = self.numbers_var.get()
            if not num_count.isdigit() or not (1 <= int(num_count) <= 45):
                raise ValueError("선택 번호 개수는 1~45 사이의 정수여야 합니다")

            learning_draws = self.learning_draws_var.get()
            if learning_draws != "전체" and (not learning_draws.isdigit() or int(learning_draws) <= 0):
                raise ValueError("학습 회차는 '전체' 또는 양의 정수여야 합니다")

            learning_rate = float(self.learning_rate_var.get())
            if not (0 < learning_rate <= 1):
                raise ValueError("학습률은 0 초과 1 이하여야 합니다")

            iterations = self.iterations_var.get()
            if not iterations.isdigit() or int(iterations) <= 0:
                raise ValueError("학습 반복 횟수는 양의 정수여야 합니다")

            for key, var in self.weights.items():
                value = var.get()
                if not value or not value.replace('.', '').isdigit():
                    raise ValueError(f"{key} 가중치는 숫자여야 합니다")
            return True
        except ValueError as e:
            messagebox.showerror("입력 오류", str(e))
            return False

    def _setup_visualization(self):
        """시각화 그래프 초기 설정"""
        try:
            plt.style.use('default')
            self.fig.suptitle('로또 번호 분석')
            self.ax1.set_title('번호별 출현 빈도')
            self.ax2.set_title('당첨금 트렌드')
            self.ax1.grid(True, linestyle='--', alpha=0.7)
            self.ax2.grid(True, linestyle='--', alpha=0.7)
            self.ax1.set_xlabel('번호')
            self.ax1.set_ylabel('출현 횟수')
            self.ax2.set_xlabel('회차')
            self.ax2.set_ylabel('당첨금')
            self.fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        except Exception as e:
            self.log_manager.log_error(f"시각화 설정 오류: {str(e)}")

    def _prediction_thread(self):
        """예측 실행 스레드"""
        try:
            self.status_var.set("데이터 준비 중...")
            self.progress_var.set(0)

            if not self._validate_inputs():
                raise ValueError("입력값이 올바르지 않습니다")

            draw_limit = None if self.learning_draws_var.get() == "전체" else int(self.learning_draws_var.get())
            historical_data = self.db_manager.get_historical_data(draw_limit)
            self.progress_var.set(10)

            self.analyzer = LottoAnalyzer(
                learning_rate=float(self.learning_rate_var.get()),
                log_manager=self.log_manager,
                pattern_weights={key: float(value.get()) / 100 for key, value in self.weights.items()},
                use_ml=self.use_ml_var.get()
            )
            self.progress_var.set(20)

            if self.use_ml_var.get():
                self.status_var.set("머신러닝 모델 학습 중...")
                self.analyzer.train_ml_model(historical_data)
                self.progress_var.set(50)

            self.status_var.set("패턴 분석 중...")
            self.analyzer.analyze_patterns(historical_data)
            self.progress_var.set(70)

            self.status_var.set("번호 예측 중...")
            num_count = int(self.numbers_var.get())
            selected_numbers = (self.analyzer.select_numbers_by_ml(num_count)
                                if self.use_ml_var.get()
                                else self.analyzer.select_numbers_by_count(num_count))
            self.progress_var.set(90)

            self._show_prediction_results(selected_numbers, historical_data)
            self._save_prediction_results(selected_numbers)
            self._update_analysis_graphs(historical_data)
            self._update_stats_tab(historical_data)
            self.progress_var.set(100)

            self.status_var.set("완료")
            messagebox.showinfo("완료", "예측이 완료되었습니다!")
        except Exception as e:
            self.log_manager.log_error(f"예측 오류: {str(e)}", exc_info=True)
            self.status_var.set("오류 발생")
            messagebox.showerror("오류", f"예측 중 오류 발생: {str(e)}")
        finally:
            self.is_running = False
            self.run_button.config(text="예측 시작")
            self.progress_var.set(0)

    def _show_prediction_results(self, numbers, historical_data):
        """예측 결과를 화면에 표시"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"예측된 번호: {numbers}\n")
        self.log_text.insert(tk.END, f"예측 결과: {numbers}\n")
        self.log_manager.log_info(f"예측된 번호: {numbers}")

    def _save_prediction_results(self, numbers):
        """예측 결과를 파일로 저장"""
        filepath = self.file_manager.get_prediction_file('txt')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"예측된 번호: {numbers}\n")
        self.log_manager.log_info(f"예측 결과 저장: {filepath}")

    def _update_analysis_graphs(self, historical_data):
        """분석 그래프 업데이트"""
        self.ax1.clear()
        self.ax2.clear()
        stats = [self.analyzer.number_stats.get(i, 0) for i in range(1, 46)]
        self.ax1.bar(range(1, 46), stats)
        self.ax1.set_title('번호별 출현 빈도')
        self.ax2.plot(historical_data['draw_number'], historical_data['money1'])
        self.ax2.set_title('당첨금 트렌드')
        self.canvas.draw()

    def _update_stats_tab(self, historical_data):
        """통계 탭 업데이트"""
        self.stats_text.delete(1.0, tk.END)
        stats = [f"번호 {i}: {self.analyzer.number_stats.get(i, 0)}회" for i in range(1, 46)]
        self.stats_text.insert(tk.END, "\n".join(stats))

    def _load_model(self):
        """저장된 모델 불러오기"""
        try:
            filepath = filedialog.askopenfilename(
                initialdir=str(self.file_manager.models_dir),
                filetypes=[("Pickle files", "*.pkl")]
            )
            if filepath:
                from .model_state import ModelState
                state = ModelState.load_from_file(filepath)
                if state and hasattr(self, 'analyzer'):
                    self.analyzer.set_state(state)
                    messagebox.showinfo("성공", "모델이 성공적으로 불러와졌습니다")
                else:
                    raise ValueError("분석기가 초기화되지 않았습니다")
        except Exception as e:
            messagebox.showerror("오류", f"모델 로드 실패: {str(e)}")

    def _save_model(self):
        """현재 모델 저장"""
        try:
            if not hasattr(self, 'analyzer'):
                raise ValueError("먼저 예측을 실행해야 합니다")
            filepath = self.file_manager.get_model_file()
            if self.analyzer.get_state().save_to_file(filepath):
                self.file_manager.backup_model(filepath)
                messagebox.showinfo("성공", f"모델이 저장되었습니다: {filepath}")
        except Exception as e:
            messagebox.showerror("오류", f"모델 저장 실패: {str(e)}")

    def run_prediction(self):
        """예측 실행 버튼 동작"""
        if self.is_running:
            self.is_running = False
            self.run_button.config(text="예측 시작")
            return
        if not self._validate_weights() or not self._validate_inputs():
            return
        self.is_running = True
        self.run_button.config(text="중지")
        thread = threading.Thread(target=self._prediction_thread)
        thread.daemon = True
        thread.start()
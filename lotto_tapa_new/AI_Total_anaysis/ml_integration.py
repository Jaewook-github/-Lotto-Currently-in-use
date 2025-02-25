import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
from lotto_ml_model import LottoMLModel
from db_manager import LottoDBManager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LottoMLIntegration')


class LottoMLIntegration:
    """
    로또 타파 분석기와 머신러닝 모델을 통합하는 클래스
    UI와 모델 간의 인터페이스 역할을 합니다.
    """

    def __init__(self, root=None):
        """
        LottoMLIntegration 초기화

        Args:
            root: tkinter UI 루트 객체 (선택 사항)
        """
        self.root = root
        self.ml_model = LottoMLModel()
        self.db_manager = LottoDBManager()
        self.training_in_progress = False

    def setup_ui(self, notebook):
        """
        머신러닝 탭 UI 설정

        Args:
            notebook: tkinter 노트북(탭) 객체
        """
        # 머신러닝 탭 생성
        self.ml_tab = ttk.Frame(notebook)
        notebook.add(self.ml_tab, text="머신러닝")

        # 메인 프레임
        main_frame = ttk.LabelFrame(self.ml_tab, text="머신러닝 로또 예측", padding=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 모델 정보 및 제어 프레임
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill="x", pady=10)

        # 모델 학습 버튼
        self.train_button = ttk.Button(
            control_frame,
            text="모델 학습",
            command=self.train_model_threaded
        )
        self.train_button.pack(side="left", padx=5)

        # 모델 상태 라벨
        self.model_status_var = tk.StringVar(value="모델 상태: 초기화 필요")
        ttk.Label(
            control_frame,
            textvariable=self.model_status_var
        ).pack(side="left", padx=20)

        # 예측 설정 프레임
        predict_frame = ttk.LabelFrame(main_frame, text="예측 설정", padding=10)
        predict_frame.pack(fill="x", pady=10)

        # 생성할 게임 수
        game_frame = ttk.Frame(predict_frame)
        game_frame.pack(fill="x", pady=5)

        ttk.Label(game_frame, text="생성할 게임 수:").pack(side="left", padx=5)
        self.ml_games_count_var = tk.StringVar(value="5")
        ttk.Entry(
            game_frame,
            textvariable=self.ml_games_count_var,
            width=5
        ).pack(side="left", padx=5)

        # 예측 방식 선택
        method_frame = ttk.Frame(predict_frame)
        method_frame.pack(fill="x", pady=5)

        ttk.Label(method_frame, text="예측 방식:").pack(side="left", padx=5)
        self.prediction_method_var = tk.StringVar(value="ml_only")
        ttk.Radiobutton(
            method_frame,
            text="머신러닝만 사용",
            variable=self.prediction_method_var,
            value="ml_only"
        ).pack(side="left", padx=5)
        ttk.Radiobutton(
            method_frame,
            text="머신러닝 + 규칙 하이브리드",
            variable=self.prediction_method_var,
            value="hybrid"
        ).pack(side="left", padx=5)

        # 번호 생성 버튼
        ttk.Button(
            main_frame,
            text="AI 번호 생성",
            command=self.generate_ml_numbers
        ).pack(pady=10)

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="AI 예측 결과", padding=10)
        result_frame.pack(fill="both", expand=True, pady=10)

        self.ml_result_text = tk.Text(result_frame, height=10, width=40)
        self.ml_result_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 모델 성능 및 통계 프레임
        stats_frame = ttk.LabelFrame(main_frame, text="모델 성능 및 통계", padding=10)
        stats_frame.pack(fill="x", pady=10)

        # 성능 지표 표시
        self.performance_text = tk.Text(stats_frame, height=5, width=40, wrap=tk.WORD)
        self.performance_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.performance_text.insert(tk.END, "모델을 학습하면 성능 지표가 표시됩니다.")
        self.performance_text.config(state="disabled")

        # 분석 탭
        self.analysis_tab = ttk.Frame(notebook)
        notebook.add(self.analysis_tab, text="데이터 분석")

        # 분석 탭 내용
        self.setup_analysis_tab()

        # 모델 상태 초기 체크
        self.check_model_status()

    def setup_analysis_tab(self):
        """분석 탭 UI 설정"""
        # 메인 프레임
        main_frame = ttk.LabelFrame(self.analysis_tab, text="로또 데이터 분석", padding=10)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 분석 선택 프레임
        select_frame = ttk.Frame(main_frame)
        select_frame.pack(fill="x", pady=10)

        ttk.Label(select_frame, text="분석 유형:").pack(side="left", padx=5)
        self.analysis_type_var = tk.StringVar(value="frequency")

        analysis_types = [
            ("번호별 출현 빈도", "frequency"),
            ("홀짝 비율 분석", "odd_even"),
            ("고저 비율 분석", "high_low"),
            ("연속 번호 패턴", "consecutive"),
            ("합계 분포", "sum_distribution")
        ]

        for text, value in analysis_types:
            ttk.Radiobutton(
                select_frame,
                text=text,
                variable=self.analysis_type_var,
                value=value
            ).pack(side="left", padx=5)

        # 분석 실행 버튼
        ttk.Button(
            main_frame,
            text="분석 실행",
            command=self.run_analysis
        ).pack(pady=10)

        # 분석 결과 표시 영역
        result_frame = ttk.LabelFrame(main_frame, text="분석 결과", padding=10)
        result_frame.pack(fill="both", expand=True, pady=10)

        # 결과 스크롤 영역
        self.analysis_text = tk.Text(result_frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar.set)

        self.analysis_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.analysis_text.insert(tk.END, "분석 유형을 선택하고 '분석 실행' 버튼을 클릭하세요.")

    def check_model_status(self):
        """모델 상태 확인 및 UI 업데이트"""
        try:
            # 모델 로딩 시간이 오래 걸릴 수 있으므로 상태 미리 업데이트
            self.model_status_var.set("모델 상태: 확인 중...")
            self.root.update_idletasks()  # UI 업데이트

            # 로딩 시도 (타임아웃 설정)
            loading_success = False
            try:
                # 비동기 처리 또는 타임아웃 설정
                loading_success = self.ml_model.load_models()
            except Exception as e:
                logger.error(f"모델 로드 중 오류: {str(e)}")
                loading_success = False

            if loading_success:
                self.model_status_var.set("모델 상태: 학습 완료 (로드됨)")
                self.train_button.config(text="모델 재학습")
            else:
                self.model_status_var.set("모델 상태: 학습 필요")
                self.train_button.config(text="모델 학습")
        except Exception as e:
            logger.error(f"모델 상태 확인 중 오류 발생: {str(e)}")
            self.model_status_var.set(f"모델 상태: 오류")
            self.train_button.config(text="모델 학습")

    def train_model_threaded(self):
        """
        백그라운드 스레드에서 모델 학습 실행
        UI 응답성 유지를 위해 스레드 사용
        """
        if self.training_in_progress:
            messagebox.showinfo("알림", "모델 학습이 이미 진행 중입니다.")
            return

        # 학습 시작 전 UI 업데이트
        self.training_in_progress = True
        self.train_button.config(state="disabled")
        self.model_status_var.set("모델 상태: 학습 중...")

        # 백그라운드 스레드에서 학습 실행
        threading.Thread(target=self.train_model_task, daemon=True).start()

    def train_model_task(self):
        """실제 모델 학습을 수행하는 작업"""
        try:
            # 모델 학습 실행
            success = self.ml_model.train_models()

            # UI 스레드에서 결과 처리
            if self.root:
                self.root.after(0, self.handle_training_result, success)
        except Exception as e:
            logger.error(f"모델 학습 중 오류 발생: {str(e)}")
            if self.root:
                self.root.after(0, self.handle_training_error, str(e))

    def handle_training_result(self, success):
        """
        모델 학습 결과 처리 (UI 스레드에서 호출)

        Args:
            success: 학습 성공 여부
        """
        self.training_in_progress = False
        self.train_button.config(state="normal")

        if success:
            self.model_status_var.set("모델 상태: 학습 완료")
            messagebox.showinfo("학습 완료", "모델 학습이 성공적으로 완료되었습니다.")

            # 성능 정보 업데이트
            self.update_performance_info()
        else:
            self.model_status_var.set("모델 상태: 학습 실패")
            messagebox.showerror("학습 실패", "모델 학습 중 오류가 발생했습니다.")

    def handle_training_error(self, error_msg):
        """
        모델 학습 오류 처리 (UI 스레드에서 호출)

        Args:
            error_msg: 오류 메시지
        """
        self.training_in_progress = False
        self.train_button.config(state="normal")
        self.model_status_var.set(f"모델 상태: 오류 발생")
        messagebox.showerror("학습 오류", f"모델 학습 중 오류가 발생했습니다:\n{error_msg}")

    def update_performance_info(self):
        """모델 성능 정보 업데이트"""
        # 성능 정보 표시 (예시)
        self.performance_text.config(state="normal")
        self.performance_text.delete(1.0, tk.END)

        performance_info = """
모델 학습 정보:
- 개별 번호 모델: 45개 (각 번호별 출현 확률 예측)
- 조합 평가 모델: Random Forest (번호 조합 품질 평가)
- 학습 데이터: 전체 당첨 번호 기록
- 특성 개수: 30+ (번호 패턴, 통계적 특성 등)
- 주요 특성: 홀짝 비율, 합계, 번호 간격, AC값 등
        """

        self.performance_text.insert(tk.END, performance_info.strip())
        self.performance_text.config(state="disabled")

    def generate_ml_numbers(self):
        """머신러닝 기반 번호 생성"""
        try:
            # 게임 수 파싱
            try:
                games_count = int(self.ml_games_count_var.get())
                if games_count < 1 or games_count > 20:
                    raise ValueError("게임 수는 1~20 사이여야 합니다.")
            except ValueError:
                messagebox.showerror("입력 오류", "유효한 게임 수를 입력하세요 (1~20).")
                return

            # 모델 상태 확인
            if not self.ml_model.model:
                if not self.ml_model.load_models():
                    result = messagebox.askyesno(
                        "모델 필요",
                        "학습된 모델이 없습니다. 지금 모델을 학습하시겠습니까?"
                    )
                    if result:
                        self.train_model_threaded()
                    return

            # 예측 방식
            prediction_method = self.prediction_method_var.get()

            # 결과 텍스트 초기화
            self.ml_result_text.delete(1.0, tk.END)
            self.ml_result_text.insert(tk.END, "AI가 번호를 생성 중입니다...\n\n")
            self.ml_result_text.update()

            # 백그라운드에서 번호 생성 (UI 응답성 유지)
            threading.Thread(
                target=self.generate_numbers_task,
                args=(games_count, prediction_method),
                daemon=True
            ).start()

        except Exception as e:
            logger.error(f"번호 생성 중 오류 발생: {str(e)}")
            messagebox.showerror("오류", f"번호 생성 중 오류가 발생했습니다:\n{str(e)}")

    def generate_numbers_task(self, games_count, prediction_method):
        """
        백그라운드에서 번호 생성 작업 수행

        Args:
            games_count: 생성할 게임 수
            prediction_method: 예측 방식 ('ml_only' 또는 'hybrid')
        """
        try:
            # 번호 예측
            combinations = self.ml_model.predict_numbers(games_count)

            if not combinations:
                self.root.after(0, lambda: self.show_generation_error("번호 생성에 실패했습니다."))
                return

            # UI 스레드에서 결과 표시
            self.root.after(0, lambda: self.display_prediction_results(combinations))

        except Exception as e:
            logger.error(f"번호 생성 작업 중 오류 발생: {str(e)}")
            self.root.after(0, lambda: self.show_generation_error(str(e)))

    def display_prediction_results(self, combinations):
        """
        예측 결과 표시

        Args:
            combinations: 예측된 번호 조합 리스트
        """
        self.ml_result_text.delete(1.0, tk.END)

        self.ml_result_text.insert(tk.END, "🔮 AI 예측 번호 🔮\n\n")

        for i, combo in enumerate(combinations, 1):
            # 번호 정렬 및 포맷팅
            sorted_combo = sorted(combo)
            formatted_numbers = " ".join(f"{num:02d}" for num in sorted_combo)

            self.ml_result_text.insert(tk.END, f"{i}번 조합: {formatted_numbers}\n")

            # 주요 특성 표시
            odd_count = sum(1 for n in combo if n % 2 == 1)
            even_count = 6 - odd_count

            high_count = sum(1 for n in combo if n >= 23)
            low_count = 6 - high_count

            sum_value = sum(combo)

            self.ml_result_text.insert(
                tk.END,
                f"   [합계: {sum_value} | 홀짝: {odd_count}:{even_count} | 고저: {low_count}:{high_count}]\n\n"
            )

    def show_generation_error(self, error_msg):
        """
        번호 생성 오류 표시

        Args:
            error_msg: 오류 메시지
        """
        self.ml_result_text.delete(1.0, tk.END)
        self.ml_result_text.insert(tk.END, f"번호 생성 중 오류가 발생했습니다:\n{error_msg}")
        messagebox.showerror("생성 오류", f"번호 생성 중 오류가 발생했습니다:\n{error_msg}")

    def run_analysis(self):
        """선택된 분석 실행"""
        analysis_type = self.analysis_type_var.get()

        # 분석 시작 메시지
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, "분석 중...\n\n")
        self.analysis_text.update()

        # 백그라운드에서 분석 실행
        threading.Thread(
            target=self.run_analysis_task,
            args=(analysis_type,),
            daemon=True
        ).start()

    def run_analysis_task(self, analysis_type):
        """
        백그라운드에서 분석 작업 수행

        Args:
            analysis_type: 분석 유형
        """
        try:
            result = None
            title = ""

            # 분석 유형에 따른 데이터 가져오기
            if analysis_type == "frequency":
                result = self.db_manager.get_overall_frequency()
                title = "번호별 출현 빈도 분석"
            elif analysis_type == "odd_even":
                result = self.db_manager.analyze_odd_even_ratio()
                title = "홀짝 비율 분석"
            elif analysis_type == "high_low":
                result = self.db_manager.analyze_high_low_ratio()
                title = "고저 비율 분석"
            elif analysis_type == "consecutive":
                result = self.db_manager.analyze_consecutive_numbers()
                title = "연속 번호 패턴 분석"
            elif analysis_type == "sum_distribution":
                result = self.db_manager.analyze_sum_distribution()
                title = "합계 분포 분석"

            # UI 스레드에서 결과 표시
            if result:
                self.root.after(0, lambda: self.display_analysis_results(result, title))
            else:
                self.root.after(0, lambda: self.show_analysis_error("분석 결과가 없습니다."))

        except Exception as e:
            logger.error(f"분석 작업 중 오류 발생: {str(e)}")
            self.root.after(0, lambda: self.show_analysis_error(str(e)))

    def display_analysis_results(self, result, title):
        """
        분석 결과 표시

        Args:
            result: 분석 결과 데이터
            title: 분석 제목
        """
        self.analysis_text.delete(1.0, tk.END)

        # 제목 추가
        self.analysis_text.insert(tk.END, f"📊 {title} 📊\n\n")

        # 분석 유형에 따라 다르게 표시
        if title == "번호별 출현 빈도 분석":
            # 번호를 빈도 기준 내림차순으로 정렬
            sorted_numbers = sorted(result.items(), key=lambda x: x[1], reverse=True)

            # 상위 10개 번호
            self.analysis_text.insert(tk.END, "🔥 출현 빈도 상위 10개 번호 🔥\n")
            for num, freq in sorted_numbers[:10]:
                self.analysis_text.insert(tk.END, f"번호 {num:2d}: {freq:3d}회\n")

            self.analysis_text.insert(tk.END, "\n📉 출현 빈도 하위 10개 번호 📉\n")
            for num, freq in sorted_numbers[-10:]:
                self.analysis_text.insert(tk.END, f"번호 {num:2d}: {freq:3d}회\n")

            # 숫자 범위별 출현 빈도
            self.analysis_text.insert(tk.END, "\n📊 번호 범위별 평균 출현 빈도 📊\n")
            ranges = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 45)]

            for start, end in ranges:
                range_nums = {num: freq for num, freq in result.items() if start <= num <= end}
                avg_freq = sum(range_nums.values()) / len(range_nums)
                self.analysis_text.insert(tk.END, f"{start:2d}~{end:2d}: 평균 {avg_freq:.1f}회\n")

        elif title == "홀짝 비율 분석" or title == "고저 비율 분석":
            # 비율 및 백분율 표시
            items = []
            percent_key_suffix = "_percent"

            for key, value in result.items():
                if not key.endswith(percent_key_suffix):
                    percent_key = f"{key}{percent_key_suffix}"
                    percent = result.get(percent_key, 0)
                    items.append((key, value, percent))

            # 빈도순 정렬
            items.sort(key=lambda x: x[1], reverse=True)

            for ratio, count, percent in items:
                self.analysis_text.insert(tk.END, f"{ratio} 비율: {count:3d}회 ({percent:.1f}%)\n")

        elif title == "연속 번호 패턴 분석":
            # 연속 번호 패턴 정보
            patterns = {
                'none': '연속 번호 없음',
                'one_pair': '2연속 1쌍',
                'two_pairs': '2연속 2쌍',
                'three_in_row': '3연속 번호',
                'four_plus': '4연속 이상'
            }

            # 패턴 및 백분율 표시
            items = []
            percent_key_suffix = "_percent"

            for key, label in patterns.items():
                count = result.get(key, 0)
                percent = result.get(f"{key}{percent_key_suffix}", 0)
                items.append((label, count, percent))

            # 빈도순 정렬
            items.sort(key=lambda x: x[1], reverse=True)

            for label, count, percent in items:
                self.analysis_text.insert(tk.END, f"{label}: {count:3d}회 ({percent:.1f}%)\n")

        elif title == "합계 분포 분석":
            # 합계 구간별 빈도 표시
            items = []
            percent_key_suffix = "_percent"

            for key, value in result.items():
                if not key.endswith(percent_key_suffix):
                    percent_key = f"{key}{percent_key_suffix}"
                    percent = result.get(percent_key, 0)
                    items.append((key, value, percent))

            # 구간순 정렬
            def range_sort_key(item):
                range_str = item[0]
                start = int(range_str.split('-')[0])
                return start

            items.sort(key=range_sort_key)

            for range_str, count, percent in items:
                self.analysis_text.insert(tk.END, f"합계 {range_str}: {count:3d}회 ({percent:.1f}%)\n")

        else:
            # 기타 분석 결과는 키-값 형태로 표시
            for key, value in result.items():
                self.analysis_text.insert(tk.END, f"{key}: {value}\n")

    def show_analysis_error(self, error_msg):
        """
        분석 오류 표시

        Args:
            error_msg: 오류 메시지
        """
        self.analysis_text.delete(1.0, tk.END)
        self.analysis_text.insert(tk.END, f"분석 중 오류가 발생했습니다:\n{error_msg}")
        messagebox.showerror("분석 오류", f"분석 중 오류가 발생했습니다:\n{error_msg}")
import tkinter as tk
from tkcalendar import DateEntry

from tkinter import ttk, messagebox, font, filedialog
from numbers_generator import LottoGenerator
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import os
import pandas as pd
from datetime import datetime, timedelta
import json

FONT_PATH = r'C:\Windows\Fonts\malgun.ttf'
CONFIG_FILE = 'config.json'


class LottoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lotto Prediction and Analysis Pro")
        self.generator = LottoGenerator()
        self.setup_config()
        self.setup_styles()
        self.create_menu()

        # 메인 컨테이너 생성
        self.main_container = ttk.Frame(root)
        self.main_container.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab_control = ttk.Notebook(self.main_container)

        # 탭 생성
        self.prediction_tab = ttk.Frame(self.tab_control)
        self.analysis_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.prediction_tab, text='예측 번호 생성')
        self.tab_control.add(self.analysis_tab, text='분석')
        self.tab_control.add(self.history_tab, text='히스토리')

        self.tab_control.pack(expand=1, fill='both')

        # 각 탭 초기화
        self.create_prediction_tab()
        self.create_analysis_tab()
        self.create_history_tab()

        # 상태바 생성
        self.create_status_bar()

        # 분석 결과를 저장할 변수
        self.current_analysis = None
        self.analysis_history = []

    def setup_config(self):
        """설정 파일 로드 및 초기화"""
        self.config = {
            'theme': 'default',
            'last_generated': None,
            'analysis_history': [],
            'favorite_numbers': []
        }

        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config.update(json.load(f))

    def setup_styles(self):
        """스타일 설정"""
        style = ttk.Style()
        style.configure('Analysis.TButton', padding=5)
        style.configure('Header.TLabel', font=('Malgun Gothic', 12, 'bold'))

    def create_menu(self):
        """메뉴바 생성"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # 파일 메뉴
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="파일", menu=file_menu)
        file_menu.add_command(label="분석 결과 저장", command=self.save_analysis)
        file_menu.add_command(label="분석 결과 불러오기", command=self.load_analysis)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self.root.quit)

        # 설정 메뉴
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="설정", menu=settings_menu)
        settings_menu.add_command(label="환경설정", command=self.show_settings)

        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="도움말", menu=help_menu)
        help_menu.add_command(label="사용 설명서", command=self.show_help)
        help_menu.add_command(label="프로그램 정보", command=self.show_about)

    def create_prediction_tab(self):
        """예측 탭 생성"""
        # 설정 프레임
        settings_frame = ttk.LabelFrame(self.prediction_tab, text="생성 설정", padding="10")
        settings_frame.pack(fill='x', padx=5, pady=5)

        # 게임 수 설정
        ttk.Label(settings_frame, text="게임 수:").grid(row=0, column=0, padx=5)
        self.num_games_entry = ttk.Entry(settings_frame, width=10)
        self.num_games_entry.grid(row=0, column=1, padx=5)
        self.num_games_entry.insert(0, "5")

        # 고정 번호 설정
        ttk.Label(settings_frame, text="고정 번호:").grid(row=0, column=2, padx=5)
        self.fixed_numbers_entry = ttk.Entry(settings_frame, width=20)
        self.fixed_numbers_entry.grid(row=0, column=3, padx=5)
        ttk.Label(settings_frame, text="(쉼표로 구분)").grid(row=0, column=4)

        # 버튼 프레임
        button_frame = ttk.Frame(self.prediction_tab)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="번호 생성",
                   command=self.generate_numbers).pack(side='left', padx=5)
        ttk.Button(button_frame, text="결과 저장",
                   command=self.save_results).pack(side='left', padx=5)
        ttk.Button(button_frame, text="초기화",
                   command=self.clear_results).pack(side='left', padx=5)

        # 결과 표시 영역
        result_frame = ttk.LabelFrame(self.prediction_tab, text="생성된 번호", padding="10")
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.results_text = tk.Text(result_frame, height=15, width=50)
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical',
                                  command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)

        self.results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_analysis_tab(self):
        """분석 탭 생성"""
        # 좌측 분석 메뉴 프레임
        menu_frame = ttk.Frame(self.analysis_tab, width=200)
        menu_frame.pack(side='left', fill='y', padx=5, pady=5)

        # 분석 옵션 그룹화
        basic_analysis = ttk.LabelFrame(menu_frame, text="기본 분석")
        basic_analysis.pack(fill='x', padx=5, pady=5)

        pattern_analysis = ttk.LabelFrame(menu_frame, text="패턴 분석")
        pattern_analysis.pack(fill='x', padx=5, pady=5)

        statistical_analysis = ttk.LabelFrame(menu_frame, text="통계 분석")
        statistical_analysis.pack(fill='x', padx=5, pady=5)

        # 기본 분석 버튼
        basic_methods = [
            ("번호 빈도 분석", self.frequency_analysis),
            ("홀수/짝수 비율", self.odd_even_ratio_analysis),
            ("끝자리 분석", self.last_digit_analysis)
        ]

        for text, command in basic_methods:
            ttk.Button(basic_analysis, text=text, command=command,
                       style='Analysis.TButton').pack(fill='x', padx=5, pady=2)

        # 패턴 분석 버튼
        pattern_methods = [
            ("연속 번호 분석", self.consecutive_numbers_analysis),
            ("구간별 분포", self.range_distribution_analysis),
            ("AC 값 분석", self.ac_value_analysis)
        ]

        for text, command in pattern_methods:
            ttk.Button(pattern_analysis, text=text, command=command,
                       style='Analysis.TButton').pack(fill='x', padx=5, pady=2)

        # 통계 분석 버튼
        statistical_methods = [
            ("소수/합성수 분석", self.prime_composite_ratio_analysis),
            ("번호 간격 분석", self.interval_analysis),
            ("고급 패턴 분석", self.advanced_pattern_analysis)
        ]

        for text, command in statistical_methods:
            ttk.Button(statistical_analysis, text=text, command=command,
                       style='Analysis.TButton').pack(fill='x', padx=5, pady=2)

        # 우측 그래프 표시 영역
        self.graph_frame = ttk.Frame(self.analysis_tab)
        self.graph_frame.pack(side='right', fill='both', expand=True, padx=5, pady=5)

    def create_history_tab(self):
        """히스토리 탭 생성"""
        # 기간 선택 프레임
        period_frame = ttk.LabelFrame(self.history_tab, text="기간 선택")
        period_frame.pack(fill='x', padx=5, pady=5)

        # 시작 날짜 선택
        ttk.Label(period_frame, text="시작:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(period_frame, width=12,
                                    background='darkblue',
                                    foreground='white',
                                    borderwidth=2,
                                    locale='ko_KR',
                                    date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        # 종료 날짜 선택
        ttk.Label(period_frame, text="종료:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(period_frame, width=12,
                                  background='darkblue',
                                  foreground='white',
                                  borderwidth=2,
                                  locale='ko_KR',
                                  date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        # 조회 버튼
        ttk.Button(period_frame, text="조회",
                   command=self.load_history).grid(row=0, column=4, padx=5, pady=5)

        # 초기화 버튼 추가
        ttk.Button(period_frame, text="초기화",
                   command=self.reset_date_range).grid(row=0, column=5, padx=5, pady=5)

        # 히스토리 표시 영역
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # 트리뷰 생성
        columns = ('날짜', '생성 번호', '당첨 여부', '등수')
        self.history_tree = ttk.Treeview(history_frame, columns=columns,
                                         show='headings')

        # 컬럼 설정
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical',
                                  command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 기본값으로 현재 달의 시작일과 마지막일 설정
        self.set_default_date_range()

    def reset_date_range(self):
        """날짜 범위를 현재 달의 시작일과 마지막일로 초기화"""
        self.set_default_date_range()
        self.load_history()

    def create_status_bar(self):
        """상태바 생성"""
        self.status_bar = ttk.Label(self.root, text="준비", relief=tk.SUNKEN,
                                    anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def update_status(self, message):
        """상태바 메시지 업데이트"""
        self.status_bar.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")

    def save_analysis(self):
        """분석 결과 저장"""
        if not self.current_analysis:
            messagebox.showwarning("경고", "저장할 분석 결과가 없습니다.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_analysis, f, ensure_ascii=False, indent=2)
                self.update_status(f"분석 결과가 {filename}에 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {str(e)}")

    def load_analysis(self):
        """분석 결과 불러오기"""
        filename = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_analysis = json.load(f)

                self.current_analysis = loaded_analysis

                # 분석 유형에 따라 그래프 다시 그리기
                if loaded_analysis['type'] == 'frequency':
                    self.frequency_analysis(loaded_data=loaded_analysis['data'])
                elif loaded_analysis['type'] == 'advanced_pattern':
                    self.advanced_pattern_analysis(loaded_data=loaded_analysis['data'])
                # 다른 분석 유형들에 대한 처리 추가

                self.update_status(f"분석 결과를 {filename}에서 불러왔습니다.")

            except Exception as e:
                messagebox.showerror("오류", f"파일 불러오기 중 오류가 발생했습니다: {str(e)}")

    def set_default_date_range(self):
        """현재 달의 시작일과 마지막일로 날짜 범위 설정"""
        today = datetime.today()
        first_day = today.replace(day=1)

        # 다음 달의 첫 날에서 하루를 빼서 현재 달의 마지막 날을 구함
        if today.month == 12:
            last_day = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = today.replace(month=today.month + 1, day=1) - timedelta(days=1)

        self.start_date.set_date(first_day)
        self.end_date.set_date(last_day)

    def reset_date_range(self):
        """날짜 범위를 현재 달의 시작일과 마지막일로 초기화"""
        self.set_default_date_range()
        self.load_history()

    def load_history(self):
        """히스토리 데이터 로드"""
        try:
            start_date = self.start_date.get_date()
            end_date = self.end_date.get_date()

            # 시작일이 종료일보다 늦은 경우 처리
            if start_date > end_date:
                messagebox.showerror("날짜 오류", "시작일이 종료일보다 늦을 수 없습니다.")
                return

            # 기존 데이터 삭제
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            try:
                # 데이터베이스에서 히스토리 조회
                history_data = self.generator.fetch_history(start_date, end_date)

                # 트리뷰에 데이터 추가
                for record in history_data:
                    self.history_tree.insert('', 'end', values=record)

                self.update_status(f"{len(history_data)}개의 기록을 불러왔습니다.")

            except Exception as e:
                messagebox.showerror("데이터베이스 오류",
                                     f"데이터를 불러오는 중 오류가 발생했습니다: {str(e)}")

        except Exception as e:
            messagebox.showerror("오류", f"날짜 처리 중 오류가 발생했습니다: {str(e)}")

    def create_history_tab(self):
        """히스토리 탭 생성"""
        # 기간 선택 프레임
        period_frame = ttk.LabelFrame(self.history_tab, text="기간 선택")
        period_frame.pack(fill='x', padx=5, pady=5)

        # 시작 날짜 선택
        ttk.Label(period_frame, text="시작:").grid(row=0, column=0, padx=5, pady=5)
        self.start_date = DateEntry(period_frame, width=12,
                                    background='darkblue',
                                    foreground='white',
                                    borderwidth=2,
                                    locale='ko_KR',
                                    date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        # 종료 날짜 선택
        ttk.Label(period_frame, text="종료:").grid(row=0, column=2, padx=5, pady=5)
        self.end_date = DateEntry(period_frame, width=12,
                                  background='darkblue',
                                  foreground='white',
                                  borderwidth=2,
                                  locale='ko_KR',
                                  date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        # 버튼 프레임
        button_frame = ttk.Frame(period_frame)
        button_frame.grid(row=0, column=4, columnspan=2, padx=5, pady=5)

        # 조회 버튼
        ttk.Button(button_frame, text="조회",
                   command=self.load_history).pack(side='left', padx=5)

        # 초기화 버튼
        ttk.Button(button_frame, text="초기화",
                   command=self.reset_date_range).pack(side='left', padx=5)

        # 히스토리 표시 영역
        history_frame = ttk.Frame(self.history_tab)
        history_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # 트리뷰 생성
        columns = ('날짜', '생성 번호', '당첨 여부', '등수')
        self.history_tree = ttk.Treeview(history_frame, columns=columns,
                                         show='headings')

        # 컬럼 설정
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(history_frame, orient='vertical',
                                  command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 기본값으로 현재 달의 시작일과 마지막일 설정
        self.set_default_date_range()

    def generate_numbers(self):
        """번호 생성"""
        try:
            num_games = int(self.num_games_entry.get())
            fixed_numbers_str = self.fixed_numbers_entry.get().strip()

            fixed_numbers = []
            if fixed_numbers_str:
                try:
                    fixed_numbers = [int(x.strip()) for x in fixed_numbers_str.split(',')]
                    # 유효성 검사
                    if not all(1 <= x <= 45 for x in fixed_numbers):
                        raise ValueError("고정 번호는 1부터 45 사이의 숫자여야 합니다.")
                    if len(fixed_numbers) > 5:
                        raise ValueError("고정 번호는 최대 5개까지만 지정할 수 있습니다.")
                except ValueError as e:
                    messagebox.showerror("입력 오류", str(e))
                    return

            # past_results를 try 블록 안으로 이동
            past_results = self.generator.fetch_past_results()

            # fixed_numbers 매개변수 추가
            results = self.generator.generate_lotto_numbers(
                num_games=num_games,
                past_results=past_results,
                fixed_numbers=fixed_numbers
            )

            # 결과 표시
            self.results_text.delete(1.0, tk.END)
            for i, result in enumerate(results, 1):
                # sorted()를 사용하여 정렬된 결과 표시
                sorted_numbers = sorted(result)
                self.results_text.insert(tk.END, f"게임 {i}: {sorted_numbers}\n")

            # CSV 파일 저장
            self.generator.save_to_csv(results)
            self.update_status(f"{num_games}게임의 번호가 생성되었습니다.")

        except ValueError as e:
            messagebox.showerror("입력 오류", "게임 수를 올바르게 입력하세요.")
        except Exception as e:
            messagebox.showerror("오류", f"번호 생성 중 오류가 발생했습니다: {str(e)}")

    def save_results(self):
        """생성된 번호 저장"""
        if not self.results_text.get("1.0", tk.END).strip():
            messagebox.showwarning("경고", "저장할 결과가 없습니다.")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get("1.0", tk.END))
                self.update_status(f"결과가 {filename}에 저장되었습니다.")
            except Exception as e:
                messagebox.showerror("오류", f"저장 중 오류가 발생했습니다: {str(e)}")

    def clear_results(self):
        """결과 초기화"""
        self.results_text.delete(1.0, tk.END)
        self.update_status("결과가 초기화되었습니다.")

    def frequency_analysis(self, loaded_data=None):
        """번호 빈도 분석"""
        if loaded_data:
            frequency = pd.Series(loaded_data)
        else:
            past_results = self.generator.fetch_past_results()
            flat_numbers = [num for sublist in past_results for num in sublist]
            frequency = pd.Series(flat_numbers).value_counts().sort_index()

        plt.figure(figsize=(10, 6))
        plt.bar(frequency.index, frequency.values)
        plt.title("번호 빈도 분석")
        plt.xlabel("번호")
        plt.ylabel("출현 빈도")

        self.display_graph(plt.gcf())

        if not loaded_data:
            self.current_analysis = {
                'type': 'frequency',
                'data': frequency.to_dict(),
                'timestamp': datetime.now().isoformat()
            }
            self.analysis_history.append(self.current_analysis)

        self.update_status("번호 빈도 분석이 완료되었습니다.")

    def odd_even_ratio_analysis(self):
        """홀수/짝수 비율 분석"""
        past_results = self.generator.fetch_past_results()
        odd_count = 0
        even_count = 0

        for result in past_results:
            for num in result:
                if num % 2 == 0:
                    even_count += 1
                else:
                    odd_count += 1

        plt.figure(figsize=(8, 8))
        plt.pie([odd_count, even_count],
                labels=['홀수', '짝수'],
                autopct='%1.1f%%',
                colors=['lightblue', 'lightgreen'])
        plt.title("홀수/짝수 비율")

        self.display_graph(plt.gcf())
        self.update_status("홀수/짝수 비율 분석이 완료되었습니다.")

    def last_digit_analysis(self):
        """끝자리 숫자 분석"""
        past_results = self.generator.fetch_past_results()
        last_digits = [num % 10 for result in past_results for num in result]
        digit_counts = pd.Series(last_digits).value_counts().sort_index()

        plt.figure(figsize=(10, 6))
        plt.bar(digit_counts.index, digit_counts.values)
        plt.title("끝자리 숫자 분석")
        plt.xlabel("끝자리 숫자")
        plt.ylabel("출현 빈도")

        self.display_graph(plt.gcf())
        self.update_status("끝자리 숫자 분석이 완료되었습니다.")

    def consecutive_numbers_analysis(self):
        """연속 번호 분석"""
        past_results = self.generator.fetch_past_results()
        consecutive_counts = []

        for result in past_results:
            count = 0
            sorted_result = sorted(result)
            for i in range(len(sorted_result) - 1):
                if sorted_result[i + 1] - sorted_result[i] == 1:
                    count += 1
            consecutive_counts.append(count)

        plt.figure(figsize=(10, 6))
        plt.hist(consecutive_counts, bins=range(max(consecutive_counts) + 2),
                 rwidth=0.8, align='left')
        plt.title("연속 번호 출현 빈도")
        plt.xlabel("연속 번호 쌍의 수")
        plt.ylabel("출현 횟수")

        self.display_graph(plt.gcf())
        self.update_status("연속 번호 분석이 완료되었습니다.")

    def range_distribution_analysis(self):
        """구간별 분포 분석"""
        past_results = self.generator.fetch_past_results()
        ranges = [0] * 5  # [1-10, 11-20, 21-30, 31-40, 41-45]

        for result in past_results:
            for num in result:
                ranges[(num - 1) // 10] += 1

        labels = ['1-10', '11-20', '21-30', '31-40', '41-45']
        plt.figure(figsize=(10, 6))
        plt.bar(labels, ranges)
        plt.title("구간별 번호 분포")
        plt.xlabel("구간")
        plt.ylabel("출현 빈도")

        self.display_graph(plt.gcf())
        self.update_status("구간별 분포 분석이 완료되었습니다.")

    def ac_value_analysis(self):
        """AC 값 분석"""
        past_results = self.generator.fetch_past_results()
        ac_values = [self.generator.calculate_ac_value(result) for result in past_results]

        plt.figure(figsize=(10, 6))
        plt.hist(ac_values, bins=range(min(ac_values), max(ac_values) + 2),
                 rwidth=0.8, align='left')
        plt.title("AC 값 분포")
        plt.xlabel("AC 값")
        plt.ylabel("빈도")

        self.display_graph(plt.gcf())
        self.update_status("AC 값 분석이 완료되었습니다.")

    def prime_composite_ratio_analysis(self):
        """소수/합성수 비율 분석"""
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
        past_results = self.generator.fetch_past_results()
        prime_count = 0
        composite_count = 0

        for result in past_results:
            for num in result:
                if num in primes:
                    prime_count += 1
                else:
                    composite_count += 1

        plt.figure(figsize=(8, 8))
        plt.pie([prime_count, composite_count],
                labels=['소수', '합성수'],
                autopct='%1.1f%%',
                colors=['lightcoral', 'lightskyblue'])
        plt.title("소수/합성수 비율")

        self.display_graph(plt.gcf())
        self.update_status("소수/합성수 비율 분석이 완료되었습니다.")

    def interval_analysis(self):
        """번호 간격 분석"""
        past_results = self.generator.fetch_past_results()
        intervals = []

        for result in past_results:
            sorted_result = sorted(result)
            for i in range(len(sorted_result) - 1):
                intervals.append(sorted_result[i + 1] - sorted_result[i])

        plt.figure(figsize=(10, 6))
        plt.hist(intervals, bins=range(min(intervals), max(intervals) + 2),
                 rwidth=0.8, align='left')
        plt.title("번호 간격 분포")
        plt.xlabel("간격")
        plt.ylabel("빈도")

        self.display_graph(plt.gcf())
        self.update_status("번호 간격 분석이 완료되었습니다.")

    def advanced_pattern_analysis(self, loaded_data=None):
        """고급 패턴 분석"""
        if loaded_data:
            patterns = loaded_data
        else:
            past_results = self.generator.fetch_past_results()
            patterns = {
                '연속수': 0,
                '격차수': 0,
                '쌍번호': 0,
                '구간조합': {},
                '끝수조합': {}
            }

            for result in past_results:
                # 연속수 검사
                for i in range(len(result) - 1):
                    if result[i + 1] - result[i] == 1:
                        patterns['연속수'] += 1

                # 격차수 검사
                for i in range(len(result) - 1):
                    if result[i + 1] - result[i] == 2:
                        patterns['격차수'] += 1

                # 쌍번호 검사
                tens = [num // 10 for num in result]
                for i in range(len(tens) - 1):
                    if tens[i] == tens[i + 1]:
                        patterns['쌍번호'] += 1

                # 구간 조합 분석
                ranges = [0] * 5
                for num in result:
                    ranges[(num - 1) // 10] += 1
                range_key = ':'.join(map(str, ranges))
                patterns['구간조합'][range_key] = patterns['구간조합'].get(range_key, 0) + 1

                # 끝수 조합 분석
                end_digits = [num % 10 for num in result]
                end_key = ':'.join(map(str, sorted(end_digits)))
                patterns['끝수조합'][end_key] = patterns['끝수조합'].get(end_key, 0) + 1

        # 시각화
        fig = plt.figure(figsize=(12, 8))
        fig.suptitle('고급 패턴 분석', fontsize=16)

        # 서브플롯 구성
        gs = fig.add_gridspec(2, 2)
        ax1 = fig.add_subplot(gs[0, 0])
        ax2 = fig.add_subplot(gs[0, 1])
        ax3 = fig.add_subplot(gs[1, :])

        # 1. 기본 패턴 분포
        basic_patterns = ['연속수', '격차수', '쌍번호']
        values = [patterns[key] for key in basic_patterns]
        ax1.bar(basic_patterns, values)
        ax1.set_title('기본 패턴 분포')

        # 2. 상위 구간 조합
        top_ranges = sorted(patterns['구간조합'].items(),
                            key=lambda x: x[1], reverse=True)[:5]
        ax2.bar([f'조합{i + 1}' for i in range(len(top_ranges))],
                [v[1] for v in top_ranges])
        ax2.set_title('상위 구간 조합')

        # 3. 끝수 조합 히트맵
        end_digit_data = pd.DataFrame(0, index=range(10), columns=range(10))
        for end_key, count in patterns['끝수조합'].items():
            ends = list(map(int, end_key.split(':')))
            for i in ends:
                for j in ends:
                    end_digit_data.iloc[i, j] += count

        im = ax3.imshow(end_digit_data, cmap='YlOrRd')
        plt.colorbar(im, ax=ax3)
        ax3.set_title('끝수 조합 히트맵')

        # 그래프 표시
        self.display_graph(fig)

        # 분석 결과 저장
        if not loaded_data:
            self.current_analysis = {
                'type': 'advanced_pattern',
                'data': patterns,
                'timestamp': datetime.now().isoformat()
            }
            self.analysis_history.append(self.current_analysis)

        self.update_status("고급 패턴 분석이 완료되었습니다.")

    def display_graph(self, fig):
        """그래프 표시"""
        # 기존 그래프 제거
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # 새 그래프 표시
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side='top', fill='both', expand=True)

        # 툴바 추가
        from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
        toolbar = NavigationToolbar2Tk(canvas, self.graph_frame)
        toolbar.update()

    def show_settings(self):
        """설정 창 표시"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("환경설정")
        settings_window.geometry("400x300")

        # 설정 탭 생성
        settings_notebook = ttk.Notebook(settings_window)

        # 일반 설정 탭
        general_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(general_tab, text='일반')

            ## 테마 설정
        ttk.Label(general_tab, text="테마:").grid(row=0, column=0, padx=5, pady=5)
        theme_combo = ttk.Combobox(general_tab,
                                 values=['기본', '다크', '라이트'])
        theme_combo.grid(row=0, column=1, padx=5, pady=5)
        theme_combo.set(self.config['theme'])

        # 분석 설정 탭
        analysis_tab = ttk.Frame(settings_notebook)
        settings_notebook.add(analysis_tab, text='분석')

        settings_notebook.pack(expand=True, fill='both')

    def show_help(self):
        """도움말 창 표시"""
        help_window = tk.Toplevel(self.root)
        help_window.title("사용 설명서")
        help_window.geometry("600x400")

        help_text = tk.Text(help_window, wrap=tk.WORD)
        help_text.pack(expand=True, fill='both', padx=10, pady=10)

        # 도움말 내용
        help_content = """
로또 분석 및 예측 프로그램 사용 설명서

1. 예측 번호 생성
   - 게임 수를 입력하고 번호 생성 버튼을 클릭합니다.
   - 고정 번호를 사용하려면 쉼표로 구분하여 입력합니다.

2. 분석 기능
   - 기본 분석: 번호 빈도, 홀짝 비율 등 기본적인 통계
   - 패턴 분석: 연속 번호, 구간별 분포 등 패턴 분석
   - 통계 분석: 소수/합성수 비율, 번호 간격 등 심화 분석

3. 히스토리 관리
   - 생성된 번호의 히스토리를 조회할 수 있습니다.
   - 기간을 설정하여 과거 데이터를 확인할 수 있습니다.

4. 결과 관리
   - 분석 결과를 저장하고 불러올 수 있습니다.
   - 생성된 번호를 파일로 저장할 수 있습니다.
"""
        help_text.insert('1.0', help_content)
        help_text.config(state='disabled')

    def show_about(self):
        """프로그램 정보 창 표시"""
        messagebox.showinfo(
            "프로그램 정보",
            "로또 분석 및 예측 프로그램 v2.0\n"
            "Copyright © 2024\n\n"
            "이 프로그램은 로또 번호 생성 및 분석을 위한 도구입니다."
        )

    def run(self):
        """프로그램 실행"""
        self.root.mainloop()
        self.generator.close()

def set_font():
    """폰트 설정"""
    if os.path.exists(FONT_PATH):
        font_prop = fm.FontProperties(fname=FONT_PATH)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        print("지정된 폰트 파일을 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'Malgun Gothic'

if __name__ == "__main__":
    set_font()
    root = tk.Tk()
    app = LottoApp(root)
    app.run()
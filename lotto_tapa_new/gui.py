import tkinter as tk
from tkinter import ttk, messagebox
from lotto_analyzer import LottoAnalyzer
from lotto_config import LottoConfig
import json


class LottoGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("로또 타파 분석기")
        self.config = LottoConfig()
        self.analyzer = LottoAnalyzer(self.config)

        # 노트북(탭) 생성
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True)

        self.setup_tabs()

    def setup_tabs(self):
        # 메인 탭
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="메인")

        # 규칙 선택 탭
        self.rules_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.rules_tab, text="규칙 선택")

        # 설정 탭
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="상세 설정")

        # 도움말 탭
        self.help_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.help_tab, text="도움말")

        self.setup_main_tab()
        self.setup_rules_tab()
        self.setup_settings_tab()
        self.setup_help_tab()

    def setup_main_tab(self):
        frame = ttk.LabelFrame(self.main_tab, text="번호 생성", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 게임 수 설정
        ttk.Label(frame, text="생성할 게임 수:").pack(pady=5)
        self.games_count_var = tk.StringVar(value=str(self.config.games_count))
        ttk.Entry(frame, textvariable=self.games_count_var, width=10).pack(pady=5)

        # 번호 생성 버튼
        ttk.Button(frame, text="번호 생성", command=self.generate_numbers).pack(pady=10)

        # 결과 표시 영역
        self.result_text = tk.Text(frame, height=20, width=40)
        self.result_text.pack(pady=10, padx=10)

    def setup_rules_tab(self):
        frame = ttk.LabelFrame(self.rules_tab, text="적용할 규칙 선택", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 전체 선택/해제 체크박스
        self.all_rules_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame, text="전체 선택/해제",
                        variable=self.all_rules_var,
                        command=self.toggle_all_rules).pack(pady=5)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=5)

        # 개별 규칙 체크박스들
        self.rule_vars = {}
        rule_descriptions = {
            'sum_range': '1. 총합 구간 (100~175)',
            'ac_value': '2. AC값 (7 이상)',
            'odd_even': '3. 홀짝 비율',
            'high_low': '4. 고저 비율',
            'prime': '5. 소수 개수',
            'composite': '6. 합성수 개수',
            'last_digit': '7. 끝수 총합',
            'multiples': '8. 3,5의 배수',
            'perfect_square': '9. 제곱수',
            'consecutive': '10. 연속번호',
            'twin': '11. 쌍수',
            'corner': '12. 모서리 패턴'
        }

        for rule_key, description in rule_descriptions.items():
            var = tk.BooleanVar(value=self.config.rules_enabled[rule_key])
            self.rule_vars[rule_key] = var
            ttk.Checkbutton(frame, text=description,
                            variable=var,
                            command=lambda k=rule_key: self.toggle_rule(k)).pack(anchor='w', pady=2)

    def setup_settings_tab(self):
        frame = ttk.LabelFrame(self.settings_tab, text="규칙별 상세 설정", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 설정 버튼 프레임
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        # 설정 저장/불러오기 버튼
        ttk.Button(button_frame, text="현재 설정 저장", command=self.save_current_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="기본값으로 복원", command=self.restore_default_settings).pack(side="left", padx=5)

        # 설정 스크롤 영역
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # 기본 설정
        basic_settings = ttk.LabelFrame(scrollable_frame, text="기본 설정", padding=5)
        basic_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(basic_settings, "총합 구간", "sum_range", self.config.sum_range)
        self.create_value_setting(basic_settings, "최소 AC값", "ac_value_min", self.config.ac_value_min)

        # 비율 설정
        ratio_settings = ttk.LabelFrame(scrollable_frame, text="비율 설정", padding=5)
        ratio_settings.pack(fill="x", padx=5, pady=5)

        self.create_ratio_setting(ratio_settings, "홀짝 비율", "odd_even_ratio", (0, 6))
        self.create_ratio_setting(ratio_settings, "고저 비율", "high_low_ratio", (0, 6))

        # 개수 설정
        count_settings = ttk.LabelFrame(scrollable_frame, text="개수 설정", padding=5)
        count_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(count_settings, "소수 개수", "prime_range", self.config.prime_range)
        self.create_range_setting(count_settings, "합성수 개수", "composite_range", self.config.composite_range)
        self.create_range_setting(count_settings, "끝수 총합 구간", "last_digit_sum_range", self.config.last_digit_sum_range)
        self.create_range_setting(count_settings, "3의 배수 개수", "multiples_of_3_range", self.config.multiples_of_3_range)
        self.create_range_setting(count_settings, "5의 배수 개수", "multiples_of_5_range", self.config.multiples_of_5_range)
        self.create_range_setting(count_settings, "제곱수 개수", "perfect_square_range", self.config.perfect_square_range)
        self.create_value_setting(count_settings, "연속번호 쌍 개수", "consecutive_pairs", 1)
        self.create_range_setting(count_settings, "쌍수 개수", "twin_numbers_range", self.config.twin_numbers_range)

        # 모서리 패턴 설정
        corner_settings = ttk.LabelFrame(scrollable_frame, text="모서리 패턴 설정", padding=5)
        corner_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(corner_settings, "모서리 숫자 개수", "corner_numbers_range",
                                  self.config.corner_numbers_range)
        self.create_value_setting(corner_settings, "한 모서리 최대 숫자", "corner_max_per_side",
                                  self.config.corner_max_per_side)
        self.create_value_setting(corner_settings, "대각선 최대 차이", "corner_diagonal_diff",
                                  self.config.corner_diagonal_diff)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def create_ratio_setting(self, parent, label, attr, range_tuple):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)

        ttk.Label(frame, text=f"{label}:").pack(side="left", padx=5)

        first_var = tk.StringVar(value=str(range_tuple[0]))
        second_var = tk.StringVar(value=str(range_tuple[1]))

        ttk.Entry(frame, textvariable=first_var, width=3).pack(side="left", padx=2)
        ttk.Label(frame, text=":").pack(side="left")
        ttk.Entry(frame, textvariable=second_var, width=3).pack(side="left", padx=2)

        setattr(self, f"{attr}_vars", (first_var, second_var))

    def create_range_setting(self, parent, label, attr, default_range):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=2)

        ttk.Label(frame, text=f"{label}:").pack(side="left", padx=5)

        min_var = tk.StringVar(value=str(default_range[0]))
        max_var = tk.StringVar(value=str(default_range[1]))

        ttk.Entry(frame, textvariable=min_var, width=5).pack(side="left", padx=2)
        ttk.Label(frame, text="~").pack(side="left")
        ttk.Entry(frame, textvariable=max_var, width=5).pack(side="left", padx=2)

        setattr(self, f"{attr}_vars", (min_var, max_var))

        # 설정 설명 추가 (모서리 패턴인 경우)
        if attr == "corner_numbers_range":
            desc_frame = ttk.Frame(parent)
            desc_frame.pack(fill="x", padx=5, pady=5)
            desc_text = """모서리 패턴 설정 가이드:
- 모서리 숫자 개수: 전체 모서리 숫자의 허용 범위
- 한 모서리 최대 숫자: 한 모서리에 올 수 있는 최대 숫자 개수
- 대각선 최대 차이: 대각선 방향 모서리 숫자 개수의 최대 차이

* 설정은 자동으로 저장되며, 프로그램 재시작 시 복원됩니다."""

            desc_label = ttk.Label(desc_frame, text=desc_text, wraplength=350, justify="left")
            desc_label.pack(fill="x", padx=5)

    def setup_settings_tab(self):
        self.settings_frame = ttk.LabelFrame(self.settings_tab, text="규칙별 상세 설정", padding=10)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 설정 버튼 프레임
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        # 설정 저장/불러오기 버튼
        ttk.Button(button_frame, text="현재 설정 저장", command=self.save_current_settings).pack(side="left", padx=5)
        ttk.Button(button_frame, text="기본값으로 복원", command=self.restore_default_settings).pack(side="left", padx=5)

        # 스크롤 가능한 메인 프레임 생성
        self.canvas = tk.Canvas(self.settings_frame)
        self.scrollbar = ttk.Scrollbar(self.settings_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # 기본 설정
        basic_settings = ttk.LabelFrame(self.scrollable_frame, text="기본 설정", padding=5)
        basic_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(basic_settings, "총합 구간", "sum_range", self.config.sum_range)
        self.create_value_setting(basic_settings, "최소 AC값", "ac_value_min", self.config.ac_value_min)

        # 비율 설정
        ratio_settings = ttk.LabelFrame(self.scrollable_frame, text="비율 설정", padding=5)
        ratio_settings.pack(fill="x", padx=5, pady=5)

        self.create_ratio_setting(ratio_settings, "홀짝 비율", "odd_even_ratio", (0, 6))
        self.create_ratio_setting(ratio_settings, "고저 비율", "high_low_ratio", (0, 6))

        # 개수 설정
        count_settings = ttk.LabelFrame(self.scrollable_frame, text="개수 설정", padding=5)
        count_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(count_settings, "소수 개수", "prime_range", self.config.prime_range)
        self.create_range_setting(count_settings, "합성수 개수", "composite_range", self.config.composite_range)
        self.create_range_setting(count_settings, "끝수 총합 구간", "last_digit_sum_range", self.config.last_digit_sum_range)
        self.create_range_setting(count_settings, "3의 배수 개수", "multiples_of_3_range", self.config.multiples_of_3_range)
        self.create_range_setting(count_settings, "5의 배수 개수", "multiples_of_5_range", self.config.multiples_of_5_range)
        self.create_range_setting(count_settings, "제곱수 개수", "perfect_square_range", self.config.perfect_square_range)
        self.create_value_setting(count_settings, "연속번호 쌍 개수", "consecutive_pairs", 1)
        self.create_range_setting(count_settings, "쌍수 개수", "twin_numbers_range", self.config.twin_numbers_range)

        # 모서리 패턴 설정
        corner_settings = ttk.LabelFrame(self.scrollable_frame, text="모서리 패턴 설정", padding=5)
        corner_settings.pack(fill="x", padx=5, pady=5)

        self.create_range_setting(corner_settings, "모서리 숫자 개수", "corner_numbers_range",
                                  self.config.corner_numbers_range)
        self.create_value_setting(corner_settings, "한 모서리 최대 숫자", "corner_max_per_side",
                                  self.config.corner_max_per_side)
        self.create_value_setting(corner_settings, "대각선 최대 차이", "corner_diagonal_diff",
                                  self.config.corner_diagonal_diff)

        # 스크롤바와 캔버스 패킹
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # 설정 설명
        desc_frame = ttk.Frame(corner_settings)
        desc_frame.pack(fill="x", padx=5, pady=5)
        desc_text = """모서리 패턴 설정 가이드:
- 모서리 숫자 개수: 전체 모서리 숫자의 허용 범위
- 한 모서리 최대 숫자: 한 모서리에 올 수 있는 최대 숫자 개수
- 대각선 최대 차이: 대각선 방향 모서리 숫자 개수의 최대 차이

* 설정은 자동으로 저장되며, 프로그램 재시작 시 복원됩니다."""

        desc_label = ttk.Label(desc_frame, text=desc_text, wraplength=350, justify="left")
        desc_label.pack(fill="x", padx=5)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def save_current_settings(self):
        # 현재 UI의 값들을 config 객체에 반영
        try:
            self.update_config_from_ui()
            self.config.save_settings()
            messagebox.showinfo("알림", "설정이 성공적으로 저장되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")

    def restore_default_settings(self):
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 되돌리시겠습니까?"):
            self.config.load_default_settings()
            self.update_ui_from_config()
            messagebox.showinfo("알림", "설정이 기본값으로 복원되었습니다.")

    def update_config_from_ui(self):
        # UI의 현재 값을 config 객체에 반영
        for rule_key, var in self.rule_vars.items():
            self.config.rules_enabled[rule_key] = var.get()

        # 각종 설정값 업데이트
        self.config.games_count = int(self.games_count_var.get())
        # ... 기타 설정값들 업데이트

    def update_ui_from_config(self):
        # config 객체의 값을 UI에 반영
        for rule_key, var in self.rule_vars.items():
            var.set(self.config.rules_enabled[rule_key])

        self.games_count_var.set(str(self.config.games_count))
        # ... 기타 UI 요소들 업데이트

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def setup_help_tab(self):
        frame = ttk.Frame(self.help_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 도움말 텍스트 스크롤
        help_text = """로또 타파 분석법 도움말

1. 총합구간 (100 ~ 175)
- 선택된 6개 번호의 총합이 이 구간에 있어야 합니다.
- 출현 확률 90% 이상

2. AC값 (7 이상)
- 번호들 간의 차이값의 고유한 개수로 계산
- 출현 확률 80% 이상 (8)

3. 홀짝 비율 분석
- 제외 조건: 6:0 또는 0:6 비율 제외
- 설명: 홀수와 짝수의 분포 비율
- 권장: 3:3, 4:2, 2:4 비율 추천 (3:3)

4. 고저 비율 분석
- 기준: 23을 기준으로 고저 구분
- 제외 조건: 6:0 또는 0:6 비율 제외
- 권장: 3:3, 4:2, 2:4 비율 추천 (3:3)

5. 소수 분석
- 소수 번호: 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43
- 권장 개수: 1 ~ 3개
근거: 4개 이상 포함 시 당첨 확률 1% 미만

6. 합성수 분석
- 합성수 번호: 1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44
- 권장 개수: 1 ~ 4개
- 근거: 5개 이상 포함 시 당첨 확률 10% 미만

7. 끝수 분석
- 범위: 15~35
- 설명: 각 번호의 일의 자리 숫자 합
- 계산 방법:
    - 한 자리 수는 그대로 사용
    - 두 자리 수는 끝자리만 사용

8. 배수 분석
- 3의 배수: 1~3개 권장
- 4의 배수: 0~3개 권장
- 5의 배수: 0~2개 권장

9. 제곱수 분석
- 제곱수 번호: 1, 4, 9, 16, 25, 36
- 권장 개수: 0~1개

10. 연속수 분석
-권장 패턴: (0 ~ 1)
    - 연속번호 없음
    - 2연속 1쌍
    - 2연속 2쌍
- 예시:
    - 1,2 (2연속 1쌍)
    - 1,2,8,9 (2연속 2쌍)
    
11. 쌍수 분석
- 쌍수 번호: 11, 22, 33, 44
- 권장 개수: 0~2개 (0 ~ 1)

12. 모서리 패턴 분석
- 대상 영역:
    - 좌측 상단: 1, 2, 8, 9
    - 우측 상단: 6, 7, 13, 14
    - 좌측 하단: 29, 30, 36, 37
    - 우측 하단: 34, 35, 41, 42
- 권장 개수: 1~4개
- 추가 규칙:
    - 한 모서리당 최대 2개
    - 대각선 방향 차이 2 이하


근거: 출현 빈도 90% 이상
[이하 각 규칙별 상세 설명...]"""

        text_widget = tk.Text(frame, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)

        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        text_widget.insert(tk.END, help_text)
        text_widget.configure(state="disabled")

    def toggle_all_rules(self):
        state = self.all_rules_var.get()
        for var in self.rule_vars.values():
            var.set(state)
        self.update_rules_state()

    def toggle_rule(self, rule_key):
        self.config.rules_enabled[rule_key] = self.rule_vars[rule_key].get()
        self.update_rules_state()

    def update_rules_state(self):
        # 모든 규칙의 상태를 설정에 반영
        for rule_key, var in self.rule_vars.items():
            self.config.rules_enabled[rule_key] = var.get()

    def create_range_setting(self, parent, label, attr, default_range):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=label).pack(side="left", padx=5)

        min_var = tk.StringVar(value=str(default_range[0]))
        max_var = tk.StringVar(value=str(default_range[1]))

        ttk.Entry(frame, textvariable=min_var, width=5).pack(side="left", padx=5)
        ttk.Label(frame, text="~").pack(side="left")
        ttk.Entry(frame, textvariable=max_var, width=5).pack(side="left", padx=5)

        setattr(self, f"{attr}_vars", (min_var, max_var))

    def create_value_setting(self, parent, label, attr, default_value):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=label).pack(side="left", padx=5)

        var = tk.StringVar(value=str(default_value))
        ttk.Entry(frame, textvariable=var, width=5).pack(side="left", padx=5)

        setattr(self, f"{attr}_var", var)

    def save_settings(self):
        try:
            # 게임 수 저장
            self.config.games_count = int(self.games_count_var.get())

            # 규칙 활성화 상태 저장
            self.update_rules_state()

            # 각 규칙별 설정값 저장
            for rule_key, var in self.rule_vars.items():
                self.config.rules_enabled[rule_key] = var.get()

            messagebox.showinfo("알림", "설정이 저장되었습니다.")
        except ValueError:
            messagebox.showerror("오류", "올바른 값을 입력해주세요.")

    def generate_numbers(self):
        try:
            self.config.games_count = int(self.games_count_var.get())
            numbers = self.analyzer.generate_numbers()

            self.result_text.delete(1.0, tk.END)
            if numbers:
                for i, nums in enumerate(numbers, 1):
                    self.result_text.insert(tk.END, f"{i}게임: {', '.join(map(str, nums))}\n")
            else:
                self.result_text.insert(tk.END, "선택한 조건에 맞는 번호를 찾을 수 없습니다.\n조건을 완화해주세요.")
        except ValueError:
            messagebox.showerror("오류", "올바른 게임 수를 입력해주세요.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = LottoGUI()
    app.run()
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import json
import os

from lotto_analyzer import LottoAnalyzer
from lotto_config import LottoConfig
from ml_integration import LottoMLIntegration

# 로깅 설정
logger = logging.getLogger('LottoGUI')


class LottoGUI:
    """
    로또 타파 분석기 GUI 클래스
    프로그램의 사용자 인터페이스와 사용자 상호작용을 관리합니다.
    """

    def __init__(self, delayed_ml_init=False):
        """초기화 함수: UI 구성 요소 설정 및 기본 변수 초기화"""
        # 메인 윈도우 설정
        self.root = tk.Tk()
        self.root.title("로또 타파 분석기 - AI 확장")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # 설정 및 분석기 인스턴스 생성
        self.config = LottoConfig()
        self.analyzer = LottoAnalyzer(self.config)
        self.ml_integration = LottoMLIntegration(self.root)

        # 지연된 ML 초기화
        if delayed_ml_init:
            # 일단 빈 프레임만 생성
            self.ml_tab = None
            # 나중에 초기화될 ML 모듈에 대한 참조 생성
            self.ml_integration = None
            # ML 초기화 버튼 표시 플래그
            self.show_ml_init_button = True
        else:
            # 즉시 ML 모듈 초기화
            self.ml_integration = LottoMLIntegration(self.root)
            self.show_ml_init_button = False


        # 스타일 설정
        self.setup_styles()

        # 노트북(탭) 생성
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, expand=True, fill="both")

        # 탭 설정
        self.setup_tabs()

        # 상태 바 설정
        self.setup_statusbar()

        # 설정 로드
        self.load_settings()

    def setup_styles(self):
        """UI 스타일 설정"""
        style = ttk.Style()

        # 일반 버튼 스타일
        style.configure("TButton", padding=6, relief="flat", background="#2E86C1")

        # 강조 버튼 스타일
        style.configure("Accent.TButton", background="#2ECC71", font=("Helvetica", 10, "bold"))

        # 프레임 스타일
        style.configure("TFrame", background="#F8F9F9")
        style.configure("TLabelframe", background="#F8F9F9")
        style.configure("TLabelframe.Label", font=("Helvetica", 10, "bold"))

        # 노트북 스타일
        style.configure("TNotebook", background="#F8F9F9")
        style.configure("TNotebook.Tab", padding=[12, 4], font=("Helvetica", 10))

    def setup_tabs(self):
        """탭 구성 설정"""
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

        # 머신러닝 탭 (지연 초기화 지원)
        if self.ml_integration:
            # 이미 초기화된 경우
            self.ml_integration.setup_ui(self.notebook)
        else:
            # 아직 초기화되지 않은 경우 빈 탭 추가
            self.ml_tab = ttk.Frame(self.notebook)
            self.notebook.add(self.ml_tab, text="머신러닝")

            # 초기화 버튼 추가
            init_frame = ttk.Frame(self.ml_tab, padding=20)
            init_frame.pack(expand=True, fill="both")

            ttk.Label(
                init_frame,
                text="머신러닝 기능이 아직 초기화되지 않았습니다.\n계속하려면 아래 버튼을 클릭하세요.",
                wraplength=400,
                justify="center",
                font=("Helvetica", 12)
            ).pack(pady=20)

            ttk.Button(
                init_frame,
                text="머신러닝 기능 초기화",
                command=self.initialize_ml_module,
                style="Accent.TButton"
            ).pack(pady=10, ipadx=10, ipady=5)

            ttk.Label(
                init_frame,
                text="참고: 이 과정은 잠시 시간이 소요될 수 있습니다.",
                wraplength=400,
                justify="center",
                font=("Helvetica", 10)
            ).pack(pady=10)

        # 각 탭 내용 설정
        self.setup_main_tab()
        self.setup_rules_tab()
        self.setup_settings_tab()
        self.setup_help_tab()

    def initialize_ml_module(self):
        """머신러닝 모듈 지연 초기화"""
        try:
            # 초기화 중 메시지
            init_label = ttk.Label(
                self.ml_tab,
                text="머신러닝 모듈을 초기화하는 중...\n잠시만 기다려주세요.",
                wraplength=400,
                justify="center",
                font=("Helvetica", 12)
            )
            init_label.pack(expand=True, pady=50)
            self.root.update_idletasks()

            # ML 모듈 초기화
            self.ml_integration = LottoMLIntegration(self.root)

            # 기존 탭 제거
            self.notebook.forget(self.ml_tab)

            # 새 탭 설정
            self.ml_integration.setup_ui(self.notebook)

            # 성공 메시지
            self.status_var.set("머신러닝 모듈 초기화 완료")
        except Exception as e:
            # 오류 처리
            logger.error(f"ML 모듈 초기화 오류: {str(e)}")
            messagebox.showerror("초기화 오류", f"머신러닝 모듈 초기화 중 오류가 발생했습니다:\n{str(e)}")

            # 재시도 버튼 표시
            if hasattr(self, 'ml_tab') and self.ml_tab:
                for widget in self.ml_tab.winfo_children():
                    widget.destroy()

                error_frame = ttk.Frame(self.ml_tab, padding=20)
                error_frame.pack(expand=True, fill="both")

                ttk.Label(
                    error_frame,
                    text=f"머신러닝 모듈 초기화 중 오류가 발생했습니다:\n{str(e)}",
                    wraplength=400,
                    justify="center",
                    foreground="red",
                    font=("Helvetica", 12)
                ).pack(pady=20)

                ttk.Button(
                    error_frame,
                    text="다시 시도",
                    command=self.initialize_ml_module
                ).pack(pady=10)

    def setup_statusbar(self):
        """상태 바 설정"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN, padding=(2, 1))
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

        # 상태 메시지
        self.status_var = tk.StringVar(value="준비")
        status_label = ttk.Label(self.statusbar, textvariable=self.status_var)
        status_label.pack(side=tk.LEFT, padx=5)

        # 버전 정보
        version_label = ttk.Label(self.statusbar, text="v2.0")
        version_label.pack(side=tk.RIGHT, padx=5)

    def setup_main_tab(self):
        """메인 탭 설정"""
        frame = ttk.LabelFrame(self.main_tab, text="번호 생성", padding=10)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 상단 컨트롤 프레임
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", pady=10)

        # 게임 수 설정
        ttk.Label(control_frame, text="생성할 게임 수:").pack(side="left", padx=5)
        self.games_count_var = tk.StringVar(value=str(self.config.games_count))
        ttk.Entry(control_frame, textvariable=self.games_count_var, width=5).pack(side="left", padx=5)

        # 번호 생성 버튼 프레임
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", pady=10)

        # 규칙 기반 번호 생성 버튼
        generate_btn = ttk.Button(
            button_frame,
            text="규칙 기반 번호 생성",
            command=self.generate_numbers,
            style="Accent.TButton"
        )
        generate_btn.pack(side="left", padx=5, expand=True, fill="x")

        # AI 번호 생성 바로가기 버튼
        ai_generate_btn = ttk.Button(
            button_frame,
            text="AI 번호 생성",
            command=lambda: self.notebook.select(4)  # ML 탭으로 이동
        )
        ai_generate_btn.pack(side="left", padx=5, expand=True, fill="x")

        # 결과 프레임
        result_frame = ttk.LabelFrame(frame, text="생성 결과", padding=5)
        result_frame.pack(fill="both", expand=True, pady=10)

        # 스크롤바 추가
        scrollbar = ttk.Scrollbar(result_frame)
        scrollbar.pack(side="right", fill="y")

        # 결과 텍스트 영역
        self.result_text = tk.Text(
            result_frame,
            height=20,
            width=50,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.result_text.yview)

        # 초기 안내 메시지
        welcome_msg = """
        환영합니다! 로또 타파 분석기 - AI 확장 버전입니다.

        ▶ 규칙 기반 번호 생성: 12가지 통계 규칙 적용 (왼쪽 버튼)
        ▶ AI 번호 생성: 머신러닝 기반 예측 (오른쪽 버튼 또는 '머신러닝' 탭)

        먼저 원하는 게임 수를 설정하고 번호 생성 버튼을 클릭하세요.
        규칙을 변경하려면 '규칙 선택' 탭에서 원하는 규칙을 선택/해제할 수 있습니다.
        """
        self.result_text.insert(tk.END, welcome_msg.strip())

    def setup_rules_tab(self):
        """규칙 선택 탭 설정"""
        main_frame = ttk.Frame(self.rules_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 안내 레이블
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill="x", pady=5)

        ttk.Label(
            info_frame,
            text="적용할 규칙을 선택하세요. 규칙이 많을수록 조건이 엄격해집니다.",
            wraplength=600,
            justify="left"
        ).pack(anchor="w", padx=5, pady=5)

        # 규칙 선택 프레임
        rules_frame = ttk.LabelFrame(main_frame, text="적용할 규칙 선택", padding=10)
        rules_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 전체 선택/해제 체크박스
        self.all_rules_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            rules_frame,
            text="전체 선택/해제",
            variable=self.all_rules_var,
            command=self.toggle_all_rules
        ).pack(pady=5)

        ttk.Separator(rules_frame, orient='horizontal').pack(fill='x', pady=5)

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

        # 규칙 설명 추가 정보
        rule_tooltips = {
            'sum_range': '6개 번호의 총합이 100~175 사이여야 함 (90% 확률)',
            'ac_value': '번호 간 차이값의 고유한 개수가 다양해야 함 (AC값 7 이상)',
            'odd_even': '홀수와 짝수의 비율 제한 (모두 홀수 또는 모두 짝수 제외)',
            'high_low': '저번호(1~22)와 고번호(23~45)의 비율 제한',
            'prime': '소수 개수 제한 (2,3,5,7,11,...,43)',
            'composite': '합성수 개수 제한',
            'last_digit': '각 번호의 일의 자리 숫자 합계 범위 제한',
            'multiples': '3의 배수와 5의 배수 개수 제한',
            'perfect_square': '제곱수(1,4,9,16,25,36) 개수 제한',
            'consecutive': '연속된 번호 패턴 제한',
            'twin': '쌍수(11,22,33,44) 개수 제한',
            'corner': '로또용지 모서리 영역 번호 분포 제한'
        }

        # 체크박스 2열로 배치
        rules_inner_frame = ttk.Frame(rules_frame)
        rules_inner_frame.pack(fill="both", expand=True)

        left_frame = ttk.Frame(rules_inner_frame)
        left_frame.pack(side="left", fill="both", expand=True)

        right_frame = ttk.Frame(rules_inner_frame)
        right_frame.pack(side="left", fill="both", expand=True)

        # 규칙 체크박스 생성
        for i, (rule_key, description) in enumerate(rule_descriptions.items()):
            frame = left_frame if i < 6 else right_frame
            var = tk.BooleanVar(value=self.config.rules_enabled[rule_key])
            self.rule_vars[rule_key] = var

            rule_frame = ttk.Frame(frame)
            rule_frame.pack(fill="x", pady=2)

            cb = ttk.Checkbutton(
                rule_frame,
                text=description,
                variable=var,
                command=lambda k=rule_key: self.toggle_rule(k)
            )
            cb.pack(side="left", anchor="w")

            # 도움말 버튼 (물음표 아이콘)
            help_button = ttk.Button(
                rule_frame,
                text="?",
                width=2,
                command=lambda r=rule_key, d=rule_tooltips[rule_key]: self.show_rule_help(r, d)
            )
            help_button.pack(side="right", padx=5)

        # 하단 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=10)

        ttk.Button(
            button_frame,
            text="변경 사항 저장",
            command=self.save_rule_settings
        ).pack(side="right", padx=5)

        ttk.Button(
            button_frame,
            text="기본값으로 복원",
            command=self.restore_default_rules
        ).pack(side="right", padx=5)

    def setup_settings_tab(self):
        """상세 설정 탭 설정"""
        self.settings_frame = ttk.LabelFrame(self.settings_tab, text="규칙별 상세 설정", padding=10)
        self.settings_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 설정 버튼 프레임
        button_frame = ttk.Frame(self.settings_frame)
        button_frame.pack(fill="x", padx=5, pady=5)

        # 설정 저장/불러오기 버튼
        ttk.Button(
            button_frame,
            text="현재 설정 저장",
            command=self.save_current_settings
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="기본값으로 복원",
            command=self.restore_default_settings
        ).pack(side="left", padx=5)

        # 스크롤 가능한 메인 프레임 생성
        settings_content_frame = ttk.Frame(self.settings_frame)
        settings_content_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.canvas = tk.Canvas(settings_content_frame)
        self.scrollbar = ttk.Scrollbar(settings_content_frame, orient="vertical", command=self.canvas.yview)
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

        self.create_ratio_setting(ratio_settings, "홀짝 비율", "odd_even_ratio", (3, 3))
        self.create_ratio_setting(ratio_settings, "고저 비율", "high_low_ratio", (3, 3))

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

    def setup_help_tab(self):
        """도움말 탭 설정"""
        frame = ttk.Frame(self.help_tab)
        frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 도움말 제목
        ttk.Label(
            frame,
            text="로또 타파 분석기 - 도움말",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # 도움말 텍스트 스크롤 추가
        help_frame = ttk.Frame(frame)
        help_frame.pack(fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(help_frame)
        scrollbar.pack(side="right", fill="y")

        help_text_widget = tk.Text(
            help_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=10
        )
        help_text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=help_text_widget.yview)

        # 도움말 내용
        help_text = """
로또 타파 분석법 도움말

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
    - 좌측 하단: 29, 30, 36, 37, 43, 44
    - 우측 하단: 34, 35, 41, 42
- 권장 개수: 1~4개
- 추가 규칙:
    - 한 모서리당 최대 2개
    - 대각선 방향 차이 2 이하

AI 분석 모듈 사용법

1. '머신러닝' 탭 이용
- AI 모델을 이용해 로또 번호를 예측하려면 '머신러닝' 탭으로 이동하세요.
- 처음 사용 시 '모델 학습' 버튼을 클릭하여 AI 모델을 학습시켜야 합니다.
- 모델 학습은 데이터 양에 따라 시간이 소요될 수 있습니다.

2. 데이터 분석 활용
- '데이터 분석' 탭에서 과거 당첨 번호의 다양한 통계를 확인할 수 있습니다.
- 번호별 출현 빈도, 홀짝 비율, 고저 비율 등 여러 분석 정보를 제공합니다.

3. 하이브리드 접근
- 규칙 기반 생성과 AI 생성을 함께 활용하는 것이 가장 효과적입니다.
- AI가 제안한 번호 중 로또 타파 규칙에 부합하는 번호를 선택하거나,
- 규칙 기반으로 생성한 번호 중 AI 모델이 높은 점수를 준 번호를 선택하세요.

4. 성능 향상 팁
- 정기적으로 모델을 재학습하면 최신 당첨 패턴을 반영할 수 있습니다.
- 당첨 번호가 업데이트되면 '모델 재학습' 버튼을 클릭하세요.

주의사항: 로또는 확률 게임입니다. 이 프로그램은 통계적 패턴을 분석하지만, 당첨을 보장하지는 않습니다. 책임감 있는 복권 구매를 실천하세요.
        """

        help_text_widget.insert(tk.END, help_text.strip())
        help_text_widget.config(state="disabled")

    def create_ratio_setting(self, parent, label, attr, range_tuple):
        """비율 설정 UI 요소 생성

        Args:
            parent: 부모 위젯
            label: 레이블 텍스트
            attr: 연결할 속성 이름
            range_tuple: 기본값 튜플 (첫번째, 두번째)
        """
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
        """범위 설정 UI 요소 생성

        Args:
            parent: 부모 위젯
            label: 레이블 텍스트
            attr: 연결할 속성 이름
            default_range: 기본값 범위 튜플 (최소, 최대)
        """
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
        """단일 값 설정 UI 요소 생성

        Args:
            parent: 부모 위젯
            label: 레이블 텍스트
            attr: 연결할 속성 이름
            default_value: 기본값
        """
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)

        ttk.Label(frame, text=label).pack(side="left", padx=5)

        var = tk.StringVar(value=str(default_value))
        ttk.Entry(frame, textvariable=var, width=5).pack(side="left", padx=5)

        setattr(self, f"{attr}_var", var)

    def toggle_all_rules(self):
        """모든 규칙 체크박스 상태 토글"""
        state = self.all_rules_var.get()
        for var in self.rule_vars.values():
            var.set(state)
        self.update_rules_state()

    def toggle_rule(self, rule_key):
        """개별 규칙 체크박스 상태 변경

        Args:
            rule_key: 변경할 규칙 키
        """
        self.config.rules_enabled[rule_key] = self.rule_vars[rule_key].get()
        self.update_rules_state()

    def update_rules_state(self):
        """모든 규칙의 상태를 설정에 반영"""
        for rule_key, var in self.rule_vars.items():
            self.config.rules_enabled[rule_key] = var.get()

    def show_rule_help(self, rule_key, help_text):
        """규칙 도움말 표시

        Args:
            rule_key: 규칙 키
            help_text: 도움말 텍스트
        """
        messagebox.showinfo(f"규칙 설명: {rule_key}", help_text)

    def save_rule_settings(self):
        """규칙 설정 저장"""
        try:
            # 규칙 활성화 상태 저장
            self.update_rules_state()
            self.config.save_settings()
            messagebox.showinfo("알림", "규칙 설정이 저장되었습니다.")
        except Exception as e:
            logger.error(f"규칙 설정 저장 오류: {str(e)}")
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")

    def restore_default_rules(self):
        """규칙 설정 기본값으로 복원"""
        if messagebox.askyesno("확인", "모든 규칙 설정을 기본값으로 되돌리시겠습니까?"):
            # 기본 규칙 상태로 복원
            for rule_key in self.config.rules_enabled:
                self.config.rules_enabled[rule_key] = True

            # UI 업데이트
            for rule_key, var in self.rule_vars.items():
                var.set(True)

            self.all_rules_var.set(True)

            messagebox.showinfo("알림", "모든 규칙이 기본값으로 복원되었습니다.")

    def save_current_settings(self):
        """모든 설정 저장"""
        try:
            # 게임 수 저장
            self.config.games_count = int(self.games_count_var.get())

            # 규칙 활성화 상태 저장
            self.update_rules_state()

            # 각 규칙별 설정값 저장
            # 총합 범위
            min_val, max_val = self.sum_range_vars
            self.config.sum_range = (int(min_val.get()), int(max_val.get()))

            # AC값
            self.config.ac_value_min = int(self.ac_value_min_var.get())

            # 소수 범위
            min_val, max_val = self.prime_range_vars
            self.config.prime_range = (int(min_val.get()), int(max_val.get()))

            # 합성수 범위
            min_val, max_val = self.composite_range_vars
            self.config.composite_range = (int(min_val.get()), int(max_val.get()))

            # 끝수 총합 범위
            min_val, max_val = self.last_digit_sum_range_vars
            self.config.last_digit_sum_range = (int(min_val.get()), int(max_val.get()))

            # 3의 배수 범위
            min_val, max_val = self.multiples_of_3_range_vars
            self.config.multiples_of_3_range = (int(min_val.get()), int(max_val.get()))

            # 5의 배수 범위
            min_val, max_val = self.multiples_of_5_range_vars
            self.config.multiples_of_5_range = (int(min_val.get()), int(max_val.get()))

            # 제곱수 범위
            min_val, max_val = self.perfect_square_range_vars
            self.config.perfect_square_range = (int(min_val.get()), int(max_val.get()))

            # 연속번호 쌍 개수
            self.config.consecutive_pairs = int(self.consecutive_pairs_var.get())

            # 쌍수 범위
            min_val, max_val = self.twin_numbers_range_vars
            self.config.twin_numbers_range = (int(min_val.get()), int(max_val.get()))

            # 모서리 패턴 설정
            min_val, max_val = self.corner_numbers_range_vars
            self.config.corner_numbers_range = (int(min_val.get()), int(max_val.get()))

            self.config.corner_max_per_side = int(self.corner_max_per_side_var.get())
            self.config.corner_diagonal_diff = int(self.corner_diagonal_diff_var.get())

            # 설정 저장
            self.config.save_settings()

            # 상태 업데이트
            self.status_var.set("설정이 저장되었습니다.")
            messagebox.showinfo("알림", "모든 설정이 성공적으로 저장되었습니다.")
        except ValueError as e:
            logger.error(f"설정 저장 오류: {str(e)}")
            messagebox.showerror("입력 오류", "숫자 형식이 올바르지 않습니다. 모든 값이 정수인지 확인하세요.")
        except Exception as e:
            logger.error(f"설정 저장 오류: {str(e)}")
            messagebox.showerror("오류", f"설정 저장 중 오류가 발생했습니다:\n{str(e)}")

    def restore_default_settings(self):
        """모든 설정 기본값으로 복원"""
        if messagebox.askyesno("확인", "모든 설정을 기본값으로 되돌리시겠습니까?"):
            try:
                self.config.load_default_settings()
                self.update_ui_from_config()
                messagebox.showinfo("알림", "설정이 기본값으로 복원되었습니다.")
            except Exception as e:
                logger.error(f"설정 복원 오류: {str(e)}")
                messagebox.showerror("오류", f"설정 복원 중 오류가 발생했습니다:\n{str(e)}")

    def update_ui_from_config(self):
        """설정 값을 UI에 반영"""
        # 규칙 체크박스 업데이트
        for rule_key, var in self.rule_vars.items():
            var.set(self.config.rules_enabled[rule_key])

        # 게임 수 업데이트
        self.games_count_var.set(str(self.config.games_count))

        # 총합 범위
        min_var, max_var = self.sum_range_vars
        min_var.set(str(self.config.sum_range[0]))
        max_var.set(str(self.config.sum_range[1]))

        # AC값
        self.ac_value_min_var.set(str(self.config.ac_value_min))

        # 소수 범위
        min_var, max_var = self.prime_range_vars
        min_var.set(str(self.config.prime_range[0]))
        max_var.set(str(self.config.prime_range[1]))

        # 합성수 범위
        min_var, max_var = self.composite_range_vars
        min_var.set(str(self.config.composite_range[0]))
        max_var.set(str(self.config.composite_range[1]))

        # 끝수 총합 범위
        min_var, max_var = self.last_digit_sum_range_vars
        min_var.set(str(self.config.last_digit_sum_range[0]))
        max_var.set(str(self.config.last_digit_sum_range[1]))

        # 기타 설정값들...

    def load_settings(self):
        """저장된 설정 불러오기"""
        try:
            self.update_ui_from_config()
            self.status_var.set("설정을 로드했습니다.")
        except Exception as e:
            logger.error(f"설정 로드 오류: {str(e)}")
            self.status_var.set("설정 로드 중 오류가 발생했습니다.")

    def generate_numbers(self):
        """규칙 기반 번호 생성"""
        try:
            # 게임 수 설정
            try:
                games_count = int(self.games_count_var.get())
                if games_count < 1:
                    raise ValueError("게임 수는 1 이상이어야 합니다.")

                self.config.games_count = games_count
            except ValueError as e:
                messagebox.showerror("입력 오류", str(e))
                return

            # 상태 업데이트
            self.status_var.set("번호 생성 중...")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "번호를 생성하는 중입니다...\n\n")
            self.root.update()  # UI 업데이트

            # 번호 생성
            numbers = self.analyzer.generate_numbers()

            # 결과 표시
            self.result_text.delete(1.0, tk.END)

            if numbers:
                # 결과 헤더
                self.result_text.insert(tk.END, f"📊 규칙 기반 생성 결과 ({len(numbers)}게임) 📊\n\n")

                for i, nums in enumerate(numbers, 1):
                    # 번호 조합
                    formatted_numbers = " ".join(f"{num:02d}" for num in sorted(nums))
                    self.result_text.insert(tk.END, f"{i}번 조합: {formatted_numbers}\n")

                    # 번호 정보
                    odd_count = sum(1 for n in nums if n % 2 == 1)
                    even_count = 6 - odd_count

                    high_count = sum(1 for n in nums if n >= 23)
                    low_count = 6 - high_count

                    sum_value = sum(nums)

                    self.result_text.insert(
                        tk.END,
                        f"   [합계: {sum_value} | 홀짝: {odd_count}:{even_count} | 고저: {low_count}:{high_count}]\n\n"
                    )

                # 상태 업데이트
                self.status_var.set(f"{len(numbers)}게임 생성 완료")
            else:
                self.result_text.insert(tk.END, "⚠️ 선택한 조건에 맞는 번호를 찾을 수 없습니다.\n\n")
                self.result_text.insert(tk.END, "다음 사항을 확인해 보세요:\n")
                self.result_text.insert(tk.END, "1. 일부 규칙을 비활성화하거나\n")
                self.result_text.insert(tk.END, "2. 규칙의 범위를 넓히거나\n")
                self.result_text.insert(tk.END, "3. 더 적은 게임 수를 시도해 보세요.\n\n")
                self.result_text.insert(tk.END, "또는 '머신러닝' 탭에서 AI 기반 번호 생성을 이용해보세요.")

                # 상태 업데이트
                self.status_var.set("번호 생성 실패")
        except Exception as e:
            logger.error(f"번호 생성 오류: {str(e)}")
            messagebox.showerror("오류", f"번호 생성 중 오류가 발생했습니다:\n{str(e)}")
            self.status_var.set("번호 생성 중 오류 발생")

    def on_window_resize(self, event):
        """창 크기 변경 시 호출되는 이벤트 핸들러

        Args:
            event: 이벤트 객체
        """
        if event.widget == self.root and hasattr(self, 'canvas'):
            # 캔버스 크기 조정 (설정 탭)
            self.canvas.configure(width=event.width - 50)  # 스크롤바 공간 고려

    def run(self):
        """애플리케이션 실행"""
        # 창 크기 조정 이벤트 바인딩
        self.root.bind("<Configure>", self.on_window_resize)

        # 앱 시작
        self.root.mainloop()


if __name__ == "__main__":
    # 독립 실행 시 테스트
    app = LottoGUI()
    app.run()
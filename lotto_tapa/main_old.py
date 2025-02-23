import tkinter as tk
from tkinter import ttk, messagebox, font
from numbers_generator import LottoGenerator
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import pandas as pd

FONT_PATH = r'C:\Windows\Fonts\malgun.ttf'

root = tk.Tk()
root.title("Lotto Prediction & Analysis")

# 한글 폰트 설정 (예: Malgun Gothic, Arial 등)
root.option_add("*Font", "Malgun Gothic 10")  # 한글 지원 폰트 지정


def set_font():
    if os.path.exists(FONT_PATH):
        font_prop = fm.FontProperties(fname=FONT_PATH)
        plt.rcParams['font.family'] = font_prop.get_name()
    else:
        print("지정된 폰트 파일을 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")
        plt.rcParams['font.family'] = 'Malgun Gothic'

class LottoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lotto Prediction and Analysis")
        self.generator = LottoGenerator()

        self.tab_control = ttk.Notebook(root)

        # Prediction Tab
        self.prediction_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.prediction_tab, text='예측 번호 생성')
        self.create_prediction_tab()

        # Analysis Tab
        self.analysis_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.analysis_tab, text='분석')
        self.create_analysis_tab()

        self.tab_control.pack(expand=1, fill='both')


    def create_prediction_tab(self):
        ttk.Label(self.prediction_tab, text="게임 개수:").grid(column=0, row=0)
        self.num_games_entry = ttk.Entry(self.prediction_tab)
        self.num_games_entry.grid(column=1, row=0)
        self.generate_button = ttk.Button(self.prediction_tab, text="번호 생성", command=self.generate_numbers)
        self.generate_button.grid(column=2, row=0)

        self.results_text = tk.Text(self.prediction_tab, height=15, width=50)
        self.results_text.grid(column=0, row=1, columnspan=3)

    def generate_numbers(self):
        try:
            num_games = int(self.num_games_entry.get())
            past_results = self.generator.fetch_past_results()
            results = self.generator.generate_lotto_numbers(num_games, past_results)
            self.results_text.delete(1.0, tk.END)
            for i, result in enumerate(results, 1):
                self.results_text.insert(tk.END, f"게임 {i}: {result}\n")
            self.generator.save_to_csv(results)
        except ValueError:
            messagebox.showerror("입력 오류", "게임 개수를 올바르게 입력하세요.")

    def create_analysis_tab(self):
        analysis_methods = [
            ("번호 빈도 분석", self.frequency_analysis),
            ("연속 번호 분석", self.consecutive_numbers_analysis),
            ("홀수/짝수 비율 분석", self.odd_even_ratio_analysis),
            ("번호 총합 분석", self.sum_analysis),
            ("끝자리 숫자 분석", self.last_digit_analysis),
            ("구간별 번호 분포 분석", self.range_distribution_analysis),
            ("AC 값 분석", self.ac_value_analysis),
            ("소수/합성수 비율 분석", self.prime_composite_ratio_analysis),
            ("번호 간 간격 분석", self.interval_analysis),
            ("특정 패턴 출현 빈도 분석", self.pattern_frequency_analysis),
            ("동일 끝수 분석", self.same_end_digit_analysis)
        ]

        for i, (method_name, method_func) in enumerate(analysis_methods):
            button = ttk.Button(self.analysis_tab, text=method_name, command=method_func)
            button.grid(column=0, row=i)

    def frequency_analysis(self):
        past_results = self.generator.fetch_past_results()
        flat_numbers = [num for sublist in past_results for num in sublist]
        frequency = pd.Series(flat_numbers).value_counts().sort_index()

        plt.bar(frequency.index, frequency.values)
        plt.title("번호 빈도 분석")
        plt.xlabel("번호")
        plt.ylabel("출현 빈도")
        plt.show()

    def consecutive_numbers_analysis(self):
        past_results = self.generator.fetch_past_results()
        consecutive_count = 0
        for result in past_results:
            consecutive_count += sum(1 for i in range(len(result) - 1) if result[i] + 1 == result[i + 1])

        plt.hist([consecutive_count], bins=range(0, 7), align='left')
        plt.title("연속 번호 분석")
        plt.xlabel("연속 번호 쌍 수")
        plt.ylabel("빈도")
        plt.show()

    def odd_even_ratio_analysis(self):
        past_results = self.generator.fetch_past_results()
        odd_count = 0
        even_count = 0

        for result in past_results:
            odd_count += sum(1 for num in result if num % 2 != 0)
            even_count += sum(1 for num in result if num % 2 == 0)

        labels = ['홀수', '짝수']
        sizes = [odd_count, even_count]
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title("홀수/짝수 비율 분석")
        plt.show()

    def sum_analysis(self):
        past_results = self.generator.fetch_past_results()
        total_sums = [sum(result) for result in past_results]

        plt.hist(total_sums, bins=range(min(total_sums), max(total_sums) + 1, 5), alpha=0.7)
        plt.title("번호 총합 분석")
        plt.xlabel("총합")
        plt.ylabel("빈도")
        plt.show()

    def last_digit_analysis(self):
        past_results = self.generator.fetch_past_results()
        last_digits = [num % 10 for result in past_results for num in result]
        last_digit_counts = pd.Series(last_digits).value_counts().sort_index()

        plt.bar(last_digit_counts.index, last_digit_counts.values)
        plt.title("끝자리 숫자 분석")
        plt.xlabel("끝자리 숫자")
        plt.ylabel("출현 빈도")
        plt.show()

    def range_distribution_analysis(self):
        past_results = self.generator.fetch_past_results()
        ranges = [0] * 5  # [1-10, 11-20, 21-30, 31-40, 41-45]

        for result in past_results:
            for num in result:
                if num <= 10:
                    ranges[0] += 1
                elif num <= 20:
                    ranges[1] += 1
                elif num <= 30:
                    ranges[2] += 1
                elif num <= 40:
                    ranges[3] += 1
                else:
                    ranges[4] += 1

        plt.bar([f"{i * 10 + 1}-{(i + 1) * 10}" for i in range(5)], ranges)
        plt.title("구간별 번호 분포 분석")
        plt.xlabel("구간")
        plt.ylabel("빈도")
        plt.show()

    def ac_value_analysis(self):
        past_results = self.generator.fetch_past_results()
        ac_values = [self.generator.calculate_ac_value(result) for result in past_results]

        plt.hist(ac_values, bins=range(0, max(ac_values) + 1), alpha=0.7)
        plt.title("AC 값 분석")
        plt.xlabel("AC 값")
        plt.ylabel("빈도")
        plt.show()

    def prime_composite_ratio_analysis(self):
        past_results = self.generator.fetch_past_results()
        prime_count = 0
        composite_count = 0
        primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]

        for result in past_results:
            for num in result:
                if num in primes:
                    prime_count += 1
                else:
                    composite_count += 1

        plt.pie([prime_count, composite_count], labels=['소수', '합성수'], autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title("소수/합성수 비율 분석")
        plt.show()

    def interval_analysis(self):
        past_results = self.generator.fetch_past_results()
        intervals = []

        for result in past_results:
            for i in range(len(result) - 1):
                intervals.append(result[i + 1] - result[i])

        plt.hist(intervals, bins=range(0, max(intervals) + 1), alpha=0.7)
        plt.title("번호 간 간격 분석")
        plt.xlabel("간격")
        plt.ylabel("빈도")
        plt.show()

    def pattern_frequency_analysis(self):
        # Placeholder for specific pattern frequency analysis logic.
        messagebox.showinfo("특정 패턴 출현 빈도 분석", "이 기능은 아직 구현되지 않았습니다.")

    def same_end_digit_analysis(self):
        past_results = self.generator.fetch_past_results()
        same_end_digits = {}

        for result in past_results:
            last_digit = result[0] % 10
            if last_digit in same_end_digits:
                same_end_digits[last_digit] += 1
            else:
                same_end_digits[last_digit] = 1

        plt.bar(same_end_digits.keys(), same_end_digits.values())
        plt.title("동일 끝수 분석")
        plt.xlabel("끝수")
        plt.ylabel("빈도")
        plt.show()

    def run(self):
        self.root.mainloop()
        self.generator.close()

if __name__ == "__main__":
    set_font()
    root = tk.Tk()
    app = LottoApp(root)
    app.run()


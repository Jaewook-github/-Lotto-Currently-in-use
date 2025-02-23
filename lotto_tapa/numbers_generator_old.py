import sqlite3
import random
import os
import csv
from datetime import datetime

class LottoGenerator:
    def __init__(self, db_name='lotto.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def fetch_past_results(self):
        self.cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        return self.cursor.fetchall()

    def calculate_ac_value(self, numbers):
        differences = []
        for i in range(len(numbers)):
            for j in range(i + 1, len(numbers)):
                differences.append(numbers[j] - numbers[i])
        ac_value = len(set(differences)) - 5
        return ac_value

    def generate_combination(self, past_results):
        while True:
            numbers = sorted(random.sample(range(1, 46), 6))
            total_sum = sum(numbers)
            if not (100 <= total_sum <= 175):
                continue
            ac_value = self.calculate_ac_value(numbers)
            if ac_value < 7:
                continue
            odds = len([n for n in numbers if n % 2 != 0])
            if odds == 0 or odds == 6:
                continue
            highs = len([n for n in numbers if n >= 23])
            if highs == 0 or highs == 6:
                continue
            end_digits = [n % 10 for n in numbers]
            if len(set(end_digits)) < 3:
                continue
            if not (15 <= sum(end_digits) <= 38):
                continue
            consecutive = [n2 - n1 for n1, n2 in zip(numbers, numbers[1:])]
            if consecutive.count(1) > 2:
                continue
            primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43]
            prime_count = len([n for n in numbers if n in primes])
            if prime_count > 3:
                continue
            composite = [1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44]
            composite_count = len([n for n in numbers if n in composite])
            if composite_count > 3:
                continue
            squares = [1, 4, 9, 16, 25, 36]
            square_count = len([n for n in numbers if n in squares])
            if square_count > 2:
                continue
            multiples_of_3 = [n for n in numbers if n % 3 == 0]
            multiples_of_5 = [n for n in numbers if n % 5 == 0]
            if len(multiples_of_3) > 3 or len(multiples_of_5) > 2:
                continue
            doubles = [11, 22, 33, 44]
            double_count = len([n for n in numbers if n in doubles])
            if double_count > 2:
                continue
            if numbers[0] >= 14 or numbers[-1] <= 30:
                continue
            ranges = [1, 2, 3, 4, 5]
            groups = [0, 0, 0, 0, 0]
            for n in numbers:
                groups[(n - 1) // 10] += 1
            if max(groups) >= 4:
                continue
            corners = [1, 2, 8, 9, 6, 7, 13, 14, 29, 30, 36, 37, 34, 35, 41, 42]
            corner_count = len([n for n in numbers if n in corners])
            if not (1 <= corner_count <= 4):
                continue
            return numbers

    def generate_lotto_numbers(self, num_games=10, past_results=None):
        results = []
        for _ in range(num_games):
            results.append(self.generate_combination(past_results))
        return results

    def save_to_csv(self, results, directory="csv"):
        if not os.path.exists(directory):
            os.makedirs(directory)
        date_str = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(directory, f"{date_str}.csv")
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["게임", "번호"])
            for i, result in enumerate(results, 1):
                writer.writerow([f"게임 {i}", result])
        print(f"결과가 {filename}에 저장되었습니다.")

    def close(self):
        self.conn.close()

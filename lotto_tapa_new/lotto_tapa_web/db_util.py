import sqlite3
import os
from collections import Counter


class LottoDatabase:
    def __init__(self, db_path='data/lotto.db'):
        # 데이터베이스 파일 경로 설정
        self.db_path = db_path
        # 데이터베이스 파일이 있는 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def get_connection(self):
        """데이터베이스 연결 반환"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """데이터베이스 초기화 및 테이블 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 로또 결과 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lotto_results (
                draw_number INTEGER PRIMARY KEY,
                num1 INTEGER,
                num2 INTEGER,
                num3 INTEGER,
                num4 INTEGER,
                num5 INTEGER,
                num6 INTEGER,
                bonus INTEGER,
                money1 INTEGER,
                money2 INTEGER,
                money3 INTEGER,
                money4 INTEGER,
                money5 INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    def get_latest_draw_number(self):
        """가장 최근 회차 번호 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT MAX(draw_number) FROM lotto_results")
        latest_draw = cursor.fetchone()[0]

        conn.close()
        return latest_draw if latest_draw else 0

    def get_number_frequency(self):
        """각 번호별 출현 빈도수 계산"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        results = cursor.fetchall()

        # 모든 번호를 하나의 리스트로 합치기
        all_numbers = [num for result in results for num in result]

        # Counter를 사용하여 각 번호의 빈도수 계산
        frequency = Counter(all_numbers)

        # 1부터 45까지의 모든 번호에 대해 빈도수 계산 (없는 번호는 0으로 설정)
        frequency_dict = {num: frequency.get(num, 0) for num in range(1, 46)}

        conn.close()
        return frequency_dict

    def get_recent_draws(self, limit=10):
        """최근 N회 당첨번호 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus 
            FROM lotto_results 
            ORDER BY draw_number DESC 
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()

        # 결과를 보기 쉬운 형태로 변환
        recent_draws = []
        for row in results:
            draw_number = row[0]
            numbers = list(row[1:7])  # 당첨번호 6개
            bonus = row[7]  # 보너스 번호

            recent_draws.append({
                'draw_number': draw_number,
                'numbers': numbers,
                'bonus': bonus
            })

        conn.close()
        return recent_draws

    def get_sum_trend(self, limit=15):
        """최근 N회 당첨번호의 합계 트렌드 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT draw_number, num1, num2, num3, num4, num5, num6 
            FROM lotto_results 
            ORDER BY draw_number DESC 
            LIMIT ?
        ''', (limit,))

        results = cursor.fetchall()

        # 각 회차별 번호 합계 계산
        sum_trend = []
        for row in results:
            draw_number = row[0]
            numbers_sum = sum(row[1:7])

            sum_trend.append({
                'draw_number': draw_number,
                'sum': numbers_sum
            })

        # 회차 순서대로 정렬 (오름차순)
        sum_trend.sort(key=lambda x: x['draw_number'])

        conn.close()
        return sum_trend

    def get_odd_even_stats(self):
        """홀짝 비율 통계 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        results = cursor.fetchall()

        # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
        odd_even_counts = {i: 0 for i in range(7)}

        for row in results:
            odd_count = sum(1 for num in row if num % 2 == 1)  # 홀수 개수
            odd_even_counts[odd_count] += 1

        # 각 비율의 퍼센트 계산
        total = sum(odd_even_counts.values())
        odd_even_stats = {
            'counts': list(odd_even_counts.values()),
            'percentages': [round(count / total * 100, 1) for count in odd_even_counts.values()],
            'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
        }

        conn.close()
        return odd_even_stats

    def get_high_low_stats(self):
        """고저 비율 통계 조회 (기준: 23)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        results = cursor.fetchall()

        # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
        high_low_counts = {i: 0 for i in range(7)}

        for row in results:
            high_count = sum(1 for num in row if num >= 23)  # 고번호(23 이상) 개수
            high_low_counts[high_count] += 1

        # 각 비율의 퍼센트 계산
        total = sum(high_low_counts.values())
        high_low_stats = {
            'counts': list(high_low_counts.values()),
            'percentages': [round(count / total * 100, 1) for count in high_low_counts.values()],
            'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
        }

        conn.close()
        return high_low_stats

    def calculate_ac_value(self, numbers):
        """AC값 계산 (Arithmetic Complexity)"""
        sorted_numbers = sorted(numbers)
        differences = set()

        for i in range(len(sorted_numbers)):
            for j in range(i + 1, len(sorted_numbers)):
                differences.add(sorted_numbers[j] - sorted_numbers[i])

        return len(differences) - 5  # 총 차이값 개수에서 5를 뺀 값 반환

    def get_ac_value_stats(self):
        """AC값 분포 통계 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        results = cursor.fetchall()

        # 각 AC값별 카운트
        ac_counts = {i: 0 for i in range(16)}  # 0부터 15까지

        for row in results:
            ac_value = self.calculate_ac_value(row)
            ac_counts[ac_value] += 1

        # AC값 통계 반환
        ac_stats = {
            'counts': [ac_counts.get(i, 0) for i in range(16)],
            'labels': [str(i) for i in range(16)]
        }

        conn.close()
        return ac_stats

    def get_consecutive_pairs_stats(self):
        """연속된 숫자 쌍 개수 통계 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
        results = cursor.fetchall()

        # 연속 쌍 개수별 카운트 (0, 1, 2, 3)
        consecutive_counts = {i: 0 for i in range(6)}

        for row in results:
            sorted_numbers = sorted(row)
            consecutive_pairs = sum(1 for i in range(len(sorted_numbers) - 1)
                                    if sorted_numbers[i + 1] - sorted_numbers[i] == 1)
            consecutive_counts[consecutive_pairs] += 1

        # 각 경우의 퍼센트 계산
        total = sum(consecutive_counts.values())
        consecutive_stats = {
            'counts': list(consecutive_counts.values()),
            'percentages': [round(count / total * 100, 1) for count in consecutive_counts.values()],
            'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍', '연속 4쌍', '연속 5쌍']
        }

        conn.close()
        return consecutive_stats

    def get_stats_for_dashboard(self):
        """대시보드에 필요한 모든 통계 데이터 조회"""
        stats = {
            'frequency': self.get_number_frequency(),
            'recent_draws': self.get_recent_draws(),
            'sum_trend': self.get_sum_trend(),
            'odd_even': self.get_odd_even_stats(),
            'high_low': self.get_high_low_stats(),
            'ac_value': self.get_ac_value_stats(),
            'consecutive_pairs': self.get_consecutive_pairs_stats(),
            'latest_draw': self.get_latest_draw_number()
        }

        return stats
import sqlite3
import os
from collections import Counter
import time


class LottoDatabase:
    def __init__(self, db_path='data/lotto.db'):
        # 데이터베이스 파일 경로 설정
        self.db_path = db_path
        # 데이터베이스 파일이 있는 디렉토리가 없으면 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        # 캐시 상태
        self.cache = {}
        self.cache_timestamp = 0
        self.cache_TTL = 300  # 5분 캐시 수명

    def get_connection(self):
        """데이터베이스 연결 반환"""
        try:
            conn = sqlite3.connect(self.db_path)
            # 행을 사전 형태로 가져오도록 설정
            conn.row_factory = sqlite3.Row
            return conn
        except sqlite3.Error as e:
            print(f"데이터베이스 연결 오류: {e}")
            # 비상용 인메모리 데이터베이스 연결
            conn = sqlite3.connect(':memory:')
            conn.row_factory = sqlite3.Row
            return conn

    def init_db(self):
        """데이터베이스 초기화 및 테이블 생성"""
        try:
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
            print("데이터베이스 초기화 완료")
        except sqlite3.Error as e:
            print(f"데이터베이스 초기화 오류: {e}")

    def get_latest_draw_number(self):
        """가장 최근 회차 번호 조회"""
        try:
            # 캐시 확인
            if 'latest_draw' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['latest_draw']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT MAX(draw_number) as latest FROM lotto_results")
            result = cursor.fetchone()
            latest_draw = result['latest'] if result and result['latest'] else 0

            conn.close()

            # 캐시 업데이트
            self.cache['latest_draw'] = latest_draw
            self.cache_timestamp = time.time()

            return latest_draw
        except sqlite3.Error as e:
            print(f"최근 회차 조회 오류: {e}")
            return 0

    def get_number_frequency(self):
        """각 번호별 출현 빈도수 계산"""
        try:
            # 캐시 확인
            if 'frequency' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['frequency']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
            results = cursor.fetchall()

            # 모든 번호를 하나의 리스트로 합치기
            all_numbers = [num for result in results for num in (result['num1'], result['num2'], result['num3'],
                                                                 result['num4'], result['num5'], result['num6'])]

            # Counter를 사용하여 각 번호의 빈도수 계산
            frequency = Counter(all_numbers)

            # 1부터 45까지의 모든 번호에 대해 빈도수 계산 (없는 번호는 0으로 설정)
            frequency_dict = {num: frequency.get(num, 0) for num in range(1, 46)}

            conn.close()

            # 캐시 업데이트
            self.cache['frequency'] = frequency_dict

            return frequency_dict
        except sqlite3.Error as e:
            print(f"번호 빈도 조회 오류: {e}")
            # 오류 시 빈 딕셔너리 반환 (샘플 데이터가 대체됨)
            return {num: 0 for num in range(1, 46)}

    def get_recent_draws(self, limit=10):
        """최근 N회 당첨번호 조회"""
        try:
            # 캐시 확인
            cache_key = f'recent_draws_{limit}'
            if cache_key in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache[cache_key]

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
                draw_number = row['draw_number']
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                bonus = row['bonus']

                recent_draws.append({
                    'draw_number': draw_number,
                    'numbers': numbers,
                    'bonus': bonus
                })

            conn.close()

            # 캐시 업데이트
            self.cache[cache_key] = recent_draws

            return recent_draws
        except sqlite3.Error as e:
            print(f"최근 당첨번호 조회 오류: {e}")
            # 오류 시 빈 리스트 반환
            return []

    def get_sum_trend(self, limit=15):
        """최근 N회 당첨번호의 합계 트렌드 조회"""
        try:
            # 캐시 확인
            cache_key = f'sum_trend_{limit}'
            if cache_key in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache[cache_key]

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
                draw_number = row['draw_number']
                numbers_sum = sum([row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']])

                sum_trend.append({
                    'draw_number': draw_number,
                    'sum': numbers_sum
                })

            # 회차 순서대로 정렬 (오름차순)
            sum_trend.sort(key=lambda x: x['draw_number'])

            conn.close()

            # 캐시 업데이트
            self.cache[cache_key] = sum_trend

            return sum_trend
        except sqlite3.Error as e:
            print(f"당첨번호 합계 조회 오류: {e}")
            # 오류 시 빈 리스트 반환
            return []

    def get_odd_even_stats(self):
        """홀짝 비율 통계 조회"""
        try:
            # 캐시 확인
            if 'odd_even' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['odd_even']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
            results = cursor.fetchall()

            # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
            odd_even_counts = {i: 0 for i in range(7)}

            for row in results:
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                odd_count = sum(1 for num in numbers if num % 2 == 1)  # 홀수 개수
                odd_even_counts[odd_count] += 1

            # 각 비율의 퍼센트 계산
            total = sum(odd_even_counts.values()) or 1  # 0으로 나누기 방지
            odd_even_stats = {
                'counts': list(odd_even_counts.values()),
                'percentages': [round(count / total * 100, 1) for count in odd_even_counts.values()],
                'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
            }

            conn.close()

            # 캐시 업데이트
            self.cache['odd_even'] = odd_even_stats

            return odd_even_stats
        except sqlite3.Error as e:
            print(f"홀짝 비율 조회 오류: {e}")
            # 오류 시 기본값 반환
            return {
                'counts': [0, 0, 0, 0, 0, 0, 0],
                'percentages': [0, 0, 0, 0, 0, 0, 0],
                'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
            }

    def get_high_low_stats(self):
        """고저 비율 통계 조회 (기준: 23)"""
        try:
            # 캐시 확인
            if 'high_low' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['high_low']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
            results = cursor.fetchall()

            # 각 조합별 카운트 (0:6, 1:5, 2:4, 3:3, 4:2, 5:1, 6:0)
            high_low_counts = {i: 0 for i in range(7)}

            for row in results:
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                high_count = sum(1 for num in numbers if num >= 23)  # 고번호(23 이상) 개수
                high_low_counts[high_count] += 1

            # 각 비율의 퍼센트 계산
            total = sum(high_low_counts.values()) or 1  # 0으로 나누기 방지
            high_low_stats = {
                'counts': list(high_low_counts.values()),
                'percentages': [round(count / total * 100, 1) for count in high_low_counts.values()],
                'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
            }

            conn.close()

            # 캐시 업데이트
            self.cache['high_low'] = high_low_stats

            return high_low_stats
        except sqlite3.Error as e:
            print(f"고저 비율 조회 오류: {e}")
            # 오류 시 기본값 반환
            return {
                'counts': [0, 0, 0, 0, 0, 0, 0],
                'percentages': [0, 0, 0, 0, 0, 0, 0],
                'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
            }

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
        try:
            # 캐시 확인
            if 'ac_value' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['ac_value']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
            results = cursor.fetchall()

            # 각 AC값별 카운트
            ac_counts = {i: 0 for i in range(16)}  # 0부터 15까지

            for row in results:
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                ac_value = self.calculate_ac_value(numbers)
                ac_counts[ac_value] += 1

            # AC값 통계 반환
            ac_stats = {
                'counts': [ac_counts.get(i, 0) for i in range(16)],
                'labels': [str(i) for i in range(16)]
            }

            conn.close()

            # 캐시 업데이트
            self.cache['ac_value'] = ac_stats

            return ac_stats
        except sqlite3.Error as e:
            print(f"AC값 통계 조회 오류: {e}")
            # 오류 시 기본값 반환
            return {
                'counts': [0] * 16,
                'labels': [str(i) for i in range(16)]
            }

    def get_consecutive_pairs_stats(self):
        """연속된 숫자 쌍 개수 통계 조회"""
        try:
            # 캐시 확인
            if 'consecutive' in self.cache and time.time() - self.cache_timestamp < self.cache_TTL:
                return self.cache['consecutive']

            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT num1, num2, num3, num4, num5, num6 FROM lotto_results")
            results = cursor.fetchall()

            # 연속 쌍 개수별 카운트 (0, 1, 2, 3, 4, 5)
            consecutive_counts = {i: 0 for i in range(6)}

            for row in results:
                numbers = [row['num1'], row['num2'], row['num3'], row['num4'], row['num5'], row['num6']]
                sorted_numbers = sorted(numbers)
                consecutive_pairs = sum(1 for i in range(len(sorted_numbers) - 1)
                                        if sorted_numbers[i + 1] - sorted_numbers[i] == 1)
                consecutive_counts[consecutive_pairs] += 1

            # 각 경우의 퍼센트 계산
            total = sum(consecutive_counts.values()) or 1  # 0으로 나누기 방지
            consecutive_stats = {
                'counts': list(consecutive_counts.values()),
                'percentages': [round(count / total * 100, 1) for count in consecutive_counts.values()],
                'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍', '연속 4쌍', '연속 5쌍']
            }

            conn.close()

            # 캐시 업데이트
            self.cache['consecutive'] = consecutive_stats

            return consecutive_stats
        except sqlite3.Error as e:
            print(f"연속 숫자 통계 조회 오류: {e}")
            # 오류 시 기본값 반환
            return {
                'counts': [0, 0, 0, 0, 0, 0],
                'percentages': [0, 0, 0, 0, 0, 0],
                'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍', '연속 4쌍', '연속 5쌍']
            }

    def get_stats_for_dashboard(self):
        """대시보드에 필요한 모든 통계 데이터 조회"""
        try:
            # 모든 통계 데이터 모아서 반환
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

            # 캐시 타임스탬프 업데이트
            self.cache_timestamp = time.time()

            return stats
        except Exception as e:
            print(f"대시보드 통계 조회 오류: {e}")
            # 메모리 내 샘플 데이터 생성
            return self.generate_sample_stats()

    def generate_sample_stats(self):
        """샘플 통계 데이터 생성 (비상용)"""
        import random

        # 번호별 출현 빈도 (랜덤)
        frequency = {num: random.randint(50, 150) for num in range(1, 46)}

        # 최근 당첨 번호 (랜덤)
        recent_draws = []
        for i in range(10):
            numbers = sorted(random.sample(range(1, 46), 6))
            bonus = random.randint(1, 45)
            while bonus in numbers:
                bonus = random.randint(1, 45)

            recent_draws.append({
                'draw_number': 1000 - i,
                'numbers': numbers,
                'bonus': bonus
            })

        # 총합 트렌드 (랜덤)
        sum_trend = []
        for i in range(15):
            sum_trend.append({
                'draw_number': 986 + i,
                'sum': random.randint(100, 175)
            })

        # 홀짝 비율
        odd_even_stats = {
            'counts': [5, 18, 35, 42, 30, 15, 4],
            'percentages': [3.4, 12.1, 23.5, 28.2, 20.1, 10.1, 2.7],
            'labels': ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
        }

        # 고저 비율
        high_low_stats = {
            'counts': [6, 20, 38, 45, 32, 18, 5],
            'percentages': [3.7, 12.2, 23.2, 27.4, 19.5, 11.0, 3.0],
            'labels': ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
        }

        # AC값 분포
        ac_counts = [3, 5, 8, 10, 15, 20, 30, 35, 25, 18, 12, 8, 5, 3, 2, 1]
        ac_stats = {
            'counts': ac_counts,
            'labels': [str(i) for i in range(16)]
        }

        # 연속 숫자 쌍
        consecutive_stats = {
            'counts': [49, 65, 35, 15, 8, 3],
            'percentages': [28.0, 37.1, 20.0, 8.6, 4.6, 1.7],
            'labels': ['연속 0쌍', '연속 1쌍', '연속 2쌍', '연속 3쌍', '연속 4쌍', '연속 5쌍']
        }

        return {
            'frequency': frequency,
            'recent_draws': recent_draws,
            'sum_trend': sum_trend,
            'odd_even': odd_even_stats,
            'high_low': high_low_stats,
            'ac_value': ac_stats,
            'consecutive_pairs': consecutive_stats,
            'latest_draw': 1000
        }
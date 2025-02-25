import sqlite3
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LottoDB')


class LottoDBManager:
    """
    로또 데이터베이스 관리 클래스
    로또 당첨 결과 데이터를 관리하고 분석에 필요한 데이터를 제공합니다.
    """

    def __init__(self, db_path='lotto.db'):
        """
        LottoDBManager 초기화

        Args:
            db_path: 로또 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.initialize_db()

    def get_connection(self):
        """
        데이터베이스 연결 객체 반환

        Returns:
            sqlite3.Connection: 데이터베이스 연결 객체
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하도록 설정
            return conn
        except sqlite3.Error as e:
            logger.error(f"데이터베이스 연결 중 오류 발생: {str(e)}")
            return None

    def initialize_db(self):
        """
        데이터베이스 초기화 및 테이블 생성
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # 로또 당첨 결과 테이블 생성
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
                    money5 INTEGER,
                    draw_date TEXT,
                    created_at TEXT
                )
                ''')

                # 머신러닝 모델 성능 기록 테이블
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS model_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model_name TEXT,
                    accuracy REAL,
                    precision REAL,
                    recall REAL,
                    f1_score REAL,
                    training_date TEXT
                )
                ''')

                # 번호 예측 기록 테이블
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS prediction_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draw_number INTEGER,
                    num1 INTEGER,
                    num2 INTEGER,
                    num3 INTEGER,
                    num4 INTEGER,
                    num5 INTEGER,
                    num6 INTEGER,
                    model_name TEXT,
                    prediction_date TEXT,
                    hit_count INTEGER DEFAULT 0,
                    is_bonus_hit INTEGER DEFAULT 0
                )
                ''')

                conn.commit()
                logger.info("데이터베이스 초기화 완료")
            except sqlite3.Error as e:
                logger.error(f"데이터베이스 초기화 중 오류 발생: {str(e)}")
            finally:
                conn.close()

    def fetch_all_draws(self):
        """
        모든 로또 당첨 결과 조회

        Returns:
            list: 모든 로또 당첨 결과 리스트
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus 
                FROM lotto_results 
                ORDER BY draw_number ASC
                ''')
                results = cursor.fetchall()
                return [dict(row) for row in results]
            except sqlite3.Error as e:
                logger.error(f"데이터 조회 중 오류 발생: {str(e)}")
                return []
            finally:
                conn.close()
        return []

    def fetch_draws_as_dataframe(self):
        """
        로또 당첨 결과를 Pandas DataFrame으로 변환

        Returns:
            pandas.DataFrame: 로또 당첨 결과 데이터프레임
        """
        draws = self.fetch_all_draws()
        if draws:
            return pd.DataFrame(draws)
        return pd.DataFrame()

    def get_last_draw_number(self):
        """
        가장 최근 회차 번호 조회

        Returns:
            int: 가장 최근 회차 번호
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('SELECT MAX(draw_number) as last_draw FROM lotto_results')
                result = cursor.fetchone()
                return result['last_draw'] if result and result['last_draw'] else 0
            except sqlite3.Error as e:
                logger.error(f"최근 회차 조회 중 오류 발생: {str(e)}")
                return 0
            finally:
                conn.close()
        return 0

    def get_draw_by_number(self, draw_number):
        """
        특정 회차의 당첨 결과 조회

        Args:
            draw_number: 조회할 회차 번호

        Returns:
            dict: 해당 회차의 당첨 결과
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT * FROM lotto_results WHERE draw_number = ?
                ''', (draw_number,))
                result = cursor.fetchone()
                return dict(result) if result else None
            except sqlite3.Error as e:
                logger.error(f"회차 {draw_number} 조회 중 오류 발생: {str(e)}")
                return None
            finally:
                conn.close()
        return None

    def get_recent_draws(self, count=10):
        """
        최근 n회차의 당첨 결과 조회

        Args:
            count: 조회할 회차 수

        Returns:
            list: 최근 n회차의 당첨 결과 리스트
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus 
                FROM lotto_results 
                ORDER BY draw_number DESC LIMIT ?
                ''', (count,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
            except sqlite3.Error as e:
                logger.error(f"최근 {count}회차 조회 중 오류 발생: {str(e)}")
                return []
            finally:
                conn.close()
        return []

    def insert_draw(self, draw_data):
        """
        새로운 회차 결과 추가

        Args:
            draw_data: 추가할 회차 데이터 딕셔너리

        Returns:
            bool: 추가 성공 여부
        """
        required_fields = ['draw_number', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'bonus']
        for field in required_fields:
            if field not in draw_data:
                logger.error(f"필수 필드 누락: {field}")
                return False

        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # 같은 회차가 이미 있는지 확인
                cursor.execute('SELECT 1 FROM lotto_results WHERE draw_number = ?', (draw_data['draw_number'],))
                if cursor.fetchone():
                    logger.warning(f"회차 {draw_data['draw_number']}는 이미 존재합니다.")
                    return False

                # 현재 시간 추가
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                draw_data['created_at'] = now

                # 데이터 삽입
                fields = ', '.join(draw_data.keys())
                placeholders = ', '.join(['?' for _ in draw_data])
                sql = f'INSERT INTO lotto_results ({fields}) VALUES ({placeholders})'

                cursor.execute(sql, tuple(draw_data.values()))
                conn.commit()

                logger.info(f"회차 {draw_data['draw_number']} 추가 성공")
                return True
            except sqlite3.Error as e:
                logger.error(f"회차 추가 중 오류 발생: {str(e)}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def update_draw(self, draw_data):
        """
        기존 회차 결과 업데이트

        Args:
            draw_data: 업데이트할 회차 데이터 딕셔너리

        Returns:
            bool: 업데이트 성공 여부
        """
        if 'draw_number' not in draw_data:
            logger.error("회차 번호가 누락되었습니다.")
            return False

        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # 회차가 존재하는지 확인
                cursor.execute('SELECT 1 FROM lotto_results WHERE draw_number = ?', (draw_data['draw_number'],))
                if not cursor.fetchone():
                    logger.warning(f"회차 {draw_data['draw_number']}가 존재하지 않습니다.")
                    return False

                # draw_number는 업데이트에서 제외
                draw_number = draw_data.pop('draw_number')

                # 업데이트 SQL 생성
                set_clause = ', '.join([f"{key} = ?" for key in draw_data.keys()])
                sql = f'UPDATE lotto_results SET {set_clause} WHERE draw_number = ?'

                # 실행
                cursor.execute(sql, list(draw_data.values()) + [draw_number])
                conn.commit()

                logger.info(f"회차 {draw_number} 업데이트 성공")
                return True
            except sqlite3.Error as e:
                logger.error(f"회차 업데이트 중 오류 발생: {str(e)}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def record_model_performance(self, model_name, metrics):
        """
        모델 성능 기록

        Args:
            model_name: 모델 이름
            metrics: 성능 지표 딕셔너리 (accuracy, precision, recall, f1_score)

        Returns:
            bool: 기록 성공 여부
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                cursor.execute('''
                INSERT INTO model_performance 
                (model_name, accuracy, precision, recall, f1_score, training_date) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    model_name,
                    metrics.get('accuracy', 0),
                    metrics.get('precision', 0),
                    metrics.get('recall', 0),
                    metrics.get('f1_score', 0),
                    now
                ))

                conn.commit()
                logger.info(f"모델 '{model_name}' 성능 기록 완료")
                return True
            except sqlite3.Error as e:
                logger.error(f"모델 성능 기록 중 오류 발생: {str(e)}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def record_prediction(self, prediction_data):
        """
        번호 예측 기록

        Args:
            prediction_data: 예측 정보 딕셔너리 (draw_number, num1~num6, model_name)

        Returns:
            bool: 기록 성공 여부
        """
        required_fields = ['draw_number', 'num1', 'num2', 'num3', 'num4', 'num5', 'num6', 'model_name']
        for field in required_fields:
            if field not in prediction_data:
                logger.error(f"필수 필드 누락: {field}")
                return False

        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                # 예측 시간 추가
                prediction_data['prediction_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 데이터 삽입
                fields = ', '.join(prediction_data.keys())
                placeholders = ', '.join(['?' for _ in prediction_data])
                sql = f'INSERT INTO prediction_history ({fields}) VALUES ({placeholders})'

                cursor.execute(sql, tuple(prediction_data.values()))
                conn.commit()

                logger.info(f"회차 {prediction_data['draw_number']} 예측 기록 완료")
                return True
            except sqlite3.Error as e:
                logger.error(f"예측 기록 중 오류 발생: {str(e)}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def update_prediction_result(self, prediction_id, hit_count, is_bonus_hit):
        """
        예측 결과 업데이트 (당첨 번호와 비교 후)

        Args:
            prediction_id: 예측 기록 ID
            hit_count: 맞춘 번호 개수
            is_bonus_hit: 보너스 번호 맞춤 여부 (0 또는 1)

        Returns:
            bool: 업데이트 성공 여부
        """
        conn = self.get_connection()
        if conn:
            try:
                cursor = conn.cursor()

                cursor.execute('''
                UPDATE prediction_history 
                SET hit_count = ?, is_bonus_hit = ? 
                WHERE id = ?
                ''', (hit_count, is_bonus_hit, prediction_id))

                conn.commit()
                logger.info(f"예측 ID {prediction_id} 결과 업데이트 완료")
                return True
            except sqlite3.Error as e:
                logger.error(f"예측 결과 업데이트 중 오류 발생: {str(e)}")
                conn.rollback()
                return False
            finally:
                conn.close()
        return False

    def get_frequency_by_position(self):
        """
        각 위치별 번호 출현 빈도 계산

        Returns:
            dict: 위치별 번호 빈도 딕셔너리
        """
        conn = self.get_connection()
        if conn:
            try:
                frequency = {}
                cursor = conn.cursor()

                for pos in range(1, 7):
                    frequency[pos] = {}
                    for num in range(1, 46):
                        cursor.execute(f'SELECT COUNT(*) FROM lotto_results WHERE num{pos} = ?', (num,))
                        count = cursor.fetchone()[0]
                        frequency[pos][num] = count

                # 보너스 번호 빈도
                frequency['bonus'] = {}
                for num in range(1, 46):
                    cursor.execute('SELECT COUNT(*) FROM lotto_results WHERE bonus = ?', (num,))
                    count = cursor.fetchone()[0]
                    frequency['bonus'][num] = count

                return frequency
            except sqlite3.Error as e:
                logger.error(f"번호 빈도 계산 중 오류 발생: {str(e)}")
                return {}
            finally:
                conn.close()
        return {}

    def get_overall_frequency(self):
        """
        전체 번호 출현 빈도 계산 (위치 무관)

        Returns:
            dict: 번호별 출현 빈도 딕셔너리
        """
        conn = self.get_connection()
        if conn:
            try:
                frequency = {num: 0 for num in range(1, 46)}
                cursor = conn.cursor()

                for pos in range(1, 7):
                    for num in range(1, 46):
                        cursor.execute(f'SELECT COUNT(*) FROM lotto_results WHERE num{pos} = ?', (num,))
                        count = cursor.fetchone()[0]
                        frequency[num] += count

                return frequency
            except sqlite3.Error as e:
                logger.error(f"전체 빈도 계산 중 오류 발생: {str(e)}")
                return {}
            finally:
                conn.close()
        return {}

    def analyze_consecutive_numbers(self):
        """
        연속된 번호 패턴 분석

        Returns:
            dict: 연속 번호 패턴 통계
        """
        draws = self.fetch_all_draws()
        consecutive_stats = {
            'none': 0,  # 연속 번호 없음
            'one_pair': 0,  # 1쌍의 연속 번호
            'two_pairs': 0,  # 2쌍의 연속 번호
            'three_in_row': 0,  # 3개 연속 번호
            'four_plus': 0  # 4개 이상 연속 번호
        }

        for draw in draws:
            numbers = sorted([draw[f'num{i}'] for i in range(1, 7)])
            consecutive_count = 0

            for i in range(len(numbers) - 1):
                if numbers[i + 1] - numbers[i] == 1:
                    consecutive_count += 1

            if consecutive_count == 0:
                consecutive_stats['none'] += 1
            elif consecutive_count == 1:
                consecutive_stats['one_pair'] += 1
            elif consecutive_count == 2:
                # 2쌍인지 3연속인지 구분
                has_three_consecutive = False
                for i in range(len(numbers) - 2):
                    if numbers[i + 2] - numbers[i] == 2:
                        has_three_consecutive = True
                        break

                if has_three_consecutive:
                    consecutive_stats['three_in_row'] += 1
                else:
                    consecutive_stats['two_pairs'] += 1
            else:
                consecutive_stats['four_plus'] += 1

        # 백분율 계산
        total = len(draws)
        if total > 0:
            for key in consecutive_stats:
                consecutive_stats[f'{key}_percent'] = round(consecutive_stats[key] / total * 100, 2)

        return consecutive_stats

    def analyze_odd_even_ratio(self):
        """
        홀짝 비율 분석

        Returns:
            dict: 홀짝 비율 통계
        """
        draws = self.fetch_all_draws()
        odd_even_stats = {f'{odd}:{even}': 0 for odd in range(7) for even in range(7) if odd + even == 6}

        for draw in draws:
            numbers = [draw[f'num{i}'] for i in range(1, 7)]
            odd_count = sum(1 for n in numbers if n % 2 == 1)
            even_count = 6 - odd_count

            odd_even_stats[f'{odd_count}:{even_count}'] += 1

        # 백분율 계산
        total = len(draws)
        if total > 0:
            for key in odd_even_stats:
                odd_even_stats[f'{key}_percent'] = round(odd_even_stats[key] / total * 100, 2)

        return odd_even_stats

    def analyze_high_low_ratio(self):
        """
        고저 비율 분석 (1-22: 저, 23-45: 고)

        Returns:
            dict: 고저 비율 통계
        """
        draws = self.fetch_all_draws()
        high_low_stats = {f'{low}:{high}': 0 for low in range(7) for high in range(7) if low + high == 6}

        for draw in draws:
            numbers = [draw[f'num{i}'] for i in range(1, 7)]
            low_count = sum(1 for n in numbers if n < 23)
            high_count = 6 - low_count

            high_low_stats[f'{low_count}:{high_count}'] += 1

        # 백분율 계산
        total = len(draws)
        if total > 0:
            for key in high_low_stats:
                high_low_stats[f'{key}_percent'] = round(high_low_stats[key] / total * 100, 2)

        return high_low_stats

    def analyze_sum_distribution(self):
        """
        번호 합계 분포 분석

        Returns:
            dict: 합계 구간별 통계
        """
        draws = self.fetch_all_draws()
        sum_ranges = {
            '0-90': 0,
            '91-100': 0,
            '101-110': 0,
            '111-120': 0,
            '121-130': 0,
            '131-140': 0,
            '141-150': 0,
            '151-160': 0,
            '161-170': 0,
            '171-180': 0,
            '181-270': 0
        }

        for draw in draws:
            numbers = [draw[f'num{i}'] for i in range(1, 7)]
            total = sum(numbers)

            if total <= 90:
                sum_ranges['0-90'] += 1
            elif total <= 100:
                sum_ranges['91-100'] += 1
            elif total <= 110:
                sum_ranges['101-110'] += 1
            elif total <= 120:
                sum_ranges['111-120'] += 1
            elif total <= 130:
                sum_ranges['121-130'] += 1
            elif total <= 140:
                sum_ranges['131-140'] += 1
            elif total <= 150:
                sum_ranges['141-150'] += 1
            elif total <= 160:
                sum_ranges['151-160'] += 1
            elif total <= 170:
                sum_ranges['161-170'] += 1
            elif total <= 180:
                sum_ranges['171-180'] += 1
            else:
                sum_ranges['181-270'] += 1

        # 백분율 계산
        total = len(draws)
        if total > 0:
            for key in sum_ranges:
                sum_ranges[f'{key}_percent'] = round(sum_ranges[key] / total * 100, 2)

        return sum_ranges
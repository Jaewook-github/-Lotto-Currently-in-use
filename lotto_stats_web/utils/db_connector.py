# utils/db_connector.py - 데이터베이스 연결 유틸리티
import sqlite3
import os
from config import Config


class DatabaseConnector:
    """데이터베이스 연결 및 기본 쿼리 유틸리티 클래스"""

    @staticmethod
    def get_connection():
        """데이터베이스 연결 반환"""
        db_path = Config.DB_PATH
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return sqlite3.connect(db_path)

    @staticmethod
    def init_db():
        """데이터베이스 초기화 및 테이블 생성"""
        conn = DatabaseConnector.get_connection()
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
                draw_date TEXT,
                money1 INTEGER,
                money2 INTEGER,
                money3 INTEGER,
                money4 INTEGER,
                money5 INTEGER
            )
        ''')

        conn.commit()
        conn.close()

    @staticmethod
    def execute_query(query, params=(), fetch_all=True):
        """SQL 쿼리 실행 및 결과 반환"""
        conn = None
        try:
            conn = DatabaseConnector.get_connection()
            cursor = conn.cursor()

            cursor.execute(query, params)

            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                if fetch_all:
                    result = cursor.fetchall()
                else:
                    result = cursor.fetchone()
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            # SQLite 오류 처리
            error_msg = f"데이터베이스 오류: {str(e)}"
            print(error_msg)  # 콘솔에 출력

            # 테이블이 없는 경우 자동으로 생성 시도
            if 'no such table' in str(e).lower():
                try:
                    if conn:
                        conn.close()
                    DatabaseConnector.init_db()
                    print("테이블이 없어 자동으로 생성했습니다. 다시 시도해주세요.")
                except Exception as init_error:
                    print(f"테이블 생성 실패: {str(init_error)}")

            raise Exception(error_msg)
        except Exception as e:
            # 기타 오류 처리
            error_msg = f"쿼리 실행 중 오류 발생: {str(e)}"
            print(error_msg)  # 콘솔에 출력
            raise Exception(error_msg)
        finally:
            if conn:
                conn.close()

    @staticmethod
    def execute_query_with_dict(query, params=(), fetch_all=True):
        """열 이름이 있는 딕셔너리 형태로 결과 반환"""
        conn = DatabaseConnector.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(query, params)

            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                if fetch_all:
                    rows = cursor.fetchall()
                    result = [{key: row[key] for key in row.keys()} for row in rows]
                else:
                    row = cursor.fetchone()
                    result = {key: row[key] for key in row.keys()} if row else None

                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return cursor.rowcount
        except Exception as e:
            conn.close()
            raise e

    @staticmethod
    def insert_many(table, columns, values):
        """여러 행 한 번에 삽입"""
        conn = DatabaseConnector.get_connection()
        cursor = conn.cursor()

        placeholders = ', '.join(['?'] * len(columns))
        columns_str = ', '.join(columns)
        query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"

        try:
            cursor.executemany(query, values)
            conn.commit()
            conn.close()
            return cursor.rowcount
        except Exception as e:
            conn.close()
            raise e
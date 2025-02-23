# DatabaseManager 클래스
# modules/database_manager.py
import sqlite3
from sqlite3 import Error
import pandas as pd
from pathlib import Path
import shutil
import tkinter.messagebox as messagebox

class DatabaseManager:
    """데이터베이스 연결 및 관리 클래스"""
    def __init__(self, db_path: str, log_manager):
        self.db_path = Path(db_path).absolute()
        self.log_manager = log_manager
        self.connection = None
        if not self.db_path.exists():
            self.log_manager.log_warning(f"데이터베이스 파일이 없습니다: {self.db_path}")
            messagebox.showwarning("경고", "데이터베이스 파일이 없습니다. 기본 모드로 실행됩니다.")
        else:
            self._validate_database()

    def _validate_database(self):
        """데이터베이스 구조 유효성 검사"""
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lotto_results'")
                if not cursor.fetchone():
                    raise ValueError("lotto_results 테이블이 존재하지 않습니다")
                self.log_manager.log_info(f"데이터베이스 유효성 검사 완료: {self.db_path}")
        except Exception as e:
            self.log_manager.log_error(f"데이터베이스 유효성 검사 실패: {str(e)}")
            raise

    def connect(self):
        """데이터베이스 연결"""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.log_manager.log_info(f"데이터베이스 연결 성공: {self.db_path}")
            return self.connection
        except Error as e:
            self.log_manager.log_error(f"데이터베이스 연결 오류: {str(e)}", exc_info=True)
            raise

    def get_historical_data(self, limit: int = None) -> pd.DataFrame:
        """과거 당첨 데이터를 조회"""
        try:
            base_query = """
                SELECT draw_number, num1, num2, num3, num4, num5, num6, bonus,
                       money1, money2, money3, money4, money5
                FROM lotto_results
            """
            query = (f"{base_query} WHERE draw_number IN (SELECT draw_number FROM lotto_results "
                    f"ORDER BY draw_number DESC LIMIT {limit}) ORDER BY draw_number ASC"
                    if limit and str(limit).isdigit() and int(limit) > 0
                    else f"{base_query} ORDER BY draw_number ASC")

            with self.connect() as conn:
                df = pd.read_sql_query(query, conn)
                self.log_manager.log_info(f"과거 데이터 조회 완료: {len(df)}건")
                return df
        except Exception as e:
            self.log_manager.log_error(f"데이터 조회 실패: {str(e)}", exc_info=True)
            raise

    def backup_database(self):
        """데이터베이스 백업 생성"""
        try:
            backup_path = f"{self.db_path}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy(self.db_path, backup_path)
            self.log_manager.log_info(f"데이터베이스 백업 완료: {backup_path}")
            return backup_path
        except Exception as e:
            self.log_manager.log_error(f"데이터베이스 백업 실패: {str(e)}")
            return None
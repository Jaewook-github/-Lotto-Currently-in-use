import sqlite3
import pandas as pd
import numpy as np
from collections import Counter


# [이전의 상수 정의와 분석 함수들을 여기에 포함]

class LottoAnalysis:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze(self):
        conn = self.get_connection()

        # [이전의 analyze_numbers 함수 내용을 여기에 포함]

        conn.close()
        return freq_dfs, stats_df

    def get_latest_numbers(self, limit=10):
        """최근 당첨번호 조회"""
        conn = self.get_connection()
        query = """
        SELECT draw_number, num1, num2, num3, num4, num5, num6
        FROM lotto_results
        ORDER BY draw_number DESC
        LIMIT ?
        """
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        return df.to_dict('records')

    def get_summary_stats(self):
        """주요 통계 정보 조회"""
        freq_dfs, stats_df = self.analyze()
        return {
            'total_draws': stats_df.iloc[-1]['값'],
            'avg_ac': stats_df[stats_df['분석 항목'] == '평균 AC 값'].iloc[0]['값'],
            'avg_prime': stats_df[stats_df['분석 항목'] == '평균 소수 개수'].iloc[0]['값'],
            'avg_composite': stats_df[stats_df['분석 항목'] == '평균 합성수 개수'].iloc[0]['값']
        }
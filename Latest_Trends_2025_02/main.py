# main.py

from lotto_analyzer import LottoAnalyzer
from lotto_generator import LottoGenerator
import sys
import sqlite3


def print_banner():
    print("\n" + "=" * 60)
    print("  트렌드 분석 기반 로또 번호 생성기 v2.0")
    print("=" * 60)
    print("  - 전체 회차, 최근 100회차, 최근 50회차 패턴 분석 기능")
    print("  - 최신 트렌드 기반 번호 생성 기능")
    print("  - 다양한 패턴별 번호 생성 기능")
    print("=" * 60 + "\n")


def print_menu():
    print("\n기능을 선택해주세요:")
    print("1. 번호 생성")
    print("2. 전체 회차 패턴 분석")
    print("3. 최근 100회차 패턴 분석")
    print("4. 최근 50회차 패턴 분석")
    print("5. 번호 조합 분석")
    print("6. 종료")


def analyze_recent(analyzer, draw_count=100):
    """최근 n회차 분석 결과 출력"""
    print(f"\n=== 최근 {draw_count}회차 패턴 분석 ===")

    # 분석 수행
    freq_dfs, stats_df = analyzer.analyze_recent_draws(draw_count)

    # 주요 통계 출력
    print("\n주요 통계:")
    main_stats = [
        '평균 총합', '평균 표준편차', '평균 간격', '대각선 패턴 출현 비율',
        '평균 AC 값', '평균 소수 개수', '평균 합성수 개수', '연속 번호 패턴 출현 회차 수',
        '무연속 번호 패턴 출현 회차 수'
    ]
    for stat in main_stats:
        idx = stats_df[stats_df['분석 항목'] == stat].index
        if len(idx) > 0:
            print(f"- {stat}: {stats_df.at[idx[0], '값']}")

    # 주요 빈도 분석 결과 출력
    print("\n주요 패턴 빈도:")

    # 홀짝 비율
    print("\n홀짝 비율 분석:")
    print(freq_dfs['odd_even_ratio_freq'].head(3).to_string())

    # 고저 비율
    print("\n고저 비율 분석:")
    print(freq_dfs['high_low_ratio_freq'].head(3).to_string())

    # AC값 분포
    print("\nAC값 분포:")
    print(freq_dfs['ac_freq'].head(3).to_string())

    # 연속번호 패턴
    print("\n연속번호 패턴:")
    print(freq_dfs['consec_freq'].to_string())

    # 대각선 패턴
    print("\n대각선 교차점 개수:")
    print(freq_dfs['diagonal_match_count_freq'].to_string())

    # 색상 개수
    print("\n색상 개수 분포:")
    print(freq_dfs['color_freq'].to_string())

    # 소수 개수
    print("\n소수 개수 분포:")
    print(freq_dfs['prime_freq'].head(3).to_string())

    # 합성수 개수
    print("\n합성수 개수 분포:")
    print(freq_dfs['composite_freq'].head(3).to_string())

    # 모서리 번호 개수
    print("\n모서리 번호 개수 분포:")
    print(freq_dfs['corner_freq'].head(3).to_string())

    print("\n분석이 완료되었습니다.")


def input_numbers():
    """사용자로부터 6개의 번호 입력 받기"""
    while True:
        try:
            input_str = input("6개의 번호를 입력하세요 (공백으로 구분): ")
            numbers = list(map(int, input_str.split()))

            # 숫자 검증
            if len(numbers) != 6:
                print("정확히 6개의 숫자를 입력해주세요.")
                continue

            for num in numbers:
                if num < 1 or num > 45:
                    print("모든 숫자는 1에서 45 사이여야 합니다.")
                    break
            else:
                # 중복 검사
                if len(set(numbers)) != 6:
                    print("중복된 숫자가 있습니다.")
                    continue

                return sorted(numbers)

        except ValueError:
            print("올바른 숫자를 입력해주세요.")


def check_database(db_path):
    """데이터베이스 연결 확인 및 기본 정보 출력"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 회차 수 확인
        cursor.execute("SELECT COUNT(*) FROM lotto_results")
        count = cursor.fetchone()[0]

        # 최신 회차 확인
        cursor.execute("SELECT MAX(draw_number) FROM lotto_results")
        latest = cursor.fetchone()[0]

        conn.close()

        print(f"데이터베이스 연결 성공: 총 {count}회차 데이터 (최신: {latest}회)")
        return True
    except Exception as e:
        print(f"데이터베이스 연결 오류: {e}")
        return False


def main():
    db_path = "lotto.db"  # SQLite DB 파일 경로

    print_banner()

    # 데이터베이스 연결 확인
    if not check_database(db_path):
        print("프로그램을 종료합니다.")
        return

    # 분석기 및 생성기 초기화
    analyzer = LottoAnalyzer(db_path)
    generator = LottoGenerator(db_path)

    while True:
        print_menu()

        choice = input("\n선택 (1-6): ")

        if choice == '1':
            # 번호 생성 - LottoGenerator의 main 메서드 대신 내부에서 직접 구현
            # 게임 수 입력 받기
            while True:
                try:
                    num_games = int(input("생성할 게임 수를 입력하세요 (1-20): "))
                    if 1 <= num_games <= 20:
                        break
                    print("1에서 20 사이의 숫자를 입력해주세요.")
                except ValueError:
                    print("올바른 숫자를 입력해주세요.")

            # 트렌드 점수 사용 여부 선택
            while True:
                use_trend = input("최근 트렌드를 반영한 번호를 생성하시겠습니까? (Y/N): ").upper()
                if use_trend in ['Y', 'N']:
                    use_trend = (use_trend == 'Y')
                    break
                print("Y 또는 N으로 입력해주세요.")

            # 생성 방식 선택
            generation_method = 1  # 기본 생성 방식
            if use_trend:
                print("\n생성 방식을 선택해주세요:")
                print("1. 기본 트렌드 기반 생성")
                print("2. 이전 당첨번호 포함 생성")
                print("3. 홀짝 패턴 기반 생성 (4:2 비율)")
                print("4. 고저 패턴 기반 생성 (4:2 비율)")
                print("5. 대각선 패턴 기반 생성 (2개 이상 교차점)")
                print("6. 모서리 패턴 기반 생성 (3개 모서리)")
                print("7. 핫-콜드 패턴 기반 생성 (3:1 비율)")

                while True:
                    try:
                        generation_method = int(input("\n방식 선택 (1-7): "))
                        if 1 <= generation_method <= 7:
                            break
                        print("1에서 7 사이의 숫자를 입력해주세요.")
                    except ValueError:
                        print("올바른 숫자를 입력해주세요.")

            # 선택한 생성 방식에 따라 번호 생성
            combinations = []

            if generation_method == 1:
                combinations = generator.generate_numbers(num_games, use_trend)
            elif generation_method == 2:
                combinations = generator.generate_numbers_with_previous(num_games, use_trend)
            elif generation_method == 3:
                combinations = generator.generate_numbers_with_pattern(num_games, 'odd_even', '4:2')
            elif generation_method == 4:
                combinations = generator.generate_numbers_with_pattern(num_games, 'high_low', '4:2')
            elif generation_method == 5:
                combinations = generator.generate_numbers_with_pattern(num_games, 'diagonal', '2')
            elif generation_method == 6:
                combinations = generator.generate_numbers_with_pattern(num_games, 'corner', '3')
            elif generation_method == 7:
                combinations = generator.generate_numbers_with_pattern(num_games, 'hot_cold', '3:1')

            # 결과 출력
            if combinations:
                print(f"\n{num_games}개의 로또 번호 조합이 생성되었습니다:")
                if use_trend:
                    for i, (numbers, score) in enumerate(combinations, 1):
                        print(f"[{i}번] {numbers} (트렌드 점수: {score:.2f})")
                else:
                    for i, numbers in enumerate(combinations, 1):
                        print(f"[{i}번] {numbers}")
            else:
                print("\n설정된 기준을 만족하는 번호 조합을 찾지 못했습니다.")


if __name__ == "__main__":
    main()
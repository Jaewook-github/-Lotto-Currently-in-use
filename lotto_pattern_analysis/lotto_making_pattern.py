import sqlite3
import pandas as pd
import numpy as np
from tabulate import tabulate
from collections import Counter

# 상수 정의
CORNER_NUMBERS = {
    '좌측 상단': [1, 2, 8, 9],
    '우측 상단': [6, 7, 13, 14],
    '좌측 하단': [29, 30, 36, 37, 43, 44],
    '우측 하단': [34, 35, 41, 42]
}

BALL_COLORS = {
    '노랑(🟡)': range(1, 10),
    '파랑(🔵)': range(11, 20),
    '빨강(🔴)': range(21, 30),
    '검정(⚫)': range(31, 40),
    '초록(🟢)': range(41, 45)
}

COMPOSITE_NUMBERS = {1, 4, 8, 10, 14, 16, 20, 22, 25, 26, 28, 32, 34, 35, 38, 40, 44}
PERFECT_SQUARES = {1, 4, 9, 16, 25, 36}
PRIME_NUMBERS = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43}

# 동형수 그룹 정의
MIRROR_NUMBER_GROUPS = [
    {12, 21}, {13, 31}, {14, 41},
    {23, 32}, {24, 42}, {34, 43},
    {6, 9}  # 6/9 그룹 포함
]

# 배수 정의
MULTIPLES = {
    '3의 배수': [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45],
    '4의 배수': [4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44],
    '5의 배수': [5, 10, 15, 20, 25, 30, 35, 40, 45]
}


def get_ball_color(number):
    """번호의 색상을 반환하는 함수"""
    for color, number_range in BALL_COLORS.items():
        if number in number_range:
            return color
    return None


def analyze_color_pattern(numbers):
    """당첨번호의 색상 패턴을 분석하는 함수"""
    colors = [get_ball_color(num) for num in numbers]
    color_counts = Counter(colors)
    return color_counts


def count_multiples(numbers, multiple_list):
    """특정 배수의 개수를 세는 함수"""
    return len([num for num in numbers if num in multiple_list])


def count_composite_numbers(numbers):
    """합성수의 개수를 세는 함수"""
    return len([num for num in numbers if num in COMPOSITE_NUMBERS])


def count_perfect_squares(numbers):
    """완전제곱수의 개수를 세는 함수"""
    return len([num for num in numbers if num in PERFECT_SQUARES])


def count_prime_numbers(numbers):
    """소수의 개수를 세는 함수"""
    return len([num for num in numbers if num in PRIME_NUMBERS])


# def calculate_last_digit_sum(numbers):
#     """끝수합을 계산하는 함수"""
#     last_digits = []
#     for num in numbers:
#         # 1~9까지는 끝수가 없으므로 제외
#         if num >= 10:
#             last_digits.append(num % 10)
#     return sum(last_digits)

def calculate_last_digit_sum(numbers):
    """끝수합을 계산하는 함수 """
    last_digits = [num % 10 for num in numbers]
    return sum(last_digits)


def is_palindrome(number):
    """회문수 여부를 확인하는 함수"""
    if number < 10:
        return False
    number_str = str(number)
    return number_str == number_str[::-1]


def count_palindrome_numbers(numbers):
    """회문수의 개수를 세는 함수"""
    return len([num for num in numbers if is_palindrome(num)])


def is_double_number(number):
    """쌍수 여부를 확인하는 함수"""
    if number < 10:
        return False
    number_str = str(number)
    return len(number_str) == 2 and number_str[0] == number_str[1]


def count_double_numbers(numbers):
    """쌍수의 개수를 세는 함수"""
    return len([num for num in numbers if is_double_number(num)])


def get_mirror_number_count(numbers):
    """동형수 그룹의 개수를 세는 함수"""
    mirror_count = 0
    numbers_set = set(numbers)

    for group in MIRROR_NUMBER_GROUPS:
        if any(num in numbers_set for num in group):
            mirror_count += 1

    return mirror_count


def find_consecutive_numbers(numbers):
    """연속된 번호 패턴을 찾는 함수"""
    sorted_nums = sorted(numbers)
    consecutive_groups = []
    current_group = [sorted_nums[0]]

    for i in range(1, len(sorted_nums)):
        if sorted_nums[i] == sorted_nums[i - 1] + 1:
            current_group.append(sorted_nums[i])
        else:
            if len(current_group) >= 2:
                consecutive_groups.append(current_group)
            current_group = [sorted_nums[i]]

    if len(current_group) >= 2:
        consecutive_groups.append(current_group)

    return consecutive_groups


def calculate_ac(numbers):
    """AC(Adjacency Criteria) 값을 계산하는 함수"""
    sorted_numbers = sorted(numbers, reverse=True)
    differences = set()

    for i in range(len(sorted_numbers)):
        for j in range(i + 1, len(sorted_numbers)):
            diff = sorted_numbers[i] - sorted_numbers[j]
            differences.add(diff)

    return len(differences) - 5


def analyze_numbers():
    """로또 번호 종합 분석 함수"""
    conn = sqlite3.connect('../lotto.db')

    query = """
    SELECT draw_number, num1, num2, num3, num4, num5, num6
    FROM lotto_results
    ORDER BY draw_number
    """

    df = pd.read_sql_query(query, conn)

    results = {
        'corner_results': [],
        'ac_results': [],
        'consecutive_patterns': [],
        'color_patterns': [],
        'color_combinations': [],
        'composite_counts': [],
        'perfect_square_counts': [],
        'mirror_number_counts': [],
        'multiples_3_counts': [],
        'multiples_4_counts': [],
        'multiples_5_counts': [],
        'prime_counts': [],
        'last_digit_sums': [],
        'palindrome_counts': [],
        'double_number_counts': []
    }

    for index, row in df.iterrows():
        draw_numbers = [row['num1'], row['num2'], row['num3'],
                        row['num4'], row['num5'], row['num6']]

        # 모서리 번호 분석
        all_corner_numbers = []
        for corner_nums in CORNER_NUMBERS.values():
            all_corner_numbers.extend(corner_nums)
        results['corner_results'].append(
            len(set(draw_numbers).intersection(set(all_corner_numbers))))

        # AC 값 분석
        results['ac_results'].append(calculate_ac(draw_numbers))

        # 연속된 번호 패턴 분석
        consecutive_groups = find_consecutive_numbers(draw_numbers)
        if consecutive_groups:
            for group in consecutive_groups:
                results['consecutive_patterns'].append(len(group))

        # 색상 패턴 분석
        color_count = analyze_color_pattern(draw_numbers)
        results['color_patterns'].append(len(color_count))
        results['color_combinations'].append(
            "-".join(f"{color}:{count}" for color, count in sorted(color_count.items())))

        # 합성수 분석
        results['composite_counts'].append(count_composite_numbers(draw_numbers))

        # 완전제곱수 분석
        results['perfect_square_counts'].append(count_perfect_squares(draw_numbers))

        # 동형수 분석
        results['mirror_number_counts'].append(get_mirror_number_count(draw_numbers))

        # 배수 분석
        results['multiples_3_counts'].append(count_multiples(draw_numbers, MULTIPLES['3의 배수']))
        results['multiples_4_counts'].append(count_multiples(draw_numbers, MULTIPLES['4의 배수']))
        results['multiples_5_counts'].append(count_multiples(draw_numbers, MULTIPLES['5의 배수']))

        # 소수 분석
        results['prime_counts'].append(count_prime_numbers(draw_numbers))

        # 끝수합 분석
        results['last_digit_sums'].append(calculate_last_digit_sum(draw_numbers))

        # 회문수 분석
        results['palindrome_counts'].append(count_palindrome_numbers(draw_numbers))

        # 쌍수 분석
        results['double_number_counts'].append(count_double_numbers(draw_numbers))

    # 빈도 데이터프레임 생성
    freq_dfs = {
        'corner_freq': pd.DataFrame(pd.Series(results['corner_results']).value_counts().sort_index()),
        'ac_freq': pd.DataFrame(pd.Series(results['ac_results']).value_counts().sort_index()),
        'consec_freq': pd.DataFrame(pd.Series(results['consecutive_patterns']).value_counts().sort_index()),
        'color_freq': pd.DataFrame(pd.Series(results['color_patterns']).value_counts().sort_index()),
        'color_comb_freq': pd.DataFrame(pd.Series(results['color_combinations']).value_counts().head(10)),
        'composite_freq': pd.DataFrame(pd.Series(results['composite_counts']).value_counts().sort_index()),
        'perfect_square_freq': pd.DataFrame(pd.Series(results['perfect_square_counts']).value_counts().sort_index()),
        'mirror_number_freq': pd.DataFrame(pd.Series(results['mirror_number_counts']).value_counts().sort_index()),
        'multiples_3_freq': pd.DataFrame(pd.Series(results['multiples_3_counts']).value_counts().sort_index()),
        'multiples_4_freq': pd.DataFrame(pd.Series(results['multiples_4_counts']).value_counts().sort_index()),
        'multiples_5_freq': pd.DataFrame(pd.Series(results['multiples_5_counts']).value_counts().sort_index()),
        'prime_freq': pd.DataFrame(pd.Series(results['prime_counts']).value_counts().sort_index()),
        'last_digit_sum_freq': pd.DataFrame(pd.Series(results['last_digit_sums']).value_counts().sort_index()),
        'palindrome_freq': pd.DataFrame(pd.Series(results['palindrome_counts']).value_counts().sort_index()),
        'double_number_freq': pd.DataFrame(pd.Series(results['double_number_counts']).value_counts().sort_index())
    }

    # 데이터프레임 이름 설정
    names = {
        'corner_freq': '모서리 번호 개수',
        'ac_freq': 'AC 값',
        'consec_freq': '연속 번호 개수',
        'color_freq': '사용된 색상 수',
        'color_comb_freq': '색상 조합 패턴',
        'composite_freq': '합성수 개수',
        'perfect_square_freq': '완전제곱수 개수',
        'mirror_number_freq': '동형수 그룹 개수',
        'multiples_3_freq': '3의 배수 개수',
        'multiples_4_freq': '4의 배수 개수',
        'multiples_5_freq': '5의 배수 개수',
        'prime_freq': '소수 개수',
        'last_digit_sum_freq': '끝수합',
        'palindrome_freq': '회문수 개수',
        'double_number_freq': '쌍수 개수'
    }

    # 각 데이터프레임 형식 설정
    for key, df in freq_dfs.items():
        df.columns = ['출현 횟수']
        df.index.name = names[key]
        df['비율(%)'] = (df['출현 횟수'] / len(df) * 100).round(2)

    # 전체 통계 계산
    total_stats = {
        '분석 항목': [
            '평균 모서리 번호',
            '최대 모서리 번호',
            '최소 모서리 번호',
            '평균 AC 값',
            '최대 AC 값',
            '최소 AC 값',
            '평균 사용 색상 수',
            '평균 합성수 개수',
            '평균 완전제곱수 개수',
            '평균 동형수 그룹 개수',
            '평균 3의 배수 개수',
            '평균 4의 배수 개수',
            '평균 5의 배수 개수',
            '평균 소수 개수',
            '평균 끝수합',
            '최대 끝수합',
            '최소 끝수합',
            '평균 회문수 개수',
            '최대 회문수 개수',
            '평균 쌍수 개수',
            '최대 쌍수 개수',
            '연속 번호 패턴 출현 회차 수',
            '총 분석 회차'
        ],
        '값': [
            round(np.mean(results['corner_results']), 2),
            max(results['corner_results']),
            min(results['corner_results']),
            round(np.mean(results['ac_results']), 2),
            max(results['ac_results']),
            min(results['ac_results']),
            round(np.mean(results['color_patterns']), 2),
            round(np.mean(results['composite_counts']), 2),
            round(np.mean(results['perfect_square_counts']), 2),
            round(np.mean(results['mirror_number_counts']), 2),
            round(np.mean(results['multiples_3_counts']), 2),
            round(np.mean(results['multiples_4_counts']), 2),
            round(np.mean(results['multiples_5_counts']), 2),
            round(np.mean(results['prime_counts']), 2),
            round(np.mean(results['last_digit_sums']), 2),
            max(results['last_digit_sums']),
            min(results['last_digit_sums']),
            round(np.mean(results['palindrome_counts']), 2),
            max(results['palindrome_counts']),
            round(np.mean(results['double_number_counts']), 2),
            max(results['double_number_counts']),
            len([x for x in results['consecutive_patterns'] if x >= 2]),
            len(results['corner_results'])
        ]
    }
    stats_df = pd.DataFrame(total_stats)

    conn.close()
    return freq_dfs, stats_df

def main():
    """메인 실행 함수"""
    freq_dfs, stats_df = analyze_numbers()

    # 테이블 제목 정의
    table_titles = {
        'corner_freq': '모서리 번호 출현 빈도 분석',
        'ac_freq': 'AC 값 빈도 분석',
        'consec_freq': '연속된 번호 패턴 분석',
        'color_freq': '색상 개수 분포 분석',
        'color_comb_freq': '상위 10개 색상 조합 패턴',
        'composite_freq': '합성수 개수 분포 분석',
        'perfect_square_freq': '완전제곱수 개수 분포 분석',
        'mirror_number_freq': '동형수 그룹 개수 분포 분석',
        'multiples_3_freq': '3의 배수 개수 분포 분석',
        'multiples_4_freq': '4의 배수 개수 분포 분석',
        'multiples_5_freq': '5의 배수 개수 분포 분석',
        'prime_freq': '소수 개수 분포 분석',
        'last_digit_sum_freq': '끝수합 분포 분석',
        'palindrome_freq': '회문수 개수 분포 분석',
        'double_number_freq': '쌍수 개수 분포 분석'
    }

    # 결과 출력
    for key, title in table_titles.items():
        print(f"\n=== {title} ===")
        print(tabulate(freq_dfs[key], headers='keys', tablefmt='pretty', showindex=True))

    print("\n=== 전체 통계 ===")
    print(tabulate(stats_df, headers='keys', tablefmt='pretty', showindex=False))

if __name__ == "__main__":
    main()
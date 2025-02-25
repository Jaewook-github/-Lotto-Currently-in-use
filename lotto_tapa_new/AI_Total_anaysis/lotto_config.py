class LottoConfig:
    def __init__(self):
        # 규칙 활성화 상태
        self.rules_enabled = {
            'sum_range': True,  # 1. 총합 구간
            'ac_value': True,  # 2. AC값
            'odd_even': True,  # 3. 홀짝 비율
            'high_low': True,  # 4. 고저 비율
            'prime': True,  # 5. 소수
            'composite': True,  # 6. 합성수
            'last_digit': True,  # 7. 끝수 총합
            'multiples': True,  # 8. 3,5의 배수
            'perfect_square': True,  # 9. 제곱수
            'consecutive': True,  # 10. 연속번호
            'twin': True,  # 11. 쌍수
            'corner': True  # 12. 모서리 패턴
        }

        # 규칙별 설정값
        self.sum_range = (100, 175)
        self.ac_value_min = 7
        self.odd_even_exclude = [(0, 6), (6, 0)]
        self.high_low_exclude = [(0, 6), (6, 0)]
        self.prime_range = (0, 3)
        self.composite_range = (0, 3)
        self.last_digit_sum_range = (15, 35)
        self.multiples_of_3_range = (0, 3)
        self.multiples_of_5_range = (0, 2)
        self.perfect_square_range = (0, 1)
        self.consecutive_numbers = [0, 1, 2]
        self.twin_numbers_range = (0, 2)

        # 모서리 패턴 상세 설정
        self.corner_numbers_range = (1, 4)  # 전체 모서리 숫자 개수
        self.corner_max_per_side = 2  # 한 모서리당 최대 숫자 개수
        self.corner_diagonal_diff = 2  # 대각선 간 최대 차이
        self.games_count = 5 # 게임 개수 설정
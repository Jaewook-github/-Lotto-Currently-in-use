// 차트 설정 및 생성 스크립트 (수정된 버전)
document.addEventListener('DOMContentLoaded', function() {
    // 색상 설정
    const colors = {
        primary: '#4158D0',
        secondary: '#3f51b5',
        accent: '#C850C0',
        yellow: '#ffc107',
        blue: '#2196f3',
        red: '#f44336',
        gray: '#757575',
        green: '#4caf50',
        gradient: ['rgba(65, 88, 208, 0.8)', 'rgba(200, 80, 192, 0.8)', 'rgba(255, 204, 112, 0.8)']
    };

    // 통계 데이터 로드 상태 관리
    let statsLoaded = false;
    let statsLoadAttempts = 0;
    const maxLoadAttempts = 3;

    // 공통 차트 설정
    Chart.defaults.font.family = "'Noto Sans KR', sans-serif";
    Chart.defaults.color = '#666';
    Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';

    // 다크 모드 감지 및 적용
    const isDarkMode = document.body.classList.contains('dark-mode');
    if (isDarkMode) {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    }

    // 그라데이션 생성 헬퍼 함수 (수정됨)
    function createGradient(chart, colorStart, colorEnd) {
        const ctx = chart.ctx;
        const chartArea = chart.chartArea;

        if (!chartArea) {
            return colorStart; // 차트 영역이 없으면 기본 색상 반환
        }

        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
        gradient.addColorStop(0, colorStart);
        gradient.addColorStop(1, colorEnd);
        return gradient;
    }

    // 통계 탭 활성화 감지
    document.addEventListener('tabActivated', function(e) {
        if (e.detail && e.detail.tabId === 'stats' && !statsLoaded) {
            loadStatsData();
        }
    });

    // 메뉴 아이템 클릭 감지
    const menuItems = document.querySelectorAll('.menu-items li');
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            if (tabId === 'stats' && !statsLoaded) {
                setTimeout(loadStatsData, 100);
            }
        });
    });

    // 초기 로드 시 메인 탭의 차트만 로드
    if (document.querySelector('.tab-content#main.active')) {
        loadMainTabCharts();
    }

    // 메인 탭 차트 로드
    function loadMainTabCharts() {
        fetch('/stats')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const stats = data.stats;
                    createNumberFrequencyChart(stats.frequency);
                    createOddEvenChart(stats.odd_even);
                    createNumberDistributionChart(stats.frequency);
                }
            })
            .catch(error => {
                console.error('메인 탭 통계 로드 실패:', error);
                // 샘플 데이터로 대체
                createSampleCharts();
            });
    }

    // 샘플 차트 생성 함수 (API 실패 시 사용)
    function createSampleCharts() {
        const sampleFrequency = {};
        for (let i = 1; i <= 45; i++) {
            sampleFrequency[i] = Math.floor(Math.random() * 20) + 10;
        }

        const sampleOddEven = {
            counts: [5, 15, 45, 35, 30, 10, 5],
            percentages: [3.4, 10.3, 31.0, 24.1, 20.7, 6.9, 3.4],
            labels: ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
        };

        createNumberFrequencyChart(sampleFrequency);
        createOddEvenChart(sampleOddEven);
        createNumberDistributionChart(sampleFrequency);
    }

    // 통계 데이터 로드 함수
    function loadStatsData() {
        if (statsLoaded || statsLoadAttempts >= maxLoadAttempts) return;

        statsLoadAttempts++;

        const statsLoading = document.getElementById('statsLoading');
        const statsError = document.getElementById('statsError');
        const statsContent = document.getElementById('statsContent');

        // 요소가 없으면 중단
        if (!statsLoading || !statsError || !statsContent) {
            console.error('통계 탭 요소를 찾을 수 없습니다.');
            return;
        }

        // 로딩 표시
        statsLoading.style.display = 'block';
        statsError.classList.add('d-none');
        statsContent.classList.add('d-none');

        // 타임아웃 설정
        const statsTimeout = setTimeout(function() {
            statsLoading.style.display = 'none';
            statsError.classList.remove('d-none');
            console.error('통계 데이터 로딩 타임아웃');
        }, 15000);

        // DB에서 통계 데이터 가져오기
        fetch('/stats', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('서버 응답 오류');
            }
            return response.json();
        })
        .then(data => {
            clearTimeout(statsTimeout);

            if (data.success) {
                statsLoaded = true;
                const stats = data.stats;
                statsLoading.style.display = 'none';
                statsContent.classList.remove('d-none');

                setTimeout(() => {
                    initializeStatsCharts(stats);
                    displayRecentDraws(stats.recent_draws);
                    updateStatsSummary(stats);
                }, 100);
            } else {
                throw new Error(data.error || '통계 데이터 로드 실패');
            }
        })
        .catch(error => {
            clearTimeout(statsTimeout);
            statsLoading.style.display = 'none';

            // 오류 시 샘플 데이터로 대체
            console.warn('통계 데이터 로드 실패, 샘플 데이터 사용:', error);
            statsContent.classList.remove('d-none');
            initializeStatsChartsWithSampleData();
        });
    }

    // 샘플 데이터로 통계 차트 초기화
    function initializeStatsChartsWithSampleData() {
        const sampleStats = {
            frequency: {},
            odd_even: {
                counts: [5, 15, 45, 35, 30, 10, 5],
                percentages: [3.4, 10.3, 31.0, 24.1, 20.7, 6.9, 3.4],
                labels: ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0']
            },
            high_low: {
                counts: [8, 18, 40, 38, 25, 12, 4],
                percentages: [5.5, 12.4, 27.6, 26.2, 17.2, 8.3, 2.8],
                labels: ['고0:저6', '고1:저5', '고2:저4', '고3:저3', '고4:저2', '고5:저1', '고6:저0']
            },
            ac_value: {
                counts: [2, 5, 12, 25, 30, 35, 28, 18, 12, 8, 5, 3, 2, 1, 0, 0],
                labels: Array.from({length: 16}, (_, i) => i.toString())
            },
            sum_trend: Array.from({length: 15}, (_, i) => ({
                draw_number: 1100 + i,
                sum: 120 + Math.floor(Math.random() * 40)
            })),
            recent_draws: Array.from({length: 10}, (_, i) => ({
                draw_number: 1110 - i,
                numbers: Array.from({length: 6}, () => Math.floor(Math.random() * 45) + 1).sort((a, b) => a - b),
                bonus: Math.floor(Math.random() * 45) + 1
            }))
        };

        // 샘플 빈도 데이터 생성
        for (let i = 1; i <= 45; i++) {
            sampleStats.frequency[i] = Math.floor(Math.random() * 20) + 10;
        }

        initializeStatsCharts(sampleStats);
        displayRecentDraws(sampleStats.recent_draws);
        updateStatsSummary(sampleStats);
    }

    // 재시도 버튼 이벤트
    const retryStatsBtn = document.getElementById('retryStatsBtn');
    if (retryStatsBtn) {
        retryStatsBtn.addEventListener('click', function() {
            statsLoadAttempts = 0;
            statsLoaded = false;
            loadStatsData();
        });
    }

    // 통계 탭 차트 초기화
    function initializeStatsCharts(stats) {
        try {
            createOddEvenDistChart(stats.odd_even);
            createHighLowDistChart(stats.high_low);
            createAcValueChart(stats.ac_value);
            createSumTrendChart(stats.sum_trend);
            createNumberFrequencyChartFull(stats.frequency);
            createSumRangeHelpChart();
            createOddEvenHelpChart(stats.odd_even);
        } catch (error) {
            console.error('차트 초기화 중 오류:', error);
        }
    }

    // 차트 생성 함수들 (수정된 버전)

    // 미니 번호 출현 빈도 차트
    function createNumberFrequencyChart(frequencyData) {
        const ctx = document.getElementById('numberFrequencyChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        const numbers = Object.keys(frequencyData).map(Number);
        const topNumbers = numbers.sort((a, b) => frequencyData[b] - frequencyData[a]).slice(0, 10);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topNumbers,
                datasets: [{
                    label: '출현 빈도',
                    data: topNumbers.map(num => frequencyData[num]),
                    backgroundColor: function(context) {
                        const value = topNumbers[context.dataIndex];
                        if (value <= 10) return colors.yellow;
                        else if (value <= 20) return colors.blue;
                        else if (value <= 30) return colors.red;
                        else if (value <= 40) return colors.gray;
                        else return colors.green;
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { display: false },
                        ticks: { display: false }
                    },
                    x: { grid: { display: false } }
                }
            }
        });

        // 미니 차트 옆에 표시할 번호 볼 생성
        const numberFreq = document.querySelector('.number-freq');
        if (numberFreq) {
            numberFreq.innerHTML = '';
            topNumbers.slice(0, 5).forEach(num => {
                const ball = document.createElement('div');
                ball.className = 'number-ball mini';
                if (num <= 10) ball.classList.add('ball-yellow');
                else if (num <= 20) ball.classList.add('ball-blue');
                else if (num <= 30) ball.classList.add('ball-red');
                else if (num <= 40) ball.classList.add('ball-gray');
                else ball.classList.add('ball-green');
                ball.textContent = num;
                numberFreq.appendChild(ball);
            });
        }
    }

    // 홀짝 비율 차트
    function createOddEvenChart(oddEvenStats) {
        const ctx = document.getElementById('oddEvenChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        let oddCount = 0;
        let evenCount = 0;

        for (let i = 0; i < oddEvenStats.counts.length; i++) {
            const count = oddEvenStats.counts[i];
            const oddNumCount = i;
            const evenNumCount = 6 - oddNumCount;
            oddCount += oddNumCount * count;
            evenCount += evenNumCount * count;
        }

        const total = oddCount + evenCount;
        const oddPercent = Math.round((oddCount / total) * 100);
        const evenPercent = 100 - oddPercent;

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['홀수', '짝수'],
                datasets: [{
                    data: [oddPercent, evenPercent],
                    backgroundColor: [colors.primary, colors.accent],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { boxWidth: 12, padding: 15 }
                    }
                }
            }
        });
    }

    // 총합 추이 차트 (수정됨)
    function createSumTrendChart(sumTrendData) {
        const ctx = document.getElementById('sumTrendChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        const labels = sumTrendData.map(item => `${item.draw_number}회`);
        const data = sumTrendData.map(item => item.sum);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '총합',
                    data: data,
                    borderColor: colors.primary,
                    backgroundColor: function(context) {
                        const chart = context.chart;
                        if (!chart.chartArea) return colors.primary;
                        return createGradient(chart, 'rgba(65, 88, 208, 0.8)', 'rgba(65, 88, 208, 0)');
                    },
                    borderWidth: 2,
                    pointBackgroundColor: colors.accent,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { min: 90, max: 185, ticks: { stepSize: 15 } }
                }
            }
        });
    }

    // 홀짝 비율 분포 차트 (통계 탭)
    function createOddEvenDistChart(oddEvenStats) {
        const ctx = document.getElementById('oddEvenDistChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: oddEvenStats.labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: oddEvenStats.counts,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                        if (value === 3) return colors.primary;
                        return 'rgba(65, 88, 208, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `홀짝 비율 ${tooltipItems[0].label}`;
                            },
                            label: function(context) {
                                const dataValue = context.parsed.y;
                                const percent = oddEvenStats.percentages[context.dataIndex];
                                return [`당첨 횟수: ${dataValue}회`, `비율: ${percent}%`];
                            }
                        }
                    }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // 고저 비율 분포 차트
    function createHighLowDistChart(highLowStats) {
        const ctx = document.getElementById('highLowDistChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: highLowStats.labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: highLowStats.counts,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                        if (value === 3) return colors.accent;
                        return 'rgba(200, 80, 192, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // AC값 분포 차트
    function createAcValueChart(acValueStats) {
        const ctx = document.getElementById('acValueChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: acValueStats.labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: acValueStats.counts,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        if (value < 6) return 'rgba(220, 53, 69, 0.7)';
                        return colors.green;
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: { y: { beginAtZero: true } }
            }
        });
    }

    // 전체 번호 분포 차트
    function createNumberDistributionChart(frequencyData) {
        const ctx = document.getElementById('numberDistributionChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        const labels = Object.keys(frequencyData).map(Number).sort((a, b) => a - b);
        const data = labels.map(num => frequencyData[num]);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: data,
                    backgroundColor: function(context) {
                        const value = labels[context.dataIndex];
                        if (value <= 10) return colors.yellow;
                        else if (value <= 20) return colors.blue;
                        else if (value <= 30) return colors.red;
                        else if (value <= 40) return colors.gray;
                        else return colors.green;
                    },
                    borderWidth: 0,
                    barPercentage: 0.9,
                    categoryPercentage: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 23,
                            callback: function(val, index) {
                                return index % 5 === 0 ? this.getLabelForValue(val) : '';
                            }
                        }
                    }
                }
            }
        });
    }

    // 전체 번호 빈도 차트 (통계 탭)
    function createNumberFrequencyChartFull(frequencyData) {
        const ctx = document.getElementById('numberFrequencyChartFull');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        const labels = Object.keys(frequencyData).map(Number).sort((a, b) => a - b);
        const data = labels.map(num => frequencyData[num]);
        const avgFrequency = data.reduce((sum, val) => sum + val, 0) / data.length;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: data,
                    backgroundColor: function(context) {
                        const value = labels[context.dataIndex];
                        const dataValue = data[context.dataIndex];
                        let alpha = dataValue > avgFrequency ? 1.0 : 0.7;

                        if (value <= 10) return `rgba(255, 193, 7, ${alpha})`;
                        else if (value <= 20) return `rgba(33, 150, 243, ${alpha})`;
                        else if (value <= 30) return `rgba(244, 67, 54, ${alpha})`;
                        else if (value <= 40) return `rgba(117, 117, 117, ${alpha})`;
                        else return `rgba(76, 175, 80, ${alpha})`;
                    },
                    borderWidth: 0,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: 'rgba(0, 0, 0, 0.05)' }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 도움말 - 총합 구간 차트
    function createSumRangeHelpChart() {
        const ctx = document.getElementById('sumRangeHelpChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        const data = [0, 2, 4, 8, 15, 25, 38, 50, 65, 78, 85, 90, 92, 88, 82, 73, 63, 50, 38, 25, 15, 8, 4, 1, 0];
        const labels = Array.from({length: 25}, (_, i) => (70 + i * 10).toString());

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '출현 빈도',
                    data: data,
                    borderColor: colors.primary,
                    backgroundColor: 'rgba(65, 88, 208, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { display: false, beginAtZero: true },
                    x: {
                        grid: { display: false },
                        ticks: { autoSkip: true, maxTicksLimit: 6 }
                    }
                },
                elements: { point: { radius: 0 } }
            }
        });
    }

    // 도움말 - 홀짝 비율 차트
    function createOddEvenHelpChart(oddEvenStats) {
        const ctx = document.getElementById('oddEvenHelpChart');
        if (!ctx) return;

        const existingChart = Chart.getChart(ctx);
        if (existingChart) existingChart.destroy();

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: oddEvenStats.labels,
                datasets: [{
                    label: '비율별 당첨 확률',
                    data: oddEvenStats.percentages,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                        if (value === 3) return 'rgba(76, 175, 80, 0.7)';
                        return 'rgba(33, 150, 243, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, display: false },
                    x: {
                        grid: { display: false },
                        ticks: { font: { size: 9 } }
                    }
                }
            }
        });
    }

    // 최근 당첨번호 표시
    function displayRecentDraws(recentDraws) {
        const container = document.querySelector('.recent-draws');
        if (!container || !recentDraws) return;

        container.innerHTML = '';

        recentDraws.forEach(draw => {
            const drawRow = document.createElement('div');
            drawRow.className = 'draw-row';

            const drawNumber = document.createElement('div');
            drawNumber.className = 'draw-number';
            drawNumber.textContent = `${draw.draw_number}회`;

            const drawBalls = document.createElement('div');
            drawBalls.className = 'draw-balls';

            draw.numbers.forEach(num => {
                const ball = document.createElement('div');
                ball.className = 'number-ball mini';

                if (num <= 10) ball.classList.add('ball-yellow');
                else if (num <= 20) ball.classList.add('ball-blue');
                else if (num <= 30) ball.classList.add('ball-red');
                else if (num <= 40) ball.classList.add('ball-gray');
                else ball.classList.add('ball-green');

                ball.textContent = num;
                drawBalls.appendChild(ball);
            });

            drawRow.appendChild(drawNumber);
            drawRow.appendChild(drawBalls);
            container.appendChild(drawRow);
        });
    }

    // 통계 요약 정보 업데이트
    function updateStatsSummary(stats) {
        try {
            // 홀짝 비율 평균 계산
            const oddEvenAvg = calculateOddEvenAverage(stats.odd_even);
            const oddEvenElement = document.getElementById('oddEvenRatioAvg');
            if (oddEvenElement) oddEvenElement.textContent = oddEvenAvg;

            // 최다 출현 홀짝 패턴
            const topOddEven = getTopPattern(stats.odd_even);
            const topOddEvenElement = document.getElementById('topOddEvenPattern');
            if (topOddEvenElement) topOddEvenElement.textContent = topOddEven;

            // 고저 비율 평균 계산
            const highLowAvg = calculateHighLowAverage(stats.high_low);
            const highLowElement = document.getElementById('highLowRatioAvg');
            if (highLowElement) highLowElement.textContent = highLowAvg;

            // 최다 출현 고저 패턴
            const topHighLow = getTopPattern(stats.high_low);
            const topHighLowElement = document.getElementById('topHighLowPattern');
            if (topHighLowElement) topHighLowElement.textContent = topHighLow;

            // 연속번호 통계
            const consecutiveElement = document.getElementById('consecutiveStats');
            if (consecutiveElement && stats.consecutive_pairs) {
                const topConsecutive = getTopConsecutivePattern(stats.consecutive_pairs);
                consecutiveElement.textContent = topConsecutive;
            }

            // 평균 AC값
            const avgAcElement = document.getElementById('avgAcValue');
            if (avgAcElement) {
                const avgAc = calculateAverageAC(stats.ac_value);
                avgAcElement.textContent = avgAc;
            }

            // 번호별 순위
            updateNumberRankings(stats.frequency);

            // 최신 회차 정보
            const latestDrawElement = document.getElementById('latestDrawNumber');
            const latestDateElement = document.getElementById('latestDrawDate');
            if (latestDrawElement) latestDrawElement.textContent = stats.latest_draw;
            if (latestDateElement) latestDateElement.textContent = new Date().toLocaleDateString('ko-KR');
        } catch (error) {
            console.error('통계 요약 업데이트 중 오류:', error);
        }
    }

    // 헬퍼 함수들
    function calculateOddEvenAverage(oddEvenStats) {
        let totalOdd = 0;
        let totalCount = 0;

        for (let i = 0; i < oddEvenStats.counts.length; i++) {
            totalOdd += i * oddEvenStats.counts[i];
            totalCount += oddEvenStats.counts[i];
        }

        const avgOdd = (totalOdd / totalCount).toFixed(1);
        const avgEven = (6 - avgOdd).toFixed(1);
        return `홀수 ${avgOdd}개, 짝수 ${avgEven}개`;
    }

    function calculateHighLowAverage(highLowStats) {
        let totalHigh = 0;
        let totalCount = 0;

        for (let i = 0; i < highLowStats.counts.length; i++) {
            totalHigh += i * highLowStats.counts[i];
            totalCount += highLowStats.counts[i];
        }

        const avgHigh = (totalHigh / totalCount).toFixed(1);
        const avgLow = (6 - avgHigh).toFixed(1);
        return `고 ${avgHigh}개, 저 ${avgLow}개`;
    }

    function getTopPattern(stats) {
        const maxIndex = stats.counts.indexOf(Math.max(...stats.counts));
        return stats.labels[maxIndex] + ` (${stats.percentages[maxIndex]}%)`;
    }

    function getTopConsecutivePattern(consecutiveStats) {
        const maxIndex = consecutiveStats.counts.indexOf(Math.max(...consecutiveStats.counts));
        return consecutiveStats.labels[maxIndex] + ` (${consecutiveStats.percentages[maxIndex]}%)`;
    }

    function calculateAverageAC(acStats) {
        let totalAC = 0;
        let totalCount = 0;

        for (let i = 0; i < acStats.counts.length; i++) {
            totalAC += i * acStats.counts[i];
            totalCount += acStats.counts[i];
        }

        return (totalAC / totalCount).toFixed(1);
    }

    function updateNumberRankings(frequency) {
        const numberArray = Object.entries(frequency).map(([num, freq]) => ({
            number: parseInt(num),
            frequency: freq
        }));

        numberArray.sort((a, b) => b.frequency - a.frequency);

        const mostFrequent = document.getElementById('mostFrequentNumbers');
        if (mostFrequent) {
            mostFrequent.innerHTML = '';
            numberArray.slice(0, 5).forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="number-ball mini ball-${getColorClass(item.number)}">${item.number}</span> ${item.frequency}회`;
                mostFrequent.appendChild(li);
            });
        }

        const leastFrequent = document.getElementById('leastFrequentNumbers');
        if (leastFrequent) {
            leastFrequent.innerHTML = '';
            numberArray.slice(-5).reverse().forEach(item => {
                const li = document.createElement('li');
                li.innerHTML = `<span class="number-ball mini ball-${getColorClass(item.number)}">${item.number}</span> ${item.frequency}회`;
                leastFrequent.appendChild(li);
            });
        }
    }

    function getColorClass(num) {
        if (num <= 10) return 'yellow';
        else if (num <= 20) return 'blue';
        else if (num <= 30) return 'red';
        else if (num <= 40) return 'gray';
        else return 'green';
    }
});
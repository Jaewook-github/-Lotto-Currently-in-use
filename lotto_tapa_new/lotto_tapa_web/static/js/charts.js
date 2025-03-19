// 차트 설정 및 생성 스크립트
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

    // 로딩 표시
    const statsLoading = document.getElementById('statsLoading');
    const statsError = document.getElementById('statsError');
    const statsContent = document.getElementById('statsContent');

    // 타임아웃 설정
    let statsTimeout = setTimeout(function() {
        statsLoading.style.display = 'none';
        statsError.classList.remove('d-none');
        console.error('통계 데이터 로딩 타임아웃');
    }, 10000); // 10초 타임아웃

    // DB에서 통계 데이터 가져오기
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            // 타임아웃 취소
            clearTimeout(statsTimeout);

            if (data.success) {
                const stats = data.stats;
                statsLoading.style.display = 'none';
                statsContent.classList.remove('d-none');
                initializeCharts(stats);
                displayRecentDraws(stats.recent_draws);
            } else {
                statsLoading.style.display = 'none';
                statsError.classList.remove('d-none');
                console.error('통계 데이터를 불러오지 못했습니다:', data.error);
            }
        })
        .catch(error => {
            // 타임아웃 취소
            clearTimeout(statsTimeout);

            statsLoading.style.display = 'none';
            statsError.classList.remove('d-none');
            console.error('통계 데이터 요청 중 오류 발생:', error);
        });

    // 재시도 버튼 이벤트
    const retryStatsBtn = document.getElementById('retryStatsBtn');
    if (retryStatsBtn) {
        retryStatsBtn.addEventListener('click', function() {
            location.reload();
        });
    }

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

    // DB에서 통계 데이터 가져오기
    fetch('/stats')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const stats = data.stats;
                initializeCharts(stats);
                displayRecentDraws(stats.recent_draws);
            } else {
                console.error('통계 데이터를 불러오지 못했습니다:', data.error);
            }
        })
        .catch(error => {
            console.error('통계 데이터 요청 중 오류 발생:', error);
        });

    // 모든 차트 초기화
    function initializeCharts(stats) {
        createNumberFrequencyChart(stats.frequency);
        createOddEvenChart(stats.odd_even);
        createNumberDistributionChart(stats.frequency);
        createOddEvenDistChart(stats.odd_even);
        createHighLowDistChart(stats.high_low);
        createAcValueChart(stats.ac_value);
        createSumTrendChart(stats.sum_trend);

        // 도움말 탭의 차트들
        createSumRangeHelpChart();
        createOddEvenHelpChart(stats.odd_even);

        // 전체 번호 빈도 차트 (통계 탭)
        createNumberFrequencyChartFull(stats.frequency);
    }

    // 최근 당첨번호 표시
    function displayRecentDraws(recentDraws) {
        const container = document.querySelector('.recent-draws');
        if (!container) return;

        container.innerHTML = '';

        recentDraws.forEach(draw => {
            const drawRow = document.createElement('div');
            drawRow.className = 'draw-row';

            const drawNumber = document.createElement('div');
            drawNumber.className = 'draw-number';
            drawNumber.textContent = `${draw.draw_number}회`;

            const drawBalls = document.createElement('div');
            drawBalls.className = 'draw-balls';

            // 정렬된 당첨번호 볼 생성
            draw.numbers.forEach(num => {
                const ball = document.createElement('div');
                ball.className = 'number-ball';

                // 번호에 따른 색상 지정
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

    // 미니 번호 출현 빈도 차트
    function createNumberFrequencyChart(frequencyData) {
        const ctx = document.getElementById('numberFrequencyChart');
        if (!ctx) return;

        // 출현 빈도가 높은 상위 10개 번호 추출
        const numbers = Object.keys(frequencyData).map(Number);
        const topNumbers = numbers.sort((a, b) => frequencyData[b] - frequencyData[a]).slice(0, 10);

        const data = {
            labels: topNumbers,
            datasets: [{
                label: '출현 빈도',
                data: topNumbers.map(num => frequencyData[num]),
                backgroundColor: function(context) {
                    const index = context.dataIndex;
                    const value = topNumbers[index];

                    if (value <= 10) return colors.yellow;
                    else if (value <= 20) return colors.blue;
                    else if (value <= 30) return colors.red;
                    else if (value <= 40) return colors.gray;
                    else return colors.green;
                },
                borderRadius: 4
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `번호 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });

        // 미니 차트 옆에 표시할 번호 볼 생성
        const numberFreq = document.querySelector('.number-freq');
        if (numberFreq) {
            numberFreq.innerHTML = '';

            // 상위 5개 번호만 표시
            topNumbers.slice(0, 5).forEach(num => {
                const ball = document.createElement('div');
                ball.className = 'number-ball';

                // 번호에 따른 색상 지정
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

        // 전체 홀수/짝수 비율 계산
        let oddCount = 0;
        let evenCount = 0;

        for (let i = 0; i < oddEvenStats.counts.length; i++) {
            const count = oddEvenStats.counts[i];
            const oddNumCount = i; // 0 홀수부터 6 홀수까지
            const evenNumCount = 6 - oddNumCount;

            oddCount += oddNumCount * count;
            evenCount += evenNumCount * count;
        }

        // 비율 계산 (퍼센트)
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
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    // 전체 번호 분포 차트
    function createNumberDistributionChart(frequencyData) {
        const ctx = document.getElementById('numberDistributionChart');
        if (!ctx) return;

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
                        const index = context.dataIndex;
                        const value = labels[index];

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
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `번호 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
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

        const labels = Object.keys(frequencyData).map(Number).sort((a, b) => a - b);
        const data = labels.map(num => frequencyData[num]);

        // 평균 빈도 계산
        const avgFrequency = data.reduce((sum, val) => sum + val, 0) / data.length;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: data,
                    backgroundColor: function(context) {
                        const index = context.dataIndex;
                        const value = labels[index];
                        const dataValue = data[index];

                        // 평균보다 높은 빈도의 번호는 더 짙은 색상
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
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `번호 ${tooltipItems[0].label}`;
                            },
                            label: function(context) {
                                const dataValue = context.parsed.y;
                                const avg = avgFrequency.toFixed(1);
                                const diff = (dataValue - avgFrequency).toFixed(1);
                                const sign = diff >= 0 ? '+' : '';

                                return [
                                    `당첨 횟수: ${dataValue}회`,
                                    `평균과의 차이: ${sign}${diff}회 (평균: ${avg}회)`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // 홀짝 비율 분포 차트 (통계 탭)
    function createOddEvenDistChart(oddEvenStats) {
        const ctx = document.getElementById('oddEvenDistChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: oddEvenStats.labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: oddEvenStats.counts,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                        gradient.addColorStop(0, colors.gradient[0]);
                        gradient.addColorStop(0.5, colors.gradient[1]);
                        gradient.addColorStop(1, colors.gradient[2]);

                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)'; // 제외 비율
                        if (value === 3) return gradient; // 가장 빈번한 비율
                        return 'rgba(65, 88, 208, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `홀짝 비율 ${tooltipItems[0].label}`;
                            },
                            label: function(context) {
                                const dataValue = context.parsed.y;
                                const percent = oddEvenStats.percentages[context.dataIndex];

                                return [
                                    `당첨 횟수: ${dataValue}회`,
                                    `비율: ${percent}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 고저 비율 분포 차트
    function createHighLowDistChart(highLowStats) {
        const ctx = document.getElementById('highLowDistChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: highLowStats.labels,
                datasets: [{
                    label: '당첨 횟수',
                    data: highLowStats.counts,
                    backgroundColor: function(context) {
                        const value = context.dataIndex;
                        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                        gradient.addColorStop(0, 'rgba(200, 80, 192, 0.7)');
                        gradient.addColorStop(1, 'rgba(65, 88, 208, 0.7)');

                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                        if (value === 3) return gradient;
                        return 'rgba(200, 80, 192, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `고저 비율 ${tooltipItems[0].label}`;
                            },
                            label: function(context) {
                                const dataValue = context.parsed.y;
                                const percent = highLowStats.percentages[context.dataIndex];

                                return [
                                    `당첨 횟수: ${dataValue}회`,
                                    `비율: ${percent}%`
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // AC값 분포 차트
    function createAcValueChart(acValueStats) {
        const ctx = document.getElementById('acValueChart');
        if (!ctx) return;

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

                        const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                        gradient.addColorStop(0, 'rgba(76, 175, 80, 0.7)');
                        gradient.addColorStop(1, 'rgba(33, 150, 243, 0.7)');
                        return gradient;
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `AC값 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 총합 추이 차트
    function createSumTrendChart(sumTrendData) {
        const ctx = document.getElementById('sumTrendChart');
        if (!ctx) return;

        // 최근 15회 당첨번호 총합
        const labels = sumTrendData.map(item => `${item.draw_number}회`);
        const data = sumTrendData.map(item => item.sum);

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(65, 88, 208, 0.8)');
        gradient.addColorStop(1, 'rgba(65, 88, 208, 0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '총합',
                    data: data,
                    borderColor: colors.primary,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointBackgroundColor: colors.accent,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                yMin: 100,
                                yMax: 100,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            },
                            line2: {
                                type: 'line',
                                yMin: 175,
                                yMax: 175,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        min: 90,
                        max: 185,
                        ticks: {
                            stepSize: 15
                        }
                    }
                }
            }
        });
    }

    // 도움말 - 총합 구간 차트
    function createSumRangeHelpChart() {
        const ctx = document.getElementById('sumRangeHelpChart');
        if (!ctx) return;

        // 총합 분포 곡선 (샘플 데이터)
        const data = [0, 2, 4, 8, 15, 25, 38, 50, 65, 78, 85, 90, 92, 88, 82, 73, 63, 50, 38, 25, 15, 8, 4, 1, 0];
        const labels = Array.from({length: 25}, (_, i) => (70 + i * 10).toString());

        const gradient = ctx.createLinearGradient(0, 0, 0, 150);
        gradient.addColorStop(0, 'rgba(65, 88, 208, 0.8)');
        gradient.addColorStop(1, 'rgba(65, 88, 208, 0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '출현 빈도',
                    data: data,
                    borderColor: colors.primary,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        display: false,
                        beginAtZero: true
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 6
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    }
                }
            }
        });
    }

    // 도움말 - 홀짝 비율 차트
    function createOddEvenHelpChart(oddEvenStats) {
        const ctx = document.getElementById('oddEvenHelpChart');
        if (!ctx) return;

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
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        display: false
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 9
                            }
                        }
                    }
                }
            }
        });
    }
});
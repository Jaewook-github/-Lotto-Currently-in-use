/**
 * pattern-charts.js - 로또 번호 패턴 분석 차트 모듈
 * 소수 패턴, 끝수 패턴, 구간별 패턴 등 다양한 패턴 시각화
 */

/**
 * 패턴 차트 생성 클래스
 */
class PatternCharts {
    /**
     * 생성자
     * @param {Object} options - 차트 옵션
     */
    constructor(options = {}) {
        this.charts = {};
        this.options = Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            showLegend: true
        }, options);
    }

    /**
     * 소수 분포 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} patternData - 패턴 데이터 {prime_numbers, prime_distribution, ...}
     */
    createPrimeChart(canvasId, patternData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const primeDistribution = patternData.prime_distribution || {};
        const labels = Object.keys(primeDistribution).map(count => `소수 ${count}개`);
        const data = Object.values(primeDistribution);

        // 총 회차 수 계산
        const totalCount = data.reduce((a, b) => a + b, 0);

        // 백분율 계산
        const percentages = data.map(count => (count / totalCount * 100).toFixed(1));

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: percentages,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(199, 199, 199, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                plugins: {
                    legend: {
                        display: this.options.showLegend,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const count = data[context.dataIndex] || 0;
                                return `${label}: ${value}% (${count}회)`;
                            },
                            footer: (tooltipItems) => {
                                return `* 소수: ${patternData.prime_numbers.join(', ')}`;
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 3의 배수 분포 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} patternData - 패턴 데이터 {mult_3_distribution, ...}
     */
    createMult3Chart(canvasId, patternData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const mult3Distribution = patternData.mult_3_distribution || {};
        const labels = Object.keys(mult3Distribution).map(count => `3의 배수 ${count}개`);
        const data = Object.values(mult3Distribution);

        // 총 회차 수 계산
        const totalCount = data.reduce((a, b) => a + b, 0);

        // 백분율 계산
        const percentages = data.map(count => (count / totalCount * 100).toFixed(1));

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: percentages,
                    backgroundColor: [
                        'rgba(255, 159, 64, 0.7)',
                        'rgba(255, 206, 86, 0.7)',
                        'rgba(75, 192, 192, 0.7)',
                        'rgba(54, 162, 235, 0.7)',
                        'rgba(153, 102, 255, 0.7)',
                        'rgba(255, 99, 132, 0.7)',
                        'rgba(199, 199, 199, 0.7)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                plugins: {
                    legend: {
                        display: this.options.showLegend,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const count = data[context.dataIndex] || 0;
                                return `${label}: ${value}% (${count}회)`;
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 끝수(일의 자리) 분포 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} lastDigitData - 끝수 데이터 {digit_distribution, sum_avg, sum_distribution, ...}
     */
    createLastDigitChart(canvasId, lastDigitData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const digitDistribution = lastDigitData.digit_distribution || {};
        const labels = Object.keys(digitDistribution).map(digit => `끝수 ${digit}`);
        const data = Object.values(digitDistribution);

        // 총 개수 계산
        const totalCount = data.reduce((a, b) => a + b, 0);

        // 이상적인 분포 (모두 동일한 빈도)
        const idealCount = totalCount / 10;
        const idealData = Array(10).fill(idealCount);

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: '실제 빈도',
                        data: data,
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        borderWidth: 1,
                        borderRadius: 4
                    },
                    {
                        label: '이상적 분포',
                        data: idealData,
                        type: 'line',
                        borderColor: 'rgba(255, 99, 132, 0.7)',
                        borderWidth: 2,
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                plugins: {
                    legend: {
                        display: this.options.showLegend
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.y || 0;
                                if (context.datasetIndex === 0) {
                                    const percent = ((value / totalCount) * 100).toFixed(1);
                                    return `${label}: ${value} (${percent}%)`;
                                }
                                return `${label}: ${value.toFixed(1)}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '빈도수'
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 끝수 합계 분포 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} lastDigitData - 끝수 데이터 {digit_distribution, sum_avg, sum_distribution, ...}
     */
    createLastDigitSumChart(canvasId, lastDigitData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const sumDistribution = lastDigitData.sum_distribution || {};
        const labels = Object.keys(sumDistribution);
        const data = Object.values(sumDistribution);

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '빈도수',
                    data: data,
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 2,
                    fill: 'origin',
                    tension: 0.4,
                    pointRadius: 3,
                    pointBackgroundColor: 'rgba(153, 102, 255, 1)'
                }]
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                plugins: {
                    legend: {
                        display: this.options.showLegend
                    },
                    annotation: {
                        annotations: {
                            avgLine: {
                                type: 'line',
                                yMin: lastDigitData.sum_avg,
                                yMax: lastDigitData.sum_avg,
                                borderColor: 'rgba(255, 99, 132, 0.7)',
                                borderWidth: 2,
                                borderDash: [5, 5],
                                label: {
                                    content: `평균: ${lastDigitData.sum_avg.toFixed(1)}`,
                                    display: true,
                                    position: 'end'
                                }
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '빈도수'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: '끝수의 합계 범위'
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 번호대별 조합 패턴 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} combinationsData - 조합 데이터 {top_patterns, pattern_labels}
     */
    createCombinationChart(canvasId, combinationsData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const topPatterns = combinationsData.top_patterns || [];
        const patternLabels = combinationsData.pattern_labels || [];

        // 패턴 레이블 생성
        const labels = topPatterns.map(pattern => {
            const patternStr = pattern.pattern.split('').join('-');
            return `${patternStr} (${pattern.percentage}%)`;
        });

        // 데이터셋 생성
        const datasets = [];
        const colors = [
            'rgba(255, 193, 7, 0.7)', // 노랑 (1-10)
            'rgba(33, 150, 243, 0.7)', // 파랑 (11-20)
            'rgba(244, 67, 54, 0.7)',  // 빨강 (21-30)
            'rgba(117, 117, 117, 0.7)', // 회색 (31-40)
            'rgba(76, 175, 80, 0.7)'   // 초록 (41-45)
        ];

        // 각 구간별 데이터셋 생성
        for (let i = 0; i < patternLabels.length; i++) {
            const data = topPatterns.map(pattern => parseInt(pattern.pattern[i]));

            datasets.push({
                label: patternLabels[i],
                data: data,
                backgroundColor: colors[i],
                stack: 'Stack 0'
            });
        }

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                plugins: {
                    legend: {
                        display: this.options.showLegend,
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            title: (tooltipItems) => {
                                const index = tooltipItems[0].dataIndex;
                                const pattern = topPatterns[index];
                                return `패턴: ${pattern.pattern} (${pattern.count}회)`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        stacked: true,
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        max: 6,
                        title: {
                            display: true,
                            text: '번호 개수'
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 연속된 번호 쌍 차트 생성
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} consecutiveData - 연속 번호 데이터 {counts, percentages, labels}
     */
    createConsecutiveChart(canvasId, consecutiveData) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        // 데이터 변환
        const labels = consecutiveData.labels || [];
        const data = consecutiveData.percentages || [];

        // 차트 생성
        this.charts[canvasId] = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: '발생 확률',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    pointBackgroundColor: 'rgba(54, 162, 235, 1)',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: this.options.responsive,
                maintainAspectRatio: this.options.maintainAspectRatio,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: Math.ceil(Math.max(...data) / 10) * 10,
                        ticks: {
                            stepSize: 10
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: this.options.showLegend
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.dataset.label || '';
                                const value = context.parsed.r || 0;
                                const count = consecutiveData.counts[context.dataIndex] || 0;
                                return `${label}: ${value}% (${count}회)`;
                            }
                        }
                    }
                }
            }
        });

        return this.charts[canvasId];
    }

    /**
     * 차트 데이터 업데이트
     * @param {string} canvasId - 차트 캔버스 ID
     * @param {Object} data - 업데이트할 데이터
     * @param {string} chartType - 차트 유형 ('prime', 'mult3', 'lastDigit', 'lastDigitSum', 'combination', 'consecutive')
     */
    updateChart(canvasId, data, chartType) {
        // 차트가 없으면 새로 생성
        if (!this.charts[canvasId]) {
            switch (chartType) {
                case 'prime':
                    return this.createPrimeChart(canvasId, data);
                case 'mult3':
                    return this.createMult3Chart(canvasId, data);
                case 'lastDigit':
                    return this.createLastDigitChart(canvasId, data);
                case 'lastDigitSum':
                    return this.createLastDigitSumChart(canvasId, data);
                case 'combination':
                    return this.createCombinationChart(canvasId, data);
                case 'consecutive':
                    return this.createConsecutiveChart(canvasId, data);
                default:
                    console.error(`알 수 없는 차트 유형: ${chartType}`);
                    return null;
            }
        }

        // 차트 유형에 따라 업데이트 방법 다르게 적용
        const chart = this.charts[canvasId];

        switch (chartType) {
            case 'prime':
                // 소수 분포 차트 업데이트
                const primeDistribution = data.prime_distribution || {};
                const primeLabels = Object.keys(primeDistribution).map(count => `소수 ${count}개`);
                const primeData = Object.values(primeDistribution);
                const primeTotalCount = primeData.reduce((a, b) => a + b, 0);
                const primePercentages = primeData.map(count => (count / primeTotalCount * 100).toFixed(1));

                chart.data.labels = primeLabels;
                chart.data.datasets[0].data = primePercentages;
                break;

            case 'mult3':
                // 3의 배수 분포 차트 업데이트
                const mult3Distribution = data.mult_3_distribution || {};
                const mult3Labels = Object.keys(mult3Distribution).map(count => `3의 배수 ${count}개`);
                const mult3Data = Object.values(mult3Distribution);
                const mult3TotalCount = mult3Data.reduce((a, b) => a + b, 0);
                const mult3Percentages = mult3Data.map(count => (count / mult3TotalCount * 100).toFixed(1));

                chart.data.labels = mult3Labels;
                chart.data.datasets[0].data = mult3Percentages;
                break;

            case 'lastDigit':
                // 끝수 분포 차트 업데이트
                const digitDistribution = data.digit_distribution || {};
                const digitLabels = Object.keys(digitDistribution).map(digit => `끝수 ${digit}`);
                const digitData = Object.values(digitDistribution);
                const totalCount = digitData.reduce((a, b) => a + b, 0);
                const idealCount = totalCount / 10;
                const idealData = Array(10).fill(idealCount);

                chart.data.labels = digitLabels;
                chart.data.datasets[0].data = digitData;
                chart.data.datasets[1].data = idealData;
                break;

            case 'lastDigitSum':
                // 끝수 합계 분포 차트 업데이트
                const sumDistribution = data.sum_distribution || {};
                const sumLabels = Object.keys(sumDistribution);
                const sumData = Object.values(sumDistribution);

                chart.data.labels = sumLabels;
                chart.data.datasets[0].data = sumData;

                // 평균선 업데이트
                if (chart.options.plugins.annotation?.annotations?.avgLine) {
                    chart.options.plugins.annotation.annotations.avgLine.yMin = data.sum_avg;
                    chart.options.plugins.annotation.annotations.avgLine.yMax = data.sum_avg;
                    chart.options.plugins.annotation.annotations.avgLine.label.content = `평균: ${data.sum_avg.toFixed(1)}`;
                }
                break;

            case 'combination':
                // 조합 패턴 차트 업데이트 (복잡한 구조로 새로 생성이 빠를 수 있음)
                this.charts[canvasId].destroy();
                this.createCombinationChart(canvasId, data);
                return;

            case 'consecutive':
                // 연속 번호 차트 업데이트
                const consecutiveLabels = data.labels || [];
                const consecutiveData = data.percentages || [];

                chart.data.labels = consecutiveLabels;
                chart.data.datasets[0].data = consecutiveData;

                // 레이더 차트 최대값 업데이트
                chart.options.scales.r.max = Math.ceil(Math.max(...consecutiveData) / 10) * 10;
                break;

            default:
                console.error(`알 수 없는 차트 유형: ${chartType}`);
                return;
        }

        // 차트 다시 그리기
        chart.update();
    }
}

// 전역 객체에 등록
window.PatternCharts = PatternCharts;
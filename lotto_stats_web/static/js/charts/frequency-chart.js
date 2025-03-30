/**
 * frequency-chart.js - 번호 빈도 차트 모듈
 */

/**
 * 번호 빈도 차트 생성 클래스
 */
class FrequencyChart {
    /**
     * 생성자
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} options - 차트 옵션
     */
    constructor(canvasId, options = {}) {
        this.canvasId = canvasId;
        this.chart = null;
        this.options = Object.assign({
            showLegend: false,
            responsive: true,
            maintainAspectRatio: false,
            barBorderRadius: 4,
            highlightAverage: true,
            showLabels: true,
            maxTicksLimit: 23
        }, options);
    }

    /**
     * 차트 생성
     * @param {Object} frequencyData - 빈도 데이터 객체 {번호: 빈도수}
     */
    createChart(frequencyData) {
        const ctx = document.getElementById(this.canvasId).getContext('2d');
        if (!ctx) {
            console.error(`캔버스 ID '${this.canvasId}'를 찾을 수 없습니다.`);
            return;
        }

        // 기존 차트 파괴
        if (this.chart) {
            this.chart.destroy();
        }

        // 데이터 변환
        const labels = Object.keys(frequencyData).map(Number).sort((a, b) => a - b);
        const data = labels.map(num => frequencyData[num]);

        // 평균 계산
        const avgFrequency = data.reduce((sum, val) => sum + val, 0) / data.length;

        // 차트 생성
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '출현 횟수',
                    data: data,
                    backgroundColor: (context) => {
                        const index = context.dataIndex;
                        const value = labels[index];
                        const dataValue = data[index];

                        // 평균보다 높은 빈도의 번호는 더 짙은 색상
                        let alpha = this.options.highlightAverage && dataValue > avgFrequency ? 1.0 : 0.7;

                        // 번호 구간별 색상
                        if (value <= 10) return `rgba(255, 193, 7, ${alpha})`;  // 노랑
                        if (value <= 20) return `rgba(33, 150, 243, ${alpha})`;  // 파랑
                        if (value <= 30) return `rgba(244, 67, 54, ${alpha})`;  // 빨강
                        if (value <= 40) return `rgba(117, 117, 117, ${alpha})`;  // 회색
                        return `rgba(76, 175, 80, ${alpha})`;  // 초록
                    },
                    borderWidth: 1,
                    borderRadius: this.options.barBorderRadius
                }]
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
                            title: (tooltipItems) => {
                                return `번호 ${tooltipItems[0].label}`;
                            },
                            label: (context) => {
                                const dataValue = context.parsed.y;
                                const avg = avgFrequency.toFixed(1);
                                const diff = (dataValue - avgFrequency).toFixed(1);
                                const sign = diff >= 0 ? '+' : '';

                                return [
                                    `${dataValue}회 출현`,
                                    `평균 대비: ${sign}${diff}회 (평균: ${avg}회)`
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
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: this.options.maxTicksLimit,
                            display: this.options.showLabels,
                            callback: function(val, index) {
                                // x축 레이블 간소화 (5의 배수만 표시)
                                const value = this.getLabelForValue(val);
                                return index % 5 === 0 ? value : '';
                            }
                        }
                    }
                }
            }
        });

        return this.chart;
    }

    /**
     * 차트 데이터 업데이트
     * @param {Object} frequencyData - 빈도 데이터 객체
     */
    updateData(frequencyData) {
        if (!this.chart) {
            this.createChart(frequencyData);
            return;
        }

        // 데이터 변환
        const labels = Object.keys(frequencyData).map(Number).sort((a, b) => a - b);
        const data = labels.map(num => frequencyData[num]);

        // 차트 데이터 업데이트
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;

        // 차트 다시 그리기
        this.chart.update();
    }

    /**
     * 상위 N개 번호 추출
     * @param {Object} frequencyData - 빈도 데이터 객체
     * @param {number} count - 추출할 개수 (기본값: 5)
     * @returns {Array} 상위 N개 번호 배열 [{number, count}]
     */
    getTopNumbers(frequencyData, count = 5) {
        const numbers = Object.keys(frequencyData).map(Number);

        // 빈도수 기준 내림차순 정렬
        return numbers
            .sort((a, b) => frequencyData[b] - frequencyData[a])
            .slice(0, count)
            .map(num => ({ number: num, count: frequencyData[num] }));
    }

    /**
     * 상위 N개 번호 HTML 생성
     * @param {Object} frequencyData - 빈도 데이터 객체
     * @param {string} containerId - 표시할 컨테이너 ID
     * @param {number} count - 표시할 개수
     */
    renderTopNumbers(frequencyData, containerId, count = 5) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 상위 번호 추출
        const topNumbers = this.getTopNumbers(frequencyData, count);

        // HTML 생성
        container.innerHTML = '';
        topNumbers.forEach(item => {
            const ball = document.createElement('div');
            ball.className = `ball ${formatUtils.getBallColorClass(item.number)}`;
            ball.textContent = item.number;

            // 툴팁 추가
            ball.setAttribute('data-bs-toggle', 'tooltip');
            ball.setAttribute('data-bs-title', `${item.number}번: ${item.count}회 출현`);

            container.appendChild(ball);
        });

        // 툴팁 초기화
        const tooltips = [].slice.call(container.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltips.map(tooltip => new bootstrap.Tooltip(tooltip));
    }
}

// 전역 객체에 등록
window.FrequencyChart = FrequencyChart;
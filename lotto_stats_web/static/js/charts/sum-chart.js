/**
 * sum-chart.js - 로또 번호 합계 차트 모듈
 */

/**
 * 번호 합계 차트 생성 클래스
 */
class SumChart {
    /**
     * 생성자
     * @param {string} canvasId - 차트를 그릴 캔버스 ID
     * @param {Object} options - 차트 옵션
     */
    constructor(canvasId, options = {}) {
        this.canvasId = canvasId;
        this.chart = null;
        this.options = Object.assign({
            responsive: true,
            maintainAspectRatio: false,
            showLegend: false,
            highlightOptimal: true,
            optimalRangeMin: 120,
            optimalRangeMax: 150,
            barColor: 'rgba(156, 39, 176, 0.7)', // 보라색
            barBorderRadius: 4
        }, options);
    }

    /**
     * 차트 생성
     * @param {Object} sumData - 합계 데이터 {min_sum, max_sum, avg_sum, median_sum, most_common_sum, sum_distribution, all_sums}
     */
    createChart(sumData) {
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
        const labels = Object.keys(sumData.sum_distribution) || [];
        const counts = Object.values(sumData.sum_distribution) || [];

        // 차트 생성
        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '빈도수',
                    data: counts,
                    backgroundColor: (context) => {
                        const index = context.dataIndex;
                        const range = labels[index];

                        if (!range) return this.options.barColor;

                        // 범위 문자열에서 시작값 추출 (예: "120-124" -> 120)
                        const rangeStart = parseInt(range.split('-')[0]);

                        // 최적 합계 범위 강조
                        if (this.options.highlightOptimal &&
                            rangeStart >= this.options.optimalRangeMin &&
                            rangeStart < this.options.optimalRangeMax) {
                            return 'rgba(0, 150, 136, 0.8)'; // 청록색
                        }
                        return this.options.barColor;
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
                                return `합계: ${tooltipItems[0].label}`;
                            },
                            label: (context) => {
                                const dataValue = context.parsed.y;
                                const totalCount = counts.reduce((a, b) => a + b, 0);
                                const percent = (dataValue / totalCount * 100).toFixed(1);
                                return `${dataValue}회 발생 (${percent}%)`;
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
                            text: '번호 합계 범위'
                        }
                    }
                }
            }
        });

        // 최적 합계 범위에 배경 표시
        if (this.options.highlightOptimal) {
            this.addOptimalSumRange();
        }

        return this.chart;
    }

    /**
     * 최적 합계 범위 표시 (배경 하이라이트)
     */
    addOptimalSumRange() {
        if (!this.chart) return;

        const chartInstance = this.chart;
        const ctx = chartInstance.ctx;
        const yAxis = chartInstance.scales.y;
        const xAxis = chartInstance.scales.x;

        // 최적 범위에 해당하는 x축 인덱스 찾기
        const optimalMinIndex = this.findRangeIndex(this.options.optimalRangeMin);
        const optimalMaxIndex = this.findRangeIndex(this.options.optimalRangeMax);

        if (optimalMinIndex === -1 || optimalMaxIndex === -1) return;

        // 플러그인 추가
        chartInstance.options.plugins.optimalSumRange = {
            id: 'optimalSumRange',
            beforeDraw: (chart) => {
                if (chart.tooltip?._active?.length) return;

                const minPixel = xAxis.getPixelForValue(optimalMinIndex);
                const maxPixel = xAxis.getPixelForValue(optimalMaxIndex);

                ctx.save();
                ctx.fillStyle = 'rgba(0, 150, 136, 0.1)';
                ctx.fillRect(minPixel, yAxis.top, maxPixel - minPixel, yAxis.bottom - yAxis.top);

                // 범위 표시 레이블
                ctx.fillStyle = 'rgba(0, 150, 136, 0.8)';
                ctx.font = '12px Arial';
                ctx.textAlign = 'center';
                ctx.fillText('최적 범위', (minPixel + maxPixel) / 2, yAxis.bottom + 20);

                ctx.restore();
            }
        };

        // 차트 업데이트
        chartInstance.update();
    }

    /**
     * 값에 해당하는 범위 인덱스 찾기
     * @param {number} value - 찾을 값
     * @returns {number} 해당 범위의 인덱스 또는 -1
     */
    findRangeIndex(value) {
        if (!this.chart) return -1;

        const labels = this.chart.data.labels;
        for (let i = 0; i < labels.length; i++) {
            const range = labels[i];
            const [start, end] = range.split('-').map(Number);

            if (value >= start && value <= end) {
                return i;
            }
        }
        return -1;
    }

    /**
     * 차트 데이터 업데이트
     * @param {Object} sumData - 합계 데이터
     */
    updateData(sumData) {
        if (!this.chart) {
            this.createChart(sumData);
            return;
        }

        // 데이터 변환
        const labels = Object.keys(sumData.sum_distribution) || [];
        const counts = Object.values(sumData.sum_distribution) || [];

        // 차트 데이터 업데이트
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = counts;

        // 최적 합계 범위 업데이트
        if (this.options.highlightOptimal) {
            this.addOptimalSumRange();
        }

        // 차트 다시 그리기
        this.chart.update();
    }

    /**
     * 통계 요약 HTML 생성
     * @param {Object} sumData - 합계 데이터
     * @param {string} containerId - 표시할 컨테이너 ID
     */
    renderSummary(sumData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 합계 데이터 추출
        const minSum = sumData.min_sum;
        const maxSum = sumData.max_sum;
        const avgSum = sumData.avg_sum;
        const medianSum = sumData.median_sum;
        const mostCommonSum = sumData.most_common_sum;

        // 최적 범위에 속하는 합계의 비율 계산
        const allSums = sumData.all_sums || [];
        const optimalCount = allSums.filter(sum =>
            sum >= this.options.optimalRangeMin && sum <= this.options.optimalRangeMax
        ).length;
        const optimalPercent = allSums.length > 0 ? (optimalCount / allSums.length * 100).toFixed(1) : 0;

        // HTML 생성
        container.innerHTML = `
            <div class="alert alert-info">
                <p><strong>평균 합계:</strong> ${avgSum.toFixed(1)}</p>
                <p><strong>중앙값:</strong> ${medianSum}</p>
                <p><strong>가장 많이 나온 합계:</strong> ${mostCommonSum}</p>
                <p><strong>범위:</strong> ${minSum} ~ ${maxSum}</p>
                <p><strong>최적 범위(${this.options.optimalRangeMin}-${this.options.optimalRangeMax}) 비율:</strong> ${optimalPercent}%</p>
                <p><small>* 합계는 당첨 번호 6개의 총합을 의미합니다.</small></p>
            </div>
        `;
    }
}

// 전역 객체에 등록
window.SumChart = SumChart;
/**
 * ac-chart.js - AC값 차트 모듈
 * AC값(Arithmetic Complexity): 로또 번호 조합의 복잡도를 측정하는 지표
 */

/**
 * AC값 차트 생성 클래스
 */
class ACChart {
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
            showValues: true,
            highlightOptimal: true,
            optimalRangeMin: 7,
            optimalRangeMax: 12,
            barBorderRadius: 4
        }, options);
    }

    /**
     * 차트 생성
     * @param {Object} acData - AC값 데이터 {counts, labels, avg_ac, most_common_ac, distribution}
     */
    createChart(acData) {
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
        const labels = acData.labels || [];
        const counts = acData.counts || [];

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
                        const value = parseInt(labels[index]);

                        // 최적 AC 범위 강조
                        if (this.options.highlightOptimal &&
                            value >= this.options.optimalRangeMin &&
                            value <= this.options.optimalRangeMax) {
                            return 'rgba(76, 175, 80, 0.8)'; // 초록색
                        }
                        return 'rgba(33, 150, 243, 0.7)'; // 파란색
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
                                return `AC값: ${tooltipItems[0].label}`;
                            },
                            label: (context) => {
                                const dataValue = context.parsed.y;
                                const percent = (dataValue / counts.reduce((a, b) => a + b, 0) * 100).toFixed(1);
                                return [
                                    `${dataValue}회 발생 (${percent}%)`,
                                    this.getACDescription(parseInt(context.label))
                                ];
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'AC값 (복잡도)'
                        }
                    }
                }
            }
        });

        // 최적 AC값 범위 표시하기
        if (this.options.highlightOptimal) {
            this.addOptimalACRange();
        }

        return this.chart;
    }

    /**
     * 최적 AC값 범위 표시 (배경 하이라이트)
     */
    addOptimalACRange() {
        if (!this.chart) return;

        const chartInstance = this.chart;
        const ctx = chartInstance.ctx;
        const yAxis = chartInstance.scales.y;
        const xAxis = chartInstance.scales.x;

        // 최적 범위의 x 위치 계산
        const minIndex = this.options.optimalRangeMin;
        const maxIndex = this.options.optimalRangeMax;

        const minPixel = xAxis.getPixelForValue(minIndex);
        const maxPixel = xAxis.getPixelForValue(maxIndex + 1); // +1 for inclusive

        // 플러그인 추가
        chartInstance.options.plugins.optimalACRange = {
            id: 'optimalACRange',
            beforeDraw: (chart) => {
                if (chart.tooltip?._active?.length) return;

                ctx.save();
                ctx.fillStyle = 'rgba(76, 175, 80, 0.1)';
                ctx.fillRect(minPixel, yAxis.top, maxPixel - minPixel, yAxis.bottom - yAxis.top);

                // 범위 표시 레이블
                ctx.fillStyle = 'rgba(76, 175, 80, 0.8)';
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
     * AC값에 따른 설명 반환
     * @param {number} acValue - AC값
     * @returns {string} AC값 설명
     */
    getACDescription(acValue) {
        if (acValue < 5) return "매우 낮은 복잡도 (간단한 패턴)";
        if (acValue < 7) return "낮은 복잡도";
        if (acValue < 10) return "적절한 복잡도";
        if (acValue < 13) return "높은 복잡도";
        return "매우 높은 복잡도 (매우 랜덤한 조합)";
    }

    /**
     * 차트 데이터 업데이트
     * @param {Object} acData - AC값 데이터
     */
    updateData(acData) {
        if (!this.chart) {
            this.createChart(acData);
            return;
        }

        // 데이터 변환
        const labels = acData.labels || [];
        const counts = acData.counts || [];

        // 차트 데이터 업데이트
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = counts;

        // 최적 AC값 범위 업데이트
        if (this.options.highlightOptimal) {
            this.addOptimalACRange();
        }

        // 차트 다시 그리기
        this.chart.update();
    }

    /**
     * 통계 요약 HTML 생성
     * @param {Object} acData - AC값 데이터
     * @param {string} containerId - 표시할 컨테이너 ID
     */
    renderSummary(acData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 가장 많이 나온 AC값
        const mostCommonAC = acData.most_common_ac;
        const avgAC = acData.avg_ac;

        // AC값 분포에서 최적 범위 내의 비율 계산
        const optimalCount = Object.entries(acData.distribution)
            .filter(([ac, _]) => {
                const acValue = parseInt(ac);
                return acValue >= this.options.optimalRangeMin && acValue <= this.options.optimalRangeMax;
            })
            .reduce((sum, [_, count]) => sum + count, 0);

        const totalCount = Object.values(acData.distribution).reduce((sum, count) => sum + count, 0);
        const optimalPercent = totalCount > 0 ? (optimalCount / totalCount * 100).toFixed(1) : 0;

        // HTML 생성
        container.innerHTML = `
            <div class="alert alert-info">
                <p><strong>평균 AC값:</strong> ${avgAC.toFixed(2)}</p>
                <p><strong>가장 많이 나온 AC값:</strong> ${mostCommonAC} (${this.getACDescription(mostCommonAC)})</p>
                <p><strong>최적 범위(${this.options.optimalRangeMin}-${this.options.optimalRangeMax}) 비율:</strong> ${optimalPercent}%</p>
                <p><small>* AC값은 번호 조합의 복잡도를 나타내며, 높을수록 더 랜덤한 조합입니다.</small></p>
            </div>
        `;
    }
}

// 전역 객체에 등록
window.ACChart = ACChart;
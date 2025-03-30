/**
 * odd-even-chart.js - 홀짝 비율 차트 모듈
 */

/**
 * 홀짝 비율 차트 생성 클래스
 */
class OddEvenChart {
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
            showLegend: true,
            showLabels: true,
            colorScheme: ['#f44336', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#795548', '#607d8b'] // 빨강, 파랑, 초록, 주황, 보라, 갈색, 회색
        }, options);
    }

    /**
     * 차트 생성
     * @param {Object} oddEvenData - 홀짝 비율 데이터 {counts, percentages, labels}
     */
    createChart(oddEvenData) {
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
        const labels = oddEvenData.labels || [];
        const data = oddEvenData.percentages || [];
        const counts = oddEvenData.counts || [];

        // 차트 생성
        this.chart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: this.options.colorScheme.slice(0, data.length),
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
                                const value = context.raw || 0;
                                const count = counts[context.dataIndex] || 0;
                                return `${label}: ${value}% (${count}회)`;
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
     * @param {Object} oddEvenData - 홀짝 비율 데이터
     */
    updateData(oddEvenData) {
        if (!this.chart) {
            this.createChart(oddEvenData);
            return;
        }

        // 데이터 변환
        const labels = oddEvenData.labels || [];
        const data = oddEvenData.percentages || [];

        // 차트 데이터 업데이트
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.data.datasets[0].backgroundColor = this.options.colorScheme.slice(0, data.length);

        // 차트 다시 그리기
        this.chart.update();
    }

    /**
     * 통계 요약 HTML 생성
     * @param {Object} oddEvenData - 홀짝 비율 데이터
     * @param {string} containerId - 표시할 컨테이너 ID
     */
    renderSummary(oddEvenData, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        // 가장 높은 비율 찾기
        const maxIndex = oddEvenData.percentages.indexOf(Math.max(...oddEvenData.percentages));
        const maxLabel = oddEvenData.labels[maxIndex];
        const maxPercent = oddEvenData.percentages[maxIndex].toFixed(1);
        const maxCount = oddEvenData.counts[maxIndex];

        // 평균 계산
        const totalOdds = oddEvenData.labels.reduce((sum, label, i) => {
            const oddCount = parseInt(label.split(':')[0].replace('홀', ''));
            return sum + (oddCount * oddEvenData.counts[i]);
        }, 0);
        const totalCounts = oddEvenData.counts.reduce((sum, count) => sum + count, 0);
        const avgOdds = totalOdds / totalCounts;

        // HTML 생성
        container.innerHTML = `
            <div class="alert alert-info">
                <p><strong>가장 많은 홀짝 조합:</strong> ${maxLabel} (${maxPercent}%, ${maxCount}회)</p>
                <p><strong>평균 홀수 개수:</strong> ${avgOdds.toFixed(2)}개</p>
                <p><strong>변동성:</strong> ${this.calculateVariability(oddEvenData)}</p>
            </div>
        `;
    }

    /**
     * 변동성 계산 (낮음, 보통, 높음)
     * @param {Object} oddEvenData - 홀짝 비율 데이터
     * @returns {string} 변동성 레벨
     */
    calculateVariability(oddEvenData) {
        const percentages = oddEvenData.percentages;

        // 표준편차 계산
        const mean = percentages.reduce((sum, p) => sum + p, 0) / percentages.length;
        const variance = percentages.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / percentages.length;
        const stdDev = Math.sqrt(variance);

        // 변동성 레벨 결정
        if (stdDev < 3) return "낮음 (고른 분포)";
        if (stdDev < 6) return "보통";
        return "높음 (특정 패턴 편중)";
    }
}

// 전역 객체에 등록
window.OddEvenChart = OddEvenChart;
/**
 * 차트 렌더링 문제 해결을 위한 추가 스크립트
 * 모든 차트 컨테이너가 보이는지 확인하고 차트 크기를 조정합니다.
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('차트 렌더링 문제 해결 스크립트 로드됨');

    // 통계 탭이 활성화되면 차트 크기 조정 및 재렌더링
    document.addEventListener('tabActivated', function(e) {
        if (e.detail.tabId === 'stats') {
            console.log('통계 탭 활성화: 차트 조정 실행');
            setTimeout(resizeAndRenderCharts, 500);
        }
    });

    // 샘플 데이터 기반 차트 즉시 렌더링 (통계 데이터 로드 전)
    document.addEventListener('loadStatsData', function() {
        console.log('통계 데이터 로드 이벤트 감지');
        // 일부 차트를 사전 렌더링하여 UI가 비어 보이지 않게 함
        preRenderCharts();
    });

    // 샘플 데이터로 차트 사전 렌더링
    function preRenderCharts() {
        try {
            // 통계 컨텐츠가 표시되기 전 차트 컨테이너 크기 조정
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {
                if (container.style.height === '') {
                    container.style.height = '200px';
                }
            });

            // 비어있는 차트들 미리 생성 (임시 내용)
            createEmptyChart('oddEvenDistChart', '홀짝 비율');
            createEmptyChart('highLowDistChart', '고저 비율');
            createEmptyChart('acValueChart', 'AC값');
            createEmptyChart('sumTrendChart', '총합 추이');
        } catch (error) {
            console.error('차트 사전 렌더링 중 오류:', error);
        }
    }

    // 빈 차트 생성 (데이터 로드 중 표시용)
    function createEmptyChart(canvasId, title) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;

        // 이미 차트가 있는지 확인
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            existingChart.destroy();
        }

        // 로딩 차트 생성
        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['로딩 중...'],
                datasets: [{
                    label: title,
                    data: [0],
                    backgroundColor: 'rgba(200, 200, 200, 0.5)',
                    borderWidth: 0
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
                            title: function() {
                                return '데이터 로딩 중...';
                            },
                            label: function() {
                                return '잠시만 기다려주세요';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 10,
                        ticks: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                animation: {
                    duration: 0
                }
            }
        });
    }

    // 차트 크기 조정 및 재렌더링
    function resizeAndRenderCharts() {
        const statsContent = document.getElementById('statsContent');
        if (!statsContent || statsContent.classList.contains('d-none')) {
            console.log('통계 컨텐츠가 표시되지 않음, 1초 후 재시도');
            setTimeout(resizeAndRenderCharts, 1000);
            return;
        }

        console.log('차트 크기 조정 및 재렌더링 시작');

        try {
            // 차트 컨테이너들의 크기 설정
            const chartContainers = document.querySelectorAll('.chart-container');
            chartContainers.forEach(container => {
                // 컨테이너가 화면에 표시되어 있고 크기가 0이면 크기 재설정
                if (container.offsetParent !== null &&
                    (container.offsetWidth === 0 || container.offsetHeight === 0)) {
                    container.style.height = '200px';
                    container.style.width = '100%';
                    console.log('차트 컨테이너 크기 조정:', container);
                }
            });

            // 차트 강제 업데이트
            const chartIds = [
                'oddEvenDistChart',
                'highLowDistChart',
                'acValueChart',
                'sumTrendChart',
                'numberFrequencyChartFull'
            ];

            chartIds.forEach(id => {
                const canvas = document.getElementById(id);
                if (canvas) {
                    const chart = Chart.getChart(canvas);
                    if (chart) {
                        // 차트가 정상적으로 렌더링되었는지 확인
                        if (chart.width === 0 || chart.height === 0) {
                            console.log(`차트 ${id} 크기가 0, 재조정 중`);
                            chart.resize();
                            chart.update();
                        }
                    }
                }
            });

            // 타이밍 문제를 해결하기 위해 약간의 지연 후 다시 확인
            setTimeout(() => {
                // 브라우저 창 크기 변경 이벤트 발생시켜 차트 재조정
                window.dispatchEvent(new Event('resize'));

                // 특정 차트에 문제가 있는지 다시 확인
                chartIds.forEach(id => {
                    const canvas = document.getElementById(id);
                    if (canvas) {
                        const chart = Chart.getChart(canvas);
                        if (chart && (chart.width === 0 || chart.height === 0)) {
                            console.log(`차트 ${id} 재생성 시도`);
                            chart.destroy();

                            // 기존 차트 데이터가 있는지 확인
                            if (window.chartData && window.chartData[id]) {
                                // 저장된 설정으로 차트 다시 생성
                                new Chart(canvas, window.chartData[id]);
                            }
                        }
                    }
                });
            }, 500);
        } catch (error) {
            console.error('차트 조정 중 오류:', error);
        }
    }

    // 차트 데이터 저장소 초기화
    window.chartData = {};

    // 원본 Chart 생성자 함수 확장
    const originalChart = Chart;
    window.Chart = function(ctx, config) {
        // 차트 ID 저장 (캔버스 ID 기준)
        if (ctx.id) {
            window.chartData[ctx.id] = config;
        }
        return new originalChart(ctx, config);
    };
    // 정적 메서드 복사
    Object.keys(originalChart).forEach(key => {
        window.Chart[key] = originalChart[key];
    });

    // URL에 #stats가 있으면 통계 탭 활성화
    if (window.location.hash === '#stats') {
        const statsTab = document.querySelector('[data-tab="stats"]');
        if (statsTab) {
            statsTab.click();
        }
    }
});
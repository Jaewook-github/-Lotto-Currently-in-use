/**
 * tab-manager.js - 탭 관리 모듈
 * 통계 탭 간 전환 및 탭 내용 로딩 관리
 */

const TabManager = (function() {
    // 로딩된 탭 목록 (중복 로딩 방지용)
    let loadedTabs = {};

    // 현재 활성화된 탭
    let activeTab = null;

    // 각 탭별 데이터 저장
    let tabsData = {};

    /**
     * 탭 초기화
     * @param {string} tabContainerId - 탭 컨테이너 ID
     * @param {Object} options - 초기화 옵션
     */
    function initTabs(tabContainerId, options = {}) {
        const tabContainer = document.getElementById(tabContainerId);
        if (!tabContainer) return;

        // 기본 옵션
        const defaultOptions = {
            defaultTab: null,          // 기본 활성화 탭 ID
            onTabChange: null,         // 탭 변경 시 콜백
            loadDataOnInit: true,      // 초기화 시 데이터 로드 여부
            autoActivate: true         // 자동 탭 활성화 여부
        };

        const settings = { ...defaultOptions, ...options };

        // 탭 버튼 이벤트 설정
        const tabButtons = tabContainer.querySelectorAll('[data-bs-toggle="tab"]');

        tabButtons.forEach(button => {
            // 탭 ID 저장
            const tabId = button.getAttribute('data-bs-target');
            const contentElement = document.querySelector(tabId);

            if (contentElement) {
                // 로딩 상태 초기화
                loadedTabs[tabId] = false;

                // 탭 전환 이벤트
                button.addEventListener('shown.bs.tab', function (e) {
                    const currentTabId = e.target.getAttribute('data-bs-target');
                    activeTab = currentTabId;

                    // 처음 활성화된 탭이면 콘텐츠 로드
                    if (!loadedTabs[currentTabId] && settings.loadDataOnInit) {
                        loadTabContent(currentTabId);
                    }

                    // 콜백 실행
                    if (typeof settings.onTabChange === 'function') {
                        settings.onTabChange(currentTabId, tabsData[currentTabId.substring(1)]);
                    }

                    // 히스토리 업데이트 (URL 해시)
                    history.replaceState(null, null, currentTabId);
                });
            }
        });

        // 기본 탭 활성화 또는 URL 해시에 따른 탭 활성화
        if (settings.autoActivate) {
            // URL 해시 확인
            const hash = window.location.hash;
            let initialTab = null;

            if (hash && document.querySelector(`[data-bs-target="${hash}"]`)) {
                initialTab = hash;
            } else if (settings.defaultTab && document.querySelector(`[data-bs-target="${settings.defaultTab}"]`)) {
                initialTab = settings.defaultTab;
            } else if (tabButtons.length > 0) {
                initialTab = tabButtons[0].getAttribute('data-bs-target');
            }

            if (initialTab) {
                const tabElement = document.querySelector(`[data-bs-target="${initialTab}"]`);
                const tab = new bootstrap.Tab(tabElement);
                tab.show();
            }
        }
    }

    /**
     * 탭 컨텐츠 로드
     * @param {string} tabId - 로드할 탭 ID (예: '#tab-all')
     * @param {boolean} forceReload - 이미 로드된 탭도 강제 새로고침
     */
    function loadTabContent(tabId, forceReload = false) {
        // 이미 로드된 탭이고 강제 새로고침이 아니면 무시
        if (loadedTabs[tabId] && !forceReload) return;

        const tabContent = document.querySelector(tabId);
        if (!tabContent) return;

        // 탭 ID에서 데이터 키 추출 (예: '#tab-all' -> 'all')
        const dataKey = tabId.split('-')[1]?.replace('#', '') || tabId.substring(1);

        // 로딩 중 표시
        showTabLoading(tabContent);

        // 탭 유형에 따른 데이터 로드
        let dataPromise = null;

        switch (dataKey) {
            case 'all':
                // 전체 회차 통계 데이터 로드
                dataPromise = ApiClient.loadFullStats().then(data => data.all);
                break;

            case 'recent100':
            case 'recent_100':
                // 최근 100회차 통계 데이터 로드
                dataPromise = ApiClient.loadFullStats().then(data => data.recent_100);
                break;

            case 'recent10':
            case 'recent_10':
                // 최근 10회차 통계 데이터 로드
                dataPromise = ApiClient.loadFullStats().then(data => data.recent_10);
                break;

            default:
                // 사용자 지정 회차 범위 데이터 로드
                dataPromise = Promise.resolve({});
                console.error(`알 수 없는 탭 유형: ${dataKey}`);
                break;
        }

        // 데이터 로드 후 처리
        dataPromise.then(data => {
            // 탭 데이터 저장
            tabsData[dataKey] = data;

            // 로딩 상태 업데이트
            loadedTabs[tabId] = true;

            // 로딩 완료 표시
            hideTabLoading(tabContent);

            // 차트 초기화
            initTabCharts(tabContent, data, dataKey);

            // 데이터 로드 완료 이벤트 발생
            document.dispatchEvent(new CustomEvent('tabDataLoaded', {
                detail: { tabId, dataKey, data }
            }));

            return data;
        }).catch(error => {
            console.error(`탭 데이터 로드 오류 (${tabId}):`, error);

            // 오류 화면 표시
            showTabError(tabContent, error);

            // 로딩 상태 업데이트 (오류 발생 시 다시 로드할 수 있도록)
            loadedTabs[tabId] = false;
        });

        return dataPromise;
    }

    /**
     * 탭 로딩 중 표시
     * @param {HTMLElement} tabContent - 탭 컨텐츠 요소
     */
    function showTabLoading(tabContent) {
        // 로딩 중 표시
        tabContent.querySelectorAll('.chart-container').forEach(container => {
            const loadingElement = document.createElement('div');
            loadingElement.className = 'chart-loading';
            loadingElement.innerHTML = `
                <div class="chart-loading-spinner"></div>
                <div class="chart-loading-text">차트 로딩 중...</div>
            `;
            container.appendChild(loadingElement);
        });
    }

    /**
     * 탭 로딩 완료 표시
     * @param {HTMLElement} tabContent - 탭 컨텐츠 요소
     */
    function hideTabLoading(tabContent) {
        // 로딩 중 표시 제거
        tabContent.querySelectorAll('.chart-loading').forEach(loader => {
            loader.remove();
        });
    }

    /**
     * 탭 로딩 오류 표시
     * @param {HTMLElement} tabContent - 탭 컨텐츠 요소
     * @param {Error} error - 오류 객체
     */
    function showTabError(tabContent, error) {
        // 로딩 중 표시 제거
        hideTabLoading(tabContent);

        // 차트 컨테이너에 오류 표시
        tabContent.querySelectorAll('.chart-container').forEach(container => {
            const errorElement = document.createElement('div');
            errorElement.className = 'chart-error';
            errorElement.innerHTML = `
                <div class="chart-error-icon"><i class="fas fa-exclamation-triangle"></i></div>
                <div class="chart-error-text">차트 로딩 중 오류가 발생했습니다: ${error.message || '알 수 없는 오류'}</div>
                <div class="chart-error-action">
                    <button class="btn btn-sm btn-danger reload-chart-btn">다시 시도</button>
                </div>
            `;
            container.appendChild(errorElement);

            // 다시 시도 버튼 이벤트
            const reloadBtn = errorElement.querySelector('.reload-chart-btn');
            if (reloadBtn) {
                reloadBtn.addEventListener('click', () => {
                    errorElement.remove();
                    loadTabContent(activeTab, true);
                });
            }
        });
    }

    /**
     * 탭 차트 초기화
     * @param {HTMLElement} tabContent - 탭 컨텐츠 요소
     * @param {Object} data - 차트 데이터
     * @param {string} dataKey - 데이터 키 (all, recent_100 등)
     */
    function initTabCharts(tabContent, data, dataKey) {
        // 주파수 차트 (출현 빈도)
        const freqChartContainer = tabContent.querySelector('#frequencyChart');
        if (freqChartContainer && data.frequency) {
            const freqCanvas = freqChartContainer.querySelector('canvas');
            if (freqCanvas) {
                const freqChart = new FrequencyChart(freqCanvas.id);
                freqChart.createChart(data.frequency);

                // 상위 번호 표시
                const topNumbersContainer = tabContent.querySelector('.top-numbers');
                if (topNumbersContainer) {
                    freqChart.renderTopNumbers(data.frequency, topNumbersContainer.id);
                }
            }
        }

        // 홀짝 비율 차트
        const oddEvenChartContainer = tabContent.querySelector('#oddEvenChart');
        if (oddEvenChartContainer && data.odd_even_stats) {
            const oddEvenCanvas = oddEvenChartContainer.querySelector('canvas');
            if (oddEvenCanvas) {
                const oddEvenChart = new OddEvenChart(oddEvenCanvas.id);
                oddEvenChart.createChart(data.odd_even_stats);

                // 요약 정보 표시
                const oddEvenSummaryContainer = tabContent.querySelector('.odd-even-summary');
                if (oddEvenSummaryContainer) {
                    oddEvenChart.renderSummary(data.odd_even_stats, oddEvenSummaryContainer.id);
                }
            }
        }

        // 고저 비율 차트
        const highLowChartContainer = tabContent.querySelector('#highLowChart');
        if (highLowChartContainer && data.high_low_stats) {
            const highLowCanvas = highLowChartContainer.querySelector('canvas');
            if (highLowCanvas) {
                const highLowChart = new HighLowChart(highLowCanvas.id);
                highLowChart.createChart(data.high_low_stats);

                // 요약 정보 표시
                const highLowSummaryContainer = tabContent.querySelector('.high-low-summary');
                if (highLowSummaryContainer) {
                    highLowChart.renderSummary(data.high_low_stats, highLowSummaryContainer.id);
                }
            }
        }

        // AC값 차트
        const acChartContainer = tabContent.querySelector('#acValueChart');
        if (acChartContainer && data.ac_value_stats) {
            const acCanvas = acChartContainer.querySelector('canvas');
            if (acCanvas) {
                const acChart = new ACChart(acCanvas.id);
                acChart.createChart(data.ac_value_stats);

                // 요약 정보 표시
                const acSummaryContainer = tabContent.querySelector('.ac-summary');
                if (acSummaryContainer) {
                    acChart.renderSummary(data.ac_value_stats, acSummaryContainer.id);
                }
            }
        }

        // 합계 차트
        const sumChartContainer = tabContent.querySelector('#sumChart');
        if (sumChartContainer && data.sum_stats) {
            const sumCanvas = sumChartContainer.querySelector('canvas');
            if (sumCanvas) {
                const sumChart = new SumChart(sumCanvas.id);
                sumChart.createChart(data.sum_stats);

                // 요약 정보 표시
                const sumSummaryContainer = tabContent.querySelector('.sum-summary');
                if (sumSummaryContainer) {
                    sumChart.renderSummary(data.sum_stats, sumSummaryContainer.id);
                }
            }
        }

        // 패턴 차트들 초기화
        const patternCharts = new PatternCharts();

        // 소수 패턴 차트
        const primeChartContainer = tabContent.querySelector('#primeChart');
        if (primeChartContainer && data.pattern_analysis) {
            const primeCanvas = primeChartContainer.querySelector('canvas');
            if (primeCanvas) {
                patternCharts.createPrimeChart(primeCanvas.id, data.pattern_analysis);
            }
        }

        // 3의 배수 패턴 차트
        const mult3ChartContainer = tabContent.querySelector('#mult3Chart');
        if (mult3ChartContainer && data.pattern_analysis) {
            const mult3Canvas = mult3ChartContainer.querySelector('canvas');
            if (mult3Canvas) {
                patternCharts.createMult3Chart(mult3Canvas.id, data.pattern_analysis);
            }
        }

        // 끝수 분포 차트
        const lastDigitChartContainer = tabContent.querySelector('#lastDigitChart');
        if (lastDigitChartContainer && data.last_digit_analysis) {
            const lastDigitCanvas = lastDigitChartContainer.querySelector('canvas');
            if (lastDigitCanvas) {
                patternCharts.createLastDigitChart(lastDigitCanvas.id, data.last_digit_analysis);
            }
        }

        // 연속 숫자 쌍 차트
        const consecutiveChartContainer = tabContent.querySelector('#consecutiveChart');
        if (consecutiveChartContainer && data.consecutive_pairs_stats) {
            const consecutiveCanvas = consecutiveChartContainer.querySelector('canvas');
            if (consecutiveCanvas) {
                patternCharts.createConsecutiveChart(consecutiveCanvas.id, data.consecutive_pairs_stats);
            }
        }

        // 번호 조합 패턴 차트
        const combinationChartContainer = tabContent.querySelector('#combinationChart');
        if (combinationChartContainer && data.combinations_analysis) {
            const combinationCanvas = combinationChartContainer.querySelector('canvas');
            if (combinationCanvas) {
                patternCharts.createCombinationChart(combinationCanvas.id, data.combinations_analysis);
            }
        }
    }

    /**
     * 현재 활성화된 탭 ID 가져오기
     * @returns {string} 활성 탭 ID
     */
    function getActiveTab() {
        return activeTab;
    }

    /**
     * 특정 탭의 로딩 상태 가져오기
     * @param {string} tabId - 탭 ID
     * @returns {boolean} 로딩 완료 여부
     */
    function isTabLoaded(tabId) {
        return loadedTabs[tabId] || false;
    }

    /**
     * 특정 탭의 데이터 가져오기
     * @param {string} tabKey - 탭 키 (all, recent_100 등)
     * @returns {Object} 탭 데이터
     */
    function getTabData(tabKey) {
        return tabsData[tabKey] || null;
    }

    /**
     * 모든 탭 데이터 새로고침
     */
    function refreshAllTabs() {
        // 모든 탭 로딩 상태 초기화
        Object.keys(loadedTabs).forEach(tabId => {
            loadedTabs[tabId] = false;
        });

        // 현재 활성화된 탭만 새로고침
        if (activeTab) {
            loadTabContent(activeTab, true);
        }
    }

    // 공개 API
    return {
        initTabs,
        loadTabContent,
        getActiveTab,
        isTabLoaded,
        getTabData,
        refreshAllTabs
    };
})();

// 전역 객체에 등록
window.TabManager = TabManager;
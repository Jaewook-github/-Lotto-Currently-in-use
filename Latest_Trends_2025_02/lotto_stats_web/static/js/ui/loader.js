/**
 * loader.js - 로딩 관리 모듈
 * 애플리케이션 전반의 로딩 상태를 관리합니다.
 */

const LoaderManager = (function() {
    // 전역 로딩 오버레이 요소
    let globalLoader;

    // 로딩 중인 요청 카운터
    let loadingCounter = 0;

    // 로딩 지연 타이머
    let loaderTimer = null;

    // 최소 로딩 표시 시간 (밀리초)
    const MIN_LOADING_TIME = 300;

    /**
     * 전역 로더 요소 가져오기
     * @returns {HTMLElement} 로더 요소
     */
    function getLoaderElement() {
        if (!globalLoader) {
            globalLoader = document.getElementById('loadingOverlay');

            // 로더가 없으면 동적으로 생성
            if (!globalLoader) {
                globalLoader = document.createElement('div');
                globalLoader.id = 'loadingOverlay';
                globalLoader.className = 'loading-overlay';

                const spinner = document.createElement('div');
                spinner.className = 'loading-spinner';

                const spinnerInner = document.createElement('div');
                spinnerInner.className = 'spinner';

                const spinnerText = document.createElement('div');
                spinnerText.className = 'spinner-text';
                spinnerText.textContent = '데이터 로딩 중...';

                spinner.appendChild(spinnerInner);
                spinner.appendChild(spinnerText);
                globalLoader.appendChild(spinner);

                document.body.appendChild(globalLoader);
            }
        }

        return globalLoader;
    }

    /**
     * 로딩 오버레이 표시
     * @param {string} text - 표시할 텍스트 (기본값: '데이터 로딩 중...')
     */
    function showLoader(text) {
        const loader = getLoaderElement();

        // 로딩 텍스트 설정
        if (text) {
            const textElement = loader.querySelector('.spinner-text');
            if (textElement) {
                textElement.textContent = text;
            }
        }

        // 이미 표시된 타이머가 있으면 클리어
        if (loaderTimer) {
            clearTimeout(loaderTimer);
            loaderTimer = null;
        }

        // 첫 번째 로딩 요청일 때만 표시
        if (loadingCounter === 0) {
            loader.classList.add('show');
        }

        // 로딩 카운터 증가
        loadingCounter++;
    }

    /**
     * 로딩 오버레이 숨김
     */
    function hideLoader() {
        // 로딩 카운터 감소
        loadingCounter = Math.max(0, loadingCounter - 1);

        // 모든 로딩이 완료되면 오버레이 숨김 (최소 표시 시간 이후)
        if (loadingCounter === 0) {
            const loader = getLoaderElement();

            // 최소 표시 시간 적용
            loaderTimer = setTimeout(() => {
                loader.classList.remove('show');
                loaderTimer = null;
            }, MIN_LOADING_TIME);
        }
    }

    /**
     * 모든 로딩 강제 종료
     */
    function forceHideLoader() {
        loadingCounter = 0;

        if (loaderTimer) {
            clearTimeout(loaderTimer);
            loaderTimer = null;
        }

        const loader = getLoaderElement();
        loader.classList.remove('show');
    }

    /**
     * 로딩 상태 가져오기
     * @returns {boolean} 로딩 중인지 여부
     */
    function isLoading() {
        return loadingCounter > 0;
    }

    /**
     * 지연 함수 (비동기 작업 중간에 로딩 상태 업데이트용)
     * @param {number} ms - 지연 시간 (밀리초)
     * @returns {Promise} 지연 프로미스
     */
    function delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 공개 API
    return {
        showLoader,
        hideLoader,
        forceHideLoader,
        isLoading,
        delay
    };
})();

// 전역 함수로 등록
window.showLoader = LoaderManager.showLoader;
window.hideLoader = LoaderManager.hideLoader;
/**
 * api-client.js - API 통신 모듈
 * 서버와의 통신을 담당하는 유틸리티 함수들
 */

/**
 * API 클라이언트 객체
 */
const ApiClient = {
    /**
     * 전체 통계 데이터 로드
     * @param {boolean} forceRefresh - 캐시 강제 갱신 여부
     * @returns {Promise} API 응답 Promise
     */
    loadFullStats: async function(forceRefresh = false) {
        try {
            showLoader();
            const url = forceRefresh ? '/api/stats?refresh=true' : '/api/stats';
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '통계 데이터를 불러오는데 실패했습니다.');
            }

            return data.stats;
        } catch (error) {
            console.error('통계 데이터 로드 오류:', error);
            showNotification('오류', error.message || '통계 데이터를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    },

    /**
     * 최근 N회 통계 데이터 로드
     * @param {number} limit - 가져올 회차 수
     * @returns {Promise} API 응답 Promise
     */
    loadRecentStats: async function(limit = 10) {
        try {
            showLoader();
            const response = await fetch(`/api/recent?limit=${limit}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '최근 통계 데이터를 불러오는데 실패했습니다.');
            }

            return data.stats;
        } catch (error) {
            console.error('최근 통계 데이터 로드 오류:', error);
            showNotification('오류', error.message || '최근 통계 데이터를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    },

    /**
     * 특정 회차 범위 조회
     * @param {number} start - 시작 회차
     * @param {number} end - 끝 회차
     * @returns {Promise} API 응답 Promise
     */
    loadDrawRange: async function(start, end) {
        try {
            showLoader();
            const response = await fetch(`/api/draws?start=${start}&end=${end}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '회차 데이터를 불러오는데 실패했습니다.');
            }

            return data.draws;
        } catch (error) {
            console.error('회차 데이터 로드 오류:', error);
            showNotification('오류', error.message || '회차 데이터를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    },

    /**
     * 최근 N회 당첨 번호 조회
     * @param {number} limit - 가져올 회차 수
     * @returns {Promise} API 응답 Promise
     */
    loadRecentDraws: async function(limit = 10) {
        try {
            showLoader();
            const response = await fetch(`/api/draws?limit=${limit}`);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '당첨 번호를 불러오는데 실패했습니다.');
            }

            return data.draws;
        } catch (error) {
            console.error('당첨 번호 로드 오류:', error);
            showNotification('오류', error.message || '당첨 번호를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    },

    /**
     * 번호 빈도 데이터 로드
     * @param {number} limit - 최근 n회 제한 (옵션)
     * @returns {Promise} API 응답 Promise
     */
    loadFrequencyData: async function(limit = null) {
        try {
            showLoader();
            const url = limit ? `/api/frequency?limit=${limit}` : '/api/frequency';
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '빈도 데이터를 불러오는데 실패했습니다.');
            }

            return data.frequency;
        } catch (error) {
            console.error('빈도 데이터 로드 오류:', error);
            showNotification('오류', error.message || '빈도 데이터를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    },

    /**
     * 특정 분석 데이터 로드
     * @param {string} analysisType - 분석 유형 (ac, sum, odd_even 등)
     * @param {number} limit - 최근 n회 제한 (옵션)
     * @param {Object} params - 추가 파라미터
     * @returns {Promise} API 응답 Promise
     */
    loadAnalysisData: async function(analysisType, limit = null, params = {}) {
        try {
            showLoader();

            // URL 파라미터 생성
            let queryParams = [];
            if (limit !== null) {
                queryParams.push(`limit=${limit}`);
            }

            // 추가 파라미터 처리
            for (const [key, value] of Object.entries(params)) {
                queryParams.push(`${key}=${value}`);
            }

            const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
            const url = `/api/analysis/${analysisType}${queryString}`;

            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || '분석 데이터를 불러오는데 실패했습니다.');
            }

            return data.data;
        } catch (error) {
            console.error(`${analysisType} 분석 데이터 로드 오류:`, error);
            showNotification('오류', error.message || '분석 데이터를 불러오는데 실패했습니다.', 'error');
            throw error;
        } finally {
            hideLoader();
        }
    }
};

// 전역 범위로 노출
window.ApiClient = ApiClient;
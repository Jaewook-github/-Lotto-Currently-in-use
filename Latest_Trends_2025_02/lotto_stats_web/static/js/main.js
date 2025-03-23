/**
 * main.js - 로또 통계 분석 사이트 메인 스크립트
 */

// 페이지 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    // 페이지 초기화
    initPage();

    // 이벤트 리스너 등록
    setupEventListeners();
});

/**
 * 페이지 초기화 함수
 */
function initPage() {
    // 현재 페이지 탭 활성화
    activateCurrentTab();

    // 툴팁 초기화
    initializeTooltips();

    // 통계 탭 활성화 (있는 경우)
    initializeStatsTabs();
}

/**
 * 이벤트 리스너 설정
 */
function setupEventListeners() {
    // 통계 새로고침 버튼
    const refreshStatsBtn = document.getElementById('refreshStats');
    if (refreshStatsBtn) {
        refreshStatsBtn.addEventListener('click', function() {
            window.location.href = '/refresh';
        });
    }

    // 통계 탭 전환 이벤트
    setupStatsTabEvents();
}

/**
 * 현재 페이지 탭 활성화
 */
function activateCurrentTab() {
    // 현재 경로 확인
    const currentPath = window.location.pathname;

    // 해당 메뉴 아이템 찾기
    const navItems = document.querySelectorAll('.navbar-nav .nav-link');

    navItems.forEach(item => {
        const href = item.getAttribute('href');

        // 경로가 일치하면 active 클래스 추가
        if (href === currentPath ||
            (href !== '/' && currentPath.startsWith(href))) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });
}

/**
 * 툴팁 초기화
 */
function initializeTooltips() {
    // Bootstrap 툴팁 초기화
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            boundary: document.body
        });
    });
}

/**
 * 통계 탭 초기화
 */
function initializeStatsTabs() {
    // 통계 탭 요소 확인
    const statsTab = document.getElementById('statsTab');
    if (!statsTab) return;

    // 첫 번째 탭 활성화
    const firstTab = statsTab.querySelector('.nav-link');
    if (firstTab) {
        firstTab.classList.add('active');

        // 탭 컨텐츠도 활성화
        const tabId = firstTab.getAttribute('data-bs-target');
        const tabContent = document.querySelector(tabId);
        if (tabContent) {
            tabContent.classList.add('show', 'active');
        }
    }
}

/**
 * 통계 탭 이벤트 설정
 */
function setupStatsTabEvents() {
    // URL 해시에 따라 탭 전환
    const hash = window.location.hash;
    if (hash) {
        const tab = document.querySelector(`[data-bs-target="${hash}"]`);
        if (tab) {
            const tabInstance = new bootstrap.Tab(tab);
            tabInstance.show();
        }
    }

    // 탭 변경 시 URL 해시 업데이트
    const tabEls = document.querySelectorAll('a[data-bs-toggle="tab"]');
    tabEls.forEach(tabEl => {
        tabEl.addEventListener('shown.bs.tab', function (e) {
            const target = e.target.getAttribute('data-bs-target');
            history.replaceState(null, null, target);
        });
    });
}

/**
 * 포맷팅 유틸리티 함수들
 */
const formatUtils = {
    /**
     * 번호 색상 클래스 반환
     * @param {number} num - 로또 번호 (1-45)
     * @returns {string} 색상 클래스
     */
    getBallColorClass: function(num) {
        if (num <= 10) return 'ball-yellow';
        if (num <= 20) return 'ball-blue';
        if (num <= 30) return 'ball-red';
        if (num <= 40) return 'ball-gray';
        return 'ball-green';
    },

    /**
     * 로또 번호 HTML 생성
     * @param {number} num - 로또 번호
     * @param {boolean} isBonus - 보너스 번호 여부
     * @returns {string} HTML 문자열
     */
    createBallHtml: function(num, isBonus = false) {
        const colorClass = this.getBallColorClass(num);
        const bonusClass = isBonus ? 'bonus' : '';
        return `<div class="ball ${colorClass} ${bonusClass}">${num}</div>`;
    },

    /**
     * 로또 번호 HTML 생성 (배열)
     * @param {Array} numbers - 로또 번호 배열
     * @param {number} bonus - 보너스 번호
     * @returns {string} HTML 문자열
     */
    createBallsHtml: function(numbers, bonus = null) {
        let html = '';

        // 일반 번호 6개
        numbers.forEach(num => {
            html += this.createBallHtml(num);
        });

        // 보너스 번호
        if (bonus !== null) {
            html += this.createBallHtml(bonus, true);
        }

        return html;
    },

    /**
     * 숫자 천단위 쉼표 포맷
     * @param {number} num - 포맷할 숫자
     * @returns {string} 포맷된 문자열
     */
    formatNumber: function(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    },

    /**
     * 날짜 포맷
     * @param {string} dateStr - 날짜 문자열 (ISO 형식)
     * @returns {string} 포맷된 날짜
     */
    formatDate: function(dateStr) {
        if (!dateStr) return '';

        const date = new Date(dateStr);
        return date.toLocaleDateString('ko-KR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
};

// 전역 변수로 노출
window.formatUtils = formatUtils;
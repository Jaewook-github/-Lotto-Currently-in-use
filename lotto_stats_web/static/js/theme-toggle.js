/**
 * theme-toggle.js - 테마 전환 모듈
 * 라이트/다크 모드 전환 및 테마 관리를 담당합니다.
 */

// 즉시 실행 함수를 통한 모듈 패턴 구현
const ThemeManager = (function() {
    // 테마 타입 정의
    const THEMES = {
        LIGHT: 'light',
        DARK: 'dark',
        HIGH_CONTRAST: 'high-contrast'
    };

    // 기본 테마
    const DEFAULT_THEME = THEMES.LIGHT;

    // 로컬 스토리지 키
    const STORAGE_KEY = 'lotto-stats-theme';

    // DOM 요소
    let themeToggleBtn;
    let themeDropdownItems;

    /**
     * 현재 테마 가져오기
     * @returns {string} 현재 테마
     */
    function getCurrentTheme() {
        return localStorage.getItem(STORAGE_KEY) || DEFAULT_THEME;
    }

    /**
     * 테마 설정 적용
     * @param {string} theme - 적용할 테마
     */
    function applyTheme(theme) {
        // body 클래스 설정
        document.body.classList.remove('dark-mode', 'high-contrast');

        if (theme === THEMES.DARK) {
            document.body.classList.add('dark-mode');
        } else if (theme === THEMES.HIGH_CONTRAST) {
            document.body.classList.add('high-contrast');
        }

        // 테마 아이콘 업데이트
        updateThemeIcon(theme);

        // 로컬 스토리지에 저장
        localStorage.setItem(STORAGE_KEY, theme);

        // 커스텀 이벤트 발생
        document.dispatchEvent(new CustomEvent('themeChange', { detail: { theme } }));
    }

    /**
     * 테마 아이콘 업데이트
     * @param {string} theme - 현재 테마
     */
    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;

        // 아이콘 설정
        if (theme === THEMES.DARK) {
            themeToggleBtn.innerHTML = '<i class="fas fa-sun"></i>';
            themeToggleBtn.setAttribute('title', '라이트 모드로 전환');
            themeToggleBtn.setAttribute('aria-label', '라이트 모드로 전환');
        } else if (theme === THEMES.HIGH_CONTRAST) {
            themeToggleBtn.innerHTML = '<i class="fas fa-adjust"></i>';
            themeToggleBtn.setAttribute('title', '라이트 모드로 전환');
            themeToggleBtn.setAttribute('aria-label', '라이트 모드로 전환');
        } else {
            themeToggleBtn.innerHTML = '<i class="fas fa-moon"></i>';
            themeToggleBtn.setAttribute('title', '다크 모드로 전환');
            themeToggleBtn.setAttribute('aria-label', '다크 모드로 전환');
        }
    }

    /**
     * 다음 테마로 순환
     */
    function cycleTheme() {
        const currentTheme = getCurrentTheme();

        // 순환 순서: 라이트 -> 다크 -> 고대비 -> 라이트
        if (currentTheme === THEMES.LIGHT) {
            applyTheme(THEMES.DARK);
        } else if (currentTheme === THEMES.DARK) {
            applyTheme(THEMES.HIGH_CONTRAST);
        } else {
            applyTheme(THEMES.LIGHT);
        }
    }

    /**
     * 이벤트 리스너 설정
     */
    function setupEventListeners() {
        // 테마 토글 버튼
        themeToggleBtn = document.getElementById('themeToggle');
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', cycleTheme);
        }

        // 테마 드롭다운 메뉴 (있는 경우)
        themeDropdownItems = document.querySelectorAll('[data-theme]');
        themeDropdownItems.forEach(item => {
            item.addEventListener('click', (e) => {
                const theme = e.currentTarget.getAttribute('data-theme');
                if (theme) {
                    applyTheme(theme);
                }
            });
        });

        // 미디어 쿼리 리스너 (시스템 테마 변경 감지)
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        darkModeMediaQuery.addEventListener('change', (e) => {
            // 사용자가 테마를 직접 선택하지 않은 경우에만 시스템 테마 적용
            if (!localStorage.getItem(STORAGE_KEY)) {
                applyTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
            }
        });
    }

    /**
     * 초기화
     */
    function init() {
        // 시스템 테마 확인
        const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const preferredTheme = prefersDarkMode ? THEMES.DARK : THEMES.LIGHT;

        // 저장된 테마 또는 시스템 테마 적용
        const savedTheme = localStorage.getItem(STORAGE_KEY);
        applyTheme(savedTheme || preferredTheme);

        // 이벤트 리스너 설정
        setupEventListeners();
    }

    // 공개 API
    return {
        init,
        applyTheme,
        getCurrentTheme,
        THEMES
    };
})();

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', ThemeManager.init);

// 전역 객체에 등록
window.ThemeManager = ThemeManager;
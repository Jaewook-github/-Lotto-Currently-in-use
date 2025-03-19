/**
 * 행운 드림 로또 웹 서비스 - 탭 제어 스크립트
 * 탭 전환 및 관련 기능을 처리합니다.
 */

document.addEventListener('DOMContentLoaded', function() {
    // 사이드바 메뉴 탭 전환
    const menuItems = document.querySelectorAll('.menu-items li');
    const tabContents = document.querySelectorAll('.tab-content');

    // URL 해시에서 탭 정보 가져오기
    const getTabFromHash = () => {
        const hash = window.location.hash.substring(1);
        return hash || 'main'; // 기본값은 'main'
    };

    // 탭 활성화 함수
    const activateTab = (tabId) => {
        // 메뉴 아이템 활성화
        menuItems.forEach(item => {
            if (item.getAttribute('data-tab') === tabId) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // 탭 컨텐츠 활성화
        tabContents.forEach(tab => {
            if (tab.id === tabId) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // URL 해시 업데이트
        window.location.hash = tabId;
    };

    // 초기 탭 설정
    activateTab(getTabFromHash());

    // 메뉴 아이템 클릭 이벤트
    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            activateTab(tabId);
        });
    });

    // 해시 변경 감지
    window.addEventListener('hashchange', function() {
        activateTab(getTabFromHash());
    });

    // 외부 링크에서 특정 탭으로 이동
    const handleExternalTabLinks = () => {
        const tabLinks = document.querySelectorAll('[data-tab-link]');

        tabLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const tabId = this.getAttribute('data-tab-link');
                activateTab(tabId);
            });
        });
    };

    handleExternalTabLinks();
});
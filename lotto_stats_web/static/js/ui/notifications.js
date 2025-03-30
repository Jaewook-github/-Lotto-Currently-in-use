/**
 * notifications.js - 알림 관리 모듈
 * 애플리케이션 사용자 알림을 관리합니다.
 */

const NotificationManager = (function() {
    // 알림 컨테이너 요소
    let notificationContainer;

    // 알림 카운터 (고유 ID 생성용)
    let notificationCounter = 0;

    // 알림 타입 정의
    const NOTIFICATION_TYPES = {
        SUCCESS: 'success',
        ERROR: 'error',
        WARNING: 'warning',
        INFO: 'info'
    };

    // 알림 기본 설정
    const DEFAULT_OPTIONS = {
        type: NOTIFICATION_TYPES.INFO,
        duration: 5000, // 5초
        closable: true,
        animationDuration: 300 // 밀리초
    };

    /**
     * 알림 컨테이너 요소 가져오기
     * @returns {HTMLElement} 알림 컨테이너
     */
    function getContainer() {
        if (!notificationContainer) {
            notificationContainer = document.getElementById('alertContainer');

            // 컨테이너가 없으면 동적으로 생성
            if (!notificationContainer) {
                notificationContainer = document.createElement('div');
                notificationContainer.id = 'alertContainer';
                notificationContainer.className = 'alert-container';
                document.body.appendChild(notificationContainer);
            }
        }

        return notificationContainer;
    }

    /**
     * 알림 요소 생성
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {HTMLElement} 알림 요소
     */
    function createNotificationElement(title, message, options) {
        const notificationId = `notification-${++notificationCounter}`;
        const alertType = options.type;

        // 알림 요소 생성
        const alertItem = document.createElement('div');
        alertItem.id = notificationId;
        alertItem.className = `alert alert-${alertType} alert-item`;
        alertItem.setAttribute('role', 'alert');

        // 알림 내용 생성
        let iconClass = '';
        switch (alertType) {
            case NOTIFICATION_TYPES.SUCCESS:
                iconClass = 'fa-check-circle';
                break;
            case NOTIFICATION_TYPES.ERROR:
                iconClass = 'fa-times-circle';
                break;
            case NOTIFICATION_TYPES.WARNING:
                iconClass = 'fa-exclamation-triangle';
                break;
            default:
                iconClass = 'fa-info-circle';
                break;
        }

        // 알림 내용 구성
        alertItem.innerHTML = `
            <div class="d-flex">
                <div class="me-3">
                    <i class="fas ${iconClass} fa-lg"></i>
                </div>
                <div class="flex-grow-1">
                    ${title ? `<div class="alert-heading">${title}</div>` : ''}
                    <div class="alert-message">${message}</div>
                </div>
                ${options.closable ? `
                <div>
                    <button type="button" class="btn-close" aria-label="닫기"></button>
                </div>` : ''}
            </div>
        `;

        // 닫기 버튼 이벤트 리스너
        if (options.closable) {
            const closeButton = alertItem.querySelector('.btn-close');
            closeButton.addEventListener('click', () => {
                removeNotification(notificationId);
            });
        }

        return alertItem;
    }

    /**
     * 알림 제거
     * @param {string} id - 알림 요소 ID
     */
    function removeNotification(id) {
        const alertItem = document.getElementById(id);
        if (!alertItem) return;

        // 페이드 아웃 애니메이션
        alertItem.style.transition = `opacity ${DEFAULT_OPTIONS.animationDuration}ms ease`;
        alertItem.style.opacity = '0';

        // 애니메이션 완료 후 제거
        setTimeout(() => {
            alertItem.remove();
        }, DEFAULT_OPTIONS.animationDuration);
    }

    /**
     * 알림 표시
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {string} 알림 ID
     */
    function showNotification(title, message, options = {}) {
        // 옵션 병합
        const mergedOptions = { ...DEFAULT_OPTIONS, ...options };

        // 제목과 메시지 처리
        if (typeof title !== 'string' && typeof message !== 'string') {
            message = '알림';
            title = '';
        } else if (typeof title === 'string' && typeof message !== 'string') {
            message = title;
            title = '';
        }

        // 알림 요소 생성
        const alertItem = createNotificationElement(title, message, mergedOptions);
        const notificationId = alertItem.id;

        // 알림 컨테이너에 추가
        const container = getContainer();
        container.appendChild(alertItem);

        // 초기 스타일 설정 (애니메이션용)
        alertItem.style.opacity = '0';

        // 트릭: 포커스를 알림에 주기 전에 레이아웃 강제 계산
        void alertItem.offsetWidth;

        // 페이드 인 애니메이션
        alertItem.style.transition = `opacity ${DEFAULT_OPTIONS.animationDuration}ms ease`;
        alertItem.style.opacity = '1';

        // 자동 제거 설정
        if (mergedOptions.duration > 0) {
            setTimeout(() => {
                removeNotification(notificationId);
            }, mergedOptions.duration);
        }

        return notificationId;
    }

    /**
     * 성공 알림
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {string} 알림 ID
     */
    function showSuccess(title, message, options = {}) {
        return showNotification(title, message, {
            ...options,
            type: NOTIFICATION_TYPES.SUCCESS
        });
    }

    /**
     * 오류 알림
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {string} 알림 ID
     */
    function showError(title, message, options = {}) {
        return showNotification(title, message, {
            ...options,
            type: NOTIFICATION_TYPES.ERROR
        });
    }

    /**
     * 경고 알림
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {string} 알림 ID
     */
    function showWarning(title, message, options = {}) {
        return showNotification(title, message, {
            ...options,
            type: NOTIFICATION_TYPES.WARNING
        });
    }

    /**
     * 정보 알림
     * @param {string} title - 알림 제목
     * @param {string} message - 알림 메시지
     * @param {Object} options - 알림 옵션
     * @returns {string} 알림 ID
     */
    function showInfo(title, message, options = {}) {
        return showNotification(title, message, {
            ...options,
            type: NOTIFICATION_TYPES.INFO
        });
    }

    /**
     * 모든 알림 제거
     */
    function clearAll() {
        const container = getContainer();
        const notifications = container.querySelectorAll('.alert-item');

        notifications.forEach(alertItem => {
            removeNotification(alertItem.id);
        });
    }

    // 공개 API
    return {
        showNotification,
        showSuccess,
        showError,
        showWarning,
        showInfo,
        removeNotification,
        clearAll,
        TYPES: NOTIFICATION_TYPES
    };
})();

// 전역 함수로 등록
window.showNotification = NotificationManager.showNotification;
window.showSuccess = NotificationManager.showSuccess;
window.showError = NotificationManager.showError;
window.showWarning = NotificationManager.showWarning;
window.showInfo = NotificationManager.showInfo;
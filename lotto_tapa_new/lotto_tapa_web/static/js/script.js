// DOM이 로드된 후 실행
document.addEventListener('DOMContentLoaded', function() {
    // 다크 모드 토글
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    // 로컬 스토리지에서 테마 설정 가져오기
    const isDarkMode = localStorage.getItem('darkMode') === 'true';

    // 초기 테마 설정
    if (isDarkMode) {
        body.classList.add('dark-mode');
        themeToggle.innerHTML = '<i class="fa-solid fa-sun"></i>';
    }

    // 테마 전환 이벤트
    themeToggle.addEventListener('click', function() {
        body.classList.toggle('dark-mode');
        const isDark = body.classList.contains('dark-mode');

        // 아이콘 변경
        themeToggle.innerHTML = isDark ?
            '<i class="fa-solid fa-sun"></i>' :
            '<i class="fa-solid fa-moon"></i>';

        // 로컬 스토리지에 설정 저장
        localStorage.setItem('darkMode', isDark);

        // 차트 새로고침 (테마 변경 시 차트 색상도 업데이트)
        setTimeout(() => {
            window.location.reload();
        }, 300);
    });

    // 사이드바 메뉴 탭 전환
    const menuItems = document.querySelectorAll('.menu-items li');
    const tabContents = document.querySelectorAll('.tab-content');

    menuItems.forEach(item => {
        item.addEventListener('click', function() {
            // 활성 메뉴 아이템 업데이트
            menuItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');

            // 탭 컨텐츠 업데이트
            const tabId = this.getAttribute('data-tab');
            tabContents.forEach(tab => tab.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
        });
    });

    // 모달 관련 함수
    const showAlert = (title, message) => {
        const modalTitle = document.getElementById('alertModalTitle');
        const modalBody = document.getElementById('alertModalBody');

        modalTitle.textContent = title;
        modalBody.textContent = message;

        const modal = new bootstrap.Modal(document.getElementById('alertModal'));
        modal.show();
    };

    // 전체 선택/해제 체크박스 이벤트
    const allRulesCheckbox = document.getElementById('allRules');
    const ruleCheckboxes = document.querySelectorAll('.rule-checkbox');

    if(allRulesCheckbox) {
        allRulesCheckbox.addEventListener('change', function() {
            ruleCheckboxes.forEach(checkbox => {
                checkbox.checked = allRulesCheckbox.checked;
            });
        });
    }

    // 개별 규칙 체크박스 이벤트 - 전체 선택 상태 업데이트
    ruleCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if(allRulesCheckbox) {
                const allChecked = Array.from(ruleCheckboxes).every(cb => cb.checked);
                allRulesCheckbox.checked = allChecked;
            }
        });
    });

    // 번호 생성 폼 제출 이벤트
    const generateForm = document.getElementById('generateForm');

    if(generateForm) {
        const resultContainer = document.getElementById('resultContainer');
        const generationTime = document.getElementById('generationTime');

        generateForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 로딩 상태 표시
            resultContainer.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">로딩 중...</span>
                    </div>
                    <p class="mt-3">번호 생성 중...</p>
                </div>
            `;

            // 폼 데이터 수집
            const formData = new FormData(generateForm);

            // 현재 활성화된 규칙 상태 추가
            ruleCheckboxes.forEach(checkbox => {
                formData.append(checkbox.name, checkbox.checked ? 'true' : 'false');
            });

            // 서버에 번호 생성 요청
            fetch('/generate', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 결과 표시
                    resultContainer.innerHTML = '';
                    generationTime.textContent = `생성 시간: ${data.timestamp}`;

                    if (data.numbers.length === 0) {
                        resultContainer.innerHTML = `
                            <div class="alert alert-warning text-center">
                                <i class="fa-solid fa-exclamation-triangle me-2"></i>
                                선택한 조건에 맞는 번호를 찾을 수 없습니다.<br>조건을 완화해주세요.
                            </div>
                        `;
                    } else {
                        // 생성된 번호들 표시
                        data.numbers.forEach((nums, i) => {
                            const gameDiv = document.createElement('div');
                            gameDiv.className = 'game-row';

                            // 번호 볼 생성
                            const ballsHtml = nums.map(num => {
                                let colorClass = '';

                                // 번호에 따른 색상 지정
                                if (num <= 10) colorClass = 'ball-yellow';
                                else if (num <= 20) colorClass = 'ball-blue';
                                else if (num <= 30) colorClass = 'ball-red';
                                else if (num <= 40) colorClass = 'ball-gray';
                                else colorClass = 'ball-green';

                                return `<div class="number-ball ${colorClass}">${num}</div>`;
                            }).join('');

                            gameDiv.innerHTML = `
                                <div class="game-info">${i+1}게임</div>
                                <div class="game-balls">${ballsHtml}</div>
                            `;
                            resultContainer.appendChild(gameDiv);
                        });
                    }
                } else {
                    showAlert('오류', data.error || '번호 생성 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                showAlert('오류', '서버 통신 중 오류가 발생했습니다.');
                console.error('Error:', error);
            });
        });
    }

    // 규칙 설정 폼 제출 이벤트
    const rulesForm = document.getElementById('rulesForm');

    if(rulesForm) {
        rulesForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 폼 데이터 수집
            const formData = new FormData();

            // 규칙 체크박스 상태 추가
            ruleCheckboxes.forEach(checkbox => {
                formData.append(checkbox.name, checkbox.checked ? 'true' : 'false');
            });

            // 서버에 설정 업데이트 요청
            fetch('/update-config', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('성공', '규칙 설정이 저장되었습니다.');
                } else {
                    showAlert('오류', data.error || '설정 저장 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                showAlert('오류', '서버 통신 중 오류가 발생했습니다.');
                console.error('Error:', error);
            });
        });
    }

    // 상세 설정 폼 제출 이벤트
    const settingsForm = document.getElementById('settingsForm');

    if(settingsForm) {
        settingsForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // 폼 데이터 수집
            const formData = new FormData(settingsForm);

            // 추가로 규칙 활성화 상태 포함
            ruleCheckboxes.forEach(checkbox => {
                formData.append(checkbox.name, checkbox.checked ? 'true' : 'false');
            });

            // 서버에 설정 업데이트 요청
            fetch('/update-config', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('성공', '상세 설정이 저장되었습니다.');
                } else {
                    showAlert('오류', data.error || '설정 저장 중 오류가 발생했습니다.');
                }
            })
            .catch(error => {
                showAlert('오류', '서버 통신 중 오류가 발생했습니다.');
                console.error('Error:', error);
            });
        });
    }

    // 설정 초기화 버튼 이벤트
    const resetConfigButton = document.getElementById('resetConfig');

    if(resetConfigButton) {
        resetConfigButton.addEventListener('click', function() {
            if (confirm('모든 설정을 기본값으로 되돌리시겠습니까?')) {
                fetch('/reset-config', {
                    method: 'POST'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showAlert('성공', '설정이 기본값으로 초기화되었습니다.');

                        // 페이지 새로고침하여 초기화된 값 표시
                        setTimeout(() => {
                            location.reload();
                        }, 1000);
                    } else {
                        showAlert('오류', data.error || '설정 초기화 중 오류가 발생했습니다.');
                    }
                })
                .catch(error => {
                    showAlert('오류', '서버 통신 중 오류가 발생했습니다.');
                    console.error('Error:', error);
                });
            }
        });
    }

    // 연속번호 체크박스 최소 1개 이상 선택 처리
    const consecutiveCheckboxes = document.querySelectorAll('input[name="consecutive"]');

    if(consecutiveCheckboxes.length > 0) {
        consecutiveCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                // 최소 1개 이상 선택되어 있는지 확인
                const anyChecked = Array.from(consecutiveCheckboxes).some(cb => cb.checked);

                // 아무것도 선택되지 않았다면 현재 체크박스 다시 선택
                if (!anyChecked) {
                    this.checked = true;
                    showAlert('알림', '연속번호 옵션은 최소 1개 이상 선택해야 합니다.');
                }
            });
        });
    }

    // 입력 범위 유효성 검사 공통 함수
    const validateRange = (minInput, maxInput, fieldName) => {
        const min = parseInt(minInput.value);
        const max = parseInt(maxInput.value);

        if (min > max) {
            showAlert('경고', `${fieldName}의 최소값이 최대값보다 큽니다. 유효한 범위를 입력해주세요.`);
            return false;
        }

        return true;
    };

    // 모든 범위 입력 필드에 대한 유효성 검사 추가
    if(settingsForm) {
        const rangeValidations = [
            { min: 'sumMin', max: 'sumMax', name: '총합 구간' },
            { min: 'primeMin', max: 'primeMax', name: '소수 개수' },
            { min: 'compositeMin', max: 'compositeMax', name: '합성수 개수' },
            { min: 'lastDigitMin', max: 'lastDigitMax', name: '끝수 총합 구간' },
            { min: 'mult3Min', max: 'mult3Max', name: '3의 배수 개수' },
            { min: 'mult5Min', max: 'mult5Max', name: '5의 배수 개수' },
            { min: 'squareMin', max: 'squareMax', name: '제곱수 개수' },
            { min: 'twinMin', max: 'twinMax', name: '쌍수 개수' },
            { min: 'cornerMin', max: 'cornerMax', name: '모서리 숫자 개수' }
        ];

        // 설정 폼 제출 전 유효성 검사
        settingsForm.addEventListener('submit', function(e) {
            for (const validation of rangeValidations) {
                const minInput = document.getElementById(validation.min);
                const maxInput = document.getElementById(validation.max);

                if (minInput && maxInput && !validateRange(minInput, maxInput, validation.name)) {
                    e.preventDefault();
                    return false;
                }
            }
        });
    }

    // CSS 애니메이션 클래스 추가
    const addAnimationToElement = () => {
        const elements = document.querySelectorAll('.card, .number-ball, .stat-item, .rule-item, .setting-section');

        elements.forEach((element, index) => {
            setTimeout(() => {
                element.classList.add('fade-in');
            }, index * 50);
        });
    };

    // 페이지 로드 시 애니메이션 적용
    addAnimationToElement();

    // 결과 항목 애니메이션 효과
    const applyResultAnimation = () => {
        const gameRows = document.querySelectorAll('.game-row');

        gameRows.forEach((row, index) => {
            setTimeout(() => {
                row.classList.add('fade-in-up');
            }, index * 100);
        });
    };

    // MutationObserver로 결과 컨테이너 변경 감지
    const resultContainer = document.getElementById('resultContainer');
    if(resultContainer) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    applyResultAnimation();
                }
            });
        });

        observer.observe(resultContainer, { childList: true });
    }

    // 게임 번호 생성 후 스크롤 애니메이션
    const scrollToResult = () => {
        const resultSection = document.querySelector('.result-container');
        if(resultSection) {
            resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    };

    if(generateForm) {
        generateForm.addEventListener('submit', () => {
            setTimeout(scrollToResult, 1000);
        });
    }

    // 반응형 사이드바 제어
    const handleResponsiveSidebar = () => {
        const sideMenu = document.querySelector('.side-menu');
        const mainContent = document.querySelector('.main-content');

        if (window.innerWidth <= 768) {
            mainContent.style.marginLeft = '0';
            sideMenu.classList.add('collapsed');
        } else {
            mainContent.style.marginLeft = sideMenu.classList.contains('collapsed') ? '70px' : '240px';
        }
    };

    // 초기 로드 및 화면 크기 변경 시 실행
    window.addEventListener('resize', handleResponsiveSidebar);
    handleResponsiveSidebar();

    // 게임 결과 애니메이션 스타일 추가
    const styleSheet = document.createElement('style');
    styleSheet.textContent = `
        @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .fade-in {
            animation: fade-in 0.5s ease forwards;
        }

        .fade-in-up {
            animation: fade-in-up 0.5s ease forwards;
        }

        .game-row {
            display: flex;
            align-items: center;
            padding: 10px 0;
            opacity: 0;
        }

        .game-info {
            flex: 0 0 60px;
            font-weight: 600;
        }

        .game-balls {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
    `;
    document.head.appendChild(styleSheet);
});
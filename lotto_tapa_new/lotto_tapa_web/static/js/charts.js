// 차트 설정 및 생성 스크립트
document.addEventListener('DOMContentLoaded', function() {
    // 색상 설정
    const colors = {
        primary: '#4158D0',
        secondary: '#3f51b5',
        accent: '#C850C0',
        yellow: '#ffc107',
        blue: '#2196f3',
        red: '#f44336',
        gray: '#757575',
        green: '#4caf50',
        gradient: ['rgba(65, 88, 208, 0.8)', 'rgba(200, 80, 192, 0.8)', 'rgba(255, 204, 112, 0.8)']
    };

    // 공통 차트 설정
    Chart.defaults.font.family = "'Noto Sans KR', sans-serif";
    Chart.defaults.color = '#666';
    Chart.defaults.borderColor = 'rgba(0, 0, 0, 0.05)';

    // 다크 모드 감지 및 적용
    const isDarkMode = document.body.classList.contains('dark-mode');
    if (isDarkMode) {
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.1)';
    }

    // 미니 번호 출현 빈도 차트
    if (document.getElementById('numberFrequencyChart')) {
        const ctx = document.getElementById('numberFrequencyChart').getContext('2d');

        // 샘플 데이터 (실제 서비스 구현 시 서버에서 가져온 데이터 사용)
        const labels = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45];
        const data = [28, 32, 22, 30, 35, 42, 38, 33, 29, 25];

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: '출현 빈도',
                    data: data,
                    backgroundColor: function(context) {
                        const index = context.dataIndex;
                        const value = labels[index];

                        if (value <= 10) return colors.yellow;
                        else if (value <= 20) return colors.blue;
                        else if (value <= 30) return colors.red;
                        else if (value <= 40) return colors.gray;
                        else return colors.green;
                    },
                    borderRadius: 4
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
                            title: function(tooltipItems) {
                                return `번호 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            display: false
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // 홀짝 비율 차트
    if (document.getElementById('oddEvenChart')) {
        const ctx = document.getElementById('oddEvenChart').getContext('2d');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['홀수', '짝수'],
                datasets: [{
                    data: [52, 48],
                    backgroundColor: [colors.primary, colors.accent],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            boxWidth: 12,
                            padding: 15
                        }
                    }
                }
            }
        });
    }

    // 전체 번호 분포 차트
    if (document.getElementById('numberDistributionChart')) {
        const ctx = document.getElementById('numberDistributionChart').getContext('2d');

        // 번호별 당첨 횟수 데이터 (샘플)
        const numberFrequency = Array.from({length: 45}, (_, i) => {
            return {
                number: i + 1,
                count: Math.floor(Math.random() * 50) + 20
            };
        });

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: numberFrequency.map(item => item.number),
                datasets: [{
                    label: '당첨 횟수',
                    data: numberFrequency.map(item => item.count),
                    backgroundColor: function(context) {
                        const index = context.dataIndex;
                        const value = index + 1;

                        if (value <= 10) return colors.yellow;
                        else if (value <= 20) return colors.blue;
                        else if (value <= 30) return colors.red;
                        else if (value <= 40) return colors.gray;
                        else return colors.green;
                    },
                    borderWidth: 0,
                    barPercentage: 0.9,
                    categoryPercentage: 1
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
                            title: function(tooltipItems) {
                                return `번호 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 20,
                            callback: function(val, index) {
                                return index % 5 === 0 ? this.getLabelForValue(val) : '';
                            }
                        }
                    }
                }
            }
        });
    }

    // 홀짝 비율 분포 차트 (통계 탭)
    if (document.getElementById('oddEvenDistChart')) {
        const ctx = document.getElementById('oddEvenDistChart').getContext('2d');

        const data = {
            labels: ['0:6', '1:5', '2:4', '3:3', '4:2', '5:1', '6:0'],
            datasets: [{
                label: '당첨 횟수',
                data: [8, 52, 138, 364, 142, 50, 6],
                backgroundColor: function(context) {
                    const value = context.dataIndex;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, colors.gradient[0]);
                    gradient.addColorStop(0.5, colors.gradient[1]);
                    gradient.addColorStop(1, colors.gradient[2]);

                    if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)'; // 제외 비율
                    if (value === 3) return gradient; // 가장 빈번한 비율
                    return 'rgba(65, 88, 208, 0.7)';
                },
                borderRadius: 4
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `홀짝 비율 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 고저 비율 분포 차트
    if (document.getElementById('highLowDistChart')) {
        const ctx = document.getElementById('highLowDistChart').getContext('2d');

        const data = {
            labels: ['0:6', '1:5', '2:4', '3:3', '4:2', '5:1', '6:0'],
            datasets: [{
                label: '당첨 횟수',
                data: [6, 48, 130, 382, 150, 46, 5],
                backgroundColor: function(context) {
                    const value = context.dataIndex;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, 'rgba(200, 80, 192, 0.7)');
                    gradient.addColorStop(1, 'rgba(65, 88, 208, 0.7)');

                    if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                    if (value === 3) return gradient;
                    return 'rgba(200, 80, 192, 0.7)';
                },
                borderRadius: 4
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `고저 비율 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // AC값 분포 차트
    if (document.getElementById('acValueChart')) {
        const ctx = document.getElementById('acValueChart').getContext('2d');

        const data = {
            labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'],
            datasets: [{
                label: '당첨 횟수',
                data: [0, 2, 5, 12, 22, 38, 86, 168, 205, 150, 80, 28, 10, 3, 0],
                backgroundColor: function(context) {
                    const value = context.dataIndex;

                    if (value < 6) return 'rgba(220, 53, 69, 0.7)';

                    const gradient = ctx.createLinearGradient(0, 0, 0, 200);
                    gradient.addColorStop(0, 'rgba(76, 175, 80, 0.7)');
                    gradient.addColorStop(1, 'rgba(33, 150, 243, 0.7)');
                    return gradient;
                },
                borderRadius: 4
            }]
        };

        new Chart(ctx, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            title: function(tooltipItems) {
                                return `AC값 ${tooltipItems[0].label}`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // 총합 추이 차트
    if (document.getElementById('sumTrendChart')) {
        const ctx = document.getElementById('sumTrendChart').getContext('2d');

        // 최근 15회 당첨번호 총합 (샘플)
        const recentSums = [135, 148, 142, 155, 129, 131, 140, 152, 139, 146, 150, 138, 147, 136, 143];

        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(65, 88, 208, 0.8)');
        gradient.addColorStop(1, 'rgba(65, 88, 208, 0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array.from({length: 15}, (_, i) => `${1000 - 14 + i}회`),
                datasets: [{
                    label: '총합',
                    data: recentSums,
                    borderColor: colors.primary,
                    backgroundColor: gradient,
                    borderWidth: 2,
                    pointBackgroundColor: colors.accent,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    annotation: {
                        annotations: {
                            line1: {
                                type: 'line',
                                yMin: 100,
                                yMax: 100,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            },
                            line2: {
                                type: 'line',
                                yMin: 175,
                                yMax: 175,
                                borderColor: 'rgba(220, 53, 69, 0.5)',
                                borderWidth: 1,
                                borderDash: [5, 5]
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        min: 90,
                        max: 185,
                        ticks: {
                            stepSize: 15
                        }
                    }
                }
            }
        });
    }

    // 도움말 - 총합 구간 차트
    if (document.getElementById('sumRangeHelpChart')) {
        const ctx = document.getElementById('sumRangeHelpChart').getContext('2d');

        const data = [0, 2, 4, 8, 15, 25, 38, 50, 65, 78, 85, 90, 92, 88, 82, 73, 63, 50, 38, 25, 15, 8, 4, 1, 0];
        const labels = Array.from({length: 25}, (_, i) => (70 + i * 10).toString());

        const gradient = ctx.createLinearGradient(0, 0, 0, 150);
        gradient.addColorStop(0, 'rgba(65, 88, 208, 0.8)');
        gradient.addColorStop(1, 'rgba(65, 88, 208, 0)');

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: '출현 빈도',
                    data: data,
                    borderColor: colors.primary,
                    backgroundColor: gradient,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        display: false,
                        beginAtZero: true
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            autoSkip: true,
                            maxTicksLimit: 6
                        }
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    }
                }
            }
        });
    }

    // 도움말 - 홀짝 비율 차트
    if (document.getElementById('oddEvenHelpChart')) {
        const ctx = document.getElementById('oddEvenHelpChart').getContext('2d');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['홀0:짝6', '홀1:짝5', '홀2:짝4', '홀3:짝3', '홀4:짝2', '홀5:짝1', '홀6:짝0'],
                datasets: [{
                    label: '비율별 당첨 확률',
                    data: [1.3, 10.8, 28.5, 36.4, 15.2, 6.8, 1.0],
                    backgroundColor: function(context) {
                        const value = context.dataIndex;

                        if (value === 0 || value === 6) return 'rgba(220, 53, 69, 0.7)';
                        if (value === 3) return 'rgba(76, 175, 80, 0.7)';
                        return 'rgba(33, 150, 243, 0.7)';
                    },
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        display: false
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            font: {
                                size: 9
                            }
                        }
                    }
                }
            }
        });
    }
});
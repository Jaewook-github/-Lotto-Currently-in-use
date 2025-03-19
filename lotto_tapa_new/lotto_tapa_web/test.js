import React, { useState } from 'react';
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from 'recharts';

const LotteryDashboard = () => {
  const [timeRange, setTimeRange] = useState('전체 회차');
  const [selectedTab, setSelectedTab] = useState('분포 패턴');

  // 색상 팔레트 정의
  const colors = {
    primary: '#3062D4',
    secondary: '#3AB2CF',
    tertiary: '#FF7D74',
    quaternary: '#FF9A73',
    accent: '#FFD96B',
    neutral: '#596780',
    neutralLight: '#BBC4D1',
    success: '#5BBF8C',
    warning: '#F2A03F',
    error: '#E15F56',
    background: '#F5F7FA',
    chartColors: ['#3062D4', '#3AB2CF', '#5BBF8C', '#FFD96B', '#FF9A73', '#E15F56'],
    gradientBlue: ['#3062D4', '#3AB2CF'],
    gradientWarm: ['#FF7D74', '#FFD96B']
  };

  // === 시간별 데이터 ===
  const timeRangeData = {
    // 고저비율 데이터
    highLowRatio: {
      '전체 회차': [
        { name: '0:6', value: 1.2 },
        { name: '1:5', value: 5.4 },
        { name: '2:4', value: 23 },
        { name: '3:3', value: 32 },
        { name: '4:2', value: 23 },
        { name: '5:1', value: 4.2 },
        { name: '6:0', value: 1.2 }
      ],
      '최근 100회차': [
        { name: '0:6', value: 1.0 },
        { name: '1:5', value: 4.0 },
        { name: '2:4', value: 25 },
        { name: '3:3', value: 35 },
        { name: '4:2', value: 29 },
        { name: '5:1', value: 5.0 },
        { name: '6:0', value: 1.0 }
      ],
      '최근 50회차': [
        { name: '0:6', value: 0.0 },
        { name: '1:5', value: 4.0 },
        { name: '2:4', value: 22 },
        { name: '3:3', value: 30 },
        { name: '4:2', value: 34 },
        { name: '5:1', value: 10 },
        { name: '6:0', value: 0.0 }
      ]
    },
    // 홀짝비율 데이터
    oddEvenRatio: {
      '전체 회차': [
        { name: '0:6', value: 1.5 },
        { name: '1:5', value: 5.0 },
        { name: '2:4', value: 22 },
        { name: '3:3', value: 33 },
        { name: '4:2', value: 25 },
        { name: '5:1', value: 5.0 },
        { name: '6:0', value: 1.5 }
      ],
      '최근 100회차': [
        { name: '0:6', value: 1.0 },
        { name: '1:5', value: 4.0 },
        { name: '2:4', value: 20 },
        { name: '3:3', value: 37 },
        { name: '4:2', value: 30 },
        { name: '5:1', value: 7.0 },
        { name: '6:0', value: 1.0 }
      ],
      '최근 50회차': [
        { name: '0:6', value: 0.0 },
        { name: '1:5', value: 4.0 },
        { name: '2:4', value: 18 },
        { name: '3:3', value: 32 },
        { name: '4:2', value: 36 },
        { name: '5:1', value: 10 },
        { name: '6:0', value: 0.0 }
      ]
    },
    // 총합구간 데이터
    sumRange: {
      '전체 회차': [
        { name: '<80', value: 2.3 },
        { name: '80-100', value: 7.7 },
        { name: '100-115', value: 13.3 },
        { name: '115-130', value: 20.5 },
        { name: '130-155', value: 27.5 },
        { name: '155-190', value: 18.4 },
        { name: '>190', value: 10.3 }
      ],
      '최근 100회차': [
        { name: '<80', value: 1.0 },
        { name: '80-100', value: 6.0 },
        { name: '100-115', value: 10.0 },
        { name: '115-130', value: 18.0 },
        { name: '130-155', value: 28.0 },
        { name: '155-190', value: 28.0 },
        { name: '>190', value: 9.0 }
      ],
      '최근 50회차': [
        { name: '<80', value: 0.0 },
        { name: '80-100', value: 4.0 },
        { name: '100-115', value: 8.0 },
        { name: '115-130', value: 16.0 },
        { name: '130-145', value: 20.0 },
        { name: '145-160', value: 32.0 },
        { name: '160-190', value: 18.0 },
        { name: '>190', value: 2.0 }
      ]
    },
    // 볼 색상 분포 데이터
    ballColors: {
      '전체 회차': [
        { name: '2가지', value: 4.5 },
        { name: '3가지', value: 36.1 },
        { name: '4가지', value: 51.3 },
        { name: '5가지', value: 8.1 }
      ],
      '최근 100회차': [
        { name: '2가지', value: 3.0 },
        { name: '3가지', value: 30.0 },
        { name: '4가지', value: 58.0 },
        { name: '5가지', value: 9.0 }
      ],
      '최근 50회차': [
        { name: '2가지', value: 2.0 },
        { name: '3가지', value: 24.0 },
        { name: '4가지', value: 62.0 },
        { name: '5가지', value: 12.0 }
      ]
    },
    // AC값 데이터
    acValues: {
      '전체 회차': [
        { name: '<6', value: 5.9 },
        { name: '6', value: 12.3 },
        { name: '7', value: 23.5 },
        { name: '8', value: 24.6 },
        { name: '9', value: 19.9 },
        { name: '>9', value: 13.8 }
      ],
      '최근 100회차': [
        { name: '<6', value: 4.0 },
        { name: '6', value: 9.0 },
        { name: '7', value: 20.0 },
        { name: '8', value: 33.0 },
        { name: '9', value: 19.0 },
        { name: '>9', value: 15.0 }
      ],
      '최근 50회차': [
        { name: '<6', value: 2.0 },
        { name: '6', value: 6.0 },
        { name: '7', value: 18.0 },
        { name: '8', value: 38.0 },
        { name: '9', value: 18.0 },
        { name: '>9', value: 18.0 }
      ]
    },
    // 연속 번호 패턴 데이터
    consecutiveNumbers: {
      '전체 회차': [
        { name: '무연속', value: 50.0 },
        { name: '2개 1쌍', value: 42.0 },
        { name: '2개 2쌍', value: 2.3 },
        { name: '3개+', value: 5.7 }
      ],
      '최근 100회차': [
        { name: '무연속', value: 44.0 },
        { name: '2개 1쌍', value: 47.0 },
        { name: '2개 2쌍', value: 3.0 },
        { name: '3개+', value: 6.0 }
      ],
      '최근 50회차': [
        { name: '무연속', value: 38.0 },
        { name: '2개 1쌍', value: 52.0 },
        { name: '2개 2쌍', value: 6.0 },
        { name: '3개+', value: 4.0 }
      ]
    },
    // 소수 분포 데이터
    primeNumbers: {
      '전체 회차': [
        { name: '0개', value: 2.3 },
        { name: '1개', value: 18.6 },
        { name: '2개', value: 35.0 },
        { name: '3개', value: 28.3 },
        { name: '4개+', value: 15.8 }
      ],
      '최근 100회차': [
        { name: '0개', value: 2.0 },
        { name: '1개', value: 15.0 },
        { name: '2개', value: 38.0 },
        { name: '3개', value: 30.0 },
        { name: '4개+', value: 15.0 }
      ],
      '최근 50회차': [
        { name: '0개', value: 2.0 },
        { name: '1개', value: 32.0 },
        { name: '2개', value: 44.0 },
        { name: '3개', value: 14.0 },
        { name: '4개+', value: 8.0 }
      ]
    },
    // 분산도 데이터
    dispersion: {
      '전체 회차': [
        { name: '<10', value: 5.2 },
        { name: '10-12', value: 15.6 },
        { name: '13-16', value: 49.3 },
        { name: '17-20', value: 22.5 },
        { name: '>20', value: 7.4 }
      ],
      '최근 100회차': [
        { name: '<10', value: 6.0 },
        { name: '10-12', value: 18.0 },
        { name: '12-15', value: 58.0 },
        { name: '15-18', value: 15.0 },
        { name: '>18', value: 3.0 }
      ],
      '최근 50회차': [
        { name: '<10', value: 8.0 },
        { name: '10-11', value: 16.0 },
        { name: '11-14', value: 64.0 },
        { name: '14-17', value: 10.0 },
        { name: '>17', value: 2.0 }
      ]
    },
    // 번호 간격 패턴 데이터
    numberGaps: {
      '전체 회차': [
        { name: '<6', value: 12.3 },
        { name: '6-7', value: 25.2 },
        { name: '7-9', value: 33.1 },
        { name: '9-12', value: 20.6 },
        { name: '>12', value: 8.8 }
      ],
      '최근 100회차': [
        { name: '<6', value: 18.0 },
        { name: '6-7', value: 28.0 },
        { name: '7-8', value: 30.0 },
        { name: '8-10', value: 20.0 },
        { name: '>10', value: 4.0 }
      ],
      '최근 50회차': [
        { name: '<5', value: 14.0 },
        { name: '5-6', value: 32.0 },
        { name: '6-7', value: 38.0 },
        { name: '7-9', value: 14.0 },
        { name: '>9', value: 2.0 }
      ]
    }
  };

  // 트렌드 추이 데이터
  const trendData = [
    { name: '전체 회차', 고저_3대3: 32, 고저_4대2: 23, 홀짝_3대3: 33, 홀짝_4대2: 25, AC_7_9: 68, 연속번호_2개1쌍: 42 },
    { name: '최근 100회차', 고저_3대3: 35, 고저_4대2: 29, 홀짝_3대3: 37, 홀짝_4대2: 30, AC_7_9: 72, 연속번호_2개1쌍: 47 },
    { name: '최근 50회차', 고저_3대3: 30, 고저_4대2: 34, 홀짝_3대3: 32, 홀짝_4대2: 36, AC_7_9: 74, 연속번호_2개1쌍: 52 }
  ];

  // 번호 분포 패턴 데이터
  const patternComparisonData = [
    { name: '고저 3:3', 전체회차: 32, 최근100회차: 35, 최근50회차: 30 },
    { name: '고저 4:2', 전체회차: 23, 최근100회차: 29, 최근50회차: 34 },
    { name: '홀짝 3:3', 전체회차: 33, 최근100회차: 37, 최근50회차: 32 },
    { name: '홀짝 4:2', 전체회차: 25, 최근100회차: 30, 최근50회차: 36 },
    { name: '색상 4가지', 전체회차: 51.3, 최근100회차: 58, 최근50회차: 62 },
    { name: '연속번호 2개1쌍', 전체회차: 42, 최근100회차: 47, 최근50회차: 52 }
  ];

  // 주요 패턴 중요도 점수 (0-100)
  const patternImportanceData = [
    { name: '고저비율 4:2', 점수: 85 },
    { name: '색상 4가지', 점수: 90 },
    { name: '홀짝비율 4:2', 점수: 82 },
    { name: 'AC값 8-9', 점수: 78 },
    { name: '연속번호 2개1쌍', 점수: 75 },
    { name: '대각선 매칭', 점수: 70 },
    { name: '번호간격 5-7', 점수: 68 },
    { name: '총합 135-160', 점수: 65 }
  ];

  // 최적 전략 레이더 차트 데이터
  const optimalStrategyData = [
    { feature: '고저비율 4:2', 전체회차: 60, 최근100회차: 70, 최근50회차: 95 },
    { feature: '홀짝비율 4:2', 전체회차: 62, 최근100회차: 75, 최근50회차: 90 },
    { feature: '색상 4가지', 전체회차: 70, 최근100회차: 85, 최근50회차: 95 },
    { feature: 'AC값 8-9', 전체회차: 55, 최근100회차: 80, 최근50회차: 90 },
    { feature: '연속번호 2개1쌍', 전체회차: 60, 최근100회차: 75, 최근50회차: 85 },
    { feature: '총합 135-160', 전체회차: 50, 최근100회차: 65, 최근50회차: 80 }
  ];

  // 피해야 할 패턴 데이터
  const avoidPatternsData = [
    { name: '세로/가로 연속 3/4줄', value: 97.6 },
    { name: '연속된 6줄 라인', value: 100 },
    { name: '3개 이상 연속번호', value: 94.3 },
    { name: '동일 구간 4개+', value: 94.2 },
    { name: '극단 고저/홀짝', value: 96.5 }
  ];

  // 대시보드 테마 스타일
  const dashboardStyle = {
    container: {
      backgroundColor: colors.background,
      padding: '20px',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
    },
    header: {
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
    },
    title: {
      fontSize: '24px',
      fontWeight: 'bold',
      color: '#333333',
      marginBottom: '5px'
    },
    subtitle: {
      fontSize: '14px',
      color: colors.neutral,
      marginBottom: '15px'
    },
    tabs: {
      display: 'flex',
      borderBottom: `1px solid ${colors.neutralLight}`,
      marginBottom: '20px'
    },
    tab: {
      padding: '10px 16px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      marginRight: '10px',
      borderBottom: '2px solid transparent'
    },
    activeTab: {
      color: colors.primary,
      borderBottom: `2px solid ${colors.primary}`
    },
    inactiveTab: {
      color: colors.neutral,
      borderBottom: '2px solid transparent'
    },
    card: {
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
    },
    cardTitle: {
      fontSize: '16px',
      fontWeight: 'bold',
      color: '#333333',
      marginBottom: '15px'
    },
    row: {
      display: 'flex',
      flexWrap: 'wrap',
      margin: '0 -10px'
    },
    col2: {
      flex: '0 0 calc(50% - 20px)',
      margin: '0 10px 20px',
      minWidth: '300px'
    },
    col3: {
      flex: '0 0 calc(33.333% - 20px)',
      margin: '0 10px 20px',
      minWidth: '250px'
    },
    selector: {
      padding: '8px 12px',
      borderRadius: '4px',
      border: `1px solid ${colors.neutralLight}`,
      fontSize: '14px',
      marginBottom: '15px',
      marginRight: '10px'
    },
    optimalBox: {
      backgroundColor: colors.primary,
      color: 'white',
      padding: '15px',
      borderRadius: '6px',
      marginBottom: '10px'
    },
    optimTitle: {
      fontSize: '18px',
      fontWeight: 'bold',
      marginBottom: '10px'
    },
    optimItem: {
      fontSize: '14px',
      marginBottom: '6px',
      display: 'flex',
      alignItems: 'center'
    },
    optimDot: {
      width: '8px',
      height: '8px',
      borderRadius: '50%',
      backgroundColor: colors.accent,
      marginRight: '8px'
    }
  };

  return (
    <div style={dashboardStyle.container}>
      {/* 헤더 섹션 */}
      <div style={dashboardStyle.header}>
        <div style={dashboardStyle.title}>로또 당첨 패턴 종합 분석 대시보드</div>
        <div style={dashboardStyle.subtitle}>전체 회차, 최근 100회차, 최근 50회차 패턴 비교 분석</div>

        {/* 시간 범위 선택 */}
        <div style={{ marginBottom: '20px' }}>
          <select
            style={dashboardStyle.selector}
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
          >
            <option value="전체 회차">전체 회차</option>
            <option value="최근 100회차">최근 100회차</option>
            <option value="최근 50회차">최근 50회차</option>
          </select>
        </div>

        {/* 탭 네비게이션 */}
        <div style={dashboardStyle.tabs}>
          <div
            style={{
              ...dashboardStyle.tab,
              ...(selectedTab === '분포 패턴' ? dashboardStyle.activeTab : dashboardStyle.inactiveTab)
            }}
            onClick={() => setSelectedTab('분포 패턴')}
          >
            분포 패턴
          </div>
          <div
            style={{
              ...dashboardStyle.tab,
              ...(selectedTab === '트렌드 분석' ? dashboardStyle.activeTab : dashboardStyle.inactiveTab)
            }}
            onClick={() => setSelectedTab('트렌드 분석')}
          >
            트렌드 분석
          </div>
          <div
            style={{
              ...dashboardStyle.tab,
              ...(selectedTab === '최적 전략' ? dashboardStyle.activeTab : dashboardStyle.inactiveTab)
            }}
            onClick={() => setSelectedTab('최적 전략')}
          >
            최적 전략
          </div>
        </div>
      </div>

      {/* 분포 패턴 탭 */}
      {selectedTab === '분포 패턴' && (
        <>
          <div style={dashboardStyle.row}>
            {/* 고저비율 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>고저비율 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.highLowRatio[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.primary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 홀짝비율 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>홀짝비율 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.oddEvenRatio[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.secondary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 총합구간 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>총합구간 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.sumRange[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.tertiary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 볼 색상 분포 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>볼 색상 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={timeRangeData.ballColors[timeRange]}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      nameKey="name"
                      label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {timeRangeData.ballColors[timeRange].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={colors.chartColors[index % colors.chartColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* AC값 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>AC값 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.acValues[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.success} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 연속 번호 패턴 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>연속 번호 패턴</div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={timeRangeData.consecutiveNumbers[timeRange]}
                      cx="50%"
                      cy="50%"
                      labelLine={true}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      nameKey="name"
                      label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    >
                      {timeRangeData.consecutiveNumbers[timeRange].map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={colors.chartColors[index % colors.chartColors.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 소수 분포 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>소수 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.primeNumbers[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.quaternary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 분산도 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>분산도 분포</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.dispersion[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.warning} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 번호 간격 패턴 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>번호 간격 패턴</div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={timeRangeData.numberGaps[timeRange]}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="비율 (%)" fill={colors.accent} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 트렌드 분석 탭 */}
      {selectedTab === '트렌드 분석' && (
        <>
          <div style={dashboardStyle.row}>
            {/* 시간에 따른 패턴 변화 추이 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>시간에 따른 주요 패턴 변화 추이</div>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={trendData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="고저_3대3" name="고저 3:3" stroke={colors.primary} activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="고저_4대2" name="고저 4:2" stroke={colors.secondary} />
                    <Line type="monotone" dataKey="홀짝_3대3" name="홀짝 3:3" stroke={colors.tertiary} />
                    <Line type="monotone" dataKey="홀짝_4대2" name="홀짝 4:2" stroke={colors.quaternary} />
                    <Line type="monotone" dataKey="연속번호_2개1쌍" name="연속번호 2개1쌍" stroke={colors.success} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 패턴 비교 분석 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>패턴 비교 분석</div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={patternComparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="전체회차" name="전체 회차" fill={colors.primary} />
                    <Bar dataKey="최근100회차" name="최근 100회차" fill={colors.secondary} />
                    <Bar dataKey="최근50회차" name="최근 50회차" fill={colors.tertiary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 패턴 중요도 점수 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>주요 패턴 중요도 점수</div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart layout="vertical" data={patternImportanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[0, 100]} />
                    <YAxis dataKey="name" type="category" width={120} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="점수" name="중요도 점수" fill={colors.primary} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 피해야 할 패턴 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>피해야 할 패턴 (회피율 %)</div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart layout="vertical" data={avoidPatternsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" domain={[90, 100]} />
                    <YAxis dataKey="name" type="category" width={150} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" name="회피율 (%)" fill={colors.error} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 트렌드 요약 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>주요 트렌드 변화 요약</div>
                <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <p><strong>홀수와 고비율 번호의 증가:</strong> 홀수와 고비율(24-45) 번호의 비중이 지속적으로 증가하고 있으며, 특히 최근 50회차에서는 4:2 비율이 가장 우세합니다.</p>
                  <p><strong>총합 범위의 상향 조정:</strong> 평균 총합이 전체 회차 132.5 → 최근 100회차 136 → 최근 50회차 140으로 지속 상승하고 있어, 총합 범위를 상향 조정할 필요가 있습니다.</p>
                  <p><strong>번호 간격의 감소:</strong> 번호 간 평균 간격이 전체 회차 7~9 → 최근 100회차 6~8 → 최근 50회차 5~7로 감소하여, 더 조밀한 번호 배치가 유리해지고 있습니다.</p>
                  <p><strong>연속 번호 패턴의 중요성 증가:</strong> 2개 연속 번호 1쌍 포함 비율이 전체 회차 42% → 최근 100회차 47% → 최근 50회차 52%로 지속 증가하여, 무연속 조합보다 더 유리해졌습니다.</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}

      {/* 최적 전략 탭 */}
      {selectedTab === '최적 전략' && (
        <>
          <div style={dashboardStyle.row}>
            {/* 최적 전략 레이더 차트 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>최적 전략 패턴 비교</div>
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={optimalStrategyData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="feature" />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} />
                    <Radar name="전체 회차" dataKey="전체회차" stroke={colors.primary} fill={colors.primary} fillOpacity={0.2} />
                    <Radar name="최근 100회차" dataKey="최근100회차" stroke={colors.secondary} fill={colors.secondary} fillOpacity={0.2} />
                    <Radar name="최근 50회차" dataKey="최근50회차" stroke={colors.tertiary} fill={colors.tertiary} fillOpacity={0.2} />
                    <Legend />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* 최적 조합 전략 박스 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>현재 최적의 당첨 패턴 조합 (최근 50회차 기준)</div>
                <div style={dashboardStyle.optimalBox}>
                  <div style={dashboardStyle.optimTitle}>균형적 분포 (최신 트렌드)</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 홀짝비율: 4:2 (홀수 우세) 또는 3:3</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 고저비율: 4:2 (고비율 우세) 또는 3:3</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 총합 범위: 135~160 (상향 조정)</div>
                </div>

                <div style={{ ...dashboardStyle.optimalBox, backgroundColor: colors.success }}>
                  <div style={dashboardStyle.optimTitle}>번호 속성 최적화</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 소수: 2개</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 합성수: 3개</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 완전제곱수: 1개</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 배수 조합: 3의 배수 1~2개, 4의 배수 1~2개, 5의 배수 1~2개</div>
                </div>

                <div style={{ ...dashboardStyle.optimalBox, backgroundColor: colors.secondary }}>
                  <div style={dashboardStyle.optimTitle}>패턴 최적화</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 색상: 4가지 색상 볼 포함 (가장 중요)</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> AC값: 8~9 (상향 조정)</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 연속 번호: 2개 연속 번호 1쌍 포함</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 번호 간격: 평균 5~7 (더욱 조밀한 분포)</div>
                  <div style={dashboardStyle.optimItem}><div style={dashboardStyle.optimDot}></div> 분산도: 표준편차 11~14 (균일한 분포)</div>
                </div>
              </div>
            </div>

            {/* 피해야 할 확실한 패턴 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>피해야 할 확실한 패턴</div>
                <div style={{ fontSize: '14px', lineHeight: '1.6' }}>
                  <p style={{ backgroundColor: colors.error, color: 'white', padding: '10px', borderRadius: '4px', marginBottom: '10px' }}>
                    <strong>세로/가로 연속 3줄 또는 4줄에 모든 번호 배치</strong><br/>
                    발생 빈도: 세로 3줄 약 2.2%, 가로 3줄 약 2.4%, 세로 4줄 약 5.3%
                  </p>
                  <p style={{ backgroundColor: colors.error, color: 'white', padding: '10px', borderRadius: '4px', marginBottom: '10px' }}>
                    <strong>연속된 6줄 라인 마킹</strong><br/>
                    발생 빈도: 0% (한 번도 발생하지 않음)
                  </p>
                  <p style={{ backgroundColor: colors.error, color: 'white', padding: '10px', borderRadius: '4px', marginBottom: '10px' }}>
                    <strong>3개 이상 연속된 번호</strong><br/>
                    발생 빈도: 약 5.7%
                  </p>
                  <p style={{ backgroundColor: colors.error, color: 'white', padding: '10px', borderRadius: '4px' }}>
                    <strong>극단적인 고저/홀짝 비율 (6:0 또는 0:6)</strong><br/>
                    발생 빈도: 각각 약 3% 미만
                  </p>
                </div>
              </div>
            </div>

            {/* 최종 추천 전략 */}
            <div style={dashboardStyle.col2}>
              <div style={dashboardStyle.card}>
                <div style={dashboardStyle.cardTitle}>최종 추천 전략 요약</div>
                <div style={{ fontSize: '14px', lineHeight: '1.6', backgroundColor: colors.background, padding: '15px', borderRadius: '6px' }}>
                  <p>로또 당첨 패턴 분석 결과, <strong>균형과 다양성</strong>이 가장 중요한 요소이지만, 최근 패턴 변화를 반영하여 다음 전략을 최우선적으로 고려하는 것이 가장 효과적입니다:</p>
                  <ol style={{ paddingLeft: '20px' }}>
                    <li style={{ marginBottom: '8px' }}><strong>홀수 우세 (4:2)</strong>와 <strong>고비율 우세 (4:2)</strong> 조합</li>
                    <li style={{ marginBottom: '8px' }}><strong>색상 다양성 (4가지 색상)</strong> 포함</li>
                    <li style={{ marginBottom: '8px' }}><strong>AC값 8~9</strong> 범위 유지</li>
                    <li style={{ marginBottom: '8px' }}><strong>2개 연속 번호 1쌍</strong> 포함</li>
                    <li style={{ marginBottom: '8px' }}><strong>번호 간격 5~7</strong> 유지 (조밀한 분포)</li>
                    <li style={{ marginBottom: '8px' }}><strong>총합 135~160</strong> 범위 내 유지</li>
                    <li style={{ marginBottom: '8px' }}>소수 2개, 합성수 3개, 완전제곱수 1개로 구성</li>
                  </ol>
                  <p style={{ marginTop: '10px' }}><strong>참고:</strong> 이 전략은 통계적 분석에 기반하며, 로또 번호 선택의 완전한 성공을 보장하지는 않습니다. 여러 조합을 시도하되, 위 패턴을 참고하시기 바랍니다.</p>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default LotteryDashboard;
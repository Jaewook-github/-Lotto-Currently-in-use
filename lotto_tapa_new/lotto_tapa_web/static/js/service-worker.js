// 서비스 워커 - 로또 타파 웹 서비스
// 오프라인 기능과 성능 향상을 위한 캐싱 구현

const CACHE_NAME = 'lotto-tapa-cache-v1';
const OFFLINE_URL = '/offline.html';

// 캐싱할 정적 자원 목록
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/script.js',
  '/static/js/charts.js',
  '/static/js/tabs.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
  'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap',
  OFFLINE_URL
];

// 서비스 워커 설치 시 캐시 설정
self.addEventListener('install', event => {
  // 기존 서비스 워커가 작업을 마칠 때까지 기다리지 않고 즉시 활성화
  self.skipWaiting();

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('캐시 생성됨');
        return cache.addAll(urlsToCache);
      })
  );
});

// 서비스 워커 활성화 시 이전 캐시 삭제
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName !== CACHE_NAME;
        }).map(cacheName => {
          console.log('오래된 캐시 삭제:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      // 새 서비스 워커가 페이지 로드 없이 바로 제어 가능하도록 함
      return self.clients.claim();
    })
  );
});

// 네트워크 요청 처리
self.addEventListener('fetch', event => {
  // API 요청은 캐싱하지 않고 네트워크 우선 처리
  if (event.request.url.includes('/generate') ||
      event.request.url.includes('/update-config') ||
      event.request.url.includes('/reset-config') ||
      event.request.url.includes('/stats')) {
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          return caches.match(OFFLINE_URL);
        })
    );
    return;
  }

  // 정적 자원 요청 처리 - 캐시 우선, 실패 시 네트워크 요청
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // 캐시에서 찾았으면 반환
        if (response) {
          return response;
        }

        // 캐시에 없으면 네트워크 요청
        return fetch(event.request)
          .then(networkResponse => {
            // 네트워크 요청이 실패하거나 200 응답이 아니면 그대로 반환
            if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
              return networkResponse;
            }

            // 응답을 캐싱하기 위해 복제 (스트림은 한 번만 사용 가능하므로)
            const responseToCache = networkResponse.clone();

            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return networkResponse;
          })
          .catch(() => {
            // 오프라인이면 오프라인 페이지 제공
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }

            // 이미지가 요청된 경우 자리 표시자 이미지 제공
            if (event.request.destination === 'image') {
              return new Response(
                '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><text x="50%" y="50%" font-family="sans-serif" font-size="12" text-anchor="middle" dominant-baseline="middle">오프라인</text></svg>',
                { headers: { 'Content-Type': 'image/svg+xml' } }
              );
            }

            // 그 외의 요청은 빈 응답 반환
            return new Response('', { status: 408, statusText: '오프라인 모드' });
          });
      })
  );
});

// 푸시 알림 수신
self.addEventListener('push', event => {
  if (!event.data) return;

  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge-96x96.png',
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(
    self.registration.showNotification('로또 타파', options)
  );
});

// 푸시 알림 클릭
self.addEventListener('notificationclick', event => {
  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data.url)
  );
});
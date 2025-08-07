// Persian File Copier Pro - Service Worker
// فارسی کاپیر فایل حرفه‌ای

const CACHE_NAME = 'pfc-pro-v3.5.0';
const OFFLINE_URL = '/offline.html';

// Files to cache for offline functionality
const CACHE_FILES = [
    '/',
    '/index.html',
    '/manifest.json',
    '/sw.js',
    // Add critical CSS and JS files here if they become separate files
];

// Install event
self.addEventListener('install', (event) => {
    console.log('[SW] Installing Service Worker...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching essential files');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('[SW] Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[SW] Error caching files:', error);
            })
    );
});

// Activate event
self.addEventListener('activate', (event) => {
    console.log('[SW] Activating Service Worker...');
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[SW] Service Worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event
self.addEventListener('fetch', (event) => {
    // Only handle GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Skip non-HTTP requests
    if (!event.request.url.startsWith('http')) {
        return;
    }
    
    // Handle API requests differently
    if (event.request.url.includes('/api/')) {
        // For API requests, always try network first
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // If network succeeds, return the response
                    return response;
                })
                .catch((error) => {
                    console.warn('[SW] API request failed, app likely offline:', error);
                    // Return a custom offline response for API requests
                    return new Response(
                        JSON.stringify({
                            error: 'Network unavailable',
                            message: 'برنامه آفلاین است',
                            offline: true
                        }),
                        {
                            status: 503,
                            headers: {
                                'Content-Type': 'application/json',
                                'Cache-Control': 'no-cache'
                            }
                        }
                    );
                })
        );
        return;
    }
    
    // For other requests, use cache-first strategy
    event.respondWith(
        caches.match(event.request)
            .then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                return fetch(event.request)
                    .then((response) => {
                        // Don't cache non-successful responses
                        if (!response.ok) {
                            return response;
                        }
                        
                        // Clone the response for caching
                        const responseToCache = response.clone();
                        
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch((error) => {
                        console.warn('[SW] Fetch failed:', error);
                        
                        // Return offline page for navigation requests
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL) || 
                                   caches.match('/') ||
                                   new Response('App is offline', { status: 503 });
                        }
                        
                        throw error;
                    });
            })
    );
});

// Handle messages from the main app
self.addEventListener('message', (event) => {
    console.log('[SW] Received message:', event.data);
    
    switch (event.data.type) {
        case 'SKIP_WAITING':
            self.skipWaiting();
            break;
            
        case 'CHECK_UPDATE':
            // Force update check
            self.registration.update();
            break;
            
        case 'CACHE_CLEAR':
            // Clear all caches
            caches.keys().then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => caches.delete(cacheName))
                );
            }).then(() => {
                event.ports[0].postMessage({ success: true });
            });
            break;
            
        default:
            console.log('[SW] Unknown message type:', event.data.type);
    }
});

// Push notification event (for future use)
self.addEventListener('push', (event) => {
    if (!event.data) {
        return;
    }
    
    const data = event.data.json();
    const options = {
        body: data.body || 'Persian File Copier Pro',
        icon: '/manifest-icon-192.png',
        badge: '/manifest-icon-72.png',
        dir: 'rtl',
        lang: 'fa',
        tag: 'pfc-notification',
        requireInteraction: false,
        actions: [
            {
                action: 'open',
                title: 'باز کردن',
                icon: '/manifest-icon-72.png'
            },
            {
                action: 'close',
                title: 'بستن'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification(data.title || 'Persian File Copier Pro', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
    event.notification.close();
    
    if (event.action === 'open' || !event.action) {
        event.waitUntil(
            clients.openWindow('/')
        );
    }
});

console.log('[SW] Persian File Copier Pro Service Worker loaded');
const CACHE_NAME = 'agroguard-v4';
const ASSETS = [
    '/farmer',
    '/static/manifest.json',
    '/static/images/agroguard_logo.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/fonts/bootstrap-icons.woff2'
];

self.addEventListener('install', (event) => {
    console.log('[SW] Installing service worker...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Caching app shell');
                return cache.addAll(ASSETS);
            })
            .then(() => {
                console.log('[SW] Service worker installed successfully');
                return self.skipWaiting(); // Activate immediately
            })
    );
});

self.addEventListener('activate', (event) => {
    console.log('[SW] Activating service worker...');
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
            console.log('[SW] Service worker activated');
            return self.clients.claim(); // Take control immediately
        })
    );
});

self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                if (response) {
                    // Cache hit - return cached response
                    return response;
                }
                // Not in cache - fetch from network
                return fetch(event.request)
                    .then((response) => {
                        // Check if valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        // Clone the response
                        const responseToCache = response.clone();
                        // Cache the fetched response for future use
                        caches.open(CACHE_NAME)
                            .then((cache) => {
                                cache.put(event.request, responseToCache);
                            });
                        return response;
                    })
                    .catch(() => {
                        // If offline and request is for page, return cached farmer page
                        if (event.request.mode === 'navigate') {
                            return caches.match('/farmer');
                        }
                    });
            })
    );
});

// Background Sync for offline scans
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-scans') {
        console.log('[SW] Background sync triggered for offline scans');
        event.waitUntil(syncOfflineScans());
    }
});

// Sync offline scans function (called by background sync)
async function syncOfflineScans() {
    try {
        // Open IndexedDB
        const db = await openDatabase();
        const transaction = db.transaction(['offlineScans'], 'readonly');
        const objectStore = transaction.objectStore('offlineScans');
        const index = objectStore.index('synced');
        const request = index.getAll(false);

        const pendingScans = await new Promise((resolve, reject) => {
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });

        console.log(`[SW] Found ${pendingScans.length} pending scans`);

        for (const scan of pendingScans) {
            try {
                // Convert base64 to blob
                const response = await fetch(scan.imageData);
                const blob = await response.blob();
                
                // Create form data
                const formData = new FormData();
                formData.append('file', blob);

                // Send to server
                const res = await fetch(`/predict?lang=${scan.language}`, {
                    method: 'POST',
                    headers: { 'device-id': scan.farmerId }
                    body: formData
                });

                if (res.ok) {
                    // Mark as synced
                    await markScanSynced(db, scan.id);
                    console.log(`[SW] Synced scan ${scan.id}`);
                }
            } catch (error) {
                console.error(`[SW] Failed to sync scan ${scan.id}:`, error);
            }
        }
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

function openDatabase() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('AgroGuardOffline', 1);
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function markScanSynced(db, scanId) {
    const transaction = db.transaction(['offlineScans'], 'readwrite');
    const objectStore = transaction.objectStore('offlineScans');
    const request = objectStore.get(scanId);
    
    return new Promise((resolve, reject) => {
        request.onsuccess = () => {
            const scan = request.result;
            if (scan) {
                scan.synced = true;
                scan.syncedAt = new Date().toISOString();
                objectStore.put(scan);
                resolve();
            }
        };
        request.onerror = () => reject(request.error);
    });
}

// Service Worker for EmotionalAI PWA
// Provides offline functionality, caching, and mobile optimization

const CACHE_NAME = 'emotionalai-v1.0.0';
const STATIC_CACHE = 'emotionalai-static-v1.0.0';
const DYNAMIC_CACHE = 'emotionalai-dynamic-v1.0.0';

// Files to cache for offline functionality
const STATIC_FILES = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/css/app.css',
  '/js/app.js',
  '/offline.html'
];

// API endpoints to cache
const API_CACHE_PATTERNS = [
  '/api/personas',
  '/api/memory',
  '/api/voice',
  '/api/scene'
];

// Install event - cache static files
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[SW] Caching static files');
        return cache.addAll(STATIC_FILES);
      })
      .then(() => {
        console.log('[SW] Static files cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('[SW] Failed to cache static files:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      })
      .then(() => {
        console.log('[SW] Service worker activated');
        return self.clients.claim();
      })
  );
});

// Fetch event - handle network requests
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle different types of requests
  if (request.method === 'GET') {
    // Static files - cache first strategy
    if (isStaticFile(url.pathname)) {
      event.respondWith(cacheFirst(request, STATIC_CACHE));
    }
    // API requests - network first with cache fallback
    else if (isApiRequest(url.pathname)) {
      event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    }
    // Other requests - network first
    else {
      event.respondWith(networkFirst(request, DYNAMIC_CACHE));
    }
  } else {
    // Non-GET requests - network only
    event.respondWith(networkOnly(request));
  }
});

// Cache first strategy
async function cacheFirst(request, cacheName) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('[SW] Cache first strategy failed:', error);
    return new Response('Offline content not available', { status: 503 });
  }
}

// Network first strategy
async function networkFirst(request, cacheName) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[SW] Network failed, trying cache:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }
    
    return new Response('Offline content not available', { status: 503 });
  }
}

// Network only strategy
async function networkOnly(request) {
  try {
    return await fetch(request);
  } catch (error) {
    console.error('[SW] Network only strategy failed:', error);
    return new Response('Network request failed', { status: 503 });
  }
}

// Check if request is for a static file
function isStaticFile(pathname) {
  return STATIC_FILES.some(file => pathname === file) ||
         pathname.startsWith('/css/') ||
         pathname.startsWith('/js/') ||
         pathname.startsWith('/icons/') ||
         pathname.startsWith('/images/') ||
         pathname.endsWith('.css') ||
         pathname.endsWith('.js') ||
         pathname.endsWith('.png') ||
         pathname.endsWith('.jpg') ||
         pathname.endsWith('.svg');
}

// Check if request is for API
function isApiRequest(pathname) {
  return API_CACHE_PATTERNS.some(pattern => pathname.startsWith(pattern));
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'voice-input') {
    event.waitUntil(syncVoiceInput());
  } else if (event.tag === 'memory-store') {
    event.waitUntil(syncMemoryStore());
  }
});

// Handle push notifications
self.addEventListener('push', (event) => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: event.data ? event.data.text() : 'New message from your companion',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open App',
        icon: '/icons/icon-72x72.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/icons/icon-72x72.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('EmotionalAI', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Notification clicked:', event.action);
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Sync voice input when back online
async function syncVoiceInput() {
  try {
    const voiceQueue = await getVoiceQueue();
    
    for (const voiceInput of voiceQueue) {
      try {
        const response = await fetch('/api/voice/input', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(voiceInput)
        });
        
        if (response.ok) {
          // Remove from queue if successful
          await removeFromVoiceQueue(voiceInput.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync voice input:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Voice sync failed:', error);
  }
}

// Sync memory store when back online
async function syncMemoryStore() {
  try {
    const memoryQueue = await getMemoryQueue();
    
    for (const memory of memoryQueue) {
      try {
        const response = await fetch('/api/memory/store', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(memory)
        });
        
        if (response.ok) {
          // Remove from queue if successful
          await removeFromMemoryQueue(memory.id);
        }
      } catch (error) {
        console.error('[SW] Failed to sync memory:', error);
      }
    }
  } catch (error) {
    console.error('[SW] Memory sync failed:', error);
  }
}

// IndexedDB helpers for offline queue
async function getVoiceQueue() {
  // Implementation would use IndexedDB to get queued voice inputs
  return [];
}

async function removeFromVoiceQueue(id) {
  // Implementation would use IndexedDB to remove from queue
}

async function getMemoryQueue() {
  // Implementation would use IndexedDB to get queued memories
  return [];
}

async function removeFromMemoryQueue(id) {
  // Implementation would use IndexedDB to remove from queue
}

// Message handling for communication with main thread
self.addEventListener('message', (event) => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_API_RESPONSE') {
    const { request, response } = event.data;
    event.waitUntil(
      caches.open(DYNAMIC_CACHE)
        .then(cache => cache.put(request, response))
    );
  }
});

console.log('[SW] Service worker script loaded'); 
// sw.js - Service Worker for handling background notifications
const CACHE_NAME = 'dashboard-cache-v1';
const NOTIFICATION_ENDPOINT = '/api/notifications/';

// Files to cache for offline access
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/img/notification-icon.png',
  '/static/img/badge-icon.png'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve cached content when offline
self.addEventListener('fetch', event => {
  // Skip for API calls
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/ws/')) {
    return;
  }
  
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Clone the request because it's a one-time use stream
        const fetchRequest = event.request.clone();
        
        return fetch(fetchRequest).then(response => {
          // Check for valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response because it's a one-time use stream
          const responseToCache = response.clone();
          
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
            
          return response;
        });
      })
  );
});

// Background sync for offline notifications
self.addEventListener('sync', event => {
  if (event.tag === 'sync-notifications') {
    event.waitUntil(syncNotifications());
  }
});

// Push event - handle incoming push notifications
self.addEventListener('push', event => {
  console.log('Push received:', event);
  
  let notificationData = {};
  
  try {
    notificationData = event.data.json();
  } catch (e) {
    notificationData = {
      title: 'New Notification',
      message: event.data ? event.data.text() : 'No details available'
    };
  }
  
  // Store notification in IndexedDB/localStorage for later retrieval
  storeNotification(notificationData);
  
  // Show notification
  const options = {
    body: notificationData.message || 'New notification received',
    icon: '/static/img/notification-icon.png',
    badge: '/static/img/badge-icon.png',
    data: notificationData
  };
  
  event.waitUntil(
    self.registration.showNotification(notificationData.title || 'Dashboard Notification', options)
  );
  
  // Notify all open tabs
  event.waitUntil(notifyClients(notificationData));
});

// Notification click event
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  // Open/focus the dashboard when notification is clicked
  event.waitUntil(
    clients.matchAll({type: 'window'})
      .then(clientList => {
        // If a dashboard window is already open, focus it
        for (const client of clientList) {
          if (client.url.includes('/dashboard') && 'focus' in client) {
            return client.focus();
          }
        }
        
        // Otherwise open a new window
        if (clients.openWindow) {
          return clients.openWindow('/dashboard');
        }
      })
  );
});

// Message event - handle messages from clients
self.addEventListener('message', event => {
  console.log('Message received in SW:', event.data);
  
  if (event.data && event.data.type === 'NOTIFICATION_STORED') {
    // Broadcast the notification to all other tabs
    notifyClients(event.data.notification, event.source.id);
  }
});

// Function to notify all clients of a new notification
async function notifyClients(notification, sourceClientId = null) {
  const clients = await self.clients.matchAll({type: 'window'});
  
  for (const client of clients) {
    // Don't send notification back to the source client
    if (sourceClientId && client.id === sourceClientId) {
      continue;
    }
    
    client.postMessage({
      type: 'NEW_NOTIFICATION',
      notification: notification
    });
  }
}

// Function to store notifications in IndexedDB
async function storeNotification(notification) {
  // This would be better with IndexedDB, but using localStorage for simplicity
  // IndexedDB would require more complex code
  
  // For a real implementation, consider using the idb-keyval library:
  // https://github.com/jakearchibald/idb-keyval
  
  // Get background notifications
  const request = await fetch('/api/store-notification/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(notification)
  });
  
  return request.ok;
}

// Function to sync offline notifications with the server
async function syncNotifications() {
  // This would retrieve unsynchronized notifications from IndexedDB
  // and send them to the server
  
  // Example implementation:
  // 1. Get offline notifications from IndexedDB
  // 2. Send them to the server
  // 3. Mark them as synchronized
  
  return fetch(NOTIFICATION_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      action: 'sync',
      notifications: [] // Would be populated from IndexedDB
    })
  }).then(response => {
    if (response.ok) {
      // Update local storage to mark notifications as synchronized
      return Promise.resolve();
    }
    return Promise.reject('Sync failed');
  });
}

// Periodic background sync for checking new notifications
self.addEventListener('periodicsync', event => {
  if (event.tag === 'check-notifications') {
    event.waitUntil(checkForNewNotifications());
  }
});

// Function to check for new notifications
async function checkForNewNotifications() {
  try {
    // Get the timestamp of most recent notification
    const lastCheck = localStorage.getItem('lastNotificationCheck') || 0;
    
    // Update the timestamp
    localStorage.setItem('lastNotificationCheck', Date.now());
    
    // Fetch new notifications
    const response = await fetch(`${NOTIFICATION_ENDPOINT}?since=${lastCheck}`);
    
    if (!response.ok) {
      throw new Error('Failed to fetch notifications');
    }
    
    const data = await response.json();
    
    if (data.notifications && data.notifications.length > 0) {
      // Process new notifications
      data.notifications.forEach(notification => {
        // Store notification
        storeNotification(notification);
        
        // Notify clients
        notifyClients(notification);
      });
    }
  } catch (error) {
    console.error('Error checking for notifications:', error);
  }
}

console.log('Service Worker loaded');
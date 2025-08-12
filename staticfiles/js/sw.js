/**
 * Service Worker لإشعارات سكنك
 * يدعم الإشعارات في الخلفية والتحديثات التلقائية
 */

const CACHE_NAME = 'sakanak-notifications-v1';
const urlsToCache = [
    '/static/js/notifications.js',
    '/static/images/logo.png',
    '/static/images/message-icon.png',
    '/static/sounds/message.mp3',
    '/static/sounds/notification.mp3'
];

// تثبيت Service Worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Service Worker: تم فتح الكاش');
                return cache.addAll(urlsToCache);
            })
    );
});

// تفعيل Service Worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Service Worker: حذف كاش قديم', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// التعامل مع طلبات الشبكة
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // إرجاع من الكاش إذا وُجد
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

// التعامل مع الإشعارات المرسلة من الخادم
self.addEventListener('push', event => {
    console.log('Service Worker: تم استلام push notification');
    
    let data = {};
    if (event.data) {
        data = event.data.json();
    }

    const options = {
        body: data.body || 'لديك رسالة جديدة',
        icon: data.icon || '/static/images/message-icon.png',
        badge: '/static/images/badge.png',
        vibrate: [200, 100, 200],
        data: data.data || {},
        actions: [
            {
                action: 'view',
                title: 'عرض',
                icon: '/static/images/view-icon.png'
            },
            {
                action: 'close',
                title: 'إغلاق',
                icon: '/static/images/close-icon.png'
            }
        ],
        requireInteraction: true,
        tag: data.tag || 'sakanak-message'
    };

    event.waitUntil(
        self.registration.showNotification(
            data.title || 'سكنك - رسالة جديدة',
            options
        )
    );
});

// التعامل مع النقر على الإشعارات
self.addEventListener('notificationclick', event => {
    console.log('Service Worker: تم النقر على الإشعار');
    
    event.notification.close();

    if (event.action === 'view') {
        // فتح المحادثة
        const chatId = event.notification.data.chatId;
        const url = chatId ? `/bookings/chat/${chatId}/` : '/bookings/user-chats/';
        
        event.waitUntil(
            clients.matchAll().then(clientList => {
                // البحث عن نافذة مفتوحة
                for (const client of clientList) {
                    if (client.url.includes('sakanak') && 'focus' in client) {
                        client.focus();
                        client.navigate(url);
                        return;
                    }
                }
                // فتح نافذة جديدة إذا لم توجد
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
        );
    } else if (event.action === 'close') {
        // إغلاق الإشعار فقط
        console.log('تم إغلاق الإشعار');
    }
});

// التعامل مع إغلاق الإشعارات
self.addEventListener('notificationclose', event => {
    console.log('Service Worker: تم إغلاق الإشعار');
});

// التعامل مع الرسائل من الصفحة الرئيسية
self.addEventListener('message', event => {
    console.log('Service Worker: تم استلام رسالة:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// دالة لإرسال إشعار مخصص
function sendNotification(title, options) {
    return self.registration.showNotification(title, {
        body: options.body || '',
        icon: options.icon || '/static/images/logo.png',
        badge: '/static/images/badge.png',
        vibrate: options.vibrate || [200, 100, 200],
        data: options.data || {},
        tag: options.tag || 'sakanak-notification',
        requireInteraction: options.requireInteraction || false,
        ...options
    });
}

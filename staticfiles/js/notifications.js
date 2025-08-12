/**
 * نظام الإشعارات المتقدم لسكنك
 * يدعم المتصفحات العادية و WebView للتطبيقات
 */

class SakanakNotifications {
    constructor() {
        this.isWebView = this.detectWebView();
        this.notificationQueue = [];
        this.soundEnabled = true;
        this.vibrationEnabled = true;
        this.updatesPaused = false;
        this.notificationPermission = false;
        this.init();
    }

    // كشف إذا كان التطبيق يعمل في WebView
    detectWebView() {
        const userAgent = navigator.userAgent;
        return /wv|WebView|Android.*Version\/\d+\.\d+.*Chrome/.test(userAgent) ||
               /iPhone.*AppleWebKit.*Mobile/.test(userAgent) ||
               window.ReactNativeWebView !== undefined ||
               window.flutter_inappwebview !== undefined;
    }

    // تهيئة نظام الإشعارات
    async init() {
        // إنشاء عناصر الإشعارات في DOM
        this.createNotificationElements();
        
        // طلب إذن الإشعارات
        await this.requestPermission();
        
        // تسجيل Service Worker للإشعارات المتقدمة
        if ('serviceWorker' in navigator && !this.isWebView) {
            this.registerServiceWorker();
        }
        
        // إعداد الأصوات
        this.setupSounds();
        
        console.log('نظام الإشعارات جاهز - WebView:', this.isWebView);
    }

    // إنشاء عناصر الإشعارات في DOM
    createNotificationElements() {
        // حاوي الإشعارات الرئيسي
        const container = document.createElement('div');
        container.id = 'sakanak-notifications-container';
        container.className = 'sakanak-notifications-container';
        document.body.appendChild(container);

        // إشعار الرسائل الجديدة
        const messageNotification = document.createElement('div');
        messageNotification.id = 'message-notification';
        messageNotification.className = 'message-notification hidden';
        container.appendChild(messageNotification);

        // إشعار الحالة (اتصال/انقطاع)
        const statusNotification = document.createElement('div');
        statusNotification.id = 'status-notification';
        statusNotification.className = 'status-notification hidden';
        container.appendChild(statusNotification);

        // إضافة الأنماط
        this.injectStyles();
    }

    // إضافة أنماط CSS للإشعارات
    injectStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .sakanak-notifications-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            }

            .message-notification {
                background: linear-gradient(135deg, #25d366 0%, #20b358 100%);
                color: white;
                padding: 16px 20px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(37, 211, 102, 0.3);
                margin-bottom: 10px;
                transform: translateX(400px);
                transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                pointer-events: auto;
                cursor: pointer;
                max-width: 350px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }

            .message-notification.show {
                transform: translateX(0);
            }

            .message-notification.hidden {
                transform: translateX(400px);
                opacity: 0;
            }

            .notification-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }

            .notification-title {
                font-weight: 600;
                font-size: 14px;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .notification-time {
                font-size: 11px;
                opacity: 0.8;
            }

            .notification-body {
                font-size: 13px;
                line-height: 1.4;
                margin-bottom: 8px;
            }

            .notification-actions {
                display: flex;
                gap: 8px;
                justify-content: flex-end;
            }

            .notification-btn {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 11px;
                cursor: pointer;
                transition: all 0.2s ease;
            }

            .notification-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }

            .notification-close {
                background: none;
                border: none;
                color: white;
                font-size: 16px;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.2s ease;
            }

            .notification-close:hover {
                opacity: 1;
            }

            .status-notification {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 16px;
                border-radius: 8px;
                font-size: 12px;
                transform: translateX(400px);
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            .status-notification.show {
                transform: translateX(0);
            }

            .status-notification.error {
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            }

            .status-notification.success {
                background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            }

            .notification-icon {
                font-size: 16px;
                animation: pulse 2s infinite;
            }

            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }

            .notification-badge {
                position: absolute;
                top: -8px;
                right: -8px;
                background: #ff4757;
                color: white;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                font-size: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                animation: bounce 1s infinite;
            }

            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
                40% { transform: translateY(-10px); }
                60% { transform: translateY(-5px); }
            }

            /* تحسينات للهواتف */
            @media (max-width: 768px) {
                .sakanak-notifications-container {
                    right: 10px;
                    left: 10px;
                    top: 10px;
                }

                .message-notification {
                    max-width: none;
                    transform: translateY(-100px);
                }

                .message-notification.show {
                    transform: translateY(0);
                }

                .message-notification.hidden {
                    transform: translateY(-100px);
                }
            }
        `;
        document.head.appendChild(style);
    }

    // طلب إذن الإشعارات
    async requestPermission() {
        if (!('Notification' in window)) {
            console.log('المتصفح لا يدعم الإشعارات');
            return false;
        }

        if (Notification.permission === 'granted') {
            return true;
        }

        if (Notification.permission !== 'denied') {
            const permission = await Notification.requestPermission();
            return permission === 'granted';
        }

        return false;
    }

    // إعداد الأصوات
    setupSounds() {
        this.sounds = {
            message: new Audio('/static/sounds/message.mp3'),
            notification: new Audio('/static/sounds/notification.mp3'),
            error: new Audio('/static/sounds/error.mp3')
        };

        // إعداد الأصوات للعمل في WebView
        Object.values(this.sounds).forEach(sound => {
            sound.preload = 'auto';
            sound.volume = 0.7;
        });
    }

    // تسجيل Service Worker
    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/static/js/sw.js');
            console.log('Service Worker مسجل بنجاح:', registration);
        } catch (error) {
            console.log('فشل تسجيل Service Worker:', error);
        }
    }

    // إظهار إشعار رسالة جديدة
    showMessageNotification(data) {
        const {
            title = 'رسالة جديدة',
            body = 'لديك رسالة جديدة',
            sender = 'مجهول',
            chatId = null,
            avatar = null
        } = data;

        // إشعار المتصفح/WebView
        this.showBrowserNotification(title, body, {
            icon: avatar || '/static/images/message-icon.png',
            badge: '/static/images/badge.png',
            tag: `message-${chatId}`,
            data: { chatId, type: 'message' }
        });

        // إشعار داخل الصفحة
        this.showInPageNotification({
            type: 'message',
            title,
            body,
            sender,
            chatId,
            actions: [
                { text: 'عرض', action: () => this.openChat(chatId) },
                { text: 'إغلاق', action: () => this.hideNotification('message') }
            ]
        });

        // تشغيل الصوت والاهتزاز
        this.playSound('message');
        this.vibrate([200, 100, 200]);
    }

    // إظهار إشعار المتصفح
    async showBrowserNotification(title, body, options = {}) {
        if (this.isWebView && window.webViewBridge) {
            // للتطبيقات - استخدام WebView Bridge
            window.webViewBridge.showNativeNotification(title, body, {
                icon: options.icon || '/static/images/logo.png',
                sound: true,
                vibrate: true,
                data: options.data || {},
                actions: [
                    { action: 'view', title: 'عرض' },
                    { action: 'dismiss', title: 'إغلاق' }
                ]
            }, (result) => {
                console.log('Native notification result:', result);
            });
        } else if (await this.requestPermission()) {
            // للمتصفحات العادية
            const notification = new Notification(title, {
                body,
                icon: '/static/images/logo.png',
                badge: '/static/images/badge.png',
                ...options
            });

            notification.onclick = () => {
                window.focus();
                if (options.data?.chatId) {
                    this.openChat(options.data.chatId);
                }
                notification.close();
            };

            setTimeout(() => notification.close(), 5000);
        }
    }

    // إظهار إشعار داخل الصفحة
    showInPageNotification(data) {
        const container = document.getElementById('message-notification');
        if (!container) return;

        const now = new Date();
        const timeStr = now.toLocaleTimeString('ar-EG', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        container.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">
                    <i class="fas fa-comment-dots notification-icon"></i>
                    ${data.title}
                </div>
                <div class="notification-time">${timeStr}</div>
                <button class="notification-close" onclick="sakanakNotifications.hideNotification('message')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-body">
                <strong>${data.sender}:</strong> ${data.body}
            </div>
            <div class="notification-actions">
                ${data.actions?.map(action => 
                    `<button class="notification-btn" onclick="(${action.action.toString()})()">${action.text}</button>`
                ).join('') || ''}
            </div>
        `;

        container.classList.remove('hidden');
        container.classList.add('show');

        // إخفاء تلقائي بعد 6 ثوان
        setTimeout(() => {
            this.hideNotification('message');
        }, 6000);
    }

    // إخفاء الإشعار
    hideNotification(type) {
        const element = document.getElementById(`${type}-notification`);
        if (element) {
            element.classList.remove('show');
            element.classList.add('hidden');
        }
    }

    // تشغيل الصوت
    playSound(type) {
        if (!this.soundEnabled) return;

        try {
            const sound = this.sounds[type];
            if (sound) {
                sound.currentTime = 0;
                sound.play().catch(e => console.log('لا يمكن تشغيل الصوت:', e));
            }
        } catch (error) {
            console.log('خطأ في تشغيل الصوت:', error);
        }
    }

    // فتح المحادثة
    openChat(chatId) {
        if (chatId) {
            window.location.href = `/bookings/chat/${chatId}/`;
        }
    }

    // إظهار إشعار الحالة
    showStatusNotification(message, type = 'info') {
        const container = document.getElementById('status-notification');
        if (!container) return;

        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        container.innerHTML = `
            <i class="${icons[type]} notification-icon"></i>
            ${message}
        `;

        container.className = `status-notification show ${type}`;

        setTimeout(() => {
            container.classList.remove('show');
        }, 3000);
    }

    // تحديث عداد الإشعارات
    updateNotificationBadge(count) {
        // تحديث عداد في التطبيق
        if (this.isWebView) {
            this.sendToNativeApp('updateBadge', { count });
        }

        // تحديث عداد في الصفحة
        const badges = document.querySelectorAll('.notification-badge');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'flex';
            } else {
                badge.style.display = 'none';
            }
        });
    }
}

// إنشاء مثيل عام
window.sakanakNotifications = new SakanakNotifications();

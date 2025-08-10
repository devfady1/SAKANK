/**
 * إعدادات نظام الإشعارات لتطبيق سكنك
 * يدعم المتصفحات العادية وتطبيقات WebView
 */

const NotificationConfig = {
    // الإعدادات العامة
    settings: {
        enabled: true,
        soundEnabled: true,
        vibrationEnabled: true,
        browserNotifications: true,
        inPageNotifications: true,
        autoMarkAsRead: true,
        updateInterval: 3000, // 3 ثوان
        chatListUpdateInterval: 10000, // 10 ثوان
        notificationTimeout: 5000, // 5 ثوان
        maxNotificationsQueue: 10
    },

    // أصوات الإشعارات
    sounds: {
        message: '/static/sounds/message.mp3',
        notification: '/static/sounds/notification.mp3',
        error: '/static/sounds/error.mp3',
        success: '/static/sounds/success.mp3'
    },

    // أنماط الاهتزاز
    vibrationPatterns: {
        message: [200, 100, 200],
        notification: [300, 200, 300],
        error: [500, 200, 500, 200, 500],
        success: [100, 50, 100]
    },

    // رسائل الإشعارات
    messages: {
        ar: {
            newMessage: 'رسالة جديدة',
            newMessageFrom: 'رسالة جديدة من',
            connectionLost: 'انقطع الاتصال',
            connectionRestored: 'تم استعادة الاتصال',
            messageSent: 'تم إرسال الرسالة',
            messageDelivered: 'تم تسليم الرسالة',
            messageRead: 'تم قراءة الرسالة',
            typingIndicator: 'يكتب...',
            online: 'متصل',
            offline: 'غير متصل',
            lastSeen: 'آخر ظهور',
            permissionDenied: 'تم رفض إذن الإشعارات',
            permissionGranted: 'تم منح إذن الإشعارات',
            notificationError: 'خطأ في الإشعار'
        },
        en: {
            newMessage: 'New Message',
            newMessageFrom: 'New message from',
            connectionLost: 'Connection Lost',
            connectionRestored: 'Connection Restored',
            messageSent: 'Message Sent',
            messageDelivered: 'Message Delivered',
            messageRead: 'Message Read',
            typingIndicator: 'Typing...',
            online: 'Online',
            offline: 'Offline',
            lastSeen: 'Last seen',
            permissionDenied: 'Notification permission denied',
            permissionGranted: 'Notification permission granted',
            notificationError: 'Notification error'
        }
    },

    // إعدادات WebView
    webview: {
        detectMethods: [
            () => window.ReactNativeWebView,
            () => window.flutter_inappwebview,
            () => window.Android && typeof window.Android.showNotification === 'function',
            () => window.webkit?.messageHandlers,
            () => /wv|WebView/.test(navigator.userAgent)
        ],
        
        platforms: {
            'react-native': {
                postMessage: (data) => window.ReactNativeWebView?.postMessage(JSON.stringify(data)),
                features: ['notifications', 'vibration', 'sound', 'badge', 'share']
            },
            'flutter': {
                postMessage: (data) => window.flutter_inappwebview?.callHandler('webview_message', data),
                features: ['notifications', 'vibration', 'sound', 'badge', 'share']
            },
            'android': {
                postMessage: (data) => window.Android?.handleWebViewMessage(JSON.stringify(data)),
                features: ['notifications', 'vibration', 'sound', 'badge']
            },
            'ios': {
                postMessage: (data) => window.webkit?.messageHandlers?.webview?.postMessage(data),
                features: ['notifications', 'vibration', 'sound', 'badge', 'share']
            }
        }
    },

    // إعدادات Service Worker
    serviceWorker: {
        enabled: true,
        scriptPath: '/static/js/sw.js',
        scope: '/',
        updateViaCache: 'imports',
        features: {
            pushNotifications: true,
            backgroundSync: true,
            caching: true,
            offlineSupport: true
        }
    },

    // إعدادات الإشعارات المتقدمة
    advanced: {
        // تجميع الإشعارات
        groupNotifications: true,
        maxGroupSize: 5,
        
        // إشعارات ذكية
        smartNotifications: {
            enabled: true,
            quietHours: {
                enabled: false,
                start: '22:00',
                end: '08:00'
            },
            doNotDisturb: {
                enabled: false,
                keywords: ['مهم', 'عاجل', 'urgent', 'important']
            }
        },
        
        // تخصيص حسب نوع المحادثة
        chatTypes: {
            tenant: {
                priority: 'high',
                sound: 'message',
                vibration: 'message',
                color: '#007bff'
            },
            owner: {
                priority: 'high',
                sound: 'notification',
                vibration: 'notification',
                color: '#28a745'
            },
            system: {
                priority: 'normal',
                sound: 'notification',
                vibration: 'notification',
                color: '#6c757d'
            }
        }
    },

    // إعدادات الأمان والخصوصية
    security: {
        // تشفير الإشعارات الحساسة
        encryptSensitiveData: true,
        
        // إخفاء المحتوى في الإشعارات
        hideContentInNotifications: false,
        
        // التحقق من المصدر
        validateNotificationSource: true,
        
        // حد أقصى لطول الرسالة في الإشعار
        maxNotificationLength: 100
    },

    // إعدادات التحليلات
    analytics: {
        enabled: false,
        trackNotificationClicks: false,
        trackNotificationDismissals: false,
        trackPermissionRequests: false
    },

    // الحصول على الإعدادات من localStorage
    loadSettings() {
        try {
            const saved = localStorage.getItem('sakanak_notification_settings');
            if (saved) {
                const settings = JSON.parse(saved);
                Object.assign(this.settings, settings);
            }
        } catch (error) {
            console.error('خطأ في تحميل إعدادات الإشعارات:', error);
        }
        return this.settings;
    },

    // حفظ الإعدادات في localStorage
    saveSettings(newSettings) {
        try {
            Object.assign(this.settings, newSettings);
            localStorage.setItem('sakanak_notification_settings', JSON.stringify(this.settings));
            return true;
        } catch (error) {
            console.error('خطأ في حفظ إعدادات الإشعارات:', error);
            return false;
        }
    },

    // إعادة تعيين الإعدادات للافتراضية
    resetSettings() {
        localStorage.removeItem('sakanak_notification_settings');
        // إعادة تحميل الإعدادات الافتراضية
        this.loadSettings();
    },

    // الحصول على رسالة بلغة محددة
    getMessage(key, lang = 'ar') {
        return this.messages[lang]?.[key] || this.messages.ar[key] || key;
    },

    // التحقق من دعم ميزة معينة
    isFeatureSupported(feature) {
        // التحقق من دعم المتصفح
        const browserSupport = {
            notifications: 'Notification' in window,
            serviceWorker: 'serviceWorker' in navigator,
            vibration: 'vibrate' in navigator,
            badge: 'setAppBadge' in navigator,
            share: 'share' in navigator,
            pushNotifications: 'PushManager' in window
        };

        return browserSupport[feature] || false;
    },

    // الحصول على معلومات المنصة
    getPlatformInfo() {
        const isWebView = this.webview.detectMethods.some(method => method());
        const userAgent = navigator.userAgent;
        
        let platform = 'web';
        if (window.ReactNativeWebView) platform = 'react-native';
        else if (window.flutter_inappwebview) platform = 'flutter';
        else if (window.Android) platform = 'android';
        else if (window.webkit?.messageHandlers) platform = 'ios';
        else if (isWebView) platform = 'webview';

        return {
            platform,
            isWebView,
            userAgent,
            supportedFeatures: Object.keys(this.webview.platforms[platform]?.features || []),
            browserFeatures: Object.keys({
                notifications: this.isFeatureSupported('notifications'),
                serviceWorker: this.isFeatureSupported('serviceWorker'),
                vibration: this.isFeatureSupported('vibration'),
                badge: this.isFeatureSupported('badge'),
                share: this.isFeatureSupported('share'),
                pushNotifications: this.isFeatureSupported('pushNotifications')
            }).filter(key => this.isFeatureSupported(key))
        };
    }
};

// تحميل الإعدادات عند بدء التشغيل
NotificationConfig.loadSettings();

// تصدير للاستخدام العام
window.NotificationConfig = NotificationConfig;

// تصدير للاستخدام في modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationConfig;
}

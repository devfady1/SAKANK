/**
 * جسر التواصل مع التطبيقات الأصلية (WebView Bridge)
 * يدعم React Native, Flutter, Android WebView, iOS WKWebView
 */

class WebViewBridge {
    constructor() {
        this.platform = this.detectPlatform();
        this.callbacks = new Map();
        this.messageId = 0;
        this.init();
    }

    // كشف منصة التطبيق
    detectPlatform() {
        const userAgent = navigator.userAgent;
        
        if (window.ReactNativeWebView) {
            return 'react-native';
        } else if (window.flutter_inappwebview) {
            return 'flutter';
        } else if (window.Android && typeof window.Android.showNotification === 'function') {
            return 'android';
        } else if (window.webkit?.messageHandlers) {
            return 'ios';
        } else if (/wv|WebView/.test(userAgent)) {
            return 'webview';
        }
        
        return 'web';
    }

    // تهيئة الجسر
    init() {
        console.log(`WebView Bridge initialized for platform: ${this.platform}`);
        
        // إعداد مستمعات الرسائل حسب المنصة
        switch (this.platform) {
            case 'react-native':
                this.setupReactNative();
                break;
            case 'flutter':
                this.setupFlutter();
                break;
            case 'android':
                this.setupAndroid();
                break;
            case 'ios':
                this.setupiOS();
                break;
        }
    }

    // إعداد React Native WebView
    setupReactNative() {
        // استقبال الرسائل من React Native
        document.addEventListener('message', (event) => {
            this.handleNativeMessage(event.data);
        });
        
        window.addEventListener('message', (event) => {
            this.handleNativeMessage(event.data);
        });
    }

    // إعداد Flutter WebView
    setupFlutter() {
        // Flutter يستخدم callHandler للتواصل
        window.flutterMessageHandler = (message) => {
            this.handleNativeMessage(message);
        };
    }

    // إعداد Android WebView
    setupAndroid() {
        // Android WebView يستخدم JavaScript Interface
        window.androidMessageHandler = (message) => {
            this.handleNativeMessage(JSON.parse(message));
        };
    }

    // إعداد iOS WKWebView
    setupiOS() {
        // iOS يستخدم message handlers
        // الرسائل تأتي عبر webkit.messageHandlers
    }

    // معالجة الرسائل من التطبيق الأصلي
    handleNativeMessage(data) {
        try {
            const message = typeof data === 'string' ? JSON.parse(data) : data;
            
            switch (message.type) {
                case 'notification_permission':
                    this.handleNotificationPermission(message.granted);
                    break;
                case 'notification_clicked':
                    this.handleNotificationClick(message.data);
                    break;
                case 'app_state_changed':
                    this.handleAppStateChange(message.state);
                    break;
                case 'callback_response':
                    this.handleCallbackResponse(message);
                    break;
            }
        } catch (error) {
            console.error('Error handling native message:', error);
        }
    }

    // إرسال رسالة للتطبيق الأصلي
    sendToNative(type, data, callback) {
        const messageId = ++this.messageId;
        const message = {
            id: messageId,
            type,
            data,
            timestamp: Date.now()
        };

        // حفظ callback إذا وُجد
        if (callback) {
            this.callbacks.set(messageId, callback);
        }

        try {
            switch (this.platform) {
                case 'react-native':
                    window.ReactNativeWebView.postMessage(JSON.stringify(message));
                    break;
                    
                case 'flutter':
                    window.flutter_inappwebview.callHandler('webview_message', message);
                    break;
                    
                case 'android':
                    window.Android.handleWebViewMessage(JSON.stringify(message));
                    break;
                    
                case 'ios':
                    window.webkit.messageHandlers.webview.postMessage(message);
                    break;
                    
                default:
                    console.log('Native message (web fallback):', message);
                    // في المتصفح العادي، نستدعي callback مباشرة
                    if (callback) {
                        setTimeout(() => callback({ success: false, reason: 'not_native_app' }), 100);
                    }
            }
        } catch (error) {
            console.error('Error sending message to native:', error);
            if (callback) {
                callback({ success: false, error: error.message });
            }
        }
    }

    // طلب إذن الإشعارات من التطبيق
    requestNotificationPermission(callback) {
        this.sendToNative('request_notification_permission', {}, callback);
    }

    // إظهار إشعار في التطبيق الأصلي
    showNativeNotification(title, body, options = {}, callback) {
        const notificationData = {
            title,
            body,
            icon: options.icon || '/static/images/logo.png',
            sound: options.sound !== false,
            vibrate: options.vibrate !== false,
            data: options.data || {},
            actions: options.actions || []
        };

        this.sendToNative('show_notification', notificationData, callback);
    }

    // تحديث عداد الإشعارات في التطبيق
    updateAppBadge(count, callback) {
        this.sendToNative('update_badge', { count }, callback);
    }

    // تشغيل اهتزاز في التطبيق
    vibrate(pattern, callback) {
        this.sendToNative('vibrate', { pattern }, callback);
    }

    // تشغيل صوت في التطبيق
    playSound(soundName, callback) {
        this.sendToNative('play_sound', { sound: soundName }, callback);
    }

    // فتح رابط في التطبيق
    openUrl(url, callback) {
        this.sendToNative('open_url', { url }, callback);
    }

    // مشاركة محتوى
    share(title, text, url, callback) {
        this.sendToNative('share', { title, text, url }, callback);
    }

    // الحصول على معلومات الجهاز
    getDeviceInfo(callback) {
        this.sendToNative('get_device_info', {}, callback);
    }

    // معالجة إذن الإشعارات
    handleNotificationPermission(granted) {
        console.log('Notification permission:', granted);
        
        // تحديث حالة الإشعارات في النظام
        if (window.sakanakNotifications) {
            window.sakanakNotifications.notificationPermission = granted;
        }
        
        // إرسال حدث مخصص
        window.dispatchEvent(new CustomEvent('notificationPermissionChanged', {
            detail: { granted }
        }));
    }

    // معالجة النقر على الإشعار
    handleNotificationClick(data) {
        console.log('Notification clicked:', data);
        
        // فتح المحادثة إذا كان الإشعار خاص برسالة
        if (data.chatId) {
            window.location.href = `/bookings/chat/${data.chatId}/`;
        } else if (data.url) {
            window.location.href = data.url;
        }
        
        // إرسال حدث مخصص
        window.dispatchEvent(new CustomEvent('notificationClicked', {
            detail: data
        }));
    }

    // معالجة تغيير حالة التطبيق
    handleAppStateChange(state) {
        console.log('App state changed:', state);
        
        // إيقاف/تشغيل التحديثات التلقائية حسب حالة التطبيق
        if (window.sakanakNotifications) {
            if (state === 'background') {
                window.sakanakNotifications.pauseUpdates();
            } else if (state === 'active') {
                window.sakanakNotifications.resumeUpdates();
            }
        }
        
        // إرسال حدث مخصص
        window.dispatchEvent(new CustomEvent('appStateChanged', {
            detail: { state }
        }));
    }

    // معالجة رد callback
    handleCallbackResponse(message) {
        const callback = this.callbacks.get(message.id);
        if (callback) {
            callback(message.data);
            this.callbacks.delete(message.id);
        }
    }

    // التحقق من دعم الميزات
    isFeatureSupported(feature) {
        if (this.platform === 'web') return false;
        
        const supportedFeatures = {
            'react-native': ['notifications', 'vibration', 'sound', 'badge', 'share'],
            'flutter': ['notifications', 'vibration', 'sound', 'badge', 'share'],
            'android': ['notifications', 'vibration', 'sound', 'badge'],
            'ios': ['notifications', 'vibration', 'sound', 'badge', 'share'],
            'webview': ['notifications']
        };
        
        return supportedFeatures[this.platform]?.includes(feature) || false;
    }

    // الحصول على معلومات المنصة
    getPlatformInfo() {
        return {
            platform: this.platform,
            isNativeApp: this.platform !== 'web',
            userAgent: navigator.userAgent,
            supportedFeatures: this.getSupportedFeatures()
        };
    }

    // الحصول على الميزات المدعومة
    getSupportedFeatures() {
        const features = ['notifications', 'vibration', 'sound', 'badge', 'share'];
        return features.filter(feature => this.isFeatureSupported(feature));
    }
}

// إنشاء مثيل عام
window.webViewBridge = new WebViewBridge();

// تصدير للاستخدام في modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebViewBridge;
}

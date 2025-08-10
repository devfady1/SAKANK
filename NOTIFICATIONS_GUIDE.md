# دليل نظام الإشعارات المتقدم - تطبيق سكنك

## نظرة عامة

تم تطوير نظام إشعارات متقدم وشامل لتطبيق سكنك يدعم:
- **المتصفحات العادية** مع إشعارات المتصفح الأصلية
- **تطبيقات WebView** (React Native, Flutter, Android, iOS)
- **Service Worker** للإشعارات المتقدمة والعمل في الخلفية
- **الإشعارات الصوتية والاهتزازية**
- **التحديث التلقائي للرسائل**

## الملفات المطلوبة

### 1. ملفات JavaScript الأساسية
```
static/js/
├── notifications.js          # النظام الأساسي للإشعارات
├── webview-bridge.js        # جسر التواصل مع التطبيقات الأصلية
├── notification-config.js   # إعدادات النظام
├── sw.js                   # Service Worker
└── payment-status.js       # فحص حالة الدفع
```

### 2. ملفات الأصوات (يجب إضافتها)
```
static/sounds/
├── message.mp3         # صوت الرسائل الجديدة
├── notification.mp3    # صوت الإشعارات العامة
├── error.mp3          # صوت الأخطاء
└── success.mp3        # صوت النجاح
```

### 3. ملفات الصور (يجب إضافتها)
```
static/images/
├── logo.png           # شعار التطبيق للإشعارات
└── badge.png         # أيقونة الشارة
```

## كيفية الاستخدام

### 1. في صفحات HTML

```html
<!-- تضمين الملفات المطلوبة -->
<script src="{% static 'js/notification-config.js' %}"></script>
<script src="{% static 'js/webview-bridge.js' %}"></script>
<script src="{% static 'js/notifications.js' %}"></script>

<!-- تهيئة النظام -->
<script>
document.addEventListener('DOMContentLoaded', function() {
    // إنشاء مثيل من نظام الإشعارات
    window.sakanakNotifications = new SakanakNotifications();
    
    // طلب إذن الإشعارات
    window.sakanakNotifications.requestPermission();
    
    // تسجيل Service Worker
    window.sakanakNotifications.registerServiceWorker();
});
</script>
```

### 2. إرسال إشعار

```javascript
// إشعار بسيط
window.sakanakNotifications.showNotification(
    'رسالة جديدة',
    'لديك رسالة جديدة من أحمد',
    {
        icon: '/static/images/logo.png',
        data: { chatId: 123 }
    }
);

// إشعار مع صوت واهتزاز
window.sakanakNotifications.showNotification(
    'رسالة مهمة',
    'رسالة عاجلة تحتاج للرد',
    {
        sound: true,
        vibrate: true,
        type: 'message'
    }
);
```

### 3. التحكم في الإعدادات

```javascript
// تعطيل الأصوات
NotificationConfig.saveSettings({ soundEnabled: false });

// تعطيل الاهتزاز
NotificationConfig.saveSettings({ vibrationEnabled: false });

// تغيير فترة التحديث
NotificationConfig.saveSettings({ updateInterval: 5000 });
```

## الميزات المتقدمة

### 1. دعم WebView للتطبيقات المحمولة

النظام يكتشف تلقائياً إذا كان يعمل داخل WebView ويستخدم الجسر المناسب:

```javascript
// React Native
if (window.ReactNativeWebView) {
    // استخدام React Native bridge
}

// Flutter
if (window.flutter_inappwebview) {
    // استخدام Flutter bridge
}

// Android WebView
if (window.Android) {
    // استخدام Android interface
}

// iOS WKWebView
if (window.webkit?.messageHandlers) {
    // استخدام iOS message handlers
}
```

### 2. Service Worker للإشعارات المتقدمة

```javascript
// تسجيل Service Worker
navigator.serviceWorker.register('/static/js/sw.js')
    .then(registration => {
        console.log('Service Worker registered');
    });

// إرسال push notification
registration.showNotification('عنوان الإشعار', {
    body: 'محتوى الإشعار',
    icon: '/static/images/logo.png',
    badge: '/static/images/badge.png',
    actions: [
        { action: 'view', title: 'عرض' },
        { action: 'dismiss', title: 'إغلاق' }
    ]
});
```

### 3. التحديث التلقائي للرسائل

```javascript
// في صفحة المحادثة
setInterval(() => {
    if (!window.sakanakNotifications.areUpdatesPaused()) {
        checkForNewMessages();
    }
}, NotificationConfig.settings.updateInterval);

// في صفحة قائمة المحادثات
setInterval(() => {
    if (!window.sakanakNotifications.areUpdatesPaused()) {
        updateChatsList();
    }
}, NotificationConfig.settings.chatListUpdateInterval);
```

## إعداد التطبيقات المحمولة

### React Native

```javascript
// في التطبيق الأصلي
const onMessage = (event) => {
    const data = JSON.parse(event.nativeEvent.data);
    
    if (data.type === 'show_notification') {
        // إظهار إشعار أصلي
        PushNotification.localNotification({
            title: data.data.title,
            message: data.data.body,
            playSound: data.data.sound,
            vibrate: data.data.vibrate
        });
    }
};

<WebView
    source={{ uri: 'https://yourapp.com' }}
    onMessage={onMessage}
    javaScriptEnabled={true}
/>
```

### Flutter

```dart
// في التطبيق الأصلي
InAppWebViewController? webViewController;

void handleWebViewMessage(String message) {
    final data = jsonDecode(message);
    
    if (data['type'] == 'show_notification') {
        // إظهار إشعار أصلي
        FlutterLocalNotificationsPlugin().show(
            0,
            data['data']['title'],
            data['data']['body'],
            NotificationDetails(...)
        );
    }
}

InAppWebView(
    onWebViewCreated: (controller) {
        webViewController = controller;
        controller.addJavaScriptHandler(
            handlerName: 'webview_message',
            callback: (args) => handleWebViewMessage(args[0])
        );
    }
)
```

## استكشاف الأخطاء

### 1. الإشعارات لا تعمل

```javascript
// التحقق من دعم الإشعارات
if (!('Notification' in window)) {
    console.log('المتصفح لا يدعم الإشعارات');
}

// التحقق من الإذن
if (Notification.permission === 'denied') {
    console.log('تم رفض إذن الإشعارات');
}
```

### 2. الأصوات لا تعمل

```javascript
// التحقق من تحميل الأصوات
Object.keys(NotificationConfig.sounds).forEach(type => {
    const audio = new Audio(NotificationConfig.sounds[type]);
    audio.addEventListener('canplaythrough', () => {
        console.log(`صوت ${type} جاهز`);
    });
    audio.addEventListener('error', (e) => {
        console.log(`خطأ في تحميل صوت ${type}:`, e);
    });
});
```

### 3. Service Worker لا يعمل

```javascript
// التحقق من تسجيل Service Worker
navigator.serviceWorker.getRegistrations().then(registrations => {
    console.log('Service Workers المسجلة:', registrations.length);
});

// التحقق من الأخطاء
navigator.serviceWorker.addEventListener('error', event => {
    console.error('Service Worker error:', event);
});
```

## الأمان والخصوصية

### 1. تشفير البيانات الحساسة

```javascript
// تفعيل تشفير البيانات الحساسة
NotificationConfig.saveSettings({
    security: {
        encryptSensitiveData: true,
        hideContentInNotifications: true
    }
});
```

### 2. التحقق من المصدر

```javascript
// التحقق من صحة مصدر الإشعار
function validateNotificationSource(data) {
    return data.source === 'sakanak_app' && 
           data.timestamp > Date.now() - 60000; // خلال آخر دقيقة
}
```

## الاختبار

### 1. اختبار الإشعارات

```javascript
// اختبار إشعار بسيط
window.sakanakNotifications.showNotification(
    'اختبار',
    'هذا إشعار تجريبي',
    { test: true }
);

// اختبار جميع أنواع الأصوات
['message', 'notification', 'error', 'success'].forEach(type => {
    setTimeout(() => {
        window.sakanakNotifications.playSound(type);
    }, 1000);
});
```

### 2. اختبار WebView

```javascript
// اختبار كشف WebView
console.log('Platform info:', window.webViewBridge?.getPlatformInfo());

// اختبار إرسال رسالة للتطبيق الأصلي
window.webViewBridge?.sendToNative('test', { message: 'Hello from WebView' });
```

## التحديثات المستقبلية

- [ ] دعم Push Notifications من الخادم
- [ ] تحليلات الإشعارات
- [ ] إشعارات ذكية حسب السلوك
- [ ] دعم الإشعارات الصوتية المخصصة
- [ ] واجهة إعدادات متقدمة للمستخدم

## الدعم الفني

للحصول على المساعدة أو الإبلاغ عن مشاكل:
1. تحقق من console المتصفح للأخطاء
2. تأكد من تحميل جميع الملفات المطلوبة
3. تحقق من إعدادات المتصفح للإشعارات
4. اختبر في متصفحات مختلفة

---

**ملاحظة**: هذا النظام مصمم ليكون متوافقاً مع جميع المتصفحات الحديثة وتطبيقات WebView، مما يضمن تجربة موحدة عبر جميع المنصات.

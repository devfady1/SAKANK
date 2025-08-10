# إعداد Stripe Webhooks لمشروع سكنك

## المشكلة
بعد الدفع عبر Stripe، حالة الدفع لا تتحديث تلقائياً في النظام.

## الحل المطبق

### 1. إصلاح إعدادات Stripe
- تم تحديث `STRIPE_WEBHOOK_SECRET` في settings.py ليقرأ من متغير البيئة
- تم توحيد العملة لتكون EGP في جميع أنحاء النظام

### 2. تحسين Webhook Handler
- تم إضافة معالجة أفضل لأحداث `checkout.session.completed`
- تم إضافة logging مفصل لتتبع العمليات
- تم إضافة حماية من معالجة نفس الحدث مرتين

### 3. إضافة نظام احتياطي
- تم إنشاء دالة `check_payment_status` للتحقق اليدوي من حالة الدفع
- تم إضافة JavaScript للتحقق التلقائي كل 3 ثوانٍ
- تم تحسين صفحة النجاح لتعرض معلومات مفصلة

## خطوات الإعداد المطلوبة

### 1. إعداد Webhook في Stripe Dashboard
1. اذهب إلى [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. انقر على "Add endpoint"
3. أضف URL: `https://yourdomain.com/payments/webhook/`
4. اختر الأحداث التالية:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. انسخ "Signing secret" وأضفه في ملف .env

### 2. تحديث ملف .env
```env
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here
```

### 3. للتطوير المحلي (اختياري)
يمكنك استخدام Stripe CLI لاختبار webhooks محلياً:
```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

## كيف يعمل النظام الآن

### 1. عند الدفع الناجح
- Stripe يرسل `checkout.session.completed` webhook
- النظام يحديث حالة الحجز إلى "paid" و "confirmed"
- يتم إنشاء سجل دفع في قاعدة البيانات

### 2. النظام الاحتياطي
- إذا فشل webhook، صفحة النجاح تتحقق مباشرة من Stripe
- JavaScript يتحقق تلقائياً كل 3 ثوانٍ من حالة الدفع
- يمكن استخدام `/payments/check-payment-status/` للتحقق اليدوي

### 3. Logging
- جميع عمليات Stripe يتم تسجيلها في `stripe_payments.log`
- يمكن متابعة العمليات في console أيضاً

## اختبار النظام
1. قم بإجراء دفعة تجريبية
2. تحقق من logs في console أو ملف `stripe_payments.log`
3. تأكد من تحديث حالة الحجز في قاعدة البيانات
4. تحقق من صفحة النجاح تعرض المعلومات الصحيحة

## ملاحظات مهمة
- تأكد من أن STRIPE_WEBHOOK_SECRET محدث في ملف .env
- في بيئة الإنتاج، استخدم HTTPS للـ webhook URL
- يمكن تعطيل التحقق من webhook signature في التطوير (موجود في الكود)

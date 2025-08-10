# سكنك - منصة حجز الشقق

منصة ويب كاملة لحجز الشقق باللغة العربية مع دعم RTL، مبنية باستخدام Django 5 و Bootstrap 5.

## المميزات

### 🏠 للمستخدمين العاديين (المشترين)
- تصفح الشقق المتاحة مع البحث والفلترة
- عرض تفاصيل الشقق مع معرض الصور
- حجز الأسرة المتاحة
- نظام دفع آمن باستخدام Stripe
- متابعة حالة الحجوزات

### 🏢 للبائعين
- نظام تحقق من الهوية (رفع البطاقة ووثيقة الملكية)
- لوحة تحكم لإدارة الشقق
- إضافة شقق جديدة مع الصور
- إدارة الغرف والأسرة
- متابعة الحجوزات والأرباح

### 🛠️ المميزات التقنية
- واجهة عربية كاملة مع دعم RTL
- تصميم متجاوب (Responsive) لجميع الأجهزة
- نظام مصادقة متقدم مع أنواع مستخدمين مختلفة
- معالجة الدفعات الآمنة عبر Stripe
- نظام إدارة شامل للمحتوى

## التقنيات المستخدمة

- **Backend**: Django 5.2, Python 3.10
- **Frontend**: Bootstrap 5 RTL, HTML5, CSS3, JavaScript
- **Database**: SQLite (قابل للترقية لـ PostgreSQL)
- **Payment**: Stripe API
- **Media**: Django Media Files
- **Authentication**: Django Auth مع نموذج مستخدم مخصص

## التثبيت والتشغيل

### المتطلبات
- Python 3.10 أو أحدث
- pip (مدير حزم Python)

### خطوات التثبيت

1. **استنساخ المشروع**
```bash
git clone <repository-url>
cd sakanak
```

2. **إنشاء البيئة الافتراضية**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# أو
source .venv/bin/activate  # Linux/Mac
```

3. **تثبيت المتطلبات**
```bash
pip install -r requirements.txt
```

4. **إعداد متغيرات البيئة**
```bash
# إنشاء ملف .env وتعديل القيم
cp .env.example .env
```

5. **إنشاء قاعدة البيانات**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **إنشاء مدير النظام**
```bash
python manage.py createsuperuser
```

7. **إنشاء البيانات التجريبية (اختياري)**
```bash
python create_sample_data.py
```

8. **تشغيل الخادم**
```bash
python manage.py runserver
```

الآن يمكنك الوصول للموقع على: http://127.0.0.1:8000

## إعداد Stripe

1. إنشاء حساب على [Stripe](https://stripe.com)
2. الحصول على مفاتيح API من لوحة تحكم Stripe
3. تحديث ملف `.env` بالمفاتيح:
```
STRIPE_PUBLIC_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## هيكل المشروع

```
sakanak/
├── accounts/           # إدارة المستخدمين والتحقق
├── listings/          # الشقق والغرف والأسرة
├── bookings/          # نظام الحجوزات
├── payments/          # معالجة الدفعات
├── pages/             # الصفحات العامة
├── templates/         # قوالب HTML
├── static/            # الملفات الثابتة
├── media/             # الملفات المرفوعة
└── manage.py
```

## النماذج الرئيسية

### User (المستخدم)
- نموذج مستخدم مخصص مع نوعين: مشتري وبائع
- حقول إضافية: نوع الحساب، الهاتف، حالة التحقق

### Location (الموقع)
- المواقع الثابتة للشقق
- اسم الموقع والمدينة

### Apartment (الشقة)
- معلومات الشقة الأساسية
- مرتبطة بالموقع والمالك

### Room (الغرفة)
- غرف الشقة مع عدد الأسرة
- صورة ووصف للغرفة

### Bed (السرير)
- الأسرة المتاحة للحجز
- السعر والحالة (متاح/محجوز/صيانة)

### Booking (الحجز)
- حجوزات المستخدمين
- مرتبطة بالسرير والمستخدم

## بيانات تسجيل الدخول التجريبية

بعد تشغيل `create_sample_data.py`:

- **البائع**: `seller1` / `password123`
- **المشتري**: `buyer1` / `password123`
- **المدير**: `admin` / `admin123`

## الصفحات الرئيسية

- `/` - الصفحة الرئيسية
- `/listings/` - قائمة الشقق
- `/listings/apartment/<id>/` - تفاصيل الشقة
- `/accounts/login/` - تسجيل الدخول
- `/accounts/signup/` - إنشاء حساب
- `/accounts/verification/` - التحقق للبائعين
- `/listings/seller/dashboard/` - لوحة تحكم البائع
- `/bookings/my-bookings/` - حجوزات المستخدم
- `/admin/` - لوحة الإدارة

## الأمان

- حماية CSRF على جميع النماذج
- تشفير كلمات المرور
- تحقق من صحة البيانات
- حماية الملفات المرفوعة
- معالجة آمنة للدفعات

## المساهمة

1. Fork المشروع
2. إنشاء branch جديد (`git checkout -b feature/amazing-feature`)
3. Commit التغييرات (`git commit -m 'Add amazing feature'`)
4. Push للـ branch (`git push origin feature/amazing-feature`)
5. فتح Pull Request

## الترخيص

هذا المشروع مرخص تحت رخصة MIT - راجع ملف [LICENSE](LICENSE) للتفاصيل.

## الدعم

للحصول على الدعم أو الإبلاغ عن مشاكل:
- فتح issue على GitHub
- التواصل عبر البريد الإلكتروني: support@sakanak.com

## الإصدارات القادمة

- [ ] تطبيق موبايل
- [ ] نظام تقييمات ومراجعات
- [ ] خرائط تفاعلية
- [ ] نظام إشعارات
- [ ] تقارير مالية متقدمة
- [ ] دعم عملات متعددة

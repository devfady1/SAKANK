# دليل إعداد نظام المصادقة والتسجيل 🔐

## نظرة عامة

تم إعداد نظام مصادقة شامل يتضمن:
- ✅ **تسجيل الدخول بجوجل**
- ✅ **إنشاء حساب جديد**
- ✅ **نسيان كلمة المرور**
- ✅ **تأكيد البريد الإلكتروني**
- ✅ **تسجيل الخروج**

## الملفات المُنشأة

### القوالب (Templates)
```
templates/account/
├── login.html                    # تسجيل الدخول
├── signup.html                   # إنشاء حساب جديد
├── logout.html                   # تسجيل الخروج
├── password_reset.html           # نسيان كلمة المرور
├── password_reset_done.html      # تأكيد إرسال رابط الاستعادة
├── password_reset_from_key.html  # إعادة تعيين كلمة المرور
├── password_reset_from_key_done.html # تأكيد تغيير كلمة المرور
├── email_confirm.html            # تأكيد البريد الإلكتروني
└── verification_sent.html        # تأكيد إرسال رابط التفعيل
```

### ملفات الإعداد
```
├── .env.example                  # مثال على متغيرات البيئة
└── AUTHENTICATION_SETUP.md       # هذا الدليل
```

## خطوات الإعداد

### 1. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` وأضف القيم الصحيحة:

```bash
cp .env.example .env
```

### 2. إعداد Gmail للبريد الإلكتروني

1. **تفعيل التحقق بخطوتين** في حساب Gmail
2. **إنشاء كلمة مرور التطبيق**:
   - اذهب إلى: https://myaccount.google.com/security
   - اختر "App passwords"
   - أنشئ كلمة مرور جديدة للتطبيق
3. **أضف البيانات في ملف .env**:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-character-app-password
   ```

### 3. إعداد Google OAuth

1. **اذهب إلى Google Cloud Console**:
   - https://console.cloud.google.com/

2. **إنشاء مشروع جديد** أو اختيار مشروع موجود

3. **تفعيل Google+ API**:
   - اذهب إلى "APIs & Services" > "Library"
   - ابحث عن "Google+ API" وفعلها

4. **إنشاء OAuth 2.0 credentials**:
   - اذهب إلى "APIs & Services" > "Credentials"
   - انقر "Create Credentials" > "OAuth 2.0 Client IDs"
   - اختر "Web application"
   - أضف Authorized redirect URIs:
     ```
     http://127.0.0.1:8000/accounts/google/login/callback/
     http://localhost:8000/accounts/google/login/callback/
     ```

5. **أضف البيانات في ملف .env**:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id.googleusercontent.com
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
   ```

### 4. إعداد قاعدة البيانات

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. إنشاء Social Application في Django Admin

1. **تشغيل الخادم**:
   ```bash
   python manage.py runserver
   ```

2. **إنشاء superuser**:
   ```bash
   python manage.py createsuperuser
   ```

3. **الدخول إلى Admin Panel**:
   - اذهب إلى: http://127.0.0.1:8000/admin/

4. **إضافة Social Application**:
   - اذهب إلى "Social Applications" > "Add"
   - املأ البيانات:
     - **Provider**: Google
     - **Name**: Google OAuth
     - **Client id**: نسخ من Google Cloud Console
     - **Secret key**: نسخ من Google Cloud Console
     - **Sites**: اختر "example.com" (Site ID: 1)

## الميزات المتاحة

### 1. تسجيل الدخول
- **URL**: `/accounts/login/`
- **الميزات**:
  - تسجيل دخول عادي بالبريد/اسم المستخدم
  - تسجيل دخول بجوجل
  - خيار "تذكرني"
  - رابط نسيان كلمة المرور

### 2. إنشاء حساب جديد
- **URL**: `/accounts/signup/`
- **الميزات**:
  - إنشاء حساب عادي
  - إنشاء حساب بجوجل
  - تأكيد البريد الإلكتروني مطلوب
  - التحقق من تطابق كلمات المرور

### 3. نسيان كلمة المرور
- **URL**: `/accounts/password/reset/`
- **الميزات**:
  - إرسال رابط الاستعادة بالبريد
  - صفحة تأكيد الإرسال
  - صفحة إعادة تعيين كلمة المرور
  - صفحة تأكيد التغيير

### 4. تأكيد البريد الإلكتروني
- **تلقائي** عند إنشاء حساب جديد
- **إجباري** لتفعيل الحساب
- **إعادة إرسال** الرابط متاحة

## الأمان والحماية

### الميزات المُفعلة:
- ✅ **تحديد محاولات تسجيل الدخول**: 5 محاولات كحد أقصى
- ✅ **مهلة زمنية**: 5 دقائق بعد المحاولات الفاشلة
- ✅ **تأكيد البريد الإلكتروني إجباري**
- ✅ **كلمة مرور قوية**: 8 أحرف كحد أدنى
- ✅ **اسم مستخدم فريد**: 3 أحرف كحد أدنى
- ✅ **حماية CSRF** في جميع النماذج

## اختبار النظام

### 1. تسجيل الدخول العادي
```
1. اذهب إلى: http://127.0.0.1:8000/accounts/login/
2. أدخل بيانات المستخدم
3. تحقق من تسجيل الدخول بنجاح
```

### 2. تسجيل الدخول بجوجل
```
1. انقر على "تسجيل الدخول بجوجل"
2. اختر حساب Google
3. تحقق من إنشاء/تسجيل دخول المستخدم
```

### 3. إنشاء حساب جديد
```
1. اذهب إلى: http://127.0.0.1:8000/accounts/signup/
2. املأ البيانات المطلوبة
3. تحقق من إرسال بريد التأكيد
4. انقر على رابط التأكيد في البريد
```

### 4. نسيان كلمة المرور
```
1. اذهب إلى: http://127.0.0.1:8000/accounts/password/reset/
2. أدخل البريد الإلكتروني
3. تحقق من إرسال رابط الاستعادة
4. انقر على الرابط وأدخل كلمة مرور جديدة
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها:

#### 1. خطأ في إرسال البريد الإلكتروني
```
الحل:
- تأكد من صحة بيانات Gmail في .env
- تأكد من تفعيل "App Password"
- تحقق من إعدادات الأمان في Gmail
```

#### 2. خطأ Google OAuth
```
الحل:
- تأكد من صحة Client ID و Secret
- تأكد من إضافة Redirect URIs الصحيحة
- تأكد من إنشاء Social Application في Admin
```

#### 3. خطأ في تأكيد البريد
```
الحل:
- تأكد من تشغيل الخادم على نفس العنوان
- تحقق من إعدادات SITE_ID في settings.py
- تأكد من وجود Site في Django Admin
```

## التخصيص

### تغيير تصميم القوالب:
```html
<!-- يمكنك تعديل ملفات HTML في مجلد templates/account/ -->
<!-- جميع القوالب تستخدم Bootstrap 5 RTL -->
```

### إضافة حقول إضافية:
```python
# في accounts/forms.py
# أضف حقول مخصصة لنموذج التسجيل
```

### تخصيص رسائل البريد:
```python
# في settings.py
# يمكن تخصيص قوالب البريد الإلكتروني
```

## الدعم والمساعدة

### الوثائق المرجعية:
- [Django Allauth Documentation](https://django-allauth.readthedocs.io/)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

### ملاحظات مهمة:
1. **لا تشارك ملف .env** مع أي شخص
2. **استخدم HTTPS في الإنتاج** لحماية البيانات
3. **راجع إعدادات الأمان** بانتظام
4. **احتفظ بنسخة احتياطية** من قاعدة البيانات

---

🎉 **تم الانتهاء من الإعداد!** نظام المصادقة جاهز للاستخدام بجميع ميزاته.

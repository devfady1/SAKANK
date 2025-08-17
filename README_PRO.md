<div align="center">

# 🏠 سكني | Sakany

Arabic-first, RTL-friendly apartment booking platform built with Django 5 + Bootstrap 5 RTL. Clean design, strong security, Stripe payments, chat, and seller verification.

<!-- Badges -->

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-0C4B33?logo=django&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5_RTL-7952B3?logo=bootstrap&logoColor=white)
![Stripe](https://img.shields.io/badge/Stripe-Integrated-635BFF?logo=stripe&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue.svg)

</div>

---

## ✨ Highlights

- 🎯 Arabic UX, full RTL support, mobile-first
- 👤 Auth via Django-Allauth (Email + Google)
- 🧾 Seller KYC: ID + Ownership docs, admin review, contract acceptance
- 🏘️ Listings: apartments → rooms → beds hierarchy, galleries, categories
- 📅 Booking flows with per-bed commission model
- 💬 Chat between buyer and seller per booking
- 💳 Stripe integration + Webhook + manual payment (Vodafone Cash)
- 🔔 Notifications-ready frontend (Service Worker/audio hooks in place)
- 🧰 Clean architecture and maintainable codebase

---

## 🧭 Table of Contents

- Overview
- Architecture
- Project Structure
- Data Model (ERD)
- Key Screens & URLs
- Setup & Run
- Environment Variables
- Stripe Setup
- Sample Data
- Security
- Testing
- Roadmap

---

## 🗺️ Overview

Sakanak delivers a polished Arabic booking experience with a minimal header (الرئيسية، الشقق، تواصل معنا), professional purple/blue gradients, modern cards, and clean typography—optimized for trust and conversions.

Design language is centralized in `templates/base.html` and reused across pages and custom error templates: `templates/errors/400.html`, `403.html`, `404.html`, `500.html`.

---

## 🧩 Architecture

```
Browser (RTL UI, Bootstrap 5 RTL)
   │
   ├─ Pages app (index, contact)
   ├─ Listings app (apartments, rooms, beds)
   ├─ Bookings app (booking lifecycle, chat)
   ├─ Accounts app (custom User, seller verification, middleware)
   └─ Payments app (Stripe, webhook, manual payments)
          │
          └─ Stripe API / Webhooks
```

- URL routing entrypoint: `sakanak/urls.py`
- Global settings: `sakanak/settings.py`
- Templates root: `templates/`
- Static assets: `static/` (compiled into `staticfiles/`)

---

## 🗂️ Project Structure

```
.
├── accounts/              # Custom user, KYC, middleware, auth views
│   ├── models.py          # User, SellerVerification
│   ├── views.py           # Auth/profile/verification flows
│   ├── forms.py           # Auth/verification forms
│   ├── urls.py
│   └── middleware.py      # SellerAccessControlMiddleware
├── listings/              # Apartments → Rooms → Beds
│   ├── models.py          # Location, Apartment, ApartmentImage, Room, Bed
│   ├── views.py           # List/detail/seller dashboard
│   └── forms.py
├── bookings/              # Bookings and chat
│   ├── models.py          # Booking, BookingOrder, Message
│   ├── views.py           # Booking flow + chat
│   └── forms.py
├── payments/              # Stripe + manual payments
│   ├── models.py          # Payment, WebhookEvent, ManualPayment
│   ├── views.py           # Stripe intents, webhook, success/cancel
│   └── urls.py
├── pages/
│   ├── views.py           # IndexView, ContactView
│   └── urls.py
├── templates/
│   ├── base.html          # Global layout/styles
│   ├── errors/400|403|404|500.html
│   ├── accounts/, listings/, bookings/, pages/
├── static/
│   ├── images/, css/, js/, sounds/
├── sakanak/
│   ├── settings.py, urls.py, wsgi.py, asgi.py
└── manage.py
```

---

## 🗃️ Data Model (ERD)

```
User (AbstractUser)
  ├─ user_type: buyer|seller
  ├─ is_verified, phone
  └─ contract_accepted, contract_accepted_at, contract_accepted_ip
      │
      └─ SellerVerification (OneToOne)
           ├─ id_card_image, ownership_document
           └─ status: pending|approved|rejected (+reason, timestamps)

Location ──< Apartment ──< Room ──< Bed
                           │            └─ status: available|booked|maintenance
                           └─ ApartmentImage (*), category: bathroom|kitchen|living|other

Booking (*)
  ├─ user → User
  ├─ bed  → Bed
  ├─ status: pending|confirmed|cancelled|completed
  ├─ payment_status: pending|paid|failed|refunded
  └─ order → BookingOrder (optional)

BookingOrder (*)
  └─ user → User, status, total_amount

Payment (OneToOne → Booking)
  ├─ stripe_payment_intent_id, stripe_charge_id
  ├─ amount, currency, status, fees, net
  └─ failure_reason

WebhookEvent (*)
ManualPayment (OneToOne → Booking)
```

---

## 🔗 Key Screens & URLs

- `/` الصفحة الرئيسية (بحث، مواقع، شقق مميزة)
- `/listings/` قائمة الشقق + فلترة
- `/listings/apartment/<id>/` تفاصيل الشقة + معرض صور
- `/bookings/book/<bed_id>/` الحجز
- `/bookings/chat/<booking_id>/` المحادثة
- `/bookings/user-chats/` كل المحادثات
- `/payments/create-payment-intent/` إنشاء نية دفع
- `/payments/confirm-payment/` تأكيد الدفع
- `/payments/success/` نجاح الدفع | `/payments/cancel/` إلغاء
- `/accounts/login|signup|logout` حسابات
- `/accounts/password/reset/` إعادة تعيين كلمة المرور
- `/accounts/verification/` تحقق البائع (KYC)
- `/admin/` لوحة الإدارة (Jazzmin Dark)

Custom error pages (HTML, gradient): 400, 403, 404, 500 via handlers in `sakanak/urls.py`.

---

## ⚙️ Setup & Run

```bash
# 1) Create & activate venv
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # Linux/Mac

# 2) Install deps
pip install -r requirements.txt

# 3) Apply migrations
python manage.py makemigrations
python manage.py migrate

# 4) Create superuser
python manage.py createsuperuser

# 5) (Optional) Load sample data
python create_sample_data.py

# 6) Run server
python manage.py runserver
```

Open http://127.0.0.1:8000

---

## 🔐 Environment Variables (.env)

```
SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000

# Email (dev uses console backend unless overridden)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
DEFAULT_FROM_EMAIL=

# Stripe
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

---

## 💳 Stripe Setup (quick)

- Add keys to `.env`.
- Ensure webhook endpoint points to: `/payments/webhook/` with the correct secret.
- Frontend uses `https://js.stripe.com/v3/` loaded in `templates/base.html`.

For full guide, see `STRIPE_SETUP.md`.

---

## 🧪 Testing (quick)

- Use `python manage.py test` for unit tests.
- Manual flows:
  - Accounts (signup/login/logout/password reset)
  - Listings browse/detail
  - Booking + payment (Stripe test cards)
  - Manual payment approval → booking status update
  - Chat send/receive

---

## 🛡️ Security

Enabled in `sakanak/settings.py` and app logic:

- CSRF on all forms
- Allauth login attempt limits & timeout
- Strong password policy (8+)
- Email verification mandatory
- Seller KYC workflow + admin review
- Secure Stripe payment handling + webhook verification

---

## 🧱 Design System (RTL + Clean)

- Minimal header: الرئيسية، الشقق، تواصل معنا
- Professional purple/blue gradients
- Modern cards with subtle hover/blur
- Clean typography (Cairo font)
- Responsive grid, mobile-first containers

Base template: `templates/base.html`

---

## 🎬 Motion & Micro-Interactions

While GitHub README cannot run CSS animations, the UI implements:

- Reveal-on-scroll and counters (inlined scripts in `base.html`)
- Button/card hover transitions
- Navbar blur & shadow

Embed your product GIFs/screens in this section for marketing:

```text
[ Place demo GIFs here ]
- Home search interactions
- Apartment detail + gallery
- Booking & payment
- Chat flow
```

---

## 📦 Deployment Notes

- Set `DEBUG=False` and configure `ALLOWED_HOSTS` + `CSRF_TRUSTED_ORIGINS`.
- Collect static files if using WhiteNoise/host provider.
- Configure email backend for production.
- Configure Stripe webhook on production domain.

---

## 📌 Roadmap (excerpt)

- Mobile app (WebView + push bridge)
- Ratings & reviews
- Interactive maps
- Advanced finance reports
- Multi-currency support

---

## 📄 License

MIT

"""
إعدادات URLs لمشروع سكنك
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import ProfileView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.utils.html import escape

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    # alias غير منصوص عليها بالأسماء لتفادي NoReverseMatch لمن يستخدم 'profile' بدون namespace
    path('accounts/profile/', ProfileView.as_view(), name='profile'),
    path('listings/', include('listings.urls')),
    path('bookings/', include('bookings.urls')),
    path('payments/', include('payments.urls')),
]

# ----------------------------------------
# Custom error handlers (responsive, RTL)
# ----------------------------------------

def _error_html(title: str, message: str, code: int) -> str:
    return f"""
<!doctype html>
<html lang=\"ar\" dir=\"rtl\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no\">
  <title>{escape(title)}</title>
  <link href=\"https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.rtl.min.css\" rel=\"stylesheet\">
  <link href=\"https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css\" rel=\"stylesheet\">
  <style>
    body{background:#faf7f3;font-family:'Cairo',sans-serif;color:#333}
    .wrap{max-width:720px;margin:10vh auto;padding:16px}
    .card{border:none;border-radius:14px;box-shadow:0 4px 20px rgba(0,0,0,.08)}
    .code{font-weight:800;font-size:2.5rem;color:#e67e22}
    .btn{border-radius:12px}
  </style>
</head>
<body>
  <div class=\"wrap\">
    <div class=\"card\">
      <div class=\"card-body p-4 text-center\">
        <div class=\"code mb-2\">{code}</div>
        <h5 class=\"fw-bold mb-2\">{escape(title)}</h5>
        <p class=\"text-muted mb-4\">{escape(message)}</p>
        <div class=\"d-grid gap-2 d-sm-flex justify-content-sm-center\">
          <a href=\"/\" class=\"btn btn-primary\"><i class=\"fa fa-home ms-1\"></i>الصفحة الرئيسية</a>
          <a href=\"javascript:history.back()\" class=\"btn btn-outline-secondary\">رجوع</a>
          <a href=\"/pages/contact/\" class=\"btn btn-outline-dark\"><i class=\"fa fa-envelope ms-1\"></i>تواصل معنا</a>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

def error_400(request, exception=None):
    html = _error_html("طلب غير صالح", "عذراً، الطلب الذي أرسلته غير صحيح.", 400)
    return HttpResponse(html, status=400)


def error_403(request, exception=None):
    html = _error_html("غير مسموح", "لا تملك صلاحية للوصول إلى هذه الصفحة.", 403)
    return HttpResponse(html, status=403)


def error_404(request, exception=None):
    html = _error_html("الصفحة غير موجودة", "يبدو أنك حاولت فتح رابط غير موجود.", 404)
    return HttpResponse(html, status=404)


def error_500(request):
    html = _error_html("خطأ في الخادم", "حدث خطأ غير متوقع. برجاء المحاولة لاحقاً.", 500)
    return HttpResponse(html, status=500)

# Wire Django handlers (use dotted paths referencing this module)
handler400 = 'sakanak.urls.error_400'
handler403 = 'sakanak.urls.error_403'
handler404 = 'sakanak.urls.error_404'
handler500 = 'sakanak.urls.error_500'

# إضافة URLs للملفات الثابتة والوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

"""
إعدادات URLs لمشروع سكنك
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import ProfileView
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

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

"""
# ----------------------------------------
# Custom error handlers rendering HTML templates
# ----------------------------------------
"""

def error_400(request, exception=None):
    context = {
        "code": 400,
        "title": "طلب غير صالح",
        "message": "عذراً، الطلب الذي أرسلته غير صحيح.",
    }
    return render(request, "errors/400.html", context=context, status=400)


def error_403(request, exception=None):
    context = {
        "code": 403,
        "title": "غير مسموح",
        "message": "لا تملك صلاحية للوصول إلى هذه الصفحة.",
    }
    return render(request, "errors/403.html", context=context, status=403)


def error_404(request, exception=None):
    context = {
        "code": 404,
        "title": "الصفحة غير موجودة",
        "message": "يبدو أنك حاولت فتح رابط غير موجود.",
    }
    return render(request, "errors/404.html", context=context, status=404)


def error_500(request):
    context = {
        "code": 500,
        "title": "خطأ في الخادم",
        "message": "حدث خطأ غير متوقع. برجاء المحاولة لاحقاً.",
    }
    return render(request, "errors/500.html", context=context, status=500)

# Wire Django handlers (use dotted paths referencing this module)
handler400 = 'sakanak.urls.error_400'
handler403 = 'sakanak.urls.error_403'
handler404 = 'sakanak.urls.error_404'
handler500 = 'sakanak.urls.error_500'

# إضافة URLs للملفات الثابتة والوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

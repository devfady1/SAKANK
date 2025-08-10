"""
إعدادات URLs لمشروع سكنك
"""
from django.contrib import admin
from django.urls import path, include
from accounts.views import ProfileView
from django.conf import settings
from django.conf.urls.static import static

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

# إضافة URLs للملفات الثابتة والوسائط في وضع التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

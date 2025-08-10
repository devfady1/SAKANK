from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from accounts.models import SellerVerification

class SellerAccessControlMiddleware:
    """
    يمنع البائع من الوصول لأي صفحة إلا بعد تحقق البطاقة، الملكية، والموافقة على العقد
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # تحقق فقط للبائعين
        if request.user.is_authenticated and getattr(request.user, 'user_type', None) == 'seller':
            # استثني صفحات التحقق والعقد وتسجيل الخروج
            allowed_paths = [
                reverse('accounts:seller_verification'),
                reverse('accounts:seller_contract'),
                reverse('accounts:logout'),
                reverse('accounts:seller_pending'),
            ]
            # استثني صفحات الأدمن
            if request.path.startswith('/admin/'):
                return self.get_response(request)
            # تحقق من حالة العقد
            if not request.user.contract_accepted:
                if request.path not in allowed_paths:
                    return redirect('accounts:seller_contract')
            # تحقق من حالة التحقق
            try:
                verification = SellerVerification.objects.get(seller=request.user)
                if verification.status != 'approved':
                    if request.path not in allowed_paths:
                        return redirect('accounts:seller_pending')
            except SellerVerification.DoesNotExist:
                if request.path not in allowed_paths:
                    return redirect('accounts:seller_verification')
        return self.get_response(request)

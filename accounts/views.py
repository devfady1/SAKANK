from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView
from django.contrib.auth.views import (
    LoginView as DjangoLoginView, LogoutView as DjangoLogoutView,
    PasswordResetView as DjangoPasswordResetView,
    PasswordResetDoneView as DjangoPasswordResetDoneView,
    PasswordResetConfirmView as DjangoPasswordResetConfirmView,
    PasswordResetCompleteView as DjangoPasswordResetCompleteView
)
class PasswordResetView(DjangoPasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = '/accounts/password-reset/done/'

class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class PasswordResetConfirmView(DjangoPasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/accounts/reset/done/'

class PasswordResetCompleteView(DjangoPasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

# Google login placeholder
class GoogleLoginView(TemplateView):
    template_name = 'accounts/google_login.html'
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import SignupForm, LoginForm, SellerVerificationForm
from .models import SellerVerification
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils import timezone

class SignupView(FormView):
    """صفحة إنشاء حساب جديد"""
    template_name = 'accounts/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, 'تم إنشاء حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
        
        # إذا كان البائع، توجيهه لصفحة التحقق
        if user.user_type == 'seller':
            messages.info(self.request, 'يرجى رفع مستندات التحقق لتفعيل حسابك كبائع.')
            self.success_url = reverse_lazy('accounts:seller_verification')
        
        return super().form_valid(form)

@login_required
def seller_contract(request):
    user = request.user
    if user.user_type != 'seller':
        return redirect('pages:index')
    if user.contract_accepted:
        return redirect('listings:seller_dashboard')
    contract_text = '''عقد شراكة منصة سكنك\n\nالطرف الأول: منصة سكنك\nالطرف الثاني: {} ("المالك")\n\nمقدمة:\nحيث إن الطرف الأول يدير منصة إلكترونية لربط الطلاب بالوحدات السكنية، وحيث يرغب الطرف الثاني في عرض وحداته السكنية عبر المنصة، فقد اتفق الطرفان على ما يلي:\n\nالبند 1 – الغرض من العقد:\nيلتزم المالك بعرض وحداته السكنية من خلال المنصة وعدم إتمام أي تعاقد أو اتفاق مع أي طالب وصل إليه عن طريق المنصة خارج النظام.\n\nالبند 2 – العمولة:\nيتقاضى الطرف الأول عمولة قدرها (%[نسبة العمولة]) من قيمة الإيجار أو الحجز المتفق عليه مع الطالب.\nيتم استحقاق العمولة بمجرد تأكيد الحجز عبر المنصة، ويلتزم المالك بسدادها فورًا.\n\nالبند 3 – حظر التجاوز:\nيمنع على المالك التواصل المباشر أو تسليم بيانات الاتصال لأي طالب قبل إتمام الحجز أو دفع العربون من خلال المنصة.\nفي حال إثبات تجاوز المالك، يحق للطرف الأول فرض غرامة مالية لا تقل عن (%[قيمة الغرامة]) من قيمة الحجز.\n\nالبند 4 – البيانات:\nيحتفظ الطرف الأول بحق إخفاء بيانات الاتصال الخاصة بالمالك لحين إتمام الدفع، على أن يتم إظهارها تلقائيًا بعد ذلك.\n\nالبند 5 – حل النزاعات:\nفي حالة حدوث أي نزاع بين المالك والطالب، يتم الرجوع إلى سجلات المحادثات المحفوظة داخل المنصة كدليل رئيسي.\n\nالبند 6 – أحكام عامة:\n\nهذا العقد ملزم قانونيًا للطرفين.\n\nلا يجوز تعديل أي بند إلا بموافقة مكتوبة من الطرفين.\n\nيخضع هذا العقد لقوانين الدولة التي تعمل بها المنصة.\n\nبالتوقيع الإلكتروني أدناه، يقر المالك بقراءة جميع البنود والموافقة عليها.\n\nالتوقيع الإلكتروني: ___________________\nالاسم: {}\nالتاريخ: ___________________'''.format(user.get_full_name(), user.get_full_name())
    if request.method == 'POST':
        user.contract_accepted = True
        user.contract_accepted_at = timezone.now()
        user.contract_accepted_ip = request.META.get('REMOTE_ADDR', '')
        user.save()
        return redirect('listings:seller_dashboard')
    return render(request, 'accounts/seller_contract.html', {'contract_text': contract_text})
class LoginView(DjangoLoginView):
    """صفحة تسجيل الدخول"""
    template_name = 'accounts/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # توجيه المستخدم حسب نوع الحساب
        if hasattr(self.request.user, 'user_type') and self.request.user.user_type == 'seller':
            return reverse_lazy('listings:seller_dashboard')
        return reverse_lazy('pages:index')


class LogoutView(DjangoLogoutView):
    """تسجيل الخروج"""
    next_page = reverse_lazy('pages:index')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'تم تسجيل خروجك بنجاح.')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """صفحة ملف المستخدم"""
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user_obj'] = user
        return context

class SellerVerificationView(LoginRequiredMixin, FormView):
    """صفحة التحقق من البائع"""
    template_name = 'accounts/seller_verification.html'
    form_class = SellerVerificationForm
    success_url = reverse_lazy('accounts:seller_verification')
    
    def dispatch(self, request, *args, **kwargs):
        # التحقق من تسجيل الدخول أولاً
        if not request.user.is_authenticated:
            messages.error(request, 'يجب تسجيل الدخول أولاً.')
            return redirect('accounts:login')
        
        # التأكد من أن المستخدم بائع
        if request.user.user_type != 'seller':
            messages.error(request, 'هذه الصفحة مخصصة للبائعين فقط.')
            return redirect('pages:index')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            verification = SellerVerification.objects.get(seller=self.request.user)
            context['verification'] = verification
        except SellerVerification.DoesNotExist:
            context['verification'] = None
        return context
    
    def form_valid(self, form):
        # إنشاء أو تحديث طلب التحقق
        verification, created = SellerVerification.objects.get_or_create(
            seller=self.request.user,
            defaults={
                'id_card_image': form.cleaned_data['id_card_image'],
                'ownership_document': form.cleaned_data['ownership_document'],
            }
        )
        
        if not created:
            # تحديث الطلب الموجود
            verification.id_card_image = form.cleaned_data['id_card_image']
            verification.ownership_document = form.cleaned_data['ownership_document']
            verification.status = 'pending'
            verification.save()
        
        messages.success(self.request, 'تم رفع مستندات التحقق بنجاح. سيتم مراجعتها خلال 24-48 ساعة.')
        return super().form_valid(form)

@login_required
def seller_pending(request):
    return render(request, 'accounts/seller_pending.html')

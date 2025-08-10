from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import SellerVerification

User = get_user_model()


class SignupForm(UserCreationForm):
    """نموذج إنشاء حساب جديد"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'البريد الإلكتروني'
        })
    )
    
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'رقم الهاتف (اختياري)'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='نوع الحساب'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'user_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المستخدم'
            }),
        }
        labels = {
            'username': 'اسم المستخدم',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة المرور'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'تأكيد كلمة المرور'
        })
        self.fields['password1'].label = 'كلمة المرور'
        self.fields['password2'].label = 'تأكيد كلمة المرور'


class LoginForm(AuthenticationForm):
    """نموذج تسجيل الدخول"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'اسم المستخدم'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'كلمة المرور'
        })
        self.fields['username'].label = 'اسم المستخدم'
        self.fields['password'].label = 'كلمة المرور'


class SellerVerificationForm(forms.ModelForm):
    """نموذج التحقق من البائع"""
    
    class Meta:
        model = SellerVerification
        fields = ['id_card_image', 'ownership_document']
        widgets = {
            'id_card_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ownership_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'id_card_image': 'صورة البطاقة الشخصية',
            'ownership_document': 'وثيقة الملكية',
        }

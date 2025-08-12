from django import forms
from .models import ManualPayment


class ManualPaymentForm(forms.ModelForm):
    class Meta:
        model = ManualPayment
        fields = [
            'amount',
            'sender_phone',
            'transaction_ref',
            'screenshot',
        ]
        labels = {
            'amount': 'المبلغ المدفوع',
            'sender_phone': 'رقم الهاتف الذي أرسل منه',
            'transaction_ref': 'رقم العملية (اختياري)',
            'screenshot': 'صورة إثبات الدفع',
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'sender_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '01XXXXXXXXX'}),
            'transaction_ref': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اختياري'}),
            'screenshot': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_sender_phone(self):
        phone = self.cleaned_data.get('sender_phone', '').strip()
        if not phone:
            raise forms.ValidationError('رقم الهاتف مطلوب')
        if not phone.startswith('01') or not phone.isdigit():
            raise forms.ValidationError('برجاء إدخال رقم هاتف صحيح يبدأ بـ 01')
        if len(phone) < 10 or len(phone) > 14:
            raise forms.ValidationError('طول الرقم غير صحيح')
        return phone

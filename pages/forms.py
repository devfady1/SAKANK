from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """نموذج التواصل"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'الاسم الكامل'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'البريد الإلكتروني'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم الهاتف (اختياري)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'موضوع الرسالة'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'نص الرسالة',
                'rows': 5
            }),
        }
        labels = {
            'name': 'الاسم',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الهاتف',
            'subject': 'الموضوع',
            'message': 'الرسالة',
        }

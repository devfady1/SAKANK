from django import forms
from .models import Booking
from datetime import date, timedelta


class BookingForm(forms.ModelForm):
    """نموذج الحجز"""
    
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date', 'notes']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': (date.today() + timedelta(days=30)).isoformat()
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'ملاحظات إضافية (اختياري)',
                'rows': 3
            }),
        }
        labels = {
            'start_date': 'تاريخ البداية',
            'end_date': 'تاريخ النهاية',
            'notes': 'ملاحظات',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية.')
            
            if start_date < date.today():
                raise forms.ValidationError('تاريخ البداية لا يمكن أن يكون في الماضي.')
            
            # الحد الأدنى شهر واحد
            if (end_date - start_date).days < 30:
                raise forms.ValidationError('الحد الأدنى للحجز هو شهر واحد.')
        
        return cleaned_data

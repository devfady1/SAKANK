from django import forms
from .models import Apartment, Room, Location, Bed


class ApartmentForm(forms.ModelForm):
    """نموذج إضافة شقة"""
    
    class Meta:
        model = Apartment
        fields = ['name', 'location', 'description', 'main_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم الشقة'
            }),
            'location': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الشقة',
                'rows': 4
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        labels = {
            'name': 'اسم الشقة',
            'location': 'الموقع',
            'description': 'الوصف',
            'main_image': 'الصورة الرئيسية',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(is_active=True)


class RoomForm(forms.ModelForm):
    """نموذج إضافة غرفة"""
    
    bed_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='سعر السرير الشهري',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'السعر بالريال',
            'step': '0.01'
        })
    )
    
    class Meta:
        model = Room
        fields = ['name', 'bed_count', 'room_image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم أو رقم الغرفة'
            }),
            'bed_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الأسرة',
                'min': '1',
                'max': '10'
            }),
            'room_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الغرفة (اختياري)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'اسم الغرفة',
            'bed_count': 'عدد الأسرة',
            'room_image': 'صورة الغرفة',
            'description': 'الوصف',
        }


class RoomUpdateForm(forms.ModelForm):
    """نموذج تعديل الغرفة (بدون إنشاء أسرة جديدة)"""

    class Meta:
        model = Room
        fields = ['name', 'room_image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم أو رقم الغرفة'
            }),
            'room_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الغرفة (اختياري)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'اسم الغرفة',
            'room_image': 'صورة الغرفة',
            'description': 'الوصف',
        }


class BedForm(forms.ModelForm):
    """نموذج تعديل السرير"""

    class Meta:
        model = Bed
        fields = ['bed_number', 'monthly_price', 'status']
        widgets = {
            'bed_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رقم السرير'
            }),
            'monthly_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'السعر الشهري',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'bed_number': 'رقم السرير',
            'monthly_price': 'السعر الشهري',
            'status': 'الحالة',
        }


class RoomWithPriceForm(forms.ModelForm):
    """نموذج غرفة مخصص للاستخدام داخل Inline Formset مع حقل سعر السرير"""

    bed_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='سعر السرير الشهري',
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'السعر بالريال',
            'step': '0.01'
        })
    )

    class Meta:
        model = Room
        fields = ['name', 'bed_count', 'room_image', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم أو رقم الغرفة'
            }),
            'bed_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'عدد الأسرة',
                'min': '1',
                'max': '10'
            }),
            'room_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'وصف الغرفة (اختياري)',
                'rows': 3
            }),
        }
        labels = {
            'name': 'اسم الغرفة',
            'bed_count': 'عدد الأسرة',
            'room_image': 'صورة الغرفة',
            'description': 'الوصف',
        }

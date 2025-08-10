from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """نموذج المستخدم المخصص مع دعم نوعين: مشتري وبائع"""
    
    USER_TYPE_CHOICES = [
        ('buyer', 'مشتري'),
        ('seller', 'بائع'),
    ]
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='buyer',
        verbose_name='نوع الحساب'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='رقم الهاتف'
    )
    
    is_verified = models.BooleanField(
        default=False,
        verbose_name='تم التحقق'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
        # حقول العقد الإلزامي لصاحب السكن
    contract_accepted = models.BooleanField(default=False, verbose_name='تمت الموافقة على العقد')
    contract_accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الموافقة على العقد')
    contract_accepted_ip = models.CharField(max_length=45, null=True, blank=True, verbose_name='IP الموافقة على العقد')
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمون'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class SellerVerification(models.Model):
    """نموذج التحقق من البائع"""
    
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'تم الموافقة'),
        ('rejected', 'مرفوض'),
    ]
    
    seller = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='verification',
        verbose_name='البائع'
    )
    
    id_card_image = models.ImageField(
        upload_to='verifications/id_cards/',
        verbose_name='صورة البطاقة الشخصية'
    )
    
    ownership_document = models.ImageField(
        upload_to='verifications/ownership/',
        verbose_name='وثيقة الملكية'
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='حالة التحقق'
    )
    
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='سبب الرفض'
    )
    
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ التقديم'
    )
    
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاريخ المراجعة'
    )
    
    class Meta:
        verbose_name = 'طلب تحقق بائع'
        verbose_name_plural = 'طلبات تحقق البائعين'
    
    def __str__(self):
        return f"تحقق {self.seller.username} - {self.get_status_display()}"

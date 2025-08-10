from django.db import models
from django.contrib.auth import get_user_model
from bookings.models import Booking

User = get_user_model()

class Payment(models.Model):
    """نموذج الدفعة"""
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('processing', 'قيد المعالجة'),
        ('succeeded', 'نجح'),
        ('failed', 'فشل'),
        ('cancelled', 'ملغي'),
        ('refunded', 'مسترد'),
    ]
    
    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='payment',
        verbose_name='الحجز'
    )
    
    stripe_payment_intent_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='معرف نية الدفع'
    )
    
    stripe_charge_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='معرف الشحن'
    )
    
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ'
    )
    
    currency = models.CharField(
        max_length=3,
        default='SAR',
        verbose_name='العملة'
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الدفع'
    )
    
    stripe_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='رسوم Stripe'
    )
    
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='المبلغ الصافي'
    )
    
    failure_reason = models.TextField(
        blank=True,
        verbose_name='سبب الفشل'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاريخ التحديث'
    )
    
    class Meta:
        verbose_name = 'دفعة'
        verbose_name_plural = 'الدفعات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"دفعة {self.booking.user.username} - {self.amount} {self.currency}"


class WebhookEvent(models.Model):
    """نموذج أحداث Webhook من Stripe"""
    
    stripe_event_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='معرف الحدث'
    )
    
    event_type = models.CharField(
        max_length=50,
        verbose_name='نوع الحدث'
    )
    
    processed = models.BooleanField(
        default=False,
        verbose_name='تم المعالجة'
    )
    
    data = models.JSONField(
        verbose_name='بيانات الحدث'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإنشاء'
    )
    
    class Meta:
        verbose_name = 'حدث Webhook'
        verbose_name_plural = 'أحداث Webhook'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.event_type} - {self.stripe_event_id}"

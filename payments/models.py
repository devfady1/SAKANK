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


class ManualPayment(models.Model):
    """دفعة يدوية (فودافون كاش)."""

    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name='manual_payment',
        verbose_name='الحجز'
    )

    method = models.CharField(
        max_length=30,
        default='vodafone_cash',
        verbose_name='طريقة الدفع'
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ المدفوع'
    )

    sender_phone = models.CharField(
        max_length=20,
        verbose_name='رقم المرسل'
    )

    transaction_ref = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='رقم العملية/المرجع (اختياري)'
    )

    screenshot = models.ImageField(
        upload_to='manual_payments/',
        verbose_name='صورة إثبات الدفع'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='الحالة'
    )

    admin_notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات المشرف'
    )

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_manual_payments',
        verbose_name='تمت المراجعة بواسطة'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ المراجعة')

    class Meta:
        verbose_name = 'دفعة يدوية'
        verbose_name_plural = 'دفعات يدوية'
        ordering = ['-created_at']

    def __str__(self):
        return f"Manual {self.method} - {self.booking_id} - {self.amount}"

    def save(self, *args, **kwargs):
        """عند اعتماد الدفعة اليدوية، حدّث حالة الحجز إلى مدفوع."""
        prev_status = None
        if self.pk:
            try:
                prev_status = ManualPayment.objects.only('status').get(pk=self.pk).status
            except ManualPayment.DoesNotExist:
                prev_status = None
        super().save(*args, **kwargs)
        # إذا أصبحت الحالة معتمدة، حدّث حالة الحجز للدفع والتأكيد
        if self.status == 'approved' and self.booking:
            changed = False
            if self.booking.payment_status != 'paid':
                self.booking.payment_status = 'paid'
                changed = True
            if self.booking.status != 'cancelled' and self.booking.status != 'confirmed':
                self.booking.status = 'confirmed'
                changed = True
            if changed:
                self.booking.save(update_fields=['payment_status', 'status'])

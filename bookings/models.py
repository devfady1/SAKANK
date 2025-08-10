from django.conf import settings
from django.db import models
from listings.models import Bed

User = settings.AUTH_USER_MODEL

class Booking(models.Model):
    """نموذج الحجز"""
    
    STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('confirmed', 'مؤكد'),
        ('cancelled', 'ملغي'),
        ('completed', 'مكتمل'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'في الانتظار'),
        ('paid', 'مدفوع'),
        ('failed', 'فشل'),
        ('refunded', 'مسترد'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='المستخدم'
    )
    
    bed = models.ForeignKey(
        Bed,
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name='السرير'
    )
    
    start_date = models.DateField(
        verbose_name='تاريخ البداية'
    )
    
    end_date = models.DateField(
        verbose_name='تاريخ النهاية'
    )
    
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر الشهري'
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='المبلغ الإجمالي'
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الحجز'
    )
    
    payment_status = models.CharField(
        max_length=15,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending',
        verbose_name='حالة الدفع'
    )
    
    stripe_payment_intent_id = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='معرف نية الدفع في Stripe'
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name='ملاحظات'
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
        verbose_name = 'حجز'
        verbose_name_plural = 'الحجوزات'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"حجز {self.user.username} - {self.bed}"
    
    def save(self, *args, **kwargs):
        # تحديث حالة السرير عند تأكيد الحجز
        if self.status == 'confirmed' and self.payment_status == 'paid':
            self.bed.status = 'booked'
            self.bed.save()
        elif self.status == 'cancelled':
            self.bed.status = 'available'
            self.bed.save()
        super().save(*args, **kwargs)

class Message(models.Model):
    """نموذج الرسائل بين الطالب وصاحب السكن"""
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE, related_name='messages', verbose_name='الحجز')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', verbose_name='المرسل')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', verbose_name='المستقبل')
    text = models.TextField(verbose_name='نص الرسالة')
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإرسال')
    is_read = models.BooleanField(default=False, verbose_name='تمت القراءة')

    class Meta:
        ordering = ['sent_at']
        verbose_name = 'رسالة'
        verbose_name_plural = 'الرسائل'

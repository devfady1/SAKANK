from django.db import models

class ContactMessage(models.Model):
    """نموذج رسائل التواصل"""
    
    name = models.CharField(
        max_length=100,
        verbose_name='الاسم'
    )
    
    email = models.EmailField(
        verbose_name='البريد الإلكتروني'
    )
    
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='رقم الهاتف'
    )
    
    subject = models.CharField(
        max_length=200,
        verbose_name='الموضوع'
    )
    
    message = models.TextField(
        verbose_name='الرسالة'
    )
    
    is_read = models.BooleanField(
        default=False,
        verbose_name='تم القراءة'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاريخ الإرسال'
    )
    
    class Meta:
        verbose_name = 'رسالة تواصل'
        verbose_name_plural = 'رسائل التواصل'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Location(models.Model):
    """نموذج المواقع الثابتة"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='اسم الموقع'
    )
    
    city = models.CharField(
        max_length=50,
        verbose_name='المدينة'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
    )
    
    class Meta:
        verbose_name = 'موقع'
        verbose_name_plural = 'المواقع'
        ordering = ['city', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Apartment(models.Model):
    """نموذج الشقة"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='اسم الشقة'
    )
    
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        related_name='apartments',
        verbose_name='الموقع'
    )
    
    description = models.TextField(
        verbose_name='الوصف'
    )
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='apartments',
        verbose_name='المالك'
    )
    
    main_image = models.ImageField(
        upload_to='apartments/main/',
        verbose_name='الصورة الرئيسية'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='نشط'
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
        verbose_name = 'شقة'
        verbose_name_plural = 'الشقق'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.location.name}"
    
    def get_min_price(self):
        """الحصول على أقل سعر في الشقة"""
        min_price = self.rooms.aggregate(
            min_price=models.Min('beds__monthly_price')
        )['min_price']
        return min_price or 0
    
    def get_active_bookings_count(self):
        """عدد الحجوزات النشطة للشقة"""
        from bookings.models import Booking
        from django.utils import timezone
        
        active_bookings = 0
        for room in self.rooms.all():
            for bed in room.beds.all():
                active_bookings += Booking.objects.filter(
                    bed=bed,
                    end_date__gte=timezone.now().date(),
                    payment_status='paid'
                ).count()
        return active_bookings


class ApartmentImage(models.Model):
    """صور إضافية للشقة"""
    
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='الشقة'
    )
    
    image = models.ImageField(
        upload_to='apartments/gallery/',
        verbose_name='الصورة'
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='وصف الصورة'
    )
    
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='الترتيب'
    )
    
    class Meta:
        verbose_name = 'صورة شقة'
        verbose_name_plural = 'صور الشقق'
        ordering = ['order']
    
    def __str__(self):
        return f"صورة {self.apartment.name}"


class Room(models.Model):
    """نموذج الغرفة"""
    
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name='الشقة'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='اسم/رقم الغرفة'
    )
    
    bed_count = models.PositiveIntegerField(
        verbose_name='عدد الأسرة'
    )
    
    room_image = models.ImageField(
        upload_to='rooms/',
        blank=True,
        verbose_name='صورة الغرفة'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='وصف الغرفة'
    )
    
    class Meta:
        verbose_name = 'غرفة'
        verbose_name_plural = 'الغرف'
        unique_together = ['apartment', 'name']
    
    def __str__(self):
        return f"{self.apartment.name} - {self.name}"


class Bed(models.Model):
    """نموذج السرير"""
    
    STATUS_CHOICES = [
        ('available', 'متاح'),
        ('booked', 'محجوز'),
        ('maintenance', 'صيانة'),
    ]
    
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name='الغرفة'
    )
    
    bed_number = models.CharField(
        max_length=10,
        verbose_name='رقم السرير'
    )
    
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='السعر الشهري'
    )
    
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='الحالة'
    )
    
    class Meta:
        verbose_name = 'سرير'
        verbose_name_plural = 'الأسرة'
        unique_together = ['room', 'bed_number']
    
    def __str__(self):
        return f"{self.room} - سرير {self.bed_number}"
    
    @property
    def is_available(self):
        return self.status == 'available'

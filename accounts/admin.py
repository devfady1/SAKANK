from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SellerVerification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """إدارة المستخدمين المخصصة"""
    list_display = ('username', 'email', 'user_type', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('معلومات إضافية', {
            'fields': ('user_type', 'phone', 'is_verified')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('معلومات إضافية', {
            'fields': ('user_type', 'phone', 'email')
        }),
    )


@admin.register(SellerVerification)
class SellerVerificationAdmin(admin.ModelAdmin):
    """إدارة طلبات التحقق من البائعين"""
    list_display = ('seller', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('seller__username', 'seller__email')
    readonly_fields = ('submitted_at',)
    
    actions = ['approve_verification', 'reject_verification']
    
    def approve_verification(self, request, queryset):
        """الموافقة على طلبات التحقق"""
        from django.utils import timezone
        
        updated = queryset.update(
            status='approved',
            reviewed_at=timezone.now()
        )
        
        # تحديث حالة المستخدمين
        for verification in queryset:
            verification.seller.is_verified = True
            verification.seller.save()
        
        self.message_user(request, f'تم الموافقة على {updated} طلب.')
    
    approve_verification.short_description = 'الموافقة على الطلبات المحددة'
    
    def reject_verification(self, request, queryset):
        """رفض طلبات التحقق"""
        from django.utils import timezone
        
        updated = queryset.update(
            status='rejected',
            reviewed_at=timezone.now()
        )
        
        self.message_user(request, f'تم رفض {updated} طلب.')
    
    reject_verification.short_description = 'رفض الطلبات المحددة'

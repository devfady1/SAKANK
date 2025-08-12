from django.contrib import admin
from django.utils import timezone
from .models import Payment, WebhookEvent, ManualPayment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "currency", "status", "created_at")
    list_filter = ("status", "currency", "created_at")
    search_fields = ("booking__user__username", "stripe_payment_intent_id")
    readonly_fields = ("created_at", "updated_at")


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_type", "stripe_event_id", "processed", "created_at")
    list_filter = ("event_type", "processed", "created_at")
    search_fields = ("stripe_event_id",)


@admin.register(ManualPayment)
class ManualPaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "amount", "sender_phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("booking__user__username", "sender_phone", "transaction_ref")
    readonly_fields = ("created_at", "processed_at", "processed_by")
    actions = ("approve_manual_payments", "reject_manual_payments",)

    @admin.action(description="اعتماد الدفعات اليدوية المحددة وتحديث حالة الحجز لمدفوع")
    def approve_manual_payments(self, request, queryset):
        count = 0
        for mp in queryset.select_related("booking"):
            mp.status = 'approved'
            mp.processed_by = request.user
            mp.processed_at = timezone.now()
            mp.save(update_fields=["status", "processed_by", "processed_at"])

            booking = mp.booking
            booking.payment_status = 'paid'
            # اجعل الحجز مؤكدًا عند اعتماد الدفع اليدوي
            if booking.status != 'cancelled':
                booking.status = 'confirmed'
            booking.save(update_fields=["payment_status", "status"])
            count += 1
        self.message_user(request, f"تم اعتماد {count} دفعة وتحديث حالات الحجوزات.")

    @admin.action(description="رفض الدفعات اليدوية المحددة")
    def reject_manual_payments(self, request, queryset):
        updated = queryset.update(status='rejected', processed_at=timezone.now(), processed_by=request.user)
        self.message_user(request, f"تم رفض {updated} دفعات.")

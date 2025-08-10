from django.contrib import admin
from .models import Payment, WebhookEvent


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

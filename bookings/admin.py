from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("user", "bed", "start_date", "end_date", "status", "payment_status")
    list_filter = ("status", "payment_status", "created_at")
    search_fields = ("user__username", "bed__room__apartment__name", "bed__room__name")
    readonly_fields = ("created_at", "updated_at")

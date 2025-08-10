from django.contrib import admin
from .models import Location, Apartment, ApartmentImage, Room, Bed


class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 1
    fields = ("image", "caption", "order")


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ("name", "bed_count", "room_image")


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("name", "city")


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "owner", "is_active", "created_at")
    list_filter = ("location", "is_active", "created_at")
    search_fields = ("name", "description", "owner__username")
    readonly_fields = ("created_at", "updated_at")
    inlines = [ApartmentImageInline, RoomInline]


class BedInline(admin.TabularInline):
    model = Bed
    extra = 0
    fields = ("bed_number", "monthly_price", "status")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "apartment", "bed_count")
    list_filter = ("apartment",)
    search_fields = ("name", "apartment__name")
    inlines = [BedInline]


@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ("__str__", "monthly_price", "status")
    list_filter = ("status", "room__apartment")
    search_fields = ("room__name", "room__apartment__name", "bed_number")

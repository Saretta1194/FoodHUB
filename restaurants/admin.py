from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "is_active",
        "opening_hours",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "address", "owner__username", "owner__email")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

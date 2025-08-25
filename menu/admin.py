from django.contrib import admin
from .models import Dish


@admin.register(Dish)
class DishAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "available", "created_at")
    list_filter = ("available", "created_at", "restaurant")
    search_fields = ("name", "description", "restaurant__name")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("name",)

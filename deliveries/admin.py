from django.contrib import admin
from .models import Delivery, DeliveryEvent

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ("order", "rider", "status", "assigned_at", "updated_at")
    list_filter = ("status", "assigned_at", "updated_at")
    search_fields = ("order__id", "rider__username")

@admin.register(DeliveryEvent)
class DeliveryEventAdmin(admin.ModelAdmin):
    list_display = ("delivery", "event_type", "actor", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("delivery__order__id", "actor__username", "message")

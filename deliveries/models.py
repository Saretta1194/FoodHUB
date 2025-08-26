from django.conf import settings
from django.db import models
from django.utils import timezone
from orders.models import Order


class Delivery(models.Model):
    STATUS_ASSIGNED = "ASSIGNED"
    STATUS_PICKED_UP = "PICKED_UP"
    STATUS_DELIVERED = "DELIVERED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_ASSIGNED, "Assigned"),
        (STATUS_PICKED_UP, "Picked up"),
        (STATUS_DELIVERED, "Delivered"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery"
    )
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deliveries",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_ASSIGNED
    )
    assigned_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        rid = f"rider={self.rider.username}" if self.rider else "rider=None"
        return f"Delivery(order={self.order_id}, {rid}, status={self.status})"


class DeliveryEvent(models.Model):
    EVENT_ASSIGNED = "ASSIGNED"
    EVENT_STATUS_CHANGE = "STATUS_CHANGE"

    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name="events"
    )
    event_type = models.CharField(max_length=50)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at} - {self.event_type}"

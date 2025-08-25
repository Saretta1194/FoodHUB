from django.conf import settings
from django.db import models
from django.utils import timezone
from menu.models import Dish


class Order(models.Model):
    STATUS_CREATED = "CREATED"
    STATUS_PAID = "PAID"
    STATUS_PREPARING = "PREPARING"
    STATUS_DELIVERING = "DELIVERING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_PAID, "Paid"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_DELIVERING, "Delivering"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_CREATED)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Order #{self.pk} by {self.user} [{self.status}]"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    dish = models.ForeignKey(Dish, on_delete=models.PROTECT, related_name="order_items")
    dish_name = models.CharField(max_length=200)  # snapshot del nome
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)  # snapshot del prezzo
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish_name} x{self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

from django.conf import settings
from django.db import models
from django.utils import timezone
from menu.models import Dish
from restaurants.models import Restaurant



class Order(models.Model):
    STATUS_CREATED = "CREATED"
    STATUS_PAID = "PAID"
    STATUS_PREPARING = "PREPARING"
    STATUS_DELIVERING = "DELIVERING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_FLOW = [STATUS_CREATED, STATUS_PAID, 
                   STATUS_PREPARING, STATUS_DELIVERING,
                   STATUS_COMPLETED]
    STATUS_CHOICES = [
        (STATUS_CREATED, "Created"),
        (STATUS_PAID, "Paid"),
        (STATUS_PREPARING, "Preparing"),
        (STATUS_DELIVERING, "Delivering"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",)
    
    restaurant = models.ForeignKey(
        Restaurant, 
        on_delete=models.PROTECT, 
        related_name="orders",)
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} by {self.user} [{self.status}]"

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    def can_advance_to(self, next_status: str) -> bool:
        """Allow only forward transitions along STATUS_FLOW."""
        if self.status == self.STATUS_CANCELLED:
            return False
        try:
            cur = self.STATUS_FLOW.index(self.status)
            nxt = self.STATUS_FLOW.index(next_status)
        except ValueError:
            return False
        return nxt > cur  # strictly forward

    def advance_to(self, next_status: str) -> None:
        """Advance status if forward, else raise ValueError."""
        if not self.can_advance_to(next_status):
            raise ValueError("Invalid status transition")
        self.status = next_status
        self.save(update_fields=["status", "updated_at"])



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    dish = models.ForeignKey(
        Dish,
        on_delete=models.PROTECT,
        related_name="order_items"
    )

    dish_name = models.CharField(max_length=200)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.dish_name} x{self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

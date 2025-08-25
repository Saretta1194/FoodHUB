from django.db import models
from django.core.validators import MinValueValidator
from restaurants.models import Restaurant


class Dish(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        on_delete=models.CASCADE,
        related_name="dishes"
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    available = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="dishes/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.restaurant.name})"

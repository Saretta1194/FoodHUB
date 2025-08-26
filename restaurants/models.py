from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


opening_hours_validator = RegexValidator(
    regex=r"^\d{2}:\d{2}-\d{2}:\d{2}$",
    message="Opening hours must be in the format HH:MM-HH:MM (e.g., 09:00-18:00).",
)


class Restaurant(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurants",
    )
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=255)
    opening_hours = models.CharField(
        max_length=20,
        validators=[opening_hours_validator],
        help_text="Format: HH:MM-HH:MM (e.g., 09:00-18:00).",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.owner})"

from django import forms
from .models import Restaurant

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ["name", "address", "opening_hours", "is_active", "description", "cover_image"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Restaurant name"}),
            "address": forms.TextInput(attrs={"placeholder": "Street, City"}),
            "opening_hours": forms.TextInput(attrs={"placeholder": "09:00-18:00"}),
            "description": forms.Textarea(attrs={"placeholder": "Short description", "rows": 3}),
        }
        labels = {
            "opening_hours": "Opening hours (e.g. 09:00-18:00)",
            "cover_image": "Cover image",
        }

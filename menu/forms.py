from django import forms
from .models import Dish

class DishForm(forms.ModelForm):
    class Meta:
        model = Dish
        fields = ["name", "description", "price", "available", "photo"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Dish name"}),
            "description": forms.Textarea(attrs={"placeholder": "Describe the dish...", "rows": 3}),
            "price": forms.NumberInput(attrs={"placeholder": "Price (€)", "step": "0.01", "min": "0.01"}),
        }
        labels = {
            "photo": "Dish photo",
        }

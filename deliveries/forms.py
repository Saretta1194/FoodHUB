from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class AssignRiderForm(forms.Form):
    rider = forms.ModelChoiceField(
        queryset=User.objects.filter(is_active=True),
        required=True,
        help_text="Select a rider to assign",
        label="Rider",
    )

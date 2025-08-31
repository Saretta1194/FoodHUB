# deliveries/forms.py
from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()

def rider_queryset():
    """
    Return a sensible queryset of riders.
    Prefer users in 'riders' group; fallback to non-staff actives.
    """
    qs = User.objects.all()
    try:
        return User.objects.filter(groups__name__iexact="riders", is_active=True).order_by("username")
    except Exception:
        return User.objects.filter(is_active=True, is_staff=False).order_by("username")

class AssignRiderForm(forms.Form):
    rider = forms.ModelChoiceField(
        label="Rider",
        queryset=rider_queryset(),
        required=True,
        widget=forms.Select(attrs={"class": "form-select"})
    )

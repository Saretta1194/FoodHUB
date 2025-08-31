from django.shortcuts import render
from restaurants.models import Restaurant

def home(request):
    restaurants = Restaurant.objects.filter(is_active=True)[:6]
    return render(request, "core/home.html", {"restaurants": restaurants})

 
from django.urls import path
from . import views

app_name = "restaurants"

urlpatterns = [
    path("my/", views.OwnerRestaurantListView.as_view(), name="owner_list"),
    path("my/create/", views.RestaurantCreateView.as_view(), name="create"),
    path("my/<int:pk>/edit/", views.RestaurantUpdateView.as_view(), name="edit"),
    path("my/<int:pk>/delete/", views.RestaurantDeleteView.as_view(), name="delete"),
]

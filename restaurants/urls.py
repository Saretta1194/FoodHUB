from django.urls import path
from . import views

app_name = "restaurants"

urlpatterns = [
    # --- Owner dashboard ---
    path("my/", views.OwnerRestaurantListView.as_view(), name="owner_list"),
    path("my/create/", views.OwnerRestaurantCreateView.as_view(), name="owner_create"),
    path(
        "my/<int:pk>/edit/", views.RestaurantUpdateView.as_view(), name="owner_update"
    ),
    path(
        "my/<int:pk>/delete/",
        views.RestaurantDeleteView.as_view(),
        name="owner_delete",
    ),
    # --- Public ---
    path("", views.RestaurantListView.as_view(), name="public_list"),
    path("<int:pk>/", views.RestaurantDetailView.as_view(), name="public_detail"),
]

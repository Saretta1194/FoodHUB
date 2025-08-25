from django.urls import path
from . import views

app_name = "menu"

urlpatterns = [
    path("<int:restaurant_id>/dishes/", views.DishListView.as_view(), name="dish_list"),
    path("<int:restaurant_id>/dishes/create/", views.DishCreateView.as_view(), name="dish_create"),
    path("dishes/<int:pk>/edit/", views.DishUpdateView.as_view(), name="dish_edit"),
    path("dishes/<int:pk>/delete/", views.DishDeleteView.as_view(), name="dish_delete"),
]

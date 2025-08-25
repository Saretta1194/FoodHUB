from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:dish_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:dish_id>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:dish_id>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.order_success, name="order_success"),
]

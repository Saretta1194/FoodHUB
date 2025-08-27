from django.urls import path
from .views import (
    OwnerOrderListView,
    OwnerOrderDetailView,
    OwnerOrderPrepareView,
)

from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:dish_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:dish_id>/", views.cart_remove, name="cart_remove"),
    path("cart/update/<int:dish_id>/", views.cart_update, name="cart_update"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "success/<int:order_id>/",
        views.order_success,
        name="order_success",
    ),
    # Owner
    path("owner/", OwnerOrderListView.as_view(), name="owner_orders"),
    path(
        "owner/<int:pk>/", OwnerOrderDetailView.as_view(), name="owner_detail"
    ),
    path(
        "owner/<int:pk>/prepare/",
        OwnerOrderPrepareView.as_view(),
        name="owner_prepare",
    ),
    # Client
    path("my/", views.my_orders, name="my_orders"),
    path("my/<int:pk>/", views.customer_order_detail, name="customer_order_detail"),
    path("my/<int:pk>/status.json", views.customer_order_status_json, name="customer_order_status_json"),
]

# orders/urls.py
from django.urls import path
from .views import (
    OwnerOrderListView,
    OwnerOrderDetailView,
    OwnerOrderPrepareView,
    cart_detail,
    cart_add,
    cart_remove,
    cart_update,
    checkout,
    order_success,
    my_orders,
    customer_order_detail,
    customer_order_status_json,
    export_orders_csv,
)

app_name = "orders"  # <-- IMPORTANTISSIMO

urlpatterns = [
    # Owner
    path("owner/", OwnerOrderListView.as_view(), name="owner_list"),
    path("owner/<int:pk>/", OwnerOrderDetailView.as_view(), name="owner_detail"),  # <--
    path(
        "owner/<int:pk>/prepare/",
        OwnerOrderPrepareView.as_view(),
        name="owner_order_prepare",
    ),
    # Customer
    path("my/", my_orders, name="my_orders"),
    path("my/<int:pk>/", customer_order_detail, name="customer_order_detail"),
    path(
        "my/<int:pk>/status.json",
        customer_order_status_json,
        name="customer_order_status_json",
    ),
    # Cart + checkout
    path("cart/", cart_detail, name="cart_detail"),
    path("cart/add/<int:dish_id>/", cart_add, name="cart_add"),
    path("cart/remove/<int:dish_id>/", cart_remove, name="cart_remove"),
    path("cart/update/<int:dish_id>/", cart_update, name="cart_update"),
    path("checkout/", checkout, name="checkout"),
    path("success/<int:order_id>/", order_success, name="order_success"),
    # Export CSV (staff)
    path("export.csv", export_orders_csv, name="export_orders_csv"),
]

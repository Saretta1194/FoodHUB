from django.urls import path, include
from . import views
from .views import (
    RiderDeliveryDetailView,
    RiderMarkPickedUpView,
    RiderMarkDeliveredView,
)

app_name = "deliveries"

urlpatterns = [
    path("operator/queue/", views.operator_queue, name="operator_queue"),
    path(
        "operator/assign/<int:pk>/",
        views.operator_assign,
        name="operator_assign",
    ),
    path("rider/", views.rider_deliveries, name="rider_deliveries"),
    path(
        "rider/delivery/<int:pk>/",
        RiderDeliveryDetailView.as_view(),
        name="rider_detail",
    ),
    path(
        "rider/delivery/<int:pk>/picked/",
        RiderMarkPickedUpView.as_view(),
        name="rider_mark_picked",
    ),
    path(
        "rider/delivery/<int:pk>/delivered/",
        RiderMarkDeliveredView.as_view(),
        name="rider_mark_delivered",
    ),
]

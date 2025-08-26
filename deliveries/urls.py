from django.urls import path
from . import views

app_name = "deliveries"

urlpatterns = [
    path("operator/queue/", views.operator_queue, name="operator_queue"),
    path(
        "operator/assign/<int:order_id>/",
        views.assign_rider,
        name="assign_rider",
    ),
    path("rider/", views.rider_deliveries, name="rider_deliveries"),
]

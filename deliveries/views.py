from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from orders.models import Order
from .models import Delivery, DeliveryEvent
from .forms import AssignRiderForm

@staff_member_required
def operator_queue(request):
    """List orders without a delivery yet (CREATED/PREPARING)."""
    qs = Order.objects.filter(
        status__in=[Order.STATUS_CREATED, Order.STATUS_PREPARING],
    ).exclude(delivery__isnull=False).order_by("-created_at")
    return render(request, "deliveries/operator_queue.html", {"orders": qs})

@staff_member_required
def assign_rider(request, order_id):
    """Assign a rider to an order, create Delivery and log event."""
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        form = AssignRiderForm(request.POST)
        if form.is_valid():
            rider = form.cleaned_data["rider"]

            delivery, _ = Delivery.objects.get_or_create(order=order)
            delivery.rider = rider
            delivery.status = Delivery.STATUS_ASSIGNED
            delivery.save()

            DeliveryEvent.objects.create(
                delivery=delivery,
                event_type=DeliveryEvent.EVENT_ASSIGNED,
                message=f"Rider {rider.username} assigned to order {order.id}",
                actor=request.user,
            )

            messages.success(request, "Rider assigned successfully.")
            return redirect("deliveries:operator_queue")
    else:
        form = AssignRiderForm()

    return render(request, "deliveries/assign.html", {"order": order, "form": form})
@login_required
def rider_deliveries(request):
    """List deliveries assigned to the current rider."""
    qs = Delivery.objects.filter(rider=request.user).order_by("-assigned_at")
    return render(request, "deliveries/rider_list.html", {"deliveries": qs})

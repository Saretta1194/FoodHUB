from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from orders.models import Order
from .models import Delivery, DeliveryEvent
from .forms import AssignRiderForm
from django.views import View
from django.conf import settings


@staff_member_required
def operator_queue(request):
    """List orders without a delivery yet (CREATED/PREPARING)."""
    qs = (
        Order.objects.filter(
            status__in=[Order.STATUS_CREATED, Order.STATUS_PREPARING],
        )
        .exclude(delivery__isnull=False)
        .order_by("-created_at")
    )
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

    return render(
        request, "deliveries/assign.html", {"order": order, "form": form}
    )


@login_required
def rider_deliveries(request):
    """List deliveries assigned to the current rider."""
    qs = Delivery.objects.filter(rider=request.user).order_by("-assigned_at")
    return render(request, "deliveries/rider_list.html", {"deliveries": qs})


class RiderDeliveryPermissionMixin(UserPassesTestMixin):
    """Allow only the assigned rider to access/modify the delivery."""

    raise_exception = True  # return 403 instead of redirect

    def get_object(self):
        pk = self.kwargs.get("pk")
        return get_object_or_404(Delivery, pk=pk)

    def test_func(self):
        delivery = self.get_object()
        return delivery.rider_id == self.request.user.id


class RiderDeliveryDetailView(
    LoginRequiredMixin, RiderDeliveryPermissionMixin, DetailView
):
    model = Delivery
    template_name = "deliveries/rider_detail.html"
    context_object_name = "delivery"


class RiderMarkPickedUpView(
    LoginRequiredMixin, RiderDeliveryPermissionMixin, View
):
    """Set delivery to PICKED_UP and notify customer."""

    def post(self, request, pk):
        delivery = self.get_object()
        try:
            delivery.advance_to(Delivery.STATUS_PICKED_UP, actor=request.user)
        except ValueError:
            messages.error(request, "Invalid status transition.")
            return redirect("deliveries:rider_detail", pk=delivery.pk)

        # notify customer
        order = delivery.order
        subject = f"Your order #{order.id} has been picked up"
        message = "Your order is on its way to you."
        from_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            "no-reply@foodhub.local"
        )
        recipient_list = (
            [order.user.email] if order.user.email else []
        )
        if recipient_list:
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, "Marked as PICKED_UP.")
        return redirect("deliveries:rider_detail", pk=delivery.pk)


class RiderMarkDeliveredView(
    LoginRequiredMixin, RiderDeliveryPermissionMixin, View
):
    """Set delivery to DELIVERED and notify customer."""

    def post(self, request, pk):
        delivery = self.get_object()
        try:
            delivery.advance_to(Delivery.STATUS_DELIVERED, actor=request.user)
        except ValueError:
            messages.error(request, "Invalid status transition.")
            return redirect("deliveries:rider_detail", pk=delivery.pk)

        # notify customer
        order = delivery.order
        subject = f"Your order #{order.id} has been delivered"
        message = "Enjoy your meal! Your order has been delivered."
        from_email = getattr(
            settings, "DEFAULT_FROM_EMAIL", "no-reply@foodhub.local"
        )
        recipient_list = [order.user.email] if order.user.email else []
        if recipient_list:
            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    recipient_list,
                    fail_silently=True,
                )
            except Exception:
                pass

        messages.success(request, "Marked as DELIVERED.")
        return redirect("deliveries:rider_detail", pk=delivery.pk)

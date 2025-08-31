from decimal import Decimal
import csv
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, View
from django.http import JsonResponse, Http404, HttpResponse
from django.utils.dateparse import parse_date
from django.utils import timezone

from menu.models import Dish
from .models import Order, OrderItem

# Session cart key, e.g. {"12": 2, "35": 1}
CART_SESSION_KEY = "cart"


# -------------------------
# Cart helpers and views
# -------------------------
def _get_cart(session):
    """Get cart dict from session or initialize it."""
    return session.setdefault(CART_SESSION_KEY, {})


def cart_detail(request):
    """Render the current cart with items, quantities, and totals."""
    cart = _get_cart(request.session)
    dish_ids = [int(did) for did in cart.keys()]
    dishes = {d.id: d for d in Dish.objects.filter(id__in=dish_ids)}
    items = []
    total = Decimal("0.00")

    for did_str, qty in cart.items():
        did = int(did_str)
        dish = dishes.get(did)
        if not dish:
            continue
        line_total = dish.price * qty
        total += line_total
        items.append(
            {
                "dish": dish,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    return render(request, "orders/cart_detail.html", {"items": items, "total": total})


@require_POST
def cart_add(request, dish_id):
    """Add one unit of a dish to the cart (only if available)."""
    dish = get_object_or_404(Dish, id=dish_id, available=True)
    cart = _get_cart(request.session)
    current_qty = int(cart.get(str(dish_id), 0))
    cart[str(dish_id)] = current_qty + 1
    request.session.modified = True
    messages.success(request, f"Added {dish.name} to cart.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, dish_id):
    """Remove a dish from the cart regardless of quantity."""
    cart = _get_cart(request.session)
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session.modified = True
    messages.info(request, "Item removed from cart.")
    return redirect("orders:cart_detail")


@require_POST
def cart_update(request, dish_id):
    """Set explicit quantity for a dish; if 0 or less, remove the dish."""
    qty = int(request.POST.get("quantity", 1))
    cart = _get_cart(request.session)
    if qty <= 0:
        cart.pop(str(dish_id), None)
    else:
        cart[str(dish_id)] = qty
    request.session.modified = True
    messages.success(request, "Cart updated.")
    return redirect("orders:cart_detail")


# -------------------------
# Checkout and success
# -------------------------
@login_required
def checkout(request):
    """
    Create an Order with snapshot items.
    Enforce single-restaurant cart and set order.restaurant accordingly.
    """
    cart = _get_cart(request.session)

    if request.method == "POST":
        # Collect dishes in cart
        dish_ids = [int(did) for did in cart.keys()]
        dishes = list(Dish.objects.filter(id__in=dish_ids))
        if not dishes:
            messages.warning(request, "Your cart is empty.")
            return redirect("orders:cart_detail")

        # Enforce single-restaurant cart
        restaurants = {d.restaurant_id for d in dishes}
        if len(restaurants) != 1:
            messages.error(request, "Cart must contain items from a single restaurant.")
            return redirect("orders:cart_detail")

        restaurant_id = restaurants.pop()

        # 1) Create order linked to that restaurant
        order = Order.objects.create(user=request.user, restaurant_id=restaurant_id)

        # 2) Snapshot items
        for dish in dishes:
            qty = int(cart.get(str(dish.id), 0))
            if qty <= 0:
                continue
            OrderItem.objects.create(
                order=order,
                dish=dish,
                dish_name=dish.name,   # snapshot name
                unit_price=dish.price, # snapshot price
                quantity=qty,
            )

        # 3) Clear cart
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        messages.success(request, "Order created successfully!")
        return redirect("orders:order_success", order_id=order.id)

    # GET → show a checkout confirmation page with current cart data
    dish_ids = [int(did) for did in cart.keys()]
    dishes = {d.id: d for d in Dish.objects.filter(id__in=dish_ids)}
    items = []
    total = Decimal("0.00")

    for did_str, qty in cart.items():
        did = int(did_str)
        dish = dishes.get(did)
        if not dish:
            continue
        line_total = dish.price * qty
        total += line_total
        items.append(
            {
                "dish": dish,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    return render(request, "orders/checkout.html", {"items": items, "total": total})


@login_required
def order_success(request, order_id):
    """Simple success page after checkout."""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/success.html", {"order": order})


# -------------------------
# Owner views (manage orders)
# -------------------------
class OwnerOrderPermissionMixin(UserPassesTestMixin):
    """Allow only the owner of the restaurant linked to the order."""

    def get_object(self):
        # Reuse object if already set by a DetailView
        if hasattr(self, "object") and self.object is not None:
            return self.object
        pk = self.kwargs.get("pk")
        return get_object_or_404(Order, pk=pk)

    def test_func(self):
        order = self.get_object()
        return order.restaurant.owner_id == self.request.user.id


class OwnerOrderListView(LoginRequiredMixin, ListView):
    """List orders for all restaurants owned by the current user."""
    model = Order
    template_name = "orders/owner_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(restaurant__owner=self.request.user).order_by(
            "-created_at"
        )


class OwnerOrderDetailView(LoginRequiredMixin, OwnerOrderPermissionMixin, DetailView):
    """Detail of a single order for the owner."""
    model = Order
    template_name = "orders/owner_detail.html"
    context_object_name = "order"

    def post(self, request, *args, **kwargs):
        """
        Handle CREATED -> PREPARING directly from the detail page.
        """
        self.object = self.get_object()
        if self.object.status != Order.STATUS_CREATED:
            messages.error(request, "Invalid transition. Only CREATED → PREPARING is allowed.")
            return redirect("orders:owner_detail", pk=self.object.pk)

        try:
            self.object.advance_to(Order.STATUS_PREPARING)
        except ValueError:
            messages.error(request, "Invalid status transition.")
            return redirect("orders:owner_detail", pk=self.object.pk)

        # Notify customer (console backend in development)
        subject = f"Your order #{self.object.id} is now PREPARING"
        message = "Good news! Your order is being prepared."
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@foodhub.local")
        recipient_list = [self.object.user.email] if self.object.user.email else []
        if recipient_list:
            try:
                send_mail(subject, message, from_email, recipient_list, fail_silently=True)
            except Exception:
                # ignore email failures in dev
                pass

        messages.success(request, "Order moved to PREPARING and customer notified.")
        return redirect("orders:owner_detail", pk=self.object.pk)


class OwnerOrderPrepareView(LoginRequiredMixin, OwnerOrderPermissionMixin, View):
    """
    (Optional endpoint) Advance an order forward to PREPARING (from CREATED/PAID).
    Kept for compatibility if templates point here explicitly.
    """
    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        try:
            order.advance_to(Order.STATUS_PREPARING)
        except ValueError:
            messages.error(request, "Invalid status transition.")
            return redirect("orders:owner_detail", pk=order.pk)

        # Notify customer by email (printed to console in development)
        subject = f"Your order #{order.id} is now PREPARING"
        message = "Good news! Your order is being prepared."
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@foodhub.local")
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

        messages.success(request, "Order moved to PREPARING and customer notified.")
        return redirect("orders:owner_detail", pk=order.pk)


@login_required
def my_orders(request):
    """List orders of the current customer."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})


def _ensure_order_owner(request, order):
    if order.user_id != request.user.id:
        raise Http404()


@login_required
def customer_order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related("restaurant").prefetch_related("items"), pk=pk
    )
    _ensure_order_owner(request, order)
    delivery = getattr(order, "delivery", None)
    events = delivery.events.all() if delivery else []
    return render(
        request,
        "orders/customer_order_detail.html",
        {
            "order": order,
            "delivery": delivery,
            "events": events,
        },
    )


@login_required
def customer_order_status_json(request, pk):
    order = get_object_or_404(Order, pk=pk)
    _ensure_order_owner(request, order)
    delivery = getattr(order, "delivery", None)
    data = {
        "order_id": order.id,
        "order_status": order.status,
        "delivery_status": getattr(delivery, "status", None),
        "rider": getattr(getattr(delivery, "rider", None), "username", None),
        "events": [
            {
                "at": ev.created_at.isoformat(),
                "type": ev.event_type,
                "message": ev.message,
            }
            for ev in (delivery.events.all() if delivery else [])
        ],
    }
    return JsonResponse(data)


@staff_member_required
def export_orders_csv(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    try:
        start_date = parse_date(start) if start else None
        end_date = parse_date(end) if end else None
    except ValueError:
        start_date = end_date = None

    qs = Order.objects.select_related("restaurant", "user").order_by("created_at")
    if start_date:
        qs = qs.filter(created_at__date__gte=start_date)
    if end_date:
        qs = qs.filter(created_at__date__lte=end_date)

    # CSV response
    filename = "orders_export.csv"
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(
        [
            "id",
            "created_at",
            "user",
            "restaurant",
            "status",
            "total_items",
            "total_amount",
        ]
    )

    for o in qs:
        total_items = sum(i.quantity for i in o.items.all())
        total_amount = sum(i.unit_price * i.quantity for i in o.items.all())
        writer.writerow(
            [
                o.id,
                timezone.localtime(o.created_at).isoformat(),
                getattr(o.user, "username", ""),
                getattr(o.restaurant, "name", ""),
                o.status,
                total_items,
                f"{total_amount:.2f}",
            ]
        )

    return response


def owner_orders(request):
    return render(request, "orders/owner_orders.html")

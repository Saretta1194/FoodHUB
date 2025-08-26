from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, View

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

    return render(
        request, "orders/cart_detail.html", {"items": items, "total": total}
    )


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
            messages.error(
                request, "Cart must contain items from a single restaurant."
            )
            return redirect("orders:cart_detail")

        restaurant_id = restaurants.pop()

        # 1) Create order linked to that restaurant
        order = Order.objects.create(
            user=request.user, restaurant_id=restaurant_id
        )

        # 2) Snapshot items
        for dish in dishes:
            qty = int(cart.get(str(dish.id), 0))
            if qty <= 0:
                continue
            OrderItem.objects.create(
                order=order,
                dish=dish,
                dish_name=dish.name,  # snapshot name
                unit_price=dish.price,  # snapshot price
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

    return render(
        request, "orders/checkout.html", {"items": items, "total": total}
    )


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
        return Order.objects.filter(
            restaurant__owner=self.request.user
        ).order_by("-created_at")


class OwnerOrderDetailView(
    LoginRequiredMixin, OwnerOrderPermissionMixin, DetailView
):
    """Detail of a single order for the owner."""

    model = Order
    template_name = "orders/owner_detail.html"
    context_object_name = "order"


class OwnerOrderPrepareView(
    LoginRequiredMixin, OwnerOrderPermissionMixin, View
):
    """
    Advance an order forward to PREPARING (from CREATED/PAID).
    Notify customer via email (console backend in development).
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
                # In development, ignore email failures
                pass

        messages.success(
            request, "Order moved to PREPARING and customer notified."
        )
        return redirect("orders:owner_detail", pk=order.pk)


@login_required
def my_orders(request):
    """List orders of the current customer."""
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/my_orders.html", {"orders": orders})

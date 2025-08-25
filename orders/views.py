from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from menu.models import Dish
from .models import Order, OrderItem


CART_SESSION_KEY = "cart"  # ex: {"12": 2, "35": 1}


def _get_cart(session):
    return session.setdefault(CART_SESSION_KEY, {})


def cart_detail(request):
    cart = _get_cart(request.session)
    # Load Dishes from DB to show updated info in cart
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
        items.append({
            "dish": dish,
            "quantity": qty,
            "line_total": line_total,
        })

    return render(request, "orders/cart_detail.html", {"items": items, "total": total})


@require_POST
def cart_add(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id, available=True)
    cart = _get_cart(request.session)
    current_qty = int(cart.get(str(dish_id), 0))
    cart[str(dish_id)] = current_qty + 1
    request.session.modified = True
    messages.success(request, f"Added {dish.name} to cart.")
    return redirect("orders:cart_detail")


@require_POST
def cart_remove(request, dish_id):
    cart = _get_cart(request.session)
    if str(dish_id) in cart:
        del cart[str(dish_id)]
        request.session.modified = True
    messages.info(request, "Item removed from cart.")
    return redirect("orders:cart_detail")


@require_POST
def cart_update(request, dish_id):
    """
    Update explicit quantity (>=1). If 0, remove.
    """
    qty = int(request.POST.get("quantity", 1))
    cart = _get_cart(request.session)
    if qty <= 0:
        cart.pop(str(dish_id), None)
    else:
        cart[str(dish_id)] = qty
    request.session.modified = True
    messages.success(request, "Cart updated.")
    return redirect("orders:cart_detail")


@login_required
def checkout(request):
    """
    Create Order + OrderItems with snapshots of name and price.
    Empty cart and display success page.
    """
    cart = _get_cart(request.session)
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("orders:cart_detail")

    if request.method == "POST":
        # 1) crea Order
        order = Order.objects.create(user=request.user)
        # 2) crea OrderItems con snapshot
        dish_ids = [int(did) for did in cart.keys()]
        for dish in Dish.objects.filter(id__in=dish_ids):
            qty = int(cart.get(str(dish.id), 0))
            if qty <= 0:
                continue
            OrderItem.objects.create(
                order=order,
                dish=dish,
                dish_name=dish.name,      # snapshot name
                unit_price=dish.price,    # snapshot price
                quantity=qty,
            )
        # 3) svuota il carrello
        request.session[CART_SESSION_KEY] = {}
        request.session.modified = True

        messages.success(request, "Order created successfully!")
        return redirect("orders:order_success", order_id=order.id)

    # GET → show a checkout confirmation page
    # (we use the current cart data)
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
        items.append({
            "dish": dish,
            "quantity": qty,
            "line_total": line_total,
        })

    return render(request, "orders/checkout.html", {"items": items, "total": total})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "orders/success.html", {"order": order})

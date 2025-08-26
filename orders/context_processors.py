from .views import CART_SESSION_KEY


def cart_item_count(request):
    """
    Returns the total number of items in the cart (sum of quantities).
    Accessible as {{ cart_item_count }} in templates.
    """
    cart = request.session.get(CART_SESSION_KEY, {})
    total_qty = sum(cart.values())
    return {"cart_item_count": total_qty}

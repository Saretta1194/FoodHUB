# core/context_processors.py
from deliveries.models import Delivery

def nav_flags(request):
    user = request.user
    if not user.is_authenticated:
        return {
            "is_owner": False,
            "is_rider": False,
            "owner_restaurant_count": 0,
            "rider_delivery_count": 0,
        }

    owner_count = getattr(user, "restaurants", None).count() if hasattr(user, "restaurants") else 0
    rider_count = Delivery.objects.filter(rider=user).only("id").count()

    return {
        "is_owner": owner_count > 0,
        "is_rider": rider_count > 0,
        "owner_restaurant_count": owner_count,
        "rider_delivery_count": rider_count,
    }

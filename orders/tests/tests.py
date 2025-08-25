from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem

User = get_user_model()


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="cust", password="pass123")
        owner = User.objects.create_user(username="owner", password="pass123")
        self.rest = Restaurant.objects.create(
            owner=owner, name="R", address="A", opening_hours="09:00-18:00", is_active=True
        )
        self.d1 = Dish.objects.create(restaurant=self.rest, name="Pasta", price=Decimal("10.00"), available=True)
        self.d2 = Dish.objects.create(restaurant=self.rest, name="Tiramisu", price=Decimal("6.00"), available=True)

    def test_checkout_creates_order_with_created_status_and_snapshots(self):
        session = self.client.session
        session["cart"] = {str(self.d1.id): 2, str(self.d2.id): 1}
        session.save()

        self.client.login(username="cust", password="pass123")
        resp = self.client.post(reverse("orders:checkout"), follow=True)
        self.assertEqual(resp.status_code, 200)

        order = Order.objects.latest("id")
        self.assertEqual(order.user.username, "cust")
        self.assertEqual(order.status, Order.STATUS_CREATED)

        items = list(order.items.all())
        self.assertEqual(len(items), 2)
        # snapshot of name and price
        self.assertEqual(items[0].dish_name in ["Pasta", "Tiramisu"], True)
        prices = {i.dish_name: i.unit_price for i in items}
        self.assertEqual(prices["Pasta"], Decimal("10.00"))
        self.assertEqual(prices["Tiramisu"], Decimal("6.00"))
        # total calcolate
        self.assertEqual(order.total_amount, Decimal("26.00"))

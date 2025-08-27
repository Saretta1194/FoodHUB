from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem
from deliveries.models import Delivery, DeliveryEvent

User = get_user_model()

class CustomerTrackingTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.cust = User.objects.create_user(username="cust", password="pass123")
        self.other = User.objects.create_user(username="other", password="pass123")
        self.rest = Restaurant.objects.create(owner=self.owner, name="R", address="A", opening_hours="09:00-18:00", is_active=True)
        self.dish = Dish.objects.create(restaurant=self.rest, name="Pasta", price=Decimal("10.00"), available=True)
        self.order = Order.objects.create(user=self.cust, restaurant=self.rest)
        OrderItem.objects.create(order=self.order, dish=self.dish, dish_name="Pasta", unit_price=Decimal("10.00"), quantity=1)
        self.delivery = Delivery.objects.create(order=self.order)
        DeliveryEvent.objects.create(delivery=self.delivery, event_type="STATUS_CHANGE", message="Assigned")

    def test_owner_only_access_for_customer_detail(self):
        self.client.login(username="other", password="pass123")
        url = reverse("orders:customer_order_detail", args=[self.order.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)

        self.client.login(username="cust", password="pass123")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Order #")

    def test_status_json_contains_delivery_info(self):
        self.client.login(username="cust", password="pass123")
        url = reverse("orders:customer_order_status_json", args=[self.order.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["order_id"], self.order.id)
        self.assertIn("events", data)

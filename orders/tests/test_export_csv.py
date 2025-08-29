from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from restaurants.models import Restaurant
from orders.models import Order, OrderItem
from menu.models import Dish

User = get_user_model()

class ExportCsvTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="op", password="x", is_staff=True)
        self.owner = User.objects.create_user(username="owner", password="x")
        self.cust = User.objects.create_user(username="cust", password="x")
        self.rest = Restaurant.objects.create(owner=self.owner, name="R", address="A", opening_hours="09-18", is_active=True)
        self.order = Order.objects.create(user=self.cust, restaurant=self.rest)
        self.dish = Dish.objects.create(restaurant=self.rest, name="P", price=Decimal("10.00"), available=True)
        OrderItem.objects.create(order=self.order, dish=self.dish, dish_name="P", unit_price=Decimal("10.00"), quantity=2)

    def test_export_requires_staff(self):
        url = reverse("orders:export_orders_csv")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 302)  # redirect to admin login

        self.client.login(username="op", password="x")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/csv")
        self.assertIn("orders_export.csv", resp["Content-Disposition"])
        self.assertIn("id,created_at,user,restaurant,status,total_items,total_amount", resp.content.decode())

    def test_export_with_date_filter(self):
        self.client.login(username="op", password="x")
        url = reverse("orders:export_orders_csv") + "?start=2000-01-01&end=2100-01-01"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode()
        self.assertIn("cust", body)
        self.assertIn("R", body)

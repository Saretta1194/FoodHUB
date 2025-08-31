from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem

User = get_user_model()


class OwnerPrepareTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            username="cust",
            password="pass123",
            email="cust@example.com",
        )
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.other = User.objects.create_user(username="other", password="pass123")

        self.rest = Restaurant.objects.create(
            owner=self.owner,
            name="R",
            address="A",
            opening_hours="09:00-18:00",
            is_active=True,
        )
        self.dish = Dish.objects.create(
            restaurant=self.rest,
            name="Pasta",
            price=Decimal("10.00"),
            available=True,
        )

        self.order = Order.objects.create(
            user=self.customer, restaurant=self.rest
        )  # status=CREATED
        OrderItem.objects.create(
            order=self.order,
            dish=self.dish,
            dish_name="Pasta",
            unit_price=Decimal("10.00"),
            quantity=1,
        )

    def test_owner_can_move_created_to_preparing(self):
        self.client.login(username="owner", password="pass123")
        url = reverse("orders:owner_prepare", args=[self.order.id])
        resp = self.client.post(url, follow=True)
        self.order.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.order.status, Order.STATUS_PREPARING)

    def test_non_owner_cannot_prepare(self):
        self.client.login(username="other", password="pass123")
        url = reverse("orders:owner_prepare", args=[self.order.id])
        resp = self.client.post(url)
        self.assertIn(resp.status_code, (302, 403, 404))  # blocked by mixin

    def test_backward_transition_blocked(self):
        # first move to PREPARING
        self.client.login(username="owner", password="pass123")
        url = reverse("orders:owner_prepare", args=[self.order.id])
        self.client.post(url, follow=True)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, Order.STATUS_PREPARING)
        # trying again should be invalid (not forward)
        resp = self.client.post(url, follow=True)
        self.assertContains(resp, "Invalid status transition.")

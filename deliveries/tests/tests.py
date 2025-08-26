from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem
from deliveries.models import Delivery, DeliveryEvent

User = get_user_model()


class AssignmentTests(TestCase):
    def setUp(self):
        # Users
        self.operator = User.objects.create_user(
            username="operator", password="pass123", is_staff=True
        )
        self.owner = User.objects.create_user(
            username="owner", password="pass123"
        )
        self.rider = User.objects.create_user(
            username="rider", password="pass123"
        )
        self.customer = User.objects.create_user(
            username="cust", password="pass123"
        )

        # Restaurant and order
        self.rest = Restaurant.objects.create(
            owner=self.owner,
            name="R",
            address="A",
            opening_hours="09:00-18:00",
            is_active=True,
        )
        self.order = Order.objects.create(
            user=self.customer, restaurant=self.rest
        )
        OrderItem.objects.create(
            order=self.order,
            dish=Dish.objects.create(
                restaurant=self.rest,
                name="Pasta",
                price=Decimal("10.00"),
                available=True,
            ),
            dish_name="Pasta",
            unit_price=Decimal("10.00"),
            quantity=1,
        )

    def test_operator_can_assign_rider_and_event_logged(self):
        self.client.login(username="operator", password="pass123")
        url = reverse("deliveries:assign_rider", args=[self.order.id])
        resp = self.client.post(
            url, data={"rider": self.rider.id}, follow=True
        )
        self.assertEqual(resp.status_code, 200)

        d = Delivery.objects.get(order=self.order)
        self.assertEqual(d.rider, self.rider)
        self.assertEqual(d.status, Delivery.STATUS_ASSIGNED)
        # event logged
        self.assertTrue(
            DeliveryEvent.objects.filter(
                delivery=d, event_type=DeliveryEvent.EVENT_ASSIGNED
            ).exists()
        )

    def test_customer_sees_assigned_rider(self):
        # Assign first
        Delivery.objects.create(order=self.order, rider=self.rider)
        self.client.login(username="cust", password="pass123")
        url = reverse("orders:my_orders")
        resp = self.client.get(url)
        self.assertContains(resp, "Rider: rider")

    def test_rider_sees_own_deliveries(self):
        Delivery.objects.create(order=self.order, rider=self.rider)
        self.client.login(username="rider", password="pass123")
        url = reverse("deliveries:rider_deliveries")
        resp = self.client.get(url)
        self.assertContains(resp, f"Order #{self.order.id}")


class OperatorPermissionTests(TestCase):
    def setUp(self):
        # Users
        self.staff = User.objects.create_user(
            username="operator", password="pass123", is_staff=True
        )
        self.user = User.objects.create_user(
            username="user", password="pass123"
        )
        self.owner = User.objects.create_user(
            username="owner", password="pass123"
        )

        # Restaurant + Order with one item
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
            price=Decimal("12.00"),
            available=True,
        )
        self.order = Order.objects.create(
            user=self.user, restaurant=self.rest
        )  # status=CREATED by default
        OrderItem.objects.create(
            order=self.order,
            dish=self.dish,
            dish_name="Pasta",
            unit_price=Decimal("12.00"),
            quantity=1,
        )

        self.queue_url = reverse("deliveries:operator_queue")
        self.assign_url = reverse(
            "deliveries:assign_rider",
            args=[self.order.id],
        )

    def test_non_staff_cannot_access_operator_queue(self):
        self.client.login(username="user", password="pass123")
        resp = self.client.get(self.queue_url)
        # staff_member_required -> redirects to admin login (302) by default
        self.assertEqual(resp.status_code, 302)

    def test_staff_can_access_operator_queue(self):
        self.client.login(username="operator", password="pass123")
        resp = self.client.get(self.queue_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f"Order #{self.order.id}")

    def test_non_staff_cannot_assign_rider(self):
        resp = self.client.post(self.assign_url, data={"rider": self.user.id})
        # staff_member_required -> redirects to admin login (302) by default
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.status_code, 302)

    def test_staff_can_open_assign_form(self):
        self.client.login(username="operator", password="pass123")
        resp = self.client.get(self.assign_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Assign rider")

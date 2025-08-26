from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from decimal import Decimal

from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem
from deliveries.models import Delivery, DeliveryEvent

User = get_user_model()


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
)
class RiderStatusFlowTests(TestCase):
    def setUp(self):
        # Users
        self.owner = User.objects.create_user(
            username="owner", password="pass123"
        )
        self.customer = User.objects.create_user(
            username="cust", password="pass123", email="cust@example.com"
        )
        self.rider = User.objects.create_user(
            username="rider", password="pass123"
        )
        self.other = User.objects.create_user(
            username="other", password="pass123"
        )

        # Restaurant, order, item
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
        )
        OrderItem.objects.create(
            order=self.order,
            dish=self.dish,
            dish_name="Pasta",
            unit_price=Decimal("10.00"),
            quantity=1,
        )

        # Delivery assigned to rider
        self.delivery = Delivery.objects.create(
            order=self.order, rider=self.rider
        )

    def test_only_assigned_rider_can_update(self):
        # non-assigned user
        self.client.login(username="other", password="pass123")
        url = reverse("deliveries:rider_mark_picked", args=[self.delivery.pk])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 403)

        # assigned rider
        self.client.login(username="rider", password="pass123")
        resp = self.client.post(url, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, Delivery.STATUS_PICKED_UP)

    def test_forward_only_and_timeline_and_notification(self):
        self.client.login(username="rider", password="pass123")

        # Can't mark delivered directly from ASSIGNED
        url_delivered = reverse(
            "deliveries:rider_mark_delivered",
            args=[self.delivery.pk],
        )
        resp = self.client.post(url_delivered, follow=True)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, Delivery.STATUS_ASSIGNED)

        # Pick up
        url_picked = reverse(
            "deliveries:rider_mark_picked", args=[self.delivery.pk]
        )
        resp = self.client.post(url_picked, follow=True)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, Delivery.STATUS_PICKED_UP)

        # One email sent to customer
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("picked up", mail.outbox[0].subject.lower())

        # Deliver
        resp = self.client.post(url_delivered, follow=True)
        self.delivery.refresh_from_db()
        self.assertEqual(self.delivery.status, Delivery.STATUS_DELIVERED)

        # Two emails in total
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn("delivered", mail.outbox[1].subject.lower())

        # Timeline has events
        self.assertTrue(
            DeliveryEvent.objects.filter(
                delivery=self.delivery,
                event_type=DeliveryEvent.EVENT_STATUS_CHANGE,
            ).exists()
        )

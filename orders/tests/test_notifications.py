from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from orders.models import Order

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class OrderEmailSignalTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.customer = User.objects.create_user(
            username="cust", password="x", email="cust@example.com"
        )
        self.rest = Restaurant.objects.create(
            owner=self.owner,
            name="R",
            address="A",
            opening_hours="09-18",
            is_active=True,
        )
        self.order = Order.objects.create(user=self.customer, restaurant=self.rest)

    def test_email_sent_on_order_status_change(self):
        self.order.status = Order.STATUS_PREPARING
        self.order.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("status changed", mail.outbox[0].subject.lower())

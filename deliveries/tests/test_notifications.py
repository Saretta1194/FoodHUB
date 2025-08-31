from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model
from decimal import Decimal
from restaurants.models import Restaurant
from orders.models import Order, OrderItem
from menu.models import Dish
from deliveries.models import Delivery

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class DeliveryEmailSignalTests(TestCase):
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
        self.dish = Dish.objects.create(
            restaurant=self.rest, name="Pasta", price=Decimal("10.00"), available=True
        )
        OrderItem.objects.create(
            order=self.order,
            dish=self.dish,
            dish_name="Pasta",
            unit_price=Decimal("10.00"),
            quantity=1,
        )
        self.delivery = Delivery.objects.create(order=self.order)

    def test_email_sent_on_delivery_status_change(self):
        self.delivery.status = Delivery.STATUS_PICKED_UP
        self.delivery.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("picked up", mail.outbox[0].subject.lower())

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from restaurants.models import Restaurant
from menu.models import Dish
from orders.models import Order, OrderItem
from deliveries.models import Delivery

User = get_user_model()

class FlashMessagesTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="x")
        self.customer = User.objects.create_user(username="cust", password="x")
        self.rider = User.objects.create_user(username="rider", password="x")
        self.rest = Restaurant.objects.create(owner=self.owner, name="R", address="A", opening_hours="09-18", is_active=True)
        self.dish = Dish.objects.create(restaurant=self.rest, name="P", price=Decimal("10.00"), available=True)
        self.order = Order.objects.create(user=self.customer, restaurant=self.rest)
        OrderItem.objects.create(order=self.order, dish=self.dish, dish_name="P", unit_price=Decimal("10.00"), quantity=1)
        self.delivery = Delivery.objects.create(order=self.order, rider=self.rider)

    def test_flash_message_on_picked_up(self):
        self.client.login(username="rider", password="x")
        url = reverse("deliveries:rider_mark_picked", args=[self.delivery.pk])
        resp = self.client.post(url, follow=True)
        # messages framework injects messages into context (with follow=True)
        messages_list = list(resp.context["messages"])
        self.assertTrue(any("Marked as PICKED_UP" in str(m) for m in messages_list))

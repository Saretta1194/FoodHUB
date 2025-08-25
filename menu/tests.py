from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from restaurants.models import Restaurant
from menu.models import Dish

User = get_user_model()


class DishTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass123")
        self.other = User.objects.create_user(username="other", password="pass123")
        self.restaurant = Restaurant.objects.create(
            owner=self.owner,
            name="Test Risto",
            address="Via Roma 10",
            opening_hours="09:00-18:00",
            is_active=True,
        )

    def test_price_must_be_positive(self):
        self.client.login(username="owner", password="pass123")
        url = reverse("menu:dish_create", args=[self.restaurant.id])
        resp = self.client.post(url, {
            "name": "Bad Dish",
            "description": "x",
            "price": -5,
            "available": True,
        })
        self.assertContains(resp, "Ensure this value is greater than or equal to 0.01")
        self.assertFalse(Dish.objects.filter(name="Bad Dish").exists())

    def test_only_owner_can_create_dish(self):
        self.client.login(username="other", password="pass123")
        url = reverse("menu:dish_create", args=[self.restaurant.id])
        resp = self.client.post(url, {
            "name": "Other Dish",
            "description": "y",
            "price": 5,
            "available": True,
        })
        self.assertEqual(resp.status_code, 404)  # not allowed
        self.assertFalse(Dish.objects.filter(name="Other Dish").exists())

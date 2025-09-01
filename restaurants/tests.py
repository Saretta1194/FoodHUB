from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from restaurants.models import Restaurant

User = get_user_model()


class RestaurantModelTests(TestCase):
    def test_str_contains_name_and_owner(self):
        user = User.objects.create_user(username="alice", password="pass1234")
        r = Restaurant.objects.create(
            owner=user,
            name="Pasta House",
            address="Via Roma 1",
            opening_hours="09:00-18:00",
            is_active=True,
        )
        self.assertIn("Pasta House", str(r))
        self.assertIn("alice", str(r))


class OwnerOnlyViewsTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass1234")
        self.other = User.objects.create_user(username="other", password="pass1234")
        self.r = Restaurant.objects.create(
            owner=self.owner,
            name="My Place",
            address="Street 1",
            opening_hours="10:00-20:00",
            is_active=True,
        )
        # Owner → OK
        self.client.logout()
        self.client.login(username="owner", password="pass1234")
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(url, payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            Restaurant.objects.filter(name="New Spot", owner=self.owner).exists()
        )

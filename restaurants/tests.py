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

    def test_owner_list_requires_login(self):
        url = reverse("restaurants:owner_list")
        resp = self.client.get(url)
        # Not logged in → redirect to login
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_only_owner_can_see_edit(self):
        edit_url = reverse("restaurants:edit", args=[self.r.pk])
        # Other user → object not in queryset → 404
        self.client.login(username="other", password="pass1234")
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 404)

        # Owner → OK
        self.client.logout()
        self.client.login(username="owner", password="pass1234")
        resp = self.client.get(edit_url)
        self.assertEqual(resp.status_code, 200)

    def test_create_sets_owner(self):
        self.client.login(username="owner", password="pass1234")
        url = reverse("restaurants:create")
        payload = {
            "name": "New Spot",
            "address": "Via Milano 2",
            "opening_hours": "09:00-18:00",
            "is_active": True,
        }
        resp = self.client.post(url, payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Restaurant.objects.filter(name="New Spot", owner=self.owner).exists())

    def test_opening_hours_validation(self):
        self.client.login(username="owner", password="pass1234")
        url = reverse("restaurants:create")
        bad_payload = {
            "name": "Bad Spot",
            "address": "Via Error 3",
            "opening_hours": "9-18",  # invalid
            "is_active": True,
        }
        resp = self.client.post(url, bad_payload)
        # Stay on the form page with errors (status 200 but invalid form)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Opening hours must be in the format")
        self.assertFalse(Restaurant.objects.filter(name="Bad Spot").exists())

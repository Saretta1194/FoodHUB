from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice", email="a@a.com", password="secret123"
        )

    def test_profile_created_by_signal(self):
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(self.user.profile.phone, "")
        self.assertEqual(self.user.profile.address, "")

    def test_profile_requires_login(self):
        resp = self.client.get(reverse("my_profile"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp["Location"])

    def test_profile_update(self):
        self.client.login(username="alice", password="secret123")
        resp = self.client.post(
            reverse("my_profile"),
            {"phone": "+41 79 123 45 67", "address": "Main St 1, Zurich"},
        )
        self.assertRedirects(resp, reverse("my_profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.phone, "+41 79 123 45 67")
        self.assertEqual(self.user.profile.address, "Main St 1, Zurich")


# Create your tests here.

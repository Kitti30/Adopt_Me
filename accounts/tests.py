from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from core.testing import PASSWORD, make_user

SIGNUP = {
    "username": "newbie",
    "email": "newbie@example.com",
    "phone": "0812345678",
    "province": "กรุงเทพฯ",
    "password1": PASSWORD,
    "password2": PASSWORD,
}


class SignUpTests(TestCase):
    def test_signup_creates_user_and_profile_and_logs_in(self):
        resp = self.client.post(reverse("accounts:signup"), SIGNUP)
        self.assertRedirects(resp, reverse("core:home"))
        user = User.objects.get(username="newbie")
        self.assertEqual(user.profile.phone, "0812345678")
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_signup_with_mismatched_passwords_fails(self):
        data = {**SIGNUP, "password2": "different-Pass9!"}
        resp = self.client.post(reverse("accounts:signup"), data)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username="newbie").exists())


class LoginLogoutTests(TestCase):
    def setUp(self):
        make_user("alice")

    def test_login_success(self):
        resp = self.client.post(
            reverse("accounts:login"), {"username": "alice", "password": PASSWORD}
        )
        self.assertRedirects(resp, reverse("core:home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_with_wrong_password_fails(self):
        resp = self.client.post(
            reverse("accounts:login"), {"username": "alice", "password": "wrong"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logout_requires_post_and_clears_session(self):
        self.client.force_login(User.objects.get(username="alice"))
        resp = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(resp, reverse("core:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
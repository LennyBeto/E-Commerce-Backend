from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User


class RegistrationTests(APITestCase):
    def test_register_success(self):
        r = self.client.post(reverse("auth-register"), {
            "username": "beto", "email": "beto@test.com",
            "password": "StrongPass123!", "password2": "StrongPass123!"})
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_password_mismatch(self):
        r = self.client.post(reverse("auth-register"), {
            "username": "beto", "email": "beto@test.com",
            "password": "StrongPass123!", "password2": "Wrong!"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_email(self):
        User.objects.create_user(username="existing", email="dupe@test.com", password="pass123!")
        r = self.client.post(reverse("auth-register"), {
            "username": "new", "email": "dupe@test.com",
            "password": "StrongPass123!", "password2": "StrongPass123!"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    def setUp(self):
        User.objects.create_user(username="beto", email="beto@test.com", password="TestPass123!")

    def test_login_returns_tokens(self):
        r = self.client.post(reverse("auth-login"),
                             {"email": "beto@test.com", "password": "TestPass123!"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data)
        self.assertIn("user", r.data)

    def test_wrong_password(self):
        r = self.client.post(reverse("auth-login"),
                             {"email": "beto@test.com", "password": "wrong"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)


class MeViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="beto", email="beto@test.com", password="TestPass123!")
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        r = self.client.get(reverse("auth-me"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["email"], "beto@test.com")

    def test_update_profile(self):
        r = self.client.patch(reverse("auth-me"), {"first_name": "Beto"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
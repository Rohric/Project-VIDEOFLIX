import pytest
from rest_framework import status


@pytest.mark.django_db
class TestRegister:

    def test_register_happy_path(self, api_client):
        """✅ Successfully register a new user."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "confirmed_password": "securepass123"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newuser@example.com"

        # User should exist but be inactive
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(email="newuser@example.com")
        assert user.is_active is False

    def test_register_passwords_mismatch(self, api_client):
        """❌ Passwords don't match."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "confirmed_password": "differentpass"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Passwords do not match" in str(response.data)

    def test_register_duplicate_email(self, api_client, test_user):
        """❌ Email already exists."""
        data = {
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "securepass123",
            "confirmed_password": "securepass123"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already in use" in str(response.data)

    def test_register_missing_username(self, api_client):
        """❌ Missing username field."""
        data = {
            "email": "newuser@example.com",
            "password": "securepass123",
            "confirmed_password": "securepass123"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email(self, api_client):
        """❌ Missing email field."""
        data = {
            "username": "newuser",
            "password": "securepass123",
            "confirmed_password": "securepass123"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_password(self, api_client):
        """❌ Missing password field."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "confirmed_password": "securepass123"
        }
        response = api_client.post("/api/register/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

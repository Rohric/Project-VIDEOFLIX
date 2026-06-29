import pytest
from rest_framework import status


@pytest.mark.django_db
class TestLogin:

    def test_login_happy_path(self, api_client, test_user):
        """✅ Successfully login with correct credentials."""
        data = {
            "username": "testuser",
            "password": "securepass123"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        # Check cookies are set
        assert "access_token" in response.cookies
        assert "refresh_token" in response.cookies

    def test_login_invalid_username(self, api_client):
        """❌ Username doesn't exist."""
        data = {
            "username": "nonexistent",
            "password": "securepass123"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_wrong_password(self, api_client, test_user):
        """❌ Wrong password."""
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client, inactive_test_user):
        """❌ User not verified (is_active=False)."""
        data = {
            "username": "inactive",
            "password": "securepass123"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_missing_username(self, api_client):
        """❌ Missing username field."""
        data = {
            "password": "securepass123"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_password(self, api_client):
        """❌ Missing password field."""
        data = {
            "username": "testuser"
        }
        response = api_client.post("/api/login/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

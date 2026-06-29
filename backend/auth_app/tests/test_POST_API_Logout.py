import pytest
from rest_framework import status


@pytest.mark.django_db
class TestLogout:

    def test_logout_happy_path(self, api_client, test_user):
        """✅ Successfully logout authenticated user."""
        # First login
        api_client.post("/api/login/", {
            "username": "testuser",
            "password": "securepass123"
        })

        # Then logout
        response = api_client.post("/api/logout/")

        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data
        # Cookies should be deleted
        assert response.cookies["access_token"].value == ""
        assert response.cookies["refresh_token"].value == ""

    def test_logout_without_token(self, api_client):
        """❌ Logout without refresh token cookie."""
        response = api_client.post("/api/logout/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_unauthenticated(self, api_client):
        """❌ Logout when not authenticated."""
        response = api_client.post("/api/logout/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

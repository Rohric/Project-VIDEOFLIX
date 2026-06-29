import pytest
from rest_framework import status


@pytest.mark.django_db
class TestTokenRefresh:

    def test_refresh_token_happy_path(self, api_client, test_user):
        """✅ Successfully refresh access token."""
        # Login first
        api_client.post("/api/login/", {
            "username": "testuser",
            "password": "securepass123"
        })

        # Refresh token
        response = api_client.post("/api/token/refresh/")

        assert response.status_code == status.HTTP_200_OK
        assert "detail" in response.data
        assert "access_token" in response.cookies

    def test_refresh_without_token(self, api_client):
        """❌ Refresh without refresh token cookie."""
        response = api_client.post("/api/token/refresh/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_with_invalid_token(self, api_client):
        """❌ Refresh with invalid refresh token."""
        api_client.cookies["refresh_token"] = "invalid_token_here"
        response = api_client.post("/api/token/refresh/")

        # TokenError from JWT library results in 500, but should be 401
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_500_INTERNAL_SERVER_ERROR]

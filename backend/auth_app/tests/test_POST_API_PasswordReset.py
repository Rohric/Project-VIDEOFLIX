import pytest
from rest_framework import status


@pytest.mark.django_db
class TestPasswordReset:

    def test_password_reset_happy_path(self, api_client, test_user):
        """✅ Successfully request password reset."""
        data = {
            "email": "test@example.com"
        }
        response = api_client.post("/api/password_reset/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "email has been sent" in response.data["detail"].lower()

    def test_password_reset_nonexistent_email(self, api_client):
        """❌ Email doesn't exist."""
        data = {
            "email": "nonexistent@example.com"
        }
        response = api_client.post("/api/password_reset/", data)

        # Security: still return 200 to prevent email enumeration
        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_missing_email(self, api_client):
        """❌ Missing email field."""
        data = {}
        response = api_client.post("/api/password_reset/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_reset_invalid_email_format(self, api_client):
        """❌ Invalid email format."""
        data = {
            "email": "not_an_email"
        }
        response = api_client.post("/api/password_reset/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

import pytest
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status


@pytest.mark.django_db
class TestPasswordConfirm:

    def test_password_confirm_happy_path(self, api_client, test_user):
        """✅ Successfully reset password with valid token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
        refresh = RefreshToken.for_user(test_user)
        token = str(refresh.access_token)

        data = {
            "new_password": "newsecurepass123",
            "confirm_password": "newsecurepass123"
        }
        response = api_client.post(f"/api/password_confirm/{uidb64}/{token}/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "successfully reset" in response.data["detail"].lower()

    def test_password_confirm_mismatch(self, api_client, test_user):
        """❌ New passwords don't match."""
        from rest_framework_simplejwt.tokens import RefreshToken
        uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
        refresh = RefreshToken.for_user(test_user)
        token = str(refresh.access_token)

        data = {
            "new_password": "newsecurepass123",
            "confirm_password": "differentpass"
        }
        response = api_client.post(f"/api/password_confirm/{uidb64}/{token}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_confirm_invalid_token(self, api_client, test_user):
        """❌ Invalid reset token."""
        uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
        token = "invalid_token_here"

        data = {
            "new_password": "newsecurepass123",
            "confirm_password": "newsecurepass123"
        }
        response = api_client.post(f"/api/password_confirm/{uidb64}/{token}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_confirm_invalid_user_id(self, api_client):
        """❌ User ID doesn't exist."""
        uidb64 = urlsafe_base64_encode(force_bytes(9999))
        token = "any_token"

        data = {
            "new_password": "newsecurepass123",
            "confirm_password": "newsecurepass123"
        }
        response = api_client.post(f"/api/password_confirm/{uidb64}/{token}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_password_confirm_missing_password(self, api_client, test_user):
        """❌ Missing password fields."""
        from rest_framework_simplejwt.tokens import RefreshToken
        uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
        refresh = RefreshToken.for_user(test_user)
        token = str(refresh.access_token)

        data = {}
        response = api_client.post(f"/api/password_confirm/{uidb64}/{token}/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

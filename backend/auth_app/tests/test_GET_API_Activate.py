import pytest
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework import status


@pytest.mark.django_db
class TestActivate:

    def test_activate_happy_path(self, api_client, inactive_test_user):
        """✅ Successfully activate account with valid token."""
        from rest_framework_simplejwt.tokens import RefreshToken
        # Generate valid token
        uidb64 = urlsafe_base64_encode(force_bytes(inactive_test_user.pk))
        refresh = RefreshToken.for_user(inactive_test_user)
        token = str(refresh.access_token)

        response = api_client.get(f"/api/activate/{uidb64}/{token}/")

        assert response.status_code == status.HTTP_200_OK
        assert "successfully activated" in response.data["message"].lower()

        # User should be active now
        inactive_test_user.refresh_from_db()
        assert inactive_test_user.is_active is True

    def test_activate_invalid_token(self, api_client, inactive_test_user):
        """❌ Invalid activation token."""
        uidb64 = urlsafe_base64_encode(force_bytes(inactive_test_user.pk))
        token = "invalid_token_here"

        response = api_client.get(f"/api/activate/{uidb64}/{token}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_invalid_user_id(self, api_client):
        """❌ User ID doesn't exist."""
        uidb64 = urlsafe_base64_encode(force_bytes(9999))
        token = "any_token"

        response = api_client.get(f"/api/activate/{uidb64}/{token}/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_activate_already_active_user(self, api_client, test_user):
        """❌ User is already active."""
        from rest_framework_simplejwt.tokens import RefreshToken
        uidb64 = urlsafe_base64_encode(force_bytes(test_user.pk))
        refresh = RefreshToken.for_user(test_user)
        token = str(refresh.access_token)

        response = api_client.get(f"/api/activate/{uidb64}/{token}/")

        # Should succeed or fail gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

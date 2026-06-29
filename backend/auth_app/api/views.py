from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    RegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordConfirmSerializer,
)


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication that reads from cookies instead of Authorization header."""

    def authenticate(self, request):
        """Extract and validate JWT from cookies."""
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except (TokenError, AuthenticationFailed):
            raise AuthenticationFailed("Invalid or expired token in cookies.")


def _get_user_model():
    """Get User model lazily."""
    return get_user_model()


class RegistrationView(APIView):
    """API view for registering a new user account."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new user account."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            saved_account = serializer.save()
            data = {"username": saved_account.username, "email": saved_account.email, "user_id": saved_account.pk}
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """API view to log out the current user by deleting auth cookies."""

    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Delete the access and refresh token cookies."""
        response = Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token", path="/", samesite="LAX")
        response.delete_cookie("refresh_token", path="/", samesite="LAX")
        return response


class ProfileView(APIView):
    """API view to read or update the authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return the profile of the current user."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Partially update the profile of the current user."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """Login view that sets JWT tokens as httpOnly cookies instead of returning them in the body."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate the user and set access and refresh token cookies."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response({"message": "Login successful."})

        response.set_cookie(key="access_token", value=access, path="/", httponly=True, secure=False, samesite="LAX")
        response.set_cookie(key="refresh_token", value=refresh, path="/", httponly=True, secure=False, samesite="LAX")

        response.data = {"message": "Login successful."}
        return response


def _get_refresh_token_from_request(request):
    """Extract refresh token from request cookies.

    Returns token or raises AuthenticationFailed."""
    refresh_token = request.COOKIES.get("refresh_token")
    if refresh_token is None:
        raise AuthenticationFailed("Refresh token not found.")
    return refresh_token


def _validate_and_get_access_token(serializer):
    """Validate serializer and extract access token.

    Returns access token or raises AuthenticationFailed."""
    try:
        serializer.is_valid(raise_exception=True)
    except (ValidationError, TokenError):
        raise AuthenticationFailed("Refresh token is invalid or expired.")
    return serializer.validated_data.get("access")


class CookieTokenRefreshView(TokenRefreshView):
    """Token refresh view that reads the refresh token from a cookie."""

    def post(self, request, *args, **kwargs):
        """Issue a new access token using the refresh_token cookie."""
        refresh_token = _get_refresh_token_from_request(request)
        serializer = self.get_serializer(data={"refresh": refresh_token})
        access_token = _validate_and_get_access_token(serializer)

        response = Response({"detail": "Token refreshed"})
        response.set_cookie(
            key="access_token", value=access_token, path="/", httponly=True, secure=False, samesite="LAX"
        )
        return response


class VerifyEmailView(APIView):
    """API view to verify email address with token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Verify email and activate user account."""
        token = request.data.get("token")
        user_id = request.data.get("user_id")

        if not token or not user_id:
            return Response(
                {"detail": "Token and user_id required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = _get_user_model().objects.get(pk=user_id, verification_token=token)
        except _get_user_model().DoesNotExist:
            return Response(
                {"detail": "Invalid token or user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.verification_token = ""
        user.save()

        return Response(
            {"detail": "Email verified successfully. You can now login."},
            status=status.HTTP_200_OK,
        )


class ActivateView(APIView):
    """API view to activate user account via email link."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Activate user account with base64 encoded user ID and token."""
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = _get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, _get_user_model().DoesNotExist):
            return Response(
                {"detail": "Invalid activation link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            AccessToken(token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired activation token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save()

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK,
        )


class PasswordResetView(APIView):
    """API view to request password reset via email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Send password reset email to user."""
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordConfirmView(APIView):
    """API view to confirm password reset with token."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Reset password with base64 encoded user ID and token."""
        serializer = PasswordConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = _get_user_model().objects.get(pk=user_id)
        except (TypeError, ValueError, _get_user_model().DoesNotExist):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            AccessToken(token)
        except TokenError:
            return Response(
                {"detail": "Invalid or expired password reset token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Your Password has been successfully reset."},
            status=status.HTTP_200_OK,
        )

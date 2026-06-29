from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegistrationSerializer, UserSerializer, CustomTokenObtainPairSerializer

User = get_user_model()


class RegistrationView(APIView):
    """Register new user with email + password. Returns HTTP 201."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create and return new user. Triggers activation email via signal."""
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"user": {"id": user.id, "email": user.email}, "token": "activation_token"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """Logout: delete cookies and blacklist refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Revoke tokens, blacklist refresh token, delete cookies."""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass

        response = Response(
            {"detail": "Logout successful! All tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK,
        )
        response.delete_cookie("access_token", path="/", samesite="LAX")
        response.delete_cookie("refresh_token", path="/", samesite="LAX")
        return response


class ProfileView(APIView):
    """Get/update authenticated user profile (email, birthdate, address, phone)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve current user profile."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        """Partial update to user profile fields."""
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CookieTokenObtainPairView(TokenObtainPairView):
    """Login with email + password. Sets access/refresh tokens as HTTP-only cookies."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Authenticate via email + password, set token cookies."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        response = Response(
            {
                "detail": "Login successful",
                "user": {
                    "id": serializer.validated_data.get("user_id"),
                    "username": serializer.validated_data.get("username"),
                },
            }
        )

        response.set_cookie(key="access_token", value=access, path="/", httponly=True, secure=False, samesite="LAX")
        response.set_cookie(key="refresh_token", value=refresh, path="/", httponly=True, secure=False, samesite="LAX")

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """Refresh expired access token using refresh token from cookie."""

    def post(self, request, *args, **kwargs):
        """Read refresh_token cookie, issue new access_token."""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"detail": "Refresh token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})

        if not serializer.is_valid():
            return Response(
                {"detail": "Refresh token is invalid."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        access_token = serializer.validated_data.get("access")

        response = Response({"detail": "Token refreshed", "access": access_token})
        response.set_cookie(
            key="access_token", value=access_token, path="/", httponly=True, secure=False, samesite="LAX"
        )
        return response


class ActivationView(APIView):
    """Activate user account via email verification link."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Decode uidb64, validate token, set is_active=True."""
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid activation link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Activation token expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        return Response({"message": "Account successfully activated."}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):
    """Request password reset link via email."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Send password reset email if user exists. Always returns 200 (prevents enumeration)."""
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            reset_link = f"{settings.FRONTEND_URL}/reset/{uidb64}/{token}/"

            subject = "Reset Your Password"
            message = f"""
Hello {user.email},

We received a request to reset your password. Click the link below:

{reset_link}

If you didn't request this, please ignore this email.

Best regards,
The Team
"""

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except User.DoesNotExist:
            pass  # Don't reveal if email exists

        return Response({"detail": "An email has been sent to reset your password."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirm password reset: validate token + set new password."""

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Verify token, check passwords match, update user password."""
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if new_password != confirm_password:
            return Response({"detail": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Reset token expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"detail": "Your Password has been successfully reset."}, status=status.HTTP_200_OK)

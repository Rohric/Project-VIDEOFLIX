from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """JWT authentication reading tokens from HTTP-only cookies instead of headers."""

    def authenticate(self, request):
        """Get token from cookies and validate. Tries header first, then cookies."""
        # Try Authorization header first
        auth = super().authenticate(request)
        if auth is not None:
            return auth

        # Fall back to access_token cookie
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return (self.get_user(validated_token), validated_token)
        except Exception:
            return None

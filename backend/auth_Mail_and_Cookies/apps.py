"""Auth app configuration. Registers signals for email on user creation."""
from django.apps import AppConfig


class AuthMailAndCookiesConfig(AppConfig):
    """Auth app with email verification, JWT cookies, password reset."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "auth_Mail_and_Cookies"

    def ready(self):
        """Register signal handlers when app is ready."""
        import auth_Mail_and_Cookies.signals  # noqa: F401

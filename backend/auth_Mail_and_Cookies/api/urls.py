"""Auth API endpoints: register, login, logout, token refresh, profile, activation, password reset."""
from django.urls import path

from .views import (
    ActivationView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetView,
    ProfileView,
    RegistrationView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="registration"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("activate/<str:uidb64>/<str:token>/", ActivationView.as_view(), name="activate"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_confirm/<str:uidb64>/<str:token>/", PasswordResetConfirmView.as_view(), name="password_confirm"),
]

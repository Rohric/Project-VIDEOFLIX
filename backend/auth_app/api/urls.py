from django.urls import path

from .views import (
    ActivateView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    LogoutView,
    PasswordConfirmView,
    PasswordResetView,
    ProfileView,
    RegistrationView,
    VerifyEmailView,
)

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="registration"),
    path("login/", CookieTokenObtainPairView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("activate/<str:uidb64>/<str:token>/", ActivateView.as_view(), name="activate"),
    path("password_reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password_confirm/<str:uidb64>/<str:token>/", PasswordConfirmView.as_view(), name="password_confirm"),
]

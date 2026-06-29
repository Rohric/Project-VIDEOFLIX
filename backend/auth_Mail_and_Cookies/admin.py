"""Admin interface for User model."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()


class CustomUserAdmin(BaseUserAdmin):
    """Admin for User model: manage authentication, permissions, profile."""

    # Was in der Liste angezeigt wird
    list_display = ("email", "username", "is_active", "is_staff", "date_joined")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("email", "username")

    # Felder beim Editieren
    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "birthdate", "address", "handynumber")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Dates", {"fields": ("last_login", "date_joined")}),
    )

    # Felder beim User hinzufügen
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "username", "password1", "password2")}),
        ("Profile", {"fields": ("first_name", "last_name", "birthdate", "address", "handynumber")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser")}),
    )

    readonly_fields = ("date_joined", "last_login")
    ordering = ("-date_joined",)  # Neueste oben


admin.site.register(User, CustomUserAdmin)

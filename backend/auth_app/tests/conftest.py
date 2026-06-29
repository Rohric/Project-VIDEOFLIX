import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def test_user(db):
    """Create an active test user."""
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="securepass123",
        is_active=True
    )


@pytest.fixture
def inactive_test_user(db):
    """Create an inactive test user (not yet verified)."""
    User = get_user_model()
    return User.objects.create_user(
        username="inactive",
        email="inactive@example.com",
        password="securepass123",
        is_active=False
    )

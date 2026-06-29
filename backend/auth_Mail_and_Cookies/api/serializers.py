from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    """Registration: validate email + password, auto-generate username."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate_confirmed_password(self, value):
        """Verify passwords match."""
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def save(self):
        """Create user with auto-generated username. Set is_active=False."""
        email = self.validated_data["email"]
        password = self.validated_data["password"]

        # Auto-generate username from email prefix
        username = email.split("@")[0]

        user = User(email=email, username=username, is_active=False)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """User profile serializer: read/update user data."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "birthdate", "address", "handynumber"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login serializer: authenticate by email + password, return JWT tokens."""

    email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Check email + password, verify account is active, return tokens."""
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationFailed("Account not activated. Please check your email.")

        # Use username for SimpleJWT internally
        data = super().validate({"username": user.username, "password": password})

        # Add user info for response
        data["user_id"] = user.id
        data["username"] = user.username

        return data

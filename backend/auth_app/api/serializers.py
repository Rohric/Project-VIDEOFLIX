from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with password confirmation."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {"password": {"write_only": True}, "email": {"required": True}}

    def validate_confirmed_password(self, value):
        """Check that password and confirmed_password match."""
        password = self.initial_data.get("password")
        if password and value and password != value:
            raise serializers.ValidationError("Passwords do not match.")
        return value

    def validate_email(self, value):
        """Check that the email address is not already in use."""
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email address is already in use.")
        return value

    def save(self):
        """Create and return a new user with the validated data.

        Returns the saved User instance."""
        User = get_user_model()
        pw = self.validated_data["password"]

        account = User(
            email=self.validated_data["email"],
            username=self.validated_data["username"],
            is_active=False,  # User must verify email first
        )
        account.set_password(pw)
        account.save()
        return account


class UserSerializer(serializers.ModelSerializer):
    """Serializer for reading and updating user profile data."""

    class Meta:
        model = get_user_model()
        fields = ["id", "username", "email", "birthdate", "address"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Token serializer that authenticates by username and password."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate credentials and return access and refresh tokens."""
        User = get_user_model()
        username = attrs.get("username")
        password = attrs.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid username or password.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid username or password.")

        if not user.is_active:
            raise AuthenticationFailed("Please verify your email before logging in.")

        data = super().validate({"username": user.username, "password": password})
        return data


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Validate email format."""
        return value


class PasswordConfirmSerializer(serializers.Serializer):
    """Serializer for password confirmation."""

    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Check that passwords match."""
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import TokenHistory

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password2",
            "first_name",
            "last_name",
            "token_auto_renew",
            "token_validity_days",
        )
        extra_kwargs = {
            "token_auto_renew": {"required": False},
            "token_validity_days": {"required": False},
        }

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        user = User.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    token_info = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "token_info",
            "daily_request_limit",
            "daily_requests_made",
            "last_request_date",
            "token_auto_renew",
            "token_validity_days",
        )
        read_only_fields = ("token_info", "daily_requests_made", "last_request_date")

    def get_token_info(self, obj):
        return obj.get_token_info()


class TokenRegenerationSerializer(serializers.Serializer):
    save_old = serializers.BooleanField(default=True)
    auto_renew = serializers.BooleanField(required=False)
    validity_days = serializers.IntegerField(required=False, min_value=1, max_value=365)


class TokenHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TokenHistory
        fields = ("token", "created_at", "expires_at", "is_active")
        read_only_fields = fields

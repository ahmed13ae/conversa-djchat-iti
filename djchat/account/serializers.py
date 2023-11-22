from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)

from .models import Account


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = Account
        fields = ("username", "password", "email", "profile_picture")

    def validate_password(self, value):
        validate_password(value, self.instance)
        return value

    def validate_username(self, value):
        if Account.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        profile_picture = validated_data.pop("profile_picture", None)
        user = Account.objects.create_user(**validated_data)
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()
        return user


# class RegisterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Account
#         fields = ("username", "password")

#     def is_valid(self, raise_exception=False):
#         valid = super().is_valid(raise_exception=raise_exception)

#         if valid:
#             username = self.validated_data["username"]
#             if Account.objects.filter(username=username).exists():
#                 self._errors["username"] = ["username already exists"]
#                 valid = False

#         return valid

#     def create(self, validated_data):
#         user = Account.objects.create_user(**validated_data)
#         return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ("username",)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(cls, user):
        token = super().get_token(user)
        token["example"] = "example"

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user_id"] = self.user.id
        return data


class JWTCookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get(
            settings.SIMPLE_JWT["REFRESH_TOKEN_NAME"])

        if attrs["refresh"]:
            return super().validate(attrs)
        else:
            raise InvalidToken("No valid refresh token found")

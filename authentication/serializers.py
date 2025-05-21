from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Verification
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from authentication.models import CustomUser
import base64

class UserSerializer(serializers.ModelSerializer):
    """ModelSerializer for User model
    """

    class Meta:
        model = get_user_model()
        # fields = ('id', 'username', 'password', 'email')
        fields = (
            "id",
            "first_name",
            "last_name",
            "username",
            "password",
            "email",
            "is_email_verified",
            "profile_image",
            "created_at",
            "updated_at"
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True}
        }

    def create(self, validated_data):
        """in saving user, the password should be hashed then saved using set_password method
            not saved directly
            so the create method is overridden to use set_password
        Args:
            validated_data: the data about user that is validated, it is like a dictionary

        Returns:
            CustomUser: the saved model of user
        """
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

class UserLoginSerializer(serializers.Serializer):
    """serializer for user login data (username and password)
       both are just charfields
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class VerificationSerializer(serializers.ModelSerializer):
    """serializer for verification code model
    """
    class Meta:
        model = Verification
        fields = ('code',)

class ChangePasswordSerializer(serializers.Serializer):
    """serializer to change user password
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ForgotPasswordSerializer(serializers.Serializer):
    """ serializer for forget-password request
    """
    email = serializers.EmailField(required=True)


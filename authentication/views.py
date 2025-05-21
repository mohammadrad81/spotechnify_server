import uuid
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from spotechnify_server.settings import EMAIL_HOST_USER
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework import views, permissions, generics
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import QuerySet
from .serializers import (UserSerializer,
                          UserLoginSerializer,
                          VerificationSerializer,
                          ChangePasswordSerializer,
                          ForgotPasswordSerializer)
from authentication.models import (
    Verification,
    CustomUser
)

def get_jwt_token(user: CustomUser) -> RefreshToken:
    """creates a token for user and sets the "email_verified" attribute for user and returns it

    Args:
        user (CustomUser): the user that the token is created for

    Returns:
        RefreshToken: jwt token that contains a refresh and access token
        token contains a refresh token and an access token
        user uses access token to request to server, and if it is expires, he/she can request to refresh service to
        get another access token, if refresh token is also expired, he/she must login again
    """


    token = RefreshToken.for_user(user)
    token["email_verified"] = user.is_email_verified
    return token

def get_random_password() -> str:
    """creates a random string and returns it (it is uuid4)


    Returns:
        str: random password
    """
    uuid_password = uuid.uuid4()
    password = str(uuid_password)
    password = password.replace("-", "")
    return password

class SignUpView(views.APIView):
    """signs up the user sending the request
    """

    def post(self, request: Request) ->Response:
        """if request method is POST, this method is called
            this method emails the user the verification code so he/she can verify his/her email
            and also signs up the user

        Args:
            request (Request): the request that is sent, containing data about user (username, email, password)

        Returns:
            Response: the response to user (jwt token, message, ...)
        """
        serializer = UserSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        verification = Verification.get_or_create_for_user(user=user)
        subject = "Spotechnify Email Verification"
        message = f"""
Dear user
Welcome to Spotechnify
{user.username}
Verification Code:
{verification.code}
"""
        recipient_list = [serializer.validated_data['email']]
        try:
            send_mail(subject, message, EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        token = get_jwt_token(user=user)
        serializer = UserSerializer(instance=user, context={"request": request})
        data = {
            "message": "Verification Code Sent",
            "refresh": str(token),
            "access": str(token.access_token),
            "user": serializer.data
        }
        return Response(data=data, status=status.HTTP_201_CREATED)


class JwtTokenObtainView(views.APIView):
    """user can login via this view, to get a new token
    """

    def post(self, request):
        """if request method is POST, this method is called
            this method verifies that username and password of user is correct
            and creates a new token for user and sends to him/her

        Args:
            request (Request): the request that is sent, containing login data (username, password)

        Returns:
            Response: the response to user, containing token and data about user
        """
        serializer = UserLoginSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password, )
        if user is None:
            detail = "Username or Password (or both) is incorrect"
            raise AuthenticationFailed(detail=detail)
        else:
            token = get_jwt_token(user=user)
            serializer = UserSerializer(instance=user, context={"request": request})
            data = {
                "refresh": str(token),
                "access": str(token.access_token),
                "user": serializer.data
            }
            return Response(data=data, status=status.HTTP_200_OK)

class ResendVerification(views.APIView):
    """if verification code is not sent to user email, this view resends it
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """if user sends request with GET method, this method is called

        Args:
            request (Request): the request the user sent (empty body)

        Returns:
            Response: response that is sent to user, containing success/fail message
        """
        user = self.request.user
        verification = Verification.get_or_create_for_user(user=user)
        subject = "Spotify Verification Code"
        message = f"""
Dear user
Welcome to Spotechnify
{user.username}
Verification Code:
{verification.code}
"""
        recipient_list = [user.email]
        try:
            send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=False)
        except Exception as e:
            return Response({"message": "There was an internal problem"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message": "Verification Code Sent."}, status=status.HTTP_200_OK)

class Verify(views.APIView):
    """verifies the user email via verification code sent to his/her email
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """if user sends request with GET method, this method is called

        Args:
            request (Request): the request sent by user, containing verification code

        Returns:
            Response: the response sent to user, containing success/fail message and tokens
        """
        user = self.request.user
        if user.is_email_verified:
            return Response({"message": f"Email of user {user.username} is already verified"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VerificationSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        verification = get_object_or_404(Verification, user=user, code=serializer.validated_data['code'])
        verification.delete()
        user.is_email_verified = True
        user.email_verification_datetime = timezone.datetime.now()
        user.save()
        token = get_jwt_token(user=user)
        data = {"message": f"Email of user: {user.username} verified",
                "refresh": str(token),
                "access": str(token.access_token)}
        return Response(data=data, status=status.HTTP_202_ACCEPTED)

class UserVerificationCheckAPIView(views.APIView):
    """check user email verification
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """if user sends request with GET request, this method is called

        Args:
            request (Request): the request the user sent, empty body

        Returns:
            Response: response sent to user, containing the information that user is email-verified or not
        """
        user = self.request.user
        return Response(data={"email_verified": user.is_email_verified}, status=status.HTTP_200_OK)


class ForgotPassword(views.APIView):
    """if user forgot his/her password, sends his/her email to this view to receive a new password in his/her email
    """

    def post(self, request: Request) -> Response:
        """if user sends request with POST method, this method is called
            changes the user's password and emails new password to user's email

        Args:
            request (Request): the request sent by user, containing user's email

        Returns:
            Response: the response sent to user, containing success message
        """
        serializer = ForgotPasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(get_user_model(), email=serializer.validated_data['email'])
        new_password = get_random_password()
        user.set_password(new_password)
        user.save()
        subject = "Spotechnify New Password"
        message = f"""
Dear user
Welcome to Spotechnify
{user.username}
Your new password:
{new_password}
"""
        recipient_list = [user.email]
        send_mail(subject, message, EMAIL_HOST_USER, recipient_list, fail_silently=True)
        return Response({"message": "New password sent"}, status=status.HTTP_201_CREATED)

class ChangePassword(views.APIView):
    """changes the user's password (while user is logged in)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """if user sends request with POST method, this method is called
            it takes old and new password, if the old password is the user's current password, user's password
            will change to new password

        Args:
            request (Request): the request sent by user, containing old and new passwords

        Returns:
            Response: the response
        """
        user = self.request.user
        serializer = ChangePasswordSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"error": "Wrong Password"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


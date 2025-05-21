from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

class CustomUser(AbstractUser):
    """ custom model for user
    """
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_datetime = models.DateTimeField(default=None, null=True)
    profile_image = models.ImageField(upload_to='profile_images', default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Verification(models.Model):
    """a 6 digit numeric code to verify user email
       this code is generated and emailed to the user after sign up
       the user must enter the sent code to verify his/her email

    """
    CODE_LENGTH = 6
    code = models.CharField(max_length=CODE_LENGTH)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def get_or_create_for_user(user: CustomUser):
        """ if there is a verification for the user already, returns it
            otherwise a new one will be created and returns it

        Args:
            user (CustomUser): _description_

        Returns:
            _type_: _description_
        """
        if Verification.objects.filter(user=user).exists():
            return Verification.objects.get(user=user)
        else:
            return Verification.objects.create(code=get_random_string(length=Verification.CODE_LENGTH, allowed_chars='1234567890'), user=user)

    def __str__(self) -> str:
        return f"user: {self.user.username}"
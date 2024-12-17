from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField

from users_management.constants import USER_TYPES, STUDENT_USER_TYPE
from users_management.managers import CustomUserManager
from users_management.tokens import generate_referral_code

class User(AbstractUser):
    """
    Custom User model using email as the unique identifier instead of a username.
    """
    username = None
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    user_type = models.CharField(max_length=31, choices=USER_TYPES, default=STUDENT_USER_TYPE, blank=True, null=True)
    is_institute = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=50, blank=True, null=True, unique=True)
    recommended_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, blank=True, null=True, related_name="referrals"
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate referral code for institutes.
        """
        if self.is_institute and not self.referral_code:
            self.referral_code = generate_referral_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User Model that extends Django's built-in AbstractUser.
    """
    class UserType(models.TextChoices):
        VENDOR = 'vendor', _('Vendor')
        CUSTOMER = 'customer', _('Customer')

    # Add custom fields
    user_type = models.CharField(
        _('user type'),
        max_length=10,
        choices=UserType.choices,
        default=UserType.CUSTOMER
    )
    phone = models.CharField(
        _('phone number'),
        max_length=15,
        blank=True,
        null=True
    )
    location = models.CharField(
        _('location'),
        max_length=255,
        blank=True,
        null=True
    )

    # Add any additional fields here
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def __str__(self):
        return self.email or self.username

    @property
    def is_vendor(self):
        return self.user_type == self.UserType.VENDOR

    @property
    def is_customer(self):
        return self.user_type == self.UserType.CUSTOMER
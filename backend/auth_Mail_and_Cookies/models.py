from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class User(AbstractUser):
    """Custom user model with optional birthdate and address fields."""

    handynumber = models.CharField(max_length=32, blank=True)
    address = models.CharField(max_length=255, blank=True)
    birthdate = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

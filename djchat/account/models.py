from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    # Add an image field
    profile_picture = models.ImageField(upload_to='account/', blank=True, null=True)

    def __str__(self):
        return self.username

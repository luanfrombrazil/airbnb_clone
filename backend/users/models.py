from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_host = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuário da plataforma: hóspede por padrão, anfitrião se is_host=True."""

    is_host = models.BooleanField("é anfitrião?", default=False)

    def __str__(self):
        return self.username

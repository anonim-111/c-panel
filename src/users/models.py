from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    telegram_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.username
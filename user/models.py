from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings


class Profile(AbstractUser):
    about = models.CharField(max_length=255, blank=True, null=True, default=None)
    avatar = models.ImageField(upload_to='users/', default=settings.AVATAR_DEFAULT)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    @property
    def is_custom_avatar(self):
        return self.avatar != settings.AVATAR_DEFAULT

    @property
    def avatar_default(self):
        return settings.AVATAR_DEFAULT

    def __str__(self):
        return f"{self.username}"


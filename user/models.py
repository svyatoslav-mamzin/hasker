from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

AVATAR_DEFAULT = 'users/avatar_def.jpeg'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=255, blank=True, null=True, default=None)
    avatar = models.ImageField(upload_to='users/', default=AVATAR_DEFAULT)
    created = models.DateTimeField(auto_now_add=True, auto_now=False)

    @property
    def is_custom_avatar(self):
        return self.avatar != AVATAR_DEFAULT

    @property
    def avatar_default(self):
        return AVATAR_DEFAULT

    def __str__(self):
        return f"{self.user.username}"


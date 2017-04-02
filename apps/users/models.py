from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    avatar = models.ImageField(_('Аватар'), upload_to='avatars', max_length=255, blank=True, null=True)

    def get_avatar(self):
        return settings.MEDIA_URL + self.avatar.name

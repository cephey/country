from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from apps.utils.image import dummy_image


class User(AbstractUser):
    avatar = models.ImageField(_('Аватар'), upload_to='avatars', max_length=255, blank=True, null=True)

    def get_avatar(self):
        if self.avatar:
            return settings.MEDIA_URL + self.avatar.name
        return dummy_image(self.username)

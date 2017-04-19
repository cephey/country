from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ForumConfig(AppConfig):
    name = 'apps.forum'
    verbose_name = _('Форум')

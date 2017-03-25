from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BloggersConfig(AppConfig):
    name = 'bloggers'
    verbose_name = _('Блогеры')

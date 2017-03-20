from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuthorsConfig(AppConfig):
    name = 'apps.authors'
    verbose_name = _('Авторы')

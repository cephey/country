from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PollsConfig(AppConfig):
    name = 'apps.polls'
    verbose_name = _('Опросы')

    def ready(self):
        import apps.polls.receivers  # noqa

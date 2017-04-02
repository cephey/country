from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VotesConfig(AppConfig):
    name = 'apps.votes'
    verbose_name = _('Голоса')

    def ready(self):
        import apps.votes.receivers  # noqa

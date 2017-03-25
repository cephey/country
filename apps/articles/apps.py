from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ArticlesConfig(AppConfig):
    name = 'apps.articles'
    verbose_name = _('Статьи')

    def ready(self):
        import apps.articles.receivers  # noqa

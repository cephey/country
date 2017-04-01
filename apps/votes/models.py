from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from apps.utils.models import TimeStampedModel


class Vote(TimeStampedModel):
    token = models.CharField(_('Идентификатор'), max_length=40, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    object_id = models.IntegerField(verbose_name=_('ID объекта'), db_index=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('Тип объекта'))
    content_object = GenericForeignKey()
    score = models.IntegerField(_('Оценка'))

    class Meta:
        verbose_name = _('Голос')
        verbose_name_plural = _('Голоса')
        ordering = ('-pk',)

    def __str__(self):
        if self.user_id:
            return 'User {} score {}'.format(self.user_id, self.score)
        return 'Token {} score {}'.format(self.token, self.score)

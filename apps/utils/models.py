from django.db import models
from django.utils.translation import ugettext_lazy as _


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.

    """
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True, editable=False)

    class Meta:
        abstract = True

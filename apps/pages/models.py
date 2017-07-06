from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.utils.models import TimeStampedModel
from apps.pages.managers import PartitionQuerySet, ResourceQuerySet

RESOURCE_UPLOAD_PATH = 'pages'


class Partition(models.Model):
    name = models.CharField(_('Название'), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    ext_id = models.IntegerField(_('Внешний ID'), editable=False, default=0, db_index=True)

    objects = models.Manager.from_queryset(PartitionQuerySet)()

    class Meta:
        verbose_name = _('Тип')
        verbose_name_plural = _('Типы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pages:partition', kwargs={'pk': self.id})


class Resource(TimeStampedModel):
    partition = models.ForeignKey('pages.Partition', verbose_name=_('Тип'))
    name = models.CharField(_('Название'), max_length=255)
    logo = models.ImageField(_('Логотип'), upload_to=RESOURCE_UPLOAD_PATH, max_length=255, blank=True, null=True)
    url = models.CharField(_('Адрес'), max_length=255, blank=True)
    rating = models.PositiveIntegerField(_('Рейтинг'), default=0)
    is_active = models.BooleanField(default=True)

    multimedia = models.ForeignKey('articles.Multimedia', blank=True, null=True)

    objects = models.Manager.from_queryset(ResourceQuerySet)()

    class Meta:
        verbose_name = _('Сайт')
        verbose_name_plural = _('Сайты')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    @property
    def get_logo(self):
        return settings.MEDIA_URL + self.logo.name

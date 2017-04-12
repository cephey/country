from django.db import models
from django.urls import reverse
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from apps.utils.models import TimeStampedModel
from apps.pages.managers import ResourceTypeQuerySet, ResourceQuerySet


class ResourceType(models.Model):
    name = models.CharField(_('Название'), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager.from_queryset(ResourceTypeQuerySet)()

    class Meta:
        verbose_name = _('Тип')
        verbose_name_plural = _('Типы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('pages:resource_list', kwargs={'pk': self.id})


class Resource(TimeStampedModel):
    type = models.ForeignKey('pages.ResourceType', verbose_name=_('Тип'))
    name = models.CharField(_('Название'), max_length=255)
    logo = models.ImageField(_('Логотип'), upload_to='pages', max_length=255, blank=True, null=True)
    url = models.CharField(_('Адрес'), max_length=255, blank=True)
    rating = models.PositiveIntegerField(_('Рейтинг'), default=0)
    is_active = models.BooleanField(default=True)

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

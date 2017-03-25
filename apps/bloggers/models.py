from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.utils.models import TimeStampedModel


class Blogger(TimeStampedModel):
    first_name = models.CharField(_('Имя'), max_length=255, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=255, blank=True)
    middle_name = models.CharField(_('Отчество'), max_length=255, blank=True)
    link = models.CharField(_('Ссылка на блог'), max_length=255, blank=True)
    photo = models.ImageField(_('Фото'), upload_to='bloggers', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Блогер')
        verbose_name_plural = _('Блогеры')
        ordering = ('-pk',)

    def __str__(self):
        return self.cover_name

    @property
    def cover_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    @property
    def icon(self):
        return '/storage/' + self.photo.name


class Entry(TimeStampedModel):
    title = models.CharField(_('Заголовок'), max_length=255)
    blogger = models.ForeignKey('bloggers.Blogger', verbose_name=_('Блогер'))
    link = models.CharField(_('Ссылка на запись'), max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Запись')
        verbose_name_plural = _('Записи')
        ordering = ('-pk',)

    def __str__(self):
        return self.title

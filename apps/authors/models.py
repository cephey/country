from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from apps.utils.models import TimeStampedModel


class Author(TimeStampedModel):
    first_name = models.CharField(_('Имя'), max_length=255, blank=True)
    last_name = models.CharField(_('Фамилия'), max_length=255, blank=True)
    middle_name = models.CharField(_('Отчество'), max_length=255, blank=True)
    description = models.TextField(_('Описание'), blank=True)
    photo = models.ImageField(_('Фото'), upload_to='authors', max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Автор')
        verbose_name_plural = _('Авторы')
        ordering = ('-pk',)

    def __str__(self):
        return self.cover_name

    @property
    def cover_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    # def get_absolute_url(self):
    #     return reverse('web:author-detail', kwargs={'pk': self.pk, 'slug': self.slug})

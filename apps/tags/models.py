from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from apps.utils.models import TimeStampedModel


class Tag(TimeStampedModel):
    name = models.CharField(_('Название'), max_length=255, unique=True)

    class Meta:
        verbose_name = _('Тег')
        verbose_name_plural = _('Теги')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('web:author-detail', kwargs={'pk': self.pk, 'slug': self.slug})


class TaggedItem(models.Model):
    tag = models.ForeignKey('tags.Tag')

    object_id = models.IntegerField(verbose_name=_('ID объекта'), db_index=True)
    content_type = models.ForeignKey(ContentType, verbose_name=_('Тип объекта'))
    content_object = GenericForeignKey()

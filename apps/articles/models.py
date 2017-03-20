from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.utils.models import TimeStampedModel


class Section(models.Model):
    name = models.CharField(_('Название'), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Раздел')
        verbose_name_plural = _('Разделы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name


class Article(TimeStampedModel):
    title = models.CharField(_('Заголовок'), max_length=255)
    content = models.TextField(_('Содержание'), blank=True)
    section = models.ForeignKey('articles.Section', verbose_name=_('Раздел'))
    authors = models.ManyToManyField('authors.Author', blank=True)
    publish_date = models.DateTimeField(_('Дата публикации'), blank=True, null=True)
    is_active = models.BooleanField(default=True)

    comments_count = models.PositiveIntegerField(_('Кол-во комментариев'), editable=False, default=0)
    # rating field

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        ordering = ('-pk',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    username = models.CharField(_('Имя'), max_length=255)
    title = models.CharField(_('Заголовок'), max_length=255, blank=True)
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)
    # votes field

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ('-pk',)

    def __str__(self):
        data = []
        if self.username:
            data.append(self.username)
        if self.title:
            data.append(self.title[:50])
        else:
            data.append(self.content[:50])
        return ': '.join(data + [self.created_at.isoformat()])

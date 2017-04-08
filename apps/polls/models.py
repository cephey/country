from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from apps.utils.models import TimeStampedModel


class Poll(TimeStampedModel):
    question = models.CharField(_('Вопрос'), max_length=255)
    sum_votes = models.PositiveIntegerField(_('Всего голосов'), editable=False, default=0)

    class Meta:
        verbose_name = _('Опрос')
        verbose_name_plural = _('Опросы')
        ordering = ('-pk',)

    def __str__(self):
        return self.question

    def get_absolute_url(self):
        return reverse('polls:detail', kwargs={'pk': self.pk})


class Choice(models.Model):
    poll = models.ForeignKey('polls.Poll', verbose_name=_('Опрос'))
    answer = models.CharField(_('Ответ'), max_length=255)
    vote_count = models.PositiveIntegerField(_('Количество проголосовавших'), editable=False, default=0)

    class Meta:
        verbose_name = _('Ответ')
        verbose_name_plural = _('Ответы')
        ordering = ('-pk',)

    def __str__(self):
        return self.answer

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation
from model_utils import Choices

from apps.utils.models import TimeStampedModel
from apps.articles.managers import ArticleQuerySet

NAVIGATE_SECTIONS = [
    'politic', 'economic', 'region', 'society', 'power', 'fpolitic', 'kompromat', 'moscow'
]


class Section(models.Model):
    name = models.CharField(_('Название'), max_length=255, unique=True)
    slug = models.CharField(_('Слаг'), max_length=255, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Раздел')
        verbose_name_plural = _('Разделы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('articles:section', kwargs={'slug': self.slug})


class Article(TimeStampedModel):
    DISCUSSION_STATUS = Choices(
        ('open', 'Открыто'),
        ('close', 'Закрыто')
    )
    STATUS = Choices(
        ('new', 'Новая'),
        ('approved', 'Одобрена')
    )
    title = models.CharField(_('Заголовок'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    content = models.TextField(_('Содержание'))
    section = models.ForeignKey('articles.Section', verbose_name=_('Раздел'), blank=True, null=True)
    is_news = models.BooleanField(_('Новость'), default=False)
    authors = models.ManyToManyField('authors.Author', verbose_name=_('Авторы'), blank=True)
    author_names = models.CharField(_('Авторы'), max_length=255, blank=True,
                                    help_text=_('Список внешних авторов через запятую'))
    publish_date = models.DateTimeField(_('Дата публикации'), blank=True, null=True)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(_('Картинка'), upload_to='articles_image', max_length=255, blank=True, null=True)
    video = models.FileField(_('Видео'), upload_to='articles_video', max_length=255, blank=True, null=True)
    source = models.CharField(_('Источник'), max_length=255, blank=True)
    source_link = models.URLField(_('Ссылка на источник'), blank=True)
    discussion_status = models.CharField(_('Статус обсуждения'), max_length=8, choices=DISCUSSION_STATUS,
                                         default=DISCUSSION_STATUS.open)
    status = models.CharField(_('Статус'), max_length=8, choices=STATUS, default=STATUS.new)
    show_comments = models.BooleanField(_('Показывать комментарии'), default=True)
    comments_count = models.PositiveIntegerField(_('Кол-во комментариев'), editable=False, default=0)
    tags = GenericRelation('tags.TaggedItem')

    votes = GenericRelation('votes.Vote')
    rating = models.FloatField(_('Рейтинг'), editable=False, default=0)
    vote_count = models.PositiveIntegerField(_('Кол-во проголосовавших'), editable=False, default=0)

    objects = models.Manager.from_queryset(ArticleQuerySet)()

    class Meta:
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        ordering = ('-pk',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.is_news:
            return reverse('articles:detail', kwargs={'slug': 'news', 'pk': self.id})
        return reverse('articles:detail', kwargs={'slug': self.section.slug, 'pk': self.id})

    @property
    def icon(self):
        """
        my $image = $news->get_multimedia_first_image;
        my $src;
        if ( $image && ref($image) ) {
            $src = $image->get_pimage('100x100');

        } elsif ($news->video) {
            $src = $news->get_preview_video_image;
        }
        """
        return settings.MEDIA_URL + self.image.name

    @property
    def video_code(self):
        return ''

    @property
    def preview(self):
        return self.description or (self.content[:400] + '...')

    @property
    def main_author(self):
        authors = self.authors.all()
        return authors[0] if authors else None

    @property
    def section_name(self):
        return 'Новости' if self.is_news else self.section.name

    @property
    def keywords(self):
        return ','.join([ti.tag.name for ti in self.tags.all()])


class Comment(models.Model):
    token = models.CharField(_('Идентификатор'), max_length=40, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    article = models.ForeignKey('articles.Article', verbose_name=_('Статья'))
    parent = models.ForeignKey('self', verbose_name=_('Родительский комментарий'), blank=True, null=True)
    username = models.CharField(_('Имя'), max_length=255)
    title = models.CharField(_('Заголовок'), max_length=255, blank=True)
    content = models.TextField(_('Содержание'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True, editable=False)
    is_active = models.BooleanField(default=True)

    votes = GenericRelation('votes.Vote')
    karma = models.IntegerField(_('Оценка'), editable=False, default=0)

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

    def get_avatar(self):
        if self.user_id:
            return self.user.get_avatar()
        if self.token:
            return 'https://dummyimage.com/45x45/ff0066/000000.png&text={}'.format(self.username[0])


class Multimedia(models.Model):
    article = models.ForeignKey('articles.Article', verbose_name=_('Статья'))
    description = models.TextField(_('Описание'), blank=True)
    link = models.URLField(_('Ссылка'), blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True, editable=False)

    class Meta:
        verbose_name = _('Мультимедиа')
        verbose_name_plural = _('Мультимедиа')
        ordering = ('-pk',)


class Notice(TimeStampedModel):
    STATUS = Choices(
        ('new', 'Новый'),
        ('approved', 'Одобрен')
    )
    content = models.CharField(_('Содержание'), max_length=200)
    status = models.CharField(_('Статус'), max_length=8, choices=STATUS, default=STATUS.new)

    class Meta:
        verbose_name = _('Анонс')
        verbose_name_plural = _('Анонсы')
        ordering = ('-pk',)

    def __str__(self):
        return self.content[:50]

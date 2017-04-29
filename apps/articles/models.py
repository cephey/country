from collections import namedtuple

from django.conf import settings
from django.db import models
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.utils.feedgenerator import RssFeed, rfc2822_date
from django.contrib.contenttypes.fields import GenericRelation
from model_utils import Choices

from apps.utils.models import TimeStampedModel
from apps.utils.image import dummy_image
from apps.utils.video import VideoHelper
from apps.articles.managers import ArticleQuerySet, SectionQuerySet, CommentQuerySet, NoticeQuerySet

Partition = namedtuple('Partition', ['slug', 'name', 'get_absolute_url', 'get_pda_url'])
BEST = 'best'
NEWS = 'news'
VIDEO = 'video'

NAVIGATE_SECTIONS = [
    'politic', 'economic', 'region', 'society', 'power', 'fpolitic', 'kompromat', 'moscow'
]
GENERIC_SECTIONS = {
    BEST: Partition(slug=BEST, name=_('Лучшие статьи ФОРУМ.мск за последнюю неделю'),
                    get_absolute_url=reverse_lazy('articles:section', kwargs={'slug': BEST}),
                    get_pda_url=reverse_lazy('pda:section', kwargs={'slug': BEST})),
    NEWS: Partition(slug=NEWS, name=_('Новости'),
                    get_absolute_url=reverse_lazy('articles:section', kwargs={'slug': NEWS}),
                    get_pda_url=reverse_lazy('pda:section', kwargs={'slug': NEWS})),
    VIDEO: Partition(slug=VIDEO, name=_('Видео'),
                     get_absolute_url=reverse_lazy('articles:section', kwargs={'slug': VIDEO}),
                     get_pda_url=reverse_lazy('pda:section', kwargs={'slug': VIDEO}))
}
VIDEO_SECTIONS = [
    'video_politic', 'video_economic', 'video_accidents', 'video_fpolitic', 'video_society', 'video_national',
    'video_partner_lugansk24', 'video_partner_dorenko', 'video_partner_krasnoetv', 'video_partner_nevextv'
]


class Section(models.Model):
    name = models.CharField(_('Название'), max_length=255)
    slug = models.CharField(_('Слаг'), max_length=255, unique=True)
    is_video = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = models.Manager.from_queryset(SectionQuerySet)()

    class Meta:
        verbose_name = _('Раздел')
        verbose_name_plural = _('Разделы')
        ordering = ('-pk',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('articles:section', kwargs={'slug': self.slug})

    def get_pda_url(self):
        return reverse('pda:section', kwargs={'slug': self.slug})


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
    source = models.CharField(_('Источник'), max_length=255, blank=True)
    source_link = models.URLField(_('Ссылка на источник'), blank=True)
    discussion_status = models.CharField(_('Статус обсуждения'), max_length=8, choices=DISCUSSION_STATUS,
                                         default=DISCUSSION_STATUS.open)
    status = models.CharField(_('Статус'), max_length=8, choices=STATUS, default=STATUS.new)
    show_comments = models.BooleanField(_('Показывать комментарии'), default=True)
    comments_count = models.PositiveIntegerField(_('Кол-во комментариев'), editable=False, default=0)
    tags = GenericRelation('tags.TaggedItem')

    image = models.ImageField(_('Картинка'), upload_to='articles_image', max_length=255, blank=True, null=True)
    video = models.URLField(_('Ссылка на видео'), blank=True)
    thumbnail = models.CharField(_('Ссылка на превью'), max_length=200, blank=True)

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
            return reverse('articles:detail', kwargs={'slug': NEWS, 'pk': self.id})
        if self.section.is_video:
            return reverse('articles:detail', kwargs={'slug': VIDEO, 'pk': self.id})
        return reverse('articles:detail', kwargs={'slug': self.section.slug, 'pk': self.id})

    def get_pda_url(self):
        if self.is_news:
            return reverse('pda:detail', kwargs={'slug': NEWS, 'pk': self.id})
        if self.section.is_video:
            return reverse('pda:detail', kwargs={'slug': VIDEO, 'pk': self.id})
        return reverse('pda:detail', kwargs={'slug': self.section.slug, 'pk': self.id})

    @property
    def icon(self):
        if self.image:
            return settings.MEDIA_URL + self.image.name
        if self.video:
            return self.thumbnail

    @property
    def video_code(self):
        return VideoHelper(self.video).iframe_code

    @property
    def preview(self):
        return self.description or (self.content[:400] + '...')

    @property
    def main_author(self):
        authors = self.authors.all()
        return authors[0] if authors else None

    @property
    def keywords(self):
        return ','.join([ti.tag.name for ti in self.tags.all()])

    def save(self, **kwargs):
        if self.video:
            self.thumbnail = VideoHelper(self.video).thumbnail
        return super().save(**kwargs)


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

    objects = models.Manager.from_queryset(CommentQuerySet)()

    class Meta:
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        ordering = ('-pk',)

    def __str__(self):
        data = []
        if self.username:
            data.append(self.username)
        data.append(self.subject)
        return ': '.join(data + [self.created_at.isoformat()])

    @property
    def subject(self):
        if self.title:
            return self.title[:50]
        return self.content[:50]

    def get_avatar(self):
        if self.user_id:
            return self.user.get_avatar()
        if self.token:
            return dummy_image(self.username)


class Multimedia(models.Model):
    article = models.ForeignKey('articles.Article', verbose_name=_('Статья'))
    link = models.URLField(_('Ссылка на youtube'), blank=True)
    description = models.TextField(_('Описание'), blank=True)
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

    objects = models.Manager.from_queryset(NoticeQuerySet)()

    class Meta:
        verbose_name = _('Анонс')
        verbose_name_plural = _('Анонсы')
        ordering = ('-pk',)

    def __str__(self):
        return self.content[:50]


class Rss201rev2Feed(RssFeed):
    # Spec: http://blogs.law.harvard.edu/tech/rss
    _version = "2.0"

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        handler.addQuickElement('pubDate', rfc2822_date(self.latest_post_date()))

    def add_item_elements(self, handler, item):
        handler.addQuickElement('title', item['title'])
        handler.addQuickElement('link', item['link'])
        if item['description'] is not None:
            handler.addQuickElement('description', item['description'])

        if item['pubdate'] is not None:
            handler.addQuickElement('pubDate', rfc2822_date(item['pubdate']))
        if item['unique_id'] is not None:
            handler.addQuickElement('guid', item['unique_id'])

        if 'custom_category' in item:
            handler.addQuickElement(
                'category',
                item['custom_category']['content'],
                item['custom_category']['extra']
            )

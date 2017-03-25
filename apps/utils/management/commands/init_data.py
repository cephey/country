import random
from django.core.management.base import BaseCommand

from apps.authors.models import Author
from apps.authors.factories import AuthorFactory
from apps.articles.models import Section, Article, Notice, Comment
from apps.articles.factories import SectionFactory, ArticleFactory, NoticeFactory, CommentFactory
from apps.bloggers.models import Blogger, Entry
from apps.bloggers.factories import BloggerFactory, EntryFactory
from apps.polls.models import Poll, Choice
from apps.polls.factories import PollFactory, ChoiceFactory


class Command(BaseCommand):
    help = 'Initial data for testing'

    def handle(self, *args, **kwargs):

        # remove all
        Notice.objects.all().delete()
        Comment.objects.all().delete()
        Article.objects.all().delete()
        Section.objects.all().delete()

        Author.objects.all().delete()
        Blogger.objects.all().delete()
        Entry.objects.all().delete()

        Poll.objects.all().delete()
        Choice.objects.all().delete()

        # create all
        authors = AuthorFactory.create_batch(30)
        sections = [
            SectionFactory(name='Политический расклад', slug='politic'),
            SectionFactory(name='Экономическая реальность', slug='economic'),
            SectionFactory(name='Жизнь регионов', slug='region'),
            SectionFactory(name='Общество и его культура', slug='society'),
            SectionFactory(name='Силовые структуры', slug='power'),
            SectionFactory(name='Особенности внешней политики', slug='fpolitic'),
            SectionFactory(name='Компрометирующие материалы', slug='kompromat'),
            SectionFactory(name='Московский листок', slug='moscow'),

            SectionFactory(name='Новости', slug='news'),
            SectionFactory(name='Лучшие статьи ФОРУМ.мск за последнюю неделю', slug='best'),
            SectionFactory(name='Видео', slug='video'),
        ]

        for section in sections:
            for i in range(random.randint(8, 12)):
                article = ArticleFactory(
                    section=section,
                    authors=random.sample(authors, random.randint(1, 2))
                )
                # Comment.objects.create(article=article, username='lolo', content='lolo')
                CommentFactory.create_batch(random.randint(0, 6), article=article)

        NoticeFactory.create_batch(16)

        polls = PollFactory.create_batch(3)
        for poll in polls:
            ChoiceFactory.create_batch(random.randint(3, 6), poll=poll)

        bloggers = BloggerFactory.create_batch(6)
        for blogger in bloggers:
            EntryFactory.create_batch(random.randint(2, 8), blogger=blogger)

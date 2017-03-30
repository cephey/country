import random
from faker import Faker
from django.core.management.base import BaseCommand

from apps.authors.models import Author
from apps.authors.factories import AuthorFactory
from apps.articles.models import Section, Article, Notice, Comment
from apps.articles.factories import SectionFactory, ArticleFactory, NoticeFactory, CommentFactory
from apps.bloggers.models import Blogger, Entry
from apps.bloggers.factories import BloggerFactory, EntryFactory
from apps.polls.models import Poll, Choice
from apps.polls.factories import PollFactory, ChoiceFactory
from apps.tags.models import Tag
from apps.tags.factories import TagFactory, TaggedItemFactory


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

        Tag.objects.all().delete()

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
            SectionFactory(name='Московский листок', slug='moscow')
        ]
        a_count_list = [2, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        tags = TagFactory.create_batch(50)

        for section in sections:
            for i in range(random.randint(8, 12)):
                # authors
                params = dict(
                    section=section,
                    is_news=not bool(random.randint(0, 6))
                )
                a_count = random.choice(a_count_list)
                if not a_count:  # no authors
                    if random.randint(0, 1):
                        params['author_names'] = AuthorFactory.build().cover_name
                        print(params['author_names'])
                else:
                    params['authors'] = random.sample(authors, a_count)

                # tags
                a_tags = random.sample(tags, random.randint(0, 6))
                if a_tags:
                    params['tags'] = a_tags

                # source
                if not random.randint(0, 5):
                    params['source'] = Faker(locale='ru_RU').company()
                    if random.randint(0, 1):
                        params['source_link'] = Faker().url()

                article = ArticleFactory(**params)
                # comments
                CommentFactory.create_batch(random.randint(0, 8), article=article)

        NoticeFactory.create_batch(16)

        polls = PollFactory.create_batch(3)
        for poll in polls:
            ChoiceFactory.create_batch(random.randint(3, 6), poll=poll)

        bloggers = BloggerFactory.create_batch(6)
        for blogger in bloggers:
            EntryFactory.create_batch(random.randint(2, 8), blogger=blogger)

import random
from django.core.management.base import BaseCommand

from apps.authors.models import Author
from apps.authors.factories import AuthorFactory
from apps.articles.models import Section, Article
from apps.articles.factories import SectionFactory, ArticleFactory


class Command(BaseCommand):
    help = 'Initial data for testing'

    def handle(self, *args, **kwargs):

        # remove all
        Article.objects.all().delete()
        Section.objects.all().delete()
        Author.objects.all().delete()

        # create all
        authors = AuthorFactory.create_batch(12)
        sections = [
            SectionFactory(name='politic', slug='Политический расклад'),
            SectionFactory(name='economic', slug='Экономическая реальность'),
            SectionFactory(name='region', slug='Жизнь регионов'),
            SectionFactory(name='society', slug='Общество и его культура'),
            SectionFactory(name='power', slug='Силовые структуры'),
            SectionFactory(name='fpolitic', slug='Особенности внешней политики'),
            SectionFactory(name='kompromat', slug='Компрометирующие материалы'),
            SectionFactory(name='moscow', slug='Московский листок'),
            SectionFactory(name='news', slug='Новости'),
            SectionFactory(name='best', slug='Лучшие статьи ФОРУМ.мск за последнюю неделю')
        ]

        for section in sections:
            for i in range(random.randint(3, 10)):
                ArticleFactory(
                    section=section,
                    authors=random.sample(authors, random.randint(1, 2))
                )

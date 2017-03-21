import random
from django.core.management.base import BaseCommand

from apps.authors.factories import AuthorFactory
from apps.articles.factories import SectionFactory, ArticleFactory


class Command(BaseCommand):
    help = 'Initial data for testing'

    def handle(self, *args, **kwargs):
        authors = AuthorFactory.create_batch(12)
        sections = SectionFactory.create_batch(8)

        for section in sections:
            for i in range(random.randint(3, 10)):
                ArticleFactory(
                    section=section,
                    authors=random.sample(authors, random.randint(1, 2))
                )

from django_bulk_update.helper import bulk_update

from django.db.models import Count
from django.core.management.base import BaseCommand

from apps.articles.models import Article

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Fill Article.comments_count field'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        max_id = Article.objects.order_by('-id').first().id

        for start in range(0, max_id, BATCH_SIZE):
            end = min(start + BATCH_SIZE, max_id)

            self.stdout.write('Update articles comments_count from {} to {}...'.format(start, end))

            articles = (Article.objects
                        .filter(id__range=(start, end))
                        .only('id')
                        .annotate(count=Count('comment'))
                        .order_by())
            for article in articles:
                article.comments_count = article.count

            bulk_update(articles, update_fields=['comments_count'])

        self.stdout.write('End...')

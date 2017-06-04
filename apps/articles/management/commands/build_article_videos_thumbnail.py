from django_bulk_update.helper import bulk_update

from django.db.models import Q
from django.core.management.base import BaseCommand

from apps.articles.models import Article
from apps.utils.video import VideoHelper, UnknownProvider

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Fill Article.thumbnail field'

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        max_id = Article.objects.order_by('-id').first().id

        for start in range(0, max_id, BATCH_SIZE):
            end = min(start + BATCH_SIZE, max_id)

            self.stdout.write('Update articles thumbnail from {} to {}...'.format(start, end))

            articles = (Article.objects
                        .filter(~Q(video=''), id__range=(start, end))
                        .only('id', 'video')
                        .order_by())
            for article in articles:
                try:
                    article.thumbnail = VideoHelper(article.video).thumbnail
                except UnknownProvider:
                    pass

            bulk_update(articles, update_fields=['thumbnail'])

        self.stdout.write('End...')

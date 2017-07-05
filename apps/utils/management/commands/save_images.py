import os
import uuid
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Article, ARTICLE_UPLOAD_PATH

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Save multimedia'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/dir/')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('--- get articles...')
        articles = (Article.objects
                    .filter(multimedia__isnull=False)
                    .only('id', 'image', 'multimedia')
                    .select_related('multimedia')
                    .order_by('-id'))

        saved_files = set()

        j = 0
        for article in articles:
            stem, ext = os.path.splitext(article.multimedia.image_url)
            new_stem = str(uuid.uuid5(uuid.NAMESPACE_DNS, stem)) + ext
            new_stem = os.path.join(new_stem[:2], new_stem[2:4], new_stem)

            if new_stem in saved_files:
                article.image.name = os.path.join(ARTICLE_UPLOAD_PATH, new_stem)
                article.save(update_fields=['image'])
            else:
                abs_path = os.path.join(path, article.multimedia.image_url)
                try:
                    article.image.save(new_stem, File(open(abs_path, 'rb')))
                except FileNotFoundError:
                    continue
                else:
                    saved_files.add(new_stem)

            j += 1
            if j % BATCH_SIZE == 0:
                self.stdout.write('Save {} images...'.format(j))

        self.stdout.write('Save {} images...'.format(j))

        self.stdout.write('End...')

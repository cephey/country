import csv
from django.core.management.base import BaseCommand, CommandError

from apps.utils.converters import perl_to_python_dict
from apps.articles.models import Multimedia

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate multimedia from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            multimedia = []
            j = 0
            for row in reader:

                try:
                    data = perl_to_python_dict(row[6])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                try:
                    suffix = data['info']['suffix']
                    if suffix in ('jpg', 'gif', 'jpeg', 'png', 'bmp'):
                        multimedia.append(
                            Multimedia(
                                image_url=data['info']['path'] + '.' + suffix,
                                ext_id=int(row[0])
                            )
                        )
                except KeyError:
                    continue

                if len(multimedia) == BATCH_SIZE:
                    self.stdout.write('Bulk create multimedia (iter {})...'.format(j))
                    j += 1
                    Multimedia.objects.bulk_create(multimedia)
                    multimedia = []

        if multimedia:
            self.stdout.write('Bulk create parents comments (iter end)...')
            Multimedia.objects.bulk_create(multimedia)

        self.stdout.write('End...')

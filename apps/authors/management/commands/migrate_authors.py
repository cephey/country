import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Multimedia
from apps.authors.models import Author
from apps.utils.converters import perl_to_python_dict, perl_to_python_list

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate authors from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        multimedia_mapping = dict(Multimedia.objects.values_list('ext_id', 'id'))

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding=settings.MIGRATE_FILE_ENCODING) as csvfile:
            reader = csv.reader(csvfile)

            authors = []
            for row in reader:
                if row[1] != 'Forum::Author':
                    continue

                try:
                    last_name, first_name = row[7].split()
                except ValueError:
                    self.stderr.write('{} not author name'.format(row[7]))
                    continue

                try:
                    data = perl_to_python_dict(row[8])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                multimedia_ext_ids = perl_to_python_list(row[10])
                multimedia_id = None
                if multimedia_ext_ids:
                    for multimedia_ext_id in multimedia_ext_ids:
                        multimedia_id = multimedia_mapping.get(multimedia_ext_id)
                        if multimedia_id:
                            break

                authors.append(
                    Author(
                        first_name=first_name,
                        last_name=last_name,
                        description=data.get('about'),
                        is_active=bool(int(row[5])),
                        multimedia_id=multimedia_id,
                        ext_id=row[0]
                    )
                )
        Author.objects.bulk_create(authors, batch_size=BATCH_SIZE)
        self.stdout.write('End...')

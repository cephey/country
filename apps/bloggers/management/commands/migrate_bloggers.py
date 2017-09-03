import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.bloggers.models import Blogger
from apps.utils.converters import perl_to_python_dict


class Command(BaseCommand):
    help = 'Migrate bloggers from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding=settings.MIGRATE_FILE_ENCODING) as csvfile:
            reader = csv.reader(csvfile)

            bloggers = []
            for row in reader:
                first_name, last_name = row[7].split()

                try:
                    data = perl_to_python_dict(row[8])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                bloggers.append(
                    Blogger(
                        first_name=first_name, last_name=last_name, link=data.get('url'),
                        is_active=bool(int(row[5])), ext_id=row[0]
                    )
                )
        Blogger.objects.bulk_create(bloggers, batch_size=100)
        self.stdout.write('End...')

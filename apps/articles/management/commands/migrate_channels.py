import csv
from urllib.parse import urlparse, parse_qs

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Section
from apps.utils.converters import perl_to_python_dict


class Command(BaseCommand):
    help = 'Migrate partners channels from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding=settings.MIGRATE_FILE_ENCODING) as csvfile:
            reader = csv.reader(csvfile)

            sections = []
            for row in reader:
                try:
                    data = perl_to_python_dict(row[8])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                query_string = urlparse(data.get('rss')).query
                query_dict = parse_qs(query_string)
                channel = query_dict.get('user')
                if isinstance(channel, (list, tuple)):
                    channel = channel[0]

                sections.append(
                    Section(
                        name=row[7], slug=data.get('section_alias'), is_video=True,
                        channel=channel, is_active=bool(int(row[5])), ext_id=row[0]
                    )
                )
        Section.objects.bulk_create(sections, batch_size=100)
        self.stdout.write('End...')

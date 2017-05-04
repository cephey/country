import csv
import html2text
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand, CommandError

from apps.bloggers.models import Entry, Blogger


class Command(BaseCommand):
    help = 'Migrate bloggers entries from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')
        current_timezone = timezone.get_current_timezone()

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        bloggers_mapping = dict(Blogger.objects.values_list('ext_id', 'id'))

        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            entries = []
            for row in reader:
                ext_id = int(row[8])
                if ext_id not in bloggers_mapping:
                    self.stderr.write('Blogger with ext_id %s not found' % ext_id)
                    continue

                entries.append(
                    Entry(
                        title=row[7],
                        description=html2text.html2text(row[9]),
                        blogger_id=bloggers_mapping[ext_id],
                        link=row[10],
                        is_active=bool(int(row[5])),
                        publish_date=timezone.make_aware(parse_datetime(row[4]), current_timezone)
                    )
                )
        Entry.objects.bulk_create(entries, batch_size=100)
        self.stdout.write('End...')

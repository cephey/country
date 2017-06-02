import csv
from django.core.management.base import BaseCommand, CommandError

from apps.tags.models import Tag


class Command(BaseCommand):
    help = 'Migrate tags from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            tags = []
            for row in reader:

                tags.append(
                    Tag(
                        name=row[7], ext_id=row[0]
                    )
                )
        Tag.objects.bulk_create(tags, batch_size=100)
        self.stdout.write('End...')

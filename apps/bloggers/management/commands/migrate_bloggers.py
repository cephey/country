import re
import csv
import json
from django.core.management.base import BaseCommand, CommandError

from apps.bloggers.models import Blogger


class Command(BaseCommand):
    help = 'Migrate bloggers from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            bloggers = []
            for row in reader:
                first_name, last_name = row[7].split()

                data = row[8]
                try:
                    data = re.search('(\{.*?\})', data).group(1)
                    data = data.replace('\'', '\"').replace('=>', ':')
                    data = json.loads(data)
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

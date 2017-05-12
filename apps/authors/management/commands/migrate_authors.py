import csv
from django.core.management.base import BaseCommand, CommandError

from apps.authors.models import Author
from apps.utils.converters import perl_to_python_dict


class Command(BaseCommand):
    help = 'Migrate authors from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding='koi8-r') as csvfile:
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

                authors.append(
                    Author(
                        first_name=first_name, last_name=last_name,
                        description=data.get('about'),
                        is_active=bool(int(row[5])), ext_id=row[0]
                    )
                )
        Author.objects.bulk_create(authors, batch_size=100)
        self.stdout.write('End...')

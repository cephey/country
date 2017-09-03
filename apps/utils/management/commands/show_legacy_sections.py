import csv
from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


def goo(parent_id, sections, elem_id, name):
    if parent_id in sections:
        sections[parent_id][1][elem_id] = (name, {})
    else:
        for k, _ in sections.items():
            goo(parent_id, sections[k][1], elem_id, name)


class Command(BaseCommand):
    help = 'Show legacy sections from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        with open(path, 'r', encoding=settings.MIGRATE_FILE_ENCODING) as csvfile:
            reader = csv.reader(csvfile)

            sections = {}
            for row in reader:

                elem_id, parent_id = row[0], row[1]
                if parent_id:
                    goo(parent_id, sections, elem_id, row[7])
                else:
                    sections[elem_id] = (row[7], {})

        pprint(sections)
        self.stdout.write('End...')

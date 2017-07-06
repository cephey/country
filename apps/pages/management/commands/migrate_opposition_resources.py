import csv
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Multimedia
from apps.pages.models import Resource, Partition
from apps.utils.converters import perl_to_python_dict, perl_to_python_list

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate opposition resources from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        partition_mapping = dict(Partition.objects.values_list('ext_id', 'id'))
        multimedia_mapping = dict(Multimedia.objects.values_list('ext_id', 'id'))

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            resources = []
            for row in reader:

                try:
                    data = perl_to_python_dict(row[9])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                section_ext_ids = set(perl_to_python_list(row[10])) - {124}
                if not section_ext_ids:
                    continue

                partition_ids = []
                for section_ext_id in section_ext_ids:
                    partition_id = partition_mapping.get(section_ext_id)
                    if partition_id:
                        partition_ids.append(partition_id)
                if not partition_ids:
                    continue

                multimedia_ext_ids = perl_to_python_list(row[11])
                multimedia_id = None
                if multimedia_ext_ids:
                    for multimedia_ext_id in multimedia_ext_ids:
                        multimedia_id = multimedia_mapping.get(multimedia_ext_id)
                        if multimedia_id:
                            break

                resources.append(
                    Resource(
                        partition_id=partition_ids[0],
                        name=row[7],
                        url=data['url'],
                        rating=int(row[8]),
                        multimedia_id=multimedia_id,
                        is_active=bool(int(row[5]))
                    )
                )

        if resources:
            self.stdout.write('Bulk create resources...')
            Resource.objects.bulk_create(resources, batch_size=BATCH_SIZE)

        self.stdout.write('End...')

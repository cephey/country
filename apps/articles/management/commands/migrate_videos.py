import csv
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Section, Article


class Command(BaseCommand):
    help = 'Migrate partners video from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')
        current_timezone = timezone.get_current_timezone()

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        sections_mapping = dict(Section.objects
                                .filter(~Q(channel=''), is_video=True)
                                .values_list('ext_id', 'id'))

        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            for row in reader:
                ext_id = int(row[8])
                if ext_id not in sections_mapping:
                    self.stderr.write('Section with ext_id %s not found' % ext_id)
                    continue

                # not using bulk_create, because generate thumbnail link in save method
                Article.objects.create(
                    title=row[7],
                    section_id=sections_mapping[ext_id],
                    publish_date=timezone.make_aware(parse_datetime(row[4]), current_timezone),
                    video=row[10],
                    status=Article.STATUS.approved
                )

        self.stdout.write('End...')

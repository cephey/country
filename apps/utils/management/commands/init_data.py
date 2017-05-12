import os
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

from apps.articles.tasks import download_latest_partners_videos
from apps.bloggers.tasks import update_bloggers_photos, download_latest_entries


class Command(BaseCommand):
    help = 'Initial data'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/dir/')

    def handle(self, *args, **kwargs):
        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('Migrate authors...')
        call_command(
            'migrate_authors',
            path=os.path.join(path, 'documents.csv')
        )

        self.stdout.write('Migrate partner video channels (partner video sections)...')
        call_command(
            'migrate_channels',
            path=os.path.join(path, 'import_video_importer.csv')
        )

        self.stdout.write('Migrate partner videos (video articles)...')
        call_command(
            'migrate_partners_videos',
            path=os.path.join(path, 'import_video_news.csv')
        )
        download_latest_partners_videos()

        self.stdout.write('Migrate bloggers...')
        call_command(
            'migrate_bloggers',
            path=os.path.join(path, 'forum_bloggers.csv')
        )
        update_bloggers_photos()

        self.stdout.write('Migrate bloggers entries...')
        call_command(
            'migrate_entries',
            path=os.path.join(path, 'forum_bloggers_news.csv')
        )
        download_latest_entries()

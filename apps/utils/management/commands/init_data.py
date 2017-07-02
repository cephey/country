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

        self.stdout.write('Create sections...')
        call_command(
            'create_sections'
        )

        self.stdout.write('Migrate tags...')
        call_command(
            'migrate_tags',
            path=os.path.join(path, 'tags.csv')
        )

        self.stdout.write('Migrate articles...')
        call_command(
            'migrate_articles',
            path=os.path.join(path, 'news.csv')
        )

        self.stdout.write('Migrate comments...')
        call_command(
            'migrate_comments',
            path=os.path.join(path, 'forum_messages.csv')
        )

        self.stdout.write('Denorm article comments count...')
        call_command(
            'denorm_article_comments_count'
        )

        self.stdout.write('Build article videos thumbnail...')
        call_command(
            'build_article_videos_thumbnail'
        )

        # opposition -------------------------------------------------------
        self.stdout.write('Create opposition partitions...')
        call_command(
            'create_opposition_partitions'
        )

        self.stdout.write('Migrate opposition resources...')
        call_command(
            'migrate_opposition_resources',
            path=os.path.join(path, 'partner_opposition.csv')
        )
        # ---------------------------------------------------------------------

        # partner video -------------------------------------------------------
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
        # ---------------------------------------------------------------------

        # bloggers ------------------------------------------------------------
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
        # ---------------------------------------------------------------------

        self.stdout.write('Migrate polls...')
        call_command(
            'migrate_polls',
            path=os.path.join(path, 'votes.csv')
        )

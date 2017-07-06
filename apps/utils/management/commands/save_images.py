import os
import uuid
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from apps.authors.models import Author, AUTHOR_UPLOAD_PATH
from apps.articles.models import Article, ARTICLE_UPLOAD_PATH
from apps.pages.models import Resource, RESOURCE_UPLOAD_PATH

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Save multimedia'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/dir/')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        # ---------------------------------------------------------------------
        self.stdout.write('--- get articles...')
        articles = (Article.objects
                    .filter(multimedia__isnull=False)
                    .only('id', 'image', 'multimedia')
                    .select_related('multimedia')
                    .order_by('-id'))

        articles_saved_files = set()

        j = 0
        for article in articles:
            stem, ext = os.path.splitext(article.multimedia.image_url)
            new_stem = str(uuid.uuid5(uuid.NAMESPACE_DNS, stem)) + ext
            new_stem = os.path.join(new_stem[:2], new_stem[2:4], new_stem)

            if new_stem in articles_saved_files:
                article.image.name = os.path.join(ARTICLE_UPLOAD_PATH, new_stem)
                article.save(update_fields=['image'])
            else:
                abs_path = os.path.join(path, article.multimedia.image_url)
                try:
                    article.image.save(new_stem, File(open(abs_path, 'rb')))
                except FileNotFoundError:
                    continue
                else:
                    articles_saved_files.add(new_stem)

            j += 1
            if j % BATCH_SIZE == 0:
                self.stdout.write('Save {} articles images...'.format(j))

        self.stdout.write('Save {} articles images...'.format(j))

        # ---------------------------------------------------------------------
        self.stdout.write('--- get authors...')
        authors = (Author.objects
                   .filter(multimedia__isnull=False)
                   .only('id', 'photo', 'multimedia')
                   .select_related('multimedia')
                   .order_by('-id'))

        authors_saved_files = set()

        j = 0
        for author in authors:
            stem, ext = os.path.splitext(author.multimedia.image_url)
            new_stem = str(uuid.uuid5(uuid.NAMESPACE_DNS, stem)) + ext
            new_stem = os.path.join(new_stem[:2], new_stem[2:4], new_stem)

            if new_stem in authors_saved_files:
                author.photo.name = os.path.join(AUTHOR_UPLOAD_PATH, new_stem)
                author.save(update_fields=['photo'])
            else:
                abs_path = os.path.join(path, author.multimedia.image_url)
                try:
                    author.photo.save(new_stem, File(open(abs_path, 'rb')))
                except FileNotFoundError:
                    continue
                else:
                    authors_saved_files.add(new_stem)

            j += 1
            if j % BATCH_SIZE == 0:
                self.stdout.write('Save {} authors images...'.format(j))

        self.stdout.write('Save {} authors images...'.format(j))

        # ---------------------------------------------------------------------
        self.stdout.write('--- get opposition resources...')
        resources = (Resource.objects
                     .filter(multimedia__isnull=False)
                     .only('id', 'logo', 'multimedia')
                     .select_related('multimedia')
                     .order_by('-id'))

        resources_saved_files = set()

        j = 0
        for resource in resources:
            stem, ext = os.path.splitext(resource.multimedia.image_url)
            new_stem = str(uuid.uuid5(uuid.NAMESPACE_DNS, stem)) + ext
            new_stem = os.path.join(new_stem[:2], new_stem[2:4], new_stem)

            if new_stem in resources_saved_files:
                resource.logo.name = os.path.join(RESOURCE_UPLOAD_PATH, new_stem)
                resource.save(update_fields=['logo'])
            else:
                abs_path = os.path.join(path, resource.multimedia.image_url)
                try:
                    resource.logo.save(new_stem, File(open(abs_path, 'rb')))
                except FileNotFoundError:
                    continue
                else:
                    resources_saved_files.add(new_stem)

            j += 1
            if j % BATCH_SIZE == 0:
                self.stdout.write('Save {} opposition resources images...'.format(j))

        self.stdout.write('Save {} opposition resources images...'.format(j))

        # ---------------------------------------------------------------------

        self.stdout.write('End...')

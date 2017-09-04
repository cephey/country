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

    def save_images(self, instances, upload_path, import_path, attr_name):
        saved_files = set()
        model_name = '{}s'.format(instances.model.__name__.lower())

        j = 0
        for instance in instances:
            stem, ext = os.path.splitext(instance.multimedia.image_url)
            new_stem = str(uuid.uuid5(uuid.NAMESPACE_DNS, stem)) + ext
            new_stem = os.path.join(new_stem[:2], new_stem[2:4], new_stem)

            if new_stem in saved_files:
                getattr(instance, attr_name).name = os.path.join(upload_path, new_stem)
                instance.save(update_fields=[attr_name])
            else:
                abs_path = os.path.join(import_path, instance.multimedia.image_url)
                try:
                    getattr(instance, attr_name).save(new_stem, File(open(abs_path, 'rb')))
                except FileNotFoundError:
                    continue
                else:
                    saved_files.add(new_stem)

            j += 1
            if j % BATCH_SIZE == 0:
                self.stdout.write('Save {} {} images...'.format(j, model_name))

        self.stdout.write('Save {} {} images...'.format(j, model_name))

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

        self.save_images(articles, ARTICLE_UPLOAD_PATH, path, 'image')

        # ---------------------------------------------------------------------
        self.stdout.write('--- get authors...')
        authors = (Author.objects
                   .filter(multimedia__isnull=False)
                   .only('id', 'photo', 'multimedia')
                   .select_related('multimedia')
                   .order_by('-id'))

        self.save_images(authors, AUTHOR_UPLOAD_PATH, path, 'photo')

        # ---------------------------------------------------------------------
        self.stdout.write('--- get opposition resources...')
        resources = (Resource.objects
                     .filter(multimedia__isnull=False)
                     .only('id', 'logo', 'multimedia')
                     .select_related('multimedia')
                     .order_by('-id'))

        self.save_images(resources, RESOURCE_UPLOAD_PATH, path, 'logo')

        # ---------------------------------------------------------------------

        self.stdout.write('End...')

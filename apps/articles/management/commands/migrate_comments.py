import csv
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Article, Comment

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate articles comments from csv'
    articles_mapping = None

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('- create articles_mapping...')
        self.articles_mapping = dict(Article.objects.filter(thread_id__gt=0).values_list('thread_id', 'id'))

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            tree_dict = defaultdict(list)

            comments = []
            i, j = 0, 0
            for row in reader:

                thread_id = int(row[5])
                if thread_id not in self.articles_mapping:
                    continue

                parent_id = row[14]
                if parent_id and parent_id != '0':
                    tree_dict[int(parent_id)].append(row)
                    continue

                comments.append(
                    Comment(
                        token=row[7] or '',
                        article_id=self.articles_mapping[thread_id],
                        username=row[10],
                        title=row[4] or '',
                        content=row[8],
                        is_active=bool(int(row[3])),
                        ext_id=row[0]
                    )
                )
                j += 1
                if j == BATCH_SIZE:
                    i += 1
                    self.stdout.write('Bulk create parents comments (iter {})...'.format(i))
                    Comment.objects.bulk_create(comments)
                    comments = []
                    j = 0

        if comments:
            self.stdout.write('Bulk create parents comments (iter end)...')
            Comment.objects.bulk_create(comments)

        self.stdout.write('First level parent count: {}'.format(len(tree_dict)))

        # ---------------------------------------------------------------------

        max_id = None
        for i in range(8):  # max depth 8
            tree_dict, max_id = self.create_deep_comments(tree_dict, max_id=max_id)

        # ---------------------------------------------------------------------

        self.stdout.write('End...')

    def create_deep_comments(self, prev_tree_dict, max_id=None):
        qs = Comment.objects.values_list('ext_id', 'id')
        if max_id:
            qs = qs.filter(id__gt=max_id)

        self.stdout.write('- create comments_mapping...')
        comments_mapping = dict(qs.all())
        new_max_id = Comment.objects.order_by('-id').first().id

        tree_dict = defaultdict(list)
        comments = []
        i, j = 0, 0

        self.stdout.write('Parse next level comments...')
        for parent_id, comment_list in prev_tree_dict.items():

            if parent_id not in comments_mapping:
                tree_dict[parent_id].extend(comment_list)
                continue

            for row in comment_list:

                comments.append(
                    Comment(
                        token=row[7] or '',
                        article_id=self.articles_mapping[int(row[5])],
                        parent_id=comments_mapping[parent_id],
                        username=row[10],
                        title=row[4] or '',
                        content=row[8],
                        is_active=bool(int(row[3])),
                        ext_id=row[0]
                    )
                )
                j += 1
                if j == BATCH_SIZE:
                    i += 1
                    self.stdout.write('Bulk create next level comments (iter {})...'.format(i))
                    Comment.objects.bulk_create(comments)
                    comments = []
                    j = 0

        if comments:
            self.stdout.write('Bulk create next level comments (iter end)...')
            Comment.objects.bulk_create(comments)

        self.stdout.write('Next level parent count: {}'.format(len(tree_dict)))
        return tree_dict, new_max_id

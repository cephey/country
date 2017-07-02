import csv
from collections import defaultdict
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Article, Comment
from apps.votes.models import Vote

BATCH_SIZE = 500


class Command(BaseCommand):
    help = 'Migrate articles comments from csv'
    articles_mapping = None
    comment_votes_relation = None

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')

        comment_ct = ContentType.objects.get_for_model(Comment)

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        self.stdout.write('- create articles_mapping...')
        self.articles_mapping = dict(Article.objects.filter(thread_id__gt=0).values_list('thread_id', 'id'))
        self.comment_votes_relation = {}

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            tree_dict = defaultdict(list)

            comments = []
            j = 0
            for row in reader:

                thread_id = int(row[5])
                if thread_id not in self.articles_mapping:
                    continue

                comment_ext_id = int(row[0])

                # store votes for later use
                karma = 0
                try:
                    karma = int(row[11])
                except (ValueError, TypeError):
                    pass
                else:
                    if karma:
                        self.comment_votes_relation[comment_ext_id] = karma

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
                        karma=karma,
                        ext_id=comment_ext_id
                    )
                )
                if len(comments) == BATCH_SIZE:
                    self.stdout.write('Bulk create parents comments (iter {})...'.format(j))
                    j += 1
                    Comment.objects.bulk_create(comments)
                    comments = []

        if comments:
            self.stdout.write('Bulk create parents comments (iter end)...')
            Comment.objects.bulk_create(comments)

        self.stdout.write('First level parent count: {}'.format(len(tree_dict)))

        # ---------------------------------------------------------------------

        max_id = None
        for i in range(8):  # max depth 8
            tree_dict, max_id = self.create_deep_comments(tree_dict, max_id=max_id)

        # ---------------------------------------------------------------------

        self.stdout.write('- create comments_mapping for votes...')
        comments_mapping = dict(Comment.objects.values_list('ext_id', 'id'))

        # attach votes --------------------------------------------------------
        self.stdout.write('Start build relations comments <-> votes...')
        votes = []
        j = 0
        for comment_ext_id, karma in self.comment_votes_relation.items():
            if comment_ext_id in comments_mapping:
                comment_id = comments_mapping[comment_ext_id]
                score = 1 if karma > 0 else -1

                if len(votes) + abs(karma) > BATCH_SIZE:
                    for i in range(abs(karma)):
                        votes.append(
                            Vote(object_id=comment_id, content_type_id=comment_ct.id, score=score)
                        )
                        if len(votes) == BATCH_SIZE:
                            self.stdout.write('Bulk create relations comments <-> votes (iter {})...'.format(j))
                            j += 1
                            Vote.objects.bulk_create(votes)
                            votes = []
                else:
                    votes.extend(
                        [Vote(object_id=comment_id, content_type_id=comment_ct.id, score=score)
                         for i in range(abs(karma))]
                    )
                    if len(votes) == BATCH_SIZE:
                        self.stdout.write('Bulk create relations comments <-> votes (iter {})...'.format(j))
                        j += 1
                        Vote.objects.bulk_create(votes)
                        votes = []
        if votes:
            self.stdout.write('Bulk create relations comments <-> votes (iter end)...')
            Vote.objects.bulk_create(votes)

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
        j = 0

        self.stdout.write('Parse next level comments...')
        for parent_id, comment_list in prev_tree_dict.items():

            if parent_id not in comments_mapping:
                tree_dict[parent_id].extend(comment_list)
                continue

            for row in comment_list:

                karma = 0
                try:
                    karma = int(row[11])
                except (ValueError, TypeError):
                    pass

                comments.append(
                    Comment(
                        token=row[7] or '',
                        article_id=self.articles_mapping[int(row[5])],
                        parent_id=comments_mapping[parent_id],
                        username=row[10],
                        title=row[4] or '',
                        content=row[8],
                        is_active=bool(int(row[3])),
                        karma=karma,
                        ext_id=row[0]
                    )
                )
                if len(comments) == BATCH_SIZE:
                    self.stdout.write('Bulk create next level comments (iter {})...'.format(j))
                    j += 1
                    Comment.objects.bulk_create(comments)
                    comments = []

        if comments:
            self.stdout.write('Bulk create next level comments (iter end)...')
            Comment.objects.bulk_create(comments)

        self.stdout.write('Next level parent count: {}'.format(len(tree_dict)))
        return tree_dict, new_max_id

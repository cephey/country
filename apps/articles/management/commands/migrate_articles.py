import csv
import math
from collections import defaultdict

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Section, Article, Notice, Multimedia
from apps.authors.models import Author
from apps.tags.models import Tag, TaggedItem
from apps.utils.converters import perl_to_python_dict, perl_to_python_list
from apps.votes.models import Vote

BATCH_SIZE = 500


def vote_values(count, summa):
    if not count:
        return []

    k = float(summa) / count
    a = int(k)
    b = math.ceil(k)
    if a == b:
        return [(a, count)]

    y = int((a * count - summa) / (a - b))
    x = count - y
    return [(x, a), (y, b)]


class Command(BaseCommand):
    help = 'Migrate articles from csv'

    def add_arguments(self, parser):
        parser.add_argument('--path', help='/path/to/file.csv')

    def handle(self, *args, **kwargs):
        self.stdout.write('Start...')
        current_timezone = timezone.get_current_timezone()

        article_ct = ContentType.objects.get_for_model(Article)

        path = kwargs.get('path')
        if not path:
            raise CommandError('Path is required')

        authors_mapping = dict(Author.objects.values_list('ext_id', 'id'))
        sections_mapping = dict(Section.objects.values_list('ext_id', 'id'))
        tags_mapping = dict(Tag.objects.values_list('ext_id', 'id'))
        multimedia_mapping = dict(Multimedia.objects.values_list('ext_id', 'id'))

        video_sections = list(Section.objects.filter(is_video=True).values_list('id', flat=True))

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            notices = []

            articles = []
            article_authors_relation = {}
            article_tags_relation = defaultdict(list)
            article_votes_relation = {}
            j = 0
            for row in reader:

                multimedia_ext_ids = perl_to_python_list(row[17])
                multimedia_id = None
                if multimedia_ext_ids:
                    for multimedia_ext_id in multimedia_ext_ids:
                        multimedia_id = multimedia_mapping.get(multimedia_ext_id)
                        if multimedia_id:
                            break

                try:
                    data = perl_to_python_dict(row[12])
                except Exception as e:
                    self.stderr.write(e)
                    continue

                # flags
                is_news = False
                is_day_material = False
                is_main_news = False
                is_ticker = False

                section_ext_ids = sorted(perl_to_python_list(row[13]))

                if 127 in section_ext_ids:
                    if row[7]:
                        notices.append(
                            Notice(
                                content=row[7],
                                status=Notice.STATUS.approved if int(row[5]) else Notice.STATUS.rejected
                            )
                        )
                    continue

                is_video = bool(row[15])

                section_id = None
                for ext_id in section_ext_ids:
                    if ext_id in sections_mapping:
                        section_id = sections_mapping[ext_id]
                        if section_id in video_sections and not is_video:
                            section_id = None
                            continue
                        break

                if 108 in section_ext_ids:
                    is_news = True
                if (113 in section_ext_ids) or (8221431 in section_ext_ids):
                    is_day_material = True
                if (114 in section_ext_ids) or (8221430 in section_ext_ids):
                    is_main_news = True
                if 123 in section_ext_ids:
                    is_ticker = True

                article_ext_id = int(row[0])

                # store authors for later use
                raw_author = row[8]
                if raw_author:
                    try:
                        ext_id = int(raw_author)
                    except (ValueError, TypeError):
                        pass
                    else:
                        if ext_id in authors_mapping:
                            article_authors_relation[article_ext_id] = authors_mapping[ext_id]

                # store tags for later use
                for ext_id in perl_to_python_list(row[18]):
                    if ext_id in tags_mapping:
                        article_tags_relation[article_ext_id].append(tags_mapping[ext_id])

                # store votes for later use
                rating = 0
                vote_count = 0
                try:
                    vote_count = int(row[10])
                    vote_sum = int(row[11])
                except (ValueError, TypeError):
                    pass
                else:
                    article_votes_relation[article_ext_id] = vote_values(vote_count, vote_sum)
                    if vote_count:
                        rating = float(vote_sum) / vote_count

                articles.append(
                    Article(
                        title=row[7],
                        description=data.get('note') or '',
                        content=data.get('body') or '',
                        section_id=section_id,
                        author_names=data.get('author') or '',
                        publish_date=timezone.make_aware(parse_datetime(row[4]), current_timezone, is_dst=True),
                        is_active=bool(int(row[5])),
                        source=data.get('source') or '',
                        source_link=data.get('sourcelink') or '',
                        discussion_status=data.get('can_comment') or Article.DISCUSSION_STATUS.open,
                        status=Article.STATUS.approved,
                        video=row[15] or '',
                        is_news=is_news,
                        is_ticker=is_ticker,
                        is_main_news=is_main_news,
                        is_day_material=is_day_material,
                        rating=rating,
                        vote_count=vote_count,
                        multimedia_id=multimedia_id,
                        thread_id=row[16] or 0,
                        ext_id=article_ext_id
                    )
                )
                if len(articles) == BATCH_SIZE:
                    self.stdout.write('Bulk create articles (iter {})...'.format(j))
                    j += 1
                    Article.objects.bulk_create(articles)
                    articles = []

        if articles:
            self.stdout.write('Bulk create articles (iter end)...')
            Article.objects.bulk_create(articles)

        self.stdout.write('Bulk create notices...')
        Notice.objects.bulk_create(notices, batch_size=BATCH_SIZE)

        self.stdout.write('- create articles_mapping...')
        articles_mapping = dict(Article.objects.values_list('ext_id', 'id'))

        # attach authors ------------------------------------------------------
        self.stdout.write('Start build relations atricles <-> authors...')
        article_authors = []
        j = 0
        for article_ext_id, author_id in article_authors_relation.items():
            if article_ext_id in articles_mapping:
                article_id = articles_mapping[article_ext_id]
                article_authors.append(
                    Article.authors.through(article_id=article_id, author_id=author_id)
                )
                if len(article_authors) == BATCH_SIZE:
                    self.stdout.write('Bulk create relations atricles <-> authors (iter {})...'.format(j))
                    j += 1
                    Article.authors.through.objects.bulk_create(article_authors)
                    article_authors = []
        if article_authors:
            self.stdout.write('Bulk create relations atricles <-> authors (iter end)...')
            Article.authors.through.objects.bulk_create(article_authors)

        # attach tags ---------------------------------------------------------
        self.stdout.write('Start build relations atricles <-> tags...')
        tagged_items = []
        j = 0
        for article_ext_id, tag_ids in article_tags_relation.items():
            if article_ext_id in articles_mapping:
                article_id = articles_mapping[article_ext_id]

                if len(tagged_items) + len(tag_ids) > BATCH_SIZE:
                    for tag_id in tag_ids:
                        tagged_items.append(
                            TaggedItem(object_id=article_id, content_type_id=article_ct.id, tag_id=tag_id)
                        )
                        if len(tagged_items) == BATCH_SIZE:
                            self.stdout.write('Bulk create relations atricles <-> tags (iter {})...'.format(j))
                            j += 1
                            TaggedItem.objects.bulk_create(tagged_items)
                            tagged_items = []
                else:
                    tagged_items.extend(
                        [TaggedItem(object_id=article_id, content_type_id=article_ct.id, tag_id=tag_id)
                         for tag_id in tag_ids]
                    )
                    if len(tagged_items) == BATCH_SIZE:
                        self.stdout.write('Bulk create relations atricles <-> tags (iter {})...'.format(j))
                        j += 1
                        TaggedItem.objects.bulk_create(tagged_items)
                        tagged_items = []
        if tagged_items:
            self.stdout.write('Bulk create relations atricles <-> tags (iter end)...')
            TaggedItem.objects.bulk_create(tagged_items)

        # attach votes --------------------------------------------------------
        self.stdout.write('Start build relations atricles <-> votes...')
        votes = []
        j = 0
        for article_ext_id, vote_data in article_votes_relation.items():
            if article_ext_id in articles_mapping:
                article_id = articles_mapping[article_ext_id]
                for count, score in vote_data:

                    if len(votes) + count > BATCH_SIZE:
                        for i in range(count):
                            votes.append(
                                Vote(object_id=article_id, content_type_id=article_ct.id, score=score)
                            )
                            if len(votes) == BATCH_SIZE:
                                self.stdout.write('Bulk create relations atricles <-> votes (iter {})...'.format(j))
                                j += 1
                                Vote.objects.bulk_create(votes)
                                votes = []
                    else:
                        votes.extend(
                            [Vote(object_id=article_id, content_type_id=article_ct.id, score=score)
                             for i in range(count)]
                        )
                        if len(votes) == BATCH_SIZE:
                            self.stdout.write('Bulk create relations atricles <-> votes (iter {})...'.format(j))
                            j += 1
                            Vote.objects.bulk_create(votes)
                            votes = []
        if votes:
            self.stdout.write('Bulk create relations atricles <-> votes (iter end)...')
            Vote.objects.bulk_create(votes)

        self.stdout.write('End...')

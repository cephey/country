import csv
from collections import defaultdict

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from apps.articles.models import Section, Article, Notice
from apps.authors.models import Author
from apps.tags.models import Tag, TaggedItem
from apps.utils.converters import perl_to_python_dict, perl_to_python_list


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

        self.stdout.write('Parse file...')
        csv.field_size_limit(500 * 1024 * 1024)
        with open(path, 'r', encoding='koi8-r') as csvfile:
            reader = csv.reader(csvfile)

            notices = []

            articles = []
            article_authors_relation = {}
            article_tags_relation = defaultdict(list)

            for row in reader:

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

                section_id = None
                for ext_id in section_ext_ids:
                    if ext_id in sections_mapping:
                        section_id = sections_mapping[ext_id]
                        break

                if 108 in section_ext_ids:
                    is_news = True
                if (113 in section_ext_ids) or (8221431 in section_ext_ids):
                    is_day_material = True
                if (114 in section_ext_ids) or (8221430 in section_ext_ids):
                    is_main_news = True
                if 123 in section_ext_ids:
                    is_ticker = True

                # store authors for later use
                raw_author = row[8]
                if raw_author:
                    try:
                        ext_id = int(raw_author)
                    except (ValueError, TypeError):
                        pass
                    else:
                        if ext_id in authors_mapping:
                            article_authors_relation[int(row[0])] = authors_mapping[ext_id]

                # store tags for later use
                for ext_id in perl_to_python_list(row[18]):
                    if ext_id in tags_mapping:
                        article_tags_relation[int(row[0])].append(tags_mapping[ext_id])

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
                        ext_id=row[0]
                    )
                )

        self.stdout.write('Bulk create notices...')
        Notice.objects.bulk_create(notices, batch_size=500)

        self.stdout.write('Bulk create articles...')
        Article.objects.bulk_create(articles, batch_size=500)

        articles_mapping = dict(Article.objects.values_list('ext_id', 'id'))

        # attach authors
        relations = {}
        for article_ext_id, author_id in article_authors_relation.items():
            if article_ext_id in articles_mapping:
                relations[articles_mapping[article_ext_id]] = author_id

        ArticleAuthor = Article.authors.through
        article_authors = [
            ArticleAuthor(article_id=article_id, author_id=author_id)
            for article_id, author_id in relations.items()
        ]
        self.stdout.write('Bulk create relations atricles <-> authors...')
        ArticleAuthor.objects.bulk_create(article_authors, batch_size=500)

        # attach tags
        tagged_item = []
        for article_ext_id, tag_ids in article_tags_relation.items():
            if article_ext_id in articles_mapping:
                article_id = articles_mapping[article_ext_id]
                tagged_item.extend(
                    [TaggedItem(object_id=article_id, content_type_id=article_ct.id, tag_id=tag_id)
                     for tag_id in tag_ids]
                )
        self.stdout.write('Bulk create relations atricles <-> tags...')
        TaggedItem.objects.bulk_create(tagged_item, batch_size=500)

        self.stdout.write('End...')

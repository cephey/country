import uuid
import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType

from apps.authors.models import Author
from apps.authors.factories import AuthorFactory
from apps.articles.models import Section, Article, Notice, Comment, Multimedia
from apps.articles.factories import (SectionFactory, ArticleFactory, NoticeFactory,
                                     CommentFactory, MultimediaFactory, VideoSectionFactory)
from apps.bloggers.models import Blogger, Entry
from apps.bloggers.factories import BloggerFactory, EntryFactory
from apps.polls.models import Poll, Choice
from apps.polls.factories import PollFactory, ChoiceFactory
from apps.tags.models import Tag
from apps.tags.factories import TagFactory
from apps.votes.models import Vote
from apps.votes.factories import VoteFactory
from apps.users.factories import UserFactory
from apps.pages.models import Resource, Partition
from apps.pages.factories import ResourceFactory, PartitionFactory

LOW = {
    'label': 'low',
    'token_count': 100,
    'user_count': 50,
    'author_count': 20,
    'tag_count': 20,
    'avg_art_count': 7,
    'max_com_count': 5,
    'max_art_vote_count': 5,
    'max_like_count': 5,
    'notice_count': 10,
    'poll_count': 5,
    'blogger_count': 5,
    'min_entry_count': 3,
    'max_entry_count': 10,
    'max_choice_vote_count': 5,
}
MIDDLE = {
    'label': 'middle',
    'token_count': 200,
    'user_count': 70,
    'author_count': 30,
    'tag_count': 40,
    'avg_art_count': 15,
    'max_com_count': 10,
    'max_art_vote_count': 10,
    'max_like_count': 10,
    'notice_count': 20,
    'poll_count': 10,
    'blogger_count': 10,
    'min_entry_count': 10,
    'max_entry_count': 20,
    'max_choice_vote_count': 10,
}
HEIGHT = {
    'label': 'height',
    'token_count': 300,
    'user_count': 100,
    'author_count': 40,
    'tag_count': 60,
    'avg_art_count': 30,
    'max_com_count': 20,
    'max_art_vote_count': 20,
    'max_like_count': 20,
    'notice_count': 50,
    'poll_count': 15,
    'blogger_count': 20,
    'min_entry_count': 20,
    'max_entry_count': 50,
    'max_choice_vote_count': 20,
}


class Command(BaseCommand):
    help = 'Initial data for testing'

    def add_arguments(self, parser):
        parser.add_argument('--middle', action='store_true')
        parser.add_argument('--height', action='store_true')
        parser.add_argument('--dev', action='store_true')

    def handle(self, *args, **kwargs):
        STR = LOW
        if kwargs.get('middle'):
            STR = MIDDLE
        elif kwargs.get('height'):
            STR = HEIGHT
        self.stdout.write('A <{}> strategy is chosen'.format(STR['label']))

        article_ct = ContentType.objects.get_for_model(Article)
        comment_ct = ContentType.objects.get_for_model(Comment)
        choice_ct = ContentType.objects.get_for_model(Choice)

        self.stdout.write('Remove all data from DB')
        Notice.objects.all().delete()
        Comment.objects.all().delete()
        Multimedia.objects.all().delete()
        Article.objects.all().delete()
        Section.objects.all().delete()

        Author.objects.all().delete()
        if kwargs.get('dev'):
            Blogger.objects.all().delete()
            Entry.objects.all().delete()

        Choice.objects.all().delete()
        Poll.objects.all().delete()

        Tag.objects.all().delete()
        Vote.objects.all().delete()

        Resource.objects.all().delete()
        Partition.objects.all().delete()

        get_user_model().objects.exclude(is_staff=True).delete()

        # ---------------------

        tokens = [str(uuid.uuid4()).replace('-', '') for i in range(STR['token_count'])]
        self.stdout.write('Generate users...')
        users = UserFactory.create_batch(STR['user_count'])

        self.stdout.write('Generate authors...')
        authors = AuthorFactory.create_batch(STR['author_count'])

        self.stdout.write('Generate tags...')
        tags = TagFactory.create_batch(STR['tag_count'])

        self.stdout.write('Generate sections...')
        sections = [
            SectionFactory(name='Политический расклад', slug='politic'),
            SectionFactory(name='Экономическая реальность', slug='economic'),
            SectionFactory(name='Жизнь регионов', slug='region'),
            SectionFactory(name='Общество и его культура', slug='society'),
            SectionFactory(name='Силовые структуры', slug='power'),
            SectionFactory(name='Особенности внешней политики', slug='fpolitic'),
            SectionFactory(name='Компрометирующие материалы', slug='kompromat'),
            SectionFactory(name='Московский листок', slug='moscow'),

            # video
            VideoSectionFactory(name='Новости политики', slug='video_politic'),
            VideoSectionFactory(name='Экономический расклад', slug='video_economic'),
            VideoSectionFactory(name='Проиcшествия', slug='video_accidents'),
            VideoSectionFactory(name='Внешняя политика', slug='video_fpolitic'),
            VideoSectionFactory(name='Общество и его культура', slug='video_society'),
            VideoSectionFactory(name='Народное видео', slug='video_national'),

            # partner video
            VideoSectionFactory(name='Луганск 24', slug='video_partner_lugansk24'),
            VideoSectionFactory(name='Программа Сергея Доренко', slug='video_partner_dorenko'),
            VideoSectionFactory(name='Красное.ТВ', slug='video_partner_krasnoetv'),
            VideoSectionFactory(name='Nevex.TV', slug='video_partner_nevextv')
        ]
        a_count_list = [2, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]

        self.stdout.write('Generate articles with comments and media...')
        for i in range(len(sections) * STR['avg_art_count'] * 2):
            section = random.choice(sections)
            if section.is_video and not random.randint(0, 1):
                continue

            # authors
            params = dict(
                section=section,
                is_news=not bool(random.randint(0, 6))
            )
            a_count = random.choice(a_count_list)
            if not a_count:  # no authors
                if random.randint(0, 1):
                    params['author_names'] = AuthorFactory.build().cover_name
            else:
                params['authors'] = random.sample(authors, a_count)

            # tags
            a_tags = random.sample(tags, random.randint(0, 6))
            if a_tags:
                params['tags'] = a_tags

            # source
            if not random.randint(0, 5):
                params['with_source'] = True
                if random.randint(0, 1):
                    params['with_source_link'] = True

            if not random.randint(0, 20):
                params['show_comments'] = False  # hide comments
            if not random.randint(0, 3):
                params['discussion_status'] = Article.DISCUSSION_STATUS.close  # close discussion

            if section.is_video:
                params.update(
                    image=None,
                    with_video=True
                )

            article = ArticleFactory(**params)

            # comments
            comment_count = random.randint(0, STR['max_com_count'])
            comment_tokens = random.sample(tokens, comment_count)
            comment_users = random.sample(users, comment_count)
            for j in range(comment_count):
                c_params = dict(article=article)
                if random.randint(0, 1):
                    c_params['token'] = comment_tokens[j]
                else:
                    c_params['user'] = comment_users[j]
                CommentFactory(**c_params)

            # multimedia
            if not random.randint(0, 8):
                if random.randint(0, 5):
                    MultimediaFactory(article=article)
                else:
                    MultimediaFactory.create_batch(2, article=article)

        self.stdout.write('Generate resources...')
        resource_types = [
            PartitionFactory(name='Персональные сайты'),
            PartitionFactory(name='Партии и общественные движения'),
            PartitionFactory(name='Оппозиционные СМИ'),
            PartitionFactory(name='Аналитика'),
            PartitionFactory(name='Креативные проекты'),
            PartitionFactory(name='Блоги и форумы'),
            PartitionFactory(name='Музыка'),
            PartitionFactory(name='Литература и искусство'),
            PartitionFactory(name='Региональные организации'),
            PartitionFactory(name='Библиотеки'),
            PartitionFactory(name='История')
        ]
        for i in range(len(resource_types) * 6):
            ResourceFactory(partition=random.choice(resource_types), rating=random.randint(0, 10))

        self.stdout.write('Generate ratings(articles votes)...')
        all_article_ids = list(Article.objects.values_list('id', flat=True))
        article_ids = random.sample(all_article_ids, int(len(all_article_ids) * 0.9))  # 90% articles with votes
        for article_id in article_ids:
            self.create_votes_for(
                article_id, article_ct, STR['max_art_vote_count'], tokens, users, lambda: random.randint(1, 5)
            )

        self.stdout.write('Generate likes(comments votes)...')
        all_comment_ids = list(Comment.objects.values_list('id', flat=True))
        comment_ids = random.sample(all_comment_ids, int(len(all_comment_ids) * 0.9))  # 90% comments with likes
        for comment_id in comment_ids:
            self.create_votes_for(
                comment_id, comment_ct, STR['max_like_count'], tokens, users, lambda: random.choice([-1, 1])
            )

        self.stdout.write('Generate notices...')
        for i in range(STR['notice_count']):
            if random.randint(0, 2):
                NoticeFactory()
            else:
                NoticeFactory(status=Notice.STATUS.new)

        self.stdout.write('Generate polls...')
        polls = PollFactory.create_batch(STR['poll_count'])
        for poll in polls:
            choices = ChoiceFactory.create_batch(random.randint(3, 8), poll=poll)
            for choice in choices:
                self.create_votes_for(
                    choice.id, choice_ct, STR['max_choice_vote_count'], tokens, users, lambda: 1
                )

        if kwargs.get('dev'):
            self.stdout.write('Generate bloggers with entries...')
            bloggers = BloggerFactory.create_batch(10)
            for blogger in bloggers:
                EntryFactory.create_batch(random.randint(STR['min_entry_count'], STR['max_entry_count']), blogger=blogger)

    def create_votes_for(self, obj_id, obj_ct, max_count, tokens, users, score_fun):
        vote_count = random.randint(0, max_count)
        vote_tokens = random.sample(tokens, vote_count)
        vote_users = random.sample(users, vote_count)
        for i in range(vote_count):
            params = dict(object_id=obj_id, content_type=obj_ct, score=score_fun())
            if random.randint(0, 1):
                params['token'] = vote_tokens[i]
            else:
                params['user'] = vote_users[i]
            VoteFactory(**params)

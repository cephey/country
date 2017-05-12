import os
import pytz
import xmltodict
import responses
from datetime import datetime
from freezegun import freeze_time

from django.conf import settings
from django.test import TestCase, Client
from django.core.management import call_command

from apps.authors.factories import AuthorFactory
from apps.articles.models import Article, Section
from apps.articles.factories import (ArticleFactory, SectionFactory, CommentFactory,
                                     MultimediaFactory, VideoSectionFactory,
                                     PartnerVideoSectionFactory)
from apps.articles.tasks import download_latest_partners_videos
from apps.tags.factories import TagFactory
from apps.votes.factories import VoteFactory
from apps.users.factories import UserFactory


class AddArticleTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_create_ok(self):
        data = {
            'title': 'Погода',
            'content': 'В городе солнечная погода',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/addnews/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/addnews/#res')
        self.assertContains(resp, 'Материал успешно добавлен. После одобрения редактора')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'Погода')
        self.assertEqual(articles[0].content, 'В городе солнечная погода')
        self.assertEqual(articles[0].status, Article.STATUS.new)

    def test_create_fail(self):
        data = {
            'title': 'Погода',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/addnews/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Произошла ошибка: неверно заполнены поля')
        self.assertContains(resp, 'Обязательное поле')
        self.assertFalse(Article.objects.exists())

    def test_add_video_ok(self):
        data = {
            'title': 'Звезды',
            'content': 'На небе яркие звезды',
            'video': 'https://www.youtube.com/watch?v=bob',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/video/add/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/video/add/#res')
        self.assertContains(resp, 'Материал успешно добавлен. После одобрения редактора')

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'Звезды')
        self.assertEqual(articles[0].content, 'На небе яркие звезды')
        self.assertEqual(articles[0].video, 'https://www.youtube.com/watch?v=bob')
        self.assertEqual(articles[0].status, Article.STATUS.new)

    def test_add_video_fail(self):
        data = {
            'title': 'Звезды',
            'video': 'bob',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/video/add/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Произошла ошибка: неверно заполнены поля')
        self.assertContains(resp, 'Введите правильный URL')
        self.assertFalse(Article.objects.exists())


class ArticleTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_detail_page(self):
        section = SectionFactory(name='Политика', slug='politic')
        author = AuthorFactory(first_name='Денис', last_name='Белов')
        tags = [TagFactory(name='оон'), TagFactory(name='greenpeace')]

        with freeze_time('2017-04-20'):
            article = ArticleFactory(title='Зимний день', section=section, authors=[author],
                                     tags=tags, source='Марс', source_link='http://mars.ru',
                                     content='Однажды в студеную зимнюю пору')

        for score in (2, 4, 5):
            VoteFactory(content_object=article, score=score)

        CommentFactory(article=article, token='123', title='Хороший пост')
        CommentFactory(article=article, token='abc', title='Плохой пост')
        CommentFactory(article=article, token='one', is_active=False)
        MultimediaFactory(article=article, link='http://vk.com', description='схема')

        resp = self.app.get('/material/politic/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['object'], article)
        self.assertEqual(len(resp.context['art_comments']), 2)
        self.assertEqual(resp.context['art_section'], section)
        self.assertNotIn('in_sections', resp.context)

        self.assertContains(resp, 'Зимний день')
        self.assertContains(resp, 'Однажды в студеную зимнюю пору')

        self.assertContains(resp, 'Опубликовано 20.04.2017')
        self.assertContains(resp, 'Белов Денис')
        self.assertContains(resp, 'комментариев 2')

        # media
        self.assertContains(resp, 'Прикреплено')
        self.assertContains(resp, 'http://vk.com')
        self.assertContains(resp, 'схема')

        # source
        self.assertContains(resp, 'Источник')
        self.assertContains(resp, 'Марс')
        self.assertContains(resp, 'http://mars.ru')

        # tags
        self.assertContains(resp, 'оон')
        self.assertContains(resp, 'greenpeace')

        self.assertContains(resp, 'Рейтинг: 3,67')
        self.assertContains(resp, 'Голосов: 3')
        self.assertContains(resp, 'Поделиться')

        # comments
        self.assertContains(resp, 'Хороший пост')
        self.assertContains(resp, 'Плохой пост')
        self.assertContains(resp, 'Написать комментарий')

    def test_detail_video_page(self):
        section = VideoSectionFactory()
        article = ArticleFactory(title='Выходка', section=section, content='Небольшое описание',
                                 video='https://www.youtube.com/watch?v=911')

        resp = self.app.get('/material/video/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)

        self.assertContains(resp, 'Выходка')
        self.assertContains(resp, 'Небольшое описание')

        self.assertContains(resp, 'Видео')
        self.assertContains(resp, '<iframe width="560" height="315" src="https://www.youtube.com/embed/911"')

    def test_detail_page_with_hide_comments(self):
        article = ArticleFactory(title='Об оружии', show_comments=False)

        CommentFactory(article=article, token='123', title='Меня не видно')
        CommentFactory(article=article, token='abc', title='Я скрыт')

        ArticleFactory(title='Машины гибриды', section__slug='politic')
        ArticleFactory(title='Электро байки', section__slug='economic')

        resp = self.app.get('/material/news/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(len(resp.context['in_sections']), 2)
        self.assertNotIn('art_comments', resp.context)

        self.assertContains(resp, 'Об оружии')
        self.assertContains(resp, 'Машины гибриды')
        self.assertContains(resp, 'Электро байки')

        self.assertNotContains(resp, 'Всего комментариев к статье')
        self.assertNotContains(resp, 'Меня не видно')
        self.assertNotContains(resp, 'Я скрыт')

    def test_discussion_status(self):
        article = ArticleFactory()

        # anonymous
        resp = self.app.get('/material/news/{}/'.format(article.id))
        self.assertNotContains(resp, 'закрыть обсуждение')

        # auth user
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.get('/material/news/{}/'.format(article.id))
        self.assertNotContains(resp, 'закрыть обсуждение')

        # admin
        user.is_staff = True
        user.save()
        resp = self.app.get('/material/news/{}/'.format(article.id))
        self.assertContains(resp, 'закрыть обсуждение')

    def test_change_discussion_status(self):
        article = ArticleFactory()

        # anonymous
        resp = self.app.get('/material/{}/close/'.format(article.id),
                            HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Article.objects.first().discussion_status, 'open')

        # auth user
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.get('/material/{}/close/'.format(article.id),
                            HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Article.objects.first().discussion_status, 'open')

        # admin
        user.is_staff = True
        user.save()
        resp = self.app.get('/material/{}/close/'.format(article.id),
                            HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')
        self.assertEqual(Article.objects.first().discussion_status, 'close')


class TasksTestCase(TestCase):

    @responses.activate
    def test_download_latest_video(self):
        responses.add(responses.GET, 'https://www.youtube.com/feeds/videos.xml',
                      body=open('fixtures/xml/video_rss.xml').read())

        section = PartnerVideoSectionFactory(channel='radio')
        download_latest_partners_videos()

        articles = Article.objects.order_by('id')
        self.assertEqual(len(articles), 2)

        self.assertEqual(articles[0].section, section)
        self.assertEqual(articles[0].title, 'Невзоровские среды 03 05 2017')
        self.assertEqual(articles[0].status, 'approved')
        self.assertEqual(articles[0].video, 'https://www.youtube.com/watch?v=gB-tmfPfPmw')
        self.assertEqual(articles[0].publish_date, datetime(2017, 5, 3, 23, 2, 8, tzinfo=pytz.utc))

        self.assertEqual(articles[1].section, section)
        self.assertEqual(articles[1].title, 'Милонов #надоел - Питер, 1 мая 2017')
        self.assertEqual(articles[1].status, 'approved')
        self.assertEqual(articles[1].video, 'https://www.youtube.com/watch?v=3VsBEIid21g')
        self.assertEqual(articles[1].publish_date, datetime(2017, 5, 1, 13, 47, 43, tzinfo=pytz.utc))


class ImportTestCase(TestCase):

    def test_import_channels(self):
        call_command(
            'migrate_channels',
            path=os.path.join(settings.BASE_DIR, 'fixtures/csv/import_video_importer.csv')
        )
        sections = Section.objects.order_by('id')
        self.assertEqual(len(sections), 4)

        self.assertEqual(sections[0].name, 'Nevex.TV')
        self.assertEqual(sections[0].slug, 'video_partner_nevextv')
        self.assertTrue(sections[0].is_video)
        self.assertEqual(sections[0].channel, 'Nevextv')
        self.assertEqual(sections[0].ext_id, 8221862)

        self.assertEqual(sections[1].slug, 'video_partner_dorenko')
        self.assertEqual(sections[1].ext_id, 10025524)

        self.assertEqual(sections[2].name, 'Красное.ТВ')
        self.assertEqual(sections[2].channel, 'krasnoetv')

        self.assertEqual(sections[3].name, 'lugansk24')
        self.assertEqual(sections[3].slug, 'video_partner_lugansk24')

    def test_import_video(self):
        section1 = PartnerVideoSectionFactory(ext_id=123456)
        section2 = PartnerVideoSectionFactory(ext_id=200300)
        call_command(
            'migrate_partners_videos',
            path=os.path.join(settings.BASE_DIR, 'fixtures/csv/import_video_news.csv')
        )
        articles = Article.objects.order_by('id')
        self.assertEqual(len(articles), 3)

        self.assertEqual(articles[0].title, 'Остальная Россия')
        self.assertEqual(articles[0].section, section2)
        self.assertEqual(articles[0].publish_date, datetime(2012, 1, 30, 14, 20, 30, 533001, tzinfo=pytz.utc))
        self.assertEqual(articles[0].video, 'http://www.youtube.com/watch?v=y39Z_4V1A9c&feature=youtube_gdata')
        self.assertEqual(articles[0].status, 'approved')

        self.assertEqual(articles[1].title, 'Новая Сила')
        self.assertEqual(articles[1].section, section1)

        self.assertEqual(articles[2].section, section1)
        self.assertEqual(articles[2].video, 'http://www.youtube.com/watch?v=tX_MY6xVvlg&feature=youtube_gdata')


class SitemapTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_index_sitemap(self):
        resp = self.app.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)

        data = xmltodict.parse(resp.content)
        sitemaps = data['sitemapindex']['sitemap']
        self.assertEqual(len(sitemaps), 3)

        paths = sorted([s['loc'] for s in sitemaps])
        self.assertTrue(paths[0].endswith('/sitemap-news.xml'))
        self.assertTrue(paths[1].endswith('/sitemap-sections.xml'))
        self.assertTrue(paths[2].endswith('/sitemap-tags.xml'))

    def test_articles_sitemap(self):
        section = SectionFactory(name='Политика', slug='politic')
        with freeze_time('2017-05-02 09:11:12'):
            article1 = ArticleFactory(section=section)
        with freeze_time('2017-05-01 10:11:12'):
            article2 = ArticleFactory(section=section, is_news=True)

        resp = self.app.get('/sitemap-news.xml')
        self.assertEqual(resp.status_code, 200)

        data = xmltodict.parse(resp.content)
        urls = data['urlset']['url']
        self.assertEqual(len(urls), 2)

        self.assertTrue(urls[0]['loc'].endswith('/material/politic/{}/'.format(article1.id)))
        self.assertEqual(urls[0]['lastmod'], '2017-05-02')
        self.assertEqual(urls[0]['changefreq'], 'daily')
        self.assertEqual(urls[0]['priority'], '0.8')

        self.assertTrue(urls[1]['loc'].endswith('/material/news/{}/'.format(article2.id)))
        self.assertEqual(urls[1]['lastmod'], '2017-05-01')

    def test_sections_sitemap(self):
        SectionFactory(name='Политика', slug='politic')

        with freeze_time('2017-05-06 07:07:59'):
            resp = self.app.get('/sitemap-sections.xml')
        self.assertEqual(resp.status_code, 200)

        data = xmltodict.parse(resp.content)
        urls = data['urlset']['url']
        self.assertEqual(len(urls), 2)

        self.assertTrue(urls[0]['loc'].endswith('/material/news/'))
        self.assertEqual(urls[0]['lastmod'], '2017-05-06')
        self.assertEqual(urls[0]['changefreq'], 'daily')
        self.assertEqual(urls[0]['priority'], '0.7')

        self.assertTrue(urls[1]['loc'].endswith('/material/politic/'))
        self.assertEqual(urls[1]['lastmod'], '2017-05-06')

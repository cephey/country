import xmltodict
from freezegun import freeze_time
from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory
from apps.tags.factories import TagFactory


class TagTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_tag_detail_page(self):
        tag1 = TagFactory(name='колибри')
        tag2 = TagFactory(name='воробей')

        ArticleFactory(title='Птицы', tags=[tag1, tag2])
        ArticleFactory(title='Северные', tags=[tag2])
        ArticleFactory(title='Южные', tags=[tag1])
        ArticleFactory(title='Западные', tags=[tag1, tag2], is_active=False)

        resp = self.app.get('/tags/{}/'.format(tag1.id))
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['object_list']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].title, 'Южные')
        self.assertEqual(articles[1].title, 'Птицы')
        self.assertEqual(resp.context['partition'], tag1)

        self.assertContains(resp, 'колибри')
        self.assertNotContains(resp, 'воробей')


class SitemapTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_tags_sitemap(self):
        with freeze_time('2017-05-04 09:11:12'):
            tag1 = TagFactory()
        with freeze_time('2017-05-03 10:11:12'):
            tag2 = TagFactory()

        resp = self.app.get('/sitemap-tags.xml')
        self.assertEqual(resp.status_code, 200)

        data = xmltodict.parse(resp.content)
        urls = data['urlset']['url']
        self.assertEqual(len(urls), 2)

        self.assertTrue(urls[0]['loc'].endswith('/tags/{}/'.format(tag1.id)))
        self.assertEqual(urls[0]['lastmod'], '2017-05-04')
        self.assertEqual(urls[0]['changefreq'], 'daily')
        self.assertEqual(urls[0]['priority'], '0.8')

        self.assertTrue(urls[1]['loc'].endswith('/tags/{}/'.format(tag2.id)))
        self.assertEqual(urls[1]['lastmod'], '2017-05-03')

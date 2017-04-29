from freezegun import freeze_time
import xml.etree.ElementTree as ET
from django.test import TestCase, Client
from apps.articles.factories import SectionFactory, ArticleFactory, VideoSectionFactory


class RSSTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_get_rss(self):
        with freeze_time('2017-04-20 21:44:02'):
            section1 = SectionFactory(name='Политика', slug='politic')
            article1 = ArticleFactory(section=section1, title='Береза', description='Белая тонкая')

            section2 = VideoSectionFactory(name='Народ', slug='video_national')
            article2 = ArticleFactory(section=section2, title='Клен', description='Шуршащие листья')
            ArticleFactory(section=section2, title='Ива', description='Мягкие ветки', is_active=False)

        resp = self.app.get('/export/rss/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), 'application/rss+xml; charset=utf-8')

        root = ET.fromstring(resp.content)
        self.assertEqual(root.tag, 'rss')
        self.assertEqual(len(root), 1)

        channel = root[0]
        self.assertEqual(channel.tag, 'channel')
        self.assertEqual(len(channel), 9)

        self.assertEqual(channel[0].tag, 'title')
        self.assertEqual(channel[0].text, 'ФОРУМ.мск')

        self.assertEqual(channel[1].tag, 'link')
        self.assertEqual(channel[1].text, 'http://forum-msk.org')

        self.assertEqual(channel[2].tag, 'description')
        self.assertEqual(channel[2].text, 'ФОРУМ.мск - Интернет-портал объединяющейся оппозиции')

        self.assertEqual(channel[4].tag, 'language')
        self.assertEqual(channel[4].text, 'ru-RU')

        self.assertEqual(channel[5].tag, 'lastBuildDate')
        self.assertEqual(channel[5].text, 'Thu, 20 Apr 2017 21:44:02 +0000')

        self.assertEqual(channel[6].tag, 'pubDate')
        self.assertEqual(channel[6].text, 'Thu, 20 Apr 2017 21:44:02 +0000')

        # article2
        self.assertEqual(channel[7].tag, 'item')
        self.assertEqual(len(channel[7]), 6)

        self.assertEqual(channel[7][0].tag, 'title')
        self.assertEqual(channel[7][0].text, 'Клен')
        self.assertEqual(channel[7][1].tag, 'link')
        self.assertTrue(channel[7][1].text.endswith('/material/video/{}/'.format(article2.id)))
        self.assertEqual(channel[7][2].tag, 'description')
        self.assertEqual(channel[7][2].text, 'Шуршащие листья')
        self.assertEqual(channel[7][3].tag, 'pubDate')
        self.assertEqual(channel[7][3].text, 'Thu, 20 Apr 2017 21:44:02 +0000')
        self.assertEqual(channel[7][4].tag, 'guid')
        self.assertTrue(channel[7][4].text.endswith('/material/video/{}/'.format(article2.id)))
        self.assertEqual(channel[7][5].tag, 'category')
        self.assertTrue(channel[7][5].attrib['domain'].endswith('/material/video_national/'))

        # article1
        self.assertEqual(channel[8].tag, 'item')
        self.assertEqual(len(channel[8]), 6)

        self.assertEqual(channel[8][0].text, 'Береза')
        self.assertTrue(channel[8][1].text.endswith('/material/politic/{}/'.format(article1.id)))
        self.assertEqual(channel[8][2].text, 'Белая тонкая')
        self.assertEqual(channel[8][3].text, 'Thu, 20 Apr 2017 21:44:02 +0000')
        self.assertTrue(channel[8][5].attrib['domain'].endswith('/material/politic/'))

    def test_rss_deprecated_url(self):
        resp = self.app.get('/export/rss.html')
        self.assertEqual(resp.status_code, 200)

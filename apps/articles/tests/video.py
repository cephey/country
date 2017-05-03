from django.test import TestCase, Client
from django.core.cache import cache
from apps.articles.factories import SectionFactory, ArticleFactory, VideoSectionFactory


class VideoTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def tearDown(self):
        cache.clear()

    def test_index_video_page(self):
        section1 = VideoSectionFactory(name='Политика', slug='video_politic')  # 3 item block
        section2 = VideoSectionFactory(name='ТВ', slug='video_partner_nevextv')  # 2 item block
        section3 = VideoSectionFactory(name='Народ', slug='video_national')  # 5 item block
        SectionFactory(name='Экономика', slug='video_economic')  # non video

        for section in (section1, section2, section3):
            ArticleFactory.create_batch(4, section=section, image=None, with_video=True)
            ArticleFactory(section=section, image=None, with_video=True, is_news=True)  # news

        resp = self.app.get('/video/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('main_news', resp.context)
        self.assertIn('main_material', resp.context)

        data = resp.context['materials']
        self.assertEqual(len(data), 3)

        self.assertEqual(data['video_politic']['section'], section1)
        self.assertEqual(len(data['video_politic']['articles']), 3)

        self.assertEqual(data['video_partner_nevextv']['section'], section2)
        self.assertEqual(len(data['video_partner_nevextv']['articles']), 2)

        self.assertEqual(data['video_national']['section'], section3)
        self.assertEqual(len(data['video_national']['articles']), 5)

        self.assertContains(resp, 'Репортаж дня')
        self.assertContains(resp, 'Главный сюжет')
        self.assertContains(resp, 'Политика')
        self.assertContains(resp, 'ТВ')
        self.assertContains(resp, 'Народ')

    def test_redirect_video_page(self):
        resp = self.app.get('/video/', {'video': 123})
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.url, '/video/123/')

    def test_detail_video_page(self):
        section = VideoSectionFactory(name='Политика', slug='video_politic')
        article = ArticleFactory(title='Скорость света', section=section, image=None,
                                 video='https://www.youtube.com/watch?v=bob')

        resp = self.app.get('/video/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)

        self.assertNotIn('main_material', resp.context)
        self.assertEqual(resp.context['main_news'], article)

        data = resp.context['materials']
        self.assertEqual(data['video_politic']['section'], section)
        self.assertEqual(len(data['video_politic']['articles']), 1)

        self.assertContains(resp, 'Скорость света')
        self.assertContains(resp, '<iframe width="560" height="315" src="https://www.youtube.com/embed/bob"')

    def test_video_section_page(self):
        section = VideoSectionFactory()
        ArticleFactory.create_batch(4, section=section)

        resp = self.app.get('/material/video/')
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.context['partition'].slug, 'video')
        self.assertIsNone(resp.context['nav_section'])
        self.assertEqual(len(resp.context['object_list']), 4)

        self.assertContains(resp, 'Видео')

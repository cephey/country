from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory, SectionFactory


class PdaTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_index_page_200(self):
        article = ArticleFactory(title='Свет фар', is_news=True)

        resp = self.app.get('/pda/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name[0], 'pda/index.html')
        self.assertEqual(resp.context['main_news'], article)

        self.assertContains(resp, 'Свет фар')

    def test_section_page_200(self):
        section = SectionFactory(name='Политика', slug='politic')
        article = ArticleFactory(section=section, title='Радуга в окне')
        ArticleFactory(title='Плотный звук')

        resp = self.app.get('/pda/material/politic/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name[0], 'pda/articles/list.html')

        self.assertEqual(resp.context['partition'], section)
        self.assertEqual(set(resp.context['object_list']), {article})

        self.assertContains(resp, 'Политика')
        self.assertContains(resp, 'Радуга в окне')
        self.assertNotContains(resp, 'Плотный звук')

    def test_article_detail_page_200(self):
        article = ArticleFactory(section__slug='politic', title='Сильный шок',
                                 content='Долгоживущий поток')

        resp = self.app.get('/pda/material/politic/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name[0], 'pda/articles/detail.html')

        self.assertEqual(resp.context['object'], article)
        self.assertEqual(resp.context['art_section'].slug, 'politic')

        self.assertContains(resp, 'Сильный шок')
        self.assertContains(resp, 'Долгоживущий поток')

from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory
from apps.authors.factories import AuthorFactory


class ForumTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_index_page(self):
        author = AuthorFactory(first_name='Глеб', last_name='Круглый')

        ArticleFactory(title='Белая бумага', authors=[author])
        ArticleFactory(title='Плотный картон', is_active=False)
        ArticleFactory(title='Толстая тетрадь')
        ArticleFactory(title='Ватман', discussion_status='close')

        resp = self.app.get('/forum/')
        with open('/Users/ptitsyn/Desktop/lolo.html', 'wb') as f:
            f.write(resp.content.replace(b'\n', b'').replace(b'\t', b''))
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['object_list']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].title, 'Толстая тетрадь')
        self.assertEqual(articles[1].title, 'Белая бумага')

        self.assertContains(resp, 'Белая бумага')
        self.assertContains(resp, 'Толстая тетрадь')
        self.assertContains(resp, 'Круглый Глеб')
        self.assertNotContains(resp, 'Плотный картон')

from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory
from apps.authors.factories import AuthorFactory


class AuthorTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_detail_page(self):
        author = AuthorFactory(first_name='Игорь', last_name='Светлов',
                               description='Родился, женился и т.д.')

        ArticleFactory(authors=[author], title='Суббота')
        ArticleFactory(authors=[author], title='Воскресенье')
        ArticleFactory(authors=[author], is_active=False)
        ArticleFactory(with_author=True)

        resp = self.app.get('/author/{}/'.format(author.id))
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['obj_atricles']
        self.assertEqual(len(articles), 2)
        self.assertEqual(resp.context['object'], author)

        self.assertContains(resp, 'Автор - Светлов Игорь')
        self.assertContains(resp, 'Об авторе')
        self.assertContains(resp, 'Родился, женился и т.д.')

        self.assertContains(resp, 'Последние статьи автора')
        self.assertContains(resp, 'Суббота')
        self.assertContains(resp, 'Воскресенье')

    def test_deprecated_url(self):
        author = AuthorFactory(first_name='Ян', last_name='Ин')
        resp = self.app.get('/author/{}/'.format(author.id))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['object'], author)
        self.assertContains(resp, 'Автор - Ин Ян')

from django.test import TestCase, Client

from apps.articles.factories import ArticleFactory, CommentFactory
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
        self.assertEqual(resp.status_code, 200)

        articles = resp.context['object_list']
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0].title, 'Толстая тетрадь')
        self.assertEqual(articles[1].title, 'Белая бумага')

        self.assertContains(resp, 'Белая бумага')
        self.assertContains(resp, 'Толстая тетрадь')
        self.assertContains(resp, 'Круглый Глеб')
        self.assertNotContains(resp, 'Плотный картон')

    def test_thread_page(self):
        article = ArticleFactory(title='Печенька')

        CommentFactory(title='Круг', content='Яркий', article=article)
        CommentFactory(title='Квадрат', content='Бледный', article=article)
        CommentFactory(title='Ромб', content='Серый')

        resp = self.app.get('/forum/{}/'.format(article.id))
        self.assertEqual(resp.status_code, 200)

        comments = resp.context['object_list']
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].title, 'Круг')
        self.assertEqual(comments[1].title, 'Квадрат')

        self.assertContains(resp, ':: Печенька')
        self.assertContains(resp, 'Яркий')
        self.assertContains(resp, 'Бледный')
        self.assertNotContains(resp, 'Серый')
        self.assertContains(resp, 'Ответить')

from django.test import TestCase, Client
from apps.articles.models import Article


class ArticleTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_create_ok(self):
        data = {
            'title': 'Погода',
            'content': 'В городе солнечная погода'
        }
        resp = self.app.post('/addnews/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/addnews/#res')
        self.assertIn('Материал успешно добавлен. После одобрения редактора',
                      resp.content.decode('utf-8'))

        articles = Article.objects.all()
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0].title, 'Погода')
        self.assertEqual(articles[0].content, 'В городе солнечная погода')
        self.assertEqual(articles[0].status, Article.STATUS.new)

    def test_create_fail(self):
        data = {
            'title': 'Погода'
        }
        resp = self.app.post('/addnews/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('Произошла ошибка: неверно заполнены поля', resp.content.decode('utf-8'))
        self.assertIn('Обязательное поле', resp.content.decode('utf-8'))
        self.assertFalse(Article.objects.exists())

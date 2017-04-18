from django.test import TestCase, Client

from apps.articles.models import Comment
from apps.articles.factories import ArticleFactory


class CommentTestCase(TestCase):

    def setUp(self):
        self.app = Client()

    def test_create_ok(self):
        article = ArticleFactory(section__slug='politic')

        data = {
            'article': article.id,
            'parent': '',
            'username': 'Колобок',
            'title': 'История начинается',
            'content': 'Жили-были старик со старухой'
        }
        resp = self.app.post('/comment/create/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/material/politic/{}/'.format(article.id))

        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].article, article)
        self.assertEqual(comments[0].username, 'Колобок')
        self.assertEqual(comments[0].content, 'Жили-были старик со старухой')

        # comment exists on page
        self.assertContains(resp, 'Колобок')
        self.assertContains(resp, 'История начинается')
        self.assertContains(resp, 'Жили-были старик со старухой')

    def test_create_fail(self):
        article = ArticleFactory(section__slug='politic')

        data = {
            'article': article.id,
            'parent': '',
            'username': 'Ряба',
            'title': '',
            'content': ''
        }
        resp = self.app.post('/comment/create/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name[0], 'articles/create_comment.html')

        self.assertEqual(resp.context['form'].errors['content'][0], 'Обязательное поле.')
        self.assertContains(resp, 'Обязательное поле.')

from django.test import TestCase, Client

from apps.articles.models import Comment
from apps.articles.factories import ArticleFactory, CommentFactory
from apps.users.factories import UserFactory


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
            'content': 'Жили-были старик со старухой',
            'captcha_0': '*',
            'captcha_1': 'passed'
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
            'content': '',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/comment/create/', data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name[0], 'articles/create_comment.html')

        self.assertEqual(resp.context['form'].errors['content'][0], 'Обязательное поле.')
        self.assertContains(resp, 'Обязательное поле.')

    def test_create_with_parent(self):
        article = ArticleFactory(section__slug='politic')
        comment = CommentFactory(article=article)

        data = {
            'article': article.id,
            'parent': comment.id,
            'username': 'Шапочка',
            'content': 'Бабушка и волки',
            'captcha_0': '*',
            'captcha_1': 'passed'
        }
        resp = self.app.post('/comment/create/', data, follow=True)
        url, status_code = resp.redirect_chain[0]
        self.assertEqual(status_code, 302)
        self.assertEqual(url, '/material/politic/{}/'.format(article.id))

        comments = Comment.objects.order_by('-id')
        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].article, article)
        self.assertEqual(comments[0].parent, comment)

        # comment exists on page
        self.assertContains(resp, 'Шапочка')
        self.assertContains(resp, '(без названия)')

    def test_delete(self):
        comment = CommentFactory()

        # anonymous
        resp = self.app.get('/comment/{}/delete/'.format(comment.id), HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Comment.objects.active().exists())

        # auth user
        user = UserFactory(username='andrey')
        user.set_password('secret')
        user.save()
        self.app.login(username='andrey', password='secret')

        resp = self.app.get('/comment/{}/delete/'.format(comment.id), HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 403)
        self.assertTrue(Comment.objects.active().exists())

        # admin
        user.is_staff = True
        user.save()
        resp = self.app.get('/comment/{}/delete/'.format(comment.id), HTTP_REFERER='/material/news/1/')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/material/news/1/')
        self.assertFalse(Comment.objects.active().exists())
